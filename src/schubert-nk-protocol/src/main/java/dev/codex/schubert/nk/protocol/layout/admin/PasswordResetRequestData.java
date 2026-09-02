package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts UPWREQ01. */
public record PasswordResetRequestData(FieldValue.Numeric userId,
    FieldValue.Text newPassword,
    FieldValue.Numeric expectedVersion,
    FieldValue.Text operationToken) implements PayloadData {
  public PasswordResetRequestData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(newPassword, "newPassword");
    Objects.requireNonNull(expectedVersion, "expectedVersion");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static PasswordResetRequestData from(FieldValueSet fields) {
    return new PasswordResetRequestData(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredText(fields, "New Password"),
        TypedFieldValues.requiredNumeric(fields, "Expected version"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", userId),
            Map.entry("New Password", newPassword),
            Map.entry("Expected version", expectedVersion),
            Map.entry("Operation token", operationToken)));
  }
}
