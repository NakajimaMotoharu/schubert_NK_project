package dev.codex.schubert.nk.storage;

import java.io.Closeable;
import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.TimeUnit;

/**
 * BUG2467/YKT2205; SS341/343; owns one existing Test ProcessBuilder child, never descendants.
 * Single calling Test thread only. Source/static alternative; original process PT remains HOLD.
 */
final class OwnedTestProcess implements AutoCloseable {
  private static final long WAIT_NANOS = TimeUnit.SECONDS.toNanos(5);
  // At most six failure records along any cleanup branch; reserve two additional slots.
  private final List<Throwable> cleanupFailures = new ArrayList<>(8);
  private final IOException terminalUnknown =
      new IOException("owned test child terminal state unknown");
  private final Process ownedChild;
  private boolean closeAttempted;
  private boolean interrupted;

  OwnedTestProcess(ProcessBuilder builder) throws IOException {
    // Instance state is ready before the final acquisition; no caller starts an unprepared owner.
    this.ownedChild = Objects.requireNonNull(builder, "owned test builder").start();
  }

  Process process() {
    return ownedChild;
  }

  /**
   * At most one termination attempt, even when inner finally and outer TWR both close this owner.
   * The two wait budgets do not claim a bound on JDK stream close or executor shutdown.
   */
  @Override
  public void close() throws IOException {
    if (closeAttempted) return;
    closeAttempted = true;
    interrupted = Thread.interrupted();
    var failures = cleanupFailures;
    boolean terminated = false;
    try {
      try {
        if (ownedChild.isAlive()) ownedChild.destroy();
      } catch (RuntimeException | Error failure) {
        failures.add(failure);
      }
      try {
        terminated = awaitExit();
      } catch (RuntimeException | Error failure) {
        failures.add(failure);
      }
      if (!terminated) {
        try {
          ownedChild.destroyForcibly();
        } catch (RuntimeException | Error failure) {
          failures.add(failure);
        }
        try {
          terminated = awaitExit();
        } catch (RuntimeException | Error failure) {
          failures.add(failure);
        }
      }
      if (terminated) {
        closeStream(ownedChild.getOutputStream(), failures);
        closeStream(ownedChild.getInputStream(), failures);
        closeStream(ownedChild.getErrorStream(), failures);
      } else {
        failures.add(terminalUnknown);
      }
    } finally {
      if (interrupted) Thread.currentThread().interrupt();
    }
    if (!failures.isEmpty()) {
      Throwable selected = failures.getFirst();
      for (Throwable failure : failures) {
        if (failure instanceof Error) {
          selected = failure;
          break;
        }
      }
      for (Throwable secondary : failures) {
        if (!reaches(selected, secondary) && !reaches(secondary, selected))
          selected.addSuppressed(secondary);
      }
      if (selected instanceof Error fatal) throw fatal;
      if (selected instanceof RuntimeException runtime) throw runtime;
      throw (IOException) selected;
    }
  }

  private boolean awaitExit() {
    long started = System.nanoTime();
    while (true) {
      long remaining = WAIT_NANOS - (System.nanoTime() - started);
      if (remaining <= 0) return !ownedChild.isAlive();
      try {
        if (ownedChild.waitFor(remaining, TimeUnit.NANOSECONDS)) return true;
      } catch (InterruptedException failure) {
        interrupted = true; // Keep the original deadline, restore only after cleanup.
      }
    }
  }

  private static void closeStream(Closeable stream, List<Throwable> failures) {
    try {
      stream.close();
    } catch (IOException | RuntimeException | Error failure) {
      failures.add(failure);
    }
  }

  private static boolean reaches(Throwable root, Throwable target) {
    var pending = new ArrayDeque<Throwable>();
    Set<Throwable> seen = Collections.newSetFromMap(new IdentityHashMap<>());
    pending.add(root);
    while (!pending.isEmpty()) {
      Throwable current = pending.remove();
      if (current == target) return true;
      if (!seen.add(current)) continue;
      Throwable cause = current.getCause();
      if (cause != null) pending.add(cause);
      Collections.addAll(pending, current.getSuppressed());
    }
    return false;
  }
}
