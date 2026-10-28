package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.MessageListener;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.time.Clock;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** CORE004..006 independent ownership faults + actual guarded broker callback Error/no ACK. */
class QuestionWorkConsumersTest {
  private static final String FIXTURE_PRIMARY_B9312202 = "primary";
  private static final String FIXTURE_START_A92AE961 = "start";
  private static final String FIXTURE_CLOSE_97959247 = "close";

  @Test
  void jmsown001AcquisitionFailureAndNullKeepIdentityWithoutFatalNotification() {
    for (Throwable failure :
        new Throwable[] {
          new IllegalArgumentException("public factory argument"),
          new IllegalStateException("public factory state"),
          new NullPointerException("public factory null"),
          new AssertionError("public factory fatal")
        }) {
      var calls = new AtomicInteger();
      var signals = new AtomicInteger();
      assertSame(
          failure,
          assertThrows(
              Throwable.class,
              () ->
                  QuestionWorkConsumers.start(
                      () -> {
                        calls.incrementAndGet();
                        if (failure instanceof RuntimeException runtime) throw runtime;
                        throw (Error) failure;
                      },
                      new QuestionWorkListener(ignored -> {}, Clock.systemUTC()),
                      ignored -> {},
                      signals::incrementAndGet)));
      assertEquals(1, calls.get());
      assertEquals(0, signals.get());
    }
    var calls = new AtomicInteger();
    var signals = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            QuestionWorkConsumers.start(
                () -> {
                  calls.incrementAndGet();
                  return null;
                },
                new QuestionWorkListener(ignored -> {}, Clock.systemUTC()),
                ignored -> {},
                signals::incrementAndGet));
    assertEquals(1, calls.get());
    assertEquals(0, signals.get());
  }

  @Test
  void core008SameCloseThrowableNeverSuppressesItselfOrSkipsLaterContexts() {
    for (Throwable shared :
        List.of(new AssertionError("shared"), new IllegalStateException("shared"))) {
      var closes = new AtomicInteger();
      var owner =
          SyncRequestConsumers.start(
              () -> context("", null, shared, closes),
              new SyncRequestListener(ignored -> new byte[0], Clock.systemUTC()),
              ignored -> {},
              () -> {});
      Class<? extends Throwable> kind =
          shared instanceof Error ? AssertionError.class : IllegalStateException.class;
      var actual = assertThrows(kind, owner::close);
      assertSame(shared, shared instanceof Error ? actual : actual.getCause());
      assertEquals(0, shared.getSuppressed().length);
      assertEquals(4, closes.get());
      assertFalse(owner.ready());
      // SSC314/BUG1554: all four contexts still fail; no successful completion exists.
      var retried = assertThrows(kind, owner::close);
      assertSame(shared, shared instanceof Error ? retried : retried.getCause());
      assertEquals(8, closes.get());
    }
  }

  @Test
  void core007AllPartialOwnersSignalStopBeforeCloseAndPreserveNotificationFaults() {
    for (int group = 0; group < 4; group++) {
      for (int mode = 0; mode < 5; mode++) {
        var stopped = new AtomicBoolean();
        var closes = new AtomicInteger();
        var signals = new AtomicInteger();
        Throwable primary =
            mode == 4
                ? new AssertionError(FIXTURE_PRIMARY_B9312202)
                : new IllegalStateException(FIXTURE_PRIMARY_B9312202);
        Throwable notification =
            switch (mode) {
              case 1 -> primary;
              case 2 -> new IllegalStateException("notification");
              case 3, 4 -> new AssertionError("notification");
              default -> null;
            };
        Supplier<JMSContext> factory =
            () -> {
              var delegate = context(FIXTURE_START_A92AE961, primary, null, closes);
              return (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals(FIXTURE_CLOSE_97959247))
                          assertTrue(stopped.get(), "shared stop precedes provider drain");
                        return invoke(delegate, m, a);
                      });
            };
        Runnable signal =
            () -> {
              stopped.set(true);
              signals.incrementAndGet();
              if (notification instanceof RuntimeException runtime) throw runtime;
              if (notification instanceof Error fatal) throw fatal;
            };
        int selected = group;
        Class<? extends Throwable> expectedType =
            mode >= 3 ? AssertionError.class : IllegalStateException.class;
        var error =
            assertThrows(
                expectedType,
                () -> {
                  switch (selected) {
                    case 0 ->
                        SyncRequestConsumers.start(
                            factory,
                            new SyncRequestListener(ignored -> new byte[0], Clock.systemUTC()),
                            ignored -> {},
                            signal);
                    case 1 ->
                        WebLogConsumers.start(
                            factory,
                            new WebLogListener(ignored -> {}, Clock.systemUTC()),
                            ignored -> {},
                            signal);
                    case 2 ->
                        QuestionWorkConsumers.start(
                            factory,
                            new QuestionWorkListener(ignored -> {}, Clock.systemUTC()),
                            ignored -> {},
                            signal);
                    default ->
                        ApiMessagingRuntime.start(
                            factory,
                            factory,
                            factory,
                            ignored -> new byte[0],
                            ignored -> {},
                            ignored -> {},
                            Clock.systemUTC(),
                            ignored -> {},
                            signal);
                  }
                });
        assertTrue(stopped.get());
        assertEquals(1, signals.get());
        assertEquals(group == 0 || group == 3 ? 4 : 1, closes.get());
        if (mode == 3) assertSame(notification, error);
        if (mode == 4) assertSame(primary, error);
        if (mode < 3) {
          // Runtime's own fixed wrapper adds one level but cannot erase original failure.
          Throwable cause = error;
          while (cause.getCause() != null) cause = cause.getCause();
          assertSame(primary, cause);
          assertEquals(mode == 2 ? 1 : 0, primary.getSuppressed().length);
        }
      }
    }
  }

  @Test
  void core004EveryPartialContextStageClosesAndFatalPriorityIsPreserved() {
    for (String point :
        List.of(
            "setAutoStart",
            "mode",
            "createConsumer",
            "null-consumer",
            "setMessageListener",
            FIXTURE_START_A92AE961)) {
      for (boolean fatal : List.of(false, true)) {
        var closes = new AtomicInteger();
        Throwable failure =
            fatal ? new AssertionError("private") : new IllegalStateException("private");
        Supplier<JMSContext> source = () -> context(point, failure, null, closes);
        Class<? extends Throwable> expected =
            fatal && !point.equals("mode") && !point.equals("null-consumer")
                ? AssertionError.class
                : IllegalStateException.class;
        var actual = assertThrows(expected, () -> start(source));
        if (expected == AssertionError.class) assertSame(failure, actual);
        assertEquals(1, closes.get(), point);
      }
    }
    for (boolean same : List.of(false, true)) {
      Error primary = new AssertionError(FIXTURE_PRIMARY_B9312202);
      Throwable close = same ? primary : new IllegalStateException(FIXTURE_CLOSE_97959247);
      var closes = new AtomicInteger();
      assertSame(
          primary,
          assertThrows(
              AssertionError.class,
              () -> start(() -> context(FIXTURE_START_A92AE961, primary, close, closes))));
      assertEquals(1, closes.get());
      assertEquals(same ? 0 : 1, primary.getSuppressed().length);
    }
    Error close = new AssertionError(FIXTURE_CLOSE_97959247);
    var closes = new AtomicInteger();
    assertSame(
        close,
        assertThrows(
            AssertionError.class,
            () ->
                start(
                    () ->
                        context(
                            FIXTURE_START_A92AE961,
                            new IllegalStateException(FIXTURE_PRIMARY_B9312202),
                            close,
                            closes))));
    assertEquals(1, closes.get());
    for (Throwable closing :
        List.of(
            new IllegalStateException(FIXTURE_CLOSE_97959247),
            new AssertionError(FIXTURE_CLOSE_97959247))) {
      var count = new AtomicInteger();
      var owner = start(() -> context("", null, closing, count));
      assertTrue(owner.ready());
      if (closing instanceof Error error)
        assertSame(error, assertThrows(AssertionError.class, owner::close));
      else
        assertEquals(
            "API Question consumer close failed",
            assertThrows(IllegalStateException.class, owner::close).getMessage());
      Class<? extends Throwable> expectedClose =
          closing instanceof Error ? AssertionError.class : IllegalStateException.class;
      var retried = assertThrows(expectedClose, owner::close);
      if (closing instanceof Error) assertSame(closing, retried);
      else assertSame(closing, retried.getCause());
      assertFalse(owner.ready());
      assertEquals(2, count.get());
    }
  }

  @Test
  void core005ActualErrorRollbackNeverAcknowledgesOrLeaksBusinessContinuation(@TempDir Path root)
      throws Exception {
    for (boolean uncertain : List.of(false, true)) {
      var broker =
          InternalEventListenerTest.start(root.resolve(uncertain ? "uncertain" : "normal"));
      try (var factory = new ActiveMQConnectionFactory("vm://0");
          var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
          var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
          var dlq =
              observer.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
        var calls = new AtomicInteger();
        var commits = new AtomicInteger();
        var rollbacks = new AtomicInteger();
        var callbacks = new CountDownLatch(2);
        var signalled = new CountDownLatch(1);
        var fatals = new AtomicInteger();
        var protocol = new AtomicInteger();
        Supplier<JMSContext> source =
            () -> {
              var real = factory.createContext(JMSContext.SESSION_TRANSACTED);
              return (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals("rollback")) {
                          rollbacks.incrementAndGet();
                          real.rollback();
                          if (uncertain) throw new JMSRuntimeException("private");
                          return null;
                        }
                        if (m.getName().equals("commit")) commits.incrementAndGet();
                        Object value = invoke(real, m, a);
                        if (!m.getName().equals("createConsumer")) return value;
                        return Proxy.newProxyInstance(
                            JMSConsumer.class.getClassLoader(),
                            new Class<?>[] {JMSConsumer.class},
                            (cp, cm, ca) -> {
                              if (cm.getName().equals("setMessageListener")) {
                                MessageListener target = (MessageListener) ca[0];
                                ((JMSConsumer) value)
                                    .setMessageListener(
                                        message -> {
                                          try {
                                            target.onMessage(message);
                                          } finally {
                                            callbacks.countDown();
                                          }
                                        });
                                return null;
                              }
                              return invoke(value, cm, ca);
                            });
                      });
            };
        try (var owner =
            QuestionWorkConsumers.start(
                source,
                new QuestionWorkListener(
                    event -> {
                      calls.incrementAndGet();
                      throw new AssertionError("private-provider");
                    },
                    Clock.systemUTC()),
                ignored -> protocol.incrementAndGet(),
                () -> {
                  fatals.incrementAndGet();
                  signalled.countDown();
                })) {
          InternalEventListenerTest.sendEvent(
              producer,
              BrokerTopology.ASYNC_WORK,
              InternalEventListenerTest.eventWire("QWKREQ01", 64));
          assertTrue(signalled.await(3, TimeUnit.SECONDS));
          assertFalse(owner.ready());
          InternalEventListenerTest.sendEvent(
              producer,
              BrokerTopology.ASYNC_WORK,
              InternalEventListenerTest.eventWire("QWKREQ01", 64));
          assertTrue(callbacks.await(3, TimeUnit.SECONDS));
          assertEquals(1, calls.get());
          assertEquals(1, fatals.get());
          assertEquals(0, protocol.get());
          assertEquals(0, commits.get());
          assertEquals(1, rollbacks.get());
          assertNull(dlq.receiveNoWait());
        }
        assertEquals(
            0,
            broker
                .getActiveMQServer()
                .locateQueue(
                    org.apache.activemq.artemis.api.core.SimpleString.of("nk.async.work.q"))
                .getConsumerCount());
      } finally {
        broker.stop();
      }
    }
  }

  @Test
  void core006NullPortsAndFactoryDoNotGrantReady() {
    var opens = new AtomicInteger();
    Supplier<JMSContext> f =
        () -> {
          opens.incrementAndGet();
          return null;
        };
    var listener = new QuestionWorkListener(ignored -> {}, Clock.systemUTC());
    assertThrows(
        NullPointerException.class,
        () -> QuestionWorkConsumers.start(null, listener, ignored -> {}, () -> {}));
    assertThrows(
        NullPointerException.class,
        () -> QuestionWorkConsumers.start(f, null, ignored -> {}, () -> {}));
    assertThrows(
        NullPointerException.class, () -> QuestionWorkConsumers.start(f, listener, null, () -> {}));
    assertThrows(
        NullPointerException.class,
        () -> QuestionWorkConsumers.start(f, listener, ignored -> {}, null));
    assertEquals(0, opens.get());
    assertThrows(NullPointerException.class, () -> start(f));
    assertEquals(1, opens.get());
  }

  static QuestionWorkConsumers start(Supplier<JMSContext> f) {
    return QuestionWorkConsumers.start(
        f, new QuestionWorkListener(ignored -> {}, Clock.systemUTC()), ignored -> {}, () -> {});
  }

  static JMSContext context(
      String point, Throwable failure, Throwable close, AtomicInteger closes) {
    var consumer =
        (JMSConsumer)
            Proxy.newProxyInstance(
                JMSConsumer.class.getClassLoader(),
                new Class<?>[] {JMSConsumer.class},
                (p, m, a) -> {
                  if (point.equals(m.getName())) throw failure;
                  return null;
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (p, m, a) -> {
              if (m.getName().equals(FIXTURE_CLOSE_97959247)) {
                closes.incrementAndGet();
                if (close != null) throw close;
                return null;
              }
              if (point.equals(m.getName())) throw failure;
              return switch (m.getName()) {
                case "getSessionMode" -> point.equals("mode") ? 1 : JMSContext.SESSION_TRANSACTED;
                case "createConsumer" -> point.equals("null-consumer") ? null : consumer;
                case "setAutoStart", FIXTURE_START_A92AE961 -> null;
                default -> throw new AssertionError(m.getName());
              };
            });
  }

  static Object invoke(Object target, Method method, Object[] arguments) throws Throwable {
    try {
      return method.invoke(target, arguments);
    } catch (InvocationTargetException ex) {
      throw ex.getCause();
    }
  }
}
