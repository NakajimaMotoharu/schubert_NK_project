package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** SSC314/BUG1548/YKT1307; PT-API-JMS-CLOSE001..006; finite owned proxies, no broker. */
final class ApiConsumerCloseOwnershipTest {
  private static final String FIXTURE_FIXTURE_B086DE7B = "fixture";
  private static final String FIXTURE_UNEXPECTED_TERMINAL_58F0270E = "unexpected terminal";

  @Test
  void close001OnlyUnconfirmedContextIsRetriedAcrossAllThreeConsumers() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      int count = kind == 0 ? 4 : 1;
      for (int bad = 0; bad < count; bad++) {
        for (Throwable marker :
            List.of(
                new IllegalStateException(FIXTURE_FIXTURE_B086DE7B),
                new AssertionError(FIXTURE_FIXTURE_B086DE7B))) {
          var contexts = fixtures(count, bad, marker, false);
          var index = new AtomicInteger();
          var owner = open(kind, () -> contexts.get(index.getAndIncrement()).context);
          assertTrue(ready(owner));
          Class<? extends Throwable> expectedType =
              marker instanceof Error ? Error.class : IllegalStateException.class;
          var failure = assertThrows(expectedType, owner::close);
          if (marker instanceof Error) assertSame(marker, failure);
          else assertSame(marker, failure.getCause());
          assertFalse(ready(owner));
          assertCounts(contexts, bad, 1, 1);
          owner.close();
          assertCounts(contexts, bad, 2, 1);
          owner.close();
          assertCounts(contexts, bad, 2, 1);
        }
      }
    }
  }

  @Test
  void close002ConcurrentConsumerCloseNeverDuplicatesConfirmedWork() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      var contexts = fixtures(kind == 0 ? 4 : 1, 0, null, true);
      var index = new AtomicInteger();
      var owner = open(kind, () -> contexts.get(index.getAndIncrement()).context);
      concurrent(owner, contexts.getFirst());
      assertCounts(contexts, 0, 1, 1);
      assertFalse(ready(owner));
      owner.close();
      assertCounts(contexts, 0, 1, 1);
    }
  }

  @Test
  void close003StoppedConsumersDoNotInspectOrProcessAnotherDelivery() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      var contexts =
          fixtures(
              kind == 0 ? 4 : 1, 0, new IllegalStateException(FIXTURE_FIXTURE_B086DE7B), false);
      var index = new AtomicInteger();
      var owner = open(kind, () -> contexts.get(index.getAndIncrement()).context);
      assertThrows(IllegalStateException.class, owner::close);
      var touched = new AtomicInteger();
      var message =
          (Message)
              Proxy.newProxyInstance(
                  Message.class.getClassLoader(),
                  new Class<?>[] {Message.class},
                  (ignored, method, arguments) -> {
                    touched.incrementAndGet();
                    throw new AssertionError("delivery after stop");
                  });
      for (var fixture : contexts) fixture.listener.get().onMessage(message);
      assertEquals(0, touched.get());
      owner.close();
    }
  }

  @Test
  void close004ParentRetainsOnlyUnknownChildAcrossReverseGroupClose() throws Exception {
    for (int bad = 0; bad < 6; bad++) {
      for (Throwable marker :
          List.of(
              new IllegalStateException(FIXTURE_FIXTURE_B086DE7B),
              new AssertionError(FIXTURE_FIXTURE_B086DE7B))) {
        var contexts = fixtures(6, bad, marker, false);
        var order = new ArrayList<Integer>();
        for (int i = 0; i < 6; i++) {
          contexts.get(i).order = order;
          contexts.get(i).ordinal = i;
        }
        var runtime = parent(contexts);
        assertTrue(runtime.ready());
        Class<? extends Throwable> expectedType =
            marker instanceof Error ? Error.class : IllegalStateException.class;
        var failure = assertThrows(expectedType, runtime::close);
        if (marker instanceof Error) assertSame(marker, failure);
        assertEquals(List.of(5, 4, 0, 1, 2, 3), order);
        assertFalse(runtime.ready());
        runtime.close();
        assertCounts(contexts, bad, 2, 1);
        assertEquals(bad, order.getLast());
        runtime.close();
        assertCounts(contexts, bad, 2, 1);
        assertEquals(7, order.size());
      }
    }
  }

  @Test
  void close005ConcurrentParentRetainsSingleCloseSequence() throws Exception {
    var contexts = fixtures(6, 5, null, true);
    var runtime = parent(contexts);
    concurrent(runtime, contexts.getLast());
    assertCounts(contexts, 0, 1, 1);
    assertFalse(runtime.ready());
  }

  @Test
  void close006PersistentUnknownNeverBecomesSuccessfulNoOp() {
    var marker = new AssertionError("fixture persistent");
    var contexts = fixtures(6, 0, marker, false);
    contexts.getFirst().persistent = true;
    var runtime = parent(contexts);
    assertSame(marker, assertThrows(AssertionError.class, runtime::close));
    assertSame(marker, assertThrows(AssertionError.class, runtime::close));
    assertCounts(contexts, 0, 2, 1);
    assertFalse(runtime.ready());
    contexts.getFirst().persistent = false;
    runtime.close();
    assertCounts(contexts, 0, 3, 1);
  }

  private static ApiMessagingRuntime parent(List<Context> contexts) {
    var index = new AtomicInteger();
    Supplier<JMSContext> factory = () -> contexts.get(index.getAndIncrement()).context;
    return ApiMessagingRuntime.start(
        factory,
        factory,
        factory,
        ignored -> new byte[0],
        ignored -> {},
        ignored -> {},
        Clock.systemUTC(),
        ignored -> fail(FIXTURE_UNEXPECTED_TERMINAL_58F0270E),
        () -> fail("unexpected fatal"));
  }

  private static AutoCloseable open(int kind, Supplier<JMSContext> factory) {
    return switch (kind) {
      case 0 ->
          SyncRequestConsumers.start(
              factory,
              new SyncRequestListener(
                  ignored -> {
                    throw new AssertionError("unexpected processor");
                  },
                  Clock.systemUTC()),
              ignored -> fail(FIXTURE_UNEXPECTED_TERMINAL_58F0270E));
      case 1 ->
          WebLogConsumers.start(
              factory,
              new WebLogListener(ignored -> fail("unexpected processor"), Clock.systemUTC()),
              ignored -> fail(FIXTURE_UNEXPECTED_TERMINAL_58F0270E));
      case 2 ->
          QuestionWorkConsumers.start(
              factory,
              new QuestionWorkListener(ignored -> fail("unexpected processor"), Clock.systemUTC()),
              ignored -> fail(FIXTURE_UNEXPECTED_TERMINAL_58F0270E),
              () -> fail("unexpected fatal"));
      default -> throw new AssertionError("fixture kind");
    };
  }

  private static boolean ready(AutoCloseable owner) {
    if (owner instanceof SyncRequestConsumers sync) return sync.ready();
    if (owner instanceof WebLogConsumers log) return log.ready();
    if (owner instanceof QuestionWorkConsumers question) return question.ready();
    return ((ApiMessagingRuntime) owner).ready();
  }

  private static List<Context> fixtures(int count, int bad, Throwable failure, boolean hold) {
    var result = new ArrayList<Context>();
    for (int i = 0; i < count; i++)
      result.add(
          new Context(
              i == bad ? Optional.ofNullable(failure) : Optional.empty(), hold && i == bad));
    return result;
  }

  private static void assertCounts(List<Context> contexts, int bad, int retried, int confirmed) {
    for (int i = 0; i < contexts.size(); i++)
      assertEquals(i == bad ? retried : confirmed, contexts.get(i).closes.get(), "child " + i);
  }

  private static void concurrent(AutoCloseable owner, Context gate) throws Exception {
    var firstFailure = new AtomicReference<Throwable>();
    var secondFailure = new AtomicReference<Throwable>();
    var first = new Thread(() -> observedClose(owner, firstFailure));
    var second = new Thread(() -> observedClose(owner, secondFailure));
    first.start();
    try {
      assertTrue(gate.entered.await(5, TimeUnit.SECONDS));
      assertFalse(ready(owner));
      second.start();
      // SS314 requires blocked serialization, not one specific private lock implementation.
      await(
          () ->
              second.getState() == Thread.State.WAITING
                  || second.getState() == Thread.State.BLOCKED);
      assertEquals(1, gate.closes.get());
    } finally {
      gate.release.countDown();
      try {
        first.join(5000);
      } finally {
        second.join(5000);
      }
    }
    assertFalse(first.isAlive());
    assertFalse(second.isAlive());
    assertNull(firstFailure.get());
    assertNull(secondFailure.get());
  }

  private static void observedClose(AutoCloseable owner, AtomicReference<Throwable> failure) {
    try {
      owner.close();
    } catch (Throwable outcome) {
      failure.set(outcome);
    }
  }

  private static void await(BooleanSupplier condition) throws InterruptedException {
    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
    while (!condition.getAsBoolean() && System.nanoTime() - deadline < 0) Thread.sleep(1);
    assertTrue(condition.getAsBoolean());
  }

  private static final class Context {
    final AtomicInteger closes = new AtomicInteger();
    final AtomicReference<MessageListener> listener = new AtomicReference<>();
    final CountDownLatch entered = new CountDownLatch(1);
    final CountDownLatch release;
    final Optional<Throwable> failure;
    final JMSContext context;
    boolean persistent;
    List<Integer> order = new ArrayList<>();
    int ordinal;

    Context(Optional<Throwable> failure, boolean hold) {
      this.failure = failure;
      release = new CountDownLatch(hold ? 1 : 0);
      var consumer =
          (JMSConsumer)
              Proxy.newProxyInstance(
                  JMSConsumer.class.getClassLoader(),
                  new Class<?>[] {JMSConsumer.class},
                  (ignored, method, arguments) -> {
                    if (method.getName().equals("setMessageListener")) {
                      listener.set((MessageListener) arguments[0]);
                      return null;
                    }
                    throw new AssertionError(method.getName());
                  });
      context =
          (JMSContext)
              Proxy.newProxyInstance(
                  JMSContext.class.getClassLoader(),
                  new Class<?>[] {JMSContext.class},
                  (ignored, method, arguments) ->
                      switch (method.getName()) {
                        case "setAutoStart", "start" -> null;
                        case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                        case "createConsumer" -> consumer;
                        case "close" -> {
                          int attempt = closes.incrementAndGet();
                          order.add(ordinal);
                          entered.countDown();
                          if (!release.await(5, TimeUnit.SECONDS))
                            throw new AssertionError("fixture gate expired");
                          if (failure.isPresent() && (attempt == 1 || persistent))
                            throw failure.orElseThrow();
                          yield null;
                        }
                        default -> throw new AssertionError(method.getName());
                      });
    }
  }
}
