package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** SS331 §8.3 and SS341 failure-pair value contract. No repository operation. */
final class BackupFailureSnapshotValueTest {
  private static final Instant CUTOFF = Instant.parse("2026-09-12T15:00:00Z");
  private static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  private static final Instant END = Instant.parse("2026-09-13T02:00:01Z");
  private static final BatchRun RUN = new BatchRun(new UUID(17, 1), CUTOFF);
  private static final BatchStepAttempt DATABASE =
      attempt(7, RUN, BatchStep.BACKUP_DB, START, false);
  private static final BatchStepAttempt CONFIGURATION =
      attempt(8, RUN, BatchStep.BACKUP_CONFIG, START, false);
  private static final String INVALID_PAIR = "failed backup pair invalid";

  /** PT-BAT-BFSVALUE001. */
  @Test
  void pair001PairKeepsIdentityAndAllowsTheSharedStartBoundary() {
    var sameTime = new BackupFailureSnapshot(DATABASE, CONFIGURATION, START);
    assertSame(DATABASE, sameTime.database());
    assertSame(CONFIGURATION, sameTime.configuration());
    assertEquals(START, sameTime.endedAt());
    var later = new BackupFailureSnapshot(DATABASE, CONFIGURATION, END);
    var identical = new BackupFailureSnapshot(DATABASE, CONFIGURATION, END);
    assertEquals(later, identical);
    assertEquals(later.hashCode(), identical.hashCode());
    assertNotEquals(later, sameTime);
    assertEquals("BackupFailureSnapshot[data=<redacted>]", later.toString());
  }

  /** PT-BAT-BFSVALUE002. */
  @Test
  void pair002MisplacedStepsSharedIdsAndSkippedEitherSideRejectIndependently() {
    var wrongDatabase = attempt(7, RUN, BatchStep.BACKUP_CONFIG, START, false);
    var wrongConfig = attempt(8, RUN, BatchStep.BACKUP_DB, START, false);
    var sharedId = attempt(7, RUN, BatchStep.BACKUP_CONFIG, START, false);
    var skippedDb = attempt(7, RUN, BatchStep.BACKUP_DB, START, true);
    var skippedConfig = attempt(8, RUN, BatchStep.BACKUP_CONFIG, START, true);
    assertInvalidPair(
        List.of(
            () -> new BackupFailureSnapshot(wrongDatabase, CONFIGURATION, END),
            () -> new BackupFailureSnapshot(DATABASE, wrongConfig, END),
            () -> new BackupFailureSnapshot(DATABASE, sharedId, END),
            () -> new BackupFailureSnapshot(skippedDb, CONFIGURATION, END),
            () -> new BackupFailureSnapshot(DATABASE, skippedConfig, END)));
  }

  /** PT-BAT-BFSVALUE003. */
  @Test
  void pair003MismatchedRunStartAndEarlierEndRejectSeparately() {
    var foreignRun = new BatchRun(new UUID(17, 2), CUTOFF);
    var foreignConfig = attempt(8, foreignRun, BatchStep.BACKUP_CONFIG, START, false);
    var laterConfig = attempt(8, RUN, BatchStep.BACKUP_CONFIG, END, false);
    assertInvalidPair(
        List.of(
            () -> new BackupFailureSnapshot(DATABASE, foreignConfig, END),
            () -> new BackupFailureSnapshot(DATABASE, laterConfig, END),
            () -> new BackupFailureSnapshot(DATABASE, CONFIGURATION, START.minusSeconds(1))));
  }

  /** PT-BAT-BFSVALUE004. */
  @Test
  void pair004RequiredReferencesAndEndPrecisionHaveExplicitBoundaries() {
    for (Executable missing :
        List.<Executable>of(
            () -> new BackupFailureSnapshot(null, CONFIGURATION, END),
            () -> new BackupFailureSnapshot(DATABASE, null, END),
            () -> new BackupFailureSnapshot(DATABASE, CONFIGURATION, null))) {
      assertThrows(NullPointerException.class, missing);
    }
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> new BackupFailureSnapshot(DATABASE, CONFIGURATION, END.plusNanos(1)));
    assertEquals("invalid batch step time", failure.getMessage());
  }

  private static BatchStepAttempt attempt(
      long id, BatchRun run, BatchStep step, Instant started, boolean skipped) {
    return new BatchStepAttempt(id, run, step, 4, started, skipped);
  }

  private static void assertInvalidPair(List<Executable> inputs) {
    for (Executable input : inputs) {
      assertEquals(INVALID_PAIR, assertThrows(IllegalArgumentException.class, input).getMessage());
    }
  }
}
