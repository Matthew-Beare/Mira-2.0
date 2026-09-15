package com.mira.client.core.capture;

import com.mira.client.core.sync.OfflineSyncStateStore;
import com.mira.client.core.sync.ReconnectCoordinator;
import com.mira.client.core.sync.VerifiedChangeQuery;

import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.Deque;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

public final class IdentifierCaptureResolverTest {
    private static final String ASSET_A = "123e4567-e89b-42d3-a456-426614174000";
    private static final String ASSET_B = "223e4567-e89b-42d3-a456-426614174001";

    @Test
    public void upcScanResolvesOneCanonicalAssetWithoutAnyMutationCall() {
        FakeTransport transport = terminalTransport(identifier(
                "identifier-upc-a",
                ASSET_A,
                "upc_a",
                null,
                null,
                "036000291452",
                "036000291452"
        ));
        IdentifierCaptureResolver resolver = resolver(transport);

        IdentifierCaptureResolver.ResolveResult result = resolver.resolve(
                IdentifierCaptureResolver.DecodedCapture.barcode(
                        IdentifierCaptureResolver.BarcodeFormat.UPC_A,
                        "036000291452"
                )
        );

        assertEquals(IdentifierCaptureResolver.Status.RESOLVED, result.status());
        assertEquals(ASSET_A, result.entityUuid());
        assertEquals("upc_a", result.identifier().identifierType());
        assertEquals(1, transport.readCalls);
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void validUnknownBarcodeRemainsUnresolvedAndDoesNotCreateAnything() {
        FakeTransport transport = terminalTransport();

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.barcode(
                        IdentifierCaptureResolver.BarcodeFormat.EAN_13,
                        "4006381333931"
                )
        );

        assertEquals(IdentifierCaptureResolver.Status.UNRESOLVED, result.status());
        assertEquals(0, result.entityUuids().size());
        assertEquals(1, transport.readCalls);
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void invalidCheckDigitFailsBeforeRemoteRead() {
        FakeTransport transport = terminalTransport();

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.barcode(
                        IdentifierCaptureResolver.BarcodeFormat.UPC_A,
                        "036000291453"
                )
        );

        assertEquals(IdentifierCaptureResolver.Status.INVALID_CAPTURE, result.status());
        assertEquals("invalid_capture", result.errorCode());
        assertEquals(0, transport.readCalls);
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void strictQrEnvelopeResolvesNamespacedSerial() {
        FakeTransport transport = terminalTransport(identifier(
                "identifier-serial-a",
                ASSET_A,
                "serial_number",
                "Vendor Name",
                "vendor name",
                " ABC-123 ",
                "abc-123"
        ));
        String qr = "{\"schema_version\":1,\"kind\":\"identifier\","
                + "\"identifier_type\":\"serial_number\","
                + "\"namespace\":\"Vendor   Name\",\"value\":\"ABC-123\"}";

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.qr(qr)
        );

        assertEquals(IdentifierCaptureResolver.Status.RESOLVED, result.status());
        assertEquals(ASSET_A, result.entityUuid());
        assertEquals("vendor name", result.identifier().namespaceKey());
        assertEquals("abc-123", result.identifier().normalizedValue());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void productIdentifierMayHonestlyResolveAmbiguousAssets() {
        FakeTransport transport = terminalTransport(
                identifier(
                        "identifier-ean-a",
                        ASSET_A,
                        "ean13",
                        null,
                        null,
                        "4006381333931",
                        "4006381333931"
                ),
                identifier(
                        "identifier-ean-b",
                        ASSET_B,
                        "ean13",
                        null,
                        null,
                        "4006381333931",
                        "4006381333931"
                )
        );

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.barcode(
                        IdentifierCaptureResolver.BarcodeFormat.EAN_13,
                        "4006381333931"
                )
        );

        assertEquals(IdentifierCaptureResolver.Status.AMBIGUOUS, result.status());
        assertEquals(Arrays.asList(ASSET_A, ASSET_B), result.entityUuids());
        assertNull(result.entityUuid());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void serialCollisionFailsIntegrityClosed() {
        FakeTransport transport = terminalTransport(
                identifier(
                        "identifier-serial-a",
                        ASSET_A,
                        "serial_number",
                        "vendor",
                        "vendor",
                        "ABC-123",
                        "abc-123"
                ),
                identifier(
                        "identifier-serial-b",
                        ASSET_B,
                        "serial_number",
                        "vendor",
                        "vendor",
                        "ABC-123",
                        "abc-123"
                )
        );
        String qr = "{\"schema_version\":1,\"kind\":\"identifier\","
                + "\"identifier_type\":\"serial_number\","
                + "\"namespace\":\"vendor\",\"value\":\"ABC-123\"}";

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.qr(qr)
        );

        assertEquals(IdentifierCaptureResolver.Status.INTEGRITY_FAILURE, result.status());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void malformedCanonicalIdentifierFailsIntegrityClosed() {
        FakeTransport transport = terminalTransport(new OfflineSyncStateStore.ResourceSnapshot(
                "identifier",
                "identifier-bad",
                1,
                bytes("{\"schema_version\":1,\"identifier_id\":\"different-id\"}")
        ));

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.barcode(
                        IdentifierCaptureResolver.BarcodeFormat.UPC_A,
                        "036000291452"
                )
        );

        assertEquals(IdentifierCaptureResolver.Status.INTEGRITY_FAILURE, result.status());
        assertEquals(0, transport.reconcileCalls);
    }

