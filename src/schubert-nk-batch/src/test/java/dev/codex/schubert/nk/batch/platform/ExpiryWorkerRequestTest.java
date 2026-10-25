package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
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
  static final String SKIP_GOLDEN =
      """
      NKEXPIRYSKIP2
      run=38100000-2222-4333-8444-555555555555
      activation=38100000-6666-4777-8888-999999999999
      cutoff=2026-09-30T00:00:00Z
      boot=38100000-3333-4333-8444-555555555555
      epoch=38100000-4444-4333-8444-555555555555
      broker=11111111111111111111111111111111
      step_id=43
      attempt=2
      started=2026-09-30T00:00:03Z
      skipped=true
      prior_run_id=38100000-2222-4333-8444-555555555555
      prior_cutoff_utc=2026-09-30T00:00:00Z
      prior_step_id=42
      prior_attempt=1
      prior_started=2026-09-30T00:00:01Z
      prior_ended=2026-09-30T00:00:02Z
      """;

  /** PT-OPS-EREQ3962-001: immutable step admission retains exact identity/start boundaries. */
  @Test
  void ereq3962001ImmutableStepAdmissionDefinesIdentityAndStartBounds() {
    UUID run = UUID.fromString("39620001-2222-4333-8444-555555555555");
    Instant cutoff = Instant.parse("2026-09-30T00:00:00Z");
    Instant started = cutoff.plusSeconds(1);
    for (long id : new long[] {-1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new CleanupWorkerRequest.Expiry.PriorExpiry(
                      run, cutoff, id, 1, started, started));
      assertEquals("invalid batch step identity", failure.getMessage());
      assertNull(failure.getCause());
    }
    for (int attempt : new int[] {-1, 0, 100, Integer.MAX_VALUE}) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new CleanupWorkerRequest.Expiry.PriorExpiry(
                      run, cutoff, 42, attempt, started, started));
      assertEquals("invalid batch step identity", failure.getMessage());
      assertNull(failure.getCause());
    }
    for (Instant invalid :
        List.of(
            cutoff.minusNanos(1000),
            started.plusNanos(1),
            Instant.parse("+10000-01-01T00:00:00Z"))) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new CleanupWorkerRequest.Expiry.PriorExpiry(
                      run, cutoff, 42, 1, invalid, invalid));
      assertEquals("invalid batch step time", failure.getMessage());
      assertNull(failure.getCause());
    }
    for (long id : new long[] {1, 999_999_999_999L})
      for (int attempt : new int[] {1, 99})
        for (Instant start : List.of(cutoff, cutoff.plusNanos(1000))) {
          var value =
              new CleanupWorkerRequest.Expiry.PriorExpiry(run, cutoff, id, attempt, start, start);
          assertEquals(run, value.run());
          assertEquals(cutoff, value.cutoff());
          assertEquals(id, value.id());
          assertEquals(attempt, value.attempt());
          assertEquals(start, value.started());
          assertEquals(start, value.ended());
        }
    assertThrows(
        NullPointerException.class,
        () -> new CleanupWorkerRequest.Expiry.PriorExpiry(run, cutoff, 0, 1, started, null));
  }

  /** PT-OPS-EREQ3042-001: original end-time precision/range and all nullable identity fields. */
  @Test
  void ereq3042001PriorBoundaryAndNullContractNeverAuthorizeCleanup() {
    UUID run = UUID.fromString("38100000-2222-4333-8444-555555555555");
    Instant cutoff = Instant.parse("2026-09-30T00:00:00Z");
    Instant start = Instant.parse("2026-09-30T00:00:01Z");
    for (Instant ended :
        List.of(start, start.plusNanos(1000), Instant.parse("9999-12-31T23:59:59.999999Z"))) {
      var value = new CleanupWorkerRequest.Expiry.PriorExpiry(run, cutoff, 42, 1, start, ended);
      assertEquals(ended, value.ended());
      assertEquals(start, value.started());
      assertEquals(42, value.id());
      assertEquals("PriorExpiry[identity/time=<redacted>]", value.toString());
    }
    for (Instant ended :
        List.of(
            start.minusNanos(1000), start.plusNanos(1), Instant.parse("+10000-01-01T00:00:00Z"))) {
      assertThrows(
          IllegalArgumentException.class,
          () -> new CleanupWorkerRequest.Expiry.PriorExpiry(run, cutoff, 42, 1, start, ended));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupWorkerRequest.Expiry.PriorExpiry(
                run, cutoff, 42, 1, start.plusNanos(1), start.plusSeconds(1)));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupWorkerRequest.Expiry.PriorExpiry(null, cutoff, 42, 1, start, start));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupWorkerRequest.Expiry.PriorExpiry(run, null, 42, 1, start, start));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupWorkerRequest.Expiry.PriorExpiry(run, cutoff, 42, 1, null, start));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupWorkerRequest.Expiry.PriorExpiry(run, cutoff, 42, 1, start, null));
  }

  /** PT-OPS-EREQ3042-002: fixed literal field grammar and consumed bytes on every rejection. */
  @Test
  void ereq3042002EveryRequiredFieldAndPriorPrecisionRejectsWithErasure() {
    for (String field :
        List.of(
            "run",
            "activation",
            "cutoff",
            "boot",
            "epoch",
            "broker",
            "step_id",
            "attempt",
            "started",
            "skipped",
            "prior_run_id",
            "prior_cutoff_utc",
            "prior_step_id",
            "prior_attempt",
            "prior_started",
            "prior_ended")) {
      String changed = SKIP_GOLDEN.replace("\n" + field + "=", "\nunknown=");
      assertNotEquals(SKIP_GOLDEN, changed, field);
      byte[] owned = changed.getBytes(StandardCharsets.US_ASCII);
      assertEquals(
          "cleanup request invalid",
          assertThrows(
                  IllegalArgumentException.class, () -> CleanupWorkerRequest.Expiry.consume(owned))
              .getMessage(),
          field);
      assertArrayEquals(new byte[owned.length], owned, field);
    }
    for (String bad :
        List.of(
            SKIP_GOLDEN.replace(
                "prior_ended=2026-09-30T00:00:02Z", "prior_ended=2026-09-30T00:00:02.000000001Z"),
            SKIP_GOLDEN.replace(
                "prior_started=2026-09-30T00:00:01Z",
                "prior_started=2026-09-30T00:00:01.000000001Z"),
            SKIP_GOLDEN.replace(
                "prior_ended=2026-09-30T00:00:02Z", "prior_ended=+10000-01-01T00:00:00Z"),
            SKIP_GOLDEN.replace("prior_step_id=42", "prior_step_id=1000000000000"),
            SKIP_GOLDEN.replace("prior_attempt=1", "prior_attempt=100"))) {
      byte[] owned = bad.getBytes(StandardCharsets.US_ASCII);
      assertThrows(
          IllegalArgumentException.class, () -> CleanupWorkerRequest.Expiry.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
    }
  }

  @Test
  void wire200001ForeignAnchorCutoffIsExplicitAndOldGrammarIsNotReinterpreted() {
    String vector =
        SKIP_GOLDEN
            .replace(
                "prior_run_id=38100000-2222-4333-8444-555555555555",
                "prior_run_id=38100000-9999-4333-8444-555555555555")
            .replace(
                "prior_cutoff_utc=2026-09-30T00:00:00Z", "prior_cutoff_utc=2026-09-29T23:00:00Z");
    var value = CleanupWorkerRequest.Expiry.consume(vector.getBytes(StandardCharsets.US_ASCII));
    assertEquals(
        UUID.fromString("38100000-9999-4333-8444-555555555555"), value.priorHandle().run().id());
    assertEquals(Instant.parse("2026-09-29T23:00:00Z"), value.priorHandle().run().cutoff());
    assertEquals(Instant.parse("2026-09-30T00:00:00Z"), value.handle().run().cutoff());
    assertArrayEquals(vector.getBytes(StandardCharsets.US_ASCII), value.encode());
    for (String bad :
        List.of(
            vector.replace(
                "prior_cutoff_utc=2026-09-29T23:00:00Z", "prior_cutoff_utc=2026-09-28T23:00:00Z"),
            vector.replace(
                "prior_cutoff_utc=2026-09-29T23:00:00Z", "prior_cutoff_utc=2026-09-30T00:00:02Z"),
            vector.replace("prior_run_id=38100000-9999-4333-8444-555555555555", "prior_run_id="),
            vector.replace("prior_cutoff_utc=", "prior_cutoff="))) {
      byte[] owned = bad.getBytes(StandardCharsets.US_ASCII);
      assertThrows(
          IllegalArgumentException.class, () -> CleanupWorkerRequest.Expiry.consume(owned));
      assertArrayEquals(new byte[owned.length], owned);
    }
  }

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
        CleanupWorkerRequest.Expiry.consume(SKIP_GOLDEN.getBytes(StandardCharsets.US_ASCII));
    assertTrue(skipped.handle().skipped());
    assertFalse(skipped.priorHandle().skipped());
    assertEquals(42, skipped.priorHandle().id());
    assertEquals(43, skipped.handle().id());
    assertArrayEquals(SKIP_GOLDEN.getBytes(StandardCharsets.US_ASCII), skipped.encode());
    assertEquals(Instant.parse("2026-09-30T00:00:02Z"), skipped.prior().orElseThrow().ended());
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

  @Test
  void ereq005SkipRequiresSeparateCompleteCanonicalOriginalAndErasesEveryRejectedInput() {
    for (String bad :
        List.of(
            GOLDEN.replace("skipped=false", "skipped=true"),
            SKIP_GOLDEN.replace("NKEXPIRYSKIP2", "NKEXPIRY1"),
            SKIP_GOLDEN.replace("NKEXPIRYSKIP2", "NKEXPIRYSKIP1"),
            SKIP_GOLDEN.replace("skipped=true", "skipped=false"),
            SKIP_GOLDEN.replace("prior_step_id=42", "prior_step_id=43"),
            SKIP_GOLDEN.replace("prior_step_id=42", "prior_step_id=042"),
            SKIP_GOLDEN.replace("prior_attempt=1", "prior_attempt=2"),
            SKIP_GOLDEN.replace("prior_attempt=1", "prior_attempt=0"),
            SKIP_GOLDEN.replace(
                "prior_started=2026-09-30T00:00:01Z", "prior_started=2026-09-29T00:00:01Z"),
            SKIP_GOLDEN.replace(
                "prior_ended=2026-09-30T00:00:02Z", "prior_ended=2026-09-30T00:00:04Z"),
            SKIP_GOLDEN.replace(
                "prior_ended=2026-09-30T00:00:02Z", "prior_ended=2026-09-30T00:00:00Z"),
            SKIP_GOLDEN.replace("prior_started=", "unknown="),
            SKIP_GOLDEN.replace("prior_attempt=1\n", ""),
            SKIP_GOLDEN + "\n",
            SKIP_GOLDEN.replace("\n", "\r\n"))) {
      byte[] bytes = bad.getBytes(StandardCharsets.US_ASCII);
      assertThrows(
          IllegalArgumentException.class, () -> CleanupWorkerRequest.Expiry.consume(bytes));
      assertArrayEquals(new byte[bytes.length], bytes);
    }
    var ordinary = CleanupWorkerRequest.Expiry.consume(GOLDEN.getBytes(StandardCharsets.US_ASCII));
    assertThrows(IllegalArgumentException.class, ordinary::priorHandle);
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupWorkerRequest.Expiry.PriorExpiry(
                UUID.randomUUID(), Instant.EPOCH, 1, 1, null, Instant.EPOCH));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupWorkerRequest.Expiry.PriorExpiry(
                UUID.randomUUID(), Instant.EPOCH, 1, 1, Instant.EPOCH, null));
    assertEquals(
        "PriorExpiry[identity/time=<redacted>]",
        new CleanupWorkerRequest.Expiry.PriorExpiry(
                UUID.randomUUID(), Instant.EPOCH, 1, 1, Instant.EPOCH, Instant.EPOCH)
            .toString());
  }
}
