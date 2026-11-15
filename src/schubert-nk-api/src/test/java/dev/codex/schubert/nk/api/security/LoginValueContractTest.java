package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-AUT-001/AUT001; UI226234242; SS314331332352; PT-LOGIN-VALUE001..004. */
final class LoginValueContractTest {
  private static final Instant AT = Instant.parse("2026-09-07T00:00:00Z");
  private static final Instant END = Instant.parse("2026-09-07T00:15:00Z");
  private static final String SYNTHETIC_HASH = "synthetic-not-a-credential";
  private static final String ADDRESS = "192.0.2.10";
  private static final String MATCH = "matched-value";
  private static final String LOWERCASE_NAME = "école";
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(7, "Alice", Role.USER);

  @Test
  void value001AccountAndLockedSnapshotPreserveEveryComponentAndStorageInvariant() {
    var user = LoginAttemptState.empty(LoginAttemptKind.USER);
    var ip = LoginAttemptState.empty(LoginAttemptKind.IP);
    var account = new LoginAccount(ACTOR, true, SYNTHETIC_HASH, user);
    equivalent(
        account,
        new LoginAccount(ACTOR, true, SYNTHETIC_HASH, user),
        List.of(
            new LoginAccount(
                new AuthenticatedActor(8, "Bob", Role.USER), true, SYNTHETIC_HASH, user),
            new LoginAccount(ACTOR, false, SYNTHETIC_HASH, user),
            new LoginAccount(ACTOR, true, "other-synthetic-hash", user),
            new LoginAccount(
                ACTOR,
                true,
                SYNTHETIC_HASH,
                new LoginAttemptState(
                    LoginAttemptKind.USER, 1, Optional.of(AT), Optional.empty()))));
    assertSame(ACTOR, account.identity());
    assertEquals(true, account.active());
    assertEquals(SYNTHETIC_HASH, account.passwordHash());
    assertSame(user, account.attempts());
    assertEquals("LoginAccount[REDACTED]", account.toString());
    assertThrows(
        NullPointerException.class, () -> new LoginAccount(null, true, SYNTHETIC_HASH, user));
    assertThrows(NullPointerException.class, () -> new LoginAccount(ACTOR, true, null, user));
    assertThrows(
        NullPointerException.class, () -> new LoginAccount(ACTOR, true, SYNTHETIC_HASH, null));
    for (String invalid : List.of("", "x".repeat(256), "é".repeat(128)))
      assertThrows(
          IllegalArgumentException.class, () -> new LoginAccount(ACTOR, true, invalid, user));
    for (String boundary : List.of("x", "x".repeat(255), "é".repeat(127) + "x"))
      assertEquals(boundary, new LoginAccount(ACTOR, true, boundary, user).passwordHash());
    assertThrows(
        IllegalArgumentException.class, () -> new LoginAccount(ACTOR, true, SYNTHETIC_HASH, ip));
    var locked = new LockedLoginAttempt(ADDRESS, Optional.of(account), ip);
    equivalent(
        locked,
        new LockedLoginAttempt(ADDRESS, Optional.of(account), ip),
        List.of(
            new LockedLoginAttempt("192.0.2.11", Optional.of(account), ip),
            new LockedLoginAttempt(ADDRESS, Optional.empty(), ip),
            new LockedLoginAttempt(
                ADDRESS,
                Optional.of(account),
                new LoginAttemptState(LoginAttemptKind.IP, 1, Optional.of(AT), Optional.empty()))));
    assertEquals(ADDRESS, locked.clientAddress());
    assertEquals(Optional.of(account), locked.account());
    assertSame(ip, locked.ip());
    assertEquals("LockedLoginAttempt[REDACTED]", locked.toString());
    assertEquals(
        "2001:db8:0:0:0:0:0:1",
        new LockedLoginAttempt("2001:db8::1", Optional.empty(), ip).clientAddress());
    assertThrows(
        NullPointerException.class, () -> new LockedLoginAttempt(null, Optional.empty(), ip));
    assertThrows(NullPointerException.class, () -> new LockedLoginAttempt(ADDRESS, null, ip));
    assertThrows(
        NullPointerException.class, () -> new LockedLoginAttempt(ADDRESS, Optional.empty(), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LockedLoginAttempt(ADDRESS, Optional.empty(), user));
    for (String invalid : List.of("", "localhost", "192.0.2.999", "fe80::1%eth0"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new LockedLoginAttempt(invalid, Optional.empty(), ip));
  }

  @Test
  void value002StateAndClosedAuditThresholdVocabulariesHaveExplicitValueContracts() {
    var state = new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(AT), Optional.empty());
    equivalent(
        state,
        new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(AT), Optional.empty()),
        List.of(
            new LoginAttemptState(LoginAttemptKind.IP, 5, Optional.of(AT), Optional.empty()),
            new LoginAttemptState(LoginAttemptKind.USER, 4, Optional.of(AT), Optional.empty()),
            new LoginAttemptState(
                LoginAttemptKind.USER, 5, Optional.of(AT.plusSeconds(1)), Optional.empty()),
            new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(AT), Optional.of(END))));
    assertEquals(
        "LoginAttemptState[kind=USER, failedCount=5, windowStartedAt=Optional[2026-09-07T00:00:00Z], lockedUntil=Optional.empty]",
        state.toString());
    assertEquals(
        List.of("USER", "IP"), Arrays.stream(LoginAttemptKind.values()).map(Enum::name).toList());
    assertSame(LoginAttemptKind.USER, LoginAttemptKind.valueOf("USER"));
    assertSame(LoginAttemptKind.IP, LoginAttemptKind.valueOf("IP"));
    assertEquals(5, LoginAttemptKind.USER.threshold());
    assertEquals(10, LoginAttemptKind.IP.threshold());
    var kinds = LoginAttemptKind.values();
    kinds[0] = LoginAttemptKind.IP;
    assertSame(LoginAttemptKind.USER, LoginAttemptKind.values()[0]);
    List<String> reasons =
        List.of("SUCCEEDED", "NO_ACCOUNT", "DISABLED", "PASSWORD_MISMATCH", "PREEXISTING_LOCK");
    assertEquals(reasons, Arrays.stream(LoginAuditReason.values()).map(Enum::name).toList());
    assertSame(LoginAuditReason.SUCCEEDED, LoginAuditReason.valueOf("SUCCEEDED"));
    assertSame(LoginAuditReason.NO_ACCOUNT, LoginAuditReason.valueOf("NO_ACCOUNT"));
    assertSame(LoginAuditReason.DISABLED, LoginAuditReason.valueOf("DISABLED"));
    assertSame(LoginAuditReason.PASSWORD_MISMATCH, LoginAuditReason.valueOf("PASSWORD_MISMATCH"));
    assertSame(LoginAuditReason.PREEXISTING_LOCK, LoginAuditReason.valueOf("PREEXISTING_LOCK"));
    var copied = LoginAuditReason.values();
    copied[0] = LoginAuditReason.DISABLED;
    assertSame(LoginAuditReason.SUCCEEDED, LoginAuditReason.values()[0]);
    for (String invalid : List.of("", "UNKNOWN", "user", " USER "))
      assertThrows(IllegalArgumentException.class, () -> LoginAttemptKind.valueOf(invalid));
    for (String invalid : List.of("", "UNKNOWN", "succeeded", " SUCCEEDED "))
      assertThrows(IllegalArgumentException.class, () -> LoginAuditReason.valueOf(invalid));
    assertThrows(NullPointerException.class, () -> LoginAttemptKind.valueOf(null));
    assertThrows(NullPointerException.class, () -> LoginAuditReason.valueOf(null));
  }

  @Test
  void value003DisjointLoginResultsEnforceOwnerRetryCodeAndExactValueSemantics() {
    var issued = issued(7, AT);
    var success = new LoginResult.Success(ACTOR, issued);
    equivalent(
        success,
        new LoginResult.Success(ACTOR, issued(7, AT)),
        List.of(
            new LoginResult.Success(new AuthenticatedActor(7, "Other", Role.USER), issued),
            new LoginResult.Success(ACTOR, issued(7, AT.plusSeconds(1)))));
    assertSame(ACTOR, success.actor());
    assertSame(issued, success.issued());
    assertEquals(ResultCode.SUCCESS, success.resultCode());
    assertEquals(0, success.retryAfterSeconds());
    assertEquals("LoginSuccess[REDACTED]", success.toString());
    assertThrows(NullPointerException.class, () -> new LoginResult.Success(null, issued));
    assertThrows(NullPointerException.class, () -> new LoginResult.Success(ACTOR, null));
    assertThrows(
        IllegalArgumentException.class, () -> new LoginResult.Success(ACTOR, issued(8, AT)));
    var denied = new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 0);
    equivalent(
        denied,
        new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 0),
        List.of(new LoginResult.Failure(ResultCode.LOCKED, 1)));
    var locked = new LoginResult.Failure(ResultCode.LOCKED, 1);
    equivalent(
        locked,
        new LoginResult.Failure(ResultCode.LOCKED, 1),
        List.of(denied, new LoginResult.Failure(ResultCode.LOCKED, 900)));
    assertEquals("LoginFailure[code=0101, retryAfterSeconds=0]", denied.toString());
    assertEquals(
        "LoginFailure[code=0106, retryAfterSeconds=900]",
        new LoginResult.Failure(ResultCode.LOCKED, 900).toString());
    assertEquals(ResultCode.LOCKED, locked.resultCode());
    assertEquals(1, locked.retryAfterSeconds());
    assertThrows(NullPointerException.class, () -> new LoginResult.Failure(null, 0));
    for (ResultCode code : ResultCode.values())
      if (code != ResultCode.AUTHENTICATION_FAILED && code != ResultCode.LOCKED)
        assertThrows(IllegalArgumentException.class, () -> new LoginResult.Failure(code, 0));
    for (int delay : new int[] {-1, 1, 900})
      assertThrows(
          IllegalArgumentException.class,
          () -> new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, delay));
    for (int delay : new int[] {-1, 0, 901})
      assertThrows(
          IllegalArgumentException.class, () -> new LoginResult.Failure(ResultCode.LOCKED, delay));
  }

  @Test
  void value004NormalizedDisplayIsTheValueWhileComparisonKeyIsIndependent() {
    var display = new LoginUsername(" E\u0301COLE ");
    equivalent(
        display,
        new LoginUsername("ÉCOLE"),
        List.of(new LoginUsername(LOWERCASE_NAME), new LoginUsername("Other")));
    assertEquals("ÉCOLE", display.value());
    assertEquals(LOWERCASE_NAME, display.key());
    assertEquals(LOWERCASE_NAME, new LoginUsername(LOWERCASE_NAME).key());
    assertEquals("LoginUsername[REDACTED]", display.toString());
  }

  private static IssuedContext issued(long userId, Instant at) {
    return new IssuedContext(
        new AuthContextIdentity(new UUID(0, 71), userId),
        AuthenticationContext.of("a".repeat(64)),
        at,
        AT.plusSeconds(28_800));
  }

  private static void equivalent(Object first, Object equal, List<Object> differences) {
    assertEquals(first, equal);
    assertEquals(equal, first);
    assertEquals(first.hashCode(), equal.hashCode());
    assertEquals(MATCH, Map.of(first, MATCH).get(equal));
    assertFalse(first.equals(null));
    assertFalse(first.equals("different-type"));
    for (Object difference : differences) {
      assertNotEquals(first, difference);
      assertNotEquals(difference, first);
      assertFalse(Map.of(first, MATCH).containsKey(difference));
    }
  }
}
