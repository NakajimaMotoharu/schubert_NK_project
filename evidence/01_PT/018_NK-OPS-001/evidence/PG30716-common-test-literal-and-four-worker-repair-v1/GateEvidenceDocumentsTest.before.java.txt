package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-CHR-META001..009. JSON consistency only; these fixtures are never operational evidence. */
final class GateEvidenceDocumentsTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final int COMPARISON = 0;
  private static final int SOURCE = 1;
  private static final int FIRST = 2;
  private static final int SECOND = 3;
  private static final int EXPECTED = 4;
  private static final int PREFLIGHT = 5;
  private static final int REVIEW = 6;
  private static final long CAPACITY = 21_474_836_480L;
  private static final String COMMIT = "843de94";
  private static final String STATUS = "status";
  private static final String FREE_BYTES = "freeBytes";
  private static final String PREFLIGHT_DISK = "PREFLIGHT_DISK";
  private static final String SOURCE_VALUE = "SOURCE_VALUE:";
  private static final String SOURCE_HASH = "sourceAggregateSha256";
  private static final String DOCUMENT_HASH = "documentAggregateSha256";
  private static final List<String> SOURCE_COUNTS =
      List.of("sourceFileCount", "documentFileCount", "masterFileCount", "masterBytes");
  private static final List<String> INVENTORY_COUNTS =
      List.of(
          "scenarioFileCount",
          "scenarioEntryCount",
          "audioMetadataCount",
          "audioLinkCount",
          "videoCount",
          "musicCount");
  private static final List<String> CHECKS =
      List.of(
          "currentSourceUnchanged",
          "currentMasterUnchanged",
          "repeatDiffZero",
          "secretScanZero",
          "qaThrough044Resolved",
          "uicThrough004Completed");

  @Test
  void acceptsIndependentLiteralMetadataAndKeepsInputsAndResultsImmutable() throws Exception {
    List<JsonNode> data = fixture();
    List<JsonNode> unchanged = data.stream().<JsonNode>map(JsonNode::deepCopy).toList();
    List<String> result = validate(data);
    assertEquals(List.of(), result);
    assertThrows(UnsupportedOperationException.class, () -> result.add("change"));
    assertEquals(unchanged, data);
  }

  @Test
  void rejectsEveryJavaNullBoundaryAndReportsJsonNullWithoutNpe() throws Exception {
    for (int index = 0; index < 7; index++) {
      List<JsonNode> data = fixture();
      data.set(index, null);
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> validate(data));
      assertEquals("evidence document is required", failure.getMessage());
      data.set(index, JSON.nullNode());
      assertFalse(validate(data).isEmpty());
    }
    IllegalArgumentException failure =
        assertThrows(IllegalArgumentException.class, () -> validate(fixture(), null));
    assertEquals("baseline reference is required", failure.getMessage());
  }

  @Test
  void comparisonCountsAndEmptyDifferenceCollectionsMustBeStrict() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (String field : List.of("firstFileCount", "secondFileCount")) {
      String code = field.startsWith("first") ? "COMPARE_FIRST_COUNT" : "COMPARE_SECOND_COUNT";
      for (JsonNode value :
          List.of(
              JSON.getNodeFactory().textNode("28"),
              JSON.getNodeFactory().numberNode(28.5),
              JSON.getNodeFactory().numberNode(new BigInteger("4294967324")),
              JSON.getNodeFactory().numberNode(27),
              JSON.nullNode())) {
        List<JsonNode> data = fixture();
        object(data, COMPARISON).set(field, value);
        reject(checks, data, code);
      }
    }
    for (String field : List.of("missing", "extra", "changed")) {
      for (JsonNode value :
          List.of(JSON.createObjectNode(), JSON.createArrayNode().add("unit-extra"))) {
        List<JsonNode> data = fixture();
        object(data, COMPARISON).set(field, value);
        reject(checks, data, "COMPARE_" + field.toUpperCase(java.util.Locale.ROOT));
      }
    }
    assertAll(checks);
  }

  @Test
  void sourceAndInventoryCountsRejectCoercionDefaultsOverflowAndNegativeValues() throws Exception {
    List<Executable> checks = new ArrayList<>();
    List<String> fields = new ArrayList<>(SOURCE_COUNTS);
    fields.addAll(INVENTORY_COUNTS);
    for (String field : fields) {
      String code =
          SOURCE_COUNTS.contains(field) ? SOURCE_VALUE + field : "run1_INVENTORY_VALUE:" + field;
      for (JsonNode value :
          List.of(
              JSON.nullNode(),
              JSON.getNodeFactory().textNode("0"),
              JSON.getNodeFactory().numberNode(0.5),
              JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")),
              JSON.getNodeFactory().numberNode(-1),
              JSON.getNodeFactory().booleanNode(true),
              JSON.createArrayNode(),
              JSON.createObjectNode())) {
        List<JsonNode> data = fixture();
        object(data, EXPECTED).set(field, value.deepCopy());
        observedCount(data, field, value);
        reject(checks, data, code);
      }
      List<JsonNode> observedText = fixture();
      observedCount(
          observedText,
          field,
          JSON.getNodeFactory().textNode(observedText.get(EXPECTED).path(field).asText()));
      reject(checks, observedText, code);
      List<JsonNode> observedOverflow = fixture();
      observedCount(
          observedOverflow,
          field,
          JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")));
      reject(checks, observedOverflow, code);
      List<JsonNode> different = fixture();
      observedCount(
          different,
          field,
          JSON.getNodeFactory().numberNode(different.get(EXPECTED).path(field).longValue() + 1));
      reject(checks, different, code);
      for (long boundary : List.of(0L, Long.MAX_VALUE)) {
        List<JsonNode> valid = fixture();
        object(valid, EXPECTED).put(field, boundary);
        observedCount(valid, field, JSON.getNodeFactory().numberNode(BigInteger.valueOf(boundary)));
        assertEquals(List.of(), validate(valid));
      }
    }
    assertAll(checks);
  }

  @Test
  void sourceHashesRequireCanonicalTextOnBothSides() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (String field : List.of(SOURCE_HASH, DOCUMENT_HASH)) {
      for (JsonNode value :
          List.of(
              JSON.nullNode(),
              JSON.getNodeFactory().numberNode(0),
              JSON.getNodeFactory().textNode("short"),
              JSON.getNodeFactory().textNode("A".repeat(64)))) {
        List<JsonNode> data = fixture();
        object(data, EXPECTED).set(field, value.deepCopy());
        object(data, SOURCE).set(field, value.deepCopy());
        reject(checks, data, SOURCE_VALUE + field);
      }
      for (JsonNode value :
          List.of(
              JSON.getNodeFactory().numberNode(0),
              JSON.getNodeFactory().textNode("0".repeat(64)))) {
        List<JsonNode> data = fixture();
        object(data, SOURCE).set(field, value);
        reject(checks, data, SOURCE_VALUE + field);
      }
    }
    assertAll(checks);
  }

  @Test
  void preflightMetadataUsesTypedCapacityAndExactStaticMarkers() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (JsonNode value :
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().textNode(Long.toString(CAPACITY)),
            JSON.getNodeFactory().numberNode(CAPACITY + 0.5),
            JSON.getNodeFactory()
                .numberNode(
                    new BigInteger("18446744073709551616").add(BigInteger.valueOf(CAPACITY))),
            JSON.getNodeFactory().numberNode(CAPACITY - 1))) {
      List<JsonNode> data = fixture();
      object(data, PREFLIGHT).set(FREE_BYTES, value);
      reject(checks, data, PREFLIGHT_DISK);
    }
    List<JsonNode> permission = fixture();
    object(permission, PREFLIGHT).put("credentialPermission", "0644");
    reject(checks, permission, "PREFLIGHT_CREDENTIAL");
    List<JsonNode> hosts = fixture();
    object(hosts, PREFLIGHT).putArray("hostAllowlist").add("127.0.0.1").add("localhost");
    reject(checks, hosts, "PREFLIGHT_HOSTS");
    for (JsonNode value :
        List.of(JSON.createObjectNode(), JSON.createArrayNode().add("unit-failure"))) {
      List<JsonNode> data = fixture();
      object(data, PREFLIGHT).set("failures", value);
      reject(checks, data, "PREFLIGHT_FAILURES");
    }
    for (long boundary : List.of(CAPACITY, Long.MAX_VALUE)) {
      List<JsonNode> data = fixture();
      object(data, PREFLIGHT).put(FREE_BYTES, BigInteger.valueOf(boundary));
      assertEquals(List.of(), validate(data));
    }
    assertAll(checks);
  }

  @Test
  void reviewMetadataRequiresBooleanChecksAndTypedRoleWithoutGrantingApproval() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (String field : CHECKS) {
      for (JsonNode value :
          List.of(
              JSON.getNodeFactory().textNode("true"),
              JSON.getNodeFactory().numberNode(1),
              JSON.getNodeFactory().booleanNode(false),
              JSON.nullNode())) {
        List<JsonNode> data = fixture();
        object(data, REVIEW).withObject("/checks").set(field, value);
        reject(checks, data, "REVIEW_CHECK:" + field);
      }
    }
    for (JsonNode value :
        List.of(
            JSON.getNodeFactory().numberNode(123),
            JSON.getNodeFactory().textNode(" "),
            JSON.nullNode())) {
      List<JsonNode> data = fixture();
      object(data, REVIEW).set("reviewerRole", value);
      reject(checks, data, "REVIEW_ROLE");
    }
    List<JsonNode> commit = fixture();
    object(commit, REVIEW).put("baselineCommit", "other-unit-reference");
    reject(checks, commit, "REVIEW_COMMIT");
    for (JsonNode value :
        List.of(JSON.createObjectNode(), JSON.createArrayNode().add("a").add("b"))) {
      List<JsonNode> data = fixture();
      object(data, REVIEW).set("evidence", value);
      reject(checks, data, "REVIEW_EVIDENCE");
    }
    assertAll(checks);
  }

  @Test
  void statusMarkersAndRepeatInventoryCannotSubstituteDifferentEvidence() throws Exception {
    for (String status : List.of("FAIL", "FAILED", "FLAKY", "SKIP", "SKIPPED", "NOT_RUN")) {
      int[] indices = {COMPARISON, SOURCE, FIRST, SECOND, PREFLIGHT, REVIEW};
      String[] codes = {
        "COMPARE_STATUS",
        "SOURCE_STATUS",
        "run1_INVENTORY_STATUS",
        "run2_INVENTORY_STATUS",
        "PREFLIGHT_STATUS",
        "REVIEW_STATUS"
      };
      for (int index = 0; index < indices.length; index++) {
        List<JsonNode> data = fixture();
        object(data, indices[index]).put(STATUS, status);
        assertTrue(validate(data).contains(codes[index]));
      }
    }
    List<JsonNode> different = fixture();
    object(different, SECOND).put("unitAdditionalObservation", 1);
    assertEquals(List.of("INVENTORY_REPEAT_DIFF"), validate(different));
    List<JsonNode> symlinkMarker = fixture();
    object(symlinkMarker, SOURCE).putArray("masterSymlinks").add("unit-logical-link");
    assertTrue(validate(symlinkMarker).contains("SOURCE_SYMLINKS"));
  }

  @Test
  void concurrentFrozenFramesKeepTheirDiagnosticsIndependent() throws Exception {
    List<JsonNode> valid = fixture();
    List<JsonNode> invalid = fixture();
    object(invalid, COMPARISON).put(STATUS, "unit-invalid");
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> validate(valid));
      var second = workers.submit(() -> validate(invalid));
      assertEquals(List.of(), first.get());
      assertTrue(second.get().contains("COMPARE_STATUS"));
    }
    assertEquals(List.of(), validate(valid));
  }

  private static List<JsonNode> fixture() throws IOException {
    JsonNode source =
        JSON.readTree(
            """
            {"status":"PASS","sourceFileCount":59,
             "sourceAggregateSha256":"c9ce7c85de2d0443b4d7bb4d9a3082b39985c1cbf3121945de1ee4a936b0bd6c",
             "documentFileCount":18,
             "documentAggregateSha256":"1904756ba0e0cbf73f3942ad8481d17d727e3e8f3770dacf8bc64ee06c2acaff",
             "masterFileCount":59627,"masterBytes":19240707190,"masterSymlinks":[]}
            """);
    JsonNode inventory =
        JSON.readTree(
            """
            {"status":"PASS","scenarioFileCount":262,"scenarioEntryCount":99661,
             "audioMetadataCount":37256,"audioLinkCount":35201,"videoCount":20,"musicCount":129}
            """);
    JsonNode comparison =
        JSON.readTree(
            """
            {"status":"PASS","firstFileCount":28,"secondFileCount":28,
             "missing":[],"extra":[],"changed":[]}
            """);
    JsonNode preflight =
        JSON.readTree(
            """
            {"status":"PASS","failures":[],"credentialPermission":"0600",
             "hostAllowlist":["localhost","127.0.0.1"],"freeBytes":21474836480}
            """);
    JsonNode review =
        JSON.readTree(
            """
            {"status":"APPROVED","baselineCommit":"843de94","reviewerRole":"UNIT_FIXTURE_ONLY",
             "evidence":["unit:a","unit:b","unit:c"],"checks":{
             "currentSourceUnchanged":true,"currentMasterUnchanged":true,"repeatDiffZero":true,
             "secretScanZero":true,"qaThrough044Resolved":true,"uicThrough004Completed":true}}
            """);
    JsonNode expected = GateDefinitionDocumentsTest.fixture().get(0).path("source").deepCopy();
    return new ArrayList<>(
        List.of(comparison, source, inventory, inventory.deepCopy(), expected, preflight, review));
  }

  private static ObjectNode object(List<JsonNode> input, int index) {
    return (ObjectNode) input.get(index);
  }

  private static List<String> validate(List<JsonNode> input) {
    return validate(input, COMMIT);
  }

  private static List<String> validate(List<JsonNode> input, String commit) {
    return GateContractValidator.validateEvidenceDocuments(
        input.get(COMPARISON),
        input.get(SOURCE),
        input.get(FIRST),
        input.get(SECOND),
        input.get(EXPECTED),
        input.get(PREFLIGHT),
        input.get(REVIEW),
        commit);
  }

  private static void reject(List<Executable> checks, List<JsonNode> input, String code) {
    checks.add(
        () -> assertTrue(validate(input).contains(code), () -> "missing fixed code: " + code));
  }

  private static void observedCount(List<JsonNode> input, String field, JsonNode value) {
    if (SOURCE_COUNTS.contains(field)) {
      object(input, SOURCE).set(field, value.deepCopy());
    } else {
      object(input, FIRST).set(field, value.deepCopy());
      object(input, SECOND).set(field, value.deepCopy());
    }
  }
}
