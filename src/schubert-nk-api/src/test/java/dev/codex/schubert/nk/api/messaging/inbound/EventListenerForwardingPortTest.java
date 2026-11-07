package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/**
 * PT-JMS-PORT-001..006: supplied-interface forwarding; no provider, broker or business processor.
 * Trace: RD MQ-006..010/ASY-002/MON-003; UI213/231/235/236; SS312/321/322/323.
 */
@Timeout(10)
final class EventListenerForwardingPortTest {
  private static final String PHASE_MODE = "mode";
  private static final String PHASE_PROCESS = "process";
  private static final String PHASE_COMMIT = "commit";
  private static final String PHASE_ATTEMPTED = "attempted";
  private static final String PHASE_ROLLBACK = "rollback";
  private static final String PHASE_CONFIRMED = "confirmed";
  private static final String QUESTION_LAYOUT = "QWKREQ01";
  private static final String LOG_LAYOUT = "WLGEVT01";
  private static final String QUESTION_ADDRESS = "nk.async.work";
  private static final String LOG_ADDRESS = "nk.web.log";
  private static final String MESSAGE_ID = "00000000-0000-0000-0000-000000000071";
  private static final String CORRELATION_ID = "00000000-0000-0000-0000-000000000072";
  private static final String TRANSPORT_ID = "ID:synthetic-event-port";
  private static final String VERSION = "001";
  private static final String TIMESTAMP = "20261108090000000";
  private static final Instant RECEIVED = Instant.parse("2026-11-08T00:00:01Z");
  private static final Clock CLOCK = Clock.fixed(RECEIVED, ZoneOffset.UTC);

  @Test
  void port001QuestionPublicEntryForwardsDeliveryAndExactGoldenData() throws JMSException {
    var port = new Port(JMSContext.SESSION_TRANSACTED);
    var observed = new ArrayList<DeliveryMetadata>();
    InternalEventProcessor processor =
        new InternalEventProcessor() {
          @Override
          public void process(WireMessage<FixedPayload> event) {
            throw new AssertionError("delivery-aware entry must be used");
          }

          @Override
          public void process(WireMessage<FixedPayload> event, DeliveryMetadata delivery) {
            assertEvent(event, true);
            observed.add(delivery);
            port.order.add(PHASE_PROCESS);
          }
        };
    new QuestionWorkListener(processor, CLOCK).onMessage(port.context(), message(true));
    assertEquals(1, observed.size());
    assertEquals(3, observed.getFirst().deliveryCount());
    assertEquals(TRANSPORT_ID, observed.getFirst().transportMessageId());
    assertEquals(RECEIVED, observed.getFirst().receivedAt());
    assertEquals(List.of(PHASE_MODE, PHASE_PROCESS, PHASE_COMMIT), port.order);
  }

  @Test
  void port002WebLogPublicEntryForwardsLegacyProcessorAndExactGoldenData() throws JMSException {
    var port = new Port(JMSContext.SESSION_TRANSACTED);
    new WebLogListener(
            event -> {
              assertEvent(event, false);
              port.order.add(PHASE_PROCESS);
            },
            CLOCK)
        .onMessage(port.context(), message(false));
    assertEquals(List.of(PHASE_MODE, PHASE_PROCESS, PHASE_COMMIT), port.order);
  }

  @Test
  void port003BothObserverEntriesCommitEachCallerDeliveryWithoutRollbackNotifications()
      throws JMSException {
    for (boolean question : List.of(true, false)) {
      var port = new Port(JMSContext.SESSION_TRANSACTED);
      InternalEventProcessor processor =
          event -> {
            assertEvent(event, question);
            port.order.add(PHASE_PROCESS);
          };
      var work = new QuestionWorkListener(processor, CLOCK);
      var log = new WebLogListener(processor, CLOCK);
      var context = port.context();
      var input = message(question);
      Runnable attempted = () -> port.order.add(PHASE_ATTEMPTED);
      Runnable confirmed = () -> port.order.add(PHASE_CONFIRMED);
      for (int delivery = 0; delivery < 2; delivery++) {
        if (question) work.onMessage(context, input, attempted, confirmed);
        else log.onMessage(context, input, attempted, confirmed);
      }
      assertEquals(
          List.of(PHASE_MODE, PHASE_PROCESS, PHASE_COMMIT, PHASE_MODE, PHASE_PROCESS, PHASE_COMMIT),
          port.order);
    }
  }

