package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts NTDRSP01. */
public record NotificationDetailResponseData(FieldValue.Numeric notificationId,
    FieldValue.Text receiptId,
    FieldValue.Text notificationType,
    FieldValue.Text internalState,
    FieldValue.Numeric submittedAt,
    Optional<FieldValue.Text> processingStartedAt,
    Optional<FieldValue.Text> processingCompletedAt,
    Optional<FieldValue.Text> errorAt,
    Optional<FieldValue.Text> cancelledAt,
    FieldValue.Flag questionDeleted,
    Optional<FieldValue.Text> questionText,
    Optional<FieldValue.Text> answerText,
    Optional<FieldValue.Text> errorCode,
    Optional<FieldValue.Text> userFacingError,
    Optional<FieldValue.Text> questionId) implements PayloadData {
  public NotificationDetailResponseData {
    Objects.requireNonNull(notificationId, "notificationId");
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(notificationType, "notificationType");
    Objects.requireNonNull(internalState, "internalState");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(processingStartedAt, "processingStartedAt");
    Objects.requireNonNull(processingCompletedAt, "processingCompletedAt");
    Objects.requireNonNull(errorAt, "errorAt");
    Objects.requireNonNull(cancelledAt, "cancelledAt");
    Objects.requireNonNull(questionDeleted, "questionDeleted");
    Objects.requireNonNull(questionText, "questionText");
    Objects.requireNonNull(answerText, "answerText");
    Objects.requireNonNull(errorCode, "errorCode");
    Objects.requireNonNull(userFacingError, "userFacingError");
    Objects.requireNonNull(questionId, "questionId");
  }

  public static NotificationDetailResponseData from(FieldValueSet fields) {
    return new NotificationDetailResponseData(
        TypedFieldValues.requiredNumeric(fields, "Notification ID"),
        TypedFieldValues.requiredText(fields, "受付ID"),
        TypedFieldValues.requiredText(fields, "通知区分"),
        TypedFieldValues.requiredText(fields, "内部状態"),
        TypedFieldValues.requiredNumeric(fields, "受付日時"),
        TypedFieldValues.optionalText(fields, "処理開始日時"),
        TypedFieldValues.optionalText(fields, "処理完了日時"),
        TypedFieldValues.optionalText(fields, "Error日時"),
        TypedFieldValues.optionalText(fields, "取消日時"),
        TypedFieldValues.requiredFlag(fields, "質問削除済み"),
        TypedFieldValues.optionalText(fields, "質問本文"),
        TypedFieldValues.optionalText(fields, "回答本文"),
        TypedFieldValues.optionalText(fields, "Error code"),
        TypedFieldValues.optionalText(fields, "利用者向けerror"),
        TypedFieldValues.optionalText(fields, "Question ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Notification ID", notificationId),
            Map.entry("受付ID", receiptId),
            Map.entry("通知区分", notificationType),
            Map.entry("内部状態", internalState),
            Map.entry("受付日時", submittedAt),
            Map.entry("処理開始日時", TypedFieldValues.orUnset(processingStartedAt)),
            Map.entry("処理完了日時", TypedFieldValues.orUnset(processingCompletedAt)),
            Map.entry("Error日時", TypedFieldValues.orUnset(errorAt)),
            Map.entry("取消日時", TypedFieldValues.orUnset(cancelledAt)),
            Map.entry("質問削除済み", questionDeleted),
            Map.entry("質問本文", TypedFieldValues.orUnset(questionText)),
            Map.entry("回答本文", TypedFieldValues.orUnset(answerText)),
            Map.entry("Error code", TypedFieldValues.orUnset(errorCode)),
            Map.entry("利用者向けerror", TypedFieldValues.orUnset(userFacingError)),
            Map.entry("Question ID", TypedFieldValues.orUnset(questionId))));
  }
}
