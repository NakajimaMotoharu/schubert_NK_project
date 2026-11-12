package dev.codex.schubert.nk.web.session;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.ProviderException;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Objects;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.jspecify.annotations.Nullable;

/**
 * Session-only NKENC1 AES-256-GCM with closed JSON and row-bound AAD. NK-WEB-001/NK-AUT-001;
 * FUN-001/AUT-001..004; UI226/242; SS314 §7.2.2/331 §9.1/352 §11.2;
 * SSC-039/PG-D-095/PT-WEB-016..023. Owns key copies; no DB, HTTP or authorization decisions.
 */
public final class SessionPayloadCodec implements AutoCloseable {
  private static final int AES_KEY_BYTES = 32;
  private static final int ENVELOPE_FORMAT_VERSION = 1;

  private static final byte[] MAGIC = "NKENC1".getBytes(StandardCharsets.US_ASCII);
  private final java.util.concurrent.locks.ReentrantLock stateLock =
      new java.util.concurrent.locks.ReentrantLock();
  private final String currentVersion;
  private final byte[] currentKey;
  private final @Nullable String previousVersion;
  private final byte @Nullable [] previousKey;
  private final SecureRandom random;
  private final SessionAttributeCodec json = new SessionAttributeCodec();
  private boolean closed;

  /** Current/previous IDs distinct; 32-byte keys paired with IDs, otherwise fail before copying. */
  public SessionPayloadCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey) {
    this(currentVersion, currentKey, previousVersion, previousKey, new SecureRandom());
  }

  SessionPayloadCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey,
      SecureRandom random) {
    this.currentVersion = EncryptedSessionPayload.validateVersion(currentVersion);
    validateKey(currentKey);
    if ((previousVersion == null) != (previousKey == null))
      throw new IllegalArgumentException("previous session key and version must be paired");
    if (previousVersion != null) EncryptedSessionPayload.validateVersion(previousVersion);
    if (previousKey != null) validateKey(previousKey);
    if (currentVersion.equals(previousVersion))
      throw new IllegalArgumentException("session key versions must be distinct");
    this.random = Objects.requireNonNull(random, "random");
    this.currentKey = currentKey.clone();
    this.previousVersion = previousVersion;
    this.previousKey = previousKey == null ? null : previousKey.clone();
  }

  /** Nonnull arguments. Writes current key with a new nonce; all owned transient arrays erased. */
  public EncryptedSessionPayload encrypt(
      SessionPayloadIdentity identity, SessionAttributes attributes) {
    stateLock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "identity");
      Objects.requireNonNull(attributes, "attributes");
      byte[] plaintext = json.encode(attributes);
      byte[] nonce = new byte[12];
      byte[] aad = identity.aad(currentVersion);
      byte[] encrypted = new byte[0];
      byte[] envelope = new byte[0];
      try {
        random.nextBytes(nonce);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
            Cipher.ENCRYPT_MODE,
            new SecretKeySpec(currentKey, "AES"),
            new GCMParameterSpec(128, nonce));
        cipher.updateAAD(aad);
        encrypted = cipher.doFinal(plaintext);
        byte[] version = currentVersion.getBytes(StandardCharsets.US_ASCII);
        envelope =
            ByteBuffer.allocate(8 + version.length + 12 + encrypted.length)
                .put(MAGIC)
                .put((byte) 1)
                .put((byte) version.length)
                .put(version)
                .put(nonce)
                .put(encrypted)
                .array();
        return new EncryptedSessionPayload(currentVersion, envelope);
      } catch (GeneralSecurityException | ProviderException failure) {
        SessionStoreException.preserveFatal(failure);
        throw new SessionPayloadException(SessionPayloadException.Reason.CRYPTO_UNAVAILABLE);
      } finally {
        Arrays.fill(plaintext, (byte) 0);
        Arrays.fill(nonce, (byte) 0);
        Arrays.fill(aad, (byte) 0);
        Arrays.fill(encrypted, (byte) 0);
        Arrays.fill(envelope, (byte) 0);
      }
    } finally {
      stateLock.unlock();
    }
  }

  /**
   * Nonnull arguments. Authenticates envelope/AAD before schema validation and releasing values.
   */
  public SessionAttributes decrypt(
      SessionPayloadIdentity identity, EncryptedSessionPayload payload) {
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
        if (stored.length < 37 || !Arrays.equals(stored, 0, 6, MAGIC, 0, 6)) throw invalid();
        if (stored[6] != ENVELOPE_FORMAT_VERSION) throw invalid();
        int keyLength = Byte.toUnsignedInt(stored[7]);
        int nonceOffset = 8 + keyLength;
        int cipherOffset = nonceOffset + 12;
        if (keyLength < 1 || keyLength > 16 || stored.length < cipherOffset + 16) throw invalid();
        String version = new String(stored, 8, keyLength, StandardCharsets.US_ASCII);
        if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")
            || !payload.keyVersion().equals(version)) throw invalid();
        byte[] key = selectKey(version);
        nonce = Arrays.copyOfRange(stored, nonceOffset, cipherOffset);
        aad = identity.aad(version);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
            Cipher.DECRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
        cipher.updateAAD(aad);
        plaintext = cipher.doFinal(stored, cipherOffset, stored.length - cipherOffset);
        return json.decode(plaintext);
      } catch (GeneralSecurityException | ProviderException | SessionAttributeException failure) {
        SessionStoreException.preserveFatal(failure);
        throw invalid();
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

  private byte[] selectKey(String version) {
    if (currentVersion.equals(version)) return currentKey;
    if (previousVersion != null && previousVersion.equals(version))
      return Objects.requireNonNull(previousKey, "paired previous key");
    throw new SessionPayloadException(SessionPayloadException.Reason.KEY_UNAVAILABLE);
  }

  private static void validateKey(byte[] key) {
    Objects.requireNonNull(key, "key");
    if (key.length != AES_KEY_BYTES)
      throw new IllegalArgumentException("session key must contain 256 bits");
  }

  private static SessionPayloadException invalid() {
    return new SessionPayloadException(SessionPayloadException.Reason.PAYLOAD_INVALID);
  }

  private void ensureOpen() {
    if (closed) throw new IllegalStateException("session payload codec is closed");
  }

  /** Erases owned key copies after in-flight operations finish; repeated close is harmless. */
  @Override
  public void close() {
    stateLock.lock();
    try {
      Arrays.fill(currentKey, (byte) 0);
      if (previousKey != null) Arrays.fill(previousKey, (byte) 0);
      closed = true;
    } finally {
      stateLock.unlock();
    }
  }
}
