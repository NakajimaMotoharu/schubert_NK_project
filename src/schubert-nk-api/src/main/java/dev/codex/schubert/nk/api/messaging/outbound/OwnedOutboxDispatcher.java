package dev.codex.schubert.nk.api.messaging.outbound;

import java.sql.SQLException;
import java.util.Objects;

/**
 * One owned dispatch thread; request threads only wake it after closing their DB transaction.
 * Shutdown stops new claims and joins the current separately owned DB/JMS dispatch before callers
 * close pool/factory/keys. No provider exception text is retained or logged. NK-MSG-002/NK-QST-001;
 * ASY001/MQ006..010; UI213241; SS312§7/324§8/342; PT-QST-OUTBOX-001..004.
 */
public final class OwnedOutboxDispatcher implements AutoCloseable {
  private final Object lock = new Object();
  private final OutboxDispatcher dispatcher;
  private final String owner;
  private final Thread worker;
  private boolean stopping;
  private boolean signalled;
  private boolean failed;

  private OwnedOutboxDispatcher(OutboxDispatcher dispatcher, String owner) {
    this.dispatcher = Objects.requireNonNull(dispatcher, "dispatcher");
    this.owner = OutboxEntry.requireLeaseOwner(owner);
    worker = new Thread(this::run, "nk-api-outbox");
    worker.setDaemon(false);
    worker.setUncaughtExceptionHandler(
        (thread, fatal) -> System.err.println("NK_API_OUTBOX_FATAL"));
  }

  public static OwnedOutboxDispatcher start(OutboxDispatcher dispatcher, String owner) {
    var result = new OwnedOutboxDispatcher(dispatcher, owner);
    result.worker.start();
    return result;
  }

  public void wake() {
    synchronized (lock) {
      if (stopping || failed) throw new IllegalStateException("outbox dispatcher unavailable");
      signalled = true;
      lock.notifyAll();
    }
  }

  public boolean healthy() {
    synchronized (lock) {
      return !stopping && !failed;
    }
  }

  private void run() {
    try {
      while (true) {
        synchronized (lock) {
          if (stopping) return;
          // Periodic wake also retries already committed work after process restart/send failure.
          if (!signalled) lock.wait(100);
          if (stopping) return;
          signalled = false;
        }
        try {
          dispatcher.dispatch(owner, 32);
        } catch (SQLException | RuntimeException temporary) {
          // Durable leases/retry rows remain authoritative; a short later cycle retries.
          // No unbounded provider text is exposed and no row is declared SENT by this owner.
        }
      }
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      synchronized (lock) {
        failed = true;
        lock.notifyAll();
      }
    } catch (Error fatal) {
      synchronized (lock) {
        failed = true;
        lock.notifyAll();
      }
      throw fatal;
    }
  }

  @Override
  public void close() {
    if (Thread.currentThread() == worker)
      throw new IllegalStateException("outbox worker cannot join itself");
    synchronized (lock) {
      stopping = true;
      lock.notifyAll();
    }
    boolean interrupted = false;
    while (worker.isAlive()) {
      try {
        worker.join();
      } catch (InterruptedException interruption) {
        interrupted = true;
      }
    }
    if (interrupted) Thread.currentThread().interrupt();
  }
}
