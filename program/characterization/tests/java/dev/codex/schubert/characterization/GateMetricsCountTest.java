package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-CHR-METRIC001..006. Provided counts/JSON only, no filesystem enumeration or actual gate. */
final class GateMetricsCountTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String CURRENT_COUNT = "currentApplicableCount";
  private static final String BASELINE_COUNT = "baselineFileCount";
  private static final String CASE_COUNT = "caseCount";
  private static final String DIFFERENCE_COUNT = "differenceCount";

  @Test
  void validSnapshotUsesExactProvidedCountsAndIsImmutable() throws Exception {
    List<JsonNode> input = fixture();
    List<JsonNode> unchanged = input.stream().<JsonNode>map(JsonNode::deepCopy).toList();
    Map<String, Object> metrics = metrics(input);
    assertEquals(
        Map.of(
            CASE_COUNT,
            24,
            CURRENT_COUNT,
            23,
            DIFFERENCE_COUNT,
            16,
            BASELINE_COUNT,
            27,
            "failureCount",
            0),
        metrics);
    assertThrows(UnsupportedOperationException.class, () -> metrics.put("change", 0));
    assertEquals(unchanged, input);
    Map<String, Object> bounds =
        GateContractValidator.gateMetrics(
            input.get(0), input.get(1), 0, Integer.MAX_VALUE, Integer.MAX_VALUE);
    assertEquals(0, bounds.get(CASE_COUNT));
    assertEquals(Integer.MAX_VALUE, bounds.get(BASELINE_COUNT));
    assertEquals(Integer.MAX_VALUE, bounds.get("failureCount"));
  }

  @Test
  void javaNullAndNegativeProvidedCountsFailWithoutNpe() throws Exception {
    List<JsonNode> input = fixture();
    for (int index = 0; index < 2; index++) {
      List<JsonNode> bad = new ArrayList<>(input);
      bad.set(index, null);
      assertThrows(IllegalArgumentException.class, () -> metrics(bad));
    }
    for (int[] counts : List.of(new int[] {-1, 0, 0}, new int[] {0, -1, 0}, new int[] {0, 0, -1})) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              GateContractValidator.gateMetrics(
                  input.get(0), input.get(1), counts[0], counts[1], counts[2]));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> GateContractValidator.matchesBaselineFileCount(null, 27));
    assertThrows(
        IllegalArgumentException.class,
        () -> GateContractValidator.matchesBaselineFileCount(input.get(0), -1));
  }

  @Test
  void invalidOrMissingCurrentCountIsUnknownAndNeverAZeroOrCoercedValue() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (JsonNode invalid :
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().textNode("23"),
            JSON.getNodeFactory().numberNode(23.5),
            JSON.getNodeFactory().numberNode(new BigInteger("4294967319")),
            JSON.getNodeFactory().numberNode(24))) {
      List<JsonNode> input = fixture();
      object(input, 0).set(CURRENT_COUNT, invalid);
      checks.add(() -> assertFalse(metrics(input).containsKey(CURRENT_COUNT)));
    }
    List<JsonNode> missing = fixture();
    object(missing, 0).remove(CURRENT_COUNT);
    checks.add(() -> assertFalse(metrics(missing).containsKey(CURRENT_COUNT)));
    assertAll(checks);
  }

  @Test
  void unavailableDeclarationArraysAreOmittedInsteadOfReportedAsZero() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (JsonNode invalid :
        List.of(JSON.nullNode(), JSON.createObjectNode(), JSON.getNodeFactory().textNode("bad"))) {
      List<JsonNode> contract = fixture();
      object(contract, 0).set("caseOrder", invalid.deepCopy());
      checks.add(() -> assertFalse(metrics(contract).containsKey(CASE_COUNT)));
      List<JsonNode> differences = fixture();
      object(differences, 1).set("differences", invalid.deepCopy());
      checks.add(() -> assertFalse(metrics(differences).containsKey(DIFFERENCE_COUNT)));
    }
    List<JsonNode> nullDocuments = new ArrayList<>(List.of(JSON.nullNode(), JSON.nullNode()));
    checks.add(
        () -> assertEquals(Map.of(BASELINE_COUNT, 27, "failureCount", 0), metrics(nullDocuments)));
    assertAll(checks);
  }

  @Test
  void baselineCountComparisonRejectsCoercionAndRespectsExactIntegerBoundary() {
    for (int valid : List.of(0, 27, Integer.MAX_VALUE)) {
      ObjectNode contract = JSON.createObjectNode().put(BASELINE_COUNT, BigInteger.valueOf(valid));
      assertTrue(GateContractValidator.matchesBaselineFileCount(contract, valid));
    }
    List<Executable> checks = new ArrayList<>();
    for (JsonNode invalid :
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().textNode("27"),
            JSON.getNodeFactory().numberNode(27.5),
            JSON.getNodeFactory().numberNode(new BigInteger("4294967323")),
            JSON.getNodeFactory().numberNode(26),
            JSON.createArrayNode())) {
      ObjectNode contract = JSON.createObjectNode().set(BASELINE_COUNT, invalid);
      checks.add(() -> assertFalse(GateContractValidator.matchesBaselineFileCount(contract, 27)));
    }
    checks.add(
        () ->
            assertFalse(
                GateContractValidator.matchesBaselineFileCount(JSON.createObjectNode(), 0)));
    checks.add(
        () -> assertFalse(GateContractValidator.matchesBaselineFileCount(JSON.nullNode(), 0)));
    assertAll(checks);
  }

  @Test
  void concurrentIndependentSnapshotsNeverShareUnknownValues() throws Exception {
    List<JsonNode> valid = fixture();
    List<JsonNode> invalid = fixture();
    object(invalid, 0).put(CURRENT_COUNT, "23");
    try (var workers = Executors.newFixedThreadPool(2)) {
      var good = workers.submit(() -> metrics(valid));
      var bad = workers.submit(() -> metrics(invalid));
      assertEquals(23, good.get().get(CURRENT_COUNT));
      assertFalse(bad.get().containsKey(CURRENT_COUNT));
    }
    assertEquals(23, metrics(valid).get(CURRENT_COUNT));
  }

  private static List<JsonNode> fixture() throws Exception {
    List<JsonNode> definitions = GateDefinitionDocumentsTest.fixture();
    return new ArrayList<>(List.of(definitions.get(0), definitions.get(3)));
  }

  private static ObjectNode object(List<JsonNode> input, int index) {
    return (ObjectNode) input.get(index);
  }

  private static Map<String, Object> metrics(List<JsonNode> input) {
    return GateContractValidator.gateMetrics(input.get(0), input.get(1), 24, 27, 0);
  }
}
