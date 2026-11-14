package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.math.BigDecimal;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * PT-MIG-CURRENTSNAPSHOT001..012; independent five SQL/typed rows and transaction-attribute faults.
 */
final class CurrentMigrationProjectionTest {
  private static final List<String> SQL =
      List.of(
          "SELECT id,game_id,name,normalized_name,is_protagonist,notes FROM scenario.speakers ORDER BY id",
          "SELECT id,game_id,relative_path,file_name,section_code,chapter_title,sha256,byte_size FROM scenario.script_files ORDER BY id",
          "SELECT id,game_id,script_file_id,entry_index,line_number,entry_type,speaker_id,speaker_label,body,raw_block FROM scenario.script_entries ORDER BY id",
          "SELECT id,game_id,relative_path,file_name,basename_upper,audio_role,container,duration_seconds,byte_size,sha256 FROM scenario.audio_files ORDER BY id",
          "SELECT entry_id,audio_file_id,link_type FROM scenario.entry_audio_links ORDER BY entry_id,audio_file_id,link_type COLLATE \"C\"");
  private static final String NAME = " Namé ";
  private static final String NORMALIZED = "stored_norm";
  private static final String ROLE = "movie_audio";
  private static final String INPUT_ERROR = "migration source snapshot input is invalid";
  private static final String ATTRIBUTE_ERROR = "migration source snapshot attributes are invalid";
  private static final String AUTO = "auto";
  private static final String READONLY = "readonly";
  private static final String ISOLATION = "isolation";
  private static final String QUERY = "query";
  private static final String CREATE = "create";
  private static final String TIMEOUT = "timeout";
  private static final String FETCH = "fetch";
  private static final String NEXT = "next";
  private static final int TABLES = 5;
  private static final int WORKERS = 8;
  private static final int TASKS = 64;
  private static final int WAIT_SECONDS = 5;
  private static final int TERMINATION_SECONDS = 10;

  @Test
  void snapshot001AllFiveFixedQueriesTypedValuesAndCloseOrder() throws Exception {
    var f = normal();
    var value = read(f, ones());
    assertEquals(
        List.of(Arrays.asList("-2", "1", NAME, NORMALIZED, "false", null)), value.speakers());
    assertEquals(
        List.of(Arrays.asList("-3", "1", "p/f", "f", null, null, null, null)), value.files());
    assertEquals(
        List.of(Arrays.asList("-4", "1", "-3", "0", "1", "narration", null, null, " Body ", null)),
        value.entries());
    assertEquals(
        List.of(Arrays.asList("-5", "1", "p/a", "a", "a_KEPT", ROLE, null, "1.234", null, null)),
        value.audio());
    assertEquals(List.of(List.of("-4", "-5", "voice")), value.links());
    assertEquals(SQL, f.sql);
    assertEquals(List.of("R0", "S0", "R1", "S1", "R2", "S2", "R3", "S3", "R4", "S4"), f.closes);
    assertEquals(List.of("L1", "I2", "S3", "S4", "B5", "S6"), f.typed.get(0));
    assertEquals(List.of("L1", "I2", "S3", "S4", "S5", "S6", "S7", "L8"), f.typed.get(1));
    assertEquals(
        List.of("L1", "I2", "L3", "I4", "I5", "S6", "L7", "S8", "S9", "S10"), f.typed.get(2));
    assertEquals(
        List.of("L1", "I2", "S3", "S4", "S5", "S6", "S7", "D8", "L9", "S10"), f.typed.get(3));
    assertEquals(List.of("L1", "L2", "S3"), f.typed.get(4));
    assertEquals(
        List.of(3, 3, 6, 3, 2),
        Arrays.asList(
            f.wasNullCounts[0],
            f.wasNullCounts[1],
            f.wasNullCounts[2],
            f.wasNullCounts[3],
            f.wasNullCounts[4]));
    assertEquals(onesList(30), f.timeouts);
    assertEquals(onesList(1000), f.fetchSizes);
    assertEquals(1, f.connectionsCreated);
    assertEquals(2, f.isolationReads);
  }

