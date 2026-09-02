package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts QSDRSP01. */
public record QuestionDetailResponseData(FieldValue.Numeric questionId,
    FieldValue.Text receiptId,
    FieldValue.Text username,
    FieldValue.Text answerState,
    FieldValue.Text questionText,
    Optional<FieldValue.Text> answerText,
    FieldValue.Numeric submittedAt,
    Optional<FieldValue.Text> answeredAt) implements PayloadData {
  public QuestionDetailResponseData {
    Objects.requireNonNull(questionId, "questionId");
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(answerState, "answerState");
    Objects.requireNonNull(questionText, "questionText");
    Objects.requireNonNull(answerText, "answerText");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(answeredAt, "answeredAt");
  }

  public static QuestionDetailResponseData from(FieldValueSet fields) {
    return new QuestionDetailResponseData(
        TypedFieldValues.requiredNumeric(fields, "Question ID"),
        TypedFieldValues.requiredText(fields, "受付ID"),
        TypedFieldValues.requiredText(fields, "Username"),
        TypedFieldValues.requiredText(fields, "回答状態"),
        TypedFieldValues.requiredText(fields, "質問本文"),
        TypedFieldValues.optionalText(fields, "回答本文"),
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
            Map.entry("回答状態", answerState),
            Map.entry("質問本文", questionText),
            Map.entry("回答本文", TypedFieldValues.orUnset(answerText)),
            Map.entry("受付日時", submittedAt),
            Map.entry("回答日時", TypedFieldValues.orUnset(answeredAt))));
  }
}
