package com.mira.client.googleworkspace;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertThrows;

import com.mira.client.core.sync.GoogleWorkspaceTransport;

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class GoogleWorkspaceBindingTest {
    private static final String SHEET_ID = "synthetic_MIRA_sheet_12345";
    private static final String TOKEN = "ephemeral-test-token";

    @Test
    public void exactWorkspaceContractBindsWithoutAnyWrite() throws Exception {
        FakeGateway gateway = validGateway();
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> {
            assertEquals(SHEET_ID, id);
            assertEquals(TOKEN, token);
            return gateway;
        });

        GoogleWorkspaceBinding.Binding result = binding.bind(authorized());

        assertEquals(SHEET_ID, result.spreadsheetId());
        assertNotNull(result.transport());
        assertEquals(Arrays.asList("Metadata", "Commands", "Changes"), gateway.reads);
        assertEquals(0, gateway.appends);
    }

    @Test
    public void missingQueuedWriterMetadataFailsClosedBeforeTransportBinding() {
        FakeGateway gateway = validGateway();
        gateway.tables.put("Metadata", metadataWithout("mutation_mode"));
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> gateway);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_protocol_invalid", error.code());
        assertEquals(0, gateway.appends);
    }

    @Test
    public void wrongWriterModelFailsClosed() {
        FakeGateway gateway = validGateway();
        List<List<Object>> rows = metadataRows();
        replaceMetadata(rows, "writer_model", "queued_writer");
        gateway.tables.put("Metadata", rows);
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> gateway);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_protocol_invalid", error.code());
        assertEquals(0, gateway.appends);
    }

    @Test
    public void duplicateMetadataKeyFailsClosed() {
        FakeGateway gateway = validGateway();
        List<List<Object>> rows = metadataRows();
        rows.add(Arrays.asList("schema_version", "mira-structured-state-v1"));
        gateway.tables.put("Metadata", rows);
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> gateway);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_protocol_invalid", error.code());
        assertEquals(0, gateway.appends);
    }

    @Test
    public void wrongCommandsHeaderFailsClosed() {
        FakeGateway gateway = validGateway();
        List<Object> header = new ArrayList<>(commandHeaders());
        header.set(0, "wrong_command_id");
        gateway.tables.put("Commands", Collections.singletonList(header));
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> gateway);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_protocol_invalid", error.code());
        assertEquals(0, gateway.appends);
    }

    @Test
    public void wrongChangesHeaderFailsClosed() {
        FakeGateway gateway = validGateway();
        List<Object> header = new ArrayList<>(changeHeaders());
        header.remove(header.size() - 1);
        gateway.tables.put("Changes", Collections.singletonList(header));
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> gateway);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_protocol_invalid", error.code());
        assertEquals(0, gateway.appends);
    }

    @Test
    public void providerReadFailureMapsToUnavailableAndNeverWrites() {
        FakeGateway gateway = validGateway();
        gateway.failOn = "Metadata";
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> gateway);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_provider_unavailable", error.code());
        assertEquals(0, gateway.appends);
    }

    @Test
    public void nullGatewayFactoryResultFailsClosed() {
        GoogleWorkspaceBinding binding = new GoogleWorkspaceBinding((id, token) -> null);

        GoogleWorkspaceBinding.BindingException error = assertThrows(
                GoogleWorkspaceBinding.BindingException.class,
                () -> binding.bind(authorized())
        );
        assertEquals("workspace_gateway_invalid", error.code());
    }

    private static GoogleWorkspaceAuthorization.AuthorizedWorkspace authorized() {
        return new GoogleWorkspaceAuthorization.AuthorizedWorkspace(TOKEN, SHEET_ID);
    }

    private static FakeGateway validGateway() {
        FakeGateway gateway = new FakeGateway();
        gateway.tables.put("Metadata", metadataRows());
        gateway.tables.put("Commands", Collections.singletonList(commandHeaders()));
        gateway.tables.put("Changes", Collections.singletonList(changeHeaders()));
        return gateway;
    }

    private static List<List<Object>> metadataRows() {
        ArrayList<List<Object>> rows = new ArrayList<>();
        rows.add(Arrays.asList("Key", "Value"));
        rows.add(Arrays.asList("schema_version", "mira-structured-state-v1"));
        rows.add(Arrays.asList("store_role", "personal_google_starter"));
        rows.add(Arrays.asList("adapter_contract", "STORE-001"));
        rows.add(Arrays.asList("writer_model", "single_writer"));
        rows.add(Arrays.asList("mutation_mode", "queued_writer"));
        return rows;
    }

    private static List<List<Object>> metadataWithout(String key) {
        List<List<Object>> rows = metadataRows();
        rows.removeIf(row -> row.size() > 0 && key.equals(String.valueOf(row.get(0))));
        return rows;
    }

    private static void replaceMetadata(List<List<Object>> rows, String key, String value) {
        for (int index = 1; index < rows.size(); index++) {
            if (key.equals(String.valueOf(rows.get(index).get(0)))) {
                rows.set(index, Arrays.asList(key, value));
                return;
            }
        }
        throw new AssertionError("metadata key not found: " + key);
    }

    private static List<Object> commandHeaders() {
        return new ArrayList<>(Arrays.asList(
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
        ));
    }

    private static List<Object> changeHeaders() {
        return new ArrayList<>(Arrays.asList(
                "change_seq",
                "change_id",
                "data_class",
                "resource_id",
                "revision",
                "payload_json",
                "recorded_at",
                "source_command_id",
                "readback_verified"
        ));
    }

    private static final class FakeGateway implements GoogleWorkspaceTransport.SheetsGateway {
        final Map<String, List<List<Object>>> tables = new LinkedHashMap<>();
        final List<String> reads = new ArrayList<>();
        int appends;
        String failOn;

        @Override
        public List<List<Object>> readTable(String tableName)
                throws GoogleWorkspaceTransport.GatewayException {
            reads.add(tableName);
            if (tableName.equals(failOn)) {
                throw new GoogleWorkspaceTransport.GatewayException("synthetic provider failure");
            }
            List<List<Object>> rows = tables.get(tableName);
            return rows == null ? Collections.emptyList() : rows;
        }

        @Override
        public void appendRow(String tableName, List<Object> row) {
            appends += 1;
        }
    }
}
