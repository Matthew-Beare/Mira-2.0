package com.mira.deviceproof;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.Intent;
import android.content.IntentSender;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import com.google.android.gms.auth.api.identity.AuthorizationResult;
import com.mira.client.core.capture.IdentifierCaptureResolver;
import com.mira.client.core.sync.CanonicalResourceMutator;
import com.mira.client.core.sync.CanonicalResourceReader;
import com.mira.client.core.sync.GoogleWorkspaceEventTransport;
import com.mira.client.core.sync.GoogleWorkspaceTransport;
import com.mira.client.core.sync.MovementCommandFacade;
import com.mira.client.core.sync.OfflineSyncStateStore;
import com.mira.client.core.sync.ReconnectCoordinator;
import com.mira.client.core.sync.VerifiedChangeQuery;
import com.mira.client.googleworkspace.GooglePlayWorkspaceAuthorization;
import com.mira.client.googleworkspace.GoogleWorkspaceConnection;
import com.mira.client.googleworkspace.GoogleWorkspaceRestApi;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Minimal installable shell for M2-M1 representative-device evidence.
 *
 * <p>This is deliberately not the finished MIRA Android UI. It exposes provider-native
 * connection/scanner actions and bounded canonical proof controls over existing client modules.
 * Provider tokens and spreadsheet IDs are never rendered or logged. Passive scanning is read-only;
 * movement requires a separate explicit button and the replay-safe MOVE-001 command facade.</p>
 */
public final class DeviceProofActivity extends Activity {
    private static final int REQUEST_GOOGLE_AUTHORIZATION = 4101;
    private static final String LOCAL_CLIENT_ID = "mira-device-proof-v1";
    private static final String API_SCHEMA_VERSION = "mira-api-1";
    private static final int MAX_FRESH_READ_PASSES = 16;

    private final ExecutorService ioExecutor = Executors.newSingleThreadExecutor();

    private GooglePlayWorkspaceAuthorization authorization;
    private GoogleWorkspaceRestApi workspaceApi;
    private GoogleWorkspaceConnection workspaceConnection;
    private GoogleWorkspaceConnection.VerifiedBinding verifiedBinding;
    private GoogleWorkspaceConnection.PickerGrant activeGrant;
    private GoogleCodeScannerCapture codeScanner;
    private IdentifierCaptureResolver captureResolver;
    private CanonicalResourceReader reader;
    private CanonicalResourceMutator mutator;
    private MovementCommandFacade movementFacade;
    private OfflineSyncStateStore stateStore;
    private ReconnectCoordinator coordinator;
    private String lastResolvedEntityUuid;

