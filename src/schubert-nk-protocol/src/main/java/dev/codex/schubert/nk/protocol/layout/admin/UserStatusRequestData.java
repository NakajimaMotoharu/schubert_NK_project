package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts USTREQ01. */
public record UserStatusRequestData(UserId userId,
    boolean enabled,
    long expectedVersion,
    UUID operationToken) implements PayloadData {
  public UserStatusRequestData {
    Objects.requireNonNull(userId, "userId");
    TypedFieldValues.requireUnsignedRange("expectedVersion", expectedVersion, 9);
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserStatusRequestData from(FieldValueSet fields) {
    return new UserStatusRequestData(
        TypedFieldValues.requiredId(fields, "User ID", UserId::new),
        TypedFieldValues.requiredBoolean(fields, "Enabled"),
        TypedFieldValues.requiredLong(fields, "Expected version"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.id(userId)),
            Map.entry("Enabled", TypedFieldValues.flag(enabled)),
            Map.entry("Expected version", TypedFieldValues.numeric(expectedVersion)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "UserStatusRequestData[REDACTED]";
  }
}
