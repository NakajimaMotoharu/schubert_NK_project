package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.NullNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.math.BigInteger;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** PT-CHR-LOG-COR-001..007, independently literal QA051/SS355 before/after/correlation oracle. */
final class CorrelatedLogEvidenceValidatorTest {
  private static final String FIXTURE_EXTRA = "extra";
  private static final String FIXTURE_EXPECTED = "/expected";
  private static final String FIXTURE_ORACLESHA256 = "oracleSha256";
  private static final String FIXTURE_CURRENT = "current";
  private static final String FIXTURE_EXPECTED_2C89F398 = "/expected/";
  private static final String FIXTURE_EXPECTED_PAYLOAD = "EXPECTED_PAYLOAD";
  private static final String FIXTURE_OPERATION = "operation";
  private static final String FIXTURE_REQUEST = "request";
  private static final String FIXTURE_EVENT = "event";
  private static final String FIXTURE_MESSAGE = "message";
  private static final String FIXTURE_CATEGORY = "category";
  private static final String FIXTURE_ACTION = "action";
  private static final String FIXTURE_HTTP = "http";
  private static final String FIXTURE_0_HTTP = "/0/http";
  private static final String FIXTURE_PATH = "path";
  private static final String FIXTURE_STATUS = "status";
  private static final String FIXTURE_ELAPSEDMS = "elapsedMs";
  private static final String FIXTURE_AFTER = "/after";
  private static final String FIXTURE_AFTER_1 = "/after/1";
  private static final String FIXTURE_ROW_PAYLOAD = "ROW_PAYLOAD";
  private static final String FIXTURE_PAYLOAD = "payload";
  private static final String FIXTURE_AFTER_1_PAYLOAD = "/after/1/payload";
  private static final String FIXTURE_AFTER_1_PAYLOAD_HTTP = "/after/1/payload/http";
  private static final String FIXTURE_OBSERVED_NK_WITNESSES_0 = "/observed/nk/witnesses/0";
  private static final String FIXTURE_WITNESS_PAYLOAD = "WITNESS_PAYLOAD";
  private static final String FIXTURE_WITNESS_UNEXPECTED = "WITNESS_UNEXPECTED";

  private static final ObjectMapper JSON = new ObjectMapper();

  @Test
  void validActionMappingRequestChainAndKnownNullOldRowsRemainDistinct() {
    ObjectNode input = fixture();
    List<String> failures = CorrelatedLogEvidenceValidator.validate(input);
    assertEquals(List.of(), failures);
    assertThrows(UnsupportedOperationException.class, () -> failures.add("mutate"));
    assertEquals("login_success", input.at("/expected/current/1/action").asText());
    assertEquals("LOGIN_SUCCEEDED", input.at("/expected/nk/1/action").asText());
    assertTrue(input.at("/observed/current/before/0/payload/request").isNull());
  }

  @Test
  void envelopeVersionAndIndependentOracleBindingAreRequired() {
    for (JsonNode node :
        List.of(
            NullNode.instance,
            JSON.createArrayNode(),
            JSON.getNodeFactory().textNode("bad"),
            JSON.createObjectNode())) {
      assertEquals(
          List.of("LOG_PROJECTION_ENVELOPE"), CorrelatedLogEvidenceValidator.validate(node));
    }
    assertEquals(List.of("LOG_PROJECTION_ENVELOPE"), CorrelatedLogEvidenceValidator.validate(null));
    reject(x -> x.put(FIXTURE_EXTRA, 1), "ENVELOPE");
    reject(
        x -> {
          x.remove("expected");
          x.put("unexpected", 1);
        },
        "ENVELOPE");
    for (JsonNode node :
        List.of(
            JSON.getNodeFactory().textNode("1"),
            JSON.getNodeFactory().numberNode(2),
            JSON.getNodeFactory().numberNode(1.5),
            JSON.getNodeFactory().numberNode(new BigInteger("4294967297")))) {
      reject(x -> x.set("version", node), "VERSION");
    }
    reject(x -> x.set("expected", NullNode.instance), "SOURCE_ENVELOPE");
    reject(x -> x.withObject("/observed").put(FIXTURE_EXTRA, 1), "SOURCE_ENVELOPE");
    reject(x -> x.withObject(FIXTURE_EXPECTED).put(FIXTURE_ORACLESHA256, 1), "ORACLE_BINDING");
    reject(
        x -> x.withObject(FIXTURE_EXPECTED).put(FIXTURE_ORACLESHA256, "A".repeat(64)),
        "ORACLE_BINDING");
    reject(
        x -> x.withObject("/observed").put(FIXTURE_ORACLESHA256, "b".repeat(64)), "ORACLE_BINDING");
  }

