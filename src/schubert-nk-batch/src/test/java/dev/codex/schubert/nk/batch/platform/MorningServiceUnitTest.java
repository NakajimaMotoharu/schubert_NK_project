package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/342/343/PG339/363/BUG316/322; PT-OPS-MUNIT001-004. */
final class MorningServiceUnitTest {
  private static String unit() throws IOException {
    return Files.readString(
        Path.of(
            System.getProperty("nk.pt.repository"),
            "src/deployment/systemd/schubert-nk-morning-controller.service.template"));
  }

  private static void exact(String content, String key, String value) {
    assertEquals(1, content.lines().filter(line -> line.equals(key + "=" + value)).count(), key);
    assertEquals(1, content.lines().filter(line -> line.startsWith(key + "=")).count(), key);
  }

  @Test
  void munit001FixedRootActorAndRealJavaEntrypoint() throws Exception {
    String content = unit();
    exact(content, "Type", "oneshot");
    exact(content, "User", "root");
    exact(content, "Group", "root");
    exact(content, "After", "postgresql.service");
    exact(content, "Requires", "postgresql.service");
    assertTrue(content.contains("dev.codex.schubert.nk.batch.file.MorningProcessMain"));
    assertFalse(content.contains("/bin/true"));
    // SSC278/BUG1162: only normal WARNING10 joins systemd's default SUCCESS0.
    // Unit success alone never substitutes for same-root DONE/gates/owned close.
    exact(content, "SuccessExitStatus", "10");
  }

  @Test
  void munit002NoUnscopedInputsOrSuccessOverride() throws Exception {
    String content = unit();
    assertFalse(content.contains("EnvironmentFile="));
    assertFalse(content.contains("PassEnvironment="));
    // SS343 §6.15 requires precisely this systemd-private batch credential even while the
    // remaining parent path is fail-closed. No ordinary service catalog or env fallback.
    for (String credential : java.util.List.of("db-batch", "mq-ops")) {
      assertEquals(
          1,
          content
              .lines()
              .filter(
                  line ->
                      line.equals(
                          "LoadCredential="
                              + credential
                              + ":/etc/schubert-nk/credentials/"
                              + credential))
              .count());
    }
    assertEquals(2, content.lines().filter(line -> line.startsWith("LoadCredential=")).count());
    assertFalse(content.contains("SetCredentialEncrypted="));
    assertFalse(content.contains("SetCredential="));
    assertFalse(content.contains("ExecStartPre="));
    // SSC109: mutation roots only; shared /run and /var remain private RO.
    exact(
        content,
        "ReadWritePaths",
        "/run/schubert-nk /var/lib/schubert-nk/maintenance /srv/schubert-nk/backup");
  }

  @Test
  void munit003DependencyAndNoForcedKill() throws Exception {
    String content = unit();
    assertFalse(content.lines().anyMatch(line -> line.startsWith("Before=")));
    exact(content, "Restart", "no");
    exact(content, "TimeoutStartSec", "30min");
    exact(content, "TimeoutStopSec", "60s");
    exact(content, "KillMode", "control-group");
    exact(content, "SendSIGKILL", "no");
    exact(content, "ProtectSystem", "strict");
    exact(content, "NoNewPrivileges", "true");
    exact(content, "CapabilityBoundingSet", "CAP_SYS_PTRACE CAP_DAC_OVERRIDE");
    exact(content, "AmbientCapabilities", "");
  }

  @Test
  void munit004ParentOnlyTargetCannotParallelStartChildren() throws Exception {
    String content =
        Files.readString(
            Path.of(
                System.getProperty("nk.pt.repository"),
                "src/deployment/systemd/schubert-nk-morning.target.template"));
    exact(content, "Requires", "schubert-nk-morning-controller.service");
    exact(content, "After", "schubert-nk-morning-controller.service");
    assertFalse(content.lines().anyMatch(line -> line.startsWith("Wants=")));
    for (String child :
        new String[] {
          "schubert-nk-backup.service",
          "schubert-nk-cleanup.service",
          "artemis.service",
          "schubert-nk-expiry-cleanup.service",
          "schubert-nk-api.service",
          "schubert-nk-web.service",
          "caddy.service"
        }) {
      assertFalse(content.contains(child));
    }
  }
}
