package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import org.junit.jupiter.api.Test;

/** NK-MSG-001/MQ003008/UI231232/SS321322; PT-JMS-MFACT001..008. No broker/provider. */
final class JmsMessageFactoryPortTest {
  private static final char EVENT_KIND = 'E';
  private static final char RESPONSE_KIND = 'S';
  private static final String REQUEST_ID = "00000000-0000-0000-0000-000000000001";
  private static final String RESPONSE_ID = "00000000-0000-0000-0000-000000000002";
  private static final String SENT_AT = "20261107210000000";
  private static final String VERSION = "001";
  private static final String LOG_RESPONSE = "LOGRSP01";
  private static final String ASYNC_RESPONSE = "QSBRSP01";
  private static final String LOG_REQUEST = "LOGREQ01";
  private static final String INTERNAL_EVENT = "QWKREQ01";
  private static final String MESSAGE_PROPERTY = "NKMessageID";
  private static final String LAYOUT_PROPERTY = "NKLayoutID";
  private static final String VERSION_PROPERTY = "NKProtocolVersion";
  private static final List<Stage> ASSEMBLY =
      List.of(
          Stage.CREATE, Stage.WRITE, Stage.CORRELATION, Stage.MESSAGE, Stage.LAYOUT, Stage.VERSION);

  /** PT-JMS-MFACT001: literal SS byte positions and properties; caller owns context/message. */
  @Test
  void syncGoldenFieldsAndCallerOwnership() throws Exception {
    byte[] wire = golden(LOG_RESPONSE, 'S', 'S', 24);
    byte[] before = wire.clone();
    Port port = new Port(Stage.NONE, false);
    assertSame(port.message, JmsMessageFactory.INSTANCE.createReply(port.context, wire));
    assertArrayEquals(before, wire);
    assertArrayEquals(before, port.body);
    assertEquals(280, port.body.length);
    assertEquals(REQUEST_ID, port.correlation);
    assertEquals(
        Map.of(
            MESSAGE_PROPERTY,
            RESPONSE_ID,
            LAYOUT_PROPERTY,
            LOG_RESPONSE,
            VERSION_PROPERTY,
            VERSION),
        port.properties);
    assertEquals(ASSEMBLY, port.calls);
  }

  /** PT-JMS-MFACT002: QSB S/A is an approved reply profile, with the same three property rules. */
  @Test
  void asyncAcceptanceGoldenFields() throws Exception {
    byte[] wire = golden(ASYNC_RESPONSE, 'S', 'A', 64);
    Port port = new Port(Stage.NONE, false);
    assertSame(port.message, JmsMessageFactory.INSTANCE.createReply(port.context, wire));
    assertArrayEquals(wire, port.body);
    assertEquals(320, port.body.length);
    assertEquals(REQUEST_ID, port.correlation);
    assertEquals(
        Map.of(
            MESSAGE_PROPERTY,
            RESPONSE_ID,
            LAYOUT_PROPERTY,
            ASYNC_RESPONSE,
            VERSION_PROPERTY,
            VERSION),
        port.properties);
    assertEquals(ASSEMBLY, port.calls);
  }

  /** PT-JMS-MFACT003: explicit null contracts fail before invoking any provider operation. */
  @Test
  void rejectsNullPortsBeforeProviderUse() {
    byte[] wire = golden(LOG_RESPONSE, 'S', 'S', 24);
    Port port = new Port(Stage.NONE, false);
    assertThrows(
        NullPointerException.class, () -> JmsMessageFactory.INSTANCE.createReply(null, wire));
    assertThrows(
        NullPointerException.class,
        () -> JmsMessageFactory.INSTANCE.createReply(port.context, null));
    assertEquals(List.of(), port.calls);
  }

