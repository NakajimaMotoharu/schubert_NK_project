package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/** SS341/342/343/SSC104/PG334; CUNIT001..003 static candidate only, not an installed Unit. */
final class CleanupServiceUnitTest {
  private static String unit() throws IOException {
    return Files.readString(
        Path.of(
            System.getProperty("nk.pt.repository"),
            "src/deployment/systemd/schubert-nk-cleanup.service.template"));
  }

  private static void exact(String content, String key, String value) {
    assertEquals(1, content.lines().filter(line -> line.equals(key + "=" + value)).count(), key);
    assertEquals(1, content.lines().filter(line -> line.startsWith(key + "=")).count(), key);
  }

  @Test
  void cunit001FixedRootChildAndRealExecutable() throws Exception {
    String content = unit();
    exact(content, "Type", "oneshot");
    exact(content, "User", "root");
    exact(content, "Group", "root");
    exact(content, "After", "postgresql.service schubert-nk-backup.service");
    exact(content, "Requires", "postgresql.service");
    assertEquals(
        1,
        content
            .lines()
            .filter(
                line ->
                    line.equals(
                        "LoadCredential=cleanup-request:/run/schubert-nk/cleanup-request/cleanup-request"))
            .count());
    assertTrue(content.contains("dev.codex.schubert.nk.batch.file.CleanupProcessMain"));
    assertFalse(content.contains("/bin/true"));
    exact(content, "SuccessExitStatus", "10");
  }

  @Test
  void cunit002PrivateBatchRoleAndNoSecretEnvironment() throws Exception {
    String content = unit();
    assertEquals(
        1,
        content
            .lines()
            .filter(
                line ->
                    line.equals("LoadCredential=db-batch:/etc/schubert-nk/credentials/db-batch"))
            .count());
    assertEquals(3, content.lines().filter(line -> line.startsWith("LoadCredential=")).count());
    assertEquals(
        1,
        content
            .lines()
            .filter(
                line ->
                    line.equals(
                        "LoadCredential=maintenance-owner:/run/schubert-nk/cleanup-request/maintenance-owner"))
            .count());
    assertFalse(content.contains("SetCredential="));
    assertFalse(content.contains("EnvironmentFile="));
    assertFalse(content.contains("ExecStartPre="));
    assertFalse(content.contains("PassEnvironment="));
  }

  @Test
  void cunit003FailureBlocksBrokerAndNoForcedKill() throws Exception {
    String content = unit();
    exact(
        content,
        "Before",
        "artemis.service schubert-nk-api.service schubert-nk-web.service caddy.service");
    exact(content, "Restart", "no");
    exact(content, "TimeoutStartSec", "30min");
    exact(content, "TimeoutStopSec", "60s");
    exact(content, "KillMode", "control-group");
    exact(content, "SendSIGKILL", "no");
    exact(content, "ProtectSystem", "strict");
    exact(content, "NoNewPrivileges", "true");
    exact(content, "CapabilityBoundingSet", "CAP_SYS_PTRACE CAP_DAC_OVERRIDE");
    exact(content, "AmbientCapabilities", "");
    exact(
        content,
        "ReadWritePaths",
        "/srv/schubert-nk/data/transfer /run/schubert-nk/maintenance /run/schubert-nk/cleanup-request");
  }

  @Test
  void cunit004ExpiryHasFixedGenuineEntryAndSameLimitedRootObservation() throws Exception {
    String content =
        Files.readString(
            Path.of(
                System.getProperty("nk.pt.repository"),
                "src/deployment/systemd/schubert-nk-expiry-cleanup.service.template"));
    exact(content, "Type", "oneshot");
    exact(content, "User", "root");
    exact(content, "Group", "root");
    exact(content, "After", "postgresql.service artemis.service");
    exact(content, "Requires", "postgresql.service artemis.service");
    exact(content, "CapabilityBoundingSet", "CAP_SYS_PTRACE CAP_DAC_OVERRIDE");
    exact(content, "AmbientCapabilities", "");
    exact(content, "NoNewPrivileges", "true");
    exact(content, "ProtectSystem", "strict");
    exact(content, "Restart", "no");
    exact(content, "RemainAfterExit", "yes");
    exact(content, "SuccessExitStatus", "10");
    exact(content, "TimeoutStartSec", "10min");
    exact(content, "TimeoutStopSec", "60s");
    exact(content, "KillMode", "control-group");
    exact(content, "SendSIGKILL", "no");
    exact(content, "Delegate", "no");
    assertEquals(5, content.lines().filter(line -> line.startsWith("LoadCredential=")).count());
    for (String credential :
        java.util.List.of(
            "expiry-request:/run/schubert-nk/expiry-request/expiry-request",
            "maintenance-owner:/run/schubert-nk/expiry-request/maintenance-owner",
            "db-batch:/etc/schubert-nk/credentials/db-batch",
            "mq-maintenance:/etc/schubert-nk/credentials/mq-maintenance",
            "mq-ops:/etc/schubert-nk/credentials/mq-ops")) {
      assertEquals(
          1, content.lines().filter(line -> line.equals("LoadCredential=" + credential)).count());
    }
    assertEquals(
        1,
        content
            .lines()
            .filter(
                line ->
                    line.startsWith("ExecStart=/usr/bin/java ")
                        && line.endsWith(
                            "dev.codex.schubert.nk.batch.file.CleanupProcessMain --expiry"))
            .count());
    assertFalse(content.contains("/bin/true"));
    assertFalse(content.contains("SetCredential="));
    assertFalse(content.contains("PassEnvironment="));
    assertFalse(content.contains("EnvironmentFile="));
    assertFalse(content.contains("ReadWritePaths="));
  }
}
