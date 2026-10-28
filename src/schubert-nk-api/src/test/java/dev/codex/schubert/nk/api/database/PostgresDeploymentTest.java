package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.time.Duration;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Independent SS342 section 6 inventory; RD SYS/DAT/PER, UI212/253; PG187/BUG208. */
final class PostgresDeploymentTest {
  private static final String FIXTURE_DATA_PG_HBA_CONF_73424ED1 = "data/pg_hba.conf";
  private static final Path REPOSITORY = Path.of(System.getProperty("nk.pt.repository"));
  private static final Path TEMPLATES = REPOSITORY.resolve("src/deployment/postgresql");
  private static final String EXPECTED =
      """
      listen_addresses=127.0.0.1,::1
      port=5432
      max_connections=40
      shared_buffers=2GB
      effective_cache_size=6GB
      work_mem=8MB
      maintenance_work_mem=512MB
      max_worker_processes=8
      max_parallel_workers=4
      max_parallel_workers_per_gather=2
      temp_file_limit=2GB
      wal_compression=on
      min_wal_size=1GB
      max_wal_size=4GB
      checkpoint_timeout=15min
      checkpoint_completion_target=0.9
      deadlock_timeout=500ms
      password_encryption=scram-sha-256
      ssl=off
      log_statement=none
      log_parameter_max_length=0
      log_parameter_max_length_on_error=0
      log_connections=on
      log_disconnections=on
      log_checkpoints=on
      log_lock_waits=on
      log_autovacuum_min_duration=0
      log_min_duration_statement=-1
      log_min_duration_sample=-1
      log_transaction_sample_rate=0
      log_min_error_statement=panic
      log_error_verbosity=terse
      """;
  private static Path root;
  private static Path pg;
  private static ApiLogDatabaseFixture database;
  private static String originalHba;

