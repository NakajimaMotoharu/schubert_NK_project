package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.*;

import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.JMSRuntimeException;
import java.io.InputStream;
import java.lang.reflect.Proxy;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;
import org.apache.activemq.artemis.core.config.Configuration;
import org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser;
import org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-IDEM-012: independent SS323 golden and actual broker transaction/duplicate after-conditions.
 */
final class WebLogMessageSenderTest {
  private static final Instant NOW = Instant.parse("2026-09-06T00:00:00Z");
  private static final WebLogPayloadIdentity IDENTITY =
      new WebLogPayloadIdentity(
          UUID.fromString("00000000-0000-0000-0000-000000000012"),
          UUID.fromString("00000000-0000-0000-0000-000000000015"));

  @Test
  void sendsExactPlaintextWithPersistentPropertiesAndSuppressesConfirmedDuplicate(
      @TempDir Path root) throws Exception {
    EmbeddedActiveMQ broker = broker(root);
    try (ActiveMQConnectionFactory factory = new ActiveMQConnectionFactory("vm://0");
        WebLogPayloadCodec codec = codec();
        JMSContext observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
        var consumer = observer.createConsumer(new ActiveMQQueue("nk.web.log::nk.web.log.q"))) {
      byte[] expected = WebLogPayloadCodecTest.goldenWire();
      ClaimedWebLog row = row(codec.encrypt(IDENTITY, expected));
      WebLogMessageSender sender =
          new WebLogMessageSender(
              codec, () -> factory.createContext(JMSContext.SESSION_TRANSACTED));
      sender.send(row);
      sender.send(row);
      BytesMessage actual = assertInstanceOf(BytesMessage.class, consumer.receive(5000));
      assertEquals(2336, actual.getBodyLength());
      byte[] bytes = new byte[2336];
      assertEquals(2336, actual.readBytes(bytes));
      assertArrayEquals(expected, bytes);
      assertEquals(IDENTITY.messageId().toString(), actual.getStringProperty("NKMessageID"));
      assertEquals(IDENTITY.messageId().toString(), actual.getStringProperty("_AMQ_DUPL_ID"));
      assertEquals(IDENTITY.correlationId().toString(), actual.getJMSCorrelationID());
      assertEquals("WLGEVT01", actual.getStringProperty("NKLayoutID"));
      assertEquals("001", actual.getStringProperty("NKProtocolVersion"));
      assertEquals(DeliveryMode.PERSISTENT, actual.getJMSDeliveryMode());
      assertEquals(0, actual.getJMSExpiration());
      assertNull(actual.getJMSReplyTo());
      assertNull(consumer.receive(250));
      assertArrayEquals(expected, codec.decrypt(IDENTITY, row.payload()));
    } finally {
      broker.stop();
    }
  }

  @Test
  void nullConfigurationAndInvalidAuthenticatedStorageNeverOpenJms() {
    try (WebLogPayloadCodec codec = codec()) {
      AtomicInteger opened = new AtomicInteger();
      WebLogMessageSender sender =
          new WebLogMessageSender(
              codec,
              () -> {
                opened.incrementAndGet();
                throw new AssertionError("invalid storage must not acquire JMS");
              });
      assertThrows(NullPointerException.class, () -> new WebLogMessageSender(null, () -> null));
      assertThrows(NullPointerException.class, () -> new WebLogMessageSender(codec, null));
      assertThrows(NullPointerException.class, () -> sender.send(null));
      assertThrows(
          WebLogPayloadException.class,
          () -> sender.send(row(new EncryptedWebLogPayload("test", new byte[64]))));
      EncryptedWebLogPayload valid = codec.encrypt(IDENTITY, WebLogPayloadCodecTest.goldenWire());
      ClaimedWebLog swapped =
          new ClaimedWebLog(
              1,
              new WebLogPayloadIdentity(new UUID(9, 9), IDENTITY.correlationId()),
              valid,
              0,
              NOW,
              NOW,
              "w",
              NOW.plusSeconds(10));
      assertThrows(WebLogPayloadException.class, () -> sender.send(swapped));
      assertEquals(0, opened.get());
    }
  }

  @Test
  void eachProviderFailureIsBoundedAndUnconfirmedSendRollsBackAndErasesPlaintext() {
    try (WebLogPayloadCodec codec = codec()) {
      ClaimedWebLog row = row(codec.encrypt(IDENTITY, WebLogPayloadCodecTest.goldenWire()));
      WebLogSendException nullContext =
          assertThrows(
              WebLogSendException.class,
              () -> new WebLogMessageSender(codec, () -> null).send(row));
      assertEquals("web log JMS lifecycle failed", nullContext.getMessage());
      assertInstanceOf(NullPointerException.class, nullContext.getCause());
      for (String failpoint :
          new String[] {"mode", "write", "send", "commit", "rollback", "close", "open"}) {
        AtomicInteger rolledBack = new AtomicInteger();
        AtomicReference<byte[]> written = new AtomicReference<>();
        WebLogMessageSender sender =
            new WebLogMessageSender(
                codec,
                () -> {
                  if (failpoint.equals("open")) {
                    throw new JMSRuntimeException("synthetic open failure");
                  }
                  return fakeContext(failpoint, rolledBack, written);
                });
        WebLogSendException error =
            assertThrows(WebLogSendException.class, () -> sender.send(row), failpoint);
        String expected =
            switch (failpoint) {
              case "mode" -> "web log JMS context is not transacted";
              case "commit" -> "web log JMS commit was not confirmed";
              case "open", "close" -> "web log JMS lifecycle failed";
              default -> "web log JMS send was not confirmed";
            };
        assertEquals(expected, error.getMessage());
        assertFalse(error.toString().contains(IDENTITY.messageId().toString()));
        if (written.get() != null) {
          assertArrayEquals(
              new byte[2336], written.get(), "owned plaintext erased on all send exits");
        }
        if (failpoint.equals("rollback")) {
          assertEquals(1, error.getCause().getSuppressed().length);
        }
        assertEquals(
            switch (failpoint) {
              case "mode", "open", "close" -> 0;
              default -> 1;
            },
            rolledBack.get());
      }
    }
  }

