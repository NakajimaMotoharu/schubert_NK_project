package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.time.Duration;
import org.flywaydb.core.Flyway;

/** Isolated PostgreSQL 18 with production Flyway scripts; never connects to deployed data. */
public final class ApiLogDatabaseFixture {
  private final Path root;
  private final Path pg;
  private final String url;

  public ApiLogDatabaseFixture(Path root) throws Exception {
    this.root = root;
    String configured = System.getenv("SCHUBERT_PG_ROOT");
    pg =
        configured == null || configured.isBlank()
            ? Path.of("/home/mini/codex/project1/work/characterization-tools/root/usr")
            : Path.of(configured);
    int port;
    try (ServerSocket socket = new ServerSocket(0, 1, InetAddress.getLoopbackAddress())) {
      port = socket.getLocalPort();
    }
    run(
        "initdb",
        "-D",
        root.resolve("data").toString(),
        "-L",
        pg.resolve("share/postgresql/18").toString(),
        "--no-locale",
        "--encoding=UTF8",
        "--auth=trust",
        "--username=pgpt_admin");
    run(
        "pg_ctl",
        "-D",
        root.resolve("data").toString(),
        "-l",
        root.resolve("postgresql.log").toString(),
        "-o",
        "-p "
            + port
            + " -h 127.0.0.1 -k /tmp -c timezone=UTC -c extension_control_path="
            + pg.resolve("share/postgresql/18")
            + " -c dynamic_library_path="
            + pg.resolve("lib/postgresql/18/lib"),
        "start");
    url = "jdbc:postgresql://127.0.0.1:" + port + "/postgres";
    Path resources =
        Path.of(System.getProperty("nk.pt.repository"))
            .resolve("src/schubert-nk-api/src/main/resources/db");
    try (Connection connection = admin();
        var statement = connection.createStatement()) {
      statement.execute(Files.readString(resources.resolve("provisioning/001_roles.sql")));
    }
    Flyway.configure()
        .dataSource(url, "schubert_migration", "")
        .defaultSchema("schubert_meta")
        .schemas("schubert_meta")
        .createSchemas(true)
        .initSql("SET ROLE nk_owner")
        .locations("filesystem:" + resources.resolve("migration"))
        .validateOnMigrate(true)
        .cleanDisabled(true)
        .load()
        .migrate();
  }

  public Connection api() throws SQLException {
    return DriverManager.getConnection(url, "schubert_app", "");
  }

  public Connection transaction() throws SQLException {
    Connection connection = api();
    connection.setAutoCommit(false);
    return connection;
  }

  public Connection admin() throws SQLException {
    return DriverManager.getConnection(url, "pgpt_admin", "");
  }

  void reset() throws SQLException {
    try (Connection connection = api();
        var statement = connection.createStatement()) {
      statement.executeUpdate("delete from schubert.app_logs");
    }
  }

  private void run(String program, String... args) throws IOException, InterruptedException {
    java.util.List<String> command = new java.util.ArrayList<>();
    command.add(pg.resolve("lib/postgresql/18/bin").resolve(program).toString());
    command.addAll(java.util.List.of(args));
    ProcessBuilder builder =
        new ProcessBuilder(command)
            .redirectErrorStream(true)
            .redirectOutput(ProcessBuilder.Redirect.appendTo(root.resolve("process.log").toFile()));
    builder
        .environment()
        .put(
            "LD_LIBRARY_PATH",
            pg.resolve("lib/x86_64-linux-gnu") + ":" + pg.resolve("lib/postgresql/18/lib"));
    Process process = builder.start();
    assertTrue(process.waitFor(Duration.ofSeconds(30)), "PostgreSQL fixture command timed out");
    assertEquals(0, process.exitValue(), "PostgreSQL fixture command failed");
  }

  public void stop() throws IOException, InterruptedException {
    run("pg_ctl", "-D", root.resolve("data").toString(), "stop", "-m", "fast");
  }
}
