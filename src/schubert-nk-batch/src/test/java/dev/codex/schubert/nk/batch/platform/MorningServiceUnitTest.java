package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/342/343/PG339/BUG316; PT-OPS-MUNIT001-003. */
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
    exact(content, "Type", "simple");
    exact(content, "User", "root");
    exact(content, "Group", "root");
    exact(content, "After", "postgresql.service");
    exact(content, "Requires", "postgresql.service");
    assertTrue(content.contains("dev.codex.schubert.nk.batch.file.MorningProcessMain"));
    assertFalse(content.contains("/bin/true"));
    assertFalse(content.contains("SuccessExitStatus="));
  }

  @Test
  void munit002NoUnscopedInputsOrSuccessOverride() throws Exception {
    String content = unit();
    assertFalse(content.contains("EnvironmentFile="));
    assertFalse(content.contains("PassEnvironment="));
    // SS343 §6.15 requires precisely this systemd-private batch credential even while the
    // remaining parent path is fail-closed. No ordinary service catalog or env fallback.
    exact(content, "LoadCredential", "db-batch:/etc/schubert-nk/credentials/db-batch");
    assertFalse(content.contains("SetCredentialEncrypted="));
    assertFalse(content.contains("SetCredential="));
    assertFalse(content.contains("ExecStartPre="));
    assertFalse(content.contains("ReadWritePaths="));
  }

  @Test
  void munit003DependencyAndNoForcedKill() throws Exception {
    String content = unit();
    exact(
        content,
        "Before",
        "schubert-nk-backup.service schubert-nk-cleanup.service artemis.service schubert-nk-expiry-cleanup.service schubert-nk-api.service schubert-nk-web.service caddy.service");
    exact(content, "Restart", "no");
    exact(content, "TimeoutStartSec", "30min");
    exact(content, "TimeoutStopSec", "60s");
    exact(content, "KillMode", "control-group");
    exact(content, "SendSIGKILL", "no");
    exact(content, "ProtectSystem", "strict");
    exact(content, "NoNewPrivileges", "true");
    exact(content, "CapabilityBoundingSet", "");
    exact(content, "AmbientCapabilities", "");
  }
}
