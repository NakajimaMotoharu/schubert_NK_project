package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC004; SS341/343/BUG1482/YKT1237: no process or Unit operations. */
final class ExceptionValueContractTest {
  @Test
  void exc004StopReasonsAreNonNullBoundedAndCauseFree() {
    for (var reason : StopGateFailure.values()) {
      var failure = new StopGateException(reason);
      assertSame(reason, failure.reason());
      assertEquals("application stop check failed", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new StopGateException(null));
  }
}
