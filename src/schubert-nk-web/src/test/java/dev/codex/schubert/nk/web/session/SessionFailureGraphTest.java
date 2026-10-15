package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/**
 * PT-OPS-CAUSE3404-003; YKT1065; SS314/331/352: transient graph never retained in redacted error.
 */
final class SessionFailureGraphTest {
  @Test
  @Timeout(value = 10, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
  void mixedCauseAndSuppressedCyclesTerminateAndReachableFatalRetainsIdentity() {
    RuntimeException first = new RuntimeException("synthetic first");
    RuntimeException second = new RuntimeException("synthetic second", first);
    first.initCause(second);
    first.addSuppressed(second);
    second.addSuppressed(first);
    SessionStoreException.preserveFatal(first);
    AssertionError fatal = new AssertionError("synthetic fatal");
    second.addSuppressed(fatal);
    assertSame(
        fatal,
        assertThrows(AssertionError.class, () -> SessionStoreException.preserveFatal(first)));
  }
}