  @Test
  void port004NullContractsRejectBeforeAnyMessageOrTransactionOperation() {
    InternalEventProcessor unused =
        event -> {
          throw new AssertionError("unexpected processor");
        };
    assertThrows(NullPointerException.class, () -> new QuestionWorkListener(null, CLOCK));
    assertThrows(NullPointerException.class, () -> new QuestionWorkListener(unused, null));
    assertThrows(NullPointerException.class, () -> new WebLogListener(null, CLOCK));
    assertThrows(NullPointerException.class, () -> new WebLogListener(unused, null));
    for (boolean question : List.of(true, false)) {
      var port = new Port(JMSContext.SESSION_TRANSACTED);
      var context = port.context();
      var input = message(question);
      var work = new QuestionWorkListener(unused, CLOCK);
      var log = new WebLogListener(unused, CLOCK);
      Runnable noOp = () -> {};
      if (question) {
        assertThrows(NullPointerException.class, () -> work.onMessage(null, input));
        assertThrows(NullPointerException.class, () -> work.onMessage(context, null));
        assertThrows(NullPointerException.class, () -> work.onMessage(context, input, null, noOp));
        assertThrows(NullPointerException.class, () -> work.onMessage(context, input, noOp, null));
      } else {
        assertThrows(NullPointerException.class, () -> log.onMessage(null, input));
        assertThrows(NullPointerException.class, () -> log.onMessage(context, null));
        assertThrows(NullPointerException.class, () -> log.onMessage(context, input, null, noOp));
        assertThrows(NullPointerException.class, () -> log.onMessage(context, input, noOp, null));
      }
      assertTrue(port.order.isEmpty());
    }
  }

  @Test
  void port005NonTransactedContextsRejectBeforeBodyBusinessOrRollback() {
    InternalEventProcessor unused =
        event -> {
          throw new AssertionError("unexpected processor");
        };
    for (boolean question : List.of(true, false)) {
      var port = new Port(JMSContext.AUTO_ACKNOWLEDGE);
      var context = port.context();
      var input = message(question);
      if (question)
        assertThrows(
            IllegalStateException.class,
            () -> new QuestionWorkListener(unused, CLOCK).onMessage(context, input));
      else
        assertThrows(
            IllegalStateException.class,
            () -> new WebLogListener(unused, CLOCK).onMessage(context, input));
      assertEquals(List.of(PHASE_MODE), port.order);
    }
  }

  @Test
  void port006BusinessFailurePreservesIdentityAndConfirmsRollbackInOrder() {
    for (boolean question : List.of(true, false)) {
      var port = new Port(JMSContext.SESSION_TRANSACTED);
      var failure = new IllegalStateException("synthetic processor failure");
      InternalEventProcessor processor =
          event -> {
            assertEvent(event, question);
            port.order.add(PHASE_PROCESS);
            throw failure;
          };
      var context = port.context();
      var input = message(question);
      Runnable attempted = () -> port.order.add(PHASE_ATTEMPTED);
      Runnable confirmed = () -> port.order.add(PHASE_CONFIRMED);
      if (question) {
        var listener = new QuestionWorkListener(processor, CLOCK);
        assertSame(
            failure,
            assertThrows(
                IllegalStateException.class,
                () -> listener.onMessage(context, input, attempted, confirmed)));
      } else {
        var listener = new WebLogListener(processor, CLOCK);
        assertSame(
            failure,
            assertThrows(
                IllegalStateException.class,
                () -> listener.onMessage(context, input, attempted, confirmed)));
      }
      assertEquals(
          List.of(PHASE_MODE, PHASE_PROCESS, PHASE_ATTEMPTED, PHASE_ROLLBACK, PHASE_CONFIRMED),
          port.order);
      assertEquals(0, failure.getSuppressed().length);
    }
  }

  private static void assertEvent(WireMessage<FixedPayload> event, boolean question) {
    assertEquals(question ? QUESTION_LAYOUT : LOG_LAYOUT, event.header().layoutId().value());
    assertEquals('E', event.header().messageKind().wireValue());
    assertEquals('I', event.header().interactionKind().wireValue());
    assertEquals(MESSAGE_ID, event.header().messageId().toString());
    assertEquals(CORRELATION_ID, event.header().correlationId().toString());
    assertEquals(Instant.parse("2026-11-08T00:00:00Z"), event.header().sentAt());
    assertEquals(question ? 320 : 2336, event.header().totalLength());
    assertEquals(0, event.payload().recordCount());
    assertEquals(0, event.payload().recordLength());
    assertArrayEquals(data(question), event.payload().copyData());
    byte[] callerCopy = event.payload().copyData();
    callerCopy[0] = '!';
    assertArrayEquals(data(question), event.payload().copyData());
  }

