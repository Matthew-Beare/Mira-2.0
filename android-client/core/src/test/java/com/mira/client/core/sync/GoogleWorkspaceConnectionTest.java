package com.mira.client.core.sync;

import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.fail;

public final class GoogleWorkspaceConnectionTest {
    private static final String FILE_ID = "miraStarterFile_12345";
    private static final String TOKEN = "token-not-persisted";

    @Test
    public void pickerGrantBindsExactVerifiedWorkspaceWithoutTokenPersistence() throws Exception {
        FakeApi api = FakeApi.valid();
        GoogleWorkspaceConnection connection = new GoogleWorkspaceConnection(api);

        GoogleWorkspaceConnection.VerifiedBinding binding = connection.connect(
                new GoogleWorkspaceConnection.PickerGrant(TOKEN, Collections.singletonList(FILE_ID))
        );

        assertEquals(FILE_ID, binding.spreadsheetId());
        assertEquals("MIRA Personal Starter", binding.displayName());
        assertEquals("mira-structured-state-v1", binding.schemaVersion());
        assertEquals("queued_writer", binding.mutationMode());
        assertEquals("ready", binding.readinessCode());
        assertFalse(binding.toString().contains(TOKEN));
        assertEquals(Arrays.asList(
                GoogleWorkspaceConnection.METADATA_RANGE,
                GoogleWorkspaceConnection.COMMAND_HEADER_RANGE,
                GoogleWorkspaceConnection.CHANGE_HEADER_RANGE
        ), api.ranges);
    }

    @Test
    public void pickerGrantRejectsMissingOrMultipleSelections() throws Exception {
        GoogleWorkspaceConnection connection = new GoogleWorkspaceConnection(FakeApi.valid());
        expectCode("picker_selection_invalid", () -> connection.connect(
                new GoogleWorkspaceConnection.PickerGrant(TOKEN, Collections.emptyList())
        ));
        expectCode("picker_selection_invalid", () -> connection.connect(
                new GoogleWorkspaceConnection.PickerGrant(
                        TOKEN,
                        Arrays.asList(FILE_ID, "otherMiraFile_12345")
                )
        ));
    }

    @Test
    public void rejectsNonSheetTrashedOrReadOnlyCandidate() throws Exception {
        FakeApi wrongType = FakeApi.valid();
        wrongType.file = new GoogleWorkspaceConnection.FileMetadata(
                FILE_ID, "MIRA", "application/pdf", false, true
        );
        expectCode("workspace_type_mismatch", () -> connect(wrongType));

        FakeApi trashed = FakeApi.valid();
        trashed.file = new GoogleWorkspaceConnection.FileMetadata(
                FILE_ID, "MIRA", GoogleWorkspaceConnection.SPREADSHEET_MIME_TYPE, true, true
        );
        expectCode("workspace_unavailable", () -> connect(trashed));

        FakeApi readOnly = FakeApi.valid();
        readOnly.file = new GoogleWorkspaceConnection.FileMetadata(
                FILE_ID, "MIRA", GoogleWorkspaceConnection.SPREADSHEET_MIME_TYPE, false, false
        );
        expectCode("workspace_read_only", () -> connect(readOnly));
    }

    @Test
    public void rejectsMetadataThatIsNotCleanPersonalQueuedWorkspace() throws Exception {
        FakeApi legacy = FakeApi.valid();
        legacy.metadata = metadataRows("environment", "legacy_production");
        expectCode("workspace_schema_mismatch", () -> connect(legacy));
    }

    @Test
    public void validDirectWriterBindsButDoesNotClaimSharedWriterReadiness() throws Exception {
        FakeApi api = FakeApi.valid();
        api.metadata = metadataRows("mutation_mode", "direct_single_writer");

        GoogleWorkspaceConnection.VerifiedBinding binding = connect(api);

        assertEquals("direct_single_writer", binding.mutationMode());
        assertEquals("needs_shared_writer_activation", binding.readinessCode());
        assertEquals(Collections.singletonList(GoogleWorkspaceConnection.METADATA_RANGE), api.ranges);
    }

    @Test
    public void rejectsDuplicateMetadataKeys() throws Exception {
        FakeApi api = FakeApi.valid();
        api.metadata = new ArrayList<>(api.metadata);
        api.metadata.add(Arrays.asList("schema_version", "mira-structured-state-v1"));
        expectCode("workspace_schema_mismatch", () -> connect(api));
    }

    @Test
    public void rejectsTransportHeaderDriftBeforeReady() throws Exception {
        FakeApi api = FakeApi.valid();
        api.commands = new ArrayList<>(api.commands);
        api.commands.set(0, new ArrayList<>(api.commands.get(0)));
        api.commands.get(0).set(0, "wrong_command_header");
        expectCode("workspace_schema_mismatch", () -> connect(api));
    }

