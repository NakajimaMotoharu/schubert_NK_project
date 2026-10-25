package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.RUN;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.locked;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.query;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.reset;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.sql;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.cleanup.InspectionAttempt;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** CEXEC host ordering/real PG only. Synthetic Unit ports are NEVER native acceptance/coverage. */
final class CleanupMaintenanceWorkTest {
  @TempDir static Path temporary;
  private static BatchDatabaseFixture db;
  private static final UUID BOOT = UUID.fromString("31100027-3333-4333-8444-555555555555");
  private static final MaintenanceOwnerFrame OWNER =
      new MaintenanceOwnerFrame(
          BOOT,
          RUN.id(),
          UUID.fromString("31100027-6666-4777-8888-999999999999"),
          RUN.cutoff(),
          UUID.fromString("31100027-4444-4333-8444-555555555555"),
          new MaintenanceOwnerFrame.Parent("1".repeat(32), 200, 100),
          Optional.empty(),
          1800000000001L);
  private static final RootStartupContext.Snapshot CLAIM =
      new RootStartupContext.Snapshot(
          RootStartupContext.Service.CLEANUP,
          BOOT.toString(),
          "2".repeat(32),
          300,
          200,
          1,
          "/system.slice/schubert-nk-cleanup.service");

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(temporary);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    reset(db);
    try (var c = db.admin()) {
      sql(c, "delete from schubert.app_logs");
      sql(c, "select setval(pg_get_serial_sequence('schubert.batch_runs','id'),90020,true)");
    }
  }

  private CleanupMaintenanceWork work(
      CleanupMaintenanceWork.Inbox inbox, CleanupMaintenanceWork.Transfer transfer) {
    return new CleanupMaintenanceWork(
        RootStartupContext.create(), CLAIM, OWNER, () -> 10_000_000_000L, inbox, transfer);
  }

  private static BatchStepResult transferResult() {
    return new BatchStepResult(
        BatchStepResult.Status.SUCCESS, 2, 2, 0, 5, BatchStepResult.Reason.NONE);
  }

  @Test
  void failedBackupPreservesEveryDeletionTableAndExecutesTransferWithActualSixSkips()
      throws Exception {
    var transfers = new AtomicInteger();
    var job =
        work(
            (c, completed) -> fail("failed Backup must never launch Inspector"),
            () -> {
              transfers.incrementAndGet();
              return transferResult();
            });
    try (var c = locked(db, true);
        var admin = db.admin()) {
      var before = new LinkedHashMap<String, String>();
      for (String table :
          List.of(
              "notifications",
              "questions",
              "answers",
              "auth_sessions",
              "request_inbox",
              "mq_outbox",
              "app_logs",
              "inbox_inspection_progress",
              "log_cleanup_progress"))
        before.put(table, query(admin, "select count(*) from schubert." + table));
      assertEquals(0, job.executeFailed(c));
      assertEquals(1, transfers.get());
      for (var entry : before.entrySet())
        assertEquals(
            entry.getValue(),
            query(admin, "select count(*) from schubert." + entry.getKey()),
            entry.getKey());
      assertEquals(
          "6",
          query(
              admin,
              "select count(*) from schubert.batch_runs where id between 90021 and 90026 and status='SKIPPED' and started_at=ended_at and target_count=0 and success_count=0 and failure_count=0 and byte_count=0 and error_code='BACKUP_UNAVAILABLE' and error_summary='verified backup unavailable'"));
      assertEquals(
          "SUCCESS|2|2|0|5",
          query(
              admin,
              "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count from schubert.batch_runs where id=90027"));
      c.setAutoCommit(false);
      var terminal = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      var observedAt = java.time.Instant.now().truncatedTo(java.time.temporal.ChronoUnit.MICROS);
      var observed = terminal.readBackupUnavailable(RUN, observedAt);
      assertEquals(7, observed.entries().size());
      assertEquals(0, observed.exitCode());
      assertThrows(BatchRepositoryException.class, () -> terminal.read(RUN, observedAt));
      assertEquals(
          7,
          terminal.readRejected(RUN, observedAt).entries().stream()
              .filter(Optional::isPresent)
              .count());
      c.rollback();
      c.setAutoCommit(true);
      assertEquals(0, job.executeFailed(c));
      assertEquals(
          1,
          transfers.get()); // Previously successful Transfer is genuine current ALREADY_SUCCESSFUL.
      assertEquals(
          "6",
          query(
              admin,
              "select count(*) from schubert.batch_runs where id between 90028 and 90033 and error_code='BACKUP_UNAVAILABLE' and status='SKIPPED'"));
    }
  }

  @Test
  void actualSqlOrderAllSevenTerminalsThenCurrentSkipIsNotOldSuccess() throws Exception {
    var events = new ArrayList<String>();
    var job =
        work(
            (c, completion) -> {
              events.add("inspection");
              completion.execute(
                  new InspectionAttempt(
                      RUN,
                      new CleanupCounts(0, 0, 0),
                      new CleanupCounts(0, 0, 0),
                      MaintenanceCompletion.Outcome.SUCCESS));
              try (var admin = db.admin()) {
                assertEquals(
                    "SUCCESS|2|2|0|0",
                    query(
                        admin,
                        "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count from schubert.batch_runs where id=90024"));
              } catch (java.sql.SQLException failure) {
                throw new IOException("fixture SQL failed");
              }
              events.add("retirement-after-outbox-readback");
            },
            () -> {
              events.add("transfer");
              return transferResult();
            });
    try (var c = locked(db, true);
        var admin = db.admin()) {
      assertEquals(0, job.execute(c));
      assertEquals(List.of("inspection", "retirement-after-outbox-readback", "transfer"), events);
      String[] counts = {
        "1|1|0|0", "1|1|0|0", "3|3|0|0", "2|2|0|0", "0|0|0|0", "3|3|0|0", "2|2|0|5"
      };
      for (int index = 0; index < 7; index++) {
        assertEquals(
            "SUCCESS|" + counts[index],
            query(
                admin,
                "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count from schubert.batch_runs where id="
                    + (90021 + index)));
      }
      var again =
          work(
              (connection, complete) -> fail("already-successful Inspector must not run"),
              () -> {
                fail("already-successful Transfer must not run");
                return transferResult();
              });
      assertEquals(0, again.execute(c));
      assertEquals(
          "7",
          query(
              admin,
              "select count(*) from schubert.batch_runs where id between 90028 and 90034 and status='SKIPPED' and target_count=0 and success_count=0 and failure_count=0 and byte_count=0 and error_code='ALREADY_SUCCESSFUL' and started_at=ended_at"));
      assertEquals(
          "7",
          query(
              admin,
              "select count(*) from schubert.batch_runs where id between 90021 and 90027 and status='SUCCESS'"));
    }
  }

  @Test
  void protectedInspectionWarnsWithAttemptDeltaAndNoInventedFailure() throws Exception {
    var job =
        work(
            (c, complete) ->
                complete.execute(
                    new InspectionAttempt(
                        RUN,
                        new CleanupCounts(11, 9, 2),
                        new CleanupCounts(1, 0, 1),
                        MaintenanceCompletion.Outcome.WARNING)),
            CleanupMaintenanceWorkTest::transferResult);
    try (var c = locked(db, true);
        var admin = db.admin()) {
      assertEquals(10, job.execute(c));
      assertEquals(
          "WARNING|3|2|0|PROTECTED_RECORDS",
          query(
              admin,
              "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||error_code from schubert.batch_runs where id=90024"));
    }
  }

  @Test
  void missingOrRepeatedInspectionAndParentFailureCannotFinishWholeCleanup() throws Exception {
    var calls = new AtomicInteger();
    try (var c = locked(db, true);
        var admin = db.admin()) {
      var job =
          work(
              (connection, completion) -> {},
              () -> {
                calls.incrementAndGet();
                return transferResult();
              });
      assertThrows(IOException.class, () -> job.execute(c));
      assertEquals(0, calls.get());
      assertEquals(
          "RUNNING", query(admin, "select status from schubert.batch_runs where id=90024"));
      assertEquals(
          "0",
          query(admin, "select count(*) from schubert.batch_runs where step='CLEAN_TRANSFER'"));
    }
    seed();
    var twice =
        work(
            (connection, completion) -> {
              var result =
                  new InspectionAttempt(
                      RUN,
                      new CleanupCounts(0, 0, 0),
                      new CleanupCounts(0, 0, 0),
                      MaintenanceCompletion.Outcome.SUCCESS);
              completion.execute(result);
              completion.execute(result);
            },
            CleanupMaintenanceWorkTest::transferResult);
    try (var c = locked(db, true)) {
      assertThrows(IOException.class, () -> twice.execute(c));
    }
    seed();
    var denied =
        new CleanupMaintenanceWork(
            RootStartupContext.create(),
            CLAIM,
            OWNER,
            () -> {
              throw new IOException("PRIVATE");
            },
            (c, completed) -> fail("owner not admitted"),
            CleanupMaintenanceWorkTest::transferResult);
    try (var c = locked(db, true);
        var admin = db.admin()) {
      assertThrows(IOException.class, () -> denied.execute(c));
      assertEquals("0", query(admin, "select count(*) from schubert.batch_runs where id>90020"));
    }
    assertThrows(
        NullPointerException.class, () -> work(null, CleanupMaintenanceWorkTest::transferResult));
    assertThrows(NullPointerException.class, () -> work((c, complete) -> {}, null));
    assertThrows(
        NullPointerException.class,
        () -> work((c, complete) -> {}, CleanupMaintenanceWorkTest::transferResult).execute(null));
  }
}
