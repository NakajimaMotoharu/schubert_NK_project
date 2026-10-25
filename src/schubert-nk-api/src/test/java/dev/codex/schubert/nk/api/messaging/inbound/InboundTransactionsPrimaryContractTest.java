package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.JMSContext;
import jakarta.jms.Message;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;

/** SS312/321/352; BUG1485/YKT1245; PT-JMS-PRE001..005, finite proxies only. */
final class InboundTransactionsPrimaryContractTest {
  @Test
  void jmsP001SameRollbackFailureNeverSelfSuppresses() {
    var primary = new IllegalStateException("synthetic primary");
    var fixture = new Fixture(primary, null);
    var observed =
        assertThrows(
            UnconfirmedJmsRollbackException.class,
            () -> InboundTransactions.rollbackAfterFailure(fixture.context(), primary));
    assertSame(primary, observed.getCause());
    assertEquals(0, observed.getSuppressed().length);
    assertEquals(1, fixture.rollbacks);
    assertEquals(0, fixture.commits);
    assertEquals(0, primary.getSuppressed().length);
  }

  @Test
  void jmsP002DistinctEqualsTrueRollbackFailureIsRetainedByIdentity() {
    var primary = new EqualFailure();
    var secondary = new EqualFailure();
    assertEquals(primary, secondary);
    assertNotSame(primary, secondary);
    var fixture = new Fixture(secondary, null);
    var observed =
        assertThrows(
            UnconfirmedJmsRollbackException.class,
            () -> InboundTransactions.rollbackAfterFailure(fixture.context(), primary));
    assertSame(primary, observed.getCause());
    assertSame(secondary, observed.getSuppressed()[0]);
    assertEquals(1, fixture.rollbacks);
    assertEquals(1, primary.getSuppressed().length);
    assertSame(secondary, primary.getSuppressed()[0]);
    assertEquals(0, fixture.commits);
  }

  @Test
  void jmsP003RollbackErrorRemainsFatalAndSameIdentity() {
    var fatal = new AssertionError("synthetic rollback fatal");
    var primary = new IllegalStateException("synthetic primary");
    var fixture = new Fixture(fatal, null);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> InboundTransactions.rollbackAfterFailure(fixture.context(), primary)));
    assertEquals(1, fixture.rollbacks);
    assertEquals(0, primary.getSuppressed().length);
    assertEquals(0, fixture.commits);
  }

  @Test
  void jmsP004SameProtocolIsolationFailureRemainsOriginalAndUncommitted() {
    var primary = new PermanentProtocolException("synthetic protocol");
    var fixture = new Fixture(null, primary);
    assertSame(
        primary,
        assertThrows(FailedJmsIsolationException.class, () -> isolate(fixture, primary))
            .getCause());
    assertEquals(1, fixture.rollbacks);
    assertEquals(0, fixture.commits);
    assertEquals(0, primary.getSuppressed().length);
  }

  @Test
  void jmsP005DistinctIsolationFailureRetainsProtocolAndNeverCommits() {
    var protocol = new PermanentProtocolException("synthetic protocol");
    var isolation = new IllegalStateException("synthetic isolation");
    var fixture = new Fixture(null, isolation);
    assertSame(
        isolation,
        assertThrows(FailedJmsIsolationException.class, () -> isolate(fixture, protocol))
            .getCause());
    assertEquals(1, fixture.rollbacks);
    assertEquals(0, fixture.commits);
    assertEquals(1, isolation.getSuppressed().length);
    assertSame(protocol, isolation.getSuppressed()[0]);
  }

  private static void isolate(Fixture fixture, PermanentProtocolException protocol)
      throws Exception {
    InboundTransactions.isolateFatal(
        fixture.context(),
        message(),
        BrokerTopology.SYNC_REQUEST,
        FatalDlqMetadata.DetectedBy.API_SYNC,
        Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC),
        protocol);
  }

  private static Message message() {
    return (Message)
        Proxy.newProxyInstance(
            Message.class.getClassLoader(),
            new Class<?>[] {Message.class},
            (proxy, method, args) ->
                switch (method.getName()) {
                  case "getJMSMessageID", "getStringProperty", "getJMSCorrelationID" -> null;
                  case "propertyExists" -> false;
                  case "clearProperties",
                      "setJMSCorrelationID",
                      "setJMSReplyTo",
                      "setJMSType",
                      "setStringProperty",
                      "setIntProperty" ->
                      null;
                  default -> throw new AssertionError("unexpected synthetic message operation");
                });
  }

  private static final class Fixture {
    private final Throwable rollbackFailure;
    private final RuntimeException sendFailure;
    private int rollbacks;
    private int commits;

    Fixture(Throwable rollbackFailure, RuntimeException sendFailure) {
      this.rollbackFailure = rollbackFailure;
      this.sendFailure = sendFailure;
    }

    JMSContext context() {
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "getSessionMode":
                    return JMSContext.SESSION_TRANSACTED;
                  case "rollback":
                    rollbacks++;
                    if (rollbackFailure != null) throw rollbackFailure;
                    return null;
                  case "commit":
                    commits++;
                    throw new AssertionError("failed isolation must never commit");
                  case "createProducer":
                    if (sendFailure == null)
                      throw new AssertionError("explicit isolation failure required");
                    throw sendFailure;
                  default:
                    throw new AssertionError("unexpected synthetic context operation");
                }
              });
    }
  }

  private static final class EqualFailure extends IllegalStateException {
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
}
