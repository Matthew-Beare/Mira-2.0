package com.mira.client.googleworkspace;

import com.mira.client.core.sync.GoogleWorkspaceTransport;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * Post-consent verifier/binder for the one Google Sheet selected through provider-owned Picker UI.
 *
 * <p>Google authorization proves access to a file. It does not prove the file is a compatible
 * MIRA authority. Binding therefore stays read-only until exact Metadata, Commands and Changes
 * protocol material has been verified. Raw provider identifiers remain inside this provider layer;
 * ordinary app/UI code receives the verified transport rather than a copyable spreadsheet ID.</p>
 */
public final class GoogleWorkspaceBinding {
    private static final List<String> METADATA_HEADERS = immutableList("Key", "Value");
    private static final List<String> COMMAND_HEADERS = immutableList(
            "command_id",
            "subject_id",
            "data_class",
            "action",
            "api_major",
            "schema_version",
            "resource_id",
            "payload_json",
            "idempotency_key",
            "expected_revision",
            "submitted_at",
            "status",
            "result_json",
            "processed_at",
            "error_code",
            "error_message"
    );
    private static final List<String> CHANGE_HEADERS = immutableList(
            "change_seq",
            "change_id",
            "data_class",
            "resource_id",
            "revision",
            "payload_json",
            "recorded_at",
            "source_command_id",
            "readback_verified"
    );

    private static final Map<String, String> REQUIRED_METADATA = requiredMetadata();
    private static final int MAX_METADATA_ROWS = 128;
    private static final int MAX_PROTOCOL_ROWS_DURING_BIND = 4097;

    private final GatewayFactory gatewayFactory;

    /** Production binder using the bounded Google Sheets REST gateway. */
    public GoogleWorkspaceBinding() {
        this(GoogleSheetsRestGateway::new);
    }

    GoogleWorkspaceBinding(GatewayFactory gatewayFactory) {
        this.gatewayFactory = Objects.requireNonNull(gatewayFactory, "gatewayFactory");
    }

    /** Verifies the selected file and only then constructs the proven Workspace transport. */
    public Binding bind(GoogleWorkspaceAuthorization.AuthorizedWorkspace authorized)
            throws BindingException {
        Objects.requireNonNull(authorized, "authorized");
        GoogleWorkspaceTransport.SheetsGateway gateway;
        try {
            gateway = gatewayFactory.create(
                    authorized.spreadsheetId(),
                    authorized.accessToken()
            );
        } catch (RuntimeException exc) {
            throw new BindingException(
                    "workspace_gateway_invalid",
                    "Google Workspace gateway could not be constructed",
                    exc
            );
        }
        if (gateway == null) {
            throw new BindingException(
                    "workspace_gateway_invalid",
                    "Google Workspace gateway factory returned no gateway"
            );
        }

        verifyMetadata(read(gateway, "Metadata"));
        verifyProtocolTable(
                "Commands",
                read(gateway, GoogleWorkspaceTransport.COMMANDS_TABLE),
                COMMAND_HEADERS,
                MAX_PROTOCOL_ROWS_DURING_BIND
        );
        verifyProtocolTable(
                "Changes",
                read(gateway, GoogleWorkspaceTransport.CHANGES_TABLE),
                CHANGE_HEADERS,
                MAX_PROTOCOL_ROWS_DURING_BIND
        );

        return new Binding(new GoogleWorkspaceTransport(gateway));
    }

    private static List<List<Object>> read(
            GoogleWorkspaceTransport.SheetsGateway gateway,
            String table
    ) throws BindingException {
        try {
            List<List<Object>> rows = gateway.readTable(table);
            if (rows == null) {
                throw new BindingException(
                        "workspace_protocol_invalid",
                        "Google Workspace " + table + " returned no table material"
                );
            }
            return rows;
        } catch (GoogleWorkspaceTransport.GatewayException exc) {
            throw new BindingException(
                    "workspace_provider_unavailable",
                    "Google Workspace verification read failed for " + table,
                    exc
            );
        }
    }

