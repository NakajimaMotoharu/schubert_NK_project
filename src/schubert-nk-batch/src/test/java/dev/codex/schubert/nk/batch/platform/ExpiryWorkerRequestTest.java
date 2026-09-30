package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.Test;

/** EREQ001..004 literal independent NKEXPIRY1 byte oracle, SSC111. No native authority claim. */
final class ExpiryWorkerRequestTest {
  static final String GOLDEN =
      """
      NKEXPIRY1
      run=38100000-2222-4333-8444-555555555555
      activation=38100000-6666-4777-8888-999999999999
      cutoff=2026-09-30T00:00:00Z
      boot=38100000-3333-4333-8444-555555555555
      epoch=38100000-4444-4333-8444-555555555555
      broker=11111111111111111111111111111111
      step_id=42
      attempt=1
      started=2026-09-30T00:00:01Z
      skipped=false
      """;

  @Test
  void independentGoldenFullHandleAndInputErasure() {
    byte[] owned = GOLDEN.getBytes(StandardCharsets.US_ASCII);
    var value = CleanupWorkerRequest.Expiry.consume(owned);
    assertArrayEquals(new byte[owned.length], owned);
    assertArrayEquals(GOLDEN.getBytes(StandardCharsets.US_ASCII), value.encode());
    assertEquals(42, value.handle().id());
    assertEquals(1, value.handle().attempt());
    assertEquals("CLEAN_EXPIRY", value.handle().step().name());
    assertEquals(Instant.parse("2026-09-30T00:00:01Z"), value.handle().startedAt());
    assertEquals(value.run(), value.original().run().id());
    assertEquals(value.cutoff(), value.original().run().cutoff());
    assertFalse(value.handle().skipped());
    assertEquals("ExpiryWorkerRequest[claims=<redacted>]", value.toString());
    var skipped =
        CleanupWorkerRequest.Expiry.consume(
            GOLDEN.replace("skipped=false", "skipped=true").getBytes(StandardCharsets.US_ASCII));
    assertTrue(skipped.handle().skipped());
  }

  @Test
  void fixedCanonicalNegativeMatrixAndCleanupMutualRejection() {
    for (String invalid :
        List.of(
            "",
            GOLDEN.stripTrailing(),
            GOLDEN + "\n",
            GOLDEN.replace("\n", "\r\n"),
            GOLDEN.replace("NKEXPIRY1", "NKCLEAN1"),
            GOLDEN.replace("step_id=42", "step_id=0"),
            GOLDEN.replace("step_id=42", "step_id=042"),
            GOLDEN.replace("attempt=1", "attempt=100"),
            GOLDEN.replace("attempt=1", "attempt=+1"),
            GOLDEN.replace("skipped=false", "skipped=FALSE"),
            GOLDEN.replace("broker=11111111111111111111111111111111", "broker=" + "0".repeat(32)),
            GOLDEN.replace(
                "38100000-4444-4333-8444-555555555555", "00000000-0000-0000-0000-000000000000"),
            GOLDEN.replace("started=2026-09-30T00:00:01Z", "started=2026-09-29T00:00:01Z"),
            GOLDEN.replace("cutoff=", "unknown="),
            GOLDEN.replace("run=", "activation="),
            "x".repeat(1025),
            GOLDEN + "\u0000",
            GOLDEN + "日本")) {
      byte[] owned = invalid.getBytes(StandardCharsets.UTF_8);
      assertThrows(
          IllegalArgumentException.class, () -> CleanupWorkerRequest.Expiry.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> CleanupWorkerRequest.consume(GOLDEN.getBytes(StandardCharsets.US_ASCII)));
    assertThrows(NullPointerException.class, () -> CleanupWorkerRequest.Expiry.consume(null));
    var v = CleanupWorkerRequest.Expiry.consume(GOLDEN.getBytes(StandardCharsets.US_ASCII));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupWorkerRequest.Expiry(
                v.run(),
                v.run(),
                v.cutoff(),
                v.boot(),
                v.epoch(),
                v.brokerInvocation(),
                v.stepId(),
                v.attempt(),
                v.started(),
                false));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupWorkerRequest.Expiry(
                v.run(),
                v.activation(),
                v.cutoff(),
                v.boot(),
                v.epoch(),
                null,
                v.stepId(),
                v.attempt(),
                v.started(),
                false));
  }
}
