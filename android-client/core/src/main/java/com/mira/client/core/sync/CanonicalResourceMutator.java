package com.mira.client.core.sync;

import java.util.Objects;

/**
 * Provider-neutral Android mutation facade over the durable offline queue and reconnect contract.
 *
 * <p>This class does not mutate canonical state directly. It durably enqueues one exact upsert
 * intent, drives the already-verified queued execution boundary, and exposes applied success only
 * after the exact command has a durable acknowledgement tombstone created from verified canonical
 * readback. The returned snapshot remains a nonauthoritative local copy of canonical state.</p>
 */
public final class CanonicalResourceMutator {
    private static final int FULL_COMMAND_LIMIT = 128;
    private static final int CHANGE_LIMIT = 128;

    private final OfflineSyncStateStore stateStore;
    private final ReconnectCoordinator coordinator;

    public CanonicalResourceMutator(
            OfflineSyncStateStore stateStore,
            ReconnectCoordinator coordinator
    ) {
        this.stateStore = Objects.requireNonNull(stateStore, "stateStore");
        this.coordinator = Objects.requireNonNull(coordinator, "coordinator");
    }

    /**
     * Durably stages and reconciles one exact canonical upsert command.
     *
     * <p>The caller owns stable command and idempotency identities. Retrying this method with the
     * exact same command is safe; changing material under an existing command ID fails closed in
     * {@link OfflineSyncStateStore} before provider I/O.</p>
     */
    public synchronized MutationResult mutate(OfflineSyncStateStore.CommandIntent command) {
        OfflineSyncStateStore.CommandIntent exact =
                Objects.requireNonNull(command, "command");
        validateSupportedIntent(exact);

        final OfflineSyncStateStore.EnqueueResult initialEnqueue;
        try {
            initialEnqueue = stateStore.enqueue(exact);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MutationResult.localFailure(
                    exact.commandId(),
                    null,
                    null,
                    "local_enqueue_failed",
                    exc.getMessage()
            );
        }

        if (initialEnqueue == OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED) {
            return appliedFromVerifiedCache(exact, initialEnqueue);
        }

        final ReconnectCoordinator.ReconnectResult reconnect =
                coordinator.reconnect(FULL_COMMAND_LIMIT, CHANGE_LIMIT);

        // Reuse the store's exact-material idempotency rules as a durable disposition probe.
        // Normal paths do not write here: acknowledged commands return ALREADY_ACKNOWLEDGED and
        // pending commands return ALREADY_PENDING. If state disappeared unexpectedly, ENQUEUED
        // safely restores the command and we fail closed rather than fabricating success.
        final OfflineSyncStateStore.EnqueueResult disposition;
        try {
            disposition = stateStore.enqueue(exact);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MutationResult.localFailure(
                    exact.commandId(),
                    reconnect.commandId(),
                    initialEnqueue,
                    "local_disposition_failed",
                    exc.getMessage()
            );
        }

        if (disposition == OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED) {
            return appliedFromVerifiedCache(exact, initialEnqueue);
        }
        if (disposition == OfflineSyncStateStore.EnqueueResult.ENQUEUED) {
            return MutationResult.localFailure(
                    exact.commandId(),
                    reconnect.commandId(),
                    initialEnqueue,
                    "local_command_state_lost",
                    "exact command disappeared during reconciliation and was safely re-enqueued"
            );
        }

        return pendingResult(exact, initialEnqueue, reconnect);
    }

    private MutationResult appliedFromVerifiedCache(
            OfflineSyncStateStore.CommandIntent command,
            OfflineSyncStateStore.EnqueueResult initialEnqueue
    ) {
        final OfflineSyncStateStore.ResourceSnapshot snapshot;
        try {
            snapshot = stateStore.snapshot(command.dataClass(), command.resourceId());
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return MutationResult.localFailure(
                    command.commandId(),
                    null,
                    initialEnqueue,
                    "verified_result_unavailable",
                    exc.getMessage()
            );
        }
        if (snapshot == null) {
            return MutationResult.localFailure(
                    command.commandId(),
                    null,
                    initialEnqueue,
                    "verified_result_missing",
                    "acknowledged command has no cached verified canonical snapshot"
            );
        }
        Long expectedRevision = command.expectedRevision();
        if (expectedRevision == null || snapshot.revision() <= expectedRevision) {
            return MutationResult.localFailure(
                    command.commandId(),
                    null,
                    initialEnqueue,
                    "verified_result_revision_invalid",
                    "acknowledged command does not have a newer verified canonical revision"
            );
        }
        return MutationResult.applied(command.commandId(), initialEnqueue, snapshot);
    }

    private static MutationResult pendingResult(
            OfflineSyncStateStore.CommandIntent command,
            OfflineSyncStateStore.EnqueueResult initialEnqueue,
            ReconnectCoordinator.ReconnectResult reconnect
    ) {
        String remoteCommandId = reconnect.commandId();
        if (remoteCommandId != null && !command.commandId().equals(remoteCommandId)) {
            return MutationResult.blockedByEarlierCommand(
                    command.commandId(),
                    remoteCommandId,
                    initialEnqueue,
                    reconnect.errorCode(),
                    reconnect.message()
            );
        }

        switch (reconnect.status()) {
            case WAITING_REMOTE:
                return MutationResult.waitingRemote(command.commandId(), initialEnqueue);
            case REMOTE_FAILURE:
                return MutationResult.remoteFailure(
                        command.commandId(),
                        initialEnqueue,
                        reconnect.errorCode(),
                        reconnect.message()
                );
            case TRANSPORT_FAILURE:
                return MutationResult.transportFailure(
                        command.commandId(),
                        initialEnqueue,
                        reconnect.errorCode(),
                        reconnect.message()
                );
            case PROTOCOL_FAILURE:
                return MutationResult.protocolFailure(
                        command.commandId(),
                        initialEnqueue,
                        reconnect.message()
                );
            case LOCAL_FAILURE:
                return MutationResult.localFailure(
                        command.commandId(),
                        null,
                        initialEnqueue,
                        reconnect.errorCode(),
                        reconnect.message()
                );
            case COMPLETE:
            case MORE_PENDING:
            case MORE_REMOTE_CHANGES:
            default:
                return MutationResult.protocolFailure(
                        command.commandId(),
                        initialEnqueue,
                        "reconnect completed without acknowledging the exact mutation command"
                );
        }
    }

