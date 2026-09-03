package com.mira.client.core.sync;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public final class GoogleWorkspaceTransportTest {
    private static final List<Object> COMMAND_HEADERS = row(
            "command_id",
            "subject_id",
            "data_class",
            "action",
            "api_major",
            "schema_version",
            "resource_id",
            "payload_json",
            "idempotency_key",
            "expected_revision",
            "submitted_at",
            "status",
            "result_json",
            "processed_at",
            "error_code",
            "error_message"
    );

    private static final List<Object> CHANGE_HEADERS = row(
            "change_seq",
            "change_id",
            "data_class",
            "resource_id",
            "revision",
            "payload_json",
            "recorded_at",
            "source_command_id",
            "readback_verified"
    );

    @Test
    public void exactCommandIntentAppendsOnceAndReadsPending() throws Exception {
        FakeGateway gateway = gateway();
        GoogleWorkspaceTransport transport = transport(gateway);

        ReconnectCoordinator.RemoteCommandState first = transport.reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.PENDING, first.status());
        assertEquals(1, gateway.appendCount);

        List<Object> written = gateway.tables.get("Commands").get(1);
        assertEquals("cmd-001", written.get(0));
        assertEquals("user-001", written.get(1));
        assertEquals("entity", written.get(2));
        assertEquals("upsert", written.get(3));
        assertEquals(1, written.get(4));
        assertEquals("mira-api-1", written.get(5));
        assertEquals("entity-001", written.get(6));
        assertEquals("{\"a\":1,\"b\":2}", written.get(7));
        assertEquals("idem-001", written.get(8));
        assertEquals(0L, written.get(9));
        assertEquals("2026-09-02T20:00:00.000Z", written.get(10));
        assertEquals("pending", written.get(11));
        assertEquals(16, written.size());

        ReconnectCoordinator.RemoteCommandState second = transport.reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.PENDING, second.status());
        assertEquals(1, gateway.appendCount);
    }

    @Test
    public void ambiguousAppendThatActuallyLandedConvergesWithoutSecondAppend() throws Exception {
        FakeGateway gateway = gateway();
        gateway.appendThenThrow = true;
        GoogleWorkspaceTransport transport = transport(gateway);

        ReconnectCoordinator.RemoteCommandState state = transport.reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.PENDING, state.status());
        assertEquals(1, gateway.appendCount);
        assertEquals(2, gateway.tables.get("Commands").size());

        gateway.appendThenThrow = false;
        transport.reconcileCommand(command());
        assertEquals(1, gateway.appendCount);
        assertEquals(2, gateway.tables.get("Commands").size());
    }

    @Test
    public void exactDuplicatePhysicalRowsRemainOneLogicalPendingCommand() throws Exception {
        FakeGateway gateway = gateway();
        List<Object> exact = commandProviderRow("pending", "", "", "");
        List<Object> duplicate = new ArrayList<>(exact);
        duplicate.set(10, "2026-09-02T20:00:05.000Z");
        gateway.tables.get("Commands").add(exact);
        gateway.tables.get("Commands").add(duplicate);

        ReconnectCoordinator.RemoteCommandState state = transport(gateway).reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.PENDING, state.status());
        assertEquals(0, gateway.appendCount);
    }

    @Test
    public void duplicateCommandIdWithDifferentMaterialFailsClosed() {
        FakeGateway gateway = gateway();
        gateway.tables.get("Commands").add(commandProviderRow("pending", "", "", ""));
        List<Object> conflicting = commandProviderRow("pending", "", "", "");
        conflicting.set(7, "{\"a\":9,\"b\":2}");
        gateway.tables.get("Commands").add(conflicting);

        ReconnectCoordinator.TransportException error = assertThrows(
                ReconnectCoordinator.TransportException.class,
                () -> transport(gateway).reconcileCommand(command())
        );
        assertEquals("protocol_error", error.code());
        assertEquals(0, gateway.appendCount);
    }

    @Test
    public void verifiedSucceededRowReturnsExactCanonicalSnapshot() throws Exception {
        FakeGateway gateway = gateway();
        String result = "{"
                + "\"authority_id\":\"google-sheets-m0\","
                + "\"command_id\":\"cmd-001\","
                + "\"event\":null,"
                + "\"idempotent_replay\":false,"
                + "\"readback_verified\":true,"
                + "\"record\":{"
                + "\"payload\":{\"b\":2,\"a\":1},"
                + "\"resource_id\":\"entity-001\","
                + "\"resource_type\":\"entity\","
                + "\"revision\":1"
                + "}}";
        gateway.tables.get("Commands").add(commandProviderRow("succeeded", result, "", ""));

        ReconnectCoordinator.RemoteCommandState state = transport(gateway).reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.SUCCEEDED, state.status());
        assertTrue(state.readbackVerified());
        assertEquals(1, state.verifiedSnapshots().size());
        OfflineSyncStateStore.ResourceSnapshot snapshot = state.verifiedSnapshots().get(0);
        assertEquals("entity", snapshot.dataClass());
        assertEquals("entity-001", snapshot.resourceId());
        assertEquals(1L, snapshot.revision());
        assertArrayEquals(
                "{\"a\":1,\"b\":2}".getBytes(StandardCharsets.UTF_8),
                snapshot.payload()
        );
    }

    @Test
    public void succeededRowWithoutVerifiedReadbackIsProtocolFailure() {
        FakeGateway gateway = gateway();
        String result = "{"
                + "\"command_id\":\"cmd-001\","
                + "\"readback_verified\":false,"
                + "\"record\":{"
                + "\"payload\":{\"a\":1,\"b\":2},"
                + "\"resource_id\":\"entity-001\","
                + "\"resource_type\":\"entity\","
                + "\"revision\":1"
                + "}}";
        gateway.tables.get("Commands").add(commandProviderRow("succeeded", result, "", ""));

        ReconnectCoordinator.TransportException error = assertThrows(
                ReconnectCoordinator.TransportException.class,
                () -> transport(gateway).reconcileCommand(command())
        );
        assertEquals("protocol_error", error.code());
    }

    @Test
    public void failedRowMapsWithoutPretendingItSucceeded() throws Exception {
        FakeGateway gateway = gateway();
        gateway.tables.get("Commands").add(
                commandProviderRow("failed", "", "conflict", "expected revision is stale")
        );

        ReconnectCoordinator.RemoteCommandState state = transport(gateway).reconcileCommand(command());
        assertEquals(ReconnectCoordinator.RemoteCommandStatus.FAILED, state.status());
        assertEquals("conflict", state.errorCode());
        assertEquals("expected revision is stale", state.errorMessage());
        assertTrue(state.verifiedSnapshots().isEmpty());
    }

    @Test
    public void initialAndIncrementalChangePagesUseOpaqueContiguousCursor() throws Exception {
        FakeGateway gateway = gateway();
        gateway.tables.get("Changes").add(changeRow(1, 1, "{\"a\":1}"));
        gateway.tables.get("Changes").add(changeRow(2, 2, "{\"a\":2}"));
        GoogleWorkspaceTransport transport = transport(gateway);

        ReconnectCoordinator.ChangePage first = transport.readChanges(null, 1);
        assertEquals(null, first.fromCursor());
        assertEquals("mira-change-v1:1", first.nextCursor());
        assertTrue(first.readbackVerified());
        assertEquals(1, first.verifiedSnapshots().size());
        assertEquals(1L, first.verifiedSnapshots().get(0).revision());

        ReconnectCoordinator.ChangePage second = transport.readChanges("mira-change-v1:1", 128);
        assertEquals("mira-change-v1:1", second.fromCursor());
        assertEquals("mira-change-v1:2", second.nextCursor());
        assertEquals(1, second.verifiedSnapshots().size());
        assertEquals(2L, second.verifiedSnapshots().get(0).revision());

        ReconnectCoordinator.ChangePage empty = transport.readChanges("mira-change-v1:2", 128);
        assertEquals("mira-change-v1:2", empty.nextCursor());
        assertTrue(empty.verifiedSnapshots().isEmpty());
    }

    @Test
    public void emptyInitialProjectionAdvancesToStableZeroCursor() throws Exception {
        ReconnectCoordinator.ChangePage page = transport(gateway()).readChanges(null, 128);
        assertEquals("mira-change-v1:0", page.nextCursor());
        assertTrue(page.verifiedSnapshots().isEmpty());
    }

    @Test
    public void changeSequenceGapFailsClosed() {
        FakeGateway gateway = gateway();
        gateway.tables.get("Changes").add(changeRow(2, 1, "{\"a\":1}"));

        ReconnectCoordinator.TransportException error = assertThrows(
                ReconnectCoordinator.TransportException.class,
                () -> transport(gateway).readChanges(null, 128)
        );
        assertEquals("protocol_error", error.code());
    }

    @Test
    public void unverifiedOrTamperedChangeFailsClosed() {
        FakeGateway unverified = gateway();
        List<Object> row = changeRow(1, 1, "{\"a\":1}");
        row.set(8, false);
        unverified.tables.get("Changes").add(row);
        assertEquals(
                "protocol_error",
                assertThrows(
                        ReconnectCoordinator.TransportException.class,
                        () -> transport(unverified).readChanges(null, 128)
                ).code()
        );

        FakeGateway tampered = gateway();
        List<Object> badHash = changeRow(1, 1, "{\"a\":1}");
        badHash.set(1, "0".repeat(64));
        tampered.tables.get("Changes").add(badHash);
        assertEquals(
                "protocol_error",
                assertThrows(
                        ReconnectCoordinator.TransportException.class,
                        () -> transport(tampered).readChanges(null, 128)
                ).code()
        );
    }

    @Test
    public void malformedCursorAndGatewayFailurePreserveTransportTruth() {
        GoogleWorkspaceTransport transport = transport(gateway());
        assertEquals(
                "protocol_error",
                assertThrows(
                        ReconnectCoordinator.TransportException.class,
                        () -> transport.readChanges("2", 128)
                ).code()
        );

        FakeGateway failing = gateway();
        failing.failReads = true;
        ReconnectCoordinator.TransportException error = assertThrows(
                ReconnectCoordinator.TransportException.class,
                () -> transport(failing).reconcileCommand(command())
        );
        assertEquals("workspace_read_failed", error.code());
    }

    @Test
    public void appendEventAndNullExpectedRevisionAreRejectedBeforeProviderWrite() {
        FakeGateway gateway = gateway();
        OfflineSyncStateStore.CommandIntent append = new OfflineSyncStateStore.CommandIntent(
                "cmd-event",
                "user-001",
                "entity",
                "append_event",
                1,
                "mira-api-1",
                "entity-001",
                "{\"a\":1}".getBytes(StandardCharsets.UTF_8),
                "idem-event",
                null,
                "event-001",
                "updated"
        );
        assertEquals(
                "unsupported_command",
                assertThrows(
                        ReconnectCoordinator.TransportException.class,
                        () -> transport(gateway).reconcileCommand(append)
                ).code()
        );
        assertEquals(0, gateway.appendCount);
    }

    private static GoogleWorkspaceTransport transport(FakeGateway gateway) {
        return new GoogleWorkspaceTransport(
                gateway,
                () -> "2026-09-02T20:00:00.000Z"
        );
    }

    private static OfflineSyncStateStore.CommandIntent command() {
        return new OfflineSyncStateStore.CommandIntent(
                "cmd-001",
                "user-001",
                "entity",
                "upsert",
                1,
                "mira-api-1",
                "entity-001",
                "{\"b\":2,\"a\":1}".getBytes(StandardCharsets.UTF_8),
                "idem-001",
                0L,
                null,
                null
        );
    }

    private static FakeGateway gateway() {
        FakeGateway gateway = new FakeGateway();
        gateway.tables.put("Commands", table(COMMAND_HEADERS));
        gateway.tables.put("Changes", table(CHANGE_HEADERS));
        return gateway;
    }

    private static List<Object> commandProviderRow(
            String status,
            String resultJson,
            String errorCode,
            String errorMessage
    ) {
        return row(
                "cmd-001",
                "user-001",
                "entity",
                "upsert",
                1,
                "mira-api-1",
                "entity-001",
                "{\"a\":1,\"b\":2}",
                "idem-001",
                0,
                "2026-09-02T20:00:00.000Z",
                status,
                resultJson,
                status.equals("pending") ? "" : "2026-09-02T20:01:00.000Z",
                errorCode,
                errorMessage
        );
    }

    private static List<Object> changeRow(long sequence, long revision, String payload)
            throws Exception {
        return row(
                sequence,
                changeId("entity", "entity-001", revision, payload),
                "entity",
                "entity-001",
                revision,
                payload,
                "2026-09-02T20:01:00.000Z",
                "cmd-001",
                true
        );
    }

    private static String changeId(
            String dataClass,
            String resourceId,
            long revision,
            String canonicalPayload
    ) throws Exception {
        String material = "{\"data_class\":\"" + dataClass + "\",\"payload\":"
                + canonicalPayload + ",\"resource_id\":\"" + resourceId
                + "\",\"revision\":" + revision + "}";
        byte[] digest = MessageDigest.getInstance("SHA-256")
                .digest(material.getBytes(StandardCharsets.UTF_8));
        StringBuilder result = new StringBuilder();
        for (byte item : digest) {
            result.append(String.format(Locale.US, "%02x", item & 0xff));
        }
        return result.toString();
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
        boolean appendThenThrow;
        boolean failReads;

        @Override
        public List<List<Object>> readTable(String tableName)
                throws GoogleWorkspaceTransport.GatewayException {
            if (failReads) {
                throw new GoogleWorkspaceTransport.GatewayException("synthetic read failure");
            }
            List<List<Object>> source = tables.get(tableName);
            assertNotNull(source);
            ArrayList<List<Object>> copy = new ArrayList<>();
            for (List<Object> row : source) {
                copy.add(new ArrayList<>(row));
            }
            return copy;
        }

        @Override
        public void appendRow(String tableName, List<Object> row)
                throws GoogleWorkspaceTransport.GatewayException {
            appendCount += 1;
            tables.get(tableName).add(new ArrayList<>(row));
            if (appendThenThrow) {
                throw new GoogleWorkspaceTransport.GatewayException(
                        "synthetic ambiguous append failure"
                );
            }
        }
    }
}
