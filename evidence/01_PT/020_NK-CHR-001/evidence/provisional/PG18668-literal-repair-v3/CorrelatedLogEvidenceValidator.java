package dev.codex.schubert.characterization;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Validates independently frozen, safe log projections without opening a DB or collecting a log.
 * Trace: QA-051; UI264 §5.1; SS355 §8.1; SS351 §3/4; WBS-P020-01. Diagnostics contain fixed codes
 * only. Real capture/source/DOM qualification remains separate.
 */
public final class CorrelatedLogEvidenceValidator {
  private static final Set<String> PAYLOAD_FIELDS =
      Set.of("operation", "request", "event", "message", "category", "action", "http");
  private static final Set<String> CATEGORIES =
      Set.of("REQUEST", "ACTION", "SECURITY", "MQ", "SYSTEM", "BATCH");
  private static final Set<String> HTTP_FIELDS =
      Set.of(
          "method",
          "path",
          "status",
          "elapsedMs",
          "responseBytes",
          "contentType",
          "clientIp",
          "actorUsername",
          "actorRole");
  private static final List<String> STAGES = List.of("LOCAL", "OUTBOX");

  private CorrelatedLogEvidenceValidator() {}

  /** Missing, ambiguous, duplicate or changed evidence is a failure, never an empty success. */
  public static List<String> validate(JsonNode evidence) {
    List<String> failures = new ArrayList<>();
    if (evidence == null || !shape(evidence, Set.of("version", "expected", "observed"))) {
      return List.of("LOG_PROJECTION_ENVELOPE");
    }
    if (!versionOne(evidence.path("version"))) {
      failures.add("LOG_PROJECTION_VERSION");
    }
    JsonNode expected = evidence.path("expected");
    JsonNode observed = evidence.path("observed");
    if (!shape(expected, Set.of("oracleSha256", "current", "nk"))
        || !shape(observed, Set.of("oracleSha256", "current", "nk"))) {
      return List.of("LOG_PROJECTION_SOURCE_ENVELOPE");
    }
    if (!expected.path("oracleSha256").isTextual()
        || !expected.path("oracleSha256").asText().matches("[0-9a-f]{64}")
        || !expected.path("oracleSha256").equals(observed.path("oracleSha256"))) {
      failures.add("LOG_PROJECTION_ORACLE_BINDING");
    }
    Map<String, JsonNode> current = expectations(expected.path("current"), false, failures);
    Map<String, JsonNode> nk = expectations(expected.path("nk"), true, failures);
    if (!operations(current).equals(operations(nk))) {
      failures.add("LOG_PROJECTION_OPERATION_SET");
    }
    compareSide(current, observed.path("current"), false, failures);
    compareSide(nk, observed.path("nk"), true, failures);
    return List.copyOf(failures);
  }

  private static Map<String, JsonNode> expectations(
      JsonNode values, boolean nk, List<String> failures) {
    Map<String, JsonNode> events = new HashMap<>();
    if (!values.isArray() || values.isEmpty()) {
      failures.add("LOG_PROJECTION_EXPECTED_EVENTS");
      return events;
    }
    for (JsonNode value : values) {
      if (!payload(value, nk)) {
        failures.add("LOG_PROJECTION_EXPECTED_PAYLOAD");
      } else if (events.putIfAbsent(value.path("event").asText(), value) != null) {
        failures.add("LOG_PROJECTION_EXPECTED_DUPLICATE");
      }
    }
    return events;
  }

  private static Set<String> operations(Map<String, JsonNode> events) {
    Set<String> operations = new HashSet<>();
    for (JsonNode value : events.values()) operations.add(value.path("operation").asText());
    return operations;
  }

  private static void compareSide(
      Map<String, JsonNode> expected, JsonNode side, boolean nk, List<String> failures) {
    if (!shape(side, Set.of("before", "after", "witnesses"))) {
      failures.add("LOG_PROJECTION_SNAPSHOT");
      return;
    }
    Map<String, JsonNode> before = rows(side.path("before"), failures);
    Map<String, JsonNode> after = rows(side.path("after"), failures);
    for (Map.Entry<String, JsonNode> row : before.entrySet()) {
      if (!row.getValue().equals(after.get(row.getKey()))) {
        failures.add("LOG_PROJECTION_EXISTING_ROW_CHANGED");
      }
    }
    Map<String, JsonNode> addedEvents = new HashMap<>();
    for (Map.Entry<String, JsonNode> row : after.entrySet()) {
      if (before.containsKey(row.getKey())) continue;
      JsonNode value = row.getValue();
      if (!payload(value, nk)) {
        failures.add("LOG_PROJECTION_DB_PAYLOAD");
        continue;
      }
      String event = value.path("event").asText();
      if (addedEvents.putIfAbsent(event, value) != null) {
        failures.add("LOG_PROJECTION_DB_DUPLICATE");
      }
      if (!value.equals(expected.get(event))) failures.add("LOG_PROJECTION_DB_UNEXPECTED");
    }
    for (String event : expected.keySet()) {
      if (!addedEvents.containsKey(event)) failures.add("LOG_PROJECTION_DB_MISSING");
    }
    witnesses(expected, side.path("witnesses"), nk, failures);
  }

