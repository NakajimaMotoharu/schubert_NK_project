package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** EXPPORT-J001..009: borrowed JDBC and Guard callbacks, no true owner/session/DB/Root. */
final class ExpiryAuditPortTest {
  private static final String HANDLE =
      "id=? and run_id=? and business_date=? and step='CLEAN_EXPIRY' and attempt=? and"
          + " started_at=?";
  private static final String REF_SQL =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final String READ_SQL =
      "select status,expiry_cutoff_at,expiry_before_count,expiry_after_count,"
          + "target_count,success_count,failure_count,byte_count,ended_at,error_code,"
          + "error_summary from schubert.batch_runs where "
          + HANDLE;
  private static final String STAGE_SQL =
      "update schubert.batch_runs set expiry_cutoff_at=?,expiry_before_count=?,"
          + "target_count=?,byte_count=? where "
          + HANDLE
          + " and status='RUNNING' and ended_at is null"
          + " and expiry_cutoff_at is null and expiry_before_count is null"
          + " and expiry_after_count is null and target_count=0 and success_count=0"
          + " and failure_count=0 and byte_count=0";
  private static final String FINISH_SQL =
      "update schubert.batch_runs set"
          + " ended_at=?,status=?,success_count=?,failure_count=?,error_code=?,error_summary=?,expiry_after_count=?"
          + " where "
          + HANDLE
          + " and status='RUNNING' and ended_at is null"
          + " and expiry_cutoff_at=? and expiry_before_count=?"
          + " and target_count=? and byte_count=? and expiry_after_count is null";
  private static final String SUCCESS_SQL =
      "select id,run_id,attempt,started_at from schubert.batch_runs where"
          + " business_date=? and step='CLEAN_EXPIRY' and status='SUCCESS' order by"
          + " attempt desc limit 2";
  private static final String REF = "ref";
  private static final String READ = "read";
  private static final String STAGE = "stage";
  private static final String FINISH = "finish";
  private static final String RETAINED = "retained";
  private static final String PREPARE = "prepare";
  private static final String TIMEOUT = "timeout";
  private static final String BIND = "bind";
  private static final String QUERY = "query";
  private static final String NEXT = "next";
  private static final String ROW_CLOSE = "rowClose";
  private static final String CLOSE = "close";
  private static final String UPDATE = "update";
  private static final String STATUS = "status";
  private static final String CUTOFF = "expiry_cutoff_at";
  private static final String BEFORE = "expiry_before_count";
  private static final String AFTER = "expiry_after_count";
  private static final String TARGET = "target_count";
  private static final String REMOVED = "success_count";
  private static final String FAILED = "failure_count";
  private static final String BYTES = "byte_count";
  private static final String ENDED = "ended_at";
  private static final String CODE = "error_code";
  private static final String SUMMARY = "error_summary";
  private static final String RUNNING = "RUNNING";
  private static final String SUCCEEDED = "SUCCESS";
  private static final String MISSING_STATEMENT = "statement";
  private static final String MISSING_ROW = "row";
  private static final Instant CUTOFF_AT = Instant.parse("2026-11-05T00:00:00Z");
  private static final Instant EXPIRY_AT = Instant.parse("2026-10-29T00:00:00Z");
  private static final Instant START_AT = Instant.parse("2026-11-05T00:00:01Z");
  private static final Instant END_AT = Instant.parse("2026-11-05T00:00:02Z");
  private static final BatchRun RUN = new BatchRun(new UUID(0, 1), CUTOFF_AT);
  private static final BatchStepAttempt ATTEMPT =
      new BatchStepAttempt(7, RUN, BatchStep.CLEAN_EXPIRY, 1, START_AT, false);
  private static final ExpiryAuditRepository.Stage STAGED =
      new ExpiryAuditRepository.Stage(EXPIRY_AT, 3, 2, 200);
  private static final BatchStepResult RESULT =
      new BatchStepResult(
          BatchStepResult.Status.SUCCESS, 2, 2, 0, 200, BatchStepResult.Reason.NONE);

