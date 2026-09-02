package dev.codex.schubert.nk.protocol.layout.auth;

import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;

/** Generated named wire record. Trace: SS 323; layouts LGNREQ01. */
public record LoginRequestData(String username,
    String password,
    String clientAddress) implements PayloadData {
  public LoginRequestData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(password, "password");
    Objects.requireNonNull(clientAddress, "clientAddress");
  }

  public static LoginRequestData from(FieldValueSet fields) {
    return new LoginRequestData(
        TypedFieldValues.requiredString(fields, "Username"),
        TypedFieldValues.requiredString(fields, "Password"),
        TypedFieldValues.requiredString(fields, "Client address"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username", TypedFieldValues.text(username)),
            Map.entry("Password", TypedFieldValues.text(password)),
            Map.entry("Client address", TypedFieldValues.text(clientAddress))));
  }

  @Override
  public String toString() {
    return "LoginRequestData[REDACTED]";
  }
}
