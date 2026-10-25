package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.CleanupMode;
import org.junit.jupiter.api.io.TempDir;

/** PT-DBFIX-1633; only this test's new loopback cluster, no deployed database or service. */
final class BatchFixtureOwnershipTest {
  @TempDir(cleanup = CleanupMode.ON_SUCCESS)
  Path temporary;

  private static final String TABLES =
      "schubert.answers,schubert.app_logs,schubert.app_users,schubert.async_jobs,"
          + "schubert.audio_files,schubert.auth_sessions,schubert.batch_runs,schubert.entry_audio_links,"
          + "schubert.games,schubert.inbox_inspection_progress,schubert.log_cleanup_progress,"
          + "schubert.login_ip_attempts,schubert.media_assets,schubert.mq_outbox,schubert.notifications,"
          + "schubert.questions,schubert.request_inbox,schubert.script_entries,schubert.script_files,"
          + "schubert.speakers,schubert_web_session.pending_context_revocations,"
          + "schubert_web_session.web_http_sessions,schubert_web_session.web_log_outbox,"
          + "schubert_web_session.web_receipt_references";

  @Test
  void dbfix1633001MissingConfigurationCreatesNoExternalOwner() throws Exception {
    int index = 0;
    for (String repository : new String[] {null, "", " "}) {
      Path database = Files.createDirectory(temporary.resolve("invalid-" + index++));
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> new BatchDatabaseFixture(database, repository));
      assertEquals("PT repository property is required", failure.getMessage());
      try (var entries = Files.list(database)) {
        assertEquals(0, entries.count());
      }
    }
  }

  @Test
  void dbfix1633002KnownStartedSetupSqlFailureCannotLeaveUnpublishedOwner() throws Exception {
    Path repository = Files.createDirectory(temporary.resolve("public-broken-repository"));
    Path script =
        repository.resolve("src/schubert-nk-api/src/main/resources/db/provisioning/001_roles.sql");
    Files.createDirectories(script.getParent());
    Files.writeString(script, "SELECT 1 / 0;\n", StandardCharsets.US_ASCII);
    Path database = Files.createDirectory(temporary.resolve("owned-failure-database"));
    try {
      var failure =
          assertThrows(
              SQLException.class, () -> new BatchDatabaseFixture(database, repository.toString()));
      assertEquals("22012", failure.getSQLState());
      assertEquals(0, failure.getSuppressed().length);
      assertTrue(Files.isDirectory(database.resolve("data")));
      assertFalse(
          Files.exists(database.resolve("data/postmaster.pid"), LinkOption.NOFOLLOW_LINKS),
          "confirmed started fixture must stop before constructor failure escapes");
    } finally {
      System.out.println(
          "PT-DBFIX-1633-B02 ownedResidualStop=" + stopOnlyThisNewFixtureIfPresent(database));
    }
  }

  @Test
  void dbfix1633003NormalRoleAllTwentyFourTablesAndExplicitStopStayOwned() throws Exception {
    Path database = Files.createDirectory(temporary.resolve("owned-normal-database"));
    BatchDatabaseFixture fixture = null;
    try {
      fixture = new BatchDatabaseFixture(database);
      assertTrue(Files.isRegularFile(database.resolve("data/postmaster.pid")));
      try (var connection = fixture.open("schubert_batch");
          var statement = connection.createStatement();
          var rows = statement.executeQuery("SELECT current_user")) {
        assertTrue(rows.next());
        assertEquals("schubert_batch", rows.getString(1));
        assertFalse(rows.next());
      }
      try (var connection = fixture.admin();
          var statement = connection.createStatement();
          var rows =
              statement.executeQuery(
                  "SELECT string_agg(table_schema || '.' || table_name, ',' ORDER BY table_schema, table_name)"
                      + " FROM information_schema.tables WHERE table_schema IN ('schubert','schubert_web_session')"
                      + " AND table_type='BASE TABLE'")) {
        assertTrue(rows.next());
        assertEquals(TABLES, rows.getString(1));
        assertFalse(rows.next());
      }
    } finally {
      if (fixture != null) fixture.stop();
      else stopOnlyThisNewFixtureIfPresent(database);
    }
    assertFalse(Files.exists(database.resolve("data/postmaster.pid"), LinkOption.NOFOLLOW_LINKS));
  }

  /**
   * Red-run cleanup only: authenticate this new TempDir's PID/user/data argv, never global
   * processes.
   */
  private static boolean stopOnlyThisNewFixtureIfPresent(Path root) throws Exception {
    Path data = root.resolve("data").toAbsolutePath().normalize();
    Path pidFile = data.resolve("postmaster.pid");
    if (!Files.exists(pidFile, LinkOption.NOFOLLOW_LINKS)) return false;
    assertTrue(Files.isRegularFile(pidFile, LinkOption.NOFOLLOW_LINKS));
    var lines = Files.readAllLines(pidFile, StandardCharsets.US_ASCII);
    assertTrue(lines.size() >= 2);
    assertEquals(data.toString(), lines.get(1));
    long pid = Long.parseLong(lines.getFirst());
    var actual = ProcessHandle.of(pid).orElseThrow();
    var info = actual.info();
    assertTrue(info.command().orElseThrow().endsWith("/postgres"));
    assertTrue(List.of(info.arguments().orElseThrow()).contains(data.toString()));
    assertEquals(Files.getOwner(data).getName(), info.user().orElseThrow());
    String configured = System.getenv("SCHUBERT_PG_ROOT");
    Path pg =
        configured == null || configured.isBlank()
            ? Path.of("/home/mini/codex/project1/work/characterization-tools/root/usr")
            : Path.of(configured);
    var builder =
        new ProcessBuilder(
                pg.resolve("lib/postgresql/18/bin/pg_ctl").toString(),
                "-D",
                data.toString(),
                "stop",
                "-m",
                "fast")
            .redirectErrorStream(true)
            .redirectOutput(root.resolve("owned-red-cleanup.log").toFile());
    builder
        .environment()
        .put(
            "LD_LIBRARY_PATH",
            pg.resolve("lib/x86_64-linux-gnu") + ":" + pg.resolve("lib/postgresql/18/lib"));
    var client = builder.start();
    assertTrue(client.waitFor(Duration.ofSeconds(30)));
    assertEquals(0, client.exitValue());
    assertFalse(Files.exists(pidFile, LinkOption.NOFOLLOW_LINKS));
    return true;
  }
}