  @Test
  void readUsesElevenTypedColumnsAndLiteralHandleOrReturnsOnlyTrueAbsence() {
    Fixture fixture = new Fixture();
    var actual = fixture.repository().read(ATTEMPT).orElseThrow();
    assertEquals(RUNNING, actual.status());
    assertEquals(EXPIRY_AT, actual.cutoff());
    assertEquals(3L, actual.before());
    assertNull(actual.after());
    assertEquals(2, actual.target());
    assertEquals(0, actual.success());
    assertEquals(0, actual.failure());
    assertEquals(200, actual.estimatedBytes());
    assertNull(actual.ended());
    assertNull(actual.errorCode());
    assertNull(actual.errorSummary());
    Port query = fixture.only(READ);
    assertEquals(READ_SQL, query.sql);
    assertEquals(handleBindings(1), query.bindings);
    assertEquals(5, query.timeout);
    fixture.assertClosed();
    Fixture absent = new Fixture();
    absent.readRows = 0;
    assertTrue(absent.repository().read(ATTEMPT).isEmpty());
    absent.assertClosed();
    Fixture emptyStage = new Fixture();
    emptyStage.snapshot.put(CUTOFF, null);
    emptyStage.snapshot.put(BEFORE, null);
    emptyStage.snapshot.put(TARGET, 0L);
    emptyStage.snapshot.put(BYTES, 0L);
    assertNull(emptyStage.repository().read(ATTEMPT).orElseThrow().cutoff());
    emptyStage.assertClosed();
    for (String field : List.of(STATUS, TARGET, REMOVED, FAILED, BYTES)) {
      Fixture invalid = new Fixture();
      invalid.snapshot.put(field, null);
      catalog(() -> invalid.repository().read(ATTEMPT));
      invalid.assertClosed();
    }
    Fixture malformed = new Fixture();
    malformed.snapshot.put(TARGET, 4L);
    catalog(() -> malformed.repository().read(ATTEMPT));
    malformed.assertClosed();
  }

  @Test
  void readOwnedScopesPreserveUnknownIdentityAndCatalogOnlySqlIncludingNullAcquisitions() {
    for (String missing : List.of(MISSING_STATEMENT, MISSING_ROW)) {
      Fixture fixture = new Fixture();
      fixture.missingRoute = READ;
      fixture.missingKind = missing;
      catalog(() -> fixture.repository().read(ATTEMPT));
      fixture.assertClosed();
    }
    var points = new ArrayList<>(List.of(PREPARE, TIMEOUT, BIND, QUERY, NEXT, ROW_CLOSE, CLOSE));
    points.addAll(
        List.of(
            STATUS, CUTOFF, BEFORE, AFTER, TARGET, REMOVED, FAILED, BYTES, ENDED, CODE, SUMMARY));
    for (String point : points) {
      for (Throwable original : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(READ + "." + point, original);
        expectedRead(original, () -> fixture.repository().read(ATTEMPT));
        fixture.assertClosed();
      }
    }
    for (String closing : List.of(ROW_CLOSE, CLOSE)) {
      for (int kind = 0; kind < 3; kind++) {
        for (Throwable secondary : failures()) {
          Throwable primary = failures().get(kind);
          Fixture fixture = new Fixture();
          fixture.faults = Map.of(READ + "." + NEXT, primary, READ + "." + closing, secondary);
          Throwable selected =
              primary instanceof SQLException && !(secondary instanceof SQLException)
                  ? secondary
                  : primary;
          expectedRead(selected, () -> fixture.repository().read(ATTEMPT));
          fixture.assertClosed();
          if (!(primary instanceof SQLException)) {
            assertEquals(1, primary.getSuppressed().length);
            assertEquals(BatchRepositoryException.class, primary.getSuppressed()[0].getClass());
          }
        }
      }
    }
  }

