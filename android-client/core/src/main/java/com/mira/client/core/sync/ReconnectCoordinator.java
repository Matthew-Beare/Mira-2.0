package com.mira.client.core.sync;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * Provider-neutral Android reconnect orchestration over durable local sync state.
 *
 * <p>The coordinator never talks to Google, Cloud Run, or any other provider directly. A concrete
 * {@link Transport} owns provider/managed authentication and remote I/O. This class only enforces
 * replay, verified-readback, and cursor ordering between that transport and
 * {@link OfflineSyncStateStore}.</p>
 *
 * <p>Submission is not acknowledgement. A local queued command is acknowledged only after the
 * transport reports terminal success for the exact command/idempotency identity with canonical
 * readback explicitly verified. Likewise, a synchronization cursor advances only after every
 * verified snapshot in the corresponding remote page has been durably persisted locally.</p>
 */
public final class ReconnectCoordinator {
    private static final int DEFAULT_COMMAND_LIMIT = 128;
    private static final int DEFAULT_CHANGE_LIMIT = 128;
    private static final int MAX_COMMAND_LIMIT = 128;
    private static final int MAX_CHANGE_LIMIT = 128;

    private final OfflineSyncStateStore stateStore;
    private final Transport transport;
    private final FaultInjector faultInjector;

    /** Creates the production coordinator with no fault injection. */
    public ReconnectCoordinator(OfflineSyncStateStore stateStore, Transport transport) {
        this(stateStore, transport, FaultInjector.NONE);
    }

    /** Package-private deterministic failure seam for JVM crash/retry tests. */
    ReconnectCoordinator(
            OfflineSyncStateStore stateStore,
            Transport transport,
            FaultInjector faultInjector
    ) {
        this.stateStore = Objects.requireNonNull(stateStore, "stateStore");
        this.transport = Objects.requireNonNull(transport, "transport");
        this.faultInjector = Objects.requireNonNull(faultInjector, "faultInjector");
    }

    /** Performs one bounded reconnect pass using the full local queue/change-page limits. */
    public synchronized ReconnectResult reconnect() {
        return reconnect(DEFAULT_COMMAND_LIMIT, DEFAULT_CHANGE_LIMIT);
    }

    /**
     * Performs one bounded reconnect pass.
     *
     * <p>Commands are reconciled in stable local FIFO order. The pass stops at the first remote
     * pending command, terminal remote command failure, protocol failure, transport failure, or
     * local persistence failure. Remote changes are requested only after every command returned in
     * this pass has reached verified terminal success. If more local commands remain because the
     * caller supplied a smaller command limit, the pass returns {@link Status#MORE_PENDING} without
     * advancing synchronization state.</p>
     */
    public synchronized ReconnectResult reconnect(int commandLimit, int changeLimit) {
        validateLimit(commandLimit, MAX_COMMAND_LIMIT, "commandLimit");
        validateLimit(changeLimit, MAX_CHANGE_LIMIT, "changeLimit");

        final List<OfflineSyncStateStore.QueuedCommand> pending;
        try {
            pending = stateStore.pendingCommands(commandLimit);
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return ReconnectResult.localFailure(null, 0, 0, exc.getMessage());
        }

        int acknowledged = 0;
        int snapshotsStored = 0;

        for (OfflineSyncStateStore.QueuedCommand queued : pending) {
            OfflineSyncStateStore.CommandIntent command = queued.command();
            final RemoteCommandState remote;
            try {
                remote = transport.reconcileCommand(command);
            } catch (TransportException exc) {
                return ReconnectResult.transportFailure(
                        command.commandId(),
                        acknowledged,
                        snapshotsStored,
                        exc.code(),
                        exc.getMessage()
                );
            }

            String protocolError = validateRemoteCommand(command, remote);
            if (protocolError != null) {
                return ReconnectResult.protocolFailure(
                        command.commandId(),
                        acknowledged,
                        snapshotsStored,
                        protocolError
                );
            }

            if (remote.status() == RemoteCommandStatus.PENDING) {
                return ReconnectResult.waitingRemote(
                        command.commandId(),
                        acknowledged,
                        snapshotsStored
                );
            }

            if (remote.status() == RemoteCommandStatus.FAILED) {
                return ReconnectResult.remoteFailure(
                        command.commandId(),
                        acknowledged,
                        snapshotsStored,
                        remote.errorCode(),
                        remote.errorMessage()
                );
            }

            try {
                for (OfflineSyncStateStore.ResourceSnapshot snapshot : remote.verifiedSnapshots()) {
                    stateStore.putSnapshot(snapshot);
                    snapshotsStored += 1;
                }
                faultInjector.afterVerifiedRemoteSuccess(command, remote);
                stateStore.acknowledge(command.commandId(), command.idempotencyKey());
                acknowledged += 1;
            } catch (OfflineSyncStateStore.OfflineStateException exc) {
                return ReconnectResult.localFailure(
                        command.commandId(),
                        acknowledged,
                        snapshotsStored,
                        exc.getMessage()
                );
            }
        }

        final int remaining;
        try {
            remaining = stateStore.pendingCount();
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return ReconnectResult.localFailure(null, acknowledged, snapshotsStored, exc.getMessage());
        }
        if (remaining > 0) {
            return ReconnectResult.morePending(acknowledged, snapshotsStored, remaining);
        }

        final String currentCursor;
        try {
            currentCursor = stateStore.cursor();
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return ReconnectResult.localFailure(null, acknowledged, snapshotsStored, exc.getMessage());
        }

        final ChangePage page;
        try {
            page = transport.readChanges(currentCursor, changeLimit);
        } catch (TransportException exc) {
            return ReconnectResult.transportFailure(
                    null,
                    acknowledged,
                    snapshotsStored,
                    exc.code(),
                    exc.getMessage()
            );
        }

        String pageError = validateChangePage(currentCursor, changeLimit, page);
        if (pageError != null) {
            return ReconnectResult.protocolFailure(
                    null,
                    acknowledged,
                    snapshotsStored,
                    pageError
            );
        }

        try {
            for (OfflineSyncStateStore.ResourceSnapshot snapshot : page.verifiedSnapshots()) {
                stateStore.putSnapshot(snapshot);
                snapshotsStored += 1;
            }
            faultInjector.afterChangeSnapshotsStored(page);
            stateStore.compareAndSetCursor(currentCursor, page.nextCursor());
        } catch (OfflineSyncStateStore.OfflineStateException exc) {
            return ReconnectResult.localFailure(null, acknowledged, snapshotsStored, exc.getMessage());
        }

        return ReconnectResult.complete(
                acknowledged,
                snapshotsStored,
                page.nextCursor()
        );
    }

