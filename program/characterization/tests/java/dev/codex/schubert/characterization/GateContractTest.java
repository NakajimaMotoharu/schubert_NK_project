package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class GateContractTest {
  private static final ObjectMapper JSON = new ObjectMapper();

  @Test
  void catalogHasExactlyTwentyFourUniqueCasesAndOnlyN01IsNkOnly() throws Exception {
    JsonNode catalog = resource("cases/catalog.json");
    List<String> ids = new ArrayList<>();
    List<String> nkOnly = new ArrayList<>();
    for (JsonNode item : catalog.path("cases")) {
      ids.add(item.path("id").asText());
      if ("NK_ONLY".equals(item.path("current").asText())) nkOnly.add(item.path("id").asText());
      assertEquals("RUN", item.path("nk").asText());
    }
    assertEquals(24, ids.size());
    assertEquals(24, new HashSet<>(ids).size());
    assertEquals(List.of("CHR-N01"), nkOnly);
  }

  @Test
  void differenceAllowlistIsCompleteUniqueAndNarrow() throws Exception {
    JsonNode dif = resource("cases/dif-allowlist.json");
    Set<String> ids = new HashSet<>();
    for (JsonNode item : dif.path("differences")) {
      String id = item.path("id").asText();
      assertTrue(ids.add(id), "duplicate " + id);
      assertFalse(item.path("field").asText().contains("*"));
      assertFalse(item.path("cases").isEmpty());
    }
    assertEquals(16, ids.size());
    for (int index = 1; index <= 16; index++) {
      assertTrue(ids.contains("DIF-%03d".formatted(index)));
    }
  }

  @Test
  void expectedBaselineContainsAllStaticCounts() throws Exception {
    JsonNode expected = resource("fixtures/expected.json");
    assertEquals(59, expected.path("sourceFileCount").asInt());
    assertEquals(18, expected.path("documentFileCount").asInt());
    assertEquals(59627, expected.path("masterFileCount").asInt());
    assertEquals(99661, expected.path("scenarioEntryCount").asInt());
    assertEquals(20, expected.path("videoCount").asInt());
    assertEquals(129, expected.path("musicCount").asInt());
  }

  @Test
  void browserManifestPinsExecutableRevisionAndLocale() throws Exception {
    JsonNode browser = resource("browser/manifest.json");
    assertEquals("chromium", browser.path("browser").asText());
    assertEquals(1187, browser.path("browserRevision").asInt());
    assertEquals("ja-JP", browser.path("locale").asText());
    assertEquals("Asia/Tokyo", browser.path("timezone").asText());
  }

  @Test
  void caddyFixturePreservesAllForwardedRequestHeaders() {
    String config =
        CharacterizationEnvironment.renderCaddyConfig(55162, 46962, Path.of("fixture-caddy-data"));
    assertTrue(config.contains("header_up X-Real-IP {remote_host}"));
    assertTrue(config.contains("header_up X-Forwarded-Host {hostport}"));
    assertTrue(config.contains("header_up X-Forwarded-Port {port}"));
    assertTrue(config.contains("header_up X-Forwarded-Proto https"));
  }

  @Test
  void secretScannerHandlesBinaryEvidenceWithoutUtf8Decoding(@TempDir Path temporaryDirectory)
      throws Exception {
    Path binary = temporaryDirectory.resolve("evidence.png");
    Files.write(binary, new byte[] {(byte) 0x89, 0x50, 0x4e, 0x47, (byte) 0xff, 0x00});
    assertFalse(GateCli.containsAny(binary, List.of("test-secret")));
    Files.write(
        binary, "prefix-test-secret-suffix".getBytes(java.nio.charset.StandardCharsets.UTF_8));
    assertTrue(GateCli.containsAny(binary, List.of("test-secret")));
  }

  @Test
  void strengthenedGateContractAcceptsTwoCompleteRepeatableRuns() throws Exception {
    Path projectRoot = Path.of(System.getProperty("chr.unitProjectRoot"));
    Path currentReports = projectRoot.resolve("program/characterization/reports/current");
    GateContractValidator.ValidationResult result =
        GateContractValidator.validate(
            projectRoot,
            currentReports.resolve("pgpt-gate-20260901-05"),
            currentReports.resolve("pgpt-gate-20260901-06"),
            projectRoot.resolve("program/characterization/reports/current-repeat-comparison.json"));
    assertTrue(result.passed(), () -> "unexpected failures: " + result.failures());
    assertEquals(24, result.metrics().get("caseCount"));
    assertEquals(0, result.metrics().get("failureCount"));
  }

  /** PT-CHR-G06-STREAM-001 / BUG2811: literal byte offsets, not scanner-generated expected. */
  @Test
  void fullByteScanIncludesLargeFilesBoundariesPrefixesEmptyAndIo(@TempDir Path directory)
      throws Exception {
    Path binary = directory.resolve("binary.dat");
    byte[] bytes = new byte[10 * 1024 * 1024 + 37];
    byte[] marker = "合成-marker-aaaab".getBytes(java.nio.charset.StandardCharsets.UTF_8);
    for (int offset : List.of(0, 8191, bytes.length - marker.length)) {
      java.util.Arrays.fill(bytes, (byte) 0xff);
      System.arraycopy(marker, 0, bytes, offset, marker.length);
      Files.write(binary, bytes);
      assertTrue(GateCli.containsAny(binary, List.of("unmatched", "合成-marker-aaaab")));
      assertFalse(GateCli.containsAny(binary, List.of("marker-aaaac", "")));
    }
    Files.writeString(binary, "aaaaab");
    assertTrue(GateCli.containsAny(binary, List.of("aaaab")));
    assertFalse(GateCli.containsAny(binary, List.of("aaaaac")));
    assertThrows(IllegalArgumentException.class, () -> GateCli.containsAny(null, List.of("x")));
    assertThrows(IllegalArgumentException.class, () -> GateCli.containsAny(binary, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> GateCli.containsAny(binary, java.util.Arrays.asList("x", null)));
    Files.write(binary, new byte[0]);
    assertFalse(GateCli.containsAny(binary, List.of("x", "")));
    assertFalse(GateCli.containsAny(binary, List.of()));
    assertThrows(
        java.io.IOException.class,
        () -> GateCli.containsAny(directory.resolve("absent"), List.of("x")));

    // Only owned synthetic files; no operational credential/master/current capture is read.
    Path reports = directory.resolve("project/program/characterization/reports");
    Files.createDirectories(reports);
    Path users = directory.resolve("synthetic-users.txt");
    Files.writeString(users, "user=synthetic-marker-only\npass=synthetic-other-only\n");
    java.util.Arrays.fill(bytes, (byte) 0xff);
    byte[] canary = "synthetic-marker-only".getBytes(java.nio.charset.StandardCharsets.UTF_8);
    System.arraycopy(canary, 0, bytes, bytes.length - canary.length, canary.length);
    Files.write(reports.resolve("large.bin"), bytes);
    assertEquals(
        List.of("program/characterization/reports/large.bin"),
        GateCli.secretScan(directory.resolve("project"), users));
  }

  private static JsonNode resource(String name) throws Exception {
    try (InputStream input = GateContractTest.class.getClassLoader().getResourceAsStream(name)) {
      if (input == null) throw new IllegalStateException("resource missing: " + name);
      return JSON.readTree(input);
    }
  }
}
