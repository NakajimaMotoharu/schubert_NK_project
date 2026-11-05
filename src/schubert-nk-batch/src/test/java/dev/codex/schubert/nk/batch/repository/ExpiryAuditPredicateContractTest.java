package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * EXPPORT-P001..005; hand-authored V022 state and equality vectors, never production expectations.
 */
final class ExpiryAuditPredicateContractTest {
  private static final Instant CUTOFF_AT = Instant.parse("2026-11-05T00:00:00Z");
  private static final Instant EXPIRY_AT = Instant.parse("2026-10-29T00:00:00Z");
  private static final Instant END_AT = Instant.parse("2026-11-05T00:00:02Z");
  private static final BatchStepAttempt ATTEMPT =
      new BatchStepAttempt(
          7,
          new BatchRun(new UUID(0, 1), CUTOFF_AT),
          BatchStep.CLEAN_EXPIRY,
          1,
          Instant.parse("2026-11-05T00:00:01Z"),
          false);
  private static final String STATUS = "status";
  private static final String CUTOFF = "cutoff";
  private static final String BEFORE = "before";
  private static final String AFTER = "after";
  private static final String TARGET = "target";
  private static final String SUCCESS = "success";
  private static final String FAILURE = "failure";
  private static final String BYTES = "bytes";
  private static final String ENDED = "ended";
  private static final String CODE = "code";
  private static final String SUMMARY = "summary";
  private static final String RUNNING = "RUNNING";
  private static final String SUCCEEDED = "SUCCESS";
  private static final String WARNING = "WARNING";
  private static final String FAILED = "FAILED";

  @Test
  void stageAndPriorEstablishRequiredInvariantsAndAllRenderingsStayRedacted() {
    var zero = new ExpiryAuditRepository.Stage(EXPIRY_AT, 0, 0, 0);
    assertEquals(0, zero.before());
    assertEquals(0, zero.target());
    assertEquals(0, zero.estimatedBytes());
    assertEquals("ExpiryAuditStage[observation=<redacted>]", zero.toString());
    assertThrows(NullPointerException.class, () -> new ExpiryAuditRepository.Stage(null, 0, 0, 0));
    for (long[] values :
        List.of(
            new long[] {-1, 0, 0},
            new long[] {0, -1, 0},
            new long[] {1, 2, 0},
            new long[] {1, 1, -1}))
      assertThrows(
          IllegalArgumentException.class,
          () -> new ExpiryAuditRepository.Stage(EXPIRY_AT, values[0], values[1], values[2]));
    var largest =
        new ExpiryAuditRepository.Stage(EXPIRY_AT, Long.MAX_VALUE, Long.MAX_VALUE, Long.MAX_VALUE);
    assertEquals(Long.MAX_VALUE, largest.target());
    assertEquals("ExpiryAuditSnapshot[observation=<redacted>]", base().toString());
    assertThrows(NullPointerException.class, () -> new ExpiryAuditRepository.Prior(null, base()));
    assertThrows(NullPointerException.class, () -> new ExpiryAuditRepository.Prior(ATTEMPT, null));
    var prior = new ExpiryAuditRepository.Prior(ATTEMPT, base());
    assertEquals(ATTEMPT, prior.handle());
    assertFalse(prior.toString().contains(ATTEMPT.run().id().toString()));
  }

  @Test
  void statusEndedAndAbsentObservationTriplesFollowIndependentV022Table() {
    assertTrue(valid(base()));
    assertTrue(valid(terminal()));
    assertTrue(valid(mutate(terminal(), STATUS, WARNING)));
    assertTrue(valid(mutate(terminal(), STATUS, FAILED)));
    for (String status : List.of("UNKNOWN", "", "success", "SKIPPED"))
      assertFalse(valid(mutate(base(), STATUS, status)));
    assertFalse(valid(mutate(base(), ENDED, END_AT)));
    assertFalse(valid(mutate(terminal(), ENDED, null)));
    assertFalse(valid(mutate(base(), CUTOFF, null)));
    assertFalse(valid(mutate(base(), BEFORE, null)));
    var absent =
        new ExpiryAuditRepository.Snapshot(RUNNING, null, null, null, 0, 0, 0, 0, null, null, null);
    assertTrue(valid(absent));
    assertTrue(valid(mutate(mutate(absent, STATUS, WARNING), ENDED, END_AT)));
    assertFalse(valid(mutate(absent, AFTER, 0L)));
    assertFalse(valid(mutate(mutate(absent, STATUS, SUCCEEDED), ENDED, END_AT)));
  }

