package dev.codex.schubert.nk.web.logging;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.jspecify.annotations.Nullable;

/**
 * Web-only NKENC1 AES-256-GCM storage of one complete, validated WLGEVT01 message.
 *
 * <p>Trace: NK-MSG-002; RD MON-003; UI 233/235 §12/242; SS 324 §9, 352 §11.2; PT-IDEM-012/015. The
 * dispatcher decrypts before sending the 2336-byte fixed-length message. Operations and close
 * serialize key/nonce access; caller arrays are never retained or erased.
 */
public final class WebLogPayloadCodec implements AutoCloseable {
  private static final int AES_KEY_BYTES = 32;
  private static final int ENVELOPE_FORMAT_VERSION = 1;

  public static final int PLAINTEXT_BYTES = 2_336;
  private static final byte[] MAGIC = "NKENC1".getBytes(StandardCharsets.US_ASCII);
  private static final int NONCE_BYTES = 12;
  private static final int TAG_BYTES = 16;
  private static final int PREFIX_BYTES = 8;
  private static final int MINIMUM_ENVELOPE_BYTES = 37;

  // BUG-036/YKT-032: callers must not own the key/nonce/close synchronization monitor.
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final String currentVersion;
  private final @Nullable String previousVersion;
  private final byte[] ownedKeys;
  private final SecureRandom random;
  private boolean closed;

