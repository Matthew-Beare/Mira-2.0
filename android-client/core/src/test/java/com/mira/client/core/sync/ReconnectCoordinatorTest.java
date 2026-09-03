package com.mira.client.core.sync;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertThrows;

public final class ReconnectCoordinatorTest {

    @Test
    public void transportReceivesExactStoredCommandIntent() {
        OfflineSyncStateStore store = newStore("client-exact");
        OfflineSyncStateStore.CommandIntent command = new OfflineSyncStateStore.CommandIntent(
                "cmd-exact",
                "user-1",
                "entity",
                "append_event",
                1,
                "schema-v1",
                "resource-1",
                bytes("{\"note\":\"exact\"}"),
                "idem-exact",
                7L,
                "event-1",
                "note_added"
        );
        store.enqueue(command);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.pending(
                        command.commandId(),
                        command.idempotencyKey()
                )
        );

        ReconnectCoordinator.ReconnectResult result =
                new ReconnectCoordinator(store, transport).reconnect();

        assertEquals(ReconnectCoordinator.Status.WAITING_REMOTE, result.status());
        assertEquals(1, transport.commands.size());
        OfflineSyncStateStore.CommandIntent captured = transport.commands.get(0);
        assertEquals(command.commandId(), captured.commandId());
        assertEquals(command.subjectId(), captured.subjectId());
        assertEquals(command.dataClass(), captured.dataClass());
        assertEquals(command.action(), captured.action());
        assertEquals(command.apiMajor(), captured.apiMajor());
        assertEquals(command.schemaVersion(), captured.schemaVersion());
        assertEquals(command.resourceId(), captured.resourceId());
        assertArrayEquals(command.payload(), captured.payload());
        assertEquals(command.idempotencyKey(), captured.idempotencyKey());
        assertEquals(command.expectedRevision(), captured.expectedRevision());
        assertEquals(command.eventId(), captured.eventId());
        assertEquals(command.eventType(), captured.eventType());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void verifiedTerminalSuccessAcknowledgesCommandsInStableFifoOrder() {
        OfflineSyncStateStore store = newStore("client-fifo");
        OfflineSyncStateStore.CommandIntent first = upsert("cmd-1", "idem-1", 1);
        OfflineSyncStateStore.CommandIntent second = upsert("cmd-2", "idem-2", 2);
        store.enqueue(first);
        store.enqueue(second);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                first.commandId(),
                ReconnectCoordinator.RemoteCommandState.succeeded(
                        first.commandId(), first.idempotencyKey(), Collections.emptyList()
                )
        );
        transport.commandStates.put(
                second.commandId(),
                ReconnectCoordinator.RemoteCommandState.succeeded(
                        second.commandId(), second.idempotencyKey(), Collections.emptyList()
                )
        );
        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                null, "cursor-0", Collections.emptyList()
        );

        ReconnectCoordinator.ReconnectResult result =
                new ReconnectCoordinator(store, transport).reconnect();

        assertEquals(ReconnectCoordinator.Status.COMPLETE, result.status());
        assertEquals(2, result.acknowledgedCommands());
        assertEquals(Arrays.asList("cmd-1", "cmd-2"), transport.commandIds());
        assertEquals(0, store.pendingCount());
        assertEquals(2, store.acknowledgedCount());
        assertEquals("cursor-0", store.cursor());
        assertEquals(1, transport.readChangesCalls);
    }

    @Test
    public void pendingRemoteCommandStopsPassWithoutLocalAcknowledgement() {
        OfflineSyncStateStore store = newStore("client-pending");
        OfflineSyncStateStore.CommandIntent command = upsert("cmd-pending", "idem-pending", 1);
        store.enqueue(command);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.pending(
                        command.commandId(), command.idempotencyKey()
                )
        );

        ReconnectCoordinator.ReconnectResult result =
                new ReconnectCoordinator(store, transport).reconnect();

        assertEquals(ReconnectCoordinator.Status.WAITING_REMOTE, result.status());
        assertEquals(command.commandId(), result.commandId());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void terminalRemoteConflictRemainsPendingForExplicitHandling() {
        OfflineSyncStateStore store = newStore("client-conflict");
        OfflineSyncStateStore.CommandIntent command = upsert("cmd-conflict", "idem-conflict", 1);
        store.enqueue(command);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.failed(
                        command.commandId(),
                        command.idempotencyKey(),
                        "conflict",
                        "stale revision"
                )
        );

        ReconnectCoordinator.ReconnectResult result =
                new ReconnectCoordinator(store, transport).reconnect();

        assertEquals(ReconnectCoordinator.Status.REMOTE_FAILURE, result.status());
        assertEquals("conflict", result.errorCode());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void unverifiedOrMismatchedRemoteSuccessFailsProtocolClosed() {
        OfflineSyncStateStore store = newStore("client-protocol");
        OfflineSyncStateStore.CommandIntent command = upsert("cmd-protocol", "idem-protocol", 1);
        store.enqueue(command);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                new ReconnectCoordinator.RemoteCommandState(
                        command.commandId(),
                        command.idempotencyKey(),
                        ReconnectCoordinator.RemoteCommandStatus.SUCCEEDED,
                        false,
                        Collections.emptyList(),
                        null,
                        null
                )
        );

        ReconnectCoordinator.ReconnectResult first =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.PROTOCOL_FAILURE, first.status());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());

        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.succeeded(
                        command.commandId(),
                        "different-idempotency-key",
                        Collections.emptyList()
                )
        );
        ReconnectCoordinator.ReconnectResult second =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.PROTOCOL_FAILURE, second.status());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
    }

    @Test
    public void transportFailurePreservesPendingCacheAndCursor() {
        OfflineSyncStateStore store = newStore("client-transport-failure");
        OfflineSyncStateStore.CommandIntent command = upsert("cmd-network", "idem-network", 1);
        store.enqueue(command);
        store.putSnapshot(snapshot("entity", "resource-existing", 2, "existing"));
        store.compareAndSetCursor(null, "cursor-existing");

        FakeTransport transport = new FakeTransport();
        transport.commandFailures.put(
                command.commandId(),
                new ReconnectCoordinator.TransportException(
                        "unavailable", "network unavailable"
                )
        );

        ReconnectCoordinator.ReconnectResult result =
                new ReconnectCoordinator(store, transport).reconnect();

        assertEquals(ReconnectCoordinator.Status.TRANSPORT_FAILURE, result.status());
        assertEquals("unavailable", result.errorCode());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertEquals("cursor-existing", store.cursor());
        OfflineSyncStateStore.ResourceSnapshot cached =
                store.snapshot("entity", "resource-existing");
        assertNotNull(cached);
        assertEquals(2, cached.revision());
        assertArrayEquals(bytes("existing"), cached.payload());
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void crashAfterVerifiedRemoteSuccessRetriesSameCommandAndConverges() {
        OfflineSyncStateStore store = newStore("client-command-crash");
        OfflineSyncStateStore.CommandIntent command = upsert("cmd-crash", "idem-crash", 1);
        store.enqueue(command);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.succeeded(
                        command.commandId(),
                        command.idempotencyKey(),
                        Collections.singletonList(
                                snapshot("entity", "resource-1", 1, "remote-readback")
                        )
                )
        );
        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                null, "cursor-after-retry", Collections.emptyList()
        );

        ReconnectCoordinator crashing = new ReconnectCoordinator(
                store,
                transport,
                new ReconnectCoordinator.FaultInjector() {
                    private boolean first = true;

                    @Override
                    public void afterVerifiedRemoteSuccess(
                            OfflineSyncStateStore.CommandIntent ignored,
                            ReconnectCoordinator.RemoteCommandState remote
                    ) {
                        if (first) {
                            first = false;
                            throw new SimulatedCrash();
                        }
                    }
                }
        );

        assertThrows(SimulatedCrash.class, crashing::reconnect);
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertNotNull(store.snapshot("entity", "resource-1"));
        assertNull(store.cursor());

        ReconnectCoordinator.ReconnectResult retry =
                new ReconnectCoordinator(store, transport).reconnect();

        assertEquals(ReconnectCoordinator.Status.COMPLETE, retry.status());
        assertEquals(0, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        assertEquals(Arrays.asList("cmd-crash", "cmd-crash"), transport.commandIds());
        assertEquals("cursor-after-retry", store.cursor());
    }

    @Test
    public void snapshotsPersistBeforeCursorAndRegressionPreventsAdvance() {
        OfflineSyncStateStore store = newStore("client-page-order");
        store.compareAndSetCursor(null, "cursor-0");

        FakeTransport transport = new FakeTransport();
        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                "cursor-0",
                "cursor-1",
                Collections.singletonList(snapshot("entity", "resource-page", 1, "page-v1"))
        );

        ReconnectCoordinator.ReconnectResult success =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.COMPLETE, success.status());
        assertEquals("cursor-1", store.cursor());
        assertArrayEquals(
                bytes("page-v1"),
                store.snapshot("entity", "resource-page").payload()
        );

        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                "cursor-1",
                "cursor-2",
                Collections.singletonList(snapshot("entity", "resource-page", 1, "forked-v1"))
        );
        ReconnectCoordinator.ReconnectResult failure =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.LOCAL_FAILURE, failure.status());
        assertEquals("cursor-1", store.cursor());
        assertArrayEquals(
                bytes("page-v1"),
                store.snapshot("entity", "resource-page").payload()
        );
    }

    @Test
    public void crashAfterSnapshotsBeforeCursorRetriesIdempotently() {
        OfflineSyncStateStore store = newStore("client-cursor-crash");
        store.compareAndSetCursor(null, "cursor-a");

        FakeTransport transport = new FakeTransport();
        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                "cursor-a",
                "cursor-b",
                Collections.singletonList(snapshot("task", "task-1", 3, "verified-task"))
        );

        ReconnectCoordinator crashing = new ReconnectCoordinator(
                store,
                transport,
                new ReconnectCoordinator.FaultInjector() {
                    private boolean first = true;

                    @Override
                    public void afterChangeSnapshotsStored(
                            ReconnectCoordinator.ChangePage ignored
                    ) {
                        if (first) {
                            first = false;
                            throw new SimulatedCrash();
                        }
                    }
                }
        );

        assertThrows(SimulatedCrash.class, crashing::reconnect);
        assertEquals("cursor-a", store.cursor());
        assertNotNull(store.snapshot("task", "task-1"));

        ReconnectCoordinator.ReconnectResult retry =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.COMPLETE, retry.status());
        assertEquals("cursor-b", store.cursor());
        assertEquals(2, transport.readChangesCalls);
    }

    @Test
    public void malformedChangePageDoesNotMutateCursor() {
        OfflineSyncStateStore store = newStore("client-page-protocol");
        store.compareAndSetCursor(null, "cursor-live");

        FakeTransport transport = new FakeTransport();
        transport.changePage = new ReconnectCoordinator.ChangePage(
                "wrong-cursor",
                "cursor-next",
                true,
                Collections.singletonList(snapshot("entity", "resource-x", 1, "x"))
        );

        ReconnectCoordinator.ReconnectResult mismatch =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.PROTOCOL_FAILURE, mismatch.status());
        assertEquals("cursor-live", store.cursor());
        assertNull(store.snapshot("entity", "resource-x"));

        transport.changePage = new ReconnectCoordinator.ChangePage(
                "cursor-live",
                "cursor-next",
                false,
                Collections.emptyList()
        );
        ReconnectCoordinator.ReconnectResult unverified =
                new ReconnectCoordinator(store, transport).reconnect();
        assertEquals(ReconnectCoordinator.Status.PROTOCOL_FAILURE, unverified.status());
        assertEquals("cursor-live", store.cursor());
    }

    @Test
    public void boundedPassDoesNotAdvanceCursorWhileMoreCommandsRemain() {
        OfflineSyncStateStore store = newStore("client-bounded");
        OfflineSyncStateStore.CommandIntent first = upsert("cmd-bound-1", "idem-bound-1", 1);
        OfflineSyncStateStore.CommandIntent second = upsert("cmd-bound-2", "idem-bound-2", 2);
        store.enqueue(first);
        store.enqueue(second);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                first.commandId(),
                ReconnectCoordinator.RemoteCommandState.succeeded(
                        first.commandId(), first.idempotencyKey(), Collections.emptyList()
                )
        );
        transport.commandStates.put(
                second.commandId(),
                ReconnectCoordinator.RemoteCommandState.succeeded(
                        second.commandId(), second.idempotencyKey(), Collections.emptyList()
                )
        );

        ReconnectCoordinator.ReconnectResult firstPass =
                new ReconnectCoordinator(store, transport).reconnect(1, 128);

        assertEquals(ReconnectCoordinator.Status.MORE_PENDING, firstPass.status());
        assertEquals(1, firstPass.acknowledgedCommands());
        assertEquals(1, firstPass.remainingPending());
        assertEquals(1, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        assertNull(store.cursor());
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void emptyReconnectCanEstablishThenReplayNoopCursor() {
        OfflineSyncStateStore store = newStore("client-empty");
        FakeTransport transport = new FakeTransport();
        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                null, "cursor-empty", Collections.emptyList()
        );

        ReconnectCoordinator coordinator = new ReconnectCoordinator(store, transport);
        ReconnectCoordinator.ReconnectResult first = coordinator.reconnect();
        assertEquals(ReconnectCoordinator.Status.COMPLETE, first.status());
        assertEquals("cursor-empty", store.cursor());

        transport.changePage = ReconnectCoordinator.ChangePage.verified(
                "cursor-empty", "cursor-empty", Collections.emptyList()
        );
        ReconnectCoordinator.ReconnectResult second = coordinator.reconnect();
        assertEquals(ReconnectCoordinator.Status.COMPLETE, second.status());
        assertEquals("cursor-empty", store.cursor());
        assertEquals(2, transport.readChangesCalls);
    }

    private static OfflineSyncStateStore newStore(String clientId) {
        return new OfflineSyncStateStore(
                clientId,
                new IdentityStateCipher(),
                new MemoryBlobStore()
        );
    }

    private static OfflineSyncStateStore.CommandIntent upsert(
            String commandId,
            String idempotencyKey,
            int value
    ) {
        return new OfflineSyncStateStore.CommandIntent(
                commandId,
                "user-1",
                "entity",
                "upsert",
                1,
                "schema-v1",
                "resource-" + value,
                bytes("{\"value\":" + value + "}"),
                idempotencyKey,
                0L,
                null,
                null
        );
    }

    private static OfflineSyncStateStore.ResourceSnapshot snapshot(
            String dataClass,
            String resourceId,
            long revision,
            String payload
    ) {
        return new OfflineSyncStateStore.ResourceSnapshot(
                dataClass,
                resourceId,
                revision,
                bytes(payload)
        );
    }

    private static byte[] bytes(String value) {
        return value.getBytes(StandardCharsets.UTF_8);
    }

    private static final class FakeTransport implements ReconnectCoordinator.Transport {
        final Map<String, ReconnectCoordinator.RemoteCommandState> commandStates = new HashMap<>();
        final Map<String, ReconnectCoordinator.TransportException> commandFailures = new HashMap<>();
        final List<OfflineSyncStateStore.CommandIntent> commands = new ArrayList<>();
        ReconnectCoordinator.ChangePage changePage;
        ReconnectCoordinator.TransportException changeFailure;
        int readChangesCalls;

        @Override
        public ReconnectCoordinator.RemoteCommandState reconcileCommand(
                OfflineSyncStateStore.CommandIntent command
        ) throws ReconnectCoordinator.TransportException {
            commands.add(command);
            ReconnectCoordinator.TransportException failure =
                    commandFailures.get(command.commandId());
            if (failure != null) {
                throw failure;
            }
            ReconnectCoordinator.RemoteCommandState state =
                    commandStates.get(command.commandId());
            if (state == null) {
                return ReconnectCoordinator.RemoteCommandState.pending(
                        command.commandId(), command.idempotencyKey()
                );
            }
            return state;
        }

        @Override
        public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit)
                throws ReconnectCoordinator.TransportException {
            readChangesCalls += 1;
            if (changeFailure != null) {
                throw changeFailure;
            }
            if (changePage != null) {
                return changePage;
            }
            String next = cursor == null ? "cursor-default" : cursor;
            return ReconnectCoordinator.ChangePage.verified(
                    cursor,
                    next,
                    Collections.emptyList()
            );
        }

        List<String> commandIds() {
            ArrayList<String> result = new ArrayList<>();
            for (OfflineSyncStateStore.CommandIntent command : commands) {
                result.add(command.commandId());
            }
            return result;
        }
    }

    private static final class IdentityStateCipher implements OfflineSyncStateStore.StateCipher {
        @Override
        public OfflineSyncStateStore.SealedState seal(String clientId, byte[] plaintext) {
            return new OfflineSyncStateStore.SealedState(new byte[12], plaintext);
        }

        @Override
        public byte[] open(String clientId, OfflineSyncStateStore.SealedState sealed) {
            return sealed.ciphertext();
        }

        @Override
        public void deleteKey(String clientId) {
        }
    }

    private static final class MemoryBlobStore implements OfflineSyncStateStore.BlobStore {
        private final Map<String, byte[]> blobs = new HashMap<>();

        @Override
        public void write(String clientId, byte[] blob) {
            blobs.put(clientId, blob.clone());
        }

        @Override
        public byte[] read(String clientId) {
            byte[] blob = blobs.get(clientId);
            if (blob == null) {
                throw new OfflineSyncStateStore.StateUnavailableException(
                        "offline state is not stored"
                );
            }
            return blob.clone();
        }

        @Override
        public boolean exists(String clientId) {
            return blobs.containsKey(clientId);
        }

        @Override
        public void delete(String clientId) {
            blobs.remove(clientId);
        }
    }

    private static final class SimulatedCrash extends RuntimeException {
    }
}
