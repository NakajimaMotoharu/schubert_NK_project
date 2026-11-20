package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.io.Serial;
import java.sql.SQLException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** SS332 SSC-461; independent SQL edge ranking and identity checks. */
final class JdbcFailureGraphOrderTest {
  @Test
  void queueRanksCauseAndSuppressedEntriesBeforeSqlNextAtTheSameDepth() {
    // PT-OPS-JDBCGRAPH006. All candidate terminal errors are two edges from the root.
    var cause = new AssertionError("cause");
    var first = new AssertionError("first suppressed");
    var second = new AssertionError("second suppressed");
    var next = new AssertionError("SQL next");

    var withCause = sqlGraph(new IOException(cause), first, second, next);
    var withSuppressed = sqlGraph(null, first, second, next);
    var onlyNext = sqlGraph(null, null, null, next);
    assertSame(
        cause, assertThrows(AssertionError.class, () -> JdbcFailureGraph.preserveFatal(withCause)));
    assertSame(
        first,
        assertThrows(AssertionError.class, () -> JdbcFailureGraph.preserveFatal(withSuppressed)));
    assertSame(
        next, assertThrows(AssertionError.class, () -> JdbcFailureGraph.preserveFatal(onlyNext)));
  }

  @Test
  void closerSuppressedErrorWinsOverAnEarlierButDeeperCause() {
    // PT-OPS-JDBCGRAPH007. The suppressed error is one edge away, the cause error is two.
    var farther = new AssertionError("deeper cause");
    var nearer = new AssertionError("nearer suppressed");
    var root = new SQLException("fixture root", new IOException(farther));
    root.addSuppressed(nearer);
    assertSame(
        nearer, assertThrows(AssertionError.class, () -> JdbcFailureGraph.preserveFatal(root)));
  }

  @Test
  void sameSqlObjectsAreQueriedOnceWhenNextAndCauseLinkBack() {
    // PT-OPS-JDBCGRAPH008. Both SQL edges are instrumented to fail immediately on a revisit.
    var root = new CountingSql();
    var peer = new CountingSql();
    root.setNextException(peer);
    peer.setNextException(root);
    root.initCause(peer);
    peer.addSuppressed(root);

    assertDoesNotThrow(() -> JdbcFailureGraph.preserveFatal(root));
    assertEquals(1, root.visits);
    assertEquals(1, peer.visits);
  }

  private static SQLException sqlGraph(
      @Nullable IOException cause,
      @Nullable AssertionError first,
      @Nullable AssertionError second,
      AssertionError next) {
    var root = new SQLException("fixture root", cause);
    if (first != null) root.addSuppressed(new IOException(first));
    if (second != null) root.addSuppressed(new IOException(second));
    root.setNextException(new SQLException("fixture next", next));
    return root;
  }

  private static final class CountingSql extends SQLException {
    @Serial private static final long serialVersionUID = 1L;
    private int visits;

    @Override
    public @Nullable SQLException getNextException() {
      if (++visits != 1) throw new AssertionError("SQL instance revisited");
      return super.getNextException();
    }
  }
}
