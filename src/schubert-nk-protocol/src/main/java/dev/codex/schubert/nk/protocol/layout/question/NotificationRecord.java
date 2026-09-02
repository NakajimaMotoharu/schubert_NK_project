package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts NTSRSP01. */
public record NotificationRecord(FieldValue.Numeric notificationId,
    FieldValue.Text receiptId,
    FieldValue.Text notificationType,
    FieldValue.Text internalState,
    FieldValue.Numeric submittedAt,
    FieldValue.Numeric lastUpdatedAt,
    FieldValue.Text questionSummary,
    FieldValue.Flag questionDeleted) implements PayloadRecord {
  public NotificationRecord {
    Objects.requireNonNull(notificationId, "notificationId");
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(notificationType, "notificationType");
    Objects.requireNonNull(internalState, "internalState");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(lastUpdatedAt, "lastUpdatedAt");
    Objects.requireNonNull(questionSummary, "questionSummary");
    Objects.requireNonNull(questionDeleted, "questionDeleted");
  }

  public static NotificationRecord from(FieldValueSet fields) {
    return new NotificationRecord(
        TypedFieldValues.requiredNumeric(fields, "Notification ID"),
        TypedFieldValues.requiredText(fields, "受付ID"),
        TypedFieldValues.requiredText(fields, "通知区分"),
        TypedFieldValues.requiredText(fields, "内部状態"),
        TypedFieldValues.requiredNumeric(fields, "受付日時"),
        TypedFieldValues.requiredNumeric(fields, "最終更新日時"),
        TypedFieldValues.requiredText(fields, "質問概要"),
        TypedFieldValues.requiredFlag(fields, "質問削除済み"));
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
            Map.entry("最終更新日時", lastUpdatedAt),
            Map.entry("質問概要", questionSummary),
            Map.entry("質問削除済み", questionDeleted)));
  }
}
