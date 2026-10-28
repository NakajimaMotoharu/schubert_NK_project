package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import jakarta.jms.BytesMessage;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import jakarta.jms.JMSProducer;
import jakarta.jms.Message;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
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
  private static final String FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90 = "unexpected processor";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-20T00:00:00Z"), ZoneOffset.UTC);

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
      for (boolean error : List.of(false, true)) {
        try (var owner = open(kind)) {
          var state = owner.states().getFirst();
          state.rollbackError = error;
          state.rollbackRuntime = !error;
          state.callback().onMessage(transportFailure(new JMSException("fixture transport")));
          assertEquals(1, state.rollbacks.get(), "unknown rollback cannot authorize its own retry");
          assertEquals(1, owner.fatal().get());
          assertFalse(owner.ready().getAsBoolean());
          assertEquals(0, state.commits.get());
          assertEquals(0, owner.processed().get());
        }
      }
    }
  }

  @Test
  void rollback319004FourContextsConfirmInParallelAndStopRejectsEveryLaterCallback()
      throws Exception {
    try (var owner = open(Kind.SYNC)) {
      var entered = new java.util.concurrent.CountDownLatch(4);
      var release = new java.util.concurrent.CountDownLatch(1);
      var modeEntered = new java.util.concurrent.CountDownLatch(4);
      var modeRelease = new java.util.concurrent.CountDownLatch(1);
      var executor = java.util.concurrent.Executors.newFixedThreadPool(4);
      try {
        var futures = new ArrayList<java.util.concurrent.Future<?>>();
        for (var state : owner.states())
          futures.add(
              executor.submit(
                  () ->
                      state
                          .callback()
                          .onMessage(
                              transportFailure(
                                  new JMSException("fixture parallel transport"),
                                  () -> {
                                    entered.countDown();
                                    try {
                                      assertTrue(
                                          release.await(5, java.util.concurrent.TimeUnit.SECONDS));
                                    } catch (InterruptedException interrupted) {
                                      Thread.currentThread().interrupt();
                                      throw new AssertionError(interrupted);
                                    }
                                  }))));
        assertTrue(entered.await(5, java.util.concurrent.TimeUnit.SECONDS));
        release.countDown();
        for (var future : futures) future.get(5, java.util.concurrent.TimeUnit.SECONDS);
        assertTrue(owner.ready().getAsBoolean());
        assertEquals(0, owner.fatal().get());
        for (var state : owner.states()) {
          assertEquals(1, state.rollbacks.get());
          assertEquals(0, state.commits.get());
        }
        futures.clear();
        for (var state : owner.states()) {
          state.mode = Mode.RUNTIME;
          state.modeFailure =
              () -> {
                modeEntered.countDown();
                try {
                  assertTrue(modeRelease.await(5, java.util.concurrent.TimeUnit.SECONDS));
                } catch (InterruptedException interrupted) {
                  Thread.currentThread().interrupt();
                  throw new AssertionError(interrupted);
                }
              };
          futures.add(
              executor.submit(
                  () ->
                      state
                          .callback()
                          .onMessage(
                              transportFailure(new JMSException("fixture parallel preflight")))));
        }
        assertTrue(modeEntered.await(5, java.util.concurrent.TimeUnit.SECONDS));
        modeRelease.countDown();
        for (var future : futures) future.get(5, java.util.concurrent.TimeUnit.SECONDS);
        assertEquals(1, owner.fatal().get());
        assertFalse(owner.ready().getAsBoolean());
        for (var state : owner.states()) {
          int reads = state.modeReads.get();
          state.callback().onMessage(null);
          assertEquals(reads, state.modeReads.get());
          assertEquals(1, state.rollbacks.get());
        }
      } finally {
        release.countDown();
        modeRelease.countDown();
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void rollback319005PublicIdentityAndInternalPhaseOrderNullAndNotificationFaults()
      throws Exception {
    for (Kind kind : Kind.values()) {
      for (int missing = 0; missing < 2; missing++) {
        var state = new State();
        int selected = missing;
        assertThrows(
            NullPointerException.class,
            () ->
                dispatch(
                    kind,
                    state.context(),
                    transportFailure(new JMSException("fixture")),
                    selected == 0 ? null : () -> {},
                    selected == 1 ? null : () -> {},
                    false));
        assertEquals(0, state.modeReads.get());
        assertEquals(0, state.rollbacks.get());
      }
      var state = new State();
      var primary = new JMSException("fixture primary transport");
      assertSame(
          primary,
          assertThrows(
              JMSException.class,
              () ->
                  dispatch(
                      kind,
                      state.context(),
                      transportFailure(primary),
                      () -> state.order.add("attempted"),
                      () -> state.order.add("confirmed"),
                      false)));
      assertEquals(List.of("attempted", "rollback", "confirmed"), state.order);
      assertEquals(1, state.rollbacks.get());
      var legacy = new State();
      assertSame(
          primary,
          assertThrows(
              JMSException.class,
              () ->
                  dispatch(
                      kind,
                      legacy.context(),
                      transportFailure(primary),
                      () -> fail("public observer must not be selected"),
                      () -> fail("public observer must not be selected"),
                      true)));
      assertEquals(1, legacy.rollbacks.get());
      assertThrows(
          NullPointerException.class,
          () -> dispatch(kind, null, transportFailure(primary), () -> {}, () -> {}, true));
      var empty = new State();
      assertThrows(
          NullPointerException.class,
          () -> dispatch(kind, empty.context(), null, () -> {}, () -> {}, true));
      assertEquals(0, empty.rollbacks.get());
      for (boolean before : List.of(false, true)) {
        var fault = new State();
        var notification = new IllegalStateException("fixture phase observer");
        Runnable throwsNotification =
            () -> {
              throw notification;
            };
        assertSame(
            notification,
            assertThrows(
                IllegalStateException.class,
                () ->
                    dispatch(
                        kind,
                        fault.context(),
                        transportFailure(primary),
                        before ? throwsNotification : () -> {},
                        before ? () -> fail("no confirmed callback") : throwsNotification,
                        false)));
        assertEquals(before ? 0 : 1, fault.rollbacks.get());
        assertEquals(0, fault.commits.get());
      }
    }
  }

  @Test
  void rollback319006LegacyHelpersAndFatalIsolationRollbackRetainPhaseAndError() throws Exception {
    for (int missing = 0; missing < 2; missing++) {
      var rejected = new State();
      int selected = missing;
      assertThrows(
          NullPointerException.class,
          () ->
              InboundTransactions.rollbackAfterFailure(
                  rejected.context(),
                  new IllegalStateException("fixture primary"),
                  selected == 0 ? null : () -> {},
                  selected == 1 ? null : () -> {}));
      assertThrows(
          NullPointerException.class,
          () ->
              InboundTransactions.isolateFatal(
                  rejected.context(),
                  malformedDelivery(),
                  dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REQUEST,
                  dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata.DetectedBy.API_SYNC,
                  CLOCK,
                  new dev.codex.schubert.nk.protocol.codec.PermanentProtocolException(
                      "fixture protocol"),
                  selected == 0 ? null : () -> {},
                  selected == 1 ? null : () -> {}));
      assertEquals(0, rejected.rollbacks.get());
      assertEquals(0, rejected.commits.get());
      assertEquals(0, rejected.modeReads.get());
    }
    var normal = new State();
    InboundTransactions.rollbackAfterFailure(
        normal.context(), new IllegalStateException("fixture primary"));
    assertEquals(1, normal.rollbacks.get());
    var isolation = new State();
    InboundTransactions.isolateFatal(
        isolation.context(),
        malformedDelivery(),
        dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REQUEST,
        dev.codex.schubert.nk.api.messaging.outbound.FatalDlqMetadata.DetectedBy.API_SYNC,
        CLOCK,
        new dev.codex.schubert.nk.protocol.codec.PermanentProtocolException("fixture protocol"));
    assertEquals(1, isolation.sends.get());
    assertEquals(1, isolation.commits.get());
    assertEquals(0, isolation.rollbacks.get());
    for (Kind kind : Kind.values()) {
      try (var owner = open(kind)) {
        var state = owner.states().getFirst();
        state.sendFailure = true;
        state.rollbackError = true;
        state.callback().onMessage(malformedDelivery());
        assertEquals(1, state.sends.get());
        assertEquals(
            1, state.rollbacks.get(), "unknown fatal-isolation rollback must not be reissued");
        assertEquals(0, state.commits.get());
        assertEquals(1, owner.fatal().get());
        assertFalse(owner.ready().getAsBoolean());
      }
    }
  }

  private static void dispatch(
      Kind kind,
      JMSContext context,
      Message message,
      Runnable attempted,
      Runnable confirmed,
      boolean legacy)
      throws JMSException {
    switch (kind) {
      case SYNC -> {
        var listener =
            new SyncRequestListener(
                ignored -> {
                  throw new AssertionError(FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90);
                },
                CLOCK);
        if (legacy) listener.onMessage(context, message);
        else listener.onMessage(context, message, attempted, confirmed);
      }
      case QUESTION -> {
        var listener =
            new QuestionWorkListener(
                ignored -> {
                  throw new AssertionError(FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90);
                },
                CLOCK);
        if (legacy) listener.onMessage(context, message);
        else listener.onMessage(context, message, attempted, confirmed);
      }
      case WEB_LOG -> {
        var listener =
            new WebLogListener(
                ignored -> {
                  throw new AssertionError(FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90);
                },
                CLOCK);
        if (legacy) listener.onMessage(context, message);
        else listener.onMessage(context, message, attempted, confirmed);
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
                      throw new AssertionError(FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90);
                    },
                    CLOCK),
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
                      throw new AssertionError(FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90);
                    },
                    CLOCK),
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
                      throw new AssertionError(FIXTURE_UNEXPECTED_PROCESSOR_F5F5DD90);
                    },
                    CLOCK),
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
    private final AtomicInteger sends = new AtomicInteger();
    private final List<String> order = new ArrayList<>();
    private Mode mode = Mode.NORMAL;
    private boolean rollbackError;
    private boolean rollbackRuntime;
    private boolean sendFailure;
    private Runnable modeFailure = () -> {};

    MessageListener callback() {
      return Objects.requireNonNull(listener.get(), "registered callback");
    }

    JMSContext context() {
      var producer =
          (JMSProducer)
              Proxy.newProxyInstance(
                  JMSProducer.class.getClassLoader(),
                  new Class<?>[] {JMSProducer.class},
                  (proxy, method, args) ->
                      switch (method.getName()) {
                        case "setDeliveryMode", "setTimeToLive" -> proxy;
                        case "send" -> {
                          sends.incrementAndGet();
                          if (sendFailure)
                            throw new IllegalStateException("fixture isolation send");
                          yield proxy;
                        }
                        default -> throw new AssertionError("unexpected producer method");
                      });
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
                        case RUNTIME -> {
                          modeFailure.run();
                          throw new IllegalStateException("fixture session mode");
                        }
                        case ERROR -> throw new AssertionError("fixture session mode");
                      };
                    }
                    case "createConsumer" -> consumer;
                    case "createProducer" -> producer;
                    case "rollback" -> {
                      rollbacks.incrementAndGet();
                      order.add("rollback");
                      if (rollbackRuntime)
                        throw new IllegalStateException("fixture unknown rollback");
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
    return transportFailure(failure, () -> {});
  }

  private static Message transportFailure(JMSException failure, Runnable access) {
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
              access.run();
              throw failure;
            });
  }

  private static Message malformedDelivery() {
    return (Message)
        Proxy.newProxyInstance(
            Message.class.getClassLoader(),
            new Class<?>[] {Message.class},
            (proxy, method, args) ->
                switch (method.getName()) {
                  case "getJMSMessageID", "getStringProperty", "getJMSCorrelationID" -> null;
                  case "propertyExists" -> false;
                  case "clearProperties",
                      "setJMSCorrelationID",
                      "setJMSReplyTo",
                      "setJMSType",
                      "setStringProperty",
                      "setIntProperty" ->
                      null;
                  default ->
                      throw new AssertionError("unexpected malformed fixture message operation");
                });
  }
}
