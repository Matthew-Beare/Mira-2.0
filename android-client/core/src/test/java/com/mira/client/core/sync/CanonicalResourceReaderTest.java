package com.mira.client.core.sync;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

public final class CanonicalResourceReaderTest {

    @Test
    public void laterPageRevisionPreventsStaleFreshClaim() {
        OfflineSyncStateStore store = newStore("reader-later-revision");
        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "cursor-1",
                true,
                Collections.singletonList(snapshot("entity", "resource-1", 1, "{\"v\":1}"))
        ));
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                "cursor-1",
                "cursor-2",
                false,
                Collections.singletonList(snapshot("entity", "resource-1", 2, "{\"v\":2}"))
        ));

        CanonicalResourceReader reader = new CanonicalResourceReader(store, transport);
        CanonicalResourceReader.ReadResult first =
                reader.refreshAndRead("entity", "resource-1", 1);

        assertEquals(CanonicalResourceReader.Status.MORE_REMOTE_CHANGES, first.status());
        assertNull(first.snapshot());
        assertEquals("cursor-1", first.cursor());
        assertEquals(1L, store.snapshot("entity", "resource-1").revision());

        CanonicalResourceReader.ReadResult second =
                reader.refreshAndRead("entity", "resource-1", 1);

        assertEquals(CanonicalResourceReader.Status.FRESH_FOUND, second.status());
        assertEquals("cursor-2", second.cursor());
        assertEquals(2L, second.snapshot().revision());
        assertArrayEquals(bytes("{\"v\":2}"), second.snapshot().payload());
    }

    @Test
    public void readOnlyRefreshNeverReconcilesPendingCommand() {
        OfflineSyncStateStore store = newStore("reader-pending-command");
        store.enqueue(new OfflineSyncStateStore.CommandIntent(
                "cmd-pending",
                "user-1",
                "entity",
                "upsert",
                1,
                "mira-api-1",
                "resource-write",
                bytes("{\"value\":1}"),
                "idem-pending",
                0L,
                null,
                null
        ));

        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "cursor-0",
                false,
                Collections.emptyList()
        ));

        CanonicalResourceReader.ReadResult result = new CanonicalResourceReader(store, transport)
                .refreshAndRead("entity", "resource-read");

        assertEquals(CanonicalResourceReader.Status.FRESH_MISSING, result.status());
        assertEquals(0, transport.reconcileCalls);
        assertEquals(1, transport.readChangesCalls);
        assertEquals(1, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
    }

    @Test
    public void freshMissingRequiresTerminalRemotePage() {
        OfflineSyncStateStore store = newStore("reader-missing");
        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "cursor-1",
                true,
                Collections.singletonList(snapshot("task", "other-resource", 1, "{\"x\":1}"))
        ));
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                "cursor-1",
                "cursor-1",
                false,
                Collections.emptyList()
        ));

        CanonicalResourceReader reader = new CanonicalResourceReader(store, transport);
        CanonicalResourceReader.ReadResult first =
                reader.refreshAndRead("entity", "missing-resource", 1);
        assertEquals(CanonicalResourceReader.Status.MORE_REMOTE_CHANGES, first.status());
        assertNull(first.snapshot());

        CanonicalResourceReader.ReadResult second =
                reader.refreshAndRead("entity", "missing-resource", 1);
        assertEquals(CanonicalResourceReader.Status.FRESH_MISSING, second.status());
        assertEquals("cursor-1", second.cursor());
        assertNull(second.snapshot());
    }

    @Test
    public void contradictoryMoreWithoutSnapshotFailsProtocolClosed() {
        OfflineSyncStateStore store = newStore("reader-contradiction");
        FakeTransport transport = new FakeTransport();
        transport.pages.add(new ReconnectCoordinator.ChangePage(
                null,
                "cursor-1",
                true,
                true,
                Collections.emptyList()
        ));

        CanonicalResourceReader.ReadResult result = new CanonicalResourceReader(store, transport)
                .refreshAndRead("entity", "resource-1");

        assertEquals(CanonicalResourceReader.Status.PROTOCOL_FAILURE, result.status());
        assertEquals("protocol_error", result.errorCode());
        assertNull(store.cursor());
    }

    @Test
    public void transportFailureDoesNotExposeCachedSnapshotAsFresh() {
        OfflineSyncStateStore store = newStore("reader-transport-failure");
        store.putSnapshot(snapshot("entity", "resource-1", 4, "{\"cached\":true}"));
        FakeTransport transport = new FakeTransport();
        transport.failure = new ReconnectCoordinator.TransportException(
                "provider_unavailable",
                "synthetic outage"
        );

        CanonicalResourceReader.ReadResult result = new CanonicalResourceReader(store, transport)
                .refreshAndRead("entity", "resource-1");

        assertEquals(CanonicalResourceReader.Status.TRANSPORT_FAILURE, result.status());
        assertEquals("provider_unavailable", result.errorCode());
        assertNull(result.snapshot());
        assertEquals(4L, store.snapshot("entity", "resource-1").revision());
    }

    @Test
    public void sameRevisionForkBlocksCursorAdvanceAndFreshClaim() {
        OfflineSyncStateStore store = newStore("reader-fork");
        store.putSnapshot(snapshot("entity", "resource-1", 2, "{\"value\":1}"));
        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "cursor-1",
                false,
                Collections.singletonList(snapshot("entity", "resource-1", 2, "{\"value\":2}"))
        ));

        CanonicalResourceReader.ReadResult result = new CanonicalResourceReader(store, transport)
                .refreshAndRead("entity", "resource-1");

        assertEquals(CanonicalResourceReader.Status.LOCAL_FAILURE, result.status());
        assertNull(result.snapshot());
        assertNull(store.cursor());
        assertArrayEquals(
                bytes("{\"value\":1}"),
                store.snapshot("entity", "resource-1").payload()
        );
    }

    @Test
    public void invalidLookupFailsBeforeProviderRead() {
        OfflineSyncStateStore store = newStore("reader-invalid");
        FakeTransport transport = new FakeTransport();

        CanonicalResourceReader.ReadResult result = new CanonicalResourceReader(store, transport)
                .refreshAndRead("bad class", "resource-1");

        assertEquals(CanonicalResourceReader.Status.LOCAL_FAILURE, result.status());
        assertEquals(0, transport.readChangesCalls);
        assertEquals(0, transport.reconcileCalls);
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

    private static OfflineSyncStateStore newStore(String clientId) {
        return new OfflineSyncStateStore(clientId, new FakeCipher(), new MemoryBlobStore());
    }

    private static final class FakeTransport implements ReconnectCoordinator.Transport {
        final Deque<ReconnectCoordinator.ChangePage> pages = new ArrayDeque<>();
        int reconcileCalls;
        int readChangesCalls;
        ReconnectCoordinator.TransportException failure;

        @Override
        public ReconnectCoordinator.RemoteCommandState reconcileCommand(
                OfflineSyncStateStore.CommandIntent command
        ) {
            reconcileCalls += 1;
            throw new AssertionError("read-only canonical reader must not reconcile commands");
        }

        @Override
        public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit)
                throws ReconnectCoordinator.TransportException {
            readChangesCalls += 1;
            if (failure != null) {
                throw failure;
            }
            if (pages.isEmpty()) {
                throw new AssertionError("unexpected readChanges call");
            }
            ReconnectCoordinator.ChangePage page = pages.removeFirst();
            assertEquals(cursor, page.fromCursor());
            return page;
        }
    }

    private static final class FakeCipher implements OfflineSyncStateStore.StateCipher {
        @Override
        public OfflineSyncStateStore.SealedState seal(String clientId, byte[] plaintext) {
            return new OfflineSyncStateStore.SealedState(new byte[12], plaintext.clone());
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
                throw new OfflineSyncStateStore.StateUnavailableException("test state missing");
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
