package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001; RD SYS-002/004, OPS-009; UI212/231/243/251/253; SS342/343; PG269/274/277. */
final class ApplicationServiceUnitTest {
  private static final String FIXTURE_API_63E3A42F = "api";
  private static final String FIXTURE_WEB_BDE14896 = "web";
  private static final Path ROOT = Path.of(System.getProperty("nk.pt.repository"));
  private static final Path UNITS = ROOT.resolve("src/deployment/systemd");
  @TempDir Path temporary;

  @Test
  void apiDependencyCredentialAndResourceContract() throws Exception {
    String unit = read("schubert-nk-api");
    common(unit, FIXTURE_API_63E3A42F, "2048M", "60s", "512m", "1024m", "256m", "256m");
    // SSC099/BUG307: SS341§2 independent complete Unit name, not SS342's old shorthand.
    exact(unit, "After", "schubert-nk-expiry-cleanup.service artemis.service postgresql.service");
    // SSC139/BUG398: ordering is retained; the parent alone starts owned maintenance.
    exact(unit, "Requires", "artemis.service postgresql.service");
    exact(unit, "SupplementaryGroups", "schubert schubert-read schubert-web");
    exact(unit, "ReadWritePaths", "/srv/schubert-nk/data/transfer");
    credentials(
        unit,
        "db-api",
        "mq-api",
        "api-context-aes-current",
        "api-inbox-response-aes-current",
        "operation-hmac-current");
    assertTrue(unit.contains("dev.codex.schubert.nk.batch.file.RootServiceLauncher API"));
    assertFalse(unit.contains("dev.codex.schubert.nk.api.bootstrap.ApiProcessMain"));
    assertFalse(unit.contains("LoadCredential=web-session-aes"));
    assertFalse(unit.contains("ReadWritePaths=/srv/schubert-nk/data/assets"));
    exactEnvTemplate(FIXTURE_API_63E3A42F);
  }

  @Test
  void webDependencyCredentialAndResourceContract() throws Exception {
    String unit = read("schubert-nk-web");
    common(unit, FIXTURE_WEB_BDE14896, "1536M", "30s", "384m", "768m", "128m", "192m");
    exact(unit, "After", "schubert-nk-api.service artemis.service postgresql.service");
    exact(unit, "Requires", "schubert-nk-api.service artemis.service postgresql.service");
    exact(unit, "SupplementaryGroups", "schubert schubert-read");
    assertFalse(unit.contains("ReadWritePaths="));
    credentials(
        unit,
        "db-web",
        "mq-web",
        "web-session-aes-current",
        "web-revoke-aes-current",
        "web-log-aes-current");
    assertTrue(unit.contains("dev.codex.schubert.nk.batch.file.RootServiceLauncher WEB"));
    assertFalse(unit.contains("dev.codex.schubert.nk.web.bootstrap.WebProcessMain"));
    assertFalse(unit.contains("LoadCredential=api-context-aes"));
    assertFalse(unit.contains("LoadCredential=operation-hmac"));
    exactEnvTemplate(FIXTURE_WEB_BDE14896);
  }

  @Test
  void noSecretInEnvironmentOrShellAndNoAutomaticWritableEscalation() throws Exception {
    for (String service : List.of(FIXTURE_API_63E3A42F, FIXTURE_WEB_BDE14896)) {
      String unit = read("schubert-nk-" + service);
      for (String line : unit.lines().toList()) {
        if (line.startsWith("#")) continue;
        assertFalse(line.startsWith("Environment="));
        assertFalse(line.contains("sh -c"));
        assertFalse(line.contains("/bin/sh"));
        assertFalse(line.contains("SetCredential="));
        assertFalse(line.contains("PassEnvironment="));
        assertFalse(line.contains("+ExecStart="));
      }
      exact(unit, "ProtectSystem", "strict");
      exact(unit, "ProtectHome", "true");
      exact(unit, "SendSIGKILL", "no");
      exact(unit, "NoNewPrivileges", "true");
      exact(unit, "RestrictAddressFamilies", "AF_UNIX AF_INET AF_INET6");
      assertEquals(1, unit.lines().filter(line -> line.startsWith("ExecStart=")).count());
      assertEquals(5, unit.lines().filter(line -> line.startsWith("LoadCredential=")).count());
    }
  }

