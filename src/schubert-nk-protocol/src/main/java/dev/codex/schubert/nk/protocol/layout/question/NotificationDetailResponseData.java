package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts NTDRSP01. */
public record NotificationDetailResponseData(long notificationId,
    String receiptId,
    String notificationType,
    String internalState,
    Instant submittedAt,
    Optional<Instant> processingStartedAt,
    Optional<Instant> processingCompletedAt,
    Optional<Instant> errorAt,
    Optional<Instant> cancelledAt,
    boolean questionDeleted,
    Optional<String> questionText,
    Optional<String> answerText,
    Optional<String> errorCode,
    Optional<String> userFacingError,
    Optional<String> questionId) implements PayloadData {
  public NotificationDetailResponseData {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(notificationType, "notificationType");
    Objects.requireNonNull(internalState, "internalState");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(processingStartedAt, "processingStartedAt");
    Objects.requireNonNull(processingCompletedAt, "processingCompletedAt");
    Objects.requireNonNull(errorAt, "errorAt");
    Objects.requireNonNull(cancelledAt, "cancelledAt");
    Objects.requireNonNull(questionText, "questionText");
    Objects.requireNonNull(answerText, "answerText");
    Objects.requireNonNull(errorCode, "errorCode");
    Objects.requireNonNull(userFacingError, "userFacingError");
    Objects.requireNonNull(questionId, "questionId");
  }

  public static NotificationDetailResponseData from(FieldValueSet fields) {
    return new NotificationDetailResponseData(
        TypedFieldValues.requiredLong(fields, "Notification ID"),
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredString(fields, "通知区分"),
        TypedFieldValues.requiredString(fields, "内部状態"),
        TypedFieldValues.requiredInstant(fields, "受付日時"),
        TypedFieldValues.optionalInstant(fields, "処理開始日時"),
        TypedFieldValues.optionalInstant(fields, "処理完了日時"),
        TypedFieldValues.optionalInstant(fields, "Error日時"),
        TypedFieldValues.optionalInstant(fields, "取消日時"),
        TypedFieldValues.requiredBoolean(fields, "質問削除済み"),
        TypedFieldValues.optionalString(fields, "質問本文"),
        TypedFieldValues.optionalString(fields, "回答本文"),
        TypedFieldValues.optionalString(fields, "Error code"),
        TypedFieldValues.optionalString(fields, "利用者向けerror"),
        TypedFieldValues.optionalString(fields, "Question ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Notification ID", TypedFieldValues.numeric(notificationId)),
            Map.entry("受付ID", TypedFieldValues.text(receiptId)),
            Map.entry("通知区分", TypedFieldValues.text(notificationType)),
            Map.entry("内部状態", TypedFieldValues.text(internalState)),
            Map.entry("受付日時", TypedFieldValues.instant(submittedAt)),
            Map.entry("処理開始日時", TypedFieldValues.optionalInstantValue(processingStartedAt)),
            Map.entry("処理完了日時", TypedFieldValues.optionalInstantValue(processingCompletedAt)),
            Map.entry("Error日時", TypedFieldValues.optionalInstantValue(errorAt)),
            Map.entry("取消日時", TypedFieldValues.optionalInstantValue(cancelledAt)),
            Map.entry("質問削除済み", TypedFieldValues.flag(questionDeleted)),
            Map.entry("質問本文", TypedFieldValues.optionalStringValue(questionText)),
            Map.entry("回答本文", TypedFieldValues.optionalStringValue(answerText)),
            Map.entry("Error code", TypedFieldValues.optionalStringValue(errorCode)),
            Map.entry("利用者向けerror", TypedFieldValues.optionalStringValue(userFacingError)),
            Map.entry("Question ID", TypedFieldValues.optionalStringValue(questionId))));
  }

  @Override
  public String toString() {
    return "NotificationDetailResponseData[REDACTED]";
  }
}
