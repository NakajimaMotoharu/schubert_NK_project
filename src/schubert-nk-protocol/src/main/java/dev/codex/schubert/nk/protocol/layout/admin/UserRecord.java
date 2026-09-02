package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts USRRSP01. */
public record UserRecord(FieldValue.Numeric userId,
    FieldValue.Text username,
    FieldValue.Text role,
    FieldValue.Text state,
    Optional<FieldValue.Text> lockedUntil,
    Optional<FieldValue.Text> lastLogin,
    FieldValue.Numeric createdAt,
    FieldValue.Numeric updatedAt,
    FieldValue.Numeric version) implements PayloadRecord {
  public UserRecord {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(lockedUntil, "lockedUntil");
    Objects.requireNonNull(lastLogin, "lastLogin");
    Objects.requireNonNull(createdAt, "createdAt");
    Objects.requireNonNull(updatedAt, "updatedAt");
    Objects.requireNonNull(version, "version");
  }

  public static UserRecord from(FieldValueSet fields) {
    return new UserRecord(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredText(fields, "Username"),
        TypedFieldValues.requiredText(fields, "Role"),
        TypedFieldValues.requiredText(fields, "State"),
        TypedFieldValues.optionalText(fields, "Locked until"),
        TypedFieldValues.optionalText(fields, "Last Login"),
        TypedFieldValues.requiredNumeric(fields, "Created at"),
        TypedFieldValues.requiredNumeric(fields, "Updated at"),
        TypedFieldValues.requiredNumeric(fields, "Version"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", userId),
            Map.entry("Username", username),
            Map.entry("Role", role),
            Map.entry("State", state),
            Map.entry("Locked until", TypedFieldValues.orUnset(lockedUntil)),
            Map.entry("Last Login", TypedFieldValues.orUnset(lastLogin)),
            Map.entry("Created at", createdAt),
            Map.entry("Updated at", updatedAt),
            Map.entry("Version", version)));
  }
}
