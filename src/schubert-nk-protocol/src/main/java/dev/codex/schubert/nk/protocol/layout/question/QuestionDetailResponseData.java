package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts QSDRSP01. */
public record QuestionDetailResponseData(QuestionId questionId,
    String receiptId,
    String username,
    AnswerState answerState,
    String questionText,
    Optional<String> answerText,
    Instant submittedAt,
    Optional<Instant> answeredAt) implements PayloadData {
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
        TypedFieldValues.requiredId(fields, "Question ID", QuestionId::new),
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredEnum(fields, "回答状態", AnswerState.class),
        TypedFieldValues.requiredString(fields, "質問本文"),
        TypedFieldValues.optionalString(fields, "回答本文"),
        TypedFieldValues.requiredInstant(fields, "受付日時"),
        TypedFieldValues.optionalInstant(fields, "回答日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", TypedFieldValues.id(questionId)),
            Map.entry("受付ID", TypedFieldValues.text(receiptId)),
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("回答状態", TypedFieldValues.enumValue(answerState)),
            Map.entry("質問本文", TypedFieldValues.text(questionText)),
            Map.entry("回答本文", TypedFieldValues.optionalStringValue(answerText)),
            Map.entry("受付日時", TypedFieldValues.instant(submittedAt)),
            Map.entry("回答日時", TypedFieldValues.optionalInstantValue(answeredAt))));
  }

  @Override
  public String toString() {
    return "QuestionDetailResponseData[REDACTED]";
  }
}
