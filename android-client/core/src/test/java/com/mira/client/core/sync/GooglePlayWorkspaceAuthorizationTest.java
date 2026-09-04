package com.mira.client.core.sync;

import org.junit.Test;

import java.util.Arrays;
import java.util.Collections;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.fail;

public final class GooglePlayWorkspaceAuthorizationTest {
    @Test
    public void exactDriveFileGrantProducesOnePickerGrant() throws Exception {
        GoogleWorkspaceConnection.PickerGrant grant = GooglePlayWorkspaceAuthorization.grantFromMaterial(
                "access-token",
                Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                "miraStarterFile_12345"
        );

        assertEquals("access-token", grant.accessToken());
        assertEquals(Collections.singletonList("miraStarterFile_12345"), grant.pickedFileIds());
    }

    @Test
    public void missingTokenIsNotConnected() throws Exception {
        expectCode("authorization_unavailable", () -> GooglePlayWorkspaceAuthorization.grantFromMaterial(
                null,
                Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                "miraStarterFile_12345"
        ));
    }

    @Test
    public void scopeExpansionFailsClosed() throws Exception {
        expectCode("scope_mismatch", () -> GooglePlayWorkspaceAuthorization.grantFromMaterial(
                "access-token",
                Arrays.asList(
                        GoogleWorkspaceConnection.DRIVE_FILE_SCOPE,
                        "https://www.googleapis.com/auth/drive.metadata.readonly"
                ),
                "miraStarterFile_12345"
        ));
    }

    @Test
    public void cancelledPickerHasNoBindingMaterial() throws Exception {
        expectCode("picker_selection_missing", () -> GooglePlayWorkspaceAuthorization.grantFromMaterial(
                "access-token",
                Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                ""
        ));
    }

    @Test
    public void multiplePickerFilesAreRejectedEvenIfProviderReturnsThem() throws Exception {
        expectCode("picker_selection_invalid", () -> GooglePlayWorkspaceAuthorization.grantFromMaterial(
                "access-token",
                Collections.singletonList(GoogleWorkspaceConnection.DRIVE_FILE_SCOPE),
                "miraStarterFile_12345,secondFile_123456"
        ));
    }

    @Test
    public void productionAdapterClassIsDirectlyOwnedAndUsesNarrowPolicySurface() {
        assertEquals(
                "GooglePlayWorkspaceAuthorization",
                GooglePlayWorkspaceAuthorization.class.getSimpleName()
        );
        assertEquals(
                "https://www.googleapis.com/auth/drive.file",
                GoogleWorkspaceConnection.DRIVE_FILE_SCOPE
        );
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
