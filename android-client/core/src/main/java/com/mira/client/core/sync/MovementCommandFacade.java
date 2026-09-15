package com.mira.client.core.sync;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/**
 * Explicit MOVE-001 Android facade over the existing encrypted FIFO command queue.
 *
 * <p>A move is a two-command saga matching canonical {@code MovementService} semantics: append the
 * inventory observation event first, then project the resulting observed state with an ordinary
 * {@code inventory_state} upsert. Both commands are durably staged in the same
 * {@link OfflineSyncStateStore}; passive capture never calls this class.</p>
 *
 * <p>The facade never claims a distributed transaction. If the event lands and projection later
 * conflicts, the event remains durable history and the projection command remains pending/failed
 * for explicit recovery. Applied success is reported only when both exact commands have durable
 * verified acknowledgements and the cached verified projection readback exactly matches MOVE-001
 * material.</p>
 */
public final class MovementCommandFacade {
    private static final String DATA_CLASS = "inventory_state";
    private static final String ACTION_EVENT = "append_event";
    private static final String ACTION_UPSERT = "upsert";
    private static final String EVENT_TYPE = "updated";
    private static final String EVENT_KIND = "inventory_observation";
    private static final int MOVEMENT_SCHEMA_VERSION = 1;
    private static final int INVENTORY_SCHEMA_VERSION = 1;
    private static final int API_MAJOR = 1;
    private static final String API_SCHEMA_VERSION = "mira-api-1";
    private static final int COMMAND_LIMIT = 2;
    private static final int CHANGE_LIMIT = 128;

    private static final Set<String> INVENTORY_KEYS = setOf(
            "schema_version",
            "entity_uuid",
            "participation_state",
            "intended_location_id",
            "observed_location_id",
            "observed_at",
            "note"
    );

    private final OfflineSyncStateStore stateStore;
    private final ReconnectCoordinator coordinator;

    public MovementCommandFacade(
            OfflineSyncStateStore stateStore,
            ReconnectCoordinator coordinator
    ) {
        this.stateStore = Objects.requireNonNull(stateStore, "stateStore");
        this.coordinator = Objects.requireNonNull(coordinator, "coordinator");
    }

