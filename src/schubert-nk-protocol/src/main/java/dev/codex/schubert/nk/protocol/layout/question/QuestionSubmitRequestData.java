package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QSBREQ01. */
public record QuestionSubmitRequestData(FieldValue.Text questionText,
    FieldValue.Text operationToken) implements PayloadData {
  public QuestionSubmitRequestData {
    Objects.requireNonNull(questionText, "questionText");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static QuestionSubmitRequestData from(FieldValueSet fields) {
    return new QuestionSubmitRequestData(
        TypedFieldValues.requiredText(fields, "質問本文"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("質問本文", questionText),
            Map.entry("Operation token", operationToken)));
  }
}
