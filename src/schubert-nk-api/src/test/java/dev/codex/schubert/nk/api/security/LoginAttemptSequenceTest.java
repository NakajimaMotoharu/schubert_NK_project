package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** PT-AUT-WINDOW-001..004; SS314 section5 memory-only independent timed policy vectors. */
final class LoginAttemptSequenceTest {
  private static final Instant START = Instant.parse("2026-10-28T00:00:00Z");
  private static final Instant END = Instant.parse("2026-10-28T00:15:00Z");
  private static final Instant USER_UNLOCK = Instant.parse("2026-10-28T00:15:04Z");
  private static final Instant IP_UNLOCK = Instant.parse("2026-10-28T00:15:09Z");

  @Test
  void spacedFailuresRestartAtTheLaterLockExpiry() {
    for (LoginAttemptKind kind : LoginAttemptKind.values()) {
      int threshold = kind == LoginAttemptKind.USER ? 5 : 10;
      Instant unlock = kind == LoginAttemptKind.USER ? USER_UNLOCK : IP_UNLOCK;
      LoginAttemptState empty = LoginAttemptState.empty(kind);
      LoginAttemptState state = empty;
      for (int index = 0; index < threshold; index++) {
        state = state.afterFailure(START.plusSeconds(index));
        assertEquals(index + 1, state.failedCount());
        assertEquals(Optional.of(START), state.windowStartedAt());
      }
      assertEquals(Optional.of(unlock), state.lockedUntil());
      assertSame(state, state.afterFailure(unlock.minusNanos(1)));
      assertEquals(1, state.retryAfterSeconds(unlock.minusNanos(1)));
      LoginAttemptState restarted = state.afterFailure(unlock);
      assertNotSame(state, restarted);
      assertEquals(1, restarted.failedCount());
      assertEquals(Optional.of(unlock), restarted.windowStartedAt());
      assertTrue(restarted.lockedUntil().isEmpty());
      assertFalse(restarted.isLocked(unlock));
      assertEquals(threshold, state.failedCount());
      assertEquals(Optional.of(unlock), state.lockedUntil());
      assertEquals(0, empty.failedCount());
      assertTrue(empty.windowStartedAt().isEmpty());
    }
  }

  @Test
  void everyRetryAfterSecondEdgeMatchesTheIndependentCeilingTable() {
    LoginAttemptState locked =
        new LoginAttemptState(LoginAttemptKind.USER, 5, Optional.of(START), Optional.of(END));
    for (int seconds = 1; seconds <= 900; seconds++) {
      Instant exact = END.minusSeconds(seconds);
      int before = seconds == 900 ? 900 : seconds + 1;
      assertEquals(before, locked.retryAfterSeconds(exact.minusNanos(1)));
      assertEquals(seconds, locked.retryAfterSeconds(exact));
      assertEquals(seconds, locked.retryAfterSeconds(exact.plusNanos(1)));
    }
    assertEquals(0, locked.retryAfterSeconds(END));
    assertEquals(0, locked.retryAfterSeconds(END.plusNanos(1)));
  }

  @Test
  void branchingUserAndIpHistoriesAndSuccessStayIndependent() {
    LoginAttemptState emptyUser = LoginAttemptState.empty(LoginAttemptKind.USER);
    LoginAttemptState emptyIp = LoginAttemptState.empty(LoginAttemptKind.IP);
    LoginAttemptState user = emptyUser;
    LoginAttemptState ip = emptyIp;
    for (int index = 0; index < 5; index++) {
      user = user.afterFailure(START);
      ip = ip.afterFailure(START);
    }
    assertTrue(user.isLocked(START));
    assertFalse(ip.isLocked(START));
    assertEquals(5, user.failedCount());
    assertEquals(5, ip.failedCount());
    LoginAttemptState cleared = user.afterSuccess();
    assertEquals(LoginAttemptKind.USER, cleared.kind());
    assertEquals(0, cleared.failedCount());
    assertTrue(cleared.windowStartedAt().isEmpty());
    assertTrue(cleared.lockedUntil().isEmpty());
    assertEquals(5, user.failedCount());
    assertEquals(Optional.of(END), user.lockedUntil());
    assertEquals(5, ip.failedCount());
    assertTrue(ip.lockedUntil().isEmpty());
    assertEquals(0, emptyUser.failedCount());
    assertEquals(0, emptyIp.failedCount());
    assertTrue(emptyUser.windowStartedAt().isEmpty());
    assertTrue(emptyIp.windowStartedAt().isEmpty());
  }

  @Test
  void everyLockedRetryKeepsTheOriginalWindowAndLock() {
    for (LoginAttemptKind kind : LoginAttemptKind.values()) {
      int threshold = kind == LoginAttemptKind.USER ? 5 : 10;
      LoginAttemptState locked =
          new LoginAttemptState(kind, threshold, Optional.of(START), Optional.of(END));
      for (int seconds = 0; seconds < 900; seconds++) {
        Instant at = START.plusSeconds(seconds);
        assertSame(locked, locked.afterFailure(at));
        assertEquals(threshold, locked.failedCount());
        assertEquals(Optional.of(START), locked.windowStartedAt());
        assertEquals(Optional.of(END), locked.lockedUntil());
        assertEquals(900 - seconds, locked.retryAfterSeconds(at));
      }
    }
  }
}
