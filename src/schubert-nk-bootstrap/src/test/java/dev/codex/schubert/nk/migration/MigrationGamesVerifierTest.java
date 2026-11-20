package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-GAMES001..020; V004 literal rows and independent fixed SQL/typed/cleanup protocol. */
final class MigrationGamesVerifierTest {
  private static final String SQL =
      "SELECT id,code,title,display_order,created_at FROM schubert.games ORDER BY id";
  private static final String STAMP = "2026-09-01T00:00:00Z";
  private static final String DIAGNOSTIC = "migration games initial rows are invalid";
  private static final String INPUT_DIAGNOSTIC = "migration games input is invalid";
  private static final String CALL_AUTO = "getAutoCommit";
  private static final String CALL_READONLY = "isReadOnly";
  private static final String CALL_CREATE = "createStatement";
  private static final String CALL_TIMEOUT = "setQueryTimeout";
  private static final String CALL_FETCH = "setFetchSize";
  private static final String CALL_QUERY = "executeQuery";
  private static final String CALL_NEXT = "next";
  private static final String CALL_ID = "getInt:1";
  private static final String CALL_CODE = "getString:2";
  private static final String CALL_TITLE = "getString:3";
  private static final String CALL_ORDER = "getInt:4";
  private static final String GET_OFFSET_DATE_TIME = "getObject";
  private static final String CALL_STAMP = GET_OFFSET_DATE_TIME + ":5";
  private static final String CALL_NULL = "wasNull";
  private static final String CALL_RESULT_CLOSE = "result.close";
  private static final String CALL_STATEMENT_CLOSE = "statement.close";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void games001FixedV004TwoRowsSqlAndExactTypedProtocol() throws Exception {
    var f = normal();
    new MigrationGamesVerifier().verify(f.connection());
    assertEquals(List.of(SQL), f.sql);
    assertEquals(List.of(30), f.timeouts);
    assertEquals(List.of(1000), f.fetchSizes);
    assertEquals(
        List.of(
            CALL_AUTO,
            CALL_CREATE,
            CALL_TIMEOUT,
            CALL_FETCH,
            CALL_QUERY,
            CALL_NEXT,
            CALL_ID,
            CALL_NULL,
            CALL_CODE,
            CALL_TITLE,
            CALL_ORDER,
            CALL_NULL,
            CALL_STAMP,
            CALL_NEXT,
            CALL_ID,
            CALL_NULL,
            CALL_CODE,
            CALL_TITLE,
            CALL_ORDER,
            CALL_NULL,
            CALL_STAMP,
            CALL_NEXT,
            CALL_RESULT_CLOSE,
            CALL_STATEMENT_CLOSE),
        f.calls);
    assertEquals(1, f.resultCloses);
    assertEquals(1, f.statementCloses);
  }

