package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumSet;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Supplied full job counts, no DB/worker/control or real collector. RD171/UI252/SS324331351;
 * PG-D539/ASYNCGAUGE001..008/spec1623.
 */
public final class AsyncJobMetricRecorder {
  public enum State {
    RECEIVED,
    PROCESSING,
    COMPLETED,
    ERROR,
    CANCELLED
  }

  public static final class Snapshot {
    private final Map<State, Long> valuesByState;
    private final long sumOfJobs;

    public Snapshot(Map<State, Long> supplied) {
      var values = Map.copyOf(Objects.requireNonNull(supplied, "async job counts"));
      if (!values.keySet().equals(EnumSet.allOf(State.class)))
        throw new IllegalArgumentException("incomplete async job counts");
      long total = 0;
      for (long count : values.values()) {
        if (count < 0) throw new IllegalArgumentException("negative async job count");
        total = Math.addExact(total, count);
      }
      valuesByState = values;
      sumOfJobs = total;
    }

    public long value(State state) {
      return Objects.requireNonNull(
          valuesByState.get(Objects.requireNonNull(state, "job state")), "closed async count");
    }

    public long totalJobs() {
      return sumOfJobs;
    }
  }

  private static final String METRIC = "nk_async_jobs";
  private final boolean detailed;
  private final AtomicReference<Optional<Snapshot>> observedCounts =
      new AtomicReference<>(Optional.empty());

  /**
   * One instance owns this registry namespace; caller retains all registry cleanup responsibility.
   */
  public AsyncJobMetricRecorder(MeterRegistry registry, String mode) {
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
                METRIC,
                observedCounts,
                snapshot ->
                    snapshot.get().map(counts -> (double) counts.value(state)).orElse(Double.NaN))
            .tag("state", state.name())
            .register(registry);
  }

  public static State state(String value) {
    Objects.requireNonNull(value, "async metric state");
    for (var state : State.values()) if (state.name().equals(value)) return state;
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public void record(Snapshot supplied) {
    Objects.requireNonNull(supplied, "async metric snapshot");
    if (detailed) observedCounts.set(Optional.of(supplied));
  }

  public void missing() {
    observedCounts.set(Optional.empty());
  }

  public Optional<Snapshot> snapshot() {
    return observedCounts.get();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
