package com.mira.client.core.sync;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import org.junit.Before;
import org.junit.Test;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

public final class OfflineSyncStateStoreTest {
    private static final String CLIENT_ID = "android-client-1";

    private TestStateCipher cipher;
    private InMemoryBlobStore blobs;
    private OfflineSyncStateStore store;

    @Before
    public void setUp() {
        cipher = new TestStateCipher();
        blobs = new InMemoryBlobStore();
        store = new OfflineSyncStateStore(CLIENT_ID, cipher, blobs);
    }

    @Test
    public void restartPreservesExactApiCommandEnvelopeAndFifo() {
        OfflineSyncStateStore.CommandIntent first = upsert(
                "cmd-1",
                "resource-1",
                3L,
                "{\"secret\":\"alpha\"}"
        );
        OfflineSyncStateStore.CommandIntent second = new OfflineSyncStateStore.CommandIntent(
                "cmd-2",
                "subject-1",
                "entity",
                "append_event",
                1,
                "schema-v1",
                "resource-1",
                bytes("{\"event\":\"moved\"}"),
                "idem-2",
                4L,
                "event-2",
                "moved"
        );

        assertEquals(OfflineSyncStateStore.EnqueueResult.ENQUEUED, store.enqueue(first));
        assertEquals(OfflineSyncStateStore.EnqueueResult.ENQUEUED, store.enqueue(second));
        assertTrue(store.hasLocalState());
        assertFalse(contains(blobs.raw(CLIENT_ID), bytes("alpha")));
        assertFalse(contains(blobs.raw(CLIENT_ID), bytes("moved")));

        OfflineSyncStateStore restarted =
                new OfflineSyncStateStore(CLIENT_ID, cipher, blobs);
        List<OfflineSyncStateStore.QueuedCommand> pending = restarted.pendingCommands(10);

        assertEquals(2, pending.size());
        assertEquals(1L, pending.get(0).sequence());
        assertEquals(2L, pending.get(1).sequence());
        assertCommandEquals(first, pending.get(0).command());
        assertCommandEquals(second, pending.get(1).command());
    }

    @Test
    public void duplicateAndAcknowledgedReplaySuppressionSurviveRestart() {
        OfflineSyncStateStore.CommandIntent command = upsert(
                "cmd-replay",
                "resource-1",
                0L,
                "{\"value\":1}"
        );

        assertEquals(OfflineSyncStateStore.EnqueueResult.ENQUEUED, store.enqueue(command));
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_PENDING,
                store.enqueue(command)
        );
        assertEquals(1, store.pendingCount());

        store.acknowledge("cmd-replay", "idem-cmd-replay");
        store.acknowledge("cmd-replay", "idem-cmd-replay");
        assertEquals(0, store.pendingCount());
        assertEquals(1, store.acknowledgedCount());

