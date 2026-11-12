package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.messaging.guard.GuardedJmsMessage;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import java.lang.reflect.Proxy;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-JMS-009 body invariance, exact metadata allowlist, bounds and null contracts. */
final class FatalDlqMessageWriterTest {
  private static final UUID MESSAGE_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
  private static final UUID CORRELATION_ID =
      UUID.fromString("00000000-0000-0000-0000-000000000002");
  private static final Instant DETECTED_AT = Instant.parse("2026-09-03T00:00:00Z");

  @Test
  void writerCopiesBodyAndOnlyApprovedBoundedMetadata() throws Exception {
    Capture capture = new Capture();
    byte[] sourceBody = {1, 2, 3};
    GuardedJmsMessage rejected = rejected(sourceBody, "ID:provider-1");
    sourceBody[0] = 9;
    FatalDlqMetadata fatal =
        new FatalDlqMetadata("PROTOCOL_INVALID", FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT);

    BytesMessage result = FatalDlqMessageWriter.INSTANCE.create(context(capture), rejected, fatal);

    assertEquals(capture.message, result);
    assertArrayEquals(new byte[] {1, 2, 3}, capture.body);
    assertEquals(CORRELATION_ID.toString(), capture.correlationId);
    assertEquals(
        Map.of(
            "_AMQ_ORIG_ADDRESS", "nk.sync.request",
            "_AMQ_ORIG_QUEUE", "nk.sync.request.q",
            "NKOriginalTransportID", "ID:provider-1",
            "NKMessageID", MESSAGE_ID.toString(),
            "NKCorrelationID", CORRELATION_ID.toString(),
            "NKLayoutID", "LOGREQ01",
            "NKErrorCode", "PROTOCOL_INVALID",
            "NKDetectedBy", "API_SYNC",
            "NKDetectedAt", "2026-09-03T00:00:00Z"),
        capture.stringProperties);
    assertEquals(Map.of("NKDeliveryCount", 4), capture.intProperties);
    assertFalse(capture.stringProperties.containsKey("Password"));
    assertFalse(capture.stringProperties.containsKey("BodyHash"));
  }

