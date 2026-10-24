package dev.codex.schubert.nk.web.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricRecorder.Counts;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;

/**
 * NK-OPS-001/RD171/UI252/SS311342351/1825/PG-D621: non-resource borrowed pool metadata. No
 * pool/config creation, connection, JMX lookup, controls, credential access or owner close. The
 * caller retains the bean and registry owners throughout every refresh/snapshot use.
 */
public final class WebDbPoolMetricBinding {
  private final HikariPoolMXBean pool;
  private final HikariConfigMXBean config;
  private final WebDbPoolMetricCollector collector;

  public WebDbPoolMetricBinding(
      HikariPoolMXBean pool, HikariConfigMXBean config, MeterRegistry registry, String mode) {
    this.pool = Objects.requireNonNull(pool, "borrowed pool observation");
    this.config = Objects.requireNonNull(config, "borrowed pool configuration observation");
    Objects.requireNonNull(registry, "metric registry");
    Objects.requireNonNull(mode, "monitoring mode");
    this.collector = new WebDbPoolMetricCollector(new WebDbPoolMetricObservation(), registry, mode);
  }

  /** Context refresh callback only; provider failure remains unconfirmed/missing, never zero. */
  public void refresh() {
    collector.collect(pool, config);
  }

  /** Last immutable observation, not a freshness, liveness or readiness certificate. */
  public Optional<Counts> snapshot() {
    return collector.snapshot();
  }
}
