package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import org.junit.jupiter.api.Test;

/** SSC095/PG312/PG-D1179/BUG3201-3202: PT-DB-ADMISSION-FAIL001..007, heap objects only. */
final class JdbcAdmissionFailuresContractTest {
  @Test
  void namespaceCannotBeInstantiatedOrRetainInstanceState() throws Exception {
    assertTrue(Modifier.isFinal(JdbcAdmissionFailures.class.getModifiers()));
    for (var method : JdbcAdmissionFailures.class.getDeclaredMethods()) {
      assertTrue(Modifier.isStatic(method.getModifiers()));
    }
    for (var field : JdbcAdmissionFailures.class.getDeclaredFields()) {
      assertTrue(Modifier.isStatic(field.getModifiers()));
    }
    var constructor = JdbcAdmissionFailures.class.getDeclaredConstructor();
    assertTrue(Modifier.isPrivate(constructor.getModifiers()));
    boolean before = constructor.canAccess(null);
    assertFalse(before);
    try {
      assertTrue(constructor.trySetAccessible());
      var failure = assertThrows(InvocationTargetException.class, constructor::newInstance);
      assertEquals(AssertionError.class, failure.getCause().getClass());
      assertEquals("static namespace", failure.getCause().getMessage());
      assertNull(failure.getCause().getCause());
      assertEquals(0, failure.getCause().getSuppressed().length);
    } finally {
      constructor.setAccessible(before);
    }
    assertFalse(constructor.canAccess(null));
  }

  @Test
  void missingSecondaryFailsAtBothBoundariesWithoutChangingAnyPrimary() {
    Throwable[] primaries = {
      null,
      new SQLException("sql"),
      new IllegalStateException("runtime"),
      new AssertionError("error"),
      new Throwable("plain")
    };
    for (var primary : primaries) {
      var discard =
          assertThrows(
              NullPointerException.class, () -> JdbcAdmissionFailures.beforeDiscard(primary, null));
      assertEquals("secondary failure", discard.getMessage());
      var replacement =
          assertThrows(
              NullPointerException.class, () -> JdbcAdmissionFailures.replace(primary, null));
      assertEquals("secondary failure", replacement.getMessage());
      if (primary != null) {
        assertEquals(0, primary.getSuppressed().length);
        assertNull(primary.getCause());
      }
    }
  }

  @Test
  void literalTwentyCellPriorityTableAndFixedDiagnosticStayIndependentOfProviderText() {
    boolean[][] replacements = {
      {true, true, true, true},
      {false, true, true, true},
      {false, false, false, false},
      {false, false, false, false},
      {false, false, false, false}
    };
    int[][] markers = {{0, 0, 0, 0}, {0, 0, 0, 0}, {1, 1, 1, 1}, {1, 1, 1, 1}, {1, 1, 1, 1}};
    for (int row = 0; row < 5; row++) {
      for (int column = 0; column < 4; column++) {
        Throwable[] primaries = {
          null,
          new SQLException("primary sql"),
          new IllegalStateException("primary runtime"),
          new AssertionError("primary error"),
          new Throwable("primary plain")
        };
        Throwable[] secondaries = {
          new SQLException("secondary sql"),
          new IllegalStateException("secondary runtime"),
          new AssertionError("secondary error"),
          new Throwable("secondary plain")
        };
        Throwable primary = primaries[row];
        Throwable secondary = secondaries[column];
        String primaryMessage = primary == null ? null : primary.getMessage();
        String secondaryMessage = secondary.getMessage();
        assertEquals(
            replacements[row][column],
            JdbcAdmissionFailures.replace(primary, secondary),
            "literal priority cell " + row + ":" + column);
        assertEquals(0, secondary.getSuppressed().length);
        assertEquals(secondaryMessage, secondary.getMessage());
        assertNull(secondary.getCause());
        if (primary != null) {
          assertEquals(primaryMessage, primary.getMessage());
          assertNull(primary.getCause());
          assertEquals(markers[row][column], primary.getSuppressed().length);
          if (markers[row][column] == 1) {
            var fixed = primary.getSuppressed()[0];
            assertEquals(SQLNonTransientConnectionException.class, fixed.getClass());
            assertEquals("database admission resource failure", fixed.getMessage());
            assertEquals("08001", ((SQLException) fixed).getSQLState());
            assertNull(fixed.getCause());
            assertEquals(0, fixed.getSuppressed().length);
            assertNotSame(primary, fixed);
            assertNotSame(secondary, fixed);
          }
        }
      }
    }
  }

