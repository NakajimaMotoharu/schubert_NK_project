package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts QSSRSP01. */
public record QuestionSummaryRecord(long questionId,
    String receiptId,
    String username,
    String questionSummary,
    String answerState,
    Instant submittedAt,
    Optional<Instant> answeredAt) implements PayloadRecord {
  public QuestionSummaryRecord {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(questionSummary, "questionSummary");
    Objects.requireNonNull(answerState, "answerState");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(answeredAt, "answeredAt");
  }

  public static QuestionSummaryRecord from(FieldValueSet fields) {
    return new QuestionSummaryRecord(
        TypedFieldValues.requiredLong(fields, "Question ID"),
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredString(fields, "質問概要"),
        TypedFieldValues.requiredString(fields, "回答状態"),
        TypedFieldValues.requiredInstant(fields, "受付日時"),
        TypedFieldValues.optionalInstant(fields, "回答日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Question ID", TypedFieldValues.numeric(questionId)),
            Map.entry("受付ID", TypedFieldValues.text(receiptId)),
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("質問概要", TypedFieldValues.text(questionSummary)),
            Map.entry("回答状態", TypedFieldValues.text(answerState)),
            Map.entry("受付日時", TypedFieldValues.instant(submittedAt)),
            Map.entry("回答日時", TypedFieldValues.optionalInstantValue(answeredAt))));
  }

  @Override
  public String toString() {
    return "QuestionSummaryRecord[REDACTED]";
  }
}
