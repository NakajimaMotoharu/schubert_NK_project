package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts URLREQ01. */
public record UserRoleRequestData(UserId userId,
    UserRole newRole,
    long expectedVersion,
    UUID operationToken) implements PayloadData {
  public UserRoleRequestData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(newRole, "newRole");
    TypedFieldValues.requireUnsignedRange("expectedVersion", expectedVersion, 9);
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserRoleRequestData from(FieldValueSet fields) {
    return new UserRoleRequestData(
        TypedFieldValues.requiredId(fields, "User ID", UserId::new),
        TypedFieldValues.requiredEnum(fields, "New role", UserRole.class),
        TypedFieldValues.requiredLong(fields, "Expected version"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.id(userId)),
            Map.entry("New role", TypedFieldValues.enumValue(newRole)),
            Map.entry("Expected version", TypedFieldValues.numeric(expectedVersion)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "UserRoleRequestData[REDACTED]";
  }
}
