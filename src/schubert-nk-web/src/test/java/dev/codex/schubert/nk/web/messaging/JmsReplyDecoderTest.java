package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.Destination;
import jakarta.jms.Message;
import jakarta.jms.TextMessage;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.apache.activemq.artemis.jms.client.ActiveMQTemporaryQueue;
import org.junit.jupiter.api.Test;

/** PT-JMS-005/006 Web reply provider, metadata, route and wire negative matrix. */
final class JmsReplyDecoderTest {
  private static final String REQUEST_ID = "00000000-0000-0000-0000-000000000001";
  private static final String RESPONSE_ID = "00000000-0000-0000-0000-000000000002";
  private static final JmsReplyDecoder DECODER = new JmsReplyDecoder();

  @Test
  void validReplyProducesAnImmutableRedactedResult() throws Exception {
    Map<String, Object> values = validReply();
    byte[] providerBody = (byte[]) values.get("body");
    ValidatedReply reply = DECODER.decode(bytesMessage(values));
    providerBody[0] = 9;
    byte[] returned = reply.body();
    returned[1] = 9;

    assertEquals(UUID.fromString(REQUEST_ID), reply.correlationId());
    assertArrayEquals(responseWire(), reply.body());
    assertTrue(reply.toString().contains("body=<redacted>"));
    assertThrows(NullPointerException.class, () -> new ValidatedReply(null, new byte[0]));
    assertThrows(
        NullPointerException.class,
        () -> new ValidatedReply(UUID.fromString(REQUEST_ID), null));
  }

  @Test
  void nullTypeBodyLengthAndCopyAnomaliesAreRejected() {
    assertThrows(NullPointerException.class, () -> DECODER.decode(null));
    assertRejected(proxy(TextMessage.class, validReply()));
    assertRejected(bytesMessage(with(validReply(), "bodyLength", -1L)));
    assertRejected(bytesMessage(with(validReply(), "bodyLength", 1_000_001L)));
    assertRejected(bytesMessage(with(validReply(), "body", null)));
    assertRejected(bytesMessage(with(validReply(), "bodyLength", 279L)));
    assertRejected(bytesMessage(with(validReply(), "body", new byte[255])));
    assertRejected(
        bytesMessage(
            with(
                with(validReply(), "body", Arrays.copyOf(responseWire(), 281)),
                "bodyLength",
                281L)));
  }

  @Test
  void destinationMustBeThePermanentApprovedAddressWithoutReplyTo() throws Exception {
    Destination foreign = new Destination() {};
    assertRejected(bytesMessage(with(validReply(), "destination", foreign)));
    assertRejected(
        bytesMessage(with(validReply(), "destination", new ActiveMQTemporaryQueue())));
    assertRejected(bytesMessage(with(validReply(), "destination", new ActiveMQQueue())));
    assertRejected(bytesMessage(with(validReply(), "destination", new ActiveMQQueue(" "))));
    assertEquals(
        UUID.fromString(REQUEST_ID),
        DECODER
            .decode(
                bytesMessage(
                    with(
                        validReply(),
                        "destination",
                        new ActiveMQQueue(
                            "nk.sync.reply.web::nk.sync.reply.web.q"))))
            .correlationId());
    assertRejected(
        bytesMessage(
            with(
                validReply(),
                "destination",
                new ActiveMQQueue("nk.sync.reply.web::unapproved.q"))));
    assertRejected(
        bytesMessage(
            with(validReply(), "destination", new ActiveMQQueue("::unapproved.q"))));
    assertRejected(
        bytesMessage(with(validReply(), "destination", new ActiveMQQueue("nk.async.work"))));
    assertRejected(
        bytesMessage(
            with(validReply(), "replyTo", new ActiveMQQueue("nk.sync.reply.web"))));
  }

  @Test
  void requiredHeadersPropertiesAndValuesDenyMissingBlankAndMalformedInputs() {
    assertRejected(bytesMessage(with(validReply(), "jmsMessageId", null)));
    assertRejected(bytesMessage(with(validReply(), "jmsMessageId", " ")));
    assertRejected(bytesMessage(with(validReply(), "correlationId", null)));
    assertRejected(bytesMessage(with(validReply(), "correlationId", "not-a-uuid")));
    assertRejected(bytesMessage(without(validReply(), "JMSXDeliveryCount")));
    assertRejected(bytesMessage(with(validReply(), "JMSXDeliveryCount", 0)));
    assertRejected(bytesMessage(without(validReply(), "NKMessageID")));
    assertRejected(bytesMessage(with(validReply(), "NKMessageID", " ")));
    assertRejected(bytesMessage(with(validReply(), "NKMessageID", "not-a-uuid")));
    assertRejected(bytesMessage(without(validReply(), "NKLayoutID")));
    assertRejected(bytesMessage(with(validReply(), "NKLayoutID", "short")));
    assertRejected(bytesMessage(without(validReply(), "NKProtocolVersion")));
    assertRejected(bytesMessage(with(validReply(), "NKProtocolVersion", " ")));
    assertRejected(bytesMessage(with(validReply(), "expiration", -1L)));
  }

  @Test
  void transportAndWireValuesMustExactlyMatchTheReplyHeaderAndRoute() {
    assertRejected(bytesMessage(with(validReply(), "deliveryMode", DeliveryMode.NON_PERSISTENT)));
    assertRejected(bytesMessage(with(validReply(), "expiration", 0L)));
    assertRejected(bytesMessage(with(validReply(), "NKProtocolVersion", "999")));
    assertRejected(bytesMessage(with(validReply(), "NKMessageID", REQUEST_ID)));
    assertRejected(bytesMessage(with(validReply(), "NKLayoutID", "LGNRSP01")));
    assertRejected(bytesMessage(with(validReply(), "correlationId", RESPONSE_ID)));
  }

  private static Map<String, Object> validReply() {
    byte[] body = responseWire();
    Map<String, Object> values = new HashMap<>();
    values.put("body", body);
    values.put("bodyLength", (long) body.length);
    values.put("destination", new ActiveMQQueue("nk.sync.reply.web"));
    values.put("replyTo", null);
    values.put("jmsMessageId", "ID:provider-transport-id");
    values.put("correlationId", REQUEST_ID);
    values.put("expiration", 1_000L);
    values.put("deliveryMode", DeliveryMode.PERSISTENT);
    values.put("JMSXDeliveryCount", 1);
    values.put("NKMessageID", RESPONSE_ID);
    values.put("NKLayoutID", "LOGRSP01");
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

  private static void assertRejected(Message message) {
    assertThrows(PermanentProtocolException.class, () -> DECODER.decode(message));
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
              if (name.equals("getIntProperty") || name.equals("getStringProperty")) {
                return values.get((String) arguments[0]);
              }
              if (name.equals("toString")) {
                return "SyntheticJmsReply";
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

  private static byte[] responseWire() {
    byte[] body = new byte[280];
    Arrays.fill(body, (byte) ' ');
    ascii(body, 0, "SCHBNK01");
    ascii(body, 8, "001");
    ascii(body, 11, "LOGRSP01");
    ascii(body, 19, "001");
    body[22] = 'S';
    body[23] = 'S';
    ascii(body, 24, RESPONSE_ID);
    ascii(body, 60, REQUEST_ID);
    ascii(body, 96, "20260903120000000");
    ascii(body, 113, "a".repeat(64));
    ascii(body, 177, "0256");
    ascii(body, 181, "000024");
    ascii(body, 187, "000000");
    ascii(body, 193, "000000");
    ascii(body, 199, "000000280");
    ascii(body, 208, "0000");
    return body;
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }
}
