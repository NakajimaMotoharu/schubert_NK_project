package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.MissingNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

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
  private static final String FIELD_BROWSER = "browser";
  private static final String FIELD_CASE_ORDER = "caseOrder";
  private static final String FIELD_DIFFERENCES = "differences";
  private static final String FIELD_TYPE = "type";
  private static final String SCHEMA_CASES = "/properties/cases";
  private static final String SCHEMA_VERSION = "/properties/version";
  private static final String FIELD_SELECTORS = "selectors";
  private static final String REQUIREMENTS_POINTER = "/requirements";
  private static final String SECOND_AUTH_CASE = "CHR-A02";
  private static final String SUPPLEMENTAL_POINTER = "/supplementalChecks";
  private static final String VIDEO_RANGE_CASE = "CHR-M04";
  private static final String VIDEO_NO_RANGE = "no-range-200";
  private static final String VIDEO_FIRST_RANGE = "multi-range-first";
  private static final String JSON_NULL = "null";
  private static final List<String> RESOURCES =
      List.of(
          "cases/gate-contract.json",
          "cases/catalog.json",
          "cases/schema.json",
          "cases/dif-allowlist.json",
          "browser/manifest.json",
          "cases/case-requirements.json");

  @Test
  void expectedBrowserRevisionRejectsMissingTypeAndIntegerOverflow() throws IOException {
    for (JsonNode invalid :
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().textNode("1187"),
            JSON.getNodeFactory().numberNode(new BigInteger("2147483648")),
            JSON.getNodeFactory().numberNode(0),
            JSON.getNodeFactory().numberNode(-1))) {
      List<JsonNode> input = fixture();
      ObjectNode expectedBrowser = (ObjectNode) object(input, CONTRACT).path(FIELD_BROWSER);
      expectedBrowser.set("browserRevision", invalid);
      assertContains(input, "BROWSER_REVISION");
    }
  }

  /** PT-CHR-DEF-019: matching definitions cannot replace the SS355 browser constants. */
  @Test
  void browserDefinitionsMustMatchTheIndependentDesignEvenWhenTheyAgree() throws IOException {
    assertEquals(List.of(), validate(fixture()));
    List<Executable> checks = new ArrayList<>();
    for (List<String> pair :
        List.of(
            List.of("playwrightJava", "1.54.0", "BROWSER_PLAYWRIGHT"),
            List.of(FIELD_BROWSER, "firefox", "BROWSER_NAME"),
            List.of("locale", "en-US", "BROWSER_LOCALE"),
            List.of("timezone", "UTC", "BROWSER_TIMEZONE"))) {
      String field = pair.get(0);
      List<JsonNode> input = fixture();
      ObjectNode contract = (ObjectNode) object(input, CONTRACT).path(FIELD_BROWSER);
      ObjectNode browser = object(input, BROWSER);
      contract.put(field, pair.get(1));
      browser.put(field, pair.get(1));
      List<String> expected = List.of(pair.get(2));
      checks.add(() -> assertEquals(expected, validate(input), field));
      List<JsonNode> missing = fixture();
      ((ObjectNode) object(missing, CONTRACT).path(FIELD_BROWSER)).remove(field);
      object(missing, BROWSER).remove(field);
      checks.add(() -> assertEquals(expected, validate(missing), field + " absent"));
    }

    List<JsonNode> input = fixture();
    ObjectNode contract = (ObjectNode) object(input, CONTRACT).path(FIELD_BROWSER);
    ObjectNode browser = object(input, BROWSER);
    contract.put("browserRevision", 1186);
    browser.put("browserRevision", 1186);
    contract.put("desktopWidth", 1280);
    ((ObjectNode) browser.path("desktop")).put("width", 1280);
    contract.put("mobileHeight", 800);
    ((ObjectNode) browser.path("mobile")).put("height", 800);
    contract.put("deviceScaleFactor", 2);
    ((ObjectNode) browser.path("desktop")).put("deviceScaleFactor", 2);
    ((ObjectNode) browser.path("mobile")).put("deviceScaleFactor", 2);
    checks.add(
        () ->
            assertEquals(
                List.of(
                    "BROWSER_REVISION",
                    "BROWSER_DESKTOP_VIEWPORT",
                    "BROWSER_MOBILE_VIEWPORT",
                    "BROWSER_DEVICE_SCALE"),
                validate(input)));
    assertAll(checks);
  }

  @Test
  void acceptsPinnedPublicDefinitionsWithoutMutationAndReturnsImmutableDiagnostics()
      throws IOException {
    List<JsonNode> input = fixture();
    List<JsonNode> unchanged = input.stream().<JsonNode>map(JsonNode::deepCopy).toList();
    assertEquals(24, input.get(CONTRACT).path(FIELD_CASE_ORDER).size());
    assertEquals(16, input.get(DIFFERENCES).path(FIELD_DIFFERENCES).size());
    assertEquals("Log", input.get(CATALOG).path(CASES).get(20).path("group").asText());
    List<String> result = validate(input);
    assertEquals(List.of(), result);
    assertThrows(UnsupportedOperationException.class, () -> result.add("change"));
    assertEquals(unchanged, input);
  }

  @Test
  void rejectsEveryJavaNullDocumentWithFixedSignal() throws IOException {
    for (int index = 0; index < RESOURCES.size(); index++) {
      List<JsonNode> input = fixture();
      input.set(index, null);
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> validate(input));
      assertEquals("definition document is required", failure.getMessage());
    }
  }

  @Test
  void malformedJsonShapesProduceFailuresRatherThanNpe() throws IOException {
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
  void allFourVersionCallersRejectCoercionOverflowMissingAndNull() throws IOException {
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
  void contractCountsOrderIdentifiersAndHashesUseIndependentConstraints() throws IOException {
    List<JsonNode> input = fixture();
    ObjectNode contract = object(input, CONTRACT);
    contract.putArray("gates").add("CHR-G01");
    ArrayNode cases = contract.withArray(FIELD_CASE_ORDER);
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

  /** PT-CHR-DEF084: a same-group replacement cannot redefine the approved contract. */
  @Test
  void contractRejectsAnUnapprovedIdAtTheSameSize() throws IOException {
    List<JsonNode> input = fixture();
    ArrayNode order = object(input, CONTRACT).withArray(FIELD_CASE_ORDER);
    assertEquals(24, order.size());
    assertEquals("CHR-A03", order.get(2).asText());
    order.set(2, JSON.getNodeFactory().textNode("CHR-A99"));
    assertContains(input, "CONTRACT_CASE_ORDER");
  }

  /** PT-CHR-DEF085: equivalent members in a different order are not the gate contract. */
  @Test
  void contractRejectsReorderedApprovedIds() throws IOException {
    List<JsonNode> input = fixture();
    ArrayNode order = object(input, CONTRACT).withArray(FIELD_CASE_ORDER);
    JsonNode first = order.get(0);
    order.set(0, order.get(1));
    order.set(1, first);
    assertContains(input, "CONTRACT_CASE_ORDER");
    assertEquals(List.of(), validate(fixture()));
  }

  /** PT-CHR-DEF087: size 16 does not permit an unapproved ID. */
  @Test
  void contractRejectsAnUnapprovedDifferenceIdAtTheSameSize() throws IOException {
    assertContractDifferenceRejected("DIF-099");
  }

  /** PT-CHR-DEF088: a repeated ID cannot replace another approved difference. */
  @Test
  void contractRejectsADuplicateDifferenceIdAtTheSameSize() throws IOException {
    assertContractDifferenceRejected("DIF-001");
  }

  private static void assertContractDifferenceRejected(String replacement) throws IOException {
    List<JsonNode> input = fixture();
    ArrayNode ids = object(input, CONTRACT).withArray("differenceIds");
    assertEquals(16, ids.size());
    assertEquals("DIF-016", ids.get(15).asText());
    ids.set(15, JSON.getNodeFactory().textNode(replacement));
    assertContains(input, "CONTRACT_DIFFERENCE_IDS");
  }

  @Test
  void schemaDraftShapeAndItemConstraintsCannotBeWeakened() throws IOException {
    List<JsonNode> input = fixture();
    ObjectNode schema = object(input, SCHEMA);
    schema.put("$schema", "invalid").put(FIELD_TYPE, "array");
    schema.putArray("required").add(CASES);
    ObjectNode cases = schema.withObject(SCHEMA_CASES);
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

  /** PT-CHR-DEF-SCHEMA001 / BUG-3805. */
  @Test
  void fixedSchemaVersionAndContainerTypesAreCheckedIndependently() throws IOException {
    assertEquals(List.of(), validate(fixture()));
    assertAll(
        () ->
            rejectSchemaValue(
                SCHEMA_VERSION,
                "const",
                JSON.getNodeFactory().textNode("1"),
                "SCHEMA_VERSION_CONST"),
        () ->
            rejectSchemaValue(
                SCHEMA_VERSION,
                "const",
                JSON.getNodeFactory().numberNode(2),
                "SCHEMA_VERSION_CONST"),
        () ->
            rejectSchemaValue(
                SCHEMA_VERSION, "const", MissingNode.getInstance(), "SCHEMA_VERSION_CONST"),
        () ->
            rejectSchemaValue(
                SCHEMA_CASES,
                FIELD_TYPE,
                JSON.getNodeFactory().textNode("object"),
                "SCHEMA_CASES_TYPE"),
        () ->
            rejectSchemaValue(
                SCHEMA_CASES, FIELD_TYPE, MissingNode.getInstance(), "SCHEMA_CASES_TYPE"),
        () ->
            rejectSchemaValue(
                "/properties/cases/items",
                FIELD_TYPE,
                JSON.getNodeFactory().textNode("array"),
                "SCHEMA_CASE_ITEM_TYPE"),
        () ->
            rejectSchemaValue(
                "/properties/cases/items",
                FIELD_TYPE,
                MissingNode.getInstance(),
                "SCHEMA_CASE_ITEM_TYPE"));
  }

  /** PT-CHR-DEF-SCHEMA002 / BUG-3809. */
  @Test
  void fixedSchemaCannotAcceptAdditionalConstraints() throws IOException {
    assertEquals(List.of(), validate(fixture()));
    List<JsonNode> root = fixture();
    object(root, SCHEMA).put("maxProperties", 1);
    assertAll(
        () -> assertEquals(List.of("SCHEMA_EXTRA_KEYWORD:root"), validate(root)),
        () ->
            rejectSchemaValue(
                "/properties",
                "unexpected",
                JSON.createObjectNode(),
                "SCHEMA_EXTRA_KEYWORD:properties"),
        () ->
            rejectSchemaValue(
                SCHEMA_VERSION,
                "minimum",
                JSON.getNodeFactory().numberNode(2),
                "SCHEMA_EXTRA_KEYWORD:version"),
        () ->
            rejectSchemaValue(
                SCHEMA_CASES,
                "enum",
                JSON.createArrayNode().add(JSON.createArrayNode()),
                "SCHEMA_EXTRA_KEYWORD:cases"),
        () ->
            rejectSchemaValue(
                "/properties/cases/items",
                "maxProperties",
                JSON.getNodeFactory().numberNode(3),
                "SCHEMA_EXTRA_KEYWORD:item"));
  }

  private static void rejectSchemaValue(
      String pointer, String key, JsonNode value, String diagnostic) throws IOException {
    List<JsonNode> input = fixture();
    ObjectNode container = object(input, SCHEMA).withObject(pointer);
    if (value.isMissingNode()) {
      container.remove(key);
    } else {
      container.set(key, value);
    }
    assertEquals(List.of(diagnostic), validate(input));
  }

  @Test
  void catalogRejectsDuplicateMalformedUnknownAndShortIdsAndWrongModes() throws IOException {
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
      throws IOException {
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
  void differencesRejectUnknownModesCasesBroadSelectorsDuplicatesAndEmptyValues()
      throws IOException {
    List<JsonNode> input = fixture();
    ArrayNode differences = object(input, DIFFERENCES).withArray(FIELD_DIFFERENCES);
    ObjectNode first = (ObjectNode) differences.get(0);
    first.put("mode", "all").put("selectorType", "unknown").put("current", "").put("nk", "");
    first.putArray(CASES);
    first.putArray(FIELD_SELECTORS);
    ObjectNode second = (ObjectNode) differences.get(1);
    second.put("field", first.path("field").asText());
    second.putArray(CASES).add(ACTION_CASE).add(ACTION_CASE).add(UNKNOWN_CASE);
    second.putArray(FIELD_SELECTORS).add("same").add("same");
    String[] invalid = {"", "all*", "a..b", "$.all"};
    for (int index = 0; index < invalid.length; index++) {
      ((ObjectNode) differences.get(index + 2)).putArray(FIELD_SELECTORS).add(invalid[index]);
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
    object(malformed, DIFFERENCES).put(FIELD_DIFFERENCES, "not-array");
    assertContains(malformed, "DIF_NOT_ARRAY", "DIF_ID_SEQUENCE");
  }

  @Test
  void requirementsRejectMissingCoreKeysDuplicatesUnknownAndUnboundSupplementals()
      throws IOException {
    List<JsonNode> input = fixture();
    ObjectNode requirements = object(input, REQUIREMENTS);
    requirements.withObject(REQUIREMENTS_POINTER).putArray(ACTION_CASE).add("caseId").add("caseId");
    requirements.withObject(REQUIREMENTS_POINTER).putArray(SECOND_AUTH_CASE).add("status");
    requirements.withObject(REQUIREMENTS_POINTER).remove("CHR-O01");
    ObjectNode supplemental = requirements.withObject(SUPPLEMENTAL_POINTER);
    supplemental.putArray(SECOND_AUTH_CASE);
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

  /** PT-CHR-DEF-MEDIA001: UI264 requires both ordinary and first-range observations. */
  @Test
  void requiredVideoRangeObservationsCannotDisappearFromDefinitions() throws IOException {
    var ordinaryOnly = fixture();
    object(ordinaryOnly, REQUIREMENTS)
        .withObject(SUPPLEMENTAL_POINTER)
        .putArray(VIDEO_RANGE_CASE)
        .add(VIDEO_NO_RANGE);
    var rangeOnly = fixture();
    object(rangeOnly, REQUIREMENTS)
        .withObject(SUPPLEMENTAL_POINTER)
        .putArray(VIDEO_RANGE_CASE)
        .add(VIDEO_FIRST_RANGE);
    var omitted = fixture();
    object(omitted, REQUIREMENTS).withObject(SUPPLEMENTAL_POINTER).remove(VIDEO_RANGE_CASE);
    var replaced = fixture();
    object(replaced, REQUIREMENTS)
        .withObject(SUPPLEMENTAL_POINTER)
        .putArray(VIDEO_RANGE_CASE)
        .add(VIDEO_NO_RANGE)
        .add("other-observation");
    var diagnostic = List.of("REQ_VIDEO_RANGE_SUPPLEMENTAL");
    assertAll(
        () -> assertEquals(diagnostic, validate(ordinaryOnly)),
        () -> assertEquals(diagnostic, validate(rangeOnly)),
        () -> assertEquals(diagnostic, validate(omitted)),
        () -> assertEquals(diagnostic, validate(replaced)),
        () -> assertEquals(List.of(), validate(fixture())));
  }

  /** PT-CHR-DEF-MEDIA002: Current must demonstrate both approved video observations. */
  @Test
  void requiredVideoRangeObservationsCannotBeDeclaredNkOnly() throws IOException {
    assertEquals(List.of(), validate(fixture()));
    for (List<String> checks :
        List.of(
            List.of(VIDEO_NO_RANGE),
            List.of(VIDEO_FIRST_RANGE),
            List.of(VIDEO_NO_RANGE, VIDEO_FIRST_RANGE))) {
      var input = fixture();
      var declaration =
          object(input, REQUIREMENTS)
              .withObject("/nkOnlySupplementalChecks")
              .putArray(VIDEO_RANGE_CASE);
      checks.forEach(declaration::add);
      assertEquals(
          List.of("REQ_VIDEO_RANGE_CURRENT_SUPPLEMENTAL"), validate(input), checks.toString());
    }
  }

  /** PT-CHR-DEF-015: structure of a declared NK-only supplemental case. */
  @Test
  void declaredNkOnlySupplementalChecksMustBeDistinctNonblankStrings() throws IOException {
    assertEquals(List.of(), validate(fixture()));
    for (String malformed :
        List.of(
            "[]",
            JSON_NULL,
            "{}",
            "\"web-log-outbox-retry\"",
            "[null]",
            "[7]",
            "[\"  \"]",
            "[\"web-log-outbox-retry\",\"web-log-outbox-retry\"]")) {
      var input = fixture();
      object(input, REQUIREMENTS)
          .withObject("/nkOnlySupplementalChecks")
          .set("CHR-L01", JSON.readTree(malformed));
      assertEquals(List.of("REQ_NK_ONLY_CHECKS:CHR-L01"), validate(input), malformed);
    }
  }

  /** PT-CHR-DEF-016: required artifact fields and supplemental check names are text arrays. */
  @Test
  void declaredRequiredFieldsAndSupplementalChecksMustBeNonblankTextArrays() throws IOException {
    assertEquals(List.of(), validate(fixture()));
    var requiredObject = fixture();
    object(requiredObject, REQUIREMENTS)
        .withObject(REQUIREMENTS_POINTER)
        .putObject(ACTION_CASE)
        .put("first", "caseId")
        .put("second", "status");
    var supplementalObject = fixture();
    object(supplementalObject, REQUIREMENTS)
        .withObject(SUPPLEMENTAL_POINTER)
        .putObject(SECOND_AUTH_CASE)
        .put("first", "ip-limit-observed-not-hardcoded");

    List<Executable> checks = new ArrayList<>();
    checks.add(() -> assertEquals(List.of("REQ_FIELDS:CHR-A01"), validate(requiredObject)));
    checks.add(
        () ->
            assertEquals(List.of("REQ_SUPPLEMENTAL_CHECKS:CHR-A02"), validate(supplementalObject)));
    for (JsonNode invalid :
        List.of(JSON.readTree("7"), JSON.readTree(JSON_NULL), JSON.readTree("\" \""))) {
      var invalidRequired = fixture();
      object(invalidRequired, REQUIREMENTS)
          .withObject(REQUIREMENTS_POINTER)
          .withArray(ACTION_CASE)
          .add(invalid);
      var invalidSupplemental = fixture();
      object(invalidSupplemental, REQUIREMENTS)
          .withObject(SUPPLEMENTAL_POINTER)
          .withArray(SECOND_AUTH_CASE)
          .add(invalid);
      checks.add(() -> assertEquals(List.of("REQ_FIELDS:CHR-A01"), validate(invalidRequired)));
      checks.add(
          () ->
              assertEquals(
                  List.of("REQ_SUPPLEMENTAL_CHECKS:CHR-A02"), validate(invalidSupplemental)));
    }
    assertAll(checks);
  }

  /** PT-CHR-DEF-017: fonts and difference selectors contain text names. */
  @Test
  void declaredFontAndSelectorNamesRejectNonTextEntries() throws IOException {
    List<Executable> checks = new ArrayList<>();
    List<String> fontFailure = List.of("BROWSER_FONTS");
    var emptyFonts = fixture();
    object(emptyFonts, BROWSER).putArray("fonts");
    checks.add(() -> assertEquals(fontFailure, validate(emptyFonts)));
    for (JsonNode invalid :
        List.of(JSON.readTree("7"), JSON.readTree(JSON_NULL), JSON.readTree("\" \""))) {
      var input = fixture();
      object(input, BROWSER).putArray("fonts").add(invalid);
      checks.add(() -> assertEquals(fontFailure, validate(input)));
    }
    for (JsonNode invalid :
        List.of(JSON.readTree("7"), JSON.readTree(JSON_NULL), JSON.readTree("false"))) {
      var input = fixture();
      var difference = (ObjectNode) object(input, DIFFERENCES).withArray(FIELD_DIFFERENCES).get(1);
      assertEquals("DIF-002", difference.path("id").textValue());
      difference.putArray(FIELD_SELECTORS).add(invalid);
      checks.add(() -> assertEquals(List.of("DIF_SELECTOR_EMPTY:DIF-002"), validate(input)));
    }
    assertAll(checks);
  }

  /** PT-CHR-DEF-018: the gate and comparison share the typed name-list reader. */
  @Test
  void sharedDefinitionNameReaderUsesOnlyTextArrays() throws IOException {
    var names = JSON.readTree("[\"first\",\"second\"]");
    var original = names.deepCopy();
    List<String> read = GateContractValidator.strings(names);
    assertEquals(List.of("first", "second"), read);
    assertEquals(original, names);
    assertThrows(UnsupportedOperationException.class, () -> read.add("third"));
    assertEquals(List.of(), GateContractValidator.strings(null));
    for (String malformed :
        List.of(JSON_NULL, "[]", "\"first\"", "{\"a\":\"first\"}", "[\"first\",7]", "[false]")) {
      assertEquals(List.of(), GateContractValidator.strings(JSON.readTree(malformed)), malformed);
    }
  }

  @Test
  void concurrentValidAndInvalidDefinitionsRemainIndependent()
      throws IOException, InterruptedException, ExecutionException, TimeoutException {
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
