package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** DIF narrow-allowlist oracle. PT-CHR-G05-003/004, PT-CHR-NK-002。 */
class ArtifactComparatorTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Path SOURCE_ROOT =
      Path.of(System.getProperty("chr.unitProjectRoot")).toAbsolutePath().normalize();
  private static final List<String> CASE_IDS =
      List.of(
          "CHR-A01", "CHR-A02", "CHR-A03", "CHR-U01", "CHR-U02", "CHR-S01", "CHR-S02", "CHR-S03",
          "CHR-S04", "CHR-S05", "CHR-S06", "CHR-S07", "CHR-S08", "CHR-M01", "CHR-M02", "CHR-M03",
          "CHR-M04", "CHR-M05", "CHR-M06", "CHR-M07", "CHR-L01", "CHR-E01", "CHR-N01", "CHR-O01");
  private static final List<Oracle> ORACLES =
      List.of(
          new Oracle(
              "DIF-001",
              "CHR-U01",
              "brand",
              "difference",
              "semantic",
              "brand",
              "schubert",
              "schubert NK"),
          new Oracle(
              "DIF-002",
              "CHR-L01",
              "authorization.log",
              "difference",
              "semantic",
              "authorization.log",
              "AUTHENTICATED",
              "ADMIN"),
          new Oracle(
              "DIF-003",
              "CHR-U01",
              "menu.cards",
              "difference",
              "semantic",
              "menu.cards",
              "4 legacy plus log",
              "legacy plus question notification answer and admin user"),
          new Oracle(
              "DIF-004",
              "CHR-A01",
              "authentication.backend",
              "difference",
              "semantic",
              "authentication.backend",
              "file/in-process",
              "PostgreSQL/MQ USER ADMIN"),
          new Oracle(
              "DIF-005",
              "CHR-E01",
              "error.presentation",
              "difference",
              "semantic",
              "error.presentation",
              "spring/default mixed",
              "common style and recovery guidance"),
          new Oracle(
              "DIF-006",
              "CHR-S01",
              "input.byteLimit",
              "difference",
              "semantic",
              "input.byteLimit",
              "mostly implicit",
              "fixed-wire explicit"),
          new Oracle(
              "DIF-007",
              "CHR-U02",
              "topbar.identity",
              "difference",
              "semantic",
              "topbar.identity",
              "partial",
              "username role logout"),
          new Oracle(
              "DIF-008",
              "CHR-S04",
              "empty.message",
              "difference",
              "semantic",
              "empty.message",
              "may be blank",
              "該当するデータはありません"),
          new Oracle(
              "DIF-009",
              "CHR-S08",
              "voice.grouping",
              "difference",
              "semantic",
              "voice.grouping",
              "body may repeat",
              "one body per entry"),
          new Oracle(
              "DIF-010",
              "CHR-L01",
              "log.filters",
              "difference",
              "semantic",
              "log.filters",
              "limited",
              "WARN date MQ SYSTEM BATCH"),
          new Oracle(
              "DIF-011",
              "CHR-O01",
              "cache.control",
              "required",
              "header",
              "cache-control",
              "no-store",
              "no-store"),
          new Oracle(
              "DIF-012",
              "CHR-M04",
              "invalid.range",
              "difference",
              "header",
              "content-range",
              "baseline capture",
              "416 with total Content-Range"),
          new Oracle(
              "DIF-013",
              "CHR-S02",
              "game.change",
              "difference",
              "semantic",
              "game.change",
              "inline onchange",
              "external same-origin JS plus button"),
          new Oracle(
              "DIF-014",
              "CHR-O01",
              "session.restart",
              "difference",
              "semantic",
              "session.restart",
              "in-memory invalidated",
              "encrypted persistent continuation"),
          new Oracle(
              "DIF-015",
              "CHR-A01",
              "http.path",
              "contract",
              "semantic",
              "http.path",
              "/same-path",
              "/same-path"),
          new Oracle(
              "DIF-016",
              "CHR-A02",
              "session.concurrentLimit",
              "difference",
              "semantic",
              "session.concurrentLimit",
              "three observed sessions remain active despite configured maximum 2",
              "maximum 2; third login revokes oldest"));

  @TempDir Path temporaryDirectory;

  @Test
  void acceptsTwentyFourPassCasesAndExactlySixteenApprovedDifferences() throws Exception {
    Fixture fixture = fixture("positive");
    Path output = temporaryDirectory.resolve("nk-comparison.json");
    withProjectRoot(
        fixture.project(),
        () ->
            GateCli.main(
                new String[] {
                  "compare-nk",
                  fixture.current().toString(),
                  fixture.nk().toString(),
                  fixture.observations().toString(),
                  output.toString()
                }));
    JsonNode report = JSON.readTree(output.toFile());
    assertEquals("PASS", report.path("status").asText());
    assertEquals(24, report.path("expectedCaseCount").asInt());
    assertEquals(24, report.path("comparedCaseCount").asInt());
    assertEquals(14, report.path("rawDifferenceCount").asInt());
    assertEquals(16, report.path("observationCount").asInt());
    assertEquals(16, report.path("usedDifferences").size());
    assertTrue(report.path("unusedDifferences").isEmpty());
    assertTrue(report.path("unregisteredDifferences").isEmpty());
    assertTrue(report.path("failures").isEmpty());
    assertFalse(Files.exists(output.resolveSibling(output.getFileName() + ".part")));

    ArtifactComparator.ComparisonResult direct =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertTrue(direct.passed());
    assertEquals("PASS", direct.status());
    assertEquals(24, direct.expectedCaseCount());
    assertEquals(24, direct.comparedCaseCount());
    assertEquals(14, direct.rawDifferenceCount());
    assertEquals(16, direct.observationCount());
    assertEquals(16, direct.usedDifferences().size());
    assertTrue(direct.unusedDifferences().isEmpty());
    assertTrue(direct.unregisteredDifferences().isEmpty());
    assertTrue(direct.failures().isEmpty());
  }

  @Test
  void rejectsNullMissingAndWrongInputTypesWithoutNpe() throws Exception {
    Fixture fixture = fixture("input-boundary");
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ArtifactComparator.compare(
                null, fixture.current(), fixture.nk(), fixture.observations()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ArtifactComparator.compare(
                fixture.project(), null, fixture.nk(), fixture.observations()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ArtifactComparator.compare(
                fixture.project(), fixture.current(), null, fixture.observations()));
    assertThrows(
        IllegalArgumentException.class,
        () -> ArtifactComparator.compare(fixture.project(), fixture.current(), fixture.nk(), null));

    Path regular = write(temporaryDirectory.resolve("regular.txt"), "file");
    Path directory = Files.createDirectories(temporaryDirectory.resolve("directory"));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ArtifactComparator.compare(
                fixture.project(), regular, fixture.nk(), fixture.observations()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ArtifactComparator.compare(
                fixture.project(), fixture.current(), regular, fixture.observations()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            ArtifactComparator.compare(
                fixture.project(), fixture.current(), fixture.nk(), directory));
  }

  @Test
  void reportsCatalogArtifactStatusSetSymlinkAndUnregisteredDrift() throws Exception {
    Fixture fixture = fixture("artifact-failures");
    mutate(
        fixture.project().resolve("program/characterization/tests/resources/cases/catalog.json"),
        root -> {
          ArrayNode cases = (ArrayNode) root.path("cases");
          ((ObjectNode) cases.get(0)).put("nk", "SKIP");
          ((ObjectNode) cases.get(1)).put("id", "CHR-A01");
        });
    mutate(
        fixture
            .project()
            .resolve("program/characterization/tests/resources/cases/dif-allowlist.json"),
        root -> ((ArrayNode) root.path("differences")).remove(15));
    Files.delete(fixture.current().resolve("CHR-A01.json"));
    Files.delete(fixture.nk().resolve("CHR-M04.json"));
    write(
        fixture.current().resolve("CHR-X99.json"), "{\"caseId\":\"CHR-X99\",\"status\":\"PASS\"}");
    write(fixture.nk().resolve("CHR-Y99.json"), "{\"caseId\":\"CHR-Y99\",\"status\":\"PASS\"}");
    Files.createSymbolicLink(
        fixture.current().resolve("linked.json"), fixture.current().resolve("CHR-A03.json"));
    Files.createSymbolicLink(
        fixture.nk().resolve("linked.json"), fixture.nk().resolve("CHR-A03.json"));
    write(fixture.current().resolve("ignored.txt"), "ignored");
    Files.createDirectories(fixture.nk().resolve("ignored-directory"));
    mutate(fixture.current().resolve("CHR-A03.json"), root -> root.put("caseId", "wrong"));
    mutate(fixture.current().resolve("CHR-U01.json"), root -> root.put("status", "FAIL"));
    mutate(fixture.nk().resolve("CHR-U02.json"), root -> root.put("caseId", "wrong"));
    mutate(fixture.nk().resolve("CHR-S01.json"), root -> root.put("status", "SKIPPED"));
    mutate(
        fixture.current().resolve("CHR-S02.json"),
        root -> {
          root.set("arrayDrift", JSON.valueToTree(List.of("same")));
          root.put("name/~field", "current");
        });
    mutate(
        fixture.nk().resolve("CHR-S02.json"),
        root -> {
          root.set("arrayDrift", JSON.valueToTree(List.of("same", "extra")));
          root.put("name/~field", "nk");
          root.put("objectToScalar", "nk-scalar");
          root.put("arrayToScalar", "nk-scalar");
        });
    mutate(
        fixture.current().resolve("CHR-S02.json"),
        root -> {
          root.set("objectToScalar", JSON.createObjectNode().put("key", "current"));
          root.set("arrayToScalar", JSON.valueToTree(List.of("current")));
        });

    ArtifactComparator.ComparisonResult result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertFalse(result.passed());
    assertContains(result.failures(), "CATALOG_CASE_COUNT");
    assertContains(result.failures(), "CATALOG_NK:CHR-A01");
    assertContains(result.failures(), "DIF_RULE_COUNT");
    assertContains(result.failures(), "CURRENT_SYMLINK:linked.json");
    assertContains(result.failures(), "NK_SYMLINK:linked.json");
    assertContains(result.failures(), "CURRENT_MISSING:CHR-A01");
    assertContains(result.failures(), "NK_MISSING:CHR-M04");
    assertContains(result.failures(), "CURRENT_EXTRA:CHR-X99");
    assertContains(result.failures(), "NK_EXTRA:CHR-Y99");
    assertContains(result.failures(), "CURRENT_CASE_ID:CHR-A03");
    assertContains(result.failures(), "CURRENT_STATUS:CHR-U01");
    assertContains(result.failures(), "NK_CASE_ID:CHR-U02");
    assertContains(result.failures(), "NK_STATUS:CHR-S01");
    assertTrue(
        result.unregisteredDifferences().stream()
            .anyMatch(value -> value.equals("CHR-S02:/arrayDrift/1")));
    assertTrue(
        result.unregisteredDifferences().stream()
            .anyMatch(value -> value.equals("CHR-S02:/name~1~0field")));
  }

  @Test
  void rejectsMalformedObservationEnvelope() throws Exception {
    Fixture fixture = fixture("observation-envelope");
    writeJson(
        fixture.observations(),
        JSON.createObjectNode().put("version", 0).put("observations", "not-array"));
    ArtifactComparator.ComparisonResult result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertContains(result.failures(), "OBSERVATION_VERSION");
    assertContains(result.failures(), "OBSERVATIONS_NOT_ARRAY");
    assertEquals(16, result.unusedDifferences().size());
    assertEquals(14, result.unregisteredDifferences().size());
  }

  @Test
  void rejectsUnknownOutOfScopeBroadWrongOverlappingAndUnusedObservations() throws Exception {
    Fixture fixture = fixture("observation-failures");
    ObjectNode envelope = (ObjectNode) JSON.readTree(fixture.observations().toFile());
    ArrayNode observations = (ArrayNode) envelope.path("observations");
    ObjectNode positive = (ObjectNode) observations.get(0);
    observations.add(positive.deepCopy());

    observations.add(
        observation(
            "DIF-X99",
            "CHR-U01",
            "brand",
            "difference",
            "semantic",
            "brand",
            "/dif/DIF-001",
            "schubert",
            "schubert NK"));
    observations.add(
        observation(
            "DIF-001",
            "CHR-Z99",
            "brand",
            "difference",
            "semantic",
            "brand",
            "/dif/DIF-001",
            "schubert",
            "schubert NK"));
    observations.add(
        observation(
            "DIF-001",
            "CHR-U01",
            "brand",
            "difference",
            "semantic",
            "brand",
            "relative",
            "schubert",
            "schubert NK"));
    observations.add(
        observation(
            "DIF-001",
            "CHR-U01",
            "brand",
            "difference",
            "semantic",
            "brand",
            "/*",
            "schubert",
            "schubert NK"));
    observations.add(
        observation(
            "DIF-001",
            "CHR-U01",
            "brand",
            "difference",
            "semantic",
            "brand",
            "/a..b",
            "schubert",
            "schubert NK"));
    observations.add(
        observation(
            "DIF-001",
            "CHR-U01",
            "brand",
            "difference",
            "semantic",
            "brand",
            "/",
            "schubert",
            "schubert NK"));

    ObjectNode missingExpected =
        observation(
            "DIF-002",
            "CHR-L01",
            "authorization.log",
            "difference",
            "semantic",
            "authorization.log",
            "/dif/DIF-002",
            "AUTHENTICATED",
            "ADMIN");
    missingExpected.remove("expectedCurrent");
    missingExpected.remove("expectedNk");
    observations.add(missingExpected);

    observations.add(
        observation(
            "DIF-001",
            "CHR-M01",
            "wrong-field",
            "contract",
            "header",
            "wrong-selector",
            "/missing",
            "wrong-current",
            "wrong-nk"));
    observations.add(
        observation(
            "DIF-001",
            "CHR-U01",
            "brand",
            "difference",
            "semantic",
            "brand",
            "/missing",
            "wrong-current",
            "wrong-nk"));

    ObjectNode currentA01 = objectFile(fixture.current().resolve("CHR-A01.json"));
    ObjectNode nkA01 = objectFile(fixture.nk().resolve("CHR-A01.json"));
    currentA01.put("same", "same");
    nkA01.put("same", "same");
    currentA01.put("shared", "current");
    nkA01.put("shared", "nk");
    writeJson(fixture.current().resolve("CHR-A01.json"), currentA01);
    writeJson(fixture.nk().resolve("CHR-A01.json"), nkA01);
    observations.add(
        observation(
            "DIF-004",
            "CHR-A01",
            "authentication.backend",
            "difference",
            "semantic",
            "authentication.backend",
            "/same",
            "same",
            "same"));
    observations.add(
        observation(
            "DIF-004",
            "CHR-A01",
            "authentication.backend",
            "difference",
            "semantic",
            "authentication.backend",
            "/shared",
            "current",
            "nk"));
    observations.add(
        observation(
            "DIF-015",
            "CHR-A01",
            "http.path",
            "contract",
            "semantic",
            "http.path",
            "/shared",
            "current",
            "nk"));
    mutate(
        fixture
            .project()
            .resolve("program/characterization/tests/resources/cases/dif-allowlist.json"),
        root -> ((ObjectNode) root.path("differences").get(1)).put("mode", "wildcard"));
    observations.add(
        observation(
            "DIF-002",
            "CHR-L01",
            "authorization.log",
            "wildcard",
            "semantic",
            "authorization.log",
            "/dif/DIF-002",
            "AUTHENTICATED",
            "ADMIN"));
    writeJson(fixture.observations(), envelope);

    Path output = temporaryDirectory.resolve("observation-failure-report.json");
    withProjectRoot(
        fixture.project(),
        () ->
            assertThrows(
                IllegalStateException.class,
                () ->
                    GateCli.main(
                        new String[] {
                          "compare-nk",
                          fixture.current().toString(),
                          fixture.nk().toString(),
                          fixture.observations().toString(),
                          output.toString()
                        })));
    JsonNode report = JSON.readTree(output.toFile());
    List<String> failures = strings(report.path("failures"));
    assertPrefix(failures, "OBSERVATION_DUPLICATE:");
    assertPrefix(failures, "OBSERVATION_UNKNOWN_DIF:");
    assertPrefix(failures, "OBSERVATION_UNKNOWN_CASE:");
    assertPrefix(failures, "OBSERVATION_POINTER:");
    assertPrefix(failures, "OBSERVATION_CURRENT_MISSING:");
    assertPrefix(failures, "OBSERVATION_NK_MISSING:");
    assertPrefix(failures, "OBSERVATION_CASE_SCOPE:");
    assertPrefix(failures, "OBSERVATION_FIELD:");
    assertPrefix(failures, "OBSERVATION_MODE:");
    assertPrefix(failures, "OBSERVATION_SELECTOR_TYPE:");
    assertPrefix(failures, "OBSERVATION_SELECTOR:");
    assertPrefix(failures, "OBSERVATION_CURRENT_POINTER:");
    assertPrefix(failures, "OBSERVATION_NK_POINTER:");
    assertPrefix(failures, "OBSERVATION_CURRENT_VALUE:");
    assertPrefix(failures, "OBSERVATION_NK_VALUE:");
    assertPrefix(failures, "OBSERVATION_DIFFERENCE_REQUIRED:");
    assertPrefix(failures, "OBSERVATION_OVERLAP:");
    assertEquals("FAIL", report.path("status").asText());
  }

  @Test
  void rejectsMissingOrUncorrelatedL01ProjectionEvenWhenDifClaimsAreValid() throws Exception {
    Fixture missing = fixture("projection-missing");
    mutate(missing.observations(), root -> root.remove("correlatedLogEvidence"));
    ArtifactComparator.ComparisonResult missingResult =
        ArtifactComparator.compare(
            missing.project(), missing.current(), missing.nk(), missing.observations());
    assertFalse(missingResult.passed());
    assertContains(missingResult.failures(), "LOG_PROJECTION_ENVELOPE");

    Fixture mismatch = fixture("projection-mismatch");
    mutate(
        mismatch.observations(),
        root ->
            ((ObjectNode) root.at("/correlatedLogEvidence/observed/nk/after/1/payload"))
                .put("request", "WRONG_REQUEST"));
    ArtifactComparator.ComparisonResult mismatchResult =
        ArtifactComparator.compare(
            mismatch.project(), mismatch.current(), mismatch.nk(), mismatch.observations());
    assertFalse(mismatchResult.passed());
    assertContains(mismatchResult.failures(), "LOG_PROJECTION_DB_UNEXPECTED");

    Fixture unrelated = fixture("projection-unrelated-artifact");
    mutate(
        unrelated.observations(),
        root ->
            ((ObjectNode) root.at("/correlatedLogArtifacts/current")).put("extra", "not-captured"));
    ArtifactComparator.ComparisonResult unrelatedResult =
        ArtifactComparator.compare(
            unrelated.project(), unrelated.current(), unrelated.nk(), unrelated.observations());
    assertFalse(unrelatedResult.passed());
    assertContains(unrelatedResult.failures(), "LOG_PROJECTION_ARTIFACT_BINDING");

    for (String side : List.of("missing", "extra", "nk")) {
      Fixture binding = fixture("projection-binding-" + side);
      mutate(
          binding.observations(),
          root -> {
            if (side.equals("missing")) root.remove("correlatedLogArtifacts");
            else if (side.equals("extra"))
              ((ObjectNode) root.path("correlatedLogArtifacts")).put("extra", true);
            else ((ObjectNode) root.at("/correlatedLogArtifacts/nk")).put("extra", "not-captured");
          });
      ArtifactComparator.ComparisonResult result =
          ArtifactComparator.compare(
              binding.project(), binding.current(), binding.nk(), binding.observations());
      assertFalse(result.passed());
      assertContains(result.failures(), "LOG_PROJECTION_ARTIFACT_BINDING");
    }
  }

  @Test
  void rejectsNonIntegralOrOversizedObservationVersions() throws Exception {
    int index = 0;
    for (JsonNode version :
        List.of(
            TextNode.valueOf("1"),
            JSON.getNodeFactory().numberNode(1.5),
            JSON.getNodeFactory().numberNode(new java.math.BigInteger("4294967297")))) {
      Fixture input = fixture("observation-version-" + index++);
      mutate(input.observations(), root -> root.set("version", version));
      ArtifactComparator.ComparisonResult result =
          ArtifactComparator.compare(
              input.project(), input.current(), input.nk(), input.observations());
      assertFalse(result.passed());
      assertContains(result.failures(), "OBSERVATION_VERSION");
    }
  }

  @Test
  void lexicalArtifactNamesRejectNullAndNamelessPathsBeforeDereference() {
    assertEquals("CHR-L01.json", ArtifactComparator.requiredArtifactFileName(Path.of("/synthetic/CHR-L01.json")));
    assertThrows(IllegalArgumentException.class, () -> ArtifactComparator.requiredArtifactFileName(null));
    assertThrows(IllegalArgumentException.class, () -> ArtifactComparator.requiredArtifactFileName(Path.of("/")));
  }

  private Fixture fixture(String name) throws Exception {
    Path root = temporaryDirectory.resolve(name);
    Path project = root.resolve("project");
    Path resources = project.resolve("program/characterization/tests/resources/cases");
    Files.createDirectories(resources);
    Files.copy(
        SOURCE_ROOT.resolve("program/characterization/tests/resources/cases/catalog.json"),
        resources.resolve("catalog.json"),
        StandardCopyOption.COPY_ATTRIBUTES);
    Files.copy(
        SOURCE_ROOT.resolve("program/characterization/tests/resources/cases/dif-allowlist.json"),
        resources.resolve("dif-allowlist.json"),
        StandardCopyOption.COPY_ATTRIBUTES);
    Path current = Files.createDirectories(root.resolve("current"));
    Path nk = Files.createDirectories(root.resolve("nk"));
    java.util.Map<String, ObjectNode> currentArtifacts = new java.util.LinkedHashMap<>();
    java.util.Map<String, ObjectNode> nkArtifacts = new java.util.LinkedHashMap<>();
    for (String caseId : CASE_IDS) {
      currentArtifacts.put(
          caseId, JSON.createObjectNode().put("caseId", caseId).put("status", "PASS"));
      nkArtifacts.put(caseId, JSON.createObjectNode().put("caseId", caseId).put("status", "PASS"));
    }

    ArrayNode observationItems = JSON.createArrayNode();
    for (Oracle oracle : ORACLES) {
      ObjectNode currentArtifact = currentArtifacts.get(oracle.caseId());
      ObjectNode nkArtifact = nkArtifacts.get(oracle.caseId());
      ObjectNode currentDif = object(currentArtifact, "dif");
      ObjectNode nkDif = object(nkArtifact, "dif");
      String pointer = "/dif/" + oracle.id();
      JsonNode currentValue = TextNode.valueOf(oracle.currentValue());
      JsonNode nkValue = TextNode.valueOf(oracle.nkValue());
      if ("DIF-003".equals(oracle.id())) {
        currentDif.set(oracle.id(), JSON.valueToTree(List.of("same", oracle.currentValue())));
        nkDif.set(oracle.id(), JSON.valueToTree(List.of("same", oracle.nkValue())));
        pointer += "/1";
      } else {
        currentDif.set(oracle.id(), currentValue);
        nkDif.set(oracle.id(), nkValue);
      }
      observationItems.add(
          observation(
              oracle.id(),
              oracle.caseId(),
              oracle.field(),
              oracle.mode(),
              oracle.selectorType(),
              oracle.selector(),
              pointer,
              oracle.currentValue(),
              oracle.nkValue()));
    }
    currentArtifacts.forEach(
        (caseId, artifact) -> uncheckedWriteJson(current.resolve(caseId + ".json"), artifact));
    nkArtifacts.forEach(
        (caseId, artifact) -> uncheckedWriteJson(nk.resolve(caseId + ".json"), artifact));
    Path observations = root.resolve("observations.json");
    ObjectNode envelope = JSON.createObjectNode().put("version", 1);
    envelope.set("observations", observationItems);
    envelope.set("correlatedLogEvidence", CorrelatedLogEvidenceValidatorTest.fixture());
    ObjectNode artifactBinding = envelope.putObject("correlatedLogArtifacts");
    artifactBinding.set("current", currentArtifacts.get("CHR-L01").deepCopy());
    artifactBinding.set("nk", nkArtifacts.get("CHR-L01").deepCopy());
    writeJson(observations, envelope);
    return new Fixture(project, current, nk, observations);
  }

  private static ObjectNode observation(
      String id,
      String caseId,
      String field,
      String mode,
      String selectorType,
      String selector,
      String pointer,
      String expectedCurrent,
      String expectedNk) {
    return JSON.createObjectNode()
        .put("id", id)
        .put("caseId", caseId)
        .put("field", field)
        .put("mode", mode)
        .put("selectorType", selectorType)
        .put("selector", selector)
        .put("jsonPointer", pointer)
        .put("expectedCurrent", expectedCurrent)
        .put("expectedNk", expectedNk);
  }

  private static ObjectNode object(ObjectNode parent, String name) {
    JsonNode existing = parent.path(name);
    return existing.isObject() ? (ObjectNode) existing : parent.putObject(name);
  }

  private static ObjectNode objectFile(Path file) throws IOException {
    return (ObjectNode) JSON.readTree(file.toFile());
  }

  private static void mutate(Path file, Consumer<ObjectNode> mutation) throws Exception {
    ObjectNode root = objectFile(file);
    mutation.accept(root);
    writeJson(file, root);
  }

  private static Path write(Path file, String text) throws IOException {
    Files.createDirectories(file.getParent());
    Files.writeString(file, text, StandardCharsets.UTF_8);
    return file;
  }

  private static void writeJson(Path file, JsonNode value) throws IOException {
    Files.createDirectories(file.getParent());
    JSON.writerWithDefaultPrettyPrinter().writeValue(file.toFile(), value);
  }

  private static void uncheckedWriteJson(Path file, JsonNode value) {
    try {
      writeJson(file, value);
    } catch (IOException error) {
      throw new IllegalStateException(error);
    }
  }

  private static List<String> strings(JsonNode values) {
    List<String> result = new ArrayList<>();
    values.forEach(value -> result.add(value.asText()));
    return result;
  }

  private static void assertContains(List<String> failures, String expected) {
    assertTrue(failures.contains(expected), () -> "missing " + expected + " in " + failures);
  }

  private static void assertPrefix(List<String> failures, String prefix) {
    assertTrue(
        failures.stream().anyMatch(value -> value.startsWith(prefix)),
        () -> "missing prefix " + prefix + " in " + failures);
  }

  private static void withProjectRoot(Path projectRoot, ThrowingRunnable action) throws Exception {
    String previous = System.getProperty("chr.projectRoot");
    try {
      System.setProperty("chr.projectRoot", projectRoot.toString());
      action.run();
    } finally {
      if (previous == null) System.clearProperty("chr.projectRoot");
      else System.setProperty("chr.projectRoot", previous);
    }
  }

  @FunctionalInterface
  private interface ThrowingRunnable {
    void run() throws Exception;
  }

  private record Fixture(Path project, Path current, Path nk, Path observations) {}

  private record Oracle(
      String id,
      String caseId,
      String field,
      String mode,
      String selectorType,
      String selector,
      String currentValue,
      String nkValue) {}
}
