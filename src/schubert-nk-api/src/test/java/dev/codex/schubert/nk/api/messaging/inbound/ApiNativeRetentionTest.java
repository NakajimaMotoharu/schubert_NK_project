package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.OwnedRetentionProcess;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.util.Collections;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-NHOLD316002: explicit native policy, self-owned proxy/child, never admitted main. */
final class ApiNativeRetentionTest {
  @Test
  void hold316003CompleteNativeComponentClosesSixKnownChildrenNormally() throws Exception {
    var closes = new AtomicInteger();
    Supplier<JMSContext> factory = () -> context(false, null, closes, false);
    var runtime = parent(factory);
    assertTrue(runtime.ready());
    runtime.close();
    runtime.close();
    assertEquals(6, closes.get());
    assertFalse(runtime.ready());
  }

  @Test
  void hold316004FiniteObserverCannotTurnFailedCloseIntoCompletion() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      var closes = new AtomicInteger();
      var seen = new AtomicReference<Throwable>();
      var marker = new IllegalStateException("fixture close");
      var owner = component(kind, () -> context(false, marker, closes, false), seen::set);
      var actual = assertThrows(IllegalStateException.class, owner::close);
      assertSame(marker, seen.get());
      assertSame(marker, actual.getCause());
      assertThrows(IllegalStateException.class, owner::close);
      assertEquals(kind == 0 ? 8 : 2, closes.get());
      var opens = new AtomicInteger();
      int selected = kind;
      assertThrows(
          NullPointerException.class,
          () ->
              component(
                  selected,
                  () -> {
                    opens.incrementAndGet();
                    throw new AssertionError("must not acquire");
                  },
                  null));
      assertEquals(0, opens.get());
    }
  }

  @Test
  void hold316005LiveAndPartialNativeConsumerOwnersKeepOuterFrame() throws Exception {
    for (int kind = 0; kind < 4; kind++)
      for (boolean partial : new boolean[] {false, true})
        OwnedRetentionProcess.assertHeld(
            Driver.class,
            Collections.nCopies(kind == 0 && !partial ? 4 : 1, "CLOSE"),
            Integer.toString(kind),
            Boolean.toString(partial));
  }

  private static ApiMessagingRuntime parent(Supplier<JMSContext> factory) {
    return ApiMessagingRuntime.startRetainingUnknown(
        factory,
        factory,
        factory,
        ignored -> new byte[0],
        ignored -> {},
        ignored -> {},
        Clock.systemUTC(),
        ignored -> {},
        () -> {});
  }

  private static AutoCloseable component(
      int kind, Supplier<JMSContext> factory, Consumer<Throwable> policy) {
    return switch (kind) {
      case 0 ->
          SyncRequestConsumers.start(
              factory,
              new SyncRequestListener(ignored -> new byte[0], Clock.systemUTC()),
              ignored -> {},
              () -> {},
              policy);
      case 1 ->
          WebLogConsumers.start(
              factory,
              new WebLogListener(ignored -> {}, Clock.systemUTC()),
              ignored -> {},
              () -> {},
              policy);
      case 2 ->
          QuestionWorkConsumers.start(
              factory,
              new QuestionWorkListener(ignored -> {}, Clock.systemUTC()),
              ignored -> {},
              () -> {},
              policy);
      default -> throw new AssertionError("fixture kind");
    };
  }

  private static JMSContext context(
      boolean partial, Throwable closing, AtomicInteger closes, boolean emit) {
    var consumer =
        (JMSConsumer)
            Proxy.newProxyInstance(
                JMSConsumer.class.getClassLoader(),
                new Class<?>[] {JMSConsumer.class},
                (ignored, method, args) -> {
                  if (method.getName().equals("setMessageListener")) return null;
                  throw new AssertionError(method.getName());
                });
    return (JMSContext)
        Proxy.newProxyInstance(
            JMSContext.class.getClassLoader(),
            new Class<?>[] {JMSContext.class},
            (ignored, method, args) ->
                switch (method.getName()) {
                  case "setAutoStart" -> {
                    if (partial) throw new IllegalStateException("fixture startup");
                    yield null;
                  }
                  case "start" -> null;
                  case "getSessionMode" -> JMSContext.SESSION_TRANSACTED;
                  case "createConsumer" -> consumer;
                  case "close" -> {
                    closes.incrementAndGet();
                    if (emit) System.out.println("CLOSE");
                    if (closing != null) throw closing;
                    yield null;
                  }
                  default -> throw new AssertionError(method.getName());
                });
  }

  public static final class Driver {
    public static void main(String[] arguments) throws Exception {
      OwnedRetentionProcess.deadline();
      int kind = Integer.parseInt(arguments[0]);
      boolean partial = Boolean.parseBoolean(arguments[1]);
      var closes = new AtomicInteger();
      var marker = new IllegalStateException("fixture close");
      Supplier<JMSContext> factory = () -> context(partial, marker, closes, true);
      try {
        var owner =
            kind == 3
                ? parent(factory)
                : component(kind, factory, ServiceProcessResources::retainUnknownRelease);
        owner.close();
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }
  }
}
