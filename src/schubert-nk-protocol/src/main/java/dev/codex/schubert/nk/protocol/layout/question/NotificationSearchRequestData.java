package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts NTSREQ01. */
public record NotificationSearchRequestData(Optional<String> notificationType,
    Optional<Instant> submittedFrom,
    Optional<Instant> submittedTo,
    long page,
    long pageSize) implements PayloadData {
  public NotificationSearchRequestData {
    Objects.requireNonNull(notificationType, "notificationType");
    Objects.requireNonNull(submittedFrom, "submittedFrom");
    Objects.requireNonNull(submittedTo, "submittedTo");
  }

  public static NotificationSearchRequestData from(FieldValueSet fields) {
    return new NotificationSearchRequestData(
        TypedFieldValues.optionalString(fields, "通知区分"),
        TypedFieldValues.optionalInstant(fields, "受付日時From"),
        TypedFieldValues.optionalInstant(fields, "受付日時To"),
        TypedFieldValues.requiredLong(fields, "Page"),
        TypedFieldValues.requiredLong(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("通知区分", TypedFieldValues.optionalStringValue(notificationType)),
            Map.entry("受付日時From", TypedFieldValues.optionalInstantValue(submittedFrom)),
            Map.entry("受付日時To", TypedFieldValues.optionalInstantValue(submittedTo)),
            Map.entry("Page", TypedFieldValues.numeric(page)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize))));
  }

  @Override
  public String toString() {
    return "NotificationSearchRequestData[REDACTED]";
  }
}