    private static String validateRemoteCommand(
            OfflineSyncStateStore.CommandIntent command,
            RemoteCommandState remote
    ) {
        if (remote == null) {
            return "transport returned null command state";
        }
        if (!command.commandId().equals(remote.commandId())) {
            return "remote command_id does not match local command";
        }
        if (!command.idempotencyKey().equals(remote.idempotencyKey())) {
            return "remote idempotency_key does not match local command";
        }
        if (remote.status() == null) {
            return "remote command status is missing";
        }
        if (remote.status() == RemoteCommandStatus.SUCCEEDED) {
            if (!remote.readbackVerified()) {
                return "remote success is missing verified canonical readback";
            }
            if (remote.errorCode() != null || remote.errorMessage() != null) {
                return "remote success must not contain terminal error material";
            }
        } else if (remote.status() == RemoteCommandStatus.PENDING) {
            if (remote.readbackVerified()) {
                return "pending remote command cannot claim verified readback";
            }
            if (!remote.verifiedSnapshots().isEmpty()) {
                return "pending remote command cannot contain verified snapshots";
            }
            if (remote.errorCode() != null || remote.errorMessage() != null) {
                return "pending remote command must not contain terminal error material";
            }
        } else {
            if (remote.readbackVerified()) {
                return "failed remote command cannot claim verified readback";
            }
            if (!remote.verifiedSnapshots().isEmpty()) {
                return "failed remote command cannot contain verified snapshots";
            }
            if (remote.errorCode() == null || remote.errorMessage() == null) {
                return "failed remote command must contain error code and message";
            }
        }
        return null;
    }

    private static String validateChangePage(
            String currentCursor,
            int requestedLimit,
            ChangePage page
    ) {
        if (page == null) {
            return "transport returned null change page";
        }
        if (!Objects.equals(currentCursor, page.fromCursor())) {
            return "remote change page does not start at the requested cursor";
        }
        if (!page.readbackVerified()) {
            return "remote change page is missing verified canonical readback";
        }
        if (page.nextCursor() == null || page.nextCursor().isBlank()) {
            return "remote change page next cursor is missing";
        }
        if (page.verifiedSnapshots().size() > requestedLimit) {
            return "remote change page exceeds requested snapshot limit";
        }
        if (
                Objects.equals(currentCursor, page.nextCursor())
                        && !page.verifiedSnapshots().isEmpty()
        ) {
            return "remote change page contains snapshots without cursor progress";
        }
        return null;
    }

    private static void validateLimit(int value, int maximum, String field) {
        if (value < 1 || value > maximum) {
            throw new IllegalArgumentException(field + " must be from 1 through " + maximum);
        }
    }