  @Test
  void snapshot002AllEmptyListsRemainEmpty() throws Exception {
    var f = normal();
    for (var rows : f.tables) rows.clear();
    var value = read(f, new int[TABLES]);
    assertTrue(value.speakers().isEmpty());
    assertTrue(value.files().isEmpty());
    assertTrue(value.entries().isEmpty());
    assertTrue(value.audio().isEmpty());
    assertTrue(value.links().isEmpty());
    assertEquals(SQL, f.sql);
    assertEquals(10, f.closes.size());
  }

  @Test
  void snapshot003NullAndEachNegativeCountFailBeforeConnectionRead() {
    assertEquals(
        INPUT_ERROR,
        assertThrows(
                IllegalArgumentException.class,
                () -> new CurrentMigrationProjection().read(null, 0, 0, 0, 0, 0))
            .getMessage());
    for (int i = 0; i < TABLES; i++) {
      var f = normal();
      var counts = ones();
      counts[i] = -1;
      assertEquals(
          INPUT_ERROR,
          assertThrows(IllegalArgumentException.class, () -> read(f, counts)).getMessage());
      assertTrue(f.calls.isEmpty());
    }
  }

  @Test
  void snapshot004BeforeAndAfterReadonlyNonautoAreRequired() {
    var a = normal();
    a.auto = true;
    attributeReject(a);
    assertEquals(0, a.sql.size());
    var b = normal();
    b.readOnly = false;
    attributeReject(b);
    assertEquals(0, b.sql.size());
    var c = normal();
    c.autoAfter = true;
    attributeReject(c);
    assertEquals(TABLES, c.sql.size());
    var d = normal();
    d.writableAfter = true;
    attributeReject(d);
    assertEquals(TABLES, d.sql.size());
  }

  @Test
  void snapshot005RepeatableAndSerializableOnlyAndNoModeChange() throws Exception {
    for (int mode : new int[] {0, 1, 2, 3, 5, 7, 9, Integer.MIN_VALUE, Integer.MAX_VALUE}) {
      var f = normal();
      f.mode = mode;
      attributeReject(f);
      assertTrue(f.sql.isEmpty());
    }
    for (int mode : new int[] {4, 8}) {
      var f = normal();
      f.mode = mode;
      assertEquals(1, read(f, ones()).speakers().size());
      assertEquals(TABLES, f.sql.size());
    }
    var changed = normal();
    changed.endMode = 8;
    attributeReject(changed);
    assertEquals(TABLES, changed.sql.size());
    var invalid = normal();
    invalid.endMode = 2;
    attributeReject(invalid);
  }

  @Test
  void snapshot006EveryAttributePhasePropagatesAllThreeFaultKinds() {
    for (String phase : List.of(AUTO, READONLY, ISOLATION))
      for (String when : List.of("begin", "end"))
        for (Throwable expected : failures()) {
          var f = normal();
          f.failurePhase = phase + ":" + when;
          f.failure = expected;
          assertSame(expected, assertThrows(expected.getClass(), () -> read(f, ones())));
          assertEquals(when.equals("end") ? TABLES : 0, f.sql.size());
          assertEquals(when.equals("end") ? 10 : 0, f.closes.size());
          assertEquals(0, expected.getSuppressed().length);
        }
  }

