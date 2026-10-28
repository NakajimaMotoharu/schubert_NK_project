package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/SSC115/BUG325/YKT257; PT-OPS-MMAIN009-010. */
final class MorningBackupObservedCompletionTest {
  private static final String FIXTURE_UNUSED_PORT_4AA9831A = "unused port";
  private static final Instant BEGIN = Instant.parse("2026-09-30T03:30:00Z");

  private static MorningDatabaseSession.BackupBegins begins() {
    var run =
        new BatchRun(
            UUID.fromString("38600001-2222-4333-8444-555555555555"), BEGIN.minusSeconds(60));
    return new MorningDatabaseSession.BackupBegins(
        new BatchStepAttempt(31, run, BatchStep.BACKUP_DB, 2, BEGIN, false),
        new BatchStepAttempt(32, run, BatchStep.BACKUP_CONFIG, 2, BEGIN, false));
  }

  @Test
  void mmain009KnownFailureRecordsLiteralResultAndSuccessOnlyGeneratesArtifacts() throws Exception {
    var db = new Recorded();
    var input = begins();
    var archive = new AtomicInteger();
    var clock = Clock.fixed(Instant.parse("2026-09-30T03:30:01.123456789Z"), ZoneOffset.UTC);
    MorningProcessMain.completeObservedBackup(
        MorningBackupUnitCycle.Outcome.SUCCESS, input, db, clock, archive::incrementAndGet);
    assertEquals(1, archive.get());
    assertEquals(0, db.calls);
    MorningProcessMain.completeObservedBackup(
        MorningBackupUnitCycle.Outcome.FAILED, input, db, clock, archive::incrementAndGet);
    assertEquals(1, archive.get());
    assertEquals(1, db.calls);
    assertSame(input, db.input);
    assertEquals("2026-09-30T03:30:01.123456Z", db.ended.toString());
    for (var r : new BatchStepResult[] {db.database, db.configuration}) {
      assertEquals(BatchStepResult.Status.FAILED, r.status());
      assertEquals(1, r.target());
      assertEquals(0, r.success());
      assertEquals(1, r.failure());
      assertEquals(0, r.bytes());
      assertEquals(BatchStepResult.Reason.COMMAND_FAILURE, r.reason());
    }
    var atBoundary = new Recorded();
    MorningProcessMain.completeObservedBackup(
        MorningBackupUnitCycle.Outcome.FAILED,
        input,
        atBoundary,
        Clock.fixed(BEGIN, ZoneOffset.UTC),
        () -> fail("archive on failure"));
    assertEquals(BEGIN, atBoundary.ended);
  }

  @Test
  void mmain010NullClockReverseIoAndUnknownCannotBecomeSuccessfulCompletion() throws Exception {
    var db = new Recorded();
    var input = begins();
    var clock = Clock.fixed(BEGIN, ZoneOffset.UTC);
    var outcome = MorningBackupUnitCycle.Outcome.FAILED;
    var archive = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            MorningProcessMain.completeObservedBackup(
                null, input, db, clock, archive::incrementAndGet));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningProcessMain.completeObservedBackup(
                outcome, null, db, clock, archive::incrementAndGet));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningProcessMain.completeObservedBackup(
                outcome, input, null, clock, archive::incrementAndGet));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningProcessMain.completeObservedBackup(
                outcome, input, db, null, archive::incrementAndGet));
    assertThrows(
        NullPointerException.class,
        () -> MorningProcessMain.completeObservedBackup(outcome, input, db, clock, null));
    assertThrows(
        IOException.class,
        () ->
            MorningProcessMain.completeObservedBackup(
                outcome,
                input,
                db,
                Clock.fixed(BEGIN.minusNanos(1000), ZoneOffset.UTC),
                archive::incrementAndGet));
    assertEquals(0, db.calls);
    assertEquals(0, archive.get());
    var denied = new IOException("private DB diagnostic");
    db.denied = denied;
    assertSame(
        denied,
        assertThrows(
            IOException.class,
            () ->
                MorningProcessMain.completeObservedBackup(
                    outcome, input, db, clock, archive::incrementAndGet)));
    assertEquals(1, db.calls);
    assertEquals(0, archive.get());
    var unknown = new IllegalStateException("programming failure");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningProcessMain.completeObservedBackup(
                    MorningBackupUnitCycle.Outcome.SUCCESS,
                    input,
                    db,
                    clock,
                    () -> {
                      throw unknown;
                    })));
    assertEquals(1, db.calls);
    Clock absent =
        new Clock() {
          public ZoneId getZone() {
            return ZoneOffset.UTC;
          }

          public Clock withZone(ZoneId zone) {
            return this;
          }

          public Instant instant() {
            return null;
          }
        };
    assertThrows(
        NullPointerException.class,
        () ->
            MorningProcessMain.completeObservedBackup(
                outcome, input, db, absent, archive::incrementAndGet));
    assertEquals(1, db.calls);
    assertEquals(0, archive.get());
  }

  private static final class Recorded implements MorningDatabaseSession.Access {
    int calls;
    MorningDatabaseSession.BackupBegins input;
    Instant ended;
    BatchStepResult database;
    BatchStepResult configuration;
    IOException denied;

    public void requireUnused(BatchRun run) {
      throw new AssertionError(FIXTURE_UNUSED_PORT_4AA9831A);
    }

    public void requireConsistent(BatchRun run) {
      throw new AssertionError(FIXTURE_UNUSED_PORT_4AA9831A);
    }

    public MorningDatabaseSession.BackupBegins beginBackup(
        BatchRun run, Instant now, boolean recover) {
      throw new AssertionError(FIXTURE_UNUSED_PORT_4AA9831A);
    }

    public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
      throw new AssertionError(FIXTURE_UNUSED_PORT_4AA9831A);
    }

    public void failBackup(
        MorningDatabaseSession.BackupBegins expected,
        Instant end,
        BatchStepResult d,
        BatchStepResult c)
        throws IOException {
      calls++;
      input = expected;
      ended = end;
      database = d;
      configuration = c;
      if (denied != null) throw denied;
    }
  }
}
