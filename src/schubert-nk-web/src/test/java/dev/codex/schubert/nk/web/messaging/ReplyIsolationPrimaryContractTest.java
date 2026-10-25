package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.Message;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;

/** SS312/321/352; BUG1485/YKT1245; PT-JMS-PRE006..007. No broker/DB/runtime operation. */
final class ReplyIsolationPrimaryContractTest {
  @Test
  void jmsP006SameProtocolIsolationFailureNeverSelfSuppressesOrCommits() {
    var protocol = new PermanentProtocolException("synthetic protocol");
    var fixture = new Fixture(protocol, protocol);
    assertSame(
        protocol,
        assertThrows(
                FailedJmsIsolationException.class,
                () -> fixture.consumer().onMessage(fixture.context(), fixture.message()))
            .getCause());
    assertEquals(1, fixture.rollbacks);
    assertEquals(0, fixture.commits);
    assertEquals(0, protocol.getSuppressed().length);
  }

  @Test
  void jmsP007DistinctIsolationFailureRetainsProtocolAndNeverCommits() {
    var protocol = new PermanentProtocolException("synthetic protocol");
    var isolation = new IllegalStateException("synthetic isolation");
    var fixture = new Fixture(protocol, isolation);
    assertSame(
        isolation,
        assertThrows(
                FailedJmsIsolationException.class,
                () -> fixture.consumer().onMessage(fixture.context(), fixture.message()))
            .getCause());
    assertEquals(1, fixture.rollbacks);
    assertEquals(0, fixture.commits);
    assertEquals(1, isolation.getSuppressed().length);
    assertSame(protocol, isolation.getSuppressed()[0]);
  }

  private static final class Fixture {
    private final PermanentProtocolException protocol;
    private final RuntimeException isolation;
    private int rollbacks;
    private int commits;

    Fixture(PermanentProtocolException protocol, RuntimeException isolation) {
      this.protocol = protocol;
      this.isolation = isolation;
    }

    ArtemisReplyConsumer consumer() {
      Clock clock = Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);
      return new ArtemisReplyConsumer(
          new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 1),
          new JmsReplyDecoder(),
          new ArtemisReplyDlqSender(clock));
    }

    Message message() {
      return (Message)
          Proxy.newProxyInstance(
              BytesMessage.class.getClassLoader(),
              new Class<?>[] {BytesMessage.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getBodyLength" -> throw protocol;
                    case "getJMSMessageID", "getStringProperty", "getJMSCorrelationID" -> null;
                    case "propertyExists" -> false;
                    case "clearProperties",
                        "setJMSCorrelationID",
                        "setJMSReplyTo",
                        "setJMSType",
                        "setStringProperty",
                        "setIntProperty" ->
                        null;
                    default -> throw new AssertionError("unexpected synthetic reply operation");
                  });
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
                    return null;
                  case "commit":
                    commits++;
                    throw new AssertionError("failed reply isolation must never commit");
                  case "createProducer":
                    throw isolation;
                  default:
                    throw new AssertionError("unexpected synthetic reply context operation");
                }
              });
    }
  }
}
