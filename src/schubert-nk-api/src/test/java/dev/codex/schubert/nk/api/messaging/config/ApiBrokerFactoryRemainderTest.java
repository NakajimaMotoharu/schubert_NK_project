package dev.codex.schubert.nk.api.messaging.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.junit.jupiter.api.Test;

/** PT-OPS-API-FACT001: fixed literal profiles, distinct failures, all earlier owners closed. */
class ApiBrokerFactoryRemainderTest {
  private static final String FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0 = "tcp://127.0.0.1:61616";
  private static final String FIXTURE_OPENSYNC_F61C9AD2 = "openSYNC";
  private static final String FIXTURE_OPENWEB_LOG_882BB65F = "openWEB_LOG";
  private static final String FIXTURE_CLOSESYNC_249C91FD = "closeSYNC";

  @Test
  void fact315004NullAtEveryPositionAndCompleteOwnerHaveLiteralReverseCleanup() {
    for (int at = 0; at <= 3; at++) {
      var calls = new ArrayList<String>();
      var factories = new ArrayList<ActiveMQConnectionFactory>();
      var index = new AtomicInteger();
      var reads = new AtomicInteger();
      int failAt = at;
      java.util.function.BiFunction<
              ArtemisConnectionFactoryProvider.ConsumerProfile, String, ActiveMQConnectionFactory>
          provider =
              (profile, endpoint) -> {
                assertEquals(FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0, endpoint);
                calls.add("open" + profile.name());
                if (index.incrementAndGet() == failAt) return null;
                var factory =
                    new ActiveMQConnectionFactory() {
                      @Override
                      public void close() {
                        calls.add("close" + profile.name());
                        super.close();
                      }
                    };
                factories.add(factory);
                return factory;
              };
      try {
        java.util.function.Supplier<char[]> passwords =
            () -> {
              reads.incrementAndGet();
              return new char[] {'P', 'T'};
            };
        if (failAt == 0) {
          var owner =
              ApiBrokerContexts.createOwned(
                  passwords, FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0, provider);
          owner.close();
          owner.close();
          assertEquals(
              List.of(
                  FIXTURE_OPENSYNC_F61C9AD2,
                  FIXTURE_OPENWEB_LOG_882BB65F,
                  "openASYNC",
                  "closeASYNC",
                  "closeWEB_LOG",
                  FIXTURE_CLOSESYNC_249C91FD),
              calls);
        } else {
          assertThrows(
              NullPointerException.class,
              () ->
                  ApiBrokerContexts.createOwned(
                      passwords, FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0, provider));
          assertEquals(
              switch (failAt) {
                case 1 -> List.of(FIXTURE_OPENSYNC_F61C9AD2);
                case 2 ->
                    List.of(
                        FIXTURE_OPENSYNC_F61C9AD2,
                        FIXTURE_OPENWEB_LOG_882BB65F,
                        FIXTURE_CLOSESYNC_249C91FD);
                default ->
                    List.of(
                        FIXTURE_OPENSYNC_F61C9AD2,
                        FIXTURE_OPENWEB_LOG_882BB65F,
                        "openASYNC",
                        "closeWEB_LOG",
                        FIXTURE_CLOSESYNC_249C91FD);
              },
              calls);
        }
        assertEquals(0, reads.get());
      } finally {
        for (var factory : factories) factory.getServerLocator().close();
      }
    }
  }

  @Test
  void everyPartialFactoryFaultClosesEarlierProfilesAndPreservesIdentity() {
    for (int failAt = 1; failAt <= 3; failAt++) {
      for (boolean fatal : List.of(false, true)) {
        for (int closeKind = 0; closeKind < 3; closeKind++) {
          Throwable primary =
              fatal ? new AssertionError("factory") : new IllegalStateException("factory");
          Throwable closing =
              closeKind == 1 ? primary : closeKind == 2 ? new AssertionError("close") : null;
          var calls = new ArrayList<String>();
          var copies = new AtomicInteger();
          int stage = failAt;
          Class<? extends Throwable> expectedType =
              fatal ? AssertionError.class : IllegalStateException.class;
          var actual =
              assertThrows(
                  expectedType,
                  () ->
                      ApiBrokerContexts.createOwned(
                          () -> {
                            copies.incrementAndGet();
                            return new char[] {'P', 'T'};
                          },
                          FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0,
                          (profile, endpoint) -> {
                            assertEquals(FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0, endpoint);
                            calls.add("open" + profile.name());
                            if (calls.stream().filter(x -> x.startsWith("open")).count() == stage)
                              raise(primary);
                            return new ActiveMQConnectionFactory() {
                              @Override
                              public void close() {
                                calls.add("close" + profile.name());
                                super.close();
                                raise(closing);
                              }
                            };
                          }));
          assertSame(primary, actual);
          assertEquals(
              switch (stage) {
                case 1 -> List.of(FIXTURE_OPENSYNC_F61C9AD2);
                case 2 ->
                    List.of(
                        FIXTURE_OPENSYNC_F61C9AD2,
                        FIXTURE_OPENWEB_LOG_882BB65F,
                        FIXTURE_CLOSESYNC_249C91FD);
                default ->
                    List.of(
                        FIXTURE_OPENSYNC_F61C9AD2,
                        FIXTURE_OPENWEB_LOG_882BB65F,
                        "openASYNC",
                        "closeWEB_LOG",
                        FIXTURE_CLOSESYNC_249C91FD);
              },
              calls);
          assertEquals(0, copies.get());
          assertEquals(closeKind == 2 ? stage - 1 : 0, primary.getSuppressed().length);
          for (var suppressed : primary.getSuppressed()) assertSame(closing, suppressed);
        }
      }
    }
  }

  @Test
  void nullInternalPortsRejectBeforeAnyFactoryOrPasswordCopy() {
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ApiBrokerContexts.createOwned(
                null,
                FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0,
                (profile, endpoint) -> {
                  calls.incrementAndGet();
                  throw new AssertionError();
                }));
    assertThrows(
        NullPointerException.class,
        () ->
            ApiBrokerContexts.createOwned(
                () -> {
                  calls.incrementAndGet();
                  return new char[] {'P', 'T'};
                },
                FIXTURE_TCP_127_0_0_1_61616_3EEAA5A0,
                null));
    assertEquals(0, calls.get());
    assertThrows(
        NullPointerException.class,
        () ->
            ApiBrokerContexts.createOwned(
                () -> new char[] {'P', 'T'},
                null,
                (profile, endpoint) -> {
                  calls.incrementAndGet();
                  throw new AssertionError("must not acquire");
                }));
    assertEquals(0, calls.get());
  }

  private static void raise(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    if (failure instanceof Error fatal) throw fatal;
  }
}
