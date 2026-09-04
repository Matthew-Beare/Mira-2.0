package com.mira.client.core.sync;

import org.junit.Test;

import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

public final class GoogleWorkspaceRestApiTest {
    private static final String FILE_ID = "miraStarterFile_12345";
    private static final String TOKEN = "ephemeral-token";

    @Test
    public void readsOnlySelectedFileMetadata() throws Exception {
        FakeHttp http = new FakeHttp();
        http.enqueue(200, "{\"id\":\"" + FILE_ID + "\",\"name\":\"MIRA Personal Starter\","
                + "\"mimeType\":\"application/vnd.google-apps.spreadsheet\",\"trashed\":false,"
                + "\"capabilities\":{\"canEdit\":true}}");
        GoogleWorkspaceRestApi api = new GoogleWorkspaceRestApi(http);

        GoogleWorkspaceConnection.FileMetadata file = api.readFileMetadata(TOKEN, FILE_ID);

        assertEquals(FILE_ID, file.id());
        assertEquals("MIRA Personal Starter", file.name());
        assertTrue(file.canEdit());
        assertEquals(1, http.requests.size());
        GoogleWorkspaceRestApi.Request request = http.requests.get(0);
        assertEquals("GET", request.method);
        assertTrue(request.url.contains("/drive/v3/files/" + FILE_ID));
        assertFalse(request.url.contains(TOKEN));
    }

    @Test
    public void parsesBoundedSheetsRowsWithoutArbitraryMutation() throws Exception {
        FakeHttp http = new FakeHttp();
        http.enqueue(200, "{\"values\":[[\"Key\",\"Value\"],[\"mutation_mode\",\"queued_writer\"]]}");
        GoogleWorkspaceRestApi api = new GoogleWorkspaceRestApi(http);

        List<List<Object>> rows = api.readValues(TOKEN, FILE_ID, "Metadata!A1:B32");

        assertEquals(2, rows.size());
        assertEquals(Arrays.asList("Key", "Value"), rows.get(0));
        assertTrue(http.requests.get(0).url.contains("Metadata%21A1%3AB32"));
    }

    @Test
    public void boundGatewayUsesProtocolRowBounds() throws Exception {
        FakeHttp http = new FakeHttp();
        http.enqueue(200, "{\"values\":[[\"command_id\"]]}");
        http.enqueue(200, "{\"values\":[[\"change_seq\"]]}");
        GoogleWorkspaceRestApi api = new GoogleWorkspaceRestApi(http);
        GoogleWorkspaceTransport.SheetsGateway gateway = api.gateway(binding(), TOKEN);

        gateway.readTable(GoogleWorkspaceTransport.COMMANDS_TABLE);
        gateway.readTable(GoogleWorkspaceTransport.CHANGES_TABLE);

        assertTrue(http.requests.get(0).url.contains("Commands%21A1%3AP4097"));
        assertTrue(http.requests.get(1).url.contains("Changes%21A1%3AI16385"));
    }

    @Test
    public void boundGatewayAppendsExactlyOneCommandRow() throws Exception {
        FakeHttp http = new FakeHttp();
        http.enqueue(200, "{}");
        GoogleWorkspaceRestApi api = new GoogleWorkspaceRestApi(http);
        GoogleWorkspaceTransport.SheetsGateway gateway = api.gateway(binding(), TOKEN);
        List<Object> row = new ArrayList<>();
        for (int index = 0; index < 16; index++) {
            row.add("v" + index);
        }

        gateway.appendRow(GoogleWorkspaceTransport.COMMANDS_TABLE, row);

        GoogleWorkspaceRestApi.Request request = http.requests.get(0);
        assertEquals("POST", request.method);
        assertTrue(request.url.contains("Commands%21A%3AP:append"));
        assertTrue(request.url.contains("valueInputOption=RAW"));
        assertTrue(request.body.contains("\"values\":"));
    }

    @Test
    public void boundGatewayRejectsArbitraryTableReadOrAppend() throws Exception {
        GoogleWorkspaceRestApi api = new GoogleWorkspaceRestApi(new FakeHttp());
        GoogleWorkspaceTransport.SheetsGateway gateway = api.gateway(binding(), TOKEN);
        expectGatewayFailure(() -> gateway.readTable("Resources"));
        expectGatewayFailure(() -> gateway.appendRow("Resources", Collections.nCopies(16, "x")));
    }

