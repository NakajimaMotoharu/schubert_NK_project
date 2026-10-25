package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC012; SS314/352/BUG1482/YKT1237: no login, counter or session access. */
final class ExceptionValueContractTest {
  @Test
  void exc012LoginFailureAndLockDelayKeepTheirClosedValues() {
    for (var reason : MqLoginExchangeException.Reason.values()) {
      var failure = new MqLoginExchangeException(reason);
      assertSame(reason, failure.reason());
      assertEquals("login exchange rejected", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new MqLoginExchangeException(null));
    for (int value : new int[] {0, 1, 899, 900}) {
      var failure = new MqLoginLockedException(value);
      assertEquals(value, failure.retryAfterSeconds());
      assertEquals("login temporarily locked", failure.getMessage());
      assertNull(failure.getCause());
    }
    for (int value : new int[] {Integer.MIN_VALUE, -1, 901, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> new MqLoginLockedException(value));
    }
  }
}
