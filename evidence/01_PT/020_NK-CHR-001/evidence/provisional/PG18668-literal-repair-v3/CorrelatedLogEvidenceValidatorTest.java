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
    reject(x -> x.put("extra", 1), "ENVELOPE");
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
    reject(x -> x.withObject("/observed").put("extra", 1), "SOURCE_ENVELOPE");
    reject(x -> x.withObject("/expected").put("oracleSha256", 1), "ORACLE_BINDING");
    reject(x -> x.withObject("/expected").put("oracleSha256", "A".repeat(64)), "ORACLE_BINDING");
    reject(x -> x.withObject("/observed").put("oracleSha256", "b".repeat(64)), "ORACLE_BINDING");
  }

  @Test
  void expectedPayloadsUseClosedSafeFieldsAndExplicitRequestHttpValues() {
    for (String side : List.of("current", "nk")) {
      reject(x -> x.withObject("/expected").set(side, JSON.createObjectNode()), "EXPECTED_EVENTS");
      reject(x -> x.withObject("/expected").set(side, JSON.createArrayNode()), "EXPECTED_EVENTS");
      reject(
          x -> array(x, "/expected/" + side).add(x.at("/expected/" + side + "/0").deepCopy()),
          "EXPECTED_DUPLICATE");
      reject(x -> object(x, "/expected/" + side + "/0").put("extra", 1), "EXPECTED_PAYLOAD");
      for (String field : List.of("operation", "request", "event", "message")) {
        for (JsonNode value :
            List.of(
                NullNode.instance,
                JSON.getNodeFactory().numberNode(1),
                JSON.getNodeFactory().textNode(""),
                JSON.getNodeFactory().textNode("bad ref"),
                JSON.getNodeFactory().textNode("x".repeat(129)))) {
          reject(x -> object(x, "/expected/" + side + "/0").set(field, value), "EXPECTED_PAYLOAD");
        }
      }
      reject(
          x -> object(x, "/expected/" + side + "/0").put("category", "UNKNOWN"),
          "EXPECTED_PAYLOAD");
      reject(x -> object(x, "/expected/" + side + "/0").put("category", 1), "EXPECTED_PAYLOAD");
      reject(x -> object(x, "/expected/" + side + "/0").putNull("action"), "EXPECTED_PAYLOAD");
      reject(
          x -> object(x, "/expected/" + side + "/0").set("http", JSON.createArrayNode()),
          "EXPECTED_PAYLOAD");
      reject(
          x -> object(x, "/expected/" + side + "/0/http").put("unapproved", "synthetic"),
          "EXPECTED_PAYLOAD");
      reject(
          x ->
              object(x, "/expected/" + side + "/0/http")
                  .set("contentType", JSON.createObjectNode()),
          "EXPECTED_PAYLOAD");
      String http = "/expected/" + side + "/0/http";
      for (String field : List.of("method", "path", "status", "elapsedMs")) {
        reject(x -> object(x, http).remove(field), "EXPECTED_PAYLOAD");
      }
      reject(x -> object(x, http).put("method", " "), "EXPECTED_PAYLOAD");
      for (String path : List.of("relative", "/search?q=raw", "/search#raw")) {
        reject(x -> object(x, http).put("path", path), "EXPECTED_PAYLOAD");
      }
      for (JsonNode status :
          List.of(
              JSON.getNodeFactory().textNode("200"),
              JSON.getNodeFactory().numberNode(99),
              JSON.getNodeFactory().numberNode(600),
              JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")))) {
        reject(x -> object(x, http).set("status", status), "EXPECTED_PAYLOAD");
      }
      for (JsonNode elapsed :
          List.of(
              JSON.getNodeFactory().textNode("1"),
              JSON.getNodeFactory().numberNode(-1),
              JSON.getNodeFactory().numberNode(1_000_000_000_000L),
              JSON.getNodeFactory().numberNode(new BigInteger("9223372036854775808")))) {
        reject(x -> object(x, http).set("elapsedMs", elapsed), "EXPECTED_PAYLOAD");
      }
    }
    reject(x -> object(x, "/expected/nk/0").put("action", "legacy"), "EXPECTED_PAYLOAD");
  }

  @Test
  void preservesAllBeforeRowsAndRejectsEveryMissingDuplicateOrUncorrelatedNewEvent() {
    for (String side : List.of("current", "nk")) {
      String prefix = "/observed/" + side;
      reject(x -> object(x, prefix).put("extra", 1), "SNAPSHOT");
      reject(x -> object(x, prefix).set("before", NullNode.instance), "ROWS");
      reject(
          x -> array(x, prefix + "/before").add(x.at(prefix + "/before/0").deepCopy()),
          "ROW_DUPLICATE");
      reject(
          x -> array(x, prefix + "/after").add(x.at(prefix + "/after/0").deepCopy()),
          "ROW_DUPLICATE");
      reject(x -> array(x, prefix + "/after").remove(0), "EXISTING_ROW_CHANGED");
      reject(
          x -> object(x, prefix + "/after/0/payload").put("action", "changed"),
          "EXISTING_ROW_CHANGED");
      reject(x -> array(x, prefix + "/after").remove(1), "DB_MISSING");
      reject(x -> object(x, prefix + "/after/1").putNull("row"), "ROW_PAYLOAD");
      reject(x -> object(x, prefix + "/after/1").put("extra", 1), "ROW_PAYLOAD");
      reject(x -> object(x, prefix + "/after/1").putNull("payload"), "ROW_PAYLOAD");
      reject(x -> object(x, prefix + "/after/1/payload").putNull("http"), "ROW_PAYLOAD");
      reject(x -> object(x, prefix + "/after/1/payload").put("message", 1), "ROW_PAYLOAD");
      reject(
          x -> object(x, prefix + "/after/1/payload/http").put("unapproved", "synthetic"),
          "ROW_PAYLOAD");
      reject(
          x -> object(x, prefix + "/after/1/payload/http").set("clientIp", JSON.createArrayNode()),
          "ROW_PAYLOAD");
      reject(x -> object(x, prefix + "/after/1/payload/http").put("status", 0), "DB_PAYLOAD");
      for (String field : List.of("operation", "request", "event", "message")) {
        reject(x -> object(x, prefix + "/after/1/payload").put(field, "WRONG"), "DB_UNEXPECTED");
      }
      reject(
          x -> {
            ObjectNode duplicate = object(x, prefix + "/after/1").deepCopy();
            duplicate.put("row", "DIFFERENT_ROW");
            array(x, prefix + "/after").add(duplicate);
          },
          "DB_DUPLICATE");
      reject(x -> object(x, prefix + "/after/1/payload/http").put("status", 201), "DB_UNEXPECTED");
    }
  }

  @Test
  void requestWitnessesMustBeBothStagesOfTheSameLogicalEventAndSameHttpFields() {
    reject(x -> object(x, "/observed/nk").set("witnesses", JSON.createObjectNode()), "WITNESSES");
    for (int index : List.of(0, 1)) {
      reject(x -> array(x, "/observed/nk/witnesses").remove(index), "WITNESS_MISSING");
    }
    reject(
        x -> array(x, "/observed/nk/witnesses").add(x.at("/observed/nk/witnesses/0").deepCopy()),
        "WITNESS_DUPLICATE");
    reject(x -> object(x, "/observed/nk/witnesses/0").put("extra", 1), "WITNESS_PAYLOAD");
    reject(x -> object(x, "/observed/nk/witnesses/0").putNull("stage"), "WITNESS_PAYLOAD");
    reject(x -> object(x, "/observed/nk/witnesses/0").put("stage", "DB"), "WITNESS_PAYLOAD");
    reject(
        x -> object(x, "/observed/nk/witnesses/0/payload").put("action", "legacy"),
        "WITNESS_PAYLOAD");
    for (String field : List.of("operation", "request", "event", "message")) {
      reject(
          x -> object(x, "/observed/nk/witnesses/0/payload").put(field, "WRONG"),
          "WITNESS_UNEXPECTED");
    }
    reject(
        x -> object(x, "/observed/nk/witnesses/0/payload/http").put("status", 201),
        "WITNESS_UNEXPECTED");
    reject(
        x ->
            array(x, "/observed/current/witnesses")
                .add(x.at("/observed/nk/witnesses/0").deepCopy()),
        "WITNESS_UNEXPECTED");
    reject(
        x ->
            object(x, "/observed/nk/witnesses/0").set("payload", x.at("/expected/nk/1").deepCopy()),
        "WITNESS_UNEXPECTED");
  }

  @Test
  void operationSetsCannotDriftAndExtraTechnicalRowsRequireTheirOwnIndependentExpectation() {
    reject(
        x -> object(x, "/expected/current/0").put("operation", "OTHER_OPERATION"), "OPERATION_SET");
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
        for (String side : List.of("current", "nk")) {
          ObjectNode http = object(input, "/expected/" + side + "/0/http");
          http.put("status", status)
              .put("elapsedMs", elapsed)
              .put("responseBytes", 0)
              .put("contentType", "text/html")
              .put("clientIp", "192.0.2.1")
              .put("actorUsername", "synthetic-user")
              .put("actorRole", "USER");
          object(input, "/observed/" + side + "/after/1/payload").set("http", http.deepCopy());
        }
        JsonNode nk = input.at("/expected/nk/0");
        for (JsonNode witness : array(input, "/observed/nk/witnesses")) {
          ((ObjectNode) witness).set("payload", nk.deepCopy());
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
    object(faulty, "/observed/nk/after/1/payload").put("request", "WRONG_REQUEST");
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
    assertTrue(CorrelatedLogEvidenceValidator.versionOne(JSON.getNodeFactory().numberNode(BigInteger.ONE)));
  }

  static ObjectNode fixture() {
    ObjectNode http =
        JSON.createObjectNode()
            .put("method", "POST")
            .put("path", "/login")
            .put("status", 200)
            .put("elapsedMs", 1);
    ObjectNode currentRequest = payload("REQUEST", "", "EV_REQ", http);
    ObjectNode nkRequest = payload("REQUEST", "HTTP_REQUEST_COMPLETED", "EV_REQ", http);
    ObjectNode currentSecurity =
        payload("SECURITY", "login_success", "EV_LOGIN", JSON.createObjectNode());
    ObjectNode nkSecurity =
        payload("SECURITY", "LOGIN_SUCCEEDED", "EV_LOGIN", JSON.createObjectNode());
    ObjectNode input = JSON.createObjectNode().put("version", 1);
    ObjectNode expected = input.putObject("expected").put("oracleSha256", "a".repeat(64));
    expected.putArray("current").add(currentRequest).add(currentSecurity);
    expected.putArray("nk").add(nkRequest).add(nkSecurity);
    ObjectNode observed = input.putObject("observed").put("oracleSha256", "a".repeat(64));
    observed.set("current", snapshot("C", currentRequest, currentSecurity));
    observed.set("nk", snapshot("N", nkRequest, nkSecurity));
    for (String stage : List.of("LOCAL", "OUTBOX")) {
      object(input, "/observed/nk")
          .withArray("witnesses")
          .add(JSON.createObjectNode().put("stage", stage).set("payload", nkRequest.deepCopy()));
    }
    return input;
  }

  private static ObjectNode payload(String category, String action, String event, ObjectNode http) {
    ObjectNode value =
        JSON.createObjectNode()
            .put("operation", "OP_LOGIN")
            .put("request", "REQ_LOGIN")
            .put("event", event)
            .put("message", "MSG_" + event)
            .put("category", category)
            .put("action", action);
    value.set("http", http.deepCopy());
    return value;
  }

  private static ObjectNode snapshot(String prefix, ObjectNode request, ObjectNode security) {
    ObjectNode old = JSON.createObjectNode();
    for (String field : List.of("operation", "request", "event", "message", "category", "action")) {
      old.putNull(field);
    }
    old.putObject("http").putNull("path");
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
    return JSON.createObjectNode().put("row", key).set("payload", payload.deepCopy());
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
