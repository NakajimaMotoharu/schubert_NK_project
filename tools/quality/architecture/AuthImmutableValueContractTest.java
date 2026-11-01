package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** Independent SS314/332 values only; public synthetic fixtures, never real authentication. */
final class AuthImmutableValueContractTest {
  private static final Instant AT = Instant.parse("2026-11-01T00:00:00Z");
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(7, "PUBLIC", Role.USER);
  private static final AuthContextIdentity IDENTITY = new AuthContextIdentity(new UUID(0, 77), 7);
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));
  private static final LoginAttemptState USER = LoginAttemptState.empty(LoginAttemptKind.USER);
  private static final LoginAttemptState IP = LoginAttemptState.empty(LoginAttemptKind.IP);

  @Test
  void authValue001AccountRetainsOnlyItsSuppliedImmutableValuesAndRedactsAllFields() {
    for (String hash : List.of("P", "P".repeat(255), "あ".repeat(85))) {
      for (boolean active : new boolean[] {false, true}) {
        var value = new LoginAccount(ACTOR, active, hash, USER);
        assertSame(ACTOR, value.identity());
        assertEquals(active, value.active());
        assertSame(hash, value.passwordHash());
        assertSame(USER, value.attempts());
        assertEquals("LoginAccount[REDACTED]", value.toString());
      }
    }
  }

  @Test
  void authValue002AccountRejectsNullUtf8LengthAndWrongAttemptKind() {
    assertThrows(NullPointerException.class, () -> new LoginAccount(null, true, "P", USER));
    assertThrows(NullPointerException.class, () -> new LoginAccount(ACTOR, true, null, USER));
    assertThrows(NullPointerException.class, () -> new LoginAccount(ACTOR, true, "P", null));
    for (String hash : List.of("", "P".repeat(256), "あ".repeat(86))) {
      assertEquals("login account storage invariant is invalid",
          assertThrows(IllegalArgumentException.class,
              () -> new LoginAccount(ACTOR, true, hash, USER)).getMessage());
    }
    assertThrows(IllegalArgumentException.class, () -> new LoginAccount(ACTOR, true, "P", IP));
  }

  @Test
  void authValue003IssuedValueRetainsExactReferencesAndNeverExposesPublicFixtureText() {
    Instant end = AT.plusSeconds(1);
    var issued = new IssuedContext(IDENTITY, CONTEXT, AT, end);
    assertSame(IDENTITY, issued.identity());
    assertSame(CONTEXT, issued.context());
    assertSame(AT, issued.issuedAt());
    assertSame(end, issued.expiresAt());
    assertEquals("IssuedContext[REDACTED]", issued.toString());
  }

  @Test
  void authValue004IssuedValueRejectsEveryNullAndNonIncreasingExpiry() {
    assertThrows(NullPointerException.class, () -> new IssuedContext(null, CONTEXT, AT, AT.plusSeconds(1)));
    assertThrows(NullPointerException.class, () -> new IssuedContext(IDENTITY, null, AT, AT.plusSeconds(1)));
    assertThrows(NullPointerException.class, () -> new IssuedContext(IDENTITY, CONTEXT, null, AT));
    assertThrows(NullPointerException.class, () -> new IssuedContext(IDENTITY, CONTEXT, AT, null));
    for (Instant end : List.of(AT, AT.minusSeconds(1))) {
      assertEquals("issued context expiry must follow issue time",
          assertThrows(IllegalArgumentException.class,
              () -> new IssuedContext(IDENTITY, CONTEXT, AT, end)).getMessage());
    }
  }

  @Test
  void authValue005RevokedValueHasOnlySuccessAndIdempotentShapes() {
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
      var value = new RevokedContext(IDENTITY, AT, code);
      assertSame(IDENTITY, value.identity());
      assertSame(AT, value.revokedAt());
      assertSame(code, value.resultCode());
      assertEquals("RevokedContext[REDACTED]", value.toString());
    }
  }

  @Test
  void authValue006RevokedValueRejectsNullAndEveryOtherClosedResultCode() {
    assertThrows(NullPointerException.class, () -> new RevokedContext(null, AT, ResultCode.SUCCESS));
    assertThrows(NullPointerException.class, () -> new RevokedContext(IDENTITY, null, ResultCode.SUCCESS));
    assertThrows(NullPointerException.class, () -> new RevokedContext(IDENTITY, AT, null));
    for (ResultCode code : ResultCode.values()) {
      if (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS) continue;
      assertEquals("invalid logout result",
          assertThrows(IllegalArgumentException.class,
              () -> new RevokedContext(IDENTITY, AT, code)).getMessage());
    }
  }

  @Test
  void authValue007LockedAttemptRetainsSnapshotAndOnlyCanonicalNumericIp() {
    String[][] rows = {{"203.0.113.7", "203.0.113.7"},
        {"2001:db8::1", "2001:db8:0:0:0:0:0:1"}};
    var account = new LoginAccount(ACTOR, true, "PUBLIC_STORED_HASH", USER);
    for (String[] row : rows) {
      for (Optional<LoginAccount> selected : List.of(Optional.<LoginAccount>empty(), Optional.of(account))) {
        var value = new LockedLoginAttempt(row[0], selected, IP);
        assertEquals(row[1], value.clientAddress());
        assertSame(selected, value.account());
        assertSame(IP, value.ip());
        assertEquals("LockedLoginAttempt[REDACTED]", value.toString());
      }
    }
  }

  @Test
  void authValue008LockedAttemptRejectsNullWrongKindScopeAndNonLiteral() {
    assertThrows(NullPointerException.class, () -> new LockedLoginAttempt(null, Optional.empty(), IP));
    assertThrows(NullPointerException.class, () -> new LockedLoginAttempt("203.0.113.7", null, IP));
    assertThrows(NullPointerException.class, () -> new LockedLoginAttempt("203.0.113.7", Optional.empty(), null));
    assertEquals("login IP state has incorrect kind",
        assertThrows(IllegalArgumentException.class,
            () -> new LockedLoginAttempt("203.0.113.7", Optional.empty(), USER)).getMessage());
    assertEquals("login IP scope is invalid",
        assertThrows(IllegalArgumentException.class,
            () -> new LockedLoginAttempt("fe80::1%1", Optional.empty(), IP)).getMessage());
    for (String address : List.of("", "example.invalid", "203.0.113.7 ")) {
      assertEquals("login IP literal is invalid",
          assertThrows(IllegalArgumentException.class,
              () -> new LockedLoginAttempt(address, Optional.empty(), IP)).getMessage());
    }
  }

  @Test
  void authValue009LoginSuccessRetainsSameOwnerAndUsesOnlyFixedSuccessProfile() {
    var issued = new IssuedContext(IDENTITY, CONTEXT, AT, AT.plusSeconds(1));
    var result = new LoginResult.Success(ACTOR, issued);
    assertSame(ACTOR, result.actor());
    assertSame(issued, result.issued());
    assertEquals("0000", result.resultCode().wireValue());
    assertEquals(0, result.retryAfterSeconds());
    assertEquals("LoginSuccess[REDACTED]", result.toString());
    assertThrows(NullPointerException.class, () -> new LoginResult.Success(null, issued));
    assertThrows(NullPointerException.class, () -> new LoginResult.Success(ACTOR, null));
    var other = new AuthenticatedActor(8, "PUBLIC", Role.ADMIN);
    assertEquals("login result owner differs",
        assertThrows(IllegalArgumentException.class, () -> new LoginResult.Success(other, issued)).getMessage());
  }

  @Test
  void authValue010LoginFailureHasClosedCodesAndExactRetryBounds() {
    var denied = new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 0);
    assertEquals("0101", denied.resultCode().wireValue());
    assertEquals(0, denied.retryAfterSeconds());
    assertEquals("LoginFailure[code=0101, retryAfterSeconds=0]", denied.toString());
    for (int seconds : new int[] {1, 900}) {
      var locked = new LoginResult.Failure(ResultCode.LOCKED, seconds);
      assertEquals("0106", locked.resultCode().wireValue());
      assertEquals(seconds, locked.retryAfterSeconds());
      assertEquals("LoginFailure[code=0106, retryAfterSeconds=" + seconds + "]", locked.toString());
    }
    assertThrows(NullPointerException.class, () -> new LoginResult.Failure(null, 0));
    for (ResultCode code : ResultCode.values()) {
      if (code != ResultCode.AUTHENTICATION_FAILED && code != ResultCode.LOCKED) {
        assertEquals("login failure code is invalid",
            assertThrows(IllegalArgumentException.class,
                () -> new LoginResult.Failure(code, 0)).getMessage());
      }
    }
    for (int seconds : new int[] {-1, 1}) {
      assertEquals("unlocked failure has no retry delay",
          assertThrows(IllegalArgumentException.class,
              () -> new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, seconds)).getMessage());
    }
    for (int seconds : new int[] {0, 901}) {
      assertEquals("login lock delay is outside 1..900",
          assertThrows(IllegalArgumentException.class,
              () -> new LoginResult.Failure(ResultCode.LOCKED, seconds)).getMessage());
    }
  }

  @Test
  void authValue011RolesAndInternalReasonsHaveOnlyLiteralClosedNamesAndOrder() {
    assertEquals(List.of("USER", "ADMIN"), Arrays.stream(Role.values()).map(Enum::name).toList());
    assertEquals(List.of("SUCCEEDED", "NO_ACCOUNT", "DISABLED", "PASSWORD_MISMATCH", "PREEXISTING_LOCK"),
        Arrays.stream(LoginAuditReason.values()).map(Enum::name).toList());
    assertEquals(List.of("LOGOUT", "DISABLED", "PASSWORD_RESET", "ADMIN", "EXPIRED", "REPLACED"),
        Arrays.stream(SessionRevocationReason.values()).map(Enum::name).toList());
  }

  @Test
  void authValue012InvalidContextExceptionHasOnlyItsFixedCatalog() {
    var value = new AuthenticationContextException();
    assertEquals("authentication context is not valid", value.getMessage());
    assertNull(value.getCause());
    assertEquals(0, value.getSuppressed().length);
  }
}
