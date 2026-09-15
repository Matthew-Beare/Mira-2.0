package com.mira.client.core.sync;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
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
 * Append-event extension for the existing Google Workspace queued transport.
 *
 * <p>Upserts and verified Changes remain owned by {@link GoogleWorkspaceTransport}. This wrapper
 * intercepts only API-001 {@code append_event} intents and maps their event metadata into the
 * existing 16-column Commands table through a strict payload envelope. No live-sheet migration is
 * required, and event success is acknowledged only after the serialized Apps Script worker reports
 * exact verified Event readback.</p>
 */
public final class GoogleWorkspaceEventTransport implements ReconnectCoordinator.Transport {
    private static final String ACTION_APPEND_EVENT = "append_event";
    private static final int MAX_REMOTE_COMMAND_ROWS = 4096;
    private static final int MAX_JSON_CHARS = 512 * 1024;
    private static final Pattern ID_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$");
    private static final Pattern DATA_CLASS_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$");
    private static final Set<String> EVENT_ENVELOPE_KEYS = immutableSet(
            "event_id", "event_type", "payload"
    );
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

    private final GoogleWorkspaceTransport delegate;
    private final GoogleWorkspaceTransport.SheetsGateway gateway;
    private final TimestampSource timestampSource;

    public GoogleWorkspaceEventTransport(GoogleWorkspaceTransport.SheetsGateway gateway) {
        this(gateway, new GoogleWorkspaceTransport(gateway), new SystemTimestampSource());
    }

    GoogleWorkspaceEventTransport(
            GoogleWorkspaceTransport.SheetsGateway gateway,
            GoogleWorkspaceTransport delegate,
            TimestampSource timestampSource
    ) {
        this.gateway = Objects.requireNonNull(gateway, "gateway");
        this.delegate = Objects.requireNonNull(delegate, "delegate");
        this.timestampSource = Objects.requireNonNull(timestampSource, "timestampSource");
    }

    @Override
    public ReconnectCoordinator.RemoteCommandState reconcileCommand(
            OfflineSyncStateStore.CommandIntent command
    ) throws ReconnectCoordinator.TransportException {
        Objects.requireNonNull(command, "command");
        if (!ACTION_APPEND_EVENT.equals(command.action())) {
            return delegate.reconcileCommand(command);
        }
        EventCommandMaterial local = EventCommandMaterial.fromIntent(command);
        List<List<Object>> rows = readCommandTable();
        List<RemoteRow> matches = matchingRows(rows, local);
        if (matches.isEmpty()) {
            List<Object> append = appendRow(local, timestampSource.now());
            try {
                gateway.appendRow(GoogleWorkspaceTransport.COMMANDS_TABLE, append);
            } catch (GoogleWorkspaceTransport.GatewayException appendFailure) {
                try {
                    rows = readCommandTable();
                    matches = matchingRows(rows, local);
                } catch (ReconnectCoordinator.TransportException readFailure) {
                    throw new ReconnectCoordinator.TransportException(
                            "workspace_read_failed",
                            "Workspace event append was ambiguous and readback also failed",
                            readFailure
                    );
                }
                if (matches.isEmpty()) {
                    throw new ReconnectCoordinator.TransportException(
                            "command_append_failed",
                            "Workspace event command append failed",
                            appendFailure
                    );
                }
            }
            if (matches.isEmpty()) {
                rows = readCommandTable();
                matches = matchingRows(rows, local);
            }
            if (matches.isEmpty()) {
                throw protocol("Workspace event command append did not read back exact material");
            }
        }
        return reduce(local, matches);
    }