  @Test
  void stageLiteralUpdateAndZeroCountReplayRespectTheExactCommittedObservation() {
    Fixture fixture = new Fixture();
    var actual = fixture.repository().stage(ATTEMPT, 3, 2, 200);
    assertEquals(EXPIRY_AT, actual.cutoff());
    assertEquals(3, actual.before());
    assertEquals(2, actual.target());
    assertEquals(200, actual.estimatedBytes());
    Port update = fixture.only(STAGE);
    var expected = handleBindings(5);
    expected.putAll(Map.of(1, EXPIRY_AT.atOffset(ZoneOffset.UTC), 2, 3L, 3, 2L, 4, 200L));
    assertEquals(expected, update.bindings);
    assertEquals(STAGE_SQL, update.sql);
    assertEquals(5, update.timeout);
    assertEquals(0, fixture.count(READ));
    fixture.assertClosed();
    Fixture replay = new Fixture();
    replay.changed = 0;
    assertEquals(STAGED, replay.repository().stage(ATTEMPT, 3, 2, 200));
    assertEquals(1, replay.count(READ));
    replay.assertClosed();
    for (boolean absent : new boolean[] {false, true}) {
      Fixture mismatch = new Fixture();
      mismatch.changed = 0;
      if (absent) mismatch.readRows = 0;
      else mismatch.snapshot.put(BYTES, 201L);
      catalog(() -> mismatch.repository().stage(ATTEMPT, 3, 2, 200));
      mismatch.assertClosed();
    }
  }

