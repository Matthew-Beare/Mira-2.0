package com.mira.client.core.sync;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import org.json.JSONObject;
import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Direct recovery/replay evidence for the explicit MOVE-001 Android facade. */
public final class MovementCommandFacadeTest {

    @Test
    public void explicitMoveStagesEventThenProjectionAndConvergesAcrossWorkerPasses()
            throws Exception {
        OfflineSyncStateStore store = newStore("movement-converges");
        FakeTransport transport = new FakeTransport();
        transport.eventMode = Mode.PENDING;
        transport.projectionMode = Mode.PENDING;
        MovementCommandFacade facade = facade(store, transport);
        MovementCommandFacade.MoveRequest request = request();

        MovementCommandFacade.MoveResult first = facade.move(request);
        assertEquals(MovementCommandFacade.Status.WAITING_EVENT, first.status());
        assertEquals(2, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
        assertEquals(Collections.singletonList("append_event"), transport.actions);

        List<OfflineSyncStateStore.QueuedCommand> pending = store.pendingCommands(128);
        assertEquals(2, pending.size());
        OfflineSyncStateStore.CommandIntent event = pending.get(0).command();
        OfflineSyncStateStore.CommandIntent projection = pending.get(1).command();
        assertEquals("append_event", event.action());
        assertEquals("inventory_state", event.dataClass());
        assertEquals("asset-001", event.resourceId());
        assertEquals("move-event-001", event.eventId());
        assertEquals("updated", event.eventType());
        assertNull(event.expectedRevision());
        JSONObject eventPayload = new JSONObject(new String(event.payload(), StandardCharsets.UTF_8));
        assertEquals("inventory_observation", eventPayload.getString("event_kind"));
        assertEquals(3, eventPayload.getInt("prior_inventory_revision"));
        assertEquals(4, eventPayload.getInt("resulting_inventory_revision"));
        assertEquals("loc-a", eventPayload.getString("prior_observed_location_id"));
        assertEquals("loc-b", eventPayload.getString("observed_location_id"));

        assertEquals("upsert", projection.action());
        assertEquals(Long.valueOf(3L), projection.expectedRevision());
        JSONObject projectionPayload = new JSONObject(
                new String(projection.payload(), StandardCharsets.UTF_8)
        );
        assertEquals("tracked", projectionPayload.getString("participation_state"));
        assertEquals("loc-b", projectionPayload.getString("observed_location_id"));
        assertEquals("loc-home", projectionPayload.getString("intended_location_id"));
        assertEquals("keep-note", projectionPayload.getString("note"));

        transport.eventMode = Mode.SUCCESS;
        MovementCommandFacade.MoveResult second = facade.move(request);
        assertEquals(MovementCommandFacade.Status.WAITING_PROJECTION, second.status());
        assertEquals(1, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        assertEquals("upsert", store.pendingCommands(128).get(0).command().action());

        transport.projectionMode = Mode.SUCCESS;
        MovementCommandFacade.MoveResult third = facade.move(request);
        assertEquals(MovementCommandFacade.Status.APPLIED, third.status());
        assertEquals(0, store.pendingCount());
        assertEquals(2, store.acknowledgedCount());
        OfflineSyncStateStore.ResourceSnapshot snapshot = third.canonicalSnapshot();
        assertNotNull(snapshot);
        assertEquals("inventory_state", snapshot.dataClass());
        assertEquals("asset-001", snapshot.resourceId());
        assertEquals(4L, snapshot.revision());
        assertArrayEquals(projection.payload(), snapshot.payload());
    }

    @Test
    public void exactReplayAfterBothAcknowledgementsUsesNoProviderIo() {
        OfflineSyncStateStore store = newStore("movement-replay");
        FakeTransport transport = new FakeTransport();
        transport.eventMode = Mode.SUCCESS;
        transport.projectionMode = Mode.SUCCESS;
        MovementCommandFacade facade = facade(store, transport);
        MovementCommandFacade.MoveRequest request = request();

        assertEquals(MovementCommandFacade.Status.APPLIED, facade.move(request).status());
        int calls = transport.actions.size();
        int changeCalls = transport.changeCalls;

        MovementCommandFacade.MoveResult replay = facade.move(request);
        assertEquals(MovementCommandFacade.Status.APPLIED, replay.status());
        assertEquals(calls, transport.actions.size());
        assertEquals(changeCalls, transport.changeCalls);
        assertEquals(0, store.pendingCount());
        assertEquals(2, store.acknowledgedCount());
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED,
                replay.eventEnqueueResult()
        );
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED,
                replay.projectionEnqueueResult()
        );
    }

