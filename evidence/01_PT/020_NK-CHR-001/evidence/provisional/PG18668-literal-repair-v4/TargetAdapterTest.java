package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Current/NK同一case runner境界。PT-CHR-NK-001。 */
class TargetAdapterTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Path PROJECT_ROOT =
      Path.of(System.getProperty("chr.unitProjectRoot")).toAbsolutePath().normalize();

  @TempDir Path temporaryDirectory;

  @Test
  void currentAndNkUseSameCatalogWithOnlyDeclaredApplicabilityDifference() throws Exception {
    JsonNode catalog =
        JSON.readTree(
            PROJECT_ROOT
                .resolve("program/characterization/tests/resources/cases/catalog.json")
                .toFile());
    Path reports = temporaryDirectory.resolve("reports");
    TargetAdapter current =
        TargetAdapter.create(
            "CURRENT",
            "https://LOCALHOST:55162",
            reports,
            reports.resolve("current/run-01"),
            Set.of("LocalHost", "127.0.0.1"));
    TargetAdapter nk =
        TargetAdapter.create(
            "nk",
            "https://127.0.0.1:56162/",
            reports,
            reports.resolve("nk/run-01"),
            Set.of("localhost", "127.0.0.1"));

    List<String> currentCases = current.executableCaseIds(catalog);
    List<String> nkCases = nk.executableCaseIds(catalog);
    assertEquals(23, currentCases.size());
    assertFalse(currentCases.contains("CHR-N01"));
    assertEquals(24, nkCases.size());
    assertTrue(nkCases.contains("CHR-N01"));
    assertEquals(TargetAdapter.Target.CURRENT, current.target());
    assertEquals("current", current.target().externalName());
    assertEquals("nk", nk.target().externalName());
    assertEquals("https://localhost:55162/", current.baseUri().toString());
    assertEquals(reports.resolve("current/run-01").toAbsolutePath(), current.evidenceRoot());
    assertEquals(
        "https://localhost:55162/search?game=NUKITASHI1#entry-1",
        current.endpoint("/search?game=NUKITASHI1#entry-1").toString());
    assertEquals(
        reports.resolve("current/run-01/artifacts/CHR-A01.json").toAbsolutePath(),
        current.caseArtifact("CHR-A01"));
  }

  @Test
  void adapterRejectsNullUnknownExternalAndOverwriteInputs() throws Exception {
    Path reports = temporaryDirectory.resolve("invalid-reports");
    Path evidence = reports.resolve("run");
    Set<String> hosts = Set.of("localhost");
    assertCreateFails(null, "https://localhost", reports, evidence, hosts);
    assertCreateFails(" ", "https://localhost", reports, evidence, hosts);
    assertCreateFails("other", "https://localhost", reports, evidence, hosts);
    assertCreateFails("current", null, reports, evidence, hosts);
    assertCreateFails("current", " ", reports, evidence, hosts);
    assertCreateFails("current", "https://localhost", null, evidence, hosts);
    assertCreateFails("current", "https://localhost", reports, null, hosts);
    assertCreateFails("current", "https://localhost", reports, evidence, null);
    assertCreateFails("current", "https://localhost", reports, evidence, Set.of());
    assertCreateFails("current", "https://localhost", reports, evidence, Set.of(" "));
    Set<String> nullHost = new HashSet<>();
    nullHost.add(null);
    assertCreateFails("current", "https://localhost", reports, evidence, nullHost);

    for (String url :
        List.of(
            "http://localhost",
            "https://external.example",
            "mailto:test@example.com",
            "https://user@localhost",
            "https://localhost?query=x",
            "https://localhost#fragment",
            "https://localhost/base")) {
      assertCreateFails("current", url, reports, evidence, hosts);
    }
    assertCreateFails("current", "https://localhost", reports, reports, hosts);
    assertCreateFails(
        "current", "https://localhost", reports, temporaryDirectory.resolve("outside"), hosts);
    Files.createDirectories(evidence);
    assertCreateFails("current", "https://localhost", reports, evidence, hosts);

    Path linkedEvidence = reports.resolve("linked");
    Files.createDirectories(reports);
    Files.createSymbolicLink(linkedEvidence, temporaryDirectory.resolve("missing-link-target"));
    assertCreateFails("current", "https://localhost", reports, linkedEvidence, hosts);
  }

  @Test
  void adapterRejectsCrossOriginPathsBadCaseIdsAndMalformedCatalogs() throws Exception {
    Path reports = temporaryDirectory.resolve("contract-reports");
    TargetAdapter current =
        TargetAdapter.create(
            "current",
            "https://localhost",
            reports,
            reports.resolve("current/run"),
            Set.of("localhost"));
    TargetAdapter nk =
        TargetAdapter.create(
            "nk", "https://localhost", reports, reports.resolve("nk/run"), Set.of("localhost"));
    assertThrows(IllegalArgumentException.class, () -> current.endpoint(null));
    assertThrows(IllegalArgumentException.class, () -> current.endpoint("relative"));
    assertThrows(IllegalArgumentException.class, () -> current.endpoint("//external.example/path"));
    assertThrows(IllegalArgumentException.class, () -> current.caseArtifact(null));
    assertThrows(IllegalArgumentException.class, () -> current.caseArtifact("bad"));
    assertThrows(IllegalArgumentException.class, () -> current.executableCaseIds(null));
    assertThrows(
        IllegalArgumentException.class,
        () -> current.executableCaseIds(JSON.createObjectNode().put("cases", "bad")));

    ObjectNode original = catalogCopy();
    ObjectNode badId = original.deepCopy();
    ((ObjectNode) cases(badId).get(0)).put("id", "bad");
    assertThrows(IllegalArgumentException.class, () -> current.executableCaseIds(badId));

    ObjectNode duplicate = original.deepCopy();
    ((ObjectNode) cases(duplicate).get(1)).put("id", "CHR-A01");
    assertThrows(IllegalArgumentException.class, () -> current.executableCaseIds(duplicate));

    ObjectNode currentUnknown = original.deepCopy();
    ((ObjectNode) cases(currentUnknown).get(0)).put("current", "SKIP");
    assertThrows(IllegalArgumentException.class, () -> current.executableCaseIds(currentUnknown));

    ObjectNode currentNkOnlyWrongCase = original.deepCopy();
    ((ObjectNode) cases(currentNkOnlyWrongCase).get(0)).put("current", "NK_ONLY");
    assertThrows(
        IllegalArgumentException.class, () -> current.executableCaseIds(currentNkOnlyWrongCase));

    ObjectNode currentN01Unknown = original.deepCopy();
    ((ObjectNode) cases(currentN01Unknown).get(22)).put("current", "SKIP");
    assertThrows(
        IllegalArgumentException.class, () -> current.executableCaseIds(currentN01Unknown));

    ObjectNode nkUnknown = original.deepCopy();
    ((ObjectNode) cases(nkUnknown).get(0)).put("nk", "NK_ONLY");
    assertThrows(IllegalArgumentException.class, () -> nk.executableCaseIds(nkUnknown));

    ObjectNode shortCatalog = original.deepCopy();
    cases(shortCatalog).remove(23);
    assertThrows(IllegalArgumentException.class, () -> current.executableCaseIds(shortCatalog));
  }

  private static ObjectNode catalogCopy() throws Exception {
    return (ObjectNode)
        JSON.readTree(
            PROJECT_ROOT
                .resolve("program/characterization/tests/resources/cases/catalog.json")
                .toFile());
  }

  private static ArrayNode cases(ObjectNode catalog) {
    return (ArrayNode) catalog.path("cases");
  }

  private static void assertCreateFails(
      String target, String baseUrl, Path reports, Path evidence, Set<String> hosts) {
    assertThrows(
        IllegalArgumentException.class,
        () -> TargetAdapter.create(target, baseUrl, reports, evidence, hosts));
  }
}