  @Test
  void finishLiteralUpdateAndZeroReplayBindAllSixteenColumnsWithoutBorrowedCommit() {
    Fixture fixture = new Fixture();
    fixture.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT);
    assertFinishBindings(fixture.only(FINISH));
    fixture.assertClosed();
    Fixture replay = new Fixture();
    replay.changed = 0;
    replay.terminal();
    replay.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT);
    assertEquals(1, replay.count(READ));
    replay.assertClosed();
    for (boolean absent : new boolean[] {false, true}) {
      Fixture mismatch = new Fixture();
      mismatch.changed = 0;
      mismatch.terminal();
      if (absent) mismatch.readRows = 0;
      else mismatch.snapshot.put(BYTES, 201L);
      catalog(() -> mismatch.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT));
      mismatch.assertClosed();
    }
    Fixture unknownAfter = new Fixture();
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 2, 0, 2, 200, BatchStepResult.Reason.IO_FAILURE);
    unknownAfter.repository().finish(ATTEMPT, STAGED, END_AT, null, failed);
    Port terminal = unknownAfter.only(FINISH);
    assertNull(terminal.bindings.get(7));
    assertEquals("IO_FAILURE", terminal.bindings.get(5));
    assertEquals("batch file operation failed", terminal.bindings.get(6));
    unknownAfter.assertClosed();
    Fixture warning = new Fixture();
    var partial =
        new BatchStepResult(
            BatchStepResult.Status.WARNING, 2, 1, 1, 200, BatchStepResult.Reason.PROTECTED_RECORDS);
    warning.repository().finish(ATTEMPT, STAGED, END_AT, 2L, partial);
    assertEquals("WARNING", warning.only(FINISH).bindings.get(2));
    assertEquals(1L, warning.only(FINISH).bindings.get(3));
    assertEquals(2L, warning.only(FINISH).bindings.get(7));
    warning.assertClosed();
  }

  @Test
  void updateCompoundFailurePreservesTheOwnedStatementPrimaryAndCloseFailure() {
    for (var route : List.of(STAGE, FINISH)) {
      var primary = new LinkageError("public update failure fixture");
      var secondary = new SQLException("public close failure fixture");
      var fixture = new Fixture();
      fixture.faults = Map.of(route + "." + UPDATE, primary, route + "." + CLOSE, secondary);
      var failure =
          assertThrows(
              LinkageError.class,
              () -> {
                if (route.equals(STAGE)) fixture.repository().stage(ATTEMPT, 3, 2, 200);
                else fixture.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT);
              });
      assertSame(primary, failure);
      assertArrayEquals(new Throwable[] {secondary}, failure.getSuppressed());
      fixture.assertClosed();
    }
  }

  @Test
  void invalidAttemptAndEveryTerminalRelationRejectBeforeAnySqlAcquisition() {
    assertThrows(NullPointerException.class, () -> new ExpiryAuditRepository(null));
    Fixture fixture = new Fixture();
    var repo = fixture.repository();
    assertThrows(NullPointerException.class, () -> repo.read(null));
    assertThrows(NullPointerException.class, () -> repo.stage(null, 3, 2, 200));
    assertThrows(NullPointerException.class, () -> repo.finish(ATTEMPT, null, END_AT, 1L, RESULT));
    assertThrows(NullPointerException.class, () -> repo.finish(ATTEMPT, STAGED, null, 1L, RESULT));
    assertThrows(NullPointerException.class, () -> repo.finish(ATTEMPT, STAGED, END_AT, 1L, null));
    for (BatchStepAttempt invalid :
        List.of(
            new BatchStepAttempt(7, RUN, BatchStep.CLEAN_LOG, 1, START_AT, false),
            new BatchStepAttempt(7, RUN, BatchStep.CLEAN_EXPIRY, 1, START_AT, true))) {
      assertThrows(IllegalArgumentException.class, () -> repo.read(invalid));
      assertThrows(IllegalArgumentException.class, () -> repo.stage(invalid, 3, 2, 200));
      assertThrows(
          IllegalArgumentException.class, () -> repo.finish(invalid, STAGED, END_AT, 1L, RESULT));
    }
    assertThrows(
        IllegalArgumentException.class, () -> repo.finish(ATTEMPT, STAGED, CUTOFF_AT, 1L, RESULT));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            repo.finish(
                ATTEMPT,
                new ExpiryAuditRepository.Stage(EXPIRY_AT.plusSeconds(1), 3, 2, 200),
                END_AT,
                1L,
                RESULT));
    var skipped =
        new BatchStepResult(
            BatchStepResult.Status.SKIPPED, 0, 0, 0, 0, BatchStepResult.Reason.ALREADY_SUCCESSFUL);
    assertThrows(
        IllegalArgumentException.class, () -> repo.finish(ATTEMPT, STAGED, END_AT, null, skipped));
    var targetMismatch =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 1, 1, 0, 200, BatchStepResult.Reason.NONE);
    assertThrows(
        IllegalArgumentException.class,
        () -> repo.finish(ATTEMPT, STAGED, END_AT, 2L, targetMismatch));
    var bytesMismatch =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 2, 2, 0, 201, BatchStepResult.Reason.NONE);
    assertThrows(
        IllegalArgumentException.class,
        () -> repo.finish(ATTEMPT, STAGED, END_AT, 1L, bytesMismatch));
    assertThrows(
        IllegalArgumentException.class, () -> repo.finish(ATTEMPT, STAGED, END_AT, null, RESULT));
    for (long after : new long[] {-1, 4, 2})
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.finish(ATTEMPT, STAGED, END_AT, after, RESULT));
    var failedNonzero =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 2, 1, 1, 200, BatchStepResult.Reason.IO_FAILURE);
    assertThrows(
        IllegalArgumentException.class,
        () -> repo.finish(ATTEMPT, STAGED, END_AT, null, failedNonzero));
    var wrongSuccess =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 2, 1, 0, 200, BatchStepResult.Reason.NONE);
    assertThrows(
        IllegalArgumentException.class,
        () -> repo.finish(ATTEMPT, STAGED, END_AT, 2L, wrongSuccess));
    assertTrue(fixture.ports.isEmpty());
  }

  @Test
  void retainedSuccessUsesDefaultOrExplicitSameDayOriginalOnlyAndClosesBeforeReturn()
      throws Exception {
    Fixture fixture = new Fixture();
    fixture.terminal();
    var guard = new GuardPort();
    var actual = fixture.repository().successful(RUN, END_AT, guard).orElseThrow();
    assertEquals(7, actual.handle().id());
    assertEquals(new UUID(0, 1), actual.handle().run().id());
    assertEquals(CUTOFF_AT, actual.handle().run().cutoff());
    assertEquals(END_AT, actual.audit().ended());
    assertEquals(SUCCESS_SQL, fixture.only(RETAINED).sql);
    assertEquals(Map.of(1, LocalDate.of(2026, 11, 5)), fixture.only(RETAINED).bindings);
    assertEquals(5, fixture.only(RETAINED).timeout);
    assertEquals(3, guard.calls);
    fixture.assertClosed();
    Fixture prior = new Fixture();
    prior.priorRun = new BatchRun(new UUID(0, 2), Instant.parse("2026-11-04T23:00:00Z"));
    prior.priorStart = Instant.parse("2026-11-04T23:00:01Z");
    prior.terminal();
    prior.snapshot.put(CUTOFF, Instant.parse("2026-10-28T23:00:00Z").atOffset(ZoneOffset.UTC));
    prior.snapshot.put(ENDED, Instant.parse("2026-11-04T23:00:02Z").atOffset(ZoneOffset.UTC));
    var old =
        prior
            .repository()
            .successful(
                RUN,
                END_AT,
                new GuardPort(),
                (id, observed) -> {
                  assertEquals(new UUID(0, 2), id);
                  assertEquals(END_AT, observed);
                  return prior.priorRun;
                })
            .orElseThrow();
    assertEquals(new UUID(0, 2), old.handle().run().id());
    assertEquals(Instant.parse("2026-11-04T23:00:00Z"), old.handle().run().cutoff());
    assertEquals(Instant.parse("2026-11-04T23:00:02Z"), old.audit().ended());
    prior.assertClosed();
    Fixture absent = new Fixture();
    absent.retainedRows = 0;
    assertTrue(absent.repository().successful(RUN, END_AT, new GuardPort()).isEmpty());
    absent.assertClosed();
  }

  @Test
  void retainedLookupAndBadProjectionsCannotFabricateAnOriginalOrAdmitBrokenAudit() {
    Fixture otherId = new Fixture();
    otherId.priorRun = new BatchRun(new UUID(0, 2), CUTOFF_AT);
    assertThrows(
        IOException.class, () -> otherId.repository().successful(RUN, END_AT, new GuardPort()));
    otherId.assertClosed();
    for (BatchRun wrong :
        List.of(
            new BatchRun(new UUID(0, 2), CUTOFF_AT),
            new BatchRun(new UUID(0, 1), Instant.parse("2026-11-03T00:00:00Z")))) {
      Fixture fixture = new Fixture();
      catalog(
          () ->
              fixture
                  .repository()
                  .successful(RUN, END_AT, new GuardPort(), (id, observed) -> wrong));
      fixture.assertClosed();
    }
    for (String bad :
        List.of(
            "duplicate",
            "missingAudit",
            "errorCode",
            "errorSummary",
            "futureEnd",
            "nullId",
            "nullRun",
            "nullAttempt",
            "nullStart")) {
      Fixture fixture = new Fixture();
      fixture.terminal();
      switch (bad) {
        case "duplicate" -> fixture.retainedRows = 2;
        case "missingAudit" -> fixture.readRows = 0;
        case "errorCode" -> fixture.snapshot.put(CODE, "");
        case "errorSummary" -> fixture.snapshot.put(SUMMARY, "");
        case "futureEnd" ->
            fixture.snapshot.put(ENDED, END_AT.plusNanos(1000).atOffset(ZoneOffset.UTC));
        default -> fixture.nullPriorColumn = bad;
      }
      catalog(() -> fixture.repository().successful(RUN, END_AT, new GuardPort()));
      fixture.assertClosed();
    }
    Fixture nullOriginal = new Fixture();
    assertThrows(
        NullPointerException.class,
        () ->
            nullOriginal.repository().successful(RUN, END_AT, new GuardPort(), (id, time) -> null));
    nullOriginal.assertClosed();
  }

  @Test
  void guardAndJdbcFailuresHaveDeclaredPhaseSemanticsWithNoPrivilegedOwnerActions() {
    for (int failing : new int[] {1, 2, 3}) {
      Fixture fixture = new Fixture();
      fixture.terminal();
      GuardPort guard = new GuardPort();
      guard.failAt = failing;
      IOException observed =
          assertThrows(
              IOException.class, () -> fixture.repository().successful(RUN, END_AT, guard));
      assertSame(guard.failure, observed);
      fixture.assertClosed();
    }
    for (String route : List.of(STAGE, FINISH, RETAINED)) {
      for (String point : List.of(PREPARE, TIMEOUT, BIND, QUERY, NEXT, ROW_CLOSE, CLOSE, UPDATE)) {
        if ((route.equals(STAGE) || route.equals(FINISH))
            && List.of(QUERY, NEXT, ROW_CLOSE).contains(point)) continue;
        if (route.equals(RETAINED) && point.equals(UPDATE)) continue;
        for (Throwable original : failures()) {
          Fixture fixture = new Fixture();
          fixture.terminal();
          fixture.faults = Map.of(route + "." + point, original);
          Executable operation =
              () -> {
                switch (route) {
                  case STAGE -> fixture.repository().stage(ATTEMPT, 3, 2, 200);
                  case FINISH -> fixture.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT);
                  default -> fixture.repository().successful(RUN, END_AT, new GuardPort());
                }
              };
          if (original instanceof Error
              || route.equals(RETAINED) && original instanceof RuntimeException)
            assertSame(original, assertThrows(original.getClass(), operation));
          else catalog(operation);
          fixture.assertClosed();
        }
      }
    }
    Fixture lookup = new Fixture();
    IOException failure = new IOException("own original lookup failure");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                lookup
                    .repository()
                    .successful(
                        RUN,
                        END_AT,
                        new GuardPort(),
                        (id, time) -> {
                          throw failure;
                        })));
    lookup.assertClosed();
  }

  @Test
  void nullPortsAndFailedParentIdentityCannotBeAcceptedByAConvenientFallback() {
    Fixture fixture = new Fixture();
    var repo = fixture.repository();
    assertThrows(NullPointerException.class, () -> repo.successful(null, END_AT, new GuardPort()));
    assertThrows(NullPointerException.class, () -> repo.successful(RUN, null, new GuardPort()));
    assertThrows(NullPointerException.class, () -> repo.successful(RUN, END_AT, null));
    assertThrows(
        NullPointerException.class, () -> repo.successful(RUN, END_AT, new GuardPort(), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> repo.successful(RUN, START_AT.minusSeconds(2), new GuardPort()));
    assertTrue(fixture.ports.isEmpty());
    for (String route : List.of(STAGE, FINISH, RETAINED)) {
      Fixture parent = new Fixture();
      parent.consistent = false;
      catalog(
          () -> {
            switch (route) {
              case STAGE -> parent.repository().stage(ATTEMPT, 3, 2, 200);
              case FINISH -> parent.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT);
              default -> parent.repository().successful(RUN, END_AT, new GuardPort());
            }
          });
      assertEquals(0, parent.count(route));
      parent.assertClosed();
    }
    for (String route : List.of(STAGE, FINISH)) {
      Fixture late = new Fixture();
      late.invalidateAfterUpdate = true;
      catalog(
          () -> {
            if (route.equals(STAGE)) late.repository().stage(ATTEMPT, 3, 2, 200);
            else late.repository().finish(ATTEMPT, STAGED, END_AT, 1L, RESULT);
          });
      assertEquals(1, late.count(route));
      late.assertClosed();
    }
    Fixture lateRead = new Fixture();
    lateRead.invalidateAfterProjection = true;
    catalog(() -> lateRead.repository().read(ATTEMPT));
    lateRead.assertClosed();
    for (String missing : List.of(MISSING_STATEMENT, MISSING_ROW)) {
      Fixture absent = new Fixture();
      absent.missingRoute = RETAINED;
      absent.missingKind = missing;
      catalog(() -> absent.repository().successful(RUN, END_AT, new GuardPort()));
      absent.assertClosed();
    }
  }

  private static Map<Integer, Object> handleBindings(int first) {
    Map<Integer, Object> values = new HashMap<>();
    values.put(first, 7L);
    values.put(first + 1, new UUID(0, 1));
    values.put(first + 2, LocalDate.of(2026, 11, 5));
    values.put(first + 3, 1);
    values.put(first + 4, START_AT.atOffset(ZoneOffset.UTC));
    return values;
  }

  private static void assertFinishBindings(Port port) {
    var expected = handleBindings(8);
    expected.put(1, END_AT.atOffset(ZoneOffset.UTC));
    expected.put(2, SUCCEEDED);
    expected.put(3, 2L);
    expected.put(4, 0L);
    expected.put(5, null);
    expected.put(6, null);
    expected.put(7, 1L);
    expected.put(13, EXPIRY_AT.atOffset(ZoneOffset.UTC));
    expected.put(14, 3L);
    expected.put(15, 2L);
    expected.put(16, 200L);
    assertEquals(expected, port.bindings);
    assertEquals(FINISH_SQL, port.sql);
    assertEquals(5, port.timeout);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("own SQL"),
        new IllegalStateException("own provider runtime"),
        new AssertionError("own provider Error"));
  }

  private static void expectedRead(Throwable original, Executable action) {
    if (original instanceof SQLException) catalog(action);
    else assertSame(original, assertThrows(original.getClass(), action));
  }

  private static void catalog(Executable action) {
    var actual = assertThrows(BatchRepositoryException.class, action);
    assertEquals("batch repository operation failed", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
  }

  /** A bounded callback only, never a real MaintenanceOwnerFrame or authority. */
  private static final class GuardPort implements Guard {
    final IOException failure = new IOException("own borrowed guard failure");
    int calls;
    int failAt = -1;

    @Override
    public long remainingNanos() throws IOException {
      calls++;
      if (calls == failAt) throw failure;
      return 5_000_000_000L;
    }
  }

  private static final class Fixture {
    final List<Port> ports = new ArrayList<>();
    final Map<String, Object> snapshot = new HashMap<>();
    Map<String, Throwable> faults = Map.of();
    String missingRoute = "none";
    String missingKind = "none";
    String nullPriorColumn = "none";
    boolean consistent = true;
    boolean invalidateAfterUpdate;
    boolean invalidateAfterProjection;
    int changed = 1;
    int readRows = 1;
    int retainedRows = 1;
    BatchRun priorRun = RUN;
    Instant priorStart = START_AT;

    Fixture() {
      snapshot.put(STATUS, RUNNING);
      snapshot.put(CUTOFF, EXPIRY_AT.atOffset(ZoneOffset.UTC));
      snapshot.put(BEFORE, 3L);
      snapshot.put(AFTER, null);
      snapshot.put(TARGET, 2L);
      snapshot.put(REMOVED, 0L);
      snapshot.put(FAILED, 0L);
      snapshot.put(BYTES, 200L);
      snapshot.put(ENDED, null);
      snapshot.put(CODE, null);
      snapshot.put(SUMMARY, null);
    }

    void terminal() {
      snapshot.put(STATUS, SUCCEEDED);
      snapshot.put(AFTER, 1L);
      snapshot.put(REMOVED, 2L);
      snapshot.put(ENDED, END_AT.atOffset(ZoneOffset.UTC));
    }

    void fault(String route, String point) throws Throwable {
      Throwable failure = faults.get(route + "." + point);
      if (failure != null) throw failure;
    }

    ExpiryAuditRepository repository() {
      return new ExpiryAuditRepository(connection());
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "getAutoCommit", "isReadOnly" -> false;
                  case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                  case "prepareStatement" -> {
                    String sql = (String) args[0];
                    String route = route(sql);
                    fault(route, PREPARE);
                    if (missingRoute.equals(route) && missingKind.equals(MISSING_STATEMENT))
                      yield null;
                    var port = new Port(this, route, sql);
                    ports.add(port);
                    yield port.statement();
                  }
                  default ->
                      throw new AssertionError("borrowed parent connection lifetime mutated");
                };
              });
    }

    static String route(String sql) {
      if (sql.equals(REF_SQL)) return REF;
      if (sql.equals(READ_SQL)) return READ;
      if (sql.equals(STAGE_SQL)) return STAGE;
      if (sql.equals(FINISH_SQL)) return FINISH;
      if (sql.equals(SUCCESS_SQL)) return RETAINED;
      throw new AssertionError("SQL differs from independent literal catalog");
    }

    Port only(String route) {
      var matches = ports.stream().filter(port -> port.route.equals(route)).toList();
      assertEquals(1, matches.size());
      return matches.getFirst();
    }

    long count(String route) {
      return ports.stream().filter(port -> port.route.equals(route)).count();
    }

    void assertClosed() {
      for (Port port : ports) {
        assertEquals(1, port.closes, port.route);
        assertEquals(port.rowOpened ? 1 : 0, port.rowCloses, port.route);
      }
    }
  }

  private static final class Port {
    final Fixture fixture;
    final String route;
    final String sql;
    final Map<Integer, Object> bindings = new HashMap<>();
    int timeout;
    int closes;
    int rowCloses;
    int nextCalls;
    boolean rowOpened;

    Port(Fixture fixture, String route, String sql) {
      this.fixture = fixture;
      this.route = route;
      this.sql = sql;
    }

    PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    timeout = (Integer) args[0];
                    fixture.fault(route, TIMEOUT);
                    yield null;
                  }
                  case "setObject", "setLong", "setInt", "setString" -> {
                    bindings.put((Integer) args[0], args[1]);
                    fixture.fault(route, BIND);
                    yield null;
                  }
                  case "executeUpdate" -> {
                    fixture.fault(route, UPDATE);
                    if (fixture.invalidateAfterUpdate) fixture.consistent = false;
                    yield fixture.changed;
                  }
                  case "executeQuery" -> {
                    fixture.fault(route, QUERY);
                    if (fixture.missingRoute.equals(route)
                        && fixture.missingKind.equals(MISSING_ROW)) yield null;
                    rowOpened = true;
                    yield rows();
                  }
                  case "close" -> {
                    closes++;
                    fixture.fault(route, CLOSE);
                    yield null;
                  }
                  default -> throw new AssertionError("unexpected owned statement operation");
                };
              });
    }

    ResultSet rows() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "next" -> {
                    fixture.fault(route, NEXT);
                    nextCalls++;
                    int count =
                        route.equals(REF)
                            ? 1
                            : route.equals(READ) ? fixture.readRows : fixture.retainedRows;
                    yield nextCalls <= count;
                  }
                  case "getObject", "getString" -> {
                    String column = (String) args[0];
                    fixture.fault(route, column);
                    Object value = value(column);
                    if (args.length == 2 && value != null)
                      assertTrue(((Class<?>) args[1]).isInstance(value), column);
                    yield value;
                  }
                  case "close" -> {
                    rowCloses++;
                    fixture.fault(route, ROW_CLOSE);
                    yield null;
                  }
                  default -> throw new AssertionError("unexpected owned row operation");
                };
              });
    }

    Object value(String column) {
      if (route.equals(READ)) {
        assertTrue(fixture.snapshot.containsKey(column));
        Object value = fixture.snapshot.get(column);
        if (fixture.invalidateAfterProjection && column.equals(SUMMARY)) fixture.consistent = false;
        return value;
      }
      if (route.equals(REF))
        return column.equals("has_batch_history")
            || column.equals("identity_consistent") && fixture.consistent;
      return switch (column) {
        case "id" -> fixture.nullPriorColumn.equals("nullId") ? null : 7L;
        case "run_id" -> fixture.nullPriorColumn.equals("nullRun") ? null : fixture.priorRun.id();
        case "attempt" -> fixture.nullPriorColumn.equals("nullAttempt") ? null : 1;
        case "started_at" ->
            fixture.nullPriorColumn.equals("nullStart")
                ? null
                : fixture.priorStart.atOffset(ZoneOffset.UTC);
        default -> throw new AssertionError("unexpected retained projection column");
      };
    }
  }
}
