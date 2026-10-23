package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Supplied API pool counts, not a pool getter/DB/management connection.
 * PG-D542/POOLMET001..008/spec1635.
 */
public final class DbPoolMetricRecorder {
  public enum State {
    ACTIVE("active"),
    IDLE("idle"),
    PENDING("pending"),
    MAX("max");

    private final String stateLabel;

    State(String stateLabel) {
      this.stateLabel = stateLabel;
    }

    public String label() {
      return stateLabel;
    }
  }

  /** Independent instantaneous counters; no invented cross-getter atomicity or count summation. */
  public record Counts(long active, long idle, long pending, long maximum) {
    public Counts {
      if (active < 0 || idle < 0 || pending < 0 || maximum < 1)
        throw new IllegalArgumentException("invalid pool counts");
    }

    public long value(State state) {
      Objects.requireNonNull(state, "pool metric state");
      if (state == State.ACTIVE) return active;
      if (state == State.IDLE) return idle;
      if (state == State.PENDING) return pending;
      return maximum;
    }
  }

  private final boolean detailed;
  private final AtomicReference<Optional<Counts>> observedCounts =
      new AtomicReference<>(Optional.empty());

  /** One instance owns API pool metric namespace; registry lifetime remains caller-owned. */
  public DbPoolMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    if (detailed)
      for (var state : State.values())
        Gauge.builder(
                "nk_db_pool_connections",
                observedCounts,
                snapshot ->
                    snapshot.get().map(counts -> (double) counts.value(state)).orElse(Double.NaN))
            .tag("service", "API")
            .tag("state", state.label())
            .register(registry);
  }

  public static State state(String supplied) {
    Objects.requireNonNull(supplied, "pool metric state");
    for (var state : State.values()) if (state.label().equals(supplied)) return state;
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public void record(Counts supplied) {
    Objects.requireNonNull(supplied, "pool metric counts");
    if (detailed) observedCounts.set(Optional.of(supplied));
  }

  public void missing() {
    observedCounts.set(Optional.empty());
  }

  public Optional<Counts> snapshot() {
    return observedCounts.get();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
