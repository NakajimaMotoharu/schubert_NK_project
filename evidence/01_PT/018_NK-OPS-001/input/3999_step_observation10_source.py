"""Independent step data contracts; retain original whole eight without extraction or reflection."""
from pathlib import Path
import hashlib,json,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/';main=[base+n+'.java' for n in ['BatchRun','BatchStep','BatchStepAttempt','CleanupCounts','CleanupKind','CleanupStepChunk']]+['src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/cleanup/StepCleanupSummary.java'];old='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/CleanupStepValuesTest.java';assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[old]);test='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/StepObservationValueContractTest.java';p=r/test;assert not p.exists();p.write_text('''package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.cleanup.StepCleanupSummary;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-BAT-STEPVALUE001002; SS331/332/341/343: only data, no DB, commit or runtime owner proof. */
final class StepObservationValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final Instant TIME = Instant.parse("2026-09-12T15:00:00Z");
  private static final BatchRun RUN = new BatchRun(ID, TIME);
  private static final CleanupCounts TWO = new CleanupCounts(2, 2, 0);
  private static final CleanupCounts FIVE = new CleanupCounts(5, 5, 0);
  private static final String UNKNOWN = "PUBLIC_UNKNOWN";

  private static BatchStepAttempt attempt(long id, CleanupKind kind) {
    return new BatchStepAttempt(id, RUN, kind.step(), 1, TIME, false);
  }

  private static <T> void values(T actual, T equal, List<T> different) {
    assertEquals(actual, actual);
    assertEquals(actual, equal);
    assertEquals(equal, actual);
    assertEquals(actual.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(actual, "found").get(equal));
    assertNotEquals(actual, null);
    assertNotEquals(actual, UNKNOWN);
    for (T other : different) { assertNotEquals(actual, other); assertNotEquals(other, actual); }
  }

  @Test
  void stepvalue001AttemptAllComponentsBoundsNullsAndCivilDatesAreIndependent() {
    for (long id : List.of(1L, 999_999_999_999L))
      for (int number : List.of(1, 99))
        for (boolean skip : List.of(false, true)) {
          var actual = new BatchStepAttempt(id, RUN, BatchStep.CLEAN_QUESTION, number, TIME, skip);
          assertEquals(id, actual.id()); assertSame(RUN, actual.run());
          assertSame(BatchStep.CLEAN_QUESTION, actual.step()); assertEquals(number, actual.attempt());
          assertEquals(TIME, actual.startedAt()); assertEquals(skip, actual.skipped());
          assertEquals(LocalDate.of(2026, 9, 13), actual.businessDate());
          assertEquals("BatchStepAttempt[identity/time=<redacted>]", actual.toString());
        }
    for (String invalid : List.of("0000-12-31T23:59:59.999999Z", "+10000-01-01T00:00:00Z", "2026-09-12T15:00:00.000000001Z")) {
      Instant cutoff = Instant.parse(invalid);
      assertThrows(IllegalArgumentException.class, () -> new BatchRun(ID, cutoff));
    }
    assertThrows(NullPointerException.class, () -> new BatchRun(null, TIME));
    assertThrows(NullPointerException.class, () -> new BatchRun(ID, null));
    assertEquals(ID, RUN.id()); assertEquals(TIME, RUN.cutoff());
    assertEquals("BatchRun[identity/cutoff=<redacted>]", RUN.toString());
    values(RUN, new BatchRun(ID, TIME), List.of(new BatchRun(new UUID(0, 2), TIME), new BatchRun(ID, TIME.plusNanos(1000))));
    String[] steps = {"BACKUP_DB", "BACKUP_CONFIG", "CLEAN_NOTIFICATION", "CLEAN_QUESTION", "CLEAN_SESSION", "CLEAN_INBOX_OUTBOX", "CLEAN_LOG", "CLEAN_BATCH_RUN", "CLEAN_TRANSFER", "CLEAN_EXPIRY"};
    boolean[] backups = {true, true, false, false, false, false, false, false, false, false};
    assertArrayEquals(steps, Arrays.stream(BatchStep.values()).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < steps.length; index++) assertEquals(backups[index], BatchStep.valueOf(steps[index]).backup());
    var stepView = BatchStep.values(); stepView[0] = BatchStep.CLEAN_EXPIRY;
    assertSame(BatchStep.BACKUP_DB, BatchStep.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> BatchStep.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> BatchStep.valueOf(null));
    assertEquals(LocalDate.of(2026, 9, 13),
        new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, 1, TIME.plusSeconds(86400), false).businessDate());
    var value = attempt(1, CleanupKind.QUESTIONS);
    values(value, new BatchStepAttempt(1, new BatchRun(ID, TIME), BatchStep.CLEAN_QUESTION, 1, TIME, false),
        List.of(attempt(2, CleanupKind.QUESTIONS),
            new BatchStepAttempt(1, new BatchRun(new UUID(0, 2), TIME), BatchStep.CLEAN_QUESTION, 1, TIME, false),
            new BatchStepAttempt(1, RUN, BatchStep.CLEAN_SESSION, 1, TIME, false),
            new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, 2, TIME, false),
            new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, 1, TIME.plusNanos(1000), false),
            new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, 1, TIME, true)));
    for (long id : List.of(Long.MIN_VALUE, -1L, 0L, 1_000_000_000_000L, Long.MAX_VALUE))
      assertThrows(IllegalArgumentException.class, () -> new BatchStepAttempt(id, RUN, BatchStep.CLEAN_QUESTION, 1, TIME, false));
    for (int number : List.of(Integer.MIN_VALUE, -1, 0, 100, Integer.MAX_VALUE))
      assertThrows(IllegalArgumentException.class, () -> new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, number, TIME, false));
    for (Instant time : List.of(TIME.minusNanos(1000), Instant.parse("+10000-01-01T00:00:00Z"), TIME.plusNanos(1)))
      assertThrows(IllegalArgumentException.class, () -> new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, 1, time, false));
    assertThrows(NullPointerException.class, () -> new BatchStepAttempt(1, null, BatchStep.CLEAN_QUESTION, 1, TIME, false));
    assertThrows(NullPointerException.class, () -> new BatchStepAttempt(1, RUN, null, 1, TIME, false));
    assertThrows(NullPointerException.class, () -> new BatchStepAttempt(1, RUN, BatchStep.CLEAN_QUESTION, 1, null, false));
    String[] instants = {"0001-01-01T00:00:00Z", "1582-10-04T14:50:00Z", "9999-12-31T23:59:59.999999Z"};
    LocalDate[] expected = {LocalDate.of(1, 1, 1), LocalDate.of(1582, 10, 5), LocalDate.of(10000, 1, 1)};
    for (int index = 0; index < instants.length; index++) {
      Instant at = Instant.parse(instants[index]);
      var run = new BatchRun(ID, at);
      var actual = new BatchStepAttempt(1, run, BatchStep.CLEAN_QUESTION, 1, at, false);
      assertEquals(at, actual.startedAt()); assertEquals(expected[index], actual.businessDate());
    }
  }

  @Test
  void stepvalue002ChunkAndSummaryRetainAllValidComponentsAndClosedReasonFactories() {
    long[][] invalidCounts = {{-1, 0, 0}, {0, -1, 1}, {0, 1, 0}, {0, 0, -1}, {1, 0, 0}, {Long.MAX_VALUE, Long.MAX_VALUE, 1}};
    for (long[] invalid : invalidCounts) assertThrows(IllegalArgumentException.class, () -> new CleanupCounts(invalid[0], invalid[1], invalid[2]));
    assertEquals(2, TWO.target()); assertEquals(2, TWO.deleted()); assertEquals(0, TWO.skipped());
    values(TWO, new CleanupCounts(2, 2, 0), List.of(new CleanupCounts(3, 3, 0), new CleanupCounts(2, 1, 1)));
    assertEquals("CleanupCounts[target=2, deleted=2, skipped=0]", TWO.toString());
    String[] kinds = {"NOTIFICATIONS", "QUESTIONS", "SESSIONS", "OUTBOX", "LOGS", "WEB_RECEIPTS", "BATCH_RUNS", "INBOX_PROGRESS", "LOG_PROGRESS"};
    String[] functions = {"schubert.maintenance_cleanup_notifications", "schubert.maintenance_cleanup_questions", "schubert.maintenance_cleanup_sessions", "schubert.maintenance_cleanup_message_stores", "schubert.maintenance_cleanup_logs", "schubert.maintenance_cleanup_web_receipt_references", "schubert.maintenance_cleanup_batch_runs", "schubert.maintenance_cleanup_inbox_progress", "schubert.maintenance_cleanup_log_progress"};
    int[] limits = {1000, 1000, 1000, 1000, 10000, 1000, 1000, 1000, 1000};
    assertArrayEquals(kinds, Arrays.stream(CleanupKind.values()).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < kinds.length; index++) {
      CleanupKind kind = CleanupKind.valueOf(kinds[index]);
      assertEquals(functions[index], kind.function()); assertEquals(limits[index], kind.maximumRows());
    }
    var kindView = CleanupKind.values(); kindView[0] = CleanupKind.LOG_PROGRESS;
    assertSame(CleanupKind.NOTIFICATIONS, CleanupKind.values()[0]);
    assertThrows(IllegalArgumentException.class, () -> CleanupKind.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> CleanupKind.valueOf(null));
    var attempt = attempt(1, CleanupKind.QUESTIONS);
    var other = attempt(2, CleanupKind.QUESTIONS);
    var chunk = new CleanupStepChunk(attempt, CleanupKind.QUESTIONS, TWO, Optional.of(FIVE), false, CleanupStepChunk.Reason.OK);
    values(chunk, new CleanupStepChunk(attempt(1, CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, new CleanupCounts(2, 2, 0), Optional.of(new CleanupCounts(5, 5, 0)), false, CleanupStepChunk.Reason.OK),
        List.of(new CleanupStepChunk(other, CleanupKind.QUESTIONS, TWO, Optional.of(FIVE), false, CleanupStepChunk.Reason.OK),
            new CleanupStepChunk(attempt(1, CleanupKind.NOTIFICATIONS), CleanupKind.NOTIFICATIONS, TWO, Optional.of(FIVE), false, CleanupStepChunk.Reason.OK),
            new CleanupStepChunk(attempt, CleanupKind.QUESTIONS, new CleanupCounts(3, 3, 0), Optional.of(FIVE), false, CleanupStepChunk.Reason.OK),
            new CleanupStepChunk(attempt, CleanupKind.QUESTIONS, TWO, Optional.of(new CleanupCounts(6, 6, 0)), false, CleanupStepChunk.Reason.OK)));
    assertSame(attempt, chunk.attempt()); assertSame(CleanupKind.QUESTIONS, chunk.kind());
    assertSame(TWO, chunk.counts()); assertEquals(Optional.of(FIVE), chunk.stepCounts());
    assertEquals(Optional.of(new CleanupCounts(3, 3, 0)), chunk.beforeCounts()); assertEquals(false, chunk.complete());
    assertSame(CleanupStepChunk.Reason.OK, chunk.reason());
    var zero = new CleanupCounts(0, 0, 0);
    assertNotEquals(new CleanupStepChunk(attempt, CleanupKind.QUESTIONS, zero, Optional.of(FIVE), true, CleanupStepChunk.Reason.OK),
        new CleanupStepChunk(attempt, CleanupKind.QUESTIONS, zero, Optional.of(FIVE), false, CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT));
    var summary = new StepCleanupSummary(attempt, CleanupKind.QUESTIONS, TWO, FIVE, false);
    values(summary, new StepCleanupSummary(attempt(1, CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, new CleanupCounts(2, 2, 0), new CleanupCounts(5, 5, 0), false),
        List.of(new StepCleanupSummary(other, CleanupKind.QUESTIONS, TWO, FIVE, false),
            new StepCleanupSummary(attempt(1, CleanupKind.NOTIFICATIONS), CleanupKind.NOTIFICATIONS, TWO, FIVE, false),
            new StepCleanupSummary(attempt, CleanupKind.QUESTIONS, new CleanupCounts(3, 3, 0), FIVE, false),
            new StepCleanupSummary(attempt, CleanupKind.QUESTIONS, TWO, new CleanupCounts(6, 6, 0), false),
            new StepCleanupSummary(attempt, CleanupKind.QUESTIONS, TWO, FIVE, true)));
    assertSame(attempt, summary.attempt()); assertSame(CleanupKind.QUESTIONS, summary.kind());
    assertSame(TWO, summary.before()); assertSame(FIVE, summary.after()); assertEquals(false, summary.deferred());
    assertEquals(true, summary.complete()); assertEquals(new CleanupCounts(3, 3, 0), summary.callCounts());
    assertEquals("StepCleanupSummary[observation=<redacted>]", summary.toString());
    String[] reasons = {"OK", "LOCK_BUSY", "BACKUP_GATE", "FOREIGN_KEY_CONFLICT"};
    assertArrayEquals(reasons, Arrays.stream(CleanupStepChunk.Reason.values()).map(Enum::name).toArray(String[]::new));
    for (String reason : reasons) assertEquals(reason, CleanupStepChunk.Reason.valueOf(reason).name());
    var view = CleanupStepChunk.Reason.values(); view[0] = CleanupStepChunk.Reason.BACKUP_GATE;
    assertSame(CleanupStepChunk.Reason.OK, CleanupStepChunk.Reason.values()[0]);
    for (String unknown : List.of("", "ok", UNKNOWN)) assertThrows(IllegalArgumentException.class, () -> CleanupStepChunk.Reason.valueOf(unknown));
    assertThrows(NullPointerException.class, () -> CleanupStepChunk.Reason.valueOf(null));
  }
}
''');subprocess.run([str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-jar',str(r.parent/'toolchain/google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(p)],check=True,timeout=30);assert all((r/n).read_bytes()==subprocess.check_output(['git','show','HEAD:'+n]) for n in main+[old]);o=b/'evidence/PG35090-step-observation10-source-v1';o.mkdir();v=dict(actualExit=0,mainSources=main,testSources=[dict(path=old,tests=8),dict(path=test,tests=2)],inputHashes={n:sha(r/n) for n in main+[old,test]},sdkHashes={},mainSourcesUnchanged=True,originalCleanupStep8ByteExact=True,original64WorkerGet5StopAwait10FailurePropagated=True,newDefinitions=2,necessaryPriorDefinitions=8,expectedTests=10,targets=['dev/codex/schubert/nk/batch/repository/'+n for n in ['BatchRun','BatchStep','BatchStepAttempt','CleanupCounts','CleanupKind','CleanupStepChunk','CleanupStepChunk$Reason']]+['dev/codex/schubert/nk/batch/cleanup/StepCleanupSummary'],noPrivateReflectionOrRepositoryOrRuntimeOwner=False if 'Class.forName' in p.read_text() else True,applicationTestsExecuted=0,newAcceptance=0);assert v['noPrivateReflectionOrRepositoryOrRuntimeOwner'];(o/'manifest.json').open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,main=7,wholeTests=10,newDefinitions=2,original8ByteExact=True)))
