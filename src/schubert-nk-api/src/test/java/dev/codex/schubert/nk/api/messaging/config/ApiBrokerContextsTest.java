package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.*;

import jakarta.jms.Connection;
import jakarta.jms.ConnectionFactory;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.lang.reflect.Proxy;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-JMS-024 A-F: synthetic public credential only; no real password or session is retained. */
final class ApiBrokerContextsTest {
  @Test
  void distinctSyncAndLogFactoriesUseFixedRoleAndEraseEveryCopy() {
    var first = new char[] {'P', 'T'};
    var second = new char[] {'P', 'T'};
    var issued = new AtomicInteger();
    var sync = new FakeFactory();
    var log = new FakeFactory();
    try (var owner =
        new ApiBrokerContexts(
            () -> issued.incrementAndGet() == 1 ? first : second, sync, log, sync, log)) {
      assertSame(sync.context, owner.sync().get());
      assertSame(log.context, owner.webLog().get());
      assertEquals(1, sync.opens);
      assertEquals(1, log.opens);
      assertTrue(sync.fixedRoleAndMode);
      assertTrue(log.fixedRoleAndMode);
      assertTrue(sync.publicSyntheticSecretOnly);
      assertTrue(log.publicSyntheticSecretOnly);
      assertEquals("ApiBrokerContexts[REDACTED]", owner.toString());
      assertArrayEquals(new char[] {'\0', '\0'}, first);
      assertArrayEquals(new char[] {'\0', '\0'}, second);
    }
    assertEquals(1, sync.closes);
    assertEquals(1, log.closes);
  }

  @Test
  void missingDependenciesFailBeforeContextCreation() {
    var sync = new FakeFactory();
    var log = new FakeFactory();
    assertThrows(
        NullPointerException.class, () -> new ApiBrokerContexts(null, sync, log, sync, log));
    assertThrows(
        NullPointerException.class,
        () -> new ApiBrokerContexts(() -> new char[] {'P'}, null, log, sync, log));
    assertThrows(
        NullPointerException.class,
        () -> new ApiBrokerContexts(() -> new char[] {'P'}, sync, null, sync, log));
    assertThrows(
        NullPointerException.class,
        () -> new ApiBrokerContexts(() -> new char[] {'P'}, sync, log, null, log));
    assertThrows(
        NullPointerException.class,
        () -> new ApiBrokerContexts(() -> new char[] {'P'}, sync, log, sync, null));
    assertThrows(
        NullPointerException.class, () -> ApiBrokerContexts.create(null, "tcp://127.0.0.1:61616"));
    assertEquals(0, sync.opens);
    assertEquals(0, log.opens);
  }

  @Test
  void passwordAcquisitionFaultsAreRedacted() {
    var sync = new FakeFactory();
    var log = new FakeFactory();
    for (Supplier<char[]> source :
        java.util.List.<Supplier<char[]>>of(
            () -> null,
            () -> {
              throw new IllegalStateException("PT_PUBLIC_MARKER");
            })) {
      try (var owner = new ApiBrokerContexts(source, sync, log, sync, log)) {
        var failure = assertThrows(IllegalStateException.class, owner.sync()::get);
        assertEquals("API broker context unavailable", failure.getMessage());
        assertNull(failure.getCause());
      }
    }
    assertEquals(0, sync.opens);
    assertEquals(0, log.opens);
  }

  @Test
  void invalidLengthsNullAndProviderFaultEraseOwnedCopies() {
    var sync = new FakeFactory();
    var log = new FakeFactory();
    var inputs = new char[][] {new char[0], new char[65_537], new char[] {'P'}, new char[] {'P'}};
    for (int index = 0; index < inputs.length; index++) {
      sync.returnNull = index == 2;
      sync.failOpen = index == 3;
      char[] copy = inputs[index];
      try (var owner = new ApiBrokerContexts(() -> copy, sync, log, sync, log)) {
        var failure = assertThrows(IllegalStateException.class, owner.sync()::get);
        assertEquals("API broker context unavailable", failure.getMessage());
        assertNull(failure.getCause());
      }
      for (char value : copy) assertEquals('\0', value);
    }
    assertEquals(2, sync.opens);
    assertEquals(0, log.opens);
  }

