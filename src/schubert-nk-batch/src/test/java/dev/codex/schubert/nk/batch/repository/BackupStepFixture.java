package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupVersions;
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
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;
import org.junit.jupiter.api.function.Executable;

/** Independent public JDBC/SQL oracle for PG168, BAT210..225. No deployed data. */
public final class BackupStepFixture {
  private BackupStepFixture() {}

  public static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  public static final Instant START = Instant.parse("2026-09-13T02:00:00Z");
  public static final Instant CONTENT = Instant.parse("2026-09-13T02:00:02Z");
  public static final Instant END = Instant.parse("2026-09-13T02:00:03Z");
  public static final List<String> COLUMNS =
      List.of(
          "id",
          "run_id",
          "business_date",
          "step",
          "attempt",
          "started_at",
          "ended_at",
          "status",
          "target_count",
          "success_count",
          "failure_count",
          "byte_count",
          "error_code",
          "error_summary");

  public static BackupManifest manifest() {
    return manifest(false);
  }

  public static BackupManifest manifest(boolean reverse) {
    var database =
        new BatchStepAttempt(reverse ? 90002 : 90001, RUN, BatchStep.BACKUP_DB, 1, START, false);
    var config =
        new BatchStepAttempt(
            reverse ? 90001 : 90002, RUN, BatchStep.BACKUP_CONFIG, 1, START, false);
    return new BackupManifest(
        database,
        config,
        START.plusSeconds(1),
        CONTENT,
        new BackupVersions(
            "public-host", "1.0", "020", "Ubuntu26.04", "25.0.4", "18.6", "2.56.0", "1.2.1"),
        "0".repeat(64),
        new BackupFileDigest(26, "1".repeat(64)),
        new BackupFileDigest(35, "2".repeat(64)),
        new BackupFileDigest(32, "3".repeat(64)));
  }

  public static void reset(BatchDatabaseFixture db) throws SQLException {
    reset(db, false);
  }

