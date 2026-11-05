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

/** PT-CHR-BMETA001..008. Manifest items in memory only, no actual baseline qualification. */
final class GateBaselineMetadataTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String SOURCE_HASH = "sourceAggregateSha256";
  private static final String DOCUMENT_HASH = "documentAggregateSha256";
  private static final List<String> MASTER_FIELDS = List.of("masterFileCount", "masterBytes");
  private static final String CASE_COUNT = "caseCount";
  private static final String CASE_FAILURE = "BASELINE_CASE_COUNT";

  @Test
  void acceptsIndependentManifestItemsWithoutMutatingInputsAndReturnsImmutableList()
      throws Exception {
    List<JsonNode> data = fixture();
    List<JsonNode> unchanged = data.stream().<JsonNode>map(JsonNode::deepCopy).toList();
    List<String> result = validate(data);
    assertEquals(List.of(), result);
    assertThrows(UnsupportedOperationException.class, () -> result.add("change"));
    assertEquals(unchanged, data);
  }

  @Test
  void javaNullBoundariesFailWithFixedSignalAndJsonNullNeverCausesNpe() throws Exception {
    for (int index = 0; index < 2; index++) {
      List<JsonNode> data = fixture();
      data.set(index, null);
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> validate(data));
      assertEquals("baseline metadata document is required", failure.getMessage());
      data.set(index, JSON.nullNode());
      assertFalse(validate(data).isEmpty());
    }
  }

  @Test
  void manifestCardinalitiesMustBeTypedExactIntegers() throws Exception {
    String[] fields = {CASE_COUNT, "screenshotFileCount", "differenceCount"};
    int[] values = {24, 2, 16};
    String[] codes = {CASE_FAILURE, "BASELINE_SCREENSHOT_COUNT", "BASELINE_DIF_COUNT"};
    List<Executable> checks = new ArrayList<>();
    for (int index = 0; index < fields.length; index++) {
      for (JsonNode invalid :
          List.of(
              JSON.getNodeFactory().textNode(Integer.toString(values[index])),
              JSON.getNodeFactory().numberNode(values[index] + 0.5),
              JSON.getNodeFactory()
                  .numberNode(new BigInteger("4294967296").add(BigInteger.valueOf(values[index]))),
              JSON.nullNode(),
              JSON.getNodeFactory().numberNode(values[index] + 1))) {
        List<JsonNode> data = fixture();
        object(data, 0).set(fields[index], invalid);
        reject(checks, data, codes[index]);
      }
    }
    assertAll(checks);
  }

  @Test
  void sourceAndDocumentHashesMustBeCanonicalMatchingText() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (String field : List.of(SOURCE_HASH, DOCUMENT_HASH)) {
      String code = SOURCE_HASH.equals(field) ? "BASELINE_SOURCE_HASH" : "BASELINE_DOCUMENT_HASH";
      for (JsonNode invalid :
          List.of(
              JSON.nullNode(),
              JSON.getNodeFactory().numberNode(0),
              JSON.getNodeFactory().textNode("A".repeat(64)),
              JSON.getNodeFactory().textNode("short"))) {
        List<JsonNode> data = fixture();
        object(data, 0).set(field, invalid.deepCopy());
        object(data, 1).set(field, invalid.deepCopy());
        reject(checks, data, code);
      }
      List<JsonNode> different = fixture();
      object(different, 0).put(field, "0".repeat(64));
      reject(checks, different, code);
    }
    assertAll(checks);
  }

  @Test
  void masterCountsAndBytesRejectCoercionDefaultsAndOverflowOnBothSides() throws Exception {
    List<Executable> checks = new ArrayList<>();
    String[] codes = {"BASELINE_MASTER_COUNT", "BASELINE_MASTER_BYTES"};
    for (int index = 0; index < MASTER_FIELDS.size(); index++) {
      String field = MASTER_FIELDS.get(index);
      for (JsonNode invalid :
          List.of(
              JSON.nullNode(),
              JSON.getNodeFactory().textNode("0"),
              JSON.getNodeFactory().numberNode(0.5),
              JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")),
              JSON.getNodeFactory().numberNode(-1))) {
        List<JsonNode> data = fixture();
        object(data, 0).set(field, invalid.deepCopy());
        object(data, 1).set(field, invalid.deepCopy());
        reject(checks, data, codes[index]);
      }
      List<JsonNode> text = fixture();
      object(text, 0).put(field, text.get(1).path(field).asText());
      reject(checks, text, codes[index]);
      List<JsonNode> overflow = fixture();
      object(overflow, 0)
          .put(
              field,
              new BigInteger("18446744073709551616")
                  .add(BigInteger.valueOf(overflow.get(1).path(field).longValue())));
      reject(checks, overflow, codes[index]);
      for (long boundary : List.of(0L, Long.MAX_VALUE)) {
        List<JsonNode> valid = fixture();
        object(valid, 0).put(field, BigInteger.valueOf(boundary));
        object(valid, 1).put(field, boundary);
        assertEquals(List.of(), validate(valid));
      }
    }
    assertAll(checks);
  }

  @Test
  void environmentAndTargetUseExactMarkersAndIntegerBrowserRevision() throws Exception {
    List<Executable> checks = new ArrayList<>();
    String[] fields = {"javaVersion", "locale", "timezone"};
    String[] codes = {"BASELINE_JAVA", "BASELINE_LOCALE", "BASELINE_TIMEZONE"};
    for (int index = 0; index < fields.length; index++) {
      for (JsonNode invalid : List.of(JSON.nullNode(), JSON.getNodeFactory().textNode("wrong"))) {
        List<JsonNode> data = fixture();
        object(data, 0).withObject("/environment").set(fields[index], invalid);
        reject(checks, data, codes[index]);
      }
    }
    for (JsonNode invalid :
        List.of(
            JSON.getNodeFactory().textNode("1187"),
            JSON.getNodeFactory().numberNode(1187.5),
            JSON.getNodeFactory().numberNode(new BigInteger("4294968483")),
            JSON.nullNode(),
            JSON.getNodeFactory().numberNode(1188))) {
      List<JsonNode> data = fixture();
      object(data, 0).withObject("/environment").set("browserRevision", invalid);
      reject(checks, data, "BASELINE_BROWSER");
    }
    List<JsonNode> target = fixture();
    object(target, 0).put("target", "nk");
    reject(checks, target, "BASELINE_TARGET");
    assertAll(checks);
  }

  @Test
  void concurrentManifestFramesNeverShareMutationsOrFailures() throws Exception {
    List<JsonNode> valid = fixture();
    List<JsonNode> invalid = fixture();
    object(invalid, 0).put(CASE_COUNT, 23);
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> validate(valid));
      var second = workers.submit(() -> validate(invalid));
      assertEquals(List.of(), first.get());
      assertTrue(second.get().contains(CASE_FAILURE));
    }
    assertEquals(List.of(), validate(valid));
  }

  @Test
  void contractCountsRejectCoercionAndKeepPinnedTwentyThreeAndTwentySeven() throws Exception {
    String[] fields = {"currentApplicableCount", "baselineFileCount"};
    int[] values = {23, 27};
    String[] codes = {"CONTRACT_CURRENT_COUNT", "CONTRACT_BASELINE_FILE_COUNT"};
    List<Executable> checks = new ArrayList<>();
    for (int index = 0; index < fields.length; index++) {
      for (JsonNode invalid :
          List.of(
              JSON.getNodeFactory().textNode(Integer.toString(values[index])),
              JSON.getNodeFactory().numberNode(values[index] + 0.5),
              JSON.getNodeFactory()
                  .numberNode(new BigInteger("4294967296").add(BigInteger.valueOf(values[index]))),
              JSON.nullNode(),
              JSON.getNodeFactory().numberNode(values[index] + 1))) {
        List<JsonNode> documents = GateDefinitionDocumentsTest.fixture();
        object(documents, 0).set(fields[index], invalid);
        String code = codes[index];
        checks.add(() -> assertTrue(definitions(documents).contains(code)));
      }
      List<JsonNode> missing = GateDefinitionDocumentsTest.fixture();
      object(missing, 0).remove(fields[index]);
      String code = codes[index];
      checks.add(() -> assertTrue(definitions(missing).contains(code)));
      List<JsonNode> valid = GateDefinitionDocumentsTest.fixture();
      object(valid, 0).put(fields[index], BigInteger.valueOf(values[index]));
      assertEquals(List.of(), definitions(valid));
    }
    assertAll(checks);
  }

  private static List<JsonNode> fixture() throws IOException {
    JsonNode source =
        JSON.readTree(
            """
            {"sourceAggregateSha256":"c9ce7c85de2d0443b4d7bb4d9a3082b39985c1cbf3121945de1ee4a936b0bd6c",
             "documentAggregateSha256":"1904756ba0e0cbf73f3942ad8481d17d727e3e8f3770dacf8bc64ee06c2acaff",
             "masterFileCount":59627,"masterBytes":19240707190}
            """);
    JsonNode manifest =
        JSON.readTree(
            """
            {"target":"current","caseCount":24,"screenshotFileCount":2,"differenceCount":16,
             "sourceAggregateSha256":"c9ce7c85de2d0443b4d7bb4d9a3082b39985c1cbf3121945de1ee4a936b0bd6c",
             "documentAggregateSha256":"1904756ba0e0cbf73f3942ad8481d17d727e3e8f3770dacf8bc64ee06c2acaff",
             "masterFileCount":59627,"masterBytes":19240707190,
             "environment":{"javaVersion":"25.0.4","browserRevision":1187,"locale":"ja-JP","timezone":"Asia/Tokyo"}}
            """);
    return new ArrayList<>(List.of(manifest, source));
  }

  private static ObjectNode object(List<JsonNode> input, int index) {
    return (ObjectNode) input.get(index);
  }

  private static List<String> validate(List<JsonNode> input) {
    return GateContractValidator.validateBaselineMetadata(input.get(0), input.get(1));
  }

  private static List<String> definitions(List<JsonNode> input) {
    return GateContractValidator.validateDefinitions(
        input.get(0), input.get(1), input.get(2), input.get(3), input.get(4), input.get(5));
  }

  private static void reject(List<Executable> checks, List<JsonNode> input, String code) {
    checks.add(
        () -> assertTrue(validate(input).contains(code), () -> "missing fixed code: " + code));
  }
}
