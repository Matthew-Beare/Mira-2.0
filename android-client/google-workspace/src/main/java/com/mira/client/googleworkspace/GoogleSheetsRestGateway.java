package com.mira.client.googleworkspace;

import com.mira.client.core.sync.GoogleWorkspaceTransport;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Bounded Google Sheets REST implementation for {@link GoogleWorkspaceTransport.SheetsGateway}.
 *
 * <p>This gateway is deliberately tiny. It can read only the MIRA protocol tables required for
 * binding/reconnect and can append only to {@code Commands}. It never lists Drive files, mutates
 * canonical Resources directly, appends Changes, or retries an ambiguous append. The surrounding
 * {@link GoogleWorkspaceTransport} owns command-idempotency/readback convergence.</p>
 */
public final class GoogleSheetsRestGateway implements GoogleWorkspaceTransport.SheetsGateway {
    private static final String API_ROOT = "https://sheets.googleapis.com/v4/spreadsheets/";
    private static final Pattern SPREADSHEET_ID_PATTERN =
            Pattern.compile("^[A-Za-z0-9_-]{10,256}$");
    private static final int MAX_RESPONSE_BYTES = 4 * 1024 * 1024;
    private static final int MAX_ROW_CELLS = 64;
    private static final int CONNECT_TIMEOUT_MILLIS = 15_000;
    private static final int READ_TIMEOUT_MILLIS = 15_000;
    private static final Set<String> READABLE_TABLES = Set.of(
            "Metadata",
            GoogleWorkspaceTransport.COMMANDS_TABLE,
            GoogleWorkspaceTransport.CHANGES_TABLE
    );

    private final String spreadsheetId;
    private final String accessToken;
    private final HttpExecutor executor;

    /** Production HTTPS gateway over the one Picker-authorized MIRA spreadsheet. */
    public GoogleSheetsRestGateway(String spreadsheetId, String accessToken) {
        this(spreadsheetId, accessToken, new UrlConnectionExecutor());
    }

    GoogleSheetsRestGateway(String spreadsheetId, String accessToken, HttpExecutor executor) {
        if (spreadsheetId == null
                || !SPREADSHEET_ID_PATTERN.matcher(spreadsheetId).matches()) {
            throw new IllegalArgumentException("spreadsheetId is invalid");
        }
        if (accessToken == null || accessToken.trim().isEmpty() || accessToken.length() > 8192) {
            throw new IllegalArgumentException("accessToken is invalid");
        }
        this.spreadsheetId = spreadsheetId;
        this.accessToken = accessToken;
        this.executor = Objects.requireNonNull(executor, "executor");
    }