    @Test
    public void revalidateUsesFreshTokenAndSameProviderBinding() throws Exception {
        FakeApi api = FakeApi.valid();
        GoogleWorkspaceConnection connection = new GoogleWorkspaceConnection(api);
        GoogleWorkspaceConnection.VerifiedBinding initial = connection.connect(
                new GoogleWorkspaceConnection.PickerGrant(TOKEN, Collections.singletonList(FILE_ID))
        );
        api.tokens.clear();

        GoogleWorkspaceConnection.VerifiedBinding refreshed = connection.revalidate(initial, "fresh-token");

        assertEquals(FILE_ID, refreshed.spreadsheetId());
        assertEquals(Arrays.asList("fresh-token", "fresh-token", "fresh-token", "fresh-token"), api.tokens);
    }

    @Test
    public void providerAuthorizationFailureIsPreservedAsConnectionState() throws Exception {
        FakeApi api = FakeApi.valid();
        api.failure = new GoogleWorkspaceConnection.ProviderException(
                "authorization_expired", "expired"
        );
        expectCode("authorization_expired", () -> connect(api));
    }

    private static GoogleWorkspaceConnection.VerifiedBinding connect(FakeApi api) throws Exception {
        return new GoogleWorkspaceConnection(api).connect(
                new GoogleWorkspaceConnection.PickerGrant(TOKEN, Collections.singletonList(FILE_ID))
        );
    }

    private static List<List<Object>> metadataRows(String overrideKey, String overrideValue) {
        Map<String, String> values = new HashMap<>();
        values.put("schema_version", "mira-structured-state-v1");
        values.put("store_role", "personal_google_starter");
        values.put("environment", "mira_2_personal_clean");
        values.put("data_policy", "clean_starter_only");
        values.put("adapter_contract", "STORE-001");
        values.put("writer_model", "single_writer");
        values.put("mutation_mode", "queued_writer");
        if (overrideKey != null) {
            values.put(overrideKey, overrideValue);
        }
        List<List<Object>> rows = new ArrayList<>();
        rows.add(Arrays.asList("Key", "Value"));
        for (String key : Arrays.asList(
                "schema_version", "store_role", "environment", "data_policy",
                "adapter_contract", "writer_model", "mutation_mode"
        )) {
            rows.add(Arrays.asList(key, values.get(key)));
        }
        return rows;
    }

    private interface CheckedRunnable {
        void run() throws Exception;
    }

    private static void expectCode(String expected, CheckedRunnable runnable) throws Exception {
        try {
            runnable.run();
            fail("expected ConnectionException " + expected);
        } catch (GoogleWorkspaceConnection.ConnectionException exc) {
            assertEquals(expected, exc.code());
        }
    }

    private static final class FakeApi implements GoogleWorkspaceConnection.WorkspaceApi {
        GoogleWorkspaceConnection.FileMetadata file;
        List<List<Object>> metadata;
        List<List<Object>> commands;
        List<List<Object>> changes;
        GoogleWorkspaceConnection.ProviderException failure;
        final List<String> ranges = new ArrayList<>();
        final List<String> tokens = new ArrayList<>();

        static FakeApi valid() {
            FakeApi api = new FakeApi();
            api.file = new GoogleWorkspaceConnection.FileMetadata(
                    FILE_ID,
                    "MIRA Personal Starter",
                    GoogleWorkspaceConnection.SPREADSHEET_MIME_TYPE,
                    false,
                    true
            );
            api.metadata = metadataRows(null, null);
            api.commands = Collections.singletonList(Arrays.asList(
                    "command_id", "subject_id", "data_class", "action", "api_major",
                    "schema_version", "resource_id", "payload_json", "idempotency_key",
                    "expected_revision", "submitted_at", "status", "result_json", "processed_at",
                    "error_code", "error_message"
            ));
            api.changes = Collections.singletonList(Arrays.asList(
                    "change_seq", "change_id", "data_class", "resource_id", "revision",
                    "payload_json", "recorded_at", "source_command_id", "readback_verified"
            ));
            return api;
        }

        @Override
        public GoogleWorkspaceConnection.FileMetadata readFileMetadata(String token, String fileId)
                throws GoogleWorkspaceConnection.ProviderException {
            tokens.add(token);
            if (failure != null) {
                throw failure;
            }
            return file;
        }

        @Override
        public List<List<Object>> readValues(String token, String fileId, String range)
                throws GoogleWorkspaceConnection.ProviderException {
            tokens.add(token);
            if (failure != null) {
                throw failure;
            }
            ranges.add(range);
            if (GoogleWorkspaceConnection.METADATA_RANGE.equals(range)) {
                return metadata;
            }
            if (GoogleWorkspaceConnection.COMMAND_HEADER_RANGE.equals(range)) {
                return commands;
            }
            if (GoogleWorkspaceConnection.CHANGE_HEADER_RANGE.equals(range)) {
                return changes;
            }
            throw new AssertionError("unexpected range " + range);
        }
    }
}
