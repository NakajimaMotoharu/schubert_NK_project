package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.Message;
import jakarta.jms.Queue;
import jakarta.jms.TextMessage;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-MSG-001; MQ008/010; UI231/251; SS321/PG-D018; PT-JMS-WDLQ001..008. */
final class ArtemisReplyDlqSenderContractTest {
  private static final String MESSAGE_ID = "00000000-0000-0000-0000-00000000000a";
  private static final String CORRELATION_ID = "00000000-0000-0000-0000-00000000000b";
  private static final String TRANSPORT_ID = "ID:public-synthetic-source";
  private static final String LAYOUT_ID = "LOGRSP01";
  private static final String PROP_PREFIX = "prop:";
  private static final String SEND = "send";
  private static final String PROVIDER_FAULT = "public synthetic fault";
  private static final String UNAVAILABLE = "UNAVAILABLE";
  private static final String ORIG_ADDRESS = "_AMQ_ORIG_ADDRESS";
  private static final String ORIG_QUEUE = "_AMQ_ORIG_QUEUE";
  private static final String ORIGINAL_ID = "NKOriginalTransportID";
  private static final String MESSAGE = "NKMessageID";
  private static final String CORRELATION = "NKCorrelationID";
  private static final String LAYOUT = "NKLayoutID";
  private static final String COUNT = "NKDeliveryCount";
  private static final String ERROR = "NKErrorCode";
  private static final String DETECTED_BY = "NKDetectedBy";
  private static final String DETECTED_AT = "NKDetectedAt";
  private static final String JMS_COUNT = "JMSXDeliveryCount";
  private static final String MODE = "mode";
  private static final String SET_CORRELATION = "set:correlation";
  private static final Instant WHEN = Instant.parse("2026-11-05T00:00:00Z");
  private static final List<String> ORDER =
      List.of(
          MODE,
          "get:transport",
          "get:" + MESSAGE,
          "get:correlation",
          "get:" + LAYOUT,
          "hasCount",
          "getCount",
          "clear",
          SET_CORRELATION,
          "replyTo",
          "type",
          PROP_PREFIX + ORIG_ADDRESS,
          PROP_PREFIX + ORIG_QUEUE,
          PROP_PREFIX + ORIGINAL_ID,
          PROP_PREFIX + MESSAGE,
          PROP_PREFIX + CORRELATION,
          PROP_PREFIX + LAYOUT,
          "int:" + COUNT,
          PROP_PREFIX + ERROR,
          PROP_PREFIX + DETECTED_BY,
          PROP_PREFIX + DETECTED_AT,
          "producer",
          "persistent",
          "ttl",
          SEND);
  private static final List<String> UNCHECKED =
      List.of(MODE, "producer", "persistent", "ttl", SEND);

  private static final Clock CLOCK = Clock.fixed(WHEN, ZoneOffset.UTC);

  @Test
  void webDlq001TextHandleAndOnlyApprovedReplyDiagnosticsAreStaged() throws Exception {
    var fixture = new Fixture(Input.normal(), 0, Fault.none());
    isolate(fixture);
    assertEquals(
        expected(TRANSPORT_ID, MESSAGE_ID, CORRELATION_ID, LAYOUT_ID, 4), fixture.raw.properties);
    assertEquals(ORDER, fixture.events);
    assertEquals(CORRELATION_ID, fixture.raw.correlation);
    untrustedPost(fixture);
  }

  @Test
  void webDlq002TransportHasIndependentAsciiAndLengthBoundaries() throws Exception {
    for (Diagnostic d :
        List.of(
            new Diagnostic(null, UNAVAILABLE),
            new Diagnostic("", UNAVAILABLE),
            new Diagnostic(" ", UNAVAILABLE),
            new Diagnostic(" X ", " X "),
            new Diagnostic("a".repeat(127), "a".repeat(127)),
            new Diagnostic("a".repeat(128), "a".repeat(128)),
            new Diagnostic("a".repeat(129), UNAVAILABLE),
            new Diagnostic("X\u001f", UNAVAILABLE),
            new Diagnostic("X\u007f", UNAVAILABLE),
            new Diagnostic("~", "~"),
            new Diagnostic("é", UNAVAILABLE))) {
      var fixture = new Fixture(Input.normal().with(Field.TRANSPORT, d.input), 0, Fault.none());
      isolate(fixture);
      assertEquals(
          expected(d.expected, MESSAGE_ID, CORRELATION_ID, LAYOUT_ID, 4), fixture.raw.properties);
      untrustedPost(fixture);
    }
  }

