package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.database.MigrationInventory;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-DAT-001; OPS009/DAT009/MQ008/UI212/241/251/SS331 3.13; SSC049/PG162; DB251..258. */
final class InspectionParentBoundaryTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static String url;
  static final UUID RUN = UUID.fromString("12345678-9abc-def0-8123-456789abcdef");
  static final String TIME = "2026-09-12T15:00:00.123456Z";
  static final String SIGNATURE = "schubert.maintenance_read_inbox_summary(uuid,timestamptz)";
  static final List<String> FIELDS =
      List.of("inspected_count", "deleted_count", "protected_count", "complete");

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

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.admin()) {
      sql(c, "delete from schubert.inbox_inspection_progress");
    }
  }

  @Test
  void summaryStatesAndCounts() throws Exception {
    StringBuilder trace = new StringBuilder();
    try (var c = locked();
        var admin = db.admin()) {
      assertEquals(List.of(), read(c, RUN, TIME));
      trace.append("absent=[]\n");
      insert(admin, TIME, 0, 0, 0, false);
      assertEquals(List.of(0L, 0L, 0L, false), read(c, RUN, TIME));
      trace.append("open=").append(read(c, RUN, TIME)).append('\n');
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      assertEquals(List.of(0L, 0L, 0L, true), read(c, RUN, TIME));
      trace.append("emptyEnd=").append(read(c, RUN, TIME)).append('\n');
      sql(admin, "delete from schubert.inbox_inspection_progress");
      insert(admin, TIME, 9, 5, 4, true);
      assertEquals(List.of(9L, 5L, 4L, true), read(c, RUN, TIME));
      trace.append("mixedEnd=").append(read(c, RUN, TIME)).append('\n');
      sql(admin, "delete from schubert.inbox_inspection_progress");
      insert(admin, TIME, Long.MAX_VALUE, Long.MAX_VALUE - 1, 1, true);
      assertEquals(List.of(Long.MAX_VALUE, Long.MAX_VALUE - 1, 1L, true), read(c, RUN, TIME));
      trace.append("maxEnd=").append(read(c, RUN, TIME)).append('\n');
    }
    Path target = Path.of("target/parent-summary-traces");
    Files.createDirectories(target);
    Files.writeString(
        target.resolve("PT-DB-INBOX-251-states.txt"), trace, StandardCharsets.US_ASCII);
  }

  @Test
  void identityAndTimeBoundaries() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        sql(c, "set timezone='" + zone + "'");
        for (String literal :
            List.of(
                "0001-01-01T00:00:00Z",
                "1582-10-05T00:00:00Z",
                "1582-10-15T00:00:00Z",
                "2026-09-12T14:59:59.999999Z",
                TIME,
                "9999-12-31T23:59:59.999999Z")) {
          sql(admin, "delete from schubert.inbox_inspection_progress");
          insert(admin, literal, 0, 0, 0, false);
          assertEquals(List.of(0L, 0L, 0L, false), read(c, RUN, literal), zone + "/" + literal);
          assertEquals(List.of(), read(c, new UUID(0, 99), literal));
        }
        for (String at :
            List.of(
                "null",
                "'infinity'",
                "'-infinity'",
                "'0001-01-01 00:00:00+00 BC'",
                "'10000-01-01 00:00:00+00'"))
          reject(
              c,
              "select * from schubert.maintenance_read_inbox_summary('" + RUN + "'," + at + ")",
              "22023");
      }
      reject(
          c, "select * from schubert.maintenance_read_inbox_summary(null,'" + TIME + "')", "22023");
      sql(admin, "delete from schubert.inbox_inspection_progress");
      insert(admin, TIME, 0, 0, 0, false);
      assertEquals(
          "55000",
          assertThrows(SQLException.class, () -> read(c, RUN, "2026-09-12T15:00:00.123457Z"))
              .getSQLState());
    }
  }

  @Test
  void parentLockNamespaces() throws Exception {
    try (var c = open("schubert_batch")) {
      reject(c, query(), "55000");
      assertEquals(
          "0",
          scalar(
              c,
              "select count(*) from pg_locks where pid=pg_backend_pid() and locktype='advisory'"));
      for (String lock :
          List.of("pg_advisory_lock_shared(71419602)", "pg_advisory_lock(0,71419602)")) {
        sql(c, "select " + lock);
        reject(c, query(), "55000");
        sql(c, "select pg_advisory_unlock_all()");
      }
      sql(c, "select pg_advisory_lock(71419602)");
      assertEquals(List.of(), read(c, RUN, TIME));
      assertEquals("t", scalar(c, "select pg_advisory_unlock(71419602)"));
      assertEquals("f", scalar(c, "select pg_advisory_unlock(71419602)"));
      c.setAutoCommit(false);
      sql(c, "select pg_advisory_xact_lock(71419602)");
      assertEquals(List.of(), read(c, RUN, TIME));
      c.rollback();
      c.setAutoCommit(true);
      reject(c, query(), "55000");
      assertTrue(c.getAutoCommit());
      assertFalse(c.isReadOnly());
      assertEquals(Connection.TRANSACTION_READ_COMMITTED, c.getTransactionIsolation());
    }
  }

  @Test
  void roleAndCatalog() throws Exception {
    try (var c = db.admin()) {
      assertEquals(
          "nk_owner/true/search_path=pg_catalog, schubert,TimeZone=UTC",
          scalar(
              c,
              "select pg_get_userbyid(proowner)||'/'||prosecdef::text||'/'||array_to_string(proconfig,',') from pg_proc where oid='"
                  + SIGNATURE
                  + "'::regprocedure"));
      assertEquals(
          "false",
          scalar(c, "select has_function_privilege('public','" + SIGNATURE + "','EXECUTE')::text"));
      assertEquals(
          "true",
          scalar(
              c,
              "select has_function_privilege('schubert_batch','"
                  + SIGNATURE
                  + "','EXECUTE')::text"));
      for (String privilege :
          List.of("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"))
        assertEquals(
            "false",
            scalar(
                c,
                "select has_table_privilege('schubert_batch','schubert.inbox_inspection_progress','"
                    + privilege
                    + "')::text"));
    }
    for (String role :
        List.of(
            "schubert_app",
            "schubert_web_session",
            "schubert_backup",
            "schubert_ops_ro",
            "schubert_inbox_inspector"))
      try (var c = open(role)) {
        reject(c, query(), "42501");
      }
  }

  @Test
  void freshReadAndRollback() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      assertEquals(List.of(), read(c, RUN, TIME));
      admin.setAutoCommit(false);
      insert(admin, TIME, 5, 2, 3, false);
      assertEquals(List.of(), read(c, RUN, TIME));
      admin.rollback();
      assertEquals(List.of(), read(c, RUN, TIME));
      insert(admin, TIME, 5, 2, 3, false);
      admin.commit();
      assertEquals(List.of(5L, 2L, 3L, false), read(c, RUN, TIME));
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      assertEquals(List.of(5L, 2L, 3L, false), read(c, RUN, TIME));
      admin.rollback();
      assertEquals(List.of(5L, 2L, 3L, false), read(c, RUN, TIME));
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      admin.commit();
      assertEquals(List.of(5L, 2L, 3L, true), read(c, RUN, TIME));
    }
  }

  @Test
  void concurrentOwners() throws Exception {
    try (var first = locked();
        var admin = db.admin();
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      admin.setAutoCommit(false);
      insert(admin, TIME, 5, 2, 3, true);
      assertEquals(List.of(), read(first, RUN, TIME));
      assertEquals(
          "55000",
          executor
              .submit(
                  () -> {
                    try (var other = open("schubert_batch")) {
                      assertEquals("f", scalar(other, "select pg_try_advisory_lock(71419602)"));
                      return assertThrows(SQLException.class, () -> read(other, RUN, TIME))
                          .getSQLState();
                    }
                  })
              .get(10, TimeUnit.SECONDS));
      admin.commit();
      assertEquals(List.of(5L, 2L, 3L, true), read(first, RUN, TIME));
      assertEquals("t", scalar(first, "select pg_advisory_unlock(71419602)"));
      assertEquals(
          List.of(5L, 2L, 3L, true),
          executor
              .submit(
                  () -> {
                    try (var other = locked()) {
                      assertEquals(List.of(), read(other, new UUID(0, 99), TIME));
                      return read(other, RUN, TIME);
                    }
                  })
              .get(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void noMutationOrPrivateProjection() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      insert(admin, TIME, 9, 5, 4, true);
      List<String> before = snapshot(admin);
      String indexes =
          scalar(
              admin,
              "select string_agg(indexname||':'||indexdef,'|' order by indexname) from pg_indexes where schemaname='schubert'");
      assertEquals("0", scalar(admin, "select count(*) from schubert.batch_runs"));
      for (int i = 0; i < 5; i++) assertEquals(List.of(9L, 5L, 4L, true), read(c, RUN, TIME));
      assertEquals(before, snapshot(admin));
      assertEquals(
          indexes,
          scalar(
              admin,
              "select string_agg(indexname||':'||indexdef,'|' order by indexname) from pg_indexes where schemaname='schubert'"));
      try (var s = c.createStatement();
          var r = s.executeQuery(query())) {
        var meta = r.getMetaData();
        assertEquals(4, meta.getColumnCount());
        for (int i = 1; i <= 4; i++) {
          assertEquals(FIELDS.get(i - 1), meta.getColumnLabel(i));
          assertEquals(i == 4 ? Types.BIT : Types.BIGINT, meta.getColumnType(i));
        }
      }
      // No row lock: an independent owner may take a NOWAIT row lock while this read transaction
      // stays open.
      c.setAutoCommit(false);
      assertEquals(List.of(9L, 5L, 4L, true), read(c, RUN, TIME));
      admin.setAutoCommit(false);
      sql(admin, "select * from schubert.inbox_inspection_progress for update nowait");
      admin.rollback();
      c.rollback();
    }
  }

  @Test
  void appendOnlyMigration() throws Exception {
    // SSC095/152 append V023/024; historical V001..018 hashes below remain immutable.
    assertEquals(
        List.of(
            "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012",
            "013", "014", "015", "016", "017", "018", "019", "020", "021", "022", "023", "024",
            "025", "026", "027", "028"),
        MigrationInventory.VERSIONS);
    assertEquals(
        "001,002,003,004,005,006,007,008,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028",
        MigrationInventory.CSV);
    assertEquals("28", MigrationInventory.COUNT_TEXT);
    assertNotEquals(MigrationInventory.VERSIONS.subList(0, 18), MigrationInventory.VERSIONS);
    assertThrows(UnsupportedOperationException.class, () -> MigrationInventory.VERSIONS.add("022"));
    Path migrations =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db/migration");
    // Frozen sha256sum from certified 510dde02, before adding V019.
    List<String> hashes =
        List.of(
            "f687a36d1e296d38306997808b0f4440e484e24dd37b3862476fb470e56930da",
            "23f82d08f89bf6abfb75cbf41d126b174fcef5cf77563755fc316b31fb817e8e",
            "85f05cda30be1dd7856fb1eee3b25f42c6513641ab5d30b92410210f5460aa5e",
            "fdf634ace2beef2d57e28ad65c2ed488eab493cb2b0d8b1d421eab8397b8079e",
            "daf64a15c753cea106b593e6da944db08f7b13c94d3f2aa4ec6626fcd8b56ff9",
            "79623b56b8fe9d27af75df6a5db5cf47f4b93fb7b5ae2b9eb4d19ce6d6624052",
            "3b93f98b801c967c78113f3931b89b32aa9dc821d336af6c81076efc26da0401",
            "a90b338170322bd190335d2cfd382bb36b6f8b1243410345ef35b54dda928412",
            "537c7844709ed116f23fa60c64ae378e79eadad79f2e8003bbfd688f42335312",
            "c27a17adba2367ded5dcefe1532f5b42e7e4e35259f32388fe2667049e8644b0",
            "18e92bfc225f39c7a0ecaf9bdbeef329e5a47c0af3283d12f858deb4aec09928",
            "21e4c781a4b4c1a18240d8e47fae5bc2d11593d7b4ad05590ed10a67ebcb9411",
            "d56446bcfb7b3fa74ad0939baa3e2c0d263dd8a975cb7e3a9ce06bac2be85a74",
            "d2ba884de86c59c5815559aaf17a83b7a0546fcc7f9f48649dd744d127270229",
            "1c5544165e1ab8441f6edf3dcc83dbb5ac9e05a6e6bfb9a7086d0d8ea0f6396b",
            "99a9ae01ff3a6833d22d7c514c67c2229eb459e38bbf3e38da17a6b796f38aa8",
            "c412685a319defa1cb4f91846c02d69dbbc18457da5feb9d66266d2aec3446ce",
            "8799bd8dbe60b34e8c7a4e507ad54b2c41979be47973943b5e868d1224f302c9");
    List<Path> files;
    try (var stream = Files.list(migrations)) {
      files = stream.sorted().toList();
    }
    assertEquals(28, files.size());
    for (int i = 0; i < 18; i++) {
      assertTrue(files.get(i).getFileName().toString().startsWith("V%03d__".formatted(i + 1)));
      assertEquals(
          hashes.get(i),
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(files.get(i)))));
    }
    try (var c = db.admin()) {
      assertEquals(
          "001,002,003,004,005,006,007,008,009,010,011,012,013,014,015,016,017,018,019,020,021,022,023,024,025,026,027,028",
          scalar(
              c,
              "select string_agg(version,',' order by installed_rank) from schubert_meta.flyway_schema_history where version is not null and success"));
    }
    var flyway =
        Flyway.configure()
            .dataSource(url, "schubert_migration", "")
            .defaultSchema("schubert_meta")
            .schemas("schubert_meta")
            .initSql("SET ROLE nk_owner")
            .locations("filesystem:" + migrations)
            .cleanDisabled(true)
            .load();
    flyway.validate();
    assertEquals(0, flyway.migrate().migrationsExecuted);
  }

  static List<String> snapshot(Connection c) throws SQLException {
    List<String> tables = new ArrayList<>();
    try (var s = c.createStatement();
        var r =
            s.executeQuery(
                "select tablename from pg_tables where schemaname='schubert' order by tablename")) {
      while (r.next()) tables.add(r.getString(1));
    }
    List<String> snapshot = new ArrayList<>();
    for (String table : tables) {
      assertTrue(table.matches("[a-z_]+"));
      snapshot.add(
          table
              + ":"
              + scalar(
                  c,
                  "select coalesce(string_agg(row_to_json(t)::text,'|' order by row_to_json(t)::text),'') from schubert."
                      + table
                      + " t"));
    }
    return List.copyOf(snapshot);
  }

  static Connection open(String role) throws SQLException {
    return DriverManager.getConnection(url, role, "");
  }

  static Connection locked() throws SQLException {
    var c = open("schubert_batch");
    sql(c, "select pg_advisory_lock(71419602)");
    return c;
  }

  static void sql(Connection c, String query) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(query);
    }
  }

  static String scalar(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String value = r.getString(1);
      assertNotNull(value);
      assertFalse(r.next());
      return value;
    }
  }

  static void reject(Connection c, String query, String state) {
    var error = assertThrows(SQLException.class, () -> sql(c, query));
    assertEquals(state, error.getSQLState());
  }

  static String query() {
    return "select * from schubert.maintenance_read_inbox_summary('" + RUN + "','" + TIME + "')";
  }

  static void insert(Connection c, String at, long t, long d, long p, boolean end)
      throws SQLException {
    sql(
        c,
        "insert into schubert.inbox_inspection_progress(run_id,cutoff,inspected_count,deleted_count,protected_count,after_message_id,completed_at) values('"
            + RUN
            + "','"
            + at
            + "',"
            + t
            + ","
            + d
            + ","
            + p
            + ","
            + (t == 0 ? "null" : "'00000000-0000-0000-0000-000000000002'")
            + ","
            + (end ? "'2000-01-01'" : "null")
            + ")");
  }

  static List<Object> read(Connection c, UUID run, String literal) throws SQLException {
    try (var s = c.prepareStatement("select * from schubert.maintenance_read_inbox_summary(?,?)")) {
      s.setObject(1, run);
      s.setObject(2, Instant.parse(literal).atOffset(ZoneOffset.UTC));
      try (var r = s.executeQuery()) {
        if (!r.next()) return List.of();
        List<Object> result =
            List.of(
                r.getObject("inspected_count", Long.class),
                r.getObject("deleted_count", Long.class),
                r.getObject("protected_count", Long.class),
                r.getObject("complete", Boolean.class));
        assertFalse(r.next());
        return result;
      }
    }
  }
}
