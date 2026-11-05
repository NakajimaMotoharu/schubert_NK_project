package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

/** BRPORT001..014: borrowed JDBC memory rows, no actual owner, DB, recovery, files or Root. */
final class BatchRunAuditPortTest {
  private static final String TEXT_RUNNING = "RUNNING";
  private static final String TEXT_SUCCESS = "SUCCESS";
  private static final String TEXT_ATTEMPT = "attempt";
  private static final String TEXT_ENDED_AT = "ended_at";
  private static final String TEXT_MATCHES = "matches";
  private static final String TEXT_NEXT = "next";
  private static final String TEXT_SETOBJECT = "setObject";
  private static final String TEXT_SETSTRING = "setString";
  private static final String TEXT_STARTED_AT = "started_at";
  private static final Instant BASE = Instant.parse("2026-11-05T00:00:00Z");
  private static final Instant NOW = BASE.plusSeconds(5);
  private static final Instant END = BASE.plusSeconds(6);
  private static final UUID ID = new UUID(0, 1);
  private static final UUID FOREIGN = new UUID(0, 2);
  private static final BatchRun RUN = new BatchRun(ID, BASE);
  private static final LocalDate DAY = LocalDate.of(2026, 11, 5);
  private static final String FIXED = "batch repository operation failed";
  private static final String REFS = "refs";
  private static final String HISTORY = "history";
  private static final String INSERT = "insert";
  private static final String ABANDON = "abandon";
  private static final String FINISH = "finish";
  private static final String REPLAY = "replay";
  private static final String SQL_REFS =
      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent"
          + " from schubert.maintenance_read_run_references(?,?)";
  private static final String SQL_HISTORY =
      "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count from schubert.batch_runs"
          + " where business_date=? and step=? order by attempt limit 100 for update";
  private static final String SQL_INSERT =
      "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,"
          + "status,target_count,success_count,failure_count,byte_count,error_code,error_summary)"
          + " values(?,?,?,?,?,?,?,0,0,0,0,?,?) returning id";
  private static final String SQL_ABANDON =
      "update schubert.batch_runs set status='FAILED',ended_at=?,error_code=?,error_summary=?"
          + " where id=? and run_id=? and started_at=? and status='RUNNING' and ended_at is null";
  private static final String HANDLE =
      "id=? and run_id=? and business_date=? and step=? and attempt=? and started_at=?";
  private static final String SQL_FINISH =
      "update schubert.batch_runs set ended_at=?,status=?,target_count=?,success_count=?,"
          + "failure_count=?,byte_count=?,error_code=?,error_summary=? where "
          + HANDLE
          + " and status='RUNNING' and ended_at is null";
  private static final String SQL_REPLAY =
      "select exists(select 1 from schubert.batch_runs where ended_at=? and status=?"
          + " and target_count=? and success_count=? and failure_count=? and byte_count=?"
          + " and error_code is not distinct from ? and error_summary is not distinct from ?"
          + " and "
          + HANDLE
          + ") as matches";

