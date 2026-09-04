package com.mira.client.googleworkspace;

import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;

import com.google.android.gms.auth.api.identity.AuthorizationClient;
import com.google.android.gms.auth.api.identity.AuthorizationRequest;
import com.google.android.gms.auth.api.identity.AuthorizationResult;
import com.google.android.gms.auth.api.identity.Identity;
import com.google.android.gms.auth.api.identity.RevokeAccessRequest;
import com.google.android.gms.common.api.ApiException;
import com.google.android.gms.common.api.Scope;
import com.google.android.gms.tasks.Task;

import java.util.Collections;
import java.util.List;
import java.util.Objects;

/**
 * Google Identity Services authorization boundary for the Android Personal Workspace lane.
 *
 * <p>The request uses Google's provider-owned mobile Picker and exactly the non-sensitive
 * {@code drive.file} scope. MIRA receives opaque ephemeral grant material and never asks an
 * ordinary user to copy a spreadsheet ID, OAuth scope, token, or developer-console value.</p>
 */
public final class GooglePlayWorkspaceAuthorization {
    static final String PICKED_FILE_IDS = "picked_file_ids";

    private final AuthorizationClient client;

    public GooglePlayWorkspaceAuthorization(Context context) {
        this(Identity.getAuthorizationClient(Objects.requireNonNull(context, "context")));
    }

    GooglePlayWorkspaceAuthorization(AuthorizationClient client) {
        this.client = Objects.requireNonNull(client, "client");
    }

    /** Begins the provider-owned consent + one-file Picker flow. */
    public Task<AuthorizationResult> beginPickerAuthorization() {
        return client.authorize(pickerRequest());
    }

    /** Returns Google's unavoidable provider-owned resolution when interactive action is needed. */
    public PendingIntent resolution(AuthorizationResult result) throws AuthorizationException {
        if (result == null || !result.hasResolution() || result.getPendingIntent() == null) {
            throw new AuthorizationException(
                    "resolution_unavailable",
                    "Google authorization did not provide an interactive resolution"
            );
        }
        return result.getPendingIntent();
    }

    /** Parses the provider Activity result into opaque grant material. */
    public GoogleWorkspaceConnection.PickerGrant grantFromIntent(Intent data)
            throws AuthorizationException {
        final AuthorizationResult result;
        try {
            result = client.getAuthorizationResultFromIntent(
                    Objects.requireNonNull(data, "data")
            );
        } catch (ApiException exc) {
            throw new AuthorizationException(
                    "authorization_denied",
                    "Google authorization or file selection was cancelled or denied",
                    exc
            );
        }
        return grantFromResult(result);
    }

    /** Parses a result that Google could satisfy without another provider UI roundtrip. */
    public GoogleWorkspaceConnection.PickerGrant grantFromResult(AuthorizationResult result)
            throws AuthorizationException {
        if (result == null) {
            throw new AuthorizationException(
                    "authorization_unavailable",
                    "Google authorization returned no result"
            );
        }
        if (result.hasResolution()) {
            throw new AuthorizationException(
                    "resolution_required",
                    "Google authorization requires provider UI before a Workspace can be bound"
            );
        }
        Bundle params = result.getTokenResponseParams();
        String picked = params == null ? null : params.getString(PICKED_FILE_IDS);
        return grantFromMaterial(result.getAccessToken(), result.getGrantedScopes(), picked);
    }

    /** Revokes MIRA's per-file Google Drive authorization scope. */
    public Task<Void> revokeAccess() {
        RevokeAccessRequest request = RevokeAccessRequest.builder()
                .setScopes(Collections.singletonList(
                        new Scope(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE)
                ))
                .build();
        return client.revokeAccess(request);
    }

    static AuthorizationRequest pickerRequest() {
        return AuthorizationRequest.builder()
                .setRequestedScopes(Collections.singletonList(
                        new Scope(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE)
                ))
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
                        GoogleWorkspaceConnection.SPREADSHEET_MIME_TYPE
                )
                .build();
    }

    static GoogleWorkspaceConnection.PickerGrant grantFromMaterial(
            String accessToken,
            List<String> grantedScopes,
            String pickedFileIds
    ) throws AuthorizationException {
        if (accessToken == null || accessToken.trim().isEmpty()
                || !accessToken.equals(accessToken.trim())
                || accessToken.length() > 8192) {
            throw new AuthorizationException(
                    "authorization_unavailable",
                    "Google authorization returned no usable access token"
            );
        }
        if (grantedScopes == null
                || grantedScopes.size() != 1
                || !GoogleWorkspaceConnection.DRIVE_FILE_SCOPE.equals(grantedScopes.get(0))) {
            throw new AuthorizationException(
                    "scope_mismatch",
                    "Google authorization did not return the exact drive.file grant requested by MIRA"
            );
        }
        if (pickedFileIds == null || pickedFileIds.trim().isEmpty()) {
            throw new AuthorizationException(
                    "picker_selection_missing",
                    "Google Picker returned no selected MIRA spreadsheet"
            );
        }
        String[] ids = pickedFileIds.split(",", -1);
        if (ids.length != 1 || ids[0].trim().isEmpty() || !ids[0].equals(ids[0].trim())) {
            throw new AuthorizationException(
                    "picker_selection_invalid",
                    "Google Picker must return exactly one file identity"
            );
        }
        return new GoogleWorkspaceConnection.PickerGrant(
                accessToken,
                Collections.singletonList(ids[0])
        );
    }

    public static final class AuthorizationException extends Exception {
        private final String code;

        AuthorizationException(String code, String message) {
            super(message);
            this.code = Objects.requireNonNull(code, "code");
        }

        AuthorizationException(String code, String message, Throwable cause) {
            super(message, cause);
            this.code = Objects.requireNonNull(code, "code");
        }

        public String code() {
            return code;
        }
    }
}