  /** PT-JMS-MFACT004: header prerequisites, including reserved bytes, cannot reach JMS. */
  @Test
  void rejectsMalformedCommonHeaderBeforeProviderUse() {
    Port port = new Port(Stage.NONE, false);
    for (int length : new int[] {0, 255}) {
      assertThrows(
          PermanentProtocolException.class,
          () -> JmsMessageFactory.INSTANCE.createReply(port.context, new byte[length]));
    }
    byte[] reserved = golden(LOG_RESPONSE, 'S', 'S', 24);
    reserved[212] = 'X';
    assertThrows(
        PermanentProtocolException.class,
        () -> JmsMessageFactory.INSTANCE.createReply(port.context, reserved));
    assertEquals(List.of(), port.calls);
  }

  /** PT-JMS-MFACT005: valid request/event headers are still not outbound replies. */
  @Test
  void rejectsRequestAndInternalEventBeforeProviderUse() {
    Port port = new Port(Stage.NONE, false);
    for (byte[] wire :
        List.of(golden(LOG_REQUEST, 'Q', 'S', 0), golden(INTERNAL_EVENT, 'E', 'I', 64))) {
      assertThrows(
          IllegalArgumentException.class,
          () -> JmsMessageFactory.INSTANCE.createReply(port.context, wire));
    }
    assertEquals(List.of(), port.calls);
  }

  /** PT-JMS-MFACT006: exact cap and cap+1; body/header mismatch on both sides of valid280. */
  @Test
  void enforcesByteLimitAndExactDeclaredLengthBoundaries() {
    Port port = new Port(Stage.NONE, false);
    byte[] wire = golden(LOG_RESPONSE, 'S', 'S', 24);
    for (int length : new int[] {279, 281, 1_000_000, 1_000_001}) {
      byte[] invalid = Arrays.copyOf(wire, length);
      assertThrows(
          IllegalArgumentException.class,
          () -> JmsMessageFactory.INSTANCE.createReply(port.context, invalid));
    }
    assertEquals(List.of(), port.calls);
  }

  /**
   * PT-JMS-MFACT007: preserve checked identity and stop without later settings or ownership calls.
   */
  @Test
  void retainsCheckedFailureAtEveryAssemblyStage() {
    byte[] wire = golden(LOG_RESPONSE, 'S', 'S', 24);
    for (int index = 1; index < ASSEMBLY.size(); index++) {
      Port port = new Port(ASSEMBLY.get(index), false);
      assertSame(
          port.checkedFailure,
          assertThrows(
              JMSException.class,
              () -> JmsMessageFactory.INSTANCE.createReply(port.context, wire)));
      assertEquals(ASSEMBLY.subList(0, index + 1), port.calls);
    }
  }

  /** PT-JMS-MFACT008: provider creation failure is not swallowed, retried or translated. */
  @Test
  void preservesProviderRuntimeFailureIdentity() {
    Port port = new Port(Stage.NONE, true);
    byte[] wire = golden(LOG_RESPONSE, 'S', 'S', 24);
    assertSame(
        port.runtimeFailure,
        assertThrows(
            JMSRuntimeException.class,
            () -> JmsMessageFactory.INSTANCE.createReply(port.context, wire)));
    assertEquals(List.of(Stage.CREATE), port.calls);
  }

  /** Independent UI232 one-based fields converted to literal zero-based offsets. */
  private static byte[] golden(String layout, char kind, char interaction, int dataLength) {
    byte[] wire = new byte[256 + dataLength];
    Arrays.fill(wire, (byte) ' ');
    put(wire, 0, "SCHBNK01");
    put(wire, 8, VERSION);
    put(wire, 11, layout);
    put(wire, 19, VERSION);
    wire[22] = (byte) kind;
    wire[23] = (byte) interaction;
    put(wire, 24, kind == 'Q' ? REQUEST_ID : RESPONSE_ID);
    put(wire, 60, REQUEST_ID);
    put(wire, 96, SENT_AT);
    if (kind != EVENT_KIND)
      put(wire, 113, "a".repeat(64)); // Public, non-live synthetic context only.
    put(wire, 177, "0256");
    put(wire, 181, String.format(Locale.ROOT, "%06d", dataLength));
    put(wire, 187, "000000");
    put(wire, 193, "000000");
    put(wire, 199, String.format(Locale.ROOT, "%09d", wire.length));
    if (kind == RESPONSE_KIND) put(wire, 208, "0000");
    if (layout.equals(LOG_RESPONSE)) put(wire, 256, SENT_AT);
    if (layout.equals(ASYNC_RESPONSE) || layout.equals(INTERNAL_EVENT)) {
      put(wire, 256, "R".repeat(26));
      put(wire, 282, "000000000001");
      put(wire, 294, layout.equals(ASYNC_RESPONSE) ? SENT_AT : "000000000002");
    }
    return wire;
  }

