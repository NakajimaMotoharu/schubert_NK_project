package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts URLREQ01. */
public record UserRoleRequestData(long userId,
    String newRole,
    long expectedVersion,
    UUID operationToken) implements PayloadData {
  public UserRoleRequestData {
    Objects.requireNonNull(newRole, "newRole");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserRoleRequestData from(FieldValueSet fields) {
    return new UserRoleRequestData(
        TypedFieldValues.requiredLong(fields, "User ID"),
        TypedFieldValues.requiredString(fields, "New role"),
        TypedFieldValues.requiredLong(fields, "Expected version"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.numeric(userId)),
            Map.entry("New role", TypedFieldValues.text(newRole)),
            Map.entry("Expected version", TypedFieldValues.numeric(expectedVersion)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "UserRoleRequestData[REDACTED]";
  }
}
