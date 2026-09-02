package dev.codex.schubert.nk.protocol.layout.auth;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/** Generated named wire record. Trace: SS 323; layouts LGNRSP01. */
public record LoginResponseData(Optional<String> username,
    Optional<String> role,
    Optional<AuthenticationContext> authenticationContextId,
    Optional<Instant> issuedAt,
    Optional<Instant> expiresAt,
    long retryAfterSeconds,
    long remainingAttempts,
    Optional<String> userMessage) implements PayloadData {
  public LoginResponseData {
    Objects.requireNonNull(username, "username");
    Objects.requireNonNull(role, "role");
    Objects.requireNonNull(authenticationContextId, "authenticationContextId");
    Objects.requireNonNull(issuedAt, "issuedAt");
    Objects.requireNonNull(expiresAt, "expiresAt");
    Objects.requireNonNull(userMessage, "userMessage");
  }

  public static LoginResponseData from(FieldValueSet fields) {
    return new LoginResponseData(
        TypedFieldValues.optionalString(fields, "Username"),
        TypedFieldValues.optionalString(fields, "Role"),
        TypedFieldValues.optionalAuthenticationContext(fields, "認証context ID"),
        TypedFieldValues.optionalInstant(fields, "発行日時"),
        TypedFieldValues.optionalInstant(fields, "期限日時"),
        TypedFieldValues.requiredLong(fields, "Retry after秒"),
        TypedFieldValues.requiredLong(fields, "残り試行回数"),
        TypedFieldValues.optionalString(fields, "利用者message"));
  }

  @Override
  public FieldValueSet fields() {
    return new FieldValueSet(
        Map.ofEntries(
            Map.entry("Username", TypedFieldValues.optionalStringValue(username)),
            Map.entry("Role", TypedFieldValues.optionalStringValue(role)),
            Map.entry("認証context ID", TypedFieldValues.optionalAuthenticationContextValue(authenticationContextId)),
            Map.entry("発行日時", TypedFieldValues.optionalInstantValue(issuedAt)),
            Map.entry("期限日時", TypedFieldValues.optionalInstantValue(expiresAt)),
            Map.entry("Retry after秒", TypedFieldValues.numeric(retryAfterSeconds)),
            Map.entry("残り試行回数", TypedFieldValues.numeric(remainingAttempts)),
            Map.entry("利用者message", TypedFieldValues.optionalStringValue(userMessage))));
  }

  @Override
  public String toString() {
    return "LoginResponseData[REDACTED]";
  }
}
