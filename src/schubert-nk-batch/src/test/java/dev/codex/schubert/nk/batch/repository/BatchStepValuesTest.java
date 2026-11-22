package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/OPS009/UI251/SS331 8.3/341; SSC055/PG163; BAT130..137. */
final class BatchStepValuesTest {
  static final BatchRun RUN = new BatchRun(new UUID(1, 2), Instant.parse("2026-09-12T15:00:00Z"));
  static final Instant NOW = Instant.parse("2026-09-13T02:00:00Z");
  static final List<String> STEPS =
      List.of(
          "BACKUP_DB",
          "BACKUP_CONFIG",
          "CLEAN_NOTIFICATION",
          "CLEAN_QUESTION",
          "CLEAN_SESSION",
          "CLEAN_INBOX_OUTBOX",
          "CLEAN_LOG",
          "CLEAN_BATCH_RUN",
          "CLEAN_TRANSFER",
          "CLEAN_EXPIRY");
  static final List<String> CODES =
      List.of(
          "NONE",
          "ALREADY_SUCCESSFUL",
          "BACKUP_UNAVAILABLE",
          "PROTECTED_RECORDS",
          "ABANDONED",
          "DATABASE_FAILURE",
          "COMMAND_FAILURE",
          "SAFETY_FAILURE",
          "IO_FAILURE",
          "TIMEOUT",
          "INTERRUPTED");
  static final List<String> SUMMARIES =
      Arrays.asList(
          null,
          "step already successful for business date",
          "verified backup unavailable",
          "protected records retained",
          "previous same-run attempt abandoned",
          "batch database operation failed",
          "batch command failed",
          "batch safety check failed",
          "batch file operation failed",
          "batch step deadline reached",
          "batch step interrupted");

  @Test
  void closedStepsAndBackupPolicy() {
    assertEquals(STEPS, Arrays.stream(BatchStep.values()).map(Enum::name).toList());
    for (String name : STEPS)
      assertEquals(name.startsWith("BACKUP_"), BatchStep.valueOf(name).backup());
    assertThrows(IllegalArgumentException.class, () -> BatchStep.valueOf("UNKNOWN"));
    assertThrows(IllegalArgumentException.class, () -> BatchStep.valueOf("clean_log"));
  }

