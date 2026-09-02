package dev.codex.schubert.nk.protocol.layout.auth;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts LGNRSP01. */
public record LoginResponseData(Optional<FieldValue.Text> username,
    Optional<FieldValue.Text> role,
    Optional<FieldValue.Text> authenticationContextId,
    Optional<FieldValue.Text> issuedAt,
    Optional<FieldValue.Text> expiresAt,
    FieldValue.Numeric retryAfterSeconds,
    FieldValue.Numeric remainingAttempts,
    Optional<FieldValue.Text> userMessage) implements PayloadData {
  public LoginResponseData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(authenticationContextId, "authenticationContextId");
    Objects.requireNonNull(issuedAt, "issuedAt");
    Objects.requireNonNull(expiresAt, "expiresAt");
    Objects.requireNonNull(retryAfterSeconds, "retryAfterSeconds");
    Objects.requireNonNull(remainingAttempts, "remainingAttempts");
    Objects.requireNonNull(userMessage, "userMessage");
  }

  public static LoginResponseData from(FieldValueSet fields) {
    return new LoginResponseData(
        TypedFieldValues.optionalText(fields, "Username"),
        TypedFieldValues.optionalText(fields, "Role"),
        TypedFieldValues.optionalText(fields, "認証context ID"),
        TypedFieldValues.optionalText(fields, "発行日時"),
        TypedFieldValues.optionalText(fields, "期限日時"),
        TypedFieldValues.requiredNumeric(fields, "Retry after秒"),
        TypedFieldValues.requiredNumeric(fields, "残り試行回数"),
        TypedFieldValues.optionalText(fields, "利用者message"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username", TypedFieldValues.orUnset(username)),
            Map.entry("Role", TypedFieldValues.orUnset(role)),
            Map.entry("認証context ID", TypedFieldValues.orUnset(authenticationContextId)),
            Map.entry("発行日時", TypedFieldValues.orUnset(issuedAt)),
            Map.entry("期限日時", TypedFieldValues.orUnset(expiresAt)),
            Map.entry("Retry after秒", retryAfterSeconds),
            Map.entry("残り試行回数", remainingAttempts),
            Map.entry("利用者message", TypedFieldValues.orUnset(userMessage))));
  }
}
