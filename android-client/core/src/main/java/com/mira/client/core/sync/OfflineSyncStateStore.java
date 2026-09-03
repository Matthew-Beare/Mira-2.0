package com.mira.client.core.sync;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/**
 * Durable local state required for later replay-safe Android synchronization.
 *
 * <p>This class is deliberately transport and provider neutral. It stores exact serialized
 * {@code API-001} command intents, local acknowledgement tombstones, nonauthoritative canonical
 * snapshots, and one opaque synchronization cursor. It does not submit commands, interpret
 * provider state, resolve server conflicts, or become canonical authority.</p>
 *
 * <p>Production state is encrypted and authenticated with a separate Android Keystore AES-GCM
 * key and is stored under {@link Context#getNoBackupFilesDir()}. Keeping this state out of Android
 * backup avoids cloning a pending-command queue onto another device and creating an accidental
 * cross-device replay path.</p>
 */
public final class OfflineSyncStateStore {
    private static final Pattern ID_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$");
    private static final Pattern DATA_CLASS_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$");

    private static final int STATE_FORMAT_VERSION = 1;
    private static final int SEALED_FORMAT_VERSION = 1;
    private static final int GCM_IV_BYTES = 12;
    private static final int SHA256_BYTES = 32;

    private static final int MAX_PENDING_COMMANDS = 128;
    private static final int MAX_ACKNOWLEDGED_COMMANDS = 512;
    private static final int MAX_SNAPSHOTS = 128;
    private static final int MAX_COMMAND_PAYLOAD_BYTES = 32 * 1024;
    private static final int MAX_SNAPSHOT_PAYLOAD_BYTES = 128 * 1024;
    private static final int MAX_STATE_PLAINTEXT_BYTES = 8 * 1024 * 1024;
    private static final int MAX_STATE_CIPHERTEXT_BYTES = MAX_STATE_PLAINTEXT_BYTES + 64;
    private static final int MAX_SEALED_BLOB_BYTES = MAX_STATE_CIPHERTEXT_BYTES + 128;

    private static final int MAX_ID_UTF8_BYTES = 128;
    private static final int MAX_DATA_CLASS_UTF8_BYTES = 96;
    private static final int MAX_TOKEN_UTF8_BYTES = 512;
    private static final int MAX_CURSOR_CHARS = 1024;
    private static final int MAX_CURSOR_UTF8_BYTES = 4096;

    private static final String ACTION_UPSERT = "upsert";
    private static final String ACTION_APPEND_EVENT = "append_event";

    private static final ConcurrentHashMap<String, Object> CLIENT_LOCKS =
            new ConcurrentHashMap<>();

    private final String clientId;
    private final StateCipher cipherEngine;
    private final BlobStore blobStore;
    private final Object clientLock;

    /** Creates the production Android local offline-state store for one enrolled MIRA client. */
    public OfflineSyncStateStore(Context context, String clientId) {
        this(
                validateId(clientId, "client_id"),
                new AndroidKeystoreStateCipher(),
                new NoBackupStateBlobStore(Objects.requireNonNull(context, "context"))
        );
    }

    /** Package-private dependency injection seam for deterministic JVM tests. */
    OfflineSyncStateStore(String clientId, StateCipher cipherEngine, BlobStore blobStore) {
        this.clientId = validateId(clientId, "client_id");
        this.cipherEngine = Objects.requireNonNull(cipherEngine, "cipherEngine");
        this.blobStore = Objects.requireNonNull(blobStore, "blobStore");
        this.clientLock = CLIENT_LOCKS.computeIfAbsent(this.clientId, ignored -> new Object());
    }

    /**
     * Durably enqueues one exact provider-neutral API command intent.
     *
     * <p>Exact duplicate command material is idempotent. Reusing a command ID for different
     * material fails closed. A command that already has a durable acknowledgement tombstone is not
     * re-enqueued after restart.</p>
     */
    public EnqueueResult enqueue(CommandIntent command) {
        CommandIntent validated = new CommandIntent(Objects.requireNonNull(command, "command"));
        byte[] fingerprint = commandFingerprint(validated);
        synchronized (clientLock) {
            LocalState state = loadState();

            QueuedCommand pending = findPending(state, validated.commandId());
            if (pending != null) {
                if (Arrays.equals(commandFingerprint(pending.command()), fingerprint)) {
                    return EnqueueResult.ALREADY_PENDING;
                }
                throw new StateConflictException(
                        "command_id is already pending with different material"
                );
            }

            AcknowledgedCommand acknowledged =
                    findAcknowledged(state, validated.commandId());
            if (acknowledged != null) {
                if (Arrays.equals(acknowledged.fingerprint, fingerprint)) {
                    return EnqueueResult.ALREADY_ACKNOWLEDGED;
                }
                throw new StateConflictException(
                        "command_id was already acknowledged with different material"
                );
            }

            if (state.pending.size() >= MAX_PENDING_COMMANDS) {
                throw new StateCapacityException("pending command capacity is exhausted");
            }
            if (state.nextSequence <= 0 || state.nextSequence == Long.MAX_VALUE) {
                throw new OfflineStateException("local command sequence is exhausted");
            }

            state.pending.add(new QueuedCommand(state.nextSequence, validated));
            state.nextSequence += 1;
            persistState(state);
            return EnqueueResult.ENQUEUED;
        }
    }

    /** Returns a stable FIFO copy of up to {@code limit} pending commands. */
    public List<QueuedCommand> pendingCommands(int limit) {
        if (limit < 1 || limit > MAX_PENDING_COMMANDS) {
            throw new OfflineStateException(
                    "pending command limit must be from 1 through " + MAX_PENDING_COMMANDS
            );
        }
        synchronized (clientLock) {
            LocalState state = loadState();
            int count = Math.min(limit, state.pending.size());
            ArrayList<QueuedCommand> result = new ArrayList<>(count);
            for (int index = 0; index < count; index++) {
                result.add(new QueuedCommand(state.pending.get(index)));
            }
            return Collections.unmodifiableList(result);
        }
    }

