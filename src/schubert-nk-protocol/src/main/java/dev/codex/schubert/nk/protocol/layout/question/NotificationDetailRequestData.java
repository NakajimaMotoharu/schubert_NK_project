package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts NTDREQ01. */
public record NotificationDetailRequestData(FieldValue.Numeric notificationId) implements PayloadData {
  public NotificationDetailRequestData {
    Objects.requireNonNull(notificationId, "notificationId");
  }

  public static NotificationDetailRequestData from(FieldValueSet fields) {
    return new NotificationDetailRequestData(
        TypedFieldValues.requiredNumeric(fields, "Notification ID"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Notification ID", notificationId)));
  }
}
