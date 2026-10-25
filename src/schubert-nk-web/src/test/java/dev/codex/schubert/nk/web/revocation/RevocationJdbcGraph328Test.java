package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-WEB-001/002; PT-REVOCATION-GRAPH328001..003/SS314354/SSC328/BUG1591; pure graph only. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class RevocationJdbcGraph328Test {
  @Test
  void graph328001SqlNextFatalCannotBecomeAnOrdinaryCatalog() {
    var fatal = new AssertionError("PUBLIC fixture fatal");
    var root = new SQLException("PUBLIC fixture root");
    var next = new SQLException("PUBLIC fixture next", fatal);
    root.setNextException(next);
    assertSame(
        fatal,
        assertThrows(AssertionError.class, () -> RevocationRetryCoordinator.preserveFatal(root)));
  }

  @Test
  void graph328002MixedCyclesAreFiniteAndLateFatalRetainsIdentity() {
    var root = new SQLException("PUBLIC fixture root");
    var next = new SQLException("PUBLIC fixture next");
    root.setNextException(next);
    next.setNextException(root);
    root.addSuppressed(new IllegalStateException("PUBLIC fixture alias", root));
    assertDoesNotThrow(() -> RevocationRetryCoordinator.preserveFatal(root));
    var fatal = new AssertionError("PUBLIC fixture fatal");
    next.addSuppressed(fatal);
    assertSame(
        fatal,
        assertThrows(AssertionError.class, () -> RevocationRetryCoordinator.preserveFatal(root)));
  }

  @Test
  void graph328003ExistingCausePriorityNullAndRedactionRemainFixed() {
    var cause = new AssertionError("PUBLIC fixture cause");
    var suppressed = new AssertionError("PUBLIC fixture suppressed");
    var root = new SQLException("PUBLIC fixture root", cause);
    root.addSuppressed(suppressed);
    root.setNextException(
        new SQLException("PUBLIC fixture next", new AssertionError("PUBLIC next fatal")));
    assertSame(
        cause,
        assertThrows(AssertionError.class, () -> RevocationRetryCoordinator.preserveFatal(root)));
    assertSame(
        suppressed,
        assertThrows(
            AssertionError.class, () -> RevocationRetryCoordinator.preserveFatal(suppressed)));
    assertDoesNotThrow(() -> RevocationRetryCoordinator.preserveFatal(new SQLException("PUBLIC")));
    assertThrows(NullPointerException.class, () -> RevocationRetryCoordinator.preserveFatal(null));
    var catalog = new RevocationRetryException();
    assertEquals("retained revocation retry infrastructure unavailable", catalog.getMessage());
    assertNull(catalog.getCause());
    assertEquals(0, catalog.getSuppressed().length);
  }
}