    @Test
    public void eventCanSucceedWhileProjectionConflictRemainsRecoverableAndNeverReappendsEvent() {
        OfflineSyncStateStore store = newStore("movement-projection-conflict");
        FakeTransport transport = new FakeTransport();
        transport.eventMode = Mode.SUCCESS;
        transport.projectionMode = Mode.FAIL;
        MovementCommandFacade facade = facade(store, transport);
        MovementCommandFacade.MoveRequest request = request();

        MovementCommandFacade.MoveResult conflict = facade.move(request);
        assertEquals(MovementCommandFacade.Status.REMOTE_FAILURE, conflict.status());
        assertEquals("conflict", conflict.errorCode());
        assertEquals(1, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());
        assertEquals(2, transport.actions.size());
        assertEquals("append_event", transport.actions.get(0));
        assertEquals("upsert", transport.actions.get(1));

        transport.projectionMode = Mode.SUCCESS;
        MovementCommandFacade.MoveResult recovered = facade.move(request);
        assertEquals(MovementCommandFacade.Status.APPLIED, recovered.status());
        assertEquals(3, transport.actions.size());
        assertEquals("upsert", transport.actions.get(2));
        assertEquals(0, store.pendingCount());
        assertEquals(2, store.acknowledgedCount());
    }

    @Test
    public void earlierFifoCommandBlocksMoveBeforeItsEventGetsProviderIo() {
        OfflineSyncStateStore store = newStore("movement-fifo-block");
        OfflineSyncStateStore.CommandIntent earlier = new OfflineSyncStateStore.CommandIntent(
                "cmd-earlier",
                "user-001",
                "entity",
                "upsert",
                1,
                "mira-api-1",
                "other-001",
                "{\"value\":1}".getBytes(StandardCharsets.UTF_8),
                "idem-earlier",
                0L,
                null,
                null
        );
        store.enqueue(earlier);
        FakeTransport transport = new FakeTransport();
        transport.earlierPending = true;

        MovementCommandFacade.MoveResult result = facade(store, transport).move(request());
        assertEquals(MovementCommandFacade.Status.BLOCKED_BY_EARLIER_COMMAND, result.status());
        assertEquals("cmd-earlier", result.blockingCommandId());
        assertEquals(Collections.singletonList("earlier"), transport.actions);
        assertEquals(3, store.pendingCount());
        assertEquals(0, store.acknowledgedCount());
    }

    @Test
    public void acknowledgedProjectionWithWrongReadbackNeverBecomesApplied() {
        OfflineSyncStateStore store = newStore("movement-bad-readback");
        FakeTransport transport = new FakeTransport();
        transport.eventMode = Mode.SUCCESS;
        transport.projectionMode = Mode.SUCCESS;
        transport.badProjection = true;

        MovementCommandFacade.MoveResult result = facade(store, transport).move(request());
        assertEquals(MovementCommandFacade.Status.PROTOCOL_FAILURE, result.status());
        assertEquals("verified_projection_mismatch", result.errorCode());
        assertEquals(0, store.pendingCount());
        assertEquals(2, store.acknowledgedCount());
        assertNull(result.canonicalSnapshot());
    }

    private static MovementCommandFacade facade(
            OfflineSyncStateStore store,
            FakeTransport transport
    ) {
        return new MovementCommandFacade(
                store,
                new ReconnectCoordinator(store, transport)
        );
    }

