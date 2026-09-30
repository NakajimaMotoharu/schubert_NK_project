package dev.codex.schubert.nk.batch.repository;

import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.*;
import static org.junit.jupiter.api.Assertions.*;

import java.nio.file.Path;
import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/** CTERM001..003: independent SQL fixture/full-row data, no native Unit acceptance. SSC119. */
final class CleanupTerminalRepositoryTest {
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  private static final Instant OBSERVED = Instant.parse("2026-09-30T00:00:00Z");
  private static final String[] STEPS = {
    "CLEAN_NOTIFICATION",
    "CLEAN_QUESTION",
    "CLEAN_SESSION",
    "CLEAN_INBOX_OUTBOX",
    "CLEAN_LOG",
    "CLEAN_BATCH_RUN",
    "CLEAN_TRANSFER"
  };

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
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs");
      for (int index = 0; index < 7; index++)
        sql(
            c,
            "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count) values("
                + (1000 + index)
                + ",'"
                + RUN.id()
                + "','2026-09-13','"
                + STEPS[index]
                + "',1,'2026-09-13T02:00:00Z','2026-09-13T02:00:01Z','SUCCESS',1,1,0,0)");
    }
  }

  private CleanupTerminalRepository.Snapshot read() throws Exception {
    try (var c = locked(db, false)) {
      var result = new CleanupTerminalRepository(c, () -> 10_000_000_000L).read(RUN, OBSERVED);
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      c.rollback();
      return result;
    }
  }

  @Test
  void cterm001FixedSevenFullColumnsWarningAndSkipRemainSeparate() throws Exception {
    var success = read();
    assertEquals(0, success.exitCode());
    assertEquals(7, success.entries().size());
    for (int index = 0; index < 7; index++) {
      var entry = success.entries().get(index);
      assertEquals(1000 + index, entry.attempt().id());
      assertEquals(STEPS[index], entry.attempt().step().name());
      assertEquals(RUN, entry.attempt().run());
      assertEquals(1, entry.attempt().attempt());
      assertEquals(Instant.parse("2026-09-13T02:00:00Z"), entry.attempt().startedAt());
      assertEquals(Instant.parse("2026-09-13T02:00:01Z"), entry.endedAt());
      assertEquals(
          new BatchStepResult(
              BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE),
          entry.result());
    }
    try (var c = db.admin()) {
      sql(
          c,
          "update schubert.batch_runs set status='WARNING',target_count=2,success_count=1,error_code='PROTECTED_RECORDS',error_summary='protected records retained' where id=1001");
      sql(
          c,
          "update schubert.batch_runs set status='SKIPPED',ended_at=started_at,target_count=0,success_count=0,error_code='ALREADY_SUCCESSFUL',error_summary='step already successful for business date' where id=1002");
    }
    var changed = read();
    assertEquals(10, changed.exitCode());
    assertEquals(0, changed.entries().get(1).result().failure());
    assertTrue(changed.entries().get(2).attempt().skipped());
    assertEquals(0, changed.entries().get(2).result().target());
    assertEquals("CleanupTerminalSnapshot[data=<redacted>]", changed.toString());
    assertThrows(UnsupportedOperationException.class, () -> changed.entries().clear());
  }

  @Test
  void cterm002MissingRunningFailedAndMalformedDiagnosticNeverPass() throws Exception {
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs where id=1002",
            "update schubert.batch_runs set status='RUNNING',ended_at=null where id=1002",
            "update schubert.batch_runs set status='FAILED',error_code='SAFETY_FAILURE',error_summary='batch safety check failed' where id=1002",
            "update schubert.batch_runs set error_code='UNKNOWN',error_summary='PUBLIC' where id=1002",
            "update schubert.batch_runs set error_summary='PUBLIC_WRONG' where id=1002")) {
      seed();
      try (var c = db.admin()) {
        sql(c, mutation);
      }
      var failure = assertThrows(BatchRepositoryException.class, this::read);
      assertNull(failure.getCause());
      assertFalse(failure.toString().contains("PUBLIC"));
    }
    seed();
    try (var c = locked(db, false)) {
      assertThrows(
          BatchRepositoryException.class,
          () ->
              new CleanupTerminalRepository(
                      c,
                      () -> {
                        throw new java.io.IOException("PRIVATE");
                      })
                  .read(RUN, OBSERVED));
      var unknown = new AssertionError("PUBLIC_UNKNOWN");
      assertSame(
          unknown,
          assertThrows(
              AssertionError.class,
              () ->
                  new CleanupTerminalRepository(
                          c,
                          () -> {
                            throw unknown;
                          })
                      .read(RUN, OBSERVED)));
      c.rollback();
    }
    try (var c = locked(db, true)) {
      assertThrows(
          BatchRepositoryException.class,
          () -> new CleanupTerminalRepository(c, () -> 10_000_000_000L).read(RUN, OBSERVED));
    }
  }

  private void insertCurrentSkips() throws Exception {
    try (var c = db.admin()) {
      for (int index = 0; index < 7; index++)
        sql(
            c,
            "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values("
                + (2000 + index)
                + ",'"
                + RUN.id()
                + "','2026-09-13','"
                + STEPS[index]
                + "',2,'2026-09-13T02:00:02Z','2026-09-13T02:00:02Z','SKIPPED',0,0,0,0,'ALREADY_SUCCESSFUL','step already successful for business date')");
    }
  }

  @Test
  void issuerStep003CurrentSkipAndPriorSuccessAreSeparateCompleteRows() throws Exception {
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      assertEquals(
          Collections.nCopies(7, Optional.empty()),
          repository.references(repository.read(RUN, OBSERVED)));
      c.rollback();
    }
    insertCurrentSkips();
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      var current = repository.read(RUN, OBSERVED);
      var references = repository.references(current);
      assertEquals(7, references.size());
      for (int index = 0; index < 7; index++) {
        var now = current.entries().get(index);
        var original = references.get(index).orElseThrow();
        assertEquals(2000 + index, now.attempt().id());
        assertEquals(2, now.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:02Z"), now.endedAt());
        assertEquals(
            new BatchStepResult(
                BatchStepResult.Status.SKIPPED,
                0,
                0,
                0,
                0,
                BatchStepResult.Reason.ALREADY_SUCCESSFUL),
            now.result());
        assertEquals(1000 + index, original.attempt().id());
        assertEquals(RUN, original.attempt().run());
        assertEquals(STEPS[index], original.attempt().step().name());
        assertEquals(1, original.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:00Z"), original.attempt().startedAt());
        assertEquals(Instant.parse("2026-09-13T02:00:01Z"), original.endedAt());
        assertEquals(
            new BatchStepResult(
                BatchStepResult.Status.SUCCESS, 1, 1, 0, 0, BatchStepResult.Reason.NONE),
            original.result());
      }
      assertThrows(UnsupportedOperationException.class, () -> references.clear());
      assertThrows(NullPointerException.class, () -> repository.references(null));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      c.rollback();
    }
  }

  @Test
  void issuerStep003MissingForeignLateAndMalformedOriginalCannotBecomeReference() throws Exception {
    for (String mutation :
        List.of(
            "delete from schubert.batch_runs where id=1002",
            "update schubert.batch_runs set run_id='47700000-2222-4333-8444-555555555555' where id=1002",
            "update schubert.batch_runs set attempt=3 where id=1002",
            "update schubert.batch_runs set ended_at='2026-09-13T02:00:03Z' where id=1002",
            "update schubert.batch_runs set error_summary='PUBLIC_WRONG' where id=1002")) {
      seed();
      insertCurrentSkips();
      try (var c = locked(db, false)) {
        var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
        var current = repository.read(RUN, OBSERVED);
        try (var admin = db.admin()) {
          sql(admin, mutation);
        }
        assertThrows(BatchRepositoryException.class, () -> repository.references(current));
        c.rollback();
      }
    }
  }

  @Test
  void cterm003ValueInvariantNullAndMissingOwner() throws Exception {
    var valid = read();
    assertThrows(NullPointerException.class, () -> new CleanupTerminalRepository(null, () -> 1));
    try (var c = locked(db, false)) {
      assertThrows(NullPointerException.class, () -> new CleanupTerminalRepository(c, null));
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      assertThrows(NullPointerException.class, () -> repository.read(null, OBSERVED));
      assertThrows(NullPointerException.class, () -> repository.read(RUN, null));
      c.rollback();
    }
    assertThrows(
        IllegalArgumentException.class, () -> new CleanupTerminalRepository.Snapshot(List.of()));
    var reversed = new ArrayList<>(valid.entries());
    Collections.reverse(reversed);
    assertThrows(
        IllegalArgumentException.class, () -> new CleanupTerminalRepository.Snapshot(reversed));
    var first = valid.entries().getFirst();
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(null, first.endedAt(), first.result()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(first.attempt(), null, first.result()));
    assertThrows(
        NullPointerException.class,
        () -> new CleanupTerminalRepository.Entry(first.attempt(), first.endedAt(), null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.Entry(
                first.attempt(), first.attempt().startedAt().minusSeconds(1), first.result()));
  }

  @Test
  void cterm004RejectedPartialRowsRemainExactAndMissingIsNotInvented() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs where id>=1003");
      sql(
          c,
          "update schubert.batch_runs set status='RUNNING',ended_at=null,target_count=0,success_count=0 where id=1001");
      sql(
          c,
          "update schubert.batch_runs set status='FAILED',error_code='SAFETY_FAILURE',error_summary='batch safety check failed' where id=1002");
    }
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      var actual = repository.readRejected(RUN, OBSERVED);
      assertEquals(RUN, actual.run());
      assertEquals(7, actual.entries().size());
      for (int index = 0; index < 3; index++) {
        var row = actual.entries().get(index).orElseThrow();
        assertEquals(1000 + index, row.attempt().id());
        assertEquals(STEPS[index], row.attempt().step().name());
        assertEquals(1, row.attempt().attempt());
        assertEquals(Instant.parse("2026-09-13T02:00:00Z"), row.attempt().startedAt());
      }
      assertEquals(
          BatchStepResult.Status.SUCCESS,
          actual.entries().get(0).orElseThrow().result().orElseThrow().status());
      assertTrue(actual.entries().get(1).orElseThrow().result().isEmpty());
      assertTrue(actual.entries().get(1).orElseThrow().endedAt().isEmpty());
      var failed = actual.entries().get(2).orElseThrow();
      assertEquals(Optional.of(Instant.parse("2026-09-13T02:00:01Z")), failed.endedAt());
      assertEquals(
          Optional.of(
              new BatchStepResult(
                  BatchStepResult.Status.FAILED,
                  1,
                  1,
                  0,
                  0,
                  BatchStepResult.Reason.SAFETY_FAILURE)),
          failed.result());
      for (int index = 3; index < 7; index++) assertTrue(actual.entries().get(index).isEmpty());
      assertEquals(actual, repository.readRejected(RUN, OBSERVED));
      assertFalse(c.getAutoCommit());
      assertFalse(c.isClosed());
      assertEquals("CleanupRejectedSnapshot[data=<redacted>]", actual.toString());
      assertThrows(UnsupportedOperationException.class, () -> actual.entries().clear());
      assertThrows(BatchRepositoryException.class, () -> repository.read(RUN, OBSERVED));
      c.rollback();
    }
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs");
    }
    try (var c = locked(db, false)) {
      var empty =
          new CleanupTerminalRepository(c, () -> 10_000_000_000L).readRejected(RUN, OBSERVED);
      assertEquals(Collections.nCopies(7, Optional.empty()), empty.entries());
      try (var s = c.createStatement();
          var rows = s.executeQuery("select count(*) from schubert.batch_runs")) {
        assertTrue(rows.next());
        assertEquals(0, rows.getLong(1));
      }
      c.rollback();
    }
  }

  @Test
  void cterm005RejectedMalformedRunningAndNullFailClosed() throws Exception {
    try (var c = db.admin()) {
      sql(c, "update schubert.batch_runs set status='RUNNING',ended_at=null where id=1001");
    }
    try (var c = locked(db, false)) {
      var repository = new CleanupTerminalRepository(c, () -> 10_000_000_000L);
      assertThrows(BatchRepositoryException.class, () -> repository.readRejected(RUN, OBSERVED));
      assertThrows(NullPointerException.class, () -> repository.readRejected(null, OBSERVED));
      assertThrows(NullPointerException.class, () -> repository.readRejected(RUN, null));
      c.rollback();
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new CleanupTerminalRepository.RejectedSnapshot(RUN, List.of()));
    assertThrows(
        NullPointerException.class,
        () ->
            new CleanupTerminalRepository.RejectedSnapshot(
                null, Collections.nCopies(7, Optional.empty())));
    var attempt =
        new BatchStepAttempt(
            1000,
            RUN,
            BatchStep.CLEAN_NOTIFICATION,
            1,
            Instant.parse("2026-09-13T02:00:00Z"),
            false);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                attempt, Optional.of(OBSERVED), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new CleanupTerminalRepository.RejectedEntry(
                attempt,
                Optional.empty(),
                Optional.of(
                    new BatchStepResult(
                        BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, BatchStepResult.Reason.NONE))));
  }
}
