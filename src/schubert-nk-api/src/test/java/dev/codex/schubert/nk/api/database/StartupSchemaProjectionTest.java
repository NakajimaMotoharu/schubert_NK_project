package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SSC095/PG312/PT-DB-SCHEMA001..008. Isolated PG; literal role/row/catalog oracle. */
final class StartupSchemaProjectionTest {
  private static final String FIXTURE_SCHUBERT_APP_5AB151CF = "schubert_app";
  private static final String FIXTURE_SCHUBERT_WEB_SESSION_1E78D426 = "schubert_web_session";
  private static final String FIXTURE_SCHUBERT_BATCH_F9C88479 = "schubert_batch";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture db;
  private static String url;
  private static final String QUERY =
      "select installed_rank,version,type,script,checksum,success from schubert_meta.startup_schema_history() order by installed_rank";
  private static final List<String> VERSIONS =
      List.of(
          "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013",
          "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024", "025", "026",
          "027", "028", "029");

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
    try (var c = db.admin()) {
      url = c.getMetaData().getURL();
    }
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void dbSchema001ExactProfileIncludesSchemaCreation() throws Exception {
    assertEquals(VERSIONS, MigrationInventory.VERSIONS);
    try (var c = role(FIXTURE_SCHUBERT_APP_5AB151CF);
        var s = c.createStatement();
        var rows = s.executeQuery(QUERY)) {
      assertTrue(rows.next());
      assertEquals(0, rows.getInt("installed_rank"));
      assertNull(rows.getString("version"));
      assertEquals("SCHEMA", rows.getString("type"));
      assertEquals("\"schubert_meta\"", rows.getString("script"));
      assertNull(rows.getObject("checksum"));
      assertTrue(rows.getBoolean("success"));
      int rank = 0;
      for (String version : VERSIONS) {
        assertTrue(rows.next());
        assertEquals(++rank, rows.getInt("installed_rank"));
        assertEquals(version, rows.getString("version"));
        assertEquals("SQL", rows.getString("type"));
        assertTrue(rows.getString("script").matches("V" + version + "__[a-z0-9_]+\\.sql"));
        assertInstanceOf(Integer.class, rows.getObject("checksum"));
        assertTrue(rows.getBoolean("success"));
      }
      assertFalse(rows.next());
      // SSC340: 29 versioned rows plus the unchanged schema-creation row.
      assertEquals(30, rank + 1);
    }
  }

