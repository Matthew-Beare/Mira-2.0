package com.mira.client.core.sync;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Date;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.TimeZone;
import java.util.regex.Pattern;

/**
 * Default-Personal Google Workspace row protocol for Android reconnect.
 *
 * <p>This class owns no spreadsheet ID, OAuth token, account identity, or network client. A future
 * Google-authorized adapter supplies the narrow {@link SheetsGateway}; this transport maps the
 * provider rows onto the already-verified {@link ReconnectCoordinator.Transport} contract.</p>
 *
 * <p>The Workspace {@code Commands} inbox and append-only {@code Changes} projection are transport
 * evidence, never canonical authority. Canonical mutation remains owned by the serialized Apps
 * Script worker and STORE-001 readback.</p>
 */
public final class GoogleWorkspaceTransport implements ReconnectCoordinator.Transport {
    public static final String COMMANDS_TABLE = "Commands";
    public static final String CHANGES_TABLE = "Changes";

    private static final Pattern ID_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$");
    private static final Pattern DATA_CLASS_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$");
    private static final Pattern CHANGE_ID_PATTERN = Pattern.compile("^[0-9a-f]{64}$");
    private static final Pattern CURSOR_PATTERN =
            Pattern.compile("^mira-change-v1:(0|[1-9][0-9]*)$");

    private static final int MAX_REMOTE_COMMAND_ROWS = 4096;
    private static final int MAX_REMOTE_CHANGE_ROWS = 16384;
    private static final int MAX_JSON_CHARS = 512 * 1024;

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

    private final SheetsGateway gateway;
    private final TimestampSource timestampSource;

    /** Creates a transport over a future Google-authorized Sheets gateway. */
    public GoogleWorkspaceTransport(SheetsGateway gateway) {
        this(gateway, new SystemTimestampSource());
    }

    GoogleWorkspaceTransport(SheetsGateway gateway, TimestampSource timestampSource) {
        this.gateway = Objects.requireNonNull(gateway, "gateway");
        this.timestampSource = Objects.requireNonNull(timestampSource, "timestampSource");
    }

    @Override
    public ReconnectCoordinator.RemoteCommandState reconcileCommand(
            OfflineSyncStateStore.CommandIntent command
    ) throws ReconnectCoordinator.TransportException {
        Objects.requireNonNull(command, "command");
        validateWorkspaceCommand(command);
        CommandMaterial local = CommandMaterial.fromIntent(command);

        List<List<Object>> rows = readValidatedTable(
                COMMANDS_TABLE,
                COMMAND_HEADERS,
                MAX_REMOTE_COMMAND_ROWS
        );
        List<RemoteCommandRow> matches = commandRows(rows, local);
        if (matches.isEmpty()) {
            List<Object> append = commandAppendRow(local, timestampSource.now());
            try {
                gateway.appendRow(COMMANDS_TABLE, append);
            } catch (GatewayException appendFailure) {
                try {
                    rows = readValidatedTable(
                            COMMANDS_TABLE,
                            COMMAND_HEADERS,
                            MAX_REMOTE_COMMAND_ROWS
                    );
                    matches = commandRows(rows, local);
                } catch (ReconnectCoordinator.TransportException readFailure) {
                    throw transportFailure(appendFailure, readFailure);
                }
                if (matches.isEmpty()) {
                    throw gatewayFailure("command_append_failed", appendFailure);
                }
            }

            if (matches.isEmpty()) {
                rows = readValidatedTable(
                        COMMANDS_TABLE,
                        COMMAND_HEADERS,
                        MAX_REMOTE_COMMAND_ROWS
                );
                matches = commandRows(rows, local);
            }
            if (matches.isEmpty()) {
                throw new ReconnectCoordinator.TransportException(
                        "protocol_error",
                        "Workspace command append did not read back exact command material"
                );
            }
        }
        return reduceCommandRows(local, matches);
    }

