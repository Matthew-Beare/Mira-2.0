package com.mira.client.core.sync;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * Narrow REST adapter for a Picker-granted MIRA Personal spreadsheet.
 *
 * <p>This adapter deliberately exposes only Drive file metadata, bounded Sheets value reads,
 * Commands/Changes transport reads, and one-row Commands append. It is not a generic Drive or
 * Sheets client and cannot mutate arbitrary ranges.</p>
 */
public final class GoogleWorkspaceRestApi implements GoogleWorkspaceConnection.WorkspaceApi {
    private static final String DRIVE_BASE = "https://www.googleapis.com/drive/v3/files/";
    private static final String SHEETS_BASE = "https://sheets.googleapis.com/v4/spreadsheets/";
    private static final int MAX_RESPONSE_BYTES = 2 * 1024 * 1024;
    private static final int CONNECT_TIMEOUT_MS = 10_000;
    private static final int READ_TIMEOUT_MS = 20_000;

    private final HttpExecutor executor;

    public GoogleWorkspaceRestApi() {
        this(new UrlConnectionExecutor());
    }

    GoogleWorkspaceRestApi(HttpExecutor executor) {
        this.executor = Objects.requireNonNull(executor, "executor");
    }

    @Override
    public GoogleWorkspaceConnection.FileMetadata readFileMetadata(String accessToken, String fileId)
            throws GoogleWorkspaceConnection.ProviderException {
        String url = DRIVE_BASE + path(fileId)
                + "?fields=id%2Cname%2CmimeType%2Ctrashed%2Ccapabilities%28canEdit%29"
                + "&supportsAllDrives=true";
        JSONObject payload = executeJson(new Request("GET", url, accessToken, null));
        JSONObject capabilities = payload.optJSONObject("capabilities");
        return new GoogleWorkspaceConnection.FileMetadata(
                payload.optString("id", ""),
                payload.optString("name", ""),
                payload.optString("mimeType", ""),
                payload.optBoolean("trashed", false),
                capabilities != null && capabilities.optBoolean("canEdit", false)
        );
    }

    @Override
    public List<List<Object>> readValues(String accessToken, String spreadsheetId, String range)
            throws GoogleWorkspaceConnection.ProviderException {
        return readValuesInternal(accessToken, spreadsheetId, range);
    }

    /** Returns the only mutation/read gateway accepted by GoogleWorkspaceTransport. */
    public GoogleWorkspaceTransport.SheetsGateway gateway(
            GoogleWorkspaceConnection.VerifiedBinding binding,
            String accessToken
    ) {
        Objects.requireNonNull(binding, "binding");
        if (!binding.sharedWriterReady()) {
            throw new IllegalStateException("MIRA Workspace is bound but shared writer is not ready");
        }
        return new BoundGateway(binding.spreadsheetId(), requireNonBlank(accessToken, "accessToken"));
    }

    private List<List<Object>> readValuesInternal(
            String accessToken,
            String spreadsheetId,
            String range
    ) throws GoogleWorkspaceConnection.ProviderException {
        String url = SHEETS_BASE + path(spreadsheetId) + "/values/" + path(range)
                + "?majorDimension=ROWS&valueRenderOption=UNFORMATTED_VALUE";
        JSONObject payload = executeJson(new Request("GET", url, accessToken, null));
        JSONArray values = payload.optJSONArray("values");
        if (values == null) {
            return Collections.emptyList();
        }
        ArrayList<List<Object>> rows = new ArrayList<>(values.length());
        try {
            for (int rowIndex = 0; rowIndex < values.length(); rowIndex++) {
                JSONArray row = values.getJSONArray(rowIndex);
                ArrayList<Object> cells = new ArrayList<>(row.length());
                for (int column = 0; column < row.length(); column++) {
                    Object value = row.get(column);
                    cells.add(value == JSONObject.NULL ? "" : value);
                }
                rows.add(Collections.unmodifiableList(cells));
            }
        } catch (JSONException exc) {
            throw new GoogleWorkspaceConnection.ProviderException(
                    "provider_protocol_error",
                    "Google Sheets returned malformed row values",
                    exc
            );
        }
        return Collections.unmodifiableList(rows);
    }

