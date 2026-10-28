package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import javax.xml.parsers.DocumentBuilderFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001; UI251/SS311/331/332/341; PG-D-137; PT-BAT-001..017. */
final class CleanupRepositoryTest {
  private static final String FIXTURE_TRUE_18D10C7D = "true";
  private static final String FIXTURE_TARGET_COUNT_5B6567D4 = "target_count";
  private static final String FIXTURE_DELETED_COUNT_EA6A9020 = "deleted_count";
  private static final String FIXTURE_RESULTCLOSE_4AFF6AC1 = "resultClose";
  private static final String FIXTURE_STATEMENTCLOSE_D5A13A63 = "statementClose";
  private static final String FIXTURE_MAINTENANCE_READ_LOG_CLEANUP_PROGRESS_75EF2AB2 =
      "maintenance_read_log_cleanup_progress";
  private static final String FIXTURE_MAINTENANCE_CLEANUP_LOGS_01FD6149 =
      "maintenance_cleanup_logs";
  @TempDir static Path root;
  private static BatchDatabaseFixture db;
  private static final BatchRun RUN =
      new BatchRun(new UUID(0, 94), Instant.parse("2026-09-17T00:00:00Z"));
  private static final CleanupCounts ZERO = new CleanupCounts(0, 0, 0);

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
      sql(c, "delete from schubert.log_cleanup_progress");
      sql(c, "delete from schubert.app_logs");
      sql(c, "delete from schubert.batch_runs");
      for (String step : List.of("BACKUP_DB", "BACKUP_CONFIG"))
        sql(
            c,
            "insert into"
                + " schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,status)"
                + " values('"
                + RUN.id()
                + "','2026-09-17','"
                + step
                + "',1,'2026-09-17 00:00:00+00','2026-09-17 00:00:00+00','SUCCESS')");
    }
  }

  @Test
  void runIdentityBoundaries() {
    assertEquals(new UUID(0, 94), RUN.id());
    assertEquals(Instant.parse("2026-09-17T00:00:00Z"), RUN.cutoff());
    for (String at : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z"))
      assertEquals(Instant.parse(at), new BatchRun(RUN.id(), Instant.parse(at)).cutoff());
    for (String at :
        List.of(
            "0000-12-31T23:59:59.999999Z",
            "+10000-01-01T00:00:00Z",
            "2026-09-17T00:00:00.000000001Z"))
      assertThrows(IllegalArgumentException.class, () -> new BatchRun(RUN.id(), Instant.parse(at)));
    assertThrows(NullPointerException.class, () -> new BatchRun(null, RUN.cutoff()));
    assertThrows(NullPointerException.class, () -> new BatchRun(RUN.id(), null));
    assertEquals("BatchRun[identity/cutoff=<redacted>]", RUN.toString());
  }

  @Test
  void countInvariants() {
    var max = new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0);
    assertEquals(Long.MAX_VALUE, max.target());
    assertEquals(Long.MAX_VALUE, max.deleted());
    assertEquals(0, max.skipped());
    assertEquals(Long.MAX_VALUE, new CleanupCounts(Long.MAX_VALUE, 0, Long.MAX_VALUE).skipped());
    for (long[] values :
        List.of(
            new long[] {-1, 0, 0},
            new long[] {0, -1, 0},
            new long[] {0, 1, 0},
            new long[] {1, 0, -1},
            new long[] {1, 0, 0},
            new long[] {Long.MAX_VALUE, 1, Long.MAX_VALUE}))
      assertThrows(
          IllegalArgumentException.class, () -> new CleanupCounts(values[0], values[1], values[2]));
  }

  @Test
  void cleanupAllowlist() throws Exception {
    Map<String, String> names =
        Map.of(
            "NOTIFICATIONS",
            "notifications",
            "QUESTIONS",
            "questions",
            "SESSIONS",
            "sessions",
            "OUTBOX",
            "message_stores",
            "LOGS",
            "logs",
            "WEB_RECEIPTS",
            "web_receipt_references",
            "BATCH_RUNS",
            "batch_runs",
            "INBOX_PROGRESS",
            "inbox_progress",
            "LOG_PROGRESS",
            "log_progress");
    assertEquals(
        names.keySet(),
        new HashSet<>(Arrays.stream(CleanupKind.values()).map(Enum::name).toList()));
    for (var kind : CleanupKind.values()) {
      assertEquals("schubert.maintenance_cleanup_" + names.get(kind.name()), kind.function());
      assertEquals(kind == CleanupKind.LOGS ? 10000 : 1000, kind.maximumRows());
      try (var c = transaction()) {
        var probe = new BatchJdbcProbe();
        assertEquals(ZERO, new CleanupRepository(probe.wrap(c)).execute(RUN, kind, 1).counts());
        assertEquals(
            "select target_count,deleted_count,skipped_count,reason_code from"
                + " schubert.maintenance_cleanup_"
                + names.get(kind.name())
                + "(?,?,?)",
            probe.lastSql);
        c.rollback();
      }
    }
  }

  @Test
  void rejectionAndProgressContracts() {
    assertEquals(
        Set.of("OK", "LOCK_BUSY", "BACKUP_GATE"),
        new HashSet<>(Arrays.stream(CleanupReason.values()).map(Enum::name).toList()));
    for (var reason : CleanupReason.values()) {
      var result = new CleanupChunk(ZERO, reason);
      assertEquals(ZERO, result.counts());
      assertEquals(reason, result.reason());
    }
    for (var reason : List.of(CleanupReason.LOCK_BUSY, CleanupReason.BACKUP_GATE))
      assertThrows(
          IllegalArgumentException.class,
          () -> new CleanupChunk(new CleanupCounts(1, 1, 0), reason));
    assertEquals(
        1, new CleanupChunk(new CleanupCounts(1, 1, 0), CleanupReason.OK).counts().target());
    assertThrows(NullPointerException.class, () -> new CleanupChunk(null, CleanupReason.OK));
    assertThrows(NullPointerException.class, () -> new CleanupChunk(ZERO, null));
    assertThrows(NullPointerException.class, () -> new LogCleanupProgress(null, ZERO, false));
    assertThrows(NullPointerException.class, () -> new LogCleanupProgress(RUN, null, false));
    var progress = new LogCleanupProgress(RUN, ZERO, false);
    assertEquals(RUN, progress.run());
    assertEquals(ZERO, progress.counts());
    assertFalse(progress.complete());
  }

  @Test
  void emptyCleanupAndExplicitTransaction() throws Exception {
    assertThrows(NullPointerException.class, () -> new CleanupRepository(null));
    try (var c = db.open("schubert_batch")) {
      var repository = new CleanupRepository(c);
      redacted(() -> repository.execute(RUN, CleanupKind.LOGS, 1));
      redacted(() -> repository.readLogProgress(RUN));
      assertTrue(c.getAutoCommit());
      c.setAutoCommit(false);
      // The parent's session lock and SQL transaction lock share this exact connection.
      assertEquals(FIXTURE_TRUE_18D10C7D, scalar(c, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals(new LogCleanupProgress(RUN, ZERO, false), repository.readLogProgress(RUN));
      for (var kind : CleanupKind.values())
        assertEquals(new CleanupChunk(ZERO, CleanupReason.OK), repository.execute(RUN, kind, 1));
      assertTrue(repository.readLogProgress(RUN).complete());
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertEquals(FIXTURE_TRUE_18D10C7D, scalar(c, "select pg_advisory_unlock(71419602)::text"));
      c.rollback();
    }
  }

  @Test
  void heldLogsAndDurableRead() throws Exception {
    logs();
    try (var c = transaction();
        var admin = db.admin()) {
      var r = new CleanupRepository(c);
      assertEquals(new CleanupCounts(2, 0, 2), r.execute(RUN, CleanupKind.LOGS, 2).counts());
      assertEquals("0", scalar(admin, "select count(*) from schubert.log_cleanup_progress"));
      c.commit();
      assertEquals(new CleanupCounts(2, 0, 2), r.readLogProgress(RUN).counts());
      c.commit();
      assertEquals(new CleanupCounts(1, 1, 0), r.execute(RUN, CleanupKind.LOGS, 2).counts());
      assertEquals("3", scalar(admin, "select count(*) from schubert.app_logs"));
      c.commit();
      assertEquals("2", scalar(admin, "select count(*) from schubert.app_logs"));
      assertEquals(ZERO, r.execute(RUN, CleanupKind.LOGS, 2).counts());
      var progress = r.readLogProgress(RUN);
      assertTrue(progress.complete());
      assertEquals(new CleanupCounts(3, 1, 2), progress.counts());
      c.commit();
    }
  }

  @Test
  void rollbackSavepointAndResume() throws Exception {
    logs();
    try (var c = transaction()) {
      var r = new CleanupRepository(c);
      var save = c.setSavepoint();
      assertEquals(new CleanupCounts(3, 1, 2), r.execute(RUN, CleanupKind.LOGS, 10000).counts());
      c.rollback(save);
      assertEquals(ZERO, r.readLogProgress(RUN).counts());
      assertEquals(new CleanupCounts(3, 1, 2), r.execute(RUN, CleanupKind.LOGS, 10000).counts());
      c.rollback();
    }
    try (var c = transaction()) {
      var r = new CleanupRepository(c);
      assertEquals(new CleanupCounts(3, 1, 2), r.execute(RUN, CleanupKind.LOGS, 10000).counts());
      c.commit();
    }
    try (var c = transaction()) {
      var r = new CleanupRepository(c);
      assertEquals(new CleanupCounts(3, 1, 2), r.readLogProgress(RUN).counts());
      assertEquals(ZERO, r.execute(RUN, CleanupKind.LOGS, 10000).counts());
      c.commit();
    }
  }

  @Test
  void backupAndAdvisoryRejection() throws Exception {
    try (var c = transaction();
        var admin = db.admin()) {
      sql(admin, "update schubert.batch_runs set status='FAILED' where step='BACKUP_CONFIG'");
      var r = new CleanupRepository(c);
      for (var kind : CleanupKind.values())
        assertEquals(new CleanupChunk(ZERO, CleanupReason.BACKUP_GATE), r.execute(RUN, kind, 1));
      redacted(() -> r.readLogProgress(RUN));
      c.rollback();
      sql(admin, "update schubert.batch_runs set status='SUCCESS'");
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(admin, "select pg_try_advisory_lock(71419602)::text"));
      for (var kind : CleanupKind.values())
        assertEquals(new CleanupChunk(ZERO, CleanupReason.LOCK_BUSY), r.execute(RUN, kind, 1));
      redacted(() -> r.readLogProgress(RUN));
      c.rollback();
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(admin, "select pg_advisory_unlock(71419602)::text"));
      assertEquals("0", scalar(admin, "select count(*) from schubert.log_cleanup_progress"));
    }
  }

  @Test
  void exactLimitsAndNullInputs() throws Exception {
    try (var c = transaction()) {
      var p = new BatchJdbcProbe();
      var r = new CleanupRepository(p.wrap(c));
      assertThrows(NullPointerException.class, () -> r.execute(null, CleanupKind.LOGS, 1));
      assertThrows(NullPointerException.class, () -> r.execute(RUN, null, 1));
      assertThrows(NullPointerException.class, () -> r.readLogProgress(null));
      for (var kind : CleanupKind.values())
        for (int limit :
            new int[] {0, -1, Integer.MIN_VALUE, Integer.MAX_VALUE, kind.maximumRows() + 1})
          assertThrows(IllegalArgumentException.class, () -> r.execute(RUN, kind, limit));
      assertEquals(0, p.selectedStatements);
      for (var kind : CleanupKind.values()) {
        assertEquals(ZERO, r.execute(RUN, kind, 1).counts());
        c.rollback();
        assertEquals(ZERO, r.execute(RUN, kind, kind.maximumRows()).counts());
        c.rollback();
      }
    }
  }

  @Test
  void rowProjectionFailures() throws Exception {
    for (String column :
        List.of(
            FIXTURE_TARGET_COUNT_5B6567D4,
            FIXTURE_DELETED_COUNT_EA6A9020,
            "skipped_count",
            "reason_code")) {
      var p = new BatchJdbcProbe();
      p.columns.put(column, null);
      rejectProjection(p, false);
    }
    for (String reason : List.of("", "ok", "UNKNOWN")) {
      var p = new BatchJdbcProbe();
      p.columns.put("reason_code", reason);
      rejectProjection(p, false);
    }
    for (String column :
        List.of(FIXTURE_TARGET_COUNT_5B6567D4, FIXTURE_DELETED_COUNT_EA6A9020, "skipped_count")) {
      var p = new BatchJdbcProbe();
      p.columns.put(column, -1L);
      rejectProjection(p, false);
    }
    var large = new BatchJdbcProbe();
    large.columns.put(FIXTURE_TARGET_COUNT_5B6567D4, 2L);
    large.columns.put(FIXTURE_DELETED_COUNT_EA6A9020, 2L);
    rejectProjection(large, false);
    var rejected = new BatchJdbcProbe();
    rejected.columns.put(FIXTURE_TARGET_COUNT_5B6567D4, 1L);
    rejected.columns.put(FIXTURE_DELETED_COUNT_EA6A9020, 1L);
    rejected.columns.put("reason_code", "LOCK_BUSY");
    rejectProjection(rejected, false);
    var empty = new BatchJdbcProbe();
    empty.empty = true;
    rejectProjection(empty, false);
    var duplicate = new BatchJdbcProbe();
    duplicate.duplicate = true;
    rejectProjection(duplicate, false);
  }

  @Test
  void progressProjectionFailures() throws Exception {
    for (String column :
        List.of(
            FIXTURE_TARGET_COUNT_5B6567D4,
            FIXTURE_DELETED_COUNT_EA6A9020,
            "skipped_count",
            "complete")) {
      var p = new BatchJdbcProbe();
      p.columns.put(column, null);
      rejectProjection(p, true);
    }
    var negative = new BatchJdbcProbe();
    negative.columns.put(FIXTURE_TARGET_COUNT_5B6567D4, -1L);
    rejectProjection(negative, true);
    var empty = new BatchJdbcProbe();
    empty.empty = true;
    rejectProjection(empty, true);
    var duplicate = new BatchJdbcProbe();
    duplicate.duplicate = true;
    rejectProjection(duplicate, true);
  }

  @Test
  void jdbcFailuresRemainRedacted() throws Exception {
    resourceCompounds();
    assertAll(
        () -> resourceRed(false, false),
        () -> resourceRed(false, true),
        () -> resourceRed(true, false),
        () -> resourceRed(true, true));
    for (boolean progress : List.of(false, true)) {
      for (String fault :
          List.of(
              "getAutoCommit",
              "prepareStatement",
              "setObject",
              "setObject#2",
              "executeQuery",
              "next",
              "getObject",
              FIXTURE_RESULTCLOSE_4AFF6AC1,
              FIXTURE_STATEMENTCLOSE_D5A13A63)) {
        var p = new BatchJdbcProbe();
        p.fault = fault;
        rejectProjection(p, progress);
      }
    }
    for (String fault : List.of("setInt", "getString")) {
      var p = new BatchJdbcProbe();
      p.fault = fault;
      rejectProjection(p, false);
    }
  }

  @Test
  void roleIsolationAndNoInboxBypass() throws Exception {
    for (String role :
        List.of(
            "schubert_app",
            "schubert_web_session",
            "schubert_backup",
            "schubert_inbox_inspector",
            "schubert_ops_ro")) {
      try (var c = db.open(role)) {
        c.setAutoCommit(false);
        var r = new CleanupRepository(c);
        for (var kind : CleanupKind.values()) {
          redacted(() -> r.execute(RUN, kind, 1));
          c.rollback();
        }
        redacted(() -> r.readLogProgress(RUN));
        c.rollback();
      }
    }
    try (var c = transaction();
        var admin = db.admin()) {
      // Existing PT065 tests 96 actual Inbox rows; additionally reject any current SQL reference.
      assertEquals(
          "false",
          scalar(
              admin,
              "select"
                  + " (pg_get_functiondef('schubert.maintenance_cleanup_message_stores(uuid,timestamptz,integer)'::regprocedure)"
                  + " like '%request_inbox%')::text"));
      assertEquals(ZERO, new CleanupRepository(c).execute(RUN, CleanupKind.OUTBOX, 1).counts());
      c.rollback();
      assertEquals(
          "false",
          scalar(
              admin,
              "select"
                  + " has_table_privilege('schubert_batch','schubert.request_inbox','DELETE')::text"));
    }
  }

  @Test
  void timezoneAndCutoffIdentity() throws Exception {
    for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
      try (var c = transaction();
          var admin = db.admin()) {
        sql(c, "set timezone='" + zone + "'");
        var r = new CleanupRepository(c);
        assertEquals(ZERO, r.execute(RUN, CleanupKind.LOGS, 1).counts());
        c.commit();
        assertEquals(
            "1789603200.000000",
            scalar(
                admin,
                "select extract(epoch from cutoff)::text from schubert.log_cleanup_progress"));
        var wrong = new BatchRun(RUN.id(), RUN.cutoff().plusSeconds(1));
        redacted(() -> r.execute(wrong, CleanupKind.LOGS, 1));
        c.rollback();
        redacted(() -> r.readLogProgress(wrong));
        c.rollback();
        assertEquals(RUN, r.readLogProgress(RUN).run());
        c.rollback();
      }
    }
  }

  @Test
  void lockedLogsDoNotAdvance() throws Exception {
    logs();
    try (var c = transaction();
        var locked = db.admin()) {
      locked.setAutoCommit(false);
      assertEquals("1", scalar(locked, "select id from schubert.app_logs where id=1 for update"));
      var r = new CleanupRepository(c);
      assertEquals(
          new CleanupChunk(ZERO, CleanupReason.LOCK_BUSY), r.execute(RUN, CleanupKind.LOGS, 10000));
      c.commit();
      assertEquals("0", scalar(locked, "select count(*) from schubert.log_cleanup_progress"));
      locked.rollback();
      assertEquals(new CleanupCounts(3, 1, 2), r.execute(RUN, CleanupKind.LOGS, 10000).counts());
      c.commit();
    }
  }

  @Test
  void retentionAndResourceOwnership() throws Exception {
    try (var admin = db.admin()) {
      sql(
          admin,
          "insert into schubert.app_logs(id,logged_at,service,category,level,action,message)"
              + " values(1,'2026-06-18"
              + " 23:59:59.999999+00','API','SECURITY','INFO','PUBLIC_TEST','public"
              + " fixture'),(2,'2026-06-19"
              + " 00:00:00+00','API','SECURITY','INFO','PUBLIC_TEST','public fixture')");
    }
    try (var c = transaction();
        var admin = db.admin()) {
      var p = new BatchJdbcProbe();
      var r = new CleanupRepository(p.wrap(c));
      assertEquals(new CleanupCounts(1, 1, 0), r.execute(RUN, CleanupKind.LOGS, 10000).counts());
      assertFalse(r.readLogProgress(RUN).complete());
      assertEquals(0, p.commits);
      assertEquals(0, p.rollbacks);
      assertEquals(0, p.closes);
      assertEquals(0, p.saves);
      assertEquals(0, p.autoChanges);
      assertEquals("2", scalar(admin, "select count(*) from schubert.app_logs"));
      c.commit();
      assertEquals("2", scalar(admin, "select string_agg(id::text,',') from schubert.app_logs"));
    }
  }

  @Test
  void moduleDependencyBoundary() throws Exception {
    var repo = Path.of(System.getProperty("nk.pt.repository"));
    // SSC098/BUG305: literal parent pins; module-local shared-version overrides are forbidden.
    var parent =
        DocumentBuilderFactory.newInstance()
            .newDocumentBuilder()
            .parse(repo.resolve("pom.xml").toFile());
    var property = parent.getElementsByTagName("jspecify.version");
    assertEquals(1, property.getLength());
    assertEquals("1.0.1", property.item(0).getTextContent());
    var pins = new HashMap<String, String>();
    var managed = parent.getElementsByTagName("dependency");
    for (int i = 0; i < managed.getLength(); i++) {
      var dependency = (org.w3c.dom.Element) managed.item(i);
      String coordinate =
          dependency.getElementsByTagName("groupId").item(0).getTextContent()
              + ":"
              + dependency.getElementsByTagName("artifactId").item(0).getTextContent();
      assertNull(
          pins.put(
              coordinate, dependency.getElementsByTagName("version").item(0).getTextContent()));
    }
    assertEquals(
        Map.of(
            "commons-logging:commons-logging",
            "1.4.0",
            "org.jspecify:jspecify",
            "${jspecify.version}",
            "org.slf4j:slf4j-api",
            "2.0.18"),
        pins);
    for (String module : List.of("protocol", "storage", "bootstrap", "api", "web", "batch")) {
      var child =
          DocumentBuilderFactory.newInstance()
              .newDocumentBuilder()
              .parse(repo.resolve("src/schubert-nk-" + module + "/pom.xml").toFile());
      assertEquals(0, child.getElementsByTagName("jspecify.version").getLength(), module);
    }
    var document =
        DocumentBuilderFactory.newInstance()
            .newDocumentBuilder()
            .parse(repo.resolve("src/schubert-nk-batch/pom.xml").toFile());
    var dependencies = document.getElementsByTagName("dependency");
    Set<String> runtime = new HashSet<>();
    for (int i = 0; i < dependencies.getLength(); i++) {
      var dependency = (org.w3c.dom.Element) dependencies.item(i);
      var scope = dependency.getElementsByTagName("scope");
      if (scope.getLength() == 0 || !scope.item(0).getTextContent().equals("test"))
        runtime.add(
            dependency.getElementsByTagName("groupId").item(0).getTextContent()
                + ":"
                + dependency.getElementsByTagName("artifactId").item(0).getTextContent());
    }
    // SS311 SSC088/BUG267: fixed bootstrap and root schema validation only, never API/Web/Protocol.
    assertEquals(
        Set.of(
            "org.jspecify:jspecify",
            "dev.codex.schubert:schubert-nk-storage",
            "dev.codex.schubert:schubert-nk-bootstrap",
            "org.flywaydb:flyway-core",
            "org.flywaydb:flyway-database-postgresql",
            "org.apache.artemis:artemis-jakarta-client",
            "org.postgresql:postgresql",
            "com.github.spotbugs:spotbugs-annotations"),
        runtime);
    // SSC084/088/095/096, BUG276/298: compatibility package is not artifact ownership.
    // Independent literal allowlist, corroborated by the actual Bootstrap source location.
    java.util.function.Predicate<String> allowedImport =
        name ->
            !name.matches("dev\\.codex\\.schubert\\.nk\\.(api|web|protocol)\\..*")
                || (Set.of(
                            "dev.codex.schubert.nk.api.file.InspectorCredentialLoader",
                            "dev.codex.schubert.nk.api.maintenance.InspectorDbCredential",
                            "dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission",
                            "dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfig",
                            "dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource",
                            "dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfig")
                        .contains(name)
                    && Files.isRegularFile(
                        repo.resolve(
                            "src/schubert-nk-bootstrap/src/main/java/"
                                + name.replace('.', '/')
                                + ".java")));
    assertTrue(allowedImport.test("dev.codex.schubert.nk.api.file.InspectorCredentialLoader"));
    assertTrue(allowedImport.test("dev.codex.schubert.nk.api.maintenance.InspectorDbCredential"));
    assertTrue(allowedImport.test("dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission"));
    assertTrue(allowedImport.test("dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfig"));
    // SSC142: pre-existing shared Bootstrap physical source, not an API artifact dependency.
    assertTrue(allowedImport.test("dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSource"));
    assertTrue(allowedImport.test("dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfig"));
    for (var forbidden :
        List.of(
            "dev.codex.schubert.nk.api.file.AssetResolver",
            "dev.codex.schubert.nk.api.file.InspectorCredentialLoaderMissing",
            "dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmissionMissing",
            "dev.codex.schubert.nk.api.bootstrap.ApiNonSecretConfigMissing",
            "dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseSourceMissing",
            "dev.codex.schubert.nk.api.bootstrap.ServiceDatabaseAdmission",
            "dev.codex.schubert.nk.web.bootstrap.WebNonSecretConfigMissing",
            "dev.codex.schubert.nk.web.bootstrap.*",
            "dev.codex.schubert.nk.api.bootstrap.*",
            "dev.codex.schubert.nk.api.file.*",
            "dev.codex.schubert.nk.web.LoginController",
            "dev.codex.schubert.nk.protocol.FixedLengthCodec")) {
      assertFalse(allowedImport.test(forbidden), forbidden);
    }
    var imports = java.util.regex.Pattern.compile("(?m)^import(?: static)? ([^;]+);");
    try (var files = Files.walk(repo.resolve("src/schubert-nk-batch/src/main/java"))) {
      for (var file : files.filter(p -> p.toString().endsWith(".java")).toList()) {
        var content = Files.readString(file);
        var matcher = imports.matcher(content);
        while (matcher.find()) {
          assertTrue(allowedImport.test(matcher.group(1)), file + ":" + matcher.group(1));
        }
      }
    }
  }

  private static void resourceCompounds() throws Exception {
    for (boolean progress : List.of(false, true)) {
      for (var sample : JdbcResourceCases.all()) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql =
            progress
                ? FIXTURE_MAINTENANCE_READ_LOG_CLEANUP_PROGRESS_75EF2AB2
                : FIXTURE_MAINTENANCE_CLEANUP_LOGS_01FD6149;
        var faults = new HashMap<String, Throwable>();
        sample.install(faults);
        faults.forEach((key, value) -> probe.thrown.put(resourceFaultName(key), value));
        try (var c = transaction()) {
          if (progress) new CleanupRepository(c).execute(RUN, CleanupKind.LOGS, 1);
          var repository = new CleanupRepository(probe.wrap(c));
          Runnable action =
              progress
                  ? () -> repository.readLogProgress(RUN)
                  : () -> repository.execute(RUN, CleanupKind.LOGS, 1);
          sample.verify(assertThrows(Throwable.class, action::run));
          assertEquals(sample.first() < 0 ? 1 : 2, probe.injected);
          assertEquals(1, probe.faultOccurrences.getOrDefault(FIXTURE_STATEMENTCLOSE_D5A13A63, 0));
          assertEquals(
              sample.first() >= 0 && sample.body().equals("statement.executeQuery") ? 0 : 1,
              probe.faultOccurrences.getOrDefault(FIXTURE_RESULTCLOSE_4AFF6AC1, 0));
          assertEquals(0, probe.liveRows);
          assertEquals(0, probe.liveStatements);
          assertEquals(0, probe.commits);
          assertEquals(0, probe.rollbacks);
          assertEquals(0, probe.closes);
          assertEquals(0, probe.autoChanges);
          assertFalse(c.isClosed());
          assertFalse(c.getAutoCommit());
          c.rollback();
        }
        try (var admin = db.admin()) {
          assertEquals("0", scalar(admin, "select count(*) from schubert.log_cleanup_progress"));
          assertEquals("0", scalar(admin, "select count(*) from schubert.app_logs"));
        }
      }
      for (boolean statement : List.of(false, true)) {
        var probe = new BatchJdbcProbe();
        probe.selectedSql =
            progress
                ? FIXTURE_MAINTENANCE_READ_LOG_CLEANUP_PROGRESS_75EF2AB2
                : FIXTURE_MAINTENANCE_CLEANUP_LOGS_01FD6149;
        probe.nullStatement = statement;
        probe.nullRows = !statement;
        try (var c = transaction()) {
          if (progress) new CleanupRepository(c).execute(RUN, CleanupKind.LOGS, 1);
          var repository = new CleanupRepository(probe.wrap(c));
          Runnable action =
              progress
                  ? () -> repository.readLogProgress(RUN)
                  : () -> repository.execute(RUN, CleanupKind.LOGS, 1);
          var failure = assertThrows(NullPointerException.class, action::run);
          assertEquals(statement ? "JDBC statement" : "JDBC result", failure.getMessage());
          assertEquals(0, probe.liveRows);
          assertEquals(0, probe.liveStatements);
          assertEquals(
              statement ? 0 : 1,
              probe.faultOccurrences.getOrDefault(FIXTURE_STATEMENTCLOSE_D5A13A63, 0));
          assertEquals(0, probe.faultOccurrences.getOrDefault(FIXTURE_RESULTCLOSE_4AFF6AC1, 0));
          assertEquals(0, probe.closes);
          c.rollback();
        }
      }
    }
  }

  private static String resourceFaultName(String name) {
    return switch (name) {
      case "row.next" -> "next";
      case "row.close" -> FIXTURE_RESULTCLOSE_4AFF6AC1;
      case "statement.executeQuery" -> "executeQuery";
      case "statement.close" -> FIXTURE_STATEMENTCLOSE_D5A13A63;
      default -> throw new AssertionError("unknown fixture boundary");
    };
  }

  private static void resourceRed(boolean progress, boolean same) throws Exception {
    var probe = new BatchJdbcProbe();
    probe.selectedSql =
        progress
            ? FIXTURE_MAINTENANCE_READ_LOG_CLEANUP_PROGRESS_75EF2AB2
            : FIXTURE_MAINTENANCE_CLEANUP_LOGS_01FD6149;
    Throwable failure =
        same
            ? new IllegalStateException("public same fixture")
            : new IllegalArgumentException("public provider argument fixture");
    probe.thrown.put(same ? "next" : "executeQuery", failure);
    if (same) probe.thrown.put(FIXTURE_RESULTCLOSE_4AFF6AC1, failure);
    try (var c = transaction()) {
      if (progress) new CleanupRepository(c).execute(RUN, CleanupKind.LOGS, 1);
      var repository = new CleanupRepository(probe.wrap(c));
      Runnable action =
          progress
              ? () -> repository.readLogProgress(RUN)
              : () -> repository.execute(RUN, CleanupKind.LOGS, 1);
      assertSame(failure, assertThrows(Throwable.class, action::run));
      assertEquals(0, probe.liveRows);
      assertEquals(0, probe.liveStatements);
      c.rollback();
    }
  }

  private static void rejectProjection(BatchJdbcProbe probe, boolean progress) throws Exception {
    probe.selectedSql =
        progress
            ? FIXTURE_MAINTENANCE_READ_LOG_CLEANUP_PROGRESS_75EF2AB2
            : FIXTURE_MAINTENANCE_CLEANUP_LOGS_01FD6149;
    try (var c = transaction()) {
      var repository = new CleanupRepository(probe.wrap(c));
      if (progress) redacted(() -> repository.readLogProgress(RUN));
      else redacted(() -> repository.execute(RUN, CleanupKind.LOGS, 1));
      assertEquals(0, probe.commits);
      assertEquals(0, probe.rollbacks);
      assertEquals(0, probe.closes);
      assertEquals(0, probe.autoChanges);
      c.rollback();
      assertFalse(c.isClosed());
    }
    try (var admin = db.admin()) {
      assertEquals("0", scalar(admin, "select count(*) from schubert.log_cleanup_progress"));
    }
  }

  private static void redacted(Runnable action) {
    var error = assertThrows(BatchRepositoryException.class, action::run);
    assertEquals("batch repository operation failed", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  private static Connection transaction() throws SQLException {
    var c = db.open("schubert_batch");
    c.setAutoCommit(false);
    return c;
  }

  private static void logs() throws SQLException {
    try (var c = db.admin()) {
      for (int id = 1; id <= 3; id++)
        sql(
            c,
            "insert into"
                + " schubert.app_logs(id,logged_at,service,category,level,action,message,security_hold_until)"
                + " values("
                + id
                + ",'2026-01-01 00:00:00+00','API','SECURITY','INFO','PUBLIC_TEST','public"
                + " fixture',"
                + (id < 3 ? "'2027-01-01 00:00:00+00'" : "null")
                + ")");
    }
  }

  private static void sql(Connection c, String query) throws SQLException {
    try (var s = c.createStatement()) {
      s.execute(query);
    }
  }

  private static String scalar(Connection c, String query) throws SQLException {
    try (var s = c.createStatement();
        var r = s.executeQuery(query)) {
      assertTrue(r.next());
      String v = r.getString(1);
      assertNotNull(v);
      assertFalse(r.next());
      return v;
    }
  }
}
