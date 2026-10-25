package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.TransportConfiguration;
import org.apache.activemq.artemis.core.remoting.impl.invm.InVMConnectorFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.junit.jupiter.api.Test;

/** NK-MSG-001/UI231253/SS321342354/SSC315; PT-API-FACT315001..004; BUG1553/YKT1307. */
final class ApiFactoryOwnershipTest {
  private static final List<String> SETTINGS =
      List.of(
          "callTimeout=2000",
          "clientFailureCheckPeriod=10000",
          "connectionTTL=30000",
          "initialConnectAttempts=3",
          "reconnectAttempts=-1",
          "retryInterval=1000",
          "retryIntervalMultiplier=2.0",
          "maxRetryInterval=30000",
          "consumerWindowSize=1048576",
          "blockOnDurableSend=true",
          "preAcknowledge=false",
          "useTopologyForLoadBalancing=false");

  @Test
  void apiFact315001IndependentLiteralsAndAcquisitionBoundaryReturnLiveOwner() {
    var probe = new ProbeFactory();
    try {
      var acquired = new AtomicInteger();
      assertSame(
          probe,
          configure(
              () -> {
                acquired.incrementAndGet();
                return probe;
              }));
      assertEquals(1, acquired.get());
      assertEquals(SETTINGS, probe.settings);
      assertEquals(0, probe.closes);
      assertNull(probe.getUser());
      assertNull(probe.getPassword());
      probe.close();
      assertEquals(1, probe.closes);
    } finally {
      probe.dispose();
    }
    assertThrows(NullPointerException.class, () -> configure(null));
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            configure(
                () -> {
                  calls.incrementAndGet();
                  return null;
                }));
    assertEquals(1, calls.get());
    for (int kind = 0; kind < 4; kind++) {
      Throwable primary = failure(kind);
      assertSame(
          primary,
          assertThrows(
              Throwable.class,
              () ->
                  configure(
                      () -> {
                        raise(primary);
                        throw new AssertionError("must not return from throwing fixture");
                      })));
    }
  }

  @Test
  void apiFact315002EachSetterFailureClosesOnceAndPreservesPrimary() {
    for (int at = 1; at <= 12; at++) {
      for (int kind = 0; kind < 4; kind++) {
        var probe = new ProbeFactory();
        try {
          probe.failAt = at;
          probe.primary = failure(kind);
          assertSame(probe.primary, assertThrows(Throwable.class, () -> configure(() -> probe)));
          assertEquals(SETTINGS.subList(0, at), probe.settings);
          assertEquals(1, probe.closes);
          assertEquals(0, probe.primary.getSuppressed().length);
        } finally {
          probe.dispose();
        }
      }
    }
  }

  @Test
  void apiFact315003IndependentCloseTableAndSameThrowableNeverSelfSuppress() {
    for (int first = 0; first < 4; first++) {
      for (int second = 0; second < 4; second++) {
        var probe = new ProbeFactory();
        try {
          probe.failAt = 5;
          probe.primary = failure(first);
          probe.closeFailure = failure(second);
          Throwable expected = second == 3 && first != 3 ? probe.closeFailure : probe.primary;
          Throwable suppressed = expected == probe.primary ? probe.closeFailure : probe.primary;
          Throwable actual = assertThrows(Throwable.class, () -> configure(() -> probe));
          assertSame(expected, actual);
          assertArrayEquals(new Throwable[] {suppressed}, actual.getSuppressed());
          assertEquals(1, probe.closes);
          assertEquals(SETTINGS.subList(0, 5), probe.settings);
        } finally {
          probe.dispose();
        }
      }
      var same = new ProbeFactory();
      try {
        same.failAt = 5;
        same.primary = same.closeFailure = failure(first);
        assertSame(same.primary, assertThrows(Throwable.class, () -> configure(() -> same)));
        assertEquals(0, same.primary.getSuppressed().length);
        assertEquals(1, same.closes);
      } finally {
        same.dispose();
      }
    }
  }

  @Test
  void apiFact315004AllThreeIndependentWindowVectorsAndNullProfile() {
    var profiles =
        List.of(
            ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC,
            ArtemisConnectionFactoryProvider.ConsumerProfile.ASYNC,
            ArtemisConnectionFactoryProvider.ConsumerProfile.WEB_LOG);
    var windows = List.of(1048576, 0, 65536);
    for (int i = 0; i < 3; i++) {
      var probe = new ProbeFactory();
      try {
        var expected = new ArrayList<>(SETTINGS);
        expected.set(8, "consumerWindowSize=" + windows.get(i));
        assertSame(
            probe, ArtemisConnectionFactoryProvider.configureOwned(profiles.get(i), () -> probe));
        assertEquals(expected, probe.settings);
        assertEquals(0, probe.closes);
      } finally {
        probe.dispose();
      }
    }
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ArtemisConnectionFactoryProvider.configureOwned(
                null,
                () -> {
                  calls.incrementAndGet();
                  throw new AssertionError("must not acquire");
                }));
    assertEquals(0, calls.get());
  }

  private static ActiveMQConnectionFactory configure(
      java.util.function.Supplier<ActiveMQConnectionFactory> acquire) {
    return ArtemisConnectionFactoryProvider.configureOwned(
        ArtemisConnectionFactoryProvider.ConsumerProfile.SYNC, acquire);
  }

  private static Throwable failure(int kind) {
    return switch (kind) {
      case 0 -> new IllegalArgumentException("public argument fixture");
      case 1 -> new IllegalStateException("public state fixture");
      case 2 -> new NullPointerException("public null fixture");
      case 3 -> new AssertionError("public fatal fixture");
      default -> throw new AssertionError("invalid fixture kind");
    };
  }

  private static void raise(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  /** No connection/session is ever opened; the test always releases its own locator. */
  static class ProbeFactory extends ActiveMQConnectionFactory {
    @java.io.Serial private static final long serialVersionUID = 1L;
    final transient List<String> settings = new ArrayList<>();
    boolean ready;
    int failAt;
    int closes;
    Throwable primary;
    Throwable closeFailure;

    public ProbeFactory() {
      super(false, new TransportConfiguration(InVMConnectorFactory.class.getName()));
      ready = true;
    }

    void setting(String name, Object value) {
      if (!ready) return; // A library superclass constructor may call an override before admission.
      settings.add(name + "=" + value);
      if (settings.size() == failAt) raise(primary);
    }

    @Override
    public synchronized void setCallTimeout(long value) {
      setting("callTimeout", value);
      super.setCallTimeout(value);
    }

    @Override
    public synchronized void setClientFailureCheckPeriod(long value) {
      setting("clientFailureCheckPeriod", value);
      super.setClientFailureCheckPeriod(value);
    }

    @Override
    public synchronized void setConnectionTTL(long value) {
      setting("connectionTTL", value);
      super.setConnectionTTL(value);
    }

    @Override
    public synchronized void setInitialConnectAttempts(int value) {
      setting("initialConnectAttempts", value);
      super.setInitialConnectAttempts(value);
    }

    @Override
    public synchronized void setReconnectAttempts(int value) {
      setting("reconnectAttempts", value);
      super.setReconnectAttempts(value);
    }

    @Override
    public synchronized void setRetryInterval(long value) {
      setting("retryInterval", value);
      super.setRetryInterval(value);
    }

    @Override
    public synchronized void setRetryIntervalMultiplier(double value) {
      setting("retryIntervalMultiplier", value);
      super.setRetryIntervalMultiplier(value);
    }

    @Override
    public synchronized void setMaxRetryInterval(long value) {
      setting("maxRetryInterval", value);
      super.setMaxRetryInterval(value);
    }

    @Override
    public synchronized void setConsumerWindowSize(int value) {
      setting("consumerWindowSize", value);
      super.setConsumerWindowSize(value);
    }

    @Override
    public synchronized void setBlockOnDurableSend(boolean value) {
      setting("blockOnDurableSend", value);
      super.setBlockOnDurableSend(value);
    }

    @Override
    public synchronized void setPreAcknowledge(boolean value) {
      setting("preAcknowledge", value);
      super.setPreAcknowledge(value);
    }

    @Override
    public synchronized void setUseTopologyForLoadBalancing(boolean value) {
      setting("useTopologyForLoadBalancing", value);
      super.setUseTopologyForLoadBalancing(value);
    }

    @Override
    public void close() {
      closes++;
      if (closeFailure != null) raise(closeFailure);
      dispose();
    }

    void dispose() {
      ready = false;
      super.close();
    }
  }
}
