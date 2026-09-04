package dev.codex.schubert.nk.api.idempotency;

import java.io.ByteArrayOutputStream;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.zip.DataFormatException;
import java.util.zip.Deflater;
import java.util.zip.Inflater;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.jspecify.annotations.Nullable;

/**
 * JDK Deflater level 3 plus AES-256-GCM response snapshot codec.
 *
 * <p>Trace: DAT-009, UI 241/242, SS 324 §6/§15 and PT-IDEM-007/008.
 */
public final class ResponseSnapshotCodec implements AutoCloseable {
  public static final int MAXIMUM_PLAINTEXT_BYTES = 1_000_000;
  private static final int AES_KEY_BYTES = 32;
  private static final int NONCE_BYTES = 12;
  private static final int GCM_TAG_BITS = 128;
  private static final int BUFFER_BYTES = 8192;

  private final String currentVersion;
  private final byte[] currentKey;
  private final @Nullable String previousVersion;
  private final byte @Nullable [] previousKey;
  private final SecureRandom secureRandom;
  private boolean closed;

  public ResponseSnapshotCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey) {
    this(currentVersion, currentKey, previousVersion, previousKey, new SecureRandom());
  }

  ResponseSnapshotCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey,
      SecureRandom secureRandom) {
    this.currentVersion = validateVersion(currentVersion, "currentVersion");
    this.currentKey = validateKey(currentKey, "currentKey");
    if ((previousVersion == null) != (previousKey == null)) {
      throw new IllegalArgumentException("previous response key version and key must be paired");
    }
    this.previousVersion =
        previousVersion == null ? null : validateVersion(previousVersion, "previousVersion");
    this.previousKey = previousKey == null ? null : validateKey(previousKey, "previousKey");
    if (this.currentVersion.equals(this.previousVersion)) {
      throw new IllegalArgumentException("response key versions must be distinct");
    }
    this.secureRandom = Objects.requireNonNull(secureRandom, "secureRandom");
  }

  public EncryptedResponseSnapshot encrypt(ResponseSnapshotIdentity identity, byte[] plaintext) {
    ensureOpen();
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(plaintext, "plaintext");
    if (plaintext.length > MAXIMUM_PLAINTEXT_BYTES) {
      throw new IllegalArgumentException("response snapshot plaintext exceeds 1000000 bytes");
    }

    byte[] compressed = compress(plaintext);
    byte[] nonce = new byte[NONCE_BYTES];
    byte[] aad = identity.aad();
    secureRandom.nextBytes(nonce);
    try {
      Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
      cipher.init(
          Cipher.ENCRYPT_MODE,
          new SecretKeySpec(currentKey, "AES"),
          new GCMParameterSpec(GCM_TAG_BITS, nonce));
      cipher.updateAAD(aad);
      byte[] encrypted = cipher.doFinal(compressed);
      byte[] stored = new byte[nonce.length + encrypted.length];
      System.arraycopy(nonce, 0, stored, 0, nonce.length);
      System.arraycopy(encrypted, 0, stored, nonce.length, encrypted.length);
      Arrays.fill(encrypted, (byte) 0);
      return new EncryptedResponseSnapshot(currentVersion, stored);
    } catch (GeneralSecurityException exception) {
      throw new ResponseSnapshotException(
          ResponseSnapshotException.Reason.CRYPTO_UNAVAILABLE,
          "response snapshot encryption is unavailable",
          exception);
    } finally {
      Arrays.fill(compressed, (byte) 0);
      Arrays.fill(nonce, (byte) 0);
      Arrays.fill(aad, (byte) 0);
    }
  }

  public byte[] decrypt(ResponseSnapshotIdentity identity, EncryptedResponseSnapshot snapshot) {
    ensureOpen();
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(snapshot, "snapshot");
    byte[] key =
        selectKey(snapshot.keyVersion())
            .orElseThrow(
                () ->
                    new ResponseSnapshotException(
                        ResponseSnapshotException.Reason.KEY_UNAVAILABLE,
                        "response snapshot key version is unavailable"));
    byte[] stored = snapshot.ciphertext();
    byte[] nonce = Arrays.copyOfRange(stored, 0, NONCE_BYTES);
    byte[] encrypted = Arrays.copyOfRange(stored, NONCE_BYTES, stored.length);
    byte[] aad = identity.aad();
    byte[] compressed = null;
    try {
      Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
      cipher.init(
          Cipher.DECRYPT_MODE,
          new SecretKeySpec(key, "AES"),
          new GCMParameterSpec(GCM_TAG_BITS, nonce));
      cipher.updateAAD(aad);
      compressed = cipher.doFinal(encrypted);
      return decompress(compressed);
    } catch (GeneralSecurityException exception) {
      throw new ResponseSnapshotException(
          ResponseSnapshotException.Reason.SNAPSHOT_INVALID,
          "response snapshot authentication failed",
          exception);
    } finally {
      Arrays.fill(stored, (byte) 0);
      Arrays.fill(nonce, (byte) 0);
      Arrays.fill(encrypted, (byte) 0);
      Arrays.fill(aad, (byte) 0);
      if (compressed != null) {
        Arrays.fill(compressed, (byte) 0);
      }
    }
  }

  private Optional<byte[]> selectKey(String version) {
    if (currentVersion.equals(version)) {
      return Optional.of(currentKey);
    }
    if (previousVersion != null && previousVersion.equals(version)) {
      return Optional.of(previousKey);
    }
    return Optional.empty();
  }

  private static byte[] compress(byte[] plaintext) {
    Deflater deflater = new Deflater(3);
    byte[] buffer = new byte[BUFFER_BYTES];
    try {
      deflater.setInput(plaintext);
      deflater.finish();
      ByteArrayOutputStream output = new ByteArrayOutputStream(Math.min(plaintext.length, BUFFER_BYTES));
      while (!deflater.finished()) {
        int count = deflater.deflate(buffer);
        output.write(buffer, 0, count);
      }
      return output.toByteArray();
    } finally {
      Arrays.fill(buffer, (byte) 0);
      deflater.end();
    }
  }

  private static byte[] decompress(byte[] compressed) {
    Inflater inflater = new Inflater();
    byte[] buffer = new byte[BUFFER_BYTES];
    try {
      inflater.setInput(compressed);
      ByteArrayOutputStream output = new ByteArrayOutputStream(Math.min(compressed.length, BUFFER_BYTES));
      while (!inflater.finished()) {
        int count = inflater.inflate(buffer);
        if (count == 0) {
          if (inflater.finished()) {
            break;
          }
          throw invalidSnapshot("response snapshot compression stream is incomplete", null);
        }
        if (output.size() > MAXIMUM_PLAINTEXT_BYTES - count) {
          throw invalidSnapshot("response snapshot plaintext exceeds 1000000 bytes", null);
        }
        output.write(buffer, 0, count);
      }
      if (inflater.getRemaining() != 0) {
        throw invalidSnapshot("response snapshot contains trailing compressed data", null);
      }
      return output.toByteArray();
    } catch (DataFormatException exception) {
      throw invalidSnapshot("response snapshot compression stream is invalid", exception);
    } finally {
      Arrays.fill(buffer, (byte) 0);
      inflater.end();
    }
  }

  private static ResponseSnapshotException invalidSnapshot(String message, @Nullable Throwable cause) {
    return cause == null
        ? new ResponseSnapshotException(ResponseSnapshotException.Reason.SNAPSHOT_INVALID, message)
        : new ResponseSnapshotException(
            ResponseSnapshotException.Reason.SNAPSHOT_INVALID, message, cause);
  }

  @Override
  public void close() {
    Arrays.fill(currentKey, (byte) 0);
    if (previousKey != null) {
      Arrays.fill(previousKey, (byte) 0);
    }
    closed = true;
  }

  private void ensureOpen() {
    if (closed) {
      throw new IllegalStateException("response snapshot codec is closed");
    }
  }

  private static String validateVersion(String version, String name) {
    Objects.requireNonNull(version, name);
    if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException(name + " is invalid");
    }
    return version;
  }

  private static byte[] validateKey(byte[] key, String name) {
    Objects.requireNonNull(key, name);
    if (key.length != AES_KEY_BYTES) {
      throw new IllegalArgumentException(name + " must contain exactly 256 bits");
    }
    return key.clone();
  }
}
