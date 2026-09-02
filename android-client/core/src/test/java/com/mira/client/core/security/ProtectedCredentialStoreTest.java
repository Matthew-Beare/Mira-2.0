package com.mira.client.core.security;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertThrows;
import static org.junit.Assert.assertTrue;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

import org.junit.Before;
import org.junit.Test;

public final class ProtectedCredentialStoreTest {
    private TestAesGcmCipherEngine cipher;
    private InMemoryBlobStore blobs;
    private ProtectedCredentialStore store;

    @Before
    public void setUp() {
        cipher = new TestAesGcmCipherEngine();
        blobs = new InMemoryBlobStore();
        store = new ProtectedCredentialStore(cipher, blobs);
    }

    @Test
    public void storeLoadRoundTripClearsCallerBufferAndPersistsNoPlaintext() {
        byte[] expected = bytes("mira-enrollment-secret-0123456789");
        byte[] caller = expected.clone();

        store.storeAndClear("client-001", caller);

        assertAllZero(caller);
        assertArrayEquals(expected, store.load("client-001"));
        assertTrue(store.hasStoredMaterial("client-001"));
        assertFalse(containsSubsequence(blobs.raw("client-001"), expected));
    }

    @Test
    public void storeFailureStillClearsCallerBuffer() {
        blobs.failWrites = true;
        byte[] caller = bytes("credential-that-must-not-survive-failure");

        assertThrows(
                ProtectedCredentialStore.CredentialStorageException.class,
                () -> store.storeAndClear("client-001", caller)
        );

        assertAllZero(caller);
    }

    @Test
    public void tamperedCiphertextFailsClosed() {
        byte[] caller = bytes("tamper-sensitive-credential");
        store.storeAndClear("client-001", caller);
        byte[] tampered = blobs.raw("client-001").clone();
        tampered[tampered.length - 1] ^= 0x01;
        blobs.overwrite("client-001", tampered);

        assertThrows(
                ProtectedCredentialStore.CredentialUnavailableException.class,
                () -> store.load("client-001")
        );
    }

    @Test
    public void ciphertextIsBoundToExactClientId() {
        store.storeAndClear("client-a", bytes("credential-for-client-a"));
        store.storeAndClear("client-b", bytes("credential-for-client-b"));
        blobs.overwrite("client-b", blobs.raw("client-a").clone());

        assertThrows(
                ProtectedCredentialStore.CredentialUnavailableException.class,
                () -> store.load("client-b")
        );
    }

    @Test
    public void replacementUsesFreshAuthenticatedCiphertextAndLoadsLatestSecret() {
        store.storeAndClear("client-001", bytes("first-client-credential"));
        byte[] firstBlob = blobs.raw("client-001").clone();

        byte[] second = bytes("second-client-credential");
        byte[] expected = second.clone();
        store.storeAndClear("client-001", second);
        byte[] secondBlob = blobs.raw("client-001").clone();

        assertFalse(Arrays.equals(firstBlob, secondBlob));
        assertArrayEquals(expected, store.load("client-001"));
    }

    @Test
    public void deleteIsIdempotentAndRemovesCiphertextAndKey() {
        store.storeAndClear("client-001", bytes("delete-this-credential"));
        assertTrue(cipher.hasKey("client-001"));

        store.delete("client-001");
        store.delete("client-001");

        assertFalse(store.hasStoredMaterial("client-001"));
        assertFalse(cipher.hasKey("client-001"));
        assertThrows(
                ProtectedCredentialStore.CredentialUnavailableException.class,
                () -> store.load("client-001")
        );
    }

    @Test
    public void malformedEnvelopeFailsClosed() {
        blobs.overwrite("client-001", new byte[] {99, 1, 2, 3});

        assertThrows(
                ProtectedCredentialStore.CredentialStorageException.class,
                () -> store.load("client-001")
        );
    }

    @Test
    public void invalidClientIdIsRejectedAndCredentialBufferIsStillCleared() {
        byte[] caller = bytes("credential-for-invalid-client");

        assertThrows(
                ProtectedCredentialStore.CredentialStorageException.class,
                () -> store.storeAndClear("../bad-client", caller)
        );

        assertAllZero(caller);
    }

