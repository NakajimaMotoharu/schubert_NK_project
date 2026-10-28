package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PG249/PT-BAT-284..287; SS331 §8.2/8.3,341 §9; SSC077/078/BUG237/238. */
final class ExpiryAuditRepositoryTest {
  private static final String FIXTURE_SUCCESS_10855C7F = "SUCCESS";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D = "SQL_SECRET_SENTINEL";
  private static final String FIXTURE_RUNNING_294BDBF9 = "RUNNING";
  private static final String FIXTURE_STAGENULL_A015B184 = "stageNull";
  private static final String FIXTURE_FINISHNULL_BE9B800A = "finishNull";
  private static final String FIXTURE_READNEXTANDROWCLOSE_548E8C85 = "readNextAndRowClose";
  private static final String FIXTURE_READNEXTANDSTATEMENTCLOSE_4EFF3B8A =
      "readNextAndStatementClose";
  private static final String FIXTURE_READSTATEMENTCLOSE_64BB69A7 = "readStatementClose";
  @TempDir static Path root;
  private static BatchDatabaseFixture db;
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00.000500Z"));
  private static final Instant START = Instant.parse("2026-09-12T15:00:01Z");
  private static final Instant END = Instant.parse("2026-09-12T15:00:02Z");
  private static final Instant EXPIRY_CUTOFF = Instant.parse("2026-09-05T15:00:00.000500Z");
  private static final BatchStepResult SUCCESS =
      new BatchStepResult(
          BatchStepResult.Status.SUCCESS, 2, 2, 0, 200, BatchStepResult.Reason.NONE);

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void clear() throws Exception {
    try (var admin = db.admin()) {
      execute(admin, "delete from schubert.batch_runs");
    }
  }

  @Test
  void exp3202001EmptyAndSameRunSuccessUseLiteralAuditWithoutMutation() throws Exception {
    var owner = (dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard) () -> 10_000_000_000L;
    try (var connection = locked()) {
      assertTrue(new ExpiryAuditRepository(connection).successful(RUN, END, owner).isEmpty());
      assertFalse(connection.isClosed());
      assertFalse(connection.getAutoCommit());
    }
    retainedSuccess();
    try (var connection = locked()) {
      var before = terminal(connection, 42);
      var prior = new ExpiryAuditRepository(connection).successful(RUN, END, owner).orElseThrow();
      assertEquals(
          new BatchStepAttempt(42, RUN, BatchStep.CLEAN_EXPIRY, 1, START, false), prior.handle());
      assertEquals(
          new ExpiryAuditRepository.Snapshot(
              FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, null, null),
          prior.audit());
      assertEquals("SUCCESS|2|0|NULL", before);
      assertEquals(before, terminal(connection, 42));
      assertFalse(connection.getAutoCommit());
      assertFalse(connection.isClosed());
      connection.rollback();
    }
  }

  /** PT-BAT-EXP3366-001: untrusted readback cannot turn a stale selection into success. */
  @Test
  void exp3366001PriorSuccessRevalidatesEveryReadbackWithoutMutation() throws Exception {
    retainedSuccess();
    var owner = (dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard) () -> 10_000_000_000L;
    try (var connection = locked()) {
      for (String fault :
          java.util.List.of(
              "duplicate",
              "missing",
              "nullRows",
              "status",
              "futureEnd",
              "missingEnd",
              "errorCode",
              "errorSummary")) {
        var injected = new java.util.concurrent.atomic.AtomicInteger();
        var live = new java.util.concurrent.atomic.AtomicInteger();
        var subject = new ExpiryAuditRepository(priorReadback(connection, fault, injected, live));
        var denied =
            assertThrows(
                BatchRepositoryException.class,
                () -> subject.successful(RUN, END, owner, (id, time) -> RUN),
                fault);
        assertNull(denied.getCause());
        assertEquals(0, denied.getSuppressed().length);
        assertFalse(denied.toString().contains("INDEPENDENT_ERROR"));
        assertEquals(1, injected.get(), fault);
        assertEquals(0, live.get(), fault);
        assertEquals("SUCCESS|2|0|NULL", terminal(connection, 42));
        assertEquals("2026-09-05 15:00:00.000500|3|1|2|2|0|200", audit(connection, 42));
        var valid =
            new ExpiryAuditRepository(connection)
                .successful(RUN, END, owner, (id, time) -> RUN)
                .orElseThrow();
        assertEquals(
            new BatchStepAttempt(42, RUN, BatchStep.CLEAN_EXPIRY, 1, START, false), valid.handle());
        assertEquals(
            new ExpiryAuditRepository.Snapshot(
                FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, null, null),
            valid.audit());
        assertFalse(connection.isClosed());
        assertFalse(connection.getAutoCommit());
      }
      connection.rollback();
    }
  }

