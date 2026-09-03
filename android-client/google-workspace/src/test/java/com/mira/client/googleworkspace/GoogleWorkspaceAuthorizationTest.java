package com.mira.client.googleworkspace;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;

public final class GoogleWorkspaceAuthorizationTest {
    private static final String TOKEN = "test-access-token-never-persist";
    private static final String SHEET_ID = "synthetic_MIRA_sheet_12345";

    @Test
    public void providerResolutionWithPendingIntentRequiresUserAction() throws Exception {
        assertEquals(
                GoogleWorkspaceAuthorization.Outcome.Status.NEEDS_USER_ACTION,
                GoogleWorkspaceAuthorization.classifyResolution(true, true)
        );
    }

    @Test
    public void resolvedProviderEvidenceMayProceedToGrantValidation() throws Exception {
        assertEquals(
                GoogleWorkspaceAuthorization.Outcome.Status.AUTHORIZED,
                GoogleWorkspaceAuthorization.classifyResolution(false, false)
        );
    }

    @Test
    public void contradictoryProviderResolutionEvidenceFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException missingIntent = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.classifyResolution(true, false)
        );
        assertEquals("authorization_protocol_error", missingIntent.code());

        GoogleWorkspaceAuthorization.AuthorizationException strayIntent = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.classifyResolution(false, true)
        );
        assertEquals("authorization_protocol_error", strayIntent.code());
    }

    @Test
    public void exactDriveFileGrantAndOnePickedSheetAreAccepted() throws Exception {
        GoogleWorkspaceAuthorization.AuthorizedWorkspace authorized =
                GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        SHEET_ID
                );

        assertEquals(TOKEN, authorized.accessToken());
        assertEquals(SHEET_ID, authorized.spreadsheetId());
    }

    @Test
    public void missingAccessTokenFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        "",
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        SHEET_ID
                )
        );
        assertEquals("authorization_missing_token", error.code());
    }

    @Test
    public void whitespaceWrappedAccessTokenFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        " " + TOKEN,
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        SHEET_ID
                )
        );
        assertEquals("authorization_invalid_token", error.code());
    }

    @Test
    public void missingDriveFileScopeFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Collections.emptyList(),
                        SHEET_ID
                )
        );
        assertEquals("authorization_scope_mismatch", error.code());
    }

    @Test
    public void inheritedAdditionalScopeFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Arrays.asList(
                                GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE,
                                "https://www.googleapis.com/auth/drive"
                        ),
                        SHEET_ID
                )
        );
        assertEquals("authorization_scope_mismatch", error.code());
    }

    @Test
    public void missingPickerSelectionFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        null
                )
        );
        assertEquals("authorization_missing_workspace", error.code());
    }

    @Test
    public void multiplePickerSelectionsFailClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        SHEET_ID + ",other_synthetic_sheet_67890"
                )
        );
        assertEquals("authorization_multiple_workspaces", error.code());
    }

    @Test
    public void malformedPickerSelectionFailsClosed() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        "bad id with spaces"
                )
        );
        assertEquals("authorization_invalid_workspace", error.code());
    }

    @Test
    public void whitespaceWrappedPickerSelectionFailsClosedInsteadOfSilentlyNormalizing() {
        GoogleWorkspaceAuthorization.AuthorizationException error = assertThrows(
                GoogleWorkspaceAuthorization.AuthorizationException.class,
                () -> GoogleWorkspaceAuthorization.validateGrantedMaterial(
                        TOKEN,
                        Collections.singletonList(GoogleWorkspaceAuthorization.DRIVE_FILE_SCOPE),
                        " " + SHEET_ID
                )
        );
        assertEquals("authorization_invalid_workspace", error.code());
    }
}
