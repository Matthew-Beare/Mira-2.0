package com.mira.client.core.security;

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
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Objects;
import java.util.regex.Pattern;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/**
 * Stores one opaque MIRA client credential using Android Keystore backed AES-GCM.
 *
 * <p>This class stores MIRA client authentication material only. Provider OAuth tokens,
 * database credentials, canonical state, and provider resource identifiers do not belong here.
 * The encryption key stays in Android Keystore; only versioned authenticated ciphertext is
 * persisted under {@link Context#getNoBackupFilesDir()}.</p>
 */
public final class ProtectedCredentialStore {
    private static final Pattern CLIENT_ID_PATTERN =
            Pattern.compile("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$");
    private static final int FORMAT_VERSION = 1;
    private static final int GCM_IV_BYTES = 12;
    private static final int MAX_CREDENTIAL_BYTES = 4096;
    private static final int MAX_CIPHERTEXT_BYTES = MAX_CREDENTIAL_BYTES + 64;
    private static final int MAX_BLOB_BYTES = 8192;

    private final CipherEngine cipherEngine;
    private final BlobStore blobStore;

    /** Creates the production Android credential store. */
    public ProtectedCredentialStore(Context context) {
        this(
                new AndroidKeystoreCipherEngine(),
                new NoBackupBlobStore(Objects.requireNonNull(context, "context"))
        );
    }

    /** Package-private dependency injection seam for deterministic JVM tests. */
    ProtectedCredentialStore(CipherEngine cipherEngine, BlobStore blobStore) {
        this.cipherEngine = Objects.requireNonNull(cipherEngine, "cipherEngine");
        this.blobStore = Objects.requireNonNull(blobStore, "blobStore");
    }

    /**
     * Encrypts and stores the credential, then zeroes the caller-provided byte array.
     *
     * <p>The caller buffer is cleared whether storage succeeds or fails. Callers that need to
     * retry after a storage failure must obtain fresh enrollment material rather than retaining a
     * second plaintext copy.</p>
     */
    public void storeAndClear(String clientId, byte[] credential) {
        if (credential == null) {
            throw new CredentialStorageException("credential must not be null");
        }
        try {
            String validatedClientId = validateClientId(clientId);
            if (credential.length == 0 || credential.length > MAX_CREDENTIAL_BYTES) {
                throw new CredentialStorageException(
                        "credential length must be from 1 through " + MAX_CREDENTIAL_BYTES
                );
            }

            byte[] working = credential.clone();
            try {
                SealedCredential sealed = cipherEngine.seal(validatedClientId, working);
                blobStore.write(validatedClientId, encode(sealed));
            } finally {
                Arrays.fill(working, (byte) 0);
            }
        } finally {
            Arrays.fill(credential, (byte) 0);
        }
    }

    /** Loads and authenticates the exact credential bytes for the supplied client ID. */
    public byte[] load(String clientId) {
        String validatedClientId = validateClientId(clientId);
        if (!blobStore.exists(validatedClientId)) {
            throw new CredentialUnavailableException("client credential is not stored");
        }
        SealedCredential sealed = decode(blobStore.read(validatedClientId));
        byte[] credential = cipherEngine.open(validatedClientId, sealed);
        if (credential.length == 0 || credential.length > MAX_CREDENTIAL_BYTES) {
            Arrays.fill(credential, (byte) 0);
            throw new CredentialStorageException("decrypted credential length is invalid");
        }
        return credential;
    }

    /** Returns whether encrypted local material exists. It does not prove the key can decrypt it. */
    public boolean hasStoredMaterial(String clientId) {
        return blobStore.exists(validateClientId(clientId));
    }

    /**
     * Deletes local ciphertext and the matching Android Keystore entry.
     *
     * <p>This operation is intentionally local-only. It does not claim or perform server-side
     * session revocation, which remains authoritative in the MIRA client-session registry.</p>
     */
    public void delete(String clientId) {
        String validatedClientId = validateClientId(clientId);
        CredentialStorageException failure = null;
        try {
            blobStore.delete(validatedClientId);
        } catch (CredentialStorageException exc) {
            failure = exc;
        }
        try {
            cipherEngine.deleteKey(validatedClientId);
        } catch (CredentialStorageException exc) {
            if (failure == null) {
                failure = exc;
            } else {
                failure.addSuppressed(exc);
            }
        }
        if (failure != null) {
            throw failure;
        }
    }

    private static String validateClientId(String clientId) {
        if (clientId == null || !CLIENT_ID_PATTERN.matcher(clientId).matches()) {
            throw new CredentialStorageException("client_id is invalid");
        }
        return clientId;
    }

    private static byte[] encode(SealedCredential sealed) {
        byte[] iv = sealed.iv();
        byte[] ciphertext = sealed.ciphertext();
        if (iv.length != GCM_IV_BYTES) {
            throw new CredentialStorageException("credential IV length is invalid");
        }
        if (ciphertext.length == 0 || ciphertext.length > MAX_CIPHERTEXT_BYTES) {
            throw new CredentialStorageException("credential ciphertext length is invalid");
        }

        try {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            try (DataOutputStream output = new DataOutputStream(bytes)) {
                output.writeByte(FORMAT_VERSION);
                output.writeByte(iv.length);
                output.write(iv);
                output.writeInt(ciphertext.length);
                output.write(ciphertext);
            }
            return bytes.toByteArray();
        } catch (IOException exc) {
            throw new CredentialStorageException("cannot encode protected credential", exc);
        }
    }

