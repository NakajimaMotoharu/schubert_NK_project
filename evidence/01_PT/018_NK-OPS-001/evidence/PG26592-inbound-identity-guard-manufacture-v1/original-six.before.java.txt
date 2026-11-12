package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.Message;
import jakarta.jms.Queue;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-JMS-INPORT001..006. Own interface ports only; no provider, broker or message-body read. */
final class InboundTransactionPortTest {
  private static final String SEND = "send";
  private static final String COMMIT = "commit";
  private static final String ROLLBACK = "rollback";
  private static final String ATTEMPTED = "attempted";
  private static final String CONFIRMED = "confirmed";
  private static final String READ = "read";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-11-05T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void defaultAndObservedIsolationSendSameSanitizedHandleThenCommitWithoutRollback()
      throws Exception {
    for (boolean observed : new boolean[] {false, true}) {
      Fixture fixture = new Fixture();
      Message original = fixture.message();
      var protocol = protocol();
      if (observed) isolate(fixture, original, protocol);
      else
        InboundTransactions.isolateFatal(
            fixture.context(),
            original,
            BrokerTopology.SYNC_REQUEST,
            FatalDlqMetadata.DetectedBy.API_SYNC,
            CLOCK,
            protocol);
      assertSame(original, fixture.sent);
      assertEquals("nk.dead.letter::nk.dead.letter.q", fixture.queue);
      assertEquals(DeliveryMode.PERSISTENT, fixture.deliveryMode);
      assertEquals(0L, fixture.ttl);
      assertEquals(List.of(SEND, COMMIT), fixture.events);
      assertEquals(1, fixture.sends);
      assertEquals(1, fixture.commits);
      assertEquals(0, fixture.rollbacks);
      assertEquals("PROTOCOL_INVALID", fixture.properties.get("NKErrorCode"));
      assertEquals("API_SYNC", fixture.properties.get("NKDetectedBy"));
      assertEquals("2026-11-05T00:00:00Z", fixture.properties.get("NKDetectedAt"));
      assertEquals("nk.sync.request", fixture.properties.get("_AMQ_ORIG_ADDRESS"));
      assertEquals("nk.sync.request.q", fixture.properties.get("_AMQ_ORIG_QUEUE"));
      assertEquals(1, fixture.properties.get("NKDeliveryCount"));
      assertEquals(10, fixture.properties.size());
      assertEquals(0, protocol.getSuppressed().length);
    }
  }

  @Test
  void checkedReadAndRuntimeSendOrCommitFailuresRollbackOnceWithoutResending() {
    for (String point : List.of(READ, SEND, COMMIT)) {
      Fixture fixture = new Fixture();
      Throwable failure =
          point.equals(READ)
              ? new JMSException("own read failure")
              : new IllegalStateException("own operation failure");
      fixture.faults = Map.of(point, failure);
      var protocol = protocol();
      var actual =
          assertThrows(
              FailedJmsIsolationException.class,
              () -> isolate(fixture, fixture.message(), protocol));
      assertSame(failure, actual.getCause());
      assertSame(protocol, actual.getSuppressed()[0]);
      assertSame(protocol, failure.getSuppressed()[0]);
      assertEquals(point.equals(READ) ? 0 : 1, fixture.sends);
      assertEquals(point.equals(COMMIT) ? 1 : 0, fixture.commits);
      assertEquals(1, fixture.rollbacks);
      assertEquals(
          List.of(ATTEMPTED, ROLLBACK, CONFIRMED),
          fixture.events.subList(fixture.events.size() - 3, fixture.events.size()));
    }
  }

  @Test
  void isolationRollbackFailureRetainsBothPhasesAndNeverConfirms() {
    for (boolean fatal : new boolean[] {false, true}) {
      Fixture fixture = new Fixture();
      var isolation = new IllegalStateException("own isolation failure");
      Throwable rollback =
          fatal
              ? new AssertionError("own rollback Error")
              : new IllegalStateException("own rollback failure");
      fixture.faults = Map.of(SEND, isolation, ROLLBACK, rollback);
      var protocol = protocol();
      if (fatal) {
        assertSame(
            rollback,
            assertThrows(
                AssertionError.class, () -> isolate(fixture, fixture.message(), protocol)));
      } else {
        var actual =
            assertThrows(
                FailedJmsIsolationException.class,
                () -> isolate(fixture, fixture.message(), protocol));
        var unconfirmed = (UnconfirmedJmsRollbackException) actual.getCause();
        assertSame(isolation, unconfirmed.getCause());
        assertSame(rollback, unconfirmed.getSuppressed()[0]);
        assertSame(protocol, actual.getSuppressed()[0]);
        assertSame(protocol, isolation.getSuppressed()[0]);
        assertSame(rollback, isolation.getSuppressed()[1]);
      }
      assertEquals(List.of(SEND, ATTEMPTED, ROLLBACK), fixture.events);
      assertEquals(0, fixture.commits);
      assertEquals(1, fixture.rollbacks);
    }
  }

