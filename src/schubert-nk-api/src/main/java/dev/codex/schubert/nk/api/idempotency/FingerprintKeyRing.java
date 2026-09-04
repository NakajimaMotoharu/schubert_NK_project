package dev.codex.schubert.nk.api.idempotency;

import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;

/** Current/previous fingerprint keys with deny-closed version selection. */
public final class FingerprintKeyRing implements AutoCloseable {
  private final String currentVersion;
  private final byte[] currentKey;
  private final @Nullable String previousVersion;
  private final byte @Nullable [] previousKey;
  private boolean closed;

  public FingerprintKeyRing(
      String currentVersion,
      byte[] currentKey,
      @Nullable String previousVersion,
      byte @Nullable [] previousKey) {
    this.currentVersion = validateVersion(currentVersion, "currentVersion");
    this.currentKey = validateKey(currentKey, "currentKey");
    if ((previousVersion == null) != (previousKey == null)) {
      throw new IllegalArgumentException("previous fingerprint key version and key must be paired");
    }
    this.previousVersion =
        previousVersion == null ? null : validateVersion(previousVersion, "previousVersion");
    this.previousKey = previousKey == null ? null : validateKey(previousKey, "previousKey");
    if (this.currentVersion.equals(this.previousVersion)) {
      throw new IllegalArgumentException("fingerprint key versions must be distinct");
    }
  }

  public Fingerprint calculate(CanonicalRequest request) {
    ensureOpen();
    return new Fingerprint(
        currentVersion, OperationFingerprint.INSTANCE.calculate(request, currentKey));
  }

  public boolean matches(Fingerprint stored, CanonicalRequest request) {
    return verify(stored, request) == FingerprintVerification.MATCH;
  }

  public FingerprintVerification verify(Fingerprint stored, CanonicalRequest request) {
    ensureOpen();
    Objects.requireNonNull(stored, "stored");
    Objects.requireNonNull(request, "request");
    Optional<byte[]> selected = select(stored.keyVersion());
    if (selected.isEmpty()) {
      return FingerprintVerification.KEY_UNAVAILABLE;
    }
    byte[] actual = OperationFingerprint.INSTANCE.calculate(request, selected.orElseThrow());
    try {
      return MessageDigest.isEqual(stored.digest(), actual)
          ? FingerprintVerification.MATCH
          : FingerprintVerification.MISMATCH;
    } finally {
      Arrays.fill(actual, (byte) 0);
    }
  }

  private Optional<byte[]> select(String version) {
    if (currentVersion.equals(version)) {
      return Optional.of(currentKey);
    }
    if (previousVersion != null && previousVersion.equals(version)) {
      return Optional.of(previousKey);
    }
    return Optional.empty();
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
      throw new IllegalStateException("fingerprint key ring is closed");
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
    if (key.length < 32) {
      throw new IllegalArgumentException(name + " must contain at least 256 bits");
    }
    return key.clone();
  }
}