    private static byte[] bytes(String value) {
        return value.getBytes(StandardCharsets.UTF_8);
    }

    private static void assertAllZero(byte[] value) {
        for (byte item : value) {
            assertTrue(item == 0);
        }
    }

    private static boolean containsSubsequence(byte[] haystack, byte[] needle) {
        if (needle.length == 0 || haystack.length < needle.length) {
            return false;
        }
        outer:
        for (int start = 0; start <= haystack.length - needle.length; start++) {
            for (int offset = 0; offset < needle.length; offset++) {
                if (haystack[start + offset] != needle[offset]) {
                    continue outer;
                }
            }
            return true;
        }
        return false;
    }

    private static final class InMemoryBlobStore implements ProtectedCredentialStore.BlobStore {
        private final Map<String, byte[]> values = new HashMap<>();
        private boolean failWrites;

        @Override
        public void write(String clientId, byte[] blob) {
            if (failWrites) {
                throw new ProtectedCredentialStore.CredentialStorageException("synthetic write failure");
            }
            values.put(clientId, blob.clone());
        }

        @Override
        public byte[] read(String clientId) {
            byte[] value = values.get(clientId);
            if (value == null) {
                throw new ProtectedCredentialStore.CredentialUnavailableException("missing synthetic blob");
            }
            return value.clone();
        }

        @Override
        public boolean exists(String clientId) {
            return values.containsKey(clientId);
        }

        @Override
        public void delete(String clientId) {
            values.remove(clientId);
        }

        byte[] raw(String clientId) {
            return values.get(clientId);
        }

        void overwrite(String clientId, byte[] blob) {
            values.put(clientId, blob.clone());
        }
    }

    private static final class TestAesGcmCipherEngine implements ProtectedCredentialStore.CipherEngine {
        private static final String TRANSFORMATION = "AES/GCM/NoPadding";
        private final SecureRandom random = new SecureRandom();
        private final Map<String, SecretKey> keys = new HashMap<>();

        @Override
        public ProtectedCredentialStore.SealedCredential seal(String clientId, byte[] plaintext) {
            try {
                SecretKey key = keys.computeIfAbsent(clientId, ignored -> newKey());
                Cipher instance = Cipher.getInstance(TRANSFORMATION);
                byte[] iv = new byte[12];
                random.nextBytes(iv);
                instance.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
                instance.updateAAD(aad(clientId));
                return new ProtectedCredentialStore.SealedCredential(
                        iv,
                        instance.doFinal(plaintext)
                );
            } catch (GeneralSecurityException exc) {
                throw new ProtectedCredentialStore.CredentialStorageException(
                        "synthetic cipher failure",
                        exc
                );
            }
        }

        @Override
        public byte[] open(
                String clientId,
                ProtectedCredentialStore.SealedCredential sealed
        ) {
            SecretKey key = keys.get(clientId);
            if (key == null) {
                throw new ProtectedCredentialStore.CredentialUnavailableException(
                        "synthetic key missing"
                );
            }
            try {
                Cipher instance = Cipher.getInstance(TRANSFORMATION);
                instance.init(
                        Cipher.DECRYPT_MODE,
                        key,
                        new GCMParameterSpec(128, sealed.iv())
                );
                instance.updateAAD(aad(clientId));
                return instance.doFinal(sealed.ciphertext());
            } catch (GeneralSecurityException exc) {
                throw new ProtectedCredentialStore.CredentialUnavailableException(
                        "synthetic authentication failure",
                        exc
                );
            }
        }

        @Override
        public void deleteKey(String clientId) {
            keys.remove(clientId);
        }

        boolean hasKey(String clientId) {
            return keys.containsKey(clientId);
        }

        private static SecretKey newKey() {
            try {
                KeyGenerator generator = KeyGenerator.getInstance("AES");
                generator.init(256);
                return generator.generateKey();
            } catch (GeneralSecurityException exc) {
                throw new ProtectedCredentialStore.CredentialStorageException(
                        "cannot create synthetic key",
                        exc
                );
            }
        }

        private static byte[] aad(String clientId) {
            return ("mira-client-credential-v1:" + clientId)
                    .getBytes(StandardCharsets.UTF_8);
        }
    }
}