    /** Returns the number of pending commands currently stored. */
    public int pendingCount() {
        synchronized (clientLock) {
            return loadState().pending.size();
        }
    }

    /** Returns the number of durable acknowledgement tombstones currently stored. */
    public int acknowledgedCount() {
        synchronized (clientLock) {
            return loadState().acknowledged.size();
        }
    }

    /**
     * Moves an exact pending command to the durable acknowledged replay-suppression ledger.
     *
     * <p>The future transport may call this only after server/canonical readback has been verified.
     * This local store does not itself claim that such verification occurred. Repeating the exact
     * acknowledgement is idempotent; acknowledging an unknown command or mismatched idempotency
     * identity fails closed.</p>
     */
    public void acknowledge(String commandId, String idempotencyKey) {
        String validatedCommandId = validateId(commandId, "command_id");
        String validatedKey = validateToken(idempotencyKey, "idempotency_key");
        synchronized (clientLock) {
            LocalState state = loadState();
            int pendingIndex = indexOfPending(state, validatedCommandId);
            if (pendingIndex >= 0) {
                QueuedCommand queued = state.pending.get(pendingIndex);
                if (!queued.command().idempotencyKey().equals(validatedKey)) {
                    throw new StateConflictException(
                            "acknowledgement idempotency_key does not match pending command"
                    );
                }
                if (state.acknowledged.size() >= MAX_ACKNOWLEDGED_COMMANDS) {
                    throw new StateCapacityException(
                            "acknowledgement tombstone capacity is exhausted"
                    );
                }
                state.acknowledged.add(
                        new AcknowledgedCommand(
                                queued.sequence(),
                                queued.command().commandId(),
                                queued.command().idempotencyKey(),
                                commandFingerprint(queued.command())
                        )
                );
                state.pending.remove(pendingIndex);
                persistState(state);
                return;
            }

            AcknowledgedCommand acknowledged = findAcknowledged(state, validatedCommandId);
            if (acknowledged == null) {
                throw new StateConflictException("cannot acknowledge an unknown command_id");
            }
            if (!acknowledged.idempotencyKey.equals(validatedKey)) {
                throw new StateConflictException(
                        "acknowledgement idempotency_key conflicts with stored tombstone"
                );
            }
        }
    }

    /**
     * Stores one nonauthoritative canonical snapshot while enforcing monotonic revision rules.
     */
    public SnapshotResult putSnapshot(ResourceSnapshot snapshot) {
        ResourceSnapshot validated =
                new ResourceSnapshot(Objects.requireNonNull(snapshot, "snapshot"));
        synchronized (clientLock) {
            LocalState state = loadState();
            int existingIndex = indexOfSnapshot(state, validated.resourceId());
            if (existingIndex >= 0) {
                ResourceSnapshot existing = state.snapshots.get(existingIndex);
                if (validated.revision() < existing.revision()) {
                    throw new StateConflictException(
                            "canonical snapshot revision cannot regress"
                    );
                }
                if (validated.revision() == existing.revision()) {
                    if (Arrays.equals(validated.payload(), existing.payload())) {
                        return SnapshotResult.UNCHANGED;
                    }
                    throw new StateConflictException(
                            "same canonical revision has different snapshot material"
                    );
                }
                state.snapshots.set(existingIndex, validated);
                sortSnapshots(state.snapshots);
                persistState(state);
                return SnapshotResult.STORED;
            }

            if (state.snapshots.size() >= MAX_SNAPSHOTS) {
                throw new StateCapacityException("canonical snapshot capacity is exhausted");
            }
            state.snapshots.add(validated);
            sortSnapshots(state.snapshots);
            persistState(state);
            return SnapshotResult.STORED;
        }
    }

    /** Returns a defensive copy of one cached canonical snapshot, or {@code null} if absent. */
    public ResourceSnapshot snapshot(String resourceId) {
        String validatedId = validateId(resourceId, "resource_id");
        synchronized (clientLock) {
            LocalState state = loadState();
            int index = indexOfSnapshot(state, validatedId);
            return index < 0 ? null : new ResourceSnapshot(state.snapshots.get(index));
        }
    }

    /** Returns the current opaque synchronization cursor, or {@code null} when none exists. */
    public String cursor() {
        synchronized (clientLock) {
            return loadState().cursor;
        }
    }

    /**
     * Advances the opaque synchronization cursor using compare-and-set semantics.
     *
     * <p>No lexical, numeric, timestamp, or provider-specific ordering is inferred from cursor
     * contents. A stale caller must present the exact currently stored cursor before replacing it.
     * Repeating an already-applied exact next cursor is idempotent.</p>
     */
    public void compareAndSetCursor(String expectedCurrent, String nextCursor) {
        String validatedExpected = validateNullableCursor(expectedCurrent, "expected_cursor");
        String validatedNext = validateCursor(nextCursor, "next_cursor");
        synchronized (clientLock) {
            LocalState state = loadState();
            if (Objects.equals(state.cursor, validatedNext)) {
                return;
            }
            if (!Objects.equals(state.cursor, validatedExpected)) {
                throw new StateConflictException("synchronization cursor compare-and-set failed");
            }
            state.cursor = validatedNext;
            persistState(state);
        }
    }

    /** Returns whether an encrypted local-state blob currently exists for this client. */
    public boolean hasLocalState() {
        synchronized (clientLock) {
            return blobStore.exists(clientId);
        }
    }

    /**
     * Explicitly discards all local offline state and the matching Keystore key.
     *
     * <p>This can destroy unsynced local commands and must never be invoked as silent recovery.
     * It does not revoke the client session, mutate canonical state, or clean up any provider.</p>
     */
    public void discardLocalState() {
        synchronized (clientLock) {
            blobStore.delete(clientId);
            cipherEngine.deleteKey(clientId);
        }
    }