    /**
     * Durably stages/reconciles one explicit movement operation.
     *
     * <p>The request contains the exact prior canonical inventory material used to build the event
     * and projection. Callers should obtain it from a freshness-qualified canonical read. Exact
     * retry of the same request is safe across process restarts; changed material under the same
     * event identity fails closed in the local queue or canonical worker.</p>
     */
    public synchronized MoveResult move(MoveRequest request) {
        MoveRequest exact = Objects.requireNonNull(request, "request");
        CommandPair pair = commandPair(exact);

        final OfflineSyncStateStore.EnqueueResult eventInitial;
        final OfflineSyncStateStore.EnqueueResult projectionInitial;
        try {
            eventInitial = stateStore.enqueue(pair.eventCommand);
            projectionInitial = stateStore.enqueue(pair.projectionCommand);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MoveResult.failure(
                    Status.LOCAL_FAILURE,
                    pair,
                    null,
                    null,
                    null,
                    "local_enqueue_failed",
                    exc.getMessage()
            );
        }

        if (eventInitial == OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED
                && projectionInitial == OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED) {
            return appliedFromVerifiedCache(pair, eventInitial, projectionInitial);
        }

        ReconnectCoordinator.ReconnectResult reconnect =
                coordinator.reconnect(COMMAND_LIMIT, CHANGE_LIMIT);

        final OfflineSyncStateStore.EnqueueResult eventDisposition;
        final OfflineSyncStateStore.EnqueueResult projectionDisposition;
        try {
            eventDisposition = stateStore.enqueue(pair.eventCommand);
            projectionDisposition = stateStore.enqueue(pair.projectionCommand);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MoveResult.failure(
                    Status.LOCAL_FAILURE,
                    pair,
                    eventInitial,
                    projectionInitial,
                    reconnect.commandId(),
                    "local_disposition_failed",
                    exc.getMessage()
            );
        }

        if (eventDisposition == OfflineSyncStateStore.EnqueueResult.ENQUEUED
                || projectionDisposition == OfflineSyncStateStore.EnqueueResult.ENQUEUED) {
            return MoveResult.failure(
                    Status.LOCAL_FAILURE,
                    pair,
                    eventInitial,
                    projectionInitial,
                    reconnect.commandId(),
                    "local_command_state_lost",
                    "movement command disappeared during reconciliation and was safely re-enqueued"
            );
        }

        boolean eventAck = eventDisposition == OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED;
        boolean projectionAck = projectionDisposition
                == OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED;
        if (projectionAck && !eventAck) {
            return MoveResult.failure(
                    Status.PROTOCOL_FAILURE,
                    pair,
                    eventInitial,
                    projectionInitial,
                    reconnect.commandId(),
                    "protocol_error",
                    "movement projection was acknowledged before its event"
            );
        }
        if (eventAck && projectionAck) {
            return appliedFromVerifiedCache(pair, eventInitial, projectionInitial);
        }

        String activeCommandId = eventAck
                ? pair.projectionCommand.commandId()
                : pair.eventCommand.commandId();
        final String firstPending;
        try {
            firstPending = firstPendingCommandId();
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MoveResult.failure(
                    Status.LOCAL_FAILURE,
                    pair,
                    eventInitial,
                    projectionInitial,
                    reconnect.commandId(),
                    "local_pending_read_failed",
                    exc.getMessage()
            );
        }
        if (firstPending != null && !activeCommandId.equals(firstPending)) {
            return MoveResult.blocked(
                    pair,
                    eventInitial,
                    projectionInitial,
                    firstPending,
                    reconnect.errorCode(),
                    reconnect.message()
            );
        }

        Status waitingStatus = eventAck ? Status.WAITING_PROJECTION : Status.WAITING_EVENT;
        switch (reconnect.status()) {
            case WAITING_REMOTE:
            case MORE_PENDING:
            case MORE_REMOTE_CHANGES:
                return MoveResult.waiting(
                        waitingStatus,
                        pair,
                        eventInitial,
                        projectionInitial,
                        reconnect.message()
                );
            case REMOTE_FAILURE:
                return MoveResult.failure(
                        Status.REMOTE_FAILURE,
                        pair,
                        eventInitial,
                        projectionInitial,
                        reconnect.commandId(),
                        reconnect.errorCode(),
                        reconnect.message()
                );
            case TRANSPORT_FAILURE:
                return MoveResult.failure(
                        Status.TRANSPORT_FAILURE,
                        pair,
                        eventInitial,
                        projectionInitial,
                        reconnect.commandId(),
                        reconnect.errorCode(),
                        reconnect.message()
                );
            case PROTOCOL_FAILURE:
                return MoveResult.failure(
                        Status.PROTOCOL_FAILURE,
                        pair,
                        eventInitial,
                        projectionInitial,
                        reconnect.commandId(),
                        "protocol_error",
                        reconnect.message()
                );
            case LOCAL_FAILURE:
                return MoveResult.failure(
                        Status.LOCAL_FAILURE,
                        pair,
                        eventInitial,
                        projectionInitial,
                        reconnect.commandId(),
                        reconnect.errorCode(),
                        reconnect.message()
                );
            case COMPLETE:
            default:
                return MoveResult.failure(
                        Status.PROTOCOL_FAILURE,
                        pair,
                        eventInitial,
                        projectionInitial,
                        reconnect.commandId(),
                        "protocol_error",
                        "reconnect completed without acknowledging both movement commands"
                );
        }
    }

