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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-MIG-AUDIOLINKREAD001..020; independent fixed SQL, typed-column calls and in-memory faults. */
final class CurrentAudioLinkProjectionReaderTest {
  private static final String SQL =
      "SELECT entry_id,audio_file_id,link_type FROM scenario.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"";
  private static final String DIAGNOSTIC = "migration audio link projection is invalid";
  private static final String INPUT_DIAGNOSTIC = "migration audio link projection input is invalid";
  private static final String CALL_AUTO = "getAutoCommit";
  private static final String CALL_READONLY = "isReadOnly";
  private static final String CALL_CREATE = "createStatement";
  private static final String CALL_TIMEOUT = "setQueryTimeout";
  private static final String CALL_FETCH = "setFetchSize";
  private static final String CALL_QUERY = "executeQuery";
  private static final String CALL_NEXT = "next";
  private static final String CALL_LONG = "getLong:1";
  private static final String CALL_AUDIO_ID = "getLong:2";
  private static final String CALL_KIND = "getString:3";
  private static final String CALL_NULL = "wasNull";
  private static final String CALL_RESULT_CLOSE = "result.close";
  private static final String CALL_STATEMENT_CLOSE = "statement.close";
  private static final String CURRENT_ENTRY = "-20";
  private static final String KIND = "voice";
  private static final String OTHER_KIND = "se";
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void audioLinkRead001SignedIdsAndThreeColumns() throws Exception {
    var f = normal();
    f.data.get(0)[0] = Long.MIN_VALUE;
    f.data.get(0)[1] = Long.MAX_VALUE;
    assertEquals(
        List.of(
            List.of("-9223372036854775808", "9223372036854775807", KIND),
            List.of("10", "-30", OTHER_KIND)),
        new CurrentAudioLinkProjectionReader().read(f.connection(), 2));
    assertEquals(1, f.resultCloses);
    assertEquals(1, f.statementCloses);
  }

  @Test
  void audioLinkRead002EmptySnapshotStillExecutesOneBoundedQuery() throws Exception {
    var f = new Fixture();
    assertEquals(List.of(), new CurrentAudioLinkProjectionReader().read(f.connection(), 0));
    assertEquals(List.of(SQL), f.sql);
    assertEquals(1, f.resultCloses);
    assertEquals(1, f.statementCloses);
  }

