package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/** SS321/341/342/343 and SSC103; independent literal unit contract, not a broker start claim. */
final class ArtemisServiceUnitTest {
  private static final String DIRECTIVE_TRUE = "true";

  private static String unit() throws IOException {
    return Files.readString(
        Path.of(System.getProperty("nk.pt.repository"), "src/deployment/systemd/artemis.service"));
  }

  private static void exact(String unit, String key, String value) {
    assertEquals(1, unit.lines().filter(line -> line.equals(key + "=" + value)).count(), key);
    assertEquals(1, unit.lines().filter(line -> line.startsWith(key + "=")).count(), key);
  }

  @Test
  void artunit001RealFixedDependencyIdentityAndInstance() throws Exception {
    String unit = unit();
    exact(unit, "After", "schubert-nk-cleanup.service");
    exact(unit, "Requires", "schubert-nk-cleanup.service");
    exact(unit, "User", "schubert-artemis");
    exact(unit, "Group", "schubert-artemis");
    exact(unit, "WorkingDirectory", "/var/lib/schubert-nk/artemis");
    exact(unit, "ExecStart", "/var/lib/schubert-nk/artemis/bin/artemis run");
    assertFalse(unit.contains("/var/lib/artemis/bin/artemis"));
    assertFalse(unit.contains("/bin/true"));
    assertFalse(unit.contains("ignore-dependencies"));
  }

  @Test
  void artunit002PrivateHashedCredentialIsFixedReadOnlyMount() throws Exception {
    String unit = unit();
    exact(unit, "LoadCredential", "artemis-users:/etc/schubert-nk/credentials/artemis-users");
    exact(
        unit,
        "BindReadOnlyPaths",
        "/run/credentials/artemis.service/artemis-users:/var/lib/schubert-nk/artemis/etc/artemis-users.properties");
    assertEquals(0, unit.lines().filter(line -> line.startsWith("SetCredential=")).count());
    assertEquals(0, unit.lines().filter(line -> line.startsWith("PassEnvironment=")).count());
    assertFalse(unit.contains("artemis-password"));
    assertFalse(unit.contains("/etc/schubert-nk/credentials/mq-ops"));
  }

  @Test
  void artunit003ExactStopAndResourceLimits() throws Exception {
    String unit = unit();
    exact(unit, "Type", "simple");
    exact(unit, "Restart", "on-failure");
    exact(unit, "SuccessExitStatus", "143");
    exact(unit, "RestartSec", "5s");
    exact(unit, "StartLimitIntervalSec", "600");
    exact(unit, "StartLimitBurst", "5");
    exact(unit, "TimeoutStartSec", "120s");
    exact(unit, "TimeoutStopSec", "60s");
    exact(unit, "KillMode", "control-group");
    exact(unit, "SendSIGKILL", "no");
    exact(unit, "MemoryMax", "2048M");
    exact(unit, "LimitNOFILE", "65536");
    exact(
        unit,
        "Environment",
        "\"JAVA_ARGS=-Xms768m -Xmx1024m -XX:MaxDirectMemorySize=256m -XX:MaxMetaspaceSize=192m"
            + " -XX:+ExitOnOutOfMemoryError -Dfile.encoding=UTF-8 -Duser.timezone=UTC\"");
  }

  @Test
  void artunit004HardeningAndNoHostSecretMutation() throws Exception {
    String unit = unit();
    exact(
        unit,
        "ReadWritePaths",
        "/var/lib/schubert-nk/artemis/data /var/lib/schubert-nk/artemis/log"
            + " /var/lib/schubert-nk/artemis/tmp /var/lib/schubert-nk/artemis/lock");
    exact(unit, "UMask", "0077");
    exact(unit, "NoNewPrivileges", DIRECTIVE_TRUE);
    exact(unit, "CapabilityBoundingSet", "");
    exact(unit, "AmbientCapabilities", "");
    exact(unit, "ProtectSystem", "strict");
    exact(unit, "ProtectHome", DIRECTIVE_TRUE);
    exact(unit, "ProtectControlGroups", DIRECTIVE_TRUE);
    exact(unit, "PrivateTmp", DIRECTIVE_TRUE);
    exact(unit, "RestrictAddressFamilies", "AF_UNIX AF_INET AF_INET6");
    assertFalse(unit.contains("ExecStartPre="));
    assertFalse(unit.contains("ExecStopPost="));
    assertFalse(unit.contains("ReadWritePaths=/etc"));
  }
}
