package com.mira.client.googleworkspace;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;

import com.google.android.gms.auth.api.identity.AuthorizationClient;
import com.google.android.gms.auth.api.identity.AuthorizationRequest;
import com.google.android.gms.auth.api.identity.AuthorizationResult;
import com.google.android.gms.auth.api.identity.Identity;
import com.google.android.gms.common.api.ApiException;
import com.google.android.gms.common.api.Scope;
import com.google.android.gms.tasks.Task;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.regex.Pattern;

/**
 * Least-privilege Google Identity Services authorization boundary for the Personal Workspace lane.
 *
 * <p>The request deliberately uses only {@code drive.file}. Google documents that scope as the
 * recommended non-sensitive scope for files explicitly used with the app, and the Sheets API
 * accepts it for both values reads and appends. Existing Personal MIRA Sheets are selected through
 * Google's own Picker during authorization; users never copy a spreadsheet ID into MIRA.</p>
 *
 * <p>Access tokens are ephemeral provider material. This class never persists them and callers must
 * not place them in MIRA's protected client credential store, offline sync state, canonical MIRROR
 * resources, logs, or Git. Raw token and provider-file identifiers are intentionally package-private
 * so ordinary app/UI code receives an opaque grant rather than secret material.</p>
 */
public final class GoogleWorkspaceAuthorization {
    public static final String DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file";
    public static final String GOOGLE_SHEET_MIME_TYPE = "application/vnd.google-apps.spreadsheet";
    public static final String PICKED_FILE_IDS_KEY = "picked_file_ids";

    private static final Pattern SPREADSHEET_ID_PATTERN =
            Pattern.compile("^[A-Za-z0-9_-]{10,256}$");

    private final AuthorizationClient client;

    /** Creates the production Google Identity Services client for the supplied Android context. */
    public GoogleWorkspaceAuthorization(Context context) {
        this(Identity.getAuthorizationClient(Objects.requireNonNull(context, "context")));
    }

    GoogleWorkspaceAuthorization(AuthorizationClient client) {
        this.client = Objects.requireNonNull(client, "client");
    }

    /**
     * Begins the Google authorization + Picker flow.
     *
     * <p>If Google can satisfy the grant without UI, the returned task contains token material.
     * Otherwise its {@link AuthorizationResult} contains a {@link PendingIntent} which the host UI
     * must launch as the unavoidable provider-owned account/consent/file-selection surface.</p>
     */
    public Task<AuthorizationResult> beginAuthorization() {
        return client.authorize(buildPickerRequest());
    }

    /** Extracts Google's resolved authorization result from the provider-owned UI result intent. */
    public AuthorizationResult resultFromIntent(Intent data) throws ApiException {
        return client.getAuthorizationResultFromIntent(Objects.requireNonNull(data, "data"));
    }

    /** Builds the exact least-privilege request used by MIRA's default Personal Android lane. */
    public static AuthorizationRequest buildPickerRequest() {
        return AuthorizationRequest.builder()
                .setRequestedScopes(Collections.singletonList(new Scope(DRIVE_FILE_SCOPE)))
                .setOptOutIncludingGrantedScopes(true)
                .setPrompt(AuthorizationRequest.Prompt.CONSENT)
                .addResourceParameter(
                        AuthorizationRequest.ResourceParameter.PICKER_OAUTH_TRIGGER,
                        "true"
                )
                .addResourceParameter(
                        AuthorizationRequest.ResourceParameter.PICKER_ALLOW_MULTIPLE,
                        "false"
                )
                .addResourceParameter(
                        AuthorizationRequest.ResourceParameter.PICKER_MIMETYPES,
                        GOOGLE_SHEET_MIME_TYPE
                )
                .build();
    }

    /**
     * Interprets an AuthorizationResult without treating provider consent alone as readiness.
     */
    public static Outcome interpret(AuthorizationResult result) throws AuthorizationException {
        Objects.requireNonNull(result, "result");
        if (result.hasResolution()) {
            PendingIntent resolution = result.getPendingIntent();
            if (resolution == null) {
                throw new AuthorizationException(
                        "authorization_protocol_error",
                        "Google authorization requires resolution but supplied no PendingIntent"
                );
            }
            return Outcome.needsUserAction(resolution);
        }

        ArrayList<String> scopes = new ArrayList<>();
        List<String> granted = result.getGrantedScopes();
        if (granted != null) {
            scopes.addAll(granted);
        }
        Bundle params = result.getTokenResponseParams();
        String pickedFileIds = params == null ? null : params.getString(PICKED_FILE_IDS_KEY);
        AuthorizedWorkspace authorized = validateGrantedMaterial(
                result.getAccessToken(),
                scopes,
                pickedFileIds
        );
        return Outcome.authorized(authorized);
    }

