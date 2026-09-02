package dev.codex.schubert.nk.api.messaging.guard;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.Destination;
import jakarta.jms.Message;
import jakarta.jms.TextMessage;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.apache.activemq.artemis.jms.client.ActiveMQTemporaryQueue;
import org.junit.jupiter.api.Test;

/** PT-JMS-005/006 independent JMS boundary matrix without production codec or constants. */
final class JmsMessageGuardTest {
  private static final String MESSAGE_ID = "00000000-0000-0000-0000-000000000001";
  private static final String CORRELATION_ID = "00000000-0000-0000-0000-000000000002";
  private static final JmsMessageGuard GUARD = new JmsMessageGuard();
  private static final ExpectedRoute REQUEST_ROUTE =
      new ExpectedRoute(
          MessageKind.REQUEST,
          InteractionKind.SYNCHRONOUS,
          "nk.sync.request",
          Optional.of("nk.sync.reply.web"),
          true);
  private static final ExpectedRoute EVENT_ROUTE =
      new ExpectedRoute(
          MessageKind.EVENT,
          InteractionKind.INTERNAL,
          "nk.web.log",
          Optional.empty(),
          false);

  @Test
  void validBytesMessageProducesAnImmutableRedactedSnapshot() throws Exception {
    Map<String, Object> values = validRequest();
    byte[] providerBody = (byte[]) values.get("body");
    GuardedJmsMessage guarded = GUARD.read(bytesMessage(values), REQUEST_ROUTE);
    providerBody[0] = 9;
    byte[] returned = guarded.body();
    returned[1] = 9;

    assertArrayEquals(new byte[] {1, 2, 3}, guarded.body());
    assertEquals(MESSAGE_ID, guarded.metadata().nkMessageId().toString());
    assertEquals(CORRELATION_ID, guarded.metadata().correlationId().toString());
    assertEquals("LOGREQ01", guarded.metadata().nkLayoutId().toString());
    assertTrue(guarded.toString().contains("body=<redacted>"));
    assertThrows(NullPointerException.class, () -> new GuardedJmsMessage(null, guarded.metadata()));
    assertThrows(NullPointerException.class, () -> new GuardedJmsMessage(new byte[0], null));
  }

  @Test
  void nullAndNonBytesMessagesAreDeniedBeforeBodyAccess() {
    assertThrows(NullPointerException.class, () -> GUARD.read(null, REQUEST_ROUTE));
    assertThrows(
        NullPointerException.class,
        () -> GUARD.read(bytesMessage(validRequest()), null));
    Message text = proxy(TextMessage.class, validRequest());
    assertThrows(PermanentProtocolException.class, () -> GUARD.read(text, REQUEST_ROUTE));
  }

