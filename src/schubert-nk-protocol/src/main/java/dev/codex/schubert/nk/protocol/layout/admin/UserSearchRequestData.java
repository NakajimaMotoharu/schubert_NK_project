package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts USRREQ01. */
public record UserSearchRequestData(Optional<String> usernamePrefix,
    Optional<String> role,
    Optional<String> state,
    long page,
    long pageSize) implements PayloadData {
  public UserSearchRequestData {
    Objects.requireNonNull(usernamePrefix, "usernamePrefix");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
  }

  public static UserSearchRequestData from(FieldValueSet fields) {
    return new UserSearchRequestData(
        TypedFieldValues.optionalString(fields, "Username prefix"),
        TypedFieldValues.optionalString(fields, "Role"),
        TypedFieldValues.optionalString(fields, "State"),
        TypedFieldValues.requiredLong(fields, "Page"),
        TypedFieldValues.requiredLong(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username prefix", TypedFieldValues.optionalStringValue(usernamePrefix)),
            Map.entry("Role", TypedFieldValues.optionalStringValue(role)),
            Map.entry("State", TypedFieldValues.optionalStringValue(state)),
            Map.entry("Page", TypedFieldValues.numeric(page)),
            Map.entry("Page size", TypedFieldValues.numeric(pageSize))));
  }

  @Override
  public String toString() {
    return "UserSearchRequestData[REDACTED]";
  }
}
