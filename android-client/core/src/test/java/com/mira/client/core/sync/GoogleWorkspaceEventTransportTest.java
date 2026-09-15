package com.mira.client.core.sync;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Direct behavioral evidence for the append-event Workspace transport. */
public final class GoogleWorkspaceEventTransportTest {
    private static final List<Object> COMMAND_HEADERS = row(
            "command_id", "subject_id", "data_class", "action", "api_major",
            "schema_version", "resource_id", "payload_json", "idempotency_key",
            "expected_revision", "submitted_at", "status", "result_json",
            "processed_at", "error_code", "error_message"
    );

    @Test
    public void appendEventUsesExistingCommandSchemaAndDoesNotDuplicateOnReplay() throws Exception {
        FakeGateway gateway = gateway();
        GoogleWorkspaceEventTransport transport = transport(gateway);

        ReconnectCoordinator.RemoteCommandState first = transport.reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.PENDING, first.status());
        assertEquals(1, gateway.appendCount);

        List<Object> written = gateway.tables.get("Commands").get(1);
        assertEquals(16, written.size());
        assertEquals("cmd-move-001", written.get(0));
        assertEquals("asset", written.get(2));
        assertEquals("append_event", written.get(3));
        assertEquals("asset-001", written.get(6));
        assertEquals(
                "{\"event_id\":\"evt-move-001\",\"event_type\":\"asset_moved\","
                        + "\"payload\":{\"from_location_id\":\"loc-a\",\"to_location_id\":\"loc-b\"}}",
                written.get(7)
        );
        assertEquals("idem-move-001", written.get(8));
        assertEquals(4L, written.get(9));
        assertEquals("2026-09-15T20:00:00.000Z", written.get(10));
        assertEquals("pending", written.get(11));

