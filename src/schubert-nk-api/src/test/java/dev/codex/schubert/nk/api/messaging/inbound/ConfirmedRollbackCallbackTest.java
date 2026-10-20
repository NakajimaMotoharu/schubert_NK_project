package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.*;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** NK-MSG-001/NK-ASY-001; MQ003008010/UI213231/SS312321342354/SSC319/BUG1565/YKT1322. */
final class ConfirmedRollbackCallbackTest {
  private enum Kind {
    SYNC,
    QUESTION,
    WEB_LOG
  }

  private enum Mode {
    NORMAL,
    INVALID,
    RUNTIME,
    ERROR
  }

  @Test
  void rollback319001PreflightWithoutConfirmationStopsEveryConsumer() throws Exception {
    for (Kind kind : Kind.values()) {
      for (int input = 0; input < 4; input++) {
        try (var owner = open(kind)) {
          var state = owner.states().getFirst();
          state.mode =
              switch (input) {
                case 1 -> Mode.INVALID;
                case 2 -> Mode.RUNTIME;
                case 3 -> Mode.ERROR;
                default -> Mode.NORMAL;
              };
          state
              .callback()
              .onMessage(
                  input == 0 ? null : transportFailure(new JMSException("fixture transport")));
          assertFalse(owner.ready().getAsBoolean(), "unconfirmed preflight is not ordinary retry");
          assertEquals(1, owner.fatal().get());
          assertEquals(input == 3 ? 1 : 0, state.rollbacks.get());
          assertEquals(0, state.commits.get());
          assertEquals(0, owner.processed().get());
          int reads = state.modeReads.get();
          state.callback().onMessage(null);
          assertEquals(reads, state.modeReads.get(), "halted callback never re-enters listener");
          assertEquals(1, owner.fatal().get());
        }
      }
    }
  }

  @Test
  void rollback319002PreviousRollbackNeverQualifiesTheNextDelivery() throws Exception {
    for (Kind kind : Kind.values()) {
      try (var owner = open(kind)) {
        var state = owner.states().getFirst();
        state.callback().onMessage(transportFailure(new JMSException("fixture transport")));
        assertEquals(1, state.rollbacks.get());
        assertEquals(0, owner.fatal().get());
        assertTrue(owner.ready().getAsBoolean());
        state.callback().onMessage(null);
        assertEquals(1, state.rollbacks.get(), "preflight catch must not issue an extra rollback");
        assertEquals(1, owner.fatal().get());
        assertFalse(owner.ready().getAsBoolean());
        assertEquals(0, owner.processed().get());
        assertEquals(0, state.commits.get());
      }
    }
  }

  @Test
  void rollback319003UnknownRollbackErrorIsNotIssuedTwice() throws Exception {
    for (Kind kind : Kind.values()) {
      try (var owner = open(kind)) {
        var state = owner.states().getFirst();
        state.rollbackError = true;
        state.callback().onMessage(transportFailure(new JMSException("fixture transport")));
        assertEquals(1, state.rollbacks.get(), "unknown rollback cannot authorize its own retry");
        assertEquals(1, owner.fatal().get());
        assertFalse(owner.ready().getAsBoolean());
        assertEquals(0, state.commits.get());
        assertEquals(0, owner.processed().get());
      }
    }
  }

