package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/OPS009/DAT009/UI251/SS332,352; BUG2757/YKT2359; JDBC2757001..008. */
final class JdbcResourceFailuresTest {
  private static final String TRANSIENT = "SYNTHETIC_TRANSIENT_DIAGNOSTIC";
  private static final String FIXED = "batch repository operation failed";

  @Test
  void absentPrimarySelectsCleanup() {
    for (Throwable cleanup :
        List.of(new SQLException(TRANSIENT), new IllegalStateException(), new AssertionError())) {
      assertTrue(JdbcResourceFailures.replace(null, cleanup));
      assertEquals(0, cleanup.getSuppressed().length);
    }
  }

  @Test
  void nonfatalSqlPairAndCyclesRemainKnown() {
    var primary = new SQLException(TRANSIENT);
    var linked = new SQLException(TRANSIENT);
    primary.initCause(linked);
    linked.initCause(primary);
    primary.addSuppressed(linked);
    primary.setNextException(linked);
    var cleanup = new SqlCycle();
    assertFalse(JdbcResourceFailures.replace(primary, cleanup));
    assertEquals(1, primary.getSuppressed().length);
    assertSame(linked, primary.getSuppressed()[0]);
    assertSame(linked, primary.getCause());
    assertSame(primary, linked.getCause());
    assertSame(cleanup, cleanup.getNextException());
    assertEquals(0, cleanup.getSuppressed().length);
  }

  @Test
  void unknownCleanupSelectionPrecedesKnownGraphClassification() {
    for (Throwable cleanup :
        List.of(new IllegalStateException(), new NullPointerException(), new AssertionError())) {
      var hidden = new AssertionError(TRANSIENT);
      var primary = new SQLException(TRANSIENT, hidden);
      assertTrue(JdbcResourceFailures.replace(primary, cleanup));
      assertSame(hidden, primary.getCause());
      assertEquals(0, primary.getSuppressed().length);
      assertEquals(0, cleanup.getSuppressed().length);
    }
  }

  @Test
  void unknownPrimaryKeepsIdentityWithFreshFixedSecondary() {
    for (int kind = 0; kind < 5; kind++) {
      for (Throwable cleanup :
          List.of(new SQLException(TRANSIENT), new IllegalStateException(), new AssertionError())) {
        Throwable primary = unknown(kind);
        assertFalse(JdbcResourceFailures.replace(primary, cleanup));
        Throwable fixed = primary.getSuppressed()[0];
        assertEquals(1, primary.getSuppressed().length);
        assertInstanceOf(BatchRepositoryException.class, fixed);
        assertEquals(FIXED, fixed.getMessage());
        assertNull(fixed.getCause());
        assertEquals(0, fixed.getSuppressed().length);
        assertNotSame(primary, fixed);
        assertNotSame(cleanup, fixed);
        assertEquals(0, cleanup.getSuppressed().length);
      }
    }
  }

  @Test
  void fatalPrimaryCauseSuppressedAndNextRetainIdentity() {
    for (int edge = 0; edge < 3; edge++) {
      var fatal = new AssertionError(TRANSIENT);
      var primary = graph(edge, fatal);
      var cleanup = new SQLException(TRANSIENT);
      assertSame(
          fatal, assertThrows(Error.class, () -> JdbcResourceFailures.replace(primary, cleanup)));
      assertEquals(edge == 1 ? 1 : 0, primary.getSuppressed().length);
      assertEquals(0, cleanup.getSuppressed().length);
    }
  }

  @Test
  void fatalCleanupCauseSuppressedAndNextRetainIdentity() {
    for (int edge = 0; edge < 3; edge++) {
      var fatal = new AssertionError(TRANSIENT);
      var primary = new SQLException(TRANSIENT);
      var cleanup = graph(edge, fatal);
      assertSame(
          fatal, assertThrows(Error.class, () -> JdbcResourceFailures.replace(primary, cleanup)));
      assertEquals(0, primary.getSuppressed().length);
      assertEquals(edge == 1 ? 1 : 0, cleanup.getSuppressed().length);
    }
  }

  @Test
  void knownPairPrimaryGraphPriorityIsStableAcrossCalls() {
    var first = new AssertionError("SYNTHETIC_FIRST");
    var second = new AssertionError("SYNTHETIC_SECOND");
    var primary = new SQLException(TRANSIENT, first);
    var cleanup = new SQLException(TRANSIENT, second);
    for (int attempt = 0; attempt < 2; attempt++) {
      assertSame(
          first, assertThrows(Error.class, () -> JdbcResourceFailures.replace(primary, cleanup)));
      assertSame(first, primary.getCause());
      assertSame(second, cleanup.getCause());
      assertEquals(0, primary.getSuppressed().length);
      assertEquals(0, cleanup.getSuppressed().length);
    }
  }

  @Test
  void repeatedIdentityAndSuppressionDisabledStayNonSuccessful() {
    var sql = new SQLException(TRANSIENT);
    assertFalse(JdbcResourceFailures.replace(sql, sql));
    assertEquals(0, sql.getSuppressed().length);
    var unknown = new IllegalStateException();
    assertFalse(JdbcResourceFailures.replace(unknown, unknown));
    Throwable first = unknown.getSuppressed()[0];
    assertInstanceOf(BatchRepositoryException.class, first);
    assertNotSame(unknown, first);
    assertFalse(JdbcResourceFailures.replace(unknown, unknown));
    assertEquals(2, unknown.getSuppressed().length);
    assertNotSame(first, unknown.getSuppressed()[1]);
    assertEquals(FIXED, unknown.getSuppressed()[1].getMessage());
    var disabled = new SuppressionDisabled();
    assertFalse(JdbcResourceFailures.replace(disabled, disabled));
    assertEquals(0, disabled.getSuppressed().length);
  }

  private static Throwable unknown(int kind) {
    return switch (kind) {
      case 0 -> new IllegalStateException();
      case 1 -> new NullPointerException();
      case 2 -> new AssertionError();
      case 3 -> new BatchRepositoryException();
      case 4 -> new IOException(TRANSIENT);
      default -> throw new IllegalArgumentException("unknown fixture kind");
    };
  }

  private static SQLException graph(int edge, Error fatal) {
    var sql = new SQLException(TRANSIENT);
    switch (edge) {
      case 0 -> sql.initCause(fatal);
      case 1 -> sql.addSuppressed(fatal);
      case 2 -> sql.setNextException(new SQLException(TRANSIENT, fatal));
      default -> throw new IllegalArgumentException("unknown fixture edge");
    }
    return sql;
  }

  private static final class SqlCycle extends SQLException {
    private static final long serialVersionUID = 1L;

    @Override
    public SQLException getNextException() {
      return this;
    }
  }

  private static final class SuppressionDisabled extends RuntimeException {
    private static final long serialVersionUID = 1L;

    SuppressionDisabled() {
      super(TRANSIENT, null, false, false);
    }
  }
}
