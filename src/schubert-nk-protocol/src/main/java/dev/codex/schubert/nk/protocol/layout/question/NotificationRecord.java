package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts NTSRSP01. */
public record NotificationRecord(long notificationId,
    String receiptId,
    String notificationType,
    String internalState,
    Instant submittedAt,
    Instant lastUpdatedAt,
    String questionSummary,
    boolean questionDeleted) implements PayloadRecord {
  public NotificationRecord {
    Objects.requireNonNull(receiptId, "receiptId");
    Objects.requireNonNull(notificationType, "notificationType");
    Objects.requireNonNull(internalState, "internalState");
    Objects.requireNonNull(submittedAt, "submittedAt");
    Objects.requireNonNull(lastUpdatedAt, "lastUpdatedAt");
    Objects.requireNonNull(questionSummary, "questionSummary");
  }

  public static NotificationRecord from(FieldValueSet fields) {
    return new NotificationRecord(
        TypedFieldValues.requiredLong(fields, "Notification ID"),
        TypedFieldValues.requiredString(fields, "受付ID"),
        TypedFieldValues.requiredString(fields, "通知区分"),
        TypedFieldValues.requiredString(fields, "内部状態"),
        TypedFieldValues.requiredInstant(fields, "受付日時"),
        TypedFieldValues.requiredInstant(fields, "最終更新日時"),
        TypedFieldValues.requiredString(fields, "質問概要"),
        TypedFieldValues.requiredBoolean(fields, "質問削除済み"));
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
            Map.entry("最終更新日時", TypedFieldValues.instant(lastUpdatedAt)),
            Map.entry("質問概要", TypedFieldValues.text(questionSummary)),
            Map.entry("質問削除済み", TypedFieldValues.flag(questionDeleted))));
  }

  @Override
  public String toString() {
    return "NotificationRecord[REDACTED]";
  }
}
