package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts UPWREQ01. */
public record PasswordResetRequestData(long userId,
    String newPassword,
    long expectedVersion,
    UUID operationToken) implements PayloadData {
  public PasswordResetRequestData {
    Objects.requireNonNull(newPassword, "newPassword");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static PasswordResetRequestData from(FieldValueSet fields) {
    return new PasswordResetRequestData(
        TypedFieldValues.requiredLong(fields, "User ID"),
        TypedFieldValues.requiredString(fields, "New Password"),
        TypedFieldValues.requiredLong(fields, "Expected version"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.numeric(userId)),
            Map.entry("New Password", TypedFieldValues.text(newPassword)),
            Map.entry("Expected version", TypedFieldValues.numeric(expectedVersion)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "PasswordResetRequestData[REDACTED]";
  }
}
