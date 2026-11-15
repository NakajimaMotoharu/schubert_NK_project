package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** BATCH-DATA001..004; SS331/332/341/343: public data only, never a commit or owner certificate. */
final class BatchRepositoryValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final UUID OTHER_ID = new UUID(0, 2);
  private static final Instant TIME = Instant.parse("2026-09-12T15:00:00Z");
  private static final BatchRun RUN = new BatchRun(ID, TIME);
  private static final CleanupCounts COUNTS = new CleanupCounts(3, 2, 1);
  private static final String EXPECTED_CLEAN_BATCH_RUN = "CLEAN_BATCH_RUN";
  private static final String UNKNOWN = "PUBLIC_UNKNOWN";

  private static <T> void values(T value, T equal, List<T> different) {
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, UNKNOWN);
    for (T other : different) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }

  @Test
  void batchdata001RunAndActivationEqualityKeepAllIdentityAndCutoffComponents() {
    values(
        RUN,
        new BatchRun(ID, TIME),
        List.of(new BatchRun(OTHER_ID, TIME), new BatchRun(ID, TIME.plusSeconds(1))));
    var activation = new MaintenanceActivation(RUN, ID);
    values(
        activation,
        new MaintenanceActivation(new BatchRun(ID, TIME), ID),
        List.of(
            new MaintenanceActivation(new BatchRun(OTHER_ID, TIME), ID),
            new MaintenanceActivation(RUN, OTHER_ID)));
    assertSame(RUN, activation.run());
    assertEquals(ID, activation.id());
  }

  @Test
  void batchdata002CleanupValuesAndClosedMetadataHaveIndependentLiteralContracts() {
    values(
        COUNTS,
        new CleanupCounts(3, 2, 1),
        List.of(new CleanupCounts(3, 1, 2), new CleanupCounts(4, 2, 2)));
    assertEquals("CleanupCounts[target=3, deleted=2, skipped=1]", COUNTS.toString());
    var chunk = new CleanupChunk(COUNTS, CleanupReason.OK);
    values(
        chunk,
        new CleanupChunk(new CleanupCounts(3, 2, 1), CleanupReason.OK),
        List.of(new CleanupChunk(new CleanupCounts(4, 2, 2), CleanupReason.OK)));
    assertSame(COUNTS, chunk.counts());
    assertSame(CleanupReason.OK, chunk.reason());
    assertEquals(
        "CleanupChunk[counts=CleanupCounts[target=3, deleted=2, skipped=1], reason=OK]",
        chunk.toString());
    var empty = new CleanupCounts(0, 0, 0);
    values(
        new CleanupChunk(empty, CleanupReason.LOCK_BUSY),
        new CleanupChunk(empty, CleanupReason.LOCK_BUSY),
        List.of(new CleanupChunk(empty, CleanupReason.BACKUP_GATE)));
    for (CleanupReason reason : List.of(CleanupReason.LOCK_BUSY, CleanupReason.BACKUP_GATE)) {
      assertThrows(IllegalArgumentException.class, () -> new CleanupChunk(COUNTS, reason));
      assertSame(reason, new CleanupChunk(empty, reason).reason());
    }
    assertThrows(NullPointerException.class, () -> new CleanupChunk(null, CleanupReason.OK));
    assertThrows(NullPointerException.class, () -> new CleanupChunk(COUNTS, null));
    String[] reasons = {"OK", "LOCK_BUSY", "BACKUP_GATE"};
    assertArrayEquals(
        reasons, Arrays.stream(CleanupReason.values()).map(Enum::name).toArray(String[]::new));
    for (String reason : reasons) assertEquals(reason, CleanupReason.valueOf(reason).name());
    var reasonView = CleanupReason.values();
    reasonView[0] = CleanupReason.BACKUP_GATE;
    assertSame(CleanupReason.OK, CleanupReason.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> CleanupReason.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> CleanupReason.valueOf(null));
    String[] steps = {
      "BACKUP_DB",
      "BACKUP_CONFIG",
      "CLEAN_NOTIFICATION",
      "CLEAN_QUESTION",
      "CLEAN_SESSION",
      "CLEAN_INBOX_OUTBOX",
      "CLEAN_LOG",
      EXPECTED_CLEAN_BATCH_RUN,
      "CLEAN_TRANSFER",
      "CLEAN_EXPIRY"
    };
    boolean[] backups = {true, true, false, false, false, false, false, false, false, false};
    assertArrayEquals(
        steps, Arrays.stream(BatchStep.values()).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < steps.length; index++)
      assertEquals(backups[index], BatchStep.valueOf(steps[index]).backup());
    var stepView = BatchStep.values();
    stepView[0] = BatchStep.CLEAN_EXPIRY;
    assertSame(BatchStep.BACKUP_DB, BatchStep.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> BatchStep.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> BatchStep.valueOf(null));
    String[] kinds = {
      "NOTIFICATIONS",
      "QUESTIONS",
      "SESSIONS",
      "OUTBOX",
      "LOGS",
      "WEB_RECEIPTS",
      "BATCH_RUNS",
      "INBOX_PROGRESS",
      "LOG_PROGRESS"
    };
    String[] parentSteps = {
      "CLEAN_NOTIFICATION",
      "CLEAN_QUESTION",
      "CLEAN_SESSION",
      "CLEAN_INBOX_OUTBOX",
      "CLEAN_LOG",
      EXPECTED_CLEAN_BATCH_RUN,
      EXPECTED_CLEAN_BATCH_RUN,
      EXPECTED_CLEAN_BATCH_RUN,
      EXPECTED_CLEAN_BATCH_RUN
    };
    assertArrayEquals(
        kinds, Arrays.stream(CleanupKind.values()).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < kinds.length; index++)
      assertEquals(parentSteps[index], CleanupKind.valueOf(kinds[index]).step().name());
    var kindView = CleanupKind.values();
    kindView[0] = CleanupKind.LOG_PROGRESS;
    assertSame(CleanupKind.NOTIFICATIONS, CleanupKind.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> CleanupKind.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> CleanupKind.valueOf(null));
  }

  @Test
  void batchdata003RunReferencesUseAnIndependentSixteenRowTruthTable() {
    // history, inbox, logs, identity-consistent, valid, any-reference.
    boolean[][] rows = {
      {false, false, false, false, false, false}, {false, false, false, true, true, false},
      {false, false, true, false, true, true}, {false, false, true, true, true, true},
      {false, true, false, false, true, true}, {false, true, false, true, true, true},
      {false, true, true, false, true, true}, {false, true, true, true, true, true},
      {true, false, false, false, true, true}, {true, false, false, true, true, true},
      {true, false, true, false, true, true}, {true, false, true, true, true, true},
      {true, true, false, false, true, true}, {true, true, false, true, true, true},
      {true, true, true, false, true, true}, {true, true, true, true, true, true}
    };
    for (boolean[] row : rows) {
      if (!row[4]) {
        assertThrows(
            IllegalArgumentException.class,
            () -> new RunReferences(row[0], row[1], row[2], row[3]));
        continue;
      }
      var actual = new RunReferences(row[0], row[1], row[2], row[3]);
      assertEquals(row[0], actual.hasBatchHistory());
      assertEquals(row[1], actual.hasInboxProgress());
      assertEquals(row[2], actual.hasLogProgress());
      assertEquals(row[3], actual.identityConsistent());
      assertEquals(row[5], actual.anyReference());
      values(actual, new RunReferences(row[0], row[1], row[2], row[3]), List.of());
      assertEquals("RunReferences[observation=<redacted>]", actual.toString());
    }
    values(
        new RunReferences(false, false, false, true),
        new RunReferences(false, false, false, true),
        List.of(
            new RunReferences(true, false, false, true),
            new RunReferences(false, true, false, true),
            new RunReferences(false, false, true, true)));
    assertNotEquals(
        new RunReferences(true, false, false, true), new RunReferences(true, false, false, false));
  }

  @Test
  void batchdata004InspectionAndLogProgressRemainDataWithNullContractsAndNoImplicitCommit() {
    var inspection = new InspectionSummary(RUN, COUNTS, true);
    values(
        inspection,
        new InspectionSummary(new BatchRun(ID, TIME), new CleanupCounts(3, 2, 1), true),
        List.of(
            new InspectionSummary(new BatchRun(OTHER_ID, TIME), COUNTS, true),
            new InspectionSummary(RUN, new CleanupCounts(4, 2, 2), true),
            new InspectionSummary(RUN, COUNTS, false)));
    assertSame(RUN, inspection.run());
    assertSame(COUNTS, inspection.counts());
    assertEquals(true, inspection.complete());
    assertEquals("InspectionSummary[observation=<redacted>]", inspection.toString());
    var progress = new LogCleanupProgress(RUN, COUNTS, true);
    values(
        progress,
        new LogCleanupProgress(new BatchRun(ID, TIME), new CleanupCounts(3, 2, 1), true),
        List.of(
            new LogCleanupProgress(new BatchRun(OTHER_ID, TIME), COUNTS, true),
            new LogCleanupProgress(RUN, new CleanupCounts(4, 2, 2), true),
            new LogCleanupProgress(RUN, COUNTS, false)));
    assertSame(RUN, progress.run());
    assertSame(COUNTS, progress.counts());
    assertEquals(true, progress.complete());
    assertEquals(
        "LogCleanupProgress[run=BatchRun[identity/cutoff=<redacted>], counts=CleanupCounts[target=3, deleted=2, skipped=1], complete=true]",
        progress.toString());
    assertThrows(NullPointerException.class, () -> new InspectionSummary(null, COUNTS, true));
    assertThrows(NullPointerException.class, () -> new InspectionSummary(RUN, null, true));
    assertThrows(NullPointerException.class, () -> new LogCleanupProgress(null, COUNTS, true));
    assertThrows(NullPointerException.class, () -> new LogCleanupProgress(RUN, null, true));
  }
}
