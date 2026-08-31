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
  private final String dbUrl = requiredProperty("chr.dbUrl");
  private final String dbUser = requiredProperty("chr.dbUser");
  private final int appPort = Integer.getInteger("chr.appPort", 46962);
  private final int proxyPort = Integer.getInteger("chr.proxyPort", 55162);
  private final List<Credential> credentials = loadCredentials(usersFile);
  private Process app;
  private Process caddy;
  private Playwright playwright;
  private Browser browser;

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
    try (Connection connection = database(); Statement statement = connection.createStatement(); ResultSet result = statement.executeQuery(sql)) {
      if (!result.next()) throw new IllegalStateException("query returned no row");
      return result.getLong(1);
    }
  }

  String queryString(String sql) throws Exception {
    try (Connection connection = database(); Statement statement = connection.createStatement(); ResultSet result = statement.executeQuery(sql)) {
      if (!result.next()) throw new IllegalStateException("query returned no row");
      return result.getString(1);
    }
  }

  void resetLogs() throws Exception {
    try (Connection connection = database(); Statement statement = connection.createStatement()) {
      statement.execute("TRUNCATE TABLE scenario.app_logs RESTART IDENTITY");
    }
  }

  void restartApp() throws Exception {
    stopProcess(app);
    app = null;
    startApp();
  }

  void stopAppForDependencyTest() throws Exception {
    stopProcess(app);
    app = null;
    waitPortClosed(appPort, Duration.ofSeconds(10));
  }

  void startAppAfterDependencyTest() throws Exception {
    startApp();
  }

  private void startApp() throws Exception {
    if (app != null && app.isAlive()) return;
    Path log = runtimeRoot.resolve("logs/current-app.log");
    ProcessBuilder builder = new ProcessBuilder(javaExecutable.toString(), "-jar", currentJar.toString());
    Map<String, String> environment = builder.environment();
    environment.put("BIND_ADDRESS", "127.0.0.1");
    environment.put("PORT", Integer.toString(appPort));
    environment.put("DATABASE_URL", dbUrl);
    environment.put("DATABASE_USER", dbUser);
    environment.put("DATABASE_PASSWORD", "characterization-local-only");
    environment.put("ASSET_ROOT", assetRoot.toString());
    environment.put("USERS_FILE", usersFile.toString());
    environment.put("LOG_FILE", runtimeRoot.resolve("logs/schubert.log").toString());
    builder.redirectErrorStream(true).redirectOutput(ProcessBuilder.Redirect.appendTo(log.toFile()));
    app = builder.start();
    waitPortOpen(appPort, Duration.ofSeconds(60), app, log);
  }

  private void startCaddy() throws Exception {
    Path config = runtimeRoot.resolve("Caddyfile");
    String text = renderCaddyConfig(proxyPort, appPort, runtimeRoot.resolve("caddy-data"));
    Files.writeString(config, text, StandardCharsets.UTF_8);
    ProcessBuilder builder = new ProcessBuilder(caddyExecutable.toString(), "run", "--config", config.toString(), "--adapter", "caddyfile");
    builder.environment().put("XDG_DATA_HOME", runtimeRoot.resolve("caddy-data").toString());
    builder.environment().put("XDG_CONFIG_HOME", runtimeRoot.resolve("caddy-config").toString());
    Path log = runtimeRoot.resolve("logs/caddy.log");
    builder.redirectErrorStream(true).redirectOutput(ProcessBuilder.Redirect.appendTo(log.toFile()));
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
        """.formatted(proxyPort + 10000, storageRoot, proxyPort, appPort);
  }

  private void verifyCredentialPermission() throws IOException {
    Set<PosixFilePermission> permissions = Files.getPosixFilePermissions(usersFile);
    Set<PosixFilePermission> required = Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE);
    if (!permissions.equals(required)) {
      throw new IllegalStateException("credential reference must be 0600");
    }
  }

  private static void waitPortOpen(int port, Duration timeout, Process process, Path log) throws Exception {
    long deadline = System.nanoTime() + timeout.toNanos();
    while (System.nanoTime() < deadline) {
      if (!process.isAlive()) throw new IllegalStateException("process exited during startup; see " + log);
      try (Socket socket = new Socket()) {
        socket.connect(new InetSocketAddress("127.0.0.1", port), 250);
        return;
      } catch (IOException ignored) {
        Thread.sleep(100);
      }
    }
    throw new IllegalStateException("port did not become ready: " + port + "; see " + log);
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
  public void close() throws Exception {
    if (browser != null) browser.close();
    if (playwright != null) playwright.close();
    stopProcess(caddy);
    stopProcess(app);
  }

  private static List<Credential> loadCredentials(Path path) {
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
    if (value == null || value.isBlank()) throw new IllegalArgumentException("missing property: " + name);
    return value;
  }

  record Credential(String username, String password) {}
}