    private MoveResult appliedFromVerifiedCache(
            CommandPair pair,
            OfflineSyncStateStore.EnqueueResult eventEnqueue,
            OfflineSyncStateStore.EnqueueResult projectionEnqueue
    ) {
        final OfflineSyncStateStore.ResourceSnapshot snapshot;
        try {
            snapshot = stateStore.snapshot(DATA_CLASS, pair.request.entityUuid());
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MoveResult.failure(
                    Status.LOCAL_FAILURE,
                    pair,
                    eventEnqueue,
                    projectionEnqueue,
                    null,
                    "verified_result_unavailable",
                    exc.getMessage()
            );
        }
        String mismatch = projectionMismatch(pair.request, snapshot);
        if (mismatch != null) {
            return MoveResult.failure(
                    Status.PROTOCOL_FAILURE,
                    pair,
                    eventEnqueue,
                    projectionEnqueue,
                    null,
                    "verified_projection_mismatch",
                    mismatch
            );
        }
        return MoveResult.applied(pair, eventEnqueue, projectionEnqueue, snapshot);
    }

    private String firstPendingCommandId() {
        List<OfflineSyncStateStore.QueuedCommand> pending = stateStore.pendingCommands(128);
        return pending.isEmpty() ? null : pending.get(0).command().commandId();
    }

    private static CommandPair commandPair(MoveRequest request) {
        String digest = sha256(request.eventId()).substring(0, 40);
        String eventCommandId = "movement-event-cmd-" + digest;
        String projectionCommandId = "movement-state-cmd-" + digest;
        String projectionIdempotencyKey = "movement-state-" + digest;

        OfflineSyncStateStore.CommandIntent event = new OfflineSyncStateStore.CommandIntent(
                eventCommandId,
                request.subjectId(),
                DATA_CLASS,
                ACTION_EVENT,
                API_MAJOR,
                API_SCHEMA_VERSION,
                request.entityUuid(),
                movementPayload(request).getBytes(StandardCharsets.UTF_8),
                request.eventIdempotencyKey(),
                null,
                request.eventId(),
                EVENT_TYPE
        );
        OfflineSyncStateStore.CommandIntent projection = new OfflineSyncStateStore.CommandIntent(
                projectionCommandId,
                request.subjectId(),
                DATA_CLASS,
                ACTION_UPSERT,
                API_MAJOR,
                API_SCHEMA_VERSION,
                request.entityUuid(),
                projectionPayload(request).getBytes(StandardCharsets.UTF_8),
                projectionIdempotencyKey,
                request.expectedInventoryRevision(),
                null,
                null
        );
        return new CommandPair(request, event, projection);
    }

    private static String movementPayload(MoveRequest request) {
        return "{"
                + "\"schema_version\":" + MOVEMENT_SCHEMA_VERSION
                + ",\"event_kind\":" + quote(EVENT_KIND)
                + ",\"event_id\":" + quote(request.eventId())
                + ",\"entity_uuid\":" + quote(request.entityUuid())
                + ",\"observed_location_id\":" + quote(request.destinationLocationId())
                + ",\"observed_at\":" + quote(request.observedAt())
                + ",\"source\":" + quote(request.source())
                + ",\"note\":" + nullableQuote(request.movementNote())
                + ",\"prior_inventory_revision\":" + request.expectedInventoryRevision()
                + ",\"prior_observed_location_id\":"
                + nullableQuote(request.priorObservedLocationId())
                + ",\"prior_observed_at\":" + nullableQuote(request.priorObservedAt())
                + ",\"prior_intended_location_id\":"
                + nullableQuote(request.priorIntendedLocationId())
                + ",\"prior_inventory_note\":" + nullableQuote(request.priorInventoryNote())
                + ",\"resulting_inventory_revision\":"
                + (request.expectedInventoryRevision() + 1)
                + "}";
    }

    private static String projectionPayload(MoveRequest request) {
        return "{"
                + "\"schema_version\":" + INVENTORY_SCHEMA_VERSION
                + ",\"entity_uuid\":" + quote(request.entityUuid())
                + ",\"participation_state\":\"tracked\""
                + ",\"intended_location_id\":"
                + nullableQuote(request.priorIntendedLocationId())
                + ",\"observed_location_id\":" + quote(request.destinationLocationId())
                + ",\"observed_at\":" + quote(request.observedAt())
                + ",\"note\":" + nullableQuote(request.priorInventoryNote())
                + "}";
    }

