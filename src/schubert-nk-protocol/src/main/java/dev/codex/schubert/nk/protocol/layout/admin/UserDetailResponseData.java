package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts UDTRSP01. */
public record UserDetailResponseData(UserId userId,
    String username,
    UserRole role,
    UserState state,
    Optional<Instant> lockedUntil,
    Optional<Instant> lastLogin,
    Instant passwordChangedAt,
    Instant createdAt,
    Instant updatedAt,
    int activeSessionCount,
    long version,
    String createdBy,
    String updatedBy) implements PayloadData {
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
    Objects.requireNonNull(createdBy, "createdBy");
    Objects.requireNonNull(updatedBy, "updatedBy");
  }

  public static UserDetailResponseData from(FieldValueSet fields) {
    return new UserDetailResponseData(
        TypedFieldValues.requiredId(fields, "User ID", UserId::new),
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredEnum(fields, "Role", UserRole.class),
        TypedFieldValues.requiredEnum(fields, "State", UserState.class),
        TypedFieldValues.optionalInstant(fields, "Locked until"),
        TypedFieldValues.optionalInstant(fields, "Last Login"),
        TypedFieldValues.requiredInstant(fields, "Password changed at"),
        TypedFieldValues.requiredInstant(fields, "Created at"),
        TypedFieldValues.requiredInstant(fields, "Updated at"),
        TypedFieldValues.requiredInt(fields, "Active session数"),
        TypedFieldValues.requiredLong(fields, "Version"),
        TypedFieldValues.requiredString(fields, "Created by"),
        TypedFieldValues.requiredString(fields, "Updated by"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("User ID", TypedFieldValues.id(userId)),
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("Role", TypedFieldValues.enumValue(role)),
            Map.entry("State", TypedFieldValues.enumValue(state)),
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
