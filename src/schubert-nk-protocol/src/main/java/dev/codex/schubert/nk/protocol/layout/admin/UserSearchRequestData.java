package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts USRREQ01. */
public record UserSearchRequestData(Optional<String> usernamePrefix,
    Optional<UserRole> role,
    Optional<UserState> state,
    int page,
    int pageSize) implements PayloadData {
  public UserSearchRequestData {
    Objects.requireNonNull(usernamePrefix, "usernamePrefix");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
  }

  public static UserSearchRequestData from(FieldValueSet fields) {
    return new UserSearchRequestData(
        TypedFieldValues.optionalString(fields, "Username prefix"),
        TypedFieldValues.optionalEnum(fields, "Role", UserRole.class),
        TypedFieldValues.optionalEnum(fields, "State", UserState.class),
        TypedFieldValues.requiredInt(fields, "Page"),
        TypedFieldValues.requiredInt(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username prefix", TypedFieldValues.optionalStringValue(usernamePrefix)),
            Map.entry("Role", TypedFieldValues.optionalEnumValue(role)),
            Map.entry("State", TypedFieldValues.optionalEnumValue(state)),
            Map.entry("Page", TypedFieldValues.numeric(page)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize))));
  }

  @Override
  public String toString() {
    return "UserSearchRequestData[REDACTED]";
  }
}
