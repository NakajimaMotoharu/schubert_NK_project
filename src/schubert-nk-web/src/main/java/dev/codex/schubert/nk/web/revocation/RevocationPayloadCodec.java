package dev.codex.schubert.nk.web.revocation;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.web.session.SessionStoreException;
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
 * Purpose-separated NKENC1 AES-256-GCM, closed 64-byte context. No authorization or expiry proof.
 * NK-WEB-002/AUT004/UI226234/SS314331352/QA050/SSC171/PG-D359/RERUN003. Owns key copies. Outer
 * owner must retain required previous keys while rows/borrowers exist.
 */
public final class RevocationPayloadCodec implements AutoCloseable {
  private static final int AES_KEY_BYTES = 32;
  private static final int ENVELOPE_FORMAT_VERSION = 1;

  private static final byte[] MAGIC = "NKENC1".getBytes(StandardCharsets.US_ASCII);
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final String currentVersion;
  private final byte[] currentKey;
  private final @Nullable String previousVersion;
  private final byte @Nullable [] previousKey;
  private final SecureRandom random;
  private boolean closed;

  public RevocationPayloadCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey) {
    this(currentVersion, currentKey, previousVersion, previousKey, new SecureRandom());
  }

  RevocationPayloadCodec(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey,
      SecureRandom random) {
    this.currentVersion = EncryptedRevocationPayload.validateVersion(currentVersion);
    validateKey(currentKey);
    if ((previousVersion == null) != (previousKey == null))
      throw new IllegalArgumentException("previous revocation key and version must be paired");
    if (previousVersion != null) EncryptedRevocationPayload.validateVersion(previousVersion);
    if (previousKey != null) validateKey(previousKey);
    if (currentVersion.equals(previousVersion))
      throw new IllegalArgumentException("revocation key versions must be distinct");
    this.random = Objects.requireNonNull(random, "revocation random");
    this.currentKey = currentKey.clone();
    this.previousVersion = previousVersion;
    this.previousKey = previousKey == null ? null : previousKey.clone();
  }

  public EncryptedRevocationPayload encrypt(
      RevocationPayloadIdentity identity, AuthenticationContext context) {
    lock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "revocation identity");
      Objects.requireNonNull(context, "revocation context");
      // SSC420/BUG3018: all owned secret acquisition takes place inside cleanup protection.
      byte[] plaintext = new byte[0];
      byte[] nonce = new byte[0];
      byte[] aad = new byte[0];
      byte[] encrypted = new byte[0];
      byte[] envelope = new byte[0];
      try {
        plaintext = context.wireValue().getBytes(StandardCharsets.US_ASCII);
        nonce = new byte[12];
        aad = identity.aad(currentVersion);
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
        return new EncryptedRevocationPayload(currentVersion, envelope);
      } catch (GeneralSecurityException | ProviderException failure) {
        SessionStoreException.preserveFatal(failure);
        throw new RevocationPayloadException(RevocationPayloadException.Reason.CRYPTO_UNAVAILABLE);
      } finally {
        Arrays.fill(plaintext, (byte) 0);
        Arrays.fill(nonce, (byte) 0);
        Arrays.fill(aad, (byte) 0);
        Arrays.fill(encrypted, (byte) 0);
        Arrays.fill(envelope, (byte) 0);
      }
    } finally {
      lock.unlock();
    }
  }

  public AuthenticationContext decrypt(
      RevocationPayloadIdentity identity, EncryptedRevocationPayload payload) {
    lock.lock();
    try {
      ensureOpen();
      Objects.requireNonNull(identity, "revocation identity");
      Objects.requireNonNull(payload, "revocation payload");
      byte[] stored = payload.ciphertext();
      byte[] nonce = new byte[0];
      byte[] aad = new byte[0];
      byte[] plaintext = new byte[0];
      try {
        if (stored.length < 101 || !Arrays.equals(stored, 0, 6, MAGIC, 0, 6)) throw invalid();
        if (stored[6] != ENVELOPE_FORMAT_VERSION) throw invalid();
        int length = Byte.toUnsignedInt(stored[7]);
        if (length < 1 || length > 16 || stored.length != 8 + length + 12 + 64 + 16)
          throw invalid();
        String version = new String(stored, 8, length, StandardCharsets.US_ASCII);
        if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")
            || !version.equals(payload.keyVersion())) throw invalid();
        byte[] key = selectKey(version);
        nonce = Arrays.copyOfRange(stored, 8 + length, 8 + length + 12);
        aad = identity.aad(version);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(
            Cipher.DECRYPT_MODE, new SecretKeySpec(key, "AES"), new GCMParameterSpec(128, nonce));
        cipher.updateAAD(aad);
        plaintext = cipher.doFinal(stored, 8 + length + 12, 80);
        return AuthenticationContext.of(new String(plaintext, StandardCharsets.US_ASCII));
      } catch (GeneralSecurityException | ProviderException | IllegalArgumentException failure) {
        SessionStoreException.preserveFatal(failure);
        throw invalid();
      } finally {
        Arrays.fill(stored, (byte) 0);
        Arrays.fill(nonce, (byte) 0);
        Arrays.fill(aad, (byte) 0);
        Arrays.fill(plaintext, (byte) 0);
      }
    } finally {
      lock.unlock();
    }
  }

  private byte[] selectKey(String version) {
    if (version.equals(currentVersion)) return currentKey;
    if (version.equals(previousVersion))
      return Objects.requireNonNull(previousKey, "paired previous revocation key");
    throw new RevocationPayloadException(RevocationPayloadException.Reason.KEY_UNAVAILABLE);
  }

  private static void validateKey(byte[] key) {
    Objects.requireNonNull(key, "revocation key");
    if (key.length != AES_KEY_BYTES)
      throw new IllegalArgumentException("revocation key must contain 256 bits");
  }

  private static RevocationPayloadException invalid() {
    return new RevocationPayloadException(RevocationPayloadException.Reason.PAYLOAD_INVALID);
  }

  private void ensureOpen() {
    if (closed) throw new IllegalStateException("revocation payload codec is closed");
  }

  @Override
  public void close() {
    lock.lock();
    try {
      Arrays.fill(currentKey, (byte) 0);
      if (previousKey != null) Arrays.fill(previousKey, (byte) 0);
      closed = true;
    } finally {
      lock.unlock();
    }
  }
}