    private static MovementCommandFacade.MoveRequest request() {
        return new MovementCommandFacade.MoveRequest(
                "user-001",
                "asset-001",
                "loc-b",
                "2026-09-15T21:00:00Z",
                "android_explicit_move",
                "move-event-001",
                "move-idem-001",
                3L,
                "loc-a",
                "2026-09-15T20:00:00Z",
                "loc-home",
                "keep-note",
                "scan-confirmed move"
        );
    }

    private static OfflineSyncStateStore newStore(String clientId) {
        return new OfflineSyncStateStore(
                clientId,
                new PassthroughCipher(),
                new MemoryBlobStore()
        );
    }

    private enum Mode {
        PENDING,
        SUCCESS,
        FAIL
    }

    private static final class FakeTransport implements ReconnectCoordinator.Transport {
        Mode eventMode = Mode.PENDING;
        Mode projectionMode = Mode.PENDING;
        boolean badProjection;
        boolean earlierPending;
        int changeCalls;
        final List<String> actions = new ArrayList<>();

        @Override
        public ReconnectCoordinator.RemoteCommandState reconcileCommand(
                OfflineSyncStateStore.CommandIntent command
        ) throws ReconnectCoordinator.TransportException {
            if ("cmd-earlier".equals(command.commandId())) {
                actions.add("earlier");
                if (earlierPending) {
                    return ReconnectCoordinator.RemoteCommandState.pending(
                            command.commandId(), command.idempotencyKey()
                    );
                }
            }
            actions.add(command.action());
            if ("append_event".equals(command.action())) {
                return state(command, eventMode, false);
            }
            if ("upsert".equals(command.action())) {
                return state(command, projectionMode, true);
            }
            throw new ReconnectCoordinator.TransportException(
                    "protocol_error", "unexpected synthetic action"
            );
        }

        private ReconnectCoordinator.RemoteCommandState state(
                OfflineSyncStateStore.CommandIntent command,
                Mode mode,
                boolean projection
        ) {
            if (mode == Mode.PENDING) {
                return ReconnectCoordinator.RemoteCommandState.pending(
                        command.commandId(), command.idempotencyKey()
                );
            }
            if (mode == Mode.FAIL) {
                return ReconnectCoordinator.RemoteCommandState.failed(
                        command.commandId(),
                        command.idempotencyKey(),
                        "conflict",
                        projection ? "stale inventory revision" : "event conflict"
                );
            }
            if (!projection) {
                return ReconnectCoordinator.RemoteCommandState.succeeded(
                        command.commandId(),
                        command.idempotencyKey(),
                        Collections.<OfflineSyncStateStore.ResourceSnapshot>emptyList()
                );
            }
            byte[] payload = command.payload();
            if (badProjection) {
                payload = ("{\"schema_version\":1,\"entity_uuid\":\"asset-001\","
                        + "\"participation_state\":\"tracked\","
                        + "\"intended_location_id\":\"loc-home\","
                        + "\"observed_location_id\":\"loc-wrong\","
                        + "\"observed_at\":\"2026-09-15T21:00:00Z\","
                        + "\"note\":\"keep-note\"}").getBytes(StandardCharsets.UTF_8);
            }
            return ReconnectCoordinator.RemoteCommandState.succeeded(
                    command.commandId(),
                    command.idempotencyKey(),
                    Collections.singletonList(
                            new OfflineSyncStateStore.ResourceSnapshot(
                                    command.dataClass(),
                                    command.resourceId(),
                                    command.expectedRevision() + 1,
                                    payload
                            )
                    )
            );
        }

        @Override
        public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit) {
            changeCalls += 1;
            return ReconnectCoordinator.ChangePage.verified(
                    cursor,
                    cursor == null ? "movement-cursor-0" : cursor,
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
            byte[] value = blobs.get(clientId);
            if (value == null) throw new IllegalStateException("missing synthetic blob");
            return value.clone();
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
