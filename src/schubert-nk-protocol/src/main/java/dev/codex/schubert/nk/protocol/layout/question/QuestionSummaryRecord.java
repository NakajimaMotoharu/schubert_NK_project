package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts QSSRSP01. */
public record QuestionSummaryRecord(FieldValue.Numeric questionId,
    FieldValue.Text receiptId,
    FieldValue.Text username,
    FieldValue.Text questionSummary,
    FieldValue.Text answerState,
    FieldValue.Numeric submittedAt,
    Optional<FieldValue.Text> answeredAt) implements PayloadRecord {
  public QuestionSummaryRecord {
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(questionSummary, "questionSummary");
    Objects.requireNonNull(answerState, "answerState");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(answeredAt, "answeredAt");
  }

  public static QuestionSummaryRecord from(FieldValueSet fields) {
    return new QuestionSummaryRecord(
        TypedFieldValues.requiredNumeric(fields, "Question ID"),
        TypedFieldValues.requiredText(fields, "受付ID"),
        TypedFieldValues.requiredText(fields, "Username"),
        TypedFieldValues.requiredText(fields, "質問概要"),
        TypedFieldValues.requiredText(fields, "回答状態"),
        TypedFieldValues.requiredNumeric(fields, "受付日時"),
        TypedFieldValues.optionalText(fields, "回答日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", questionId),
            Map.entry("受付ID", receiptId),
            Map.entry("Username", username),
            Map.entry("質問概要", questionSummary),
            Map.entry("回答状態", answerState),
            Map.entry("受付日時", submittedAt),
            Map.entry("回答日時", TypedFieldValues.orUnset(answeredAt))));
  }
}
