package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.jms.JMSException;
import java.sql.SQLException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** SS312/342/354; SSC330/BUG1593/YKT1346; PT-WEB-STARTUP-GRAPH330001..003; pure graph only. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class WebStartupGraph330Test {
  private static final String PUBLIC_DIAGNOSTIC = "PUBLIC";

  @Test
  void startup330001LinkedSqlNextFatalAndMixedCyclesRetainIdentityWithoutMutation() {
    var fatal = new AssertionError("PUBLIC fatal");
    var root = new JMSException("PUBLIC root");
    var sql = new SQLException("PUBLIC sql");
    var next = new SQLException("PUBLIC next", fatal);
    root.setLinkedException(sql);
    sql.setNextException(next);
    assertSame(
        fatal, assertThrows(AssertionError.class, () -> WebStartupException.preserveFatal(root)));
    assertSame(sql, root.getLinkedException());
    assertSame(next, sql.getNextException());
    assertSame(fatal, next.getCause());
    var cycle = new JMSException("PUBLIC cycle");
    var shared = new SQLException("PUBLIC shared");
    var alias = new IllegalStateException("PUBLIC alias", cycle);
    cycle.setLinkedException(shared);
    cycle.addSuppressed(shared);
    shared.initCause(alias);
    shared.setNextException(shared);
    assertDoesNotThrow(() -> WebStartupException.preserveFatal(cycle));
    shared.addSuppressed(fatal);
    assertSame(
        fatal, assertThrows(AssertionError.class, () -> WebStartupException.preserveFatal(cycle)));
    assertSame(shared, cycle.getLinkedException());
    assertArrayEquals(new Throwable[] {shared}, cycle.getSuppressed());
    assertSame(alias, shared.getCause());
    assertSame(shared, shared.getNextException());
  }

  @Test
  void startup330002RootCauseSuppressedLinkedPriorityNullAndRedactionStayFixed() {
    var cause = new AssertionError("PUBLIC cause");
    var suppressed = new AssertionError("PUBLIC suppressed");
    var linked = new AssertionError("PUBLIC linked");
    var direct = new AssertionError("PUBLIC direct");
    direct.initCause(cause);
    assertSame(
        direct,
        assertThrows(AssertionError.class, () -> WebStartupException.preserveFatal(direct)));
    var root = new JMSException("PUBLIC root");
    root.initCause(cause);
    root.addSuppressed(suppressed);
    root.setLinkedException(new IllegalStateException("PUBLIC link", linked));
    assertSame(
        cause, assertThrows(AssertionError.class, () -> WebStartupException.preserveFatal(root)));
    var noCause = new JMSException("PUBLIC root");
    noCause.addSuppressed(suppressed);
    noCause.setLinkedException(new IllegalStateException("PUBLIC link", linked));
    assertSame(
        suppressed,
        assertThrows(AssertionError.class, () -> WebStartupException.preserveFatal(noCause)));
    assertDoesNotThrow(
        () -> WebStartupException.preserveFatal(new JMSException(PUBLIC_DIAGNOSTIC)));
    assertDoesNotThrow(
        () -> WebStartupException.preserveFatal(new SQLException(PUBLIC_DIAGNOSTIC)));
    assertDoesNotThrow(() -> WebStartupException.preserveFatal(new Throwable(PUBLIC_DIAGNOSTIC)));
    assertThrows(NullPointerException.class, () -> WebStartupException.preserveFatal(null));
    var catalog = new WebStartupException(PUBLIC_DIAGNOSTIC);
    assertEquals("PUBLIC is unavailable", catalog.getMessage());
    assertNull(catalog.getCause());
    assertEquals(0, catalog.getSuppressed().length);
  }

  @Test
  void startup330003SecondaryIdentityDisabledSuppressionAndNullContracts() {
    var primary = new IllegalStateException("PUBLIC primary");
    var secondary = new SQLException("PUBLIC secondary");
    assertDoesNotThrow(() -> WebStartupException.attachSecondary(primary, primary));
    assertEquals(0, primary.getSuppressed().length);
    assertDoesNotThrow(() -> WebStartupException.attachSecondary(primary, secondary));
    assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
    var fatal = new AssertionError("PUBLIC fatal");
    var disabled = new DisabledRuntime(null);
    var wrapped = new IllegalArgumentException("PUBLIC secondary", fatal);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> WebStartupException.attachSecondary(disabled, wrapped)));
    assertEquals(0, disabled.getSuppressed().length);
    var disabledError = new DisabledError();
    assertSame(
        disabledError,
        assertThrows(
            DisabledError.class,
            () -> WebStartupException.attachSecondary(disabledError, wrapped)));
    var firstFatal = new AssertionError("PUBLIC first");
    var disabledCause = new DisabledRuntime(firstFatal);
    assertSame(
        firstFatal,
        assertThrows(
            AssertionError.class,
            () -> WebStartupException.attachSecondary(disabledCause, wrapped)));
    var ordinary = new DisabledRuntime(null);
    assertDoesNotThrow(() -> WebStartupException.attachSecondary(ordinary, secondary));
    assertEquals(0, ordinary.getSuppressed().length);
    assertThrows(
        NullPointerException.class, () -> WebStartupException.attachSecondary(null, secondary));
    assertThrows(
        NullPointerException.class, () -> WebStartupException.attachSecondary(primary, null));
  }

  private static final class DisabledRuntime extends RuntimeException {
    private static final long serialVersionUID = 1L;

    DisabledRuntime(@Nullable Throwable cause) {
      super(PUBLIC_DIAGNOSTIC, cause, false, false);
    }
  }

  private static final class DisabledError extends Error {
    private static final long serialVersionUID = 1L;

    DisabledError() {
      super(PUBLIC_DIAGNOSTIC, null, false, false);
    }
  }
}