    @Test
    public void qrRejectsUnexpectedFieldsBeforeRemoteRead() {
        FakeTransport transport = terminalTransport();
        String qr = "{\"schema_version\":1,\"kind\":\"identifier\","
                + "\"identifier_type\":\"upc_a\",\"value\":\"036000291452\","
                + "\"move_to\":\"garage\"}";

        IdentifierCaptureResolver.ResolveResult result = resolver(transport).resolve(
                IdentifierCaptureResolver.DecodedCapture.qr(qr)
        );

        assertEquals(IdentifierCaptureResolver.Status.INVALID_CAPTURE, result.status());
        assertEquals(0, transport.readCalls);
        assertEquals(0, transport.reconcileCalls);
    }

    private static IdentifierCaptureResolver resolver(FakeTransport transport) {
        return new IdentifierCaptureResolver(new VerifiedChangeQuery(transport));
    }

    private static FakeTransport terminalTransport(
            OfflineSyncStateStore.ResourceSnapshot... snapshots
    ) {
        FakeTransport transport = new FakeTransport();
        transport.pages.add(ReconnectCoordinator.ChangePage.verified(
                null,
                "mira-change-v1:" + snapshots.length,
                false,
                Arrays.asList(snapshots)
        ));
        return transport;
    }

    private static OfflineSyncStateStore.ResourceSnapshot identifier(
            String identifierId,
            String entityUuid,
            String type,
            String namespace,
            String namespaceKey,
            String source,
            String normalized
    ) {
        String namespaceJson = namespace == null ? "null" : "\"" + namespace + "\"";
        String namespaceKeyJson = namespaceKey == null ? "null" : "\"" + namespaceKey + "\"";
        String payload = "{"
                + "\"schema_version\":1,"
                + "\"identifier_id\":\"" + identifierId + "\","
                + "\"entity_uuid\":\"" + entityUuid + "\","
                + "\"identifier_type\":\"" + type + "\","
                + "\"namespace\":" + namespaceJson + ","
                + "\"namespace_key\":" + namespaceKeyJson + ","
                + "\"source_value\":\"" + source + "\","
                + "\"normalized_value\":\"" + normalized + "\","
                + "\"verification_state\":\"verified\","
                + "\"note\":null}"
                ;
        return new OfflineSyncStateStore.ResourceSnapshot(
                "identifier",
                identifierId,
                1,
                bytes(payload)
        );
    }

    private static byte[] bytes(String value) {
        return value.getBytes(StandardCharsets.UTF_8);
    }

    private static final class FakeTransport implements ReconnectCoordinator.Transport {
        final Deque<ReconnectCoordinator.ChangePage> pages = new ArrayDeque<>();
        int readCalls;
        int reconcileCalls;

        @Override
        public ReconnectCoordinator.RemoteCommandState reconcileCommand(
                OfflineSyncStateStore.CommandIntent command
        ) {
            reconcileCalls += 1;
            throw new AssertionError("passive capture must never reconcile or submit a command");
        }

        @Override
        public ReconnectCoordinator.ChangePage readChanges(String cursor, int limit) {
            readCalls += 1;
            if (pages.isEmpty()) {
                throw new AssertionError("unexpected readChanges call");
            }
            ReconnectCoordinator.ChangePage page = pages.removeFirst();
            assertEquals(cursor, page.fromCursor());
            return page;
        }
    }
}
