package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-CHR-LOG-COR-015/016; independent SS351 §3.3 N12 literal vectors, BUG2273/YKT2018. */
final class CorrelatedLogHttpNumberTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String NK_SIDE = "nk";
  private static final String FIELD = "responseBytes";

  @Test
  void rejectsConsistentlyInvalidNewResponseBytesAcrossBothSidesAndAllStages() {
    List<Executable> cases = new ArrayList<>();
    List<JsonNode> invalid =
        List.of(
            JSON.nullNode(),
            JSON.getNodeFactory().booleanNode(true),
            JSON.getNodeFactory().textNode("0"),
            JSON.getNodeFactory().numberNode(-1),
            JSON.getNodeFactory().numberNode(1_000_000_000_000L),
            JSON.getNodeFactory().numberNode(new BigInteger("18446744073709551616")),
            JSON.getNodeFactory().numberNode(0.5),
            JSON.getNodeFactory().numberNode(1.0),
            JSON.createArrayNode(),
            JSON.createObjectNode());
    for (String side : List.of("current", NK_SIDE)) {
      for (JsonNode value : invalid) {
        ObjectNode input = CorrelatedLogEvidenceValidatorTest.fixture();
        setNewRequest(input, side, value);
        cases.add(() -> assertFalse(CorrelatedLogEvidenceValidator.validate(input).isEmpty()));
      }
    }
    assertAll("20 independent present-invalid N12 vectors", cases);
  }

  @Test
  void acceptsAbsentAndIntegralN12BoundariesWithoutNormalizingKnownNullOldRows() {
    ObjectNode absent = CorrelatedLogEvidenceValidatorTest.fixture();
    assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(absent));
    for (long value : List.of(0L, 1L, 999_999_999_999L)) {
      ObjectNode input = CorrelatedLogEvidenceValidatorTest.fixture();
      for (String side : List.of("current", NK_SIDE)) {
        setNewRequest(input, side, JSON.getNodeFactory().numberNode(value));
        for (String snapshot : List.of("before", "after")) {
          object(input, "/observed/" + side + "/" + snapshot + "/0/payload/http").putNull(FIELD);
        }
      }
      ObjectNode unchanged = input.deepCopy();
      assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(input));
      assertEquals(unchanged, input);
    }
  }

  private static void setNewRequest(ObjectNode input, String side, JsonNode value) {
    object(input, "/expected/" + side + "/0/http").set(FIELD, value.deepCopy());
    object(input, "/observed/" + side + "/after/1/payload/http").set(FIELD, value.deepCopy());
    if (NK_SIDE.equals(side)) {
      for (JsonNode witness : input.at("/observed/nk/witnesses")) {
        ((ObjectNode) witness.path("payload").path("http")).set(FIELD, value.deepCopy());
      }
    }
  }

  private static ObjectNode object(JsonNode input, String pointer) {
    return (ObjectNode) input.at(pointer);
  }
}
