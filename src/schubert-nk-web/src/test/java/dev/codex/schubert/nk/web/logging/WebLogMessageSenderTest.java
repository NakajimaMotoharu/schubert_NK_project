package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
import java.util.Optional;
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

  /** SSC321/BUG1569: independent fixed outcome table, not production-derived expected failures. */
  @Test
  void cleanup321002FatalCleanupPriorityAndPlaintextWipe() throws Exception {
    int[][] outcome = {{0, 1, 2}, {1, 1, 2}, {3, 3, 3}, {1, 1, 2}};
    try (WebLogPayloadCodec codec = codec()) {
      byte[] golden = WebLogPayloadCodecTest.goldenWire();
      ClaimedWebLog row = row(codec.encrypt(IDENTITY, golden));
      for (int primaryKind : new int[] {1, 0, 2, 3}) {
        for (int closeKind : new int[] {2, 0, 1}) {
          Optional<Throwable> primary =
              switch (primaryKind) {
                case 0 -> Optional.empty();
                case 1 -> Optional.of(new IllegalStateException("independent primary"));
                case 2 -> Optional.of(new AssertionError("independent primary"));
                default -> Optional.of(new JMSException("independent primary"));
              };
          Optional<Throwable> closing =
              switch (closeKind) {
                case 0 -> Optional.empty();
                case 1 -> Optional.of(new IllegalArgumentException("independent cleanup"));
                default -> Optional.of(new LinkageError("independent cleanup"));
              };
          var counts = cleanup321Counters();
          var plain = new AtomicReference<byte[]>();
          var captured = new AtomicReference<byte[]>();
          JMSContext context = cleanup321Context(primary, closing, counts, plain, captured);
          int expected = outcome[primaryKind][closeKind];
          if (expected == 0) new WebLogMessageSender(codec, () -> context).send(row);
          else {
            Throwable actual =
                assertThrows(
                    Throwable.class, () -> new WebLogMessageSender(codec, () -> context).send(row));
            if (expected == 2) {
              assertSame(closing.orElseThrow(), actual);
              if (primaryKind == 0) assertEquals(0, actual.getSuppressed().length);
              else {
                assertEquals(1, actual.getSuppressed().length);
                if (primaryKind == 3)
                  assertSame(
                      primary.orElseThrow(),
                      assertInstanceOf(WebLogSendException.class, actual.getSuppressed()[0])
                          .getCause());
                else assertSame(primary.orElseThrow(), actual.getSuppressed()[0]);
              }
            } else if (expected == 3) {
              assertSame(primary.orElseThrow(), actual);
              assertArrayEquals(
                  closing.map(value -> new Throwable[] {value}).orElseGet(() -> new Throwable[0]),
                  actual.getSuppressed());
            } else {
              WebLogSendException typed = assertInstanceOf(WebLogSendException.class, actual);
              assertSame(
                  primaryKind == 0 ? closing.orElseThrow() : primary.orElseThrow(),
                  typed.getCause());
              Throwable carrier = primaryKind == 3 ? typed : primary.orElse(typed);
              assertArrayEquals(
                  primaryKind == 0
                      ? new Throwable[0]
                      : closing
                          .map(value -> new Throwable[] {value})
                          .orElseGet(() -> new Throwable[0]),
                  carrier.getSuppressed());
            }
            for (Throwable secondary : actual.getSuppressed()) assertNotSame(actual, secondary);
          }
          assertEquals(1, counts[0].get());
          assertEquals(primaryKind == 0 || primaryKind == 3 ? 1 : 0, counts[1].get());
          assertEquals(primaryKind == 0 ? 1 : 0, counts[2].get());
          assertEquals(primaryKind == 3 ? 1 : 0, counts[3].get());
          if (primaryKind == 0 || primaryKind == 3) {
            assertArrayEquals(golden, captured.get());
            assertArrayEquals(new byte[2336], plain.get());
          } else {
            assertNull(captured.get());
            assertNull(plain.get());
          }
        }
      }
    }
  }

  @Test
  void cleanup321003SameThrowableNeverMasksOriginalFailure() {
    try (WebLogPayloadCodec codec = codec()) {
      ClaimedWebLog row = row(codec.encrypt(IDENTITY, WebLogPayloadCodecTest.goldenWire()));
      for (Throwable primary :
          new Throwable[] {
            new AssertionError("independent same fatal"),
            new IllegalStateException("independent same runtime")
          }) {
        var counts = cleanup321Counters();
        var plain = new AtomicReference<byte[]>();
        var captured = new AtomicReference<byte[]>();
        JMSContext context =
            cleanup321Context(Optional.of(primary), Optional.of(primary), counts, plain, captured);
        Throwable actual =
            assertThrows(
                Throwable.class, () -> new WebLogMessageSender(codec, () -> context).send(row));
        if (primary instanceof Error) assertSame(primary, actual);
        else assertSame(primary, assertInstanceOf(WebLogSendException.class, actual).getCause());
        assertEquals(0, primary.getSuppressed().length);
        assertEquals(1, counts[0].get());
        assertEquals(0, counts[1].get());
        assertEquals(0, counts[2].get());
        assertEquals(0, counts[3].get());
        assertNull(captured.get());
        assertNull(plain.get());
      }
    }
  }

  private static AtomicInteger[] cleanup321Counters() {
    return new AtomicInteger[] {
      new AtomicInteger(), new AtomicInteger(), new AtomicInteger(), new AtomicInteger()
    };
  }

  private static JMSContext cleanup321Context(
      Optional<Throwable> primary,
      Optional<Throwable> closing,
      AtomicInteger[] counts,
      AtomicReference<byte[]> plain,
      AtomicReference<byte[]> captured) {
    BytesMessage bytes =
        (BytesMessage)
            Proxy.newProxyInstance(
                BytesMessage.class.getClassLoader(),
                new Class<?>[] {BytesMessage.class},
                (proxy, method, arguments) -> {
                  switch (method.getName()) {
                    case "writeBytes":
                      counts[1].incrementAndGet();
                      plain.set((byte[]) arguments[0]);
                      captured.set(((byte[]) arguments[0]).clone());
                      if (primary.orElse(null) instanceof JMSException) throw primary.orElseThrow();
                      return null;
                    case "setJMSCorrelationID", "setStringProperty":
                      return null;
                    default:
                      throw new AssertionError("unexpected synthetic message call");
                  }
                });
    JMSProducer producer =
        (JMSProducer)
            Proxy.newProxyInstance(
                JMSProducer.class.getClassLoader(),
                new Class<?>[] {JMSProducer.class},
                (proxy, method, arguments) -> {
                  if (!java.util.List.of("setDeliveryMode", "setTimeToLive", "send")
                      .contains(method.getName()))
                    throw new AssertionError("unexpected synthetic producer call");
                  return proxy;
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (proxy, method, arguments) -> {
              switch (method.getName()) {
                case "getSessionMode":
                  if (primary.isPresent() && !(primary.orElseThrow() instanceof JMSException))
                    throw primary.orElseThrow();
                  return JMSContext.SESSION_TRANSACTED;
                case "createBytesMessage":
                  return bytes;
                case "createProducer":
                  return producer;
                case "commit":
                  counts[2].incrementAndGet();
                  return null;
                case "rollback":
                  counts[3].incrementAndGet();
                  return null;
                case "close":
                  counts[0].incrementAndGet();
                  if (closing.isPresent()) throw closing.orElseThrow();
                  return null;
                default:
                  throw new AssertionError("unexpected synthetic context call");
              }
            });
  }

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
  void idem012r01SameProviderFailureOnStageAndRollbackKeepsOriginalCauseAndErasesWire() {
    try (WebLogPayloadCodec codec = codec()) {
      ClaimedWebLog row = row(codec.encrypt(IDENTITY, WebLogPayloadCodecTest.goldenWire()));
      JMSRuntimeException primary = new JMSRuntimeException("synthetic-shared-provider-failure");
      AtomicInteger rollbacks = new AtomicInteger();
      AtomicInteger closes = new AtomicInteger();
      AtomicReference<byte[]> plaintext = new AtomicReference<>();
      BytesMessage message =
          (BytesMessage)
              Proxy.newProxyInstance(
                  BytesMessage.class.getClassLoader(),
                  new Class<?>[] {BytesMessage.class},
                  (ignored, method, args) -> {
                    if (method.getName().equals("writeBytes")) {
                      plaintext.set((byte[]) args[0]);
                      throw primary;
                    }
                    return null;
                  });
      JMSContext context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (ignored, method, args) ->
                      switch (method.getName()) {
                        case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                        case "createBytesMessage" -> message;
                        case "rollback" -> {
                          rollbacks.incrementAndGet();
                          throw primary;
                        }
                        case "close" -> {
                          closes.incrementAndGet();
                          yield null;
                        }
                        default -> throw new AssertionError(method.getName());
                      });
      WebLogSendException failure =
          assertThrows(
              WebLogSendException.class,
              () -> new WebLogMessageSender(codec, () -> context).send(row));
      assertEquals("web log JMS send was not confirmed", failure.getMessage());
      assertSame(primary, failure.getCause());
      assertEquals(0, primary.getSuppressed().length);
      assertEquals(1, rollbacks.get());
      assertEquals(1, closes.get());
      assertArrayEquals(new byte[2336], plaintext.get());
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
