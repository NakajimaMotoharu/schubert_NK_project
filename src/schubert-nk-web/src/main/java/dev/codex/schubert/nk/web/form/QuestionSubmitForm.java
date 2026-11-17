package dev.codex.schubert.nk.web.form;

import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitRequestData;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/** SCR018/QST001/UI224,236/SS313,323; PG-D351/PT-QST-FORM001..008. Request scope only. */
@NullMarked
public final class QuestionSubmitForm implements AutoCloseable {
  private static final int SINGLE_PARAMETER_VALUE_COUNT = 1;

  private static final java.lang.String LITERAL_QUESTION = "question";

  private static final Set<String> FIELDS = Set.of(LITERAL_QUESTION, "operation_token");
  private static final String INVALID = "入力項目を確認してください。";
  private final char[] question;
  private final UUID retainedOperationToken;
  private final Map<String, String> issues;
  private boolean closed;

  private QuestionSubmitForm(String question, UUID token, Map<String, String> issues) {
    retainedOperationToken = token;
    this.issues = Map.copyOf(issues);
    this.question = question.toCharArray();
  }

  /** The security chain owns CSRF; the caller separately verifies token purpose/session. */
  public static QuestionSubmitForm bind(Map<String, List<String>> parameters) {
    Objects.requireNonNull(parameters, "parameters");
    var snapshot = new HashMap<String, List<String>>();
    parameters.forEach(
        (key, value) -> snapshot.put(Objects.requireNonNull(key, "name"), List.copyOf(value)));
    var issues = new HashMap<String, String>();
    for (var entry : snapshot.entrySet()) {
      if (!FIELDS.contains(entry.getKey()) && !entry.getKey().equals("_csrf"))
        issues.put("form", INVALID);
      if (entry.getValue().size() != SINGLE_PARAMETER_VALUE_COUNT) issues.put("form", INVALID);
    }
    var values = new HashMap<String, String>();
    for (String name : FIELDS) {
      List<String> input = snapshot.getOrDefault(name, List.of());
      if (input.size() == SINGLE_PARAMETER_VALUE_COUNT) values.put(name, input.getFirst());
      else {
        values.put(name, "");
        issues.put(name, INVALID);
      }
    }
    String question =
        Normalizer.normalize(
            Objects.requireNonNull(values.get(LITERAL_QUESTION)), Normalizer.Form.NFC);
    // Invalid Unicode/control is not redisplayed; do not trim it into an accepted question.
    if (question.codePoints().anyMatch(QuestionSubmitForm::invalidCharacter)) {
      issues.put(LITERAL_QUESTION, INVALID);
      question = "";
    }
    byte[] encoded = question.getBytes(StandardCharsets.UTF_8);
    int byteLength = encoded.length;
    // Consume and wipe this local byte buffer before any later validation (BUG3196).
    Arrays.fill(encoded, (byte) 0);
    if (byteLength < 1 || byteLength > 4096 || question.endsWith(" "))
      issues.put(LITERAL_QUESTION, INVALID);
    UUID token = new UUID(0, 0);
    String text = Objects.requireNonNull(values.get("operation_token"));
    if (!text.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"))
      issues.put("operation_token", INVALID);
    else token = UUID.fromString(text);
    return new QuestionSubmitForm(question, token, issues);
  }

  private static boolean invalidCharacter(int value) {
    return Character.isISOControl(value)
        || (value >= Character.MIN_SURROGATE && value <= Character.MAX_SURROGATE);
  }

  public boolean isValid() {
    return issues.isEmpty();
  }

  public Map<String, String> getIssues() {
    return issues;
  }

  /** Request-scoped hidden field, not an authorization or API result proof. */
  public UUID operationToken() {
    ensureOpen();
    return retainedOperationToken;
  }

  /** Only the caller's request/template receives this body copy; never put it in session/flash. */
  public Map<String, Object> displayValues() {
    ensureOpen();
    return Map.of(LITERAL_QUESTION, new String(question));
  }

  /** The returned DTO has its own lifetime; this form is not an authorization grant. */
  public QuestionSubmitRequestData toRequest() {
    ensureOpen();
    if (!isValid()) throw new IllegalArgumentException("invalid question submit form");
    return new QuestionSubmitRequestData(new String(question), retainedOperationToken);
  }

  private void ensureOpen() {
    if (closed) throw new IllegalStateException("question submit form is closed");
  }

  @Override
  public void close() {
    Arrays.fill(question, '\0');
    closed = true;
  }

  @Override
  public String toString() {
    return "QuestionSubmitForm[REDACTED]";
  }
}
