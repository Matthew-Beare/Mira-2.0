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
import com.mira.client.core.sync.CanonicalResourceMutator;
import com.mira.client.core.sync.CanonicalResourceReader;
import com.mira.client.core.sync.GoogleWorkspaceTransport;
import com.mira.client.core.sync.OfflineSyncStateStore;
import com.mira.client.core.sync.ReconnectCoordinator;
import com.mira.client.googleworkspace.GooglePlayWorkspaceAuthorization;
import com.mira.client.googleworkspace.GoogleWorkspaceConnection;
import com.mira.client.googleworkspace.GoogleWorkspaceRestApi;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Minimal installable shell for M2-M1 representative-device evidence.
 *
 * <p>This is deliberately not the finished MIRA Android UI. It exposes one provider-native
 * connection action and bounded read/mutate proof controls over the existing client modules.
 * Provider tokens and spreadsheet IDs are never rendered or logged.</p>
 */
public final class DeviceProofActivity extends Activity {
    private static final int REQUEST_GOOGLE_AUTHORIZATION = 4101;
    private static final String LOCAL_CLIENT_ID = "mira-device-proof-v1";
    private static final String API_SCHEMA_VERSION = "mira-api-1";

    private final ExecutorService ioExecutor = Executors.newSingleThreadExecutor();

    private GooglePlayWorkspaceAuthorization authorization;
    private GoogleWorkspaceRestApi workspaceApi;
    private GoogleWorkspaceConnection workspaceConnection;
    private GoogleWorkspaceConnection.VerifiedBinding verifiedBinding;
    private GoogleWorkspaceConnection.PickerGrant activeGrant;
    private CanonicalResourceReader reader;
    private CanonicalResourceMutator mutator;

    private TextView connectionStatus;
    private TextView proofStatus;
    private EditText subjectId;
    private EditText dataClass;
    private EditText resourceId;
    private EditText expectedRevision;
    private EditText payloadJson;
    private Button connectButton;
    private Button readButton;
    private Button mutateButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        authorization = new GooglePlayWorkspaceAuthorization(this);
        workspaceApi = new GoogleWorkspaceRestApi();
        workspaceConnection = new GoogleWorkspaceConnection(workspaceApi);
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

        TextView proofHeader = text("Canonical proof controls", 18f);
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
                GoogleWorkspaceTransport transport = new GoogleWorkspaceTransport(
                        workspaceApi.gateway(binding, grant)
                );
                OfflineSyncStateStore stateStore = new OfflineSyncStateStore(
                        getApplicationContext(),
                        LOCAL_CLIENT_ID
                );
                ReconnectCoordinator coordinator = new ReconnectCoordinator(stateStore, transport);
                CanonicalResourceReader newReader = new CanonicalResourceReader(stateStore, transport);
                CanonicalResourceMutator newMutator = new CanonicalResourceMutator(
                        stateStore,
                        coordinator
                );
                runOnUiThread(() -> {
                    activeGrant = grant;
                    verifiedBinding = binding;
                    reader = newReader;
                    mutator = newMutator;
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
        reader = null;
        mutator = null;
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
