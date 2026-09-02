package dev.codex.schubert.nk.protocol.layout.admin;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts USRREQ01. */
public record UserSearchRequestData(Optional<FieldValue.Text> usernamePrefix,
    Optional<FieldValue.Text> role,
    Optional<FieldValue.Text> state,
    FieldValue.Numeric page,
    FieldValue.Numeric pageSize) implements PayloadData {
  public UserSearchRequestData {
    Objects.requireNonNull(usernamePrefix, "usernamePrefix");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(state, "state");
    Objects.requireNonNull(page, "page");
    Objects.requireNonNull(pageSize, "pageSize");
  }

  public static UserSearchRequestData from(FieldValueSet fields) {
    return new UserSearchRequestData(
        TypedFieldValues.optionalText(fields, "Username prefix"),
        TypedFieldValues.optionalText(fields, "Role"),
        TypedFieldValues.optionalText(fields, "State"),
        TypedFieldValues.requiredNumeric(fields, "Page"),
        TypedFieldValues.requiredNumeric(fields, "Page size"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username prefix", TypedFieldValues.orUnset(usernamePrefix)),
            Map.entry("Role", TypedFieldValues.orUnset(role)),
            Map.entry("State", TypedFieldValues.orUnset(state)),
            Map.entry("Page", page),
            Map.entry("Page size", pageSize)));
  }
}