  @Test
  void webDlq003BothUuidDiagnosticsRequireCanonicalLowercase() throws Exception {
    for (Field field : List.of(Field.MESSAGE, Field.CORRELATION)) {
      for (Diagnostic d :
          List.of(
              new Diagnostic(null, UNAVAILABLE),
              new Diagnostic("", UNAVAILABLE),
              new Diagnostic(" ", UNAVAILABLE),
              new Diagnostic(MESSAGE_ID, MESSAGE_ID),
              new Diagnostic("00000000-0000-0000-0000-00000000000A", UNAVAILABLE),
              new Diagnostic(
                  "00000000-0000-0000-0000-000000000000", "00000000-0000-0000-0000-000000000000"),
              new Diagnostic("1-1-1-1-1", UNAVAILABLE),
              new Diagnostic("x".repeat(36), UNAVAILABLE),
              new Diagnostic(MESSAGE_ID.substring(0, 35), UNAVAILABLE),
              new Diagnostic(MESSAGE_ID + "a", UNAVAILABLE))) {
        var fixture = new Fixture(Input.normal().with(field, d.input), 0, Fault.none());
        isolate(fixture);
        String message = field == Field.MESSAGE ? d.expected : MESSAGE_ID;
        String correlation = field == Field.CORRELATION ? d.expected : CORRELATION_ID;
        assertEquals(
            expected(TRANSPORT_ID, message, correlation, LAYOUT_ID, 4), fixture.raw.properties);
        assertEquals(correlation, fixture.raw.correlation);
        untrustedPost(fixture);
      }
    }
  }

  @Test
  void webDlq004LayoutAndCountsAreBoundedDiagnostics() throws Exception {
    for (Diagnostic d :
        List.of(
            new Diagnostic(null, UNAVAILABLE),
            new Diagnostic("", UNAVAILABLE),
            new Diagnostic(" ", UNAVAILABLE),
            new Diagnostic("QWKREQ01", "QWKREQ01"),
            new Diagnostic("qwkreq01", UNAVAILABLE),
            new Diagnostic("QWKREQ0", UNAVAILABLE),
            new Diagnostic("QWKREQ011", UNAVAILABLE),
            new Diagnostic("XXXXXXX?", UNAVAILABLE),
            new Diagnostic("ZZZZZZZZ", "ZZZZZZZZ"))) {
      var fixture = new Fixture(Input.normal().with(Field.LAYOUT, d.input), 0, Fault.none());
      isolate(fixture);
      assertEquals(
          expected(TRANSPORT_ID, MESSAGE_ID, CORRELATION_ID, d.expected, 4),
          fixture.raw.properties);
      untrustedPost(fixture);
    }
    for (Count d :
        List.of(
            new Count(false, 0, 1),
            new Count(true, Integer.MIN_VALUE, 1),
            new Count(true, -1, 1),
            new Count(true, 0, 1),
            new Count(true, 1, 1),
            new Count(true, 2, 2),
            new Count(true, 4, 4),
            new Count(true, Integer.MAX_VALUE, Integer.MAX_VALUE))) {
      Input input =
          new Input(TRANSPORT_ID, MESSAGE_ID, CORRELATION_ID, LAYOUT_ID, d.present, d.input);
      var fixture = new Fixture(input, 0, Fault.none());
      isolate(fixture);
      assertEquals(
          expected(TRANSPORT_ID, MESSAGE_ID, CORRELATION_ID, LAYOUT_ID, d.expected),
          fixture.raw.properties);
      assertEquals(d.present ? 1 : 0, fixture.raw.countReads);
      untrustedPost(fixture);
    }
  }

  @Test
  void webDlq005NullClockContextMessageAndNontransactedModeFailClosed() {
    var fixture = new Fixture(Input.normal(), 0, Fault.none());
    var sender = new ArtemisReplyDlqSender(CLOCK);
    assertThrows(NullPointerException.class, () -> new ArtemisReplyDlqSender(null));
    assertThrows(NullPointerException.class, () -> sender.send(null, fixture.incoming));
    assertThrows(NullPointerException.class, () -> sender.send(fixture.context, null));
    assertEquals(List.of(), fixture.events);
    var wrong = new Fixture(Input.normal(), 1, Fault.none());
    assertThrows(IllegalStateException.class, () -> sender.send(wrong.context, wrong.incoming));
    assertEquals(List.of(MODE), wrong.events);
  }

  @Test
  void webDlq006EveryProviderFaultRetainsIdentityAndStopsTheStage() {
    for (String stage : ORDER) {
      List<Throwable> failures =
          UNCHECKED.contains(stage)
              ? List.of(
                  new IllegalArgumentException(PROVIDER_FAULT), new AssertionError(PROVIDER_FAULT))
              : List.of(
                  new JMSException(PROVIDER_FAULT),
                  new IllegalArgumentException(PROVIDER_FAULT),
                  new AssertionError(PROVIDER_FAULT));
      for (Throwable failure : failures) {
        var fixture = new Fixture(Input.normal(), 0, new Fault(stage, failure));
        var sender = new ArtemisReplyDlqSender(CLOCK);
        assertSame(
            failure,
            assertThrows(failure.getClass(), () -> sender.send(fixture.context, fixture.incoming)));
        assertEquals(ORDER.subList(0, ORDER.indexOf(stage) + 1), fixture.events);
      }
    }
  }

