package dev.codex.schubert.nk.api.idempotency;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
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
 * <p>Trace: DAT-009, UI 241/242, SS 324 §6/§15, SS 352 §11.2 and PT-IDEM-007/008.
 */
public final class ResponseSnapshotCodec implements AutoCloseable {
  public static final int MAXIMUM_PLAINTEXT_BYTES = 1_000_000;
  private static final byte[] ENVELOPE_MAGIC = "NKENC1".getBytes(StandardCharsets.US_ASCII);
  private static final byte ENVELOPE_FORMAT_VERSION = 1;
  private static final int AES_KEY_BYTES = 32;
  private static final int NONCE_BYTES = 12;
  private static final int GCM_TAG_BYTES = 16;
  private static final int GCM_TAG_BITS = 128;
  private static final int ENVELOPE_FIXED_BYTES = ENVELOPE_MAGIC.length + 2 + NONCE_BYTES;
  private static final int MINIMUM_ENVELOPE_BYTES = ENVELOPE_FIXED_BYTES + 1 + GCM_TAG_BYTES;
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
    byte[] keyId = currentVersion.getBytes(StandardCharsets.US_ASCII);
    byte[] aad = identity.aad(ENVELOPE_FORMAT_VERSION, currentVersion);
    byte[] encrypted = null;
    byte[] stored = null;
    try {
      // The provider can fail before Cipher acquisition; owned buffers still need erasure.
      secureRandom.nextBytes(nonce);
      Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
      cipher.init(
          Cipher.ENCRYPT_MODE,
          new SecretKeySpec(currentKey, "AES"),
          new GCMParameterSpec(GCM_TAG_BITS, nonce));
      cipher.updateAAD(aad);
      encrypted = cipher.doFinal(compressed);
      stored =
          ByteBuffer.allocate(ENVELOPE_FIXED_BYTES + keyId.length + encrypted.length)
              .put(ENVELOPE_MAGIC)
              .put(ENVELOPE_FORMAT_VERSION)
              .put((byte) keyId.length)
              .put(keyId)
              .put(nonce)
              .put(encrypted)
              .array();
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
      if (encrypted != null) {
        Arrays.fill(encrypted, (byte) 0);
      }
      if (stored != null) {
        Arrays.fill(stored, (byte) 0);
      }
    }
  }

  public byte[] decrypt(ResponseSnapshotIdentity identity, EncryptedResponseSnapshot snapshot) {
    ensureOpen();
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(snapshot, "snapshot");
    byte[] stored = snapshot.ciphertext();
    byte[] nonce = null;
    byte[] encrypted = null;
    byte[] aad = null;
    byte[] compressed = null;
    try {
      if (stored.length < MINIMUM_ENVELOPE_BYTES
          || !Arrays.equals(
              stored, 0, ENVELOPE_MAGIC.length, ENVELOPE_MAGIC, 0, ENVELOPE_MAGIC.length)) {
        throw invalidSnapshot("response snapshot envelope is invalid", null);
      }
      if (stored[ENVELOPE_MAGIC.length] != ENVELOPE_FORMAT_VERSION) {
        throw invalidSnapshot("response snapshot format version is invalid", null);
      }
      int keyIdLength = Byte.toUnsignedInt(stored[ENVELOPE_MAGIC.length + 1]);
      int nonceOffset = ENVELOPE_MAGIC.length + 2 + keyIdLength;
      int encryptedOffset = nonceOffset + NONCE_BYTES;
      if (keyIdLength < 1 || keyIdLength > 16 || stored.length < encryptedOffset + GCM_TAG_BYTES) {
        throw invalidSnapshot("response snapshot envelope length is invalid", null);
      }
      String envelopeKeyVersion =
          new String(stored, ENVELOPE_MAGIC.length + 2, keyIdLength, StandardCharsets.US_ASCII);
      if (!envelopeKeyVersion.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")
          || !snapshot.keyVersion().equals(envelopeKeyVersion)) {
        throw invalidSnapshot("response snapshot key version is invalid", null);
      }
      byte[] key =
          selectKey(envelopeKeyVersion)
              .orElseThrow(
                  () ->
                      new ResponseSnapshotException(
                          ResponseSnapshotException.Reason.KEY_UNAVAILABLE,
                          "response snapshot key version is unavailable"));
      nonce = Arrays.copyOfRange(stored, nonceOffset, encryptedOffset);
      encrypted = Arrays.copyOfRange(stored, encryptedOffset, stored.length);
      aad = identity.aad(ENVELOPE_FORMAT_VERSION, envelopeKeyVersion);
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
      if (nonce != null) {
        Arrays.fill(nonce, (byte) 0);
      }
      if (encrypted != null) {
        Arrays.fill(encrypted, (byte) 0);
      }
      if (aad != null) {
        Arrays.fill(aad, (byte) 0);
      }
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
      // BUG-016/YKT-013: constructor establishes the version/key pair invariant.
      return Optional.of(Objects.requireNonNull(previousKey, "paired previous key"));
    }
    return Optional.empty();
  }

  private static byte[] compress(byte[] plaintext) {
    // BUG1453/PG-D434: scratch failure must precede native ownership; retain end() priority.
    byte[] buffer = new byte[BUFFER_BYTES];
    Deflater deflater = new Deflater(3);
    try (var output = new WipingByteArrayOutputStream()) {
      deflater.setInput(plaintext);
      deflater.finish();
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
    // PT-IDEM-SCRATCH002: no native Inflater exists if this allocation fails.
    byte[] buffer = new byte[BUFFER_BYTES];
    Inflater inflater = new Inflater();
    try (var output = new WipingByteArrayOutputStream()) {
      inflater.setInput(compressed);
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

  private static ResponseSnapshotException invalidSnapshot(
      String message, @Nullable Throwable cause) {
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
