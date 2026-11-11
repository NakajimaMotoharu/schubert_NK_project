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
  private static final String BODY_FIELD = "body";
  private static final String BODY_LENGTH_FIELD = "bodyLength";
  private static final String LAYOUT_ID_PROPERTY = "NKLayoutID";
  private static final String MESSAGE_ID_PROPERTY = "NKMessageID";
  private static final String DESTINATION_FIELD = "destination";
  private static final String TRANSPORT_ID_FIELD = "jmsMessageId";
  private static final String CORRELATION_FIELD = "correlationId";
  private static final String VERSION_PROPERTY = "NKProtocolVersion";
  private static final String EXPIRATION_FIELD = "expiration";
  private static final String REQUEST_ID = "00000000-0000-0000-0000-000000000001";
  private static final String RESPONSE_ID = "00000000-0000-0000-0000-000000000002";
  private static final JmsReplyDecoder DECODER = new JmsReplyDecoder();

  @Test
  void acceptanceReplyUsesExactRegisteredAsyncProfile() throws Exception {
    byte[] expected = Arrays.copyOf(responseWire(), 320);
    Arrays.fill(expected, 256, 320, (byte) ' ');
    ascii(expected, 11, "QSBRSP01");
    expected[23] = 'A';
    ascii(expected, 181, "000064");
    ascii(expected, 199, "000000320");
    ascii(expected, 256, "0".repeat(26));
    ascii(expected, 282, "000000000001");
    ascii(expected, 294, "20260903120000000");
    var valid =
        with(
            with(with(validReply(), BODY_FIELD, expected), BODY_LENGTH_FIELD, 320L),
            LAYOUT_ID_PROPERTY,
            "QSBRSP01");
    assertArrayEquals(expected, DECODER.decode(bytesMessage(valid)).body());
    assertEquals(UUID.fromString(REQUEST_ID), DECODER.decode(bytesMessage(valid)).correlationId());
    for (char wrong : new char[] {'S', 'I'}) {
      byte[] invalid = expected.clone();
      invalid[23] = (byte) wrong;
      assertRejected(bytesMessage(with(valid, BODY_FIELD, invalid)));
    }
    byte[] requestKind = expected.clone();
    requestKind[22] = 'Q';
    assertRejected(bytesMessage(with(valid, BODY_FIELD, requestKind)));
    assertRejected(bytesMessage(with(valid, LAYOUT_ID_PROPERTY, "LOGRSP01")));
    assertRejected(bytesMessage(with(valid, MESSAGE_ID_PROPERTY, REQUEST_ID)));
    assertRejected(
        bytesMessage(with(valid, DESTINATION_FIELD, new ActiveMQQueue("nk.async.work"))));
    byte[] wrongA = responseWire();
    wrongA[23] = 'A';
    assertRejected(bytesMessage(with(validReply(), BODY_FIELD, wrongA)));
  }

  @Test
  void validReplyProducesAnImmutableRedactedResult() throws Exception {
    Map<String, Object> values = validReply();
    byte[] providerBody = (byte[]) values.get(BODY_FIELD);
    ValidatedReply reply = DECODER.decode(bytesMessage(values));
    providerBody[0] = 9;
    byte[] returned = reply.body();
    returned[1] = 9;

    assertEquals(UUID.fromString(REQUEST_ID), reply.correlationId());
    assertArrayEquals(responseWire(), reply.body());
    assertTrue(reply.toString().contains("body=<redacted>"));
    // YKT-056: transport decoding preserves the common 0200 profile; only the domain decides grant.
    Map<String, Object> replayValues = validReply();
    byte[] replayBody = (byte[]) replayValues.get(BODY_FIELD);
    System.arraycopy("0200".getBytes(StandardCharsets.US_ASCII), 0, replayBody, 208, 4);
    assertArrayEquals(replayBody, DECODER.decode(bytesMessage(replayValues)).body());
    assertThrows(NullPointerException.class, () -> new ValidatedReply(null, new byte[0]));
    assertThrows(
        NullPointerException.class, () -> new ValidatedReply(UUID.fromString(REQUEST_ID), null));
  }

  @Test
  void nullTypeBodyLengthAndCopyAnomaliesAreRejected() {
    assertThrows(NullPointerException.class, () -> DECODER.decode(null));
    assertRejected(proxy(TextMessage.class, validReply()));
    assertRejected(bytesMessage(with(validReply(), BODY_LENGTH_FIELD, -1L)));
    assertRejected(bytesMessage(with(validReply(), BODY_LENGTH_FIELD, 1_000_001L)));
    assertRejected(bytesMessage(with(validReply(), BODY_FIELD, null)));
    assertRejected(bytesMessage(with(validReply(), BODY_LENGTH_FIELD, 279L)));
    assertRejected(bytesMessage(with(validReply(), BODY_FIELD, new byte[255])));
    assertRejected(
        bytesMessage(
            with(
                with(validReply(), BODY_FIELD, Arrays.copyOf(responseWire(), 281)),
                BODY_LENGTH_FIELD,
                281L)));
  }

  @Test
  void destinationMustBeThePermanentApprovedAddressWithoutReplyTo() throws Exception {
    Destination foreign = new Destination() {};
    assertRejected(bytesMessage(with(validReply(), DESTINATION_FIELD, foreign)));
    assertRejected(
        bytesMessage(with(validReply(), DESTINATION_FIELD, new ActiveMQTemporaryQueue())));
    assertRejected(bytesMessage(with(validReply(), DESTINATION_FIELD, new ActiveMQQueue())));
    assertRejected(bytesMessage(with(validReply(), DESTINATION_FIELD, new ActiveMQQueue(" "))));
    assertEquals(
        UUID.fromString(REQUEST_ID),
        DECODER
            .decode(
                bytesMessage(
                    with(
                        validReply(),
                        DESTINATION_FIELD,
                        new ActiveMQQueue("nk.sync.reply.web::nk.sync.reply.web.q"))))
            .correlationId());
    assertRejected(
        bytesMessage(
            with(
                validReply(),
                DESTINATION_FIELD,
                new ActiveMQQueue("nk.sync.reply.web::unapproved.q"))));
    assertRejected(
        bytesMessage(with(validReply(), DESTINATION_FIELD, new ActiveMQQueue("::unapproved.q"))));
    assertRejected(
        bytesMessage(with(validReply(), DESTINATION_FIELD, new ActiveMQQueue("nk.async.work"))));
    assertRejected(
        bytesMessage(with(validReply(), "replyTo", new ActiveMQQueue("nk.sync.reply.web"))));
  }

  @Test
  void requiredHeadersPropertiesAndValuesDenyMissingBlankAndMalformedInputs() {
    assertRejected(bytesMessage(with(validReply(), TRANSPORT_ID_FIELD, null)));
    assertRejected(bytesMessage(with(validReply(), TRANSPORT_ID_FIELD, " ")));
    assertRejected(bytesMessage(with(validReply(), CORRELATION_FIELD, null)));
    assertRejected(bytesMessage(with(validReply(), CORRELATION_FIELD, "not-a-uuid")));
    assertRejected(bytesMessage(without(validReply(), "JMSXDeliveryCount")));
    assertRejected(bytesMessage(with(validReply(), "JMSXDeliveryCount", 0)));
    assertRejected(bytesMessage(without(validReply(), MESSAGE_ID_PROPERTY)));
    assertRejected(bytesMessage(with(validReply(), MESSAGE_ID_PROPERTY, " ")));
    assertRejected(bytesMessage(with(validReply(), MESSAGE_ID_PROPERTY, "not-a-uuid")));
    assertRejected(bytesMessage(without(validReply(), LAYOUT_ID_PROPERTY)));
    assertRejected(bytesMessage(with(validReply(), LAYOUT_ID_PROPERTY, "short")));
    assertRejected(bytesMessage(without(validReply(), VERSION_PROPERTY)));
    assertRejected(bytesMessage(with(validReply(), VERSION_PROPERTY, " ")));
    assertRejected(bytesMessage(with(validReply(), EXPIRATION_FIELD, -1L)));
  }

  @Test
  void transportAndWireValuesMustExactlyMatchTheReplyHeaderAndRoute() {
    assertRejected(bytesMessage(with(validReply(), "deliveryMode", DeliveryMode.NON_PERSISTENT)));
    assertRejected(bytesMessage(with(validReply(), EXPIRATION_FIELD, 0L)));
    assertRejected(bytesMessage(with(validReply(), VERSION_PROPERTY, "999")));
    assertRejected(bytesMessage(with(validReply(), MESSAGE_ID_PROPERTY, REQUEST_ID)));
    assertRejected(bytesMessage(with(validReply(), LAYOUT_ID_PROPERTY, "LGNRSP01")));
    assertRejected(bytesMessage(with(validReply(), CORRELATION_FIELD, RESPONSE_ID)));
  }

  @Test
  void identityPropertiesMustRetainExactLowercaseCanonicalUuidText() throws Exception {
    // Independent UI232 offsets 25/61 and §6 identity rule; no production encoder.
    String messageId = "0000000a-000b-000c-000d-00000000000e";
    String correlationId = "0000000f-0010-0011-0012-000000000013";
    byte[] wire = responseWire();
    ascii(wire, 24, messageId);
    ascii(wire, 60, correlationId);
    Map<String, Object> canonical =
        with(
            with(with(validReply(), BODY_FIELD, wire), MESSAGE_ID_PROPERTY, messageId),
            CORRELATION_FIELD,
            correlationId);
    ValidatedReply accepted = DECODER.decode(bytesMessage(canonical));
    assertArrayEquals(wire, accepted.body());
    assertEquals(correlationId, accepted.correlationId().toString());

    String[][] aliases = {
      {
        "0000000A-000B-000C-000D-00000000000E",
        "a-b-c-d-e",
        "0000000a-b-000c-000d-00000000000e",
        " " + messageId,
        messageId + " "
      },
      {
        "0000000F-0010-0011-0012-000000000013",
        "f-10-11-12-13",
        "0000000f-10-0011-0012-000000000013",
        " " + correlationId,
        correlationId + " "
      }
    };
    String[] fields = {MESSAGE_ID_PROPERTY, CORRELATION_FIELD};
    for (int field = 0; field < fields.length; field++) {
      for (String alias : aliases[field]) {
        assertRejected(bytesMessage(with(canonical, fields[field], alias)));
      }
    }
  }

  private static Map<String, Object> validReply() {
    byte[] body = responseWire();
    Map<String, Object> values = new HashMap<>();
    values.put(BODY_FIELD, body);
    values.put(BODY_LENGTH_FIELD, (long) body.length);
    values.put(DESTINATION_FIELD, new ActiveMQQueue("nk.sync.reply.web"));
    values.put("replyTo", null);
    values.put(TRANSPORT_ID_FIELD, "ID:provider-transport-id");
    values.put(CORRELATION_FIELD, REQUEST_ID);
    values.put(EXPIRATION_FIELD, 1_000L);
    values.put("deliveryMode", DeliveryMode.PERSISTENT);
    values.put("JMSXDeliveryCount", 1);
    values.put(MESSAGE_ID_PROPERTY, RESPONSE_ID);
    values.put(LAYOUT_ID_PROPERTY, "LOGRSP01");
    values.put(VERSION_PROPERTY, "001");
    return values;
  }

  private static Map<String, Object> with(Map<String, Object> source, String name, Object value) {
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
                return values.get(BODY_LENGTH_FIELD);
              }
              if (name.equals("getBody")) {
                byte[] body = (byte[]) values.get(BODY_FIELD);
                return body == null ? null : body.clone();
              }
              if (name.equals("getJMSDestination")) {
                return values.get(DESTINATION_FIELD);
              }
              if (name.equals("getJMSReplyTo")) {
                return values.get("replyTo");
              }
              if (name.equals("getJMSMessageID")) {
                return values.get(TRANSPORT_ID_FIELD);
              }
              if (name.equals("getJMSCorrelationID")) {
                return values.get(CORRELATION_FIELD);
              }
              if (name.equals("getJMSExpiration")) {
                return values.get(EXPIRATION_FIELD);
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