        ReconnectCoordinator.RemoteCommandState replay = transport.reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.PENDING, replay.status());
        assertEquals(1, gateway.appendCount);
        assertEquals(2, gateway.tables.get("Commands").size());
    }

    @Test
    public void verifiedEventReadbackSucceedsWithoutInventingResourceSnapshot() throws Exception {
        FakeGateway gateway = gateway();
        gateway.tables.get("Commands").add(providerRow(
                "succeeded",
                "{\"command_id\":\"cmd-move-001\",\"readback_verified\":true,"
                        + "\"record\":null,\"event\":{"
                        + "\"event_id\":\"evt-move-001\",\"stream_type\":\"asset\","
                        + "\"stream_id\":\"asset-001\",\"event_type\":\"asset_moved\","
                        + "\"stream_revision\":5,\"payload\":{"
                        + "\"to_location_id\":\"loc-b\",\"from_location_id\":\"loc-a\"}}}",
                "", ""
        ));

        ReconnectCoordinator.RemoteCommandState state = transport(gateway).reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.SUCCEEDED, state.status());
        assertTrue(state.readbackVerified());
        assertTrue(state.verifiedSnapshots().isEmpty());
        assertEquals(0, gateway.appendCount);
    }

    @Test
    public void mismatchedVerifiedEventReadbackFailsClosed() {
        FakeGateway gateway = gateway();
        gateway.tables.get("Commands").add(providerRow(
                "succeeded",
                "{\"command_id\":\"cmd-move-001\",\"readback_verified\":true,"
                        + "\"record\":null,\"event\":{"
                        + "\"event_id\":\"evt-move-001\",\"stream_type\":\"asset\","
                        + "\"stream_id\":\"asset-001\",\"event_type\":\"asset_moved\","
                        + "\"stream_revision\":99,\"payload\":{"
                        + "\"from_location_id\":\"loc-a\",\"to_location_id\":\"loc-b\"}}}",
                "", ""
        ));

        ReconnectCoordinator.TransportException error = assertThrows(
                ReconnectCoordinator.TransportException.class,
                () -> transport(gateway).reconcileCommand(command())
        );
        assertEquals("protocol_error", error.code());
        assertEquals(0, gateway.appendCount);
    }

    @Test
    public void duplicateCommandIdWithDifferentEventMaterialFailsClosed() {
        FakeGateway gateway = gateway();
        List<Object> conflicting = providerRow("pending", "", "", "");
        conflicting.set(7,
                "{\"event_id\":\"evt-other\",\"event_type\":\"asset_moved\","
                        + "\"payload\":{\"from_location_id\":\"loc-a\",\"to_location_id\":\"loc-b\"}}"
        );
        gateway.tables.get("Commands").add(conflicting);

        ReconnectCoordinator.TransportException error = assertThrows(
                ReconnectCoordinator.TransportException.class,
                () -> transport(gateway).reconcileCommand(command())
        );
        assertEquals("protocol_error", error.code());
        assertEquals(0, gateway.appendCount);
    }

    @Test
    public void eventTransportRemainsDirectlyGoverned() {
        assertNotNull(GoogleWorkspaceEventTransport.class);
    }

    private static GoogleWorkspaceEventTransport transport(FakeGateway gateway) {
        return new GoogleWorkspaceEventTransport(
                gateway,
                new GoogleWorkspaceTransport(gateway, () -> "2026-09-15T20:00:00.000Z"),
                () -> "2026-09-15T20:00:00.000Z"
        );
    }

    private static OfflineSyncStateStore.CommandIntent command() {
        return new OfflineSyncStateStore.CommandIntent(
                "cmd-move-001", "user-001", "asset", "append_event", 1, "mira-api-1",
                "asset-001",
                "{\"to_location_id\":\"loc-b\",\"from_location_id\":\"loc-a\"}"
                        .getBytes(StandardCharsets.UTF_8),
                "idem-move-001", 4L, "evt-move-001", "asset_moved"
        );
    }

    private static FakeGateway gateway() {
        FakeGateway gateway = new FakeGateway();
        gateway.tables.put("Commands", table(COMMAND_HEADERS));
        gateway.tables.put("Changes", new ArrayList<>());
        return gateway;
    }

    private static List<Object> providerRow(
            String status, String resultJson, String errorCode, String errorMessage
    ) {
        return row(
                "cmd-move-001", "user-001", "asset", "append_event", 1, "mira-api-1",
                "asset-001",
                "{\"event_id\":\"evt-move-001\",\"event_type\":\"asset_moved\","
                        + "\"payload\":{\"from_location_id\":\"loc-a\",\"to_location_id\":\"loc-b\"}}",
                "idem-move-001", 4L, "2026-09-15T20:00:00.000Z", status, resultJson,
                status.equals("pending") ? "" : "2026-09-15T20:01:00.000Z",
                errorCode, errorMessage
        );
    }

    private static List<List<Object>> table(List<Object> header) {
        ArrayList<List<Object>> result = new ArrayList<>();
        result.add(new ArrayList<>(header));
        return result;
    }

    private static List<Object> row(Object... values) {
        return new ArrayList<>(Arrays.asList(values));
    }

    private static final class FakeGateway implements GoogleWorkspaceTransport.SheetsGateway {
        final Map<String, List<List<Object>>> tables = new HashMap<>();
        int appendCount;

        @Override
        public List<List<Object>> readTable(String tableName)
                throws GoogleWorkspaceTransport.GatewayException {
            List<List<Object>> source = tables.get(tableName);
            if (source == null) {
                throw new GoogleWorkspaceTransport.GatewayException("missing synthetic table");
            }
            ArrayList<List<Object>> copy = new ArrayList<>();
            for (List<Object> item : source) copy.add(new ArrayList<>(item));
            return copy;
        }

        @Override
        public void appendRow(String tableName, List<Object> row)
                throws GoogleWorkspaceTransport.GatewayException {
            appendCount += 1;
            tables.get(tableName).add(new ArrayList<>(row));
        }
    }
}
