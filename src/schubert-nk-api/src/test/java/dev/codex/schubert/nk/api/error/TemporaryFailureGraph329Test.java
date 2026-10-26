package dev.codex.schubert.nk.api.error;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-MSG-002; SS312/324/354; SSC329/BUG1592; PT-TEMP-GRAPH329001..003, no I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class TemporaryFailureGraph329Test {
  private static final String PUBLIC_ROOT_DIAGNOSTIC = "PUBLIC root";
  private static final String PUBLIC_NEXT_DIAGNOSTIC = "PUBLIC next";

  @Test
  void temporary329001MixedCyclesTerminateAndLateFatalRetainsIdentityWithoutMutation() {
    var root = new SQLException(PUBLIC_ROOT_DIAGNOSTIC);
    var next = new SQLException(PUBLIC_NEXT_DIAGNOSTIC);
    var alias = new IllegalStateException("PUBLIC alias", root);
    root.initCause(alias);
    root.addSuppressed(next);
    root.setNextException(next);
    next.setNextException(root);
    assertDoesNotThrow(() -> TemporaryInfrastructureException.preserveFatal(root));
    var fatal = new AssertionError("PUBLIC fatal");
    next.initCause(fatal);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> TemporaryInfrastructureException.preserveFatal(root)));
    assertSame(alias, root.getCause());
    assertArrayEquals(new Throwable[] {next}, root.getSuppressed());
    assertSame(next, root.getNextException());
    assertSame(root, next.getNextException());
    assertSame(fatal, next.getCause());
  }

  @Test
  void temporary329002DirectThenCauseSuppressedNextPriorityIsFixed() {
    var direct = new AssertionError("PUBLIC direct");
    var cause = new AssertionError("PUBLIC cause");
    var suppressed = new AssertionError("PUBLIC suppressed");
    var next = new AssertionError(PUBLIC_NEXT_DIAGNOSTIC);
    direct.initCause(cause);
    assertSame(
        direct,
        assertThrows(
            AssertionError.class, () -> TemporaryInfrastructureException.preserveFatal(direct)));
    var root = new SQLException(PUBLIC_ROOT_DIAGNOSTIC, cause);
    root.addSuppressed(suppressed);
    root.setNextException(new SQLException(PUBLIC_NEXT_DIAGNOSTIC, next));
    assertSame(
        cause,
        assertThrows(
            AssertionError.class, () -> TemporaryInfrastructureException.preserveFatal(root)));
    var noCause = new SQLException(PUBLIC_ROOT_DIAGNOSTIC);
    noCause.addSuppressed(suppressed);
    noCause.setNextException(new SQLException(PUBLIC_NEXT_DIAGNOSTIC, next));
    assertSame(
        suppressed,
        assertThrows(
            AssertionError.class, () -> TemporaryInfrastructureException.preserveFatal(noCause)));
    var onlyNext = new SQLException(PUBLIC_ROOT_DIAGNOSTIC);
    onlyNext.setNextException(new SQLException(PUBLIC_NEXT_DIAGNOSTIC, next));
    assertSame(
        next,
        assertThrows(
            AssertionError.class, () -> TemporaryInfrastructureException.preserveFatal(onlyNext)));
  }

  @Test
  void temporary329003NullContractNonFatalAndFixedRedaction() {
    assertThrows(
        NullPointerException.class, () -> TemporaryInfrastructureException.preserveFatal(null));
    assertDoesNotThrow(
        () -> TemporaryInfrastructureException.preserveFatal(new Throwable("PUBLIC")));
    assertDoesNotThrow(
        () -> TemporaryInfrastructureException.preserveFatal(new SQLException("PUBLIC")));
    var catalog = new TemporaryInfrastructureException();
    assertEquals("request transaction is unavailable", catalog.getMessage());
    assertNull(catalog.getCause());
    assertEquals(0, catalog.getSuppressed().length);
  }
}
