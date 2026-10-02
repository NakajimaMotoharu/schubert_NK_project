package dev.codex.schubert.nk.api.bootstrap;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
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

/**
 * Stop notification only; outer main owns acquisition/drain/close. Hook never closes a provider
 * context or calls System.exit. SS312321342/SSC158/PG-D334/PT-OPS-API-READY001..008.
 */
final class ApiProcessLifetime implements AutoCloseable {
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final AtomicBoolean failed = new AtomicBoolean();
  private final CountDownLatch finished = new CountDownLatch(1);
  private final Thread owner = Thread.currentThread();
  private final Thread hook = new Thread(this::shutdown, "api-stop-owner");
  private volatile boolean installed;

  void install() {
    Runtime.getRuntime().addShutdownHook(hook);
    installed = true;
  }

  boolean stopping() {
    return stopping.get();
  }

  void stop() {
    stopping.set(true);
  }

  void fail() {
    failed.set(true);
    stop();
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
    stop();
    // Invoked only after all admitted scopes have returned/unwound, including failed cleanup.
    try {
      if (installed) {
        installed = false;
        try {
          Runtime.getRuntime().removeShutdownHook(hook);
        } catch (IllegalStateException shutdownInProgress) {
          // VM already waits on this exact hook; notification follows this final owner action.
        }
      }
    } finally {
      finished.countDown();
    }
  }
}
