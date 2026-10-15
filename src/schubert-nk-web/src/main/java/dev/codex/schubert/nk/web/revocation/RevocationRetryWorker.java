package dev.codex.schubert.nk.web.revocation;

import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.LockSupport;

/**
 * Owned scheduler; DB row backoff is authoritative.
 * AUT004/MON003/UI226242/SS314324342/QA050/SSC171/PG-D364/RERUN008. Borrowed dependencies; never
 * native ready by itself.
 */
public final class RevocationRetryWorker implements AutoCloseable {
  private static final Duration CLOSE_TIMEOUT = Duration.ofSeconds(5);
  private final DispatchAction action;
  private final long intervalNanos;
  private final Duration closeTimeout;
  private final Thread thread;
  private final AtomicBoolean active = new AtomicBoolean(true);
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicLong completed = new AtomicLong();
  private final AtomicLong failed = new AtomicLong();

  private RevocationRetryWorker(DispatchAction action, Duration interval, Duration closeTimeout) {
    this.action = Objects.requireNonNull(action, "revocation dispatch");
    Objects.requireNonNull(interval, "revocation interval");
    Objects.requireNonNull(closeTimeout, "revocation close timeout");
    if (interval.compareTo(Duration.ofMillis(1)) < 0
        || interval.compareTo(Duration.ofMinutes(1)) > 0
        || closeTimeout.compareTo(Duration.ofMillis(1)) < 0
        || closeTimeout.compareTo(CLOSE_TIMEOUT) > 0)
      throw new IllegalArgumentException("revocation worker interval or close timeout is invalid");
    intervalNanos = interval.toNanos();
    this.closeTimeout = closeTimeout;
    thread =
        Thread.ofPlatform()
            .daemon(true)
            .name("nk-web-revocation-retry")
            .uncaughtExceptionHandler((ignoredThread, ignoredFailure) -> terminal.set(true))
            .unstarted(this::run);
  }

  public static RevocationRetryWorker start(
      RevocationRetryCoordinator coordinator, Duration interval) {
    Objects.requireNonNull(coordinator, "revocation coordinator");
    return start(coordinator::dispatchOne, interval, CLOSE_TIMEOUT);
  }

  static RevocationRetryWorker start(
      DispatchAction action, Duration interval, Duration closeTimeout) {
    var worker = new RevocationRetryWorker(action, interval, closeTimeout);
    worker.thread.start();
    return worker;
  }

  private void run() {
    while (active.get()) {
      try {
        action.dispatch();
        completed.incrementAndGet();
      } catch (RuntimeException fixedFailure) {
        RevocationRetryCoordinator.preserveFatal(fixedFailure);
        failed.incrementAndGet();
      }
      if (active.get()) LockSupport.parkNanos(intervalNanos);
    }
  }

  /** Scheduled-work health; a false value is not proof of actual worker termination. */
  public boolean running() {
    return active.get() && !terminal.get();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  public Snapshot snapshot() {
    return new Snapshot(completed.get(), failed.get());
  }

  @Override
  public void close() {
    closeWithin(closeTimeout);
  }

  /** Remaining native budget; a timed-out actual join retains the borrowed dependencies. */
  public void closeWithin(Duration remaining) {
    Objects.requireNonNull(remaining, "revocation close budget");
    if (remaining.isNegative() || remaining.compareTo(Duration.ofSeconds(30)) > 0)
      throw new IllegalArgumentException("invalid revocation close budget");
    active.set(false);
    if (Thread.currentThread() == thread)
      throw new IllegalStateException("revocation worker cannot join its own owner");
    thread.interrupt();
    try {
      if (!thread.join(remaining))
        throw new IllegalStateException("revocation worker did not stop within its deadline");
    } catch (InterruptedException interruption) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("revocation worker stop was interrupted");
    }
  }

  @FunctionalInterface
  interface DispatchAction {
    void dispatch();
  }

  public record Snapshot(long completedCycles, long failedCycles) {
    public Snapshot {
      if (completedCycles < 0 || failedCycles < 0)
        throw new IllegalArgumentException("revocation worker counters are invalid");
    }
  }
}
