package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC008..010; SS311/352/BUG1482/1483: finite values, never sends/receives JMS. */
final class ExceptionValueContractTest {
  @Test
  void exc008MessageReasonsAndOptionalCauseRemainExact() {
    for (var reason : JmsRequestReplyException.Reason.values()) {
      var failure = new JmsRequestReplyException(reason, "bounded exchange failure");
      assertSame(reason, failure.reason());
      assertEquals("bounded exchange failure", failure.getMessage());
      assertNull(failure.getCause());
      var cause = new IllegalStateException("synthetic cause");
      var caused = new JmsRequestReplyException(reason, "bounded exchange failure", cause);
      assertSame(reason, caused.reason());
      assertSame(cause, caused.getCause());
    }
    for (var reason : ProtectedReadWireException.Reason.values()) {
      var failure = new ProtectedReadWireException(reason);
      assertSame(reason, failure.reason());
      assertEquals("protected read exchange rejected", failure.getMessage());
      assertNull(failure.getCause());
    }
    for (var reason : ScenarioWireException.Reason.values()) {
      var failure = new ScenarioWireException(reason);
      assertSame(reason, failure.reason());
      assertEquals("scenario exchange rejected", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new ProtectedReadWireException(null));
    assertThrows(NullPointerException.class, () -> new ScenarioWireException(null));
  }

  @Test
  void exc009NullReasonWithoutCauseIsRejectedAtConstruction() {
    assertThrows(NullPointerException.class, () -> new JmsRequestReplyException(null, "bounded"));
  }

  @Test
  void exc010NullReasonWithCauseIsRejectedAtConstruction() {
    assertThrows(
        NullPointerException.class, () -> new JmsRequestReplyException(null, "bounded", null));
  }
}