  @Test
  void webDlq007ClockRuntimeAndErrorNeverAcquireProducerOrCompleteDiagnostic() {
    for (Throwable failure :
        List.of(new IllegalArgumentException(PROVIDER_FAULT), new AssertionError(PROVIDER_FAULT))) {
      var fixture = new Fixture(Input.normal(), 0, Fault.none());
      var calls = new AtomicInteger();
      Clock clock = faultClock(failure, false, calls);
      var sender = new ArtemisReplyDlqSender(clock);
      assertSame(
          failure,
          assertThrows(failure.getClass(), () -> sender.send(fixture.context, fixture.incoming)));
      assertEquals(1, calls.get());
      assertEquals(ORDER.subList(0, ORDER.indexOf(PROP_PREFIX + DETECTED_AT)), fixture.events);
      assertFalse(fixture.raw.properties.containsKey(DETECTED_AT));
    }
  }

  @Test
  void webDlq008NullClockResultCannotBecomeSuccessfulIsolation() {
    var fixture = new Fixture(Input.normal(), 0, Fault.none());
    var calls = new AtomicInteger();
    Clock clock = faultClock(null, true, calls);
    var sender = new ArtemisReplyDlqSender(clock);
    assertThrows(NullPointerException.class, () -> sender.send(fixture.context, fixture.incoming));
    assertEquals(1, calls.get());
    assertEquals(ORDER.subList(0, ORDER.indexOf(PROP_PREFIX + DETECTED_AT)), fixture.events);
    assertFalse(fixture.raw.properties.containsKey(DETECTED_AT));
  }

  private static Clock faultClock(Throwable failure, boolean nullResult, AtomicInteger calls) {
    return new Clock() {
      @Override
      public ZoneId getZone() {
        throw new AssertionError("unexpected clock zone");
      }

      @Override
      public Clock withZone(ZoneId zone) {
        throw new AssertionError("unexpected clock zone change");
      }

      @Override
      public Instant instant() {
        calls.incrementAndGet();
        if (nullResult) return null;
        if (failure instanceof RuntimeException runtime) throw runtime;
        throw (Error) failure;
      }
    };
  }

  private static void isolate(Fixture fixture) throws JMSException {
    new ArtemisReplyDlqSender(CLOCK).send(fixture.context, fixture.incoming);
  }

  private static void staged(Fixture fixture) {
    assertEquals(2, fixture.sent.deliveryMode);
    assertEquals(0L, fixture.sent.ttl);
    assertEquals("nk.dead.letter::nk.dead.letter.q", fixture.sent.destination);
  }

  private static void untrustedPost(Fixture fixture) {
    assertSame(fixture.incoming, fixture.sent.message);
    assertTrue(fixture.raw.replyToCleared);
    assertTrue(fixture.raw.typeCleared);
    staged(fixture);
  }

  private static Map<String, Object> expected(
      String transport, String message, String correlation, String layout, int count) {
    return Map.of(
        ORIG_ADDRESS,
        "nk.sync.reply.web",
        ORIG_QUEUE,
        "nk.sync.reply.web.q",
        ORIGINAL_ID,
        transport,
        MESSAGE,
        message,
        CORRELATION,
        correlation,
        LAYOUT,
        layout,
        COUNT,
        count,
        ERROR,
        "PROTOCOL_INVALID",
        DETECTED_BY,
        "WEB_REPLY",
        DETECTED_AT,
        "2026-11-05T00:00:00Z");
  }

  private enum Field {
    TRANSPORT,
    MESSAGE,
    CORRELATION,
    LAYOUT
  }

  private record Diagnostic(String input, String expected) {}

  private record Count(boolean present, int input, int expected) {}

  private record Fault(String stage, Throwable failure) {
    Fault {
      if ((stage == null) != (failure == null))
        throw new IllegalArgumentException("paired public fault required");
    }

    static Fault none() {
      return new Fault(null, null);
    }
  }

  private record Input(
      String transport,
      String message,
      String correlation,
      String layout,
      boolean countPresent,
      int count) {
    static Input normal() {
      return new Input(TRANSPORT_ID, MESSAGE_ID, CORRELATION_ID, LAYOUT_ID, true, 4);
    }

    Input with(Field field, String value) {
      return new Input(
          field == Field.TRANSPORT ? value : transport,
          field == Field.MESSAGE ? value : message,
          field == Field.CORRELATION ? value : correlation,
          field == Field.LAYOUT ? value : layout,
          countPresent,
          count);
    }
  }

