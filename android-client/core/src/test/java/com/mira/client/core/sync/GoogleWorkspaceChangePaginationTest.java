package com.mira.client.core.sync;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

public final class GoogleWorkspaceChangePaginationTest {
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
    public void truncatedVerifiedPageReportsMoreAvailable() throws Exception {
        FakeGateway gateway = gateway();
        gateway.tables.get("Changes").add(changeRow(1, 1, "{\"v\":1}"));
        gateway.tables.get("Changes").add(changeRow(2, 2, "{\"v\":2}"));

        ReconnectCoordinator.ChangePage page =
                new GoogleWorkspaceTransport(gateway).readChanges(null, 1);

        assertEquals("mira-change-v1:1", page.nextCursor());
        assertEquals(1, page.verifiedSnapshots().size());
        assertTrue(page.moreAvailable());
    }

    @Test
    public void exactlyFullTerminalPageDoesNotInventMoreData() throws Exception {
        FakeGateway gateway = gateway();
        gateway.tables.get("Changes").add(changeRow(1, 1, "{\"v\":1}"));

        ReconnectCoordinator.ChangePage page =
                new GoogleWorkspaceTransport(gateway).readChanges(null, 1);

        assertEquals("mira-change-v1:1", page.nextCursor());
        assertEquals(1, page.verifiedSnapshots().size());
        assertFalse(page.moreAvailable());
    }

    @Test
    public void incrementalTerminalPageClearsMoreAvailable() throws Exception {
        FakeGateway gateway = gateway();
        gateway.tables.get("Changes").add(changeRow(1, 1, "{\"v\":1}"));
        gateway.tables.get("Changes").add(changeRow(2, 2, "{\"v\":2}"));
        GoogleWorkspaceTransport transport = new GoogleWorkspaceTransport(gateway);

        ReconnectCoordinator.ChangePage first = transport.readChanges(null, 1);
        ReconnectCoordinator.ChangePage second =
                transport.readChanges(first.nextCursor(), 1);

        assertTrue(first.moreAvailable());
        assertFalse(second.moreAvailable());
        assertEquals("mira-change-v1:2", second.nextCursor());
        assertEquals(2L, second.verifiedSnapshots().get(0).revision());
    }

    @Test
    public void emptyStableProjectionIsTerminal() throws Exception {
        ReconnectCoordinator.ChangePage page =
                new GoogleWorkspaceTransport(gateway()).readChanges(null, 128);

        assertEquals("mira-change-v1:0", page.nextCursor());
        assertTrue(page.verifiedSnapshots().isEmpty());
        assertFalse(page.moreAvailable());
    }

    private static FakeGateway gateway() {
        FakeGateway gateway = new FakeGateway();
        ArrayList<List<Object>> changes = new ArrayList<>();
        changes.add(new ArrayList<>(CHANGE_HEADERS));
        gateway.tables.put("Changes", changes);
        return gateway;
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
                "2026-09-04T00:00:00.000Z",
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

    private static List<Object> row(Object... values) {
        return new ArrayList<>(Arrays.asList(values));
    }

    private static final class FakeGateway implements GoogleWorkspaceTransport.SheetsGateway {
        final Map<String, List<List<Object>>> tables = new HashMap<>();

        @Override
        public List<List<Object>> readTable(String tableName)
                throws GoogleWorkspaceTransport.GatewayException {
            List<List<Object>> table = tables.get(tableName);
            if (table == null) {
                throw new GoogleWorkspaceTransport.GatewayException(
                        "unexpected test table: " + tableName
                );
            }
            ArrayList<List<Object>> copy = new ArrayList<>();
            for (List<Object> row : table) {
                copy.add(new ArrayList<>(row));
            }
            return copy;
        }

        @Override
        public void appendRow(String tableName, List<Object> row) {
            throw new AssertionError("pagination test must not append provider rows");
        }
    }
}