  @Test
  void games002NullInputFailsBeforeAnyBorrowedRead() {
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(
                IllegalArgumentException.class, () -> new MigrationGamesVerifier().verify(null))
            .getMessage());
  }

  @Test
  void games003AutoAndNullVendorHandlesHaveOwnedPostconditions() {
    var a = normal();
    a.auto = true;
    reject(a);
    assertEquals(List.of(CALL_AUTO), a.calls);
    var s = normal();
    s.nullStatement = true;
    reject(s);
    assertEquals(0, s.statementCloses);
    var r = normal();
    r.nullResult = true;
    reject(r);
    assertEquals(1, r.statementCloses);
    assertEquals(0, r.resultCloses);
  }

  @Test
  void games004MissingAndExtraRowsRejectWithoutReadingExtraFields() {
    for (int count : new int[] {0, 1}) {
      var f = normal();
      while (f.data.size() > count) f.data.remove(f.data.size() - 1);
      reject(f);
      assertEquals(count, f.calls.stream().filter(CALL_ID::equals).count());
    }
    var extra = normal();
    extra.data.add(extra.data.get(0).clone());
    reject(extra);
    assertEquals(2, extra.calls.stream().filter(CALL_ID::equals).count());
    assertEquals(1, extra.resultCloses);
    assertEquals(1, extra.statementCloses);
  }

  @Test
  void games005AllTenSqlNullPositionsReject() {
    for (int row = 0; row < 2; row++)
      for (int column = 0; column < 5; column++) {
        var f = normal();
        f.data.get(row)[column] = null;
        reject(f);
        assertEquals(1, f.resultCloses);
        assertEquals(1, f.statementCloses);
      }
  }

  @Test
  void games006IdsAndOrdersMatchCanonicalFixedValuesAndOrder() {
    for (int column : List.of(0, 3))
      for (int value : new int[] {Integer.MIN_VALUE, -1, 0, 3, Integer.MAX_VALUE}) {
        var f = normal();
        f.data.get(0)[column] = value;
        reject(f);
      }
    var swap = normal();
    Collections.reverse(swap.data);
    reject(swap);
  }

  @Test
  void games007StoredCodeTitleMustMatchWithoutRepair() {
    for (int column : List.of(1, 2))
      for (String value :
          List.of(
              "", "unknown", "nukitashi1", " NUKITASHI1", "NUKITASHI１", "e\u0301", "NUKITASHI\0")) {
        var f = normal();
        f.data.get(0)[column] = value;
        reject(f);
      }
  }

  @Test
  void games008CreatedAtIsTheExactV004Instant() throws SQLException {
    var equivalent = normal();
    equivalent.data.get(0)[4] = OffsetDateTime.parse("2026-09-01T09:00:00+09:00");
    equivalent.data.get(1)[4] = OffsetDateTime.parse("2026-08-31T17:00:00-07:00");
    new MigrationGamesVerifier().verify(equivalent.connection());
    assertEquals(2, equivalent.calls.stream().filter(CALL_STAMP::equals).count());
    for (String stamp :
        List.of(
            "2026-08-31T23:59:59Z",
            "2026-09-01T00:00:01Z",
            "2026-09-01T00:00:00.000000001Z",
            "0001-01-01T00:00:00Z")) {
      var f = normal();
      f.data.get(0)[4] = OffsetDateTime.parse(stamp);
      reject(f);
    }
  }

  @Test
  void games009EveryPhaseAndGetterOccurrenceKeepsOriginalFault() {
    var phases =
        List.of(
            CALL_AUTO,
            CALL_CREATE,
            CALL_TIMEOUT,
            CALL_FETCH,
            CALL_QUERY,
            CALL_NEXT,
            CALL_ID,
            CALL_NULL,
            CALL_CODE,
            CALL_TITLE,
            CALL_ORDER,
            CALL_STAMP);
    for (int phase = 0; phase < phases.size(); phase++) {
      int occurrences =
          phase < 5
              ? 1
              : phases.get(phase).equals(CALL_NULL)
                  ? 4
                  : phases.get(phase).equals(CALL_NEXT) ? 3 : 2;
      for (int occurrence = 1; occurrence <= occurrences; occurrence++)
        for (Throwable expected : failures()) {
          var f = normal();
          f.failurePhase = phases.get(phase);
          f.failureOccurrence = occurrence;
          f.failure = expected;
          assertSame(
              expected,
              assertThrows(
                  expected.getClass(), () -> new MigrationGamesVerifier().verify(f.connection())));
          assertEquals(phase >= 2 ? 1 : 0, f.statementCloses);
          assertEquals(phase >= 5 ? 1 : 0, f.resultCloses);
          assertEquals(occurrence, f.failurePhaseHits);
          assertEquals(0, expected.getSuppressed().length);
        }
    }
  }

  @Test
  void games010CleanCloseFailuresAreNotSuccess() {
    for (boolean result : List.of(true, false))
      for (Throwable expected : failures()) {
        var f = normal();
        if (result) f.resultCloseFailure = expected;
        else f.statementCloseFailure = expected;
        assertSame(
            expected,
            assertThrows(
                expected.getClass(), () -> new MigrationGamesVerifier().verify(f.connection())));
        assertEquals(1, f.resultCloses);
        assertEquals(1, f.statementCloses);
        assertEquals(0, expected.getSuppressed().length);
      }
  }

  @Test
  void games011AllPrimaryAndBothCleanupKindsKeepSuppressionOrder() {
    for (int p = 0; p < 3; p++)
      for (int rc = 0; rc < 3; rc++)
        for (int sc = 0; sc < 3; sc++) {
          var f = normal();
          Throwable primary = failures().get(p);
          Throwable result = failures().get(rc);
          Throwable statement = failures().get(sc);
          f.failurePhase = CALL_ID;
          f.failure = primary;
          f.resultCloseFailure = result;
          f.statementCloseFailure = statement;
          assertSame(
              primary,
              assertThrows(
                  primary.getClass(), () -> new MigrationGamesVerifier().verify(f.connection())));
          assertSame(result, primary.getSuppressed()[0]);
          assertSame(statement, primary.getSuppressed()[1]);
          assertEquals(1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
  }

  @Test
  void games012SelfIdentityNeverSelfSuppresses() {
    for (Throwable primary : failures()) {
      var f = normal();
      f.failurePhase = CALL_ID;
      f.failure = primary;
      f.resultCloseFailure = primary;
      f.statementCloseFailure = primary;
      assertSame(
          primary,
          assertThrows(
              primary.getClass(), () -> new MigrationGamesVerifier().verify(f.connection())));
      assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void games013NullResultAndTimeoutFailureCloseOnlyTheStatement() {
    var nullResult = normal();
    nullResult.nullResult = true;
    reject(nullResult);
    assertEquals(0, nullResult.resultCloses);
    assertEquals(1, nullResult.statementCloses);
    var timeout = normal();
    timeout.failurePhase = CALL_TIMEOUT;
    timeout.failure = new SQLException("synthetic timeout");
    assertThrows(
        SQLException.class, () -> new MigrationGamesVerifier().verify(timeout.connection()));
    assertEquals(0, timeout.resultCloses);
    assertEquals(1, timeout.statementCloses);
  }

  @Test
  void games014CallerWriteTransactionIsAllowedAndNeverMutated() throws Exception {
    var f = normal();
    f.readOnly = false;
    new MigrationGamesVerifier().verify(f.connection());
    assertEquals(0, f.calls.stream().filter(CALL_READONLY::equals).count());
    assertEquals(1, f.calls.stream().filter(CALL_AUTO::equals).count());
  }

  @Test
  void games015FailureDoesNotPoisonLaterInvocation() throws Exception {
    var reader = new MigrationGamesVerifier();
    var bad = normal();
    bad.data.get(0)[2] = "wrong";
    assertThrows(SQLException.class, () -> reader.verify(bad.connection()));
    var good = normal();
    reader.verify(good.connection());
    assertEquals(List.of(SQL), good.sql);
    assertEquals(1, good.resultCloses);
  }

  @Test
  void games016DiagnosticsAndDisplayNeverContainRowValues() {
    var f = normal();
    f.data.get(0)[2] = "private-looking synthetic marker";
    var error =
        assertThrows(SQLException.class, () -> new MigrationGamesVerifier().verify(f.connection()));
    assertEquals(DIAGNOSTIC, error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertEquals("MigrationGamesVerifier[REDACTED]", new MigrationGamesVerifier().toString());
  }

  @Test
  void games017IndependentLiteralTitlesAreNotRecomputedFromInput() {
    var f = normal();
    f.data.get(0)[2] = "NUKITASHI2";
    reject(f);
    var code = normal();
    code.data.get(1)[1] = "NUKITASHI1";
    reject(code);
  }

  @Test
  void games018VerificationDoesNotModifyTheFixture() throws Exception {
    var f = normal();
    var before = f.data.stream().map(row -> Arrays.asList(row.clone())).toList();
    new MigrationGamesVerifier().verify(f.connection());
    assertEquals(before, f.data.stream().map(Arrays::asList).toList());
    f.data.get(1)[3] = 1;
    reject(f);
    assertEquals(4, f.calls.stream().filter(CALL_ID::equals).count());
    assertEquals(1, f.position);
  }

  @Test
  void games019EqualValueThrowableInstancesRemainDistinctSuppressedObjects() {
    var f = normal();
    var primary = new EqualSql();
    var inner = new EqualSql();
    var outer = new EqualSql();
    assertTrue(primary.equals(inner));
    f.failurePhase = CALL_ID;
    f.failure = primary;
    f.resultCloseFailure = inner;
    f.statementCloseFailure = outer;
    assertSame(
        primary,
        assertThrows(
            SQLException.class, () -> new MigrationGamesVerifier().verify(f.connection())));
    assertSame(inner, primary.getSuppressed()[0]);
    assertSame(outer, primary.getSuppressed()[1]);
  }

  @Test
  void games020FiniteConcurrentCallsUseIndependentOwnedHandles() throws Exception {
    var reader = new MigrationGamesVerifier();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<Boolean>>();
      for (int i = 0; i < TASKS; i++)
        futures.add(
            executor.submit(
                () -> {
                  var f = normal();
                  reader.verify(f.connection());
                  assertEquals(1, f.resultCloses);
                  assertEquals(1, f.statementCloses);
                  return f.sql.equals(List.of(SQL));
                }));
      for (var future : futures) assertTrue(future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static Fixture normal() {
    var f = new Fixture();
    f.data.add(new Object[] {1, "NUKITASHI1", "NUKITASHI", 1, OffsetDateTime.parse(STAMP)});
    f.data.add(new Object[] {2, "NUKITASHI2", "NUKITASHI2", 2, OffsetDateTime.parse(STAMP)});
    return f;
  }

  private static final class EqualSql extends SQLException {
    private static final long serialVersionUID = 1L;

    @Override
    public boolean equals(@Nullable Object value) {
      return value instanceof EqualSql;
    }

    @Override
    public int hashCode() {
      return 1;
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static void reject(Fixture f) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(SQLException.class, () -> new MigrationGamesVerifier().verify(f.connection()))
            .getMessage());
  }

  private static final class Fixture {
    final List<Object[]> data = new ArrayList<>();
    final List<String> calls = new ArrayList<>();
    final List<String> sql = new ArrayList<>();
    final List<Integer> timeouts = new ArrayList<>();
    final List<Integer> fetchSizes = new ArrayList<>();
    boolean auto;
    boolean readOnly = true;
    boolean nullStatement;
    boolean nullResult;
    boolean lastNull;
    int position = -1;
    int resultCloses;
    int statementCloses;
    int failureOccurrence = 1;
    int failurePhaseHits;
    @Nullable String failurePhase;
    @Nullable Throwable failure;
    @Nullable Throwable resultCloseFailure;
    @Nullable Throwable statementCloseFailure;

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals(CALL_AUTO)) {
                  call(name);
                  return auto;
                }
                if (name.equals(CALL_READONLY)) {
                  call(name);
                  return readOnly;
                }
                if (name.equals(CALL_CREATE)) {
                  call(name);
                  return nullStatement ? null : statement();
                }
                throw new AssertionError("unexpected borrowed-connection operation " + name);
              });
    }

    Statement statement() {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  statementCloses++;
                  calls.add(CALL_STATEMENT_CLOSE);
                  if (statementCloseFailure != null) throw statementCloseFailure;
                  return null;
                }
                if (name.equals(CALL_TIMEOUT)) {
                  call(name);
                  timeouts.add((Integer) args[0]);
                  return null;
                }
                if (name.equals(CALL_FETCH)) {
                  call(name);
                  fetchSizes.add((Integer) args[0]);
                  return null;
                }
                if (name.equals(CALL_QUERY)) {
                  call(name);
                  sql.add((String) args[0]);
                  return nullResult ? null : result();
                }
                throw new AssertionError("unexpected statement operation " + name);
              });
    }

    ResultSet result() {
      position = -1;
      lastNull = false;
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  resultCloses++;
                  calls.add(CALL_RESULT_CLOSE);
                  if (resultCloseFailure != null) throw resultCloseFailure;
                  return null;
                }
                if (name.equals(CALL_NEXT)) {
                  call(name);
                  position++;
                  return position < data.size();
                }
                if (name.equals(CALL_NULL)) {
                  call(name);
                  return lastNull;
                }
                if (List.of("getInt", "getString", GET_OFFSET_DATE_TIME).contains(name)) {
                  if (name.equals(GET_OFFSET_DATE_TIME)) {
                    assertEquals(2, args.length);
                    assertSame(OffsetDateTime.class, args[1]);
                  }
                  int column = (Integer) args[0];
                  call(name + ":" + column);
                  Object value = data.get(position)[column - 1];
                  lastNull = value == null;
                  return switch (name) {
                    case "getInt" -> value == null ? 0 : (Integer) value;
                    default -> value;
                  };
                }
                throw new AssertionError("unexpected result operation " + name);
              });
    }

    void call(String phase) throws Throwable {
      calls.add(phase);
      if (phase.equals(failurePhase)) {
        failurePhaseHits++;
        if (failurePhaseHits == failureOccurrence && failure != null) throw failure;
      }
    }
  }
}
