package com.mira.client.googleworkspace;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import com.mira.client.core.sync.GoogleWorkspaceTransport;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public final class GoogleSheetsRestGatewayTest {
    private static final String SHEET_ID = "synthetic_MIRA_sheet_12345";
    private static final String TOKEN = "test-token-never-persist";

    @Test
    public void readTableMapsExactSheetsValues() throws Exception {
        FakeExecutor executor = new FakeExecutor();
        executor.response = jsonResponse(200, new JSONObject()
                .put("values", new JSONArray()
                        .put(new JSONArray().put("Key").put("Value"))
                        .put(new JSONArray().put("mutation_mode").put("queued_writer"))));
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        List<List<Object>> rows = gateway.readTable("Metadata");

        assertEquals(2, rows.size());
        assertEquals(Arrays.asList("Key", "Value"), rows.get(0));
        assertEquals(Arrays.asList("mutation_mode", "queued_writer"), rows.get(1));
        assertEquals(1, executor.requests.size());
        GoogleSheetsRestGateway.HttpRequest request = executor.requests.get(0);
        assertEquals("GET", request.method);
        assertEquals(
                "https://sheets.googleapis.com/v4/spreadsheets/" + SHEET_ID
                        + "/values/Metadata?majorDimension=ROWS&valueRenderOption=UNFORMATTED_VALUE",
                request.url
        );
        assertEquals("Bearer " + TOKEN, request.headers.get("Authorization"));
        assertEquals(null, request.body);
    }

    @Test
    public void appendUsesRawCommandsRequestExactlyOnce() throws Exception {
        FakeExecutor executor = new FakeExecutor();
        executor.response = jsonResponse(200, new JSONObject().put("updates", new JSONObject()));
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);
        List<Object> row = Arrays.asList("cmd-1", "subject-1", 1L, true, "");

        gateway.appendRow(GoogleWorkspaceTransport.COMMANDS_TABLE, row);

        assertEquals(1, executor.requests.size());
        GoogleSheetsRestGateway.HttpRequest request = executor.requests.get(0);
        assertEquals("POST", request.method);
        assertTrue(request.url.endsWith(
                "/values/Commands:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS"
        ));
        assertEquals("application/json; charset=utf-8", request.headers.get("Content-Type"));
        JSONObject body = new JSONObject(new String(request.body, StandardCharsets.UTF_8));
        assertEquals("ROWS", body.getString("majorDimension"));
        JSONArray encoded = body.getJSONArray("values").getJSONArray(0);
        assertEquals("cmd-1", encoded.getString(0));
        assertEquals("subject-1", encoded.getString(1));
        assertEquals(1L, encoded.getLong(2));
        assertTrue(encoded.getBoolean(3));
        assertEquals("", encoded.getString(4));
    }

    @Test
    public void appendNetworkFailureIsNotRetriedByGateway() {
        FakeExecutor executor = new FakeExecutor();
        executor.failure = new IOException("synthetic ambiguous failure");
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.appendRow(
                        GoogleWorkspaceTransport.COMMANDS_TABLE,
                        Collections.singletonList("cmd-1")
                )
        );
        assertEquals(1, executor.requests.size());
    }

    @Test
    public void changesAppendIsForbidden() {
        FakeExecutor executor = new FakeExecutor();
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.appendRow(
                        GoogleWorkspaceTransport.CHANGES_TABLE,
                        Collections.singletonList("not-allowed")
                )
        );
        assertEquals(0, executor.requests.size());
    }

    @Test
    public void arbitraryTableReadIsForbidden() {
        FakeExecutor executor = new FakeExecutor();
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.readTable("Resources")
        );
        assertEquals(0, executor.requests.size());
    }

    @Test
    public void nonSuccessHttpFailsWithoutLeakingProviderBody() {
        FakeExecutor executor = new FakeExecutor();
        executor.response = new GoogleSheetsRestGateway.HttpResponse(
                401,
                "sensitive provider detail".getBytes(StandardCharsets.UTF_8)
        );
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        GoogleWorkspaceTransport.GatewayException error = assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.readTable("Metadata")
        );
        assertEquals("Google Sheets request failed with HTTP 401", error.getMessage());
        assertFalse(error.getMessage().contains("sensitive"));
    }

    @Test
    public void malformedJsonFailsClosed() {
        FakeExecutor executor = new FakeExecutor();
        executor.response = new GoogleSheetsRestGateway.HttpResponse(
                200,
                "not-json".getBytes(StandardCharsets.UTF_8)
        );
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.readTable("Metadata")
        );
    }

    @Test
    public void oversizedResponseFailsClosedBeforeJsonParsing() {
        FakeExecutor executor = new FakeExecutor();
        executor.response = new GoogleSheetsRestGateway.HttpResponse(
                200,
                new byte[(4 * 1024 * 1024) + 1]
        );
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        GoogleWorkspaceTransport.GatewayException error = assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.readTable("Metadata")
        );
        assertEquals(
                "Google Sheets response is empty or exceeds the bounded response size",
                error.getMessage()
        );
        assertEquals(1, executor.requests.size());
    }

    @Test
    public void nestedCellMaterialFailsClosed() throws Exception {
        FakeExecutor executor = new FakeExecutor();
        executor.response = jsonResponse(200, new JSONObject().put(
                "values",
                new JSONArray().put(new JSONArray().put(new JSONObject().put("bad", true)))
        ));
        GoogleSheetsRestGateway gateway = new GoogleSheetsRestGateway(SHEET_ID, TOKEN, executor);

        assertThrows(
                GoogleWorkspaceTransport.GatewayException.class,
                () -> gateway.readTable("Metadata")
        );
    }

    private static GoogleSheetsRestGateway.HttpResponse jsonResponse(int status, JSONObject body) {
        return new GoogleSheetsRestGateway.HttpResponse(
                status,
                body.toString().getBytes(StandardCharsets.UTF_8)
        );
    }

    private static final class FakeExecutor implements GoogleSheetsRestGateway.HttpExecutor {
        final List<GoogleSheetsRestGateway.HttpRequest> requests = new ArrayList<>();
        GoogleSheetsRestGateway.HttpResponse response = jsonResponse(200, new JSONObject());
        IOException failure;

        @Override
        public GoogleSheetsRestGateway.HttpResponse execute(GoogleSheetsRestGateway.HttpRequest request)
                throws IOException {
            requests.add(request);
            if (failure != null) {
                throw failure;
            }
            return response;
        }
    }
}