  @Test
  void expectedPayloadsUseClosedSafeFieldsAndExplicitRequestHttpValues() {
    for (String side : List.of(FIXTURE_CURRENT, "nk")) {
      reject(
          x -> x.withObject(FIXTURE_EXPECTED).set(side, JSON.createObjectNode()),
          "EXPECTED_EVENTS");
      reject(
          x -> x.withObject(FIXTURE_EXPECTED).set(side, JSON.createArrayNode()), "EXPECTED_EVENTS");
      reject(
          x ->
              array(x, FIXTURE_EXPECTED_2C89F398 + side)
                  .add(x.at(FIXTURE_EXPECTED_2C89F398 + side + "/0").deepCopy()),
          "EXPECTED_DUPLICATE");
      reject(
          x -> object(x, FIXTURE_EXPECTED_2C89F398 + side + "/0").put(FIXTURE_EXTRA, 1),
          FIXTURE_EXPECTED_PAYLOAD);
      for (String field :
          List.of(FIXTURE_OPERATION, FIXTURE_REQUEST, FIXTURE_EVENT, FIXTURE_MESSAGE)) {
        for (JsonNode value :
            List.of(
                NullNode.instance,
                JSON.getNodeFactory().numberNode(1),
                JSON.getNodeFactory().textNode(""),
                JSON.getNodeFactory().textNode("bad ref"),
                JSON.getNodeFactory().textNode("x".repeat(129)))) {
          reject(
              x -> object(x, FIXTURE_EXPECTED_2C89F398 + side + "/0").set(field, value),
              FIXTURE_EXPECTED_PAYLOAD);
        }
      }
      reject(
          x -> object(x, FIXTURE_EXPECTED_2C89F398 + side + "/0").put(FIXTURE_CATEGORY, "UNKNOWN"),
          FIXTURE_EXPECTED_PAYLOAD);
      reject(
          x -> object(x, FIXTURE_EXPECTED_2C89F398 + side + "/0").put(FIXTURE_CATEGORY, 1),
          FIXTURE_EXPECTED_PAYLOAD);
      reject(
          x -> object(x, FIXTURE_EXPECTED_2C89F398 + side + "/0").putNull(FIXTURE_ACTION),
          FIXTURE_EXPECTED_PAYLOAD);
      reject(
          x ->
              object(x, FIXTURE_EXPECTED_2C89F398 + side + "/0")
                  .set(FIXTURE_HTTP, JSON.createArrayNode()),
          FIXTURE_EXPECTED_PAYLOAD);
      reject(
          x ->
              object(x, FIXTURE_EXPECTED_2C89F398 + side + FIXTURE_0_HTTP)
                  .put("unapproved", "synthetic"),
          FIXTURE_EXPECTED_PAYLOAD);
      reject(
          x ->
              object(x, FIXTURE_EXPECTED_2C89F398 + side + FIXTURE_0_HTTP)
                  .set("contentType", JSON.createObjectNode()),
          FIXTURE_EXPECTED_PAYLOAD);
      String http = FIXTURE_EXPECTED_2C89F398 + side + FIXTURE_0_HTTP;
      for (String field : List.of("method", FIXTURE_PATH, FIXTURE_STATUS, FIXTURE_ELAPSEDMS)) {
        reject(x -> object(x, http).remove(field), FIXTURE_EXPECTED_PAYLOAD);
      }
      reject(x -> object(x, http).put("method", " "), FIXTURE_EXPECTED_PAYLOAD);
      for (String path : List.of("relative", "/search?q=raw", "/search#raw")) {
        reject(x -> object(x, http).put(FIXTURE_PATH, path), FIXTURE_EXPECTED_PAYLOAD);
      }
      for (JsonNode status :
          List.of(
              JSON.getNodeFactory().textNode("200"),
              JSON.getNodeFactory().numberNode(99),
              JSON.getNodeFactory().numberNode(600),
              JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")))) {
        reject(x -> object(x, http).set(FIXTURE_STATUS, status), FIXTURE_EXPECTED_PAYLOAD);
      }
      for (JsonNode elapsed :
          List.of(
              JSON.getNodeFactory().textNode("1"),
              JSON.getNodeFactory().numberNode(-1),
              JSON.getNodeFactory().numberNode(1_000_000_000_000L),
              JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")))) {
        reject(x -> object(x, http).set(FIXTURE_ELAPSEDMS, elapsed), FIXTURE_EXPECTED_PAYLOAD);
      }
    }
    reject(
        x -> object(x, "/expected/nk/0").put(FIXTURE_ACTION, "legacy"), FIXTURE_EXPECTED_PAYLOAD);
  }

  @Test
  void preservesAllBeforeRowsAndRejectsEveryMissingDuplicateOrUncorrelatedNewEvent() {
    for (String side : List.of(FIXTURE_CURRENT, "nk")) {
      String prefix = "/observed/" + side;
      reject(x -> object(x, prefix).put(FIXTURE_EXTRA, 1), "SNAPSHOT");
      reject(x -> object(x, prefix).set("before", NullNode.instance), "ROWS");
      reject(
          x -> array(x, prefix + "/before").add(x.at(prefix + "/before/0").deepCopy()),
          "ROW_DUPLICATE");
      reject(
          x -> array(x, prefix + FIXTURE_AFTER).add(x.at(prefix + "/after/0").deepCopy()),
          "ROW_DUPLICATE");
      reject(x -> array(x, prefix + FIXTURE_AFTER).remove(0), "EXISTING_ROW_CHANGED");
      reject(
          x -> object(x, prefix + "/after/0/payload").put(FIXTURE_ACTION, "changed"),
          "EXISTING_ROW_CHANGED");
      reject(x -> array(x, prefix + FIXTURE_AFTER).remove(1), "DB_MISSING");
      reject(x -> object(x, prefix + FIXTURE_AFTER_1).putNull("row"), FIXTURE_ROW_PAYLOAD);
      reject(x -> object(x, prefix + FIXTURE_AFTER_1).put(FIXTURE_EXTRA, 1), FIXTURE_ROW_PAYLOAD);
      reject(
          x -> object(x, prefix + FIXTURE_AFTER_1).putNull(FIXTURE_PAYLOAD), FIXTURE_ROW_PAYLOAD);
      reject(
          x -> object(x, prefix + FIXTURE_AFTER_1_PAYLOAD).putNull(FIXTURE_HTTP),
          FIXTURE_ROW_PAYLOAD);
      reject(
          x -> object(x, prefix + FIXTURE_AFTER_1_PAYLOAD).put(FIXTURE_MESSAGE, 1),
          FIXTURE_ROW_PAYLOAD);
      reject(
          x -> object(x, prefix + FIXTURE_AFTER_1_PAYLOAD_HTTP).put("unapproved", "synthetic"),
          FIXTURE_ROW_PAYLOAD);
      reject(
          x ->
              object(x, prefix + FIXTURE_AFTER_1_PAYLOAD_HTTP)
                  .set("clientIp", JSON.createArrayNode()),
          FIXTURE_ROW_PAYLOAD);
      reject(
          x -> object(x, prefix + FIXTURE_AFTER_1_PAYLOAD_HTTP).put(FIXTURE_STATUS, 0),
          "DB_PAYLOAD");
      for (String field :
          List.of(FIXTURE_OPERATION, FIXTURE_REQUEST, FIXTURE_EVENT, FIXTURE_MESSAGE)) {
        reject(
            x -> object(x, prefix + FIXTURE_AFTER_1_PAYLOAD).put(field, "WRONG"), "DB_UNEXPECTED");
      }
      reject(
          x -> {
            ObjectNode duplicate = object(x, prefix + FIXTURE_AFTER_1).deepCopy();
            duplicate.put("row", "DIFFERENT_ROW");
            array(x, prefix + FIXTURE_AFTER).add(duplicate);
          },
          "DB_DUPLICATE");
      reject(
          x -> object(x, prefix + FIXTURE_AFTER_1_PAYLOAD_HTTP).put(FIXTURE_STATUS, 201),
          "DB_UNEXPECTED");
    }
  }

  @Test
  void requestWitnessesMustBeBothStagesOfTheSameLogicalEventAndSameHttpFields() {
    reject(x -> object(x, "/observed/nk").set("witnesses", JSON.createObjectNode()), "WITNESSES");
    for (int index : List.of(0, 1)) {
      reject(x -> array(x, "/observed/nk/witnesses").remove(index), "WITNESS_MISSING");
    }
    reject(
        x ->
            array(x, "/observed/nk/witnesses")
                .add(x.at(FIXTURE_OBSERVED_NK_WITNESSES_0).deepCopy()),
        "WITNESS_DUPLICATE");
    reject(
        x -> object(x, FIXTURE_OBSERVED_NK_WITNESSES_0).put(FIXTURE_EXTRA, 1),
        FIXTURE_WITNESS_PAYLOAD);
    reject(
        x -> object(x, FIXTURE_OBSERVED_NK_WITNESSES_0).putNull("stage"), FIXTURE_WITNESS_PAYLOAD);
    reject(
        x -> object(x, FIXTURE_OBSERVED_NK_WITNESSES_0).put("stage", "DB"),
        FIXTURE_WITNESS_PAYLOAD);
    reject(
        x -> object(x, "/observed/nk/witnesses/0/payload").put(FIXTURE_ACTION, "legacy"),
        FIXTURE_WITNESS_PAYLOAD);
    for (String field :
        List.of(FIXTURE_OPERATION, FIXTURE_REQUEST, FIXTURE_EVENT, FIXTURE_MESSAGE)) {
      reject(
          x -> object(x, "/observed/nk/witnesses/0/payload").put(field, "WRONG"),
          FIXTURE_WITNESS_UNEXPECTED);
    }
    reject(
        x -> object(x, "/observed/nk/witnesses/0/payload/http").put(FIXTURE_STATUS, 201),
        FIXTURE_WITNESS_UNEXPECTED);
    reject(
        x ->
            array(x, "/observed/current/witnesses")
                .add(x.at(FIXTURE_OBSERVED_NK_WITNESSES_0).deepCopy()),
        FIXTURE_WITNESS_UNEXPECTED);
    reject(
        x ->
            object(x, FIXTURE_OBSERVED_NK_WITNESSES_0)
                .set(FIXTURE_PAYLOAD, x.at("/expected/nk/1").deepCopy()),
        FIXTURE_WITNESS_UNEXPECTED);
  }

  @Test
  void operationSetsCannotDriftAndExtraTechnicalRowsRequireTheirOwnIndependentExpectation() {
    reject(
        x -> object(x, "/expected/current/0").put(FIXTURE_OPERATION, "OTHER_OPERATION"),
        "OPERATION_SET");
    ObjectNode input = fixture();
    ObjectNode technical =
        payload("SYSTEM", "INTEGRITY_FAILED", "EV_TECH", JSON.createObjectNode());
    array(input, "/observed/nk/after").add(row("N_TECH", technical));
    assertFalse(CorrelatedLogEvidenceValidator.validate(input).isEmpty());
    array(input, "/expected/nk").add(technical.deepCopy());
    assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(input));
  }

  @Test
  void inclusiveHttpBoundariesAndOptionalFieldsArePreservedExactly() {
    for (int status : List.of(100, 599)) {
      for (long elapsed : List.of(0L, 999_999_999_999L)) {
        ObjectNode input = fixture();
        for (String side : List.of(FIXTURE_CURRENT, "nk")) {
          ObjectNode http = object(input, FIXTURE_EXPECTED_2C89F398 + side + FIXTURE_0_HTTP);
          http.put(FIXTURE_STATUS, status)
              .put(FIXTURE_ELAPSEDMS, elapsed)
              .put("responseBytes", 0)
              .put("contentType", "text/html")
              .put("clientIp", "192.0.2.1")
              .put("actorUsername", "synthetic-user")
              .put("actorRole", "USER");
          object(input, "/observed/" + side + FIXTURE_AFTER_1_PAYLOAD)
              .set(FIXTURE_HTTP, http.deepCopy());
        }
        JsonNode nk = input.at("/expected/nk/0");
        for (JsonNode witness : array(input, "/observed/nk/witnesses")) {
          ((ObjectNode) witness).set(FIXTURE_PAYLOAD, nk.deepCopy());
        }
        assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(input));
      }
    }
  }

