package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-OPS-BMODE197001..003; independent SS343 6.9/SSC197 literal mode oracle. */
final class MorningBackupInputModeTest {
  @Test
  void fixedPublicConfigurationIncludesStaticInspectorAt0640() {
    for (String name :
        List.of(
            "common.yml",
            "api.yml",
            "web.yml",
            "batch.yml",
            "backup-profile.json",
            "inbox-inspector.env"))
      assertEquals(0100640, MorningBackupArtifacts.inputMode(name, false), name);
    assertEquals(0100600, MorningBackupArtifacts.inputMode("api.env", false));
    assertEquals(0100600, MorningBackupArtifacts.inputMode("web.env", false));
  }

  @Test
  void everyFixedCredentialRemains0600WithoutUsingProductionCatalogForExpected() {
    for (String name :
        List.of(
            "db-api",
            "db-web",
            "db-batch",
            "db-migration",
            "backup-pgpass",
            "mq-api",
            "mq-web",
            "mq-maintenance",
            "mq-ops",
            "api-context-aes-current",
            "api-inbox-response-aes-current",
            "operation-hmac-current",
            "web-session-aes-current",
            "web-revoke-aes-current",
            "web-log-aes-current",
            "artemis-users",
            "db-inbox-inspector"))
      assertEquals(0100600, MorningBackupArtifacts.inputMode(name, true), name);
  }

  @Test
  void missingUnknownAndCrossCatalogNamesAreNeverAdmitted() {
    for (boolean credential : List.of(false, true)) {
      assertThrows(
          NullPointerException.class, () -> MorningBackupArtifacts.inputMode(null, credential));
      for (String name : List.of("", "unknown.env", "../api.env", "runtime/inbox-inspector.env"))
        assertThrows(
            IllegalArgumentException.class,
            () -> MorningBackupArtifacts.inputMode(name, credential));
    }
    assertThrows(
        IllegalArgumentException.class, () -> MorningBackupArtifacts.inputMode("db-api", false));
    assertThrows(
        IllegalArgumentException.class, () -> MorningBackupArtifacts.inputMode("api.env", true));
    assertThrows(
        IllegalArgumentException.class,
        () -> MorningBackupArtifacts.inputMode("inbox-inspector.env", true));
  }
}