    /**
     * Remote adapter contract used by the reconnect coordinator.
     *
     * <p>A concrete implementation is responsible for authenticating through its selected lane and
     * for preserving the M2-M1 serialized command boundary. Personal Google implementations must
     * submit/read the Workspace command inbox rather than perform direct canonical mutation.</p>
     */
    public interface Transport {
        /** Ensures the exact command exists remotely and returns its current durable remote state. */
        RemoteCommandState reconcileCommand(OfflineSyncStateStore.CommandIntent command)
                throws TransportException;

        /** Returns one verified canonical change page beginning at the supplied opaque cursor. */
        ChangePage readChanges(String cursor, int limit) throws TransportException;
    }

    public enum RemoteCommandStatus {
        PENDING,
        SUCCEEDED,
        FAILED
    }

    public enum Status {
        COMPLETE,
        MORE_PENDING,
        WAITING_REMOTE,
        REMOTE_FAILURE,
        TRANSPORT_FAILURE,
        PROTOCOL_FAILURE,
        LOCAL_FAILURE
    }

    /** Immutable remote command projection. */
    public static final class RemoteCommandState {
        private final String commandId;
        private final String idempotencyKey;
        private final RemoteCommandStatus status;
        private final boolean readbackVerified;
        private final List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots;
        private final String errorCode;
        private final String errorMessage;

        public RemoteCommandState(
                String commandId,
                String idempotencyKey,
                RemoteCommandStatus status,
                boolean readbackVerified,
                List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots,
                String errorCode,
                String errorMessage
        ) {
            this.commandId = requireText(commandId, "commandId");
            this.idempotencyKey = requireText(idempotencyKey, "idempotencyKey");
            this.status = Objects.requireNonNull(status, "status");
            this.readbackVerified = readbackVerified;
            this.verifiedSnapshots = copySnapshots(verifiedSnapshots);
            this.errorCode = optionalText(errorCode, "errorCode");
            this.errorMessage = optionalText(errorMessage, "errorMessage");
        }

        public static RemoteCommandState pending(
                String commandId,
                String idempotencyKey
        ) {
            return new RemoteCommandState(
                    commandId,
                    idempotencyKey,
                    RemoteCommandStatus.PENDING,
                    false,
                    List.of(),
                    null,
                    null
            );
        }

        public static RemoteCommandState succeeded(
                String commandId,
                String idempotencyKey,
                List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots
        ) {
            return new RemoteCommandState(
                    commandId,
                    idempotencyKey,
                    RemoteCommandStatus.SUCCEEDED,
                    true,
                    verifiedSnapshots,
                    null,
                    null
            );
        }

        public static RemoteCommandState failed(
                String commandId,
                String idempotencyKey,
                String errorCode,
                String errorMessage
        ) {
            return new RemoteCommandState(
                    commandId,
                    idempotencyKey,
                    RemoteCommandStatus.FAILED,
                    false,
                    List.of(),
                    requireText(errorCode, "errorCode"),
                    requireText(errorMessage, "errorMessage")
            );
        }

        public String commandId() {
            return commandId;
        }

        public String idempotencyKey() {
            return idempotencyKey;
        }

        public RemoteCommandStatus status() {
            return status;
        }

        public boolean readbackVerified() {
            return readbackVerified;
        }

        public List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots() {
            return copySnapshots(verifiedSnapshots);
        }

        public String errorCode() {
            return errorCode;
        }

        public String errorMessage() {
            return errorMessage;
        }
    }

    /** Immutable verified canonical change page with opaque cursor semantics. */
    public static final class ChangePage {
        private final String fromCursor;
        private final String nextCursor;
        private final boolean readbackVerified;
        private final List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots;

        public ChangePage(
                String fromCursor,
                String nextCursor,
                boolean readbackVerified,
                List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots
        ) {
            this.fromCursor = optionalText(fromCursor, "fromCursor");
            this.nextCursor = requireText(nextCursor, "nextCursor");
            this.readbackVerified = readbackVerified;
            this.verifiedSnapshots = copySnapshots(verifiedSnapshots);
        }

        public static ChangePage verified(
                String fromCursor,
                String nextCursor,
                List<OfflineSyncStateStore.ResourceSnapshot> snapshots
        ) {
            return new ChangePage(fromCursor, nextCursor, true, snapshots);
        }

        public String fromCursor() {
            return fromCursor;
        }

        public String nextCursor() {
            return nextCursor;
        }

        public boolean readbackVerified() {
            return readbackVerified;
        }

        public List<OfflineSyncStateStore.ResourceSnapshot> verifiedSnapshots() {
            return copySnapshots(verifiedSnapshots);
        }
    }

    /** Stable reconnect pass result suitable for later UI/state mapping. */
    public static final class ReconnectResult {
        private final Status status;
        private final String commandId;
        private final int acknowledgedCommands;
        private final int snapshotsStored;
        private final int remainingPending;
        private final String cursor;
        private final String errorCode;
        private final String message;

