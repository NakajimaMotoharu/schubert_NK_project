package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.function.LongSupplier;

/**
 * NK-OPS-001/RD171/UI252/SS311332342351/1864/PG-D635: caller-held observation worker. No
 * pool/credential acquisition. Retain before start; a failed stop must retain this exact owner and
 * borrowed-pool frame through the existing UNKNOWN policy, not continue downstream cleanup.
 */
public final class OwnedApiObservationWorker {
  private static final String UNCONFIRMED = "observation worker stop unconfirmed";
  private final Object startLock = new Object();
  private final ApiOutboxObservationPump pump;
  private final Consumer<? super Throwable> onFailure;
  private final LongSupplier nanos;
  private final Consumer<Thread> starter;
  private final Semaphore wake;
  private final Thread worker;
  private final CountDownLatch startReturned = new CountDownLatch(1);
  private final AtomicBoolean starting = new AtomicBoolean();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final AtomicBoolean unconfirmedStop = new AtomicBoolean();
  private boolean attempted;

  /** Resource-free except an unstarted Java Thread; no sampler/factory is executed here. */
  public OwnedApiObservationWorker(
      ApiOutboxObservationPump pump, Consumer<? super Throwable> onFailure, LongSupplier nanos) {
    this(pump, onFailure, nanos, Thread::start, new Semaphore(0));
  }

  /** Own-component doubles only; starter must synchronously start this exact Thread once. */
  OwnedApiObservationWorker(
      ApiOutboxObservationPump pump,
      Consumer<? super Throwable> onFailure,
      LongSupplier nanos,
      Consumer<Thread> starter,
      Semaphore wake) {
    this.pump = Objects.requireNonNull(pump, "observation pump");
    this.onFailure = Objects.requireNonNull(onFailure, "observation failure notification");
    this.nanos = Objects.requireNonNull(nanos, "stop monotonic time");
    this.starter = Objects.requireNonNull(starter, "synchronous worker starter");
    this.wake = Objects.requireNonNull(wake, "private worker signal");
    worker = new Thread(this::run, "nk-api-observation");
    worker.setDaemon(false);
    worker.setUncaughtExceptionHandler(OwnedApiObservationWorker::uncaught);
  }

  private static void uncaught(Thread thread, Throwable failure) {
    System.err.println("NK_API_OBSERVATION_WORKER_FAILED");
  }

  public void start() {
    synchronized (startLock) {
      if (attempted || stopping.get())
        throw new IllegalStateException("observation worker start unavailable");
      attempted = true;
      starting.set(true);
    }
    try {
      starter.accept(worker);
      if (worker.getState() == Thread.State.NEW)
        throw new IllegalStateException("observation worker start unconfirmed");
    } finally {
      starting.set(false);
      startReturned.countDown();
    }
  }

  private void run() {
    try {
      while (!stopping.get()) {
        try {
          pump.sampleIfDue();
        } catch (SQLException temporary) {
          TemporaryInfrastructureException.preserveFatal(temporary);
        }
        if (!stopping.get()) wake.tryAcquire(1, TimeUnit.SECONDS);
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      if (!stopping.get()) {
        try {
          onFailure.accept(interrupted);
        } catch (RuntimeException | Error diagnostic) {
          TemporaryInfrastructureException.attachSecondary(interrupted, diagnostic);
          TemporaryInfrastructureException.preserveFatal(interrupted);
          throw diagnostic;
        }
      }
    } catch (RuntimeException | Error primary) {
      try {
        onFailure.accept(primary);
      } catch (RuntimeException | Error diagnostic) {
        TemporaryInfrastructureException.attachSecondary(primary, diagnostic);
      }
      TemporaryInfrastructureException.preserveFatal(primary);
      throw primary;
    } finally {
      requestStop();
    }
  }

  /** No join or new I/O; repeated requests never accumulate signal permits. */
  public void requestStop() {
    boolean first = stopping.compareAndSet(false, true);
    pump.requestStop();
    if (first) wake.release();
  }

  /** Uses the existing caller remainder, freezes its first value, and never renews a deadline. */
  public void awaitStopped(LongSupplier remainingNanos) throws IOException {
    Objects.requireNonNull(remainingNanos, "original remaining stop budget");
    boolean interrupted = false;
    try {
      requestStop();
      if (Thread.currentThread() == worker || unconfirmedStop.get())
        throw new IOException(UNCONFIRMED);
      if (starting.get() || worker.isAlive()) {
        long firstRemaining = remainingNanos.getAsLong();
        long began = nanos.getAsLong();
        while (starting.get() || worker.isAlive()) {
          long elapsed = nanos.getAsLong() - began;
          long remaining = Math.min(firstRemaining - elapsed, remainingNanos.getAsLong());
          if (elapsed < 0 || remaining <= 0) throw new IOException(UNCONFIRMED);
          try {
            if (starting.get()) {
              startReturned.await(remaining, TimeUnit.NANOSECONDS);
            } else {
              worker.join(Duration.ofNanos(remaining));
            }
          } catch (InterruptedException interruption) {
            interrupted = true;
          }
        }
      }
      if (!pump.isQuiescent()) throw new IOException(UNCONFIRMED);
    } catch (IOException | RuntimeException | Error primary) {
      unconfirmedStop.set(true);
      throw primary;
    } finally {
      if (interrupted) Thread.currentThread().interrupt();
    }
  }
}
