package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC011; SS352/QA050/BUG1482/YKT1237: no cryptography or retransmission. */
final class ExceptionValueContractTest {
  @Test
  void exc011RevocationReasonsRetainOnlyTheClosedDiagnostic() {
    for (var reason : RevocationPayloadException.Reason.values()) {
      var failure = new RevocationPayloadException(reason);
      assertSame(reason, failure.reason());
      assertEquals("revocation encrypted payload rejected: " + reason.name(), failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new RevocationPayloadException(null));
  }
}