    private static void verifyMetadata(List<List<Object>> rows) throws BindingException {
        if (rows.isEmpty() || rows.size() > MAX_METADATA_ROWS) {
            throw protocol("MIRA Metadata table is missing or exceeds the bounded row limit");
        }
        requireExactHeader("Metadata", rows.get(0), METADATA_HEADERS);

        LinkedHashMap<String, String> metadata = new LinkedHashMap<>();
        for (int index = 1; index < rows.size(); index++) {
            List<Object> row = rows.get(index);
            if (isBlankRow(row)) {
                continue;
            }
            if (row.size() > 2) {
                throw protocol("MIRA Metadata row contains unexpected cells");
            }
            String key = cell(row, 0).trim();
            String value = cell(row, 1).trim();
            if (key.isEmpty() || value.isEmpty()) {
                throw protocol("MIRA Metadata key/value must be non-empty trimmed text");
            }
            if (metadata.put(key, value) != null) {
                throw protocol("MIRA Metadata contains duplicate key: " + key);
            }
        }

        for (Map.Entry<String, String> required : REQUIRED_METADATA.entrySet()) {
            String actual = metadata.get(required.getKey());
            if (!required.getValue().equals(actual)) {
                throw protocol(
                        "MIRA Metadata does not satisfy required " + required.getKey()
                );
            }
        }
    }

    private static void verifyProtocolTable(
            String name,
            List<List<Object>> rows,
            List<String> expectedHeader,
            int maximumRows
    ) throws BindingException {
        if (rows.isEmpty() || rows.size() > maximumRows) {
            throw protocol("MIRA " + name + " table is missing or exceeds the bounded row limit");
        }
        requireExactHeader(name, rows.get(0), expectedHeader);
    }

    private static void requireExactHeader(
            String name,
            List<Object> actual,
            List<String> expected
    ) throws BindingException {
        if (actual == null || actual.size() != expected.size()) {
            throw protocol("MIRA " + name + " headers are invalid");
        }
        for (int index = 0; index < expected.size(); index++) {
            if (!expected.get(index).equals(cell(actual, index))) {
                throw protocol("MIRA " + name + " headers are invalid");
            }
        }
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

    private static Map<String, String> requiredMetadata() {
        LinkedHashMap<String, String> result = new LinkedHashMap<>();
        result.put("schema_version", "mira-structured-state-v1");
        result.put("store_role", "personal_google_starter");
        result.put("adapter_contract", "STORE-001");
        result.put("writer_model", "single_writer");
        result.put("mutation_mode", "queued_writer");
        return Collections.unmodifiableMap(result);
    }

    private static List<String> immutableList(String... values) {
        ArrayList<String> result = new ArrayList<>(values.length);
        Collections.addAll(result, values);
        return Collections.unmodifiableList(result);
    }

    private static BindingException protocol(String message) {
        return new BindingException("workspace_protocol_invalid", message);
    }

    interface GatewayFactory {
        GoogleWorkspaceTransport.SheetsGateway create(String spreadsheetId, String accessToken);
    }

    /** Verified provider binding. Raw provider token/file identifiers are intentionally not exposed. */
    public static final class Binding {
        private final GoogleWorkspaceTransport transport;

        Binding(GoogleWorkspaceTransport transport) {
            this.transport = transport;
        }

        public GoogleWorkspaceTransport transport() {
            return transport;
        }
    }

    /** Stable fail-closed binding error for future Connections status mapping. */
    public static final class BindingException extends Exception {
        private final String code;

        BindingException(String code, String message) {
            super(message);
            this.code = code;
        }

        BindingException(String code, String message, Throwable cause) {
            super(message, cause);
            this.code = code;
        }

        public String code() {
            return code;
        }
    }
}
