package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-CHR-DEF-012..014; SS355 integer schema/browser fields, BUG2275/YKT2020. */
final class GateDefinitionNumericTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String DESKTOP = "BROWSER_DESKTOP_VIEWPORT";
  private static final String MOBILE = "BROWSER_MOBILE_VIEWPORT";
  private static final String SCALE = "BROWSER_DEVICE_SCALE";
  private static final String REVISION = "BROWSER_REVISION";
  private static final List<NumericField> FIELDS =
      List.of(
          new NumericField(2, "/properties/cases/minItems", 24, "SCHEMA_MIN_ITEMS"),
          new NumericField(2, "/properties/cases/maxItems", 24, "SCHEMA_MAX_ITEMS"),
          new NumericField(4, "/browserRevision", 1187, REVISION),
          new NumericField(4, "/desktop/width", 1366, DESKTOP),
          new NumericField(4, "/desktop/height", 768, DESKTOP),
          new NumericField(4, "/mobile/width", 390, MOBILE),
          new NumericField(4, "/mobile/height", 844, MOBILE),
          new NumericField(4, "/desktop/deviceScaleFactor", 1, SCALE),
          new NumericField(4, "/mobile/deviceScaleFactor", 1, SCALE),
          new NumericField(0, "/browser/browserRevision", 1187, REVISION),
          new NumericField(0, "/browser/desktopWidth", 1366, DESKTOP),
          new NumericField(0, "/browser/desktopHeight", 768, DESKTOP),
          new NumericField(0, "/browser/mobileWidth", 390, MOBILE),
          new NumericField(0, "/browser/mobileHeight", 844, MOBILE),
          new NumericField(0, "/browser/deviceScaleFactor", 1, SCALE));
  private static final List<NumericPair> PAIRS =
      List.of(
          new NumericPair("/browser/browserRevision", List.of("/browserRevision"), REVISION),
          new NumericPair("/browser/desktopWidth", List.of("/desktop/width"), DESKTOP),
          new NumericPair("/browser/desktopHeight", List.of("/desktop/height"), DESKTOP),
          new NumericPair("/browser/mobileWidth", List.of("/mobile/width"), MOBILE),
          new NumericPair("/browser/mobileHeight", List.of("/mobile/height"), MOBILE),
          new NumericPair(
              "/browser/deviceScaleFactor",
              List.of("/desktop/deviceScaleFactor", "/mobile/deviceScaleFactor"),
              SCALE));

  @Test
  void schemaAndBrowserIntegersRejectTextFractionAndOverflow() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (NumericField field : FIELDS) {
      for (JsonNode invalid :
          List.of(
              JSON.getNodeFactory().textNode(Integer.toString(field.expected())),
              JSON.getNodeFactory().numberNode(field.expected() + 0.5),
              JSON.getNodeFactory()
                  .numberNode(
                      new BigInteger("4294967296").add(BigInteger.valueOf(field.expected()))))) {
        List<JsonNode> input = GateDefinitionDocumentsTest.fixture();
        set(input.get(field.document()), field.pointer(), invalid);
        checks.add(() -> assertTrue(validate(input).contains(field.failure())));
      }
    }
    assertAll("45 independent numeric schema/browser coercion vectors", checks);
  }

  @Test
  void equalMalformedExpectedAndObservedNumbersNeverValidateThroughDefaultZero() throws Exception {
    List<Executable> checks = new ArrayList<>();
    for (NumericPair pair : PAIRS) {
      for (JsonNode invalid :
          List.of(
              JSON.nullNode(),
              JSON.getNodeFactory().textNode("wrong"),
              JSON.getNodeFactory().booleanNode(true),
              JSON.getNodeFactory().numberNode(0))) {
        List<JsonNode> input = GateDefinitionDocumentsTest.fixture();
        set(input.get(0), pair.expectedPointer(), invalid);
        for (String pointer : pair.actualPointers()) set(input.get(4), pointer, invalid);
        checks.add(() -> assertTrue(validate(input).contains(pair.failure())));
      }
    }
    assertAll("24 malformed or nonpositive matching pairs", checks);
  }

  @Test
  void validIntegralRepresentationsStayEquivalentAndDifferentIntegersFail() throws Exception {
    for (NumericField field : FIELDS) {
      for (JsonNode valid :
          List.of(
              JSON.getNodeFactory().numberNode(field.expected()),
              JSON.getNodeFactory().numberNode((long) field.expected()),
              JSON.getNodeFactory().numberNode(BigInteger.valueOf(field.expected())))) {
        List<JsonNode> input = GateDefinitionDocumentsTest.fixture();
        set(input.get(field.document()), field.pointer(), valid);
        assertEquals(List.of(), validate(input));
      }
      List<JsonNode> different = GateDefinitionDocumentsTest.fixture();
      set(
          different.get(field.document()),
          field.pointer(),
          JSON.getNodeFactory().numberNode(field.expected() + 1));
      assertFalse(validate(different).isEmpty());
      assertTrue(validate(different).contains(field.failure()));
    }
  }

  private static List<String> validate(List<JsonNode> input) {
    return GateContractValidator.validateDefinitions(
        input.get(0), input.get(1), input.get(2), input.get(3), input.get(4), input.get(5));
  }

  private static void set(JsonNode root, String pointer, JsonNode value) {
    int slash = pointer.lastIndexOf('/');
    ObjectNode parent =
        slash == 0 ? (ObjectNode) root : (ObjectNode) root.at(pointer.substring(0, slash));
    parent.set(pointer.substring(slash + 1), value.deepCopy());
  }

  private record NumericField(int document, String pointer, int expected, String failure) {}

  private record NumericPair(String expectedPointer, List<String> actualPointers, String failure) {}
}