  @Test
  void renderedSyntaxIsAcceptedWithoutStartingService() throws Exception {
    for (String service : List.of(FIXTURE_API_63E3A42F, FIXTURE_WEB_BDE14896)) {
      String name = "schubert-nk-" + service;
      Path directory = Files.createDirectory(temporary.resolve(service));
      String unit = read(name);
      String executable =
          unit.lines().filter(line -> line.startsWith("ExecStart=")).findFirst().orElseThrow();
      Files.writeString(
          directory.resolve(name + ".service"),
          unit.replace(executable, "ExecStart=/bin/true")
              .replace(
                  "WorkingDirectory=/opt/schubert-nk/current/" + service,
                  "WorkingDirectory=" + directory));
      for (String dependency :
          List.of("schubert-nk-expiry-cleanup", "artemis", "postgresql", "schubert-nk-api")) {
        Files.writeString(
            directory.resolve(dependency + ".service"),
            "[Service]\nType=oneshot\nExecStart=/bin/true\n");
      }
      ProcessBuilder process =
          new ProcessBuilder(
              "/usr/bin/systemd-analyze",
              "verify",
              "--man=no",
              directory.resolve(name + ".service").toString());
      process.environment().clear();
      process.environment().putAll(UnitSyntaxFixture.environment(directory));
      process.redirectErrorStream(true);
      Process running = process.start();
      assertTrue(running.waitFor(Duration.ofSeconds(10)));
      String output = new String(running.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
      assertEquals(0, running.exitValue(), output);
      assertEquals("", output);
    }
  }

  @Test
  void isolatedLookupStillReportsProjectSyntaxWarnings() throws Exception {
    Path directory = Files.createDirectory(temporary.resolve("negative"));
    Path unit = directory.resolve("negative.service");
    Files.writeString(
        unit,
        "[Service]\nType=oneshot\nExecStart=/bin/true\nNKInvalidDirectiveForNegativeOracle=yes\n");
    ProcessBuilder process =
        new ProcessBuilder("/usr/bin/systemd-analyze", "verify", "--man=no", unit.toString());
    process.environment().clear();
    process.environment().putAll(UnitSyntaxFixture.environment(directory));
    process.redirectErrorStream(true);
    Process running = process.start();
    assertTrue(running.waitFor(Duration.ofSeconds(10)));
    String output = new String(running.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    // systemd returns zero for unknown directives, so exit zero alone is never
    // a successful syntax oracle. Positive cases above require empty output.
    assertEquals(0, running.exitValue());
    assertTrue(output.contains("Unknown key 'NKInvalidDirectiveForNegativeOracle'"));
    assertTrue(output.contains("negative.service"));
    assertFalse(output.contains("xfs_scrub_all.service"));
  }

  private static String read(String name) throws Exception {
    return Files.readString(UNITS.resolve(name + ".service.template"));
  }

  private static void exactEnvTemplate(String service) throws Exception {
    byte[] actual =
        Files.readAllBytes(ROOT.resolve("src/deployment/config/" + service + ".env.template"));
    assertTrue(
        java.util.Arrays.equals(
            "SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk\n".getBytes(StandardCharsets.US_ASCII),
            actual));
  }

  private static void exact(String unit, String key, String value) {
    List<String> found = new ArrayList<>();
    for (String line : unit.lines().toList()) {
      if (line.startsWith(key + "=")) found.add(line.substring(key.length() + 1));
    }
    assertEquals(List.of(value), found, key);
  }

  private static void credentials(String unit, String... ids) {
    List<String> actual = unit.lines().filter(line -> line.startsWith("LoadCredential=")).toList();
    List<String> expected = new ArrayList<>();
    for (String id : ids) {
      expected.add("LoadCredential=" + id + ":/etc/schubert-nk/credentials/" + id);
    }
    assertEquals(expected, actual);
  }

  private static void common(
      String unit,
      String service,
      String memory,
      String stop,
      String xms,
      String xmx,
      String direct,
      String metaspace) {
    exact(unit, "Type", "simple");
    exact(unit, "User", "schubert-" + service);
    exact(unit, "Group", "schubert-" + service);
    exact(unit, "WorkingDirectory", "/opt/schubert-nk/current/" + service);
    exact(unit, "EnvironmentFile", "/etc/schubert-nk/" + service + ".env");
    exact(unit, "Restart", "on-failure");
    exact(unit, "RestartSec", "5s");
    exact(unit, "StartLimitIntervalSec", "600");
    exact(unit, "StartLimitBurst", "5");
    exact(unit, "TimeoutStartSec", "120s");
    exact(unit, "TimeoutStopSec", stop);
    exact(unit, "MemoryMax", memory);
    exact(unit, "LimitNOFILE", "65536");
    exact(unit, "RuntimeDirectory", "schubert-nk/" + service);
    exact(unit, "UMask", "0027");
    // SS342/SSC137: ! keeps only this Root entry privileged; ordinary exec vectors are
    // independently fixed in FixedServiceExecArgumentsTest and drop every capability.
    exact(
        unit,
        "CapabilityBoundingSet",
        "CAP_SETUID CAP_SETGID CAP_SETPCAP CAP_SYS_PTRACE CAP_DAC_READ_SEARCH");
    assertTrue(
        unit.lines()
            .filter(line -> line.startsWith("ExecStart="))
            .findFirst()
            .orElseThrow()
            .startsWith("ExecStart=!/usr/bin/java "));
    String command =
        unit.lines().filter(line -> line.startsWith("ExecStart=")).findFirst().orElseThrow();
    for (String fixed :
        List.of(
            "/usr/bin/java",
            "--enable-native-access=ALL-UNNAMED",
            "-Dfile.encoding=UTF-8",
            "-Duser.timezone=UTC",
            "-XX:+ExitOnOutOfMemoryError",
            "-XX:MaxDirectMemorySize=" + direct,
            "-XX:MaxMetaspaceSize=" + metaspace,
            "-XX:ReservedCodeCacheSize=128m",
            "-Xms" + xms,
            "-Xmx" + xmx,
            "-Xlog:gc*=info:stdout:time,uptime,level,tags")) {
      assertTrue(command.contains(fixed), fixed);
    }
  }
}
