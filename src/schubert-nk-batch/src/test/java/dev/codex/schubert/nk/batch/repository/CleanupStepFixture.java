package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;

/** Independent public PG164 JDBC fixture/oracle, SS331 3.14; BAT162..177. No deployed data. */
public final class CleanupStepFixture {
  private CleanupStepFixture() {}

  public static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  public static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  public static final List<CleanupKind> KINDS =
      List.of(
          CleanupKind.NOTIFICATIONS,
          CleanupKind.QUESTIONS,
          CleanupKind.SESSIONS,
          CleanupKind.OUTBOX,
          CleanupKind.BATCH_RUNS,
          CleanupKind.INBOX_PROGRESS,
          CleanupKind.LOG_PROGRESS);
  public static final List<String> COLS =
      List.of(
          "target_count",
          "deleted_count",
          "skipped_count",
          "step_target_count",
          "step_success_count",
          "complete",
          "reason_code");

  public static BatchStepAttempt attempt(CleanupKind k) {
    long id =
        switch (k) {
          case NOTIFICATIONS -> 90010;
          case QUESTIONS -> 90011;
          case SESSIONS -> 90012;
          case OUTBOX -> 90013;
          case WEB_RECEIPTS, BATCH_RUNS, INBOX_PROGRESS, LOG_PROGRESS -> 90014;
          case LOGS -> 90015;
        };
    return new BatchStepAttempt(id, RUN, k.step(), 1, START, false);
  }

  public static void reset(BatchDatabaseFixture db) throws Exception {
    try (var c = db.admin()) {
      sql(
          c,
          Files.readString(
              Path.of(System.getProperty("nk.pt.repository"))
                  .resolve(
                      "src/schubert-nk-api/src/test/resources/maintenance/step-cleanup-fixture.sql")));
    }
  }

  public static Connection locked(BatchDatabaseFixture db, boolean auto) throws SQLException {
    var c = db.open("schubert_batch");
    sql(c, "set timezone='UTC'");
    sql(c, "select pg_advisory_lock(71419602)");
    c.setAutoCommit(auto);
    return c;
  }