  // Independent SS322/323 literal offsets, zero-based here; no Production encoder/layout lookup.
  private static byte[] data(boolean question) {
    byte[] bytes = new byte[question ? 64 : 2080];
    Arrays.fill(bytes, (byte) ' ');
    if (question) {
      ascii(bytes, 0, "00000000000000000000000001");
      ascii(bytes, 26, "000000000061");
      ascii(bytes, 38, "000000000062");
    } else {
      ascii(bytes, 0, TIMESTAMP);
      ascii(bytes, 17, "REQUEST");
      ascii(bytes, 33, "INFO");
      ascii(bytes, 105, "HTTP request completed");
      ascii(bytes, 617, "00000000-0000-0000-0000-000000000073");
      ascii(bytes, 653, "GET");
      ascii(bytes, 661, "/login");
      ascii(bytes, 917, "200");
      ascii(bytes, 920, "0");
      ascii(bytes, 929, "127.0.0.1");
    }
    return bytes;
  }

  private static byte[] wire(boolean question) {
    byte[] payload = data(question);
    byte[] bytes = new byte[question ? 320 : 2336];
    Arrays.fill(bytes, (byte) ' ');
    ascii(bytes, 0, "SCHBNK01");
    ascii(bytes, 8, VERSION);
    ascii(bytes, 11, question ? QUESTION_LAYOUT : LOG_LAYOUT);
    ascii(bytes, 19, VERSION);
    ascii(bytes, 22, "EI");
    ascii(bytes, 24, MESSAGE_ID);
    ascii(bytes, 60, CORRELATION_ID);
    ascii(bytes, 96, TIMESTAMP);
    ascii(bytes, 177, "0256");
    ascii(bytes, 181, question ? "000064" : "002080");
    ascii(bytes, 187, "000000000000");
    ascii(bytes, 199, question ? "000000320" : "000002336");
    System.arraycopy(payload, 0, bytes, 256, payload.length);
    return bytes;
  }

  private static void ascii(byte[] bytes, int offset, String value) {
    byte[] part = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(part, 0, bytes, offset, part.length);
  }

  private static BytesMessage message(boolean question) {
    byte[] body = wire(question);
    var destination = new ActiveMQQueue(question ? QUESTION_ADDRESS : LOG_ADDRESS);
    return (BytesMessage)
        Proxy.newProxyInstance(
            BytesMessage.class.getClassLoader(),
            new Class<?>[] {BytesMessage.class},
            (proxy, method, args) ->
                switch (method.getName()) {
                  case "getBodyLength" -> (long) body.length;
                  case "getBody" -> {
                    assertSame(byte[].class, args[0]);
                    yield body.clone();
                  }
                  case "getJMSDestination" -> destination;
                  case "getJMSReplyTo" -> null;
                  case "getJMSMessageID" -> TRANSPORT_ID;
                  case "getJMSCorrelationID" -> CORRELATION_ID;
                  case "getJMSExpiration" -> 0L;
                  case "getJMSDeliveryMode" -> 2;
                  case "propertyExists" ->
                      List.of("JMSXDeliveryCount", "NKMessageID", "NKLayoutID", "NKProtocolVersion")
                          .contains(args[0]);
                  case "getIntProperty" -> {
                    assertEquals("JMSXDeliveryCount", args[0]);
                    yield 3;
                  }
                  case "getStringProperty" ->
                      switch ((String) args[0]) {
                        case "NKMessageID" -> MESSAGE_ID;
                        case "NKLayoutID" -> question ? QUESTION_LAYOUT : LOG_LAYOUT;
                        case "NKProtocolVersion" -> VERSION;
                        default -> throw new AssertionError("unexpected property");
                      };
                  default ->
                      throw new AssertionError("unexpected message operation: " + method.getName());
                });
  }

  private static final class Port {
    private final int mode;
    private final List<String> order = new ArrayList<>();

    Port(int mode) {
      this.mode = mode;
    }

    JMSContext context() {
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getSessionMode" -> {
                      order.add(PHASE_MODE);
                      yield mode;
                    }
                    case PHASE_COMMIT -> {
                      order.add(PHASE_COMMIT);
                      yield null;
                    }
                    case PHASE_ROLLBACK -> {
                      order.add(PHASE_ROLLBACK);
                      yield null;
                    }
                    default ->
                        throw new AssertionError(
                            "unexpected context operation: " + method.getName());
                  });
    }
  }
}
