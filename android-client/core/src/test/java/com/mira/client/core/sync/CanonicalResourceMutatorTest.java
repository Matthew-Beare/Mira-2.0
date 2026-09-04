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

public final class CanonicalResourceMutatorTest {

    @Test
    public void durableEnqueueOccursBeforeProviderIoAndPendingRemainsQueued() {
        OfflineSyncStateStore store = newStore("mutator-enqueue-first");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-enqueue-first", "idem-enqueue-first", "resource-1", 0L, "one"
        );
        FakeTransport transport = new FakeTransport();
        transport.storeObservedAtCommandIo = store;
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.pending(
                        command.commandId(), command.idempotencyKey()
                )
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.WAITING_REMOTE, result.status());
        assertEquals(OfflineSyncStateStore.EnqueueResult.ENQUEUED, result.enqueueResult());
        assertEquals(command.commandId(), result.commandId());
        assertNull(result.blockingCommandId());
        assertNull(result.canonicalSnapshot());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertEquals(Collections.singletonList(command.commandId()), transport.commandIds);
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void verifiedTerminalSuccessStoresSnapshotAcknowledgesAndReturnsApplied() {
        OfflineSyncStateStore store = newStore("mutator-applied");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-applied", "idem-applied", "resource-applied", 3L, "four"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                success(command, 4L, "four")
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.APPLIED, result.status());
        assertEquals(OfflineSyncStateStore.EnqueueResult.ENQUEUED, result.enqueueResult());
        assertEquals(0, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        OfflineSyncStateStore.ResourceSnapshot snapshot = result.canonicalSnapshot();
        assertNotNull(snapshot);
        assertEquals("entity", snapshot.dataClass());
        assertEquals("resource-applied", snapshot.resourceId());
        assertEquals(4L, snapshot.revision());
        assertArrayEquals(json("four"), snapshot.payload());
        assertEquals(1, transport.readChangesCalls);
    }

    @Test
    public void exactReplayAfterAcknowledgementReturnsAppliedWithoutProviderIo() {
        OfflineSyncStateStore store = newStore("mutator-replay");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-replay", "idem-replay", "resource-replay", 0L, "one"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(command.commandId(), success(command, 1L, "one"));
        CanonicalResourceMutator mutator = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        );

        CanonicalResourceMutator.MutationResult first = mutator.mutate(command);
        assertEquals(CanonicalResourceMutator.Status.APPLIED, first.status());
        int commandCalls = transport.commandIds.size();
        int changeCalls = transport.readChangesCalls;

        CanonicalResourceMutator.MutationResult replay = mutator.mutate(command);

        assertEquals(CanonicalResourceMutator.Status.APPLIED, replay.status());
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED,
                replay.enqueueResult()
        );
        assertEquals(commandCalls, transport.commandIds.size());
        assertEquals(changeCalls, transport.readChangesCalls);
        assertEquals(0, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        assertEquals(1L, replay.canonicalSnapshot().revision());
    }

    @Test
    public void exactPendingRetryDoesNotDuplicateLocalQueueAndCanConverge() {
        OfflineSyncStateStore store = newStore("mutator-pending-retry");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-pending-retry", "idem-pending-retry", "resource-retry", 1L, "two"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.pending(
                        command.commandId(), command.idempotencyKey()
                )
        );
        CanonicalResourceMutator mutator = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        );

        CanonicalResourceMutator.MutationResult first = mutator.mutate(command);
        assertEquals(CanonicalResourceMutator.Status.WAITING_REMOTE, first.status());
        assertEquals(1, store.pendingCount());

        transport.commandStates.put(command.commandId(), success(command, 2L, "two"));
        CanonicalResourceMutator.MutationResult retry = mutator.mutate(command);

        assertEquals(CanonicalResourceMutator.Status.APPLIED, retry.status());
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_PENDING,
                retry.enqueueResult()
        );
        assertEquals(Arrays.asList(command.commandId(), command.commandId()), transport.commandIds);
        assertEquals(0, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
    }

    @Test
    public void staleRevisionRemoteFailureRemainsPending() {
        OfflineSyncStateStore store = newStore("mutator-conflict");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-conflict", "idem-conflict", "resource-conflict", 4L, "five"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                ReconnectCoordinator.RemoteCommandState.failed(
                        command.commandId(), command.idempotencyKey(),
                        "conflict", "stale revision"
                )
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.REMOTE_FAILURE, result.status());
        assertEquals("conflict", result.errorCode());
        assertEquals("stale revision", result.message());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertNull(result.canonicalSnapshot());
    }

    @Test
    public void transportFailurePreservesPendingCommand() {
        OfflineSyncStateStore store = newStore("mutator-transport");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-transport", "idem-transport", "resource-transport", 0L, "one"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandFailures.put(
                command.commandId(),
                new ReconnectCoordinator.TransportException("unavailable", "network down")
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.TRANSPORT_FAILURE, result.status());
        assertEquals("unavailable", result.errorCode());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
    }

    @Test
    public void earlierFifoCommandBlocksLaterMutationHonestly() {
        OfflineSyncStateStore store = newStore("mutator-fifo-block");
        OfflineSyncStateStore.CommandIntent earlier = upsert(
                "cmd-earlier", "idem-earlier", "resource-earlier", 0L, "earlier"
        );
        OfflineSyncStateStore.CommandIntent requested = upsert(
                "cmd-requested", "idem-requested", "resource-requested", 0L, "requested"
        );
        store.enqueue(earlier);

        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                earlier.commandId(),
                ReconnectCoordinator.RemoteCommandState.pending(
                        earlier.commandId(), earlier.idempotencyKey()
                )
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(requested);

        assertEquals(
                CanonicalResourceMutator.Status.BLOCKED_BY_EARLIER_COMMAND,
                result.status()
        );
        assertEquals(earlier.commandId(), result.blockingCommandId());
        assertEquals(Collections.singletonList(earlier.commandId()), transport.commandIds);
        assertEquals(2, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
    }

    @Test
    public void commandSuccessStillReturnsAppliedWhenLaterChangeRefreshFails() {
        OfflineSyncStateStore store = newStore("mutator-change-failure");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-change-failure", "idem-change-failure", "resource-change", 1L, "two"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(command.commandId(), success(command, 2L, "two"));
        transport.changeFailure = new ReconnectCoordinator.TransportException(
                "unavailable", "Changes refresh unavailable"
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.APPLIED, result.status());
        assertEquals(0, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        assertNotNull(result.canonicalSnapshot());
        assertEquals(2L, result.canonicalSnapshot().revision());
        assertEquals(1, transport.readChangesCalls);
    }

    @Test
    public void unverifiedRemoteSuccessNeverBecomesApplied() {
        OfflineSyncStateStore store = newStore("mutator-unverified");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-unverified", "idem-unverified", "resource-unverified", 0L, "one"
        );
        FakeTransport transport = new FakeTransport();
        transport.commandStates.put(
                command.commandId(),
                new ReconnectCoordinator.RemoteCommandState(
                        command.commandId(), command.idempotencyKey(),
                        ReconnectCoordinator.RemoteCommandStatus.SUCCEEDED,
                        false,
                        Collections.singletonList(snapshot(command, 1L, "one")),
                        null,
                        null
                )
        );

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.PROTOCOL_FAILURE, result.status());
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertNull(result.canonicalSnapshot());
    }

    @Test
    public void acknowledgedCommandWithoutVerifiedSnapshotFailsClosed() {
        OfflineSyncStateStore store = newStore("mutator-missing-snapshot");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-missing", "idem-missing", "resource-missing", 0L, "one"
        );
        store.enqueue(command);
        store.acknowledge(command.commandId(), command.idempotencyKey());
        FakeTransport transport = new FakeTransport();

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.LOCAL_FAILURE, result.status());
        assertEquals("verified_result_missing", result.errorCode());
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED,
                result.enqueueResult()
        );
        assertEquals(0, transport.commandIds.size());
        assertEquals(0, transport.readChangesCalls);
    }

    @Test
    public void acknowledgedCommandRequiresRevisionNewerThanExpectedRevision() {
        OfflineSyncStateStore store = newStore("mutator-old-snapshot");
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-old", "idem-old", "resource-old", 3L, "four"
        );
        store.enqueue(command);
        store.putSnapshot(snapshot(command, 3L, "old"));
        store.acknowledge(command.commandId(), command.idempotencyKey());

        CanonicalResourceMutator.MutationResult result = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, new FakeTransport())
        ).mutate(command);

        assertEquals(CanonicalResourceMutator.Status.LOCAL_FAILURE, result.status());
        assertEquals("verified_result_revision_invalid", result.errorCode());
    }

    @Test
    public void unsupportedCommandShapeFailsBeforeQueueOrProviderIo() {
        OfflineSyncStateStore store = newStore("mutator-unsupported");
        OfflineSyncStateStore.CommandIntent event = new OfflineSyncStateStore.CommandIntent(
                "cmd-event",
                "user-1",
                "entity",
                "append_event",
                1,
                "schema-v1",
                "resource-event",
                json("event"),
                "idem-event",
                0L,
                "event-1",
                "changed"
        );
        FakeTransport transport = new FakeTransport();
        CanonicalResourceMutator mutator = new CanonicalResourceMutator(
                store,
                new ReconnectCoordinator(store, transport)
        );

        assertThrows(IllegalArgumentException.class, () -> mutator.mutate(event));
        assertEquals(0, store.pendingCount());
        assertEquals(0, transport.commandIds.size());

        OfflineSyncStateStore.CommandIntent missingRevision = new OfflineSyncStateStore.CommandIntent(
                "cmd-no-revision",
                "user-1",
                "entity",
                "upsert",
                1,
                "schema-v1",
                "resource-no-revision",
                json("value"),
                "idem-no-revision",
                null,
                null,
                null
        );
        assertThrows(IllegalArgumentException.class, () -> mutator.mutate(missingRevision));
        assertEquals(0, store.pendingCount());
        assertEquals(0, transport.commandIds.size());
    }

    private static ReconnectCoordinator.RemoteCommandState success(
            OfflineSyncStateStore.CommandIntent command,
            long revision,
            String value
    ) {
        return ReconnectCoordinator.RemoteCommandState.succeeded(
                command.commandId(),
                command.idempotencyKey(),
                Collections.singletonList(snapshot(command, revision, value))
        );
    }

    private static OfflineSyncStateStore.ResourceSnapshot snapshot(
            OfflineSyncStateStore.CommandIntent command,
            long revision,
            String value
    ) {
        return new OfflineSyncStateStore.ResourceSnapshot(
                command.dataClass(), command.resourceId(), revision, json(value)
        );
    }

    private static OfflineSyncStateStore.CommandIntent upsert(
            String commandId,
            String idempotencyKey,
            String resourceId,
            Long expectedRevision,
            String value
    ) {
        return new OfflineSyncStateStore.CommandIntent(
                commandId,
                "user-1",
                "entity",
                "upsert",
                1,
                "schema-v1",
                resourceId,
                json(value),
                idempotencyKey,
                expectedRevision,
                null,
                null
        );
    }

    private static byte[] json(String value) {
        return ("{\"value\":\"" + value + "\"}").getBytes(StandardCharsets.UTF_8);
    }

    private static OfflineSyncStateStore newStore(String clientId) {
        return new OfflineSyncStateStore(
                clientId,
                new PassthroughCipher(),
                new MemoryBlobStore()
        );
    }

    private static final class FakeTransport implements ReconnectCoordinator.Transport {
        final Map<String, ReconnectCoordinator.RemoteCommandState> commandStates = new HashMap<>();
        final Map<String, ReconnectCoordinator.TransportException> commandFailures = new HashMap<>();
        final List<String> commandIds = new ArrayList<>();
        OfflineSyncStateStore storeObservedAtCommandIo;
        ReconnectCoordinator.ChangePage changePage;
        ReconnectCoordinator.TransportException changeFailure;
        int readChangesCalls;

        @Override
        public ReconnectCoordinator.RemoteCommandState reconcileCommand(
                OfflineSyncStateStore.CommandIntent command
        ) throws ReconnectCoordinator.TransportException {
            if (storeObservedAtCommandIo != null && storeObservedAtCommandIo.pendingCount() < 1) {
                throw new AssertionError("provider I/O occurred before durable local enqueue");
            }
            commandIds.add(command.commandId());
            ReconnectCoordinator.TransportException failure =
                    commandFailures.get(command.commandId());
            if (failure != null) {
                throw failure;
            }
            ReconnectCoordinator.RemoteCommandState state = commandStates.get(command.commandId());
            if (state == null) {
                throw new AssertionError("missing fake command state for " + command.commandId());
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
            String next = cursor == null ? "mira-change-v1:0" : cursor;
            return ReconnectCoordinator.ChangePage.verified(
                    cursor,
                    next,
                    Collections.<OfflineSyncStateStore.ResourceSnapshot>emptyList()
            );
        }
    }

    private static final class PassthroughCipher implements OfflineSyncStateStore.StateCipher {
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
                throw new OfflineSyncStateStore.OfflineStateException("missing test blob");
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
}
