package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts USRRSP01. */
public record UserRecord(UserId userId,
    String username,
    UserRole role,
    UserState state,
    Optional<Instant> lockedUntil,
    Optional<Instant> lastLogin,
    Instant createdAt,
    Instant updatedAt,
    long version) implements PayloadRecord {
  public UserRecord {
    Objects.requireNonNull(userId, "userId");
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(lockedUntil, "lockedUntil");
    Objects.requireNonNull(lastLogin, "lastLogin");
    Objects.requireNonNull(createdAt, "createdAt");
    Objects.requireNonNull(updatedAt, "updatedAt");
    TypedFieldValues.requireUnsignedRange("version", version, 9);
  }

  public static UserRecord from(FieldValueSet fields) {
    return new UserRecord(
        TypedFieldValues.requiredId(fields, "User ID", UserId::new),
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredEnum(fields, "Role", UserRole.class),
        TypedFieldValues.requiredEnum(fields, "State", UserState.class),
        TypedFieldValues.optionalInstant(fields, "Locked until"),
        TypedFieldValues.optionalInstant(fields, "Last Login"),
        TypedFieldValues.requiredInstant(fields, "Created at"),
        TypedFieldValues.requiredInstant(fields, "Updated at"),
        TypedFieldValues.requiredLong(fields, "Version"));
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
            Map.entry("Created at", TypedFieldValues.instant(createdAt)),
            Map.entry("Updated at", TypedFieldValues.instant(updatedAt)),
            Map.entry("Version", TypedFieldValues.numeric(version))));
  }

  @Override
  public String toString() {
    return "UserRecord[REDACTED]";
  }
}
