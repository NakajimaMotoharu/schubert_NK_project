package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.DateTimeException;
import java.time.Instant;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** PT-AUT-003 policy only; SQL persistence and Login transaction remain separate required tests. */
final class LoginAttemptStateTest {
  private static final Instant START = Instant.parse("2026-09-07T00:00:00Z");
  private static final Instant END = Instant.parse("2026-09-07T00:15:00Z");

  @Test
  void exactUserAndIpThresholdsLockWithoutExtensionThenSuccessClears() {
    for (LoginAttemptKind kind : LoginAttemptKind.values()) {
      int threshold = kind == LoginAttemptKind.USER ? 5 : 10;
      assertEquals(threshold, kind.threshold());
      LoginAttemptState state = LoginAttemptState.empty(kind);
      assertEquals(kind, state.kind());
      assertEquals(0, state.failedCount());
      assertTrue(state.windowStartedAt().isEmpty());
      assertTrue(state.lockedUntil().isEmpty());
      assertFalse(state.isLocked(START));
      assertEquals(0, state.retryAfterSeconds(START));
      for (int count = 1; count <= threshold; count++) {
        state = state.afterFailure(START);
        assertEquals(count, state.failedCount());
        assertEquals(Optional.of(START), state.windowStartedAt());
        assertEquals(count == threshold, state.isLocked(START));
      }
      assertEquals(Optional.of(END), state.lockedUntil());
      assertSame(state, state.afterFailure(START.plusSeconds(899)));
      assertEquals(900, state.retryAfterSeconds(START));
      LoginAttemptState cleared = state.afterSuccess();
      assertEquals(0, cleared.failedCount());
      assertTrue(cleared.windowStartedAt().isEmpty());
      assertTrue(cleared.lockedUntil().isEmpty());
    }
  }

  @Test
  void fifteenMinuteWindowAndLockBoundariesAreIndependent() {
    LoginAttemptState state =
        new LoginAttemptState(LoginAttemptKind.USER, 1, Optional.of(START), Optional.empty());
    assertEquals(2, state.afterFailure(END.minusNanos(1)).failedCount());
    LoginAttemptState at = state.afterFailure(END);
    assertEquals(2, at.failedCount());
    assertEquals(Optional.of(START), at.windowStartedAt());
    assertEquals(1, state.afterFailure(END.plusNanos(1)).failedCount());
    LoginAttemptState locked =
        new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(START), Optional.of(END));
    assertTrue(locked.isLocked(END.minusNanos(1)));
    assertFalse(locked.isLocked(END));
    assertFalse(locked.isLocked(END.plusNanos(1)));
    assertEquals(5, locked.afterFailure(END).failedCount());
    assertEquals(
        Optional.of(Instant.parse("2026-09-07T00:30:00Z")), locked.afterFailure(END).lockedUntil());
    assertEquals(0, locked.retryAfterSeconds(END));
    assertEquals(0, locked.retryAfterSeconds(END.plusNanos(1)));
    // SQL count may remain saturated after lock clear; never exceeds the DDL count bound.
    LoginAttemptState saturated =
        new LoginAttemptState(LoginAttemptKind.IP, 10, Optional.of(START), Optional.empty());
    assertEquals(10, saturated.afterFailure(START.plusSeconds(1)).failedCount());
  }

  @Test
  void currentObservedWindowEndpointVectorAppliesToUserAndIp() {
    // Independent Current fixed-Clock probe: one failure then threshold-1 at end +/- 1ns.
    // BUG-021/SSC-009 expected [true, true, false], not computed by production policy.
    for (LoginAttemptKind kind : LoginAttemptKind.values()) {
      int additional = kind == LoginAttemptKind.USER ? 4 : 9;
      for (long offset : new long[] {-1, 0, 1}) {
        LoginAttemptState state = LoginAttemptState.empty(kind).afterFailure(START);
        Instant at = END.plusNanos(offset);
        for (int i = 0; i < additional; i++) state = state.afterFailure(at);
        assertEquals(offset <= 0, state.isLocked(at));
      }
    }
  }

  @Test
  void retryAfterCeilsAndCapsUsingLiteralSeconds() {
    LoginAttemptState state =
        new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(START), Optional.of(END));
    assertEquals(1, state.retryAfterSeconds(END.minusNanos(1)));
    assertEquals(1, state.retryAfterSeconds(END.minusSeconds(1)));
    assertEquals(2, state.retryAfterSeconds(END.minusSeconds(1).minusNanos(1)));
    assertEquals(899, state.retryAfterSeconds(START.plusSeconds(1)));
    assertEquals(900, state.retryAfterSeconds(START.minusSeconds(100)));
  }

  @Test
  void nullMalformedAndClockRegressionCannotInventAValidState() {
    assertThrows(NullPointerException.class, () -> LoginAttemptState.empty(null));
    assertThrows(
        NullPointerException.class,
        () -> new LoginAttemptState(LoginAttemptKind.USER, 0, null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new LoginAttemptState(LoginAttemptKind.USER, 0, Optional.empty(), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LoginAttemptState(LoginAttemptKind.USER, -1, Optional.empty(), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LoginAttemptState(LoginAttemptKind.USER, 6, Optional.of(START), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LoginAttemptState(LoginAttemptKind.IP, 11, Optional.of(START), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () -> new LoginAttemptState(LoginAttemptKind.USER, 1, Optional.empty(), Optional.empty()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LoginAttemptState(LoginAttemptKind.USER, 1, Optional.of(START), Optional.of(END)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(END), Optional.of(START)));
    LoginAttemptState state = LoginAttemptState.empty(LoginAttemptKind.USER);
    assertThrows(NullPointerException.class, () -> state.isLocked(null));
    assertThrows(NullPointerException.class, () -> state.retryAfterSeconds(null));
    assertThrows(NullPointerException.class, () -> state.afterFailure(null));
    LoginAttemptState active = state.afterFailure(START);
    assertThrows(IllegalArgumentException.class, () -> active.afterFailure(START.minusNanos(1)));
    LoginAttemptState farFuture =
        new LoginAttemptState(LoginAttemptKind.USER, 1, Optional.of(Instant.MAX), Optional.empty());
    assertThrows(DateTimeException.class, () -> farFuture.afterFailure(Instant.MAX));
    LoginAttemptState threshold =
        new LoginAttemptState(
            LoginAttemptKind.USER, 4, Optional.of(Instant.MAX.minusSeconds(1)), Optional.empty());
    assertThrows(DateTimeException.class, () -> threshold.afterFailure(Instant.MAX));
  }
}
