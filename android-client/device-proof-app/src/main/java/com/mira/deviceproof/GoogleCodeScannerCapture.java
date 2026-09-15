package com.mira.deviceproof;

import android.app.Activity;

import com.google.mlkit.vision.barcode.common.Barcode;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanner;
import com.google.mlkit.vision.codescanner.GmsBarcodeScannerOptions;
import com.google.mlkit.vision.codescanner.GmsBarcodeScanning;
import com.mira.client.core.capture.IdentifierCaptureResolver;

import java.util.Objects;

/**
 * Thin app-edge adapter from Google Code Scanner output to provider-neutral MIRA capture input.
 *
 * <p>This class owns camera-provider interaction only. It cannot read or mutate canonical state.
 * Google Play services owns the scanner UI/camera permission; the resulting decoded value is
 * handed to {@link IdentifierCaptureResolver} semantics by the Activity after this edge returns.</p>
 */
public final class GoogleCodeScannerCapture {
    private final GmsBarcodeScanner scanner;

    public GoogleCodeScannerCapture(Activity activity) {
        Objects.requireNonNull(activity, "activity");
        GmsBarcodeScannerOptions options = new GmsBarcodeScannerOptions.Builder()
                .setBarcodeFormats(
                        Barcode.FORMAT_QR_CODE,
                        Barcode.FORMAT_EAN_8,
                        Barcode.FORMAT_UPC_A,
                        Barcode.FORMAT_EAN_13
                )
                .enableAutoZoom()
                .build();
        scanner = GmsBarcodeScanning.getClient(activity, options);
    }

    /** Start one provider-owned scanner interaction. */
    public void start(Callback callback) {
        Callback target = Objects.requireNonNull(callback, "callback");
        scanner.startScan()
                .addOnSuccessListener(barcode -> {
                    try {
                        target.onCaptured(decodedCapture(barcode.getFormat(), barcode.getRawValue()));
                    } catch (RuntimeException exc) {
                        target.onFailure("scanner_result_invalid");
                    }
                })
                .addOnCanceledListener(target::onCancelled)
                .addOnFailureListener(ignored -> target.onFailure("scanner_failed"));
    }

    static IdentifierCaptureResolver.DecodedCapture decodedCapture(int format, String rawValue) {
        if (format == Barcode.FORMAT_QR_CODE) {
            return IdentifierCaptureResolver.DecodedCapture.qr(rawValue);
        }
        if (format == Barcode.FORMAT_EAN_8) {
            return IdentifierCaptureResolver.DecodedCapture.barcode(
                    IdentifierCaptureResolver.BarcodeFormat.EAN_8,
                    rawValue
            );
        }
        if (format == Barcode.FORMAT_UPC_A) {
            return IdentifierCaptureResolver.DecodedCapture.barcode(
                    IdentifierCaptureResolver.BarcodeFormat.UPC_A,
                    rawValue
            );
        }
        if (format == Barcode.FORMAT_EAN_13) {
            return IdentifierCaptureResolver.DecodedCapture.barcode(
                    IdentifierCaptureResolver.BarcodeFormat.EAN_13,
                    rawValue
            );
        }
        return IdentifierCaptureResolver.DecodedCapture.barcode(
                IdentifierCaptureResolver.BarcodeFormat.UNSUPPORTED,
                rawValue
        );
    }

    public interface Callback {
        void onCaptured(IdentifierCaptureResolver.DecodedCapture capture);

        void onCancelled();

        void onFailure(String code);
    }
}
