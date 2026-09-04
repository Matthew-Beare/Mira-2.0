package com.mira.client.googleworkspace;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Verifies one Google Picker grant and binds Android to one compatible MIRA Personal Workspace.
 *
 * <p>The binding contains no access token. Token material remains inside this provider module and
 * is consumed only while verifying or constructing a bounded transport gateway. The ordinary-user
 * path uses Google's own Picker, never a copied spreadsheet ID or broad Drive enumeration.</p>
 */
public final class GoogleWorkspaceConnection {
    public static final String DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file";
    public static final String SPREADSHEET_MIME_TYPE = "application/vnd.google-apps.spreadsheet";

    static final String METADATA_RANGE = "Metadata!A1:B32";
    static final String COMMAND_HEADER_RANGE = "Commands!A1:P1";
    static final String CHANGE_HEADER_RANGE = "Changes!A1:I1";

    private static final Pattern FILE_ID_PATTERN = Pattern.compile("^[A-Za-z0-9_-]{10,256}$");
    private static final int MAX_METADATA_ROWS = 32;
    private static final List<String> COMMAND_HEADERS = immutableList(
            "command_id", "subject_id", "data_class", "action", "api_major",
            "schema_version", "resource_id", "payload_json", "idempotency_key",
            "expected_revision", "submitted_at", "status", "result_json", "processed_at",
            "error_code", "error_message"
    );
    private static final List<String> CHANGE_HEADERS = immutableList(
            "change_seq", "change_id", "data_class", "resource_id", "revision",
            "payload_json", "recorded_at", "source_command_id", "readback_verified"
    );

    private static final Map<String, String> REQUIRED_METADATA;
    static {
        LinkedHashMap<String, String> required = new LinkedHashMap<>();
        required.put("schema_version", "mira-structured-state-v1");
        required.put("store_role", "personal_google_starter");
        required.put("environment", "mira_2_personal_clean");
        required.put("data_policy", "clean_starter_only");
        required.put("adapter_contract", "STORE-001");
        required.put("writer_model", "single_writer");
        REQUIRED_METADATA = Collections.unmodifiableMap(required);
    }

    private final WorkspaceApi api;

    public GoogleWorkspaceConnection(WorkspaceApi api) {
        this.api = Objects.requireNonNull(api, "api");
    }

    /** Verifies the one file explicitly granted by Google Picker and returns a token-free binding. */
    public VerifiedBinding connect(PickerGrant grant) throws ConnectionException {
        Objects.requireNonNull(grant, "grant");
        String token = requireToken(grant.accessToken());
        List<String> ids = grant.pickedFileIds();
        if (ids.size() != 1) {
            throw failure(
                    "picker_selection_invalid",
                    "Google Picker must grant exactly one MIRA spreadsheet"
            );
        }
        return verify(token, requireFileId(ids.get(0)), null);
    }

    /**
     * Revalidates a prior token-free binding from a fresh Picker grant and rejects provider-file
     * drift explicitly. Useful when the provider intentionally returns selected-file evidence.
     */
    public VerifiedBinding revalidate(VerifiedBinding binding, PickerGrant grant)
            throws ConnectionException {
        Objects.requireNonNull(binding, "binding");
        Objects.requireNonNull(grant, "grant");
        List<String> ids = grant.pickedFileIds();
        if (ids.size() != 1) {
            throw failure(
                    "picker_selection_invalid",
                    "Google Picker must grant exactly one MIRA spreadsheet"
            );
        }
        return verify(requireToken(grant.accessToken()), requireFileId(ids.get(0)), binding);
    }

    /** Provider-package seam for refreshing a stored binding with a fresh token and no new Picker. */
    VerifiedBinding revalidateWithToken(VerifiedBinding binding, String accessToken)
            throws ConnectionException {
        Objects.requireNonNull(binding, "binding");
        return verify(
                requireToken(accessToken),
                requireFileId(binding.spreadsheetId()),
                binding
        );
    }

    private VerifiedBinding verify(String token, String spreadsheetId, VerifiedBinding prior)
            throws ConnectionException {
        final FileMetadata file;
        final List<List<Object>> metadataRows;
        final List<List<Object>> commandHeader;
        final List<List<Object>> changeHeader;
        try {
            file = api.readFileMetadata(token, spreadsheetId);
            metadataRows = api.readValues(token, spreadsheetId, METADATA_RANGE);
            String mutationMode = mutationMode(metadataRows);
            if ("queued_writer".equals(mutationMode)) {
                commandHeader = api.readValues(token, spreadsheetId, COMMAND_HEADER_RANGE);
                changeHeader = api.readValues(token, spreadsheetId, CHANGE_HEADER_RANGE);
            } else {
                commandHeader = Collections.emptyList();
                changeHeader = Collections.emptyList();
            }
        } catch (ProviderException exc) {
            throw new ConnectionException(exc.code(), exc.getMessage(), exc);
        }

        validateFile(file, spreadsheetId);
        Map<String, String> metadata = validateMetadata(metadataRows);
        String mutationMode = normalizedMutationMode(metadata.get("mutation_mode"));
        boolean sharedWriterReady = "queued_writer".equals(mutationMode);
        if (sharedWriterReady) {
            validateHeader(commandHeader, COMMAND_HEADERS, "Commands");
            validateHeader(changeHeader, CHANGE_HEADERS, "Changes");
        }

        VerifiedBinding verified = new VerifiedBinding(
                spreadsheetId,
                file.name(),
                metadata.get("schema_version"),
                mutationMode,
                sharedWriterReady
        );
        if (prior != null && !prior.spreadsheetId().equals(verified.spreadsheetId())) {
            throw failure("binding_changed", "Workspace revalidation resolved a different spreadsheet");
        }
        return verified;
    }

