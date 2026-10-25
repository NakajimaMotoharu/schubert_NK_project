package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.jms.Connection;
import jakarta.jms.ConnectionFactory;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.lang.reflect.Proxy;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.apache.activemq.artemis.core.remoting.impl.netty.NettyConnectorFactory;
import org.junit.jupiter.api.Test;

/** PT-JMS-WEB-001/002; public synthetic password only. */
final class WebBrokerContextsTest {
  @Test
  void endpointAndProviderSettingsMatchIndependentSs321Literals() {
    for (int port : new int[] {1, 61616, 65535}) {
      try (var factory = WebBrokerContexts.newFactory("tcp://127.0.0.1:" + port)) {
        assertFalse(factory.isHA());
        assertEquals(2_000L, factory.getCallTimeout());
        assertEquals(10_000L, factory.getClientFailureCheckPeriod());
        assertEquals(30_000L, factory.getConnectionTTL());
        assertEquals(3, factory.getInitialConnectAttempts());
        assertEquals(-1, factory.getReconnectAttempts());
        assertEquals(1_000L, factory.getRetryInterval());
        assertEquals(2.0, factory.getRetryIntervalMultiplier());
        assertEquals(30_000L, factory.getMaxRetryInterval());
        assertEquals(1_048_576, factory.getConsumerWindowSize());
        assertTrue(factory.isBlockOnDurableSend());
        assertFalse(factory.isPreAcknowledge());
        assertFalse(factory.isUseTopologyForLoadBalancing());
        assertNull(factory.getUser());
        assertNull(factory.getPassword());
        var connectors = factory.getStaticConnectors();
        assertEquals(1, connectors.length);
        assertEquals(NettyConnectorFactory.class.getName(), connectors[0].getFactoryClassName());
        assertEquals("schubert-nk-core", connectors[0].getName());
        assertEquals(
            Map.of("host", "127.0.0.1", "port", port, "connect-timeout-millis", 3_000),
            connectors[0].getParams());
      }
    }
    for (String rejected :
        new String[] {
          "tcp://127.0.0.1:0", "tcp://127.0.0.1:65536", "tcp://127.0.0.1:061616",
          "tcp://localhost:61616", "tcp://0.0.0.0:61616", "tcp://127.0.0.1:61616?ha=true",
          "vm://0", ""
        }) {
      assertThrows(IllegalArgumentException.class, () -> WebBrokerContexts.newFactory(rejected));
    }
    assertThrows(NullPointerException.class, () -> WebBrokerContexts.newFactory(null));
    assertThrows(
        NullPointerException.class, () -> WebBrokerContexts.create(null, "tcp://127.0.0.1:61616"));
  }

  @Test
  void everyContextHasFixedWebRoleAndModeAndErasesBorrowedCopy() {
    var first = new char[] {'P', 'T'};
    var second = new char[] {'P', 'T'};
    var reads = new AtomicInteger();
    var fake = new FakeFactory();
    JmsContextFactory escaped;
    try (var owner =
        new WebBrokerContexts(() -> reads.incrementAndGet() == 1 ? first : second, fake, fake)) {
      escaped = owner.contexts();
      assertSame(fake.context, escaped.open());
      assertSame(fake.context, escaped.open());
      assertEquals(2, fake.opens);
      assertTrue(fake.fixedRoleAndMode);
      assertTrue(fake.publicSyntheticSecretOnly);
      assertArrayEquals(new char[] {'\0', '\0'}, first);
      assertArrayEquals(new char[] {'\0', '\0'}, second);
      assertEquals("WebBrokerContexts[REDACTED]", owner.toString());
    }
    assertEquals(1, fake.closes);
    assertEquals(
        "Web broker context unavailable",
        assertThrows(IllegalStateException.class, escaped::open).getMessage());
    assertEquals(2, reads.get());
  }