  @Test
  void closeIsIdempotentAndRejectsEscapedSupplierBeforeSecretAccess() {
    var reads = new AtomicInteger();
    var sync = new FakeFactory();
    var log = new FakeFactory();
    var owner =
        new ApiBrokerContexts(
            () -> {
              reads.incrementAndGet();
              return new char[] {'P'};
            },
            sync,
            log,
            sync,
            log);
    var escaped = owner.sync();
    owner.close();
    owner.close();
    var failure = assertThrows(IllegalStateException.class, escaped::get);
    assertEquals("API broker context unavailable", failure.getMessage());
    assertEquals(0, reads.get());
    assertEquals(1, sync.closes);
    assertEquals(1, log.closes);
  }

  @Test
  void closeTriesBothFactoriesAndPreservesFatalPriority() {
    var ordinarySync = new FakeFactory();
    var ordinaryLog = new FakeFactory();
    ordinarySync.closeFault = new IllegalStateException("PT_PUBLIC_MARKER");
    ordinaryLog.closeFault = new IllegalStateException("PT_PUBLIC_MARKER");
    var owner =
        new ApiBrokerContexts(
            () -> new char[] {'P'}, ordinarySync, ordinaryLog, ordinarySync, ordinaryLog);
    var failure = assertThrows(IllegalStateException.class, owner::close);
    assertEquals("API broker factory close failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(1, ordinarySync.closes);
    assertEquals(1, ordinaryLog.closes);
    owner.close();

    var fatalSync = new FakeFactory();
    var fatalLog = new FakeFactory();
    var fatal = new AssertionError("PT_PUBLIC_FATAL");
    fatalSync.closeFault = fatal;
    fatalLog.closeFault = new IllegalStateException("PT_PUBLIC_MARKER");
    var fatalOwner =
        new ApiBrokerContexts(() -> new char[] {'P'}, fatalSync, fatalLog, fatalSync, fatalLog);
    assertSame(fatal, assertThrows(AssertionError.class, fatalOwner::close));
    assertEquals(1, fatalSync.closes);
    assertEquals(1, fatalLog.closes);

    var onlySyncFault = new FakeFactory();
    var healthyLog = new FakeFactory();
    onlySyncFault.closeFault = new IllegalStateException("PT_PUBLIC_MARKER");
    var syncOwner =
        new ApiBrokerContexts(
            () -> new char[] {'P'}, onlySyncFault, healthyLog, onlySyncFault, healthyLog);
    assertEquals(
        "API broker factory close failed",
        assertThrows(IllegalStateException.class, syncOwner::close).getMessage());
    assertEquals(1, onlySyncFault.closes);
    assertEquals(1, healthyLog.closes);

    var ordinarySyncAfterFatal = new FakeFactory();
    var fatalLogOnly = new FakeFactory();
    var logFatal = new AssertionError("PT_PUBLIC_FATAL");
    ordinarySyncAfterFatal.closeFault = new IllegalStateException("PT_PUBLIC_MARKER");
    fatalLogOnly.closeFault = logFatal;
    var logOwner =
        new ApiBrokerContexts(
            () -> new char[] {'P'},
            ordinarySyncAfterFatal,
            fatalLogOnly,
            ordinarySyncAfterFatal,
            fatalLogOnly);
    assertSame(logFatal, assertThrows(AssertionError.class, logOwner::close));
    assertEquals(1, ordinarySyncAfterFatal.closes);
    assertEquals(1, fatalLogOnly.closes);

    var doubleFatalSync = new FakeFactory();
    var doubleFatalLog = new FakeFactory();
    var firstFatal = new AssertionError("PT_PUBLIC_FIRST_FATAL");
    doubleFatalSync.closeFault = new AssertionError("PT_PUBLIC_SECOND_FATAL");
    doubleFatalLog.closeFault = firstFatal;
    var doubleFatalOwner =
        new ApiBrokerContexts(
            () -> new char[] {'P'},
            doubleFatalSync,
            doubleFatalLog,
            doubleFatalSync,
            doubleFatalLog);
    assertSame(firstFatal, assertThrows(AssertionError.class, doubleFatalOwner::close));
    assertEquals(1, doubleFatalSync.closes);
    assertEquals(1, doubleFatalLog.closes);
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
      fixedRoleAndMode = "nk_api".equals(user) && sessionMode == JMSContext.SESSION_TRANSACTED;
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
