package dev.codex.schubert.nk.api.maintenance;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Base64;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Owned, destroyable private-inspector AES material. File/ACL admission is a separate mandatory
 * boundary. NK-DAT-001; DAT-009/OPS-009; UI212/241/251; SS343 6.1/324 12/352;
 * QA-046/SSC-049/PG-D-131; PT-DB-INBOX-105..112.
 */
@NullMarked
public final class InspectorAesCredential implements AutoCloseable {
  private static final byte[] MAGIC = "NKKEY1\n".getBytes(StandardCharsets.US_ASCII);
  private final Object stateLock = new Object();
  private final String version;
  private final byte[] key;
  private boolean closed;

  private InspectorAesCredential(String version, byte[] ownedKey) {
    this.version = version;
    this.key = ownedKey;
  }

  /**
   * Transfers exclusive ownership: input is cleared on both success and failure. Caller must not
   * retain/use aliases concurrently. Never creates a String containing encoded or decoded key.
   */
  public static InspectorAesCredential consume(byte[] input) {
    Objects.requireNonNull(input, "credential input");
    byte[] encoded = new byte[0];
    byte @Nullable [] decoded = null;
    try {
      if (input.length < 54 || input.length > 69 || !Arrays.equals(input, 0, 7, MAGIC, 0, 7))
        throw invalid();
      int versionLength = input.length - 53;
      if (input[7 + versionLength] != '\n' || input[input.length - 1] != '\n') throw invalid();
      String version = new String(input, 7, versionLength, StandardCharsets.US_ASCII);
      if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}")) throw invalid();
      encoded = Arrays.copyOfRange(input, 8 + versionLength, input.length - 1);
      decoded = Base64.getDecoder().decode(encoded);
      if (decoded.length != 32) throw invalid();
      byte[] canonical = Base64.getEncoder().encode(decoded);
      try {
        if (!Arrays.equals(encoded, canonical)) throw invalid();
      } finally {
        Arrays.fill(canonical, (byte) 0);
      }
      var result = new InspectorAesCredential(version, decoded);
      decoded = null; // ownership moved, not a second live reference retained by this method
      return result;
    } catch (IllegalArgumentException failure) {
      throw invalid(); // never retain decoder detail, input, cause or suppressed exceptions
    } finally {
      Arrays.fill(input, (byte) 0);
      Arrays.fill(encoded, (byte) 0);
      if (decoded != null) Arrays.fill(decoded, (byte) 0);
    }
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("inspector AES credential format is invalid");
  }

  /** Version is non-secret metadata, available after destruction as well. */
  public String version() {
    return version;
  }

  /** Caller owns and must clear this copy after initializing the existing cipher codec. */
  public byte[] copyKey() {
    synchronized (stateLock) {
      if (closed) throw new IllegalStateException("inspector AES credential is closed");
      return key.clone();
    }
  }

  @Override
  public void close() {
    synchronized (stateLock) {
      if (!closed) {
        Arrays.fill(key, (byte) 0);
        closed = true;
      }
    }
  }

  @Override
  public String toString() {
    synchronized (stateLock) {
      return "InspectorAesCredential[version="
          + version
          + ", key=<redacted>, closed="
          + closed
          + "]";
    }
  }
}
