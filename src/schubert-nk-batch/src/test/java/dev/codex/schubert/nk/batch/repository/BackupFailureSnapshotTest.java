package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/** CFDB001..002: isolated real PostgreSQL with independent SQL/full 14-column postconditions. */
final class BackupFailureSnapshotTest {
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  private static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  private static final Instant END = Instant.parse("2026-09-13T02:00:03Z");

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    db.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("delete from schubert.batch_runs");
      for (String row : List.of("7,'BACKUP_DB'", "8,'BACKUP_CONFIG'"))
        s.execute(
            "insert into schubert.batch_runs(id,step,run_id,business_date,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values("
                + row
                + ",'12345678-9abc-def0-8123-456789abcdef','2026-09-13',4,'2026-09-13T02:00:00Z','2026-09-13T02:00:03Z','FAILED',1,0,1,0,'COMMAND_FAILURE','batch command failed')");
    }
  }

  private static BackupFailureSnapshot snapshot() {
    return new BackupFailureSnapshot(
        new BatchStepAttempt(7, RUN, BatchStep.BACKUP_DB, 4, START, false),
        new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
        END);
  }

  private void verify() throws Exception {
    try (var c = CleanupStepFixture.locked(db, false)) {
      snapshot().verifyLatest(c, () -> 10_000_000_000L);
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      c.rollback();
    }
  }

  @Test
  void cfdb001ActualBothLatestFullRowsAreReadWithoutMutationAndLockIsMandatory() throws Exception {
    verify();
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select count(*),sum(target_count),sum(success_count),sum(failure_count),sum(byte_count) from schubert.batch_runs where status='FAILED' and error_code='COMMAND_FAILURE' and error_summary='batch command failed'")) {
      assertTrue(r.next());
      assertEquals(2, r.getLong(1));
      assertEquals(2, r.getLong(2));
      assertEquals(0, r.getLong(3));
      assertEquals(2, r.getLong(4));
      assertEquals(0, r.getLong(5));
      assertFalse(r.next());
    }
    try (var c = db.open("schubert_batch")) {
      assertThrows(
          BatchRepositoryException.class, () -> snapshot().verifyLatest(c, () -> 10_000_000_000L));
    }
    assertThrows(NullPointerException.class, () -> snapshot().verifyLatest(null, () -> 1));
    try (var c = CleanupStepFixture.locked(db, false)) {
      assertThrows(NullPointerException.class, () -> snapshot().verifyLatest(c, null));
      var failure = new IOException("independent owner fault");
      assertSame(
          failure,
          assertThrows(
              IOException.class,
              () ->
                  snapshot()
                      .verifyLatest(
                          c,
                          () -> {
                            throw failure;
                          })));
      c.rollback();
    }
  }

  @Test
  void cfdb002LatestIdentityAndEveryTerminalColumnRejectMismatch() throws Exception {
    for (String assignment :
        List.of(
            "id=70",
            "attempt=5",
            "started_at='2026-09-13T02:00:01Z'",
            "ended_at='2026-09-13T02:00:04Z'",
            "status='SUCCESS',success_count=1,failure_count=0,error_code=null,error_summary=null",
            "target_count=2",
            "success_count=1,target_count=2",
            "failure_count=0",
            "byte_count=1",
            "error_code='ABANDONED',error_summary='previous same-run attempt abandoned'")) {
      seed();
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("update schubert.batch_runs set " + assignment + " where id=7");
      }
      assertThrows(IOException.class, this::verify);
    }
    seed();
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute(
          "insert into schubert.batch_runs(id,step,run_id,business_date,attempt,started_at,status) values(9,'BACKUP_DB','12345678-9abc-def0-8123-456789abcdef','2026-09-13',5,'2026-09-13T02:00:04Z','RUNNING')");
    }
    assertThrows(IOException.class, this::verify);
    seed();
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("delete from schubert.batch_runs where id=8");
    }
    assertThrows(IOException.class, this::verify);
  }

  @Test
  void cfdb003SnapshotInvariantUsesActualPairNotAFrameCertificate() {
    var value = snapshot();
    assertThrows(
        NullPointerException.class,
        () -> new BackupFailureSnapshot(null, value.configuration(), END));
    assertThrows(
        NullPointerException.class, () -> new BackupFailureSnapshot(value.database(), null, END));
    assertThrows(
        NullPointerException.class,
        () -> new BackupFailureSnapshot(value.database(), value.configuration(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupFailureSnapshot(
                value.database(), value.configuration(), START.minusSeconds(1)));
    for (var handle :
        List.of(
            new BatchStepAttempt(7, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
            new BatchStepAttempt(8, RUN, BatchStep.CLEAN_LOG, 4, START, false),
            new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 4, START, true),
            new BatchStepAttempt(8, RUN, BatchStep.BACKUP_CONFIG, 4, START.plusSeconds(1), false)))
      assertThrows(
          IllegalArgumentException.class,
          () -> new BackupFailureSnapshot(value.database(), handle, END));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupFailureSnapshot(
                new BatchStepAttempt(7, RUN, BatchStep.BACKUP_CONFIG, 4, START, false),
                value.configuration(),
                END));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BackupFailureSnapshot(
                new BatchStepAttempt(7, RUN, BatchStep.BACKUP_DB, 4, START, true),
                value.configuration(),
                END));
  }
}
