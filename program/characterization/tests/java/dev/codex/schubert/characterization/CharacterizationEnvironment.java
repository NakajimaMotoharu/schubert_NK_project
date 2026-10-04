package dev.codex.schubert.characterization;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Playwright;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermission;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

final class CharacterizationEnvironment implements AutoCloseable {
  private final Path currentJar = pathProperty("chr.currentJar");
  private final Path assetRoot = pathProperty("chr.assetRoot");
  private final Path usersFile = pathProperty("chr.usersFile");
  private final Path javaExecutable = pathProperty("chr.javaExecutable");
  private final Path caddyExecutable = pathProperty("chr.caddyExecutable");
  private final Path runtimeRoot = pathProperty("chr.runtimeRoot");
  private final Path pgCtl = pathProperty("chr.pgCtl");
  private final Path pgData = pathProperty("chr.pgData");
  private final Path pgLog = pathProperty("chr.pgLog");
  private final Path pgSocket = pathProperty("chr.pgSocket");
  private final String dbUrl = requiredProperty("chr.dbUrl");
  private final String dbUser = requiredProperty("chr.dbUser");
  private final int appPort = Integer.getInteger("chr.appPort", 46962);
  private final int proxyPort = Integer.getInteger("chr.proxyPort", 55162);
  private final List<Credential> credentials = loadCredentials(usersFile);
  private Process app;
  private Process caddy;
  private Playwright playwright;
  private Browser browser;
  private boolean databaseStopped;