  @Test
  void concurrentValidAndInvalidSnapshotsKeepTheirDiagnosticsAndInputsIsolated() throws Exception {
    ObjectNode healthy = fixture();
    ObjectNode unchanged = healthy.deepCopy();
    ObjectNode faulty = fixture();
    object(faulty, "/observed/nk/after/1/payload").put(FIXTURE_REQUEST, "WRONG_REQUEST");
    try (var workers = Executors.newFixedThreadPool(2)) {
      var good = workers.submit(() -> CorrelatedLogEvidenceValidator.validate(healthy));
      var bad = workers.submit(() -> CorrelatedLogEvidenceValidator.validate(faulty));
      assertEquals(List.of(), good.get());
      assertTrue(bad.get().contains("LOG_PROJECTION_DB_UNEXPECTED"));
    }
    assertEquals(unchanged, healthy);
  }

  @Test
  void strictVersionPredicateNeverCoercesMissingFractionalTextOrOversizedValues() {
    assertFalse(CorrelatedLogEvidenceValidator.versionOne(null));
    for (JsonNode value :
        List.of(
            NullNode.instance,
            JSON.getNodeFactory().textNode("1"),
            JSON.getNodeFactory().numberNode(1.5),
            JSON.getNodeFactory().numberNode(0),
            JSON.getNodeFactory().numberNode(new BigInteger("4294967297")))) {
      assertFalse(CorrelatedLogEvidenceValidator.versionOne(value));
    }
    assertTrue(CorrelatedLogEvidenceValidator.versionOne(JSON.getNodeFactory().numberNode(1)));
    assertTrue(CorrelatedLogEvidenceValidator.versionOne(JSON.getNodeFactory().numberNode(1L)));
    assertTrue(
        CorrelatedLogEvidenceValidator.versionOne(
            JSON.getNodeFactory().numberNode(BigInteger.ONE)));
  }

