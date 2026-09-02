package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts UDTRSP01. */
public record UserDetailResponseData(long userId,
    String username,
    String role,
    String state,
    Optional<Instant> lockedUntil,
    Optional<Instant> lastLogin,
    Instant passwordChangedAt,
    Instant createdAt,
    Instant updatedAt,
    long activeSessionCount,
    long version,
    String createdBy,
    String updatedBy) implements PayloadData {
  public UserDetailResponseData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(lockedUntil, "lockedUntil");
    Objects.requireNonNull(lastLogin, "lastLogin");
    Objects.requireNonNull(passwordChangedAt, "passwordChangedAt");
    Objects.requireNonNull(createdAt, "createdAt");
    Objects.requireNonNull(updatedAt, "updatedAt");
    Objects.requireNonNull(createdBy, "createdBy");
    Objects.requireNonNull(updatedBy, "updatedBy");
  }

  public static UserDetailResponseData from(FieldValueSet fields) {
    return new UserDetailResponseData(
        TypedFieldValues.requiredLong(fields, "User ID"),
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredString(fields, "Role"),
        TypedFieldValues.requiredString(fields, "State"),
        TypedFieldValues.optionalInstant(fields, "Locked until"),
        TypedFieldValues.optionalInstant(fields, "Last Login"),
        TypedFieldValues.requiredInstant(fields, "Password changed at"),
        TypedFieldValues.requiredInstant(fields, "Created at"),
        TypedFieldValues.requiredInstant(fields, "Updated at"),
        TypedFieldValues.requiredLong(fields, "Active session数"),
        TypedFieldValues.requiredLong(fields, "Version"),
        TypedFieldValues.requiredString(fields, "Created by"),
        TypedFieldValues.requiredString(fields, "Updated by"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.numeric(userId)),
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("Role", TypedFieldValues.text(role)),
            Map.entry("State", TypedFieldValues.text(state)),
            Map.entry("Locked until", TypedFieldValues.optionalInstantValue(lockedUntil)),
            Map.entry("Last Login", TypedFieldValues.optionalInstantValue(lastLogin)),
            Map.entry("Password changed at", TypedFieldValues.instant(passwordChangedAt)),
            Map.entry("Created at", TypedFieldValues.instant(createdAt)),
            Map.entry("Updated at", TypedFieldValues.instant(updatedAt)),
            Map.entry("Active session数", TypedFieldValues.numeric(activeSessionCount)),
            Map.entry("Version", TypedFieldValues.numeric(version)),
            Map.entry("Created by", TypedFieldValues.text(createdBy)),
            Map.entry("Updated by", TypedFieldValues.text(updatedBy))));
  }

  @Override
  public String toString() {
    return "UserDetailResponseData[REDACTED]";
  }
}