    /** Pure validation seam used by deterministic JVM tests and the Google result adapter. */
    static AuthorizedWorkspace validateGrantedMaterial(
            String accessToken,
            List<String> grantedScopes,
            String pickedFileIds
    ) throws AuthorizationException {
        if (accessToken == null || accessToken.trim().isEmpty()) {
            throw new AuthorizationException(
                    "authorization_missing_token",
                    "Google authorization did not return an access token"
            );
        }
        if (!accessToken.equals(accessToken.trim()) || accessToken.length() > 8192) {
            throw new AuthorizationException(
                    "authorization_invalid_token",
                    "Google authorization returned invalid access-token material"
            );
        }
        if (grantedScopes == null || grantedScopes.size() != 1
                || !DRIVE_FILE_SCOPE.equals(grantedScopes.get(0))) {
            throw new AuthorizationException(
                    "authorization_scope_mismatch",
                    "Google authorization must grant exactly drive.file for the Personal Workspace lane"
            );
        }
        if (pickedFileIds == null || pickedFileIds.trim().isEmpty()) {
            throw new AuthorizationException(
                    "authorization_missing_workspace",
                    "Google Picker did not return a selected spreadsheet"
            );
        }

        String[] raw = pickedFileIds.split(",", -1);
        if (raw.length != 1) {
            throw new AuthorizationException(
                    "authorization_multiple_workspaces",
                    "Personal Workspace authorization must select exactly one spreadsheet"
            );
        }
        String spreadsheetId = raw[0].trim();
        if (!spreadsheetId.equals(raw[0])
                || !SPREADSHEET_ID_PATTERN.matcher(spreadsheetId).matches()) {
            throw new AuthorizationException(
                    "authorization_invalid_workspace",
                    "Google Picker returned an invalid spreadsheet identifier"
            );
        }
        return new AuthorizedWorkspace(accessToken, spreadsheetId);
    }

    /** Ephemeral successful provider grant. Raw provider material stays inside this package. */
    public static final class AuthorizedWorkspace {
        private final String accessToken;
        private final String spreadsheetId;

        AuthorizedWorkspace(String accessToken, String spreadsheetId) {
            this.accessToken = accessToken;
            this.spreadsheetId = spreadsheetId;
        }

        String accessToken() {
            return accessToken;
        }

        String spreadsheetId() {
            return spreadsheetId;
        }
    }

    /** Provider authorization outcome before MIRA Workspace schema verification. */
    public static final class Outcome {
        public enum Status {
            NEEDS_USER_ACTION,
            AUTHORIZED
        }

        private final Status status;
        private final PendingIntent pendingIntent;
        private final AuthorizedWorkspace authorizedWorkspace;

        private Outcome(
                Status status,
                PendingIntent pendingIntent,
                AuthorizedWorkspace authorizedWorkspace
        ) {
            this.status = status;
            this.pendingIntent = pendingIntent;
            this.authorizedWorkspace = authorizedWorkspace;
        }

        static Outcome needsUserAction(PendingIntent pendingIntent) {
            return new Outcome(Status.NEEDS_USER_ACTION, pendingIntent, null);
        }

        static Outcome authorized(AuthorizedWorkspace authorizedWorkspace) {
            return new Outcome(Status.AUTHORIZED, null, authorizedWorkspace);
        }

        public Status status() {
            return status;
        }

        public PendingIntent pendingIntent() {
            return pendingIntent;
        }

        public AuthorizedWorkspace authorizedWorkspace() {
            return authorizedWorkspace;
        }
    }

    /** Fail-closed provider authorization error with stable code for future Connections UI mapping. */
    public static final class AuthorizationException extends Exception {
        private final String code;

        AuthorizationException(String code, String message) {
            super(message);
            this.code = code;
        }

        public String code() {
            return code;
        }
    }
}