  static ObjectNode fixture() {
    ObjectNode http =
        JSON.createObjectNode()
            .put("method", "POST")
            .put(FIXTURE_PATH, "/login")
            .put(FIXTURE_STATUS, 200)
            .put(FIXTURE_ELAPSEDMS, 1);
    ObjectNode currentRequest = payload("REQUEST", "", "EV_REQ", http);
    ObjectNode nkRequest = payload("REQUEST", "HTTP_REQUEST_COMPLETED", "EV_REQ", http);
    ObjectNode currentSecurity =
        payload("SECURITY", "login_success", "EV_LOGIN", JSON.createObjectNode());
    ObjectNode nkSecurity =
        payload("SECURITY", "LOGIN_SUCCEEDED", "EV_LOGIN", JSON.createObjectNode());
    ObjectNode input = JSON.createObjectNode().put("version", 1);
    ObjectNode expected = input.putObject("expected").put(FIXTURE_ORACLESHA256, "a".repeat(64));
    expected.putArray(FIXTURE_CURRENT).add(currentRequest).add(currentSecurity);
    expected.putArray("nk").add(nkRequest).add(nkSecurity);
    ObjectNode observed = input.putObject("observed").put(FIXTURE_ORACLESHA256, "a".repeat(64));
    observed.set(FIXTURE_CURRENT, snapshot("C", currentRequest, currentSecurity));
    observed.set("nk", snapshot("N", nkRequest, nkSecurity));
    for (String stage : List.of("LOCAL", "OUTBOX")) {
      object(input, "/observed/nk")
          .withArray("witnesses")
          .add(
              JSON.createObjectNode()
                  .put("stage", stage)
                  .set(FIXTURE_PAYLOAD, nkRequest.deepCopy()));
    }
    return input;
  }