  @Test
  void observerNullContractsRejectBeforeAnyContextOrMessageOperation() {
    Fixture fixture = new Fixture();
    assertThrows(
        NullPointerException.class,
        () ->
            InboundTransactions.rollbackAfterFailure(
                fixture.context(), protocol(), null, () -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            InboundTransactions.rollbackAfterFailure(
                fixture.context(), protocol(), () -> {}, null));
    assertThrows(
        NullPointerException.class,
        () ->
            InboundTransactions.isolateFatal(
                fixture.context(),
                fixture.message(),
                BrokerTopology.SYNC_REQUEST,
                FatalDlqMetadata.DetectedBy.API_SYNC,
                CLOCK,
                protocol(),
                null,
                () -> {}));
    assertThrows(
        NullPointerException.class,
        () ->
            InboundTransactions.isolateFatal(
                fixture.context(),
                fixture.message(),
                BrokerTopology.SYNC_REQUEST,
                FatalDlqMetadata.DetectedBy.API_SYNC,
                CLOCK,
                protocol(),
                () -> {},
                null));
    assertEquals(0, fixture.contextCalls);
    assertEquals(0, fixture.messageCalls);
    assertTrue(fixture.events.isEmpty());
  }

  @Test
  void observerFailuresPropagateIdentityAtTheirDeclaredSequenceBoundary() {
    for (boolean before : new boolean[] {false, true}) {
      for (Throwable failure :
          List.of(
              new IllegalStateException("own observer failure"),
              new AssertionError("own observer Error"))) {
        Fixture fixture = new Fixture();
        Runnable throwing =
            () -> {
              if (failure instanceof Error error) throw error;
              throw (RuntimeException) failure;
            };
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () ->
                    InboundTransactions.rollbackAfterFailure(
                        fixture.context(),
                        protocol(),
                        before ? throwing : () -> fixture.events.add(ATTEMPTED),
                        before ? () -> fixture.events.add(CONFIRMED) : throwing)));
        assertEquals(before ? 0 : 1, fixture.rollbacks);
        assertEquals(0, fixture.commits);
        assertEquals(before ? List.of() : List.of(ATTEMPTED, ROLLBACK), fixture.events);
      }
    }
  }

  @Test
  void successfulDefaultAndObservedRollbackOnlyNotifyAfterProviderReturns() {
    Fixture plain = new Fixture();
    InboundTransactions.rollbackAfterFailure(plain.context(), protocol());
    assertEquals(List.of(ROLLBACK), plain.events);
    assertEquals(1, plain.rollbacks);
    Fixture observed = new Fixture();
    InboundTransactions.rollbackAfterFailure(
        observed.context(),
        protocol(),
        () -> observed.events.add(ATTEMPTED),
        () -> observed.events.add(CONFIRMED));
    assertEquals(List.of(ATTEMPTED, ROLLBACK, CONFIRMED), observed.events);
    assertEquals(1, observed.rollbacks);
    assertEquals(0, observed.commits);
  }

  private static PermanentProtocolException protocol() {
    return new PermanentProtocolException("own invalid wire fixture");
  }

  private static void isolate(
      Fixture fixture, Message message, PermanentProtocolException protocol) {
    InboundTransactions.isolateFatal(
        fixture.context(),
        message,
        BrokerTopology.SYNC_REQUEST,
        FatalDlqMetadata.DetectedBy.API_SYNC,
        CLOCK,
        protocol,
        () -> fixture.events.add(ATTEMPTED),
        () -> fixture.events.add(CONFIRMED));
  }

  private static final class Fixture {
    final List<String> events = new ArrayList<>();
    final Map<String, Object> properties = new HashMap<>();
    Map<String, Throwable> faults = Map.of();
    Message sent;
    String queue;
    int deliveryMode;
    long ttl = -1;
    int sends;
    int commits;
    int rollbacks;
    int contextCalls;
    int messageCalls;

    void event(String point) throws Throwable {
      events.add(point);
      Throwable failure = faults.get(point);
      if (failure != null) throw failure;
    }

    JMSContext context() {
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (proxy, method, args) -> {
                contextCalls++;
                return switch (method.getName()) {
                  case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                  case ROLLBACK -> {
                    rollbacks++;
                    event(ROLLBACK);
                    yield null;
                  }
                  case COMMIT -> {
                    commits++;
                    event(COMMIT);
                    yield null;
                  }
                  case "createProducer" -> producer();
                  default -> throw new AssertionError("unexpected borrowed context operation");
                };
              });
    }

    JMSProducer producer() {
      return (JMSProducer)
          Proxy.newProxyInstance(
              JMSProducer.class.getClassLoader(),
              new Class<?>[] {JMSProducer.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "setDeliveryMode" -> {
                    deliveryMode = (Integer) args[0];
                    yield proxy;
                  }
                  case "setTimeToLive" -> {
                    ttl = (Long) args[0];
                    yield proxy;
                  }
                  case SEND -> {
                    queue = ((Queue) args[0]).getQueueName();
                    sent = (Message) args[1];
                    sends++;
                    event(SEND);
                    yield proxy;
                  }
                  default -> throw new AssertionError("unexpected borrowed producer operation");
                };
              });
    }

    Message message() {
      return (Message)
          Proxy.newProxyInstance(
              Message.class.getClassLoader(),
              new Class<?>[] {Message.class},
              (proxy, method, args) -> {
                messageCalls++;
                return switch (method.getName()) {
                  case "getJMSMessageID" -> {
                    Throwable failure = faults.get(READ);
                    if (failure != null) throw failure;
                    yield null;
                  }
                  case "getStringProperty", "getJMSCorrelationID" -> null;
                  case "propertyExists" -> false;
                  case "clearProperties" -> {
                    properties.clear();
                    yield null;
                  }
                  case "setStringProperty", "setIntProperty" -> {
                    properties.put((String) args[0], args[1]);
                    yield null;
                  }
                  case "setJMSCorrelationID", "setJMSReplyTo", "setJMSType" -> null;
                  default ->
                      throw new AssertionError("message body or unsupported operation accessed");
                };
              });
    }
  }
}
