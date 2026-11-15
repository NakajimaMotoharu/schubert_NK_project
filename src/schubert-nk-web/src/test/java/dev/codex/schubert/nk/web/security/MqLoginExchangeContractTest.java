package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SSC431/YKT2556; PT-WEB-LOGINFAILVALUE001: closed failure cannot carry a hidden Error graph. */
final class MqLoginExchangeContractTest {
  @Test
  void loginfailvalue001ReasonAndFailureCannotRetainMutableDiagnostics() {
    assertEquals(
        List.of("INVALID_INPUT", "UNAVAILABLE"),
        Arrays.stream(MqLoginExchangeException.Reason.values()).map(Enum::name).toList());
    assertSame(
        MqLoginExchangeException.Reason.INVALID_INPUT,
        MqLoginExchangeException.Reason.valueOf("INVALID_INPUT"));
    assertSame(
        MqLoginExchangeException.Reason.UNAVAILABLE,
        MqLoginExchangeException.Reason.valueOf("UNAVAILABLE"));
    var reasons = MqLoginExchangeException.Reason.values();
    reasons[0] = MqLoginExchangeException.Reason.UNAVAILABLE;
    assertSame(
        MqLoginExchangeException.Reason.INVALID_INPUT, MqLoginExchangeException.Reason.values()[0]);
    for (var reason : MqLoginExchangeException.Reason.values()) {
      var failure = new MqLoginExchangeException(reason);
      assertSame(reason, failure.reason());
      assertEquals("login exchange rejected", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      var fatal = new AssertionError("public synthetic closed failure");
      failure.addSuppressed(fatal);
      assertEquals(0, failure.getSuppressed().length);
      assertThrows(IllegalStateException.class, () -> failure.initCause(fatal));
      assertNull(failure.getCause());
    }
    for (String invalid : List.of("", "UNKNOWN", "unavailable", " UNAVAILABLE "))
      assertThrows(
          IllegalArgumentException.class, () -> MqLoginExchangeException.Reason.valueOf(invalid));
    assertThrows(NullPointerException.class, () -> MqLoginExchangeException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new MqLoginExchangeException(null));
  }
}