    private static void validateSupportedIntent(OfflineSyncStateStore.CommandIntent command) {
        if (!"upsert".equals(command.action())) {
            throw new IllegalArgumentException("canonical mutation facade supports upsert only");
        }
        if (command.expectedRevision() == null) {
            throw new IllegalArgumentException(
                    "canonical mutation facade requires expected_revision"
            );
        }
    }

    public enum Status {
        APPLIED,
        WAITING_REMOTE,
        BLOCKED_BY_EARLIER_COMMAND,
        REMOTE_FAILURE,
        TRANSPORT_FAILURE,
        PROTOCOL_FAILURE,
        LOCAL_FAILURE
    }

    /** Stable mutation result suitable for later UI/state mapping without provider material. */
    public static final class MutationResult {
        private final Status status;
        private final String commandId;
        private final String blockingCommandId;
        private final OfflineSyncStateStore.EnqueueResult enqueueResult;
        private final OfflineSyncStateStore.ResourceSnapshot canonicalSnapshot;
        private final String errorCode;
        private final String message;

        private MutationResult(
                Status status,
                String commandId,
                String blockingCommandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                OfflineSyncStateStore.ResourceSnapshot canonicalSnapshot,
                String errorCode,
                String message
        ) {
            this.status = Objects.requireNonNull(status, "status");
            this.commandId = Objects.requireNonNull(commandId, "commandId");
            this.blockingCommandId = blockingCommandId;
            this.enqueueResult = enqueueResult;
            this.canonicalSnapshot = canonicalSnapshot == null
                    ? null
                    : copySnapshot(canonicalSnapshot);
            this.errorCode = errorCode;
            this.message = message;
        }

        static MutationResult applied(
                String commandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                OfflineSyncStateStore.ResourceSnapshot snapshot
        ) {
            return new MutationResult(
                    Status.APPLIED,
                    commandId,
                    null,
                    enqueueResult,
                    Objects.requireNonNull(snapshot, "snapshot"),
                    null,
                    null
            );
        }

        static MutationResult waitingRemote(
                String commandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult
        ) {
            return new MutationResult(
                    Status.WAITING_REMOTE,
                    commandId,
                    null,
                    enqueueResult,
                    null,
                    null,
                    "canonical mutation is queued and remote processing is not terminal"
            );
        }

        static MutationResult blockedByEarlierCommand(
                String commandId,
                String blockingCommandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                String errorCode,
                String message
        ) {
            return new MutationResult(
                    Status.BLOCKED_BY_EARLIER_COMMAND,
                    commandId,
                    Objects.requireNonNull(blockingCommandId, "blockingCommandId"),
                    enqueueResult,
                    null,
                    errorCode,
                    message == null
                            ? "an earlier FIFO command blocks this mutation"
                            : message
            );
        }

        static MutationResult remoteFailure(
                String commandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                String errorCode,
                String message
        ) {
            return new MutationResult(
                    Status.REMOTE_FAILURE,
                    commandId,
                    null,
                    enqueueResult,
                    null,
                    errorCode,
                    message
            );
        }

        static MutationResult transportFailure(
                String commandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                String errorCode,
                String message
        ) {
            return new MutationResult(
                    Status.TRANSPORT_FAILURE,
                    commandId,
                    null,
                    enqueueResult,
                    null,
                    errorCode,
                    message
            );
        }

        static MutationResult protocolFailure(
                String commandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                String message
        ) {
            return new MutationResult(
                    Status.PROTOCOL_FAILURE,
                    commandId,
                    null,
                    enqueueResult,
                    null,
                    "protocol_error",
                    message
            );
        }

        static MutationResult localFailure(
                String commandId,
                String blockingCommandId,
                OfflineSyncStateStore.EnqueueResult enqueueResult,
                String errorCode,
                String message
        ) {
            return new MutationResult(
                    Status.LOCAL_FAILURE,
                    commandId,
                    blockingCommandId,
                    enqueueResult,
                    null,
                    errorCode,
                    message
            );
        }

        public Status status() {
            return status;
        }

        public String commandId() {
            return commandId;
        }

        public String blockingCommandId() {
            return blockingCommandId;
        }

        public OfflineSyncStateStore.EnqueueResult enqueueResult() {
            return enqueueResult;
        }

        public OfflineSyncStateStore.ResourceSnapshot canonicalSnapshot() {
            return canonicalSnapshot == null ? null : copySnapshot(canonicalSnapshot);
        }

        public String errorCode() {
            return errorCode;
        }

        public String message() {
            return message;
        }

        private static OfflineSyncStateStore.ResourceSnapshot copySnapshot(
                OfflineSyncStateStore.ResourceSnapshot snapshot
        ) {
            return new OfflineSyncStateStore.ResourceSnapshot(
                    snapshot.dataClass(),
                    snapshot.resourceId(),
                    snapshot.revision(),
                    snapshot.payload()
            );
        }
    }
}
