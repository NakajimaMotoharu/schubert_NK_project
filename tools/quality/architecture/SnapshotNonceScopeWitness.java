package dev.codex.schubert.nk.api.idempotency;

import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.UUID;

/** Old-source witness: public synthetic buffers only, no real keys, service, DB or reflection. */
public final class SnapshotNonceScopeWitness {
  private SnapshotNonceScopeWitness() {}

  private static final class FailingRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;
    private final Throwable marker;
    private byte[] captured = new byte[0];
    private int calls;

    private FailingRandom(Throwable marker) {
      this.marker = marker;
    }

    @Override
    public void nextBytes(byte[] bytes) {
      captured = bytes;
      calls++;
      Arrays.fill(bytes, (byte) 0x55);
      if (marker instanceof RuntimeException failure) throw failure;
      throw (Error) marker;
    }
  }

  private static boolean run(String kind, Throwable marker) {
    byte[] key = new byte[32]; // Public all-zero test fixture, not an actual credential.
    byte[] plain = "public synthetic buffer scope".getBytes(StandardCharsets.US_ASCII);
    byte[] before = plain.clone();
    var random = new FailingRandom(marker);
    var identity = ResponseSnapshotIdentity.authenticated(new UUID(0, 1), "QSSRSP01", "001", 1);
    boolean same = false;
    try (var codec = new ResponseSnapshotCodec("test-v1", key, null, null, random)) {
      try {
        codec.encrypt(identity, plain);
      } catch (RuntimeException | Error actual) {
        same = actual == marker;
      }
    }
    boolean caller = Arrays.equals(plain, before) && Arrays.equals(key, new byte[32]);
    boolean initialized = random.calls == 1 && random.captured.length == 12;
    boolean cleared = initialized && Arrays.equals(random.captured, new byte[12]);
    System.out.println(
        "CASE\t"
            + kind
            + "\tPRIMARY="
            + same
            + "\tINITIALIZED="
            + initialized
            + "\tNONCE_CLEAR="
            + cleared
            + "\tCALLER="
            + caller);
    if (!same || !caller || !initialized)
      throw new AssertionError("independent witness setup failed");
    return cleared;
  }

  public static void main(String[] args) {
    if (args.length != 0) throw new IllegalArgumentException("no external inputs");
    boolean runtime = run("RUNTIME", new IllegalStateException("synthetic RNG failure"));
    boolean error = run("ERROR", new AssertionError("synthetic RNG failure"));
    if (!runtime && !error) System.exit(1);
    if (!runtime || !error) System.exit(2);
  }
}