  private static Owner open(Kind kind) {
    var states = new ArrayList<State>();
    var fatal = new AtomicInteger();
    var processed = new AtomicInteger();
    Supplier<JMSContext> factory =
        () -> {
          var state = new State();
          states.add(state);
          return state.context();
        };
    java.util.function.Consumer<CommittedFatalInboundException> committed =
        ignored -> fail("no protocol/DLQ path for fixture transport/preflight faults");
    return switch (kind) {
      case SYNC -> {
        var runtime =
            SyncRequestConsumers.start(
                factory,
                new SyncRequestListener(
                    ignored -> {
                      processed.incrementAndGet();
                      throw new AssertionError("unexpected processor");
                    },
                    Clock.systemUTC()),
                committed,
                fatal::incrementAndGet);
        assertEquals(4, states.size());
        yield new Owner(runtime::ready, runtime::close, List.copyOf(states), fatal, processed);
      }
      case QUESTION -> {
        var runtime =
            QuestionWorkConsumers.start(
                factory,
                new QuestionWorkListener(
                    ignored -> {
                      processed.incrementAndGet();
                      throw new AssertionError("unexpected processor");
                    },
                    Clock.systemUTC()),
                committed,
                fatal::incrementAndGet);
        assertEquals(1, states.size());
        yield new Owner(runtime::ready, runtime::close, List.copyOf(states), fatal, processed);
      }
      case WEB_LOG -> {
        var runtime =
            WebLogConsumers.start(
                factory,
                new WebLogListener(
                    ignored -> {
                      processed.incrementAndGet();
                      throw new AssertionError("unexpected processor");
                    },
                    Clock.systemUTC()),
                committed,
                fatal::incrementAndGet);
        assertEquals(1, states.size());
        yield new Owner(runtime::ready, runtime::close, List.copyOf(states), fatal, processed);
      }
    };
  }

  private record Owner(
      BooleanSupplier ready,
      Runnable closeAction,
      List<State> states,
      AtomicInteger fatal,
      AtomicInteger processed)
      implements AutoCloseable {
    @Override
    public void close() {
      closeAction.run();
      for (var state : states) assertEquals(1, state.closes.get());
    }
  }

  private static final class State {
    private final AtomicReference<MessageListener> listener = new AtomicReference<>();
    private final AtomicInteger modeReads = new AtomicInteger();
    private final AtomicInteger rollbacks = new AtomicInteger();
    private final AtomicInteger commits = new AtomicInteger();
    private final AtomicInteger closes = new AtomicInteger();
    private Mode mode = Mode.NORMAL;
    private boolean rollbackError;

    MessageListener callback() {
      return Objects.requireNonNull(listener.get(), "registered callback");
    }

    JMSContext context() {
      var consumer =
          (JMSConsumer)
              Proxy.newProxyInstance(
                  JMSConsumer.class.getClassLoader(),
                  new Class<?>[] {JMSConsumer.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("setMessageListener")) {
                      listener.set((MessageListener) Objects.requireNonNull(args)[0]);
                      return null;
                    }
                    throw new AssertionError("unexpected consumer method");
                  });
      return (JMSContext)
          Proxy.newProxyInstance(
              JMSContext.class.getClassLoader(),
              new Class<?>[] {JMSContext.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "getSessionMode" -> {
                      if (modeReads.incrementAndGet() == 1) yield JMSContext.SESSION_TRANSACTED;
                      yield switch (mode) {
                        case NORMAL -> JMSContext.SESSION_TRANSACTED;
                        case INVALID -> JMSContext.AUTO_ACKNOWLEDGE;
                        case RUNTIME -> throw new IllegalStateException("fixture session mode");
                        case ERROR -> throw new AssertionError("fixture session mode");
                      };
                    }
                    case "createConsumer" -> consumer;
                    case "rollback" -> {
                      rollbacks.incrementAndGet();
                      if (rollbackError) throw new AssertionError("fixture unknown rollback");
                      yield null;
                    }
                    case "commit" -> {
                      commits.incrementAndGet();
                      yield null;
                    }
                    case "close" -> {
                      closes.incrementAndGet();
                      yield null;
                    }
                    case "setAutoStart", "start" -> null;
                    default -> throw new AssertionError("unexpected context method");
                  });
    }
  }

  private static Message transportFailure(JMSException failure) {
    return (BytesMessage)
        Proxy.newProxyInstance(
            BytesMessage.class.getClassLoader(),
            new Class<?>[] {BytesMessage.class},
            (proxy, method, args) -> {
              if (method.getDeclaringClass() == Object.class)
                return switch (method.getName()) {
                  case "toString" -> "synthetic delivery";
                  case "hashCode" -> System.identityHashCode(proxy);
                  case "equals" -> proxy == Objects.requireNonNull(args)[0];
                  default -> throw new AssertionError("unexpected Object method");
                };
              throw failure;
            });
  }
}
