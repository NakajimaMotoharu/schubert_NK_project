package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.CommittedFatalInboundException;
import dev.codex.schubert.nk.api.messaging.inbound.DeliveryMetadata;
import dev.codex.schubert.nk.api.messaging.inbound.InternalEventProcessor;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import java.util.function.LongSupplier;

/**
 * Stop notification only; outer main owns acquisition/drain/close. Hook never closes a provider
 * context or calls System.exit. SS312321342/SSC158/PG-D334/PT-OPS-API-READY001..008.
 */
final class ApiProcessLifetime implements AutoCloseable {
  private final AtomicBoolean failed = new AtomicBoolean();
  private final CountDownLatch finished = new CountDownLatch(1);
  private final Thread owner = Thread.currentThread();
  private final Thread hook = new Thread(this::shutdown, "api-stop-owner");
  private final ApiStopBudget stopBudget;
  private final AtomicBoolean installed = new AtomicBoolean();

  ApiProcessLifetime() {
    this(System::nanoTime);
  }

  // 1872/PG-D638: resource-free clock port; normal production uses only the fixed constructor.
  ApiProcessLifetime(LongSupplier nanos) {
    stopBudget = new ApiStopBudget(nanos);
  }

  void install() {
    Runtime.getRuntime().addShutdownHook(hook);
    installed.set(true);
  }

  boolean stopping() {
    return stopBudget.stopping();
  }

  void stop() {
    stopBudget.begin();
  }

  /** Existing first-notification budget only; no new deadline at a later owner's close. */
  long remainingStopNanos() {
    return stopBudget.remainingNanos();
  }

  void fail() {
    failed.set(true);
    stop();
  }

  /** PG-D412: bind durable-fatal notification to this owner without reading/logging its payload. */
  Consumer<CommittedFatalInboundException> committedFailureHandler() {
    return ignored -> fail();
  }

  SyncRequestProcessor guardSync(SyncRequestProcessor delegate) {
    Objects.requireNonNull(delegate, "sync processor");
    return request -> {
      checkRunning();
      return delegate.process(request);
    };
  }

  InternalEventProcessor guardEvent(InternalEventProcessor delegate) {
    Objects.requireNonNull(delegate, "event processor");
    return new InternalEventProcessor() {
      public void process(WireMessage<FixedPayload> event) {
        checkRunning();
        delegate.process(event);
      }

      public void process(WireMessage<FixedPayload> event, DeliveryMetadata delivery) {
        checkRunning();
        delegate.process(event, delivery);
      }
    };
  }

  private void checkRunning() {
    if (stopping()) throw new TemporaryInfrastructureException();
  }

  void await(BooleanSupplier healthy) throws IOException {
    Objects.requireNonNull(healthy, "runtime health");
    while (!stopping()) {
      if (!healthy.getAsBoolean()) {
        fail();
        break;
      }
      try {
        Thread.sleep(100);
      } catch (InterruptedException interrupted) {
        Thread.currentThread().interrupt();
        fail();
      }
    }
    if (failed.get()) throw new IOException("API runtime unavailable");
  }

  void shutdown() {
    stop();
    if (Thread.currentThread() == owner) return;
    boolean interrupted = false;
    while (true) {
      try {
        finished.await();
        break;
      } catch (InterruptedException interruption) {
        interrupted = true;
      }
    }
    if (interrupted) Thread.currentThread().interrupt();
  }

  @Override
  public void close() {
    // Invoked only after all admitted scopes have returned/unwound, including failed cleanup.
    try {
      stop();
      if (installed.getAndSet(false)) {
        try {
          Runtime.getRuntime().removeShutdownHook(hook);
        } catch (IllegalStateException shutdownInProgress) {
          // VM already waits on this exact hook; notification follows this final owner action.
          return; // Terminal close still passes through the one owner notification in finally.
        }
      }
    } finally {
      finished.countDown();
    }
  }
}
