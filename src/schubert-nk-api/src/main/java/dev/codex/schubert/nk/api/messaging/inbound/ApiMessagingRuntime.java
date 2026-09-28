package dev.codex.schubert.nk.api.messaging.inbound;

import jakarta.jms.JMSContext;
import java.time.Clock;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * Owns the synchronous-request and Web-log receive groups as one API startup unit. The two
 * factories are distinct so the SS321 consumer-window profiles cannot be silently shared. It is not
 * the full API process: asynchronous events, broker-management readiness, and process exit remain
 * with the outer owner. Trace: NK-MSG-001/002; RD MQ-003/006/008/010; UI 212/231/251; SS 312/321;
 * PG229/PT-JMS-016.
 */
public final class ApiMessagingRuntime implements AutoCloseable {
  private final SyncRequestConsumers sync;
  private final WebLogConsumers webLog;
  private final AtomicBoolean terminal;
  private volatile boolean closed;

  private ApiMessagingRuntime(
      SyncRequestConsumers sync, WebLogConsumers webLog, AtomicBoolean terminal) {
    this.sync = sync;
    this.webLog = webLog;
    this.terminal = terminal;
  }

  /** Opens both transacted groups; a failed second group releases the first. */
  public static ApiMessagingRuntime start(
      Supplier<JMSContext> syncFactory,
      Supplier<JMSContext> webLogFactory,
      SyncRequestProcessor syncProcessor,
      InternalEventProcessor webLogProcessor,
      Clock clock,
      Consumer<CommittedFatalInboundException> onTerminal) {
    Objects.requireNonNull(syncFactory, "sync factory");
    Objects.requireNonNull(webLogFactory, "Web Log factory");
    Objects.requireNonNull(syncProcessor, "syncProcessor");
    Objects.requireNonNull(webLogProcessor, "webLogProcessor");
    Objects.requireNonNull(clock, "clock");
    Objects.requireNonNull(onTerminal, "onTerminal");
    AtomicBoolean terminal = new AtomicBoolean();
    Consumer<CommittedFatalInboundException> signal =
        failure -> {
          if (terminal.compareAndSet(false, true)) {
            onTerminal.accept(failure);
          }
        };
    SyncRequestConsumers sync =
        SyncRequestConsumers.start(
            syncFactory, new SyncRequestListener(syncProcessor, clock), signal);
    try {
      WebLogConsumers webLog =
          WebLogConsumers.start(webLogFactory, new WebLogListener(webLogProcessor, clock), signal);
      return new ApiMessagingRuntime(sync, webLog, terminal);
    } catch (RuntimeException failure) {
      try {
        sync.close();
      } catch (RuntimeException closing) {
        failure.addSuppressed(closing);
      }
      throw new IllegalStateException("API messaging startup failed", failure);
    }
  }

  /** Receive-group readiness only; the process must also check DB and broker configuration. */
  public boolean ready() {
    return !closed && !terminal.get();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  @Override
  public void close() {
    if (closed) {
      return;
    }
    closed = true;
    RuntimeException failure = null;
    try {
      webLog.close();
    } catch (RuntimeException closing) {
      failure = closing;
    }
    try {
      sync.close();
    } catch (RuntimeException closing) {
      if (failure == null) {
        failure = closing;
      } else {
        failure.addSuppressed(closing);
      }
    }
    if (failure != null) {
      throw new IllegalStateException("API messaging close failed", failure);
    }
  }
}
