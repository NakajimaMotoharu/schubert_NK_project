package dev.codex.schubert.nk.web.bootstrap;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import java.io.IOException;
import java.time.Duration;
import java.util.Objects;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * NK-WEB-002/NK-OPS-001; SS342352; PG-D377/1142; PT-OPS-NWEB-STOP001..006. Owner-lock guarded
 * phases; BUG2409/YKT2154 uses relative time across signed clock wrap; later unknown phases stay
 * owned.
 */
@NullMarked
final class WebRuntimeStop {
  private final LongSupplier nanoTime;
  private int confirmed;
  private long deadline;

  WebRuntimeStop(LongSupplier nanoTime) {
    this.nanoTime = Objects.requireNonNull(nanoTime, "Web stop clock");
  }

  /** Native owner calls once on its stopping CAS, before refusing/draining admission. */
  void begin() {
    deadline = nanoTime.getAsLong() + Duration.ofSeconds(30).toNanos();
  }

  void close(Step[] phases) throws IOException {
    while (confirmed < phases.length) {
      Duration left = Duration.ofNanos(Math.max(0, deadline - nanoTime.getAsLong()));
      try {
        phases[confirmed].close(left);
      } catch (IOException | org.apache.catalina.LifecycleException | RuntimeException failure) {
        SessionStoreException.preserveFatal(failure);
        throw new IOException("Web stop unconfirmed");
      }
      confirmed++;
      if (deadline - nanoTime.getAsLong() < 0) throw new IOException("Web stop unconfirmed");
    }
  }

  @FunctionalInterface
  interface Step {
    void close(Duration remaining) throws IOException, org.apache.catalina.LifecycleException;
  }
}