  private static void put(byte[] wire, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, wire, offset, bytes.length);
  }

  private enum Stage {
    NONE,
    CREATE,
    WRITE,
    CORRELATION,
    MESSAGE,
    LAYOUT,
    VERSION
  }

  /** Strict supplied interface port. Unknown JMS operations fail; no provider is constructed. */
  private static final class Port {
    private final Stage failureStage;
    private final boolean failCreate;
    private final JMSException checkedFailure = new JMSException("PUBLIC-ASSEMBLY-FAILURE");
    private final JMSRuntimeException runtimeFailure =
        new JMSRuntimeException("PUBLIC-CREATE-FAILURE");
    private final List<Stage> calls = new ArrayList<>();
    private final Map<String, String> properties = new LinkedHashMap<>();
    private final BytesMessage message;
    private final JMSContext context;
    private byte[] body = new byte[0];
    private String correlation = "";

    private Port(Stage failureStage, boolean failCreate) {
      this.failureStage = Objects.requireNonNull(failureStage, "failure stage");
      this.failCreate = failCreate;
      message =
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  this::messageCall);
      context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (proxy, method, args) -> {
                    if (method.getDeclaringClass() == Object.class)
                      return objectCall(proxy, method, args);
                    if (!method.getName().equals("createBytesMessage"))
                      throw new AssertionError("unapproved context call " + method.getName());
                    calls.add(Stage.CREATE);
                    if (this.failCreate) throw runtimeFailure;
                    return message;
                  });
    }

    private Object messageCall(Object proxy, Method method, Object[] args) throws JMSException {
      if (method.getDeclaringClass() == Object.class) return objectCall(proxy, method, args);
      Object[] values = Objects.requireNonNull(args, "message arguments");
      switch (method.getName()) {
        case "writeBytes" -> {
          recordCall(Stage.WRITE);
          body = ((byte[]) values[0]).clone();
        }
        case "setJMSCorrelationID" -> {
          recordCall(Stage.CORRELATION);
          correlation = (String) values[0];
        }
        case "setStringProperty" -> {
          String key = (String) values[0];
          Stage step =
              switch (key) {
                case MESSAGE_PROPERTY -> Stage.MESSAGE;
                case LAYOUT_PROPERTY -> Stage.LAYOUT;
                case VERSION_PROPERTY -> Stage.VERSION;
                default -> throw new AssertionError("unapproved property " + key);
              };
          recordCall(step);
          properties.put(key, (String) values[1]);
        }
        default -> throw new AssertionError("unapproved message call " + method.getName());
      }
      return null; // InvocationHandler contract for these three void JMS methods.
    }

    private void recordCall(Stage step) throws JMSException {
      calls.add(step);
      if (failureStage == step) throw checkedFailure;
    }

    private static Object objectCall(Object proxy, Method method, Object[] args) {
      return switch (method.getName()) {
        case "equals" -> proxy == Objects.requireNonNull(args)[0];
        case "hashCode" -> System.identityHashCode(proxy);
        case "toString" -> "JMSPort[TEST-ONLY]";
        default -> throw new AssertionError("unapproved Object call");
      };
    }
  }
}
