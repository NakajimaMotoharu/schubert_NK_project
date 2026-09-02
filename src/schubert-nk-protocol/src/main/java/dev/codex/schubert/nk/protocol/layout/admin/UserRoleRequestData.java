package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts URLREQ01. */
public record UserRoleRequestData(FieldValue.Numeric userId,
    FieldValue.Text newRole,
    FieldValue.Numeric expectedVersion,
    FieldValue.Text operationToken) implements PayloadData {
  public UserRoleRequestData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(newRole, "newRole");
    Objects.requireNonNull(expectedVersion, "expectedVersion");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserRoleRequestData from(FieldValueSet fields) {
    return new UserRoleRequestData(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredText(fields, "New role"),
        TypedFieldValues.requiredNumeric(fields, "Expected version"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", userId),
            Map.entry("New role", newRole),
            Map.entry("Expected version", expectedVersion),
            Map.entry("Operation token", operationToken)));
  }
}
