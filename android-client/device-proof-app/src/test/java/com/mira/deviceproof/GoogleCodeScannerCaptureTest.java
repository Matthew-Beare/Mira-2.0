package com.mira.deviceproof;

import com.google.mlkit.vision.barcode.common.Barcode;
import com.mira.client.core.capture.IdentifierCaptureResolver;

import org.junit.Test;

import static org.junit.Assert.assertEquals;

public final class GoogleCodeScannerCaptureTest {

    @Test
    public void qrResultMapsToQrCaptureWithoutInterpretation() {
        String raw = "{\"schema_version\":1,\"kind\":\"identifier\","
                + "\"identifier_type\":\"upc_a\",\"value\":\"036000291452\"}";

        IdentifierCaptureResolver.DecodedCapture capture =
                GoogleCodeScannerCapture.decodedCapture(Barcode.FORMAT_QR_CODE, raw);

        assertEquals(IdentifierCaptureResolver.CaptureKind.QR_CODE, capture.kind());
        assertEquals(raw, capture.rawValue());
    }

    @Test
    public void supportedLinearFormatsMapExactly() {
        assertEquals(
                IdentifierCaptureResolver.BarcodeFormat.EAN_8,
                GoogleCodeScannerCapture.decodedCapture(Barcode.FORMAT_EAN_8, "96385074")
                        .barcodeFormat()
        );
        assertEquals(
                IdentifierCaptureResolver.BarcodeFormat.UPC_A,
                GoogleCodeScannerCapture.decodedCapture(Barcode.FORMAT_UPC_A, "036000291452")
                        .barcodeFormat()
        );
        assertEquals(
                IdentifierCaptureResolver.BarcodeFormat.EAN_13,
                GoogleCodeScannerCapture.decodedCapture(Barcode.FORMAT_EAN_13, "4006381333931")
                        .barcodeFormat()
        );
    }

    @Test
    public void unexpectedProviderFormatFailsLaterAsUnsupportedCapture() {
        IdentifierCaptureResolver.DecodedCapture capture =
                GoogleCodeScannerCapture.decodedCapture(Barcode.FORMAT_CODE_128, "unexpected");

        assertEquals(IdentifierCaptureResolver.CaptureKind.BARCODE, capture.kind());
        assertEquals(IdentifierCaptureResolver.BarcodeFormat.UNSUPPORTED, capture.barcodeFormat());
    }
}
