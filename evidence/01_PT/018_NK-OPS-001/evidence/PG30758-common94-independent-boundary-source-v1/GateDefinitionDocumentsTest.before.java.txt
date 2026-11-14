package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-CHR-DEF-001..011. Pure definition checks, never capture/baseline/preflight/run validation. */
final class GateDefinitionDocumentsTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final int CONTRACT = 0;
  private static final int CATALOG = 1;
  private static final int SCHEMA = 2;
  private static final int DIFFERENCES = 3;
  private static final int BROWSER = 4;
  private static final int REQUIREMENTS = 5;
  private static final String BAD_VALUE = "bad";
  private static final String UNKNOWN_CASE = "CHR-Z99";
  private static final String VERSION = "version";
  private static final String CASES = "cases";
  private static final String ACTION_CASE = "CHR-A01";
  private static final List<String> RESOURCES =
      List.of(
          "cases/gate-contract.json",
          "cases/catalog.json",
          "cases/schema.json",
          "cases/dif-allowlist.json",
          "browser/manifest.json",
          "cases/case-requirements.json");

  @Test
  void acceptsPinnedPublicDefinitionsWithoutMutationAndReturnsImmutableDiagnostics()
      throws Exception {
    List<JsonNode> input = fixture();
    List<JsonNode> unchanged = input.stream().<JsonNode>map(JsonNode::deepCopy).toList();
    assertEquals(24, input.get(CONTRACT).path("caseOrder").size());
    assertEquals(16, input.get(DIFFERENCES).path("differences").size());
    assertEquals("Log", input.get(CATALOG).path(CASES).get(20).path("group").asText());
    List<String> result = validate(input);
    assertEquals(List.of(), result);
    assertThrows(UnsupportedOperationException.class, () -> result.add("change"));
    assertEquals(unchanged, input);
  }

  @Test
  void rejectsEveryJavaNullDocumentWithFixedSignal() throws Exception {
    for (int index = 0; index < RESOURCES.size(); index++) {
      List<JsonNode> input = fixture();
      input.set(index, null);
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> validate(input));
      assertEquals("definition document is required", failure.getMessage());
    }
  }

  @Test
  void malformedJsonShapesProduceFailuresRatherThanNpe() throws Exception {
    for (int index = 0; index < RESOURCES.size(); index++) {
      for (JsonNode replacement :
          List.of(
              JSON.nullNode(), JSON.createArrayNode(), JSON.getNodeFactory().textNode(BAD_VALUE))) {
        List<JsonNode> input = fixture();
        input.set(index, replacement);
        assertFalse(validate(input).isEmpty());
      }
    }
  }

  @Test
  void allFourVersionCallersRejectCoercionOverflowMissingAndNull() throws Exception {
    int[] indices = {CONTRACT, CATALOG, DIFFERENCES, REQUIREMENTS};
    String[] codes = {"CONTRACT_VERSION", "CATALOG_VERSION", "DIF_VERSION", "REQ_VERSION"};
    List<JsonNode> invalid =
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().textNode("1"),
            JSON.getNodeFactory().numberNode(1.0),
            JSON.getNodeFactory().numberNode(new BigInteger("4294967297")),
            JSON.getNodeFactory().numberNode(0),
            JSON.getNodeFactory().numberNode(2));
    for (int offset = 0; offset < indices.length; offset++) {
      for (JsonNode value : invalid) {
        List<JsonNode> input = fixture();
        object(input, indices[offset]).set(VERSION, value);
        assertContains(input, codes[offset]);
      }
      List<JsonNode> missing = fixture();
      object(missing, indices[offset]).remove(VERSION);
      assertContains(missing, codes[offset]);
      List<JsonNode> largeIntegerOne = fixture();
      object(largeIntegerOne, indices[offset]).put(VERSION, BigInteger.ONE);
      assertEquals(List.of(), validate(largeIntegerOne));
    }
  }

  @Test
  void contractCountsOrderIdentifiersAndHashesUseIndependentConstraints() throws Exception {
    List<JsonNode> input = fixture();
    ObjectNode contract = object(input, CONTRACT);
    contract.putArray("gates").add("CHR-G01");
    ArrayNode cases = contract.withArray("caseOrder");
    cases.set(1, cases.get(0));
    cases.remove(23);
    contract.putArray("differenceIds");
    contract.put("baselineCommit", "not-a-commit");
    contract.put("baselineAggregateSha256", "UPPERCASE");
    assertContains(
        input,
        "CONTRACT_GATE_IDS",
        "CONTRACT_CASE_COUNT",
        "CONTRACT_CASE_DUPLICATE",
        "CONTRACT_DIFFERENCE_COUNT",
        "CONTRACT_BASELINE_COMMIT",
        "CONTRACT_BASELINE_HASH");
  }

  @Test
  void schemaDraftShapeAndItemConstraintsCannotBeWeakened() throws Exception {
    List<JsonNode> input = fixture();
    ObjectNode schema = object(input, SCHEMA);
    schema.put("$schema", "invalid").put("type", "array");
    schema.putArray("required").add(CASES);
    ObjectNode cases = schema.withObject("/properties/cases");
    cases.put("minItems", 23).put("maxItems", 25);
    cases.withObject("/items").putArray("required").add("id");
    assertContains(
        input,
        "SCHEMA_DRAFT",
        "SCHEMA_ROOT_TYPE",
        "SCHEMA_REQUIRED",
        "SCHEMA_MIN_ITEMS",
        "SCHEMA_MAX_ITEMS",
        "SCHEMA_CASE_REQUIRED");
  }

  @Test
  void catalogRejectsDuplicateMalformedUnknownAndShortIdsAndWrongModes() throws Exception {
    List<JsonNode> input = fixture();
    ArrayNode cases = object(input, CATALOG).withArray(CASES);
    for (int index : List.of(0, 1)) {
      ((ObjectNode) cases.get(index))
          .put("id", "X")
          .put("group", BAD_VALUE)
          .put("current", BAD_VALUE)
          .put("nk", BAD_VALUE);
    }
    ((ObjectNode) cases.get(23)).put("id", UNKNOWN_CASE).put("group", BAD_VALUE);
    assertContains(
        input,
        "CATALOG_DUPLICATE:X",
        "CATALOG_ID:X",
        "CATALOG_GROUP:X",
        "CATALOG_CURRENT:X",
        "CATALOG_NK:X",
        "CATALOG_GROUP:CHR-Z99",
        "CATALOG_ORDER");
    List<JsonNode> missing = fixture();
    object(missing, CATALOG).put(CASES, "not-array");
    assertContains(missing, "CATALOG_CASES_NOT_ARRAY", "CATALOG_ORDER");
  }

  @Test
  void everyBrowserConstraintHasAnIndependentWrongValueIncludingSecondaryDimensions()
      throws Exception {
    String[] pointers = {
      "/playwrightJava",
      "/browser",
      "/browserRevision",
      "/locale",
      "/timezone",
      "/desktop/width",
      "/desktop/height",
      "/mobile/width",
      "/mobile/height",
      "/desktop/deviceScaleFactor",
      "/mobile/deviceScaleFactor",
      "/fonts",
      "/fontReady",
      "/colorScheme",
      "/reducedMotion"
    };
    String[] codes = {
      "BROWSER_PLAYWRIGHT",
      "BROWSER_NAME",
      "BROWSER_REVISION",
      "BROWSER_LOCALE",
      "BROWSER_TIMEZONE",
      "BROWSER_DESKTOP_VIEWPORT",
      "BROWSER_DESKTOP_VIEWPORT",
      "BROWSER_MOBILE_VIEWPORT",
      "BROWSER_MOBILE_VIEWPORT",
      "BROWSER_DEVICE_SCALE",
      "BROWSER_DEVICE_SCALE",
      "BROWSER_FONTS",
      "BROWSER_FONT_READY",
      "BROWSER_COLOR_SCHEME",
      "BROWSER_REDUCED_MOTION"
    };
    for (int index = 0; index < pointers.length; index++) {
      List<JsonNode> input = fixture();
      ObjectNode browser = object(input, BROWSER);
      String pointer = pointers[index];
      int lastSlash = pointer.lastIndexOf('/');
      ObjectNode parent =
          lastSlash == 0 ? browser : (ObjectNode) browser.at(pointer.substring(0, lastSlash));
      parent.put(pointer.substring(lastSlash + 1), "wrong");
      assertContains(input, codes[index]);
    }
  }

  @Test
  void differencesRejectUnknownModesCasesBroadSelectorsDuplicatesAndEmptyValues() throws Exception {
    List<JsonNode> input = fixture();
    ArrayNode differences = object(input, DIFFERENCES).withArray("differences");
    ObjectNode first = (ObjectNode) differences.get(0);
    first.put("mode", "all").put("selectorType", "unknown").put("current", "").put("nk", "");
    first.putArray(CASES);
    first.putArray("selectors");
    ObjectNode second = (ObjectNode) differences.get(1);
    second.put("field", first.path("field").asText());
    second.putArray(CASES).add(ACTION_CASE).add(ACTION_CASE).add(UNKNOWN_CASE);
    second.putArray("selectors").add("same").add("same");
    String[] invalid = {"", "all*", "a..b", "$.all"};
    for (int index = 0; index < invalid.length; index++) {
      ((ObjectNode) differences.get(index + 2)).putArray("selectors").add(invalid[index]);
    }
    ((ObjectNode) differences.get(14)).put("id", "MISSING-015");
    assertContains(
        input,
        "DIF_MODE:DIF-001",
        "DIF_SELECTOR_TYPE:DIF-001",
        "DIF_CURRENT:DIF-001",
        "DIF_NK:DIF-001",
        "DIF_CASES_EMPTY:DIF-001",
        "DIF_SELECTOR_EMPTY:DIF-001",
        "DIF_DUPLICATE_FIELD:DIF-002",
        "DIF_CASES_DUPLICATE:DIF-002",
        "DIF_UNKNOWN_CASE:DIF-002:CHR-Z99",
        "DIF_SELECTOR_DUPLICATE:DIF-002",
        "DIF_SELECTOR_WILDCARD:DIF-003",
        "DIF_SELECTOR_WILDCARD:DIF-004",
        "DIF_SELECTOR_WILDCARD:DIF-005",
        "DIF_SELECTOR_WILDCARD:DIF-006",
        "DIF_ID_SEQUENCE",
        "DIF-015_CASE_COVERAGE");
    List<JsonNode> malformed = fixture();
    object(malformed, DIFFERENCES).put("differences", "not-array");
    assertContains(malformed, "DIF_NOT_ARRAY", "DIF_ID_SEQUENCE");
  }

  @Test
  void requirementsRejectMissingCoreKeysDuplicatesUnknownAndUnboundSupplementals()
      throws Exception {
    List<JsonNode> input = fixture();
    ObjectNode requirements = object(input, REQUIREMENTS);
    requirements.withObject("/requirements").putArray(ACTION_CASE).add("caseId").add("caseId");
    requirements.withObject("/requirements").putArray("CHR-A02").add("status");
    requirements.withObject("/requirements").remove("CHR-O01");
    ObjectNode supplemental = requirements.withObject("/supplementalChecks");
    supplemental.putArray("CHR-A02");
    supplemental.putArray("CHR-A03").add("unsafe-post-denied").add("unsafe-post-denied");
    supplemental.putArray(UNKNOWN_CASE).add("unknown");
    ObjectNode nkOnly = requirements.withObject("/nkOnlySupplementalChecks");
    nkOnly.putArray(UNKNOWN_CASE).add("unknown");
    nkOnly.putArray("CHR-E01").add("undefined");
    assertContains(
        input,
        "REQ_CASE_ORDER",
        "REQ_CORE:CHR-A01",
        "REQ_CORE:CHR-A02",
        "REQ_DUPLICATE:CHR-A01",
        "REQ_SUPPLEMENTAL_EMPTY:CHR-A02",
        "REQ_SUPPLEMENTAL_DUPLICATE:CHR-A03",
        "REQ_SUPPLEMENTAL_CASE:CHR-Z99",
        "REQ_NK_ONLY_CASE:CHR-Z99",
        "REQ_NK_ONLY_UNKNOWN:CHR-E01:undefined");
    for (String field : List.of("requirements", "supplementalChecks", "nkOnlySupplementalChecks")) {
      List<JsonNode> malformed = fixture();
      object(malformed, REQUIREMENTS).put(field, "wrong");
      assertFalse(validate(malformed).isEmpty());
    }
  }

  @Test
  void concurrentValidAndInvalidDefinitionsRemainIndependent() throws Exception {
    List<JsonNode> valid = fixture();
    List<JsonNode> invalid = fixture();
    object(invalid, CONTRACT).put(VERSION, 2);
    var workers = Executors.newFixedThreadPool(2);
    try {
      var first = workers.submit(() -> validate(valid));
      var second = workers.submit(() -> validate(invalid));
      assertEquals(List.of(), first.get(5, TimeUnit.SECONDS));
      assertTrue(second.get(5, TimeUnit.SECONDS).contains("CONTRACT_VERSION"));
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(List.of(), validate(valid));
  }

  static List<JsonNode> fixture() throws IOException {
    List<JsonNode> result = new ArrayList<>();
    for (String name : RESOURCES) {
      try (InputStream input = GateDefinitionDocumentsTest.class.getResourceAsStream("/" + name)) {
        if (input == null) throw new IOException("public definition resource missing");
        result.add(JSON.readTree(input));
      }
    }
    return result;
  }

  private static ObjectNode object(List<JsonNode> input, int index) {
    return (ObjectNode) input.get(index);
  }

  private static List<String> validate(List<JsonNode> input) {
    return GateContractValidator.validateDefinitions(
        input.get(CONTRACT),
        input.get(CATALOG),
        input.get(SCHEMA),
        input.get(DIFFERENCES),
        input.get(BROWSER),
        input.get(REQUIREMENTS));
  }

  private static void assertContains(List<JsonNode> input, String... codes) {
    List<String> failures = validate(input);
    for (String code : codes)
      assertTrue(failures.contains(code), () -> "missing fixed diagnostic: " + code);
  }
}
