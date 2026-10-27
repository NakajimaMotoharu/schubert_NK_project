package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SSC104/SS341/342/343: independent fixed ASCII vectors, not deletion authority. */
final class CleanupWorkerRequestTest {
  private static final String RUN_UUID_TEXT = "31100027-2222-4333-8444-555555555555";
  private static final String CUTOFF_TEXT = "2026-09-27T15:00:00Z";

  private static final UUID RUN = UUID.fromString(RUN_UUID_TEXT);
  private static final UUID ACTIVATION = UUID.fromString("31100027-6666-4777-8888-999999999999");
  private static final Instant CUTOFF = Instant.parse(CUTOFF_TEXT);
  private static final String DIGEST = "0123456789abcdef".repeat(4);
  private static final String GOLDEN =
      "NKCLEAN1\n"
          + "run=31100027-2222-4333-8444-555555555555\n"
          + "activation=31100027-6666-4777-8888-999999999999\n"
          + "cutoff=2026-09-27T15:00:00Z\n"
          + "manifest=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n";

  private static void invalid(String text) {
    byte[] owned = text.getBytes(StandardCharsets.US_ASCII);
    assertEquals(
        "cleanup request invalid",
        assertThrows(IllegalArgumentException.class, () -> CleanupWorkerRequest.consume(owned))
            .getMessage());
    assertArrayEquals(new byte[owned.length], owned);
  }

