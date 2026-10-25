package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC003; SS341/352/BUG1482/YKT1237: constructs values, never starts cleanup. */
final class ExceptionValueContractTest {
  @Test
  void exc003CleanupReasonsAreNonNullBoundedAndCauseFree() {
    for (var reason : CleanupStopReason.values()) {
      var failure = new CleanupStoppedException(reason);
      assertSame(reason, failure.reason());
      assertEquals("cleanup did not complete", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new CleanupStoppedException(null));
  }
}
