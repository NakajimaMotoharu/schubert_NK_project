package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.List;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** QA054/UI264/SS351355 independent synthetic rows, no capture/DB/driver/baseline access. */
final class CorrelatedMenuActionContractTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final String CURRENT = "current";
  private static final String NK = "nk";
  private static final String ACTION = "action";
  private static final String CATEGORY = "category";
  private static final String OPERATION = "operation";
  private static final String EVENT = "event";
  private static final String HTTP = "http";
  private static final String MENU_EVENT = "NK_MENU";
  private static final String SEARCH_EVENT = "NK_SEARCH";
  private static final String PAIR_ERROR = "LOG_PROJECTION_APPROVED_ACTION_PAIR";
  private static final String EXPECTED_ERROR = "LOG_PROJECTION_EXPECTED_PAYLOAD";

  @Test
  void qa054log001ApprovedPairsAndMenuWitnessesPassWithoutMutatingEvidence() {
    var input = fixture();
    String before = input.toString();
    assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(input));
    assertEquals(before, input.toString());
    assertTrue(input.at("/expected/current/0/http").isEmpty());
    assertTrue(input.at("/expected/nk/1/http").isEmpty());
    assertEquals(6, input.at("/observed/nk/witnesses").size());
  }

  @Test
  void qa054log002MenuNeedsExactlyOneLocalAndOutboxWitnessEach() {
    for (String stage : List.of("LOCAL", "OUTBOX")) {
      var input = fixture();
      var witnesses = array(input, "/observed/nk/witnesses");
      for (int i = witnesses.size() - 1; i >= 0; i--) {
        if (witnesses.get(i).path("stage").asText().equals(stage)
            && witnesses.get(i).at("/payload/event").asText().equals(MENU_EVENT))
          witnesses.remove(i);
      }
      assertTrue(
          CorrelatedLogEvidenceValidator.validate(input)
              .contains("LOG_PROJECTION_WITNESS_MISSING"));
    }
    var duplicate = fixture();
    var witnesses = array(duplicate, "/observed/nk/witnesses");
    witnesses.add(witnesses.get(0).deepCopy());
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(duplicate)
            .contains("LOG_PROJECTION_WITNESS_DUPLICATE"));
  }

  @Test
  void qa054log003MenuKeepsHttpContractAndApiSearchNeverUsesWebWitness() {
    for (Consumer<ObjectNode> mutation :
        List.<Consumer<ObjectNode>>of(
            x -> object(x, "/http").remove("method"),
            x -> object(x, "/http").put("method", "POST"),
            x -> object(x, "/http").put("path", "/logs"),
            x -> object(x, "/http").put("path", "/?raw"),
            x -> object(x, "/http").put("status", 201),
            x -> object(x, "/http").put("elapsedMs", -1),
            x -> object(x, "/http").put("elapsedMs", "1"),
            x -> object(x, "/http").put("status", 0))) {
      var input = fixture();
      update(input, NK, MENU_EVENT, mutation);
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(EXPECTED_ERROR));
    }
    var input = fixture();
    var search = (ObjectNode) array(input, "/expected/nk").get(1);
    array(input, "/observed/nk/witnesses")
        .add(JSON.createObjectNode().put("stage", "LOCAL").set("payload", search.deepCopy()));
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(input)
            .contains("LOG_PROJECTION_WITNESS_UNEXPECTED"));
  }

  @Test
  void qa054log004OnlyExactActionCategoryAliasesAreApproved() {
    for (String alias : List.of("MENU", "menu ", "other")) {
      var input = fixture();
      update(input, CURRENT, "C_MENU", x -> x.put(ACTION, alias));
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(PAIR_ERROR));
    }
    for (String replacement : List.of("menu", "LOG_SEARCHED", "HTTP_REQUEST_COMPLETED")) {
      var input = fixture();
      update(input, NK, MENU_EVENT, x -> x.put(ACTION, replacement));
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(PAIR_ERROR));
    }
    var input = fixture();
    update(input, CURRENT, "C_MENU", x -> x.put(CATEGORY, "SECURITY"));
    assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(PAIR_ERROR));
  }

  @Test
  void qa054log005OperationBindingAndDatabaseReplayCountsRemainStrict() {
    var swapped = fixture();
    update(swapped, NK, MENU_EVENT, x -> x.put(OPERATION, "OP_SEARCH"));
    assertTrue(CorrelatedLogEvidenceValidator.validate(swapped).contains(PAIR_ERROR));
    var missing = fixture();
    array(missing, "/observed/nk/after").remove(2);
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(missing).contains("LOG_PROJECTION_DB_MISSING"));
    var replay = fixture();
    var after = array(replay, "/observed/nk/after");
    after.add(
        JSON.createObjectNode()
            .put("row", "ROW_REPLAY")
            .set("payload", array(replay, "/expected/nk").get(1).deepCopy()));
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(replay).contains("LOG_PROJECTION_DB_DUPLICATE"));
  }

  @Test
  void qa054log006TwoActionsInBothExpectationsCannotHideDuplicateSuccess() {
    var input = fixture();
    for (String side : List.of(CURRENT, NK)) {
      ObjectNode copy = (ObjectNode) array(input, "/expected/" + side).get(0).deepCopy();
      copy.put(EVENT, "DUP_" + side).put("message", "MSG_DUP_" + side);
      array(input, "/expected/" + side).add(copy);
      array(input, "/observed/" + side + "/after")
          .add(
              JSON.createObjectNode()
                  .put("row", "ROW_DUP_" + side)
                  .set("payload", copy.deepCopy()));
      if (side.equals(NK))
        for (String stage : List.of("LOCAL", "OUTBOX")) {
          array(input, "/observed/nk/witnesses")
              .add(JSON.createObjectNode().put("stage", stage).set("payload", copy.deepCopy()));
        }
    }
    assertEquals(List.of(PAIR_ERROR), CorrelatedLogEvidenceValidator.validate(input));
  }

  private static ObjectNode fixture() {
    var input = JSON.createObjectNode().put("version", 1);
    var expected = input.putObject("expected").put("oracleSha256", "a".repeat(64));
    var current = expected.putArray(CURRENT);
    var nk = expected.putArray(NK);
    current.add(payload("OP_MENU", "C_MENU", "ACTION", "menu", JSON.createObjectNode()));
    current.add(payload("OP_SEARCH", "C_SEARCH", "ACTION", "log_search", JSON.createObjectNode()));
    current.add(payload("OP_MENU", "C_HTTP_MENU", "REQUEST", "", http("/")));
    current.add(payload("OP_SEARCH", "C_HTTP_SEARCH", "REQUEST", "", http("/logs")));
    nk.add(payload("OP_MENU", MENU_EVENT, "ACTION", "MENU_VIEWED", http("/")));
    nk.add(payload("OP_SEARCH", SEARCH_EVENT, "ACTION", "LOG_SEARCHED", JSON.createObjectNode()));
    nk.add(payload("OP_MENU", "NK_HTTP_MENU", "REQUEST", "HTTP_REQUEST_COMPLETED", http("/")));
    nk.add(
        payload("OP_SEARCH", "NK_HTTP_SEARCH", "REQUEST", "HTTP_REQUEST_COMPLETED", http("/logs")));
    var observed = input.putObject("observed").put("oracleSha256", "a".repeat(64));
    for (String side : List.of(CURRENT, NK)) {
      var snapshot = observed.putObject(side);
      var old = JSON.createObjectNode();
      for (String field : List.of(OPERATION, "request", EVENT, "message", CATEGORY, ACTION))
        old.putNull(field);
      old.putObject(HTTP);
      var before = snapshot.putArray("before");
      before.add(JSON.createObjectNode().put("row", "OLD_" + side).set("payload", old));
      var after = snapshot.putArray("after");
      after.add(before.get(0).deepCopy());
      var witnesses = snapshot.putArray("witnesses");
      int index = 0;
      for (var event : expected.path(side)) {
        after.add(
            JSON.createObjectNode()
                .put("row", "NEW_" + side + index++)
                .set("payload", event.deepCopy()));
        if (side.equals(NK) && !event.path(ACTION).asText().equals("LOG_SEARCHED")) {
          for (String stage : List.of("LOCAL", "OUTBOX"))
            witnesses.add(
                JSON.createObjectNode().put("stage", stage).set("payload", event.deepCopy()));
        }
      }
    }
    return input;
  }

  private static ObjectNode http(String path) {
    return JSON.createObjectNode()
        .put("method", "GET")
        .put("path", path)
        .put("status", 200)
        .put("elapsedMs", 1);
  }

  private static ObjectNode payload(
      String operation, String event, String category, String action, ObjectNode http) {
    var value =
        JSON.createObjectNode()
            .put(OPERATION, operation)
            .put("request", "REQ_" + operation)
            .put(EVENT, event)
            .put("message", "MSG_" + event)
            .put(CATEGORY, category)
            .put(ACTION, action);
    value.set(HTTP, http);
    return value;
  }

  private static ObjectNode object(ObjectNode input, String path) {
    return (ObjectNode) input.at(path);
  }

  private static ArrayNode array(ObjectNode input, String path) {
    return (ArrayNode) input.at(path);
  }

  private static void update(
      ObjectNode input, String side, String event, Consumer<ObjectNode> mutation) {
    for (var value : array(input, "/expected/" + side))
      if (value.path(EVENT).asText().equals(event)) mutation.accept((ObjectNode) value);
    for (var row : array(input, "/observed/" + side + "/after"))
      if (row.at("/payload/event").asText().equals(event))
        mutation.accept((ObjectNode) row.path("payload"));
    for (var row : array(input, "/observed/" + side + "/witnesses"))
      if (row.at("/payload/event").asText().equals(event))
        mutation.accept((ObjectNode) row.path("payload"));
  }
}