  @Test
  void bodyLengthAndCopyAnomaliesAreDeniedBeforeAllocationUse() {
    assertRejected(with(validRequest(), "bodyLength", -1L), REQUEST_ROUTE);
    assertRejected(
        with(validRequest(), "bodyLength", (long) LayoutDefinition.MAXIMUM_BODY_LENGTH + 1),
        REQUEST_ROUTE);
    assertRejected(with(validRequest(), "body", null), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "bodyLength", 2L), REQUEST_ROUTE);
  }

  @Test
  void destinationMustBePermanentArtemisUnqualifiedAndExact() throws Exception {
    Destination foreign = new Destination() {};
    assertRejected(with(validRequest(), "destination", foreign), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "destination", new ActiveMQTemporaryQueue()), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "destination", new ActiveMQQueue()), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "destination", new ActiveMQQueue(" ")), REQUEST_ROUTE);
    Map<String, Object> qualified =
        with(
            validRequest(),
            "destination",
            new ActiveMQQueue("nk.sync.request::nk.sync.request.q"));
    assertEquals(
        "nk.sync.request",
        GUARD.read(bytesMessage(qualified), REQUEST_ROUTE).metadata().destinationAddress());
    assertRejected(
        with(
            validRequest(),
            "destination",
            new ActiveMQQueue("nk.sync.request::unapproved.q")),
        REQUEST_ROUTE);
    assertRejected(
        with(validRequest(), "destination", new ActiveMQQueue("::unapproved.q")), REQUEST_ROUTE);
    assertRejected(
        with(validRequest(), "destination", new ActiveMQQueue("nk.async.work")), REQUEST_ROUTE);
  }

  @Test
  void replyToMustMatchPresenceAndPermanentAllowlistedAddress() throws Exception {
    assertRejected(with(validRequest(), "replyTo", null), REQUEST_ROUTE);
    assertRejected(
        with(validRequest(), "replyTo", new Destination() {}), REQUEST_ROUTE);
    assertRejected(
        with(validRequest(), "replyTo", new ActiveMQTemporaryQueue()), REQUEST_ROUTE);
    assertRejected(
        with(validRequest(), "replyTo", new ActiveMQQueue("nk.expiry")), REQUEST_ROUTE);

    Map<String, Object> event = validEvent();
    GuardedJmsMessage guarded = GUARD.read(bytesMessage(event), EVENT_ROUTE);
    assertEquals(Optional.empty(), guarded.metadata().replyToAddress());
    assertRejected(
        with(event, "replyTo", new ActiveMQQueue("nk.sync.reply.web")), EVENT_ROUTE);
  }

  @Test
  void requiredHeadersAndPropertiesDenyNullBlankMissingAndMalformedValues() {
    assertRejected(with(validRequest(), "jmsMessageId", null), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "jmsMessageId", " "), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "correlationId", null), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "correlationId", "not-a-uuid"), REQUEST_ROUTE);
    assertRejected(without(validRequest(), "JMSXDeliveryCount"), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "JMSXDeliveryCount", 0), REQUEST_ROUTE);
    assertRejected(without(validRequest(), "NKMessageID"), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "NKMessageID", " "), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "NKMessageID", "not-a-uuid"), REQUEST_ROUTE);
    assertRejected(without(validRequest(), "NKLayoutID"), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "NKLayoutID", "short"), REQUEST_ROUTE);
    assertRejected(without(validRequest(), "NKProtocolVersion"), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "NKProtocolVersion", " "), REQUEST_ROUTE);
    assertRejected(with(validRequest(), "expiration", -1L), REQUEST_ROUTE);
  }

  private static Map<String, Object> validRequest() {
    Map<String, Object> values = baseValues();
    values.put("destination", new ActiveMQQueue("nk.sync.request"));
    values.put("replyTo", new ActiveMQQueue("nk.sync.reply.web"));
    values.put("expiration", 1_000L);
    return values;
  }

  private static Map<String, Object> validEvent() {
    Map<String, Object> values = baseValues();
    values.put("destination", new ActiveMQQueue("nk.web.log"));
    values.put("replyTo", null);
    values.put("expiration", 0L);
    return values;
  }

  private static Map<String, Object> baseValues() {
    Map<String, Object> values = new HashMap<>();
    values.put("body", new byte[] {1, 2, 3});
    values.put("bodyLength", 3L);
    values.put("jmsMessageId", "ID:provider-transport-id");
    values.put("correlationId", CORRELATION_ID);
    values.put("deliveryMode", DeliveryMode.PERSISTENT);
    values.put("JMSXDeliveryCount", 1);
    values.put("NKMessageID", MESSAGE_ID);
    values.put("NKLayoutID", "LOGREQ01");
    values.put("NKProtocolVersion", "001");
    return values;
  }

  private static Map<String, Object> with(
      Map<String, Object> source, String name, Object value) {
    Map<String, Object> copy = new HashMap<>(source);
    copy.put(name, value);
    return copy;
  }

  private static Map<String, Object> without(Map<String, Object> source, String name) {
    Map<String, Object> copy = new HashMap<>(source);
    copy.remove(name);
    return copy;
  }

  private static void assertRejected(Map<String, Object> values, ExpectedRoute route) {
    assertThrows(PermanentProtocolException.class, () -> GUARD.read(bytesMessage(values), route));
  }

  private static BytesMessage bytesMessage(Map<String, Object> values) {
    return proxy(BytesMessage.class, values);
  }

  @SuppressWarnings("unchecked")
  private static <T> T proxy(Class<T> type, Map<String, Object> values) {
    return (T)
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (ignored, method, arguments) -> {
              String name = method.getName();
              if (name.equals("getBodyLength")) {
                return values.get("bodyLength");
              }
              if (name.equals("getBody")) {
                byte[] body = (byte[]) values.get("body");
                return body == null ? null : body.clone();
              }
              if (name.equals("getJMSDestination")) {
                return values.get("destination");
              }
              if (name.equals("getJMSReplyTo")) {
                return values.get("replyTo");
              }
              if (name.equals("getJMSMessageID")) {
                return values.get("jmsMessageId");
              }
              if (name.equals("getJMSCorrelationID")) {
                return values.get("correlationId");
              }
              if (name.equals("getJMSExpiration")) {
                return values.get("expiration");
              }
              if (name.equals("getJMSDeliveryMode")) {
                return values.get("deliveryMode");
              }
              if (name.equals("propertyExists")) {
                return values.containsKey((String) arguments[0]);
              }
              if (name.equals("getIntProperty")) {
                return values.get((String) arguments[0]);
              }
              if (name.equals("getStringProperty")) {
                return values.get((String) arguments[0]);
              }
              if (name.equals("toString")) {
                return "SyntheticJmsMessage";
              }
              if (name.equals("hashCode")) {
                return System.identityHashCode(ignored);
              }
              if (name.equals("equals")) {
                return ignored == arguments[0];
              }
              throw new UnsupportedOperationException(name);
            });
  }
}