  @Test
  void attemptIdentityAndBounds() {
    for (long id : List.of(1L, 999999999999L))
      for (int number : List.of(1, 99))
        for (boolean skip : List.of(false, true)) {
          var a = new BatchStepAttempt(id, RUN, BatchStep.CLEAN_LOG, number, NOW, skip);
          assertEquals(id, a.id());
          assertSame(RUN, a.run());
          assertEquals(BatchStep.CLEAN_LOG, a.step());
          assertEquals(number, a.attempt());
          assertEquals(NOW, a.startedAt());
          assertEquals(skip, a.skipped());
        }
    for (long id : List.of(Long.MIN_VALUE, 0L, 1000000000000L, Long.MAX_VALUE))
      assertThrows(
          IllegalArgumentException.class,
          () -> new BatchStepAttempt(id, RUN, BatchStep.CLEAN_LOG, 1, NOW, false));
    for (int n : List.of(Integer.MIN_VALUE, 0, 100, Integer.MAX_VALUE))
      assertThrows(
          IllegalArgumentException.class,
          () -> new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, n, NOW, false));
  }

  @Test
  void terminalStatesAndReasonMatrix() {
    assertEquals(
        List.of("SUCCESS", "WARNING", "FAILED", "SKIPPED"),
        Arrays.stream(BatchStepResult.Status.values()).map(Enum::name).toList());
    assertEquals(CODES, Arrays.stream(BatchStepResult.Reason.values()).map(Enum::name).toList());
    for (int i = 0; i < CODES.size(); i++) {
      var reason = BatchStepResult.Reason.valueOf(CODES.get(i));
      assertEquals(i == 0 ? null : CODES.get(i), reason.code());
      assertEquals(SUMMARIES.get(i), reason.summary());
      for (var status : BatchStepResult.Status.values()) {
        boolean allowed =
            switch (CODES.get(i)) {
              case "NONE" -> status.name().equals("SUCCESS");
              case "ALREADY_SUCCESSFUL", "BACKUP_UNAVAILABLE" -> status.name().equals("SKIPPED");
              case "PROTECTED_RECORDS" -> status.name().equals("WARNING");
              case "ABANDONED" -> status.name().equals("FAILED");
              default -> Set.of("WARNING", "FAILED").contains(status.name());
            };
        if (allowed) {
          var result = new BatchStepResult(status, 0, 0, 0, 0, reason);
          assertEquals(status, result.status());
          assertEquals(reason, result.reason());
        } else
          assertThrows(
              IllegalArgumentException.class,
              () -> new BatchStepResult(status, 0, 0, 0, 0, reason));
      }
    }
    assertThrows(IllegalArgumentException.class, () -> BatchStepResult.Status.valueOf("RUNNING"));
    assertThrows(IllegalArgumentException.class, () -> BatchStepResult.Reason.valueOf("raw"));
  }

  @Test
  void counterAndStatusBoundaries() {
    for (int field = 0; field < 4; field++) {
      long[] v = {0, 0, 0, 0};
      v[field] = -1;
      assertThrows(
          IllegalArgumentException.class,
          () -> result(v, BatchStepResult.Status.WARNING, BatchStepResult.Reason.IO_FAILURE));
      v[field] = Long.MIN_VALUE;
      assertThrows(
          IllegalArgumentException.class,
          () -> result(v, BatchStepResult.Status.WARNING, BatchStepResult.Reason.IO_FAILURE));
      v[field] = 1;
      assertThrows(
          IllegalArgumentException.class,
          () ->
              result(v, BatchStepResult.Status.SKIPPED, BatchStepResult.Reason.BACKUP_UNAVAILABLE));
    }
    var max =
        result(
            new long[] {Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE},
            BatchStepResult.Status.FAILED,
            BatchStepResult.Reason.IO_FAILURE);
    assertEquals(Long.MAX_VALUE, max.target());
    assertEquals(Long.MAX_VALUE, max.success());
    assertEquals(Long.MAX_VALUE, max.failure());
    assertEquals(Long.MAX_VALUE, max.bytes());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            result(
                new long[] {1, 1, 1, 1},
                BatchStepResult.Status.SUCCESS,
                BatchStepResult.Reason.NONE));
    var noInventedSum =
        result(
            new long[] {1, 2, 0, Long.MAX_VALUE},
            BatchStepResult.Status.SUCCESS,
            BatchStepResult.Reason.NONE);
    assertEquals(1, noInventedSum.target());
    assertEquals(2, noInventedSum.success());
    assertEquals(0, noInventedSum.failure());
    assertEquals(Long.MAX_VALUE, noInventedSum.bytes());
  }

  @Test
  void temporalContractAndBusinessDay() {
    // YKT143: IANA historical LMT crosses midnight before fixed +09 would do so.
    var historical = new BatchRun(new UUID(0, 143), Instant.parse("1582-10-04T14:50:00Z"));
    assertEquals(
        LocalDate.of(1582, 10, 5),
        new BatchStepAttempt(1, historical, BatchStep.CLEAN_LOG, 1, historical.cutoff(), false)
            .businessDate());
    assertEquals(
        LocalDate.of(1582, 10, 5),
        new MaintenanceActivation(historical, new UUID(0, 1)).businessDate());
    for (String s :
        List.of("0001-01-01T00:00:00Z", "1582-10-10T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      var run = new BatchRun(new UUID(0, 1), Instant.parse(s));
      var a = new BatchStepAttempt(1, run, BatchStep.CLEAN_LOG, 1, run.cutoff(), false);
      assertEquals(run.cutoff(), a.startedAt());
    }
    assertEquals(
        LocalDate.of(2026, 9, 13),
        new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, NOW.plusSeconds(86400), false)
            .businessDate());
    for (Instant bad :
        List.of(
            RUN.cutoff().minusNanos(1000),
            Instant.parse("+10000-01-01T00:00:00Z"),
            NOW.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, bad, false));
    var upper = new BatchRun(new UUID(0, 3), Instant.parse("9999-12-31T23:59:59.999999Z"));
    assertEquals(
        LocalDate.of(10000, 1, 1),
        new BatchStepAttempt(1, upper, BatchStep.CLEAN_LOG, 1, upper.cutoff(), false)
            .businessDate());
  }

  @Test
  void nullContractsAndRedaction() throws ReflectiveOperationException {
    assertThrows(
        NullPointerException.class,
        () -> new BatchStepAttempt(1, null, BatchStep.CLEAN_LOG, 1, NOW, false));
    assertThrows(
        NullPointerException.class, () -> new BatchStepAttempt(1, RUN, null, 1, NOW, false));
    assertThrows(
        NullPointerException.class,
        () -> new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, null, false));
    assertThrows(
        NullPointerException.class,
        () -> new BatchStepResult(null, 0, 0, 0, 0, BatchStepResult.Reason.NONE));
    assertThrows(
        NullPointerException.class,
        () -> new BatchStepResult(BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, null));
    assertEquals(
        "BatchStepAttempt[identity/time=<redacted>]",
        new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, NOW, false).toString());
    assertEquals(
        "BatchStepResult[observation=<redacted>]",
        new BatchStepResult(BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, BatchStepResult.Reason.NONE)
            .toString());
    // Security audit of private diagnostic object: default record rendering would leak legacy
    // identity.
    var type = Class.forName("dev.codex.schubert.nk.batch.repository.BatchRunRepository$History");
    var ctor =
        type.getDeclaredConstructor(long.class, UUID.class, int.class, Instant.class, String.class);
    ctor.setAccessible(true);
    assertEquals(
        "BatchStepHistory[identity/time=<redacted>]",
        ctor.newInstance(123L, RUN.id(), 1, NOW, "RUNNING").toString());
  }

  @Test
  void immutableValueSemantics() {
    var a = new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, NOW, false);
    var b =
        new BatchStepAttempt(
            1, new BatchRun(RUN.id(), RUN.cutoff()), BatchStep.CLEAN_LOG, 1, NOW, false);
    assertEquals(a, b);
    assertEquals(a.hashCode(), b.hashCode());
    assertNotEquals(a, new BatchStepAttempt(1, RUN, BatchStep.CLEAN_LOG, 1, NOW, true));
    var r =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 5, 2, 0, 3, BatchStepResult.Reason.PROTECTED_RECORDS);
    var copy =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 5, 2, 0, 3, BatchStepResult.Reason.PROTECTED_RECORDS);
    assertEquals(r, copy);
    assertEquals(r.hashCode(), copy.hashCode());
    assertNotEquals(
        r,
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 6, 2, 0, 3, BatchStepResult.Reason.PROTECTED_RECORDS));
  }

  @Test
  void independentConcurrentValues()
      throws InterruptedException, ExecutionException, TimeoutException {
    var pool = Executors.newVirtualThreadPerTaskExecutor();
    try {
      List<Future<BatchStepAttempt>> futures = new ArrayList<>();
      for (int i = 1; i <= 64; i++) {
        int n = i;
        futures.add(
            pool.submit(() -> new BatchStepAttempt(n, RUN, BatchStep.CLEAN_LOG, n, NOW, false)));
      }
      for (int i = 1; i <= 64; i++) {
        var a = futures.get(i - 1).get(5, TimeUnit.SECONDS);
        assertEquals(i, a.id());
        assertEquals(i, a.attempt());
        assertEquals(LocalDate.of(2026, 9, 13), a.businessDate());
      }
    } finally {
      pool.shutdownNow();
      if (!pool.awaitTermination(10, TimeUnit.SECONDS))
        throw new AssertionError("owned virtual value workers did not terminate");
    }
  }

  static BatchStepResult result(
      long[] v, BatchStepResult.Status status, BatchStepResult.Reason reason) {
    return new BatchStepResult(status, v[0], v[1], v[2], v[3], reason);
  }
}