  @Test
  void metadataAndWriterContractsDenyNullAndUnboundedValues() {
    FatalDlqMetadata valid =
        new FatalDlqMetadata("INVALID", FatalDlqMetadata.DetectedBy.WEB_REPLY, DETECTED_AT);
    JMSContext context = context(new Capture());
    GuardedJmsMessage rejected = rejected(new byte[0], "ID:1");
    assertThrows(
        NullPointerException.class,
        () -> FatalDlqMessageWriter.INSTANCE.create(null, rejected, valid));
    assertThrows(
        NullPointerException.class,
        () -> FatalDlqMessageWriter.INSTANCE.create(context, null, valid));
    assertThrows(
        NullPointerException.class,
        () -> FatalDlqMessageWriter.INSTANCE.create(context, rejected, null));
    assertThrows(
        NullPointerException.class,
        () -> new FatalDlqMetadata(null, FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT));
    assertThrows(
        NullPointerException.class, () -> new FatalDlqMetadata("INVALID", null, DETECTED_AT));
    assertThrows(
        NullPointerException.class,
        () -> new FatalDlqMetadata("INVALID", FatalDlqMetadata.DetectedBy.API_SYNC, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FatalDlqMetadata("", FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FatalDlqMetadata("1BAD", FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FatalDlqMetadata("lower", FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new FatalDlqMetadata(
                "A".repeat(33), FatalDlqMetadata.DetectedBy.API_SYNC, DETECTED_AT));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FatalDlqMessageWriter.INSTANCE.create(
                context, rejected(new byte[0], "A".repeat(129)), valid));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FatalDlqMessageWriter.INSTANCE.create(context, rejected(new byte[0], "ID:\n1"), valid));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            FatalDlqMessageWriter.INSTANCE.create(
                context, rejected(new byte[0], "ID:\u00e9"), valid));
  }

  @Test
  void enumsExposeTheClosedWriterAndDetectedBySets() {
    assertEquals(1, FatalDlqMessageWriter.values().length);
    assertEquals(FatalDlqMessageWriter.INSTANCE, FatalDlqMessageWriter.valueOf("INSTANCE"));
    assertEquals(4, FatalDlqMetadata.DetectedBy.values().length);
    assertEquals(
        FatalDlqMetadata.DetectedBy.API_WEB_LOG,
        FatalDlqMetadata.DetectedBy.valueOf("API_WEB_LOG"));
    assertEquals(FatalDlqMetadata.DetectedBy.API_WORK, FatalDlqMetadata.DetectedBy.values()[1]);
  }

  @Test
  void exactPrintable128AndErrorCode32BoundariesAreRetainedWithoutTrimming() throws Exception {
    // SS321 section11: independently authored exact maxima, including ASCII space and tilde.
    for (String transport : new String[] {"!" + " ".repeat(126) + "~", "~".repeat(128)}) {
      for (String code : new String[] {"A", "A" + "Z".repeat(31)}) {
        Capture capture = new Capture();
        byte[] body = {0, 32, (byte) 0xff};
        FatalDlqMetadata metadata =
            new FatalDlqMetadata(code, FatalDlqMetadata.DetectedBy.WEB_REPLY, DETECTED_AT);
        FatalDlqMessageWriter.INSTANCE.create(
            context(capture), rejected(body, transport), metadata);
        assertArrayEquals(new byte[] {0, 32, (byte) 0xff}, capture.body);
        assertEquals(128, transport.length());
        assertEquals(transport, capture.stringProperties.get("NKOriginalTransportID"));
        assertEquals(code, capture.stringProperties.get("NKErrorCode"));
      }
    }
    FatalDlqMetadata metadata =
        new FatalDlqMetadata("A", FatalDlqMetadata.DetectedBy.WEB_REPLY, DETECTED_AT);
    for (String bad : new String[] {"X\u001f", "X\u007f"}) {
      Capture capture = new Capture();
      assertThrows(
          IllegalArgumentException.class,
          () ->
              FatalDlqMessageWriter.INSTANCE.create(
                  context(capture), rejected(new byte[0], bad), metadata));
      assertEquals(0, capture.stringProperties.size());
    }
  }

  private static GuardedJmsMessage rejected(byte[] body, String transportId) {
    return new GuardedJmsMessage(
        body,
        new TransportMetadata(
            TransportBodyType.BYTES,
            transportId,
            CORRELATION_ID,
            Optional.of("nk.sync.reply.web"),
            1_000,
            2,
            4,
            MESSAGE_ID,
            new LayoutId("LOGREQ01"),
            "001",
            "nk.sync.request"));
  }

  private static JMSContext context(Capture capture) {
    return proxy(
        JMSContext.class,
        (ignored, method, arguments) -> {
          if (method.getName().equals("createBytesMessage")) {
            return capture.message;
          }
          return objectMethod(ignored, method.getName(), arguments);
        });
  }

  private static BytesMessage message(Capture capture) {
    return proxy(
        BytesMessage.class,
        (ignored, method, arguments) -> {
          switch (method.getName()) {
            case "writeBytes" -> capture.body = ((byte[]) arguments[0]).clone();
            case "setJMSCorrelationID" -> capture.correlationId = (String) arguments[0];
            case "setStringProperty" ->
                capture.stringProperties.put((String) arguments[0], (String) arguments[1]);
            case "setIntProperty" ->
                capture.intProperties.put((String) arguments[0], (Integer) arguments[1]);
            default -> {
              return objectMethod(ignored, method.getName(), arguments);
            }
          }
          return null;
        });
  }

  private static Object objectMethod(Object proxy, String method, Object[] arguments) {
    return switch (method) {
      case "toString" -> "SyntheticJmsBoundary";
      case "hashCode" -> System.identityHashCode(proxy);
      case "equals" -> proxy == arguments[0];
      default -> throw new UnsupportedOperationException(method);
    };
  }

  private static <T> T proxy(Class<T> type, java.lang.reflect.InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  private static final class Capture {
    private final Map<String, String> stringProperties = new HashMap<>();
    private final Map<String, Integer> intProperties = new HashMap<>();
    private final BytesMessage message = message(this);
    private byte[] body;
    private String correlationId;
  }
}