    private TextView connectionStatus;
    private TextView proofStatus;
    private EditText subjectId;
    private EditText movementDestination;
    private EditText dataClass;
    private EditText resourceId;
    private EditText expectedRevision;
    private EditText payloadJson;
    private Button connectButton;
    private Button scanButton;
    private Button moveButton;
    private Button readButton;
    private Button mutateButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        authorization = new GooglePlayWorkspaceAuthorization(this);
        workspaceApi = new GoogleWorkspaceRestApi();
        workspaceConnection = new GoogleWorkspaceConnection(workspaceApi);
        codeScanner = new GoogleCodeScannerCapture(this);
        setContentView(buildContent());
        renderDisconnected();
    }

    private View buildContent() {
        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(16), dp(16), dp(24));
        scroll.addView(root);

        TextView title = text("MIRA representative-device proof", 22f);
        root.addView(title);

        TextView warning = text(
                "Developer proof shell only. Uses Google provider UI and existing MIRA client modules. "
                        + "No OAuth token or Workspace file ID is displayed.",
                14f
        );
        warning.setPadding(0, dp(8), 0, dp(16));
        root.addView(warning);

        connectionStatus = text("", 15f);
        root.addView(connectionStatus);

        connectButton = new Button(this);
        connectButton.setText("Connect Google Workspace");
        connectButton.setOnClickListener(ignored -> beginAuthorization());
        root.addView(connectButton);

        TextView captureHeader = text("Capture / movement proof", 18f);
        captureHeader.setPadding(0, dp(20), 0, dp(8));
        root.addView(captureHeader);

        scanButton = new Button(this);
        scanButton.setText("Scan identifier (read-only)");
        scanButton.setOnClickListener(ignored -> runScan());
        root.addView(scanButton);

        movementDestination = input("Move destination location ID", "existing canonical location");
        root.addView(movementDestination);

        moveButton = new Button(this);
        moveButton.setText("Move scanned asset explicitly");
        moveButton.setOnClickListener(ignored -> runExplicitMove());
        root.addView(moveButton);

        TextView proofHeader = text("Generic canonical proof controls", 18f);
        proofHeader.setPadding(0, dp(20), 0, dp(8));
        root.addView(proofHeader);

        subjectId = input("Proof subject ID", "synthetic same-user subject identity");
        root.addView(subjectId);
        dataClass = input("Data class", "entity");
        dataClass.setText("entity");
        root.addView(dataClass);
        resourceId = input("Resource ID", "device-proof-entity");
        root.addView(resourceId);
        expectedRevision = input("Expected revision", "0");
        expectedRevision.setText("0");
        root.addView(expectedRevision);
        payloadJson = input("Payload JSON object", "{\"device_proof\":true}");
        payloadJson.setMinLines(3);
        root.addView(payloadJson);

        readButton = new Button(this);
        readButton.setText("Read canonical resource");
        readButton.setOnClickListener(ignored -> runRead());
        root.addView(readButton);

        mutateButton = new Button(this);
        mutateButton.setText("Queue canonical mutation");
        mutateButton.setOnClickListener(ignored -> runMutation());
        root.addView(mutateButton);

        proofStatus = text("Proof: not run", 15f);
        proofStatus.setPadding(0, dp(12), 0, 0);
        root.addView(proofStatus);

        return scroll;
    }

    private void beginAuthorization() {
        disableProofActions();
        connectionStatus.setText(DeviceProofPresentation.connectionSummary(
                DeviceProofPresentation.ConnectionStatus.AUTHORIZING,
                null,
                null,
                null,
                null
        ));
        authorization.beginPickerAuthorization()
                .addOnSuccessListener(this, this::handleAuthorizationResult)
                .addOnFailureListener(this, ignored -> renderConnectionFailure("authorization_failed"));
    }

    private void handleAuthorizationResult(AuthorizationResult result) {
        try {
            if (result != null && result.hasResolution()) {
                PendingIntent pending = authorization.resolution(result);
                startIntentSenderForResult(
                        pending.getIntentSender(),
                        REQUEST_GOOGLE_AUTHORIZATION,
                        null,
                        0,
                        0,
                        0
                );
                return;
            }
            verifyGrant(authorization.grantFromResult(result));
        } catch (GooglePlayWorkspaceAuthorization.AuthorizationException exc) {
            renderConnectionFailure(exc.code());
        } catch (IntentSender.SendIntentException exc) {
            renderConnectionFailure("authorization_resolution_failed");
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != REQUEST_GOOGLE_AUTHORIZATION) {
            return;
        }
        if (resultCode != RESULT_OK || data == null) {
            renderConnectionFailure("authorization_cancelled");
            return;
        }
        try {
            verifyGrant(authorization.grantFromIntent(data));
        } catch (GooglePlayWorkspaceAuthorization.AuthorizationException exc) {
            renderConnectionFailure(exc.code());
        }
    }

    private void verifyGrant(GoogleWorkspaceConnection.PickerGrant grant) {
        connectionStatus.setText(DeviceProofPresentation.connectionSummary(
                DeviceProofPresentation.ConnectionStatus.VERIFYING,
                null,
                null,
                null,
                null
        ));
        disableProofActions();
        ioExecutor.execute(() -> {
            try {
                GoogleWorkspaceConnection.VerifiedBinding binding = workspaceConnection.connect(grant);
                GoogleWorkspaceTransport.SheetsGateway gateway = workspaceApi.gateway(binding, grant);
                GoogleWorkspaceEventTransport transport = new GoogleWorkspaceEventTransport(gateway);
                OfflineSyncStateStore newStateStore = new OfflineSyncStateStore(
                        getApplicationContext(),
                        LOCAL_CLIENT_ID
                );
                ReconnectCoordinator newCoordinator = new ReconnectCoordinator(
                        newStateStore,
                        transport
                );
                CanonicalResourceReader newReader = new CanonicalResourceReader(
                        newStateStore,
                        transport
                );
                CanonicalResourceMutator newMutator = new CanonicalResourceMutator(
                        newStateStore,
                        newCoordinator
                );
                MovementCommandFacade newMovementFacade = new MovementCommandFacade(
                        newStateStore,
                        newCoordinator
                );
                IdentifierCaptureResolver newCaptureResolver = new IdentifierCaptureResolver(
                        new VerifiedChangeQuery(transport)
                );
                runOnUiThread(() -> {
                    activeGrant = grant;
                    verifiedBinding = binding;
                    stateStore = newStateStore;
                    coordinator = newCoordinator;
                    reader = newReader;
                    mutator = newMutator;
                    movementFacade = newMovementFacade;
                    captureResolver = newCaptureResolver;
                    lastResolvedEntityUuid = null;
                    renderBinding(binding);
                });
            } catch (GoogleWorkspaceConnection.ConnectionException exc) {
                runOnUiThread(() -> renderConnectionFailure(exc.code()));
            } catch (RuntimeException exc) {
                runOnUiThread(() -> renderConnectionFailure("workspace_verification_failed"));
            }
        });
    }

    private void renderBinding(GoogleWorkspaceConnection.VerifiedBinding binding) {
        if (binding.sharedWriterReady()) {
            connectionStatus.setText(DeviceProofPresentation.connectionSummary(
                    DeviceProofPresentation.ConnectionStatus.VERIFIED_READY,
                    binding.displayName(),
                    binding.schemaVersion(),
                    binding.mutationMode(),
                    null
            ));
            scanButton.setEnabled(true);
            moveButton.setEnabled(false);
            readButton.setEnabled(true);
            mutateButton.setEnabled(true);
        } else {
            connectionStatus.setText(DeviceProofPresentation.connectionSummary(
                    DeviceProofPresentation.ConnectionStatus.NEEDS_ATTENTION,
                    binding.displayName(),
                    binding.schemaVersion(),
                    binding.mutationMode(),
                    null
            ));
            disableProofActions();
        }
    }

    private void runScan() {
        final IdentifierCaptureResolver resolver = captureResolver;
        if (resolver == null || verifiedBinding == null || activeGrant == null) {
            proofStatus.setText("Scan: unavailable [workspace_not_verified]");
            return;
        }
        scanButton.setEnabled(false);
        moveButton.setEnabled(false);
        codeScanner.start(new GoogleCodeScannerCapture.Callback() {
            @Override
            public void onCaptured(IdentifierCaptureResolver.DecodedCapture capture) {
                ioExecutor.execute(() -> {
                    IdentifierCaptureResolver.ResolveResult result;
                    try {
                        result = resolver.resolve(capture);
                    } catch (RuntimeException exc) {
                        runOnUiThread(() -> finishScan(null, "Scan: local failure [capture_exception]"));
                        return;
                    }
                    String resolved = null;
                    if (result.status() == IdentifierCaptureResolver.Status.RESOLVED
                            && result.entityUuids().size() == 1) {
                        resolved = result.entityUuids().get(0);
                    }
                    final String resolvedEntity = resolved;
                    runOnUiThread(() -> finishScan(resolvedEntity, scanSummary(result)));
                });
            }

            @Override
            public void onCancelled() {
                runOnUiThread(() -> finishScan(null, "Scan: cancelled"));
            }

            @Override
            public void onFailure(String code) {
                runOnUiThread(() -> finishScan(null, "Scan: failed [" + code + "]"));
            }
        });
    }

    private void finishScan(String resolvedEntityUuid, String summary) {
        lastResolvedEntityUuid = resolvedEntityUuid;
        proofStatus.setText(summary);
        if (captureResolver != null && verifiedBinding != null && activeGrant != null) {
            scanButton.setEnabled(true);
            moveButton.setEnabled(resolvedEntityUuid != null);
        }
    }

    private static String scanSummary(IdentifierCaptureResolver.ResolveResult result) {
        switch (result.status()) {
            case RESOLVED:
                return "Scan: resolved one canonical asset (read-only)";
            case UNRESOLVED:
                return "Scan: identifier not found in canonical inventory (read-only)";
            case AMBIGUOUS:
                return "Scan: ambiguous across " + result.entityUuids().size()
                        + " canonical assets (read-only)";
            case INVALID_CAPTURE:
                return "Scan: invalid or unsupported code [invalid_capture]";
            case TRANSPORT_FAILURE:
            case PROTOCOL_FAILURE:
            case LOCAL_FAILURE:
            case INTEGRITY_FAILURE:
            default:
                String code = result.errorCode() == null ? "capture_resolution_failed" : result.errorCode();
                return "Scan: resolution failed [" + code + "]";
        }
    }

    private void runExplicitMove() {
        final MovementCommandFacade activeMovement = movementFacade;
        final CanonicalResourceReader activeReader = reader;
        final OfflineSyncStateStore activeStateStore = stateStore;
        final ReconnectCoordinator activeCoordinator = coordinator;
        final String entityUuid = lastResolvedEntityUuid;
        final String destination = trimmed(movementDestination);
        final String subject = trimmed(subjectId);
        if (activeMovement == null || activeReader == null || activeStateStore == null
                || activeCoordinator == null || verifiedBinding == null || activeGrant == null) {
            proofStatus.setText("Move: unavailable [workspace_not_verified]");
            return;
        }
        if (entityUuid == null || entityUuid.isEmpty()) {
            proofStatus.setText("Move: scan and resolve one asset first [asset_not_resolved]");
            return;
        }
        if (destination.isEmpty() || subject.isEmpty()) {
            proofStatus.setText("Move: destination and subject are required [invalid_move_input]");
            return;
        }

        moveButton.setEnabled(false);
        ioExecutor.execute(() -> {
            try {
                if (activeStateStore.pendingCount() > 0) {
                    ReconnectCoordinator.ReconnectResult resumed = activeCoordinator.reconnect();
                    if (activeStateStore.pendingCount() > 0) {
                        runOnUiThread(() -> finishMove(
                                "Move: existing queued work still pending ["
                                        + resumed.status().name().toLowerCase(Locale.US) + "]"
                        ));
                        return;
                    }
                }

                CanonicalResourceReader.ReadResult destinationRead = freshRead(
                        activeReader,
                        "location",
                        destination
                );
                if (destinationRead.status() != CanonicalResourceReader.Status.FRESH_FOUND) {
                    runOnUiThread(() -> finishMove(
                            "Move: destination is not a verified canonical location ["
                                    + readFailureCode(destinationRead) + "]"
                    ));
                    return;
                }

                CanonicalResourceReader.ReadResult inventoryRead = freshRead(
                        activeReader,
                        "inventory_state",
                        entityUuid
                );
                if (inventoryRead.status() != CanonicalResourceReader.Status.FRESH_FOUND
                        || inventoryRead.snapshot() == null) {
                    runOnUiThread(() -> finishMove(
                            "Move: canonical inventory state unavailable ["
                                    + readFailureCode(inventoryRead) + "]"
                    ));
                    return;
                }

                OfflineSyncStateStore.ResourceSnapshot prior = inventoryRead.snapshot();
                JSONObject payload = new JSONObject(
                        new String(prior.payload(), StandardCharsets.UTF_8)
                );
                if (payload.optInt("schema_version", -1) != 1
                        || !entityUuid.equals(payload.optString("entity_uuid", ""))
                        || !"tracked".equals(payload.optString("participation_state", ""))) {
                    runOnUiThread(() -> finishMove(
                            "Move: canonical inventory payload failed validation [inventory_integrity]"
                    ));
                    return;
                }

                String observedAt = utcNow();
                String identityMaterial = entityUuid + "\n" + destination + "\n" + prior.revision();
                String digest = DeviceProofPresentation.sha256(
                        identityMaterial.getBytes(StandardCharsets.UTF_8)
                );
                if ("unavailable".equals(digest)) {
                    throw new IllegalStateException("SHA-256 unavailable");
                }
                String identity = digest.substring(0, 40);
                MovementCommandFacade.MoveRequest request = new MovementCommandFacade.MoveRequest(
                        subject,
                        entityUuid,
                        destination,
                        observedAt,
                        "android_explicit_move",
                        "device-proof-move-" + identity,
                        "device-proof-move-idem-" + identity,
                        prior.revision(),
                        nullableString(payload, "observed_location_id"),
                        nullableString(payload, "observed_at"),
                        nullableString(payload, "intended_location_id"),
                        nullableString(payload, "note"),
                        null
                );
                MovementCommandFacade.MoveResult result = activeMovement.move(request);
                runOnUiThread(() -> finishMove(moveSummary(result)));
            } catch (JSONException | RuntimeException exc) {
                runOnUiThread(() -> finishMove("Move: local failure [movement_exception]"));
            }
        });
    }

    private void finishMove(String summary) {
        proofStatus.setText(summary);
        if (movementFacade != null && lastResolvedEntityUuid != null
                && verifiedBinding != null && activeGrant != null) {
            moveButton.setEnabled(true);
        }
    }

    private static String moveSummary(MovementCommandFacade.MoveResult result) {
        switch (result.status()) {
            case APPLIED:
                return "Move: applied with verified canonical location readback";
            case WAITING_EVENT:
                return "Move: event queued; canonical movement not yet complete";
            case WAITING_PROJECTION:
                return "Move: event verified; location projection still queued";
            case BLOCKED_BY_EARLIER_COMMAND:
                return "Move: blocked by earlier queued work";
            case REMOTE_FAILURE:
            case TRANSPORT_FAILURE:
            case PROTOCOL_FAILURE:
            case LOCAL_FAILURE:
            default:
                String code = result.errorCode() == null ? "movement_failed" : result.errorCode();
                return "Move: failed [" + code + "]";
        }
    }

    private static CanonicalResourceReader.ReadResult freshRead(
            CanonicalResourceReader activeReader,
            String dataClassValue,
            String resourceIdValue
    ) {
        CanonicalResourceReader.ReadResult result = null;
        for (int pass = 0; pass < MAX_FRESH_READ_PASSES; pass++) {
            result = activeReader.refreshAndRead(dataClassValue, resourceIdValue);
            if (result.status() != CanonicalResourceReader.Status.MORE_REMOTE_CHANGES) {
                return result;
            }
        }
        return result;
    }

    private static String readFailureCode(CanonicalResourceReader.ReadResult result) {
        if (result == null) {
            return "read_unavailable";
        }
        return result.errorCode() == null
                ? result.status().name().toLowerCase(Locale.US)
                : result.errorCode();
    }

    private static String nullableString(JSONObject payload, String key) throws JSONException {
        return !payload.has(key) || payload.isNull(key) ? null : payload.getString(key);
    }

    private static String utcNow() {
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US);
        format.setTimeZone(TimeZone.getTimeZone("UTC"));
        return format.format(new Date());
    }

    private void runRead() {
        final CanonicalResourceReader activeReader = reader;
        if (activeReader == null || verifiedBinding == null || activeGrant == null) {
            proofStatus.setText("Read: unavailable [workspace_not_verified]");
            return;
        }
        String dataClassValue = trimmed(dataClass);
        String resourceIdValue = trimmed(resourceId);
        readButton.setEnabled(false);
        ioExecutor.execute(() -> {
            CanonicalResourceReader.ReadResult result;
            try {
                result = activeReader.refreshAndRead(dataClassValue, resourceIdValue);
            } catch (RuntimeException exc) {
                runOnUiThread(() -> {
                    proofStatus.setText("Read: local failure [invalid_proof_input]");
                    readButton.setEnabled(true);
                });
                return;
            }
            OfflineSyncStateStore.ResourceSnapshot snapshot = result.snapshot();
            long revision = snapshot == null ? 0L : snapshot.revision();
            byte[] payload = snapshot == null ? null : snapshot.payload();
            String shownResource = snapshot == null ? resourceIdValue : snapshot.resourceId();
            String summary = DeviceProofPresentation.readSummary(
                    result.status(),
                    shownResource,
                    revision,
                    payload,
                    result.errorCode()
            );
            runOnUiThread(() -> {
                proofStatus.setText(summary);
                readButton.setEnabled(true);
            });
        });
    }

    private void runMutation() {
        final CanonicalResourceMutator activeMutator = mutator;
        if (activeMutator == null || verifiedBinding == null || activeGrant == null) {
            proofStatus.setText("Mutation: unavailable [workspace_not_verified]");
            return;
        }
        final OfflineSyncStateStore.CommandIntent command;
        try {
            command = proofCommand();
        } catch (RuntimeException | JSONException exc) {
            proofStatus.setText("Mutation: local failure [invalid_proof_input]");
            return;
        }

        mutateButton.setEnabled(false);
        ioExecutor.execute(() -> {
            CanonicalResourceMutator.MutationResult result;
            try {
                result = activeMutator.mutate(command);
            } catch (RuntimeException exc) {
                runOnUiThread(() -> {
                    proofStatus.setText("Mutation: local failure [mutation_exception]");
                    mutateButton.setEnabled(true);
                });
                return;
            }
            OfflineSyncStateStore.ResourceSnapshot snapshot = result.canonicalSnapshot();
            long revision = snapshot == null ? 0L : snapshot.revision();
            byte[] payload = snapshot == null ? null : snapshot.payload();
            String shownResource = snapshot == null ? command.resourceId() : snapshot.resourceId();
            String summary = DeviceProofPresentation.mutationSummary(
                    result.status(),
                    shownResource,
                    revision,
                    payload,
                    result.errorCode()
            );
            runOnUiThread(() -> {
                proofStatus.setText(summary);
                mutateButton.setEnabled(true);
            });
        });
    }

    private OfflineSyncStateStore.CommandIntent proofCommand() throws JSONException {
        String subject = trimmed(subjectId);
        String dataClassValue = trimmed(dataClass);
        String resource = trimmed(resourceId);
        long revision = Long.parseLong(trimmed(expectedRevision));
        String normalizedPayload = new JSONObject(trimmed(payloadJson)).toString();
        String material = subject + "\n" + dataClassValue + "\n" + resource + "\n"
                + revision + "\n" + normalizedPayload;
        String digest = DeviceProofPresentation.sha256(material.getBytes(StandardCharsets.UTF_8));
        if ("unavailable".equals(digest)) {
            throw new IllegalStateException("SHA-256 unavailable");
        }
        String identity = digest.substring(0, 32);
        return new OfflineSyncStateStore.CommandIntent(
                "device-proof-cmd-" + identity,
                subject,
                dataClassValue,
                "upsert",
                1,
                API_SCHEMA_VERSION,
                resource,
                normalizedPayload.getBytes(StandardCharsets.UTF_8),
                "device-proof-idem-" + identity,
                revision,
                null,
                null
        );
    }

    private void renderDisconnected() {
        connectionStatus.setText(DeviceProofPresentation.connectionSummary(
                DeviceProofPresentation.ConnectionStatus.DISCONNECTED,
                null,
                null,
                null,
                null
        ));
        disableProofActions();
    }

    private void renderConnectionFailure(String code) {
        activeGrant = null;
        verifiedBinding = null;
        captureResolver = null;
        reader = null;
        mutator = null;
        movementFacade = null;
        stateStore = null;
        coordinator = null;
        lastResolvedEntityUuid = null;
        connectionStatus.setText(DeviceProofPresentation.connectionSummary(
                DeviceProofPresentation.ConnectionStatus.FAILED,
                null,
                null,
                null,
                code
        ));
        disableProofActions();
    }

    private void disableProofActions() {
        if (scanButton != null) {
            scanButton.setEnabled(false);
        }
        if (moveButton != null) {
            moveButton.setEnabled(false);
        }
        if (readButton != null) {
            readButton.setEnabled(false);
        }
        if (mutateButton != null) {
            mutateButton.setEnabled(false);
        }
    }

    private TextView text(String value, float sizeSp) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sizeSp);
        return view;
    }

    private EditText input(String label, String hint) {
        EditText view = new EditText(this);
        view.setHint(label + " — " + hint);
        view.setSingleLine(!"Payload JSON object".equals(label));
        return view;
    }

    private static String trimmed(EditText view) {
        return view.getText() == null ? "" : view.getText().toString().trim();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    @Override
    protected void onDestroy() {
        ioExecutor.shutdownNow();
        super.onDestroy();
    }
}
