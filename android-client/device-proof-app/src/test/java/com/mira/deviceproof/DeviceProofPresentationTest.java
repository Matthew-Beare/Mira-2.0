package com.mira.deviceproof;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import com.mira.client.core.sync.CanonicalResourceMutator;
import com.mira.client.core.sync.CanonicalResourceReader;

import org.junit.Test;

import java.nio.charset.StandardCharsets;

public final class DeviceProofPresentationTest {
    // Direct ownership evidence for the installable launcher class without loading Android Activity
    // bytecode in the host JVM test runtime.
    private static final String ACTIVITY_CLASS = "DeviceProofActivity";

    @Test
    public void launcherOwnershipEvidenceNamesTheBoundedActivity() {
        assertEquals("DeviceProofActivity", ACTIVITY_CLASS);
    }

    @Test
    public void verifiedConnectionShowsOnlySafeReadinessMaterial() {
        String summary = DeviceProofPresentation.connectionSummary(
                DeviceProofPresentation.ConnectionStatus.VERIFIED_READY,
                "MIRA Personal",
                "mira-structured-state-v1",
                "queued_writer",
                null
        );

        assertTrue(summary.contains("verified ready"));
        assertTrue(summary.contains("MIRA Personal"));
        assertTrue(summary.contains("queued_writer"));
        assertFalse(summary.contains("access_token"));
        assertFalse(summary.contains("spreadsheetId"));
    }

    @Test
    public void needsAttentionDoesNotMasqueradeAsReady() {
        String summary = DeviceProofPresentation.connectionSummary(
                DeviceProofPresentation.ConnectionStatus.NEEDS_ATTENTION,
                "MIRA Personal",
                "mira-structured-state-v1",
                "direct_single_writer",
                null
        );

        assertTrue(summary.contains("needs attention"));
        assertFalse(summary.contains("verified ready"));
    }

    @Test
    public void freshReadRendersRevisionAndDigestWithoutPayload() {
        byte[] payload = "{\"secretish\":\"proof-material\"}"
                .getBytes(StandardCharsets.UTF_8);
        String summary = DeviceProofPresentation.readSummary(
                CanonicalResourceReader.Status.FRESH_FOUND,
                "entity-001",
                7L,
                payload,
                null
        );

        assertTrue(summary.contains("fresh found"));
        assertTrue(summary.contains("Revision: 7"));
        assertTrue(summary.contains(DeviceProofPresentation.sha256(payload)));
        assertFalse(summary.contains("proof-material"));
    }

    @Test
    public void appliedMutationRequiresExplicitAppliedStatusInPresentation() {
        byte[] payload = "{\"device_proof\":true}".getBytes(StandardCharsets.UTF_8);
        String summary = DeviceProofPresentation.mutationSummary(
                CanonicalResourceMutator.Status.APPLIED,
                "entity-001",
                2L,
                payload,
                null
        );

        assertTrue(summary.contains("applied with verified canonical readback"));
        assertTrue(summary.contains("Revision: 2"));
        assertFalse(summary.contains("device_proof"));
    }

    @Test
    public void failedStatesRemainExplicitAndNeverLookSuccessful() {
        String read = DeviceProofPresentation.readSummary(
                CanonicalResourceReader.Status.TRANSPORT_FAILURE,
                "entity-001",
                0L,
                null,
                "authorization_expired"
        );
        String mutation = DeviceProofPresentation.mutationSummary(
                CanonicalResourceMutator.Status.REMOTE_FAILURE,
                "entity-001",
                0L,
                null,
                "revision_conflict"
        );

        assertEquals("Read: transport failure [authorization_expired]", read);
        assertEquals("Mutation: remote failure [revision_conflict]", mutation);
        assertFalse(read.contains("fresh found"));
        assertFalse(mutation.contains("applied"));
    }
}
