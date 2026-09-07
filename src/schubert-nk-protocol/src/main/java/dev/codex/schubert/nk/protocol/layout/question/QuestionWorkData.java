package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AsyncJobId;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QWKREQ01. */
public record QuestionWorkData(String receiptId, QuestionId questionId, AsyncJobId asyncJobId)
    implements PayloadData {
  public QuestionWorkData {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(asyncJobId, "asyncJobId");
  }

  public static QuestionWorkData from(FieldValueSet fields) {
    return new QuestionWorkData(
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredId(fields, "Question ID", QuestionId::new),
        TypedFieldValues.requiredId(fields, "Async job ID", AsyncJobId::new));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("受付ID", TypedFieldValues.text(receiptId)),
            Map.entry("Question ID", TypedFieldValues.id(questionId)),
            Map.entry("Async job ID", TypedFieldValues.id(asyncJobId))));
  }

  @Override
  public String toString() {
    return "QuestionWorkData[REDACTED]";
  }
}