        private ReconnectResult(
                Status status,
                String commandId,
                int acknowledgedCommands,
                int snapshotsStored,
                int remainingPending,
                String cursor,
                String errorCode,
                String message
        ) {
            this.status = Objects.requireNonNull(status, "status");
            this.commandId = commandId;
            this.acknowledgedCommands = acknowledgedCommands;
            this.snapshotsStored = snapshotsStored;
            this.remainingPending = remainingPending;
            this.cursor = cursor;
            this.errorCode = errorCode;
            this.message = message;
        }

        static ReconnectResult complete(int acknowledged, int snapshots, String cursor) {
            return new ReconnectResult(
                    Status.COMPLETE,
                    null,
                    acknowledged,
                    snapshots,
                    0,
                    cursor,
                    null,
                    null
            );
        }

        static ReconnectResult morePending(int acknowledged, int snapshots, int remaining) {
            return new ReconnectResult(
                    Status.MORE_PENDING,
                    null,
                    acknowledged,
                    snapshots,
                    remaining,
                    null,
                    null,
                    "more local commands remain for a later bounded reconnect pass"
            );
        }

        static ReconnectResult waitingRemote(String commandId, int acknowledged, int snapshots) {
            return new ReconnectResult(
                    Status.WAITING_REMOTE,
                    commandId,
                    acknowledged,
                    snapshots,
                    0,
                    null,
                    null,
                    "remote command is not terminal yet"
            );
        }

        static ReconnectResult remoteFailure(
                String commandId,
                int acknowledged,
                int snapshots,
                String code,
                String message
        ) {
            return new ReconnectResult(
                    Status.REMOTE_FAILURE,
                    commandId,
                    acknowledged,
                    snapshots,
                    0,
                    null,
                    code,
                    message
            );
        }

        static ReconnectResult transportFailure(
                String commandId,
                int acknowledged,
                int snapshots,
                String code,
                String message
        ) {
            return new ReconnectResult(
                    Status.TRANSPORT_FAILURE,
                    commandId,
                    acknowledged,
                    snapshots,
                    0,
                    null,
                    code,
                    message
            );
        }

        static ReconnectResult protocolFailure(
                String commandId,
                int acknowledged,
                int snapshots,
                String message
        ) {
            return new ReconnectResult(
                    Status.PROTOCOL_FAILURE,
                    commandId,
                    acknowledged,
                    snapshots,
                    0,
                    null,
                    "protocol_error",
                    message
            );
        }

        static ReconnectResult localFailure(
                String commandId,
                int acknowledged,
                int snapshots,
                String message
        ) {
            return new ReconnectResult(
                    Status.LOCAL_FAILURE,
                    commandId,
                    acknowledged,
                    snapshots,
                    0,
                    null,
                    "local_state_error",
                    message
            );
        }

        public Status status() {
            return status;
        }

        public String commandId() {
            return commandId;
        }

        public int acknowledgedCommands() {
            return acknowledgedCommands;
        }

        public int snapshotsStored() {
            return snapshotsStored;
        }

        public int remainingPending() {
            return remainingPending;
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
    }

    /** Transport/authentication/unavailability failure with stable adapter-owned category. */
    public static class TransportException extends Exception {
        private final String code;

        public TransportException(String code, String message) {
            super(requireText(message, "message"));
            this.code = requireText(code, "code");
        }

        public TransportException(String code, String message, Throwable cause) {
            super(requireText(message, "message"), cause);
            this.code = requireText(code, "code");
        }

        public String code() {
            return code;
        }
    }

    interface FaultInjector {
        FaultInjector NONE = new FaultInjector() {};

        default void afterVerifiedRemoteSuccess(
                OfflineSyncStateStore.CommandIntent command,
                RemoteCommandState remote
        ) {
        }

        default void afterChangeSnapshotsStored(ChangePage page) {
        }
    }

    private static List<OfflineSyncStateStore.ResourceSnapshot> copySnapshots(
            List<OfflineSyncStateStore.ResourceSnapshot> snapshots
    ) {
        Objects.requireNonNull(snapshots, "snapshots");
        ArrayList<OfflineSyncStateStore.ResourceSnapshot> result =
                new ArrayList<>(snapshots.size());
        for (OfflineSyncStateStore.ResourceSnapshot snapshot : snapshots) {
            Objects.requireNonNull(snapshot, "snapshot");
            result.add(
                    new OfflineSyncStateStore.ResourceSnapshot(
                            snapshot.dataClass(),
                            snapshot.resourceId(),
                            snapshot.revision(),
                            snapshot.payload()
                    )
            );
        }
        return Collections.unmodifiableList(result);
    }

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank() || !value.equals(value.trim())) {
            throw new IllegalArgumentException(field + " must be non-empty trimmed text");
        }
        return value;
    }

    private static String optionalText(String value, String field) {
        if (value == null) {
            return null;
        }
        return requireText(value, field);
    }
}
