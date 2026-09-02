package dev.codex.schubert.nk.protocol.layout.auth;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts LGNREQ01. */
public record LoginRequestData(FieldValue.Text username,
    FieldValue.Text password,
    FieldValue.Text clientAddress) implements PayloadData {
  public LoginRequestData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(password, "password");
    Objects.requireNonNull(clientAddress, "clientAddress");
  }

  public static LoginRequestData from(FieldValueSet fields) {
    return new LoginRequestData(
        TypedFieldValues.requiredText(fields, "Username"),
        TypedFieldValues.requiredText(fields, "Password"),
        TypedFieldValues.requiredText(fields, "Client address"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username", username),
            Map.entry("Password", password),
            Map.entry("Client address", clientAddress)));
  }
}