    private static SealedCredential decode(byte[] blob) {
        if (blob == null || blob.length == 0 || blob.length > MAX_BLOB_BYTES) {
            throw new CredentialStorageException("protected credential blob is invalid");
        }
        try (DataInputStream input = new DataInputStream(new ByteArrayInputStream(blob))) {
            int version = input.readUnsignedByte();
            if (version != FORMAT_VERSION) {
                throw new CredentialStorageException(
                        "unsupported protected credential format version"
                );
            }
            int ivLength = input.readUnsignedByte();
            if (ivLength != GCM_IV_BYTES) {
                throw new CredentialStorageException("protected credential IV is invalid");
            }
            byte[] iv = new byte[ivLength];
            input.readFully(iv);

            int ciphertextLength = input.readInt();
            if (ciphertextLength <= 0 || ciphertextLength > MAX_CIPHERTEXT_BYTES) {
                throw new CredentialStorageException(
                        "protected credential ciphertext is invalid"
                );
            }
            byte[] ciphertext = new byte[ciphertextLength];
            input.readFully(ciphertext);
            if (input.read() != -1) {
                throw new CredentialStorageException(
                        "protected credential blob contains trailing bytes"
                );
            }
            return new SealedCredential(iv, ciphertext);
        } catch (EOFException exc) {
            throw new CredentialStorageException("protected credential blob is truncated", exc);
        } catch (IOException exc) {
            throw new CredentialStorageException("cannot decode protected credential", exc);
        }
    }

    interface CipherEngine {
        SealedCredential seal(String clientId, byte[] plaintext);

        byte[] open(String clientId, SealedCredential sealed);

        void deleteKey(String clientId);
    }

    interface BlobStore {
        void write(String clientId, byte[] blob);

        byte[] read(String clientId);

        boolean exists(String clientId);

        void delete(String clientId);
    }

    static final class SealedCredential {
        private final byte[] iv;
        private final byte[] ciphertext;

        SealedCredential(byte[] iv, byte[] ciphertext) {
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

    static final class AndroidKeystoreCipherEngine implements CipherEngine {
        private static final String ANDROID_KEYSTORE = "AndroidKeyStore";
        private static final String TRANSFORMATION = "AES/GCM/NoPadding";
        private static final String KEY_ALIAS_PREFIX = "mira.client.credential.v1.";
        private static final String AAD_PREFIX = "mira-client-credential-v1:";

        @Override
        public synchronized SealedCredential seal(String clientId, byte[] plaintext) {
            try {
                SecretKey key = getOrCreateKey(clientId);
                Cipher cipher = Cipher.getInstance(TRANSFORMATION);
                cipher.init(Cipher.ENCRYPT_MODE, key);
                cipher.updateAAD(aad(clientId));
                byte[] ciphertext = cipher.doFinal(plaintext);
                return new SealedCredential(cipher.getIV(), ciphertext);
            } catch (GeneralSecurityException | IOException exc) {
                throw new CredentialStorageException(
                        "Android Keystore could not protect client credential",
                        exc
                );
            }
        }

        @Override
        public synchronized byte[] open(String clientId, SealedCredential sealed) {
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
                throw new CredentialUnavailableException(
                        "Android Keystore could not authenticate client credential",
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
                throw new CredentialStorageException(
                        "Android Keystore could not delete client credential key",
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
                throw new CredentialUnavailableException(
                        "Android Keystore client credential key is missing"
                );
            }
            return existingKey(keyStore, alias);
        }

        private SecretKey existingKey(KeyStore keyStore, String alias)
                throws GeneralSecurityException {
            java.security.Key key = keyStore.getKey(alias, null);
            if (!(key instanceof SecretKey)) {
                throw new CredentialUnavailableException(
                        "Android Keystore client credential key is invalid"
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

    static final class NoBackupBlobStore implements BlobStore {
        private static final String DIRECTORY_NAME = "mira-client-credentials";
        private final File root;

        NoBackupBlobStore(Context context) {
            root = new File(context.getNoBackupFilesDir(), DIRECTORY_NAME);
            if (!root.isDirectory() && !root.mkdirs() && !root.isDirectory()) {
                throw new CredentialStorageException(
                        "cannot create protected credential storage directory"
                );
            }
        }

        @Override
        public void write(String clientId, byte[] blob) {
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
                throw new CredentialStorageException(
                        "cannot persist protected client credential",
                        exc
                );
            }
        }

        @Override
        public byte[] read(String clientId) {
            AtomicFile file = atomicFile(clientId);
            if (!file.getBaseFile().isFile()) {
                throw new CredentialUnavailableException("client credential is not stored");
            }
            try (FileInputStream input = file.openRead();
                 ByteArrayOutputStream output = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[1024];
                int count;
                while ((count = input.read(buffer)) != -1) {
                    output.write(buffer, 0, count);
                    if (output.size() > MAX_BLOB_BYTES) {
                        throw new CredentialStorageException(
                                "protected credential blob exceeds size limit"
                        );
                    }
                }
                return output.toByteArray();
            } catch (IOException exc) {
                throw new CredentialStorageException(
                        "cannot read protected client credential",
                        exc
                );
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
            throw new CredentialStorageException("SHA-256 is unavailable", exc);
        }
    }

    public static class CredentialStorageException extends RuntimeException {
        public CredentialStorageException(String message) {
            super(message);
        }

        public CredentialStorageException(String message, Throwable cause) {
            super(message, cause);
        }
    }

    public static final class CredentialUnavailableException extends CredentialStorageException {
        public CredentialUnavailableException(String message) {
            super(message);
        }

        public CredentialUnavailableException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
