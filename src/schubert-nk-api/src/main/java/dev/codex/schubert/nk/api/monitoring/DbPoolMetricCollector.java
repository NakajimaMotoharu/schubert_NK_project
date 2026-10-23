package dev.codex.schubert.nk.api.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorder.Counts;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;

/**
 * Owner-local borrowed getter publication only, not a real-pool collector startup. PG-D543/1639.
 */
public final class DbPoolMetricCollector {
  private final Object lock = new Object();
  private final DbPoolMetricObservation observation;
  private final DbPoolMetricRecorder metrics;

  public DbPoolMetricCollector(
      DbPoolMetricObservation observation, MeterRegistry registry, String mode) {
    this.observation = Objects.requireNonNull(observation, "pool metric observation");
    metrics = new DbPoolMetricRecorder(registry, mode);
  }

  public Optional<Counts> collect(HikariPoolMXBean pool, HikariConfigMXBean config) {
    Objects.requireNonNull(pool, "borrowed pool observation");
    Objects.requireNonNull(config, "borrowed pool configuration observation");
    synchronized (lock) {
      if (!metrics.detailedMetricsRequested()) return Optional.empty();
      try {
        Optional<Counts> supplied = observation.observe(pool, config);
        if (supplied.isPresent()) metrics.record(supplied.orElseThrow());
        else metrics.missing();
        return supplied;
      } catch (RuntimeException | Error unavailableObservation) {
        metrics.missing();
        throw unavailableObservation;
      }
    }
  }

  public Optional<Counts> snapshot() {
    return metrics.snapshot();
  }
}
