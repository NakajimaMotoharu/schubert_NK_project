package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import jakarta.jms.JMSContext;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-OPS-API-REM001..003: independent provider identity/order, not native acceptance. */
class ApiConsumerRemainderTest {
  @Test
  void factoryFailureSignalsBeforeClosingAllEarlierOwnersWithFatalPriority() {
    for (boolean primaryFatal : List.of(false, true)) {
      for (int notificationKind = 0; notificationKind < 4; notificationKind++) {
        for (int cleanupKind = 0; cleanupKind < 4; cleanupKind++) {
          Throwable primary =
              primaryFatal ? new AssertionError("primary") : new IllegalStateException("primary");
          Throwable notification =
              switch (notificationKind) {
                case 1 -> primary;
                case 2 -> new IllegalStateException("notification");
                case 3 -> new AssertionError("notification");
                default -> null;
              };
          Throwable cleanup =
              switch (cleanupKind) {
                case 1 -> new IllegalStateException("cleanup");
                case 2 -> new AssertionError("cleanup");
                case 3 -> primary;
                default -> null;
              };
          var calls = new ArrayList<String>();
          var index = new AtomicInteger();
          Supplier<JMSContext> sync = () -> context(index.incrementAndGet(), calls, cleanup);
          Supplier<JMSContext> failed =
              () -> {
                raise(primary);
                throw new AssertionError("unreachable fixture");
              };
          Throwable selected =
              notification instanceof Error && !primaryFatal ? notification : primary;
          Throwable expected =
              cleanup instanceof Error && !(selected instanceof Error) ? cleanup : selected;
          Class<? extends Throwable> expectedType =
              expected instanceof Error ? AssertionError.class : IllegalStateException.class;
          var actual =
              assertThrows(
                  expectedType,
                  () ->
                      ApiMessagingRuntime.start(
                          sync,
                          failed,
                          sync,
                          ignored -> new byte[0],
                          ignored -> {},
                          ignored -> {},
                          Clock.systemUTC(),
                          ignored -> fail("no delivery"),
                          () -> {
                            calls.add("signal");
                            raise(notification);
                          }));
          assertSame(expected, expected instanceof Error ? actual : actual.getCause());
          assertEquals(List.of("signal", "close1", "close2", "close3", "close4"), calls);
          assertEquals(4, index.get());
          if (selected != primary) assertSame(primary, selected.getSuppressed()[0]);
          if (notification != null && notification != primary && selected == primary)
            assertSame(notification, primary.getSuppressed()[0]);
        }
      }
    }
  }

  @Test
  void syncDrainPromotesLaterErrorButAttemptsAllFourContexts() {
    var closes = new AtomicInteger();
    var opened = new AtomicInteger();
    var fatal = new AssertionError("later close fatal");
    var owner =
        SyncRequestConsumers.start(
            () ->
                QuestionWorkConsumersTest.context(
                    "",
                    null,
                    opened.incrementAndGet() == 1
                        ? new IllegalStateException("first close")
                        : fatal,
                    closes),
            new SyncRequestListener(ignored -> new byte[0], Clock.systemUTC()),
            ignored -> {},
            () -> {});
    assertSame(fatal, assertThrows(AssertionError.class, owner::close));
    assertEquals(4, closes.get());
    assertEquals(0, fatal.getSuppressed().length);
    assertSame(fatal, assertThrows(AssertionError.class, owner::close));
    assertFalse(owner.ready());
    assertEquals(8, closes.get());
  }

