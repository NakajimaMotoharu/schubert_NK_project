package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
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
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
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

/** NK-DAT-001; DAT-009/OPS-009/UI251/SS331 3.12/332/343; SSC055/056/PG159/160; DB241..250. */
final class RunReferenceBoundaryTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static String url;
  static final UUID RUN = UUID.fromString("12345678-9abc-def0-8123-456789abcdef");
  static final UUID OTHER = UUID.fromString("11111111-2222-3333-4444-555555555555");
  static final Instant TIME = Instant.parse("2026-09-12T15:00:00.123456Z");
  static final String SIGNATURE = "schubert.maintenance_read_run_references(uuid,timestamptz)";
  static final String[] TABLES = {
    "batch_runs", "inbox_inspection_progress", "log_cleanup_progress"
  };
  static final String[] FLAGS = {
    "has_batch_history", "has_inbox_progress", "has_log_progress", "identity_consistent"
  };
  static int sequence;

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
      clear(c);
    }
  }

  @Test
  void referenceCombinations() throws Exception {
    StringBuilder actual = new StringBuilder();
    try (var c = locked();
        var admin = db.admin()) {
      for (int mask = 0; mask < 8; mask++) {
        clear(admin);
        for (int bit = 0; bit < 3; bit++) {
          insert(admin, bit, OTHER, TIME);
          if ((mask & (1 << bit)) != 0) insert(admin, bit, RUN, TIME);
        }
        List<Boolean> expected = List.of((mask & 1) != 0, (mask & 2) != 0, (mask & 4) != 0, true);
        List<Boolean> observed = read(c, RUN, TIME);
        assertEquals(expected, observed);
        actual.append(mask).append(':').append(observed).append('\n');
      }
      for (String status : List.of("RUNNING", "SUCCESS", "WARNING", "FAILED", "SKIPPED")) {
        sql(
            admin,
            "update schubert.batch_runs set status='"
                + status
                + "',started_at='2000-01-01',ended_at='2000-01-02'");
        assertEquals(List.of(true, true, true, true), read(c, RUN, TIME));
      }
      sql(admin, "update schubert.inbox_inspection_progress set completed_at='2000-01-01'");
      sql(admin, "update schubert.log_cleanup_progress set completed_at='2000-01-01'");
      assertEquals(List.of(true, true, true, true), read(c, RUN, TIME));
    }
    Path target = Path.of("target/run-reference-traces");
    Files.createDirectories(target);
    Files.writeString(
        target.resolve("PT-DB-INBOX-241-combinations.txt"), actual, StandardCharsets.US_ASCII);
  }

  @Test
  void identityConsistency() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      for (int bit = 0; bit < 3; bit++) insert(admin, bit, RUN, TIME);
      assertEquals(List.of(true, true, true, true), read(c, RUN, TIME));
      for (int bit = 0; bit < 3; bit++) {
        // Reset the one changed column after this committed mutation.
        sql(
            admin,
            bit == 0
                ? "update schubert.batch_runs set business_date='2026-09-12' where run_id='"
                    + RUN
                    + "'"
                : "update schubert."
                    + TABLES[bit]
                    + " set cutoff=cutoff+interval '1 microsecond' where run_id='"
                    + RUN
                    + "'");
        assertEquals(List.of(true, true, true, false), read(c, RUN, TIME));
        sql(
            admin,
            bit == 0
                ? "update schubert.batch_runs set business_date=\'2026-09-13\'"
                : "update schubert."
                    + TABLES[bit]
                    + " set cutoff=cutoff-interval \'1 microsecond\'");
      }
    }
  }

  @Test
  void temporalAndNullBoundaries() throws Exception {
    try (var c = locked()) {
      // BUG165 diagnostic: independently observe SQL literal admission before changing fixture.
      sql(c, "set timezone='Asia/Tokyo'");
      assertEquals(
          "9999-12-31 15:00:00",
          scalar(c, "select ('10000-01-01'::timestamptz at time zone 'UTC')::text"));
      for (String value :
          List.of(
              "0001-01-01T00:00:00Z",
              "9999-12-31T23:59:59.999999Z",
              "2026-09-12T14:59:59.999999Z",
              "2026-09-12T15:00:00Z")) {
        Instant instant = Instant.parse(value);
        assertEquals(List.of(false, false, false, true), read(c, RUN, instant));
        // Literal SQL is independent of JDBC timestamp formatting, including pre-1582 dates.
        try (var admin = db.admin()) {
          sql(
              admin,
              "insert into schubert.inbox_inspection_progress(run_id,cutoff) values('"
                  + RUN
                  + "','"
                  + value
                  + "')");
          assertEquals(List.of(false, true, false, true), read(c, RUN, instant), value);
          sql(admin, "delete from schubert.inbox_inspection_progress");
        }
      }
      for (String at :
          List.of(
              "null",
              "'infinity'",
              "'-infinity'",
              "'0001-01-01 00:00:00+00 BC'",
              "'10000-01-01 00:00:00+00'")) {
        reject(
            c,
            "select * from schubert.maintenance_read_run_references('" + RUN + "'," + at + ")",
            "22023");
      }
      reject(
          c, "select * from schubert.maintenance_read_run_references(null,'2026-09-13')", "22023");
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        sql(c, "set timezone='" + zone + "'");
        assertEquals(List.of(false, false, false, true), read(c, RUN, TIME));
        reject(
            c,
            "select * from schubert.maintenance_read_run_references('"
                + RUN
                + "','10000-01-01 00:00:00+00')",
            "22023");
      }
    }
    try (var admin = db.admin();
        var c = locked()) {
      insert(admin, 0, RUN, Instant.parse("9999-12-31T23:59:59.999999Z"));
      assertEquals(
          "10000-01-01", scalar(admin, "select business_date::text from schubert.batch_runs"));
      assertEquals(
          List.of(true, false, false, true),
          read(c, RUN, Instant.parse("9999-12-31T23:59:59.999999Z")));
    }
  }

  /** PT-DB-INBOX-249; handwritten SQL literals are independent of the JDBC bind/read path. */
  @Test
  void jdbcUtcVectors() throws Exception {
    List<String> vectors =
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
            "9999-12-31T23:59:59.999999Z");
    try (var c = db.admin()) {
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        sql(c, "set timezone='" + zone + "'");
        for (String literal : vectors) {
          Instant expected = Instant.parse(literal);
          // Equality and epoch are evaluated by SQL against the literal, not a JDBC round trip.
          try (var p =
              c.prepareStatement(
                  "select ?::timestamptz = timestamptz '"
                      + literal
                      + "' as equal,"
                      + "extract(epoch from timestamptz '"
                      + literal
                      + "') as epoch")) {
            p.setObject(1, expected.atOffset(ZoneOffset.UTC));
            try (var row = p.executeQuery()) {
              assertTrue(row.next());
              assertTrue(row.getBoolean("equal"), zone + "/" + literal);
              assertEquals(
                  0,
                  new java.math.BigDecimal(expected.getEpochSecond())
                      .add(java.math.BigDecimal.valueOf(expected.getNano(), 9))
                      .compareTo(row.getBigDecimal("epoch")));
              assertFalse(row.next());
            }
          }
          // Projection starts from SQL literal only: a bind defect cannot cancel a read defect.
          try (var p = c.createStatement();
              var row =
                  p.executeQuery(
                      "select timestamptz '"
                          + literal
                          + "' as at,"
                          + "null::timestamptz as absent")) {
            assertTrue(row.next());
            assertEquals(expected, row.getObject("at", OffsetDateTime.class).toInstant());
            assertNull(row.getObject("absent", OffsetDateTime.class));
            assertFalse(row.next());
          }
        }
        assertEquals(
            "-62135596800.000000",
            scalar(c, "select extract(epoch from timestamptz '0001-01-01 00:00:00+00')::text"));
      }
    }
  }

  /**
   * PT-DB-INBOX-250; fixed target inventory plus actual per-program regressions, not search alone.
   */
  @Test
  void productionUtcBoundaryInventory() throws Exception {
    Path source = Path.of(System.getProperty("nk.pt.repository")).resolve("src");
    List<String> targets =
        List.of(
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserAuditWriter.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserCommandService.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserQueryAuditWriter.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/admin/UserRequestAuditWriter.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/log/LogQueryAuditWriter.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/JdbcInboxCoordinator.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/WebLogIngestService.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InboxCleanup.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/LogQueryRepository.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/persistence/UserQueryRepository.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthSessionRevocationService.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthSessionService.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationContextVerifier.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptRepository.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAuditWriter.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginReplayService.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LogoutReplayService.java",
            "schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/SessionAuditWriter.java",
            "schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupRepository.java",
            "schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/RunReferenceRepository.java",
            "schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebLogOutboxRepository.java",
            "schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/session/JdbcWebSessionStore.java");
    assertEquals(23, new HashSet<>(targets).size());
    for (String target : targets) {
      String code = Files.readString(source.resolve(target));
      assertTrue(code.contains("PG-D-160/SSC056/BUG167/YKT128"), target);
      assertTrue(code.contains("ZoneOffset.UTC") || code.contains("OffsetDateTime.class"), target);
    }
    try (var paths = Files.walk(source)) {
      for (Path path :
          paths
              .filter(p -> p.toString().contains("/src/main/java/"))
              .filter(p -> p.toString().endsWith(".java"))
              .toList()) {
        String code = Files.readString(path);
        for (String forbidden :
            List.of(
                "java.sql.Timestamp",
                "Timestamp.from(",
                ".setTimestamp(",
                ".getTimestamp(",
                "java.sql.Date",
                ".setDate(",
                ".getDate(")) assertFalse(code.contains(forbidden), path + ":" + forbidden);
      }
    }
  }

  @Test
  void lockOwnership() throws Exception {
    try (var c = open("schubert_batch")) {
      reject(c, query(), "55000");
      assertEquals(
          "0",
          scalar(
              c,
              "select count(*) from pg_locks where pid=pg_backend_pid() and locktype='advisory'"));
      sql(c, "select pg_advisory_lock_shared(71419602)");
      reject(c, query(), "55000");
      assertEquals("t", scalar(c, "select pg_advisory_unlock_shared(71419602)"));
      sql(c, "select pg_advisory_lock(0,71419602)");
      reject(c, query(), "55000");
      assertEquals("t", scalar(c, "select pg_advisory_unlock(0,71419602)"));
      sql(c, "select pg_advisory_lock(71419602)");
      assertEquals(List.of(false, false, false, true), read(c, RUN, TIME));
      assertEquals("t", scalar(c, "select pg_advisory_unlock(71419602)"));
      assertEquals("f", scalar(c, "select pg_advisory_unlock(71419602)"));
      c.setAutoCommit(false);
      sql(c, "select pg_advisory_xact_lock(71419602)");
      assertEquals(List.of(false, false, false, true), read(c, RUN, TIME));
      c.rollback();
      c.setAutoCommit(true);
      reject(c, query(), "55000");
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
      for (String table : List.of("inbox_inspection_progress", "log_cleanup_progress"))
        assertEquals(
            "false",
            scalar(
                c,
                "select has_table_privilege('schubert_batch','schubert."
                    + table
                    + "','SELECT')::text"));
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
  void transactionVisibility() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      c.setAutoCommit(false);
      insert(c, 0, RUN, TIME);
      assertEquals(List.of(true, false, false, true), read(c, RUN, TIME));
      c.rollback();
      assertEquals(List.of(false, false, false, true), read(c, RUN, TIME));
      admin.setAutoCommit(false);
      insert(admin, 1, RUN, TIME);
      assertEquals(List.of(false, false, false, true), read(c, RUN, TIME));
      admin.commit();
      assertEquals(List.of(false, true, false, true), read(c, RUN, TIME));
      admin.setAutoCommit(true);
      sql(admin, "delete from schubert.inbox_inspection_progress");
      assertEquals(List.of(false, false, false, true), read(c, RUN, TIME));
      c.rollback();
    }
  }

  @Test
  void concurrentOwnership() throws Exception {
    try (var first = locked();
        var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      assertEquals(
          "55000",
          executor
              .submit(
                  () -> {
                    try (var other = open("schubert_batch")) {
                      assertEquals("f", scalar(other, "select pg_try_advisory_lock(71419602)"));
                      return assertThrows(SQLException.class, () -> read(other, OTHER, TIME))
                          .getSQLState();
                    }
                  })
              .get(10, TimeUnit.SECONDS));
      assertEquals("t", scalar(first, "select pg_advisory_unlock(71419602)"));
      assertEquals(
          List.of(false, false, false, true),
          executor
              .submit(
                  () -> {
                    try (var other = locked()) {
                      return read(other, OTHER, TIME);
                    }
                  })
              .get(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void migrationAndReadOnlyHistory() throws Exception {
    try (var c = locked();
        var admin = db.admin()) {
      for (int bit = 0; bit < 3; bit++) insert(admin, bit, RUN, TIME);
      List<String> before = snapshot(admin);
      for (int i = 0; i < 5; i++) assertEquals(List.of(true, true, true, true), read(c, RUN, TIME));
      assertEquals(before, snapshot(admin));
      assertEquals(
          MigrationInventory.CSV,
          scalar(
              admin,
              "select string_agg(version,',' order by installed_rank) from schubert_meta.flyway_schema_history where version is not null and success"));
    }
    Path migrations =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db/migration");
    // Independently frozen at certified source364ea265, before V018 existed.
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
            "c412685a319defa1cb4f91846c02d69dbbc18457da5feb9d66266d2aec3446ce");
    List<Path> files;
    try (var stream = Files.list(migrations)) {
      files = stream.sorted().toList();
    }
    assertEquals(MigrationInventory.VERSIONS.size(), files.size());
    for (int i = 0; i < 17; i++) {
      assertTrue(files.get(i).getFileName().toString().startsWith("V%03d__".formatted(i + 1)));
      assertEquals(
          hashes.get(i),
          HexFormat.of()
              .formatHex(
                  MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(files.get(i)))));
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
    List<String> data = new ArrayList<>();
    for (String table : TABLES)
      data.add(
          scalar(
              c,
              "select coalesce(string_agg(row_to_json(t)::text,'|' order by run_id),'') from schubert."
                  + table
                  + " t"));
    return data;
  }

  static void clear(Connection c) throws SQLException {
    for (String table : TABLES) sql(c, "delete from schubert." + table);
  }

  static void insert(Connection c, int bit, UUID run, Instant cutoff) throws SQLException {
    if (bit == 0) {
      try (var s =
          c.prepareStatement(
              "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,status) values(?,?,?,1,'2000-01-01','RUNNING')")) {
        s.setObject(1, run);
        s.setObject(2, cutoff.atZone(ZoneId.of("Asia/Tokyo")).toLocalDate());
        s.setString(3, "PUBLIC_" + (++sequence));
        s.executeUpdate();
      }
    } else
      try (var s =
          c.prepareStatement(
              "insert into schubert." + TABLES[bit] + "(run_id,cutoff) values(?,?)")) {
        s.setObject(1, run);
        s.setObject(2, cutoff.atOffset(ZoneOffset.UTC));
        s.executeUpdate();
      }
  }

  static Connection open(String role) throws SQLException {
    return DriverManager.getConnection(url, role, "");
  }

  static Connection locked() throws SQLException {
    var c = open("schubert_batch");
    sql(c, "select pg_advisory_lock(71419602)");
    return c;
  }

  static List<Boolean> read(Connection c, UUID run, Instant at) throws SQLException {
    try (var s =
        c.prepareStatement("select * from schubert.maintenance_read_run_references(?,?)")) {
      s.setObject(1, run);
      s.setObject(2, at.atOffset(ZoneOffset.UTC));
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        List<Boolean> result = new ArrayList<>();
        for (String flag : FLAGS) {
          Boolean value = r.getObject(flag, Boolean.class);
          assertNotNull(value);
          result.add(value);
        }
        assertFalse(r.next());
        return List.copyOf(result);
      }
    }
  }

  static String query() {
    return "select * from schubert.maintenance_read_run_references('"
        + RUN
        + "','2026-09-12 15:00:00.123456+00')";
  }

  static void reject(Connection c, String sql, String state) {
    assertEquals(state, assertThrows(SQLException.class, () -> sql(c, sql), sql).getSQLState());
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
}