  public static void reset(BatchDatabaseFixture db, boolean reverse) throws SQLException {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.batch_runs");
      sql(c, "delete from schubert.inbox_inspection_progress");
      sql(c, "delete from schubert.log_cleanup_progress");
      sql(
          c,
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,status) values "
              + "(90001,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','"
              + (reverse ? "BACKUP_CONFIG" : "BACKUP_DB")
              + "',1,'2026-09-13T02:00:00Z','RUNNING'),"
              + "(90002,'12345678-9abc-def0-8123-456789abcdef','2026-09-13','"
              + (reverse ? "BACKUP_DB" : "BACKUP_CONFIG")
              + "',1,'2026-09-13T02:00:00Z','RUNNING')");
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
      String value = r.getString(1);
      assertFalse(r.next());
      return value;
    }
  }

  public static String state(Connection c) throws SQLException {
    return query(
        c,
        "select string_agg(step||'|'||status||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count||'|'||coalesce(to_char(ended_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US')||'+00','NULL')||'|'||(error_code is null)||'|'||(error_summary is null),E'\\n' order by step) from schubert.batch_runs");
  }

  public static final String RUNNING =
      "BACKUP_CONFIG|RUNNING|0|0|0|0|NULL|true|true\nBACKUP_DB|RUNNING|0|0|0|0|NULL|true|true";
  public static final String SUCCEEDED =
      "BACKUP_CONFIG|SUCCESS|2|2|0|67|2026-09-13 02:00:03.000000+00|true|true\nBACKUP_DB|SUCCESS|1|1|0|26|2026-09-13 02:00:03.000000+00|true|true";

  public static void seedSuccess(Connection c) throws SQLException {
    sql(
        c,
        "update schubert.batch_runs set status='SUCCESS',ended_at='2026-09-13T02:00:03Z',target_count=case step when 'BACKUP_DB' then 1 else 2 end,success_count=case step when 'BACKUP_DB' then 1 else 2 end,byte_count=case step when 'BACKUP_DB' then 26 else 67 end");
  }

  public static void failed(Executable work) {
    var e = assertThrows(BatchRepositoryException.class, work);
    assertEquals("batch repository operation failed", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  public static void trace(String name, String data) throws Exception {
    Path root = Path.of("target/backup-step-traces");
    Files.createDirectories(root);
    Files.writeString(root.resolve(name), data);
  }

  /** Derived from SS331/341 fixed JDBC projection, not the production call recording. */
  public static Map<String, Integer> inventory(boolean fresh, boolean service) {
    var r = new TreeMap<String, Integer>();
    int refs = fresh ? 8 : 2;
    int pairs = fresh ? 2 : 1;
    int updates = fresh ? 2 : 0;
    r.put("connection.getAutoCommit", refs + (service ? 1 : 0));
    r.put("connection.isReadOnly", refs + (service ? 1 : 0));
    r.put("connection.getTransactionIsolation", refs + (service ? 1 : 0));
    r.put("connection.prepareStatement", refs + pairs + updates);
    for (var e :
        Map.of(
                "statement.setQueryTimeout",
                1,
                "statement.setObject",
                2,
                "statement.executeQuery",
                1,
                "statement.close",
                1,
                "row.next",
                2,
                "row.getObject",
                4,
                "row.close",
                1)
            .entrySet()) r.put("refs." + e.getKey(), refs * e.getValue());
    for (var e :
        Map.of(
                "statement.setQueryTimeout",
                1,
                "statement.setLong",
                2,
                "statement.executeQuery",
                1,
                "statement.close",
                1,
                "row.next",
                3,
                "row.getObject",
                20,
                "row.getString",
                8,
                "row.close",
                1)
            .entrySet()) r.put("pair." + e.getKey(), pairs * e.getValue());
    if (updates > 0)
      for (var e :
          Map.of(
                  "statement.setQueryTimeout",
                  1,
                  "statement.setObject",
                  4,
                  "statement.setString",
                  4,
                  "statement.setLong",
                  5,
                  "statement.setInt",
                  1,
                  "statement.executeUpdate",
                  1,
                  "statement.close",
                  1)
              .entrySet()) r.put("update." + e.getKey(), updates * e.getValue());
    if (service) {
      r.put("connection.setAutoCommit", 2);
      r.put("connection.commit", 1);
    }
    return r;
  }

  @FunctionalInterface
  public interface Hook {
    void call(String key, int n) throws Throwable;
  }

  public static final class Probe {
    public final Map<String, Integer> seen = new TreeMap<>();
    public final Map<String, Set<Integer>> faults = new HashMap<>();
    public final Map<String, Throwable> unknown = new HashMap<>();
    public final Map<String, Throwable> compound = new HashMap<>();
    public int compoundInjected;
    public final Map<Integer, Map<String, Object>> override = new HashMap<>();
    public final Set<String> columns = new TreeSet<>();
    public Hook before = (k, n) -> {};
    public Hook after = (k, n) -> {};
    public String anomaly = "";
    public int rows;
    public int statements;
    public int hits;
    public int pairSequence;
    public int badReferences;
    public int overrideSequence; // 0 means every pair query.

    public void fail(String key, int... positions) {
      var set = new HashSet<Integer>();
      for (int p : positions) set.add(p);
      faults.put(key, set);
    }

    public void change(int row, String col, Object value) {
      override.computeIfAbsent(row, k -> new HashMap<>()).put(col, value);
    }

    private void hit(String key) throws Throwable {
      int n = seen.merge(key, 1, Integer::sum);
      before.call(key, n);
      if (n == 1 && compound.containsKey(key)) {
        compoundInjected++;
        throw compound.get(key);
      }
      if (faults.getOrDefault(key, Set.of()).contains(n)) {
        hits++;
        throw new SQLException("PUBLIC_DIAGNOSTIC_CANARY", "08006");
      }
      if (unknown.containsKey(key)) throw unknown.get(key);
    }

    public Connection wrap(Connection c) {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (p, m, a) -> {
                String name = m.getName();
                String key = "connection." + name;
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
                    "borrowed ownership " + name);
                hit(key);
                if (name.equals("prepareStatement")) {
                  String sql = (String) a[0];
                  String kind;
                  if (sql.contains("maintenance_read_run_references")) kind = "refs";
                  else if (sql.startsWith("select id,run_id,")) kind = "pair";
                  else if (sql.startsWith("update schubert.batch_runs set ended_at="))
                    kind = "update";
                  else throw new AssertionError("unexpected SQL shape");
                  if (kind.equals("pair")) {
                    assertEquals(
                        "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
                            + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
                            + " from schubert.batch_runs where id in (?,?) order by id for update",
                        sql);
                    if (anomaly.equals("nullStatement")) return null;
                  }
                  var s = (PreparedStatement) invoke(c, m, a);
                  statements++;
                  return statement(s, kind);
                }
                Object result = invoke(c, m, a);
                after.call(key, seen.get(key));
                return result;
              });
    }

    private PreparedStatement statement(PreparedStatement s, String kind) {
      Map<Integer, Object> binds = new TreeMap<>();
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (p, m, a) -> {
                String name = m.getName();
                String key = kind + ".statement." + name;
                if (name.equals("close")) {
                  Object r = invoke(s, m, a);
                  statements--;
                  hit(key);
                  after.call(key, seen.get(key));
                  return r;
                }
                hit(key);
                if (name.equals("setQueryTimeout")) assertEquals(5, a[0]);
                if (Set.of("setObject", "setLong", "setString", "setInt").contains(name)) {
                  binds.put((Integer) a[0], a[1]);
                  if (a[1] instanceof OffsetDateTime time)
                    assertEquals(ZoneOffset.UTC, time.getOffset());
                }
                if (name.equals("executeQuery")) {
                  if (kind.equals("pair")) {
                    assertEquals(Set.of(90001L, 90002L), new HashSet<>(binds.values()));
                    if (anomaly.equals("nullRows")) return null;
                  }
                  var row = (ResultSet) invoke(s, m, a);
                  rows++;
                  int sequence = kind.equals("pair") ? ++pairSequence : 0;
                  return row(row, kind, sequence);
                }
                Object r = invoke(s, m, a);
                after.call(key, seen.get(key));
                return r;
              });
    }

    private ResultSet row(ResultSet row, String kind, int sequence) {
      int[] position = {0};
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (p, m, a) -> {
                String name = m.getName();
                String key = kind + ".row." + name;
                if (name.equals("close")) {
                  Object r = invoke(row, m, a);
                  rows--;
                  hit(key);
                  after.call(key, seen.get(key));
                  return r;
                }
                hit(key);
                if (name.equals("next")) {
                  position[0]++;
                  if (kind.equals("pair")) {
                    if (anomaly.equals("empty")) return false;
                    if (anomaly.equals("one") && position[0] == 2) return false;
                    if (anomaly.equals("extra") && position[0] == 3) return true;
                  }
                }
                if (name.equals("getObject") || name.equals("getString")) {
                  String col = (String) a[0];
                  if (kind.equals("pair")) {
                    columns.add(col);
                    var map = override.getOrDefault(position[0], Map.of());
                    if ((overrideSequence == 0 || overrideSequence == sequence)
                        && map.containsKey(col)) return map.get(col);
                  } else if (col.equals("identity_consistent") && badReferences > 0) return false;
                }
                Object r = invoke(row, m, a);
                after.call(key, seen.get(key));
                return r;
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
