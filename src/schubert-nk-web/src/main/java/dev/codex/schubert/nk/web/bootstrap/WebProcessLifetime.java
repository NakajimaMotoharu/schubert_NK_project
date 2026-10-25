package dev.codex.schubert.nk.web.bootstrap;

import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Native stop notification only. Hook does not close borrowed providers or call exit; it waits for
 * the one owner and confirmed scope cleanup. UNKNOWN keeps that frame alive. NK-WEB-002/NK-OPS-001;
 * SYS004/AUT002/MON003; UI212243253; SS313342352/PG-D369.
 */
@NullMarked
final class WebProcessLifetime implements AutoCloseable {
  private final Object stateLock = new Object();
  private final AtomicBoolean retainedStopping = new AtomicBoolean();
  private final AtomicBoolean failed = new AtomicBoolean();
  private final CountDownLatch finished = new CountDownLatch(1);
  private final Thread owner = Thread.currentThread();
  private final Thread hook = new Thread(this::shutdown, "web-stop-owner");
  private boolean installed;

  void install() {
    synchronized (stateLock) {
      if (installed) throw new IllegalStateException("Web stop owner already installed");
      Runtime.getRuntime().addShutdownHook(hook);
      installed = true;
    }
  }

  boolean stopping() {
    return retainedStopping.get();
  }

  void stop() {
    retainedStopping.set(true);
  }

  void fail() {
    failed.set(true);
    stop();
  }

  void await(BooleanSupplier healthy) throws IOException {
    Objects.requireNonNull(healthy, "Web runtime health");
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
    if (failed.get()) throw new IOException("Web runtime unavailable");
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

  /** Only called after every admitted owner scope confirmed cleanup. */
  @Override
  public void close() {
    synchronized (stateLock) {
      stop();
      try {
        if (installed) {
          installed = false;
          try {
            Runtime.getRuntime().removeShutdownHook(hook);
          } catch (IllegalStateException shutdownInProgress) {
            /* Exact hook already waiting. */
            return; // The existing finally notifies the held owner before leaving this scope.
          }
        }
      } finally {
        finished.countDown();
      }
    }
  }

  /** Never unwind the native borrowed frame or manufacture a clean-stop marker after UNKNOWN. */
  static void retainUnknown() {
    while (true) holdUnknownInterval();
  }

  /** Observation wakeup only: never confirms, retries, releases or returns an UNKNOWN owner. */
  static void holdUnknownInterval() {
    try {
      Thread.sleep(1000);
    } catch (InterruptedException notification) {
      /* Still unconfirmed; caller retains the exact outer resources and failure frame. */
    }
  }
}
