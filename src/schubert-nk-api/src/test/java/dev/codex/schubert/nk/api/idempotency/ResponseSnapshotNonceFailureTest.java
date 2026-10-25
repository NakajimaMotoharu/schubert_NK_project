package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS324/352; PG-D674; BUG1771/YKT1522; public synthetic buffers, never actual credentials. */
class ResponseSnapshotNonceFailureTest {
  private static final int SYNTHETIC_KEY_BYTES = 32;
  private static final int NONCE_BYTES = 12;

  @Test
  void rngscope001RuntimeFailureClearsOwnedNonceAndPreservesIdentity() {
    assertFailure(new IllegalStateException("synthetic RNG failure"));
  }

  @Test
  void rngscope002ErrorClearsOwnedNonceAndPreservesIdentity() {
    assertFailure(new AssertionError("synthetic RNG failure"));
  }

  private static void assertFailure(Throwable marker) {
    byte[] key = new byte[SYNTHETIC_KEY_BYTES];
    byte[] plaintext = "public synthetic buffer scope".getBytes(StandardCharsets.US_ASCII);
    byte[] original = plaintext.clone();
    var random = new FailingRandom(marker);
    var identity = ResponseSnapshotIdentity.authenticated(new UUID(0, 1), "QSSRSP01", "001", 1);
    try (var codec = new ResponseSnapshotCodec("test-v1", key, null, null, random)) {
      Throwable actual = assertThrows(marker.getClass(), () -> codec.encrypt(identity, plaintext));
      assertSame(marker, actual);
      assertEquals(1, random.calls);
      assertEquals(NONCE_BYTES, random.captured.length);
      assertArrayEquals(new byte[NONCE_BYTES], random.captured);
      assertArrayEquals(original, plaintext);
      assertArrayEquals(new byte[SYNTHETIC_KEY_BYTES], key);
    }
  }

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
}