    private static String projectionMismatch(
            MoveRequest request,
            OfflineSyncStateStore.ResourceSnapshot snapshot
    ) {
        if (snapshot == null) {
            return "acknowledged movement projection has no cached verified canonical snapshot";
        }
        if (!DATA_CLASS.equals(snapshot.dataClass()) || !request.entityUuid().equals(snapshot.resourceId())) {
            return "verified movement snapshot identity does not match requested inventory state";
        }
        if (snapshot.revision() != request.expectedInventoryRevision() + 1) {
            return "verified movement snapshot revision does not equal expected projection revision";
        }
        final JSONObject payload;
        try {
            payload = new JSONObject(new String(snapshot.payload(), StandardCharsets.UTF_8));
        } catch (JSONException exc) {
            return "verified movement snapshot payload is invalid JSON";
        }
        if (!jsonKeys(payload).equals(INVENTORY_KEYS)) {
            return "verified movement snapshot fields do not match inventory_state schema";
        }
        try {
            if (payload.getInt("schema_version") != INVENTORY_SCHEMA_VERSION
                    || !request.entityUuid().equals(payload.getString("entity_uuid"))
                    || !"tracked".equals(payload.getString("participation_state"))
                    || !Objects.equals(
                            request.priorIntendedLocationId(),
                            nullableJsonString(payload, "intended_location_id")
                    )
                    || !request.destinationLocationId().equals(payload.getString("observed_location_id"))
                    || !request.observedAt().equals(payload.getString("observed_at"))
                    || !Objects.equals(
                            request.priorInventoryNote(),
                            nullableJsonString(payload, "note")
                    )) {
                return "verified movement snapshot material does not match requested projection";
            }
        } catch (JSONException exc) {
            return "verified movement snapshot payload has invalid field types";
        }
        return null;
    }

    private static String nullableJsonString(JSONObject object, String key) throws JSONException {
        return object.isNull(key) ? null : object.getString(key);
    }

    private static Set<String> jsonKeys(JSONObject object) {
        HashSet<String> keys = new HashSet<>();
        Iterator<String> iterator = object.keys();
        while (iterator.hasNext()) keys.add(iterator.next());
        return keys;
    }

    private static Set<String> setOf(String... values) {
        HashSet<String> result = new HashSet<>();
        for (String value : values) result.add(value);
        return result;
    }

    private static String quote(String value) {
        return JSONObject.quote(value);
    }

    private static String nullableQuote(String value) {
        return value == null ? "null" : quote(value);
    }

