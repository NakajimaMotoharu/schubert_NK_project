package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;

/** Generated named wire record. Trace: SS 323; layouts UCRREQ01. */
public record UserCreateRequestData(String username,
    String initialPassword,
    String role,
    boolean enabled,
    UUID operationToken) implements PayloadData {
  public UserCreateRequestData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(initialPassword, "initialPassword");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserCreateRequestData from(FieldValueSet fields) {
    return new UserCreateRequestData(
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredString(fields, "Initial Password"),
        TypedFieldValues.requiredString(fields, "Role"),
        TypedFieldValues.requiredBoolean(fields, "Enabled"),
        TypedFieldValues.requiredUuid(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("Initial Password", TypedFieldValues.text(initialPassword)),
            Map.entry("Role", TypedFieldValues.text(role)),
            Map.entry("Enabled", TypedFieldValues.flag(enabled)),
            Map.entry("Operation token", TypedFieldValues.uuid(operationToken))));
  }

  @Override
  public String toString() {
    return "UserCreateRequestData[REDACTED]";
  }
}