    private static String mutationMode(List<List<Object>> rows) throws ConnectionException {
        Map<String, String> metadata = validateMetadata(rows);
        return normalizedMutationMode(metadata.get("mutation_mode"));
    }

    private static String normalizedMutationMode(String value) throws ConnectionException {
        if (value == null || value.isEmpty()) {
            return "direct_single_writer";
        }
        if ("direct_single_writer".equals(value) || "queued_writer".equals(value)) {
            return value;
        }
        throw failure("workspace_schema_mismatch", "MIRA Metadata mutation_mode is unsupported");
    }

    private static void validateFile(FileMetadata file, String expectedId) throws ConnectionException {
        if (file == null || !expectedId.equals(file.id())) {
            throw failure(
                    "workspace_identity_mismatch",
                    "Drive metadata did not read back the selected file identity"
            );
        }
        if (!SPREADSHEET_MIME_TYPE.equals(file.mimeType())) {
            throw failure("workspace_type_mismatch", "Selected Google Drive file is not a Google Sheet");
        }
        if (file.trashed()) {
            throw failure("workspace_unavailable", "Selected MIRA spreadsheet is in Trash");
        }
        if (!file.canEdit()) {
            throw failure("workspace_read_only", "Selected MIRA spreadsheet is not editable by this account");
        }
        if (file.name().trim().isEmpty()) {
            throw failure(
                    "workspace_identity_mismatch",
                    "Selected MIRA spreadsheet has no readable name"
            );
        }
    }

    private static Map<String, String> validateMetadata(List<List<Object>> rows)
            throws ConnectionException {
        if (rows == null || rows.isEmpty() || rows.size() > MAX_METADATA_ROWS) {
            throw failure(
                    "workspace_schema_mismatch",
                    "MIRA Metadata table is missing or exceeds the bounded row limit"
            );
        }
        List<Object> header = rows.get(0);
        if (header == null || header.size() != 2
                || !"Key".equals(cell(header, 0))
                || !"Value".equals(cell(header, 1))) {
            throw failure("workspace_schema_mismatch", "MIRA Metadata header is invalid");
        }

        LinkedHashMap<String, String> values = new LinkedHashMap<>();
        for (int index = 1; index < rows.size(); index++) {
            List<Object> row = rows.get(index);
            if (isBlankRow(row)) {
                continue;
            }
            if (row == null || row.size() > 2) {
                throw failure(
                        "workspace_schema_mismatch",
                        "MIRA Metadata contains unexpected cells"
                );
            }
            String key = cell(row, 0).trim();
            String value = cell(row, 1).trim();
            if (key.isEmpty() || value.isEmpty()) {
                throw failure(
                        "workspace_schema_mismatch",
                        "MIRA Metadata contains an incomplete key/value row"
                );
            }
            if (values.put(key, value) != null) {
                throw failure(
                        "workspace_schema_mismatch",
                        "MIRA Metadata contains duplicate key: " + key
                );
            }
        }
        for (Map.Entry<String, String> required : REQUIRED_METADATA.entrySet()) {
            String actual = values.get(required.getKey());
            if (!required.getValue().equals(actual)) {
                throw failure(
                        "workspace_schema_mismatch",
                        "MIRA Metadata mismatch for " + required.getKey()
                );
            }
        }
        return Collections.unmodifiableMap(values);
    }

    private static void validateHeader(
            List<List<Object>> rows,
            List<String> expected,
            String table
    ) throws ConnectionException {
        if (rows == null || rows.size() != 1 || rows.get(0) == null
                || rows.get(0).size() != expected.size()) {
            throw failure(
                    "workspace_schema_mismatch",
                    table + " header is missing or has the wrong width"
            );
        }
        List<Object> row = rows.get(0);
        for (int index = 0; index < expected.size(); index++) {
            if (!expected.get(index).equals(cell(row, index))) {
                throw failure(
                        "workspace_schema_mismatch",
                        table + " header does not match MIRA protocol"
                );
            }
        }
    }

