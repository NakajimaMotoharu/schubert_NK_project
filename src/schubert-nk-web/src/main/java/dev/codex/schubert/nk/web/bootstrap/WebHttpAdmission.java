package dev.codex.schubert.nk.web.bootstrap;

import java.io.IOException;
import java.time.Duration;
import java.util.Objects;
import java.util.function.BooleanSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * One native HTTP ownership/drain gate, not authentication. Existing requests keep their lease
 * through actual Tomcat terminal completion, including ASYNC/media and REQUEST persistence.
 * NK-WEB-002; SYS004/AUT002/MON003; UI212243253; SS313342352; PG-D369; NATIVE-GRAPH/READY/STOP. No
 * thread interrupt is a termination proof.
 */
@NullMarked
public final class WebHttpAdmission {
  private final Object lock = new Object();
  private final BooleanSupplier ownerStopping;
  private boolean accepting;
  private boolean stopping;
  private int active;

  public WebHttpAdmission() {
    this(() -> false);
  }

  WebHttpAdmission(BooleanSupplier ownerStopping) {
    this.ownerStopping = Objects.requireNonNull(ownerStopping, "HTTP stop notification");
  }

  public void admit() throws IOException {
    synchronized (lock) {
      if (stopping || accepting || ownerStopping.getAsBoolean())
        throw new IOException("Web HTTP admission unavailable");
      accepting = true;
    }
  }

  public boolean accepting() {
    synchronized (lock) {
      return accepting && !ownerStopping.getAsBoolean();
    }
  }

  boolean acquire() {
    synchronized (lock) {
      if (!accepting || ownerStopping.getAsBoolean()) return false;
      active++;
      return true;
    }
  }

  void completed() {
    synchronized (lock) {
      if (active < 1) throw new IllegalStateException("Web HTTP completion unavailable");
      active--;
      lock.notifyAll();
    }
  }

  public void refuse() {
    synchronized (lock) {
      stopping = true;
      accepting = false;
    }
  }

  public void drain(Duration remaining) throws IOException {
    Objects.requireNonNull(remaining, "HTTP drain budget");
    if (remaining.isNegative() || remaining.compareTo(Duration.ofSeconds(30)) > 0)
      throw new IllegalArgumentException("invalid HTTP drain budget");
    long deadline = System.nanoTime() + remaining.toNanos();
    synchronized (lock) {
      stopping = true;
      accepting = false;
      while (active != 0) {
        long left = deadline - System.nanoTime();
        if (left <= 0) throw new IOException("Web HTTP drain unconfirmed");
        try {
          lock.wait(left / 1_000_000, (int) (left % 1_000_000));
        } catch (InterruptedException interruption) {
          Thread.currentThread().interrupt();
          throw new IOException("Web HTTP drain unconfirmed");
        }
      }
    }
  }
}
