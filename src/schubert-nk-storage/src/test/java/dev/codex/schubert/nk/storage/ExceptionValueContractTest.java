package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-F03-EXC005; SS333/BUG1482/YKT1237: no file/native access. */
final class ExceptionValueContractTest {
  @Test
  void exc005StorageReasonsAreNonNullBoundedAndCauseFree() {
    for (var reason : StorageIoException.Reason.values()) {
      var failure = new StorageIoException(reason);
      assertSame(reason, failure.reason());
      assertEquals("transfer storage operation failed", failure.getMessage());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new StorageIoException(null));
  }
}
