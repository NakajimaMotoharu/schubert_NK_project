package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts USTREQ01. */
public record UserStatusRequestData(FieldValue.Numeric userId,
    FieldValue.Flag enabled,
    FieldValue.Numeric expectedVersion,
    FieldValue.Text operationToken) implements PayloadData {
  public UserStatusRequestData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(enabled, "enabled");
    Objects.requireNonNull(expectedVersion, "expectedVersion");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserStatusRequestData from(FieldValueSet fields) {
    return new UserStatusRequestData(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredFlag(fields, "Enabled"),
        TypedFieldValues.requiredNumeric(fields, "Expected version"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", userId),
            Map.entry("Enabled", enabled),
            Map.entry("Expected version", expectedVersion),
            Map.entry("Operation token", operationToken)));
  }
}
