package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts NTSREQ01. */
public record NotificationSearchRequestData(Optional<FieldValue.Text> notificationType,
    Optional<FieldValue.Text> submittedFrom,
    Optional<FieldValue.Text> submittedTo,
    FieldValue.Numeric page,
    FieldValue.Numeric pageSize) implements PayloadData {
  public NotificationSearchRequestData {
    Objects.requireNonNull(notificationType, "notificationType");
    Objects.requireNonNull(submittedFrom, "submittedFrom");
    Objects.requireNonNull(submittedTo, "submittedTo");
    Objects.requireNonNull(page, "page");
    Objects.requireNonNull(pageSize, "pageSize");
  }

  public static NotificationSearchRequestData from(FieldValueSet fields) {
    return new NotificationSearchRequestData(
        TypedFieldValues.optionalText(fields, "通知区分"),
        TypedFieldValues.optionalText(fields, "受付日時From"),
        TypedFieldValues.optionalText(fields, "受付日時To"),
        TypedFieldValues.requiredNumeric(fields, "Page"),
        TypedFieldValues.requiredNumeric(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("通知区分", TypedFieldValues.orUnset(notificationType)),
            Map.entry("受付日時From", TypedFieldValues.orUnset(submittedFrom)),
            Map.entry("受付日時To", TypedFieldValues.orUnset(submittedTo)),
            Map.entry("Page", page),
            Map.entry("Page size", pageSize)));
  }
}