    @Override
    public List<List<Object>> readTable(String tableName)
            throws GoogleWorkspaceTransport.GatewayException {
        if (!READABLE_TABLES.contains(tableName)) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets table is not allowed for Personal Workspace read"
            );
        }
        String url = API_ROOT + spreadsheetId + "/values/" + tableName
                + "?majorDimension=ROWS&valueRenderOption=UNFORMATTED_VALUE";
        HttpResponse response = execute(new HttpRequest(
                "GET",
                url,
                headers(false),
                null
        ));
        requireSuccess(response);
        return parseValues(response.body);
    }

    @Override
    public void appendRow(String tableName, List<Object> row)
            throws GoogleWorkspaceTransport.GatewayException {
        if (!GoogleWorkspaceTransport.COMMANDS_TABLE.equals(tableName)) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets append is allowed only for the MIRA Commands inbox"
            );
        }
        if (row == null || row.isEmpty() || row.size() > MAX_ROW_CELLS) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets append row is empty or exceeds the bounded cell limit"
            );
        }

        JSONArray values = new JSONArray();
        JSONArray encodedRow = new JSONArray();
        for (Object cell : row) {
            encodedRow.put(encodeCell(cell));
        }
        values.put(encodedRow);
        JSONObject body = new JSONObject();
        try {
            body.put("majorDimension", "ROWS");
            body.put("values", values);
        } catch (JSONException exc) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets append body could not be encoded",
                    exc
            );
        }

        String url = API_ROOT + spreadsheetId + "/values/" + tableName
                + ":append?valueInputOption=RAW&insertDataOption=INSERT_ROWS";
        // Intentionally exactly one POST attempt. A network failure after Google accepted the row
        // is ambiguous; GoogleWorkspaceTransport performs readback convergence before any retry.
        HttpResponse response = execute(new HttpRequest(
                "POST",
                url,
                headers(true),
                body.toString().getBytes(StandardCharsets.UTF_8)
        ));
        requireSuccess(response);
    }

    String spreadsheetIdForVerification() {
        return spreadsheetId;
    }

    private Map<String, String> headers(boolean jsonBody) {
        LinkedHashMap<String, String> result = new LinkedHashMap<>();
        result.put("Authorization", "Bearer " + accessToken);
        result.put("Accept", "application/json");
        if (jsonBody) {
            result.put("Content-Type", "application/json; charset=utf-8");
        }
        return Collections.unmodifiableMap(result);
    }

    private HttpResponse execute(HttpRequest request)
            throws GoogleWorkspaceTransport.GatewayException {
        try {
            return executor.execute(request);
        } catch (IOException exc) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets network request failed",
                    exc
            );
        }
    }

    private static void requireSuccess(HttpResponse response)
            throws GoogleWorkspaceTransport.GatewayException {
        if (response == null || response.statusCode < 200 || response.statusCode > 299) {
            int status = response == null ? 0 : response.statusCode;
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets request failed with HTTP " + status
            );
        }
    }

    private static List<List<Object>> parseValues(byte[] body)
            throws GoogleWorkspaceTransport.GatewayException {
        if (body == null || body.length == 0 || body.length > MAX_RESPONSE_BYTES) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets response is empty or exceeds the bounded response size"
            );
        }
        final Object parsed;
        try {
            JSONTokener tokener = new JSONTokener(new String(body, StandardCharsets.UTF_8));
            parsed = tokener.nextValue();
            if (tokener.nextClean() != 0 || !(parsed instanceof JSONObject)) {
                throw new JSONException("response must contain one JSON object");
            }
        } catch (JSONException exc) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets response JSON is invalid",
                    exc
            );
        }

        JSONObject object = (JSONObject) parsed;
        if (!object.has("values")) {
            return Collections.emptyList();
        }
        final JSONArray values;
        try {
            values = object.getJSONArray("values");
        } catch (JSONException exc) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets response values are invalid",
                    exc
            );
        }

        ArrayList<List<Object>> rows = new ArrayList<>(values.length());
        try {
            for (int rowIndex = 0; rowIndex < values.length(); rowIndex++) {
                JSONArray encodedRow = values.getJSONArray(rowIndex);
                if (encodedRow.length() > MAX_ROW_CELLS) {
                    throw new GoogleWorkspaceTransport.GatewayException(
                            "Google Sheets response row exceeds the bounded cell limit"
                    );
                }
                ArrayList<Object> row = new ArrayList<>(encodedRow.length());
                for (int cellIndex = 0; cellIndex < encodedRow.length(); cellIndex++) {
                    row.add(decodeCell(encodedRow.get(cellIndex)));
                }
                rows.add(Collections.unmodifiableList(row));
            }
        } catch (JSONException exc) {
            throw new GoogleWorkspaceTransport.GatewayException(
                    "Google Sheets response rows are invalid",
                    exc
            );
        }
        return Collections.unmodifiableList(rows);
    }

    private static Object encodeCell(Object value)
            throws GoogleWorkspaceTransport.GatewayException {
        if (value == null) {
            return "";
        }
        if (value instanceof String || value instanceof Boolean || value instanceof Number) {
            return value;
        }
        throw new GoogleWorkspaceTransport.GatewayException(
                "Google Sheets append contains unsupported cell material"
        );
    }

    private static Object decodeCell(Object value)
            throws GoogleWorkspaceTransport.GatewayException {
        if (value == null || value == JSONObject.NULL) {
            return "";
        }
        if (value instanceof String || value instanceof Boolean || value instanceof Number) {
            return value;
        }
        throw new GoogleWorkspaceTransport.GatewayException(
                "Google Sheets response contains unsupported cell material"
        );
    }

    interface HttpExecutor {
        HttpResponse execute(HttpRequest request) throws IOException;
    }

    static final class HttpRequest {
        final String method;
        final String url;
        final Map<String, String> headers;
        final byte[] body;

        HttpRequest(String method, String url, Map<String, String> headers, byte[] body) {
            this.method = method;
            this.url = url;
            this.headers = headers;
            this.body = body;
        }
    }

    static final class HttpResponse {
        final int statusCode;
        final byte[] body;

        HttpResponse(int statusCode, byte[] body) {
            this.statusCode = statusCode;
            this.body = body == null ? new byte[0] : body.clone();
        }
    }

    private static final class UrlConnectionExecutor implements HttpExecutor {
        @Override
        public HttpResponse execute(HttpRequest request) throws IOException {
            HttpURLConnection connection = (HttpURLConnection) new URL(request.url).openConnection();
            connection.setConnectTimeout(CONNECT_TIMEOUT_MILLIS);
            connection.setReadTimeout(READ_TIMEOUT_MILLIS);
            connection.setInstanceFollowRedirects(false);
            connection.setRequestMethod(request.method);
            for (Map.Entry<String, String> entry : request.headers.entrySet()) {
                connection.setRequestProperty(entry.getKey(), entry.getValue());
            }
            if (request.body != null) {
                connection.setDoOutput(true);
                connection.setFixedLengthStreamingMode(request.body.length);
                try (OutputStream stream = connection.getOutputStream()) {
                    stream.write(request.body);
                }
            }

            int status = connection.getResponseCode();
            InputStream stream = status >= 200 && status <= 299
                    ? connection.getInputStream()
                    : connection.getErrorStream();
            byte[] body = stream == null ? new byte[0] : readBounded(stream);
            connection.disconnect();
            return new HttpResponse(status, body);
        }

        private static byte[] readBounded(InputStream stream) throws IOException {
            try (InputStream input = stream; ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[8192];
                int total = 0;
                int read;
                while ((read = input.read(buffer)) != -1) {
                    total += read;
                    if (total > MAX_RESPONSE_BYTES) {
                        throw new IOException("Google Sheets response exceeds bounded size");
                    }
                    output.write(buffer, 0, read);
                }
                return output.toByteArray();
            }
        }
    }
}
