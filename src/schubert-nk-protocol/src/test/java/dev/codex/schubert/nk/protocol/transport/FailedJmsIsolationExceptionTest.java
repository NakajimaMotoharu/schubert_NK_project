package dev.codex.schubert.nk.protocol.transport;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import org.junit.jupiter.api.Test;

/** SS322§11; PG-D442/BUG1494/YKT1254; PT-JMS-ISO009..012, literal/null/identity only. */
final class FailedJmsIsolationExceptionTest {
  private static final String PROTOCOL_FAILURE_MESSAGE = "synthetic protocol";

  @Test
  void iso009PrimaryAndProtocolAreRequired() {
    var protocol = new PermanentProtocolException(PROTOCOL_FAILURE_MESSAGE);
    assertThrows(NullPointerException.class, () -> new FailedJmsIsolationException(null, protocol));
    assertThrows(NullPointerException.class, () -> new FailedJmsIsolationException(protocol, null));
  }

  @Test
  void iso010SameNodeIsRetainedWithoutSelfSuppression() {
    var protocol = new PermanentProtocolException(PROTOCOL_FAILURE_MESSAGE);
    var observed = new FailedJmsIsolationException(protocol, protocol);
    assertSame(protocol, observed.getCause());
    assertEquals(0, observed.getSuppressed().length);
    assertEquals(0, protocol.getSuppressed().length);
    assertEquals("JMS permanent message isolation failed", observed.getMessage());
  }

  @Test
  void iso011EqualsTrueDoesNotHideDistinctProtocolIdentity() {
    var primary = new EqualFailure();
    var protocol = new PermanentProtocolException(PROTOCOL_FAILURE_MESSAGE);
    assertEquals(primary, protocol);
    assertNotSame(primary, protocol);
    var observed = new FailedJmsIsolationException(primary, protocol);
    assertSame(primary, observed.getCause());
    assertArrayEquals(new Throwable[] {protocol}, observed.getSuppressed());
  }

  @Test
  void iso012DisabledPrimarySuppressionCannotHideProtocol() {
    var primary = new SuppressionDisabledFailure();
    var protocol = new PermanentProtocolException(PROTOCOL_FAILURE_MESSAGE);
    var observed = new FailedJmsIsolationException(primary, protocol);
    assertSame(primary, observed.getCause());
    assertEquals(0, primary.getSuppressed().length);
    assertArrayEquals(new Throwable[] {protocol}, observed.getSuppressed());
  }

  private static final class EqualFailure extends RuntimeException {
    private static final long serialVersionUID = 1L;

    @Override
    public boolean equals(Object other) {
      return other instanceof PermanentProtocolException || other instanceof EqualFailure;
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