  private static Map<String, JsonNode> rows(JsonNode values, List<String> failures) {
    Map<String, JsonNode> rows = new HashMap<>();
    if (!values.isArray()) {
      failures.add("LOG_PROJECTION_ROWS");
      return rows;
    }
    for (JsonNode row : values) {
      if (!shape(row, Set.of("row", "payload"))
          || !reference(row.path("row"))
          || !safeProjection(row.path("payload"))) {
        failures.add("LOG_PROJECTION_ROW_PAYLOAD");
      } else if (rows.putIfAbsent(row.path("row").asText(), row.path("payload")) != null) {
        failures.add("LOG_PROJECTION_ROW_DUPLICATE");
      }
    }
    return rows;
  }

  // Old rows need no invented run correlation. Preserve known nulls and the entire safe projection.
  private static boolean safeProjection(JsonNode value) {
    if (!shape(value, PAYLOAD_FIELDS) || !value.path("http").isObject()) return false;
    for (String field : List.of("operation", "request", "event", "message", "category", "action")) {
      JsonNode item = value.path(field);
      if (!item.isTextual() && !item.isNull()) return false;
    }
    for (Map.Entry<String, JsonNode> item : value.path("http").properties()) {
      if (!HTTP_FIELDS.contains(item.getKey()) || !item.getValue().isValueNode()) return false;
    }
    return true;
  }

  private static void witnesses(
      Map<String, JsonNode> expected, JsonNode values, boolean nk, List<String> failures) {
    Set<String> found = new HashSet<>();
    if (!values.isArray()) {
      failures.add("LOG_PROJECTION_WITNESSES");
      return;
    }
    for (JsonNode witness : values) {
      if (!shape(witness, Set.of("stage", "payload"))
          || !witness.path("stage").isTextual()
          || !STAGES.contains(witness.path("stage").asText())
          || !payload(witness.path("payload"), true)) {
        failures.add("LOG_PROJECTION_WITNESS_PAYLOAD");
        continue;
      }
      JsonNode value = witness.path("payload");
      String event = value.path("event").asText();
      if (!nk
          || !"REQUEST".equals(value.path("category").asText())
          || !value.equals(expected.get(event))) {
        failures.add("LOG_PROJECTION_WITNESS_UNEXPECTED");
      }
      if (!found.add(witness.path("stage").asText() + "/" + event)) {
        failures.add("LOG_PROJECTION_WITNESS_DUPLICATE");
      }
    }
    if (nk) {
      for (Map.Entry<String, JsonNode> event : expected.entrySet()) {
        if ("REQUEST".equals(event.getValue().path("category").asText())) {
          for (String stage : STAGES) {
            if (!found.contains(stage + "/" + event.getKey())) {
              failures.add("LOG_PROJECTION_WITNESS_MISSING");
            }
          }
        }
      }
    }
  }

  private static boolean payload(JsonNode value, boolean nk) {
    if (!shape(value, PAYLOAD_FIELDS)) return false;
    for (String field : List.of("operation", "request", "event", "message")) {
      if (!reference(value.path(field))) return false;
    }
    if (!value.path("category").isTextual()
        || !CATEGORIES.contains(value.path("category").asText())
        || !value.path("action").isTextual()) return false;
    boolean request = "REQUEST".equals(value.path("category").asText());
    if (nk && request && !"HTTP_REQUEST_COMPLETED".equals(value.path("action").asText())) {
      return false;
    }
    JsonNode http = value.path("http");
    if (!http.isObject()) return false;
    for (Map.Entry<String, JsonNode> field : http.properties()) {
      if (!HTTP_FIELDS.contains(field.getKey()) || !field.getValue().isValueNode()) return false;
    }
    if (request) {
      if (!http.path("method").isTextual()
          || http.path("method").asText().isBlank()
          || !http.path("path").isTextual()
          || !http.path("path").asText().startsWith("/")
          || http.path("path").asText().contains("?")
          || http.path("path").asText().contains("#")
          || !http.path("status").isIntegralNumber()
          || !http.path("status").canConvertToInt()
          || http.path("status").asInt() < 100
          || http.path("status").asInt() > 599
          || !http.path("elapsedMs").isIntegralNumber()
          || !http.path("elapsedMs").canConvertToLong()
          || http.path("elapsedMs").asLong() < 0
          || http.path("elapsedMs").asLong() > 999_999_999_999L) {
        return false;
      }
    }
    return true;
  }

  private static boolean reference(JsonNode value) {
    return value.isTextual() && value.asText().matches("[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}");
  }

  /** Shared strict schema boundary: no string/fraction coercion or truncating integer conversion. */
  static boolean versionOne(JsonNode value) {
    return value != null
        && value.isIntegralNumber()
        && value.canConvertToInt()
        && value.asInt() == 1;
  }

  private static boolean shape(JsonNode value, Set<String> fields) {
    if (!value.isObject() || value.size() != fields.size()) return false;
    for (String field : fields) if (!value.has(field)) return false;
    return true;
  }
}
