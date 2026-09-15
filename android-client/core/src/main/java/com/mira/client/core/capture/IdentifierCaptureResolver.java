package com.mira.client.core.capture;

import com.mira.client.core.sync.OfflineSyncStateStore;
import com.mira.client.core.sync.VerifiedChangeQuery;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Passive decoded-camera identifier parsing and canonical asset resolution.
 *
 * <p>This component has no mutation dependency. It accepts already-decoded QR/barcode material,
 * validates the identifier using the bounded IDENT-001 capture semantics, queries only verified
 * canonical readback projection, and returns matching Entity UUIDs. A passive scan cannot create
 * an asset, attach an identifier, or move inventory because no write surface is reachable here.</p>
 */
public final class IdentifierCaptureResolver {
    private static final String IDENTIFIER_DATA_CLASS = "identifier";
    private static final int IDENTIFIER_SCHEMA_VERSION = 1;
    private static final int QR_SCHEMA_VERSION = 1;
    private static final int MAX_QR_CHARS = 4096;
    private static final int MAX_VALUE_CHARS = 500;
    private static final int MAX_NAMESPACE_CHARS = 300;

    private static final Pattern ENTITY_UUID = Pattern.compile(
            "^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    );
    private static final Pattern MAC_COMPACT = Pattern.compile("^[0-9A-Fa-f]{12}$");
    private static final Pattern MAC_COLON =
            Pattern.compile("^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$");
    private static final Pattern MAC_HYPHEN =
            Pattern.compile("^(?:[0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$");
    private static final Pattern MAC_CISCO =
            Pattern.compile("^(?:[0-9A-Fa-f]{4}\\.){2}[0-9A-Fa-f]{4}$");

    private static final Set<String> IDENTIFIER_TYPES = immutableSet(
            "gtin8",
            "upc_a",
            "ean13",
            "gtin14",
            "merchant_sku",
            "manufacturer_part_number",
            "model_number",
            "serial_number",
            "imei",
            "mac"
    );
    private static final Set<String> NAMESPACED_TYPES = immutableSet(
            "merchant_sku",
            "manufacturer_part_number",
            "model_number",
            "serial_number"
    );
    private static final Set<String> SERIAL_LEVEL_TYPES = immutableSet(
            "serial_number",
            "imei",
            "mac"
    );
    private static final Set<String> QR_KEYS = immutableSet(
            "schema_version",
            "kind",
            "identifier_type",
            "namespace",
            "value"
    );

    private final VerifiedChangeQuery query;

    public IdentifierCaptureResolver(VerifiedChangeQuery query) {
        this.query = Objects.requireNonNull(query, "query");
    }

    /** Resolve one passive decoded observation against verified canonical identifier state. */
    public ResolveResult resolve(DecodedCapture capture) {
        final CapturedIdentifier wanted;
        try {
            wanted = parse(Objects.requireNonNull(capture, "capture"));
        } catch (CaptureValidationException | IllegalArgumentException exc) {
            return ResolveResult.failure(Status.INVALID_CAPTURE, "invalid_capture", exc.getMessage());
        }

        VerifiedChangeQuery.QueryResult rows = query.queryLatest(IDENTIFIER_DATA_CLASS);
        if (rows.status() == VerifiedChangeQuery.Status.TRANSPORT_FAILURE) {
            return ResolveResult.failure(Status.TRANSPORT_FAILURE, rows.errorCode(), rows.message());
        }
        if (rows.status() == VerifiedChangeQuery.Status.PROTOCOL_FAILURE) {
            return ResolveResult.failure(Status.PROTOCOL_FAILURE, rows.errorCode(), rows.message());
        }
        if (rows.status() == VerifiedChangeQuery.Status.LOCAL_FAILURE) {
            return ResolveResult.failure(Status.LOCAL_FAILURE, rows.errorCode(), rows.message());
        }
        if (rows.status() != VerifiedChangeQuery.Status.COMPLETE) {
            return ResolveResult.failure(
                    Status.PROTOCOL_FAILURE,
                    "protocol_error",
                    "verified identifier query returned unexpected status"
            );
        }

        ArrayList<String> matches = new ArrayList<>();
        for (OfflineSyncStateStore.ResourceSnapshot snapshot : rows.snapshots()) {
            final IdentifierSnapshot identifier;
            try {
                identifier = parseIdentifierSnapshot(snapshot);
            } catch (CaptureValidationException exc) {
                return ResolveResult.failure(
                        Status.INTEGRITY_FAILURE,
                        "identifier_integrity_error",
                        exc.getMessage()
                );
            }
            if (!wanted.identifierType.equals(identifier.identifierType)) {
                continue;
            }
            if (!Objects.equals(wanted.namespaceKey, identifier.namespaceKey)) {
                continue;
            }
            if (!wanted.normalizedValue.equals(identifier.normalizedValue)) {
                continue;
            }
            if (!matches.contains(identifier.entityUuid)) {
                matches.add(identifier.entityUuid);
            }
        }
        Collections.sort(matches);

        if (matches.isEmpty()) {
            return ResolveResult.completed(Status.UNRESOLVED, wanted, matches);
        }
        if (matches.size() == 1) {
            return ResolveResult.completed(Status.RESOLVED, wanted, matches);
        }
        if (SERIAL_LEVEL_TYPES.contains(wanted.identifierType)) {
            return ResolveResult.failure(
                    Status.INTEGRITY_FAILURE,
                    "identifier_integrity_error",
                    "serial-level identifier resolves to multiple canonical assets"
            );
        }
        return ResolveResult.completed(Status.AMBIGUOUS, wanted, matches);
    }

    /** Parse one decoded capture without performing provider I/O. */
    public static CapturedIdentifier parse(DecodedCapture capture)
            throws CaptureValidationException {
        Objects.requireNonNull(capture, "capture");
        if (capture.kind == CaptureKind.BARCODE) {
            return parseBarcode(capture);
        }
        if (capture.kind == CaptureKind.QR_CODE) {
            return parseQr(capture.rawValue);
        }
        throw new CaptureValidationException("unsupported capture kind");
    }

    private static CapturedIdentifier parseBarcode(DecodedCapture capture)
            throws CaptureValidationException {
        final String identifierType;
        switch (capture.barcodeFormat) {
            case EAN_8:
                identifierType = "gtin8";
                break;
            case UPC_A:
                identifierType = "upc_a";
                break;
            case EAN_13:
                identifierType = "ean13";
                break;
            case UNSUPPORTED:
            default:
                throw new CaptureValidationException("barcode symbology is unsupported");
        }
        String source = requireText(capture.rawValue, "barcode value", MAX_VALUE_CHARS);
        return new CapturedIdentifier(
                identifierType,
                null,
                null,
                source,
                normalizedValue(identifierType, source)
        );
    }

    private static CapturedIdentifier parseQr(String raw) throws CaptureValidationException {
        String body = requireText(raw, "QR payload", MAX_QR_CHARS);
        final JSONObject payload;
        try {
            payload = new JSONObject(body);
        } catch (JSONException exc) {
            throw new CaptureValidationException("QR payload must be a JSON object", exc);
        }

        // Android's platform org.json does not expose JSONObject.keySet() on every supported API.
        // keys() is available throughout this app's API range and keeps strict unknown-field checks.
        Iterator<String> keys = payload.keys();
        while (keys.hasNext()) {
            String key = keys.next();
            if (!QR_KEYS.contains(key)) {
                throw new CaptureValidationException("QR payload contains unsupported field: " + key);
            }
        }

        if (payload.optInt("schema_version", -1) != QR_SCHEMA_VERSION) {
            throw new CaptureValidationException("QR schema_version must be 1");
        }
        if (!"identifier".equals(payload.optString("kind", null))) {
            throw new CaptureValidationException("QR kind must be identifier");
        }
        String type = identifierType(payload.optString("identifier_type", null));
        String source = requireText(payload.optString("value", null), "value", MAX_VALUE_CHARS);

        String namespace = null;
        String namespaceKey = null;
        boolean namespacePresent = payload.has("namespace") && !payload.isNull("namespace");
        if (NAMESPACED_TYPES.contains(type)) {
            if (!namespacePresent) {
                throw new CaptureValidationException(
                        "namespace is required for identifier type " + type
                );
            }
            namespace = requireText(
                    payload.optString("namespace", null),
                    "namespace",
                    MAX_NAMESPACE_CHARS
            );
            namespaceKey = normalizeAsciiLocal(namespace, "namespace");
        } else if (namespacePresent) {
            throw new CaptureValidationException(type + " is global and must not include namespace");
        }

        return new CapturedIdentifier(
                type,
                namespace,
                namespaceKey,
                source,
                normalizedValue(type, source)
        );
    }

    private static IdentifierSnapshot parseIdentifierSnapshot(
            OfflineSyncStateStore.ResourceSnapshot snapshot
    ) throws CaptureValidationException {
        if (!IDENTIFIER_DATA_CLASS.equals(snapshot.dataClass())) {
            throw new CaptureValidationException("identifier query returned wrong data class");
        }
        final JSONObject payload;
        try {
            payload = new JSONObject(new String(snapshot.payload(), StandardCharsets.UTF_8));
        } catch (JSONException exc) {
            throw new CaptureValidationException("canonical identifier payload is invalid JSON", exc);
        }
        if (payload.optInt("schema_version", -1) != IDENTIFIER_SCHEMA_VERSION) {
            throw new CaptureValidationException("canonical identifier schema version is unsupported");
        }

        String identifierId = requireText(
                payload.optString("identifier_id", null),
                "identifier_id",
                128
        );
        if (!snapshot.resourceId().equals(identifierId)) {
            throw new CaptureValidationException(
                    "canonical identifier_id does not match resource identity"
            );
        }
        String entityUuid = requireText(
                payload.optString("entity_uuid", null),
                "entity_uuid",
                128
        ).toLowerCase(Locale.ROOT);
        if (!ENTITY_UUID.matcher(entityUuid).matches()) {
            throw new CaptureValidationException("canonical identifier entity_uuid is invalid");
        }

        String type = identifierType(payload.optString("identifier_type", null));
        String source = requireText(
                payload.optString("source_value", null),
                "source_value",
                MAX_VALUE_CHARS
        );
        String normalized = requireText(
                payload.optString("normalized_value", null),
                "normalized_value",
                MAX_VALUE_CHARS
        );
        String verification = requireText(
                payload.optString("verification_state", null),
                "verification_state",
                32
        );
        if (!"observed".equals(verification) && !"verified".equals(verification)) {
            throw new CaptureValidationException("canonical identifier verification_state is invalid");
        }

        String namespace = nullableText(payload, "namespace", MAX_NAMESPACE_CHARS);
        String namespaceKey = nullableText(payload, "namespace_key", MAX_NAMESPACE_CHARS);
        if (NAMESPACED_TYPES.contains(type)) {
            if (namespace == null || namespaceKey == null) {
                throw new CaptureValidationException(
                        "canonical namespaced identifier is missing namespace material"
                );
            }
        } else if (namespace != null || namespaceKey != null) {
            throw new CaptureValidationException(
                    "canonical global identifier contains namespace material"
            );
        }

        return new IdentifierSnapshot(entityUuid, type, namespaceKey, source, normalized);
    }

    private static String nullableText(JSONObject payload, String field, int maximum)
            throws CaptureValidationException {
        if (!payload.has(field) || payload.isNull(field)) {
            return null;
        }
        return requireText(payload.optString(field, null), field, maximum);
    }

    private static String identifierType(String value) throws CaptureValidationException {
        String normalized = requireText(value, "identifier_type", 64).toLowerCase(Locale.ROOT);
        if (!IDENTIFIER_TYPES.contains(normalized)) {
            throw new CaptureValidationException("identifier_type is unsupported: " + normalized);
        }
        return normalized;
    }

    private static String normalizedValue(String type, String source)
            throws CaptureValidationException {
        if ("gtin8".equals(type)) {
            return validateGtin(source, 8, "GTIN-8");
        }
        if ("upc_a".equals(type)) {
            return validateGtin(source, 12, "UPC-A");
        }
        if ("ean13".equals(type)) {
            return validateGtin(source, 13, "EAN-13");
        }
        if ("gtin14".equals(type)) {
            return validateGtin(source, 14, "GTIN-14");
        }
        if ("imei".equals(type)) {
            if (!source.matches("^[0-9]{15}$") || !luhnValid(source)) {
                throw new CaptureValidationException("IMEI must be 15 digits with valid Luhn check");
            }
            return source;
        }
        if ("mac".equals(type)) {
            return normalizeMac(source);
        }
        return normalizeAsciiLocal(source, "identifier value");
    }

    private static String validateGtin(String value, int length, String label)
            throws CaptureValidationException {
        if (!value.matches("^[0-9]{" + length + "}$")) {
            throw new CaptureValidationException(
                    label + " must contain exactly " + length + " digits"
            );
        }
        int weighted = 0;
        int bodyIndex = 0;
        for (int index = value.length() - 2; index >= 0; index--) {
            int digit = value.charAt(index) - '0';
            weighted += digit * (bodyIndex % 2 == 0 ? 3 : 1);
            bodyIndex += 1;
        }
        int expected = (10 - (weighted % 10)) % 10;
        if (expected != value.charAt(value.length() - 1) - '0') {
            throw new CaptureValidationException(label + " check digit is invalid");
        }
        return value;
    }

    private static boolean luhnValid(String digits) {
        int total = 0;
        for (int index = 0; index < digits.length(); index++) {
            int value = digits.charAt(index) - '0';
            if (index % 2 == 1) {
                value *= 2;
                if (value > 9) {
                    value -= 9;
                }
            }
            total += value;
        }
        return total % 10 == 0;
    }

    private static String normalizeMac(String value) throws CaptureValidationException {
        if (!MAC_COMPACT.matcher(value).matches()
                && !MAC_COLON.matcher(value).matches()
                && !MAC_HYPHEN.matcher(value).matches()
                && !MAC_CISCO.matcher(value).matches()) {
            throw new CaptureValidationException(
                    "MAC must use compact, colon, hyphen, or Cisco-dot form"
            );
        }
        return value.replace(":", "").replace("-", "").replace(".", "")
                .toUpperCase(Locale.ROOT);
    }

    private static String normalizeAsciiLocal(String value, String field)
            throws CaptureValidationException {
        String normalized = Normalizer.normalize(value, Normalizer.Form.NFKC).trim()
                .replaceAll("\\s+", " ");
        if (normalized.isEmpty()) {
            throw new CaptureValidationException(field + " cannot normalize to blank");
        }
        for (int index = 0; index < normalized.length(); index++) {
            char character = normalized.charAt(index);
            if (character < 0x20 || character > 0x7e) {
                throw new CaptureValidationException(
                        field + " contains Unicode not supported by Android capture v1"
                );
            }
        }
        return normalized.toLowerCase(Locale.ROOT);
    }

    private static String requireText(String value, String field, int maximum)
            throws CaptureValidationException {
        if (value == null) {
            throw new CaptureValidationException(field + " must be text");
        }
        String normalized = value.trim();
        if (normalized.isEmpty()) {
            throw new CaptureValidationException(field + " must not be blank");
        }
        if (normalized.length() > maximum) {
            throw new CaptureValidationException(field + " exceeds maximum length " + maximum);
        }
        return normalized;
    }

    private static Set<String> immutableSet(String... values) {
        return Collections.unmodifiableSet(new HashSet<>(Arrays.asList(values)));
    }

    public enum CaptureKind {
        QR_CODE,
        BARCODE
    }

    public enum BarcodeFormat {
        EAN_8,
        UPC_A,
        EAN_13,
        UNSUPPORTED
    }

    public enum Status {
        RESOLVED,
        UNRESOLVED,
        AMBIGUOUS,
        INVALID_CAPTURE,
        TRANSPORT_FAILURE,
        PROTOCOL_FAILURE,
        LOCAL_FAILURE,
        INTEGRITY_FAILURE
    }

    /** Raw output from a camera/scanner edge, before canonical interpretation. */
    public static final class DecodedCapture {
        private final CaptureKind kind;
        private final BarcodeFormat barcodeFormat;
        private final String rawValue;

        private DecodedCapture(CaptureKind kind, BarcodeFormat barcodeFormat, String rawValue) {
            this.kind = Objects.requireNonNull(kind, "kind");
            this.barcodeFormat = barcodeFormat;
            this.rawValue = rawValue;
        }

        public static DecodedCapture qr(String rawValue) {
            return new DecodedCapture(CaptureKind.QR_CODE, null, rawValue);
        }

        public static DecodedCapture barcode(BarcodeFormat format, String rawValue) {
            return new DecodedCapture(
                    CaptureKind.BARCODE,
                    Objects.requireNonNull(format, "format"),
                    rawValue
            );
        }

        public CaptureKind kind() {
            return kind;
        }

        public BarcodeFormat barcodeFormat() {
            return barcodeFormat;
        }

        public String rawValue() {
            return rawValue;
        }
    }

    /** Validated nonauthoritative identifier material extracted from a scan. */
    public static final class CapturedIdentifier {
        private final String identifierType;
        private final String namespace;
        private final String namespaceKey;
        private final String sourceValue;
        private final String normalizedValue;

        CapturedIdentifier(
                String identifierType,
                String namespace,
                String namespaceKey,
                String sourceValue,
                String normalizedValue
        ) {
            this.identifierType = identifierType;
            this.namespace = namespace;
            this.namespaceKey = namespaceKey;
            this.sourceValue = sourceValue;
            this.normalizedValue = normalizedValue;
        }

        public String identifierType() {
            return identifierType;
        }

        public String namespace() {
            return namespace;
        }

        public String namespaceKey() {
            return namespaceKey;
        }

        public String sourceValue() {
            return sourceValue;
        }

        public String normalizedValue() {
            return normalizedValue;
        }
    }

    /** Immutable passive resolution result. */
    public static final class ResolveResult {
        private final Status status;
        private final CapturedIdentifier identifier;
        private final List<String> entityUuids;
        private final String errorCode;
        private final String message;

        private ResolveResult(
                Status status,
                CapturedIdentifier identifier,
                List<String> entityUuids,
                String errorCode,
                String message
        ) {
            this.status = Objects.requireNonNull(status, "status");
            this.identifier = identifier;
            this.entityUuids = Collections.unmodifiableList(new ArrayList<>(entityUuids));
            this.errorCode = errorCode;
            this.message = message;
        }

        static ResolveResult completed(
                Status status,
                CapturedIdentifier identifier,
                List<String> entityUuids
        ) {
            return new ResolveResult(status, identifier, entityUuids, null, null);
        }

        static ResolveResult failure(Status status, String errorCode, String message) {
            return new ResolveResult(
                    status,
                    null,
                    Collections.<String>emptyList(),
                    errorCode,
                    message
            );
        }

        public Status status() {
            return status;
        }

        public CapturedIdentifier identifier() {
            return identifier;
        }

        public List<String> entityUuids() {
            return entityUuids;
        }

        public String entityUuid() {
            return entityUuids.size() == 1 ? entityUuids.get(0) : null;
        }

        public String errorCode() {
            return errorCode;
        }

        public String message() {
            return message;
        }
    }

    public static final class CaptureValidationException extends Exception {
        CaptureValidationException(String message) {
            super(message);
        }

        CaptureValidationException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    private static final class IdentifierSnapshot {
        final String entityUuid;
        final String identifierType;
        final String namespaceKey;
        final String sourceValue;
        final String normalizedValue;

        IdentifierSnapshot(
                String entityUuid,
                String identifierType,
                String namespaceKey,
                String sourceValue,
                String normalizedValue
        ) {
            this.entityUuid = entityUuid;
            this.identifierType = identifierType;
            this.namespaceKey = namespaceKey;
            this.sourceValue = sourceValue;
            this.normalizedValue = normalizedValue;
        }
    }
}