    private LocalState loadState() {
        if (!blobStore.exists(clientId)) {
            return LocalState.empty();
        }
        SealedState sealed = decodeSealed(blobStore.read(clientId));
        byte[] plaintext = cipherEngine.open(clientId, sealed);
        try {
            if (plaintext.length == 0 || plaintext.length > MAX_STATE_PLAINTEXT_BYTES) {
                throw new StateUnavailableException("decrypted offline state size is invalid");
            }
            return decodeState(plaintext);
        } finally {
            Arrays.fill(plaintext, (byte) 0);
        }
    }

    private void persistState(LocalState state) {
        validateState(state);
        byte[] plaintext = encodeState(state);
        try {
            SealedState sealed = cipherEngine.seal(clientId, plaintext);
            blobStore.write(clientId, encodeSealed(sealed));
        } finally {
            Arrays.fill(plaintext, (byte) 0);
        }
    }

    private static byte[] encodeState(LocalState state) {
        try {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            try (DataOutputStream output = new DataOutputStream(bytes)) {
                output.writeInt(STATE_FORMAT_VERSION);
                output.writeLong(state.nextSequence);
                writeNullableCursor(output, state.cursor);

                output.writeInt(state.pending.size());
                for (QueuedCommand queued : state.pending) {
                    output.writeLong(queued.sequence());
                    writeCommand(output, queued.command());
                }

                output.writeInt(state.acknowledged.size());
                for (AcknowledgedCommand acknowledged : state.acknowledged) {
                    output.writeLong(acknowledged.sequence);
                    writeString(output, acknowledged.commandId);
                    writeString(output, acknowledged.idempotencyKey);
                    output.writeInt(acknowledged.fingerprint.length);
                    output.write(acknowledged.fingerprint);
                }

                output.writeInt(state.snapshots.size());
                for (ResourceSnapshot snapshot : state.snapshots) {
                    writeString(output, snapshot.resourceId());
                    output.writeLong(snapshot.revision());
                    writeBytes(output, snapshot.payload());
                }
            }
            byte[] encoded = bytes.toByteArray();
            if (encoded.length == 0 || encoded.length > MAX_STATE_PLAINTEXT_BYTES) {
                Arrays.fill(encoded, (byte) 0);
                throw new StateCapacityException("offline state exceeds encoded size limit");
            }
            return encoded;
        } catch (IOException exc) {
            throw new OfflineStateException("cannot encode offline state", exc);
        }
    }

    private static LocalState decodeState(byte[] plaintext) {
        try (DataInputStream input =
                     new DataInputStream(new ByteArrayInputStream(plaintext))) {
            int version = input.readInt();
            if (version != STATE_FORMAT_VERSION) {
                throw new StateUnavailableException("unsupported offline state format version");
            }
            long nextSequence = input.readLong();
            String cursor = readNullableCursor(input);

            int pendingCount = readCount(input, MAX_PENDING_COMMANDS, "pending command");
            ArrayList<QueuedCommand> pending = new ArrayList<>(pendingCount);
            for (int index = 0; index < pendingCount; index++) {
                long sequence = input.readLong();
                pending.add(new QueuedCommand(sequence, readCommand(input)));
            }

            int acknowledgedCount =
                    readCount(input, MAX_ACKNOWLEDGED_COMMANDS, "acknowledged command");
            ArrayList<AcknowledgedCommand> acknowledged =
                    new ArrayList<>(acknowledgedCount);
            for (int index = 0; index < acknowledgedCount; index++) {
                long sequence = input.readLong();
                String commandId = readString(input, MAX_ID_UTF8_BYTES, "command_id");
                String idempotencyKey =
                        readString(input, MAX_TOKEN_UTF8_BYTES, "idempotency_key");
                int fingerprintLength = input.readInt();
                if (fingerprintLength != SHA256_BYTES) {
                    throw new StateUnavailableException(
                            "acknowledgement fingerprint length is invalid"
                    );
                }
                byte[] fingerprint = new byte[fingerprintLength];
                input.readFully(fingerprint);
                acknowledged.add(
                        new AcknowledgedCommand(
                                sequence,
                                commandId,
                                idempotencyKey,
                                fingerprint
                        )
                );
            }

            int snapshotCount = readCount(input, MAX_SNAPSHOTS, "snapshot");
            ArrayList<ResourceSnapshot> snapshots = new ArrayList<>(snapshotCount);
            for (int index = 0; index < snapshotCount; index++) {
                String resourceId = readString(input, MAX_ID_UTF8_BYTES, "resource_id");
                long revision = input.readLong();
                byte[] payload =
                        readBytes(input, MAX_SNAPSHOT_PAYLOAD_BYTES, "snapshot payload");
                snapshots.add(new ResourceSnapshot(resourceId, revision, payload));
            }

            if (input.read() != -1) {
                throw new StateUnavailableException("offline state contains trailing bytes");
            }

            LocalState state = new LocalState(
                    nextSequence,
                    cursor,
                    pending,
                    acknowledged,
                    snapshots
            );
            validateState(state);
            return state;
        } catch (EOFException exc) {
            throw new StateUnavailableException("offline state is truncated", exc);
        } catch (IOException exc) {
            throw new StateUnavailableException("cannot decode offline state", exc);
        }
    }