    private void appendCommandRow(String accessToken, String spreadsheetId, List<Object> row)
            throws GoogleWorkspaceConnection.ProviderException {
        if (row == null || row.size() != 16) {
            throw new GoogleWorkspaceConnection.ProviderException(
                    "provider_request_invalid",
                    "Commands append requires exactly 16 protocol cells"
            );
        }
        JSONArray values = new JSONArray();
        JSONArray cells = new JSONArray();
        for (Object value : row) {
            cells.put(value == null ? "" : value);
        }
        values.put(cells);
        JSONObject body = new JSONObject();
        try {
            body.put("majorDimension", "ROWS");
            body.put("values", values);
        } catch (JSONException exc) {
            throw new GoogleWorkspaceConnection.ProviderException(
                    "provider_request_invalid",
                    "Could not encode Commands append",
                    exc
            );
        }
        String url = SHEETS_BASE + path(spreadsheetId) + "/values/" + path("Commands!A:P")
                + ":append?valueInputOption=RAW&insertDataOption=INSERT_ROWS";
        executeJson(new Request("POST", url, accessToken, body.toString()));
    }

    private JSONObject executeJson(Request request) throws GoogleWorkspaceConnection.ProviderException {
        final Response response;
        try {
            response = executor.execute(request);
        } catch (IOException exc) {
            throw new GoogleWorkspaceConnection.ProviderException(
                    "provider_unavailable",
                    "Google Workspace network request failed",
                    exc
            );
        }
        if (response.statusCode < 200 || response.statusCode >= 300) {
            throw httpFailure(response.statusCode);
        }
        if (response.body == null || response.body.trim().isEmpty()) {
            return new JSONObject();
        }
        try {
            return new JSONObject(response.body);
        } catch (JSONException exc) {
            throw new GoogleWorkspaceConnection.ProviderException(
                    "provider_protocol_error",
                    "Google Workspace returned invalid JSON",
                    exc
            );
        }
    }

    private static GoogleWorkspaceConnection.ProviderException httpFailure(int status) {
        if (status == 401) {
            return new GoogleWorkspaceConnection.ProviderException(
                    "authorization_expired", "Google authorization is expired or invalid"
            );
        }
        if (status == 403) {
            return new GoogleWorkspaceConnection.ProviderException(
                    "authorization_denied", "Google account does not grant access to the selected MIRA spreadsheet"
            );
        }
        if (status == 404) {
            return new GoogleWorkspaceConnection.ProviderException(
                    "workspace_not_found", "Selected MIRA spreadsheet is no longer available"
            );
        }
        if (status == 409 || status == 412) {
            return new GoogleWorkspaceConnection.ProviderException(
                    "provider_conflict", "Google Workspace rejected the request because provider state changed"
            );
        }
        if (status == 429 || status >= 500) {
            return new GoogleWorkspaceConnection.ProviderException(
                    "provider_unavailable", "Google Workspace is temporarily unavailable"
            );
        }
        return new GoogleWorkspaceConnection.ProviderException(
                "provider_error", "Google Workspace request failed with HTTP " + status
        );
    }

    private static String path(String value) throws GoogleWorkspaceConnection.ProviderException {
        String text = requireNonBlank(value, "provider path value");
        try {
            return URLEncoder.encode(text, StandardCharsets.UTF_8.name()).replace("+", "%20");
        } catch (Exception exc) {
            throw new GoogleWorkspaceConnection.ProviderException(
                    "provider_request_invalid", "Could not encode Google Workspace request", exc
            );
        }
    }

    private static String requireNonBlank(String value, String field) {
        if (value == null || value.trim().isEmpty() || !value.equals(value.trim())) {
            throw new IllegalArgumentException(field + " must be non-empty trimmed text");
        }
        return value;
    }

