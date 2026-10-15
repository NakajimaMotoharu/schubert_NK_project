package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-OPS-CAUSE3404-002; YKT1065; SS314/352: fatal JDBC cleanup identity, not duplicate commit. */
final class AuthenticationFailureGraphTest {
  @Test
  @Timeout(value = 10, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
  void suppressedCyclesTerminateAndReachableFatalRetainsIdentity() {
    RuntimeException first = new RuntimeException("synthetic first");
    RuntimeException second = new RuntimeException("synthetic second");
    first.addSuppressed(second);
    second.addSuppressed(first);
    AuthenticationInfrastructureException.preserveFatal(first);
    AssertionError fatal = new AssertionError("synthetic fatal");
    second.addSuppressed(fatal);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> AuthenticationInfrastructureException.preserveFatal(first)));
  }
}
