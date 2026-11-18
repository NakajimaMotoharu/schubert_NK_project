package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SSC-461 / PT-OPS-JDBCGRAPH001..005. JDK Throwable values and finite ownership only. */
final class JdbcFailureGraphContractTest {
  @Test
  void jdbcGraph001CallerEdgeIsLastAndEveryNodeIsInspectedAtMostOnce() {
    var direct = new IOException("outer");
    var prior = new IOException("existing");
    var extra = new IOException("additional");
    direct.initCause(prior);
    direct.addSuppressed(prior);

    var visited = new ArrayList<Throwable>();
    StorageIoException.preserveFatal(
        direct,
        node -> {
          visited.add(node);
          return node == direct ? extra : null;
        });
    assertEquals(List.of(direct, prior, extra), visited);
    assertThrows(NullPointerException.class, () -> StorageIoException.preserveFatal(direct, null));
    assertThrows(NullPointerException.class, () -> StorageIoException.preserveFatal(null));
  }

  @Test
  void jdbcGraph002ExistingCauseWinsAndDirectErrorSkipsTheOptionalEdge() {
    var early = new AssertionError("expected cause");
    var later = new AssertionError("suppressed");
    var tail = new AssertionError("extra");
    var outer = new IOException("outer", early);
    outer.addSuppressed(later);
    assertSame(
        early,
        assertThrows(
            AssertionError.class, () -> StorageIoException.preserveFatal(outer, unused -> tail)));
    var visited = new ArrayList<Throwable>();
    assertSame(
        early,
        assertThrows(
            AssertionError.class,
            () ->
                StorageIoException.preserveFatal(
                    early,
                    value -> {
                      visited.add(value);
                      return null;
                    })));
    assertTrue(visited.isEmpty());
  }

  @Test
  void jdbcGraph003SqlNextUsesTheSameOriginalFatalObjectAsTheLegacyEntry() {
    var marker = new AssertionError("expected synthetic next cause");
    var first = new SQLException("fixture first");
    var next = new SQLException("fixture next", marker);
    first.setNextException(next);

    assertSame(
        marker, assertThrows(AssertionError.class, () -> JdbcFailureGraph.preserveFatal(first)));
    assertSame(
        marker, assertThrows(AssertionError.class, () -> StorageIoException.preserveFatal(first)));
    assertDoesNotThrow(() -> JdbcFailureGraph.preserveFatal(new IOException("fixed harmless")));
  }

  @Test
  void jdbcGraph004AdmissionDiscardChecksBothOwnedSqlFailurePositions() {
    var marker = new AssertionError("expected synthetic cause");
    var carrying = new SQLException("fixture", marker);
    var simple = new SQLException("harmless fixture");
    assertSame(
        marker,
        assertThrows(
            AssertionError.class, () -> JdbcAdmissionFailures.beforeDiscard(carrying, simple)));
    assertSame(
        marker,
        assertThrows(
            AssertionError.class, () -> JdbcAdmissionFailures.beforeDiscard(simple, carrying)));
    assertDoesNotThrow(
        () -> JdbcAdmissionFailures.beforeDiscard(new IOException("first"), carrying));
    assertThrows(NullPointerException.class, () -> JdbcAdmissionFailures.beforeDiscard(null, null));
  }

  @Test
  void jdbcGraph005AdmissionReplacementKeepsTheEstablishedPrimaryConditions() {
    var quiet = new SQLException("fixed fixture");
    assertTrue(JdbcAdmissionFailures.replace(null, quiet));
    assertTrue(JdbcAdmissionFailures.replace(quiet, new IOException("second")));
    assertFalse(JdbcAdmissionFailures.replace(quiet, new SQLException("next fixture")));
    assertEquals(0, quiet.getSuppressed().length);

    var first = new IOException("first fixture");
    assertFalse(JdbcAdmissionFailures.replace(first, quiet));
    var suppressed = first.getSuppressed();
    assertEquals(1, suppressed.length);
    assertEquals("database admission resource failure", suppressed[0].getMessage());
    assertEquals("08001", ((SQLException) suppressed[0]).getSQLState());
  }
}
