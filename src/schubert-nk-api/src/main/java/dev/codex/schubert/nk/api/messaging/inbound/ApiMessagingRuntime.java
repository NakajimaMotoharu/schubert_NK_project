package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.ServiceProcessResources;
import jakarta.jms.JMSContext;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.jspecify.annotations.Nullable;

/**
 * Owns four sync + one WebLog + one Question transacted context in the complete profile. Distinct
 * SS321 factory windows remain required. Close drains all groups before external Outbox/key/root
 * owners close. Legacy two-group entry is path PT only, not full readiness. NK-MSG-001/002/ASY-001;
 * MQ003/006/008/010; UI212213231251; SS312321342; PG-D333/BUG488/YKT362/PT-JMS016/CORE001..006.
 */
public final class ApiMessagingRuntime implements AutoCloseable {
  private static final int MAXIMUM_CONSUMER_GROUPS = 3;
  private final List<InboundConsumerGroup> groups;
  private final AtomicBoolean terminal;
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final Object closeLock = new Object();
  private final boolean[] groupClosed = new boolean[MAXIMUM_CONSUMER_GROUPS];
  private boolean closed;

  private ApiMessagingRuntime(List<InboundConsumerGroup> groups, AtomicBoolean terminal) {
    this.groups = groups;
    this.terminal = terminal;
  }

  /** Compatibility for limited Login/Log path; ordinary main uses complete overload below. */
  public static ApiMessagingRuntime start(
      Supplier<JMSContext> syncFactory,
      Supplier<JMSContext> webLogFactory,
      SyncRequestProcessor syncProcessor,
      InternalEventProcessor webLogProcessor,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal) {
    return startSelected(
        syncFactory,
        webLogFactory,
        syncProcessor,
        webLogProcessor,
        null,
        clock,
        onTerminal,
        () -> {},
        false);
  }

  public static ApiMessagingRuntime start(
      Supplier<JMSContext> syncFactory,
      Supplier<JMSContext> webLogFactory,
      Supplier<JMSContext> asyncFactory,
      SyncRequestProcessor syncProcessor,
      InternalEventProcessor webLogProcessor,
      InternalEventProcessor questionProcessor,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal) {
    return startComplete(
        syncFactory,
        webLogFactory,
        asyncFactory,
        syncProcessor,
        webLogProcessor,
        questionProcessor,
        clock,
        onTerminal,
        onFatal,
        false);
  }

  /** SSC316: native partial cleanup retains its exact outer frame after an unconfirmed close. */
  public static ApiMessagingRuntime startRetainingUnknown(
      Supplier<JMSContext> syncFactory,
      Supplier<JMSContext> webLogFactory,
      Supplier<JMSContext> asyncFactory,
      SyncRequestProcessor syncProcessor,
      InternalEventProcessor webLogProcessor,
      InternalEventProcessor questionProcessor,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal) {
    return startComplete(
        syncFactory,
        webLogFactory,
        asyncFactory,
        syncProcessor,
        webLogProcessor,
        questionProcessor,
        clock,
        onTerminal,
        onFatal,
        true);
  }

  private static ApiMessagingRuntime startComplete(
      Supplier<JMSContext> syncFactory,
      Supplier<JMSContext> webLogFactory,
      Supplier<JMSContext> asyncFactory,
      SyncRequestProcessor syncProcessor,
      InternalEventProcessor webLogProcessor,
      InternalEventProcessor questionProcessor,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal,
      boolean retainUnknown) {
    return startSelected(
        syncFactory,
        webLogFactory,
        syncProcessor,
        webLogProcessor,
        new Async(
            Objects.requireNonNull(asyncFactory, "async factory"),
            Objects.requireNonNull(questionProcessor, "question processor")),
        clock,
        onTerminal,
        onFatal,
        retainUnknown);
  }

  private record Async(Supplier<JMSContext> factory, InternalEventProcessor processor) {}

