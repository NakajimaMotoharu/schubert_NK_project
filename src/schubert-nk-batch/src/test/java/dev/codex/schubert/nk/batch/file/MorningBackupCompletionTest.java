package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.repository.BackupStepFixture;
import dev.codex.schubert.nk.batch.repository.BackupStepRepository;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SSC134/ISSCOMP004..006: real operation ordering against independent row/status literals. */
final class MorningBackupCompletionTest {
  static final String MORNING = "a".repeat(32);
  static final BackupManifest MANIFEST = BackupStepFixture.manifest();
  static final Instant END = Instant.parse("2026-09-13T02:00:03Z");
  static final Clock CLOCK = Clock.fixed(END, ZoneOffset.UTC);

  @Test
  void isscomp004ActualSuccessAndRejectionReturnOnlyAfterIndependentReadback() throws Exception {
    for (int code : List.of(0, 1, 30, 255)) {
      var db = new Recorded();
      var archiveCalls = new AtomicInteger();
      var archive =
          MorningProcessMain.archive(
              () -> {
                archiveCalls.incrementAndGet();
                return MANIFEST;
              });
      var receipt = ExpiryReceiptFixture.backupReceipt(code);
      var outcome =
          code == 0
              ? MorningBackupUnitCycle.Outcome.SUCCESS
              : MorningBackupUnitCycle.Outcome.FAILED;
      db.outcome = outcome;
      var result =
          MorningBackupCompletion.complete(
              outcome, receipt, db.begins, db, CLOCK, archive, MORNING, () -> 10_000_000_000L);
      assertEquals(code == 0 ? 1 : 0, archiveCalls.get());
      assertEquals(code == 0 ? 0 : 1, db.failures);
      assertEquals(1, db.reads);
      assertEquals(0, result.localExitCode());
      assertEquals(MORNING, result.morning());
      assertSame(receipt, result.receipt());
      assertEquals(code, result.receipt().exitCode());
      assertEquals(
          code == 0 ? BatchStepResult.Status.SUCCESS : BatchStepResult.Status.FAILED,
          result.rows().current().get(0).result().status());
      result.recheck();
      assertEquals(2, db.reads);
      assertFalse(result.toString().contains(MORNING));
      var threadFailure = new java.util.concurrent.atomic.AtomicReference<Throwable>();
      var thread =
          new Thread(
              () -> {
                try {
                  result.recheck();
                } catch (Throwable e) {
                  threadFailure.set(e);
                }
              });
      thread.start();
      thread.join();
      assertInstanceOf(IOException.class, threadFailure.get());
      db.changed = true;
      assertThrows(IOException.class, result::recheck);
    }
  }