    private static byte[] encodeSealed(SealedState sealed) {
        byte[] iv = sealed.iv();
        byte[] ciphertext = sealed.ciphertext();
        if (iv.length != GCM_IV_BYTES) {
            throw new OfflineStateException("offline state IV length is invalid");
        }
        if (ciphertext.length == 0 || ciphertext.length > MAX_STATE_CIPHERTEXT_BYTES) {
            throw new OfflineStateException("offline state ciphertext length is invalid");
        }
        try {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            try (DataOutputStream output = new DataOutputStream(bytes)) {
                output.writeInt(SEALED_FORMAT_VERSION);
                output.writeInt(iv.length);
                output.write(iv);
                output.writeInt(ciphertext.length);
                output.write(ciphertext);
            }
            byte[] encoded = bytes.toByteArray();
            if (encoded.length > MAX_SEALED_BLOB_BYTES) {
                throw new StateCapacityException("sealed offline state exceeds size limit");
            }
            return encoded;
        } catch (IOException exc) {
            throw new OfflineStateException("cannot encode sealed offline state", exc);
        }
    }

    private static SealedState decodeSealed(byte[] blob) {
        if (blob == null || blob.length == 0 || blob.length > MAX_SEALED_BLOB_BYTES) {
            throw new StateUnavailableException("sealed offline state blob is invalid");
        }
        try (DataInputStream input = new DataInputStream(new ByteArrayInputStream(blob))) {
            int version = input.readInt();
            if (version != SEALED_FORMAT_VERSION) {
                throw new StateUnavailableException(
                        "unsupported sealed offline state format version"
                );
            }
            int ivLength = input.readInt();
            if (ivLength != GCM_IV_BYTES) {
                throw new StateUnavailableException("sealed offline state IV is invalid");
            }
            byte[] iv = new byte[ivLength];
            input.readFully(iv);

            int ciphertextLength = input.readInt();
            if (ciphertextLength <= 0 || ciphertextLength > MAX_STATE_CIPHERTEXT_BYTES) {
                throw new StateUnavailableException(
                        "sealed offline state ciphertext length is invalid"
                );
            }
            byte[] ciphertext = new byte[ciphertextLength];
            input.readFully(ciphertext);
            if (input.read() != -1) {
                throw new StateUnavailableException(
                        "sealed offline state contains trailing bytes"
                );
            }
            return new SealedState(iv, ciphertext);
        } catch (EOFException exc) {
            throw new StateUnavailableException("sealed offline state is truncated", exc);
        } catch (IOException exc) {
            throw new StateUnavailableException("cannot decode sealed offline state", exc);
        }
    }

    private static void writeCommand(DataOutputStream output, CommandIntent command)
            throws IOException {
        writeString(output, command.commandId());
        writeString(output, command.subjectId());
        writeString(output, command.dataClass());
        writeString(output, command.action());
        output.writeInt(command.apiMajor());
        writeString(output, command.schemaVersion());
        writeString(output, command.resourceId());
        writeBytes(output, command.payload());
        writeString(output, command.idempotencyKey());
        writeNullableLong(output, command.expectedRevision());
        writeNullableString(output, command.eventId());
        writeNullableString(output, command.eventType());
    }

    private static CommandIntent readCommand(DataInputStream input) throws IOException {
        String commandId = readString(input, MAX_ID_UTF8_BYTES, "command_id");
        String subjectId = readString(input, MAX_ID_UTF8_BYTES, "subject_id");
        String dataClass = readString(input, MAX_DATA_CLASS_UTF8_BYTES, "data_class");
        String action = readString(input, MAX_TOKEN_UTF8_BYTES, "action");
        int apiMajor = input.readInt();
        String schemaVersion =
                readString(input, MAX_TOKEN_UTF8_BYTES, "schema_version");
        String resourceId = readString(input, MAX_ID_UTF8_BYTES, "resource_id");
        byte[] payload = readBytes(input, MAX_COMMAND_PAYLOAD_BYTES, "command payload");
        String idempotencyKey =
                readString(input, MAX_TOKEN_UTF8_BYTES, "idempotency_key");
        Long expectedRevision = readNullableLong(input);
        String eventId = readNullableString(input, MAX_ID_UTF8_BYTES, "event_id");
        String eventType =
                readNullableString(input, MAX_TOKEN_UTF8_BYTES, "event_type");
        return new CommandIntent(
                commandId,
                subjectId,
                dataClass,
                action,
                apiMajor,
                schemaVersion,
                resourceId,
                payload,
                idempotencyKey,
                expectedRevision,
                eventId,
                eventType
        );
    }