  @Test
  void counterCutoffAndKnownOrUnknownAfterBoundariesUseLiteralPostconditions() {
    for (String field : List.of(TARGET, SUCCESS, FAILURE, BYTES, BEFORE))
      assertFalse(valid(mutate(base(), field, -1L)));
    assertFalse(valid(mutate(base(), CUTOFF, EXPIRY_AT.plusSeconds(1))));
    assertFalse(valid(mutate(base(), TARGET, 4L)));
    assertFalse(valid(mutate(base(), SUCCESS, 1L)));
    assertFalse(valid(mutate(terminal(), AFTER, -1L)));
    assertFalse(valid(mutate(terminal(), AFTER, 4L)));
    assertFalse(valid(mutate(terminal(), SUCCESS, 1L)));
    assertFalse(valid(mutate(terminal(), TARGET, 3L)));
    assertFalse(valid(mutate(terminal(), FAILURE, 1L)));
    var warning =
        new ExpiryAuditRepository.Snapshot(
            WARNING,
            EXPIRY_AT,
            3L,
            1L,
            3,
            2,
            1,
            200,
            END_AT,
            "PROTECTED_RECORDS",
            "protected records retained");
    assertTrue(valid(warning));
    var failedUnknown =
        new ExpiryAuditRepository.Snapshot(
            FAILED,
            EXPIRY_AT,
            3L,
            null,
            2,
            0,
            2,
            200,
            END_AT,
            "IO_FAILURE",
            "batch file operation failed");
    assertTrue(valid(failedUnknown));
    assertFalse(valid(mutate(failedUnknown, SUCCESS, 1L)));
    assertFalse(valid(mutate(terminal(), AFTER, null)));
    var zeroRemoved =
        new ExpiryAuditRepository.Snapshot(
            SUCCEEDED, EXPIRY_AT, 3L, 3L, 0, 0, 0, 0, END_AT, null, null);
    assertTrue(valid(zeroRemoved));
    assertTrue(valid(mutate(zeroRemoved, STATUS, FAILED)));
  }

  @Test
  void stageReplayAcceptsExactNineConditionsAndRejectsEachIndependentDifference() {
    var stage = new ExpiryAuditRepository.Stage(EXPIRY_AT, 3, 2, 200);
    assertTrue(ExpiryAuditRepository.matchesStage(Optional.of(base()), stage));
    assertFalse(ExpiryAuditRepository.matchesStage(Optional.empty(), stage));
    for (Change change :
        List.of(
            new Change(STATUS, WARNING),
            new Change(AFTER, 0L),
            new Change(CUTOFF, EXPIRY_AT.plusSeconds(1)),
            new Change(BEFORE, 4L),
            new Change(TARGET, 1L),
            new Change(SUCCESS, 1L),
            new Change(FAILURE, 1L),
            new Change(BYTES, 201L)))
      assertFalse(
          ExpiryAuditRepository.matchesStage(
              Optional.of(mutate(base(), change.field(), change.value())), stage),
          change.field());
  }

  @Test
  void terminalReplayRequiresEveryLiteralCountTimeDiagnosticAndNullableField() {
    var stage = new ExpiryAuditRepository.Stage(EXPIRY_AT, 3, 2, 200);
    var result =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 2, 2, 0, 200, BatchStepResult.Reason.NONE);
    assertTrue(
        ExpiryAuditRepository.matchesTerminal(Optional.of(terminal()), stage, END_AT, 1L, result));
    assertFalse(ExpiryAuditRepository.matchesTerminal(Optional.empty(), stage, END_AT, 1L, result));
    for (Change change :
        List.of(
            new Change(CUTOFF, EXPIRY_AT.plusSeconds(1)),
            new Change(BEFORE, 4L),
            new Change(AFTER, 0L),
            new Change(TARGET, 1L),
            new Change(SUCCESS, 1L),
            new Change(FAILURE, 1L),
            new Change(BYTES, 201L),
            new Change(STATUS, WARNING),
            new Change(ENDED, END_AT.plusNanos(1000)),
            new Change(CODE, ""),
            new Change(SUMMARY, "")))
      assertFalse(
          ExpiryAuditRepository.matchesTerminal(
              Optional.of(mutate(terminal(), change.field(), change.value())),
              stage,
              END_AT,
              1L,
              result),
          change.field());
    assertTrue(
        ExpiryAuditRepository.matchesTerminal(
            Optional.of(mutate(terminal(), AFTER, null)), stage, END_AT, null, result));
  }

  private static boolean valid(ExpiryAuditRepository.Snapshot snapshot) {
    return ExpiryAuditRepository.validSnapshot(ATTEMPT, snapshot);
  }

  private static ExpiryAuditRepository.Snapshot base() {
    return new ExpiryAuditRepository.Snapshot(
        RUNNING, EXPIRY_AT, 3L, null, 2, 0, 0, 200, null, null, null);
  }

  private static ExpiryAuditRepository.Snapshot terminal() {
    return new ExpiryAuditRepository.Snapshot(
        SUCCEEDED, EXPIRY_AT, 3L, 1L, 2, 2, 0, 200, END_AT, null, null);
  }

  /** Fixture field replacement only, never a duplicate of the production validity algorithm. */
  private static ExpiryAuditRepository.Snapshot mutate(
      ExpiryAuditRepository.Snapshot base, String field, Object value) {
    Map<String, Object> data = new HashMap<>();
    data.put(STATUS, base.status());
    data.put(CUTOFF, base.cutoff());
    data.put(BEFORE, base.before());
    data.put(AFTER, base.after());
    data.put(TARGET, base.target());
    data.put(SUCCESS, base.success());
    data.put(FAILURE, base.failure());
    data.put(BYTES, base.estimatedBytes());
    data.put(ENDED, base.ended());
    data.put(CODE, base.errorCode());
    data.put(SUMMARY, base.errorSummary());
    data.put(field, value);
    return new ExpiryAuditRepository.Snapshot(
        (String) data.get(STATUS),
        (Instant) data.get(CUTOFF),
        (Long) data.get(BEFORE),
        (Long) data.get(AFTER),
        (Long) data.get(TARGET),
        (Long) data.get(SUCCESS),
        (Long) data.get(FAILURE),
        (Long) data.get(BYTES),
        (Instant) data.get(ENDED),
        (String) data.get(CODE),
        (String) data.get(SUMMARY));
  }

  private record Change(String field, Object value) {}
}