    private static String requireToken(String value) throws ConnectionException {
        if (value == null || value.trim().isEmpty() || !value.equals(value.trim())
                || value.length() > 8192) {
            throw failure(
                    "authorization_unavailable",
                    "Google authorization did not return a usable access token"
            );
        }
        return value;
    }

    private static String requireFileId(String value) throws ConnectionException {
        if (value == null || !FILE_ID_PATTERN.matcher(value).matches()) {
            throw failure(
                    "picker_selection_invalid",
                    "Google Picker returned an invalid file identity"
            );
        }
        return value;
    }

    private static String cell(List<Object> row, int index) {
        if (row == null || index < 0 || index >= row.size() || row.get(index) == null) {
            return "";
        }
        return String.valueOf(row.get(index));
    }

    private static boolean isBlankRow(List<Object> row) {
        if (row == null || row.isEmpty()) {
            return true;
        }
        for (Object value : row) {
            if (value != null && !String.valueOf(value).trim().isEmpty()) {
                return false;
            }
        }
        return true;
    }

    private static List<String> immutableList(String... values) {
        return Collections.unmodifiableList(Arrays.asList(values.clone()));
    }

    private static ConnectionException failure(String code, String message) {
        return new ConnectionException(code, message);
    }

    /** Opaque ephemeral authorization result. Token/file details remain provider-package internal. */
    public static final class PickerGrant {
        private final String accessToken;
        private final List<String> pickedFileIds;

        PickerGrant(String accessToken, List<String> pickedFileIds) {
            this.accessToken = accessToken;
            this.pickedFileIds = pickedFileIds == null
                    ? Collections.emptyList()
                    : Collections.unmodifiableList(new ArrayList<>(pickedFileIds));
        }

        String accessToken() {
            return accessToken;
        }

        List<String> pickedFileIds() {
            return pickedFileIds;
        }

        @Override
        public String toString() {
            return "PickerGrant{opaque}";
        }
    }

    /** Token-free provider binding. Provider identity is deliberately not included in toString(). */
    public static final class VerifiedBinding {
        private final String spreadsheetId;
        private final String displayName;
        private final String schemaVersion;
        private final String mutationMode;
        private final boolean sharedWriterReady;

        VerifiedBinding(
                String spreadsheetId,
                String displayName,
                String schemaVersion,
                String mutationMode,
                boolean sharedWriterReady
        ) {
            this.spreadsheetId = spreadsheetId;
            this.displayName = displayName;
            this.schemaVersion = schemaVersion;
            this.mutationMode = mutationMode;
            this.sharedWriterReady = sharedWriterReady;
        }

        String spreadsheetId() {
            return spreadsheetId;
        }

        public String displayName() {
            return displayName;
        }

        public String schemaVersion() {
            return schemaVersion;
        }

        public String mutationMode() {
            return mutationMode;
        }

        public boolean sharedWriterReady() {
            return sharedWriterReady;
        }

        public String readinessCode() {
            return sharedWriterReady ? "ready" : "needs_shared_writer_activation";
        }

        @Override
        public String toString() {
            return "VerifiedBinding{schemaVersion=" + schemaVersion
                    + ", mutationMode=" + mutationMode
                    + ", sharedWriterReady=" + sharedWriterReady + "}";
        }
    }

    public static final class FileMetadata {
        private final String id;
        private final String name;
        private final String mimeType;
        private final boolean trashed;
        private final boolean canEdit;

        public FileMetadata(String id, String name, String mimeType, boolean trashed, boolean canEdit) {
            this.id = id == null ? "" : id;
            this.name = name == null ? "" : name;
            this.mimeType = mimeType == null ? "" : mimeType;
            this.trashed = trashed;
            this.canEdit = canEdit;
        }

        public String id() { return id; }
        public String name() { return name; }
        public String mimeType() { return mimeType; }
        public boolean trashed() { return trashed; }
        public boolean canEdit() { return canEdit; }
    }

    public interface WorkspaceApi {
        FileMetadata readFileMetadata(String accessToken, String fileId) throws ProviderException;

        List<List<Object>> readValues(String accessToken, String spreadsheetId, String range)
                throws ProviderException;
    }

    public static class ProviderException extends Exception {
        private final String code;

        public ProviderException(String code, String message) {
            super(message);
            this.code = Objects.requireNonNull(code, "code");
        }

        public ProviderException(String code, String message, Throwable cause) {
            super(message, cause);
            this.code = Objects.requireNonNull(code, "code");
        }

        public String code() { return code; }
    }

    public static class ConnectionException extends Exception {
        private final String code;

        public ConnectionException(String code, String message) {
            super(message);
            this.code = Objects.requireNonNull(code, "code");
        }

        public ConnectionException(String code, String message, Throwable cause) {
            super(message, cause);
            this.code = Objects.requireNonNull(code, "code");
        }

        public String code() { return code; }
    }
}
