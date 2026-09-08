package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts QSBREQ01. */
public record QuestionSubmitRequestData(String questionText, UUID operationToken)
    implements PayloadData {
  public QuestionSubmitRequestData {
    Objects.requireNonNull(questionText, "questionText");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static QuestionSubmitRequestData from(FieldValueSet fields) {
    return new QuestionSubmitRequestData(
        TypedFieldValues.requiredString(fields, "質問本文"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("質問本文", TypedFieldValues.text(questionText)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "QuestionSubmitRequestData[REDACTED]";
  }
}
