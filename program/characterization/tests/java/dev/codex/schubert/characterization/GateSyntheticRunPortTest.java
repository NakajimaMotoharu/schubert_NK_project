package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-CHR-SYN001..007 / UI264 SS355. Own synthetic files only, never real CHR qualification. */
final class GateSyntheticRunPortTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Path OWN_INPUT = Path.of(System.getProperty("chr.unitProjectRoot"));
  private static final String PREFIX = "program/characterization/";
  private static final String CONTRACT = PREFIX + "tests/resources/cases/gate-contract.json";
  private static final String BASELINE = PREFIX + "baseline/current/";
  private static final String FIRST = PREFIX + "reports/current/pgpt-gate-20260901-05/";
  private static final String SECOND = PREFIX + "reports/current/pgpt-gate-20260901-06/";
  private static final String A01 = "artifacts/CHR-A01.json";
  private static final String U01 = "artifacts/CHR-U01.json";
  private static final String STATUS = "status";
  @TempDir Path temporaryDirectory;

  @Test
  void completeSyntheticTreeAcceptsIndependentAggregateAndOwnsImmutableReports() throws Exception {
    Path root = fixture("complete");
    var result = validate(root);
    assertEquals(List.of(), result.failures());
    assertTrue(result.passed());
    assertEquals(24, result.metrics().get("caseCount"));
    assertEquals(27, result.metrics().get("baselineFileCount"));
    assertEquals(0, result.metrics().get("failureCount"));
    assertThrows(UnsupportedOperationException.class, () -> result.failures().add("change"));
    assertThrows(UnsupportedOperationException.class, () -> result.metrics().put("change", 1));
  }

  @Test
  void screenshotHashAndUnknownArtifactNamesFailOrIgnoreByExplicitContract() throws Exception {
    Path root = fixture("names");
    Files.writeString(root.resolve(FIRST + "artifacts/x.json"), "ignored-not-a-case");
    Files.writeString(root.resolve(FIRST + "artifacts/CHR-Axx.json"), "ignored-not-a-case");
    Files.writeString(root.resolve(FIRST + "screenshots/readme.txt"), "ignored-not-a-png");
    assertTrue(validate(root).passed());
    Files.writeString(root.resolve(FIRST + "screenshots/CHR-U01-desktop.png"), "changed");
    assertTrue(validate(root).failures().contains("run1_SCREENSHOT_DESKTOP_HASH"));
    Files.delete(root.resolve(FIRST + U01));
    assertTrue(validate(root).failures().contains("run1_MISSING:CHR-U01"));
  }

  @Test
  void nkOnlySupplementalAllowedOnlyForExplicitApprovedCheckAndEvidence() throws Exception {
    Path root = fixture("supplemental");
    Path path = root.resolve(FIRST + "supplemental.json");
    ObjectNode report = (ObjectNode) JSON.readTree(path.toFile());
    ObjectNode result =
        (ObjectNode) report.path("checks").path("CHR-L01").path("web-log-outbox-retry");
    result.put(STATUS, "NK_ONLY");
    JSON.writeValue(path.toFile(), report);
    assertTrue(validate(root).passed());
    result.put(STATUS, "UNKNOWN");
    JSON.writeValue(path.toFile(), report);
    assertTrue(
        validate(root).failures().contains("run1_SUPPLEMENTAL:CHR-L01:web-log-outbox-retry"));
  }

  @Test
  void missingAndMalformedRequiredDocumentsAreIoFailuresNeverPassingGate() throws Exception {
    Path root = fixture("missing");
    Files.delete(root.resolve(CONTRACT));
    assertThrows(IOException.class, () -> validate(root));
    Files.writeString(root.resolve(CONTRACT), "{malformed");
    assertThrows(IOException.class, () -> validate(root));
    Files.delete(root.resolve(SECOND + "inventory.json"));
    Files.copy(
        OWN_INPUT.resolve(CONTRACT), root.resolve(CONTRACT), StandardCopyOption.REPLACE_EXISTING);
    assertTrue(validate(root).failures().contains("run2_INVENTORY_STATUS"));
  }

  @Test
  void requiredEvidenceContainsExactlyOneJsonDocument() throws Exception {
    Path root = fixture("single-document");
    Path file = root.resolve(CONTRACT);
    String document = Files.readString(file);
    Files.writeString(file, document + "\n \t\n");
    assertTrue(validate(root).passed());

    Files.writeString(file, document + "\n{}\n");
    assertThrows(IOException.class, () -> validate(root));
  }

  @Test
  void hashFixedVectorsIncludeEmptyMultiBufferNullAndMissingFile() throws Exception {
    Path empty = temporaryDirectory.resolve("empty");
    Files.write(empty, new byte[0]);
    assertEquals(
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        GateContractValidator.sha256(empty));
    Path million = temporaryDirectory.resolve("million-a");
    byte[] bytes = new byte[1_048_577];
    java.util.Arrays.fill(bytes, (byte) 'a');
    Files.write(million, bytes);
    assertEquals(
        "4a3f0c0c213adea174f9a3d4c13177315b588bdb2e9c1012d3d0bf0453ca0f6a",
        GateContractValidator.sha256(million));
    assertThrows(IllegalArgumentException.class, () -> GateContractValidator.sha256(null));
    assertThrows(
        IOException.class,
        () -> GateContractValidator.sha256(temporaryDirectory.resolve("missing")));
  }

  @Test
  void concurrentSeparateTreesNeverShareFailuresOrInputMutation() throws Exception {
    Path valid = fixture("parallel-valid");
    Path invalid = fixture("parallel-invalid");
    ObjectNode item = (ObjectNode) JSON.readTree(invalid.resolve(FIRST + A01).toFile());
    item.put(STATUS, "FAIL");
    JSON.writeValue(invalid.resolve(FIRST + A01).toFile(), item);
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> validate(valid));
      var second = workers.submit(() -> validate(invalid));
      assertTrue(first.get().passed());
      assertFalse(second.get().passed());
      assertTrue(second.get().failures().contains("run1_STATUS:CHR-A01"));
    }
    assertTrue(validate(valid).passed());
  }

  private Path fixture(String name) throws IOException {
    Path root = temporaryDirectory.resolve(name);
    try (Stream<Path> paths = Files.walk(OWN_INPUT)) {
      for (Path source : paths.sorted().toList()) {
        Path target = root.resolve(OWN_INPUT.relativize(source));
        if (Files.isDirectory(source)) Files.createDirectories(target);
        else Files.copy(source, target, StandardCopyOption.COPY_ATTRIBUTES);
      }
    }
    return root;
  }

  private static GateContractValidator.ValidationResult validate(Path root) throws Exception {
    return GateContractValidator.validate(
        root,
        root.resolve(FIRST),
        root.resolve(SECOND),
        root.resolve(PREFIX + "reports/current-repeat-comparison.json"));
  }
}
