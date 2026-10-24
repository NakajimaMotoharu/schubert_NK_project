package dev.codex.schubert.nk.api.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.api.monitoring.DbPoolMetricRecorder.Counts;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS311342351/1825/PG-D621: non-resource borrowed pool metadata. No
 * pool/config creation, connection, JMX lookup, controls, credential access or owner close. The
 * caller retains the bean and registry owners throughout every refresh/snapshot use.
 */
public final class ApiDbPoolMetricBinding {
  private final HikariPoolMXBean pool;
  private final HikariConfigMXBean config;
  private final DbPoolMetricCollector collector;

  /**
   * 1827/PG-D622: resource-free; retain returned owner before initialize. Suppliers borrow only.
   */
  public static ApiMetricContext<ApiDbPoolMetricBinding> prepareContext(
      String mode,
      Supplier<? extends HikariPoolMXBean> pool,
      Supplier<? extends HikariConfigMXBean> config) {
    Objects.requireNonNull(pool, "borrowed pool supplier");
    Objects.requireNonNull(config, "borrowed pool configuration supplier");
    return new ApiMetricContext<ApiDbPoolMetricBinding>(
        mode,
        registry ->
            new ApiDbPoolMetricBinding(
                Objects.requireNonNull(pool.get(), "borrowed pool observation"),
                Objects.requireNonNull(config.get(), "borrowed pool configuration observation"),
                registry,
                mode),
        ApiDbPoolMetricBinding::refresh);
  }

  public ApiDbPoolMetricBinding(
      HikariPoolMXBean pool, HikariConfigMXBean config, MeterRegistry registry, String mode) {
    this.pool = Objects.requireNonNull(pool, "borrowed pool observation");
    this.config = Objects.requireNonNull(config, "borrowed pool configuration observation");
    Objects.requireNonNull(registry, "metric registry");
    Objects.requireNonNull(mode, "monitoring mode");
    this.collector = new DbPoolMetricCollector(new DbPoolMetricObservation(), registry, mode);
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
