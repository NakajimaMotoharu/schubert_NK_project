package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts USTREQ01. */
public record UserStatusRequestData(long userId,
    boolean enabled,
    long expectedVersion,
    UUID operationToken) implements PayloadData {
  public UserStatusRequestData {
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserStatusRequestData from(FieldValueSet fields) {
    return new UserStatusRequestData(
        TypedFieldValues.requiredLong(fields, "User ID"),
        TypedFieldValues.requiredBoolean(fields, "Enabled"),
        TypedFieldValues.requiredLong(fields, "Expected version"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.numeric(userId)),
            Map.entry("Enabled", TypedFieldValues.flag(enabled)),
            Map.entry("Expected version", TypedFieldValues.numeric(expectedVersion)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "UserStatusRequestData[REDACTED]";
  }
}