    @Override
    public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit)
            throws ReconnectCoordinator.TransportException {
        if (limit < 1 || limit > 128) {
            throw new ReconnectCoordinator.TransportException(
                    "protocol_error",
                    "Workspace change limit must be from 1 through 128"
            );
        }
        long current = parseCursor(cursor);
        List<List<Object>> rows = readValidatedTable(
                CHANGES_TABLE,
                CHANGE_HEADERS,
                MAX_REMOTE_CHANGE_ROWS
        );

        ArrayList<ChangeRow> parsed = new ArrayList<>();
        long expectedSequence = 1;
        Set<String> identities = new HashSet<>();
        for (int index = 1; index < rows.size(); index++) {
            List<Object> row = rows.get(index);
            if (isBlankRow(row)) {
                continue;
            }
            ChangeRow change = parseChangeRow(row, expectedSequence);
            String identity = change.dataClass + "\u0000" + change.resourceId
                    + "\u0000" + change.revision;
            if (!identities.add(identity)) {
                throw new ReconnectCoordinator.TransportException(
                        "protocol_error",
                        "Workspace Changes contains duplicate canonical revision identity"
                );
            }
            parsed.add(change);
            expectedSequence += 1;
        }

        long lastSequence = parsed.isEmpty() ? 0 : parsed.get(parsed.size() - 1).sequence;
        if (current > lastSequence) {
            throw new ReconnectCoordinator.TransportException(
                    "protocol_error",
                    "Workspace change cursor is ahead of the verified projection"
            );
        }

        ArrayList<OfflineSyncStateStore.ResourceSnapshot> snapshots = new ArrayList<>();
        long next = current;
        for (ChangeRow change : parsed) {
            if (change.sequence <= current) {
                continue;
            }
            if (snapshots.size() >= limit) {
                break;
            }
            snapshots.add(
                    new OfflineSyncStateStore.ResourceSnapshot(
                            change.dataClass,
                            change.resourceId,
                            change.revision,
                            change.canonicalPayload.getBytes(StandardCharsets.UTF_8)
                    )
            );
            next = change.sequence;
        }

        boolean moreAvailable = lastSequence > next;
        String nextCursor = formatCursor(next);
        return ReconnectCoordinator.ChangePage.verified(
                cursor,
                nextCursor,
                moreAvailable,
                Collections.unmodifiableList(snapshots)
        );
    }

    private List<List<Object>> readValidatedTable(
            String table,
            List<String> headers,
            int maximumRows
    ) throws ReconnectCoordinator.TransportException {
        final List<List<Object>> rows;
        try {
            rows = gateway.readTable(table);
        } catch (GatewayException exc) {
            throw gatewayFailure("workspace_read_failed", exc);
        }
        if (rows == null || rows.isEmpty()) {
            throw new ReconnectCoordinator.TransportException(
                    "protocol_error",
                    "Workspace " + table + " table is missing its header row"
            );
        }
        if (rows.size() > maximumRows + 1) {
            throw new ReconnectCoordinator.TransportException(
                    "protocol_error",
                    "Workspace " + table + " table exceeds bounded transport row limit"
            );
        }
        List<Object> header = rows.get(0);
        if (header == null || header.size() != headers.size()) {
            throw new ReconnectCoordinator.TransportException(
                    "protocol_error",
                    "Workspace " + table + " headers are invalid"
            );
        }
        for (int index = 0; index < headers.size(); index++) {
            if (!headers.get(index).equals(stringCell(header, index))) {
                throw new ReconnectCoordinator.TransportException(
                        "protocol_error",
                        "Workspace " + table + " headers are invalid"
                );
            }
        }
        return rows;
    }

    private static List<RemoteCommandRow> commandRows(
            List<List<Object>> table,
            CommandMaterial local
    ) throws ReconnectCoordinator.TransportException {
        ArrayList<RemoteCommandRow> matches = new ArrayList<>();
        for (int index = 1; index < table.size(); index++) {
            List<Object> row = table.get(index);
            if (isBlankRow(row)) {
                continue;
            }
            String commandId = stringCell(row, 0).trim();
            if (!local.commandId.equals(commandId)) {
                continue;
            }
            RemoteCommandRow parsed = parseCommandRow(row);
            if (!local.sameLogicalMaterial(parsed.material)) {
                throw new ReconnectCoordinator.TransportException(
                        "protocol_error",
                        "Workspace contains duplicate command_id with different material"
                );
            }
            matches.add(parsed);
        }
        return matches;
    }

    private static RemoteCommandRow parseCommandRow(List<Object> row)
            throws ReconnectCoordinator.TransportException {
        String commandId = requiredId(stringCell(row, 0), "command_id");
        String subjectId = requiredId(stringCell(row, 1), "subject_id");
        String dataClass = requiredDataClass(stringCell(row, 2));
        String action = requiredText(stringCell(row, 3), "action");
        int apiMajor = requiredInt(cell(row, 4), 1, Integer.MAX_VALUE, "api_major");
        String schemaVersion = requiredText(stringCell(row, 5), "schema_version");
        String resourceId = requiredId(stringCell(row, 6), "resource_id");
        String payload = canonicalObject(stringCell(row, 7), "payload_json");
        String idempotencyKey = requiredId(stringCell(row, 8), "idempotency_key");
        long expectedRevision = requiredLong(
                cell(row, 9),
                0,
                Long.MAX_VALUE,
                "expected_revision"
        );
        String status = requiredText(stringCell(row, 11), "status");
        if (!"pending".equals(status) && !"succeeded".equals(status) && !"failed".equals(status)) {
            throw protocol("Workspace command status is invalid");
        }

        return new RemoteCommandRow(
                new CommandMaterial(
                        commandId,
                        subjectId,
                        dataClass,
                        action,
                        apiMajor,
                        schemaVersion,
                        resourceId,
                        payload,
                        idempotencyKey,
                        expectedRevision
                ),
                status,
                stringCell(row, 12),
                stringCell(row, 14).trim(),
                stringCell(row, 15).trim()
        );
    }

    private static ReconnectCoordinator.RemoteCommandState reduceCommandRows(
            CommandMaterial local,
            List<RemoteCommandRow> rows
    ) throws ReconnectCoordinator.TransportException {
        ParsedSuccess success = null;
        RemoteFailure failure = null;
        boolean pending = false;

        for (RemoteCommandRow row : rows) {
            if ("pending".equals(row.status)) {
                if (!row.resultJson.trim().isEmpty()
                        || !row.errorCode.isEmpty()
                        || !row.errorMessage.isEmpty()) {
                    throw protocol("pending Workspace command contains terminal material");
                }
                pending = true;
                continue;
            }
            if ("succeeded".equals(row.status)) {
                if (!row.errorCode.isEmpty() || !row.errorMessage.isEmpty()) {
                    throw protocol("succeeded Workspace command contains error material");
                }
                ParsedSuccess candidate = parseSuccess(local, row.resultJson);
                if (success != null && !success.same(candidate)) {
                    throw protocol("duplicate Workspace command rows disagree on success readback");
                }
                success = candidate;
                continue;
            }

            if (!row.resultJson.trim().isEmpty()) {
                throw protocol("failed Workspace command contains success result material");
            }
            if (row.errorCode.isEmpty() || row.errorMessage.isEmpty()) {
                throw protocol("failed Workspace command is missing error material");
            }
            RemoteFailure candidate = new RemoteFailure(row.errorCode, row.errorMessage);
            if (failure != null && !failure.same(candidate)) {
                throw protocol("duplicate Workspace command rows disagree on terminal failure");
            }
            failure = candidate;
        }

        if (success != null && failure != null) {
            throw protocol("duplicate Workspace command rows contain contradictory terminal states");
        }
        if (success != null) {
            return ReconnectCoordinator.RemoteCommandState.succeeded(
                    local.commandId,
                    local.idempotencyKey,
                    Collections.singletonList(
                            new OfflineSyncStateStore.ResourceSnapshot(
                                    local.dataClass,
                                    local.resourceId,
                                    success.revision,
                                    success.canonicalPayload.getBytes(StandardCharsets.UTF_8)
                            )
                    )
            );
        }
        if (failure != null) {
            return ReconnectCoordinator.RemoteCommandState.failed(
                    local.commandId,
                    local.idempotencyKey,
                    failure.code,
                    failure.message
            );
        }
        if (!pending) {
            throw protocol("Workspace command rows have no durable state");
        }
        return ReconnectCoordinator.RemoteCommandState.pending(
                local.commandId,
                local.idempotencyKey
        );
    }

    private static ParsedSuccess parseSuccess(CommandMaterial local, String resultJson)
            throws ReconnectCoordinator.TransportException {
        JSONObject result = parseObject(resultJson, "result_json");
        String commandId = requiredId(jsonString(result, "command_id"), "result command_id");
        if (!local.commandId.equals(commandId)) {
            throw protocol("Workspace success result command_id does not match command row");
        }
        if (!jsonBoolean(result, "readback_verified")) {
            throw protocol("Workspace success result is missing verified canonical readback");
        }
        if (!result.has("record") || result.isNull("record")) {
            throw protocol("Workspace success result is missing canonical record");
        }

        final JSONObject record;
        try {
            record = result.getJSONObject("record");
        } catch (JSONException exc) {
            throw protocol("Workspace success result record is invalid", exc);
        }
        String dataClass = requiredDataClass(jsonString(record, "resource_type"));
        String resourceId = requiredId(jsonString(record, "resource_id"), "result resource_id");
        long revision = jsonLong(record, "revision", 1, Long.MAX_VALUE);
        String payload = canonicalJsonValue(jsonValue(record, "payload"), true);
        if (!local.dataClass.equals(dataClass)
                || !local.resourceId.equals(resourceId)
                || !local.canonicalPayload.equals(payload)) {
            throw protocol("Workspace success result record does not match submitted command");
        }
        return new ParsedSuccess(revision, payload);
    }

    private static ChangeRow parseChangeRow(List<Object> row, long expectedSequence)
            throws ReconnectCoordinator.TransportException {
        long sequence = requiredLong(
                cell(row, 0),
                1,
                Long.MAX_VALUE,
                "change_seq"
        );
        if (sequence != expectedSequence) {
            throw protocol("Workspace Changes sequence is not contiguous");
        }
        String changeId = requiredText(stringCell(row, 1), "change_id");
        if (!CHANGE_ID_PATTERN.matcher(changeId).matches()) {
            throw protocol("Workspace change_id is invalid");
        }
        String dataClass = requiredDataClass(stringCell(row, 2));
        String resourceId = requiredId(stringCell(row, 3), "resource_id");
        long revision = requiredLong(cell(row, 4), 1, Long.MAX_VALUE, "revision");
        String rawPayload = requiredText(stringCell(row, 5), "payload_json");
        String canonicalPayload = canonicalObject(rawPayload, "payload_json");
        if (!rawPayload.equals(canonicalPayload)) {
            throw protocol("Workspace Changes payload_json is not canonical JSON");
        }
        if (!booleanTrue(cell(row, 8))) {
            throw protocol("Workspace Changes row is not readback verified");
        }

        String expectedChangeId = changeId(dataClass, resourceId, revision, canonicalPayload);
        if (!expectedChangeId.equals(changeId)) {
            throw protocol("Workspace change_id does not match canonical row material");
        }
        return new ChangeRow(sequence, dataClass, resourceId, revision, canonicalPayload);
    }

    private static List<Object> commandAppendRow(CommandMaterial command, String submittedAt) {
        ArrayList<Object> row = new ArrayList<>(COMMAND_HEADERS.size());
        row.add(command.commandId);
        row.add(command.subjectId);
        row.add(command.dataClass);
        row.add(command.action);
        row.add(command.apiMajor);
        row.add(command.schemaVersion);
        row.add(command.resourceId);
        row.add(command.canonicalPayload);
        row.add(command.idempotencyKey);
        row.add(command.expectedRevision);
        row.add(requiredTextUnchecked(submittedAt, "submittedAt"));
        row.add("pending");
        row.add("");
        row.add("");
        row.add("");
        row.add("");
        return Collections.unmodifiableList(row);
    }

    private static void validateWorkspaceCommand(OfflineSyncStateStore.CommandIntent command)
            throws ReconnectCoordinator.TransportException {
        if (!"upsert".equals(command.action())) {
            throw new ReconnectCoordinator.TransportException(
                    "unsupported_command",
                    "Personal Workspace transport currently supports upsert commands only"
            );
        }
        if (command.expectedRevision() == null) {
            throw new ReconnectCoordinator.TransportException(
                    "unsupported_command",
                    "Personal Workspace upsert requires expected_revision"
            );
        }
        if (!ID_PATTERN.matcher(command.idempotencyKey()).matches()) {
            throw new ReconnectCoordinator.TransportException(
                    "unsupported_command",
                    "Personal Workspace idempotency_key must use canonical ID syntax"
            );
        }
        canonicalObject(
                new String(command.payload(), StandardCharsets.UTF_8),
                "command payload"
        );
    }

    private static long parseCursor(String cursor) throws ReconnectCoordinator.TransportException {
        if (cursor == null) {
            return 0;
        }
        if (!CURSOR_PATTERN.matcher(cursor).matches()) {
            throw protocol("Workspace synchronization cursor is invalid");
        }
        String raw = cursor.substring("mira-change-v1:".length());
        try {
            return Long.parseLong(raw);
        } catch (NumberFormatException exc) {
            throw protocol("Workspace synchronization cursor is out of range", exc);
        }
    }

    private static String formatCursor(long value) {
        return "mira-change-v1:" + value;
    }

    private static String changeId(
            String dataClass,
            String resourceId,
            long revision,
            String canonicalPayload
    ) throws ReconnectCoordinator.TransportException {
        String material = "{\"data_class\":" + JSONObject.quote(dataClass)
                + ",\"payload\":" + canonicalPayload
                + ",\"resource_id\":" + JSONObject.quote(resourceId)
                + ",\"revision\":" + revision + "}";
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hashed = digest.digest(material.getBytes(StandardCharsets.UTF_8));
            StringBuilder result = new StringBuilder(hashed.length * 2);
            for (byte item : hashed) {
                result.append(String.format(Locale.US, "%02x", item & 0xff));
            }
            return result.toString();
        } catch (NoSuchAlgorithmException exc) {
            throw new ReconnectCoordinator.TransportException(
                    "transport_crypto_unavailable",
                    "SHA-256 is unavailable for Workspace change verification",
                    exc
            );
        }
    }

    private static String canonicalObject(String raw, String field)
            throws ReconnectCoordinator.TransportException {
        if (raw == null || raw.isEmpty() || raw.length() > MAX_JSON_CHARS) {
            throw protocol(field + " is empty or exceeds bounded JSON size");
        }
        Object value = parseJson(raw, field);
        if (!(value instanceof JSONObject)) {
            throw protocol(field + " must be a JSON object");
        }
        return canonicalJsonValue(value, true);
    }

    private static JSONObject parseObject(String raw, String field)
            throws ReconnectCoordinator.TransportException {
        Object value = parseJson(raw, field);
        if (!(value instanceof JSONObject)) {
            throw protocol(field + " must be a JSON object");
        }
        return (JSONObject) value;
    }

    private static Object parseJson(String raw, String field)
            throws ReconnectCoordinator.TransportException {
        if (raw == null || raw.isEmpty() || raw.length() > MAX_JSON_CHARS) {
            throw protocol(field + " is empty or exceeds bounded JSON size");
        }
        try {
            JSONTokener tokener = new JSONTokener(raw);
            Object value = tokener.nextValue();
            if (tokener.nextClean() != 0) {
                throw protocol(field + " contains trailing JSON material");
            }
            return value;
        } catch (JSONException exc) {
            throw protocol(field + " is invalid JSON", exc);
        }
    }

    private static String canonicalJsonValue(Object value, boolean requireObject)
            throws ReconnectCoordinator.TransportException {
        if (requireObject && !(value instanceof JSONObject)) {
            throw protocol("canonical payload must be a JSON object");
        }
        if (value == null || value == JSONObject.NULL) {
            return "null";
        }
        if (value instanceof JSONObject) {
            JSONObject object = (JSONObject) value;
            ArrayList<String> keys = new ArrayList<>();
            Iterator<String> iterator = object.keys();
            while (iterator.hasNext()) {
                keys.add(iterator.next());
            }
            Collections.sort(keys);
            StringBuilder result = new StringBuilder("{");
            for (int index = 0; index < keys.size(); index++) {
                if (index > 0) result.append(',');
                String key = keys.get(index);
                result.append(JSONObject.quote(key)).append(':');
                try {
                    result.append(canonicalJsonValue(object.get(key), false));
                } catch (JSONException exc) {
                    throw protocol("cannot read JSON object member", exc);
                }
            }
            return result.append('}').toString();
        }
        if (value instanceof JSONArray) {
            JSONArray array = (JSONArray) value;
            StringBuilder result = new StringBuilder("[");
            for (int index = 0; index < array.length(); index++) {
                if (index > 0) result.append(',');
                try {
                    result.append(canonicalJsonValue(array.get(index), false));
                } catch (JSONException exc) {
                    throw protocol("cannot read JSON array member", exc);
                }
            }
            return result.append(']').toString();
        }
        if (value instanceof String) {
            return JSONObject.quote((String) value);
        }
        if (value instanceof Boolean) {
            return ((Boolean) value) ? "true" : "false";
        }
        if (value instanceof Number) {
            try {
                return JSONObject.numberToString((Number) value);
            } catch (JSONException exc) {
                throw protocol("JSON number is invalid", exc);
            }
        }
        throw protocol("JSON value type is unsupported");
    }

    private static Object jsonValue(JSONObject object, String field)
            throws ReconnectCoordinator.TransportException {
        try {
            if (!object.has(field)) {
                throw protocol("JSON result is missing " + field);
            }
            return object.get(field);
        } catch (JSONException exc) {
            throw protocol("JSON result field is invalid: " + field, exc);
        }
    }

    private static String jsonString(JSONObject object, String field)
            throws ReconnectCoordinator.TransportException {
        Object value = jsonValue(object, field);
        if (!(value instanceof String)) {
            throw protocol("JSON result field must be text: " + field);
        }
        return (String) value;
    }

    private static boolean jsonBoolean(JSONObject object, String field)
            throws ReconnectCoordinator.TransportException {
        Object value = jsonValue(object, field);
        if (!(value instanceof Boolean)) {
            throw protocol("JSON result field must be boolean: " + field);
        }
        return (Boolean) value;
    }

    private static long jsonLong(JSONObject object, String field, long minimum, long maximum)
            throws ReconnectCoordinator.TransportException {
        Object value = jsonValue(object, field);
        return requiredLong(value, minimum, maximum, field);
    }

    private static String requiredId(String value, String field)
            throws ReconnectCoordinator.TransportException {
        String text = requiredText(value, field);
        if (!ID_PATTERN.matcher(text).matches()) {
            throw protocol("Workspace " + field + " is invalid");
        }
        return text;
    }

    private static String requiredDataClass(String value)
            throws ReconnectCoordinator.TransportException {
        String text = requiredText(value, "data_class");
        if (!DATA_CLASS_PATTERN.matcher(text).matches()) {
            throw protocol("Workspace data_class is invalid");
        }
        return text;
    }

    private static String requiredText(String value, String field)
            throws ReconnectCoordinator.TransportException {
        if (value == null || value.isEmpty() || !value.equals(value.trim())) {
            throw protocol("Workspace " + field + " must be non-empty trimmed text");
        }
        return value;
    }

    private static String requiredTextUnchecked(String value, String field) {
        if (value == null || value.isEmpty() || !value.equals(value.trim())) {
            throw new IllegalArgumentException(field + " must be non-empty trimmed text");
        }
        return value;
    }

    private static int requiredInt(
            Object value,
            int minimum,
            int maximum,
            String field
    ) throws ReconnectCoordinator.TransportException {
        long parsed = requiredLong(value, minimum, maximum, field);
        return (int) parsed;
    }

    private static long requiredLong(
            Object value,
            long minimum,
            long maximum,
            String field
    ) throws ReconnectCoordinator.TransportException {
        final long parsed;
        if (value instanceof Byte || value instanceof Short || value instanceof Integer || value instanceof Long) {
            parsed = ((Number) value).longValue();
        } else if (value instanceof Float || value instanceof Double) {
            double raw = ((Number) value).doubleValue();
            if (Double.isNaN(raw) || Double.isInfinite(raw) || raw != Math.rint(raw)) {
                throw protocol("Workspace " + field + " must be an integer");
            }
            parsed = (long) raw;
        } else {
            String raw = String.valueOf(value == null ? "" : value).trim();
            try {
                parsed = Long.parseLong(raw);
            } catch (NumberFormatException exc) {
                throw protocol("Workspace " + field + " must be an integer", exc);
            }
        }
        if (parsed < minimum || parsed > maximum) {
            throw protocol("Workspace " + field + " is outside allowed range");
        }
        return parsed;
    }

    private static boolean booleanTrue(Object value) {
        if (Boolean.TRUE.equals(value)) {
            return true;
        }
        return "TRUE".equals(value);
    }

    private static Object cell(List<Object> row, int index) {
        if (row == null || index < 0 || index >= row.size()) {
            return "";
        }
        Object value = row.get(index);
        return value == null ? "" : value;
    }

    private static String stringCell(List<Object> row, int index) {
        return String.valueOf(cell(row, index));
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

    private static ReconnectCoordinator.TransportException gatewayFailure(
            String code,
            GatewayException exc
    ) {
        return new ReconnectCoordinator.TransportException(code, exc.getMessage(), exc);
    }

    private static ReconnectCoordinator.TransportException transportFailure(
            GatewayException appendFailure,
            ReconnectCoordinator.TransportException readFailure
    ) {
        return new ReconnectCoordinator.TransportException(
                "workspace_append_outcome_unknown",
                "Workspace command append outcome is ambiguous and readback failed: "
                        + readFailure.getMessage(),
                appendFailure
        );
    }

    private static ReconnectCoordinator.TransportException protocol(String message) {
        return new ReconnectCoordinator.TransportException("protocol_error", message);
    }

    private static ReconnectCoordinator.TransportException protocol(String message, Throwable cause) {
        return new ReconnectCoordinator.TransportException("protocol_error", message, cause);
    }

    private static List<String> immutableList(String... values) {
        ArrayList<String> result = new ArrayList<>(values.length);
        Collections.addAll(result, values);
        return Collections.unmodifiableList(result);
    }

    /** Narrow future provider seam. Implementations own Google authorization and spreadsheet ID. */
    public interface SheetsGateway {
        List<List<Object>> readTable(String tableName) throws GatewayException;

        void appendRow(String tableName, List<Object> row) throws GatewayException;
    }

    /** Provider/network failure from the concrete Google Sheets adapter. */
    public static class GatewayException extends Exception {
        public GatewayException(String message) {
            super(requiredTextUnchecked(message, "message"));
        }

        public GatewayException(String message, Throwable cause) {
            super(requiredTextUnchecked(message, "message"), cause);
        }
    }

    interface TimestampSource {
        String now();
    }

    private static final class SystemTimestampSource implements TimestampSource {
        @Override
        public String now() {
            SimpleDateFormat format = new SimpleDateFormat(
                    "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'",
                    Locale.US
            );
            format.setTimeZone(TimeZone.getTimeZone("UTC"));
            return format.format(new Date());
        }
    }

    private static final class CommandMaterial {
        final String commandId;
        final String subjectId;
        final String dataClass;
        final String action;
        final int apiMajor;
        final String schemaVersion;
        final String resourceId;
        final String canonicalPayload;
        final String idempotencyKey;
        final long expectedRevision;

        CommandMaterial(
                String commandId,
                String subjectId,
                String dataClass,
                String action,
                int apiMajor,
                String schemaVersion,
                String resourceId,
                String canonicalPayload,
                String idempotencyKey,
                long expectedRevision
        ) {
            this.commandId = commandId;
            this.subjectId = subjectId;
            this.dataClass = dataClass;
            this.action = action;
            this.apiMajor = apiMajor;
            this.schemaVersion = schemaVersion;
            this.resourceId = resourceId;
            this.canonicalPayload = canonicalPayload;
            this.idempotencyKey = idempotencyKey;
            this.expectedRevision = expectedRevision;
        }

        static CommandMaterial fromIntent(OfflineSyncStateStore.CommandIntent command)
                throws ReconnectCoordinator.TransportException {
            return new CommandMaterial(
                    command.commandId(),
                    command.subjectId(),
                    command.dataClass(),
                    command.action(),
                    command.apiMajor(),
                    command.schemaVersion(),
                    command.resourceId(),
                    canonicalObject(
                            new String(command.payload(), StandardCharsets.UTF_8),
                            "command payload"
                    ),
                    command.idempotencyKey(),
                    Objects.requireNonNull(command.expectedRevision(), "expectedRevision")
            );
        }

        boolean sameLogicalMaterial(CommandMaterial other) {
            return commandId.equals(other.commandId)
                    && subjectId.equals(other.subjectId)
                    && dataClass.equals(other.dataClass)
                    && action.equals(other.action)
                    && apiMajor == other.apiMajor
                    && schemaVersion.equals(other.schemaVersion)
                    && resourceId.equals(other.resourceId)
                    && canonicalPayload.equals(other.canonicalPayload)
                    && idempotencyKey.equals(other.idempotencyKey)
                    && expectedRevision == other.expectedRevision;
        }
    }

    private static final class RemoteCommandRow {
        final CommandMaterial material;
        final String status;
        final String resultJson;
        final String errorCode;
        final String errorMessage;

        RemoteCommandRow(
                CommandMaterial material,
                String status,
                String resultJson,
                String errorCode,
                String errorMessage
        ) {
            this.material = material;
            this.status = status;
            this.resultJson = resultJson;
            this.errorCode = errorCode;
            this.errorMessage = errorMessage;
        }
    }

    private static final class ParsedSuccess {
        final long revision;
        final String canonicalPayload;

        ParsedSuccess(long revision, String canonicalPayload) {
            this.revision = revision;
            this.canonicalPayload = canonicalPayload;
        }

        boolean same(ParsedSuccess other) {
            return revision == other.revision && canonicalPayload.equals(other.canonicalPayload);
        }
    }

    private static final class RemoteFailure {
        final String code;
        final String message;

        RemoteFailure(String code, String message) {
            this.code = code;
            this.message = message;
        }

        boolean same(RemoteFailure other) {
            return code.equals(other.code) && message.equals(other.message);
        }
    }

    private static final class ChangeRow {
        final long sequence;
        final String dataClass;
        final String resourceId;
        final long revision;
        final String canonicalPayload;

        ChangeRow(
                long sequence,
                String dataClass,
                String resourceId,
                long revision,
                String canonicalPayload
        ) {
            this.sequence = sequence;
            this.dataClass = dataClass;
            this.resourceId = resourceId;
            this.revision = revision;
            this.canonicalPayload = canonicalPayload;
        }
    }
}
