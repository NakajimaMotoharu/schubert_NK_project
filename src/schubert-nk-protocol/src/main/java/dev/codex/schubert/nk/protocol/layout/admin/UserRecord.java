package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts USRRSP01. */
public record UserRecord(long userId,
    String username,
    String role,
    String state,
    Optional<Instant> lockedUntil,
    Optional<Instant> lastLogin,
    Instant createdAt,
    Instant updatedAt,
    long version) implements PayloadRecord {
  public UserRecord {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(lockedUntil, "lockedUntil");
    Objects.requireNonNull(lastLogin, "lastLogin");
    Objects.requireNonNull(createdAt, "createdAt");
    Objects.requireNonNull(updatedAt, "updatedAt");
  }

  public static UserRecord from(FieldValueSet fields) {
    return new UserRecord(
        TypedFieldValues.requiredLong(fields, "User ID"),
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredString(fields, "Role"),
        TypedFieldValues.requiredString(fields, "State"),
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
            Map.entry("User ID", TypedFieldValues.numeric(userId)),
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("Role", TypedFieldValues.text(role)),
            Map.entry("State", TypedFieldValues.text(state)),
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
