package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;

/** BCATALOG001: SS341 SSC121 independent public-name catalog; no secret/archive content. */
final class MorningBackupCatalogTest {
  @Test
  void currentRecoveryCatalogIncludesInspectorAndSeparatesRuntimeFromEncryptedCredentials() {
    assertEquals(
        List.of(
            "common.yml",
            "api.yml",
            "web.yml",
            "batch.yml",
            "api.env",
            "web.env",
            "backup-profile.json",
            "inbox-inspector.env"),
        MorningBackupArtifacts.CONFIG);
    assertEquals(
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
            "db-inbox-inspector"),
        MorningBackupArtifacts.CREDENTIALS);
    assertThrows(
        UnsupportedOperationException.class,
        () -> MorningBackupArtifacts.CONFIG.add("runtime.env"));
    assertThrows(
        UnsupportedOperationException.class, () -> MorningBackupArtifacts.CREDENTIALS.clear());
  }
}
