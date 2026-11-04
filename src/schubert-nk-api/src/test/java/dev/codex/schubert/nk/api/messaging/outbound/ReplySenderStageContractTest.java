package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.Message;
import jakarta.jms.Queue;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** NK-MSG-001; MQ003/008; UI212/231/232; SS312/321; PT-JMS-STAGE001..004. */
final class ReplySenderStageContractTest {
  private static final String MODE = "mode";
  private static final String BYTES = "bytes";
  private static final String WRITE = "write";
  private static final String CORRELATION = "correlation";
  private static final String PRODUCER = "producer";
  private static final String PERSISTENT = "persistent";
  private static final String TTL = "ttl";
  private static final String SEND = "send";
  private static final String FAILURE = "synthetic reply stage";
  private static final List<String> ORDER =
      List.of(
          MODE,
          BYTES,
          WRITE,
          CORRELATION,
          "NKMessageID",
          "NKLayoutID",
          "NKProtocolVersion",
          PRODUCER,
          PERSISTENT,
          TTL,
          SEND);

  @Test
  void stage001FixedPersistentReplyUsesBorrowedContextWithoutCommitOrClose() throws Exception {
    var fixture = new Fixture(0, null, null);
    byte[] wire = loginErrorReply();
    new ReplySender().send(fixture.context, wire);
    assertEquals(ORDER, fixture.events);
    assertEquals(2, fixture.deliveryMode);
    assertEquals(10_000L, fixture.timeToLive);
    assertEquals("nk.sync.reply.web::nk.sync.reply.web.q", fixture.destination);
    assertSame(fixture.message, fixture.sentMessage);
  }

  @Test
  void stage002NullAndEveryNontransactedModeRejectBeforeMessageCreation() {
    var sender = new ReplySender();
    byte[] wire = loginErrorReply();
    var fixture = new Fixture(0, null, null);
    assertThrows(NullPointerException.class, () -> sender.send(null, wire));
    assertThrows(NullPointerException.class, () -> sender.send(fixture.context, null));
    assertEquals(List.of(), fixture.events);
    for (int mode : new int[] {1, 2, 3, -1}) {
      var invalid = new Fixture(mode, null, null);
      assertThrows(IllegalStateException.class, () -> sender.send(invalid.context, wire));
      assertEquals(List.of(MODE), invalid.events);
    }
  }

  @Test
  void stage003EveryRuntimeOrFatalStageKeepsIdentityAndNeverRetries() {
    byte[] wire = loginErrorReply();
    var sender = new ReplySender();
    for (String stage : List.of(MODE, PRODUCER, PERSISTENT, TTL, SEND)) {
      for (Throwable failure :
          List.of(new IllegalStateException(FAILURE), new AssertionError(FAILURE))) {
        var fixture = new Fixture(0, stage, failure);
        assertSame(
            failure, assertThrows(failure.getClass(), () -> sender.send(fixture.context, wire)));
        assertEquals(ORDER.subList(0, ORDER.indexOf(stage) + 1), fixture.events);
      }
    }
  }

  @Test
  void stage004CheckedMessageConstructionFailureNeverAcquiresProducer() {
    byte[] wire = loginErrorReply();
    var sender = new ReplySender();
    var failure = new JMSException(FAILURE);
    var fixture = new Fixture(0, WRITE, failure);
    assertSame(failure, assertThrows(JMSException.class, () -> sender.send(fixture.context, wire)));
    assertEquals(List.of(MODE, BYTES, WRITE), fixture.events);
  }

  /** UI232/233 IF001 independent literal error header, no auth or production encoder. */
  private static byte[] loginErrorReply() {
    byte[] body = new byte[688];
    Arrays.fill(body, (byte) ' ');
    put(body, 0, "SCHBNK01");
    put(body, 8, "001");
    put(body, 11, "LGNRSP01");
    put(body, 19, "001");
    put(body, 22, "SS");
    put(body, 24, "00000000-0000-0000-0000-000000000002");
    put(body, 60, "00000000-0000-0000-0000-000000000001");
    put(body, 96, "20260903120000000");
    put(body, 177, "0256");
    put(body, 181, "000432");
    put(body, 187, "000000");
    put(body, 193, "000000");
    put(body, 199, "000000688");
    put(body, 208, "0100");
    return body;
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }

  private static final class Fixture {
    private final List<String> events = new ArrayList<>();
    private final BytesMessage message;
    private final JMSContext context;
    private int deliveryMode;
    private long timeToLive;
    private String destination;
    private Message sentMessage;

    Fixture(int mode, String failedStage, Throwable failure) {
      message =
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  (proxy, method, args) -> {
                    String stage =
                        switch (method.getName()) {
                          case "writeBytes" -> {
                            assertEquals(1, method.getParameterCount());
                            yield WRITE;
                          }
                          case "setJMSCorrelationID" -> CORRELATION;
                          case "setStringProperty" -> (String) args[0];
                          default -> throw new AssertionError("unexpected message method");
                        };
                    events.add(stage);
                    if (stage.equals(failedStage)) throw failure;
                    return null;
                  });
      JMSProducer producer =
          (JMSProducer)
              Proxy.newProxyInstance(
                  JMSProducer.class.getClassLoader(),
                  new Class<?>[] {JMSProducer.class},
                  (proxy, method, args) -> {
                    String stage =
                        switch (method.getName()) {
                          case "setDeliveryMode" -> PERSISTENT;
                          case "setTimeToLive" -> TTL;
                          case "send" -> SEND;
                          default -> throw new AssertionError("unexpected producer method");
                        };
                    events.add(stage);
                    if (stage.equals(failedStage)) throw failure;
                    switch (method.getName()) {
                      case "setDeliveryMode" -> deliveryMode = (Integer) args[0];
                      case "setTimeToLive" -> timeToLive = (Long) args[0];
                      case "send" -> {
                        assertEquals(2, method.getParameterCount());
                        assertEquals(Message.class, method.getParameterTypes()[1]);
                        destination = ((Queue) args[0]).getQueueName();
                        sentMessage = (Message) args[1];
                      }
                      default -> throw new AssertionError("unexpected producer method");
                    }
                    return proxy;
                  });
      context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (proxy, method, args) -> {
                    String stage =
                        switch (method.getName()) {
                          case "getSessionMode" -> MODE;
                          case "createBytesMessage" -> BYTES;
                          case "createProducer" -> PRODUCER;
                          default ->
                              throw new AssertionError("borrowed context operation forbidden");
                        };
                    events.add(stage);
                    if (stage.equals(failedStage)) throw failure;
                    return switch (method.getName()) {
                      case "getSessionMode" -> mode;
                      case "createBytesMessage" -> message;
                      case "createProducer" -> producer;
                      default -> throw new AssertionError("borrowed context operation forbidden");
                    };
                  });
    }
  }
}
