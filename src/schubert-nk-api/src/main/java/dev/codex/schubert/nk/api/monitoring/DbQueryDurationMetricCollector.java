package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder.Outcome;
import dev.codex.schubert.nk.api.monitoring.DbQueryDurationMetricRecorder.Query;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;

/**
 * Complete supplied observations only; RD171/UI252/SS332351/1714, never query or clock authority.
 */
public final class DbQueryDurationMetricCollector {
  public record Observation(Outcome outcome, long elapsedNanoseconds) {
    public Observation {
      Objects.requireNonNull(outcome, "DB duration outcome");
      if (elapsedNanoseconds < 0)
        throw new IllegalArgumentException("invalid DB duration observation");
    }
  }

  private final ReentrantLock lock = new ReentrantLock();
  private final Function<Query, Optional<Observation>> observation;
  private final DbQueryDurationMetricRecorder metrics;

  public DbQueryDurationMetricCollector(
      Function<Query, Optional<Observation>> observation, MeterRegistry registry, String mode) {
    this.observation = Objects.requireNonNull(observation, "DB duration observation source");
    metrics = new DbQueryDurationMetricRecorder(registry, mode);
  }

  /** Missing or failed acquisition is no event, never invented zero duration/SUCCESS/FAILURE. */
  public Optional<Observation> collect(Query query) {
    Objects.requireNonNull(query, "DB duration query");
    lock.lock();
    try {
      if (!metrics.detailedMetricsRequested()) return Optional.empty();
      Optional<Observation> supplied =
          Objects.requireNonNull(observation.apply(query), "DB duration observation");
      if (supplied.isPresent()) {
        var value = supplied.orElseThrow();
        metrics.record(query, value.outcome(), value.elapsedNanoseconds());
      }
      return supplied;
    } finally {
      lock.unlock();
    }
  }
}