  @Test
  void snapshot007EveryChildMainPhasePropagatesAndStopsLaterReaders() {
    for (int table = 0; table < TABLES; table++)
      for (String phase : List.of(CREATE, TIMEOUT, FETCH, QUERY, NEXT, "getLong"))
        for (Throwable expected : failures()) {
          var f = normal();
          f.failurePhase = phase + ":" + table + (phase.equals("getLong") ? ":1" : "");
          f.failure = expected;
          assertSame(expected, assertThrows(expected.getClass(), () -> read(f, ones())));
          assertEquals(
              table + (List.of(QUERY, NEXT, "getLong").contains(phase) ? 1 : 0), f.sql.size());
          assertEquals(table + (phase.equals(CREATE) ? 0 : 1), f.statementsCreated);
          assertEquals(0, expected.getSuppressed().length);
          assertEquals(
              2 * table
                  + (phase.equals(CREATE) ? 0 : List.of(NEXT, "getLong").contains(phase) ? 2 : 1),
              f.closes.size());
        }
  }

  @Test
  void snapshot008EveryChildExactCardinalityAndNoExtraFields() {
    for (int table = 0; table < TABLES; table++)
      for (int expected : new int[] {0, 2}) {
        var f = normal();
        var counts = ones();
        counts[table] = expected;
        assertThrows(SQLException.class, () -> read(f, counts));
        assertEquals(table + 1, f.sql.size());
        assertEquals(
            expected == 0 ? 0 : 1, f.typed.get(table).stream().filter("L1"::equals).count());
        assertEquals(2 * (table + 1), f.closes.size());
      }
  }

  @Test
  void snapshot009OwnedCleanupKeepsPrimarySuppressionOrderAndIdentity() {
    for (int table = 0; table < TABLES; table++) {
      for (boolean result : List.of(true, false))
        for (Throwable expected : failures()) {
          var f = normal();
          if (result) f.resultFailures.put(table, expected);
          else f.statementFailures.put(table, expected);
          assertSame(expected, assertThrows(expected.getClass(), () -> read(f, ones())));
          assertEquals(table + 1, f.sql.size());
          assertEquals(2 * (table + 1), f.closes.size());
        }
      for (int p = 0; p < 3; p++)
        for (int rc = 0; rc < 3; rc++)
          for (int sc = 0; sc < 3; sc++) {
            var f = normal();
            Throwable primary = failures().get(p);
            Throwable result = failures().get(rc);
            Throwable statement = failures().get(sc);
            f.failurePhase = "getLong:" + table + ":1";
            f.failure = primary;
            f.resultFailures.put(table, result);
            f.statementFailures.put(table, statement);
            assertSame(primary, assertThrows(primary.getClass(), () -> read(f, ones())));
            assertEquals(List.of(result, statement), Arrays.asList(primary.getSuppressed()));
            assertEquals(2 * (table + 1), f.closes.size());
          }
      for (Throwable primary : failures()) {
        var f = normal();
        f.failurePhase = "getLong:" + table + ":1";
        f.failure = primary;
        f.resultFailures.put(table, primary);
        f.statementFailures.put(table, primary);
        assertSame(primary, assertThrows(primary.getClass(), () -> read(f, ones())));
        assertEquals(0, primary.getSuppressed().length);
      }
    }
  }

  @Test
  void snapshot010DeepImmutableRowsRetainNullableStoredValues() throws Exception {
    var f = normal();
    var value = read(f, ones());
    f.tables.get(0).get(0)[2] = "changed";
    for (var table : f.tables) table.clear();
    assertEquals(NAME, value.speakers().get(0).get(2));
    assertNull(value.speakers().get(0).get(5));
    assertNull(value.audio().get(0).get(8));
    for (var rows :
        List.of(value.speakers(), value.files(), value.entries(), value.audio(), value.links())) {
      assertThrows(UnsupportedOperationException.class, rows::clear);
      assertThrows(UnsupportedOperationException.class, () -> rows.get(0).clear());
    }
  }