  private static Connection priorReadback(
      Connection delegate,
      String fault,
      java.util.concurrent.atomic.AtomicInteger injected,
      java.util.concurrent.atomic.AtomicInteger live) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              Object result = invokePublicJdbc(method, delegate, args);
              if (!method.getName().equals("prepareStatement") || args == null) return result;
              String sql = (String) args[0];
              boolean selected = sql.startsWith("select id,run_id,attempt,started_at");
              boolean audit = sql.startsWith("select status,expiry_cutoff_at");
              if (!selected && !audit) return result;
              var statement = (java.sql.PreparedStatement) result;
              live.incrementAndGet();
              var statementClosed = new java.util.concurrent.atomic.AtomicBoolean();
              return Proxy.newProxyInstance(
                  java.sql.PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {java.sql.PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals(FIXTURE_CLOSE_97959247)) {
                      assertTrue(statementClosed.compareAndSet(false, true));
                      try {
                        return invokePublicJdbc(sm, statement, sa);
                      } finally {
                        live.decrementAndGet();
                      }
                    }
                    Object answer = invokePublicJdbc(sm, statement, sa);
                    if (!sm.getName().equals("executeQuery")) return answer;
                    var rows = (java.sql.ResultSet) answer;
                    if (selected && fault.equals("nullRows")) {
                      rows.close();
                      injected.incrementAndGet();
                      return null;
                    }
                    live.incrementAndGet();
                    var rowsClosed = new java.util.concurrent.atomic.AtomicBoolean();
                    var advances = new java.util.concurrent.atomic.AtomicInteger();
                    return Proxy.newProxyInstance(
                        java.sql.ResultSet.class.getClassLoader(),
                        new Class<?>[] {java.sql.ResultSet.class},
                        (rp, rm, ra) -> {
                          if (rm.getName().equals(FIXTURE_CLOSE_97959247)) {
                            assertTrue(rowsClosed.compareAndSet(false, true));
                            try {
                              return invokePublicJdbc(rm, rows, ra);
                            } finally {
                              live.decrementAndGet();
                            }
                          }
                          if (rm.getName().equals("next")) {
                            int call = advances.incrementAndGet();
                            if (selected && fault.equals("duplicate") && call == 2) {
                              injected.incrementAndGet();
                              return true;
                            }
                            if (audit && fault.equals("missing")) {
                              injected.incrementAndGet();
                              return false;
                            }
                          }
                          if (audit && ra != null) {
                            Object value = null;
                            boolean changed = false;
                            if (rm.getName().equals("getString")) {
                              if (fault.equals("status") && ra[0].equals("status")) {
                                value = "WARNING";
                                changed = true;
                              }
                              if (fault.equals("errorCode") && ra[0].equals("error_code")) {
                                value = "INDEPENDENT_ERROR";
                                changed = true;
                              }
                              if (fault.equals("errorSummary") && ra[0].equals("error_summary")) {
                                value = "INDEPENDENT_ERROR";
                                changed = true;
                              }
                            }
                            if (rm.getName().equals("getObject") && ra[0].equals("ended_at")) {
                              if (fault.equals("futureEnd")) {
                                value = END.plusSeconds(1).atOffset(java.time.ZoneOffset.UTC);
                                changed = true;
                              }
                              if (fault.equals("missingEnd")) changed = true;
                            }
                            if (changed) {
                              injected.incrementAndGet();
                              return value;
                            }
                          }
                          return invokePublicJdbc(rm, rows, ra);
                        });
                  });
            });
  }

  private static Object invokePublicJdbc(
      java.lang.reflect.Method method, Object target, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException failure) {
      throw failure.getCause();
    }
  }

  @Test
  void exp3202002SuccessRefusesForeignDayFutureEndNullAndSqlBeforeAnyRewrite() throws Exception {
    retainedSuccess();
    var owner = (dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard) () -> 10_000_000_000L;
    try (var connection = locked()) {
      var subject = new ExpiryAuditRepository(connection);
      var wrongDay =
          new BatchRun(RUN.id(), RUN.cutoff().plus(1, java.time.temporal.ChronoUnit.DAYS));
      assertThrows(
          BatchRepositoryException.class,
          () -> subject.successful(RUN, END, owner, (id, time) -> wrongDay));
      assertThrows(
          BatchRepositoryException.class,
          () -> subject.successful(RUN, END.minusNanos(1000), owner));
      assertThrows(NullPointerException.class, () -> subject.successful(null, END, owner));
      assertThrows(NullPointerException.class, () -> subject.successful(RUN, null, owner));
      assertThrows(NullPointerException.class, () -> subject.successful(RUN, END, null));
      assertThrows(
          NullPointerException.class,
          () -> subject.successful(RUN, END, owner, (id, time) -> null));
      for (String failure : new String[] {"successSelect", "successNullStatement"}) {
        var fault = new ExpiryAuditRepository(failingConnection(connection, failure));
        var actual =
            assertThrows(BatchRepositoryException.class, () -> fault.successful(RUN, END, owner));
        assertNull(actual.getCause());
        assertFalse(actual.toString().contains(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D));
      }
      assertEquals("SUCCESS|2|0|NULL", terminal(connection, 42));
      assertFalse(connection.isClosed());
      assertFalse(connection.getAutoCommit());
      connection.rollback();
    }
  }

  private static void retainedSuccess() throws Exception {
    try (var admin = db.admin()) {
      execute(
          admin,
          """
          insert into schubert.batch_runs
          (id,run_id,business_date,step,attempt,started_at,ended_at,status,
           target_count,success_count,failure_count,byte_count,error_code,error_summary,
           expiry_cutoff_at,expiry_before_count,expiry_after_count)
          values (42,'12345678-9abc-def0-8123-456789abcdef','2026-09-13',
           'CLEAN_EXPIRY',1,'2026-09-12T15:00:01Z','2026-09-12T15:00:02Z',
           'SUCCESS',2,2,0,200,null,null,'2026-09-05T15:00:00.000500Z',3,1)
          """);
    }
  }

  @Test
  void exp200001SameDayForeignSuccessUsesRetainedCutoffAndDoesNotRewriteAudit() throws Exception {
    try (var admin = db.admin()) {
      execute(
          admin,
          """
          insert into schubert.batch_runs
          (id,run_id,business_date,step,attempt,started_at,ended_at,status,
           target_count,success_count,failure_count,byte_count,error_code,error_summary,
           expiry_cutoff_at,expiry_before_count,expiry_after_count)
          values (42,'12345678-9abc-def0-8123-456789abcdef','2026-09-13',
           'CLEAN_EXPIRY',1,'2026-09-12T15:00:01Z','2026-09-12T15:00:02Z',
           'SUCCESS',2,2,0,200,null,null,'2026-09-05T15:00:00.000500Z',3,1)
          """);
    }
    var current =
        new BatchRun(
            UUID.fromString("00000000-0000-4000-8000-000000000200"),
            Instant.parse("2026-09-12T15:00:03Z"));
    var observed = Instant.parse("2026-09-12T15:00:04Z");
    var owner = (dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard) () -> 10_000_000_000L;
    try (var connection = locked()) {
      var subject = new ExpiryAuditRepository(connection);
      assertThrows(java.io.IOException.class, () -> subject.successful(current, observed, owner));
      var calls = new java.util.ArrayList<UUID>();
      var found =
          subject
              .successful(
                  current,
                  observed,
                  owner,
                  (id, time) -> {
                    assertEquals(RUN.id(), id);
                    assertEquals(observed, time);
                    calls.add(id);
                    return RUN;
                  })
              .orElseThrow();
      assertEquals(java.util.List.of(RUN.id()), calls);
      assertEquals(
          new BatchStepAttempt(42, RUN, BatchStep.CLEAN_EXPIRY, 1, START, false), found.handle());
      assertEquals(
          new ExpiryAuditRepository.Snapshot(
              FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, null, null),
          found.audit());
      assertEquals("SUCCESS|2|0|NULL", terminal(connection, 42));
      assertThrows(
          BatchRepositoryException.class,
          () -> subject.successful(current, observed, owner, (id, time) -> current));
      var unavailable = new java.io.IOException("owned reference unavailable");
      assertSame(
          unavailable,
          assertThrows(
              java.io.IOException.class,
              () ->
                  subject.successful(
                      current,
                      observed,
                      owner,
                      (id, time) -> {
                        throw unavailable;
                      })));
      assertThrows(
          NullPointerException.class, () -> subject.successful(current, observed, owner, null));
      assertEquals("SUCCESS|2|0|NULL", terminal(connection, 42));
      assertFalse(connection.getAutoCommit());
      assertFalse(connection.isClosed());
      connection.rollback();
    }
  }

  @Test
  void bat284StageIsInvisibleUntilCallerCommitAndKeepsExactCutoff() throws Exception {
    try (var parent = locked();
        var observer = db.open("schubert_batch")) {
      var attempt = new BatchRunRepository(parent).begin(RUN, BatchStep.CLEAN_EXPIRY, START, false);
      parent.commit();
      var repo = new ExpiryAuditRepository(parent);
      var stage = repo.stage(attempt, 3, 2, 200);
      assertEquals(new ExpiryAuditRepository.Stage(EXPIRY_CUTOFF, 3, 2, 200), stage);
      assertEquals("NULL|NULL|NULL|0|0|0|0", audit(observer, attempt.id()));
      assertEquals("ExpiryAuditStage[observation=<redacted>]", stage.toString());
      parent.commit();
      assertEquals("2026-09-05 15:00:00.000500|3|NULL|2|0|0|200", audit(observer, attempt.id()));
      assertEquals(stage, repo.stage(attempt, 3, 2, 200)); // Same committed stage is idempotent.
      var snapshot = repo.read(attempt).orElseThrow();
      assertEquals(FIXTURE_RUNNING_294BDBF9, snapshot.status());
      assertEquals(EXPIRY_CUTOFF, snapshot.cutoff());
      assertEquals(3L, snapshot.before());
      assertNull(snapshot.after());
      assertNull(snapshot.ended());
      assertEquals("ExpiryAuditSnapshot[observation=<redacted>]", snapshot.toString());
    }
  }

  @Test
  void bat285TerminalSuccessAndExactReplayCannotRewriteOldResult() throws Exception {
    try (var parent = locked()) {
      var attempt = new BatchRunRepository(parent).begin(RUN, BatchStep.CLEAN_EXPIRY, START, false);
      var repo = new ExpiryAuditRepository(parent);
      var stage = repo.stage(attempt, 3, 2, 200);
      parent.commit();
      repo.finish(attempt, stage, END, 1L, SUCCESS);
      parent.commit();
      var snapshot = repo.read(attempt).orElseThrow();
      assertEquals(FIXTURE_SUCCESS_10855C7F, snapshot.status());
      assertEquals(1L, snapshot.after());
      assertEquals(END, snapshot.ended());
      assertEquals(2, snapshot.success());
      repo.finish(attempt, stage, END, 1L, SUCCESS);
      assertThrows(
          BatchRepositoryException.class,
          () -> repo.finish(attempt, stage, END.plusSeconds(1), 1L, SUCCESS));
      assertEquals("SUCCESS|2|0|NULL", terminal(parent, attempt.id()));
    }
  }

  @Test
  void bat286RollbackUnknownAfterAndSameRunAttemptAreNeverGuessed() throws Exception {
    try (var parent = locked()) {
      var attempts = new BatchRunRepository(parent);
      var first = attempts.begin(RUN, BatchStep.CLEAN_EXPIRY, START, false);
      parent.commit();
      var repo = new ExpiryAuditRepository(parent);
      var stage = repo.stage(first, 3, 2, 200);
      parent.rollback();
      var unobserved = repo.read(first).orElseThrow();
      assertNull(unobserved.cutoff());
      assertNull(unobserved.before());
      assertNull(unobserved.after());
      assertEquals(0, unobserved.target());
      stage = repo.stage(first, 3, 2, 200);
      parent.commit();
      var failed =
          new BatchStepResult(
              BatchStepResult.Status.FAILED, 2, 0, 0, 200, BatchStepResult.Reason.COMMAND_FAILURE);
      repo.finish(first, stage, END, null, failed);
      parent.commit();
      assertEquals("FAILED|0|0|COMMAND_FAILURE", terminal(parent, first.id()));
      assertNull(repo.read(first).orElseThrow().after());
      var second = attempts.begin(RUN, BatchStep.CLEAN_EXPIRY, START.plusSeconds(2), false);
      assertEquals(2, second.attempt());
      var laterStage = repo.stage(second, 3, 2, 200);
      var warning =
          new BatchStepResult(
              BatchStepResult.Status.WARNING, 2, 1, 1, 200, BatchStepResult.Reason.COMMAND_FAILURE);
      repo.finish(second, laterStage, END.plusSeconds(2), 2L, warning);
      parent.commit();
      assertEquals("WARNING|1|1|COMMAND_FAILURE", terminal(parent, second.id()));
      assertEquals(2L, repo.read(second).orElseThrow().after());
      assertNull(repo.read(first).orElseThrow().after());
    }
  }

  @Test
  void bat287NullInvalidHandleAndTerminalAreRejectedWithoutMutation() throws Exception {
    projectionMatrix();
    assertThrows(BatchRepositoryException.class, () -> ExpiryAuditRepository.required(null));
    assertEquals(7L, ExpiryAuditRepository.required(7L));
    assertThrows(NullPointerException.class, () -> new ExpiryAuditRepository(null));
    assertThrows(NullPointerException.class, () -> new ExpiryAuditRepository.Stage(null, 1, 1, 1));
    for (long[] invalid : new long[][] {{-1, 0, 0}, {1, -1, 0}, {1, 2, 0}, {1, 1, -1}})
      assertThrows(
          IllegalArgumentException.class,
          () -> new ExpiryAuditRepository.Stage(EXPIRY_CUTOFF, invalid[0], invalid[1], invalid[2]));
    try (var parent = locked()) {
      var attempts = new BatchRunRepository(parent);
      var attempt = attempts.begin(RUN, BatchStep.CLEAN_EXPIRY, START, false);
      var repo = new ExpiryAuditRepository(parent);
      assertThrows(NullPointerException.class, () -> repo.stage(null, 1, 1, 1));
      assertThrows(NullPointerException.class, () -> repo.read(null));
      var otherStep = attempts.begin(RUN, BatchStep.CLEAN_LOG, START, false);
      assertThrows(IllegalArgumentException.class, () -> repo.stage(otherStep, 1, 1, 1));
      var skipped =
          new BatchStepAttempt(
              attempt.id(), RUN, BatchStep.CLEAN_EXPIRY, attempt.attempt(), START, true);
      assertThrows(IllegalArgumentException.class, () -> repo.stage(skipped, 1, 1, 1));
      var missing =
          new BatchStepAttempt(
              attempt.id() + 100, RUN, BatchStep.CLEAN_EXPIRY, attempt.attempt(), START, false);
      assertTrue(repo.read(missing).isEmpty());
      assertThrows(BatchRepositoryException.class, () -> repo.stage(missing, 1, 1, 1));
      var stage = repo.stage(attempt, 3, 2, 200);
      assertThrows(BatchRepositoryException.class, () -> repo.stage(attempt, 3, 1, 200));
      assertThrows(NullPointerException.class, () -> repo.finish(null, stage, END, 1L, SUCCESS));
      assertThrows(NullPointerException.class, () -> repo.finish(attempt, null, END, 1L, SUCCESS));
      assertThrows(
          NullPointerException.class, () -> repo.finish(attempt, stage, null, 1L, SUCCESS));
      assertThrows(NullPointerException.class, () -> repo.finish(attempt, stage, END, 1L, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(attempt, stage, START.minusSeconds(1), 1L, SUCCESS));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, null, SUCCESS));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, -1L, SUCCESS));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 4L, SUCCESS));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 2L, SUCCESS));
      var skippedResult =
          new BatchStepResult(
              BatchStepResult.Status.SKIPPED,
              0,
              0,
              0,
              0,
              BatchStepResult.Reason.ALREADY_SUCCESSFUL);
      var warningSuccess =
          new BatchStepResult(
              BatchStepResult.Status.WARNING, 2, 1, 0, 200, BatchStepResult.Reason.COMMAND_FAILURE);
      var warningMismatch =
          new BatchStepResult(
              BatchStepResult.Status.WARNING, 2, 0, 1, 200, BatchStepResult.Reason.COMMAND_FAILURE);
      var wrongTarget =
          new BatchStepResult(
              BatchStepResult.Status.WARNING, 1, 0, 0, 200, BatchStepResult.Reason.COMMAND_FAILURE);
      var wrongBytes =
          new BatchStepResult(
              BatchStepResult.Status.WARNING, 2, 0, 0, 201, BatchStepResult.Reason.COMMAND_FAILURE);
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(attempt, stage, END, null, skippedResult));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 1L, wrongTarget));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 1L, wrongBytes));
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(attempt, stage, END, null, warningSuccess));
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(attempt, stage, END, 2L, warningMismatch));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 2L, SUCCESS));
      var tooFew =
          new BatchStepResult(
              BatchStepResult.Status.SUCCESS, 2, 1, 0, 200, BatchStepResult.Reason.NONE);
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 1L, tooFew));
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(attempt, stage, RUN.cutoff(), 1L, SUCCESS));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(attempt, stage, END, 2L, tooFew));
      var forgedRun =
          new BatchRun(RUN.id(), RUN.cutoff().plus(1, java.time.temporal.ChronoUnit.DAYS));
      var forgedAttempt =
          new BatchStepAttempt(
              attempt.id(),
              forgedRun,
              attempt.step(),
              attempt.attempt(),
              START.plus(1, java.time.temporal.ChronoUnit.DAYS),
              false);
      assertThrows(BatchRepositoryException.class, () -> repo.read(forgedAttempt));
      for (String operation :
          new String[] {
            "stage",
            FIXTURE_STAGENULL_A015B184,
            "stageRuntime",
            "finish",
            FIXTURE_FINISHNULL_BE9B800A,
            "finishRuntime",
            "read",
            "readNullStatement",
            "readNullRows",
            "readExecute",
            "readNext",
            FIXTURE_READNEXTANDROWCLOSE_548E8C85,
            FIXTURE_READNEXTANDSTATEMENTCLOSE_4EFF3B8A,
            "readRowClose",
            FIXTURE_READSTATEMENTCLOSE_64BB69A7
          }) {
        var fault = new ExpiryAuditRepository(failingConnection(parent, operation));
        BatchRepositoryException caught =
            assertThrows(
                BatchRepositoryException.class,
                () -> {
                  switch (operation) {
                    case "stage", FIXTURE_STAGENULL_A015B184, "stageRuntime" ->
                        fault.stage(attempt, 3, 2, 200);
                    case "finish", FIXTURE_FINISHNULL_BE9B800A, "finishRuntime" ->
                        fault.finish(attempt, stage, END, 1L, SUCCESS);
                    default -> fault.read(attempt);
                  }
                });
        assertNull(caught.getCause());
        assertFalse(caught.toString().contains(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D));
      }
      // SSC310: unknown provider Runtime is not malformed SQL/data projection.
      var provider = new IllegalStateException("public unknown provider fixture");
      assertSame(
          provider,
          assertThrows(
              IllegalStateException.class,
              () ->
                  new ExpiryAuditRepository(failingConnection(parent, "readRuntime", provider))
                      .read(attempt)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              repo.finish(
                  attempt,
                  new ExpiryAuditRepository.Stage(EXPIRY_CUTOFF.plusNanos(1_000), 3, 2, 200),
                  END,
                  1L,
                  SUCCESS));
      assertThrows(
          BatchRepositoryException.class, () -> repo.finish(missing, stage, END, 1L, SUCCESS));
      execute(
          parent,
          "update schubert.batch_runs set expiry_cutoff_at=expiry_cutoff_at"
              + "+interval '1 microsecond' where id="
              + attempt.id());
      assertThrows(BatchRepositoryException.class, () -> repo.read(attempt));
      execute(
          parent,
          "update schubert.batch_runs set expiry_cutoff_at=expiry_cutoff_at"
              + "-interval '1 microsecond' where id="
              + attempt.id());
      assertEquals("RUNNING|0|0|NULL", terminal(parent, attempt.id()));
      assertEquals("2026-09-05 15:00:00.000500|3|NULL|2|0|0|200", audit(parent, attempt.id()));
      parent.rollback();
    }
    try (var autoCommit = db.open("schubert_batch")) {
      var repo = new ExpiryAuditRepository(autoCommit);
      var forged = new BatchStepAttempt(1, RUN, BatchStep.CLEAN_EXPIRY, 1, START, false);
      assertThrows(BatchRepositoryException.class, () -> repo.read(forged));
    }
  }

  private static Connection failingConnection(Connection delegate, String operation) {
    return failingConnection(
        delegate, operation, new IllegalStateException(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D));
  }

  private static Connection failingConnection(
      Connection delegate, String operation, IllegalStateException provider) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (proxy, method, args) -> {
              if (method.getName().equals("prepareStatement") && args != null && args.length > 0) {
                String sql = (String) args[0];
                boolean selected =
                    switch (operation) {
                      case "successSelect", "successNullStatement" ->
                          sql.startsWith("select id,run_id,attempt,started_at");
                      case "stage", FIXTURE_STAGENULL_A015B184, "stageRuntime" ->
                          sql.startsWith("update schubert.batch_runs set expiry_cutoff_at");
                      case "finish", FIXTURE_FINISHNULL_BE9B800A, "finishRuntime" ->
                          sql.startsWith("update schubert.batch_runs set ended_at");
                      default -> sql.startsWith("select status,expiry_cutoff_at");
                    };
                if (selected) {
                  if (operation.equals(FIXTURE_STAGENULL_A015B184)
                      || operation.equals(FIXTURE_FINISHNULL_BE9B800A)
                      || operation.equals("readNullStatement")
                      || operation.equals("successNullStatement")) return null;
                  if (operation.endsWith("Runtime")) throw provider;
                  if (operation.equals("readExecute")
                      || operation.equals("readNext")
                      || operation.equals(FIXTURE_READNEXTANDROWCLOSE_548E8C85)
                      || operation.equals(FIXTURE_READNEXTANDSTATEMENTCLOSE_4EFF3B8A)
                      || operation.equals("readNullRows")
                      || operation.equals("readRowClose")
                      || operation.equals(FIXTURE_READSTATEMENTCLOSE_64BB69A7)) {
                    var statement = (java.sql.PreparedStatement) method.invoke(delegate, args);
                    return Proxy.newProxyInstance(
                        java.sql.PreparedStatement.class.getClassLoader(),
                        new Class<?>[] {java.sql.PreparedStatement.class},
                        (statementProxy, statementMethod, statementArgs) -> {
                          if (statementMethod.getName().equals(FIXTURE_CLOSE_97959247)
                              && (operation.equals(FIXTURE_READSTATEMENTCLOSE_64BB69A7)
                                  || operation.equals(
                                      FIXTURE_READNEXTANDSTATEMENTCLOSE_4EFF3B8A))) {
                            statement.close();
                            throw new SQLException(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D);
                          }
                          if (statementMethod.getName().equals("executeQuery")) {
                            if (operation.equals("readExecute"))
                              throw new SQLException(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D);
                            if (operation.equals("readNullRows")) return null;
                            var rows = statement.executeQuery();
                            if (operation.equals(FIXTURE_READSTATEMENTCLOSE_64BB69A7)) return rows;
                            return Proxy.newProxyInstance(
                                java.sql.ResultSet.class.getClassLoader(),
                                new Class<?>[] {java.sql.ResultSet.class},
                                (rowsProxy, rowsMethod, rowsArgs) -> {
                                  if (rowsMethod.getName().equals("next")
                                      && (operation.equals("readNext")
                                          || operation.equals(FIXTURE_READNEXTANDROWCLOSE_548E8C85)
                                          || operation.equals(
                                              FIXTURE_READNEXTANDSTATEMENTCLOSE_4EFF3B8A)))
                                    throw new SQLException(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D);
                                  if (rowsMethod.getName().equals(FIXTURE_CLOSE_97959247)
                                      && (operation.equals("readRowClose")
                                          || operation.equals(
                                              FIXTURE_READNEXTANDROWCLOSE_548E8C85))) {
                                    rows.close();
                                    throw new SQLException(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D);
                                  }
                                  return rowsMethod.invoke(rows, rowsArgs);
                                });
                          }
                          try {
                            return statementMethod.invoke(statement, statementArgs);
                          } catch (InvocationTargetException failure) {
                            throw failure.getCause();
                          }
                        });
                  }
                  throw new SQLException(FIXTURE_SQL_SECRET_SENTINEL_1EEDE57D);
                }
              }
              try {
                return method.invoke(delegate, args);
              } catch (InvocationTargetException failure) {
                throw failure.getCause();
              }
            });
  }

  private static void projectionMatrix() {
    var handle = new BatchStepAttempt(1, RUN, BatchStep.CLEAN_EXPIRY, 1, START, false);
    var stage = new ExpiryAuditRepository.Stage(EXPIRY_CUTOFF, 3, 2, 200);
    var running =
        snapshot(FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 200, null, null, null);
    var success =
        snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, null, null);
    assertTrue(ExpiryAuditRepository.validSnapshot(handle, running));
    assertTrue(ExpiryAuditRepository.validSnapshot(handle, success));
    assertTrue(ExpiryAuditRepository.matchesStage(java.util.Optional.of(running), stage));
    assertTrue(
        ExpiryAuditRepository.matchesTerminal(
            java.util.Optional.of(success), stage, END, 1L, SUCCESS));

    // Independent V022 projection mutations: none may be promoted into a replay oracle.
    var invalid =
        new ExpiryAuditRepository.Snapshot[] {
          snapshot("UNKNOWN", EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 200, END, null, null),
          snapshot("FAILED", EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, -1, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, -1, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 0, -1, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 0, 0, -1, null, null, null),
          snapshot(FIXTURE_RUNNING_294BDBF9, null, 3L, null, 2, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, null, null, 2, 0, 0, 200, null, null, null),
          snapshot(FIXTURE_RUNNING_294BDBF9, null, null, 1L, 0, 0, 0, 0, null, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, null, null, null, 0, 0, 0, 0, END, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9,
              EXPIRY_CUTOFF.plusSeconds(1),
              3L,
              null,
              2,
              0,
              0,
              200,
              null,
              null,
              null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, -1L, null, 0, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 4, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 200, END, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 1, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, -1L, 2, 0, 0, 200, null, null, null),
          snapshot(FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, 4L, 2, 0, 0, 200, null, null, null),
          snapshot("WARNING", EXPIRY_CUTOFF, 3L, 2L, 2, 0, 1, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 1, 0, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 1, 2, 0, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 1, 200, END, null, null),
        };
    for (var candidate : invalid)
      assertFalse(ExpiryAuditRepository.validSnapshot(handle, candidate), candidate.toString());

    assertFalse(ExpiryAuditRepository.matchesStage(java.util.Optional.empty(), stage));
    var stageMutations =
        new ExpiryAuditRepository.Snapshot[] {
          snapshot("FAILED", EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 200, END, null, null),
          snapshot(FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, 1L, 2, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9,
              EXPIRY_CUTOFF.plusSeconds(1),
              3L,
              null,
              2,
              0,
              0,
              200,
              null,
              null,
              null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 4L, null, 2, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 1, 0, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 1, 0, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 0, 1, 200, null, null, null),
          snapshot(
              FIXTURE_RUNNING_294BDBF9, EXPIRY_CUTOFF, 3L, null, 2, 0, 0, 201, null, null, null)
        };
    for (var candidate : stageMutations)
      assertFalse(ExpiryAuditRepository.matchesStage(java.util.Optional.of(candidate), stage));

    assertFalse(
        ExpiryAuditRepository.matchesTerminal(java.util.Optional.empty(), stage, END, 1L, SUCCESS));
    var terminalMutations =
        new ExpiryAuditRepository.Snapshot[] {
          snapshot(
              FIXTURE_SUCCESS_10855C7F,
              EXPIRY_CUTOFF.plusSeconds(1),
              3L,
              1L,
              2,
              2,
              0,
              200,
              END,
              null,
              null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 4L, 1L, 2, 2, 0, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 0L, 2, 2, 0, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 1, 2, 0, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 1, 0, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 1, 200, END, null, null),
          snapshot(FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 201, END, null, null),
          snapshot("WARNING", EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, null, null),
          snapshot(
              FIXTURE_SUCCESS_10855C7F,
              EXPIRY_CUTOFF,
              3L,
              1L,
              2,
              2,
              0,
              200,
              END.plusSeconds(1),
              null,
              null),
          snapshot(
              FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, "OTHER", null),
          snapshot(
              FIXTURE_SUCCESS_10855C7F, EXPIRY_CUTOFF, 3L, 1L, 2, 2, 0, 200, END, null, "OTHER")
        };
    for (var candidate : terminalMutations)
      assertFalse(
          ExpiryAuditRepository.matchesTerminal(
              java.util.Optional.of(candidate), stage, END, 1L, SUCCESS));
  }

  private static ExpiryAuditRepository.Snapshot snapshot(
      String status,
      Instant cutoff,
      Long before,
      Long after,
      long target,
      long success,
      long failure,
      long bytes,
      Instant ended,
      String code,
      String summary) {
    return new ExpiryAuditRepository.Snapshot(
        status, cutoff, before, after, target, success, failure, bytes, ended, code, summary);
  }

  private static Connection locked() throws SQLException {
    var connection = db.open("schubert_batch");
    execute(connection, "set timezone='UTC'");
    execute(connection, "select pg_advisory_lock(71419602)");
    connection.setAutoCommit(false);
    return connection;
  }

  private static void execute(Connection connection, String sql) throws SQLException {
    try (var statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }

  private static String audit(Connection connection, long id) throws SQLException {
    try (var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select coalesce(to_char(expiry_cutoff_at AT TIME ZONE 'UTC',"
                    + "'YYYY-MM-DD HH24:MI:SS.US'),'NULL')||'|'||"
                    + "coalesce(expiry_before_count::text,'NULL')||'|'||"
                    + "coalesce(expiry_after_count::text,'NULL')||'|'||target_count||'|'||"
                    + "success_count||'|'||failure_count||'|'||byte_count from schubert.batch_runs"
                    + " where id="
                    + id)) {
      assertTrue(rows.next());
      String result = rows.getString(1);
      assertFalse(rows.next());
      return result;
    }
  }

  private static String terminal(Connection connection, long id) throws SQLException {
    try (var statement = connection.createStatement();
        var rows =
            statement.executeQuery(
                "select status||'|'||success_count||'|'||failure_count||'|'||"
                    + "coalesce(error_code,'NULL') from schubert.batch_runs where id="
                    + id)) {
      assertTrue(rows.next());
      String result = rows.getString(1);
      assertFalse(rows.next());
      return result;
    }
  }
}
