package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.jspecify.annotations.Nullable;

/**
 * API-only context NKENC1 codec. No compression or keys shared with Inbox/Web purposes. Trace:
 * NK-AUT-001, AUT-001/DAT-009; UI226; SS314 §6/352 §11.2; PT-AUT-005-C01..04.
 */
public final class AuthContextCodec implements AutoCloseable {
  private static final int AUTH_CONTEXT_KEY_BYTES = 32;

  private static final byte[] MAGIC = "NKENC1".getBytes(StandardCharsets.US_ASCII);
  // BUG-036/YKT-032: caller monitors must not control internal state/resource lifetime.
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final String currentVersion;
  private final Map<String, byte[]> keys;
  private final SecureRandom random;
  private boolean closed;

  public AuthContextCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey) {
    this(currentVersion, currentKey, previousVersion, previousKey, new SecureRandom());
  }

  AuthContextCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey,
      SecureRandom random) {
    validateVersion(currentVersion);
    validateKey(currentKey);
    Objects.requireNonNull(random, "random");
    if ((previousVersion == null) != (previousKey == null)) {
      throw new IllegalArgumentException("previous auth context key and version must be paired");
    }
    if (previousVersion != null) {
      validateVersion(previousVersion);
      validateKey(Objects.requireNonNull(previousKey, "paired previous key"));
      if (currentVersion.equals(previousVersion)) {
        throw new IllegalArgumentException("auth context key versions must differ");
      }
    }
    this.currentVersion = currentVersion;
    this.random = random;
    Map<String, byte[]> copies = new HashMap<>();
    copies.put(currentVersion, currentKey.clone());
    if (previousVersion != null) {
      copies.put(
          previousVersion, Objects.requireNonNull(previousKey, "paired previous key").clone());
    }
    keys = Map.copyOf(copies);
  }

  public EncryptedAuthContext encrypt(AuthContextIdentity identity, AuthenticationContext raw) {
    stateLock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "identity");
      Objects.requireNonNull(raw, "raw");
      // SSC421/BUG3021: acquire every owned buffer inside its cleanup region.
      byte[] plaintext = new byte[0];
      byte[] nonce = new byte[0];
      try {
        plaintext = raw.wireValue().getBytes(StandardCharsets.US_ASCII);
        nonce = new byte[12];
        random.nextBytes(nonce);
        byte[] encrypted =
            crypt(
                Cipher.ENCRYPT_MODE,
                key(currentVersion),
                nonce,
                identity.aad(currentVersion),
                plaintext);
        try {
          byte[] id = currentVersion.getBytes(StandardCharsets.US_ASCII);
          byte[] stored =
              ByteBuffer.allocate(20 + id.length + encrypted.length)
                  .put(MAGIC)
                  .put((byte) 1)
                  .put((byte) id.length)
                  .put(id)
                  .put(nonce)
                  .put(encrypted)
                  .array();
          try {
            return new EncryptedAuthContext(currentVersion, stored);
          } finally {
            Arrays.fill(stored, (byte) 0);
          }
        } finally {
          Arrays.fill(encrypted, (byte) 0);
        }
      } catch (GeneralSecurityException failure) {
        throw new AuthContextCryptoException(AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE);
      } finally {
        Arrays.fill(plaintext, (byte) 0);
        Arrays.fill(nonce, (byte) 0);
      }
    } finally {
      stateLock.unlock();
    }
  }

  public AuthenticationContext decrypt(
      AuthContextIdentity identity, EncryptedAuthContext storedContext) {
    stateLock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "identity");
      Objects.requireNonNull(storedContext, "storedContext");
      byte[] stored = storedContext.ciphertext();
      try {
        if (!Arrays.equals(stored, 0, 6, MAGIC, 0, 6) || stored[6] != 1) {
          throw new AuthContextCryptoException(AuthContextCryptoException.Reason.INVALID);
        }
        int idLength = Byte.toUnsignedInt(stored[7]);
        if (idLength < 1 || idLength > 16 || stored.length != 100 + idLength) {
          throw new AuthContextCryptoException(AuthContextCryptoException.Reason.INVALID);
        }
        String version = new String(stored, 8, idLength, StandardCharsets.US_ASCII);
        if (!storedContext.keyVersion().equals(version)) {
          throw new AuthContextCryptoException(AuthContextCryptoException.Reason.INVALID);
        }
        byte[] selected = key(version);
        byte[] nonce = new byte[0];
        byte[] encrypted = new byte[0];
        try {
          nonce = Arrays.copyOfRange(stored, 8 + idLength, 20 + idLength);
          encrypted = Arrays.copyOfRange(stored, 20 + idLength, stored.length);
          byte[] plaintext =
              crypt(Cipher.DECRYPT_MODE, selected, nonce, identity.aad(version), encrypted);
          try {
            return AuthenticationContext.of(new String(plaintext, StandardCharsets.US_ASCII));
          } finally {
            Arrays.fill(plaintext, (byte) 0);
          }
        } finally {
          Arrays.fill(nonce, (byte) 0);
          Arrays.fill(encrypted, (byte) 0);
        }
      } catch (BadPaddingException | IllegalArgumentException failure) {
        throw new AuthContextCryptoException(AuthContextCryptoException.Reason.INVALID);
      } catch (GeneralSecurityException failure) {
        throw new AuthContextCryptoException(AuthContextCryptoException.Reason.CRYPTO_UNAVAILABLE);
      } finally {
        Arrays.fill(stored, (byte) 0);
      }
    } finally {
      stateLock.unlock();
    }
  }

  private byte[] key(String version) {
    byte[] key = keys.get(version);
    if (key == null)
      throw new AuthContextCryptoException(AuthContextCryptoException.Reason.KEY_UNAVAILABLE);
    return key;
  }

  private static byte[] crypt(int mode, byte[] key, byte[] nonce, byte[] aad, byte[] data)
      throws GeneralSecurityException {
    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(mode, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad);
    return cipher.doFinal(data);
  }

  private static void validateVersion(String version) {
    Objects.requireNonNull(version, "version");
    if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException("auth context key version is invalid");
    }
  }

  private static void validateKey(byte[] key) {
    Objects.requireNonNull(key, "key");
    if (key.length != AUTH_CONTEXT_KEY_BYTES)
      throw new IllegalArgumentException("auth context key must be 256 bits");
  }

  private void ensureOpen() {
    if (closed) throw new IllegalStateException("auth context codec is closed");
  }

  @Override
  public void close() {
    stateLock.lock();
    try {
      for (byte[] key : keys.values()) Arrays.fill(key, (byte) 0);
      closed = true;
    } finally {
      stateLock.unlock();
    }
  }
}