  @Test
  void duplicateDetectionUsesTypedCauseAndLinkedGraphNotTextAndTerminatesCycles() {
    assertThrows(NullPointerException.class, () -> WebLogMessageSender.duplicateConfirmed(null));
    assertFalse(WebLogMessageSender.duplicateConfirmed(new JMSException("duplicate")));
    assertFalse(
        WebLogMessageSender.duplicateConfirmed(
            new RuntimeException("ActiveMQDuplicateIdException")));
    ActiveMQDuplicateIdException duplicate =
        new ActiveMQDuplicateIdException("synthetic duplicate");
    assertTrue(WebLogMessageSender.duplicateConfirmed(duplicate));
    assertTrue(WebLogMessageSender.duplicateConfirmed(new RuntimeException(duplicate)));
    JMSException linked = new JMSException("synthetic linked");
    linked.setLinkedException(duplicate);
    assertTrue(WebLogMessageSender.duplicateConfirmed(linked));
    Exception first = new Exception("first");
    Exception second = new Exception("second", first);
    first.initCause(second);
    assertFalse(WebLogMessageSender.duplicateConfirmed(first));
    JMSException branched = new JMSException("branched");
    branched.initCause(duplicate);
    branched.setLinkedException(first);
    assertTrue(WebLogMessageSender.duplicateConfirmed(branched));
  }

  private static WebLogPayloadCodec codec() {
    return new WebLogPayloadCodec("test", new byte[32], null, null);
  }

  private static ClaimedWebLog row(EncryptedWebLogPayload payload) {
    return new ClaimedWebLog(1, IDENTITY, payload, 0, NOW, NOW, "worker", NOW.plusSeconds(10));
  }

  static JMSContext fakeContext(
      String point, AtomicInteger rolledBack, AtomicReference<byte[]> written) {
    BytesMessage bytes =
        (BytesMessage)
            Proxy.newProxyInstance(
                BytesMessage.class.getClassLoader(),
                new Class<?>[] {BytesMessage.class},
                (proxy, method, args) -> {
                  if (method.getName().equals("writeBytes")) {
                    written.set((byte[]) args[0]);
                    if (point.equals("write")) {
                      throw new JMSException("synthetic write failure");
                    }
                  }
                  return null;
                });
    JMSProducer producer =
        (JMSProducer)
            Proxy.newProxyInstance(
                JMSProducer.class.getClassLoader(),
                new Class<?>[] {JMSProducer.class},
                (proxy, method, args) -> {
                  if (method.getName().equals("send")
                      && (point.equals("send") || point.equals("rollback"))) {
                    throw new JMSRuntimeException("synthetic send failure");
                  }
                  return proxy;
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, args) ->
                switch (method.getName()) {
                  case "getSessionMode" ->
                      point.equals("mode")
                          ? JMSContext.AUTO_ACKNOWLEDGE
                          : JMSContext.SESSION_TRANSACTED;
                  case "createBytesMessage" -> bytes;
                  case "createProducer" -> producer;
                  case "commit" -> {
                    if (point.equals("commit")) {
                      throw new JMSRuntimeException("synthetic commit failure");
                    }
                    yield null;
                  }
                  case "rollback" -> {
                    rolledBack.incrementAndGet();
                    if (point.equals("rollback")) {
                      throw new JMSRuntimeException("synthetic rollback failure");
                    }
                    yield null;
                  }
                  case "close" -> {
                    if (point.equals("close")) {
                      throw new JMSRuntimeException("synthetic close failure");
                    }
                    yield null;
                  }
                  default ->
                      throw new AssertionError(
                          "unexpected synthetic context method " + method.getName());
                });
  }

  static EmbeddedActiveMQ broker(Path root) throws Exception {
    Configuration configuration;
    try (InputStream input = Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration = new FileConfigurationParser().parseMainConfig(input);
    }
    configuration
        .setPagingDirectory(root.resolve("paging").toString())
        .setBindingsDirectory(root.resolve("bindings").toString())
        .setJournalDirectory(root.resolve("journal").toString())
        .setLargeMessagesDirectory(root.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", "vm://0");
    return new EmbeddedActiveMQ().setConfiguration(configuration).start();
  }
}
