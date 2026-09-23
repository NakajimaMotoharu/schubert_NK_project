package dev.codex.schubert.nk.web.logging;

import java.sql.SQLException;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.LockSupport;

/**
 * Runs the existing short-DB-transaction Web log dispatcher off every HTTP thread. A transient
 * failure is counted without logging its potentially sensitive cause; the persisted outbox and
 * lease/backoff remain the retry oracle. Trace: NK-MSG-002; RD MON-003/MQ-008; UI242; SS311/324
 * section 9/332; PG226/PT-IDEM-012-W01.
 */
public final class WebLogReplayWorker implements AutoCloseable {
  private static final Duration CLOSE_TIMEOUT = Duration.ofSeconds(5);
  private final DispatchAction action;
  private final long intervalNanos;
  private final long closeTimeoutMillis;
  private final Thread thread;
  private final AtomicBoolean active = new AtomicBoolean(true);
  private final AtomicBoolean terminal = new AtomicBoolean();
  private final AtomicLong completedCycles = new AtomicLong();
  private final AtomicLong failedCycles = new AtomicLong();
  private volatile WebLogDispatcher.Report lastReport = new WebLogDispatcher.Report(0, 0, 0, 0);

  private WebLogReplayWorker(DispatchAction action, Duration interval, Duration closeTimeout) {
    this.action = Objects.requireNonNull(action, "action");
    Objects.requireNonNull(interval, "interval");
    Objects.requireNonNull(closeTimeout, "closeTimeout");
    if (interval.compareTo(Duration.ofMillis(1)) < 0
        || interval.compareTo(Duration.ofMinutes(1)) > 0
        || closeTimeout.compareTo(Duration.ofMillis(1)) < 0
        || closeTimeout.compareTo(CLOSE_TIMEOUT) > 0) {
      throw new IllegalArgumentException("web log worker interval or close timeout is invalid");
    }
    this.intervalNanos = interval.toNanos();
    this.closeTimeoutMillis = closeTimeout.toMillis();
    this.thread =
        Thread.ofPlatform()
            .daemon(true)
            .name("nk-web-log-replay")
            .uncaughtExceptionHandler((ignoredThread, ignoredFailure) -> terminal.set(true))
            .unstarted(this::run);
  }

  /** Starts one background worker; the caller owns this handle and its dispatcher dependencies. */
  public static WebLogReplayWorker start(
      WebLogDispatcher dispatcher, String worker, int limit, Duration interval) {
    Objects.requireNonNull(dispatcher, "dispatcher");
    ClaimedWebLog.requireWorker(worker);
    if (limit < 1 || limit > 100) {
      throw new IllegalArgumentException("web log worker batch limit is outside 1..100");
    }
    return start(() -> dispatcher.dispatch(worker, limit), interval, CLOSE_TIMEOUT);
  }

  static WebLogReplayWorker start(DispatchAction action, Duration interval, Duration closeTimeout) {
    WebLogReplayWorker runtime = new WebLogReplayWorker(action, interval, closeTimeout);
    runtime.thread.start();
    return runtime;
  }

  private void run() {
    while (active.get()) {
      try {
        lastReport = Objects.requireNonNull(action.dispatch(), "web log report");
        completedCycles.incrementAndGet();
      } catch (SQLException | RuntimeException failure) {
        // Do not emit provider text or payload. A later due/expired lease is replayed next cycle.
        failedCycles.incrementAndGet();
      }
      if (active.get()) {
        LockSupport.parkNanos(intervalNanos);
      }
    }
  }

  /** This is worker liveness, not full Web/API readiness or delivery confirmation. */
  public boolean running() {
    return active.get() && thread.isAlive();
  }

  public boolean terminalFailureObserved() {
    return terminal.get();
  }

  /** Aggregate-only health snapshot; no row IDs, body, credential or exception text. */
  public Snapshot snapshot() {
    return new Snapshot(completedCycles.get(), failedCycles.get(), lastReport);
  }

  @Override
  public void close() {
    if (!active.compareAndSet(true, false)) {
      return;
    }
    thread.interrupt();
    try {
      thread.join(closeTimeoutMillis);
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("web log worker stop was interrupted", failure);
    }
    if (thread.isAlive()) {
      throw new IllegalStateException("web log worker did not stop within its deadline");
    }
  }

  @FunctionalInterface
  interface DispatchAction {
    WebLogDispatcher.Report dispatch() throws SQLException;
  }

  public record Snapshot(long completedCycles, long failedCycles, WebLogDispatcher.Report last) {
    public Snapshot {
      if (completedCycles < 0 || failedCycles < 0) {
        throw new IllegalArgumentException("web log worker counters are invalid");
      }
      Objects.requireNonNull(last, "last");
    }
  }
}