  @Test
  void identicalPrimaryAndSecondaryNeverCauseSelfSuppression() {
    Throwable[] values = {
      new SQLException("same sql"),
      new IllegalStateException("same runtime"),
      new AssertionError("same error"),
      new Throwable("same plain")
    };
    int[] markerCounts = {0, 1, 1, 1};
    for (int index = 0; index < values.length; index++) {
      var failure = values[index];
      assertFalse(JdbcAdmissionFailures.replace(failure, failure));
      assertEquals(markerCounts[index], failure.getSuppressed().length);
      assertNull(failure.getCause());
      if (markerCounts[index] == 1) {
        var marker = failure.getSuppressed()[0];
        assertNotSame(failure, marker);
        assertEquals(SQLNonTransientConnectionException.class, marker.getClass());
        assertEquals("database admission resource failure", marker.getMessage());
        assertEquals("08001", ((SQLException) marker).getSQLState());
      }
    }
  }

  @Test
  void knownSqlFatalClassificationKeepsCauseSuppressedNextAndPrimaryPrecedence() {
    var cause = new AssertionError("cause");
    var suppressed = new LinkageError("suppressed");
    var nextFatal = new AssertionError("next");
    var primary = new SQLException("primary");
    primary.initCause(cause);
    primary.addSuppressed(suppressed);
    var next = new SQLException("next sql", nextFatal);
    primary.setNextException(next);
    var secondary = new SQLException("secondary", new LinkageError("secondary fatal"));
    assertSame(
        cause,
        assertThrows(
            AssertionError.class, () -> JdbcAdmissionFailures.replace(primary, secondary)));
    assertSame(cause, primary.getCause());
    assertSame(suppressed, primary.getSuppressed()[0]);
    assertSame(next, primary.getNextException());
    var suppressedOnly = new SQLException("suppressed only");
    suppressedOnly.addSuppressed(suppressed);
    suppressedOnly.setNextException(next);
    assertSame(
        suppressed,
        assertThrows(
            LinkageError.class,
            () -> JdbcAdmissionFailures.beforeDiscard(suppressedOnly, secondary)));
    var nextOnly = new SQLException("next only");
    nextOnly.setNextException(next);
    assertSame(
        nextFatal,
        assertThrows(
            AssertionError.class, () -> JdbcAdmissionFailures.beforeDiscard(nextOnly, secondary)));
    var secondaryFatal = new AssertionError("secondary cause");
    var fatalSecondary = new SQLException("secondary", secondaryFatal);
    assertSame(
        secondaryFatal,
        assertThrows(
            AssertionError.class, () -> JdbcAdmissionFailures.beforeDiscard(null, fatalSecondary)));
    var cleanPrimary = new SQLException("clean");
    assertSame(
        secondaryFatal,
        assertThrows(
            AssertionError.class,
            () -> JdbcAdmissionFailures.beforeDiscard(cleanPrimary, fatalSecondary)));
    assertEquals(0, cleanPrimary.getSuppressed().length);
  }

  @Test
  void unknownPrimaryDoesNotTraverseProviderGettersOrKnownSecondaryFatal() {
    var primary = new UntouchableCause();
    var secondary = new SQLException("secondary", new AssertionError("unselected"));
    JdbcAdmissionFailures.beforeDiscard(primary, secondary);
    assertFalse(JdbcAdmissionFailures.replace(primary, secondary));
    assertEquals(0, primary.causeReads);
    assertEquals(1, primary.getSuppressed().length);
    var fixed = primary.getSuppressed()[0];
    assertEquals(SQLNonTransientConnectionException.class, fixed.getClass());
    assertEquals("database admission resource failure", fixed.getMessage());
    assertEquals("08001", ((SQLException) fixed).getSQLState());
    assertNotSame(secondary, fixed);
  }

  @Test
  void sharedCyclicSqlGraphTerminatesWithoutMutationOrInventedFailure() {
    var first = new SQLException("first");
    var second = new SQLException("second");
    first.initCause(second);
    second.initCause(first);
    first.addSuppressed(second);
    second.addSuppressed(first);
    first.setNextException(second);
    second.setNextException(first);
    JdbcAdmissionFailures.beforeDiscard(first, second);
    assertFalse(JdbcAdmissionFailures.replace(first, second));
    assertSame(second, first.getCause());
    assertSame(first, second.getCause());
    assertEquals(1, first.getSuppressed().length);
    assertEquals(1, second.getSuppressed().length);
    assertSame(second, first.getSuppressed()[0]);
    assertSame(first, second.getSuppressed()[0]);
    assertSame(second, first.getNextException());
    assertSame(first, second.getNextException());
  }

  private static final class UntouchableCause extends RuntimeException {
    private static final long serialVersionUID = 1L;
    private int causeReads;

    @Override
    public synchronized Throwable getCause() {
      causeReads++;
      throw new AssertionError("unknown primary getter must stay unselected");
    }
  }
}