  @Test
  void dbSchema002FixedDefinitionOwnerSearchPathAndNoPublicGrant() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select pg_get_userbyid(proowner),prosecdef,provolatile,proconfig,pg_get_function_result(oid),pronargs,pg_get_functiondef(oid) from pg_proc where oid='schubert_meta.startup_schema_history()'::regprocedure")) {
      assertTrue(r.next());
      assertEquals("nk_owner", r.getString(1));
      assertTrue(r.getBoolean(2));
      assertEquals("s", r.getString(3));
      assertArrayEquals(
          new String[] {"search_path=pg_catalog, pg_temp"}, (String[]) r.getArray(4).getArray());
      assertEquals(
          "TABLE(installed_rank integer, version text, type text, script text, checksum integer, success boolean)",
          r.getString(5));
      assertEquals(0, r.getInt(6));
      String definition = r.getString(7);
      assertTrue(definition.contains("schubert_meta.flyway_schema_history"));
      assertFalse(definition.toLowerCase(Locale.ROOT).contains("where"));
      assertFalse(r.next());
      try (var a =
          s.executeQuery(
              "select count(*) from pg_proc p cross join lateral aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a where p.oid='schubert_meta.startup_schema_history()'::regprocedure and a.grantee=0")) {
        assertTrue(a.next());
        assertEquals(0, a.getInt(1));
      }
    }
  }

  @Test
  void dbSchema003OnlyExactRuntimeRolesMayExecute() throws Exception {
    for (String name :
        List.of(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_SCHUBERT_WEB_SESSION_1E78D426,
            FIXTURE_SCHUBERT_BATCH_F9C88479))
      try (var c = role(name);
          var s = c.createStatement();
          var r = s.executeQuery(QUERY)) {
        int count = 0;
        while (r.next()) count++;
        assertEquals(29, count); // SSC201: 28 approved SQL rows and one SCHEMA row.
      }
    for (String name : List.of("schubert_backup", "schubert_inbox_inspector", "schubert_ops_ro"))
      try (var c = role(name)) {
        denied(c, QUERY);
      }
    try (var c = db.admin();
        var s = c.createStatement()) {
      s.execute("create role pgpt_schema_untrusted login");
    }
    try (var c = role("pgpt_schema_untrusted")) {
      denied(c, QUERY);
    } finally {
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute("drop role pgpt_schema_untrusted");
      }
    }
  }

  @Test
  void dbSchema004NoDirectHistoryOrMetadataCreateOrOwnerEscalation() throws Exception {
    for (String name :
        List.of(
            FIXTURE_SCHUBERT_APP_5AB151CF,
            FIXTURE_SCHUBERT_WEB_SESSION_1E78D426,
            FIXTURE_SCHUBERT_BATCH_F9C88479))
      try (var c = role(name)) {
        denied(c, "select * from schubert_meta.flyway_schema_history");
        denied(c, "create table schubert_meta.pgpt_forbidden(id integer)");
        denied(c, "set role nk_owner");
        try (var s = c.createStatement();
            var r =
                s.executeQuery(
                    "select has_schema_privilege(current_user,'schubert_meta','USAGE'),has_schema_privilege(current_user,'schubert_meta','CREATE'),pg_has_role(current_user,'nk_owner','MEMBER')")) {
          assertTrue(r.next());
          assertTrue(r.getBoolean(1));
          assertFalse(r.getBoolean(2));
          assertFalse(r.getBoolean(3));
        }
      }
    try (var c = role(FIXTURE_SCHUBERT_WEB_SESSION_1E78D426)) {
      denied(c, "select * from schubert.users");
      try (var s = c.createStatement();
          var r = s.executeQuery("select has_schema_privilege(current_user,'schubert','USAGE')")) {
        assertTrue(r.next());
        assertFalse(r.getBoolean(1));
      }
    }
  }

  @Test
  void dbSchema005FailedAndNullVersionRowsNeverFiltered() throws Exception {
    try (var c = db.admin()) {
      c.setAutoCommit(false);
      try (var s = c.createStatement()) {
        assertEquals(
            1,
            s.executeUpdate(
                "update schubert_meta.flyway_schema_history set success=false,version=null where installed_rank=23"));
        try (var r = s.executeQuery(QUERY)) {
          int count = 0;
          while (r.next()) {
            count++;
            if (r.getInt("installed_rank") == 23) {
              assertNull(r.getString("version"));
              assertFalse(r.getBoolean("success"));
              assertEquals("SQL", r.getString("type"));
            }
          }
          assertEquals(29, count);
        }
      } finally {
        c.rollback();
      }
    }
    try (var c = role(FIXTURE_SCHUBERT_BATCH_F9C88479);
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select count(*) from schubert_meta.startup_schema_history() where not success")) {
      assertTrue(r.next());
      assertEquals(0, r.getInt(1));
    }
  }

  @Test
  void dbSchema006TemporaryShadowCannotChangeQualifiedProjection() throws Exception {
    try (var c = role(FIXTURE_SCHUBERT_BATCH_F9C88479);
        var s = c.createStatement()) {
      s.execute("create temp table flyway_schema_history(installed_rank integer)");
      s.execute("insert into flyway_schema_history values(9999)");
      s.execute("set search_path=pg_temp,public");
      try (var r = s.executeQuery(QUERY)) {
        assertTrue(r.next());
        assertEquals(0, r.getInt(1));
        int count = 1;
        while (r.next()) count++;
        assertEquals(29, count);
      }
    }
  }

  @Test
  void dbSchema007ReadOnlyTransactionAndNoBusinessWrites() throws Exception {
    try (var c = role(FIXTURE_SCHUBERT_BATCH_F9C88479)) {
      c.setReadOnly(true);
      c.setAutoCommit(false);
      try (var s = c.createStatement();
          var r = s.executeQuery(QUERY)) {
        int count = 0;
        while (r.next()) count++;
        assertEquals(29, count);
      }
      c.rollback();
    }
    try (var c = db.admin();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert.batch_runs")) {
      assertTrue(r.next());
      assertEquals(0, r.getInt(1));
    }
  }

  @Test
  void dbSchema008ConcurrentRolesHaveIndependentResultAndConnections() throws Exception {
    try (var pool = java.util.concurrent.Executors.newVirtualThreadPerTaskExecutor()) {
      var barrier = new java.util.concurrent.CyclicBarrier(3);
      var tasks = new ArrayList<java.util.concurrent.Future<Integer>>();
      for (String name :
          List.of(
              FIXTURE_SCHUBERT_APP_5AB151CF,
              FIXTURE_SCHUBERT_WEB_SESSION_1E78D426,
              FIXTURE_SCHUBERT_BATCH_F9C88479))
        tasks.add(
            pool.submit(
                () -> {
                  try (var c = role(name);
                      var s = c.createStatement()) {
                    barrier.await();
                    try (var r = s.executeQuery(QUERY)) {
                      int count = 0;
                      while (r.next()) count++;
                      return count;
                    }
                  }
                }));
      for (var task : tasks) assertEquals(29, task.get().intValue());
    }
  }

  private static Connection role(String name) throws SQLException {
    return DriverManager.getConnection(url, name, "");
  }

  private static void denied(Connection c, String sql) throws SQLException {
    try (var s = c.createStatement()) {
      SQLException error = assertThrows(SQLException.class, () -> s.execute(sql));
      assertEquals("42501", error.getSQLState());
    }
  }
}