    @Test
    public void commandAppendRejectsWrongProtocolWidthBeforeNetwork() throws Exception {
        FakeHttp http = new FakeHttp();
        GoogleWorkspaceTransport.SheetsGateway gateway = new GoogleWorkspaceRestApi(http)
                .gateway(binding(), TOKEN);

        expectGatewayFailure(() -> gateway.appendRow(
                GoogleWorkspaceTransport.COMMANDS_TABLE,
                Collections.singletonList("too-short")
        ));

        assertEquals(0, http.requests.size());
    }

    @Test
    public void mapsExpiredAndDeniedAuthorizationWithoutLeakingProviderBody() throws Exception {
        FakeHttp expired = new FakeHttp();
        expired.enqueue(401, "{\"error\":{\"message\":\"secret provider detail\"}}");
        expectProviderCode("authorization_expired", () -> new GoogleWorkspaceRestApi(expired)
                .readFileMetadata(TOKEN, FILE_ID));

        FakeHttp denied = new FakeHttp();
        denied.enqueue(403, "permission body");
        expectProviderCode("authorization_denied", () -> new GoogleWorkspaceRestApi(denied)
                .readFileMetadata(TOKEN, FILE_ID));
    }

    @Test
    public void networkFailureNormalizesToProviderUnavailable() throws Exception {
        FakeHttp http = new FakeHttp();
        http.ioFailure = new IOException("socket exploded");
        expectProviderCode("provider_unavailable", () -> new GoogleWorkspaceRestApi(http)
                .readFileMetadata(TOKEN, FILE_ID));
    }

    @Test
    public void gatewayRefusesBoundButNotSharedWriterReadyWorkspace() {
        GoogleWorkspaceConnection.VerifiedBinding notReady = new GoogleWorkspaceConnection.VerifiedBinding(
                FILE_ID, "MIRA Personal Starter", "mira-structured-state-v1",
                "direct_single_writer", false
        );
        try {
            new GoogleWorkspaceRestApi(new FakeHttp()).gateway(notReady, TOKEN);
            fail("expected shared writer readiness guard");
        } catch (IllegalStateException expected) {
            assertTrue(expected.getMessage().contains("not ready"));
        }
    }

    @Test
    public void productionRestClassHasDirectJvmEvidence() {
        assertEquals("GoogleWorkspaceRestApi", GoogleWorkspaceRestApi.class.getSimpleName());
    }

    private static GoogleWorkspaceConnection.VerifiedBinding binding() {
        return new GoogleWorkspaceConnection.VerifiedBinding(
                FILE_ID,
                "MIRA Personal Starter",
                "mira-structured-state-v1",
                "queued_writer",
                true
        );
    }

    private interface CheckedRunnable {
        void run() throws Exception;
    }

    private static void expectProviderCode(String expected, CheckedRunnable action) throws Exception {
        try {
            action.run();
            fail("expected ProviderException " + expected);
        } catch (GoogleWorkspaceConnection.ProviderException exc) {
            assertEquals(expected, exc.code());
        }
    }

    private static void expectGatewayFailure(CheckedRunnable action) throws Exception {
        try {
            action.run();
            fail("expected GatewayException");
        } catch (GoogleWorkspaceTransport.GatewayException expected) {
            // expected
        }
    }

    private static final class FakeHttp implements GoogleWorkspaceRestApi.HttpExecutor {
        final Deque<GoogleWorkspaceRestApi.Response> responses = new ArrayDeque<>();
        final List<GoogleWorkspaceRestApi.Request> requests = new ArrayList<>();
        IOException ioFailure;

        void enqueue(int status, String body) {
            responses.addLast(new GoogleWorkspaceRestApi.Response(status, body));
        }

        @Override
        public GoogleWorkspaceRestApi.Response execute(GoogleWorkspaceRestApi.Request request)
                throws IOException {
            requests.add(request);
            if (ioFailure != null) {
                throw ioFailure;
            }
            if (responses.isEmpty()) {
                throw new AssertionError("unexpected HTTP request " + request.url);
            }
            return responses.removeFirst();
        }
    }
}
