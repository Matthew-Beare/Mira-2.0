package com.mira.client.googleworkspace;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.fail;

public final class GooglePlayWorkspaceAuthorizationTest {
    private static final String FILE_ID = "miraStarterFile_12345";

    @Test
    public void exactDriveFileGrantProducesOneOpaquePickerGrant() throws Exception {
        GoogleWorkspaceConnection.PickerGrant grant =
                GooglePlayWorkspaceAuthorization.grantFromMaterial(
                        "access-token",
                        Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                        FILE_ID
                );

        assertEquals("access-token", grant.accessToken());
        assertEquals(Collections.singletonList(FILE_ID), grant.pickedFileIds());
        assertFalse(grant.toString().contains("access-token"));
        assertFalse(grant.toString().contains(FILE_ID));
    }

    @Test
    public void missingOrOversizedTokenIsNotConnected() throws Exception {
        expectCode("authorization_unavailable", () ->
                GooglePlayWorkspaceAuthorization.grantFromMaterial(
                        null,
                        Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                        FILE_ID
                ));
        expectCode("authorization_unavailable", () ->
                GooglePlayWorkspaceAuthorization.grantFromMaterial(
                        repeat('x', 8193),
                        Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                        FILE_ID
                ));
    }

    @Test
    public void scopeExpansionFailsClosed() throws Exception {
        expectCode("scope_mismatch", () ->
                GooglePlayWorkspaceAuthorization.grantFromMaterial(
                        "access-token",
                        Arrays.asList(
                                GoogleWorkspaceConnection.DRIVE_FILE_SCOPE,
                                "https://www.googleapis.com/auth/drive.metadata.readonly"
                        ),
                        FILE_ID
                ));
    }

    @Test
    public void cancelledPickerHasNoBindingMaterial() throws Exception {
        expectCode("picker_selection_missing", () ->
                GooglePlayWorkspaceAuthorization.grantFromMaterial(
                        "access-token",
                        Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                        ""
                ));
    }

    @Test
    public void multiplePickerFilesAreRejectedEvenIfProviderReturnsThem() throws Exception {
        expectCode("picker_selection_invalid", () ->
                GooglePlayWorkspaceAuthorization.grantFromMaterial(
                        "access-token",
                        Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                        FILE_ID + ",secondFile_123456"
                ));
    }

    @Test
    public void productionAdapterUsesNarrowGooglePolicySurface() {
        assertEquals(
                "GooglePlayWorkspaceAuthorization",
                GooglePlayWorkspaceAuthorization.class.getSimpleName()
        );
        assertEquals(
                "https://www.googleapis.com/auth/drive.file",
                GoogleWorkspaceConnection.DRIVE_FILE_SCOPE
        );
    }

    private static String repeat(char value, int count) {
        StringBuilder result = new StringBuilder(count);
        for (int index = 0; index < count; index++) {
            result.append(value);
        }
        return result.toString();
    }

    private interface CheckedRunnable {
        void run() throws Exception;
    }

    private static void expectCode(String expected, CheckedRunnable runnable) throws Exception {
        try {
            runnable.run();
            fail("expected AuthorizationException " + expected);
        } catch (GooglePlayWorkspaceAuthorization.AuthorizationException exc) {
            assertEquals(expected, exc.code());
        }
    }
}