  @Test
  void audioLinkRead003NullAndNegativeInputFailBeforeAnyConnectionRead() {
    var reader = new CurrentAudioLinkProjectionReader();
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> reader.read(null, 0)).getMessage());
    var f = normal();
    assertEquals(
        INPUT_DIAGNOSTIC,
        assertThrows(IllegalArgumentException.class, () -> reader.read(f.connection(), -1))
            .getMessage());
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void audioLinkRead004CallerMustAlreadyOwnReadonlyNonautoSnapshot() {
    var auto = normal();
    auto.auto = true;
    reject(auto, 2);
    assertEquals(List.of(CALL_AUTO), auto.calls);
    var writable = normal();
    writable.readOnly = false;
    reject(writable, 2);
    assertEquals(List.of(CALL_AUTO, CALL_READONLY), writable.calls);
  }

  @Test
  void audioLinkRead005NullVendorStatementCreatesNoOwnedHandle() {
    var f = normal();
    f.nullStatement = true;
    reject(f, 2);
    assertEquals(List.of(CALL_AUTO, CALL_READONLY, CALL_CREATE), f.calls);
    assertEquals(0, f.statementCloses);
    assertEquals(0, f.resultCloses);
  }

  @Test
  void audioLinkRead006NullVendorResultClosesOnlyTheStatement() {
    var f = normal();
    f.nullResult = true;
    reject(f, 2);
    assertEquals(1, f.statementCloses);
    assertEquals(0, f.resultCloses);
    assertEquals(CALL_STATEMENT_CLOSE, f.calls.get(f.calls.size() - 1));
  }

  @Test
  void audioLinkRead007ExactCardinalityAndExtraRowsNotRead() {
    var few = normal();
    reject(few, 3);
    assertEquals(2, few.calls.stream().filter(CALL_LONG::equals).count());
    var extra = normal();
    reject(extra, 1);
    assertEquals(1, extra.calls.stream().filter(CALL_LONG::equals).count());
    var zero = normal();
    reject(zero, 0);
    assertEquals(0, zero.calls.stream().filter(CALL_LONG::equals).count());
    for (var f : List.of(few, extra, zero)) {
      assertEquals(1, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void audioLinkRead008BothRequiredLongSqlNullsAreRejected() {
    for (int column : List.of(0, 1)) {
      var f = normal();
      f.data.get(0)[column] = null;
      reject(f, 2);
      assertEquals(1, f.resultCloses);
      assertEquals(1, f.statementCloses);
      assertEquals(0, f.calls.stream().filter(CALL_KIND::equals).count());
    }
  }

  @Test
  void audioLinkRead009ZeroNegativeAndBothLongExtremesAreRetained() throws Exception {
    for (long value : new long[] {Long.MIN_VALUE, -1, 0, 1, Long.MAX_VALUE}) {
      var f = normal();
      f.data.get(0)[0] = value;
      f.data.get(0)[1] = value;
      var row = new CurrentAudioLinkProjectionReader().read(f.connection(), 2).get(0);
      assertEquals(Long.toString(value), row.get(0));
      assertEquals(Long.toString(value), row.get(1));
    }
  }

  @Test
  void audioLinkRead010RequiredKindSqlNullFailsWithoutPartialOutput() {
    var f = normal();
    f.data.get(1)[2] = null;
    reject(f, 2);
    assertEquals(1, f.resultCloses);
    assertEquals(1, f.statementCloses);
  }

  @Test
  void audioLinkRead011StoredKindNotRecomputedValidatedOrNormalized() throws Exception {
    for (String value :
        List.of("", "unknown", "voice", "se", "bgm", "other", "e\u0301", "  音声\t\n\0 ")) {
      var f = normal();
      f.data.get(0)[2] = value;
      assertEquals(
          value, new CurrentAudioLinkProjectionReader().read(f.connection(), 2).get(0).get(2));
    }
  }

  @Test
  void audioLinkRead012DeepImmutableSnapshotIsIndependentOfLaterFixtureChange() throws Exception {
    var f = normal();
    var rows = new CurrentAudioLinkProjectionReader().read(f.connection(), 2);
    f.data.get(0)[2] = "changed";
    f.data.clear();
    assertEquals(KIND, rows.get(0).get(2));
    assertThrows(UnsupportedOperationException.class, rows::clear);
    assertThrows(UnsupportedOperationException.class, () -> rows.get(0).set(0, "changed"));
  }

  @Test
  void audioLinkRead013IndependentSqlTypedCallsWasNullTimeoutAndCloseOrder() throws Exception {
    var f = normal();
    f.data.remove(1);
    new CurrentAudioLinkProjectionReader().read(f.connection(), 1);
    assertEquals(List.of(SQL), f.sql);
    assertEquals(List.of(30), f.timeouts);
    assertEquals(List.of(1000), f.fetchSizes);
    assertEquals(
        List.of(
            CALL_AUTO,
            CALL_READONLY,
            CALL_CREATE,
            CALL_TIMEOUT,
            CALL_FETCH,
            CALL_QUERY,
            CALL_NEXT,
            CALL_LONG,
            CALL_NULL,
            CALL_AUDIO_ID,
            CALL_NULL,
            CALL_KIND,
            CALL_NEXT,
            CALL_RESULT_CLOSE,
            CALL_STATEMENT_CLOSE),
        f.calls);
  }

  @Test
  void audioLinkRead014EveryJdbcPhasePropagatesSqlRuntimeAndErrorAndClosesOwnedHandles() {
    var phases =
        List.of(
            CALL_AUTO,
            CALL_READONLY,
            CALL_CREATE,
            CALL_TIMEOUT,
            CALL_FETCH,
            CALL_QUERY,
            CALL_NEXT,
            CALL_LONG,
            CALL_NULL,
            CALL_AUDIO_ID,
            CALL_KIND);
    for (int phase = 0; phase < phases.size(); phase++) {
      int occurrences =
          phase < 6
              ? 1
              : phases.get(phase).equals(CALL_NULL)
                  ? 4
                  : phases.get(phase).equals(CALL_NEXT) ? 3 : 2;
      for (int occurrence = 1; occurrence <= occurrences; occurrence++) {
        for (Throwable expected : failures()) {
          var f = normal();
          f.failurePhase = phases.get(phase);
          f.failureOccurrence = occurrence;
          f.failure = expected;
          assertSame(
              expected,
              assertThrows(
                  expected.getClass(),
                  () -> new CurrentAudioLinkProjectionReader().read(f.connection(), 2)));
          assertEquals(phase >= 3 ? 1 : 0, f.statementCloses);
          assertEquals(phase >= 6 ? 1 : 0, f.resultCloses);
          assertEquals(occurrence, f.failurePhaseHits);
          assertEquals(0, expected.getSuppressed().length);
        }
      }
    }
  }

  @Test
  void audioLinkRead015CleanPathResultOrStatementCloseFailureIsNotSuccess() {
    for (boolean result : List.of(true, false)) {
      for (Throwable expected : failures()) {
        var f = normal();
        if (result) f.resultCloseFailure = expected;
        else f.statementCloseFailure = expected;
        assertSame(
            expected,
            assertThrows(
                expected.getClass(),
                () -> new CurrentAudioLinkProjectionReader().read(f.connection(), 2)));
        assertEquals(1, f.resultCloses);
        assertEquals(1, f.statementCloses);
        assertEquals(0, expected.getSuppressed().length);
      }
    }
  }

  @Test
  void audioLinkRead016PrimaryThenResultThenStatementSuppressionAllFaultKinds() {
    for (int p = 0; p < 3; p++) {
      for (int rc = 0; rc < 3; rc++) {
        for (int sc = 0; sc < 3; sc++) {
          var f = normal();
          Throwable expected = failures().get(p);
          Throwable resultClose = failures().get(rc);
          Throwable statementClose = failures().get(sc);
          f.failurePhase = CALL_LONG;
          f.failure = expected;
          f.resultCloseFailure = resultClose;
          f.statementCloseFailure = statementClose;
          assertSame(
              expected,
              assertThrows(
                  expected.getClass(),
                  () -> new CurrentAudioLinkProjectionReader().read(f.connection(), 2)));
          assertEquals(
              List.of(resultClose, statementClose), Arrays.asList(expected.getSuppressed()));
          assertEquals(1, f.resultCloses);
          assertEquals(1, f.statementCloses);
        }
      }
    }
  }

  @Test
  void audioLinkRead017SameThrowableAtCleanupPreservesPrimaryWithoutSelfSuppression() {
    for (Throwable expected : failures()) {
      var f = normal();
      f.failurePhase = CALL_LONG;
      f.failure = expected;
      f.resultCloseFailure = expected;
      f.statementCloseFailure = expected;
      assertSame(
          expected,
          assertThrows(
              expected.getClass(),
              () -> new CurrentAudioLinkProjectionReader().read(f.connection(), 2)));
      assertEquals(0, expected.getSuppressed().length);
      assertEquals(1, f.resultCloses);
      assertEquals(1, f.statementCloses);
    }
  }

  @Test
  void audioLinkRead018ExtractionDoesNotRepairDuplicatesOrGivenResultOrder() throws Exception {
    var f = normal();
    f.data.add(new Object[] {-20L, 700L, KIND});
    assertEquals(
        List.of(
            List.of(CURRENT_ENTRY, "700", KIND),
            List.of("10", "-30", OTHER_KIND),
            List.of(CURRENT_ENTRY, "700", KIND)),
        new CurrentAudioLinkProjectionReader().read(f.connection(), 3));
    var reversed = normal();
    java.util.Collections.reverse(reversed.data);
    assertEquals(
        List.of(List.of("10", "-30", OTHER_KIND), List.of(CURRENT_ENTRY, "700", KIND)),
        new CurrentAudioLinkProjectionReader().read(reversed.connection(), 2));
  }

  @Test
  void audioLinkRead019FailureDoesNotPoisonLaterReadAndRedactionIsFixed() throws Exception {
    var reader = new CurrentAudioLinkProjectionReader();
    var bad = normal();
    bad.nullResult = true;
    assertThrows(SQLException.class, () -> reader.read(bad.connection(), 2));
    var good = normal();
    assertEquals(CURRENT_ENTRY, reader.read(good.connection(), 2).get(0).get(0));
    assertEquals("CurrentAudioLinkProjectionReader[REDACTED]", reader.toString());
    Throwable diagnostic =
        assertThrows(SQLException.class, () -> reader.read(normal().connection(), 0));
    assertEquals(DIAGNOSTIC, diagnostic.getMessage());
    assertNull(diagnostic.getCause());
    assertEquals(0, diagnostic.getSuppressed().length);
  }

  @Test
  void audioLinkRead020SharedStatelessReaderUsesOnlyPerCallOwnedResources() throws Exception {
    var reader = new CurrentAudioLinkProjectionReader();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int index = 0; index < TASKS; index++) {
        futures.add(
            executor.submit(
                () -> {
                  var f = normal();
                  var rows = reader.read(f.connection(), 2);
                  assertEquals(1, f.resultCloses);
                  assertEquals(1, f.statementCloses);
                  return rows.get(0).get(0);
                }));
      }
      for (var future : futures)
        assertEquals(CURRENT_ENTRY, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static Fixture normal() {
    var f = new Fixture();
    f.data.add(new Object[] {-20L, 700L, KIND});
    f.data.add(new Object[] {10L, -30L, OTHER_KIND});
    return f;
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static void reject(Fixture f, int expected) {
    assertEquals(
        DIAGNOSTIC,
        assertThrows(
                SQLException.class,
                () -> new CurrentAudioLinkProjectionReader().read(f.connection(), expected))
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
                if (List.of("getLong", "getString").contains(name)) {
                  int column = (Integer) args[0];
                  call(name + ":" + column);
                  Object value = data.get(position)[column - 1];
                  lastNull = value == null;
                  return switch (name) {
                    case "getLong" -> value == null ? 0L : (Long) value;
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
