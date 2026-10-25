package dev.codex.schubert.nk.protocol.transport;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** SS321§7; PG-D441/BUG1489; UNC005..008: independent identity/null contract. */
final class UnconfirmedJmsRollbackExceptionTest {
  @Test
  void primaryAndRollbackMustBothBePresent() {
    var failure = new IllegalStateException("synthetic");
    assertThrows(
        NullPointerException.class, () -> new UnconfirmedJmsRollbackException(null, failure));
    assertThrows(
        NullPointerException.class, () -> new UnconfirmedJmsRollbackException(failure, null));
  }

  @Test
  void sameNodeIsRetainedOnceWithoutSelfSuppression() {
    var primary = new IllegalStateException("synthetic");
    var observed = new UnconfirmedJmsRollbackException(primary, primary);
    assertSame(primary, observed.getCause());
    assertEquals(0, observed.getSuppressed().length);
    assertEquals(0, primary.getSuppressed().length);
    assertEquals("JMS receiver rollback unconfirmed", observed.getMessage());
  }

  @Test
  void distinctEqualValuedNodesAreBothRetained() {
    var primary = new EqualFailure();
    var rollback = new EqualFailure();
    assertEquals(primary, rollback);
    assertNotSame(primary, rollback);
    var observed = new UnconfirmedJmsRollbackException(primary, rollback);
    assertSame(primary, observed.getCause());
    assertEquals(1, observed.getSuppressed().length);
    assertSame(rollback, observed.getSuppressed()[0]);
  }

  @Test
  void disabledPrimarySuppressionDoesNotHideRollbackFailure() {
    var primary = new SuppressionDisabledFailure();
    var rollback = new IllegalStateException("synthetic rollback");
    var observed = new UnconfirmedJmsRollbackException(primary, rollback);
    assertSame(primary, observed.getCause());
    assertEquals(0, primary.getSuppressed().length);
    assertArrayEquals(new Throwable[] {rollback}, observed.getSuppressed());
  }

  private static final class EqualFailure extends RuntimeException {
    private static final long serialVersionUID = 1L;

    @Override
    public boolean equals(Object other) {
      return other instanceof EqualFailure;
    }

    @Override
    public int hashCode() {
      return 1;
    }
  }

  private static final class SuppressionDisabledFailure extends RuntimeException {
    private static final long serialVersionUID = 1L;

    SuppressionDisabledFailure() {
      super("synthetic primary", null, false, false);
    }
  }
}