  /**
   * Configures current writes and optional previous reads; keys must be 32 bytes and IDs distinct.
   */
  public WebLogPayloadCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey) {
    this(currentVersion, currentKey, previousVersion, previousKey, new SecureRandom());
  }

  WebLogPayloadCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey,
      SecureRandom random) {
    this.currentVersion = requireVersion(currentVersion);
    requireKey(currentKey);
    if ((previousVersion == null) != (previousKey == null)) {
      throw new IllegalArgumentException("previous web log key and version must be paired");
    }
    this.previousVersion = previousVersion == null ? null : requireVersion(previousVersion);
    if (previousKey != null) {
      requireKey(previousKey);
    }
    if (this.currentVersion.equals(this.previousVersion)) {
      throw new IllegalArgumentException("web log key versions must be distinct");
    }
    this.random = Objects.requireNonNull(random, "random");
    // Allocate once before copying material. Each source and destination range is fixed at 32
    // bytes.
    this.ownedKeys = new byte[previousKey == null ? AES_KEY_BYTES : 2 * AES_KEY_BYTES];
    System.arraycopy(currentKey, 0, ownedKeys, 0, AES_KEY_BYTES);
    if (previousKey != null) {
      System.arraycopy(previousKey, 0, ownedKeys, AES_KEY_BYTES, AES_KEY_BYTES);
    }
  }

  /** Validates identity and wire content, then encrypts with the current key and a new nonce. */
  public EncryptedWebLogPayload encrypt(WebLogPayloadIdentity identity, byte[] plaintext) {
    stateLock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "identity");
      Objects.requireNonNull(plaintext, "plaintext");
      // SSC420/BUG3018: allocate no owned plaintext before the cleanup region starts.
      byte[] candidate = new byte[0];
      byte[] nonce = new byte[0];
      byte[] aad = new byte[0];
      byte[] encrypted = new byte[0];
      byte[] stored = new byte[0];
      try {
        candidate = plaintext.clone();
        nonce = new byte[NONCE_BYTES];
        aad = identity.aad(currentVersion);
        validatePlaintext(identity, candidate);
        random.nextBytes(nonce);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
            Cipher.ENCRYPT_MODE,
            new SecretKeySpec(ownedKeys, 0, AES_KEY_BYTES, "AES"),
            new GCMParameterSpec(TAG_BYTES * Byte.SIZE, nonce));
        cipher.updateAAD(aad);
        encrypted = cipher.doFinal(candidate);
        byte[] keyId = currentVersion.getBytes(StandardCharsets.US_ASCII);
        stored =
            ByteBuffer.allocate(PREFIX_BYTES + keyId.length + NONCE_BYTES + encrypted.length)
                .put(MAGIC)
                .put((byte) 1)
                .put((byte) keyId.length)
                .put(keyId)
                .put(nonce)
                .put(encrypted)
                .array();
        return new EncryptedWebLogPayload(currentVersion, stored);
      } catch (GeneralSecurityException exception) {
        throw new WebLogPayloadException(WebLogPayloadException.Reason.CRYPTO_UNAVAILABLE);
      } finally {
        Arrays.fill(candidate, (byte) 0);
        Arrays.fill(nonce, (byte) 0);
        Arrays.fill(aad, (byte) 0);
        Arrays.fill(encrypted, (byte) 0);
        Arrays.fill(stored, (byte) 0);
      }
    } finally {
      stateLock.unlock();
    }
  }

  /** Authenticates envelope/row identity before releasing an exact, validated WLGEVT01 copy. */
  public byte[] decrypt(WebLogPayloadIdentity identity, EncryptedWebLogPayload payload) {
    stateLock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "identity");
      Objects.requireNonNull(payload, "payload");
      byte[] stored = payload.ciphertext();
      byte[] nonce = new byte[0];
      byte[] aad = new byte[0];
      byte[] plaintext = new byte[0];
      try {
        if (stored.length < MINIMUM_ENVELOPE_BYTES
            || !Arrays.equals(stored, 0, MAGIC.length, MAGIC, 0, MAGIC.length)) {
          throw invalidPayload();
        }
        if (stored[6] != ENVELOPE_FORMAT_VERSION) {
          throw invalidPayload();
        }
        int keyLength = Byte.toUnsignedInt(stored[7]);
        int nonceOffset = PREFIX_BYTES + keyLength;
        int cipherOffset = nonceOffset + NONCE_BYTES;
        if (keyLength < 1 || keyLength > 16 || stored.length < cipherOffset + TAG_BYTES) {
          throw invalidPayload();
        }
        String version = new String(stored, PREFIX_BYTES, keyLength, StandardCharsets.US_ASCII);
        if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")
            || !payload.keyVersion().equals(version)) {
          throw invalidPayload();
        }
        int keyOffset = selectKeyOffset(version);
        nonce = Arrays.copyOfRange(stored, nonceOffset, cipherOffset);
        aad = identity.aad(version);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
            Cipher.DECRYPT_MODE,
            new SecretKeySpec(ownedKeys, keyOffset, AES_KEY_BYTES, "AES"),
            new GCMParameterSpec(TAG_BYTES * Byte.SIZE, nonce));
        cipher.updateAAD(aad);
        plaintext = cipher.doFinal(stored, cipherOffset, stored.length - cipherOffset);
        validatePlaintext(identity, plaintext);
        return plaintext.clone();
      } catch (GeneralSecurityException exception) {
        throw invalidPayload();
      } finally {
        Arrays.fill(stored, (byte) 0);
        Arrays.fill(nonce, (byte) 0);
        Arrays.fill(aad, (byte) 0);
        Arrays.fill(plaintext, (byte) 0);
      }
    } finally {
      stateLock.unlock();
    }
  }

  private int selectKeyOffset(String version) {
    if (currentVersion.equals(version)) {
      return 0;
    }
    if (previousVersion != null && previousVersion.equals(version)) {
      // BUG-016/YKT-013: the constructor accepts this version only with the second 32-byte key.
      return AES_KEY_BYTES;
    }
    throw new WebLogPayloadException(WebLogPayloadException.Reason.KEY_UNAVAILABLE);
  }

  private static void validatePlaintext(WebLogPayloadIdentity identity, byte[] plaintext) {
    if (plaintext.length != PLAINTEXT_BYTES) {
      throw invalidPayload();
    }
    try {
      CommonHeader header = HeaderCodec.standard().peek(plaintext);
      if (!header.layoutId().value().equals("WLGEVT01")
          || !header.messageId().equals(identity.messageId())
          || !header.correlationId().equals(identity.correlationId())) {
        throw invalidPayload();
      }
      PayloadTypeCatalog.decode(
          PayloadCodec.standard()
              .decode(
                  header.layoutId(),
                  Arrays.copyOfRange(plaintext, 256, PLAINTEXT_BYTES),
                  List.of(),
                  false));
    } catch (PermanentProtocolException | LayoutValidationException exception) {
      throw invalidPayload();
    }
  }

  private static WebLogPayloadException invalidPayload() {
    return new WebLogPayloadException(WebLogPayloadException.Reason.PAYLOAD_INVALID);
  }

  private static String requireVersion(String version) {
    Objects.requireNonNull(version, "version");
    if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) {
      throw new IllegalArgumentException("web log key version is invalid");
    }
    return version;
  }

  private static void requireKey(byte[] key) {
    Objects.requireNonNull(key, "key");
    if (key.length != AES_KEY_BYTES) {
      throw new IllegalArgumentException("web log key must contain exactly 256 bits");
    }
  }

  private void ensureOpen() {
    if (closed) {
      throw new IllegalStateException("web log payload codec is closed");
    }
  }

  /** Erases owned key copies; repeated close is safe and all later operations fail closed. */
  @Override
  public void close() {
    stateLock.lock();
    try {
      Arrays.fill(ownedKeys, (byte) 0);
      closed = true;
    } finally {
      stateLock.unlock();
    }
  }
}
