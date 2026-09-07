package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts QDLREQ01. */
public record QuestionDeleteRequestData(QuestionId questionId, UUID operationToken)
    implements PayloadData {
  public QuestionDeleteRequestData {
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static QuestionDeleteRequestData from(FieldValueSet fields) {
    return new QuestionDeleteRequestData(
        TypedFieldValues.requiredId(fields, "Question ID", QuestionId::new),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", TypedFieldValues.id(questionId)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "QuestionDeleteRequestData[REDACTED]";
  }
}
