package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts NTCREQ01. */
public record NotificationCancelRequestData(NotificationId notificationId, UUID operationToken)
    implements PayloadData {
  public NotificationCancelRequestData {
    Objects.requireNonNull(notificationId, "notificationId");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static NotificationCancelRequestData from(FieldValueSet fields) {
    return new NotificationCancelRequestData(
        TypedFieldValues.requiredId(fields, "Notification ID", NotificationId::new),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Notification ID", TypedFieldValues.id(notificationId)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "NotificationCancelRequestData[REDACTED]";
  }
}
