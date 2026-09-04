package com.mira.deviceproof;

import com.mira.client.core.sync.CanonicalResourceMutator;
import com.mira.client.core.sync.CanonicalResourceReader;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Locale;

/** Pure presentation mapping for the bounded representative-device proof shell. */
public final class DeviceProofPresentation {
    private DeviceProofPresentation() {}

    public enum ConnectionStatus {
        DISCONNECTED,
        AUTHORIZING,
        VERIFYING,
        VERIFIED_READY,
        NEEDS_ATTENTION,
        FAILED
    }

    public static String connectionSummary(
            ConnectionStatus status,
            String displayName,
            String schemaVersion,
            String mutationMode,
            String errorCode
    ) {
        switch (status) {
            case DISCONNECTED:
                return "Connection: disconnected";
            case AUTHORIZING:
                return "Connection: Google authorization required";
            case VERIFYING:
                return "Connection: authorized, verifying MIRA Workspace";
            case VERIFIED_READY:
                return "Connection: verified ready\nWorkspace: " + safe(displayName)
                        + "\nSchema: " + safe(schemaVersion)
                        + "\nMutation mode: " + safe(mutationMode);
            case NEEDS_ATTENTION:
                return "Connection: needs attention\nWorkspace: " + safe(displayName)
                        + "\nSchema: " + safe(schemaVersion)
                        + "\nMutation mode: " + safe(mutationMode);
            case FAILED:
            default:
                return "Connection: failed" + codeSuffix(errorCode);
        }
    }

    public static String readSummary(
            CanonicalResourceReader.Status status,
            String resourceId,
            long revision,
            byte[] payload,
            String errorCode
    ) {
        switch (status) {
            case FRESH_FOUND:
                return "Read: fresh found\nResource: " + safe(resourceId)
                        + "\nRevision: " + revision
                        + "\nPayload SHA-256: " + sha256(payload);
            case FRESH_MISSING:
                return "Read: fresh missing\nResource: " + safe(resourceId);
            case MORE_REMOTE_CHANGES:
                return "Read: more verified remote changes remain; run Read again";
            case TRANSPORT_FAILURE:
                return "Read: transport failure" + codeSuffix(errorCode);
            case PROTOCOL_FAILURE:
                return "Read: protocol failure" + codeSuffix(errorCode);
            case LOCAL_FAILURE:
            default:
                return "Read: local failure" + codeSuffix(errorCode);
        }
    }

    public static String mutationSummary(
            CanonicalResourceMutator.Status status,
            String resourceId,
            long revision,
            byte[] payload,
            String errorCode
    ) {
        switch (status) {
            case APPLIED:
                return "Mutation: applied with verified canonical readback"
                        + "\nResource: " + safe(resourceId)
                        + "\nRevision: " + revision
                        + "\nPayload SHA-256: " + sha256(payload);
            case WAITING_REMOTE:
                return "Mutation: queued; worker result pending. Run Mutate again after worker execution.";
            case BLOCKED_BY_EARLIER_COMMAND:
                return "Mutation: blocked by earlier queued command" + codeSuffix(errorCode);
            case REMOTE_FAILURE:
                return "Mutation: remote failure" + codeSuffix(errorCode);
            case TRANSPORT_FAILURE:
                return "Mutation: transport failure" + codeSuffix(errorCode);
            case PROTOCOL_FAILURE:
                return "Mutation: protocol failure" + codeSuffix(errorCode);
            case LOCAL_FAILURE:
            default:
                return "Mutation: local failure" + codeSuffix(errorCode);
        }
    }

    public static String sha256(byte[] value) {
        if (value == null || value.length == 0) {
            return "unavailable";
        }
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(value);
            StringBuilder text = new StringBuilder(digest.length * 2);
            for (byte item : digest) {
                text.append(String.format(Locale.ROOT, "%02x", item & 0xff));
            }
            return text.toString();
        } catch (NoSuchAlgorithmException exc) {
            return "unavailable";
        }
    }

    public static byte[] utf8(String value) {
        return safe(value).getBytes(StandardCharsets.UTF_8);
    }

    private static String codeSuffix(String errorCode) {
        String value = safe(errorCode);
        return value.isEmpty() ? "" : " [" + value + "]";
    }

    private static String safe(String value) {
        return value == null ? "" : value.trim();
    }
}
