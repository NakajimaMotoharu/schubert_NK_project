package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts UDTRSP01. */
public record UserDetailResponseData(FieldValue.Numeric userId,
    FieldValue.Text username,
    FieldValue.Text role,
    FieldValue.Text state,
    Optional<FieldValue.Text> lockedUntil,
    Optional<FieldValue.Text> lastLogin,
    FieldValue.Numeric passwordChangedAt,
    FieldValue.Numeric createdAt,
    FieldValue.Numeric updatedAt,
    FieldValue.Numeric activeSessionCount,
    FieldValue.Numeric version,
    FieldValue.Text createdBy,
    FieldValue.Text updatedBy) implements PayloadData {
  public UserDetailResponseData {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(lockedUntil, "lockedUntil");
    Objects.requireNonNull(lastLogin, "lastLogin");
    Objects.requireNonNull(passwordChangedAt, "passwordChangedAt");
    Objects.requireNonNull(createdAt, "createdAt");
    Objects.requireNonNull(updatedAt, "updatedAt");
    Objects.requireNonNull(activeSessionCount, "activeSessionCount");
    Objects.requireNonNull(version, "version");
    Objects.requireNonNull(createdBy, "createdBy");
    Objects.requireNonNull(updatedBy, "updatedBy");
  }

  public static UserDetailResponseData from(FieldValueSet fields) {
    return new UserDetailResponseData(
        TypedFieldValues.requiredNumeric(fields, "User ID"),
        TypedFieldValues.requiredText(fields, "Username"),
        TypedFieldValues.requiredText(fields, "Role"),
        TypedFieldValues.requiredText(fields, "State"),
        TypedFieldValues.optionalText(fields, "Locked until"),
        TypedFieldValues.optionalText(fields, "Last Login"),
        TypedFieldValues.requiredNumeric(fields, "Password changed at"),
        TypedFieldValues.requiredNumeric(fields, "Created at"),
        TypedFieldValues.requiredNumeric(fields, "Updated at"),
        TypedFieldValues.requiredNumeric(fields, "Active session数"),
        TypedFieldValues.requiredNumeric(fields, "Version"),
        TypedFieldValues.requiredText(fields, "Created by"),
        TypedFieldValues.requiredText(fields, "Updated by"));
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
            Map.entry("Password changed at", passwordChangedAt),
            Map.entry("Created at", createdAt),
            Map.entry("Updated at", updatedAt),
            Map.entry("Active session数", activeSessionCount),
            Map.entry("Version", version),
            Map.entry("Created by", createdBy),
            Map.entry("Updated by", updatedBy)));
  }
}