    private static byte[] commandFingerprint(CommandIntent command) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            try (DataOutputStream output = new DataOutputStream(bytes)) {
                writeCommand(output, command);
            }
            return digest.digest(bytes.toByteArray());
        } catch (NoSuchAlgorithmException exc) {
            throw new OfflineStateException("SHA-256 is unavailable", exc);
        } catch (IOException exc) {
            throw new OfflineStateException("cannot fingerprint command intent", exc);
        }
    }

    private static void validateState(LocalState state) {
        if (state.nextSequence <= 0) {
            throw new StateUnavailableException("local next sequence is invalid");
        }
        validateNullableCursor(state.cursor, "cursor");
        if (state.pending.size() > MAX_PENDING_COMMANDS) {
            throw new StateUnavailableException("pending command count exceeds limit");
        }
        if (state.acknowledged.size() > MAX_ACKNOWLEDGED_COMMANDS) {
            throw new StateUnavailableException(
                    "acknowledgement tombstone count exceeds limit"
            );
        }
        if (state.snapshots.size() > MAX_SNAPSHOTS) {
            throw new StateUnavailableException("snapshot count exceeds limit");
        }

        Set<String> commandIds = new HashSet<>();
        long priorPendingSequence = 0;
        long maxSequence = 0;
        for (QueuedCommand queued : state.pending) {
            if (queued.sequence() <= priorPendingSequence) {
                throw new StateUnavailableException(
                        "pending command sequences are not strictly increasing"
                );
            }
            priorPendingSequence = queued.sequence();
            maxSequence = Math.max(maxSequence, queued.sequence());
            if (!commandIds.add(queued.command().commandId())) {
                throw new StateUnavailableException("duplicate command_id in local state");
            }
        }

        for (AcknowledgedCommand acknowledged : state.acknowledged) {
            if (acknowledged.sequence <= 0 || acknowledged.sequence >= state.nextSequence) {
                throw new StateUnavailableException(
                        "acknowledgement sequence is outside local sequence range"
                );
            }
            maxSequence = Math.max(maxSequence, acknowledged.sequence);
            validateId(acknowledged.commandId, "command_id");
            validateToken(acknowledged.idempotencyKey, "idempotency_key");
            if (acknowledged.fingerprint.length != SHA256_BYTES) {
                throw new StateUnavailableException(
                        "acknowledgement fingerprint length is invalid"
                );
            }
            if (!commandIds.add(acknowledged.commandId)) {
                throw new StateUnavailableException("duplicate command_id in local state");
            }
        }

        if (maxSequence >= state.nextSequence) {
            throw new StateUnavailableException("local next sequence does not advance state");
        }

        String priorResourceId = null;
        for (ResourceSnapshot snapshot : state.snapshots) {
            if (priorResourceId != null
                    && priorResourceId.compareTo(snapshot.resourceId()) >= 0) {
                throw new StateUnavailableException(
                        "canonical snapshots are not uniquely sorted by resource_id"
                );
            }
            priorResourceId = snapshot.resourceId();
        }

        long approximateBytes = 128;
        for (QueuedCommand queued : state.pending) {
            approximateBytes = safeAdd(approximateBytes, estimateCommandBytes(queued.command()));
        }
        approximateBytes = safeAdd(
                approximateBytes,
                (long) state.acknowledged.size() * 1024L
        );
        for (ResourceSnapshot snapshot : state.snapshots) {
            approximateBytes = safeAdd(
                    approximateBytes,
                    256L + snapshot.payload().length
            );
        }
        if (approximateBytes > MAX_STATE_PLAINTEXT_BYTES) {
            throw new StateCapacityException("offline state exceeds total size limit");
        }
    }

    private static long estimateCommandBytes(CommandIntent command) {
        long total = 512L + command.payload().length;
        total = safeAdd(total, utf8Length(command.commandId()));
        total = safeAdd(total, utf8Length(command.subjectId()));
        total = safeAdd(total, utf8Length(command.dataClass()));
        total = safeAdd(total, utf8Length(command.action()));
        total = safeAdd(total, utf8Length(command.schemaVersion()));
        total = safeAdd(total, utf8Length(command.resourceId()));
        total = safeAdd(total, utf8Length(command.idempotencyKey()));
        if (command.eventId() != null) {
            total = safeAdd(total, utf8Length(command.eventId()));
        }
        if (command.eventType() != null) {
            total = safeAdd(total, utf8Length(command.eventType()));
        }
        return total;
    }

    private static long safeAdd(long left, long right) {
        if (right < 0 || left > Long.MAX_VALUE - right) {
            throw new StateCapacityException("offline state size calculation overflowed");
        }
        return left + right;
    }

    private static int utf8Length(String value) {
        return value.getBytes(StandardCharsets.UTF_8).length;
    }

    private static QueuedCommand findPending(LocalState state, String commandId) {
        int index = indexOfPending(state, commandId);
        return index < 0 ? null : state.pending.get(index);
    }

    private static int indexOfPending(LocalState state, String commandId) {
        for (int index = 0; index < state.pending.size(); index++) {
            if (state.pending.get(index).command().commandId().equals(commandId)) {
                return index;
            }
        }
        return -1;
    }

    private static AcknowledgedCommand findAcknowledged(LocalState state, String commandId) {
        for (AcknowledgedCommand acknowledged : state.acknowledged) {
            if (acknowledged.commandId.equals(commandId)) {
                return acknowledged;
            }
        }
        return null;
    }

    private static int indexOfSnapshot(LocalState state, String resourceId) {
        for (int index = 0; index < state.snapshots.size(); index++) {
            if (state.snapshots.get(index).resourceId().equals(resourceId)) {
                return index;
            }
        }
        return -1;
    }

    private static void sortSnapshots(ArrayList<ResourceSnapshot> snapshots) {
        snapshots.sort(Comparator.comparing(ResourceSnapshot::resourceId));
    }

    private static int readCount(DataInputStream input, int maximum, String field)
            throws IOException {
        int count = input.readInt();
        if (count < 0 || count > maximum) {
            throw new StateUnavailableException(field + " count is invalid");
        }
        return count;
    }

    private static void writeString(DataOutputStream output, String value) throws IOException {
        byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
        output.writeInt(encoded.length);
        output.write(encoded);
    }

    private static String readString(DataInputStream input, int maximumBytes, String field)
            throws IOException {
        int length = input.readInt();
        if (length <= 0 || length > maximumBytes) {
            throw new StateUnavailableException(field + " encoded length is invalid");
        }
        byte[] encoded = new byte[length];
        input.readFully(encoded);
        try {
            return StandardCharsets.UTF_8
                    .newDecoder()
                    .onMalformedInput(CodingErrorAction.REPORT)
                    .onUnmappableCharacter(CodingErrorAction.REPORT)
                    .decode(ByteBuffer.wrap(encoded))
                    .toString();
        } catch (CharacterCodingException exc) {
            throw new StateUnavailableException(field + " is not valid UTF-8", exc);
        }
    }

    private static void writeNullableString(DataOutputStream output, String value)
            throws IOException {
        output.writeBoolean(value != null);
        if (value != null) {
            writeString(output, value);
        }
    }

    private static String readNullableString(
            DataInputStream input,
            int maximumBytes,
            String field
    ) throws IOException {
        return input.readBoolean() ? readString(input, maximumBytes, field) : null;
    }

    private static void writeBytes(DataOutputStream output, byte[] value) throws IOException {
        output.writeInt(value.length);
        output.write(value);
    }

    private static byte[] readBytes(DataInputStream input, int maximumBytes, String field)
            throws IOException {
        int length = input.readInt();
        if (length <= 0 || length > maximumBytes) {
            throw new StateUnavailableException(field + " length is invalid");
        }
        byte[] value = new byte[length];
        input.readFully(value);
        return value;
    }

    private static void writeNullableLong(DataOutputStream output, Long value)
            throws IOException {
        output.writeBoolean(value != null);
        if (value != null) {
            output.writeLong(value);
        }
    }

    private static Long readNullableLong(DataInputStream input) throws IOException {
        return input.readBoolean() ? input.readLong() : null;
    }

    private static void writeNullableCursor(DataOutputStream output, String value)
            throws IOException {
        output.writeBoolean(value != null);
        if (value != null) {
            writeString(output, value);
        }
    }

    private static String readNullableCursor(DataInputStream input) throws IOException {
        if (!input.readBoolean()) {
            return null;
        }
        return validateCursor(
                readString(input, MAX_CURSOR_UTF8_BYTES, "cursor"),
                "cursor"
        );
    }

    private static String validateId(String value, String field) {
        if (value == null || !ID_PATTERN.matcher(value).matches()) {
            throw new OfflineStateException(field + " is invalid");
        }
        return value;
    }

    private static String validateDataClass(String value) {
        if (value == null || !DATA_CLASS_PATTERN.matcher(value).matches()) {
            throw new OfflineStateException("data_class is invalid");
        }
        return value;
    }

    private static String validateToken(String value, String field) {
        if (value == null || value.isEmpty() || value.length() > 128 || !isTrimmed(value)) {
            throw new OfflineStateException(
                    field + " must be a non-empty trimmed string of at most 128 characters"
            );
        }
        if (utf8Length(value) > MAX_TOKEN_UTF8_BYTES) {
            throw new OfflineStateException(field + " encoded length is too large");
        }
        return value;
    }

    private static String validateCursor(String value, String field) {
        if (value == null
                || value.isEmpty()
                || value.length() > MAX_CURSOR_CHARS
                || !isTrimmed(value)
                || utf8Length(value) > MAX_CURSOR_UTF8_BYTES) {
            throw new OfflineStateException(field + " is invalid");
        }
        return value;
    }

    private static String validateNullableCursor(String value, String field) {
        return value == null ? null : validateCursor(value, field);
    }

    private static boolean isTrimmed(String value) {
        if (value.isEmpty()) {
            return false;
        }
        int first = value.codePointAt(0);
        int last = value.codePointBefore(value.length());
        return !Character.isWhitespace(first) && !Character.isWhitespace(last);
    }

    private static String stableHash(String value) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder result = new StringBuilder(digest.length * 2);
            for (byte item : digest) {
                result.append(String.format("%02x", item & 0xff));
            }
            return result.toString();
        } catch (NoSuchAlgorithmException exc) {
            throw new OfflineStateException("SHA-256 is unavailable", exc);
        }
    }

    /** Result from one enqueue attempt. */
    public enum EnqueueResult {
        ENQUEUED,
        ALREADY_PENDING,
        ALREADY_ACKNOWLEDGED
    }

    /** Result from one cached-snapshot write attempt. */
    public enum SnapshotResult {
        STORED,
        UNCHANGED
    }

    /** Exact transport-independent command intent preserved for later replay. */
    public static final class CommandIntent {
        private final String commandId;
        private final String subjectId;
        private final String dataClass;
        private final String action;
        private final int apiMajor;
        private final String schemaVersion;
        private final String resourceId;
        private final byte[] payload;
        private final String idempotencyKey;
        private final Long expectedRevision;
        private final String eventId;
        private final String eventType;

        public CommandIntent(
                String commandId,
                String subjectId,
                String dataClass,
                String action,
                int apiMajor,
                String schemaVersion,
                String resourceId,
                byte[] payload,
                String idempotencyKey,
                Long expectedRevision,
                String eventId,
                String eventType
        ) {
            this.commandId = validateId(commandId, "command_id");
            this.subjectId = validateId(subjectId, "subject_id");
            this.dataClass = validateDataClass(dataClass);
            if (!ACTION_UPSERT.equals(action) && !ACTION_APPEND_EVENT.equals(action)) {
                throw new OfflineStateException("unsupported command action: " + action);
            }
            this.action = action;
            if (apiMajor < 1) {
                throw new OfflineStateException("api_major must be a positive integer");
            }
            this.apiMajor = apiMajor;
            this.schemaVersion = validateToken(schemaVersion, "schema_version");
            this.resourceId = validateId(resourceId, "resource_id");
            if (payload == null
                    || payload.length == 0
                    || payload.length > MAX_COMMAND_PAYLOAD_BYTES) {
                throw new OfflineStateException(
                        "command payload length must be from 1 through "
                                + MAX_COMMAND_PAYLOAD_BYTES
                );
            }
            this.payload = payload.clone();
            this.idempotencyKey = validateToken(idempotencyKey, "idempotency_key");
            if (expectedRevision != null && expectedRevision < 0) {
                throw new OfflineStateException(
                        "expected_revision must be non-negative or null"
                );
            }
            this.expectedRevision = expectedRevision;

            if (ACTION_APPEND_EVENT.equals(action)) {
                this.eventId = validateId(eventId, "event_id");
                this.eventType = validateToken(eventType, "event_type");
            } else {
                if (eventId != null || eventType != null) {
                    throw new OfflineStateException(
                            "upsert command must not contain event fields"
                    );
                }
                this.eventId = null;
                this.eventType = null;
            }
        }

        CommandIntent(CommandIntent other) {
            this(
                    other.commandId,
                    other.subjectId,
                    other.dataClass,
                    other.action,
                    other.apiMajor,
                    other.schemaVersion,
                    other.resourceId,
                    other.payload,
                    other.idempotencyKey,
                    other.expectedRevision,
                    other.eventId,
                    other.eventType
            );
        }

        public String commandId() {
            return commandId;
        }

        public String subjectId() {
            return subjectId;
        }

        public String dataClass() {
            return dataClass;
        }

        public String action() {
            return action;
        }

        public int apiMajor() {
            return apiMajor;
        }

        public String schemaVersion() {
            return schemaVersion;
        }

        public String resourceId() {
            return resourceId;
        }

        public byte[] payload() {
            return payload.clone();
        }

        public String idempotencyKey() {
            return idempotencyKey;
        }

        public Long expectedRevision() {
            return expectedRevision;
        }

        public String eventId() {
            return eventId;
        }

        public String eventType() {
            return eventType;
        }
    }

    /** One queued command paired with its stable local FIFO sequence. */
    public static final class QueuedCommand {
        private final long sequence;
        private final CommandIntent command;

        QueuedCommand(long sequence, CommandIntent command) {
            if (sequence <= 0) {
                throw new OfflineStateException("queued command sequence must be positive");
            }
            this.sequence = sequence;
            this.command = new CommandIntent(Objects.requireNonNull(command, "command"));
        }

        QueuedCommand(QueuedCommand other) {
            this(other.sequence, other.command);
        }

        public long sequence() {
            return sequence;
        }

        public CommandIntent command() {
            return new CommandIntent(command);
        }
    }

    /** One nonauthoritative canonical resource snapshot read back from the future API layer. */
    public static final class ResourceSnapshot {
        private final String resourceId;
        private final long revision;
        private final byte[] payload;

        public ResourceSnapshot(String resourceId, long revision, byte[] payload) {
            this.resourceId = validateId(resourceId, "resource_id");
            if (revision < 1) {
                throw new OfflineStateException("snapshot revision must be positive");
            }
            this.revision = revision;
            if (payload == null
                    || payload.length == 0
                    || payload.length > MAX_SNAPSHOT_PAYLOAD_BYTES) {
                throw new OfflineStateException(
                        "snapshot payload length must be from 1 through "
                                + MAX_SNAPSHOT_PAYLOAD_BYTES
                );
            }
            this.payload = payload.clone();
        }

        ResourceSnapshot(ResourceSnapshot other) {
            this(other.resourceId, other.revision, other.payload);
        }

        public String resourceId() {
            return resourceId;
        }

        public long revision() {
            return revision;
        }

        public byte[] payload() {
            return payload.clone();
        }
    }

    interface StateCipher {
        SealedState seal(String clientId, byte[] plaintext);

        byte[] open(String clientId, SealedState sealed);

        void deleteKey(String clientId);
    }

    interface BlobStore {
        void write(String clientId, byte[] blob);

        byte[] read(String clientId);

        boolean exists(String clientId);

        void delete(String clientId);
    }

    static final class SealedState {
        private final byte[] iv;
        private final byte[] ciphertext;

        SealedState(byte[] iv, byte[] ciphertext) {
            this.iv = Objects.requireNonNull(iv, "iv").clone();
            this.ciphertext = Objects.requireNonNull(ciphertext, "ciphertext").clone();
        }

        byte[] iv() {
            return iv.clone();
        }

        byte[] ciphertext() {
            return ciphertext.clone();
        }
    }

    static final class AndroidKeystoreStateCipher implements StateCipher {
        private static final String ANDROID_KEYSTORE = "AndroidKeyStore";
        private static final String TRANSFORMATION = "AES/GCM/NoPadding";
        private static final String KEY_ALIAS_PREFIX = "mira.client.offline-state.v1.";
        private static final String AAD_PREFIX = "mira-client-offline-state-v1:";

        @Override
        public synchronized SealedState seal(String clientId, byte[] plaintext) {
            try {
                SecretKey key = getOrCreateKey(clientId);
                Cipher cipher = Cipher.getInstance(TRANSFORMATION);
                cipher.init(Cipher.ENCRYPT_MODE, key);
                cipher.updateAAD(aad(clientId));
                byte[] ciphertext = cipher.doFinal(plaintext);
                return new SealedState(cipher.getIV(), ciphertext);
            } catch (GeneralSecurityException | IOException exc) {
                throw new OfflineStateException(
                        "Android Keystore could not protect offline state",
                        exc
                );
            }
        }

        @Override
        public synchronized byte[] open(String clientId, SealedState sealed) {
            try {
                SecretKey key = existingKey(clientId);
                Cipher cipher = Cipher.getInstance(TRANSFORMATION);
                cipher.init(
                        Cipher.DECRYPT_MODE,
                        key,
                        new GCMParameterSpec(128, sealed.iv())
                );
                cipher.updateAAD(aad(clientId));
                return cipher.doFinal(sealed.ciphertext());
            } catch (GeneralSecurityException | IOException exc) {
                throw new StateUnavailableException(
                        "Android Keystore could not authenticate offline state",
                        exc
                );
            }
        }

        @Override
        public synchronized void deleteKey(String clientId) {
            try {
                KeyStore keyStore = keyStore();
                String alias = alias(clientId);
                if (keyStore.containsAlias(alias)) {
                    keyStore.deleteEntry(alias);
                }
            } catch (GeneralSecurityException | IOException exc) {
                throw new OfflineStateException(
                        "Android Keystore could not delete offline state key",
                        exc
                );
            }
        }

        private SecretKey getOrCreateKey(String clientId)
                throws GeneralSecurityException, IOException {
            KeyStore keyStore = keyStore();
            String alias = alias(clientId);
            if (keyStore.containsAlias(alias)) {
                return existingKey(keyStore, alias);
            }

            KeyGenerator generator = KeyGenerator.getInstance(
                    KeyProperties.KEY_ALGORITHM_AES,
                    ANDROID_KEYSTORE
            );
            generator.init(
                    new KeyGenParameterSpec.Builder(
                            alias,
                            KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT
                    )
                            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                            .setKeySize(256)
                            .setRandomizedEncryptionRequired(true)
                            .build()
            );
            return generator.generateKey();
        }

        private SecretKey existingKey(String clientId)
                throws GeneralSecurityException, IOException {
            KeyStore keyStore = keyStore();
            String alias = alias(clientId);
            if (!keyStore.containsAlias(alias)) {
                throw new StateUnavailableException(
                        "Android Keystore offline state key is missing"
                );
            }
            return existingKey(keyStore, alias);
        }

        private SecretKey existingKey(KeyStore keyStore, String alias)
                throws GeneralSecurityException {
            java.security.Key key = keyStore.getKey(alias, null);
            if (!(key instanceof SecretKey)) {
                throw new StateUnavailableException(
                        "Android Keystore offline state key is invalid"
                );
            }
            return (SecretKey) key;
        }

        private KeyStore keyStore() throws GeneralSecurityException, IOException {
            KeyStore keyStore = KeyStore.getInstance(ANDROID_KEYSTORE);
            keyStore.load(null);
            return keyStore;
        }

        private static byte[] aad(String clientId) {
            return (AAD_PREFIX + clientId).getBytes(StandardCharsets.UTF_8);
        }

        private static String alias(String clientId) {
            return KEY_ALIAS_PREFIX + stableHash(clientId);
        }
    }

    static final class NoBackupStateBlobStore implements BlobStore {
        private static final String DIRECTORY_NAME = "mira-client-offline-state";
        private final File root;

        NoBackupStateBlobStore(Context context) {
            root = new File(context.getNoBackupFilesDir(), DIRECTORY_NAME);
            if (!root.isDirectory() && !root.mkdirs() && !root.isDirectory()) {
                throw new OfflineStateException("cannot create offline state directory");
            }
        }

        @Override
        public void write(String clientId, byte[] blob) {
            if (blob == null || blob.length == 0 || blob.length > MAX_SEALED_BLOB_BYTES) {
                throw new OfflineStateException("offline state blob size is invalid");
            }
            AtomicFile file = atomicFile(clientId);
            FileOutputStream output = null;
            try {
                output = file.startWrite();
                output.write(blob);
                file.finishWrite(output);
            } catch (IOException exc) {
                if (output != null) {
                    file.failWrite(output);
                }
                throw new OfflineStateException("cannot persist offline state", exc);
            }
        }

        @Override
        public byte[] read(String clientId) {
            AtomicFile file = atomicFile(clientId);
            if (!file.getBaseFile().isFile()) {
                throw new StateUnavailableException("offline state is not stored");
            }
            try (FileInputStream input = file.openRead();
                 ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[4096];
                int count;
                while ((count = input.read(buffer)) != -1) {
                    output.write(buffer, 0, count);
                    if (output.size() > MAX_SEALED_BLOB_BYTES) {
                        throw new StateUnavailableException(
                                "offline state blob exceeds size limit"
                        );
                    }
                }
                return output.toByteArray();
            } catch (IOException exc) {
                throw new StateUnavailableException("cannot read offline state", exc);
            }
        }

        @Override
        public boolean exists(String clientId) {
            return atomicFile(clientId).getBaseFile().isFile();
        }

        @Override
        public void delete(String clientId) {
            atomicFile(clientId).delete();
        }

        private AtomicFile atomicFile(String clientId) {
            return new AtomicFile(new File(root, stableHash(clientId) + ".bin"));
        }
    }

    private static final class LocalState {
        long nextSequence;
        String cursor;
        final ArrayList<QueuedCommand> pending;
        final ArrayList<AcknowledgedCommand> acknowledged;
        final ArrayList<ResourceSnapshot> snapshots;

        LocalState(
                long nextSequence,
                String cursor,
                ArrayList<QueuedCommand> pending,
                ArrayList<AcknowledgedCommand> acknowledged,
                ArrayList<ResourceSnapshot> snapshots
        ) {
            this.nextSequence = nextSequence;
            this.cursor = cursor;
            this.pending = pending;
            this.acknowledged = acknowledged;
            this.snapshots = snapshots;
        }

        static LocalState empty() {
            return new LocalState(
                    1L,
                    null,
                    new ArrayList<>(),
                    new ArrayList<>(),
                    new ArrayList<>()
            );
        }
    }

    private static final class AcknowledgedCommand {
        final long sequence;
        final String commandId;
        final String idempotencyKey;
        final byte[] fingerprint;

        AcknowledgedCommand(
                long sequence,
                String commandId,
                String idempotencyKey,
                byte[] fingerprint
        ) {
            if (sequence <= 0) {
                throw new OfflineStateException(
                        "acknowledgement sequence must be positive"
                );
            }
            this.sequence = sequence;
            this.commandId = validateId(commandId, "command_id");
            this.idempotencyKey = validateToken(idempotencyKey, "idempotency_key");
            if (fingerprint == null || fingerprint.length != SHA256_BYTES) {
                throw new OfflineStateException(
                        "acknowledgement fingerprint length is invalid"
                );
            }
            this.fingerprint = fingerprint.clone();
        }
    }

    public static class OfflineStateException extends RuntimeException {
        public OfflineStateException(String message) {
            super(message);
        }

        public OfflineStateException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    public static final class StateUnavailableException extends OfflineStateException {
        public StateUnavailableException(String message) {
            super(message);
        }

        public StateUnavailableException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    public static final class StateConflictException extends OfflineStateException {
        public StateConflictException(String message) {
            super(message);
        }
    }

    public static final class StateCapacityException extends OfflineStateException {
        public StateCapacityException(String message) {
            super(message);
        }
    }
}
