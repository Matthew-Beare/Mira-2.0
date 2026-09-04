package com.mira.client.core.sync;

import java.util.Objects;

/**
 * Provider-neutral Android read surface over verified canonical change synchronization.
 *
 * <p>The local snapshot store remains a nonauthoritative cache. This reader reports a resource as
 * fresh only after a read-only refresh proves that the current verified remote change projection is
 * exhausted. If another verified page remains, cached material is deliberately not returned as
 * fresh even when the requested resource is already present locally.</p>
 */
public final class CanonicalResourceReader {
    private static final int DEFAULT_CHANGE_LIMIT = 128;

    private final OfflineSyncStateStore stateStore;
    private final ReconnectCoordinator coordinator;

    public CanonicalResourceReader(
            OfflineSyncStateStore stateStore,
            ReconnectCoordinator.Transport transport
    ) {
        this(
                Objects.requireNonNull(stateStore, "stateStore"),
                new ReconnectCoordinator(
                        stateStore,
                        Objects.requireNonNull(transport, "transport")
                )
        );
    }

    CanonicalResourceReader(
            OfflineSyncStateStore stateStore,
            ReconnectCoordinator coordinator
    ) {
        this.stateStore = Objects.requireNonNull(stateStore, "stateStore");
        this.coordinator = Objects.requireNonNull(coordinator, "coordinator");
    }

    public synchronized ReadResult refreshAndRead(String dataClass, String resourceId) {
        return refreshAndRead(dataClass, resourceId, DEFAULT_CHANGE_LIMIT);
    }

    /**
     * Performs one bounded read-only refresh and returns the requested resource only when fresh.
     *
     * <p>Callers receiving {@link Status#MORE_REMOTE_CHANGES} may repeat the same request. Each pass
     * advances only after verified snapshots are durably stored. Pending local commands are not
     * reconciled or submitted by this read path.</p>
     */
    public synchronized ReadResult refreshAndRead(
            String dataClass,
            String resourceId,
            int changeLimit
    ) {
        try {
            // Validate lookup identity and local-state readability before making a provider call.
            // The cached result is intentionally discarded because it may not yet be fresh.
            stateStore.snapshot(dataClass, resourceId);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return ReadResult.localFailure(exc.getMessage());
        }

        ReconnectCoordinator.ReconnectResult refresh =
                coordinator.refreshChangesOnly(changeLimit);

        if (refresh.status() == ReconnectCoordinator.Status.MORE_REMOTE_CHANGES) {
            return ReadResult.moreRemoteChanges(refresh.cursor());
        }
        if (refresh.status() == ReconnectCoordinator.Status.TRANSPORT_FAILURE) {
            return ReadResult.transportFailure(refresh.errorCode(), refresh.message());
        }
        if (refresh.status() == ReconnectCoordinator.Status.PROTOCOL_FAILURE) {
            return ReadResult.protocolFailure(refresh.message());
        }
        if (refresh.status() == ReconnectCoordinator.Status.LOCAL_FAILURE) {
            return ReadResult.localFailure(refresh.message());
        }
        if (refresh.status() != ReconnectCoordinator.Status.COMPLETE) {
            return ReadResult.protocolFailure(
                    "read-only refresh returned unexpected status: " + refresh.status()
            );
        }

        final OfflineSyncStateStore.ResourceSnapshot snapshot;
        try {
            snapshot = stateStore.snapshot(dataClass, resourceId);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return ReadResult.localFailure(exc.getMessage());
        }
        if (snapshot == null) {
            return ReadResult.freshMissing(refresh.cursor());
        }
        return ReadResult.freshFound(snapshot, refresh.cursor());
    }

    public enum Status {
        FRESH_FOUND,
        FRESH_MISSING,
        MORE_REMOTE_CHANGES,
        TRANSPORT_FAILURE,
        PROTOCOL_FAILURE,
        LOCAL_FAILURE
    }

    /** Immutable freshness-qualified read result. */
    public static final class ReadResult {
        private final Status status;
        private final OfflineSyncStateStore.ResourceSnapshot snapshot;
        private final String cursor;
        private final String errorCode;
        private final String message;

        private ReadResult(
                Status status,
                OfflineSyncStateStore.ResourceSnapshot snapshot,
                String cursor,
                String errorCode,
                String message
        ) {
            this.status = Objects.requireNonNull(status, "status");
            this.snapshot = copySnapshot(snapshot);
            this.cursor = cursor;
            this.errorCode = errorCode;
            this.message = message;
        }

        static ReadResult freshFound(
                OfflineSyncStateStore.ResourceSnapshot snapshot,
                String cursor
        ) {
            return new ReadResult(
                    Status.FRESH_FOUND,
                    Objects.requireNonNull(snapshot, "snapshot"),
                    requireCursor(cursor),
                    null,
                    null
            );
        }

        static ReadResult freshMissing(String cursor) {
            return new ReadResult(
                    Status.FRESH_MISSING,
                    null,
                    requireCursor(cursor),
                    null,
                    null
            );
        }

        static ReadResult moreRemoteChanges(String cursor) {
            return new ReadResult(
                    Status.MORE_REMOTE_CHANGES,
                    null,
                    requireCursor(cursor),
                    null,
                    "more verified remote changes must be consumed before freshness can be claimed"
            );
        }

        static ReadResult transportFailure(String code, String message) {
            return new ReadResult(
                    Status.TRANSPORT_FAILURE,
                    null,
                    null,
                    requireText(code, "code"),
                    requireText(message, "message")
            );
        }

        static ReadResult protocolFailure(String message) {
            return new ReadResult(
                    Status.PROTOCOL_FAILURE,
                    null,
                    null,
                    "protocol_error",
                    requireText(message, "message")
            );
        }

        static ReadResult localFailure(String message) {
            return new ReadResult(
                    Status.LOCAL_FAILURE,
                    null,
                    null,
                    "local_state_error",
                    requireText(message, "message")
            );
        }

        public Status status() {
            return status;
        }

        public OfflineSyncStateStore.ResourceSnapshot snapshot() {
            return copySnapshot(snapshot);
        }

        public String cursor() {
            return cursor;
        }

        public String errorCode() {
            return errorCode;
        }

        public String message() {
            return message;
        }

        private static OfflineSyncStateStore.ResourceSnapshot copySnapshot(
                OfflineSyncStateStore.ResourceSnapshot value
        ) {
            if (value == null) {
                return null;
            }
            return new OfflineSyncStateStore.ResourceSnapshot(
                    value.dataClass(),
                    value.resourceId(),
                    value.revision(),
                    value.payload()
            );
        }

        private static String requireCursor(String value) {
            return requireText(value, "cursor");
        }

        private static String requireText(String value, String field) {
            if (value == null || value.trim().isEmpty() || !value.equals(value.trim())) {
                throw new IllegalArgumentException(field + " must be non-empty trimmed text");
            }
            return value;
        }
    }
}