  @BeforeAll
  static void start() throws Exception {
    root = Files.createTempDirectory(Path.of("target").toAbsolutePath(), "pg-config-");
    String configured = System.getenv("SCHUBERT_PG_ROOT");
    pg =
        configured == null || configured.isBlank()
            ? Path.of("/home/mini/codex/project1/work/characterization-tools/root/usr")
            : Path.of(configured);
    database = new ApiLogDatabaseFixture(root);
    originalHba = Files.readString(root.resolve(FIXTURE_DATA_PG_HBA_CONF_73424ED1));
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-001 independent complete configuration inventory")
  void literalConfiguration() throws Exception {
    assertEquals(settings(EXPECTED), settings(configuration()));
    assertEquals(32, settings(EXPECTED).size());
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-002 PostgreSQL native configuration parser")
  void nativeConfiguration() throws Exception {
    Map<String, String> expected = new LinkedHashMap<>(settings(EXPECTED));
    expected.put("shared_buffers", "262144");
    expected.put("effective_cache_size", "786432");
    expected.put("work_mem", "8192");
    expected.put("maintenance_work_mem", "524288");
    expected.put("temp_file_limit", "2097152");
    expected.put("min_wal_size", "1024");
    expected.put("max_wal_size", "4096");
    expected.put("checkpoint_timeout", "900");
    expected.put("deadlock_timeout", "500");
    // PostgreSQL 18 runtime-config-wal: on is the historical spelling of pglz (BUG209).
    expected.put("wal_compression", "pglz");
    // log_connections is a string GUC: on is retained, with the documented three-event meaning.
    for (var entry : expected.entrySet()) {
      Result result = nativeValue(TEMPLATES.resolve("postgresql.conf.template"), entry.getKey());
      assertEquals(0, result.exit(), entry.getKey());
      assertEquals(entry.getValue(), result.output().strip(), entry.getKey());
    }
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-003 exact ordered least privilege HBA rules")
  void literalHba() throws Exception {
    assertEquals(expectedHba(), lines(hba()));
    assertEquals(16, expectedHba().size());
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-004 native HBA catalog with restoration")
  void nativeHba() throws Exception {
    List<String> expected = new ArrayList<>();
    for (String rule : expectedHba()) {
      String[] fields = rule.split(" ");
      if (fields[0].equals("local")) {
        expected.add("local|all|postgres|||peer");
      } else {
        String address = fields[3].split("/")[0];
        String mask =
            fields[3].endsWith("/32")
                ? "255.255.255.255"
                : fields[3].endsWith("/128")
                    ? "ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
                    : address.contains(":") ? "::" : "0.0.0.0";
        expected.add(String.join("|", fields[0], fields[1], fields[2], address, mask, fields[4]));
      }
    }
    assertEquals(expected, inspectHba(hba(), false));
    assertEquals(originalHba, Files.readString(root.resolve(FIXTURE_DATA_PG_HBA_CONF_73424ED1)));
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-005 independent role timeout catalog BUG208 YKT164")
  void roleTimeouts() throws Exception {
    Map<String, List<String>> expected =
        Map.of(
            "schubert_app", List.of("1500ms", "500ms", "15s"),
            "schubert_web_session", List.of("1500ms", "500ms", "15s"),
            "schubert_batch", List.of("30min", "5s", "60s"),
            "schubert_backup", List.of("30min", "5s", "60s"),
            "schubert_migration", List.of("30min", "5s", "60s"),
            "schubert_ops_ro", List.of("10s", "1s", "15s"),
            "schubert_inbox_inspector", List.of("30s", "5s"));
    try (Connection connection = database.admin();
        var query = connection.prepareStatement("SELECT rolconfig FROM pg_roles WHERE rolname=?")) {
      for (var entry : expected.entrySet()) {
        query.setString(1, entry.getKey());
        try (var rows = query.executeQuery()) {
          assertTrue(rows.next());
          var array = rows.getArray(1);
          assertNotNull(array);
          Map<String, String> actual;
          try {
            actual = settings(String.join("\n", (String[]) array.getArray()));
          } finally {
            array.free();
          }
          assertEquals(entry.getValue().get(0), actual.get("statement_timeout"), entry.getKey());
          assertEquals(entry.getValue().get(1), actual.get("lock_timeout"), entry.getKey());
          if (entry.getValue().size() == 3)
            assertEquals(
                entry.getValue().get(2),
                actual.get("idle_in_transaction_session_timeout"),
                entry.getKey());
          else assertFalse(actual.containsKey("idle_in_transaction_session_timeout"));
          assertFalse(rows.next());
        }
      }
    }
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-006 native invalid settings and independent policy canaries")
  void invalidConfiguration() throws Exception {
    for (String invalid : List.of("nk_unknown_setting=1", "shared_buffers='unterminated")) {
      Path file = Files.createTempFile(root, "bad-", ".conf");
      Files.writeString(file, invalid);
      assertNotEquals(0, nativeValue(file, "port").exit());
    }
    Map<String, String> expected = settings(EXPECTED);
    for (String changed :
        List.of(
            configuration().replace("127.0.0.1,::1", "0.0.0.0"),
            configuration().replace("'none'", "'all'"),
            configuration().replace("port = 5432", "")))
      assertNotEquals(expected, settings(changed));
    assertThrows(AssertionError.class, () -> settings("port=1\nport=2"));
    assertNotEquals(expected, settings(""));
    assertThrows(NullPointerException.class, () -> settings(null));
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-007 invalid HBA and policy canaries with restoration")
  void invalidHba() throws Exception {
    assertFalse(inspectHba("host all all 127.0.0.1/32 unknown_auth\n", true).isEmpty());
    for (String changed :
        List.of(
            hba().replace("scram-sha-256", "trust"),
            hba().replace("scram-sha-256", "md5"),
            hba().replace("127.0.0.1/32", "0.0.0.0/0"),
            hba().replace("host all all ::/0 reject", "")))
      assertNotEquals(expectedHba(), lines(changed));
    assertEquals(originalHba, Files.readString(root.resolve(FIXTURE_DATA_PG_HBA_CONF_73424ED1)));
  }

  @Test
  @DisplayName("PT-OPS-PGCFG-008 isolated fixture and public evidence")
  void isolationAndEvidence() throws Exception {
    assertTrue(root.startsWith(Path.of("target").toAbsolutePath()));
    assertEquals(originalHba, Files.readString(root.resolve(FIXTURE_DATA_PG_HBA_CONF_73424ED1)));
    try (Connection connection = database.admin()) {
      assertTrue(connection.getMetaData().getURL().startsWith("jdbc:postgresql://127.0.0.1:"));
    }
    Path trace = Path.of("target/postgres-deployment-traces");
    Files.createDirectories(trace);
    Files.writeString(
        trace.resolve("PT-OPS-PGCFG-008.txt"),
        "isolated=true\nhostConfigurationChanged=false\nhbaReload=false\nrawDatabaseLogCopied=false\nconfigurationKeys=32\nhbaRules=16\n");
  }

  private static String configuration() throws Exception {
    return Files.readString(TEMPLATES.resolve("postgresql.conf.template"));
  }

  private static String hba() throws Exception {
    return Files.readString(TEMPLATES.resolve("pg_hba.conf.template"));
  }

  private static List<String> lines(String text) {
    return text.lines()
        .map(String::strip)
        .filter(s -> !s.isEmpty() && !s.startsWith("#"))
        .map(s -> s.replaceAll("\\s+", " "))
        .toList();
  }

  private static Map<String, String> settings(String text) {
    Map<String, String> result = new LinkedHashMap<>();
    for (String line : lines(text)) {
      String[] pair = line.split("=", 2);
      assertEquals(2, pair.length);
      assertNull(result.put(pair[0].strip(), pair[1].strip().replace("'", "")));
    }
    return result;
  }

  private static List<String> expectedHba() {
    List<String> result = new ArrayList<>();
    result.add("local all postgres peer");
    for (String role : List.of("app", "web_session", "batch", "backup", "ops_ro", "migration"))
      for (String address : List.of("127.0.0.1/32", "::1/128"))
        result.add("host schubert_nk schubert_" + role + " " + address + " scram-sha-256");
    result.add("host schubert_nk schubert_inbox_inspector 127.0.0.1/32 scram-sha-256");
    result.add("host all all 0.0.0.0/0 reject");
    result.add("host all all ::/0 reject");
    return result;
  }

  private static List<String> inspectHba(String text, boolean errors) throws Exception {
    Path file = root.resolve(FIXTURE_DATA_PG_HBA_CONF_73424ED1);
    try (Connection connection = database.admin()) {
      try {
        Files.writeString(file, text);
        try (var query = connection.createStatement();
            var rows =
                query.executeQuery(
                    "SELECT type, database, user_name, address, netmask, auth_method, error FROM pg_hba_file_rules ORDER BY rule_number NULLS LAST, line_number")) {
          List<String> result = new ArrayList<>();
          while (rows.next()) {
            if (errors) {
              assertNotNull(rows.getString(7));
              result.add("REJECTED");
            } else {
              assertNull(rows.getString(7));
              var db = rows.getArray(2);
              var users = rows.getArray(3);
              try {
                result.add(
                    String.join(
                        "|",
                        rows.getString(1),
                        String.join(",", (String[]) db.getArray()),
                        String.join(",", (String[]) users.getArray()),
                        rows.getString(4) == null ? "" : rows.getString(4),
                        rows.getString(5) == null ? "" : rows.getString(5),
                        rows.getString(6)));
              } finally {
                db.free();
                users.free();
              }
            }
          }
          return result;
        }
      } finally {
        Files.writeString(file, originalHba);
      }
    }
  }

  private static Result nativeValue(Path configuration, String key) throws Exception {
    Path output = Files.createTempFile(root, "native-", ".txt");
    ProcessBuilder builder =
        new ProcessBuilder(
                pg.resolve("lib/postgresql/18/bin/postgres").toString(),
                "-D",
                root.resolve("data").toString(),
                "-c",
                "config_file=" + configuration,
                "-C",
                key)
            .redirectOutput(output.toFile())
            .redirectError(ProcessBuilder.Redirect.DISCARD);
    builder
        .environment()
        .put(
            "LD_LIBRARY_PATH",
            pg.resolve("lib/x86_64-linux-gnu") + ":" + pg.resolve("lib/postgresql/18/lib"));
    Process process = builder.start();
    try {
      assertTrue(process.waitFor(Duration.ofSeconds(30)));
      return new Result(process.exitValue(), Files.readString(output));
    } finally {
      if (process.isAlive()) {
        process.destroyForcibly();
        assertTrue(process.waitFor(5, TimeUnit.SECONDS));
      }
    }
  }

  private record Result(int exit, String output) {}
}
