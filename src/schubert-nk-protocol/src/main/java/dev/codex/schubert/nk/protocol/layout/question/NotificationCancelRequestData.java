package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts NTCREQ01. */
public record NotificationCancelRequestData(FieldValue.Numeric notificationId,
    FieldValue.Text operationToken) implements PayloadData {
  public NotificationCancelRequestData {
    Objects.requireNonNull(notificationId, "notificationId");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static NotificationCancelRequestData from(FieldValueSet fields) {
    return new NotificationCancelRequestData(
        TypedFieldValues.requiredNumeric(fields, "Notification ID"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Notification ID", notificationId),
            Map.entry("Operation token", operationToken)));
  }
}
