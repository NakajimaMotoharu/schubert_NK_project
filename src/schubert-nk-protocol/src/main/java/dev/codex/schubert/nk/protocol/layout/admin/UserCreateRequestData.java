package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts UCRREQ01. */
public record UserCreateRequestData(FieldValue.Text username,
    FieldValue.Text initialPassword,
    FieldValue.Text role,
    FieldValue.Flag enabled,
    FieldValue.Text operationToken) implements PayloadData {
  public UserCreateRequestData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(initialPassword, "initialPassword");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(enabled, "enabled");
    Objects.requireNonNull(operationToken, "operationToken");
  }

  public static UserCreateRequestData from(FieldValueSet fields) {
    return new UserCreateRequestData(
        TypedFieldValues.requiredText(fields, "Username"),
        TypedFieldValues.requiredText(fields, "Initial Password"),
        TypedFieldValues.requiredText(fields, "Role"),
        TypedFieldValues.requiredFlag(fields, "Enabled"),
        TypedFieldValues.requiredText(fields, "Operation token"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username", username),
            Map.entry("Initial Password", initialPassword),
            Map.entry("Role", role),
            Map.entry("Enabled", enabled),
            Map.entry("Operation token", operationToken)));
  }
}