  @Test
  void nullAndProviderFaultsDoNotExposeSecretAndAlwaysEraseOwnedCopy() {
    var fake = new FakeFactory();
    assertThrows(NullPointerException.class, () -> new WebBrokerContexts(null, fake, fake));
    assertThrows(
        NullPointerException.class,
        () -> new WebBrokerContexts(() -> new char[] {'P'}, null, fake));
    assertThrows(
        NullPointerException.class,
        () -> new WebBrokerContexts(() -> new char[] {'P'}, fake, null));
    for (Supplier<char[]> source :
        java.util.List.<Supplier<char[]>>of(
            () -> null,
            () -> {
              throw new IllegalStateException("PT_PUBLIC_MARKER");
            })) {
      try (var owner = new WebBrokerContexts(source, fake, fake)) {
        var failure = assertThrows(IllegalStateException.class, owner.contexts()::open);
        assertEquals("Web broker context unavailable", failure.getMessage());
        assertNull(failure.getCause());
      }
    }
    var inputs = new char[][] {new char[0], new char[65_537], new char[] {'P'}, new char[] {'P'}};
    for (int index = 0; index < inputs.length; index++) {
      fake.returnNull = index == 2;
      fake.failOpen = index == 3;
      char[] copy = inputs[index];
      try (var owner = new WebBrokerContexts(() -> copy, fake, fake)) {
        var failure = assertThrows(IllegalStateException.class, owner.contexts()::open);
        assertEquals("Web broker context unavailable", failure.getMessage());
        assertNull(failure.getCause());
      }
      for (char value : copy) assertEquals('\0', value);
    }
    assertEquals(2, fake.opens);
  }

  @Test
  void closeIsIdempotentAndPreservesFatalOverOrdinary() {
    var ordinary = new FakeFactory();
    ordinary.closeFault = new IllegalStateException("PT_PUBLIC_MARKER");
    var owner = new WebBrokerContexts(() -> new char[] {'P'}, ordinary, ordinary);
    var failure = assertThrows(IllegalStateException.class, owner::close);
    assertEquals("Web broker factory close failed", failure.getMessage());
    assertNull(failure.getCause());
    assertThrows(IllegalStateException.class, owner::close);
    assertEquals(2, ordinary.closes);
    assertThrows(IllegalStateException.class, () -> owner.contexts().open());
    ordinary.closeFault = null;
    owner.close();
    owner.close();
    assertEquals(3, ordinary.closes);

    var fatal = new FakeFactory();
    var marker = new AssertionError("PT_PUBLIC_FATAL");
    fatal.closeFault = marker;
    var fatalOwner = new WebBrokerContexts(() -> new char[] {'P'}, fatal, fatal);
    assertSame(marker, assertThrows(AssertionError.class, fatalOwner::close));
    assertEquals(1, fatal.closes);
    assertSame(marker, assertThrows(AssertionError.class, fatalOwner::close));
    assertEquals(2, fatal.closes);
    fatal.closeFault = null;
    fatalOwner.close();
    fatalOwner.close();
    assertEquals(3, fatal.closes);
  }

  private static final class FakeFactory implements ConnectionFactory, AutoCloseable {
    private final JMSContext context =
        (JMSContext)
            Proxy.newProxyInstance(
                JMSContext.class.getClassLoader(),
                new Class<?>[] {JMSContext.class},
                (proxy, method, arguments) -> {
                  if (method.getName().equals("close")) return null;
                  throw new AssertionError(method.getName());
                });
    private int opens;
    private int closes;
    private boolean fixedRoleAndMode;
    private boolean publicSyntheticSecretOnly;
    private boolean returnNull;
    private boolean failOpen;
    private Throwable closeFault;

    @Override
    public JMSContext createContext(String user, String password, int sessionMode) {
      opens++;
      fixedRoleAndMode = "nk_web".equals(user) && sessionMode == JMSContext.SESSION_TRANSACTED;
      publicSyntheticSecretOnly = "PT".equals(password);
      if (failOpen) throw new IllegalStateException("PT_PUBLIC_MARKER");
      return returnNull ? null : context;
    }

    @Override
    public Connection createConnection() throws JMSException {
      throw new AssertionError("unexpected connection");
    }

    @Override
    public Connection createConnection(String user, String password) throws JMSException {
      throw new AssertionError("unexpected connection");
    }

    @Override
    public JMSContext createContext() {
      throw new AssertionError("unexpected context");
    }

    @Override
    public JMSContext createContext(String user, String password) {
      throw new AssertionError("unexpected context");
    }

    @Override
    public JMSContext createContext(int sessionMode) {
      throw new AssertionError("unexpected context");
    }

    @Override
    public void close() {
      closes++;
      if (closeFault instanceof RuntimeException ordinary) throw ordinary;
      if (closeFault instanceof Error fatal) throw fatal;
    }
  }
}