  private static ObjectNode payload(String category, String action, String event, ObjectNode http) {
    ObjectNode value =
        JSON.createObjectNode()
            .put(FIXTURE_OPERATION, "OP_LOGIN")
            .put(FIXTURE_REQUEST, "REQ_LOGIN")
            .put(FIXTURE_EVENT, event)
            .put(FIXTURE_MESSAGE, "MSG_" + event)
            .put(FIXTURE_CATEGORY, category)
            .put(FIXTURE_ACTION, action);
    value.set(FIXTURE_HTTP, http.deepCopy());
    return value;
  }

  private static ObjectNode snapshot(String prefix, ObjectNode request, ObjectNode security) {
    ObjectNode old = JSON.createObjectNode();
    for (String field :
        List.of(
            FIXTURE_OPERATION,
            FIXTURE_REQUEST,
            FIXTURE_EVENT,
            FIXTURE_MESSAGE,
            FIXTURE_CATEGORY,
            FIXTURE_ACTION)) {
      old.putNull(field);
    }
    old.putObject(FIXTURE_HTTP).putNull(FIXTURE_PATH);
    ObjectNode value = JSON.createObjectNode();
    value.putArray("before").add(row(prefix + "_OLD", old));
    value
        .putArray("after")
        .add(row(prefix + "_OLD", old))
        .add(row(prefix + "_REQ", request))
        .add(row(prefix + "_LOGIN", security));
    value.putArray("witnesses");
    return value;
  }

  private static ObjectNode row(String key, ObjectNode payload) {
    return JSON.createObjectNode().put("row", key).set(FIXTURE_PAYLOAD, payload.deepCopy());
  }

  private static ObjectNode object(JsonNode value, String pointer) {
    return (ObjectNode) value.at(pointer);
  }

  private static ArrayNode array(JsonNode value, String pointer) {
    return (ArrayNode) value.at(pointer);
  }

  private static void reject(Consumer<ObjectNode> mutation, String code) {
    ObjectNode value = fixture();
    mutation.accept(value);
    List<String> actual = CorrelatedLogEvidenceValidator.validate(value);
    assertTrue(actual.contains("LOG_PROJECTION_" + code), () -> "missing fixed code: " + code);
  }
}