  @Test
  void completeProfileClosesInReverseGroupOrderAndPreservesDistinctFatalIdentity() {
    for (int kind = 0; kind < 5; kind++) {
      var calls = new ArrayList<String>();
      var index = new AtomicInteger();
      var firstFatal = new AssertionError("first fatal");
      var laterFatal = new AssertionError("later fatal");
      Throwable[] faults = new Throwable[6];
      switch (kind) {
        case 1 -> {
          faults[5] = firstFatal;
          faults[4] = laterFatal;
        }
        case 2 -> {
          faults[5] = new IllegalStateException("question close");
          faults[4] = firstFatal;
        }
        case 3 -> {
          faults[5] = firstFatal;
          faults[0] = firstFatal;
        }
        case 4 -> {
          faults[5] = firstFatal;
          faults[4] = firstFatal;
        }
        default -> {}
      }
      Supplier<JMSContext> factory =
          () -> {
            int n = index.incrementAndGet();
            return context(n, calls, faults[n - 1]);
          };
      var runtime =
          ApiMessagingRuntime.start(
              factory,
              factory,
              factory,
              ignored -> new byte[0],
              ignored -> {},
              ignored -> {},
              Clock.systemUTC(),
              ignored -> fail("no delivery"),
              () -> fail("no fatal signal"));
      assertTrue(runtime.ready());
      assertFalse(runtime.terminalFailureObserved());
      if (kind == 0) runtime.close();
      else assertSame(firstFatal, assertThrows(AssertionError.class, runtime::close));
      assertEquals(List.of("close6", "close5", "close1", "close2", "close3", "close4"), calls);
      assertEquals(kind == 1 ? 1 : 0, firstFatal.getSuppressed().length);
      if (kind == 1) assertSame(laterFatal, firstFatal.getSuppressed()[0]);
      if (kind == 0) {
        runtime.close();
        assertEquals(6, calls.size());
      } else {
        assertSame(firstFatal, assertThrows(AssertionError.class, runtime::close));
        // Successful children never run again; only the two faulting contexts remain unknown.
        assertEquals(8, calls.size());
        assertEquals(
            kind == 3 ? List.of("close6", "close1") : List.of("close6", "close5"),
            calls.subList(6, 8));
      }
      assertFalse(runtime.ready());
    }
  }

  @Test
  void partialConsumerCleanupFatalAndSameIdentityAreNeverNormalSuccess() {
    for (boolean webLog : List.of(false, true)) {
      for (boolean primaryFatal : List.of(false, true)) {
        for (boolean same : List.of(false, true)) {
          Throwable primary =
              primaryFatal ? new AssertionError("startup") : new IllegalStateException("startup");
          Throwable closing = same ? primary : new AssertionError("close");
          var count = new AtomicInteger();
          var stopped = new AtomicInteger();
          Supplier<JMSContext> source =
              () -> {
                var delegate = QuestionWorkConsumersTest.context("start", primary, closing, count);
                return (JMSContext)
                    Proxy.newProxyInstance(
                        JMSContext.class.getClassLoader(),
                        new Class<?>[] {JMSContext.class},
                        (p, m, a) -> {
                          if (m.getName().equals("close")) assertEquals(1, stopped.get());
                          return QuestionWorkConsumersTest.invoke(delegate, m, a);
                        });
              };
          Class<? extends Throwable> expectedType =
              primaryFatal || !same ? AssertionError.class : IllegalStateException.class;
          var actual =
              assertThrows(
                  expectedType,
                  () -> {
                    if (webLog)
                      WebLogConsumers.start(
                          source,
                          new WebLogListener(ignored -> {}, Clock.systemUTC()),
                          ignored -> {},
                          stopped::incrementAndGet);
                    else
                      SyncRequestConsumers.start(
                          source,
                          new SyncRequestListener(ignored -> new byte[0], Clock.systemUTC()),
                          ignored -> {},
                          stopped::incrementAndGet);
                  });
          if (primaryFatal) assertSame(primary, actual);
          else if (!same) assertSame(closing, actual);
          else assertSame(primary, actual.getCause());
          assertEquals(webLog ? 1 : 4, count.get());
          assertEquals(1, stopped.get());
          assertFalse(List.of(primary.getSuppressed()).contains(primary));
        }
      }
    }
  }

  private static JMSContext context(int number, List<String> calls, Throwable close) {
    var delegate = QuestionWorkConsumersTest.context("", null, close, new AtomicInteger());
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (p, m, a) -> {
              if (m.getName().equals("close")) calls.add("close" + number);
              return QuestionWorkConsumersTest.invoke(delegate, m, a);
            });
  }

  private static void raise(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    if (failure instanceof Error fatal) throw fatal;
  }
}
