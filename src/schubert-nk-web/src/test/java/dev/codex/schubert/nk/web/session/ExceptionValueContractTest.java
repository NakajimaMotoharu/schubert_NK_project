package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC013; SS314/352/BUG1482/YKT1237: no session or serialization access. */
final class ExceptionValueContractTest {
  @Test
  void exc013SessionReasonsRetainOnlyTheClosedDiagnostic() {
    for (var reason : SessionPayloadException.Reason.values()) {
      var failure = new SessionPayloadException(reason);
      assertSame(reason, failure.reason());
      assertEquals("session encrypted payload rejected: " + reason.name(), failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new SessionPayloadException(null));
  }
}
