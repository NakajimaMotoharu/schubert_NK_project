package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

/** NK-DAT-001, SS312/351/354, P00405-ORACLE04: independent safe retryable diagnostic. */
final class LogProjectionDatabaseExceptionContractTest {
  @Test
  void projection001FixedDiagnosticHasNoDatabaseDetailsOrSharedFailureState() {
    var first = new LogProjectionDatabaseException();
    var second = new LogProjectionDatabaseException();

    assertEquals(RuntimeException.class, first.getClass().getSuperclass());
    assertEquals("DB request log projection was not confirmed", first.getMessage());
    assertNull(first.getCause());
    assertEquals(0, first.getSuppressed().length);
    assertNotSame(first, second);
    assertNull(second.getCause());
    assertEquals(0, second.getSuppressed().length);
  }
}
