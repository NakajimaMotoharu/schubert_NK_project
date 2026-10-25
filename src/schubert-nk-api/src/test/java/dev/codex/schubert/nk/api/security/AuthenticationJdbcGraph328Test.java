package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-AUT-001; PT-AUTH-GRAPH328001..003/SS314354/SSC328/BUG1591; pure graph only. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthenticationJdbcGraph328Test {
  @Test
  void auth328001CauseFatalCannotBecomeAnInfrastructureResult() {
    var fatal = new AssertionError("PUBLIC fixture fatal");
    var root = new IllegalStateException("PUBLIC fixture root", fatal);
    var alias = new IllegalArgumentException("PUBLIC fixture alias", root);
    root.addSuppressed(alias);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> AuthenticationInfrastructureException.preserveFatal(root)));
  }

  @Test
  void auth328002SqlNextCycleTerminatesAndPreservesTheOriginalFatal() {
    var root = new SQLException("PUBLIC fixture root");
    var next = new SQLException("PUBLIC fixture next");
    root.setNextException(next);
    next.setNextException(root);
    assertDoesNotThrow(() -> AuthenticationInfrastructureException.preserveFatal(root));
    var fatal = new AssertionError("PUBLIC fixture fatal");
    next.initCause(fatal);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> AuthenticationInfrastructureException.preserveFatal(root)));
  }

  @Test
  void auth328003ExistingSuppressedPriorityNullAndRedactionRemainFixed() {
    var cause = new AssertionError("PUBLIC fixture cause");
    var suppressed = new AssertionError("PUBLIC fixture suppressed");
    var root = new IllegalStateException("PUBLIC fixture root", cause);
    root.addSuppressed(suppressed);
    assertSame(
        suppressed,
        assertThrows(
            AssertionError.class, () -> AuthenticationInfrastructureException.preserveFatal(root)));
    assertSame(
        cause,
        assertThrows(
            AssertionError.class,
            () -> AuthenticationInfrastructureException.preserveFatal(cause)));
    var first = new IllegalStateException("PUBLIC fixture first");
    var second = new IllegalStateException("PUBLIC fixture second", first);
    first.initCause(second);
    first.addSuppressed(second);
    second.addSuppressed(first);
    assertDoesNotThrow(() -> AuthenticationInfrastructureException.preserveFatal(first));
    assertDoesNotThrow(
        () -> AuthenticationInfrastructureException.preserveFatal(new SQLException("PUBLIC")));
    assertThrows(
        NullPointerException.class,
        () -> AuthenticationInfrastructureException.preserveFatal(null));
    var catalog = new AuthenticationInfrastructureException();
    assertEquals("authentication storage is unavailable", catalog.getMessage());
    assertNull(catalog.getCause());
    assertEquals(0, catalog.getSuppressed().length);
  }
}
