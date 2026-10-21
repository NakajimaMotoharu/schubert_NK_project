package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;
import java.util.function.BiPredicate;

/**
 * Authenticate only an anonymous Inbox NEW request, within its caller-owned transaction.
 * NK-AUT-001; FUN-001/AUT-001/MQ-021/MON-004; UI226/234; SS312 §4/314 §5/324 §5; PT-AUT-004.
 */
public final class AuthenticationService {
  // Deliberately non-account synthetic digest, not a credential. Same v1 algorithm/work factor.
  private static final String DUMMY_HASH = "{pbkdf2-v1}" + "0".repeat(96);
  private final LoginAttemptRepository attempts;
  private final BiPredicate<char[], String> passwords;
  private final AuthSessionService sessions;
  private final LoginAuditWriter audit;

  public AuthenticationService(
      LoginAttemptRepository attempts,
      PasswordHasher passwords,
      AuthSessionService sessions,
      LoginAuditWriter audit) {
    this(attempts, Objects.requireNonNull(passwords, "passwords")::matches, sessions, audit);
  }

  AuthenticationService(
      LoginAttemptRepository attempts,
      BiPredicate<char[], String> passwords,
      AuthSessionService sessions,
      LoginAuditWriter audit) {
    this.attempts = Objects.requireNonNull(attempts, "attempts");
    this.passwords = Objects.requireNonNull(passwords, "passwords");
    this.sessions = Objects.requireNonNull(sessions, "sessions");
    this.audit = Objects.requireNonNull(audit, "audit");
  }

  /**
   * Wire validation precedes this method; username is display input, not its comparison key. UI226
   * normalization preserves the audit name separately (SSC-014). Consumes password on all exits,
   * including lock/DB failure. Caller commits the result/Inbox or rolls back on exception.
   */
  public LoginResult authenticate(
      Connection connection,
      String username,
      char[] password,
      InetAddress client,
      UUID messageId,
      UUID correlationId,
      Instant now) {
    Objects.requireNonNull(password, "password");
    try {
      Objects.requireNonNull(connection, "connection");
      var name = new LoginUsername(username);
      Objects.requireNonNull(client, "client");
      Objects.requireNonNull(messageId, "messageId");
      Objects.requireNonNull(correlationId, "correlationId");
      Instant at = Objects.requireNonNull(now, "now").truncatedTo(ChronoUnit.MICROS);
      LockedLoginAttempt locked = attempts.lockForAttempt(connection, name.key(), client, at);
      int retry = retry(locked, at, false);
      LoginResult result;
      LoginAuditReason reason;
      if (retry > 0) {
        result = new LoginResult.Failure(ResultCode.LOCKED, retry);
        reason = LoginAuditReason.PREEXISTING_LOCK;
      } else {
        boolean active = locked.account().isPresent() && locked.account().orElseThrow().active();
        String stored = active ? locked.account().orElseThrow().passwordHash() : DUMMY_HASH;
        boolean matches = passwords.test(password, stored);
        if (active && matches) {
          attempts.recordSuccess(connection, locked, at);
          IssuedContext issued =
              sessions.issue(
                  connection,
                  locked.account().orElseThrow().identity().userId(),
                  client,
                  messageId,
                  correlationId,
                  at);
          result = new LoginResult.Success(locked.account().orElseThrow().identity(), issued);
          reason = LoginAuditReason.SUCCEEDED;
        } else {
          attempts.recordFailure(connection, locked, at);
          int after = retry(locked, at, true);
          result =
              new LoginResult.Failure(
                  after > 0 ? ResultCode.LOCKED : ResultCode.AUTHENTICATION_FAILED, after);
          reason =
              active
                  ? LoginAuditReason.PASSWORD_MISMATCH
                  : locked.account().isPresent()
                      ? LoginAuditReason.DISABLED
                      : LoginAuditReason.NO_ACCOUNT;
        }
      }
      audit.write(connection, result, reason, name.value(), client, messageId, correlationId, at);
      return result;
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | AuthContextCryptoException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      // No provider, credential, SQL parameter or encoding contents cross the application boundary.
      throw new AuthenticationInfrastructureException();
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  private static int retry(LockedLoginAttempt locked, Instant now, boolean afterFailure) {
    LoginAttemptState ip = afterFailure ? locked.ip().afterFailure(now) : locked.ip();
    int value = ip.retryAfterSeconds(now);
    if (locked.account().isPresent()) {
      var original = locked.account().orElseThrow().attempts();
      var user = afterFailure ? original.afterFailure(now) : original;
      value = Math.max(value, user.retryAfterSeconds(now));
    }
    return value;
  }
}
