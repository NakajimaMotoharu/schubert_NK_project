package dev.codex.schubert.nk.bootstrap;

import java.util.concurrent.CountDownLatch;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC194 / BUG753: PT-only outer shutdown wait. Never stops/closes providers or calls exit. Default
 * main does not create it. Main must close after owned terminal export (or non-success unwind) and
 * BEFORE requesting exit, or its own shutdown would wait forever on this hook. NK-OPS-001 /
 * SYS004,OPS009,TST004 / UI212251 / SS342343451 / PT-OPS-NHOLD194001..005.
 */
@NullMarked
public final class FixedNativeCoverageStopHold implements AutoCloseable {
  enum Removal {
    REMOVED,
    NOT_OWNED,
    SHUTTING_DOWN
  }

  interface Calls {
    void add(Thread hook);

    @Nullable Removal remove(Thread hook);
  }

  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final Calls calls;
  private final CountDownLatch finished = new CountDownLatch(1);
  private final Thread owner = Thread.currentThread();
  private final Thread hook = new Thread(this::shutdown, "fixed-pt-native-capture-stop");
  private boolean installed;
  private boolean closed;

  FixedNativeCoverageStopHold(@Nullable Calls calls) {
    if (calls == null) throw new IllegalArgumentException("fixed PT stop hold required");
    this.calls = calls;
  }

  public static FixedNativeCoverageStopHold open() {
    var value =
        new FixedNativeCoverageStopHold(
            new Calls() {
              @Override
              public void add(Thread hook) {
                Runtime.getRuntime().addShutdownHook(hook);
              }

              @Override
              public Removal remove(Thread hook) {
                return removeNative(hook);
              }
            });
    value.install();
    return value;
  }

  static Removal removeNative(@Nullable Thread hook) {
    if (hook == null) throw new IllegalArgumentException("fixed PT hook required");
    try {
      return Runtime.getRuntime().removeShutdownHook(hook) ? Removal.REMOVED : Removal.NOT_OWNED;
    } catch (IllegalStateException shutdownInProgress) {
      // Runtime documents this refusal only for shutdown already in progress; the hook
      // need not have started yet. Thread.isAlive is not a shutdown authority.
      return Removal.SHUTTING_DOWN;
    }
  }

  /** Main's exclusive capture owner, not the waiting VM hook, controls this outer release. */
  public void verifyOwner() {
    lock.lock();
    try {
      // closed is checked first: close consumes installed, so an installed-then-closed state
      // must not be represented by an unreachable later condition. Same refusal semantics.
      if (closed || !installed || Thread.currentThread() != owner)
        throw new IllegalStateException("fixed PT stop hold unavailable");
    } finally {
      lock.unlock();
    }
  }

  void install() {
    lock.lock();
    try {
      if (installed || closed) throw new IllegalStateException("fixed PT stop hold unavailable");
      installed = true;
      calls.add(hook); // Consume install attempt before possible unknown native refusal.
    } finally {
      lock.unlock();
    }
  }

  void shutdown() {
    if (Thread.currentThread() == owner) return;
    boolean interrupted = false;
    while (true) {
      try {
        finished.await();
        break;
      } catch (InterruptedException notification) {
        interrupted = true;
      }
    }
    if (interrupted) Thread.currentThread().interrupt();
  }

  @Override
  public void close() {
    lock.lock();
    try {
      if (closed) return;
      closed = true;
      try {
        if (installed) {
          installed = false;
          Removal result = calls.remove(hook);
          if (result == null || result == Removal.NOT_OWNED)
            throw new IllegalStateException("fixed PT stop hold unavailable");
        }
      } finally {
        finished.countDown();
      }
    } finally {
      lock.unlock();
    }
  }
}
