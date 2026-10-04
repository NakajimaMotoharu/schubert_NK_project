package dev.codex.schubert.nk.web.form;

import java.util.*;
import org.jspecify.annotations.NullMarked;

/** Closed SCR021/023 input only; UI224/236; SS313/314/323; PG-D368/PT-TARGET001..008. */
@NullMarked
final class TargetOperationInput {
  private static final String INVALID = "入力項目を確認してください。";
  private static final Set<String> FIELDS = Set.of("operation", "id", "confirm", "operation_token");
  final long id;
  final UUID token;
  final Map<String, String> issues;
  final Map<String, Object> values;

  private TargetOperationInput(
      long id, UUID token, Map<String, String> issues, Map<String, Object> values) {
    this.id = id;
    this.token = token;
    this.issues = Map.copyOf(issues);
    this.values = Map.copyOf(values);
  }

  static TargetOperationInput bind(
      String operation, long pathId, Map<String, List<String>> parameters) {
    Objects.requireNonNull(operation, "operation");
    Objects.requireNonNull(parameters, "parameters");
    if (!Set.of("CANCEL", "DELETE").contains(operation))
      throw new IllegalArgumentException("unsupported target operation");
    var issues = new LinkedHashMap<String, String>();
    var fields = new LinkedHashMap<String, String>();
    for (String key : parameters.keySet())
      if (key == null || (!FIELDS.contains(key) && !"_csrf".equals(key)))
        issues.put("form", INVALID);
    for (String field : FIELDS) {
      var supplied = parameters.get(field);
      if (supplied == null || supplied.size() != 1 || supplied.getFirst() == null) {
        issues.put(field, INVALID);
        fields.put(field, "");
      } else fields.put(field, supplied.getFirst());
    }
    if (!operation.equals(fields.get("operation"))) issues.put("operation", INVALID);
    String rawId = Objects.requireNonNull(fields.get("id"));
    long id = 0;
    if (rawId.matches("[0-9]{1,12}")) id = Long.parseLong(rawId);
    if (id < 1 || id != pathId) issues.put("id", INVALID);
    boolean confirmed = "true".equals(fields.get("confirm"));
    if (!confirmed) issues.put("confirm", INVALID);
    String text = Objects.requireNonNull(fields.get("operation_token"));
    UUID token = new UUID(0, 0);
    if (text.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))
      token = UUID.fromString(text);
    else issues.put("operation_token", INVALID);
    return new TargetOperationInput(
        id,
        token,
        issues,
        Map.of(
            "operation", operation, "id", pathId, "confirm", confirmed, "operation_token", text));
  }

  void requireValid() {
    if (!issues.isEmpty()) throw new IllegalStateException("invalid target operation form");
  }
}
