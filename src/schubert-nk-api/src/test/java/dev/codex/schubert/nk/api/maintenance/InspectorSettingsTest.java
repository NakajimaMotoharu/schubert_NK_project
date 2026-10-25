package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** PT-DB-INBOX-209..211; independent startup boundaries, no IO. */
final class InspectorSettingsTest {
  private static final Path ROOT = Path.of("/run/credentials/schubert-nk-inbox-inspector.service");
  private static final String URL = "jdbc:postgresql://127.0.0.1:5432/schubert_nk";

  @Test
  void validSnapshot() {
    var input = new HashSet<>(Set.of("fp1", "old-v.2"));
    var settings = new InspectorSettings(ROOT, URL, input);
    input.clear();
    assertEquals(ROOT, settings.credentialRoot());
    assertEquals(URL, settings.databaseUrl());
    assertEquals(Set.of("fp1", "old-v.2"), settings.fingerprintVersions());
    assertThrows(UnsupportedOperationException.class, () -> settings.fingerprintVersions().clear());
    assertEquals("InspectorSettings[REDACTED]", settings.toString());
  }

  @Test
  void invalidSettings() {
    assertThrows(NullPointerException.class, () -> new InspectorSettings(null, URL, Set.of("v")));
    assertThrows(NullPointerException.class, () -> new InspectorSettings(ROOT, null, Set.of("v")));
    assertThrows(NullPointerException.class, () -> new InspectorSettings(ROOT, URL, null));
    var nullElement = new HashSet<String>();
    nullElement.add(null);
    assertThrows(NullPointerException.class, () -> new InspectorSettings(ROOT, URL, nullElement));
    for (String root : List.of("", "/", "relative", "/run/../credentials", "/run/./credentials"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new InspectorSettings(Path.of(root), URL, Set.of("v")));
    for (String url :
        List.of(
            "",
            "jdbc:postgresql://localhost:5432/db",
            URL + "?password=public-canary",
            "jdbc:postgresql://127.0.0.1:0/db",
            "jdbc:postgresql://127.0.0.1:65536/db"))
      assertThrows(
          IllegalArgumentException.class, () -> new InspectorSettings(ROOT, url, Set.of("v")));
    assertThrows(IllegalArgumentException.class, () -> new InspectorSettings(ROOT, URL, Set.of()));
    for (String version : List.of("", "-v", "a b", "é", "a".repeat(17)))
      assertThrows(
          IllegalArgumentException.class, () -> new InspectorSettings(ROOT, URL, Set.of(version)));
  }

  @Test
  void sharedValidation() {
    for (String version : List.of("v", "a".repeat(16))) {
      for (int port : new int[] {1, 65535}) {
        String url = "jdbc:postgresql://127.0.0.1:" + port + "/db";
        var settings = new InspectorSettings(ROOT, url, Set.of(version));
        assertEquals("db", InspectorDatabaseConnections.databaseName(settings.databaseUrl()));
        assertEquals(
            Set.of(version), InspectorSettings.requireVersions(settings.fingerprintVersions()));
      }
    }
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> InspectorDatabaseConnections.databaseName(URL + "#UNTRUSTED"));
    assertEquals("inspector database URL is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