        OfflineSyncStateStore restarted =
                new OfflineSyncStateStore(CLIENT_ID, cipher, blobs);
        assertEquals(
                OfflineSyncStateStore.EnqueueResult.ALREADY_ACKNOWLEDGED,
                restarted.enqueue(command)
        );
        assertEquals(0, restarted.pendingCount());
        assertEquals(1, restarted.acknowledgedCount());
    }

    @Test
    public void conflictingCommandOrAcknowledgementIdentityFailsClosed() {
        OfflineSyncStateStore.CommandIntent original = upsert(
                "cmd-conflict",
                "resource-1",
                1L,
                "{\"value\":1}"
        );
        store.enqueue(original);

        OfflineSyncStateStore.CommandIntent changed = new OfflineSyncStateStore.CommandIntent(
                "cmd-conflict",
                "subject-1",
                "entity",
                "upsert",
                1,
                "schema-v1",
                "resource-1",
                bytes("{\"value\":2}"),
                "idem-cmd-conflict",
                1L,
                null,
                null
        );

        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> store.enqueue(changed)
        );
        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> store.acknowledge("cmd-conflict", "wrong-idempotency")
        );
        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> store.acknowledge("unknown-command", "idem-unknown")
        );
        assertEquals(1, store.pendingCount());
    }

    @Test
    public void snapshotIdentityUsesDataClassAndRevisionRulesFailClosed() {
        OfflineSyncStateStore.ResourceSnapshot entityV1 =
                new OfflineSyncStateStore.ResourceSnapshot(
                        "entity",
                        "shared-id",
                        1,
                        bytes("{\"kind\":\"entity\"}")
                );
        OfflineSyncStateStore.ResourceSnapshot taskV1 =
                new OfflineSyncStateStore.ResourceSnapshot(
                        "task",
                        "shared-id",
                        1,
                        bytes("{\"kind\":\"task\"}")
                );

        assertEquals(OfflineSyncStateStore.SnapshotResult.STORED, store.putSnapshot(entityV1));
        assertEquals(OfflineSyncStateStore.SnapshotResult.STORED, store.putSnapshot(taskV1));
        assertEquals(
                OfflineSyncStateStore.SnapshotResult.UNCHANGED,
                store.putSnapshot(entityV1)
        );
        assertArrayEquals(
                bytes("{\"kind\":\"entity\"}"),
                store.snapshot("entity", "shared-id").payload()
        );
        assertArrayEquals(
                bytes("{\"kind\":\"task\"}"),
                store.snapshot("task", "shared-id").payload()
        );

        OfflineSyncStateStore.ResourceSnapshot fork =
                new OfflineSyncStateStore.ResourceSnapshot(
                        "entity",
                        "shared-id",
                        1,
                        bytes("{\"kind\":\"fork\"}")
                );
        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> store.putSnapshot(fork)
        );

        OfflineSyncStateStore.ResourceSnapshot entityV2 =
                new OfflineSyncStateStore.ResourceSnapshot(
                        "entity",
                        "shared-id",
                        2,
                        bytes("{\"kind\":\"entity\",\"revision\":2}")
                );
        assertEquals(OfflineSyncStateStore.SnapshotResult.STORED, store.putSnapshot(entityV2));
        assertEquals(2L, store.snapshot("entity", "shared-id").revision());

        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> store.putSnapshot(entityV1)
        );
    }

    @Test
    public void opaqueCursorUsesCompareAndSetAcrossRestart() {
        assertNull(store.cursor());
        store.compareAndSetCursor(null, "cursor-A");
        assertEquals("cursor-A", store.cursor());

        OfflineSyncStateStore restarted =
                new OfflineSyncStateStore(CLIENT_ID, cipher, blobs);
        assertEquals("cursor-A", restarted.cursor());
        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> restarted.compareAndSetCursor(null, "cursor-B")
        );

        restarted.compareAndSetCursor("cursor-A", "cursor-B");
        restarted.compareAndSetCursor("cursor-A", "cursor-B");
        assertEquals("cursor-B", restarted.cursor());
        assertThrows(
                OfflineSyncStateStore.StateConflictException.class,
                () -> restarted.compareAndSetCursor("cursor-A", "cursor-C")
        );
    }

    @Test
    public void tamperAndMissingKeyFailClosedWithoutSilentReset() {
        store.enqueue(upsert("cmd-tamper", "resource-1", 0L, "{\"secret\":42}"));
        byte[] original = blobs.raw(CLIENT_ID);
        byte[] tampered = original.clone();
        tampered[tampered.length - 1] ^= 0x01;
        blobs.setRaw(CLIENT_ID, tampered);

        OfflineSyncStateStore restarted =
                new OfflineSyncStateStore(CLIENT_ID, cipher, blobs);
        assertThrows(
                OfflineSyncStateStore.StateUnavailableException.class,
                restarted::pendingCount
        );
        assertTrue(blobs.exists(CLIENT_ID));

        blobs.setRaw(CLIENT_ID, original);
        cipher.deleteKey(CLIENT_ID);
        assertThrows(
                OfflineSyncStateStore.StateUnavailableException.class,
                restarted::pendingCount
        );
        assertTrue(blobs.exists(CLIENT_ID));
    }

    @Test
    public void copiedCiphertextCannotAuthenticateForDifferentClientEvenWithSameKey() {
        store.enqueue(upsert("cmd-aad", "resource-1", 0L, "{\"secret\":\"bound\"}"));

        String otherClient = "android-client-2";
        blobs.setRaw(otherClient, blobs.raw(CLIENT_ID));
        cipher.copyKey(CLIENT_ID, otherClient);
        OfflineSyncStateStore wrongClient =
                new OfflineSyncStateStore(otherClient, cipher, blobs);

        assertThrows(
                OfflineSyncStateStore.StateUnavailableException.class,
                wrongClient::pendingCount
        );
        assertTrue(blobs.exists(otherClient));
    }

    @Test
    public void explicitDiscardDeletesOnlyLocalBlobAndKey() {
        store.enqueue(upsert("cmd-discard", "resource-1", 0L, "{\"local\":true}"));
        store.putSnapshot(
                new OfflineSyncStateStore.ResourceSnapshot(
                        "entity",
                        "resource-1",
                        1,
                        bytes("{\"server\":true}")
                )
        );
        store.compareAndSetCursor(null, "cursor-1");
        assertTrue(cipher.hasKey(CLIENT_ID));
        assertTrue(store.hasLocalState());

        store.discardLocalState();
        store.discardLocalState();
        assertFalse(store.hasLocalState());
        assertFalse(cipher.hasKey(CLIENT_ID));

        OfflineSyncStateStore restarted =
                new OfflineSyncStateStore(CLIENT_ID, cipher, blobs);
        assertEquals(0, restarted.pendingCount());
        assertEquals(0, restarted.acknowledgedCount());
        assertNull(restarted.cursor());
        assertNull(restarted.snapshot("entity", "resource-1"));
    }

    @Test
    public void pendingCapacityFailsExplicitlyWithoutDroppingStoredCommands() {
        for (int index = 0; index < 128; index++) {
            String id = String.format("cmd-%03d", index);
            store.enqueue(upsert(id, "resource-1", 0L, "{\"n\":" + index + "}"));
        }
        assertEquals(128, store.pendingCount());
        assertThrows(
                OfflineSyncStateStore.StateCapacityException.class,
                () -> store.enqueue(
                        upsert("cmd-over-capacity", "resource-1", 0L, "{\"n\":129}")
                )
        );
        assertEquals(128, store.pendingCount());
    }

    @Test
    public void commandValidationMatchesCurrentApiActionAndEventShape() {
        assertThrows(
                OfflineSyncStateStore.OfflineStateException.class,
                () -> new OfflineSyncStateStore.CommandIntent(
                        "cmd-invalid-upsert",
                        "subject-1",
                        "entity",
                        "upsert",
                        1,
                        "schema-v1",
                        "resource-1",
                        bytes("{}"),
                        "idem-invalid-upsert",
                        0L,
                        "event-not-allowed",
                        "event-type"
                )
        );

        assertThrows(
                OfflineSyncStateStore.OfflineStateException.class,
                () -> new OfflineSyncStateStore.CommandIntent(
                        "cmd-invalid-event",
                        "subject-1",
                        "entity",
                        "append_event",
                        1,
                        "schema-v1",
                        "resource-1",
                        bytes("{}"),
                        "idem-invalid-event",
                        0L,
                        null,
                        null
                )
        );

        assertThrows(
                OfflineSyncStateStore.OfflineStateException.class,
                () -> upsert("cmd-negative", "resource-1", -1L, "{}")
        );
    }

    private static OfflineSyncStateStore.CommandIntent upsert(
            String commandId,
            String resourceId,
            Long expectedRevision,
            String payload
    ) {
        return new OfflineSyncStateStore.CommandIntent(
                commandId,
                "subject-1",
                "entity",
                "upsert",
                1,
                "schema-v1",
                resourceId,
                bytes(payload),
                "idem-" + commandId,
                expectedRevision,
                null,
                null
        );
    }

    private static void assertCommandEquals(
            OfflineSyncStateStore.CommandIntent expected,
            OfflineSyncStateStore.CommandIntent actual
    ) {
        assertEquals(expected.commandId(), actual.commandId());
        assertEquals(expected.subjectId(), actual.subjectId());
        assertEquals(expected.dataClass(), actual.dataClass());
        assertEquals(expected.action(), actual.action());
        assertEquals(expected.apiMajor(), actual.apiMajor());
        assertEquals(expected.schemaVersion(), actual.schemaVersion());
        assertEquals(expected.resourceId(), actual.resourceId());
        assertArrayEquals(expected.payload(), actual.payload());
        assertEquals(expected.idempotencyKey(), actual.idempotencyKey());
        assertEquals(expected.expectedRevision(), actual.expectedRevision());
        assertEquals(expected.eventId(), actual.eventId());
        assertEquals(expected.eventType(), actual.eventType());
    }

    private static byte[] bytes(String value) {
        return value.getBytes(StandardCharsets.UTF_8);
    }

    private static boolean contains(byte[] haystack, byte[] needle) {
        if (needle.length == 0 || haystack.length < needle.length) {
            return false;
        }
        for (int start = 0; start <= haystack.length - needle.length; start++) {
            boolean match = true;
            for (int offset = 0; offset < needle.length; offset++) {
                if (haystack[start + offset] != needle[offset]) {
                    match = false;
                    break;
                }
            }
            if (match) {
                return true;
            }
        }
        return false;
    }

    private static final class TestStateCipher implements OfflineSyncStateStore.StateCipher {
        private static final String TRANSFORMATION = "AES/GCM/NoPadding";
        private static final String AAD_PREFIX = "test-mira-offline-state:";
        private final Map<String, SecretKey> keys = new HashMap<>();

        @Override
        public synchronized OfflineSyncStateStore.SealedState seal(
                String clientId,
                byte[] plaintext
        ) {
            try {
                SecretKey key = keys.get(clientId);
                if (key == null) {
                    KeyGenerator generator = KeyGenerator.getInstance("AES");
                    generator.init(256);
                    key = generator.generateKey();
                    keys.put(clientId, key);
                }
                Cipher cipher = Cipher.getInstance(TRANSFORMATION);
                cipher.init(Cipher.ENCRYPT_MODE, key);
                cipher.updateAAD(aad(clientId));
                return new OfflineSyncStateStore.SealedState(
                        cipher.getIV(),
                        cipher.doFinal(plaintext)
                );
            } catch (GeneralSecurityException exc) {
                throw new OfflineSyncStateStore.OfflineStateException(
                        "test cipher could not seal state",
                        exc
                );
            }
        }

        @Override
        public synchronized byte[] open(
                String clientId,
                OfflineSyncStateStore.SealedState sealed
        ) {
            SecretKey key = keys.get(clientId);
            if (key == null) {
                throw new OfflineSyncStateStore.StateUnavailableException(
                        "test state key is missing"
                );
            }
            try {
                Cipher cipher = Cipher.getInstance(TRANSFORMATION);
                cipher.init(
                        Cipher.DECRYPT_MODE,
                        key,
                        new GCMParameterSpec(128, sealed.iv())
                );
                cipher.updateAAD(aad(clientId));
                return cipher.doFinal(sealed.ciphertext());
            } catch (GeneralSecurityException exc) {
                throw new OfflineSyncStateStore.StateUnavailableException(
                        "test state authentication failed",
                        exc
                );
            }
        }

        @Override
        public synchronized void deleteKey(String clientId) {
            keys.remove(clientId);
        }

        synchronized void copyKey(String fromClientId, String toClientId) {
            SecretKey key = keys.get(fromClientId);
            if (key == null) {
                throw new AssertionError("source test key is missing");
            }
            keys.put(toClientId, key);
        }

        synchronized boolean hasKey(String clientId) {
            return keys.containsKey(clientId);
        }

        private static byte[] aad(String clientId) {
            return (AAD_PREFIX + clientId).getBytes(StandardCharsets.UTF_8);
        }
    }

    private static final class InMemoryBlobStore implements OfflineSyncStateStore.BlobStore {
        private final Map<String, byte[]> blobs = new HashMap<>();

        @Override
        public synchronized void write(String clientId, byte[] blob) {
            blobs.put(clientId, blob.clone());
        }

        @Override
        public synchronized byte[] read(String clientId) {
            byte[] blob = blobs.get(clientId);
            if (blob == null) {
                throw new OfflineSyncStateStore.StateUnavailableException(
                        "test offline state is not stored"
                );
            }
            return blob.clone();
        }

        @Override
        public synchronized boolean exists(String clientId) {
            return blobs.containsKey(clientId);
        }

        @Override
        public synchronized void delete(String clientId) {
            blobs.remove(clientId);
        }

        synchronized byte[] raw(String clientId) {
            byte[] blob = blobs.get(clientId);
            if (blob == null) {
                throw new AssertionError("test blob is missing");
            }
            return blob.clone();
        }

        synchronized void setRaw(String clientId, byte[] blob) {
            blobs.put(clientId, blob.clone());
        }
    }
}