  @Test
  void creq001IndependentCanonicalByteVectorAndConsumedZeroing() {
    var request = new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, DIGEST);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), request.encode());
    byte[] owned = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    assertEquals(request, CleanupWorkerRequest.consume(owned));
    assertArrayEquals(new byte[owned.length], owned);
    assertEquals(RUN, request.run());
    assertEquals(ACTIVATION, request.activation());
    assertEquals(CUTOFF, request.cutoff());
    assertEquals(DIGEST, request.manifestSha256());
    assertEquals(
        request.hashCode(), new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, DIGEST).hashCode());
    assertNotEquals(request, new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, "a".repeat(64)));
  }

  @Test
  void creq002ConstructorNullNilDistinctCutoffAndDigestContract() {
    assertThrows(
        NullPointerException.class,
        () -> new CleanupWorkerRequest(null, ACTIVATION, CUTOFF, DIGEST));
    assertThrows(
        NullPointerException.class, () -> new CleanupWorkerRequest(RUN, null, CUTOFF, DIGEST));
    assertThrows(
        NullPointerException.class, () -> new CleanupWorkerRequest(RUN, ACTIVATION, null, DIGEST));
    assertThrows(
        NullPointerException.class, () -> new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupWorkerRequest(new UUID(0, 0), ACTIVATION, CUTOFF, DIGEST));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupWorkerRequest(RUN, new UUID(0, 0), CUTOFF, DIGEST));
    assertThrows(
        IllegalArgumentException.class, () -> new CleanupWorkerRequest(RUN, RUN, CUTOFF, DIGEST));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupWorkerRequest(
                RUN, ACTIVATION, Instant.parse("0000-12-31T23:59:59Z"), DIGEST));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupWorkerRequest(
                RUN, ACTIVATION, Instant.parse("9999-12-31T23:59:59.999999999Z"), DIGEST));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF.plusNanos(1), DIGEST));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, "a".repeat(63)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, "A".repeat(64)));
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, "g".repeat(64)));
    assertDoesNotThrow(
        () ->
            new CleanupWorkerRequest(
                RUN, ACTIVATION, Instant.parse("0001-01-01T00:00:00Z"), DIGEST));
    assertDoesNotThrow(
        () ->
            new CleanupWorkerRequest(
                RUN, ACTIVATION, Instant.parse("9999-12-31T23:59:59.999999Z"), DIGEST));
  }

  @Test
  void creq003LengthAsciiControlAndNullInput() {
    assertThrows(NullPointerException.class, () -> CleanupWorkerRequest.consume(null));
    byte[] empty = new byte[0];
    assertThrows(IllegalArgumentException.class, () -> CleanupWorkerRequest.consume(empty));
    byte[] tooLong = new byte[CleanupWorkerRequest.MAXIMUM_BYTES + 1];
    Arrays.fill(tooLong, (byte) 'a');
    assertThrows(IllegalArgumentException.class, () -> CleanupWorkerRequest.consume(tooLong));
    assertArrayEquals(new byte[tooLong.length], tooLong);
    for (byte bad : new byte[] {0, 13, 127, (byte) 0x80}) {
      byte[] owned = GOLDEN.getBytes(StandardCharsets.US_ASCII);
      owned[1] = bad;
      assertThrows(IllegalArgumentException.class, () -> CleanupWorkerRequest.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
    }
  }

  @Test
  void creq004FramingUnknownMissingDuplicateOrderAndSuffixRefused() {
    invalid(GOLDEN.replace("NKCLEAN1", "NKCLEAN2"));
    invalid(GOLDEN.replace("run=", "id="));
    invalid(GOLDEN.replace("activation=", "run="));
    invalid(GOLDEN.replace("cutoff=", "when="));
    invalid(GOLDEN.replace("manifest=", "hash="));
    invalid(GOLDEN.substring(0, GOLDEN.length() - 1));
    invalid(GOLDEN + "trailing");
    invalid(GOLDEN + "extra=1\n");
    invalid(GOLDEN.replace("run=311", "run=311\n"));
  }

  @Test
  void creq005NoncanonicalAndSemanticallyInvalidValuesRefused() {
    invalid(GOLDEN.replace(RUN_UUID_TEXT, "not-a-uuid"));
    invalid(GOLDEN.replace("31100027-6666-4777-8888-999999999999", "not-a-uuid"));
    invalid(GOLDEN.replace(RUN_UUID_TEXT, "00000000-0000-0000-0000-000000000000"));
    invalid(
        GOLDEN.replace(
            "activation=31100027-6666-4777-8888-999999999999",
            "activation=31100027-2222-4333-8444-555555555555"));
    invalid(GOLDEN.replace(CUTOFF_TEXT, "not-a-time"));
    invalid(GOLDEN.replace(CUTOFF_TEXT, "2026-09-27T15:00:00.000000001Z"));
    invalid(GOLDEN.replace(CUTOFF_TEXT, "2026-09-27T15:00:00+00:00"));
    invalid(GOLDEN.replace(DIGEST, DIGEST.toUpperCase(java.util.Locale.ROOT)));
    invalid(GOLDEN.replace(RUN_UUID_TEXT, "31100027-2222-4333-8444-55555555555A"));
  }

  @Test
  void creq006RedactedDiagnosticNeverContainsCorrelationValues() {
    var request = new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, DIGEST);
    String diagnostic = request.toString();
    assertEquals("CleanupWorkerRequest[identity/cutoff/manifest=<redacted>]", diagnostic);
    assertFalse(diagnostic.contains(RUN.toString()));
    assertFalse(diagnostic.contains(ACTIVATION.toString()));
    assertFalse(diagnostic.contains(DIGEST));
  }

  @Test
  void creq007ConcurrentIndependentBuffersAndParserLevelReplay() throws Exception {
    byte[] first = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    byte[] second = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    try (var workers = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
      var a = workers.submit(() -> CleanupWorkerRequest.consume(first));
      var b = workers.submit(() -> CleanupWorkerRequest.consume(second));
      assertEquals(new CleanupWorkerRequest(RUN, ACTIVATION, CUTOFF, DIGEST), a.get());
      assertEquals(a.get(), b.get());
    }
    assertArrayEquals(new byte[first.length], first);
    assertArrayEquals(new byte[second.length], second);
    // Decoding the same correlation value twice is not authorization to rerun Cleanup.
  }
}
