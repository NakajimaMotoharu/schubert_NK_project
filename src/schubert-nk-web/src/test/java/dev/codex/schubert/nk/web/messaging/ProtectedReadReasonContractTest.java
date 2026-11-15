package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException.Reason;
import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * PT-JMS-WIRE-REASON001; NK-MSG-001/NK-WEB-001; MQ/AUT; UI232/234/235; SS311/321/323/352. Closed
 * reason symbols, defensive enumeration and explicit nonnull Java enum precondition. YKT2431; no
 * backend, SDK provider, Root or held fixture substitute.
 */
final class ProtectedReadReasonContractTest {
  @Test
  void wireReason001ClosedSymbolsAreExactAndEnumerationIsDefensive() {
    assertArrayEquals(
        new Reason[] {Reason.INVALID_INPUT, Reason.INVALID_RESPONSE, Reason.UNAVAILABLE},
        Reason.values());
    assertSame(Reason.INVALID_INPUT, Reason.valueOf("INVALID_INPUT"));
    assertSame(Reason.INVALID_RESPONSE, Reason.valueOf("INVALID_RESPONSE"));
    assertSame(Reason.UNAVAILABLE, Reason.valueOf("UNAVAILABLE"));

    Reason[] changedView = Reason.values();
    changedView[0] = Reason.UNAVAILABLE;
    assertSame(Reason.INVALID_INPUT, Reason.values()[0]);

    for (String unknown : List.of("", "invalid_input", " INVALID_INPUT", "MISSING")) {
      assertThrows(IllegalArgumentException.class, () -> Reason.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> Reason.valueOf(null));
  }
}
