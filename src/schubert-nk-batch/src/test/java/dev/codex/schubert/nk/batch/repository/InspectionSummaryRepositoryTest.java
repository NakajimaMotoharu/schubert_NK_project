package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001; SS331 3.13/341 7.3; SSC049/PG162; BAT114..121. */
final class InspectionSummaryRepositoryTest {
  private static final String FIXTURE_STATEMENT_EXECUTEQUERY_67733F33 = "statement.executeQuery";
  private static final String FIXTURE_STATEMENT_CLOSE_FE807BAF = "statement.close";
  private static final String FIXTURE_ROW_CLOSE_F197F129 = "row.close";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00.123456Z"));
  static final List<String> FLAGS =
      List.of("inspected_count", "deleted_count", "protected_count", "complete");
  // Hand-counted SS protocol: 3 state + prepare + timeout + 2 bind + execute
  // + next + 4 fields + next + 2 owned closes = 16; absent omits 4 fields/second next = 11.
  static final Map<String, Integer> ONE =
      Map.ofEntries(
          Map.entry("connection.getAutoCommit", 1),
          Map.entry("connection.isReadOnly", 1),
          Map.entry("connection.getTransactionIsolation", 1),
          Map.entry("connection.prepareStatement", 1),
          Map.entry("statement.setQueryTimeout", 1),
          Map.entry("statement.setObject", 2),
          Map.entry(FIXTURE_STATEMENT_EXECUTEQUERY_67733F33, 1),
          Map.entry(FIXTURE_STATEMENT_CLOSE_FE807BAF, 1),
          Map.entry("row.next", 2),
          Map.entry("row.getObject", 4),
          Map.entry(FIXTURE_ROW_CLOSE_F197F129, 1));
  static final Map<String, Integer> EMPTY =
      Map.ofEntries(
          Map.entry("connection.getAutoCommit", 1), Map.entry("connection.isReadOnly", 1),
          Map.entry("connection.getTransactionIsolation", 1),
              Map.entry("connection.prepareStatement", 1),
          Map.entry("statement.setQueryTimeout", 1), Map.entry("statement.setObject", 2),
          Map.entry(FIXTURE_STATEMENT_EXECUTEQUERY_67733F33, 1),
              Map.entry(FIXTURE_STATEMENT_CLOSE_FE807BAF, 1),
          Map.entry("row.next", 1), Map.entry(FIXTURE_ROW_CLOSE_F197F129, 1));

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.inbox_inspection_progress");
    }
  }

  @Test
  void summaryValueInvariants() {
    assertThrows(
        NullPointerException.class,
        () -> new InspectionSummary(null, new CleanupCounts(0, 0, 0), false));
    assertThrows(NullPointerException.class, () -> new InspectionSummary(RUN, null, false));
    for (boolean end : List.of(false, true)) {
      var value = new InspectionSummary(RUN, new CleanupCounts(5, 2, 3), end);
      var copy =
          new InspectionSummary(
              new BatchRun(RUN.id(), RUN.cutoff()), new CleanupCounts(5, 2, 3), end);
      assertEquals(RUN, value.run());
      assertEquals(new CleanupCounts(5, 2, 3), value.counts());
      assertEquals(end, value.complete());
      assertEquals(value, copy);
      assertEquals(value.hashCode(), copy.hashCode());
      assertEquals("InspectionSummary[observation=<redacted>]", value.toString());
      assertNotEquals(value, new InspectionSummary(RUN, value.counts(), !end));
    }
  }

  @Test
  void realBoundedRead() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      var repo = new InspectionSummaryRepository(c);
      assertEquals(Optional.empty(), repo.read(RUN));
      insert(admin, RUN.cutoff().toString());
      assertEquals(
          Optional.of(new InspectionSummary(RUN, new CleanupCounts(0, 0, 0), false)),
          repo.read(RUN));
      sql(
          admin,
          "update schubert.inbox_inspection_progress set inspected_count=5,deleted_count=2,protected_count=3,after_message_id='00000000-0000-0000-0000-000000000002'");
      assertEquals(
          Optional.of(new InspectionSummary(RUN, new CleanupCounts(5, 2, 3), false)),
          repo.read(RUN));
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      assertEquals(
          Optional.of(new InspectionSummary(RUN, new CleanupCounts(5, 2, 3), true)),
          repo.read(RUN));
      assertTrue(repo.read(new BatchRun(new UUID(0, 99), RUN.cutoff())).isEmpty());
      redacted(() -> repo.read(new BatchRun(RUN.id(), RUN.cutoff().plusNanos(1000))));
    }
  }

  @Test
  void parentStateAndLock() throws Exception {
    try (var c = db.open("schubert_batch")) {
      redacted(() -> new InspectionSummaryRepository(c).read(RUN));
      sql(c, "select pg_advisory_lock_shared(71419602)");
      redacted(() -> new InspectionSummaryRepository(c).read(RUN));
      sql(c, "select pg_advisory_unlock_shared(71419602)");
      sql(c, "select pg_advisory_lock(71419602)");
      c.setAutoCommit(false);
      redacted(() -> new InspectionSummaryRepository(c).read(RUN));
      c.rollback();
      c.setAutoCommit(true);
      c.setReadOnly(true);
      redacted(() -> new InspectionSummaryRepository(c).read(RUN));
      c.setReadOnly(false);
      for (int level :
          List.of(
              Connection.TRANSACTION_REPEATABLE_READ,
              Connection.TRANSACTION_SERIALIZABLE,
              Connection.TRANSACTION_READ_UNCOMMITTED)) {
        c.setTransactionIsolation(level);
        redacted(() -> new InspectionSummaryRepository(c).read(RUN));
      }
      c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      assertTrue(new InspectionSummaryRepository(c).read(RUN).isEmpty());
      try (var other = db.open("schubert_batch")) {
        redacted(() -> new InspectionSummaryRepository(other).read(RUN));
      }
      assertTrue(c.getAutoCommit());
      assertFalse(c.isReadOnly());
      assertFalse(c.isClosed());
    }
  }

  @Test
  void projectionAndNull() throws Exception {
    assertThrows(NullPointerException.class, () -> new InspectionSummaryRepository(null));
    try (var c = locked();
        var admin = db.admin()) {
      Probe p = new Probe();
      assertThrows(
          NullPointerException.class, () -> new InspectionSummaryRepository(p.wrap(c)).read(null));
      assertTrue(p.seen.isEmpty());
      assertEquals(Optional.empty(), new InspectionSummaryRepository(c).read(RUN));
      insert(admin, RUN.cutoff().toString());
      for (String anomaly :
          List.of(
              "nullStatement",
              "nullRows",
              "duplicate",
              "negative",
              "inconsistent",
              "inspected_count",
              "deleted_count",
              "protected_count",
              "complete")) {
        Probe broken = new Probe();
        broken.anomaly = anomaly;
        redacted(() -> new InspectionSummaryRepository(broken.wrap(c)).read(RUN));
        broken.assertOwnedClosed();
      }
    }
  }

  @Test
  void allJdbcFailurePositions() throws Exception {
    assertEquals(16, ONE.values().stream().mapToInt(Integer::intValue).sum());
    assertEquals(11, EMPTY.values().stream().mapToInt(Integer::intValue).sum());
    try (var c = locked();
        var admin = db.admin()) {
      for (boolean populated : List.of(false, true)) {
        if (populated) insert(admin, RUN.cutoff().toString());
        var expected = populated ? ONE : EMPTY;
        Probe normal = new Probe();
        assertEquals(
            populated, new InspectionSummaryRepository(normal.wrap(c)).read(RUN).isPresent());
        assertEquals(expected, normal.seen);
        normal.assertOwnedClosed();
        for (var entry : expected.entrySet())
          for (int pos = 1; pos <= entry.getValue(); pos++) {
            Probe fault = new Probe();
            fault.failAt.put(entry.getKey(), pos);
            redacted(() -> new InspectionSummaryRepository(fault.wrap(c)).read(RUN));
            assertEquals(1, fault.failures);
            fault.assertOwnedClosed();
            assertFalse(c.isClosed());
          }
        Probe both = new Probe();
        both.failAt.put(FIXTURE_ROW_CLOSE_F197F129, 1);
        both.failAt.put(FIXTURE_STATEMENT_CLOSE_FE807BAF, 1);
        redacted(() -> new InspectionSummaryRepository(both.wrap(c)).read(RUN));
        assertEquals(2, both.failures);
        both.assertOwnedClosed();
      }
    }
  }

  @Test
  void historicalUtcIdentity() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        sql(c, "set timezone='" + zone + "'");
        for (String literal :
            List.of(
                "0001-01-01T00:00:00Z",
                "1582-10-04T00:00:00Z",
                "1582-10-05T00:00:00Z",
                "1582-10-14T00:00:00Z",
                "1582-10-15T00:00:00Z",
                "1900-03-01T00:00:00Z",
                "1970-01-01T00:00:00Z",
                "2026-09-12T14:59:59.999999Z",
                "2026-09-12T15:00:00.123456Z",
                "9999-12-31T23:59:59.999999Z")) {
          sql(admin, "delete from schubert.inbox_inspection_progress");
          insert(admin, literal);
          var expected = new BatchRun(RUN.id(), Instant.parse(literal));
          assertEquals(
              Optional.of(new InspectionSummary(expected, new CleanupCounts(0, 0, 0), false)),
              new InspectionSummaryRepository(c).read(expected),
              zone + "/" + literal);
        }
      }
    }
  }

  @Test
  void freshVisibilityAndBorrowing() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      Probe p = new Probe();
      var repo = new InspectionSummaryRepository(p.wrap(c));
      assertTrue(repo.read(RUN).isEmpty());
      admin.setAutoCommit(false);
      insert(admin, RUN.cutoff().toString());
      assertTrue(repo.read(RUN).isEmpty());
      admin.commit();
      assertEquals(
          new InspectionSummary(RUN, new CleanupCounts(0, 0, 0), false),
          repo.read(RUN).orElseThrow());
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      assertFalse(repo.read(RUN).orElseThrow().complete());
      admin.rollback();
      assertFalse(repo.read(RUN).orElseThrow().complete());
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      admin.commit();
      assertTrue(repo.read(RUN).orElseThrow().complete());
      for (String forbidden :
          List.of(
              "commit",
              "rollback",
              FIXTURE_CLOSE_97959247,
              "setAutoCommit",
              "setReadOnly",
              "setTransactionIsolation"))
        assertFalse(p.seen.containsKey("connection." + forbidden), forbidden);
      p.assertOwnedClosed();
      assertTrue(c.getAutoCommit());
      assertFalse(c.isReadOnly());
      assertEquals(Connection.TRANSACTION_READ_COMMITTED, c.getTransactionIsolation());
    }
  }

  @Test
  void interruptAndRuntime() throws Exception {
    try (var c = locked()) {
      for (var sample : JdbcResourceCases.all()) {
        var probe = new Probe();
        sample.install(probe.thrown);
        sample.verify(
            assertThrows(
                Throwable.class, () -> new InspectionSummaryRepository(probe.wrap(c)).read(RUN)));
        probe.assertOwnedClosed();
        assertEquals(sample.first() < 0 ? 1 : 2, probe.failures);
        assertEquals(1, probe.seen.getOrDefault(FIXTURE_STATEMENT_CLOSE_FE807BAF, 0));
        assertEquals(
            sample.first() >= 0 && sample.body().equals(FIXTURE_STATEMENT_EXECUTEQUERY_67733F33)
                ? 0
                : 1,
            probe.seen.getOrDefault(FIXTURE_ROW_CLOSE_F197F129, 0));
        for (String call :
            List.of(
                FIXTURE_CLOSE_97959247,
                "commit",
                "rollback",
                "setAutoCommit",
                "setReadOnly",
                "setTransactionIsolation"))
          assertEquals(0, probe.seen.getOrDefault("connection." + call, 0));
        assertFalse(c.isClosed());
        assertEquals(true, c.getAutoCommit());
      }
      assertAll(
          () -> {
            var probe = new Probe();
            var failure = new IllegalArgumentException("public unknown provider fault");
            probe.thrown.put(FIXTURE_STATEMENT_EXECUTEQUERY_67733F33, failure);
            assertSame(
                failure,
                assertThrows(
                    Throwable.class,
                    () -> new InspectionSummaryRepository(probe.wrap(c)).read(RUN)));
          },
          () -> {
            var probe = new Probe();
            var failure = new IllegalStateException("public same provider fault");
            probe.thrown.put("row.next", failure);
            probe.thrown.put(FIXTURE_ROW_CLOSE_F197F129, failure);
            assertSame(
                failure,
                assertThrows(
                    Throwable.class,
                    () -> new InspectionSummaryRepository(probe.wrap(c)).read(RUN)));
          });
      Probe first = new Probe();
      Thread.currentThread().interrupt();
      try {
        redacted(() -> new InspectionSummaryRepository(first.wrap(c)).read(RUN));
        assertTrue(Thread.currentThread().isInterrupted());
        assertTrue(first.seen.isEmpty());
      } finally {
        Thread.interrupted();
      }
      Probe last = new Probe();
      last.interruptAt = FIXTURE_STATEMENT_CLOSE_FE807BAF;
      try {
        redacted(() -> new InspectionSummaryRepository(last.wrap(c)).read(RUN));
        assertTrue(Thread.currentThread().isInterrupted());
        last.assertOwnedClosed();
      } finally {
        Thread.interrupted();
      }
      for (RuntimeException error :
          List.of(
              new IllegalStateException("public-runtime"),
              new NullPointerException("public-null"))) {
        Probe fault = new Probe();
        fault.runtime = error;
        assertSame(
            error,
            assertThrows(
                RuntimeException.class,
                () -> new InspectionSummaryRepository(fault.wrap(c)).read(RUN)));
        fault.assertOwnedClosed();
        assertFalse(c.isClosed());
      }
    }
  }

  static Connection locked() throws SQLException {
    var c = db.open("schubert_batch");
    sql(c, "select pg_advisory_lock(71419602)");
    return c;
  }

  static void insert(Connection c, String literal) throws SQLException {
    sql(
        c,
        "insert into schubert.inbox_inspection_progress(run_id,cutoff) values('"
            + RUN.id()
            + "','"
            + literal
            + "')");
  }

  static void sql(Connection c, String query) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(query);
    }
  }

  static void redacted(Runnable action) {
    var error = assertThrows(BatchRepositoryException.class, action::run);
    assertEquals("batch repository operation failed", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  static final class Probe {
    final Map<String, Integer> seen = new HashMap<>();
    final Map<String, Integer> failAt = new HashMap<>();
    final Map<String, Throwable> thrown = new HashMap<>();
    String anomaly = "";
    String interruptAt = "";
    RuntimeException runtime;
    int failures;
    int statements;
    int rows;

    Connection wrap(Connection connection) {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (p, m, a) -> {
                hit("connection." + m.getName());
                if (m.getName().equals("prepareStatement")) {
                  assertEquals(
                      "select inspected_count,deleted_count,protected_count,complete from schubert.maintenance_read_inbox_summary(?,?)",
                      a[0]);
                  if (anomaly.equals("nullStatement")) return null;
                  statements++;
                  return statement((PreparedStatement) invoke(connection, m, a));
                }
                return invoke(connection, m, a);
              });
    }

    PreparedStatement statement(PreparedStatement statement) {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (p, m, a) -> {
                String name = m.getName();
                if (name.equals(FIXTURE_CLOSE_97959247)) {
                  Object value = invoke(statement, m, a);
                  statements--;
                  hit(FIXTURE_STATEMENT_CLOSE_FE807BAF);
                  return value;
                }
                hit("statement." + name);
                if (name.equals("setQueryTimeout")) assertEquals(5, a[0]);
                if (name.equals("setObject")) {
                  assertTrue(a[0].equals(1) || a[0].equals(2));
                  assertEquals(
                      a[0].equals(1)
                          ? RUN.id()
                          : java.time.OffsetDateTime.parse("2026-09-12T15:00:00.123456Z"),
                      a[1]);
                }
                if (name.equals("executeQuery")) {
                  if (runtime != null) throw runtime;
                  if (anomaly.equals("nullRows")) return null;
                  ResultSet result = (ResultSet) invoke(statement, m, a);
                  rows++;
                  return row(result);
                }
                return invoke(statement, m, a);
              });
    }

    ResultSet row(ResultSet row) {
      int[] position = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (p, m, a) -> {
                String name = m.getName();
                if (name.equals(FIXTURE_CLOSE_97959247)) {
                  Object value = invoke(row, m, a);
                  rows--;
                  hit(FIXTURE_ROW_CLOSE_F197F129);
                  return value;
                }
                hit("row." + name);
                if (name.equals("next")) {
                  position[0]++;

                  if (anomaly.equals("duplicate") && position[0] == 2) return true;
                }
                if (name.equals("getObject")) {
                  assertTrue(FLAGS.contains(a[0]));
                  assertEquals(a[0].equals("complete") ? Boolean.class : Long.class, a[1]);
                  if (anomaly.equals(a[0])) return null;
                  if (anomaly.equals("negative") && a[0].equals("inspected_count")) return -1L;
                  if (anomaly.equals("inconsistent") && a[0].equals("protected_count")) return 2L;
                }
                return invoke(row, m, a);
              });
    }

    void hit(String name) throws Throwable {
      int count = seen.merge(name, 1, Integer::sum);
      if (count == 1 && thrown.containsKey(name)) {
        failures++;
        throw thrown.get(name);
      }
      if (name.equals(interruptAt)) Thread.currentThread().interrupt();
      if (Objects.equals(failAt.get(name), count)) {
        failures++;
        throw new SQLException("public-provider-fixture", "08006");
      }
    }

    void assertOwnedClosed() {
      assertEquals(0, statements);
      assertEquals(0, rows);
    }

    static Object invoke(Object target, Method method, Object[] args) throws Throwable {
      try {
        return method.invoke(target, args);
      } catch (InvocationTargetException failure) {
        throw failure.getCause();
      }
    }
  }
}
