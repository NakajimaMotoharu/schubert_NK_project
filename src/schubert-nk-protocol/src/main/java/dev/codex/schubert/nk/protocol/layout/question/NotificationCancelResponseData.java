package dev.codex.schubert.nk.protocol.layout.question;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts NTCRSP01. */
public record NotificationCancelResponseData(
    Optional<NotificationState> updatedState, Optional<Instant> cancelledAt)
    implements PayloadData {
  public NotificationCancelResponseData {
    Objects.requireNonNull(updatedState, "updatedState");
    Objects.requireNonNull(cancelledAt, "cancelledAt");
  }

  public static NotificationCancelResponseData from(FieldValueSet fields) {
    return new NotificationCancelResponseData(
        TypedFieldValues.optionalEnum(fields, "更新後状態", NotificationState.class),
        TypedFieldValues.optionalInstant(fields, "取消日時"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("更新後状態", TypedFieldValues.optionalEnumValue(updatedState)),
            Map.entry("取消日時", TypedFieldValues.optionalInstantValue(cancelledAt))));
  }

  @Override
  public String toString() {
    return "NotificationCancelResponseData[REDACTED]";
  }
}