    private static String sha256(String value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder(64);
            for (byte item : digest) out.append(String.format("%02x", item & 0xff));
            return out.toString();
        } catch (NoSuchAlgorithmException exc) {
            throw new IllegalStateException("SHA-256 unavailable", exc);
        }
    }

    private static String required(String value, String field, int maximum) {
        if (value == null || value.trim().isEmpty() || !value.equals(value.trim())) {
            throw new IllegalArgumentException(field + " must be non-empty trimmed text");
        }
        if (value.length() > maximum) {
            throw new IllegalArgumentException(field + " exceeds length limit");
        }
        return value;
    }

    private static String optional(String value, String field, int maximum) {
        if (value == null) return null;
        if (value.trim().isEmpty() || !value.equals(value.trim())) {
            throw new IllegalArgumentException(field + " must be null or non-empty trimmed text");
        }
        if (value.length() > maximum) {
            throw new IllegalArgumentException(field + " exceeds length limit");
        }
        return value;
    }

    public enum Status {
        APPLIED,
        WAITING_EVENT,
        WAITING_PROJECTION,
        BLOCKED_BY_EARLIER_COMMAND,
        REMOTE_FAILURE,
        TRANSPORT_FAILURE,
        PROTOCOL_FAILURE,
        LOCAL_FAILURE
    }

    /** Exact immutable movement material supplied by an explicit user/action surface. */
    public static final class MoveRequest {
        private final String subjectId;
        private final String entityUuid;
        private final String destinationLocationId;
        private final String observedAt;
        private final String source;
        private final String eventId;
        private final String eventIdempotencyKey;
        private final long expectedInventoryRevision;
        private final String priorObservedLocationId;
        private final String priorObservedAt;
        private final String priorIntendedLocationId;
        private final String priorInventoryNote;
        private final String movementNote;

        public MoveRequest(
                String subjectId,
                String entityUuid,
                String destinationLocationId,
                String observedAt,
                String source,
                String eventId,
                String eventIdempotencyKey,
                long expectedInventoryRevision,
                String priorObservedLocationId,
                String priorObservedAt,
                String priorIntendedLocationId,
                String priorInventoryNote,
                String movementNote
        ) {
            this.subjectId = required(subjectId, "subjectId", 128);
            this.entityUuid = required(entityUuid, "entityUuid", 128);
            this.destinationLocationId = required(destinationLocationId, "destinationLocationId", 128);
            this.observedAt = required(observedAt, "observedAt", 128);
            this.source = required(source, "source", 128);
            this.eventId = required(eventId, "eventId", 128);
            this.eventIdempotencyKey = required(eventIdempotencyKey, "eventIdempotencyKey", 128);
            if (expectedInventoryRevision < 1) {
                throw new IllegalArgumentException("expectedInventoryRevision must be positive");
            }
            this.expectedInventoryRevision = expectedInventoryRevision;
            this.priorObservedLocationId = optional(
                    priorObservedLocationId, "priorObservedLocationId", 128
            );
            this.priorObservedAt = optional(priorObservedAt, "priorObservedAt", 128);
            this.priorIntendedLocationId = optional(
                    priorIntendedLocationId, "priorIntendedLocationId", 128
            );
            this.priorInventoryNote = optional(priorInventoryNote, "priorInventoryNote", 4000);
            this.movementNote = optional(movementNote, "movementNote", 4000);
        }

        public String subjectId() { return subjectId; }
        public String entityUuid() { return entityUuid; }
        public String destinationLocationId() { return destinationLocationId; }
        public String observedAt() { return observedAt; }
        public String source() { return source; }
        public String eventId() { return eventId; }
        public String eventIdempotencyKey() { return eventIdempotencyKey; }
        public long expectedInventoryRevision() { return expectedInventoryRevision; }
        public String priorObservedLocationId() { return priorObservedLocationId; }
        public String priorObservedAt() { return priorObservedAt; }
        public String priorIntendedLocationId() { return priorIntendedLocationId; }
        public String priorInventoryNote() { return priorInventoryNote; }
        public String movementNote() { return movementNote; }
    }

    /** Stable movement outcome with no provider identifiers or credentials. */
    public static final class MoveResult {
        private final Status status;
        private final String eventCommandId;
        private final String projectionCommandId;
        private final String blockingCommandId;
        private final OfflineSyncStateStore.EnqueueResult eventEnqueueResult;
        private final OfflineSyncStateStore.EnqueueResult projectionEnqueueResult;
        private final OfflineSyncStateStore.ResourceSnapshot canonicalSnapshot;
        private final String errorCode;
        private final String message;

        private MoveResult(
                Status status,
                CommandPair pair,
                String blockingCommandId,
                OfflineSyncStateStore.EnqueueResult eventEnqueueResult,
                OfflineSyncStateStore.EnqueueResult projectionEnqueueResult,
                OfflineSyncStateStore.ResourceSnapshot canonicalSnapshot,
                String errorCode,
                String message
        ) {
            this.status = Objects.requireNonNull(status, "status");
            this.eventCommandId = pair.eventCommand.commandId();
            this.projectionCommandId = pair.projectionCommand.commandId();
            this.blockingCommandId = blockingCommandId;
            this.eventEnqueueResult = eventEnqueueResult;
            this.projectionEnqueueResult = projectionEnqueueResult;
            this.canonicalSnapshot = canonicalSnapshot == null ? null : new OfflineSyncStateStore.ResourceSnapshot(
                    canonicalSnapshot.dataClass(),
                    canonicalSnapshot.resourceId(),
                    canonicalSnapshot.revision(),
                    canonicalSnapshot.payload()
            );
            this.errorCode = errorCode;
            this.message = message;
        }

        static MoveResult applied(
                CommandPair pair,
                OfflineSyncStateStore.EnqueueResult eventEnqueue,
                OfflineSyncStateStore.EnqueueResult projectionEnqueue,
                OfflineSyncStateStore.ResourceSnapshot snapshot
        ) {
            return new MoveResult(
                    Status.APPLIED,
                    pair,
                    null,
                    eventEnqueue,
                    projectionEnqueue,
                    snapshot,
                    null,
                    null
            );
        }

        static MoveResult waiting(
                Status status,
                CommandPair pair,
                OfflineSyncStateStore.EnqueueResult eventEnqueue,
                OfflineSyncStateStore.EnqueueResult projectionEnqueue,
                String message
        ) {
            return new MoveResult(
                    status,
                    pair,
                    null,
                    eventEnqueue,
                    projectionEnqueue,
                    null,
                    null,
                    message
            );
        }

        static MoveResult blocked(
                CommandPair pair,
                OfflineSyncStateStore.EnqueueResult eventEnqueue,
                OfflineSyncStateStore.EnqueueResult projectionEnqueue,
                String blockingCommandId,
                String errorCode,
                String message
        ) {
            return new MoveResult(
                    Status.BLOCKED_BY_EARLIER_COMMAND,
                    pair,
                    blockingCommandId,
                    eventEnqueue,
                    projectionEnqueue,
                    null,
                    errorCode,
                    message
            );
        }

        static MoveResult failure(
                Status status,
                CommandPair pair,
                OfflineSyncStateStore.EnqueueResult eventEnqueue,
                OfflineSyncStateStore.EnqueueResult projectionEnqueue,
                String blockingCommandId,
                String errorCode,
                String message
        ) {
            return new MoveResult(
                    status,
                    pair,
                    blockingCommandId,
                    eventEnqueue,
                    projectionEnqueue,
                    null,
                    errorCode,
                    message
            );
        }

        public Status status() { return status; }
        public String eventCommandId() { return eventCommandId; }
        public String projectionCommandId() { return projectionCommandId; }
        public String blockingCommandId() { return blockingCommandId; }
        public OfflineSyncStateStore.EnqueueResult eventEnqueueResult() { return eventEnqueueResult; }
        public OfflineSyncStateStore.EnqueueResult projectionEnqueueResult() { return projectionEnqueueResult; }
        public OfflineSyncStateStore.ResourceSnapshot canonicalSnapshot() {
            return canonicalSnapshot == null ? null : new OfflineSyncStateStore.ResourceSnapshot(
                    canonicalSnapshot.dataClass(),
                    canonicalSnapshot.resourceId(),
                    canonicalSnapshot.revision(),
                    canonicalSnapshot.payload()
            );
        }
        public String errorCode() { return errorCode; }
        public String message() { return message; }
    }

    private static final class CommandPair {
        final MoveRequest request;
        final OfflineSyncStateStore.CommandIntent eventCommand;
        final OfflineSyncStateStore.CommandIntent projectionCommand;

        CommandPair(
                MoveRequest request,
                OfflineSyncStateStore.CommandIntent eventCommand,
                OfflineSyncStateStore.CommandIntent projectionCommand
        ) {
            this.request = request;
            this.eventCommand = eventCommand;
            this.projectionCommand = projectionCommand;
        }
    }
}
