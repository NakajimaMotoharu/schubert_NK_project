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
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001; DAT-009/OPS-009/UI251/SS311/331 3.12/332/343; SSC055/PG159; BAT082..089. */
final class RunReferenceRepositoryTest {
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00.123456Z"));
  static final BatchRun OTHER =
      new BatchRun(UUID.fromString("11111111-2222-3333-4444-555555555555"), RUN.cutoff());
  static final RunReferences EMPTY = new RunReferences(false, false, false, true);
  static final List<String> FLAGS =
      List.of("has_batch_history", "has_inbox_progress", "has_log_progress", "identity_consistent");
  static final Map<String, Integer> INVENTORY =
      Map.ofEntries(
          Map.entry("connection.getAutoCommit", 1),
          Map.entry("connection.isReadOnly", 1),
          Map.entry("connection.getTransactionIsolation", 1),
          Map.entry("connection.prepareStatement", 1),
          Map.entry("statement.setQueryTimeout", 1),
          Map.entry("statement.setObject", 2),
          Map.entry("statement.executeQuery", 1),
          Map.entry("statement.close", 1),
          Map.entry("row.next", 2),
          Map.entry("row.getObject", 4),
          Map.entry("row.close", 1));

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
      for (String table :
          List.of("batch_runs", "inbox_inspection_progress", "log_cleanup_progress"))
        sql(c, "delete from schubert." + table);
    }
  }

  @Test
  void referenceValueInvariants() {
    for (int mask = 0; mask < 8; mask++)
      for (boolean consistent : List.of(false, true)) {
        boolean history = (mask & 1) != 0;
        boolean inbox = (mask & 2) != 0;
        boolean log = (mask & 4) != 0;
        if (mask == 0 && !consistent) {
          assertThrows(
              IllegalArgumentException.class, () -> new RunReferences(history, inbox, log, false));
        } else {
          var value = new RunReferences(history, inbox, log, consistent);
          assertEquals(history, value.hasBatchHistory());
          assertEquals(inbox, value.hasInboxProgress());
          assertEquals(log, value.hasLogProgress());
          assertEquals(consistent, value.identityConsistent());
          assertEquals(mask != 0, value.anyReference());
          assertEquals(new RunReferences(history, inbox, log, consistent), value);
          assertEquals(
              new RunReferences(history, inbox, log, consistent).hashCode(), value.hashCode());
          assertEquals("RunReferences[observation=<redacted>]", value.toString());
        }
      }
    assertNotEquals(EMPTY, new RunReferences(true, false, false, true));
  }

  @Test
  void realReferenceRead() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      var repository = new RunReferenceRepository(c);
      assertEquals(EMPTY, repository.read(RUN));
      history(admin, OTHER);
      assertEquals(EMPTY, repository.read(RUN));
      history(admin, RUN);
      assertEquals(new RunReferences(true, false, false, true), repository.read(RUN));
      progress(admin, "inbox_inspection_progress", RUN);
      assertEquals(new RunReferences(true, true, false, true), repository.read(RUN));
      progress(admin, "log_cleanup_progress", RUN);
      assertEquals(new RunReferences(true, true, true, true), repository.read(RUN));
      sql(admin, "update schubert.log_cleanup_progress set cutoff=cutoff+interval '1 microsecond'");
      assertEquals(new RunReferences(true, true, true, false), repository.read(RUN));
      assertEquals(Instant.parse("2026-09-12T15:00:00.123456Z"), RUN.cutoff());
      c.rollback();
      // BUG167/DB249/BAT083: SQL literal fixture cannot cancel a JDBC bind calendar defect.
      for (String table :
          List.of("batch_runs", "inbox_inspection_progress", "log_cleanup_progress"))
        sql(admin, "delete from schubert." + table);
      for (String literal :
          List.of("0001-01-01T00:00:00Z", "1582-10-05T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
        sql(
            admin,
            "insert into schubert.inbox_inspection_progress(run_id,cutoff) values('"
                + RUN.id()
                + "','"
                + literal
                + "')");
        assertEquals(
            new RunReferences(false, true, false, true),
            repository.read(new BatchRun(RUN.id(), Instant.parse(literal))),
            literal);
        sql(admin, "delete from schubert.inbox_inspection_progress");
      }
    }
  }

  @Test
  void transactionAndLockContracts() throws Exception {
    try (var c = db.open("schubert_batch")) {
      redacted(() -> new RunReferenceRepository(c).read(RUN));
      c.setAutoCommit(false);
      redacted(() -> new RunReferenceRepository(c).read(RUN));
      c.rollback();
      c.setReadOnly(true);
      redacted(() -> new RunReferenceRepository(c).read(RUN));
      c.setReadOnly(false);
      for (int level :
          List.of(
              Connection.TRANSACTION_SERIALIZABLE,
              Connection.TRANSACTION_REPEATABLE_READ,
              Connection.TRANSACTION_READ_UNCOMMITTED)) {
        c.setTransactionIsolation(level);
        redacted(() -> new RunReferenceRepository(c).read(RUN));
      }
      c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      sql(c, "select pg_advisory_lock_shared(71419602)");
      redacted(() -> new RunReferenceRepository(c).read(RUN));
      c.rollback();
      sql(c, "select pg_advisory_unlock_shared(71419602)");
      c.rollback();
      sql(c, "select pg_advisory_lock(71419602)");
      c.rollback();
      Probe p = new Probe();
      assertEquals(EMPTY, new RunReferenceRepository(p.wrap(c)).read(RUN));
      assertEquals(INVENTORY, p.seen);
      p.assertOwnedClosed();
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertFalse(c.isReadOnly());
      assertEquals(Connection.TRANSACTION_READ_COMMITTED, c.getTransactionIsolation());
      c.rollback();
    }
  }

  @Test
  void projectionAndNullContracts() throws Exception {
    assertThrows(NullPointerException.class, () -> new RunReferenceRepository(null));
    try (var c = locked()) {
      Probe nullInput = new Probe();
      assertThrows(
          NullPointerException.class,
          () -> new RunReferenceRepository(nullInput.wrap(c)).read(null));
      assertTrue(nullInput.seen.isEmpty());
      for (String anomaly :
          List.of(
              "nullStatement",
              "nullRows",
              "missing",
              "duplicate",
              "inconsistent",
              "has_batch_history",
              "has_inbox_progress",
              "has_log_progress",
              "identity_consistent")) {
        Probe p = new Probe();
        p.anomaly = anomaly;
        redacted(() -> new RunReferenceRepository(p.wrap(c)).read(RUN));
        p.assertOwnedClosed();
        c.rollback();
      }
    }
  }

  @Test
  void jdbcFailureMatrix() throws Exception {
    try (var c = locked()) {
      Probe observed = new Probe();
      assertEquals(EMPTY, new RunReferenceRepository(observed.wrap(c)).read(RUN));
      assertEquals(INVENTORY, observed.seen);
      observed.assertOwnedClosed();
      c.rollback();
      for (var entry : INVENTORY.entrySet())
        for (int pos = 1; pos <= entry.getValue(); pos++) {
          Probe p = new Probe();
          p.failAt.put(entry.getKey(), pos);
          redacted(() -> new RunReferenceRepository(p.wrap(c)).read(RUN));
          assertEquals(1, p.failures);
          p.assertOwnedClosed();
          assertFalse(c.isClosed());
          c.rollback();
        }
      Probe both = new Probe();
      both.failAt.put("row.close", 1);
      both.failAt.put("statement.close", 1);
      redacted(() -> new RunReferenceRepository(both.wrap(c)).read(RUN));
      assertEquals(2, both.failures);
      both.assertOwnedClosed();
      c.rollback();
    }
  }

  @Test
  void interruptionAndRuntime() throws Exception {
    try (var c = locked()) {
      for (var sample : JdbcResourceCases.all()) {
        var probe = new Probe();
        sample.install(probe.thrown);
        sample.verify(
            assertThrows(
                Throwable.class, () -> new RunReferenceRepository(probe.wrap(c)).read(RUN)));
        probe.assertOwnedClosed();
        assertEquals(sample.first() < 0 ? 1 : 2, probe.failures);
        assertEquals(1, probe.seen.getOrDefault("statement.close", 0));
        assertEquals(
            sample.first() >= 0 && sample.body().equals("statement.executeQuery") ? 0 : 1,
            probe.seen.getOrDefault("row.close", 0));
        for (String call :
            List.of(
                "close",
                "commit",
                "rollback",
                "setAutoCommit",
                "setReadOnly",
                "setTransactionIsolation"))
          assertEquals(0, probe.seen.getOrDefault("connection." + call, 0));
        assertFalse(c.isClosed());
        assertEquals(false, c.getAutoCommit());
      }
      assertAll(
          () -> {
            var probe = new Probe();
            var failure = new IllegalArgumentException("public unknown provider fault");
            probe.thrown.put("statement.executeQuery", failure);
            assertSame(
                failure,
                assertThrows(
                    Throwable.class, () -> new RunReferenceRepository(probe.wrap(c)).read(RUN)));
          },
          () -> {
            var probe = new Probe();
            var failure = new IllegalStateException("public same provider fault");
            probe.thrown.put("row.next", failure);
            probe.thrown.put("row.close", failure);
            assertSame(
                failure,
                assertThrows(
                    Throwable.class, () -> new RunReferenceRepository(probe.wrap(c)).read(RUN)));
          });
      Probe initial = new Probe();
      Thread.currentThread().interrupt();
      try {
        redacted(() -> new RunReferenceRepository(initial.wrap(c)).read(RUN));
        assertTrue(Thread.currentThread().isInterrupted());
        assertTrue(initial.seen.isEmpty());
      } finally {
        Thread.interrupted();
      }
      Probe last = new Probe();
      last.interruptAt = "statement.close";
      try {
        redacted(() -> new RunReferenceRepository(last.wrap(c)).read(RUN));
        assertTrue(Thread.currentThread().isInterrupted());
        last.assertOwnedClosed();
      } finally {
        Thread.interrupted();
      }
      c.rollback();
      for (RuntimeException failure :
          List.of(
              new IllegalStateException("public-runtime"),
              new NullPointerException("public-null"))) {
        Probe p = new Probe();
        p.runtime = failure;
        assertSame(
            failure,
            assertThrows(
                RuntimeException.class, () -> new RunReferenceRepository(p.wrap(c)).read(RUN)));
        p.assertOwnedClosed();
        assertFalse(c.isClosed());
        c.rollback();
      }
    }
  }

  @Test
  void rollbackAndFreshVisibility() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      var repository = new RunReferenceRepository(c);
      assertEquals(EMPTY, repository.read(RUN));
      history(c, RUN);
      assertEquals(new RunReferences(true, false, false, true), repository.read(RUN));
      c.rollback();
      assertEquals(EMPTY, repository.read(RUN));
      progress(admin, "inbox_inspection_progress", RUN);
      assertEquals(new RunReferences(false, true, false, true), repository.read(RUN));
      sql(
          admin,
          "update schubert.inbox_inspection_progress set cutoff=cutoff-interval '1 microsecond'");
      assertEquals(new RunReferences(false, true, false, false), repository.read(RUN));
      sql(admin, "delete from schubert.inbox_inspection_progress");
      assertEquals(EMPTY, repository.read(RUN));
      c.rollback();
    }
  }

  @Test
  void independentConcurrentConnections() throws Exception {
    try (var owner = locked();
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      assertEquals(
          Boolean.TRUE,
          executor
              .submit(
                  () -> {
                    try (var c = db.open("schubert_batch")) {
                      c.setAutoCommit(false);
                      redacted(() -> new RunReferenceRepository(c).read(OTHER));
                      c.rollback();
                      return !c.isClosed();
                    }
                  })
              .get(10, TimeUnit.SECONDS));
      assertEquals(EMPTY, new RunReferenceRepository(owner).read(RUN));
      owner.rollback();
      sql(owner, "select pg_advisory_unlock(71419602)");
      owner.rollback();
      assertEquals(
          EMPTY,
          executor
              .submit(
                  () -> {
                    try (var c = locked()) {
                      var value = new RunReferenceRepository(c).read(OTHER);
                      c.rollback();
                      return value;
                    }
                  })
              .get(10, TimeUnit.SECONDS));
      assertFalse(owner.isClosed());
    }
  }

  static Connection locked() throws SQLException {
    var c = db.open("schubert_batch");
    sql(c, "select pg_advisory_lock(71419602)");
    c.setAutoCommit(false);
    return c;
  }

  static void history(Connection c, BatchRun run) throws SQLException {
    try (var s =
        c.prepareStatement(
            "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,status) values(?,'2026-09-13',?,1,'2000-01-01','RUNNING')")) {
      s.setObject(1, run.id());
      s.setString(2, run.equals(RUN) ? "PUBLIC_RUN" : "PUBLIC_OTHER");
      s.executeUpdate();
    }
  }

  static void progress(Connection c, String table, BatchRun run) throws SQLException {
    try (var s =
        c.prepareStatement("insert into schubert." + table + "(run_id,cutoff) values(?,?)")) {
      s.setObject(1, run.id());
      s.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
      s.executeUpdate();
    }
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
                      "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent from schubert.maintenance_read_run_references(?,?)",
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
                if (name.equals("close")) {
                  Object value = invoke(statement, m, a);
                  statements--;
                  hit("statement.close");
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
                if (name.equals("close")) {
                  Object value = invoke(row, m, a);
                  rows--;
                  hit("row.close");
                  return value;
                }
                hit("row." + name);
                if (name.equals("next")) {
                  position[0]++;
                  if (anomaly.equals("missing")) return false;
                  if (anomaly.equals("duplicate") && position[0] == 2) return true;
                }
                if (name.equals("getObject")) {
                  assertTrue(FLAGS.contains(a[0]));
                  assertEquals(Boolean.class, a[1]);
                  if (anomaly.equals(a[0])) return null;
                  if (anomaly.equals("inconsistent") && a[0].equals("identity_consistent"))
                    return false;
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
