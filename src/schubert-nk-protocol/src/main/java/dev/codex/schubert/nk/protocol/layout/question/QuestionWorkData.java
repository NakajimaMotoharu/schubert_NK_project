package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QWKREQ01. */
public record QuestionWorkData(FieldValue.Text receiptId,
    FieldValue.Numeric questionId,
    FieldValue.Numeric asyncJobId) implements PayloadData {
  public QuestionWorkData {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(asyncJobId, "asyncJobId");
  }

  public static QuestionWorkData from(FieldValueSet fields) {
    return new QuestionWorkData(
        TypedFieldValues.requiredText(fields, "受付ID"),
        TypedFieldValues.requiredNumeric(fields, "Question ID"),
        TypedFieldValues.requiredNumeric(fields, "Async job ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("受付ID", receiptId),
            Map.entry("Question ID", questionId),
            Map.entry("Async job ID", asyncJobId)));
  }
}
