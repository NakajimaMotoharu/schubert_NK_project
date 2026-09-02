package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QDLREQ01. */
public record QuestionDeleteRequestData(FieldValue.Numeric questionId,
    FieldValue.Text operationToken) implements PayloadData {
  public QuestionDeleteRequestData {
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static QuestionDeleteRequestData from(FieldValueSet fields) {
    return new QuestionDeleteRequestData(
        TypedFieldValues.requiredNumeric(fields, "Question ID"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", questionId),
            Map.entry("Operation token", operationToken)));
  }
}