  @Test
  void isscomp005MissingBindingIoUnknownAndNonInvokedProducerCannotComplete() throws Exception {
    var db = new Recorded();
    var receipt = ExpiryReceiptFixture.backupReceipt(0);
    var archive = MorningProcessMain.archive(() -> MANIFEST);
    for (String morning : List.of("0".repeat(32), "A".repeat(32), "7".repeat(32), "short"))
      assertThrows(
          IOException.class,
          () ->
              MorningBackupCompletion.complete(
                  MorningBackupUnitCycle.Outcome.SUCCESS,
                  receipt,
                  db.begins,
                  db,
                  CLOCK,
                  archive,
                  morning,
                  () -> 1));
    assertEquals(0, db.reads);
    assertEquals(0, db.failures);
    assertThrows(
        IOException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.FAILED,
                receipt,
                db.begins,
                db,
                CLOCK,
                archive,
                MORNING,
                () -> 1));
    assertThrows(
        IOException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                ExpiryReceiptFixture.receipt(0),
                db.begins,
                db,
                CLOCK,
                archive,
                MORNING,
                () -> 1));
    assertThrows(
        IOException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                db.begins,
                db,
                CLOCK,
                archive,
                MORNING,
                () -> 0));
    var unknown = new IllegalStateException("PRIVATE_PROGRAMMING");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningBackupCompletion.complete(
                    MorningBackupUnitCycle.Outcome.SUCCESS,
                    receipt,
                    db.begins,
                    db,
                    CLOCK,
                    () -> {
                      throw unknown;
                    },
                    MORNING,
                    () -> 1)));
    var io = new IOException("PRIVATE_CLOSE");
    assertSame(
        io,
        assertThrows(
            IOException.class,
            () ->
                MorningBackupCompletion.complete(
                    MorningBackupUnitCycle.Outcome.SUCCESS,
                    receipt,
                    db.begins,
                    db,
                    CLOCK,
                    () -> {
                      throw io;
                    },
                    MORNING,
                    () -> 1)));
    assertEquals(0, db.reads);
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                null, receipt, db.begins, db, CLOCK, archive, MORNING, () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                null,
                db.begins,
                db,
                CLOCK,
                archive,
                MORNING,
                () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                null,
                db,
                CLOCK,
                archive,
                MORNING,
                () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                db.begins,
                null,
                CLOCK,
                archive,
                MORNING,
                () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                db.begins,
                db,
                null,
                archive,
                MORNING,
                () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                db.begins,
                db,
                CLOCK,
                null,
                MORNING,
                () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                db.begins,
                db,
                CLOCK,
                archive,
                null,
                () -> 1));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupCompletion.complete(
                MorningBackupUnitCycle.Outcome.SUCCESS,
                receipt,
                db.begins,
                db,
                CLOCK,
                archive,
                MORNING,
                null));
  }

  static final class Recorded implements MorningDatabaseSession.Access {
    final MorningDatabaseSession.BackupBegins begins =
        new MorningDatabaseSession.BackupBegins(
            MANIFEST.databaseStep(), MANIFEST.configurationStep());
    MorningBackupUnitCycle.Outcome outcome = MorningBackupUnitCycle.Outcome.SUCCESS;
    int reads;
    int failures;
    boolean changed;

    public void requireUnused(BatchRun run) {
      throw new AssertionError();
    }

    public void requireConsistent(BatchRun run) {
      throw new AssertionError();
    }

    public MorningDatabaseSession.BackupBegins beginBackup(
        BatchRun run, Instant now, boolean recover) {
      throw new AssertionError();
    }

    public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
      throw new AssertionError();
    }

    public void failBackup(
        MorningDatabaseSession.BackupBegins b, Instant end, BatchStepResult d, BatchStepResult c) {
      assertEquals(begins, b);
      assertEquals(END, end);
      assertEquals(BatchStepResult.Status.FAILED, d.status());
      assertEquals(1, d.target());
      assertEquals(0, d.success());
      assertEquals(1, d.failure());
      assertEquals(0, d.bytes());
      assertEquals(d, c);
      failures++;
    }

    public MorningDatabaseSession.BackupObservation observeBackup(
        MorningDatabaseSession.BackupBegins b,
        Optional<BackupManifest> actual,
        Instant now,
        dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) {
      reads++;
      assertEquals(begins, b);
      assertEquals(END, now);
      assertEquals(outcome == MorningBackupUnitCycle.Outcome.SUCCESS, actual.isPresent());
      var list = new ArrayList<BackupStepRepository.Terminal>();
      for (var handle : List.of(b.database(), b.configuration())) {
        boolean failed = outcome == MorningBackupUnitCycle.Outcome.FAILED;
        var result =
            new BatchStepResult(
                failed ? BatchStepResult.Status.FAILED : BatchStepResult.Status.SUCCESS,
                failed ? 1 : handle.step() == BatchStep.BACKUP_DB ? 1 : 2,
                failed ? 0 : handle.step() == BatchStep.BACKUP_DB ? 1 : 2,
                failed ? 1 : 0,
                failed ? 0 : handle.step() == BatchStep.BACKUP_DB ? 26 : 67,
                failed ? BatchStepResult.Reason.COMMAND_FAILURE : BatchStepResult.Reason.NONE);
        list.add(
            new BackupStepRepository.Terminal(
                handle,
                changed ? END.plusSeconds(1) : END,
                result,
                failed ? Optional.of("COMMAND_FAILURE") : Optional.empty(),
                failed ? Optional.of("batch command failed") : Optional.empty()));
      }
      return new MorningDatabaseSession.BackupObservation(list, List.of());
    }
  }
}