    @Override
    public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit)
            throws ReconnectCoordinator.TransportException {
        return delegate.readChanges(cursor, limit);
    }

    private List<List<Object>> readCommandTable() throws ReconnectCoordinator.TransportException {
        final List<List<Object>> rows;
        try {
            rows = gateway.readTable(GoogleWorkspaceTransport.COMMANDS_TABLE);
        } catch (GoogleWorkspaceTransport.GatewayException exc) {
            throw new ReconnectCoordinator.TransportException(
                    "workspace_read_failed",
                    "Workspace Commands read failed",
                    exc
            );
        }
        if (rows == null || rows.isEmpty()) {
            throw protocol("Workspace Commands table is missing its header row");
        }
        if (rows.size() > MAX_REMOTE_COMMAND_ROWS + 1) {
            throw protocol("Workspace Commands table exceeds bounded row limit");
        }
        List<Object> header = rows.get(0);
        if (header == null || header.size() != COMMAND_HEADERS.size()) {
            throw protocol("Workspace Commands headers are invalid");
        }
        for (int index = 0; index < COMMAND_HEADERS.size(); index++) {
            if (!COMMAND_HEADERS.get(index).equals(stringCell(header, index))) {
                throw protocol("Workspace Commands headers are invalid");
            }
        }
        return rows;
    }

    private static List<RemoteRow> matchingRows(
            List<List<Object>> table,
            EventCommandMaterial local
    ) throws ReconnectCoordinator.TransportException {
        ArrayList<RemoteRow> matches = new ArrayList<>();
        for (int index = 1; index < table.size(); index++) {
            List<Object> row = table.get(index);
            if (isBlankRow(row)) {
                continue;
            }
            if (!local.commandId.equals(stringCell(row, 0).trim())) {
                continue;
            }
            RemoteRow parsed = parseRow(row);
            if (!local.same(parsed.material)) {
                throw protocol("Workspace contains duplicate event command_id with different material");
            }
            matches.add(parsed);
        }
        return matches;
    }

    private static RemoteRow parseRow(List<Object> row)
            throws ReconnectCoordinator.TransportException {
        String commandId = requiredId(stringCell(row, 0), "command_id");
        String subjectId = requiredId(stringCell(row, 1), "subject_id");
        String dataClass = requiredDataClass(stringCell(row, 2));
        String action = requiredText(stringCell(row, 3), "action");
        if (!ACTION_APPEND_EVENT.equals(action)) {
            throw protocol("event command row has non-event action");
        }
        int apiMajor = requiredInt(cell(row, 4), "api_major");
        String schemaVersion = requiredText(stringCell(row, 5), "schema_version");
        String resourceId = requiredId(stringCell(row, 6), "resource_id");
        EventEnvelope envelope = parseEnvelope(stringCell(row, 7));
        String idempotencyKey = requiredId(stringCell(row, 8), "idempotency_key");
        Long expectedRevision = optionalRevision(cell(row, 9));
        String status = requiredText(stringCell(row, 11), "status");
        if (!"pending".equals(status) && !"succeeded".equals(status) && !"failed".equals(status)) {
            throw protocol("Workspace event command status is invalid");
        }
        return new RemoteRow(
                new EventCommandMaterial(
                        commandId,
                        subjectId,
                        dataClass,
                        apiMajor,
                        schemaVersion,
                        resourceId,
                        envelope.canonicalPayload,
                        idempotencyKey,
                        expectedRevision,
                        envelope.eventId,
                        envelope.eventType
                ),
                status,
                stringCell(row, 12),
                stringCell(row, 14).trim(),
                stringCell(row, 15).trim()
        );
    }

    private static ReconnectCoordinator.RemoteCommandState reduce(
            EventCommandMaterial local,
            List<RemoteRow> rows
    ) throws ReconnectCoordinator.TransportException {
        ParsedSuccess success = null;
        RemoteFailure failure = null;
        boolean pending = false;
        for (RemoteRow row : rows) {
            if ("pending".equals(row.status)) {
                if (!row.resultJson.trim().isEmpty()
                        || !row.errorCode.isEmpty()
                        || !row.errorMessage.isEmpty()) {
                    throw protocol("pending Workspace event command contains terminal material");
                }
                pending = true;
                continue;
            }
            if ("succeeded".equals(row.status)) {
                if (!row.errorCode.isEmpty() || !row.errorMessage.isEmpty()) {
                    throw protocol("succeeded Workspace event command contains error material");
                }
                ParsedSuccess candidate = parseSuccess(local, row.resultJson);
                if (success != null && !success.same(candidate)) {
                    throw protocol("duplicate Workspace event rows disagree on success readback");
                }
                success = candidate;
                continue;
            }
            if (!row.resultJson.trim().isEmpty()) {
                throw protocol("failed Workspace event command contains success material");
            }
            if (row.errorCode.isEmpty() || row.errorMessage.isEmpty()) {
                throw protocol("failed Workspace event command is missing error material");
            }
            RemoteFailure candidate = new RemoteFailure(row.errorCode, row.errorMessage);
            if (failure != null && !failure.same(candidate)) {
                throw protocol("duplicate Workspace event rows disagree on terminal failure");
            }
            failure = candidate;
        }
        if (success != null && failure != null) {
            throw protocol("duplicate Workspace event rows contain contradictory terminal states");
        }
        if (success != null) {
            return ReconnectCoordinator.RemoteCommandState.succeeded(
                    local.commandId,
                    local.idempotencyKey,
                    Collections.<OfflineSyncStateStore.ResourceSnapshot>emptyList()
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
            throw protocol("Workspace event command rows have no durable state");
        }
        return ReconnectCoordinator.RemoteCommandState.pending(local.commandId, local.idempotencyKey);
    }

    private static ParsedSuccess parseSuccess(EventCommandMaterial local, String resultJson)
            throws ReconnectCoordinator.TransportException {
        JSONObject result = parseObject(resultJson, "result_json");
        if (!local.commandId.equals(requiredId(jsonString(result, "command_id"), "result command_id"))) {
            throw protocol("Workspace event result command_id does not match command row");
        }
        if (!jsonBoolean(result, "readback_verified")) {
            throw protocol("Workspace event success is missing verified canonical readback");
        }
        if (result.has("record") && !result.isNull("record")) {
            throw protocol("Workspace event success must not contain a Resource record");
        }
        final JSONObject event;
        try {
            event = result.getJSONObject("event");
        } catch (JSONException exc) {
            throw protocol("Workspace event success is missing canonical event readback", exc);
        }
        String eventId = requiredId(jsonString(event, "event_id"), "result event_id");
        String streamType = requiredDataClass(jsonString(event, "stream_type"));
        String streamId = requiredId(jsonString(event, "stream_id"), "result stream_id");
        String eventType = requiredText(jsonString(event, "event_type"), "result event_type");
        long streamRevision = jsonLong(event, "stream_revision");
        String canonicalPayload = canonicalJsonValue(jsonValue(event, "payload"), true);
        if (!local.eventId.equals(eventId)
                || !local.dataClass.equals(streamType)
                || !local.resourceId.equals(streamId)
                || !local.eventType.equals(eventType)
                || !local.canonicalPayload.equals(canonicalPayload)) {
            throw protocol("Workspace event success does not match submitted event command");
        }
        if (local.expectedRevision != null && streamRevision != local.expectedRevision + 1) {
            throw protocol("Workspace event success stream revision does not follow expected revision");
        }
        return new ParsedSuccess(streamRevision, canonicalPayload);
    }

    private static List<Object> appendRow(EventCommandMaterial local, String submittedAt) {
        ArrayList<Object> row = new ArrayList<>(16);
        row.add(local.commandId);
        row.add(local.subjectId);
        row.add(local.dataClass);
        row.add(ACTION_APPEND_EVENT);
        row.add(local.apiMajor);
        row.add(local.schemaVersion);
        row.add(local.resourceId);
        row.add(local.transportEnvelope());
        row.add(local.idempotencyKey);
        row.add(local.expectedRevision == null ? "" : local.expectedRevision);
        row.add(submittedAt);
        row.add("pending");
        row.add("");
        row.add("");
        row.add("");
        row.add("");
        return row;
    }

    private static EventEnvelope parseEnvelope(String raw)
            throws ReconnectCoordinator.TransportException {
        JSONObject envelope = parseObject(raw, "event payload envelope");
        HashSet<String> keys = new HashSet<>();
        Iterator<String> iterator = envelope.keys();
        while (iterator.hasNext()) {
            keys.add(iterator.next());
        }
        if (!keys.equals(EVENT_ENVELOPE_KEYS)) {
            throw protocol("Workspace event payload envelope fields are invalid");
        }
        String eventId = requiredId(jsonString(envelope, "event_id"), "event_id");
        String eventType = requiredText(jsonString(envelope, "event_type"), "event_type");
        String payload = canonicalJsonValue(jsonValue(envelope, "payload"), true);
        return new EventEnvelope(eventId, eventType, payload);
    }

    private static JSONObject parseObject(String value, String field)
            throws ReconnectCoordinator.TransportException {
        String text = requiredText(value, field);
        if (text.length() > MAX_JSON_CHARS) {
            throw protocol(field + " exceeds bounded JSON size");
        }
        try {
            Object parsed = new JSONTokener(text).nextValue();
            if (!(parsed instanceof JSONObject)) {
                throw protocol(field + " must be a JSON object");
            }
            return (JSONObject) parsed;
        } catch (JSONException exc) {
            throw protocol(field + " is invalid JSON", exc);
        }
    }

    private static String canonicalPayload(byte[] payload)
            throws ReconnectCoordinator.TransportException {
        if (payload == null || payload.length == 0) {
            throw protocol("append_event payload must not be empty");
        }
        final String text;
        try {
            text = StandardCharsets.UTF_8.newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(payload))
                    .toString();
        } catch (CharacterCodingException exc) {
            throw protocol("append_event payload is not valid UTF-8", exc);
        }
        JSONObject object = parseObject(text, "append_event payload");
        return canonicalJsonValue(object, true);
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
            StringBuilder out = new StringBuilder("{");
            for (int index = 0; index < keys.size(); index++) {
                if (index > 0) out.append(',');
                String key = keys.get(index);
                out.append(JSONObject.quote(key)).append(':');
                try {
                    out.append(canonicalJsonValue(object.get(key), false));
                } catch (JSONException exc) {
                    throw protocol("canonical JSON object is malformed", exc);
                }
            }
            return out.append('}').toString();
        }
        if (value instanceof JSONArray) {
            JSONArray array = (JSONArray) value;
            StringBuilder out = new StringBuilder("[");
            for (int index = 0; index < array.length(); index++) {
                if (index > 0) out.append(',');
                try {
                    out.append(canonicalJsonValue(array.get(index), false));
                } catch (JSONException exc) {
                    throw protocol("canonical JSON array is malformed", exc);
                }
            }
            return out.append(']').toString();
        }
        if (value instanceof String) {
            return JSONObject.quote((String) value);
        }
        if (value instanceof Boolean) {
            return value.toString();
        }
        if (value instanceof Number) {
            try {
                return JSONObject.numberToString((Number) value);
            } catch (JSONException exc) {
                throw protocol("canonical JSON number is invalid", exc);
            }
        }
        throw protocol("canonical JSON contains unsupported value type");
    }

    private static Object jsonValue(JSONObject object, String key)
            throws ReconnectCoordinator.TransportException {
        try {
            if (!object.has(key) || object.isNull(key)) {
                throw protocol("missing JSON field: " + key);
            }
            return object.get(key);
        } catch (JSONException exc) {
            throw protocol("invalid JSON field: " + key, exc);
        }
    }

    private static String jsonString(JSONObject object, String key)
            throws ReconnectCoordinator.TransportException {
        Object value = jsonValue(object, key);
        if (!(value instanceof String)) {
            throw protocol("JSON field must be text: " + key);
        }
        return (String) value;
    }

    private static boolean jsonBoolean(JSONObject object, String key)
            throws ReconnectCoordinator.TransportException {
        Object value = jsonValue(object, key);
        if (!(value instanceof Boolean)) {
            throw protocol("JSON field must be boolean: " + key);
        }
        return (Boolean) value;
    }

    private static long jsonLong(JSONObject object, String key)
            throws ReconnectCoordinator.TransportException {
        Object value = jsonValue(object, key);
        long parsed = requiredLong(value, key);
        if (parsed < 1) {
            throw protocol(key + " must be positive");
        }
        return parsed;
    }

    private static Long optionalRevision(Object value)
            throws ReconnectCoordinator.TransportException {
        if (value == null || stringCell(Collections.singletonList(value), 0).trim().isEmpty()) {
            return null;
        }
        long parsed = requiredLong(value, "expected_revision");
        if (parsed < 0) {
            throw protocol("expected_revision must be non-negative or blank");
        }
        return parsed;
    }

    private static long requiredLong(Object value, String field)
            throws ReconnectCoordinator.TransportException {
        if (value instanceof Number) {
            double number = ((Number) value).doubleValue();
            long parsed = ((Number) value).longValue();
            if (!Double.isFinite(number) || number != parsed) {
                throw protocol(field + " must be an integer");
            }
            return parsed;
        }
        String text = requiredText(String.valueOf(value), field);
        try {
            return Long.parseLong(text);
        } catch (NumberFormatException exc) {
            throw protocol(field + " must be an integer", exc);
        }
    }

    private static int requiredInt(Object value, String field)
            throws ReconnectCoordinator.TransportException {
        long parsed = requiredLong(value, field);
        if (parsed < 1 || parsed > Integer.MAX_VALUE) {
            throw protocol(field + " must be a positive integer");
        }
        return (int) parsed;
    }

    private static String requiredId(String value, String field)
            throws ReconnectCoordinator.TransportException {
        String text = requiredText(value, field);
        if (!ID_PATTERN.matcher(text).matches()) {
            throw protocol(field + " is invalid");
        }
        return text;
    }

    private static String requiredDataClass(String value)
            throws ReconnectCoordinator.TransportException {
        String text = requiredText(value, "data_class");
        if (!DATA_CLASS_PATTERN.matcher(text).matches()) {
            throw protocol("data_class is invalid");
        }
        return text;
    }

    private static String requiredText(String value, String field)
            throws ReconnectCoordinator.TransportException {
        if (value == null || value.trim().isEmpty() || !value.equals(value.trim())) {
            throw protocol(field + " must be non-empty trimmed text");
        }
        return value;
    }

    private static Object cell(List<Object> row, int index) {
        if (row == null || index >= row.size()) {
            return "";
        }
        Object value = row.get(index);
        return value == null ? "" : value;
    }

    private static String stringCell(List<Object> row, int index) {
        Object value = cell(row, index);
        return value instanceof String ? (String) value : String.valueOf(value);
    }

    private static boolean isBlankRow(List<Object> row) {
        if (row == null) return true;
        for (Object value : row) {
            if (value != null && !String.valueOf(value).trim().isEmpty()) return false;
        }
        return true;
    }

    private static ReconnectCoordinator.TransportException protocol(String message) {
        return new ReconnectCoordinator.TransportException("protocol_error", message);
    }

    private static ReconnectCoordinator.TransportException protocol(String message, Throwable cause) {
        return new ReconnectCoordinator.TransportException("protocol_error", message, cause);
    }

    private static List<String> immutableList(String... values) {
        ArrayList<String> result = new ArrayList<>();
        Collections.addAll(result, values);
        return Collections.unmodifiableList(result);
    }

    private static Set<String> immutableSet(String... values) {
        HashSet<String> result = new HashSet<>();
        Collections.addAll(result, values);
        return Collections.unmodifiableSet(result);
    }

    interface TimestampSource {
        String now();
    }

    private static final class SystemTimestampSource implements TimestampSource {
        @Override
        public String now() {
            SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US);
            format.setTimeZone(TimeZone.getTimeZone("UTC"));
            return format.format(new Date());
        }
    }

    private static final class EventCommandMaterial {
        final String commandId;
        final String subjectId;
        final String dataClass;
        final int apiMajor;
        final String schemaVersion;
        final String resourceId;
        final String canonicalPayload;
        final String idempotencyKey;
        final Long expectedRevision;
        final String eventId;
        final String eventType;

        EventCommandMaterial(
                String commandId,
                String subjectId,
                String dataClass,
                int apiMajor,
                String schemaVersion,
                String resourceId,
                String canonicalPayload,
                String idempotencyKey,
                Long expectedRevision,
                String eventId,
                String eventType
        ) {
            this.commandId = commandId;
            this.subjectId = subjectId;
            this.dataClass = dataClass;
            this.apiMajor = apiMajor;
            this.schemaVersion = schemaVersion;
            this.resourceId = resourceId;
            this.canonicalPayload = canonicalPayload;
            this.idempotencyKey = idempotencyKey;
            this.expectedRevision = expectedRevision;
            this.eventId = eventId;
            this.eventType = eventType;
        }

        static EventCommandMaterial fromIntent(OfflineSyncStateStore.CommandIntent command)
                throws ReconnectCoordinator.TransportException {
            if (!ACTION_APPEND_EVENT.equals(command.action())) {
                throw protocol("event transport received non-event command");
            }
            return new EventCommandMaterial(
                    requiredId(command.commandId(), "command_id"),
                    requiredId(command.subjectId(), "subject_id"),
                    requiredDataClass(command.dataClass()),
                    requiredInt(command.apiMajor(), "api_major"),
                    requiredText(command.schemaVersion(), "schema_version"),
                    requiredId(command.resourceId(), "resource_id"),
                    canonicalPayload(command.payload()),
                    requiredId(command.idempotencyKey(), "idempotency_key"),
                    command.expectedRevision(),
                    requiredId(command.eventId(), "event_id"),
                    requiredText(command.eventType(), "event_type")
            );
        }

        boolean same(EventCommandMaterial other) {
            return commandId.equals(other.commandId)
                    && subjectId.equals(other.subjectId)
                    && dataClass.equals(other.dataClass)
                    && apiMajor == other.apiMajor
                    && schemaVersion.equals(other.schemaVersion)
                    && resourceId.equals(other.resourceId)
                    && canonicalPayload.equals(other.canonicalPayload)
                    && idempotencyKey.equals(other.idempotencyKey)
                    && Objects.equals(expectedRevision, other.expectedRevision)
                    && eventId.equals(other.eventId)
                    && eventType.equals(other.eventType);
        }

        String transportEnvelope() {
            return "{\"event_id\":" + JSONObject.quote(eventId)
                    + ",\"event_type\":" + JSONObject.quote(eventType)
                    + ",\"payload\":" + canonicalPayload + "}";
        }
    }

    private static final class EventEnvelope {
        final String eventId;
        final String eventType;
        final String canonicalPayload;

        EventEnvelope(String eventId, String eventType, String canonicalPayload) {
            this.eventId = eventId;
            this.eventType = eventType;
            this.canonicalPayload = canonicalPayload;
        }
    }

    private static final class RemoteRow {
        final EventCommandMaterial material;
        final String status;
        final String resultJson;
        final String errorCode;
        final String errorMessage;

        RemoteRow(
                EventCommandMaterial material,
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
}
