package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.BooleanNode;
import com.fasterxml.jackson.databind.node.IntNode;
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
  private static final String FIXTURE_DIF015 = "DIF-015";
  private static final String FIXTURE_OBSERVATIONS = "observations";
  private static final String FIXTURE_EXPECTED_NK = "expectedNk";
  private static final String FIXTURE_EXPECTED_CURRENT = "expectedCurrent";
  private static final String FIXTURE_JSON_SUFFIX = ".json";
  private static final String FIXTURE_EXTRA = "extra";

  private static final String ASYNC_MENU_DIFFERENCE = "DIF-003";
  private static final String FIXTURE_CHR_A01 = "CHR-A01";
  private static final String FIXTURE_CHR_A02 = "CHR-A02";
  private static final String FIXTURE_CHR_A02_JSON = "CHR-A02.json";
  private static final String FIXTURE_DIF_016 = "DIF-016";
  private static final String FIXTURE_CHR_O01 = "CHR-O01";
  private static final String FIXTURE_CHR_O01_JSON = "CHR-O01.json";
  private static final String FIXTURE_DIF_011 = "DIF-011";
  private static final String FIXTURE_DIF_012 = "DIF-012";
  private static final String FIXTURE_DIF_013 = "DIF-013";
  private static final String FIXTURE_CHR_S02 = "CHR-S02";
  private static final String FIXTURE_CHR_E01 = "CHR-E01";
  private static final String FIXTURE_SECRET_LEAK = "secretLeak";
  private static final String FIXTURE_PATH_LEAK = "absolutePathLeak";
  private static final String FIXTURE_EXCEPTION_LEAK = "exceptionClassLeak";
  private static final List<String> FIXTURE_ERROR_FLAGS =
      List.of(FIXTURE_SECRET_LEAK, FIXTURE_PATH_LEAK, FIXTURE_EXCEPTION_LEAK);
  private static final String FIXTURE_UI_ERROR_POINTER = "/dif/DIF-005";
  private static final String FIXTURE_CURRENT_ERROR_PREFIX = "CURRENT_ERROR_DISCLOSURE:";
  private static final String FIXTURE_NK_ERROR_PREFIX = "NK_ERROR_DISCLOSURE:";
  private static final String FIXTURE_GAME_CHANGE = "gameOnchange";
  private static final String FIXTURE_GAME_CHANGE_POINTER = "/gameOnchange";
  private static final String FIXTURE_GAME_CHANGE_FIELD = "game.change";
  private static final String FIXTURE_GAME_CHANGE_FALLBACK = "javascriptDisabledSubmitButton";
  private static final String FIXTURE_CURRENT_HANDLER = "this.form.submit()";
  private static final String FIXTURE_OTHER_HANDLER = "syntheticHandler()";
  private static final String GAME_CHANGE_DIFFERENCE = "CHR-S02:/gameOnchange";
  private static final String REQUIRED_GAME_CHANGE = "FIXED_DIF_REQUIRED:CHR-S02:/gameOnchange";
  private static final String FIXTURE_CHR_M04 = "CHR-M04";
  private static final String FIXTURE_CHR_M07 = "CHR-M07";
  private static final String FIXTURE_INVALID_RANGE = "invalidRange";
  private static final String FIXTURE_INVALID_RANGE_STATUS = "/invalidRange/status";
  private static final String AUDIO_STATUS_DIFFERENCE = "CHR-M07:/invalidRange/status";
  private static final String FIXTURE_INVALID_RANGE_HEADER = "/invalidRange/contentRange";
  private static final String FIXTURE_CONTENT_RANGE = "contentRange";
  private static final String FIXTURE_RANGE_SELECTOR = "content-range";
  private static final String FIXTURE_RANGE_FIELD = "invalid.range";
  private static final String FIXTURE_HEADER = "header";
  private static final String FIXTURE_CACHE_CONTROL = "cacheControl";
  private static final String FIXTURE_CACHE_POINTER = "/cacheControl";
  private static final String FIXTURE_CACHE_BEFORE =
      "no-cache, no-store, max-age=0, must-revalidate";
  private static final String FIXTURE_CACHE_AFTER = "no-store";
  private static final String FIXTURE_COUNT = "observedActiveSessionCount";
  private static final String FIXTURE_COUNT_POINTER = "/observedActiveSessionCount";
  private static final String FIXTURE_OLDEST = "oldestSessionInvalidated";
  private static final String FIXTURE_ACTIVE = "sessionActiveOldestToNewest";
  private static final String FIXTURE_REDIRECT = "sessionRedirectsOldestToNewest";
  private static final String FIXTURE_REDIRECT_POINTER = "/sessionRedirectsOldestToNewest/0";
  private static final String FIXTURE_LIMIT = "configuredMaximumSessions";
  private static final String FIXTURE_RULE_SESSION = "session.concurrentLimit";
  private static final String FIXTURE_SESSION_EXPIRED = "/login?session-expired";
  private static final String FIXTURE_FIXED_POINTER = "OBSERVATION_FIXED_POINTER";
  private static final String FIXTURE_FIXED_NK = "OBSERVATION_FIXED_NK";
  private static final String FIXTURE_CACHE_REQUIRED = "FIXED_DIF_REQUIRED:CHR-O01:/cacheControl";
  private static final String FIXTURE_CHR_U01 = "CHR-U01";
  private static final String FIXTURE_CHR_U02 = "CHR-U02";
  private static final String FIXTURE_CHR_L01 = "CHR-L01";
  private static final String FIXTURE_DIF_001 = "DIF-001";
  private static final String FIXTURE_DIF_008 = "DIF-008";
  private static final String FIXTURE_CHR_S04 = "CHR-S04";
  private static final String FIXTURE_SEARCH_EMPTY_TEXT = "emptyVisibleText";
  private static final String FIXTURE_SEARCH_EMPTY_POINTER = "/emptyVisibleText";
  private static final String FIXTURE_SEARCH_EMPTY_FIELD = "empty.message";
  private static final String FIXTURE_SEARCH_EMPTY_NK = "該当するデータはありません";
  private static final String FIXTURE_SEARCH_EMPTY_REQUIRED =
      "FIXED_DIF_REQUIRED:CHR-S04:/emptyVisibleText";
  private static final String SEARCH_EMPTY_DIFFERENCE = "CHR-S04:/emptyVisibleText";
  private static final String FIXTURE_UNAPPROVED_EMPTY_LABEL = "synthetic empty label";
  private static final String FIXTURE_BRAND = "brand";
  private static final String FIXTURE_BRAND_POINTER = "/brand";
  private static final String FIXTURE_POINTER = "jsonPointer";
  private static final String FIXTURE_DIFFERENCE = "difference";
  private static final String FIXTURE_SEMANTIC = "semantic";
  private static final String FIXTURE_SCHUBERT = "schubert";
  private static final String FIXTURE_SCHUBERT_NK = "schubert NK";
  private static final String FIXTURE_AUTHORIZATION_LOG = "authorization.log";
  private static final String FIXTURE_AUTHENTICATION_BACKEND = "authentication.backend";
  private static final String FIXTURE_HTTP_PATH = "http.path";
  private static final String FIXTURE_PASS = "PASS";
  private static final String FIXTURE_STATUS = "status";
  private static final String FIXTURE_CHR_A01_JSON = "CHR-A01.json";
  private static final String FIXTURE_LOGIN_TITLE = "title";
  private static final String FIXTURE_LOGIN_POINTER = "/title";
  private static final String FIXTURE_CURRENT_LOGIN_TITLE = "schubert - ログイン";
  private static final String FIXTURE_NK_LOGIN_TITLE = "schubert NK - ログイン";
  private static final String FIXTURE_UNAPPROVED_LOGIN_TITLE = "public synthetic different title";
  private static final String FIXTURE_LOGIN_TITLE_REQUIRED = "LOGIN_TITLE_DIF_REQUIRED";
  private static final String FIXTURE_UNREGISTERED_LOGIN_TITLE = "CHR-A01:/title";
  private static final String FIXTURE_TITLES = "titles";
  private static final String FIXTURE_MENU_TITLE_POINTER = "/titles/0";
  private static final String FIXTURE_SEARCH_TITLE_POINTER = "/titles/1";
  private static final String FIXTURE_CURRENT_SEARCH_TITLE = "schubert - 検索";
  private static final String FIXTURE_NK_SEARCH_TITLE = "schubert NK - 検索";
  private static final String FIXTURE_CHR_U02_JSON = "CHR-U02.json";
  private static final String BRAND_SEARCH_REQUIRED = "BRAND_DIF_REQUIRED:CHR-U02:/titles/1";
  private static final String UNREGISTERED_SEARCH = "CHR-U02:/titles/1";
  private static final String UNREGISTERED_BRAND = "CHR-U01:/brand";
  private static final String FIXTURE_CASEID = "caseId";
  private static final String FIXTURE_SAME = "same";
  private static final String FIXTURE_CURRENT = "current";
  private static final String FIXTURE_CHR_PROJECTROOT = "chr.projectRoot";

  private static final ObjectMapper JSON = new ObjectMapper();
  private static final Path SOURCE_ROOT =
      Path.of(System.getProperty("chr.unitProjectRoot")).toAbsolutePath().normalize();
  private static final List<String> CASE_IDS =
      List.of(
          FIXTURE_CHR_A01,
          "CHR-A02",
          "CHR-A03",
          FIXTURE_CHR_U01,
          "CHR-U02",
          "CHR-S01",
          "CHR-S02",
          "CHR-S03",
          "CHR-S04",
          "CHR-S05",
          "CHR-S06",
          "CHR-S07",
          "CHR-S08",
          "CHR-M01",
          "CHR-M02",
          "CHR-M03",
          "CHR-M04",
          "CHR-M05",
          "CHR-M06",
          "CHR-M07",
          FIXTURE_CHR_L01,
          "CHR-E01",
          "CHR-N01",
          "CHR-O01");
  private static final List<Oracle> ORACLES =
      List.of(
          new Oracle(
              FIXTURE_DIF_001,
              FIXTURE_CHR_U01,
              FIXTURE_BRAND,
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              FIXTURE_BRAND,
              FIXTURE_SCHUBERT,
              FIXTURE_SCHUBERT_NK),
          new Oracle(
              "DIF-002",
              FIXTURE_CHR_L01,
              FIXTURE_AUTHORIZATION_LOG,
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              FIXTURE_AUTHORIZATION_LOG,
              "AUTHENTICATED",
              "ADMIN"),
          new Oracle(
              "DIF-003",
              FIXTURE_CHR_U01,
              "menu.cards",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "menu.cards",
              "4 legacy plus log",
              "legacy plus question notification answer and admin user"),
          new Oracle(
              "DIF-004",
              FIXTURE_CHR_A01,
              FIXTURE_AUTHENTICATION_BACKEND,
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              FIXTURE_AUTHENTICATION_BACKEND,
              "file/in-process",
              "PostgreSQL/MQ USER ADMIN"),
          new Oracle(
              "DIF-005",
              FIXTURE_CHR_E01,
              "error.presentation",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "error.presentation",
              "spring/default mixed",
              "common style and recovery guidance"),
          new Oracle(
              "DIF-006",
              "CHR-S01",
              "input.byteLimit",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "input.byteLimit",
              "mostly implicit",
              "fixed-wire explicit"),
          new Oracle(
              "DIF-007",
              "CHR-U02",
              "topbar.identity",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "topbar.identity",
              "partial",
              "username role logout"),
          new Oracle(
              FIXTURE_DIF_008,
              FIXTURE_CHR_S04,
              FIXTURE_SEARCH_EMPTY_FIELD,
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              FIXTURE_SEARCH_EMPTY_FIELD,
              "",
              FIXTURE_SEARCH_EMPTY_NK),
          new Oracle(
              "DIF-009",
              "CHR-S08",
              "voice.grouping",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "voice.grouping",
              "body may repeat",
              "one body per entry"),
          new Oracle(
              "DIF-010",
              FIXTURE_CHR_L01,
              "log.filters",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "log.filters",
              "limited",
              "WARN date MQ SYSTEM BATCH"),
          new Oracle(
              "DIF-014",
              "CHR-O01",
              "session.restart",
              FIXTURE_DIFFERENCE,
              FIXTURE_SEMANTIC,
              "session.restart",
              "in-memory invalidated",
              "encrypted persistent continuation"),
          new Oracle(
              FIXTURE_DIF015,
              FIXTURE_CHR_A01,
              FIXTURE_HTTP_PATH,
              "contract",
              FIXTURE_SEMANTIC,
              FIXTURE_HTTP_PATH,
              "/same-path",
              "/same-path"));

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
    assertEquals(FIXTURE_PASS, report.path(FIXTURE_STATUS).asText());
    assertEquals(24, report.path("expectedCaseCount").asInt());
    assertEquals(24, report.path("comparedCaseCount").asInt());
    assertEquals(24, report.path("rawDifferenceCount").asInt());
    assertEquals(25, report.path("observationCount").asInt());
    assertEquals(16, report.path("usedDifferences").size());
    assertTrue(report.path("unusedDifferences").isEmpty());
    assertTrue(report.path("unregisteredDifferences").isEmpty());
    assertTrue(report.path("failures").isEmpty());
    assertFalse(Files.exists(output.resolveSibling(output.getFileName() + ".part")));

    ArtifactComparator.ComparisonResult direct =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertTrue(direct.passed());
    assertEquals(FIXTURE_PASS, direct.status());
    assertEquals(24, direct.expectedCaseCount());
    assertEquals(24, direct.comparedCaseCount());
    assertEquals(24, direct.rawDifferenceCount());
    assertEquals(25, direct.observationCount());
    assertEquals(16, direct.usedDifferences().size());
    assertTrue(direct.unusedDifferences().isEmpty());
    assertTrue(direct.unregisteredDifferences().isEmpty());
    assertTrue(direct.failures().isEmpty());
  }

  @Test
  void rejectsRepeatedCaseDefinitionEvenWhenTwentyFourCasesStillCompare() throws Exception {
    Fixture fixture = fixture("duplicate-case-definition");
    appendDuplicateDefinition(fixture, "catalog.json", "cases");

    ArtifactComparator.ComparisonResult result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());

    assertFalse(result.passed());
    assertEquals(List.of("CATALOG_DUPLICATE:CHR-A01"), result.failures());
    assertEquals(24, result.expectedCaseCount());
    assertEquals(24, result.comparedCaseCount());
  }

  @Test
  void rejectsRepeatedDifferenceDefinitionEvenWhenSixteenRulesStillMatch() throws Exception {
    Fixture fixture = fixture("duplicate-difference-definition");
    appendDuplicateDefinition(fixture, "dif-allowlist.json", "differences");

    ArtifactComparator.ComparisonResult result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());

    assertFalse(result.passed());
    assertEquals(List.of("DIF_DUPLICATE:DIF-001"), result.failures());
    assertEquals(25, result.observationCount());
    assertEquals(16, result.usedDifferences().size());
  }

  private static void appendDuplicateDefinition(Fixture fixture, String fileName, String array)
      throws IOException {
    Path file =
        fixture
            .project()
            .resolve("program/characterization/tests/resources/cases")
            .resolve(fileName);
    JsonNode document = JSON.readTree(file.toFile());
    ArrayNode definitions = (ArrayNode) document.path(array);
    definitions.add(definitions.get(0).deepCopy());
    writeJson(file, document);
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
          ((ObjectNode) cases.get(1)).put("id", FIXTURE_CHR_A01);
        });
    mutate(
        fixture
            .project()
            .resolve("program/characterization/tests/resources/cases/dif-allowlist.json"),
        root -> ((ArrayNode) root.path("differences")).remove(15));
    Files.delete(fixture.current().resolve(FIXTURE_CHR_A01_JSON));
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
    mutate(fixture.current().resolve("CHR-A03.json"), root -> root.put(FIXTURE_CASEID, "wrong"));
    mutate(fixture.current().resolve("CHR-U01.json"), root -> root.put(FIXTURE_STATUS, "FAIL"));
    mutate(fixture.nk().resolve("CHR-U02.json"), root -> root.put(FIXTURE_CASEID, "wrong"));
    mutate(fixture.nk().resolve("CHR-S01.json"), root -> root.put(FIXTURE_STATUS, "SKIPPED"));
    mutate(
        fixture.current().resolve("CHR-S02.json"),
        root -> {
          root.set("arrayDrift", JSON.valueToTree(List.of(FIXTURE_SAME)));
          root.put("name/~field", FIXTURE_CURRENT);
        });
    mutate(
        fixture.nk().resolve("CHR-S02.json"),
        root -> {
          root.set("arrayDrift", JSON.valueToTree(List.of(FIXTURE_SAME, FIXTURE_EXTRA)));
          root.put("name/~field", "nk");
          root.put("objectToScalar", "nk-scalar");
          root.put("arrayToScalar", "nk-scalar");
        });
    mutate(
        fixture.current().resolve("CHR-S02.json"),
        root -> {
          root.set("objectToScalar", JSON.createObjectNode().put("key", FIXTURE_CURRENT));
          root.set("arrayToScalar", JSON.valueToTree(List.of(FIXTURE_CURRENT)));
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
        JSON.createObjectNode().put("version", 0).put(FIXTURE_OBSERVATIONS, "not-array"));
    ArtifactComparator.ComparisonResult result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertContains(result.failures(), "OBSERVATION_VERSION");
    assertContains(result.failures(), "OBSERVATIONS_NOT_ARRAY");
    assertEquals(16, result.unusedDifferences().size());
    assertEquals(24, result.unregisteredDifferences().size());
  }

  @Test
  void rejectsUnknownOutOfScopeBroadWrongOverlappingAndUnusedObservations() throws Exception {
    Fixture fixture = fixture("observation-failures");
    ObjectNode envelope = (ObjectNode) JSON.readTree(fixture.observations().toFile());
    ArrayNode observations = (ArrayNode) envelope.path(FIXTURE_OBSERVATIONS);
    ObjectNode positive = (ObjectNode) observations.get(0);
    observations.add(positive.deepCopy());

    observations.add(
        observation(
            "DIF-X99",
            FIXTURE_CHR_U01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "/dif/DIF-001",
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));
    observations.add(
        observation(
            FIXTURE_DIF_001,
            "CHR-Z99",
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "/dif/DIF-001",
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));
    observations.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_U01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "relative",
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));
    observations.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_U01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "/*",
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));
    observations.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_U01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "/a..b",
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));
    observations.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_U01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "/",
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));

    ObjectNode missingExpected =
        observation(
            "DIF-002",
            FIXTURE_CHR_L01,
            FIXTURE_AUTHORIZATION_LOG,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_AUTHORIZATION_LOG,
            "/dif/DIF-002",
            "AUTHENTICATED",
            "ADMIN");
    missingExpected.remove(FIXTURE_EXPECTED_CURRENT);
    missingExpected.remove(FIXTURE_EXPECTED_NK);
    observations.add(missingExpected);

    observations.add(
        observation(
            FIXTURE_DIF_001,
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
            FIXTURE_DIF_001,
            FIXTURE_CHR_U01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            "/missing",
            "wrong-current",
            "wrong-nk"));

    ObjectNode currentA01 = objectFile(fixture.current().resolve(FIXTURE_CHR_A01_JSON));
    ObjectNode nkA01 = objectFile(fixture.nk().resolve(FIXTURE_CHR_A01_JSON));
    currentA01.put(FIXTURE_SAME, FIXTURE_SAME);
    nkA01.put(FIXTURE_SAME, FIXTURE_SAME);
    currentA01.put("shared", FIXTURE_CURRENT);
    nkA01.put("shared", "nk");
    writeJson(fixture.current().resolve(FIXTURE_CHR_A01_JSON), currentA01);
    writeJson(fixture.nk().resolve(FIXTURE_CHR_A01_JSON), nkA01);
    observations.add(
        observation(
            "DIF-004",
            FIXTURE_CHR_A01,
            FIXTURE_AUTHENTICATION_BACKEND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_AUTHENTICATION_BACKEND,
            "/same",
            FIXTURE_SAME,
            FIXTURE_SAME));
    observations.add(
        observation(
            "DIF-004",
            FIXTURE_CHR_A01,
            FIXTURE_AUTHENTICATION_BACKEND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_AUTHENTICATION_BACKEND,
            "/shared",
            FIXTURE_CURRENT,
            "nk"));
    observations.add(
        observation(
            FIXTURE_DIF015,
            FIXTURE_CHR_A01,
            FIXTURE_HTTP_PATH,
            "contract",
            FIXTURE_SEMANTIC,
            FIXTURE_HTTP_PATH,
            "/shared",
            FIXTURE_CURRENT,
            "nk"));
    mutate(
        fixture
            .project()
            .resolve("program/characterization/tests/resources/cases/dif-allowlist.json"),
        root -> ((ObjectNode) root.path("differences").get(1)).put("mode", "wildcard"));
    observations.add(
        observation(
            "DIF-002",
            FIXTURE_CHR_L01,
            FIXTURE_AUTHORIZATION_LOG,
            "wildcard",
            FIXTURE_SEMANTIC,
            FIXTURE_AUTHORIZATION_LOG,
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
    assertEquals("FAIL", report.path(FIXTURE_STATUS).asText());
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
            ((ObjectNode) root.at("/correlatedLogArtifacts/current"))
                .put(FIXTURE_EXTRA, "not-captured"));
    ArtifactComparator.ComparisonResult unrelatedResult =
        ArtifactComparator.compare(
            unrelated.project(), unrelated.current(), unrelated.nk(), unrelated.observations());
    assertFalse(unrelatedResult.passed());
    assertContains(unrelatedResult.failures(), "LOG_PROJECTION_ARTIFACT_BINDING");

    for (String side : List.of("missing", FIXTURE_EXTRA, "nk")) {
      Fixture binding = fixture("projection-binding-" + side);
      mutate(
          binding.observations(),
          root -> {
            if (side.equals("missing")) root.remove("correlatedLogArtifacts");
            else if (side.equals(FIXTURE_EXTRA))
              ((ObjectNode) root.path("correlatedLogArtifacts")).put(FIXTURE_EXTRA, true);
            else
              ((ObjectNode) root.at("/correlatedLogArtifacts/nk"))
                  .put(FIXTURE_EXTRA, "not-captured");
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
      Fixture input = fixture("observation-version-" + index);
      index++;
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
    assertEquals(
        "CHR-L01.json",
        ArtifactComparator.requiredArtifactFileName(Path.of("/synthetic/CHR-L01.json")));
    assertThrows(
        IllegalArgumentException.class, () -> ArtifactComparator.requiredArtifactFileName(null));
    assertThrows(
        IllegalArgumentException.class,
        () -> ArtifactComparator.requiredArtifactFileName(Path.of("/")));
  }

  /** PT-CHR-DIF015-001 / BUG2812: one drift, no overlapping claim or unrelated failure. */
  @Test
  void contractChangeAndInvalidClaimCannotHideUnregisteredDrift() throws Exception {
    Fixture contract = fixture("isolated-contract-change");
    mutate(
        contract.nk().resolve(FIXTURE_CHR_A01_JSON),
        root -> ((ObjectNode) root.path("dif")).put(FIXTURE_DIF015, "/changed-path"));
    mutate(
        contract.observations(),
        root -> {
          for (JsonNode item : root.path(FIXTURE_OBSERVATIONS)) {
            if (FIXTURE_DIF015.equals(item.path("id").asText())) {
              ((ObjectNode) item).put(FIXTURE_EXPECTED_NK, "/changed-path");
            }
          }
        });
    ArtifactComparator.ComparisonResult changed =
        ArtifactComparator.compare(
            contract.project(), contract.current(), contract.nk(), contract.observations());
    assertFalse(changed.passed());
    assertEquals(List.of("CHR-A01:/dif/DIF-015"), changed.unregisteredDifferences());
    assertEquals(List.of(FIXTURE_DIF015), changed.unusedDifferences());
    assertEquals(
        List.of(
            "OBSERVATION_CONTRACT_CHANGED:DIF-015:CHR-A01:/dif/DIF-015",
            "UNREGISTERED_DIFF:CHR-A01:/dif/DIF-015",
            "UNUSED_DIF:DIF-015"),
        changed.failures());

    Fixture invalid = fixture("isolated-invalid-claim");
    mutate(
        invalid.observations(),
        root ->
            ((ObjectNode) root.path(FIXTURE_OBSERVATIONS).get(0))
                .put(FIXTURE_EXPECTED_NK, "wrong-expectation"));
    ArtifactComparator.ComparisonResult rejected =
        ArtifactComparator.compare(
            invalid.project(), invalid.current(), invalid.nk(), invalid.observations());
    assertFalse(rejected.passed());
    assertEquals(List.of(UNREGISTERED_BRAND), rejected.unregisteredDifferences());
    assertTrue(rejected.unusedDifferences().isEmpty());
    assertEquals(
        List.of(
            "OBSERVATION_NK_VALUE:DIF-001:CHR-U01:/brand",
            "BRAND_DIF_REQUIRED:CHR-U01:/brand",
            "UNREGISTERED_DIFF:CHR-U01:/brand"),
        rejected.failures());
  }

  @Test
  void requiresLoginTitleObservationEvenWhenAnotherCaseUsesBrandDifference() throws Exception {
    Fixture fixture = fixture("login-title-observation-missing");
    mutate(
        fixture.observations(),
        envelope -> {
          var observations = (ArrayNode) envelope.path(FIXTURE_OBSERVATIONS);
          observations.remove(observations.size() - 1);
        });

    var result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertFalse(result.passed());
    assertTrue(result.usedDifferences().contains(FIXTURE_DIF_001));
    assertContains(result.failures(), FIXTURE_LOGIN_TITLE_REQUIRED);
    assertEquals(List.of(FIXTURE_UNREGISTERED_LOGIN_TITLE), result.unregisteredDifferences());
  }

  @Test
  void rejectsLoginTitleObservationAtAnotherPointer() throws Exception {
    Fixture fixture = fixture("wrong-login-title-pointer");
    mutate(
        fixture.observations(),
        envelope -> {
          JsonNode observations = envelope.path(FIXTURE_OBSERVATIONS);
          var login = (ObjectNode) observations.get(observations.size() - 1);
          login.put(FIXTURE_POINTER, "/missingLoginField");
        });

    var result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertFalse(result.passed());
    assertContains(result.failures(), "OBSERVATION_LOGIN_TITLE_POINTER");
    assertContains(result.failures(), FIXTURE_LOGIN_TITLE_REQUIRED);
    assertEquals(List.of(FIXTURE_UNREGISTERED_LOGIN_TITLE), result.unregisteredDifferences());
  }

  @Test
  void rejectsCurrentLoginTitleOutsideTheApprovedPair() throws Exception {
    Fixture fixture = fixture("wrong-current-login-title");
    mutate(
        fixture.current().resolve(FIXTURE_CHR_A01_JSON),
        artifact -> artifact.put(FIXTURE_LOGIN_TITLE, FIXTURE_UNAPPROVED_LOGIN_TITLE));

    var result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertFalse(result.passed());
    assertContains(result.failures(), "OBSERVATION_LOGIN_TITLE_CURRENT");
    assertContains(result.failures(), FIXTURE_LOGIN_TITLE_REQUIRED);
    assertEquals(List.of(FIXTURE_UNREGISTERED_LOGIN_TITLE), result.unregisteredDifferences());
  }

  @Test
  void rejectsNkLoginTitleOutsideTheApprovedPair() throws Exception {
    Fixture fixture = fixture("wrong-nk-login-title");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_A01_JSON),
        artifact -> artifact.put(FIXTURE_LOGIN_TITLE, FIXTURE_UNAPPROVED_LOGIN_TITLE));

    var result =
        ArtifactComparator.compare(
            fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
    assertFalse(result.passed());
    assertContains(result.failures(), "OBSERVATION_LOGIN_TITLE_NK");
    assertContains(result.failures(), FIXTURE_LOGIN_TITLE_REQUIRED);
    assertEquals(List.of(FIXTURE_UNREGISTERED_LOGIN_TITLE), result.unregisteredDifferences());
  }

  @Test
  void requiresSearchTitleEvidenceEvenWithoutAnyUnregisteredDrift() throws Exception {
    Fixture fixture = fixture("unchanged-search-title-without-observation");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_U02_JSON),
        root -> ((ArrayNode) root.path(FIXTURE_TITLES)).set(1, FIXTURE_CURRENT_SEARCH_TITLE));
    removeObservation(fixture, FIXTURE_CHR_U02, FIXTURE_SEARCH_TITLE_POINTER);

    var result = compare(fixture);
    assertFalse(result.passed());
    assertEquals(List.of(BRAND_SEARCH_REQUIRED), result.failures());
    assertTrue(result.unregisteredDifferences().isEmpty());
  }

  @Test
  void requiresMenuBrandEvidenceFromTheMenuCase() throws Exception {
    Fixture fixture = fixture("missing-menu-brand-observation");
    removeObservation(fixture, FIXTURE_CHR_U01, FIXTURE_BRAND_POINTER);

    var result = compare(fixture);
    assertFalse(result.passed());
    assertTrue(result.usedDifferences().contains(FIXTURE_DIF_001));
    assertContains(result.failures(), "BRAND_DIF_REQUIRED:CHR-U01:/brand");
    assertEquals(List.of(UNREGISTERED_BRAND), result.unregisteredDifferences());
  }

  @Test
  void requiresBothCommonStyleTitlesWhenTheSecondOneChanged() throws Exception {
    Fixture fixture = fixture("missing-common-style-search-observation");
    removeObservation(fixture, FIXTURE_CHR_U02, FIXTURE_SEARCH_TITLE_POINTER);

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), BRAND_SEARCH_REQUIRED);
    assertEquals(List.of(UNREGISTERED_SEARCH), result.unregisteredDifferences());
  }

  @Test
  void refusesCommonStyleTitleOutsideApprovedBrandPositions() throws Exception {
    Fixture fixture = fixture("different-common-style-title-pointer");
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          ((ObjectNode)
                  claims.get(
                      findObservation(claims, FIXTURE_CHR_U02, FIXTURE_SEARCH_TITLE_POINTER)))
              .put(FIXTURE_POINTER, "/titles/2");
        });

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), "OBSERVATION_BRAND_POINTER");
    assertContains(result.failures(), BRAND_SEARCH_REQUIRED);
    assertEquals(List.of(UNREGISTERED_SEARCH), result.unregisteredDifferences());
  }

  @Test
  void leavesNonBrandTitleChangeUnregistered() throws Exception {
    Fixture fixture = fixture("changed-unapproved-sibling-title");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_U02_JSON),
        root -> ((ArrayNode) root.path(FIXTURE_TITLES)).set(2, "synthetic unrelated title change"));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertEquals(List.of("CHR-U02:/titles/2"), result.unregisteredDifferences());
    assertEquals(List.of("UNREGISTERED_DIFF:CHR-U02:/titles/2"), result.failures());
  }

  @Test
  void requiresCacheObservationEvenWhenTheOldHeaderWasUnchanged() throws Exception {
    Fixture fixture = fixture("missing-cache-control-observation");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_O01_JSON),
        root -> root.put(FIXTURE_CACHE_CONTROL, FIXTURE_CACHE_BEFORE));
    removeObservation(fixture, FIXTURE_CHR_O01, FIXTURE_CACHE_POINTER);

    var result = compare(fixture);
    assertFalse(result.passed());
    assertEquals(List.of(FIXTURE_CACHE_REQUIRED, "UNUSED_DIF:DIF-011"), result.failures());
    assertTrue(result.unregisteredDifferences().isEmpty());
  }

  @Test
  void rejectsCacheControlOtherThanApprovedNoStore() throws Exception {
    Fixture fixture = fixture("incorrect-cache-control");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_O01_JSON),
        root -> root.put(FIXTURE_CACHE_CONTROL, "private, max-age=0"));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_NK);
    assertContains(result.failures(), FIXTURE_CACHE_REQUIRED);
    assertEquals(List.of("CHR-O01:/cacheControl"), result.unregisteredDifferences());
  }

  @Test
  void rejectsCacheObservationForADifferentField() throws Exception {
    Fixture fixture = fixture("wrong-cache-control-field");
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          ((ObjectNode) claims.get(findObservation(claims, FIXTURE_CHR_O01, FIXTURE_CACHE_POINTER)))
              .put(FIXTURE_POINTER, "/cacheControlMissing");
        });

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_POINTER);
    assertContains(result.failures(), FIXTURE_CACHE_REQUIRED);
    assertEquals(List.of("CHR-O01:/cacheControl"), result.unregisteredDifferences());
  }

  @Test
  void rejectsStringCountEvenWhenItsCharactersMatchTheApprovedNumber() throws Exception {
    Fixture fixture = fixture("session-count-is-not-numeric");
    mutate(fixture.nk().resolve(FIXTURE_CHR_A02_JSON), root -> root.put(FIXTURE_COUNT, "2"));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_NK);
    assertEquals(List.of("CHR-A02:/observedActiveSessionCount"), result.unregisteredDifferences());
  }

  @Test
  void requiresOldestInvalidationEvidenceAlongsideTheCorrectCount() throws Exception {
    Fixture fixture = fixture("missing-oldest-invalidation-observation");
    mutate(fixture.nk().resolve(FIXTURE_CHR_A02_JSON), root -> root.put(FIXTURE_OLDEST, false));
    removeObservation(fixture, FIXTURE_CHR_A02, "/oldestSessionInvalidated");

    var result = compare(fixture);
    assertFalse(result.passed());
    assertEquals(
        List.of("FIXED_DIF_REQUIRED:CHR-A02:/oldestSessionInvalidated"), result.failures());
    assertTrue(result.unregisteredDifferences().isEmpty());
  }

  @Test
  void leavesAnAdditionalSessionLossUnregistered() throws Exception {
    Fixture fixture = fixture("also-inactivated-newest-session");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_A02_JSON),
        root -> ((ArrayNode) root.path(FIXTURE_ACTIVE)).set(2, BooleanNode.FALSE));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertEquals(
        List.of("CHR-A02:/sessionActiveOldestToNewest/2"), result.unregisteredDifferences());
    assertEquals(
        List.of("UNREGISTERED_DIFF:CHR-A02:/sessionActiveOldestToNewest/2"), result.failures());
  }

  @Test
  void rejectsAnUnapprovedConfiguredMaximum() throws Exception {
    Fixture fixture = fixture("unapproved-session-maximum");
    mutate(fixture.nk().resolve(FIXTURE_CHR_A02_JSON), root -> root.put(FIXTURE_LIMIT, 3));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), "NK_SESSION_LIMIT");
    assertEquals(List.of("CHR-A02:/configuredMaximumSessions"), result.unregisteredDifferences());
  }

  @Test
  void requiresTheOldestSessionsObservedRedirect() throws Exception {
    Fixture fixture = fixture("missing-oldest-redirect-observation");
    removeObservation(fixture, FIXTURE_CHR_A02, FIXTURE_REDIRECT_POINTER);

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(
        result.failures(), "FIXED_DIF_REQUIRED:CHR-A02:/sessionRedirectsOldestToNewest/0");
    assertEquals(
        List.of("CHR-A02:/sessionRedirectsOldestToNewest/0"), result.unregisteredDifferences());
  }

  @Test
  void requiresTheSecondMediaCaseToReportItsOwnRangeStatus() throws Exception {
    Fixture fixture = fixture("missing-audio-range-status-observation");
    removeObservation(fixture, FIXTURE_CHR_M07, FIXTURE_INVALID_RANGE_STATUS);

    var result = compare(fixture);
    assertFalse(result.passed());
    assertTrue(result.usedDifferences().contains(FIXTURE_DIF_012));
    assertContains(result.failures(), "FIXED_DIF_REQUIRED:CHR-M07:/invalidRange/status");
    assertEquals(List.of(AUDIO_STATUS_DIFFERENCE), result.unregisteredDifferences());
  }

  @Test
  void rejectsAContentRangeWithTheWrongVideoSize() throws Exception {
    Fixture fixture = fixture("wrong-video-total-in-range");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_M04 + FIXTURE_JSON_SUFFIX),
        root -> object(root, FIXTURE_INVALID_RANGE).put(FIXTURE_CONTENT_RANGE, "bytes */84084293"));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_NK);
    assertEquals(List.of("CHR-M04:/invalidRange/contentRange"), result.unregisteredDifferences());
  }

  @Test
  void rejectsTheOtherApprovedHeaderSelectorAtTheStatusPointer() throws Exception {
    Fixture fixture = fixture("wrong-selector-for-range-status");
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          ((ObjectNode)
                  claims.get(
                      findObservation(claims, FIXTURE_CHR_M04, FIXTURE_INVALID_RANGE_STATUS)))
              .put("selector", FIXTURE_RANGE_SELECTOR);
        });

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), "OBSERVATION_RANGE_SELECTOR");
    assertEquals(List.of("CHR-M04:/invalidRange/status"), result.unregisteredDifferences());
  }

  @Test
  void rejectsAnInvalidRangeStatusOfAnotherHttpError() throws Exception {
    Fixture fixture = fixture("wrong-audio-range-http-status");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_M07 + FIXTURE_JSON_SUFFIX),
        root -> object(root, FIXTURE_INVALID_RANGE).put(FIXTURE_STATUS, 404));

    var result = compare(fixture);
    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_NK);
    assertEquals(List.of(AUDIO_STATUS_DIFFERENCE), result.unregisteredDifferences());
  }

  @Test
  void acceptsTheExactEmptySearchMessageAtItsVisibleField() throws Exception {
    var result = compare(fixture("approved-empty-search-message"));

    assertTrue(result.passed(), result.failures().toString());
    assertTrue(result.usedDifferences().contains(FIXTURE_DIF_008));
  }

  @Test
  void requiresAnExplicitEmptySearchObservation() throws Exception {
    Fixture fixture = fixture("missing-empty-search-observation");
    removeObservation(fixture, FIXTURE_CHR_S04, FIXTURE_SEARCH_EMPTY_POINTER);

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_SEARCH_EMPTY_REQUIRED);
    assertEquals(List.of(SEARCH_EMPTY_DIFFERENCE), result.unregisteredDifferences());
  }

  @Test
  void rejectsASelfReportedDifferentNkEmptySearchLabel() throws Exception {
    Fixture fixture = fixture("self-reported-empty-search-label");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_S04 + FIXTURE_JSON_SUFFIX),
        root -> root.put(FIXTURE_SEARCH_EMPTY_TEXT, FIXTURE_UNAPPROVED_EMPTY_LABEL));
    changeSearchEmptyClaim(
        fixture, claim -> claim.put(FIXTURE_EXPECTED_NK, FIXTURE_UNAPPROVED_EMPTY_LABEL));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_NK);
    assertEquals(List.of(SEARCH_EMPTY_DIFFERENCE), result.unregisteredDifferences());
  }

  @Test
  void rejectsAnEmptySearchClaimOnAnUnrelatedField() throws Exception {
    Fixture fixture = fixture("empty-search-claim-on-extra-field");
    mutate(
        fixture.current().resolve(FIXTURE_CHR_S04 + FIXTURE_JSON_SUFFIX),
        root -> root.put(FIXTURE_EXTRA, ""));
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_S04 + FIXTURE_JSON_SUFFIX),
        root -> root.put(FIXTURE_EXTRA, FIXTURE_SEARCH_EMPTY_NK));
    changeSearchEmptyClaim(fixture, claim -> claim.put(FIXTURE_POINTER, "/" + FIXTURE_EXTRA));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_POINTER);
    assertTrue(result.unregisteredDifferences().contains("CHR-S04:/extra"));
  }

  @Test
  void doesNotTreatAnL01ClaimAsTheRequiredS04Observation() throws Exception {
    Fixture fixture = fixture("empty-claim-from-log-case");
    changeSearchEmptyClaim(fixture, claim -> claim.put(FIXTURE_CASEID, FIXTURE_CHR_L01));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_SEARCH_EMPTY_REQUIRED);
    assertFalse(result.failures().contains(FIXTURE_FIXED_POINTER));
    assertEquals(List.of(SEARCH_EMPTY_DIFFERENCE), result.unregisteredDifferences());
  }

  private static void changeSearchEmptyClaim(Fixture fixture, Consumer<ObjectNode> change)
      throws Exception {
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          change.accept(
              (ObjectNode)
                  claims.get(
                      findObservation(claims, FIXTURE_CHR_S04, FIXTURE_SEARCH_EMPTY_POINTER)));
        });
  }

  @Test
  void acceptsAnAbsentInlineAttributeWithTheDisabledScriptSubmitButton() throws Exception {
    var result = compare(fixture("approved-game-change-observation"));
    assertTrue(result.passed(), result.failures().toString());
    assertTrue(result.usedDifferences().contains(FIXTURE_DIF_013));
  }

  @Test
  void rejectsAMissingGameChangeFieldInsteadOfAnObservedAbsentAttribute() throws Exception {
    Fixture fixture = fixture("missing-game-attribute-projection");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_S02 + FIXTURE_JSON_SUFFIX),
        root -> root.remove(FIXTURE_GAME_CHANGE));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), "OBSERVATION_NK_POINTER:DIF-013:CHR-S02:/gameOnchange");
    assertEquals(List.of(GAME_CHANGE_DIFFERENCE), result.unregisteredDifferences());
  }

  @Test
  void refusesASelfReportedNewInlineChangeHandler() throws Exception {
    Fixture fixture = fixture("inline-change-handler-remains");
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_S02 + FIXTURE_JSON_SUFFIX),
        root -> root.put(FIXTURE_GAME_CHANGE, FIXTURE_OTHER_HANDLER));
    changeGameClaim(fixture, row -> row.put(FIXTURE_EXPECTED_NK, FIXTURE_OTHER_HANDLER));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_NK);
    assertEquals(List.of(GAME_CHANGE_DIFFERENCE), result.unregisteredDifferences());
  }

  @Test
  void refusesTheGameChangeClaimAtAnotherField() throws Exception {
    Fixture fixture = fixture("game-change-claim-on-extra-field");
    mutate(
        fixture.current().resolve(FIXTURE_CHR_S02 + FIXTURE_JSON_SUFFIX),
        root -> root.put(FIXTURE_EXTRA, FIXTURE_CURRENT_HANDLER));
    mutate(
        fixture.nk().resolve(FIXTURE_CHR_S02 + FIXTURE_JSON_SUFFIX),
        root -> root.putNull(FIXTURE_EXTRA));
    changeGameClaim(fixture, row -> row.put(FIXTURE_POINTER, "/" + FIXTURE_EXTRA));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), FIXTURE_FIXED_POINTER);
    assertTrue(result.unregisteredDifferences().contains("CHR-S02:/extra"));
  }

  @Test
  void rejectsTheAbsentFallbackButtonEvenIfBothArtifactsAgree() throws Exception {
    Fixture fixture = fixture("game-change-submit-button-lost");
    for (Path artifacts : List.of(fixture.current(), fixture.nk())) {
      mutate(
          artifacts.resolve(FIXTURE_CHR_S02 + FIXTURE_JSON_SUFFIX),
          root -> root.put(FIXTURE_GAME_CHANGE_FALLBACK, false));
    }

    var result = compare(fixture);

    assertFalse(result.passed());
    assertEquals(
        List.of("CURRENT_GAME_CHANGE_FALLBACK", "NK_GAME_CHANGE_FALLBACK"), result.failures());
    assertTrue(result.unregisteredDifferences().isEmpty());
  }

  @Test
  void requiresAnExplicitGameChangeClaim() throws Exception {
    Fixture fixture = fixture("game-change-without-observation");
    removeObservation(fixture, FIXTURE_CHR_S02, FIXTURE_GAME_CHANGE_POINTER);

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(result.failures(), REQUIRED_GAME_CHANGE);
    assertEquals(List.of(GAME_CHANGE_DIFFERENCE), result.unregisteredDifferences());
  }

  private static void changeGameClaim(Fixture fixture, Consumer<ObjectNode> change)
      throws Exception {
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          change.accept(
              (ObjectNode)
                  claims.get(
                      findObservation(claims, FIXTURE_CHR_S02, FIXTURE_GAME_CHANGE_POINTER)));
        });
  }

  @Test
  void rejectsLoginOnlyEvidenceAtTheFullL01Gate() throws Exception {
    Fixture fixture = fixture("login-only-is-not-full-l01");
    mutate(
        fixture.observations(),
        root -> root.set("correlatedLogEvidence", CorrelatedLogEvidenceValidatorTest.fixture()));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertTrue(result.unregisteredDifferences().isEmpty());
    assertEquals(
        List.of(
            "LOG_PROJECTION_REQUIRED_INITIAL_ACTION:MENU_VIEWED",
            "LOG_PROJECTION_REQUIRED_INITIAL_ACTION:LOG_SEARCHED"),
        result.failures());
  }

  @Test
  void acceptsTheCommonErrorPresentationWithThreeExplicitFalseLeakFlags() throws Exception {
    var result = compare(fixture("error-projection-closed"));
    assertTrue(result.passed(), result.failures().toString());
    assertTrue(result.usedDifferences().contains("DIF-005"));
  }

  @Test
  void rejectsEveryPositiveLeakOnEachSide() throws Exception {
    for (String field : FIXTURE_ERROR_FLAGS) {
      Fixture fixture = fixture("positive-disclosure-" + field);
      for (Path artifacts : List.of(fixture.current(), fixture.nk())) {
        Path projection = errorProjection(artifacts);
        mutate(projection, root -> root.put(field, true));

        var result = compare(fixture);
        String prefix =
            artifacts.equals(fixture.current())
                ? FIXTURE_CURRENT_ERROR_PREFIX
                : FIXTURE_NK_ERROR_PREFIX;
        assertFalse(result.passed());
        assertContains(result.failures(), prefix + field);
        assertEquals(List.of(FIXTURE_CHR_E01 + ":/" + field), result.unregisteredDifferences());

        mutate(projection, root -> root.put(field, false));
      }
    }
  }

  @Test
  void rejectsAnIdenticalPositiveLeakEvenWithoutAChangedField() throws Exception {
    Fixture fixture = fixture("shared-positive-disclosure");
    for (Path artifacts : List.of(fixture.current(), fixture.nk()))
      mutate(errorProjection(artifacts), root -> root.put(FIXTURE_SECRET_LEAK, true));

    var result = compare(fixture);

    assertFalse(result.passed());
    assertTrue(result.unregisteredDifferences().isEmpty());
    assertContains(result.failures(), FIXTURE_CURRENT_ERROR_PREFIX + FIXTURE_SECRET_LEAK);
    assertContains(result.failures(), FIXTURE_NK_ERROR_PREFIX + FIXTURE_SECRET_LEAK);
  }

  @Test
  void rejectsMissingNullAndTextualLeakFlags() throws Exception {
    Fixture fixture = fixture("disclosure-flag-type");
    mutate(
        errorProjection(fixture.nk()),
        root -> {
          root.remove(FIXTURE_SECRET_LEAK);
          root.putNull(FIXTURE_PATH_LEAK);
          root.put(FIXTURE_EXCEPTION_LEAK, "false");
        });

    var result = compare(fixture);

    assertFalse(result.passed());
    for (String field : FIXTURE_ERROR_FLAGS)
      assertContains(result.failures(), FIXTURE_NK_ERROR_PREFIX + field);
  }

  @Test
  void rejectsAnErrorStyleClaimThatTriesToCoverAChangedLeakFlag() throws Exception {
    Fixture fixture = fixture("style-claim-on-disclosure");
    mutate(errorProjection(fixture.nk()), root -> root.put(FIXTURE_PATH_LEAK, true));
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          var claim =
              (ObjectNode)
                  claims.get(findObservation(claims, FIXTURE_CHR_E01, FIXTURE_UI_ERROR_POINTER));
          claim
              .put(FIXTURE_POINTER, "/" + FIXTURE_PATH_LEAK)
              .put(FIXTURE_EXPECTED_CURRENT, false)
              .put(FIXTURE_EXPECTED_NK, true);
        });

    var result = compare(fixture);

    assertFalse(result.passed());
    assertContains(
        result.failures(), "OBSERVATION_ERROR_DISCLOSURE_FIELD:DIF-005:CHR-E01:/absolutePathLeak");
    assertTrue(result.unregisteredDifferences().contains("CHR-E01:/absolutePathLeak"));
  }

  private static Path errorProjection(Path artifacts) {
    return artifacts.resolve(FIXTURE_CHR_E01 + FIXTURE_JSON_SUFFIX);
  }

  private static ArtifactComparator.ComparisonResult compare(Fixture fixture) throws IOException {
    return ArtifactComparator.compare(
        fixture.project(), fixture.current(), fixture.nk(), fixture.observations());
  }

  private static void removeObservation(Fixture fixture, String caseId, String pointer)
      throws Exception {
    mutate(
        fixture.observations(),
        root -> {
          var claims = (ArrayNode) root.path(FIXTURE_OBSERVATIONS);
          claims.remove(findObservation(claims, caseId, pointer));
        });
  }

  private static int findObservation(ArrayNode claims, String caseId, String pointer) {
    for (int i = 0; i < claims.size(); i++) {
      JsonNode claim = claims.get(i);
      if (caseId.equals(claim.path(FIXTURE_CASEID).asText())
          && pointer.equals(claim.path(FIXTURE_POINTER).asText())) {
        return i;
      }
    }
    throw new AssertionError("independent observation missing");
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
    Path current = Files.createDirectories(root.resolve(FIXTURE_CURRENT));
    Path nk = Files.createDirectories(root.resolve("nk"));
    java.util.Map<String, ObjectNode> currentArtifacts = new java.util.LinkedHashMap<>();
    java.util.Map<String, ObjectNode> nkArtifacts = new java.util.LinkedHashMap<>();
    for (String caseId : CASE_IDS) {
      currentArtifacts.put(
          caseId,
          JSON.createObjectNode().put(FIXTURE_CASEID, caseId).put(FIXTURE_STATUS, FIXTURE_PASS));
      nkArtifacts.put(
          caseId,
          JSON.createObjectNode().put(FIXTURE_CASEID, caseId).put(FIXTURE_STATUS, FIXTURE_PASS));
    }

    for (String field : FIXTURE_ERROR_FLAGS) {
      currentArtifacts.get(FIXTURE_CHR_E01).put(field, false);
      nkArtifacts.get(FIXTURE_CHR_E01).put(field, false);
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
      if (FIXTURE_DIF_001.equals(oracle.id())) {
        currentArtifact.set(FIXTURE_BRAND, currentValue);
        nkArtifact.set(FIXTURE_BRAND, nkValue);
        pointer = FIXTURE_BRAND_POINTER;
      } else if (FIXTURE_DIF_008.equals(oracle.id())) {
        currentArtifact.set(FIXTURE_SEARCH_EMPTY_TEXT, currentValue);
        nkArtifact.set(FIXTURE_SEARCH_EMPTY_TEXT, nkValue);
        pointer = FIXTURE_SEARCH_EMPTY_POINTER;
      } else if (ASYNC_MENU_DIFFERENCE.equals(oracle.id())) {
        currentDif.set(oracle.id(), JSON.valueToTree(List.of(FIXTURE_SAME, oracle.currentValue())));
        nkDif.set(oracle.id(), JSON.valueToTree(List.of(FIXTURE_SAME, oracle.nkValue())));
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
    var commonCurrent = currentArtifacts.get(FIXTURE_CHR_U02).putArray(FIXTURE_TITLES);
    var commonNk = nkArtifacts.get(FIXTURE_CHR_U02).putArray(FIXTURE_TITLES);
    commonCurrent.add(FIXTURE_SCHUBERT).add(FIXTURE_CURRENT_SEARCH_TITLE);
    commonNk.add(FIXTURE_SCHUBERT_NK).add(FIXTURE_NK_SEARCH_TITLE);
    for (String unchangedTitle : List.of("Scenario Games", "Animation", "Music", "Logs")) {
      commonCurrent.add(unchangedTitle);
      commonNk.add(unchangedTitle);
    }
    observationItems.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_U02,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            FIXTURE_MENU_TITLE_POINTER,
            FIXTURE_SCHUBERT,
            FIXTURE_SCHUBERT_NK));
    observationItems.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_U02,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            FIXTURE_SEARCH_TITLE_POINTER,
            FIXTURE_CURRENT_SEARCH_TITLE,
            FIXTURE_NK_SEARCH_TITLE));
    addCacheObservation(
        currentArtifacts.get(FIXTURE_CHR_O01), nkArtifacts.get(FIXTURE_CHR_O01), observationItems);
    ObjectNode currentGame = currentArtifacts.get(FIXTURE_CHR_S02);
    ObjectNode nkGame = nkArtifacts.get(FIXTURE_CHR_S02);
    currentGame
        .put(FIXTURE_GAME_CHANGE, FIXTURE_CURRENT_HANDLER)
        .put(FIXTURE_GAME_CHANGE_FALLBACK, true);
    nkGame.putNull(FIXTURE_GAME_CHANGE).put(FIXTURE_GAME_CHANGE_FALLBACK, true);
    observationItems.add(
        observation(
            FIXTURE_DIF_013,
            FIXTURE_CHR_S02,
            FIXTURE_GAME_CHANGE_FIELD,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_GAME_CHANGE_FIELD,
            FIXTURE_GAME_CHANGE_POINTER,
            FIXTURE_CURRENT_HANDLER,
            null));
    addSessionObservations(
        currentArtifacts.get(FIXTURE_CHR_A02), nkArtifacts.get(FIXTURE_CHR_A02), observationItems);
    addRangeObservations(
        observationItems,
        FIXTURE_CHR_M04,
        currentArtifacts.get(FIXTURE_CHR_M04),
        nkArtifacts.get(FIXTURE_CHR_M04),
        "bytes 999999999999-84084291/84084292",
        "bytes */84084292");
    addRangeObservations(
        observationItems,
        FIXTURE_CHR_M07,
        currentArtifacts.get(FIXTURE_CHR_M07),
        nkArtifacts.get(FIXTURE_CHR_M07),
        "bytes 999999999999-3388626/3388627",
        "bytes */3388627");
    currentArtifacts.get(FIXTURE_CHR_A01).put(FIXTURE_LOGIN_TITLE, FIXTURE_CURRENT_LOGIN_TITLE);
    nkArtifacts.get(FIXTURE_CHR_A01).put(FIXTURE_LOGIN_TITLE, FIXTURE_NK_LOGIN_TITLE);
    observationItems.add(
        observation(
            FIXTURE_DIF_001,
            FIXTURE_CHR_A01,
            FIXTURE_BRAND,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_BRAND,
            FIXTURE_LOGIN_POINTER,
            FIXTURE_CURRENT_LOGIN_TITLE,
            FIXTURE_NK_LOGIN_TITLE));
    currentArtifacts.forEach(
        (caseId, artifact) ->
            uncheckedWriteJson(current.resolve(caseId + FIXTURE_JSON_SUFFIX), artifact));
    nkArtifacts.forEach(
        (caseId, artifact) ->
            uncheckedWriteJson(nk.resolve(caseId + FIXTURE_JSON_SUFFIX), artifact));
    Path observations = root.resolve("observations.json");
    ObjectNode envelope = JSON.createObjectNode().put("version", 1);
    envelope.set(FIXTURE_OBSERVATIONS, observationItems);
    envelope.set("correlatedLogEvidence", CorrelatedMenuActionContractTest.fixture());
    ObjectNode artifactBinding = envelope.putObject("correlatedLogArtifacts");
    artifactBinding.set(FIXTURE_CURRENT, currentArtifacts.get(FIXTURE_CHR_L01).deepCopy());
    artifactBinding.set("nk", nkArtifacts.get(FIXTURE_CHR_L01).deepCopy());
    writeJson(observations, envelope);
    return new Fixture(project, current, nk, observations);
  }

  private static void addCacheObservation(
      ObjectNode current, ObjectNode nk, ArrayNode observations) {
    current.put(FIXTURE_CACHE_CONTROL, FIXTURE_CACHE_BEFORE);
    nk.put(FIXTURE_CACHE_CONTROL, FIXTURE_CACHE_AFTER);
    observations.add(
        observation(
            FIXTURE_DIF_011,
            FIXTURE_CHR_O01,
            "cache.control",
            "required",
            "header",
            "cache-control",
            FIXTURE_CACHE_POINTER,
            FIXTURE_CACHE_BEFORE,
            FIXTURE_CACHE_AFTER));
  }

  private static void addSessionObservations(
      ObjectNode current, ObjectNode nk, ArrayNode observations) {
    current.put(FIXTURE_LIMIT, 2).put(FIXTURE_COUNT, 3).put(FIXTURE_OLDEST, false);
    nk.put(FIXTURE_LIMIT, 2).put(FIXTURE_COUNT, 2).put(FIXTURE_OLDEST, true);
    current.putArray(FIXTURE_ACTIVE).add(true).add(true).add(true);
    nk.putArray(FIXTURE_ACTIVE).add(false).add(true).add(true);
    current.putArray(FIXTURE_REDIRECT).add("/").add("/").add("/");
    nk.putArray(FIXTURE_REDIRECT).add(FIXTURE_SESSION_EXPIRED).add("/").add("/");
    observations.add(
        sessionObservation(FIXTURE_COUNT_POINTER, IntNode.valueOf(3), IntNode.valueOf(2)));
    observations.add(
        sessionObservation("/oldestSessionInvalidated", BooleanNode.FALSE, BooleanNode.TRUE));
    observations.add(
        sessionObservation("/sessionActiveOldestToNewest/0", BooleanNode.TRUE, BooleanNode.FALSE));
    observations.add(
        sessionObservation(
            FIXTURE_REDIRECT_POINTER,
            TextNode.valueOf("/"),
            TextNode.valueOf(FIXTURE_SESSION_EXPIRED)));
  }

  private static void addRangeObservations(
      ArrayNode observations,
      String caseId,
      ObjectNode current,
      ObjectNode nk,
      String currentContentRange,
      String nkContentRange) {
    current
        .putObject(FIXTURE_INVALID_RANGE)
        .put(FIXTURE_STATUS, 500)
        .put(FIXTURE_CONTENT_RANGE, currentContentRange);
    nk.putObject(FIXTURE_INVALID_RANGE)
        .put(FIXTURE_STATUS, 416)
        .put(FIXTURE_CONTENT_RANGE, nkContentRange);
    var status =
        observation(
            FIXTURE_DIF_012,
            caseId,
            FIXTURE_RANGE_FIELD,
            FIXTURE_DIFFERENCE,
            FIXTURE_HEADER,
            FIXTURE_STATUS,
            FIXTURE_INVALID_RANGE_STATUS,
            "",
            "");
    status.put(FIXTURE_EXPECTED_CURRENT, 500).put(FIXTURE_EXPECTED_NK, 416);
    observations.add(status);
    observations.add(
        observation(
            FIXTURE_DIF_012,
            caseId,
            FIXTURE_RANGE_FIELD,
            FIXTURE_DIFFERENCE,
            FIXTURE_HEADER,
            FIXTURE_RANGE_SELECTOR,
            FIXTURE_INVALID_RANGE_HEADER,
            currentContentRange,
            nkContentRange));
  }

  private static ObjectNode sessionObservation(String pointer, JsonNode current, JsonNode nk) {
    var row =
        observation(
            FIXTURE_DIF_016,
            FIXTURE_CHR_A02,
            FIXTURE_RULE_SESSION,
            FIXTURE_DIFFERENCE,
            FIXTURE_SEMANTIC,
            FIXTURE_RULE_SESSION,
            pointer,
            "",
            "");
    row.set(FIXTURE_EXPECTED_CURRENT, current);
    row.set(FIXTURE_EXPECTED_NK, nk);
    return row;
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
        .put(FIXTURE_CASEID, caseId)
        .put("field", field)
        .put("mode", mode)
        .put("selectorType", selectorType)
        .put("selector", selector)
        .put(FIXTURE_POINTER, pointer)
        .put(FIXTURE_EXPECTED_CURRENT, expectedCurrent)
        .put(FIXTURE_EXPECTED_NK, expectedNk);
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
    String previous = System.getProperty(FIXTURE_CHR_PROJECTROOT);
    try {
      System.setProperty(FIXTURE_CHR_PROJECTROOT, projectRoot.toString());
      action.run();
    } finally {
      if (previous == null) System.clearProperty(FIXTURE_CHR_PROJECTROOT);
      else System.setProperty(FIXTURE_CHR_PROJECTROOT, previous);
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
