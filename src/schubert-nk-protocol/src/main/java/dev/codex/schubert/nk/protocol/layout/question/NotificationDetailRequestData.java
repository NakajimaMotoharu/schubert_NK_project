package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;

/** Generated named wire record. Trace: SS 323; layouts NTDREQ01. */
public record NotificationDetailRequestData(long notificationId) implements PayloadData {
  public NotificationDetailRequestData {
  }

  public static NotificationDetailRequestData from(FieldValueSet fields) {
    return new NotificationDetailRequestData(
        TypedFieldValues.requiredLong(fields, "Notification ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Notification ID", TypedFieldValues.numeric(notificationId))));
  }

  @Override
  public String toString() {
    return "NotificationDetailRequestData[REDACTED]";
  }
}