  private static final class Capture {
    private final Map<String, Object> properties = new LinkedHashMap<>();
    private String correlation;
    private boolean replyToCleared;
    private boolean typeCleared;
    private int countReads;
  }

  private static final class Sent {
    private Message message;
    private String destination;
    private int deliveryMode;
    private long ttl;
  }

  private static final class Fixture {
    private final Capture raw = new Capture();
    private final Sent sent = new Sent();
    private final List<String> events = new ArrayList<>();
    private final Fault fault;
    private final int mode;
    private final String transport;
    private final TextMessage incoming;
    private final JMSProducer producer;
    private final JMSContext context;

    Fixture(Input input, int mode, Fault fault) {
      this.mode = mode;
      this.fault = fault;
      transport = input.transport;
      raw.correlation = input.correlation;
      raw.properties.put(MESSAGE, input.message);
      raw.properties.put(LAYOUT, input.layout);
      raw.properties.put("Password", "PUBLIC_SYNTHETIC_MARKER");
      raw.properties.put("BodyHash", "PUBLIC_SYNTHETIC_MARKER");
      if (input.countPresent) raw.properties.put(JMS_COUNT, input.count);
      incoming = proxy(TextMessage.class, this::readOrMutate);
      producer = proxy(JMSProducer.class, this::produce);
      context = proxy(JMSContext.class, this::contextCall);
    }

    private void step(String stage) throws Throwable {
      events.add(stage);
      if (stage.equals(fault.stage)) throw fault.failure;
    }

    private Object readOrMutate(Object proxy, Method method, Object[] args) throws Throwable {
      return switch (method.getName()) {
        case "getJMSMessageID" -> {
          step("get:transport");
          yield transport;
        }
        case "getJMSCorrelationID" -> {
          step("get:correlation");
          yield raw.correlation;
        }
        case "getStringProperty" -> {
          String key = (String) args[0];
          assertTrue(key.equals(MESSAGE) || key.equals(LAYOUT));
          step("get:" + key);
          yield raw.properties.get(key);
        }
        case "propertyExists" -> {
          assertEquals(JMS_COUNT, args[0]);
          step("hasCount");
          yield raw.properties.containsKey(JMS_COUNT);
        }
        case "getIntProperty" -> {
          assertEquals(JMS_COUNT, args[0]);
          step("getCount");
          raw.countReads++;
          yield raw.properties.get(JMS_COUNT);
        }
        case "clearProperties" -> {
          step("clear");
          raw.properties.clear();
          yield null;
        }
        default -> mutate(raw, method, args);
      };
    }

    private Object mutate(Capture capture, Method method, Object[] args) throws Throwable {
      switch (method.getName()) {
        case "setJMSCorrelationID" -> {
          step(SET_CORRELATION);
          capture.correlation = (String) args[0];
        }
        case "setJMSReplyTo" -> {
          step("replyTo");
          assertSame(null, args[0]);
          capture.replyToCleared = true;
        }
        case "setJMSType" -> {
          step("type");
          assertSame(null, args[0]);
          capture.typeCleared = true;
        }
        case "setStringProperty" -> {
          step(PROP_PREFIX + args[0]);
          capture.properties.put((String) args[0], args[1]);
        }
        case "setIntProperty" -> {
          step("int:" + args[0]);
          capture.properties.put((String) args[0], args[1]);
        }
        default ->
            throw new AssertionError(
                "body reads, deserialization, ACK and unknown message operations forbidden");
      }
      return null;
    }

    private Object produce(Object proxy, Method method, Object[] args) throws Throwable {
      switch (method.getName()) {
        case "setDeliveryMode" -> {
          step("persistent");
          sent.deliveryMode = (Integer) args[0];
        }
        case "setTimeToLive" -> {
          step("ttl");
          sent.ttl = (Long) args[0];
        }
        case SEND -> {
          assertEquals(2, method.getParameterCount());
          assertEquals(Message.class, method.getParameterTypes()[1]);
          step(SEND);
          sent.destination = ((Queue) args[0]).getQueueName();
          sent.message = (Message) args[1];
        }
        default -> throw new AssertionError("unknown producer operation forbidden");
      }
      return proxy;
    }

    private Object contextCall(Object proxy, Method method, Object[] args) throws Throwable {
      return switch (method.getName()) {
        case "getSessionMode" -> {
          step(MODE);
          yield mode;
        }
        case "createProducer" -> {
          step("producer");
          yield producer;
        }
        default ->
            throw new AssertionError(
                "borrowed context commit, rollback, close or unknown operation forbidden");
      };
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
