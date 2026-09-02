package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QSBRSP01. */
public record QuestionSubmitResponseData(String receiptId,
    long questionId,
    Instant submittedAt) implements PayloadData {
  public QuestionSubmitResponseData {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(submittedAt, "submittedAt");
  }

  public static QuestionSubmitResponseData from(FieldValueSet fields) {
    return new QuestionSubmitResponseData(
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredLong(fields, "Question ID"),
        TypedFieldValues.requiredInstant(fields, "受付日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("受付ID", TypedFieldValues.text(receiptId)),
            Map.entry("Question ID", TypedFieldValues.numeric(questionId)),
            Map.entry("受付日時", TypedFieldValues.instant(submittedAt))));
  }

  @Override
  public String toString() {
    return "QuestionSubmitResponseData[REDACTED]";
  }
}
