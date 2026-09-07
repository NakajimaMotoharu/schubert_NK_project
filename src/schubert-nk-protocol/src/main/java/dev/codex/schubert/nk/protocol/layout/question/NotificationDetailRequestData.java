package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts NTDREQ01. */
public record NotificationDetailRequestData(NotificationId notificationId) implements PayloadData {
  public NotificationDetailRequestData {
    Objects.requireNonNull(notificationId, "notificationId");
  }

  public static NotificationDetailRequestData from(FieldValueSet fields) {
    return new NotificationDetailRequestData(
        TypedFieldValues.requiredId(fields, "Notification ID", NotificationId::new));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(Map.entry("Notification ID", TypedFieldValues.id(notificationId))));
  }

  @Override
  public String toString() {
    return "NotificationDetailRequestData[REDACTED]";
  }
}
