package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import dev.codex.schubert.nk.protocol.transport.FailedJmsIsolationException;
import dev.codex.schubert.nk.protocol.transport.UnconfirmedJmsRollbackException;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-JMS-TXP-001..009. RD MQ006..010/UI231/SS312,321,322. Supplied ports only. */
@Timeout(10)
final class EventTransactionPortTest {
  private static final String UNEXPECTED_PROCESSOR = "unexpected processor";
  private static final String MODE = "mode";
  private static final String PROCESS = "process";
  private static final String COMMIT = "commit";
  private static final String ROLLBACK = "rollback";
  private static final String ATTEMPTED = "attempted";
  private static final String CONFIRMED = "confirmed";
  private static final String SEND = "send";
  private static final String WORK_LAYOUT = "QWKREQ01";
  private static final String LOG_LAYOUT = "WLGEVT01";
  private static final String EVENT_ID = "00000000-0000-0000-0000-000000000081";
  private static final String CORRELATION_ID = "00000000-0000-0000-0000-000000000082";
  private static final String TRANSPORT_ID = "ID:synthetic-transaction-port";
  private static final String VERSION = "001";
  private static final String DEAD_LETTER_QUEUE = "nk.dead.letter::nk.dead.letter.q";
  private static final String ORIGINAL_TRANSPORT_PROPERTY = "NKOriginalTransportID";
  private static final Instant NOW = Instant.parse("2026-11-08T00:00:01Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);

  @Test
  void txp001BothRoutesDecodeLiteralGoldenAndCommitOnlyAfterProcessor() throws JMSException {
    for (boolean question : List.of(true, false)) {
      var s = new Scenario(question);
      var listener =
          listener(
              s,
              event -> {
                assertEquals(
                    question ? WORK_LAYOUT : LOG_LAYOUT, event.header().layoutId().value());
                assertEquals(EVENT_ID, event.header().messageId().toString());
                assertEquals(question ? 64 : 2080, event.payload().dataLength());
                assertArrayEquals(
                    Arrays.copyOfRange(s.body, 256, s.body.length), event.payload().copyData());
                s.order.add(PROCESS);
              },
              CLOCK);
      listener.onMessage(s.context(), s.message());
      assertEquals(List.of(MODE, PROCESS, COMMIT), s.order);
      assertEquals(1, s.bodyReads);
    }
  }

  @Test
  void txp002ConstructorRejectsNullDependenciesAndEveryNonEventDestination() {
    var s = new Scenario(true);
    InternalEventProcessor unused =
        event -> {
          throw new AssertionError(UNEXPECTED_PROCESSOR);
        };
    assertThrows(
        NullPointerException.class,
        () ->
            new TransactedEventListener(null, FatalDlqMetadata.DetectedBy.API_WORK, unused, CLOCK));
    assertThrows(
        NullPointerException.class,
        () -> new TransactedEventListener(BrokerTopology.ASYNC_WORK, null, unused, CLOCK));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransactedEventListener(
                BrokerTopology.ASYNC_WORK, FatalDlqMetadata.DetectedBy.API_WORK, null, CLOCK));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransactedEventListener(
                BrokerTopology.ASYNC_WORK, FatalDlqMetadata.DetectedBy.API_WORK, unused, null));
    for (BrokerTopology destination : BrokerTopology.values()) {
      if (destination == BrokerTopology.ASYNC_WORK || destination == BrokerTopology.WEB_LOG)
        continue;
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new TransactedEventListener(
                  destination, FatalDlqMetadata.DetectedBy.API_WORK, unused, CLOCK));
    }
    assertTrue(s.order.isEmpty());
  }

  @Test
  void txp003NullAndNonTransactedInputsHaveNoBodyBusinessOrRollbackEffects() {
    for (boolean question : List.of(true, false)) {
      var s = new Scenario(question);
      var listener =
          listener(
              s,
              event -> {
                throw new AssertionError(UNEXPECTED_PROCESSOR);
              },
              CLOCK);
      var context = s.context();
      var message = s.message();
      Runnable noop = () -> {};
      assertThrows(NullPointerException.class, () -> listener.onMessage(null, message));
      assertThrows(NullPointerException.class, () -> listener.onMessage(context, null));
      assertThrows(
          NullPointerException.class, () -> listener.onMessage(context, message, null, noop));
      assertThrows(
          NullPointerException.class, () -> listener.onMessage(context, message, noop, null));
      assertTrue(s.order.isEmpty());
      s.mode = JMSContext.AUTO_ACKNOWLEDGE;
      assertThrows(IllegalStateException.class, () -> listener.onMessage(context, message));
      assertEquals(List.of(MODE), s.order);
      assertEquals(0, s.bodyReads);
    }
  }

  @Test
  void txp004TransportFailureRollsBackOnceWithLegacyOrConfirmedCallbackPorts() {
    for (boolean legacy : List.of(true, false)) {
      var s = new Scenario(true);
      var failure = new JMSException("synthetic transport read failure");
      s.readFailure = failure;
      var listener =
          listener(
              s,
              event -> {
                throw new AssertionError(UNEXPECTED_PROCESSOR);
              },
              CLOCK);
      var context = s.context();
      var message = s.message();
      if (legacy) {
        assertSame(
            failure, assertThrows(JMSException.class, () -> listener.onMessage(context, message)));
        assertEquals(List.of(MODE, ROLLBACK), s.order);
      } else {
        assertSame(
            failure,
            assertThrows(
                JMSException.class,
                () ->
                    listener.onMessage(
                        context,
                        message,
                        () -> s.order.add(ATTEMPTED),
                        () -> s.order.add(CONFIRMED))));
        assertEquals(List.of(MODE, ATTEMPTED, ROLLBACK, CONFIRMED), s.order);
      }
      assertEquals(1, s.bodyReads);
      assertEquals(0, failure.getSuppressed().length);
    }
  }

  @Test
  void txp005ClockProcessorAndCommitFailuresPreserveIdentityAndRollbackPhase() {
    for (FailureSite site : FailureSite.values()) {
      var s = new Scenario(false);
      var failure = new IllegalStateException("synthetic stage failure");
      Clock clock = site == FailureSite.CLOCK ? new FailingClock(failure) : CLOCK;
      InternalEventProcessor processor =
          event -> {
            s.order.add(PROCESS);
            if (site == FailureSite.PROCESSOR) throw failure;
          };
      if (site == FailureSite.COMMIT) s.commitFailure = failure;
      var listener = listener(s, processor, clock);
      var context = s.context();
      var message = s.message();
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () ->
                  listener.onMessage(
                      context,
                      message,
                      () -> s.order.add(ATTEMPTED),
                      () -> s.order.add(CONFIRMED))));
      var expected = new ArrayList<>(List.of(MODE));
      if (site != FailureSite.CLOCK) expected.add(PROCESS);
      if (site == FailureSite.COMMIT) expected.add(COMMIT);
      expected.addAll(List.of(ATTEMPTED, ROLLBACK, CONFIRMED));
      assertEquals(expected, s.order);
      assertEquals(0, failure.getSuppressed().length);
    }
  }

  @Test
  void txp006PermanentProtocolFailureCommitsBodyPreservingIsolationAndSignalsTerminal() {
    for (boolean question : List.of(true, false)) {
      var s = new Scenario(question);
      s.body[0] = '!';
      byte[] before = s.body.clone();
      var listener =
          listener(
              s,
              event -> {
                throw new AssertionError(UNEXPECTED_PROCESSOR);
              },
              CLOCK);
      var context = s.context();
      var message = s.message();
      var failure =
          assertThrows(
              CommittedFatalInboundException.class, () -> listener.onMessage(context, message));
      assertInstanceOf(PermanentProtocolException.class, failure.getCause());
      assertEquals(List.of(MODE, MODE, SEND, COMMIT), s.order);
      assertArrayEquals(before, s.body);
      assertSame(message, s.sent);
      assertEquals(TRANSPORT_ID, s.properties.get(ORIGINAL_TRANSPORT_PROPERTY));
      assertIsolationProperties(s, question);
    }
  }

  @Test
  void txp007InvalidDeliveryMetadataIsIsolatedBeforeProcessorWithBoundedDiagnostic() {
    var s = new Scenario(true);
    s.transport = "x".repeat(129);
    var listener =
        listener(
            s,
            event -> {
              throw new AssertionError(UNEXPECTED_PROCESSOR);
            },
            CLOCK);
    var context = s.context();
    var message = s.message();
    var failure =
        assertThrows(
            CommittedFatalInboundException.class, () -> listener.onMessage(context, message));
    assertInstanceOf(PermanentProtocolException.class, failure.getCause());
    assertEquals(List.of(MODE, MODE, SEND, COMMIT), s.order);
    assertEquals("UNAVAILABLE", s.properties.get(ORIGINAL_TRANSPORT_PROPERTY));
    assertIsolationProperties(s, true);
  }

  @Test
  void txp008FailedIsolationPreservesPrimaryAndConfirmedRollbackWithoutCommitSuccess() {
    var s = new Scenario(false);
    s.body[0] = '!';
    var sendFailure = new IllegalStateException("synthetic isolation send failure");
    s.sendFailure = sendFailure;
    var listener =
        listener(
            s,
            event -> {
              throw new AssertionError(UNEXPECTED_PROCESSOR);
            },
            CLOCK);
    var context = s.context();
    var message = s.message();
    var failure =
        assertThrows(
            FailedJmsIsolationException.class,
            () ->
                listener.onMessage(
                    context, message, () -> s.order.add(ATTEMPTED), () -> s.order.add(CONFIRMED)));
    assertSame(sendFailure, failure.getCause());
    assertInstanceOf(PermanentProtocolException.class, sendFailure.getSuppressed()[0]);
    assertSame(sendFailure.getSuppressed()[0], failure.getSuppressed()[0]);
    assertEquals(List.of(MODE, MODE, SEND, ATTEMPTED, ROLLBACK, CONFIRMED), s.order);
  }

  @Test
  void txp009UnconfirmedRollbackRetainsUnknownPhaseAndNeverRetriesOrConfirms() {
    for (boolean isolation : List.of(true, false)) {
      var s = new Scenario(true);
      var rollbackFailure = new IllegalArgumentException("synthetic rollback failure");
      var primary = new IllegalStateException("synthetic operation failure");
      s.rollbackFailure = rollbackFailure;
      if (isolation) {
        s.body[0] = '!';
        s.sendFailure = primary;
      }
      var listener =
          listener(
              s,
              event -> {
                s.order.add(PROCESS);
                throw primary;
              },
              CLOCK);
      var context = s.context();
      var message = s.message();
      UnconfirmedJmsRollbackException unconfirmed;
      if (isolation) {
        var failure =
            assertThrows(
                FailedJmsIsolationException.class,
                () ->
                    listener.onMessage(
                        context,
                        message,
                        () -> s.order.add(ATTEMPTED),
                        () -> s.order.add(CONFIRMED)));
        unconfirmed = assertInstanceOf(UnconfirmedJmsRollbackException.class, failure.getCause());
        assertEquals(List.of(MODE, MODE, SEND, ATTEMPTED, ROLLBACK), s.order);
      } else {
        unconfirmed =
            assertThrows(
                UnconfirmedJmsRollbackException.class,
                () ->
                    listener.onMessage(
                        context,
                        message,
                        () -> s.order.add(ATTEMPTED),
                        () -> s.order.add(CONFIRMED)));
        assertEquals(List.of(MODE, PROCESS, ATTEMPTED, ROLLBACK), s.order);
      }
      assertSame(primary, unconfirmed.getCause());
      assertSame(rollbackFailure, unconfirmed.getSuppressed()[0]);
      assertSame(rollbackFailure, primary.getSuppressed()[primary.getSuppressed().length - 1]);
    }
  }

  private static TransactedEventListener listener(
      Scenario s, InternalEventProcessor processor, Clock clock) {
    return new TransactedEventListener(
        s.question ? BrokerTopology.ASYNC_WORK : BrokerTopology.WEB_LOG,
        s.question ? FatalDlqMetadata.DetectedBy.API_WORK : FatalDlqMetadata.DetectedBy.API_WEB_LOG,
        processor,
        clock);
  }

  private static void assertIsolationProperties(Scenario s, boolean question) {
    assertEquals(10, s.properties.size());
    assertEquals(question ? "nk.async.work" : "nk.web.log", s.properties.get("_AMQ_ORIG_ADDRESS"));
    assertEquals(
        question ? "nk.async.work.q" : "nk.web.log.q", s.properties.get("_AMQ_ORIG_QUEUE"));
    assertEquals(EVENT_ID, s.properties.get("NKMessageID"));
    assertEquals(CORRELATION_ID, s.properties.get("NKCorrelationID"));
    assertEquals(question ? WORK_LAYOUT : LOG_LAYOUT, s.properties.get("NKLayoutID"));
    assertEquals(3, s.properties.get("NKDeliveryCount"));
    assertEquals("PROTOCOL_INVALID", s.properties.get("NKErrorCode"));
    assertEquals(question ? "API_WORK" : "API_WEB_LOG", s.properties.get("NKDetectedBy"));
    assertEquals("2026-11-08T00:00:01Z", s.properties.get("NKDetectedAt"));
    assertEquals(1, s.clears);
    assertEquals(1, s.correlationWrites);
    assertEquals(2, s.nullHeaderWrites);
  }

  // SS322/323 literal zero-based positions; no Product encoder or registry creates expected bytes.
  private static byte[] golden(boolean question) {
    byte[] b = new byte[question ? 320 : 2336];
    Arrays.fill(b, (byte) ' ');
    ascii(b, 0, "SCHBNK01");
    ascii(b, 8, VERSION);
    ascii(b, 11, question ? WORK_LAYOUT : LOG_LAYOUT);
    ascii(b, 19, VERSION);
    ascii(b, 22, "EI");
    ascii(b, 24, EVENT_ID);
    ascii(b, 60, CORRELATION_ID);
    ascii(b, 96, "20261108090000000");
    ascii(b, 177, "0256");
    ascii(b, 181, question ? "000064" : "002080");
    ascii(b, 187, "000000000000");
    ascii(b, 199, question ? "000000320" : "000002336");
    if (question) {
      ascii(b, 256, "00000000000000000000000001");
      ascii(b, 282, "000000000061");
      ascii(b, 294, "000000000062");
    } else {
      ascii(b, 256, "20261108090000000");
      ascii(b, 273, "REQUEST");
      ascii(b, 289, "INFO");
      ascii(b, 361, "HTTP request completed");
      ascii(b, 873, "00000000-0000-0000-0000-000000000083");
      ascii(b, 909, "GET");
      ascii(b, 917, "/login");
      ascii(b, 1173, "200");
      ascii(b, 1176, "0");
      ascii(b, 1185, "127.0.0.1");
    }
    return b;
  }

  private static void ascii(byte[] b, int offset, String value) {
    byte[] part = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(part, 0, b, offset, part.length);
  }

  private enum FailureSite {
    CLOCK,
    PROCESSOR,
    COMMIT
  }

  private static final class FailingClock extends Clock {
    private final RuntimeException failure;

    FailingClock(RuntimeException failure) {
      this.failure = failure;
    }

    @Override
    public java.time.ZoneId getZone() {
      return ZoneOffset.UTC;
    }

    @Override
    public Clock withZone(java.time.ZoneId zone) {
      return this;
    }

    @Override
    public Instant instant() {
      throw failure;
    }
  }

  private static final class Scenario {
    private final boolean question;
    private final byte[] body;
    private final List<String> order = new ArrayList<>();
    private final Map<String, Object> properties = new LinkedHashMap<>();
    private int mode = JMSContext.SESSION_TRANSACTED;
    private int bodyReads;
    private int clears;
    private int correlationWrites;
    private int nullHeaderWrites;
    private String transport = TRANSPORT_ID;
    private @Nullable JMSException readFailure;
    private @Nullable RuntimeException commitFailure;
    private @Nullable RuntimeException sendFailure;
    private @Nullable RuntimeException rollbackFailure;
    private @Nullable Object sent;

    Scenario(boolean question) {
      this.question = question;
      body = golden(question);
    }

    JMSContext context() {
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getSessionMode" -> {
                      order.add(MODE);
                      yield mode;
                    }
                    case COMMIT -> {
                      order.add(COMMIT);
                      if (commitFailure != null) throw commitFailure;
                      yield null;
                    }
                    case ROLLBACK -> {
                      order.add(ROLLBACK);
                      if (rollbackFailure != null) throw rollbackFailure;
                      yield null;
                    }
                    case "createProducer" -> producer();
                    default -> throw new AssertionError("unexpected context operation");
                  });
    }

    private JMSProducer producer() {
      return (JMSProducer)
          Proxy.newProxyInstance(
              JMSProducer.class.getClassLoader(),
              new Class<?>[] {JMSProducer.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "setDeliveryMode" -> {
                      assertEquals(2, args[0]);
                      yield proxy;
                    }
                    case "setTimeToLive" -> {
                      assertEquals(0L, args[0]);
                      yield proxy;
                    }
                    case SEND -> {
                      assertEquals(DEAD_LETTER_QUEUE, ((ActiveMQQueue) args[0]).getAddress());
                      sent = args[1];
                      order.add(SEND);
                      if (sendFailure != null) throw sendFailure;
                      yield proxy;
                    }
                    default -> throw new AssertionError("unexpected producer operation");
                  });
    }

    BytesMessage message() {
      var destination = new ActiveMQQueue(question ? "nk.async.work" : "nk.web.log");
      return (BytesMessage)
          Proxy.newProxyInstance(
              BytesMessage.class.getClassLoader(),
              new Class<?>[] {BytesMessage.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getBodyLength" -> {
                      bodyReads++;
                      if (readFailure != null) throw readFailure;
                      yield (long) body.length;
                    }
                    case "getBody" -> {
                      assertSame(byte[].class, args[0]);
                      yield body.clone();
                    }
                    case "getJMSDestination" -> destination;
                    case "getJMSReplyTo" -> null;
                    case "getJMSMessageID" -> transport;
                    case "getJMSCorrelationID" -> CORRELATION_ID;
                    case "getJMSExpiration" -> 0L;
                    case "getJMSDeliveryMode" -> 2;
                    case "propertyExists" ->
                        List.of(
                                "JMSXDeliveryCount",
                                "NKMessageID",
                                "NKLayoutID",
                                "NKProtocolVersion")
                            .contains(args[0]);
                    case "getIntProperty" -> {
                      assertEquals("JMSXDeliveryCount", args[0]);
                      yield 3;
                    }
                    case "getStringProperty" ->
                        switch ((String) args[0]) {
                          case "NKMessageID" -> EVENT_ID;
                          case "NKLayoutID" -> question ? WORK_LAYOUT : LOG_LAYOUT;
                          case "NKProtocolVersion" -> VERSION;
                          default -> throw new AssertionError("unexpected input property");
                        };
                    case "clearProperties" -> {
                      properties.clear();
                      clears++;
                      yield null;
                    }
                    case "setStringProperty", "setIntProperty" -> {
                      properties.put((String) args[0], args[1]);
                      yield null;
                    }
                    case "setJMSCorrelationID" -> {
                      assertEquals(CORRELATION_ID, args[0]);
                      correlationWrites++;
                      yield null;
                    }
                    case "setJMSReplyTo", "setJMSType" -> {
                      assertEquals(null, args[0]);
                      nullHeaderWrites++;
                      yield null;
                    }
                    default -> throw new AssertionError("unexpected message operation");
                  });
    }
  }
}
