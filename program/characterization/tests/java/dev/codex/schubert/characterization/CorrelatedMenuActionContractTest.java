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
  private static final String WITNESSES_PATH = "/observed/nk/witnesses";
  private static final String LOCAL_STAGE = "LOCAL";
  private static final String STAGE_FIELD = "stage";
  private static final String HTTP_PATH = "/http";
  private static final String HTTP_METHOD_FIELD = "method";
  private static final String HTTP_PATH_FIELD = "path";
  private static final String HTTP_STATUS_FIELD = "status";
  private static final String LOG_PAGE = "/logs";
  private static final String CURRENT_MENU_EVENT = "C_MENU";
  private static final String RESPONSE_BYTES_FIELD = "responseBytes";
  private static final String PAYLOAD_FIELD = "payload";
  private static final String SEARCH_OPERATION = "OP_SEARCH";
  private static final String ROW_FIELD = "row";
  private static final String MENU_OPERATION = "OP_MENU";
  private static final String ACTION_CATEGORY = "ACTION";
  private static final String REQUEST_CATEGORY = "REQUEST";
  private static final String CURRENT = "current";
  private static final String NK = "nk";
  private static final String ACTION = "action";
  private static final String CATEGORY = "category";
  private static final String OPERATION = "operation";
  private static final String EVENT = "event";
  private static final String HTTP_FIELD = "http";
  private static final String MENU_EVENT = "NK_MENU";
  private static final String SEARCH_EVENT = "NK_SEARCH";
  private static final String MENU_REQUEST_EVENT = "NK_HTTP_MENU";
  private static final String SEARCH_REQUEST_EVENT = "NK_HTTP_SEARCH";
  private static final String MISSING_MENU_REQUEST =
      "LOG_PROJECTION_REQUIRED_INITIAL_REQUEST:MENU_VIEWED";
  private static final String MISSING_SEARCH_REQUEST =
      "LOG_PROJECTION_REQUIRED_INITIAL_REQUEST:LOG_SEARCHED";
  private static final String REQUEST_FIELD = "request";
  private static final String EXPECTED_SIDE = "/expected/";
  private static final String OBSERVED_SIDE = "/observed/";
  private static final String ROW_EVENT = "/payload/event";
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
    assertEquals(6, input.at(WITNESSES_PATH).size());
  }

  @Test
  void qa054log002MenuNeedsExactlyOneLocalAndOutboxWitnessEach() {
    for (String stage : List.of(LOCAL_STAGE, "OUTBOX")) {
      var input = fixture();
      var witnesses = array(input, WITNESSES_PATH);
      for (int i = witnesses.size() - 1; i >= 0; i--) {
        if (witnesses.get(i).path(STAGE_FIELD).asText().equals(stage)
            && witnesses.get(i).at("/payload/event").asText().equals(MENU_EVENT))
          witnesses.remove(i);
      }
      assertTrue(
          CorrelatedLogEvidenceValidator.validate(input)
              .contains("LOG_PROJECTION_WITNESS_MISSING"));
    }
    var duplicate = fixture();
    var witnesses = array(duplicate, WITNESSES_PATH);
    witnesses.add(witnesses.get(0).deepCopy());
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(duplicate)
            .contains("LOG_PROJECTION_WITNESS_DUPLICATE"));
  }

  @Test
  void qa054log003MenuKeepsHttpContractAndApiSearchNeverUsesWebWitness() {
    for (Consumer<ObjectNode> mutation :
        List.<Consumer<ObjectNode>>of(
            x -> object(x, HTTP_PATH).remove(HTTP_METHOD_FIELD),
            x -> object(x, HTTP_PATH).put(HTTP_METHOD_FIELD, "POST"),
            x -> object(x, HTTP_PATH).put(HTTP_PATH_FIELD, LOG_PAGE),
            x -> object(x, HTTP_PATH).put(HTTP_PATH_FIELD, "/?raw"),
            x -> object(x, HTTP_PATH).put(HTTP_STATUS_FIELD, 201),
            x -> object(x, HTTP_PATH).put("elapsedMs", -1),
            x -> object(x, HTTP_PATH).put("elapsedMs", "1"),
            x -> object(x, HTTP_PATH).put(HTTP_STATUS_FIELD, 0))) {
      var input = fixture();
      update(input, NK, MENU_EVENT, mutation);
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(EXPECTED_ERROR));
    }
    var input = fixture();
    var search = (ObjectNode) array(input, "/expected/nk").get(1);
    array(input, WITNESSES_PATH)
        .add(
            JSON.createObjectNode()
                .put(STAGE_FIELD, LOCAL_STAGE)
                .set(PAYLOAD_FIELD, search.deepCopy()));
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(input)
            .contains("LOG_PROJECTION_WITNESS_UNEXPECTED"));
  }

  @Test
  void qa054log004OnlyExactActionCategoryAliasesAreApproved() {
    for (String alias : List.of("MENU", "menu ", "other")) {
      var input = fixture();
      update(input, CURRENT, CURRENT_MENU_EVENT, x -> x.put(ACTION, alias));
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(PAIR_ERROR));
    }
    for (String replacement : List.of("menu", "LOG_SEARCHED", "HTTP_REQUEST_COMPLETED")) {
      var input = fixture();
      update(input, NK, MENU_EVENT, x -> x.put(ACTION, replacement));
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(PAIR_ERROR));
    }
    var input = fixture();
    update(input, CURRENT, CURRENT_MENU_EVENT, x -> x.put(CATEGORY, "SECURITY"));
    assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(PAIR_ERROR));
  }

  @Test
  void qa054log005OperationBindingAndDatabaseReplayCountsRemainStrict() {
    var swapped = fixture();
    update(swapped, NK, MENU_EVENT, x -> x.put(OPERATION, SEARCH_OPERATION));
    assertTrue(CorrelatedLogEvidenceValidator.validate(swapped).contains(PAIR_ERROR));
    var missing = fixture();
    array(missing, "/observed/nk/after").remove(2);
    assertTrue(
        CorrelatedLogEvidenceValidator.validate(missing).contains("LOG_PROJECTION_DB_MISSING"));
    var replay = fixture();
    var after = array(replay, "/observed/nk/after");
    after.add(
        JSON.createObjectNode()
            .put(ROW_FIELD, "ROW_REPLAY")
            .set(PAYLOAD_FIELD, array(replay, "/expected/nk").get(1).deepCopy()));
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
                  .put(ROW_FIELD, "ROW_DUP_" + side)
                  .set(PAYLOAD_FIELD, copy.deepCopy()));
      if (side.equals(NK))
        for (String stage : List.of(LOCAL_STAGE, "OUTBOX")) {
          array(input, WITNESSES_PATH)
              .add(
                  JSON.createObjectNode()
                      .put(STAGE_FIELD, stage)
                      .set(PAYLOAD_FIELD, copy.deepCopy()));
        }
    }
    assertEquals(List.of(PAIR_ERROR), CorrelatedLogEvidenceValidator.validate(input));
  }

  @Test
  void qa054log007OptionalResponseBytesHaveIndependentUnsignedN12Boundaries() {
    for (long value : new long[] {0L, 999_999_999_999L}) {
      var input = fixture();
      update(input, NK, MENU_EVENT, x -> object(x, HTTP_PATH).put(RESPONSE_BYTES_FIELD, value));
      assertEquals(List.of(), CorrelatedLogEvidenceValidator.validate(input));
    }
    for (Consumer<ObjectNode> mutation :
        List.<Consumer<ObjectNode>>of(
            x -> object(x, HTTP_PATH).put(RESPONSE_BYTES_FIELD, -1),
            x -> object(x, HTTP_PATH).put(RESPONSE_BYTES_FIELD, 1_000_000_000_000L),
            x -> object(x, HTTP_PATH).put(RESPONSE_BYTES_FIELD, 0.5),
            x -> object(x, HTTP_PATH).put(RESPONSE_BYTES_FIELD, "0"),
            x -> object(x, HTTP_PATH).putNull(RESPONSE_BYTES_FIELD))) {
      var input = fixture();
      update(input, NK, MENU_EVENT, mutation);
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).contains(EXPECTED_ERROR));
    }
  }

  @Test
  void completeL01RequiresBothInitialOperationsAndTheirCompanionRequests() {
    assertEquals(List.of(), CorrelatedLogEvidenceValidator.validateCompleteL01(fixture()));
  }

  @Test
  void completeL01DoesNotAcceptBothSidesOmittingTheMenuAction() {
    var input = fixture();
    removeEvent(input, CURRENT, CURRENT_MENU_EVENT);
    removeEvent(input, NK, MENU_EVENT);

    assertTrue(CorrelatedLogEvidenceValidator.validate(input).isEmpty());
    assertEquals(
        List.of("LOG_PROJECTION_REQUIRED_INITIAL_ACTION:MENU_VIEWED"),
        CorrelatedLogEvidenceValidator.validateCompleteL01(input));
  }

  @Test
  void completeL01DoesNotAcceptBothSidesOmittingTheLogSearchAction() {
    var input = fixture();
    removeEvent(input, CURRENT, "C_SEARCH");
    removeEvent(input, NK, SEARCH_EVENT);

    assertTrue(CorrelatedLogEvidenceValidator.validate(input).isEmpty());
    assertEquals(
        List.of("LOG_PROJECTION_REQUIRED_INITIAL_ACTION:LOG_SEARCHED"),
        CorrelatedLogEvidenceValidator.validateCompleteL01(input));
  }

  @Test
  void completeL01ChecksCompanionRequestCountRouteMethodAndStatus() {
    var missing = fixture();
    removeEvent(missing, NK, MENU_REQUEST_EVENT);
    assertEquals(
        List.of(MISSING_MENU_REQUEST), CorrelatedLogEvidenceValidator.validateCompleteL01(missing));

    var duplicate = fixture();
    update(duplicate, NK, SEARCH_REQUEST_EVENT, row -> row.put(OPERATION, MENU_OPERATION));
    assertEquals(
        List.of(MISSING_MENU_REQUEST, MISSING_SEARCH_REQUEST),
        CorrelatedLogEvidenceValidator.validateCompleteL01(duplicate));

    for (Consumer<ObjectNode> wrong :
        List.<Consumer<ObjectNode>>of(
            http -> http.put(HTTP_METHOD_FIELD, "POST"),
            http -> http.put(HTTP_PATH_FIELD, "/other"),
            http -> http.put(HTTP_STATUS_FIELD, 404))) {
      var input = fixture();
      update(input, NK, SEARCH_REQUEST_EVENT, row -> wrong.accept(object(row, HTTP_PATH)));
      assertTrue(CorrelatedLogEvidenceValidator.validate(input).isEmpty());
      assertEquals(
          List.of(MISSING_SEARCH_REQUEST),
          CorrelatedLogEvidenceValidator.validateCompleteL01(input));
    }
  }

  @Test
  void completeL01MenuActionAndRequestNeedOneHttpRequestIdentity() {
    var input = fixture();
    update(input, NK, MENU_REQUEST_EVENT, row -> row.put(REQUEST_FIELD, "UNRELATED_HTTP"));
    assertTrue(CorrelatedLogEvidenceValidator.validate(input).isEmpty());
    assertEquals(
        List.of(MISSING_MENU_REQUEST), CorrelatedLogEvidenceValidator.validateCompleteL01(input));
  }

  static ObjectNode fixture() {
    var input = JSON.createObjectNode().put("version", 1);
    var expected = input.putObject("expected").put("oracleSha256", "a".repeat(64));
    var current = expected.putArray(CURRENT);
    var nk = expected.putArray(NK);
    current.add(
        payload(
            MENU_OPERATION, CURRENT_MENU_EVENT, ACTION_CATEGORY, "menu", JSON.createObjectNode()));
    current.add(
        payload(
            SEARCH_OPERATION, "C_SEARCH", ACTION_CATEGORY, "log_search", JSON.createObjectNode()));
    current.add(payload(MENU_OPERATION, "C_HTTP_MENU", REQUEST_CATEGORY, "", http("/")));
    current.add(payload(SEARCH_OPERATION, "C_HTTP_SEARCH", REQUEST_CATEGORY, "", http(LOG_PAGE)));
    nk.add(payload(MENU_OPERATION, MENU_EVENT, ACTION_CATEGORY, "MENU_VIEWED", http("/")));
    nk.add(
        payload(
            SEARCH_OPERATION,
            SEARCH_EVENT,
            ACTION_CATEGORY,
            "LOG_SEARCHED",
            JSON.createObjectNode()));
    nk.add(
        payload(
            MENU_OPERATION,
            MENU_REQUEST_EVENT,
            REQUEST_CATEGORY,
            "HTTP_REQUEST_COMPLETED",
            http("/")));
    nk.add(
        payload(
            SEARCH_OPERATION,
            SEARCH_REQUEST_EVENT,
            REQUEST_CATEGORY,
            "HTTP_REQUEST_COMPLETED",
            http(LOG_PAGE)));
    var observed = input.putObject("observed").put("oracleSha256", "a".repeat(64));
    for (String side : List.of(CURRENT, NK)) {
      var snapshot = observed.putObject(side);
      var old = JSON.createObjectNode();
      for (String field : List.of(OPERATION, REQUEST_FIELD, EVENT, "message", CATEGORY, ACTION))
        old.putNull(field);
      old.putObject(HTTP_FIELD);
      var before = snapshot.putArray("before");
      before.add(JSON.createObjectNode().put(ROW_FIELD, "OLD_" + side).set(PAYLOAD_FIELD, old));
      var after = snapshot.putArray("after");
      after.add(before.get(0).deepCopy());
      var witnesses = snapshot.putArray("witnesses");
      int index = 0;
      for (var event : expected.path(side)) {
        String rowId = "NEW_" + side + index;
        index++;
        after.add(
            JSON.createObjectNode().put(ROW_FIELD, rowId).set(PAYLOAD_FIELD, event.deepCopy()));
        if (side.equals(NK) && !event.path(ACTION).asText().equals("LOG_SEARCHED")) {
          for (String stage : List.of(LOCAL_STAGE, "OUTBOX"))
            witnesses.add(
                JSON.createObjectNode()
                    .put(STAGE_FIELD, stage)
                    .set(PAYLOAD_FIELD, event.deepCopy()));
        }
      }
    }
    return input;
  }

  private static ObjectNode http(String path) {
    return JSON.createObjectNode()
        .put(HTTP_METHOD_FIELD, "GET")
        .put(HTTP_PATH_FIELD, path)
        .put(HTTP_STATUS_FIELD, 200)
        .put("elapsedMs", 1);
  }

  private static ObjectNode payload(
      String operation, String event, String category, String action, ObjectNode http) {
    var value =
        JSON.createObjectNode()
            .put(OPERATION, operation)
            .put(REQUEST_FIELD, "REQ_" + operation)
            .put(EVENT, event)
            .put("message", "MSG_" + event)
            .put(CATEGORY, category)
            .put(ACTION, action);
    value.set(HTTP_FIELD, http);
    return value;
  }

  private static ObjectNode object(ObjectNode input, String path) {
    return (ObjectNode) input.at(path);
  }

  private static ArrayNode array(ObjectNode input, String path) {
    return (ArrayNode) input.at(path);
  }

  private static void removeEvent(ObjectNode input, String side, String event) {
    removeMatching(array(input, EXPECTED_SIDE + side), "/event", event);
    removeMatching(array(input, OBSERVED_SIDE + side + "/after"), ROW_EVENT, event);
    removeMatching(array(input, OBSERVED_SIDE + side + "/witnesses"), ROW_EVENT, event);
  }

  private static void removeMatching(ArrayNode entries, String pointer, String event) {
    for (int index = entries.size() - 1; index >= 0; index--) {
      if (entries.get(index).at(pointer).asText().equals(event)) entries.remove(index);
    }
  }

  private static void update(
      ObjectNode input, String side, String event, Consumer<ObjectNode> mutation) {
    for (var value : array(input, EXPECTED_SIDE + side))
      if (value.path(EVENT).asText().equals(event)) mutation.accept((ObjectNode) value);
    for (var row : array(input, OBSERVED_SIDE + side + "/after"))
      if (row.at(ROW_EVENT).asText().equals(event))
        mutation.accept((ObjectNode) row.path(PAYLOAD_FIELD));
    for (var row : array(input, OBSERVED_SIDE + side + "/witnesses"))
      if (row.at(ROW_EVENT).asText().equals(event))
        mutation.accept((ObjectNode) row.path(PAYLOAD_FIELD));
  }
}
