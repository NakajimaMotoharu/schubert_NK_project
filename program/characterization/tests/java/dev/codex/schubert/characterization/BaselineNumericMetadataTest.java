package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-CHR-NUM001..005. Pure values only; never invokes promoteCurrent or creates a baseline. */
final class BaselineNumericMetadataTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String MASTER_COUNT = "masterFileCount";
  private static final String MASTER_BYTES = "masterBytes";
  private static final String BROWSER_REVISION = "browserRevision";
  private static final List<String> FIELDS = List.of(MASTER_COUNT, MASTER_BYTES, BROWSER_REVISION);

  @Test
  void fixedAndBoundaryValuesStayExactAndInputsRemainFrozen() {
    List<JsonNode> input = fixture();
    List<JsonNode> unchanged = input.stream().<JsonNode>map(JsonNode::deepCopy).toList();
    GateCli.BaselineNumbers value = numbers(input);
    assertEquals(59627L, value.masterFileCount());
    assertEquals(19240707190L, value.masterBytes());
    assertEquals(1187, value.browserRevision());
    assertEquals(unchanged, input);
    for (long count : List.of(0L, Long.MAX_VALUE)) {
      for (long bytes : List.of(0L, Long.MAX_VALUE)) {
        for (int revision : List.of(1, Integer.MAX_VALUE)) {
          List<JsonNode> data = fixture();
          object(data, 0)
              .put(MASTER_COUNT, BigInteger.valueOf(count))
              .put(MASTER_BYTES, BigInteger.valueOf(bytes));
          object(data, 1).put(BROWSER_REVISION, BigInteger.valueOf(revision));
          GateCli.BaselineNumbers boundary = numbers(data);
          assertEquals(count, boundary.masterFileCount());
          assertEquals(bytes, boundary.masterBytes());
          assertEquals(revision, boundary.browserRevision());
        }
      }
    }
  }

  @Test
  void missingAndNullDocumentsOrFieldsNeverBecomeZeroDefaults() {
    List<Executable> checks = new ArrayList<>();
    for (int index = 0; index < 2; index++) {
      List<JsonNode> javaNull = fixture();
      javaNull.set(index, null);
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> numbers(javaNull));
      assertEquals("baseline numeric documents are required", failure.getMessage());
      for (JsonNode invalid :
          List.of(JSON.nullNode(), JSON.createArrayNode(), JSON.createObjectNode())) {
        List<JsonNode> data = fixture();
        data.set(index, invalid);
        checks.add(() -> assertThrows(IllegalArgumentException.class, () -> numbers(data)));
      }
    }
    for (String field : FIELDS) {
      List<JsonNode> missing = fixture();
      object(missing, FIELDS.indexOf(field) / 2).remove(field);
      checks.add(() -> assertThrows(IllegalArgumentException.class, () -> numbers(missing)));
    }
    assertAll(checks);
  }

  @Test
  void invalidScalarKindsFractionsOverflowAndNegativeNumbersAreRejected() {
    List<Executable> checks = new ArrayList<>();
    long[] expected = {59627L, 19240707190L, 1187L};
    for (int index = 0; index < FIELDS.size(); index++) {
      String field = FIELDS.get(index);
      BigInteger wrap =
          BigInteger.ONE.shiftLeft(index < 2 ? 64 : 32).add(BigInteger.valueOf(expected[index]));
      for (JsonNode invalid :
          List.of(
              JSON.nullNode(),
              JSON.getNodeFactory().textNode(Long.toString(expected[index])),
              JSON.getNodeFactory().numberNode(expected[index] + 0.5),
              JSON.getNodeFactory().numberNode(wrap),
              JSON.getNodeFactory().booleanNode(true),
              JSON.createArrayNode(),
              JSON.createObjectNode(),
              JSON.getNodeFactory().numberNode(-1))) {
        List<JsonNode> data = fixture();
        object(data, index / 2).set(field, invalid);
        checks.add(() -> assertThrows(IllegalArgumentException.class, () -> numbers(data)));
      }
    }
    assertAll(checks);
  }

  @Test
  void primitiveRecordConstructorEstablishesRangeInvariants() {
    for (long[] input :
        List.of(
            new long[] {-1, 0, 1},
            new long[] {0, -1, 1},
            new long[] {0, 0, 0},
            new long[] {0, 0, -1})) {
      IllegalArgumentException failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> new GateCli.BaselineNumbers(input[0], input[1], (int) input[2]));
      assertEquals("invalid baseline numeric metadata", failure.getMessage());
    }
  }

  @Test
  void concurrentIndependentValidAndInvalidInputsPreserveTheirOwnResults() throws Exception {
    List<JsonNode> good = fixture();
    List<JsonNode> bad = fixture();
    object(bad, 0).put(MASTER_COUNT, -1);
    var workers = Executors.newFixedThreadPool(2);
    try {
      var valid = workers.submit(() -> numbers(good));
      var invalid =
          workers.submit(() -> assertThrows(IllegalArgumentException.class, () -> numbers(bad)));
      assertEquals(59627L, valid.get(5, TimeUnit.SECONDS).masterFileCount());
      assertEquals(
          "invalid baseline numeric metadata", invalid.get(5, TimeUnit.SECONDS).getMessage());
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(59627L, numbers(good).masterFileCount());
  }

  private static List<JsonNode> fixture() {
    return new ArrayList<>(
        List.of(
            JSON.createObjectNode().put(MASTER_COUNT, 59627).put(MASTER_BYTES, 19240707190L),
            JSON.createObjectNode().put(BROWSER_REVISION, 1187)));
  }

  private static ObjectNode object(List<JsonNode> input, int index) {
    return (ObjectNode) input.get(index);
  }

  private static GateCli.BaselineNumbers numbers(List<JsonNode> input) {
    return GateCli.baselineNumericMetadata(input.get(0), input.get(1));
  }
}