  @Test
  void snapshot011FailureDoesNotPoisonSharedCoordinatorAndNoPartialSuccess() throws Exception {
    var reader = new CurrentMigrationProjection();
    var bad = normal();
    bad.nullResultTable = 4;
    assertThrows(SQLException.class, () -> reader.read(bad.connection(), 1, 1, 1, 1, 1));
    assertEquals(9, bad.closes.size());
    assertEquals(List.of("R0", "S0", "R1", "S1", "R2", "S2", "R3", "S3", "S4"), bad.closes);
    var good = normal();
    var value = reader.read(good.connection(), 1, 1, 1, 1, 1);
    assertEquals("CurrentMigrationProjection[REDACTED]", reader.toString());
    assertEquals("CurrentSourceSnapshot[REDACTED]", value.toString());
    assertEquals(SQL, good.sql);
  }

  @Test
  void snapshot012FiniteConcurrentCallsOwnAllFiveFixtures() throws Exception {
    var reader = new CurrentMigrationProjection();
    var executor = Executors.newFixedThreadPool(WORKERS);
    try {
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < TASKS; i++)
        futures.add(
            executor.submit(
                () -> {
                  var f = normal();
                  var v = reader.read(f.connection(), 1, 1, 1, 1, 1);
                  assertEquals(10, f.closes.size());
                  assertEquals(1, f.connectionsCreated);
                  return v.speakers().get(0).get(2);
                }));
      for (var future : futures) assertEquals(NAME, future.get(WAIT_SECONDS, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(TERMINATION_SECONDS, TimeUnit.SECONDS));
    }
  }

  private static CurrentMigrationProjection.SourceSnapshot read(Fixture f, int[] counts)
      throws SQLException {
    return new CurrentMigrationProjection()
        .read(f.connection(), counts[0], counts[1], counts[2], counts[3], counts[4]);
  }

  private static int[] ones() {
    return new int[] {1, 1, 1, 1, 1};
  }

  private static List<Integer> onesList(int value) {
    return List.of(value, value, value, value, value);
  }