    private final class BoundGateway implements GoogleWorkspaceTransport.SheetsGateway {
        private final String spreadsheetId;
        private final String accessToken;

        BoundGateway(String spreadsheetId, String accessToken) {
            this.spreadsheetId = spreadsheetId;
            this.accessToken = accessToken;
        }

        @Override
        public List<List<Object>> readTable(String tableName) throws GoogleWorkspaceTransport.GatewayException {
            final String range;
            if (GoogleWorkspaceTransport.COMMANDS_TABLE.equals(tableName)) {
                range = "Commands!A1:P4097";
            } else if (GoogleWorkspaceTransport.CHANGES_TABLE.equals(tableName)) {
                range = "Changes!A1:I16385";
            } else {
                throw new GoogleWorkspaceTransport.GatewayException(
                        "Workspace gateway cannot read arbitrary table: " + tableName
                );
            }
            try {
                return readValuesInternal(accessToken, spreadsheetId, range);
            } catch (GoogleWorkspaceConnection.ProviderException exc) {
                throw new GoogleWorkspaceTransport.GatewayException(
                        exc.code() + ": " + exc.getMessage(), exc
                );
            }
        }

        @Override
        public void appendRow(String tableName, List<Object> row)
                throws GoogleWorkspaceTransport.GatewayException {
            if (!GoogleWorkspaceTransport.COMMANDS_TABLE.equals(tableName)) {
                throw new GoogleWorkspaceTransport.GatewayException(
                        "Workspace gateway can append only Commands"
                );
            }
            try {
                appendCommandRow(accessToken, spreadsheetId, row);
            } catch (GoogleWorkspaceConnection.ProviderException exc) {
                throw new GoogleWorkspaceTransport.GatewayException(
                        exc.code() + ": " + exc.getMessage(), exc
                );
            }
        }
    }

    static final class Request {
        final String method;
        final String url;
        final String accessToken;
        final String body;

        Request(String method, String url, String accessToken, String body) {
            this.method = requireNonBlank(method, "method");
            this.url = requireNonBlank(url, "url");
            this.accessToken = requireNonBlank(accessToken, "accessToken");
            this.body = body;
        }
    }

    static final class Response {
        final int statusCode;
        final String body;

        Response(int statusCode, String body) {
            this.statusCode = statusCode;
            this.body = body == null ? "" : body;
        }
    }

    interface HttpExecutor {
        Response execute(Request request) throws IOException;
    }

    private static final class UrlConnectionExecutor implements HttpExecutor {
        @Override
        public Response execute(Request request) throws IOException {
            HttpURLConnection connection = (HttpURLConnection) URI.create(request.url).toURL().openConnection();
            connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
            connection.setReadTimeout(READ_TIMEOUT_MS);
            connection.setRequestMethod(request.method);
            connection.setRequestProperty("Authorization", "Bearer " + request.accessToken);
            connection.setRequestProperty("Accept", "application/json");
            connection.setUseCaches(false);
            if (request.body != null) {
                byte[] encoded = request.body.getBytes(StandardCharsets.UTF_8);
                connection.setDoOutput(true);
                connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
                connection.setFixedLengthStreamingMode(encoded.length);
                try (OutputStream output = connection.getOutputStream()) {
                    output.write(encoded);
                }
            }
            int status = connection.getResponseCode();
            InputStream stream = status >= 200 && status < 400
                    ? connection.getInputStream()
                    : connection.getErrorStream();
            String body = stream == null ? "" : readBounded(stream);
            connection.disconnect();
            return new Response(status, body);
        }

        private static String readBounded(InputStream stream) throws IOException {
            try (InputStream input = stream; ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[8192];
                int total = 0;
                while (true) {
                    int read = input.read(buffer);
                    if (read < 0) {
                        break;
                    }
                    total += read;
                    if (total > MAX_RESPONSE_BYTES) {
                        throw new IOException("Google Workspace response exceeds bounded size");
                    }
                    output.write(buffer, 0, read);
                }
                return output.toString(StandardCharsets.UTF_8.name());
            }
        }
    }
}