  @Test
  void emptyBeginAndSixBackupDependentSkipsUseLiteralSqlAndTypedNineBindings() {
    Fixture fixture = new Fixture();
    var actual = fixture.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false);
    assertEquals(new BatchStepAttempt(7, RUN, BatchStep.CLEAN_LOG, 1, NOW, false), actual);
    assertEquals(List.of(REFS, HISTORY, INSERT, REFS), fixture.routes);
    assertEquals(Map.of(1, DAY, 2, "CLEAN_LOG"), fixture.bindings.get(HISTORY).getFirst());
    assertEquals(
        insertBindings(BatchStep.CLEAN_LOG, 1, false, null, null),
        fixture.bindings.get(INSERT).getFirst());
    fixture.assertClosed();
    for (BatchStep step :
        List.of(
            BatchStep.CLEAN_NOTIFICATION,
            BatchStep.CLEAN_QUESTION,
            BatchStep.CLEAN_SESSION,
            BatchStep.CLEAN_INBOX_OUTBOX,
            BatchStep.CLEAN_LOG,
            BatchStep.CLEAN_BATCH_RUN)) {
      Fixture skipped = new Fixture();
      var attempt = skipped.repository().beginBackupUnavailable(RUN, step, NOW, false);
      assertTrue(attempt.skipped());
      assertEquals(
          insertBindings(step, 1, true, "BACKUP_UNAVAILABLE", "verified backup unavailable"),
          skipped.bindings.get(INSERT).getFirst());
      skipped.assertClosed();
    }
  }

  @Test
  void successfulDaySkipsNonBackupButManualAndMorningBackupFollowDifferentRunContracts() {
    for (BatchStep step : List.of(BatchStep.CLEAN_LOG, BatchStep.BACKUP_DB)) {
      for (boolean sameRun : List.of(false, true)) {
        for (boolean morning : List.of(false, true)) {
          Fixture fixture = new Fixture();
          fixture.history =
              List.of(historicalRow(1, 1, sameRun ? ID : FOREIGN, step, TEXT_SUCCESS));
          var actual =
              morning
                  ? fixture.repository().beginMorningResume(RUN, step, NOW, false)
                  : fixture.repository().begin(RUN, step, NOW, false);
          boolean expected = step == BatchStep.CLEAN_LOG || (morning && sameRun);
          assertEquals(expected, actual.skipped());
          assertEquals(
              insertBindings(
                  step,
                  2,
                  expected,
                  expected ? "ALREADY_SUCCESSFUL" : null,
                  expected ? "step already successful for business date" : null),
              fixture.bindings.get(INSERT).getFirst());
          fixture.assertClosed();
        }
      }
    }
    Fixture backup = new Fixture();
    backup.history =
        List.of(
            historicalRow(1, 1, ID, BatchStep.BACKUP_DB, TEXT_SUCCESS),
            historicalRow(2, 2, FOREIGN, BatchStep.BACKUP_DB, TEXT_SUCCESS));
    assertFalse(backup.repository().begin(RUN, BatchStep.BACKUP_DB, NOW, false).skipped());
    assertEquals(3, backup.bindings.get(INSERT).getFirst().get(4));
    backup.assertClosed();
    Fixture morningWithoutSuccess = new Fixture();
    morningWithoutSuccess.history = List.of(historicalRow(1, 1, ID, BatchStep.BACKUP_DB, "FAILED"));
    assertFalse(
        morningWithoutSuccess
            .repository()
            .beginMorningResume(RUN, BatchStep.BACKUP_DB, NOW, false)
            .skipped());
    morningWithoutSuccess.assertClosed();
  }

  @Test
  void sameRunAbandonRequiresExplicitFlagAndValidatesEveryRowBeforeAnyMutation() {
    Fixture recovered = new Fixture();
    recovered.history =
        List.of(
            historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, TEXT_RUNNING),
            historicalRow(2, 2, ID, BatchStep.CLEAN_LOG, TEXT_RUNNING));
    assertEquals(3, recovered.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, true).attempt());
    assertEquals(2, recovered.bindings.get(ABANDON).size());
    for (int index = 0; index < 2; index++)
      assertEquals(
          Map.of(
              1,
              NOW.atOffset(ZoneOffset.UTC),
              2,
              "ABANDONED",
              3,
              "previous same-run attempt abandoned",
              4,
              index + 1L,
              5,
              ID,
              6,
              BASE.plusSeconds(1).atOffset(ZoneOffset.UTC)),
          recovered.bindings.get(ABANDON).get(index));
    recovered.assertClosed();
    for (boolean foreign : List.of(false, true)) {
      Fixture invalid = new Fixture();
      invalid.history =
          List.of(
              historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, TEXT_RUNNING),
              historicalRow(2, 2, foreign ? FOREIGN : ID, BatchStep.CLEAN_LOG, TEXT_RUNNING));
      catalog(() -> invalid.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, foreign));
      assertFalse(invalid.bindings.containsKey(ABANDON));
      assertFalse(invalid.bindings.containsKey(INSERT));
      invalid.assertClosed();
    }
    Fixture duplicateSuccess = new Fixture();
    duplicateSuccess.history =
        List.of(
            historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, TEXT_RUNNING),
            historicalRow(2, 2, ID, BatchStep.CLEAN_LOG, TEXT_SUCCESS),
            historicalRow(3, 3, FOREIGN, BatchStep.CLEAN_LOG, TEXT_SUCCESS));
    catalog(() -> duplicateSuccess.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, true));
    assertFalse(duplicateSuccess.bindings.containsKey(ABANDON));
    duplicateSuccess.assertClosed();
  }

  @Test
  void everyHistoryRequiredNullIdentityAttemptStatusCounterAndStoredTimeBoundaryIsIndependent() {
    for (String column :
        List.of(
            "id",
            "run_id",
            "business_date",
            "step",
            TEXT_ATTEMPT,
            TEXT_STARTED_AT,
            "status",
            "target_count",
            "success_count",
            "failure_count",
            "byte_count")) rejectHistory(List.of(changed(historicalRow(), column, null)));
    var invalid = new HashMap<String, Object>();
    invalid.put("id", 0L);
    invalid.put("business_date", DAY.plusDays(1));
    invalid.put("step", "CLEAN_QUESTION");
    invalid.put(TEXT_ATTEMPT, 0);
    invalid.put("status", "UNKNOWN");
    for (String column : List.of("target_count", "success_count", "failure_count", "byte_count"))
      invalid.put(column, -1L);
    invalid.forEach(
        (column, value) -> rejectHistory(List.of(changed(historicalRow(), column, value))));
    rejectHistory(List.of(changed(historicalRow(), "id", 1000000000000L)));
    rejectHistory(List.of(changed(historicalRow(), TEXT_ATTEMPT, 100)));
    rejectHistory(List.of(changed(historicalRow(), TEXT_ATTEMPT, 99)));
    rejectHistory(
        List.of(
            historicalRow(),
            changed(historicalRow(2, 2, ID, BatchStep.CLEAN_LOG, TEXT_SUCCESS), "id", 1L)));
    rejectHistory(
        List.of(historicalRow(), historicalRow(2, 1, ID, BatchStep.CLEAN_LOG, TEXT_SUCCESS)));
    for (Instant time :
        List.of(
            Instant.parse("0000-12-31T23:59:59Z"),
            NOW.plusSeconds(1),
            BASE.plusNanos(1),
            BASE.minusSeconds(1)))
      rejectHistory(
          List.of(changed(historicalRow(), TEXT_STARTED_AT, time.atOffset(ZoneOffset.UTC))));
    Fixture otherOriginal = new Fixture();
    otherOriginal.history =
        List.of(
            changed(
                historicalRow(1, 1, FOREIGN, BatchStep.CLEAN_LOG, TEXT_SUCCESS),
                TEXT_STARTED_AT,
                BASE.minusSeconds(1).atOffset(ZoneOffset.UTC)));
    assertTrue(otherOriginal.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false).skipped());
    otherOriginal.assertClosed();
    Fixture maxId = new Fixture();
    maxId.history = List.of(changed(historicalRow(), "id", 999999999999L));
    assertTrue(maxId.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false).skipped());
    maxId.assertClosed();
    var tooMany = new ArrayList<Map<String, Object>>();
    for (int number = 1; number <= 100; number++)
      tooMany.add(historicalRow(number, number, ID, BatchStep.CLEAN_LOG, TEXT_SUCCESS));
    rejectHistory(tooMany);
  }

  @Test
  void historyTerminalTimeAndRunningNullRelationshipRejectWithoutChangingAnyPastAttempt() {
    rejectHistory(
        List.of(
            changed(
                historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, TEXT_RUNNING),
                TEXT_ENDED_AT,
                END.atOffset(ZoneOffset.UTC))));
    rejectHistory(List.of(changed(historicalRow(), TEXT_ENDED_AT, null)));
    for (Instant invalid :
        List.of(Instant.parse("0000-12-31T23:59:59Z"), NOW.plusSeconds(1), BASE, NOW.minusNanos(1)))
      rejectHistory(
          List.of(changed(historicalRow(), TEXT_ENDED_AT, invalid.atOffset(ZoneOffset.UTC))));
    for (String status : List.of(TEXT_SUCCESS, "WARNING", "FAILED", "SKIPPED")) {
      Fixture fixture = new Fixture();
      fixture.history = List.of(historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, status));
      assertEquals(2, fixture.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false).attempt());
      assertFalse(fixture.bindings.containsKey(ABANDON));
      fixture.assertClosed();
    }
    Fixture last = new Fixture();
    last.history = List.of(historicalRow(1, 98, ID, BatchStep.CLEAN_LOG, "FAILED"));
    assertEquals(99, last.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false).attempt());
    last.assertClosed();
  }

  @Test
  void insertedIdMustBeExactlyOneNonNullValidHandleAndFailureClosesTheReturningRow() {
    for (List<Map<String, Object>> rows :
        List.<List<Map<String, Object>>>of(
            List.<Map<String, Object>>of(),
            List.of(Map.of("id", 7L), Map.of("id", 8L)),
            List.of(changed(Map.of("id", 7L), "id", null)),
            List.of(Map.of("id", 0L)),
            List.of(Map.of("id", 1000000000000L)))) {
      Fixture fixture = new Fixture();
      fixture.insertRows = rows;
      catalog(() -> fixture.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false));
      fixture.assertClosed();
    }
  }

  @Test
  void finishAndExactReplayUseFourteenTypedBindingsAndSkipReasonsAreNotInterchangeable() {
    for (int changed : new int[] {0, 1}) {
      Fixture fixture = new Fixture();
      fixture.finishChanged = changed;
      fixture.repository().finish(attempt(false), END, result());
      assertEquals(
          finishBindings(TEXT_SUCCESS, 1, 1, 0, 3, null, null, END),
          fixture.bindings.get(FINISH).getFirst());
      assertEquals(changed == 0, fixture.bindings.containsKey(REPLAY));
      fixture.assertClosed();
    }
    Fixture verified = new Fixture();
    verified.repository().verifyFinished(attempt(false), END, result());
    assertEquals(
        finishBindings(TEXT_SUCCESS, 1, 1, 0, 3, null, null, END),
        verified.bindings.get(REPLAY).getFirst());
    assertFalse(verified.bindings.containsKey(FINISH));
    verified.assertClosed();
    for (boolean unavailable : List.of(false, true)) {
      Fixture skipped = new Fixture();
      if (unavailable) skipped.repository().verifyBackupUnavailable(attempt(true));
      else skipped.repository().verifyAlreadySuccessful(attempt(true));
      assertEquals(
          finishBindings(
              "SKIPPED",
              0,
              0,
              0,
              0,
              unavailable ? "BACKUP_UNAVAILABLE" : "ALREADY_SUCCESSFUL",
              unavailable
                  ? "verified backup unavailable"
                  : "step already successful for business date",
              NOW),
          skipped.bindings.get(REPLAY).getFirst());
      skipped.assertClosed();
    }
  }

  @Test
  void replayRequiresExactlyOnePresentTrueBooleanAndNeverRepairsAnUnknownSavedRow() {
    for (List<Map<String, Object>> rows :
        List.<List<Map<String, Object>>>of(
            List.<Map<String, Object>>of(),
            List.of(Map.of(TEXT_MATCHES, false)),
            List.of(changed(Map.of(TEXT_MATCHES, true), TEXT_MATCHES, null)),
            List.of(Map.of(TEXT_MATCHES, true), Map.of(TEXT_MATCHES, true)))) {
      for (String mode : List.of(FINISH, REPLAY, "already", "unavailable")) {
        Fixture fixture = new Fixture();
        fixture.finishChanged = 0;
        fixture.replayRows = rows;
        catalog(
            () -> {
              if (mode.equals(FINISH)) fixture.repository().finish(attempt(false), END, result());
              else if (mode.equals(REPLAY))
                fixture.repository().verifyFinished(attempt(false), END, result());
              else if (mode.equals("already"))
                fixture.repository().verifyAlreadySuccessful(attempt(true));
              else fixture.repository().verifyBackupUnavailable(attempt(true));
            });
        assertFalse(fixture.bindings.containsKey(INSERT));
        fixture.assertClosed();
      }
    }
  }

  @Test
  void everyPublicNullAndInvalidTimeOrSkipContractRejectsBeforeAnyJdbcAcquisition() {
    assertThrows(NullPointerException.class, () -> new BatchRunRepository(null));
    Fixture fixture = new Fixture();
    var repository = fixture.repository();
    for (Executable nullInput :
        List.<Executable>of(
            () -> repository.begin(null, BatchStep.CLEAN_LOG, NOW, false),
            () -> repository.begin(RUN, null, NOW, false),
            () -> repository.begin(RUN, BatchStep.CLEAN_LOG, null, false),
            () -> repository.beginBackupUnavailable(RUN, null, NOW, false),
            () -> repository.finish(null, END, result()),
            () -> repository.finish(attempt(false), null, result()),
            () -> repository.finish(attempt(false), END, null),
            () -> repository.verifyFinished(null, END, result()),
            () -> repository.verifyFinished(attempt(false), null, result()),
            () -> repository.verifyFinished(attempt(false), END, null),
            () -> repository.verifyAlreadySuccessful(null),
            () -> repository.verifyBackupUnavailable(null)))
      assertThrows(NullPointerException.class, nullInput);
    for (BatchStep invalid :
        List.of(
            BatchStep.BACKUP_DB,
            BatchStep.BACKUP_CONFIG,
            BatchStep.CLEAN_TRANSFER,
            BatchStep.CLEAN_EXPIRY))
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.beginBackupUnavailable(RUN, invalid, NOW, false));
    for (Instant invalid : List.of(BASE.minusSeconds(1), NOW.plusNanos(1)))
      assertThrows(
          IllegalArgumentException.class,
          () -> repository.begin(RUN, BatchStep.CLEAN_LOG, invalid, false));
    for (Executable invalid :
        List.<Executable>of(
            () -> repository.finish(attempt(true), END, result()),
            () -> repository.finish(attempt(false), BASE, result()),
            () -> repository.verifyFinished(attempt(true), END, result()),
            () -> repository.verifyFinished(attempt(false), BASE, result()),
            () -> repository.verifyAlreadySuccessful(attempt(false)),
            () -> repository.verifyBackupUnavailable(attempt(false))))
      assertThrows(IllegalArgumentException.class, invalid);
    assertTrue(fixture.routes.isEmpty());
  }

  @Test
  void everyHistoryInsertAbandonFinishReplayPortFailurePreservesItsDeclaredFailureIdentity() {
    for (String route : List.of(HISTORY, INSERT, ABANDON, FINISH, REPLAY)) {
      var points = new ArrayList<>(List.of("prepare", "timeout", "bind1", "statementClose"));
      if (route.equals(ABANDON) || route.equals(FINISH)) points.add("update");
      else {
        points.addAll(List.of("query", TEXT_NEXT, "rowClose"));
        points.add(route.equals(REPLAY) ? TEXT_MATCHES : "id");
      }
      for (String point : points) {
        for (Throwable failure : failures()) {
          Fixture fixture = new Fixture();
          fixture.faults.put(route + ":" + point, failure);
          Executable action = () -> action(fixture, route);
          if (failure instanceof SQLException) catalog(action);
          else assertSame(failure, assertThrows(failure.getClass(), action));
          fixture.assertClosed();
        }
      }
    }
  }

  @Test
  void allOwnedScopesUseExplicitBodyVersusClosePrecedenceWithSafeSecondaryDiagnostics() {
    for (String route : List.of(HISTORY, INSERT, ABANDON, FINISH, REPLAY)) {
      for (Throwable body : failures()) {
        for (Throwable closing : failures()) {
          Fixture fixture = new Fixture();
          boolean update = route.equals(ABANDON) || route.equals(FINISH);
          fixture.faults.put(route + ":" + (update ? "update" : TEXT_NEXT), body);
          fixture.faults.put(route + ":" + (update ? "statementClose" : "rowClose"), closing);
          if (!update)
            fixture.faults.put(route + ":statementClose", new SQLException("private extra close"));
          Throwable expected = body instanceof SQLException ? closing : body;
          Executable action = () -> action(fixture, route);
          if (expected instanceof SQLException) catalog(action);
          else {
            var actual = assertThrows(expected.getClass(), action);
            assertSame(expected, actual);
            for (Throwable suppressed : actual.getSuppressed()) {
              assertEquals(BatchRepositoryException.class, suppressed.getClass());
              assertEquals(FIXED, suppressed.getMessage());
            }
          }
          fixture.assertClosed();
        }
      }
    }
  }

  @Test
  void nullAcquisitionsAndLostParentIdentityNeverAuthorizeSuccessOrFallback() {
    for (String route : List.of(HISTORY, INSERT, ABANDON, FINISH, REPLAY)) {
      for (String missing : List.of("statement", "row")) {
        if (missing.equals("row") && (route.equals(ABANDON) || route.equals(FINISH))) continue;
        Fixture fixture = new Fixture();
        fixture.missing = route + ":" + missing;
        catalog(() -> action(fixture, route));
        fixture.assertClosed();
      }
      for (int bad : new int[] {1, 2}) {
        Fixture fixture = new Fixture();
        fixture.badReference = bad;
        catalog(() -> action(fixture, route));
        assertEquals(bad, fixture.referenceCalls);
        fixture.assertClosed();
      }
    }
  }

  @Test
  void invalidAffectedCountsAndFailedReplayCannotInsertOrUpdateAnExtraAttempt() {
    for (int count : new int[] {-1, 2}) {
      Fixture fixture = new Fixture();
      fixture.finishChanged = count;
      catalog(() -> fixture.repository().finish(attempt(false), END, result()));
      assertFalse(fixture.bindings.containsKey(REPLAY));
      fixture.assertClosed();
    }
    for (int count : new int[] {0, 2}) {
      Fixture fixture = new Fixture();
      fixture.abandonChanged = count;
      catalog(() -> action(fixture, ABANDON));
      assertFalse(fixture.bindings.containsKey(INSERT));
      fixture.assertClosed();
    }
  }

  @Test
  void internalHistoryRenderingUsesFixedRedactionWithoutExposingItsInputIdentityOrTime()
      throws Exception {
    var type = Class.forName("dev.codex.schubert.nk.batch.repository.BatchRunRepository$History");
    var constructor =
        type.getDeclaredConstructor(long.class, UUID.class, int.class, Instant.class, String.class);
    constructor.setAccessible(true);
    Object history = constructor.newInstance(123L, FOREIGN, 2, BASE, TEXT_SUCCESS);
    assertEquals("BatchStepHistory[identity/time=<redacted>]", history.toString());
    assertFalse(history.toString().contains(FOREIGN.toString()));
    assertFalse(history.toString().contains(BASE.toString()));
  }

  private static void action(Fixture fixture, String route) {
    if (route.equals(ABANDON)) {
      fixture.history = List.of(historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, TEXT_RUNNING));
      fixture.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, true);
    } else if (route.equals(FINISH)) fixture.repository().finish(attempt(false), END, result());
    else if (route.equals(REPLAY))
      fixture.repository().verifyFinished(attempt(false), END, result());
    else fixture.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false);
  }

  private static BatchStepAttempt attempt(boolean skipped) {
    return new BatchStepAttempt(7, RUN, BatchStep.CLEAN_LOG, 1, NOW, skipped);
  }

  private static BatchStepResult result() {
    return new BatchStepResult(
        BatchStepResult.Status.SUCCESS, 1, 1, 0, 3, BatchStepResult.Reason.NONE);
  }

  private static Map<Integer, Object> insertBindings(
      BatchStep step, int number, boolean skipped, String code, String summary) {
    var map = new HashMap<Integer, Object>();
    map.put(1, ID);
    map.put(2, DAY);
    map.put(3, step.name());
    map.put(4, number);
    map.put(5, NOW.atOffset(ZoneOffset.UTC));
    map.put(6, skipped ? NOW.atOffset(ZoneOffset.UTC) : null);
    map.put(7, skipped ? "SKIPPED" : TEXT_RUNNING);
    map.put(8, code);
    map.put(9, summary);
    return map;
  }

  private static Map<Integer, Object> finishBindings(
      String status,
      long target,
      long success,
      long failure,
      long bytes,
      String code,
      String summary,
      Instant ended) {
    var map = new HashMap<Integer, Object>();
    map.put(1, ended.atOffset(ZoneOffset.UTC));
    map.put(2, status);
    map.put(3, target);
    map.put(4, success);
    map.put(5, failure);
    map.put(6, bytes);
    map.put(7, code);
    map.put(8, summary);
    map.put(9, 7L);
    map.put(10, ID);
    map.put(11, DAY);
    map.put(12, "CLEAN_LOG");
    map.put(13, 1);
    map.put(14, NOW.atOffset(ZoneOffset.UTC));
    return map;
  }

  private static Map<String, Object> historicalRow() {
    return historicalRow(1, 1, ID, BatchStep.CLEAN_LOG, TEXT_SUCCESS);
  }

  private static Map<String, Object> historicalRow(
      long id, int number, UUID run, BatchStep step, String status) {
    var map = new HashMap<String, Object>();
    map.put("id", id);
    map.put("run_id", run);
    map.put("business_date", DAY);
    map.put("step", step.name());
    map.put(TEXT_ATTEMPT, number);
    map.put(TEXT_STARTED_AT, BASE.plusSeconds(1).atOffset(ZoneOffset.UTC));
    map.put(
        TEXT_ENDED_AT,
        status.equals(TEXT_RUNNING) ? null : BASE.plusSeconds(2).atOffset(ZoneOffset.UTC));
    map.put("status", status);
    map.put("target_count", 0L);
    map.put("success_count", 0L);
    map.put("failure_count", 0L);
    map.put("byte_count", 0L);
    return map;
  }

  private static Map<String, Object> changed(Map<String, Object> row, String key, Object value) {
    var map = new HashMap<>(row);
    map.put(key, value);
    return map;
  }

  private static void rejectHistory(List<Map<String, Object>> rows) {
    Fixture fixture = new Fixture();
    fixture.history = rows;
    catalog(() -> fixture.repository().begin(RUN, BatchStep.CLEAN_LOG, NOW, false));
    assertFalse(fixture.bindings.containsKey(INSERT));
    assertFalse(fixture.bindings.containsKey(ABANDON));
    fixture.assertClosed();
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("private JDBC"),
        new IllegalStateException("private provider"),
        new AssertionError("private fatal"));
  }

  private static void catalog(Executable action) {
    var failure = assertThrows(BatchRepositoryException.class, action);
    assertEquals(FIXED, failure.getMessage());
    assertEquals(null, failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Fixture {
    private final List<String> routes = new ArrayList<>();
    private final Map<String, List<Map<Integer, Object>>> bindings = new HashMap<>();
    private final Map<String, Throwable> faults = new HashMap<>();
    private List<Map<String, Object>> history = List.of();
    private List<Map<String, Object>> insertRows = List.of(Map.of("id", 7L));
    private List<Map<String, Object>> replayRows = List.of(Map.of(TEXT_MATCHES, true));
    private String missing = "";
    private int finishChanged = 1;
    private int abandonChanged = 1;
    private int referenceCalls;
    private int badReference;
    private int openedStatements;
    private int closedStatements;
    private int openedRows;
    private int closedRows;

    private BatchRunRepository repository() {
      return new BatchRunRepository(connection());
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getAutoCommit", "isReadOnly" -> false;
                    case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                    case "prepareStatement" -> statement((String) args[0]);
                    default ->
                        throw new AssertionError(
                            "borrowed connection operation forbidden: " + method.getName());
                  });
    }

    private PreparedStatement statement(String sql) throws Throwable {
      String route =
          Map.of(
                  SQL_REFS,
                  REFS,
                  SQL_HISTORY,
                  HISTORY,
                  SQL_INSERT,
                  INSERT,
                  SQL_ABANDON,
                  ABANDON,
                  SQL_FINISH,
                  FINISH,
                  SQL_REPLAY,
                  REPLAY)
              .get(sql);
      assertTrue(route != null, sql);
      routes.add(route);
      hit(route, "prepare");
      if (missing.equals(route + ":statement")) return null;
      openedStatements++;
      var values = new HashMap<Integer, Object>();
      bindings.computeIfAbsent(route, key -> new ArrayList<>()).add(values);
      return (PreparedStatement)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("setQueryTimeout")) {
                  hit(route, "timeout");
                  assertEquals(5, args[0]);
                  return null;
                }
                if (List.of(TEXT_SETOBJECT, TEXT_SETSTRING, "setLong", "setInt").contains(name)) {
                  int position = (Integer) args[0];
                  hit(route, "bind" + position);
                  assertEquals(setter(route, position), name);
                  values.put(position, args[1]);
                  return null;
                }
                if (name.equals("executeUpdate")) {
                  hit(route, "update");
                  assertTrue(route.equals(ABANDON) || route.equals(FINISH));
                  return route.equals(ABANDON) ? abandonChanged : finishChanged;
                }
                if (name.equals("executeQuery")) {
                  hit(route, "query");
                  if (missing.equals(route + ":row")) return null;
                  if (route.equals(REFS)) {
                    referenceCalls++;
                    return rows(
                        route,
                        List.of(
                            Map.of(
                                "has_batch_history",
                                true,
                                "has_inbox_progress",
                                false,
                                "has_log_progress",
                                false,
                                "identity_consistent",
                                referenceCalls != badReference)));
                  }
                  return rows(
                      route,
                      switch (route) {
                        case HISTORY -> history;
                        case INSERT -> insertRows;
                        case REPLAY -> replayRows;
                        default -> throw new AssertionError("update route cannot query");
                      });
                }
                if (name.equals("close")) {
                  closedStatements++;
                  hit(route, "statementClose");
                  return null;
                }
                throw new AssertionError("unexpected statement operation: " + name);
              });
    }

    private ResultSet rows(String route, List<Map<String, Object>> inputs) {
      openedRows++;
      int[] index = {-1};
      return (ResultSet)
          Proxy.newProxyInstance(
              Fixture.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals(TEXT_NEXT)) {
                  hit(route, TEXT_NEXT);
                  index[0]++;
                  return index[0] < inputs.size();
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  String column = (String) args[0];
                  hit(route, column);
                  assertTrue(inputs.get(index[0]).containsKey(column));
                  return inputs.get(index[0]).get(column);
                }
                if (name.equals("close")) {
                  closedRows++;
                  hit(route, "rowClose");
                  return null;
                }
                throw new AssertionError("unexpected row operation: " + name);
              });
    }

    private static String setter(String route, int position) {
      if (route.equals(REFS)) return TEXT_SETOBJECT;
      if (route.equals(HISTORY)) return position == 1 ? TEXT_SETOBJECT : TEXT_SETSTRING;
      if (route.equals(INSERT))
        return switch (position) {
          case 1, 2, 5, 6 -> TEXT_SETOBJECT;
          case 3, 7, 8, 9 -> TEXT_SETSTRING;
          case 4 -> "setInt";
          default -> throw new AssertionError("unknown insert index");
        };
      if (route.equals(ABANDON))
        return switch (position) {
          case 1, 5, 6 -> TEXT_SETOBJECT;
          case 2, 3 -> TEXT_SETSTRING;
          case 4 -> "setLong";
          default -> throw new AssertionError("unknown abandon index");
        };
      return switch (position) {
        case 1, 10, 11, 14 -> TEXT_SETOBJECT;
        case 2, 7, 8, 12 -> TEXT_SETSTRING;
        case 3, 4, 5, 6, 9 -> "setLong";
        case 13 -> "setInt";
        default -> throw new AssertionError("unknown terminal index");
      };
    }

    private void hit(String route, String point) throws Throwable {
      Throwable failure = faults.get(route + ":" + point);
      if (failure != null) throw failure;
    }

    private void assertClosed() {
      assertEquals(openedStatements, closedStatements, "every owned statement closed exactly once");
      assertEquals(openedRows, closedRows, "every owned row closed exactly once");
    }
  }
}