  private static void attributeReject(Fixture f) {
    assertEquals(
        ATTRIBUTE_ERROR, assertThrows(SQLException.class, () -> read(f, ones())).getMessage());
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic sql"),
        new IllegalStateException("synthetic runtime"),
        new AssertionError("synthetic error"));
  }

  private static Fixture normal() {
    var f = new Fixture();
    f.tables.add(
        new ArrayList<>(List.<Object[]>of(new Object[] {-2L, 1, NAME, NORMALIZED, false, null})));
    f.tables.add(
        new ArrayList<>(
            List.<Object[]>of(new Object[] {-3L, 1, "p/f", "f", null, null, null, null})));
    f.tables.add(
        new ArrayList<>(
            List.<Object[]>of(
                new Object[] {-4L, 1, -3L, 0, 1, "narration", null, null, " Body ", null})));
    f.tables.add(
        new ArrayList<>(
            List.<Object[]>of(
                new Object[] {
                  -5L, 1, "p/a", "a", "a_KEPT", ROLE, null, new BigDecimal("1.234"), null, null
                })));
    f.tables.add(new ArrayList<>(List.<Object[]>of(new Object[] {-4L, -5L, "voice"})));
    return f;
  }

  private static final class Fixture {
    final List<List<Object[]>> tables = new ArrayList<>();
    final List<String> calls = new ArrayList<>();
    final List<String> sql = new ArrayList<>();
    final List<String> closes = new ArrayList<>();
    final List<Integer> timeouts = new ArrayList<>();
    final List<Integer> fetchSizes = new ArrayList<>();
    final List<List<String>> typed = new ArrayList<>();
    final int[] wasNullCounts = new int[TABLES];
    final Map<Integer, Throwable> resultFailures = new HashMap<>();
    final Map<Integer, Throwable> statementFailures = new HashMap<>();
    boolean auto;
    boolean readOnly = true;
    boolean autoAfter;
    boolean writableAfter;
    int mode = 4;
    int endMode = -1;
    int isolationReads;
    int statementsCreated;
    int connectionsCreated;
    int nullResultTable = -1;
    @Nullable String failurePhase;
    @Nullable Throwable failure;
    int failureHits;

    Fixture() {
      for (int i = 0; i < TABLES; i++) typed.add(new ArrayList<>());
    }

    Connection connection() {
      connectionsCreated++;
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                String name = method.getName();
                String when = sql.size() == TABLES ? "end" : "begin";
                if (name.equals("getAutoCommit")) {
                  hit(AUTO + ":" + when);
                  return auto || (autoAfter && sql.size() == TABLES);
                }
                if (name.equals("isReadOnly")) {
                  hit(READONLY + ":" + when);
                  return readOnly && !(writableAfter && sql.size() == TABLES);
                }
                if (name.equals("getTransactionIsolation")) {
                  hit(ISOLATION + ":" + when);
                  isolationReads++;
                  return sql.size() == TABLES && endMode >= 0 ? endMode : mode;
                }
                if (name.equals("createStatement")) {
                  int table = statementsCreated;
                  hit(CREATE + ":" + table);
                  statementsCreated++;
                  return statement(table);
                }
                throw new AssertionError("unexpected borrowed connection operation " + name);
              });
    }

    Statement statement(int table) {
      return (Statement)
          Proxy.newProxyInstance(
              Statement.class.getClassLoader(),
              new Class<?>[] {Statement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  closes.add("S" + table);
                  Throwable failure = statementFailures.get(table);
                  if (failure != null) throw failure;
                  return null;
                }
                if (name.equals("setQueryTimeout")) {
                  hit(TIMEOUT + ":" + table);
                  timeouts.add((Integer) args[0]);
                  return null;
                }
                if (name.equals("setFetchSize")) {
                  hit(FETCH + ":" + table);
                  fetchSizes.add((Integer) args[0]);
                  return null;
                }
                if (name.equals("executeQuery")) {
                  sql.add((String) args[0]);
                  assertEquals(SQL.get(table), args[0]);
                  hit(QUERY + ":" + table);
                  return table == nullResultTable ? null : result(table);
                }
                throw new AssertionError("unexpected Statement operation " + name);
              });
    }

    ResultSet result(int table) {
      var cursor = new Cursor();
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.equals("close")) {
                  closes.add("R" + table);
                  Throwable failure = resultFailures.get(table);
                  if (failure != null) throw failure;
                  return null;
                }
                if (name.equals("next")) {
                  hit(NEXT + ":" + table);
                  cursor.position++;
                  return cursor.position < tables.get(table).size();
                }
                if (name.equals("wasNull")) {
                  hit("wasNull:" + table);
                  wasNullCounts[table]++;
                  return cursor.lastNull;
                }
                if (List.of("getLong", "getInt", "getBoolean", "getString", "getBigDecimal")
                    .contains(name)) {
                  int column = (Integer) args[0];
                  hit(name + ":" + table + ":" + column);
                  Object value = tables.get(table).get(cursor.position)[column - 1];
                  cursor.lastNull = value == null;
                  typed
                      .get(table)
                      .add(
                          (name.equals("getLong")
                                  ? "L"
                                  : name.equals("getInt")
                                      ? "I"
                                      : name.equals("getBoolean")
                                          ? "B"
                                          : name.equals("getBigDecimal") ? "D" : "S")
                              + column);
                  return switch (name) {
                    case "getLong" -> value == null ? 0L : (Long) value;
                    case "getInt" -> value == null ? 0 : (Integer) value;
                    case "getBoolean" -> value == null ? false : (Boolean) value;
                    default -> value;
                  };
                }
                throw new AssertionError("unexpected ResultSet operation " + name);
              });
    }

    void hit(String phase) throws Throwable {
      calls.add(phase);
      if (phase.equals(failurePhase)) {
        failureHits++;
        if (failureHits == 1 && failure != null) throw failure;
      }
    }
  }

  private static final class Cursor {
    int position = -1;
    boolean lastNull;
  }
}