  public static void sql(Connection c, String text) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(text);
    }
  }

  public static String query(Connection c, String text) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(text)) {
      assertTrue(r.next());
      String v = r.getString(1);
      assertFalse(r.next());
      return v;
    }
  }

  public static String totals(Connection c, long id) throws SQLException {
    return query(
        c,
        "select status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count||'|'||(ended_at is null)::text from schubert.batch_runs where id="
            + id);
  }

  public static void trace(String name, String text) throws Exception {
    Path d = Path.of("target/atomic-cleanup-traces");
    Files.createDirectories(d);
    Files.writeString(d.resolve(name), text);
  }

  /** SS331/332 fixed call protocol, computed before implementation; 32 refs + 21 cleanup = 53. */
  public static Map<String, Integer> repositoryInventory() {
    return Map.ofEntries(
        Map.entry("connection.getAutoCommit", 2),
        Map.entry("connection.isReadOnly", 2),
        Map.entry("connection.getTransactionIsolation", 2),
        Map.entry("connection.prepareStatement", 3),
        Map.entry("statement.setQueryTimeout", 3),
        Map.entry("statement.setObject", 7),
        Map.entry("statement.setLong", 1),
        Map.entry("statement.setInt", 2),
        Map.entry("statement.setString", 1),
        Map.entry("statement.executeQuery", 3),
        Map.entry("statement.close", 3),
        Map.entry("row.next", 6),
        Map.entry("row.getObject", 14),
        Map.entry("row.getString", 1),
        Map.entry("row.close", 3));
  }

  @FunctionalInterface
  public interface Hook {
    void call(String key, int occurrence) throws Throwable;
  }

  /**
   * Observe real JDBC, selectively fail one independently enumerated position; no fake database
   * success.
   */
  public static final class Probe {
    public final Map<String, Integer> seen = new TreeMap<>();
    public final Map<String, Set<Integer>> faults = new HashMap<>();
    public final Map<String, Throwable> unknown = new HashMap<>();
    public final Map<String, Throwable> cleanupFaults = new HashMap<>();
    public final Map<String, Integer> cleanupSeen = new TreeMap<>();
    public int cleanupInjected;
    public final Map<String, Object> overrides = new HashMap<>();
    public final Map<Integer, Map<String, Object>> cleanupOverrides = new HashMap<>();
    public final List<Map<Integer, Object>> cleanupBinds = new ArrayList<>();
    public final List<Long> deletedCounts = new ArrayList<>();
    public final Set<String> columns = new TreeSet<>();
    public Hook before = (k, n) -> {};
    public Hook after = (k, n) -> {};
    public String anomaly = "";
    public int badRefs;
    public int failures;
    public int rows;
    public int statements;
    public int cleanupQueries;
    public int refsQueries;

    public void fail(String key, int... positions) {
      var s = new HashSet<Integer>();
      for (int i : positions) s.add(i);
      faults.put(key, s);
    }

    private void hit(String key) throws Throwable {
      int n = seen.merge(key, 1, Integer::sum);
      before.call(key, n);
      if (faults.getOrDefault(key, Set.of()).contains(n)) {
        failures++;
        throw new SQLException("public provider diagnostic", "08006");
      }
      if (unknown.containsKey(key)) throw unknown.get(key);
    }

    private void cleanupHit(boolean cleanup, String key) throws Throwable {
      if (!cleanup) return;
      int n = cleanupSeen.merge(key, 1, Integer::sum);
      if (n == 1 && cleanupFaults.containsKey(key)) {
        cleanupInjected++;
        throw cleanupFaults.get(key);
      }
    }

    public Connection wrap(Connection c) {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (p, m, a) -> {
                String name = m.getName();
                String key = "connection." + name;
                hit(key);
                assertTrue(
                    Set.of(
                            "getAutoCommit",
                            "isReadOnly",
                            "getTransactionIsolation",
                            "prepareStatement",
                            "setAutoCommit",
                            "commit",
                            "rollback")
                        .contains(name),
                    "borrowed connection ownership: " + name);
                if (name.equals("prepareStatement")) {
                  String text = (String) a[0];
                  boolean cleanup;
                  if (text.equals(
                      "select target_count,deleted_count,skipped_count,step_target_count,step_success_count,complete,reason_code from schubert.maintenance_execute_cleanup_step(?,?,?,?,?,?,?)"))
                    cleanup = true;
                  else {
                    assertEquals(
                        "select has_batch_history,has_inbox_progress,has_log_progress,identity_consistent from schubert.maintenance_read_run_references(?,?)",
                        text);
                    cleanup = false;
                  }
                  if (cleanup && anomaly.equals("nullStatement")) return null;
                  var s = (PreparedStatement) invoke(c, m, a);
                  statements++;
                  return statement(s, cleanup);
                }
                Object v = invoke(c, m, a);
                after.call(key, seen.get(key));
                return v;
              });
    }

    private PreparedStatement statement(PreparedStatement s, boolean cleanup) {
      Map<Integer, Object> binds = new TreeMap<>();
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (p, m, a) -> {
                String name = m.getName();
                String key = "statement." + name;
                if (name.equals("close")) {
                  Object v = invoke(s, m, a);
                  statements--;
                  hit(key);
                  cleanupHit(cleanup, key);
                  after.call(key, seen.get(key));
                  return v;
                }
                hit(key);
                cleanupHit(cleanup, key);
                if (name.equals("setQueryTimeout")) assertEquals(5, a[0]);
                if (Set.of("setObject", "setLong", "setInt", "setString").contains(name)) {
                  binds.put((Integer) a[0], a[1]);
                  if (a[1] instanceof OffsetDateTime time)
                    assertEquals(ZoneOffset.UTC, time.getOffset());
                }
                if (name.equals("executeQuery")) {
                  assertEquals(cleanup ? 7 : 2, binds.size());
                  for (int i = 1; i <= binds.size(); i++) assertTrue(binds.containsKey(i));
                  if (cleanup) cleanupBinds.add(Map.copyOf(binds));
                  if (cleanup && anomaly.equals("nullRows")) return null;
                  var r = (ResultSet) invoke(s, m, a);
                  rows++;
                  int sequence = cleanup ? ++cleanupQueries : ++refsQueries;
                  return row(r, cleanup, sequence);
                }
                Object v = invoke(s, m, a);
                after.call(key, seen.get(key));
                return v;
              });
    }

    private ResultSet row(ResultSet r, boolean cleanup, int sequence) {
      int[] position = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (p, m, a) -> {
                String name = m.getName();
                String key = "row." + name;
                if (name.equals("close")) {
                  Object v = invoke(r, m, a);
                  rows--;
                  hit(key);
                  cleanupHit(cleanup, key);
                  after.call(key, seen.get(key));
                  return v;
                }
                hit(key);
                cleanupHit(cleanup, key);
                if (name.equals("next")) {
                  position[0]++;
                  if (cleanup && anomaly.equals("empty")) return false;
                  if (cleanup && anomaly.equals("extra") && position[0] == 2) return true;
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  String col = (String) a[0];
                  if (cleanup) {
                    columns.add(col);
                    if (name.equals("getObject"))
                      assertEquals(col.equals("complete") ? Boolean.class : Long.class, a[1]);
                    var local = cleanupOverrides.getOrDefault(sequence, Map.of());
                    if (local.containsKey(col)) return local.get(col);
                    if (overrides.containsKey(col)) return overrides.get(col);
                  } else if (sequence == badRefs && col.equals("identity_consistent")) return false;
                }
                Object v = invoke(r, m, a);
                if (cleanup && name.equals("getObject") && a[0].equals("deleted_count"))
                  deletedCounts.add((Long) v);
                after.call(key, seen.get(key));
                return v;
              });
    }

    public void closed() {
      assertEquals(0, rows, "owned rows");
      assertEquals(0, statements, "owned statements");
    }

    private static Object invoke(Object target, Method m, Object[] a) throws Throwable {
      try {
        return m.invoke(target, a);
      } catch (InvocationTargetException e) {
        throw e.getCause();
      }
    }
  }
}
