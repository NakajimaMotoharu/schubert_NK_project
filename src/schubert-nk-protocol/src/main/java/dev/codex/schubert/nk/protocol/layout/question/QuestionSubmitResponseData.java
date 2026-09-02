package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts QSBRSP01. */
public record QuestionSubmitResponseData(FieldValue.Text receiptId,
    FieldValue.Numeric questionId,
    FieldValue.Numeric submittedAt) implements PayloadData {
  public QuestionSubmitResponseData {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(submittedAt, "submittedAt");
  }

  public static QuestionSubmitResponseData from(FieldValueSet fields) {
    return new QuestionSubmitResponseData(
        TypedFieldValues.requiredText(fields, "受付ID"),
        TypedFieldValues.requiredNumeric(fields, "Question ID"),
        TypedFieldValues.requiredNumeric(fields, "受付日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("受付ID", receiptId),
            Map.entry("Question ID", questionId),
            Map.entry("受付日時", submittedAt)));
  }
}
