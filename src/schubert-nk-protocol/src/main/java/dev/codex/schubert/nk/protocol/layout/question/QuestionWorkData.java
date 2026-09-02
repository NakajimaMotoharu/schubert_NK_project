package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QWKREQ01. */
public record QuestionWorkData(String receiptId,
    long questionId,
    long asyncJobId) implements PayloadData {
  public QuestionWorkData {
    Objects.requireNonNull(receiptId, "receiptId");
  }

  public static QuestionWorkData from(FieldValueSet fields) {
    return new QuestionWorkData(
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredLong(fields, "Question ID"),
        TypedFieldValues.requiredLong(fields, "Async job ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("受付ID", TypedFieldValues.text(receiptId)),
            Map.entry("Question ID", TypedFieldValues.numeric(questionId)),
            Map.entry("Async job ID", TypedFieldValues.numeric(asyncJobId))));
  }

  @Override
  public String toString() {
    return "QuestionWorkData[REDACTED]";
  }
}
