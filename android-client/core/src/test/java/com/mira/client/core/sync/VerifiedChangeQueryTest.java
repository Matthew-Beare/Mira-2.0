package com.mira.client.core.sync;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

public final class VerifiedChangeQueryTest {

    @Test
    public void foldsLatestRevisionAcrossVerifiedPagesWithoutReconcilingCommands() {
        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "mira-change-v1:2",
                true,
                Arrays.asList(
                        snapshot("identifier", "identifier-a", 1, "{\"v\":1}"),
                        snapshot("entity", "entity-a", 1, "{\"ignored\":true}")
                )
        ));
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                "mira-change-v1:2",
                "mira-change-v1:3",
                false,
                Collections.singletonList(
                        snapshot("identifier", "identifier-a", 2, "{\"v\":2}")
                )
        ));

        VerifiedChangeQuery.QueryResult result =
                new VerifiedChangeQuery(transport).queryLatest("identifier", 2);

        assertEquals(VerifiedChangeQuery.Status.COMPLETE, result.status());
        assertEquals("mira-change-v1:3", result.cursor());
        assertEquals(1, result.snapshots().size());
        assertEquals(2L, result.snapshots().get(0).revision());
        assertArrayEquals(bytes("{\"v\":2}"), result.snapshots().get(0).payload());
        assertEquals(2, transport.readCalls);
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void sameRevisionForkFailsClosed() {
        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "mira-change-v1:1",
                true,
                Collections.singletonList(
                        snapshot("identifier", "identifier-a", 2, "{\"v\":1}")
                )
        ));
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                "mira-change-v1:1",
                "mira-change-v1:2",
                false,
                Collections.singletonList(
                        snapshot("identifier", "identifier-a", 2, "{\"v\":2}")
                )
        ));

        VerifiedChangeQuery.QueryResult result =
                new VerifiedChangeQuery(transport).queryLatest("identifier", 1);

        assertEquals(VerifiedChangeQuery.Status.PROTOCOL_FAILURE, result.status());
        assertEquals("protocol_error", result.errorCode());
        assertEquals(0, result.snapshots().size());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void unverifiedPageFailsClosed() {
        FakeTransport transport = new FakeTransport();
        transport.pages.add(new ReconnectCoordinator.ChangePage(
                null,
                "mira-change-v1:1",
                false,
                false,
                Collections.singletonList(
                        snapshot("identifier", "identifier-a", 1, "{\"v\":1}")
                )
        ));

        VerifiedChangeQuery.QueryResult result =
                new VerifiedChangeQuery(transport).queryLatest("identifier");

        assertEquals(VerifiedChangeQuery.Status.PROTOCOL_FAILURE, result.status());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void transportFailureDoesNotReturnPartialProjection() {
        FakeTransport transport = new FakeTransport();
        transport.failure = new ReconnectCoordinator.TransportException(
                "provider_unavailable",
                "synthetic outage"
        );

        VerifiedChangeQuery.QueryResult result =
                new VerifiedChangeQuery(transport).queryLatest("identifier");

        assertEquals(VerifiedChangeQuery.Status.TRANSPORT_FAILURE, result.status());
        assertEquals("provider_unavailable", result.errorCode());
        assertEquals(0, result.snapshots().size());
        assertNull(result.cursor());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void invalidDataClassFailsBeforeTransportRead() {
        FakeTransport transport = new FakeTransport();

        VerifiedChangeQuery.QueryResult result =
                new VerifiedChangeQuery(transport).queryLatest("bad class");

        assertEquals(VerifiedChangeQuery.Status.LOCAL_FAILURE, result.status());
        assertEquals(0, transport.readCalls);
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

    private static final class FakeTransport implements ReconnectCoordinator.Transport {
        final Deque<ReconnectCoordinator.ChangePage> pages = new ArrayDeque<>();
        int readCalls;
        int reconcileCalls;
        ReconnectCoordinator.TransportException failure;

        @Override
        public ReconnectCoordinator.RemoteCommandState reconcileCommand(
                OfflineSyncStateStore.CommandIntent command
        ) {
            reconcileCalls += 1;
            throw new AssertionError("passive verified query must not reconcile commands");
        }

        @Override
        public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit)
                throws ReconnectCoordinator.TransportException {
            readCalls += 1;
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
}
