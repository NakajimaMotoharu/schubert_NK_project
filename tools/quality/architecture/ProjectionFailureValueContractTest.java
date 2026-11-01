package dev.codex.schubert.nk.api.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

/** SS312/351; FIXED-PROJECTION001. No SQL/provider/transaction. */
final class ProjectionFailureValueContractTest {
  @Test
  void projectionFailure001FixedUnconfirmedValueHasNoProviderDiagnostics() {
    var failure = new LogProjectionDatabaseException();
    assertEquals("DB request log projection was not confirmed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