  void start() throws Exception {
    Files.createDirectories(runtimeRoot.resolve("logs"));
    Files.createDirectories(runtimeRoot.resolve("caddy-data"));
    verifyCredentialPermission();
    resetLogs();
    startApp();
    startCaddy();
    playwright = Playwright.create();
    browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setHeadless(true));
  }

  Browser browser() {
    return browser;
  }

  Playwright playwright() {
    return playwright;
  }

  String baseUrl() {
    return "https://localhost:" + proxyPort;
  }

  Credential primaryCredential() {
    return credentials.getFirst();
  }

  Credential secondaryCredential() {
    return credentials.size() > 1 ? credentials.get(1) : credentials.getFirst();
  }

  List<Credential> credentials() {
    return credentials;
  }

  Connection database() throws Exception {
    return DriverManager.getConnection(dbUrl, dbUser, "");
  }

  long queryLong(String sql) throws Exception {
    try (Connection connection = database();
        Statement statement = connection.createStatement();
        ResultSet result = statement.executeQuery(sql)) {
      if (!result.next()) throw new IllegalStateException("query returned no row");
      return result.getLong(1);
    }
  }

  String queryString(String sql) throws Exception {
    try (Connection connection = database();
        Statement statement = connection.createStatement();
        ResultSet result = statement.executeQuery(sql)) {
      if (!result.next()) throw new IllegalStateException("query returned no row");
      return result.getString(1);
    }
  }

  void resetLogs() throws Exception {
    try (Connection connection = database();
        Statement statement = connection.createStatement()) {
      statement.execute("TRUNCATE TABLE scenario.app_logs RESTART IDENTITY");
    }
  }

  long createUnclassifiedRouteFixture() throws Exception {
    try (Connection connection = database();
        PreparedStatement statement =
            connection.prepareStatement(
                "INSERT INTO scenario.script_files "
                    + "(game_id,relative_path,file_name,section_code,chapter_title,sha256,byte_size) "
                    + "VALUES (2,'__characterization__/99_fixture.txt','99_fixture.txt',"
                    + "'99_fixture','Characterization fixture',repeat('0',64),0) RETURNING id")) {
      try (ResultSet result = statement.executeQuery()) {
        if (!result.next()) throw new IllegalStateException("route fixture insert returned no row");
        return result.getLong(1);
      }
    }
  }

  void deleteUnclassifiedRouteFixture(long scriptFileId) throws Exception {
    try (Connection connection = database();
        PreparedStatement statement =
            connection.prepareStatement("DELETE FROM scenario.script_files WHERE id=?")) {
      statement.setLong(1, scriptFileId);
      if (statement.executeUpdate() != 1) {
        throw new IllegalStateException("route fixture cleanup affected an unexpected row count");
      }
    }
  }

  MultipleVoiceFixture createMultipleVoiceFixture() throws Exception {
    String sql =
        "WITH chosen AS ("
            + " SELECT e.id,e.script_file_id FROM scenario.script_entries e"
            + " JOIN scenario.entry_audio_links l ON l.entry_id=e.id AND l.link_type='voice'"
            + " GROUP BY e.id,e.script_file_id HAVING count(*)=1 ORDER BY e.id LIMIT 1"
            + "), candidate_audio AS ("
            + " SELECT a.id FROM scenario.audio_files a, chosen c"
            + " WHERE NOT EXISTS (SELECT 1 FROM scenario.entry_audio_links l"
            + " WHERE l.entry_id=c.id AND l.audio_file_id=a.id AND l.link_type='voice')"
            + " ORDER BY a.id LIMIT 1"
            + ") INSERT INTO scenario.entry_audio_links"
            + " (entry_id,audio_file_id,link_type,reference_text,reference_line_number)"
            + " SELECT c.id,a.id,'voice','characterization fixture',0 FROM chosen c,candidate_audio a"
            + " RETURNING entry_id,audio_file_id";
    try (Connection connection = database();
        Statement statement = connection.createStatement()) {
      long entryId;
      long audioId;
      try (ResultSet result = statement.executeQuery(sql)) {
        if (!result.next())
          throw new IllegalStateException("multiple voice fixture insert returned no row");
        entryId = result.getLong(1);
        audioId = result.getLong(2);
      }
      try (PreparedStatement file =
          connection.prepareStatement(
              "SELECT script_file_id FROM scenario.script_entries WHERE id=?")) {
        file.setLong(1, entryId);
        try (ResultSet result = file.executeQuery()) {
          if (!result.next()) throw new IllegalStateException("multiple voice fixture has no file");
          return new MultipleVoiceFixture(entryId, audioId, result.getLong(1));
        }
      }
    }
  }

  void deleteMultipleVoiceFixture(MultipleVoiceFixture fixture) throws Exception {
    try (Connection connection = database();
        PreparedStatement statement =
            connection.prepareStatement(
                "DELETE FROM scenario.entry_audio_links "
                    + "WHERE entry_id=? AND audio_file_id=? AND link_type='voice'")) {
      statement.setLong(1, fixture.entryId());
      statement.setLong(2, fixture.audioId());
      if (statement.executeUpdate() != 1) {
        throw new IllegalStateException(
            "multiple voice fixture cleanup affected an unexpected row count");
      }
    }
  }

  void restartApp() throws Exception {
    stopProcess(app);
    app = null;
    startApp(List.of());
  }

  void stopAppForDependencyTest() throws Exception {
    stopProcess(app);
    app = null;
    waitPortClosed(appPort, Duration.ofSeconds(10));
  }

  void startAppAfterDependencyTest() throws Exception {
    startApp(List.of());
  }

  void stopDatabaseForDependencyTest() throws Exception {
    if (databaseStopped) {
      return;
    }
    runPostgresControl("stop", List.of("-m", "fast"));
    databaseStopped = true;
    waitPortClosed(databasePort(), Duration.ofSeconds(30));
  }

  void startDatabaseAfterDependencyTest() throws Exception {
    if (!databaseStopped) {
      return;
    }
    Files.createDirectories(pgSocket);
    String options = "-p " + databasePort() + " -h 127.0.0.1 -k " + pgSocket;
    runPostgresControl("start", List.of("-l", pgLog.toString(), "-o", options));
    waitPortOpen(databasePort(), Duration.ofSeconds(30));
    databaseStopped = false;
  }

  private void startApp() throws Exception {
    startApp(List.of());
  }

  private void startApp(List<String> arguments) throws Exception {
    if (app != null && app.isAlive()) return;
    Path log = runtimeRoot.resolve("logs/current-app.log");
    List<String> command = new ArrayList<>();
    command.add(javaExecutable.toString());
    command.add("-jar");
    command.add(currentJar.toString());
    command.add("--spring.datasource.hikari.connection-timeout=1000");
    command.addAll(arguments);
    ProcessBuilder builder = new ProcessBuilder(command);
    Map<String, String> environment = builder.environment();
    environment.put("BIND_ADDRESS", "127.0.0.1");
    environment.put("PORT", Integer.toString(appPort));
    environment.put("DATABASE_URL", dbUrl);
    environment.put("DATABASE_USER", dbUser);
    environment.put("DATABASE_PASSWORD", "characterization-local-only");
    environment.put("ASSET_ROOT", assetRoot.toString());
    environment.put("USERS_FILE", usersFile.toString());
    environment.put("LOG_FILE", runtimeRoot.resolve("logs/schubert.log").toString());
    builder
        .redirectErrorStream(true)
        .redirectOutput(ProcessBuilder.Redirect.appendTo(log.toFile()));
    app = builder.start();
    waitPortOpen(appPort, Duration.ofSeconds(60), app, log);
  }

  private void startCaddy() throws Exception {
    Path config = runtimeRoot.resolve("Caddyfile");
    String text = renderCaddyConfig(proxyPort, appPort, runtimeRoot.resolve("caddy-data"));
    Files.writeString(config, text, StandardCharsets.UTF_8);
    ProcessBuilder builder =
        new ProcessBuilder(
            caddyExecutable.toString(),
            "run",
            "--config",
            config.toString(),
            "--adapter",
            "caddyfile");
    builder.environment().put("XDG_DATA_HOME", runtimeRoot.resolve("caddy-data").toString());
    builder.environment().put("XDG_CONFIG_HOME", runtimeRoot.resolve("caddy-config").toString());
    Path log = runtimeRoot.resolve("logs/caddy.log");
    builder
        .redirectErrorStream(true)
        .redirectOutput(ProcessBuilder.Redirect.appendTo(log.toFile()));
    caddy = builder.start();
    waitPortOpen(proxyPort, Duration.ofSeconds(30), caddy, log);
  }

  static String renderCaddyConfig(int proxyPort, int appPort, Path storageRoot) {
    return """
        {
          admin localhost:%d
          auto_https disable_redirects
          skip_install_trust
          storage file_system {
            root %s
          }
        }
        https://localhost:%d {
          tls internal
          header {
            Strict-Transport-Security "max-age=31536000"
            X-Content-Type-Options "nosniff"
            X-Frame-Options "DENY"
            Referrer-Policy "same-origin"
            Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
            -Server
          }
          reverse_proxy 127.0.0.1:%d {
            header_up X-Real-IP {remote_host}
            header_up X-Forwarded-Host {hostport}
            header_up X-Forwarded-Port {port}
            header_up X-Forwarded-Proto https
          }
        }
        """
        .formatted(proxyPort + 10000, storageRoot, proxyPort, appPort);
  }

  private void verifyCredentialPermission() throws IOException {
    Set<PosixFilePermission> permissions = Files.getPosixFilePermissions(usersFile);
    Set<PosixFilePermission> required =
        Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE);
    if (!permissions.equals(required)) {
      throw new IllegalStateException("credential reference must be 0600");
    }
  }

  private static void waitPortOpen(int port, Duration timeout, Process process, Path log)
      throws Exception {
    long deadline = System.nanoTime() + timeout.toNanos();
    while (System.nanoTime() < deadline) {
      if (!process.isAlive())
        throw new IllegalStateException("process exited during startup; see " + log);
      try (Socket socket = new Socket()) {
        socket.connect(new InetSocketAddress("127.0.0.1", port), 250);
        return;
      } catch (IOException ignored) {
        Thread.sleep(100);
      }
    }
    throw new IllegalStateException("port did not become ready: " + port + "; see " + log);
  }

  private static void waitPortOpen(int port, Duration timeout) throws Exception {
    long deadline = System.nanoTime() + timeout.toNanos();
    while (System.nanoTime() < deadline) {
      try (Socket socket = new Socket()) {
        socket.connect(new InetSocketAddress("127.0.0.1", port), 250);
        return;
      } catch (IOException ignored) {
        Thread.sleep(100);
      }
    }
    throw new IllegalStateException("port did not become ready: " + port);
  }

  private static void waitPortClosed(int port, Duration timeout) throws Exception {
    long deadline = System.nanoTime() + timeout.toNanos();
    while (System.nanoTime() < deadline) {
      try (Socket socket = new Socket()) {
        socket.connect(new InetSocketAddress("127.0.0.1", port), 250);
        Thread.sleep(100);
      } catch (IOException expected) {
        return;
      }
    }
    throw new IllegalStateException("port remained open: " + port);
  }

  private static void stopProcess(Process process) throws Exception {
    if (process == null || !process.isAlive()) return;
    process.destroy();
    if (!process.waitFor(10, java.util.concurrent.TimeUnit.SECONDS)) {
      process.destroyForcibly();
      process.waitFor(10, java.util.concurrent.TimeUnit.SECONDS);
    }
  }

  @Override
  public void close() {
    Exception failure = null;
    failure =
        cleanup(
            failure,
            () -> {
              if (databaseStopped) startDatabaseAfterDependencyTest();
            });
    failure =
        cleanup(
            failure,
            () -> {
              if (browser != null) browser.close();
            });
    failure =
        cleanup(
            failure,
            () -> {
              if (playwright != null) playwright.close();
            });
    failure = cleanup(failure, () -> stopProcess(caddy));
    failure = cleanup(failure, () -> stopProcess(app));
    if (failure != null)
      throw new IllegalStateException("characterization cleanup failed", failure);
  }

  private static Exception cleanup(Exception previous, CheckedCleanup action) {
    try {
      action.run();
      return previous;
    } catch (Exception error) {
      if (error instanceof InterruptedException) Thread.currentThread().interrupt();
      if (previous == null) return error;
      previous.addSuppressed(error);
      return previous;
    }
  }

  private void runPostgresControl(String action, List<String> extraArguments) throws Exception {
    List<String> command = new ArrayList<>();
    command.add(pgCtl.toString());
    command.add("-D");
    command.add(pgData.toString());
    command.add("-w");
    command.addAll(extraArguments);
    command.add(action);
    Process process =
        new ProcessBuilder(command)
            .redirectErrorStream(true)
            .redirectOutput(ProcessBuilder.Redirect.appendTo(pgLog.toFile()))
            .start();
    if (!process.waitFor(60, java.util.concurrent.TimeUnit.SECONDS)) {
      process.destroyForcibly();
      throw new IllegalStateException("pg_ctl timed out: " + action);
    }
    if (process.exitValue() != 0) {
      throw new IllegalStateException("pg_ctl failed: " + action + "; see " + pgLog);
    }
  }

  private int databasePort() {
    java.util.regex.Matcher matcher =
        java.util.regex.Pattern.compile("jdbc:postgresql://[^:/]+:([0-9]+)/").matcher(dbUrl);
    if (!matcher.find()) {
      throw new IllegalStateException("database URL has no explicit TCP port");
    }
    return Integer.parseInt(matcher.group(1));
  }

  static List<Credential> loadCredentials(Path path) {
    try {
      List<Credential> result = new ArrayList<>();
      String user = null;
      for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
        if (line.isBlank() || line.stripLeading().startsWith("#")) continue;
        if (line.startsWith("user=")) user = line.substring(5);
        else if (line.startsWith("pass=") && user != null) {
          result.add(new Credential(user, line.substring(5)));
          user = null;
        }
      }
      if (result.isEmpty()) throw new IllegalStateException("credential reference has no account");
      return List.copyOf(result);
    } catch (IOException error) {
      throw new IllegalStateException("credential reference is unreadable", error);
    }
  }

  private static Path pathProperty(String name) {
    return Path.of(requiredProperty(name)).toAbsolutePath().normalize();
  }

  private static String requiredProperty(String name) {
    String value = System.getProperty(name);
    if (value == null || value.isBlank())
      throw new IllegalArgumentException("missing property: " + name);
    return value;
  }

  record Credential(String username, String password) {}

  record MultipleVoiceFixture(long entryId, long audioId, long scriptFileId) {}

  @FunctionalInterface
  private interface CheckedCleanup {
    void run() throws Exception;
  }
}
