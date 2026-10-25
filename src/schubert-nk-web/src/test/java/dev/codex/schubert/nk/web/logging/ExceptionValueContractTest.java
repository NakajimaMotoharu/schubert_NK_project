package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC006; SS324/352/BUG1482/YKT1237: no key/logger/DB access. */
final class ExceptionValueContractTest {
  @Test
  void exc006LogReasonsRetainOnlyTheClosedDiagnostic() {
    for (var reason : WebLogPayloadException.Reason.values()) {
      var failure = new WebLogPayloadException(reason);
      assertSame(reason, failure.reason());
      assertEquals("web log encrypted payload rejected: " + reason.name(), failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new WebLogPayloadException(null));
  }
}