  private static ApiMessagingRuntime startSelected(
      Supplier<JMSContext> syncFactory,
      Supplier<JMSContext> webLogFactory,
      SyncRequestProcessor syncProcessor,
      InternalEventProcessor webLogProcessor,
      @Nullable Async async,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal,
      Runnable onFatal,
      boolean retainUnknown) {
    Objects.requireNonNull(syncFactory, "sync factory");
    Objects.requireNonNull(webLogFactory, "Web Log factory");
    Objects.requireNonNull(syncProcessor, "syncProcessor");
    Objects.requireNonNull(webLogProcessor, "webLogProcessor");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(onTerminal, "onTerminal");
    Objects.requireNonNull(onFatal, "fatal signal");
    Consumer<Throwable> onUnconfirmed =
        retainUnknown ? ServiceProcessResources.unknownReleasePolicy() : ignored -> {};
    var terminal = new AtomicBoolean();
    Consumer<CommittedFatalInboundException> signal =
        failure -> {
          if (terminal.compareAndSet(false, true)) onTerminal.accept(failure);
        };
    Runnable fatalSignal =
        () -> {
          if (terminal.compareAndSet(false, true)) onFatal.run();
        };
    // BUG1537: no first-add backing-array allocation after a group already owns JMS contexts.
    var groups = new ArrayList<InboundConsumerGroup>(MAXIMUM_CONSUMER_GROUPS);
    var runtime = new ApiMessagingRuntime(groups, terminal);
    try {
      groups.add(
          SyncRequestConsumers.start(
              syncFactory,
              new SyncRequestListener(syncProcessor, clock),
              signal,
              fatalSignal,
              onUnconfirmed));
      groups.add(
          WebLogConsumers.start(
              webLogFactory,
              new WebLogListener(webLogProcessor, clock),
              signal,
              fatalSignal,
              onUnconfirmed));
      if (async != null)
        groups.add(
            QuestionWorkConsumers.start(
                async.factory(),
                new QuestionWorkListener(async.processor(), clock),
                signal,
                fatalSignal,
                onUnconfirmed));
      return runtime;
    } catch (RuntimeException | Error failure) {
      Throwable retained = failure;
      Throwable notificationFailure = null;
      Throwable cleanupFailure = null;
      try {
        fatalSignal.run();
      } catch (RuntimeException | Error notification) {
        notificationFailure = notification;
        if (notification instanceof Error && !(failure instanceof Error)) {
          retained = notification;
          // Error notification and non-Error failure cannot be the same object (PG-D379).
          notification.addSuppressed(failure);
        } else if (notification != failure) failure.addSuppressed(notification);
      }
      try {
        runtime.close();
      } catch (RuntimeException | Error closing) {
        // closeGroups exposes Error directly, otherwise its own fixed wrapper with nonnull
        // first group cause. Preserve the original startup cleanup boundary, not that wrapper.
        var cleanup =
            closing instanceof Error ? closing : Objects.requireNonNull(closing.getCause());
        cleanupFailure = cleanup;
        if (cleanup instanceof Error fatal && !(retained instanceof Error)) throw fatal;
        if (cleanup != retained) retained.addSuppressed(cleanup);
      }
      if (retained instanceof Error fatal) throw fatal;
      // SSC334/FACT334005: all owned groups have been attempted before graph classification.
      TemporaryInfrastructureException.preserveFatal(retained);
      if (notificationFailure != null)
        TemporaryInfrastructureException.preserveFatal(notificationFailure);
      if (cleanupFailure != null) TemporaryInfrastructureException.preserveFatal(cleanupFailure);
      throw new IllegalStateException("API messaging startup failed", retained);
    }
  }

  /** Group liveness only. Outer owner also admits DB/management/storage/all31 and Outbox. */
  public boolean ready() {
    return !stopping.get() && !terminal.get();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  @Override
  public void close() {
    stopping.set(true);
    synchronized (closeLock) {
      if (closed) return;
      // SSC314/BUG2407: stop every admission gate before the first child close can block.
      // Index traversal uses the already prepared owner list without allocating an iterator.
      for (int index = 0; index < groups.size(); index++) groups.get(index).stopDelivery();
      closeGroups(groups, groupClosed);
      closed = true;
    }
  }

  private static void closeGroups(List<InboundConsumerGroup> groups, boolean[] groupClosed) {
    Throwable failure = null;
    for (int index = groups.size() - 1; index >= 0; index--) {
      if (groupClosed[index]) continue;
      try {
        groups.get(index).close();
        groupClosed[index] = true;
      } catch (Exception | Error closing) {
        if (failure == null || closing instanceof Error && !(failure instanceof Error))
          failure = closing;
        else if (closing != failure) failure.addSuppressed(closing);
      }
    }
    if (failure instanceof Error fatal) throw fatal;
    if (failure != null) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new IllegalStateException("API messaging close failed", failure);
    }
  }
}
