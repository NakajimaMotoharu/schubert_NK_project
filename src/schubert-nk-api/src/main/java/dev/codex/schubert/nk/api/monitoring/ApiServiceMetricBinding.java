package dev.codex.schubert.nk.api.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS311332342351/1852/PG-D630: strongly retained non-resource metadata only.
 * A snapshot source borrows immutable, already owned observations; it must not query, acquire
 * connections/workers, reenter this context or operate on its SDK owner. Actual RO source/lifetime
 * qualification is separate. Missing observations are NaN, never invented zero or readiness.
 */
public final class ApiServiceMetricBinding {
  private final ApiDbPoolMetricBinding database;
  private final OutboxRowsMetricRecorder rows;
  private final OutboxAgeMetricRecorder ages;
  private final Supplier<? extends Optional<Snapshot>> observations;
  private final AtomicReference<Optional<Snapshot>> lastObservation =
      new AtomicReference<>(Optional.empty());

  /** Resource-free default: no actual Outbox source is claimed or acquired. */
  public static ApiMetricContext<ApiServiceMetricBinding> prepareContext(
      String mode,
      Supplier<? extends HikariPoolMXBean> pool,
      Supplier<? extends HikariConfigMXBean> config) {
    return prepareContext(mode, pool, config, Optional::<Snapshot>empty);
  }

  /** Caller captures the context before initialize; STANDARD reads none of the suppliers. */
  public static ApiMetricContext<ApiServiceMetricBinding> prepareContext(
      String mode,
      Supplier<? extends HikariPoolMXBean> pool,
      Supplier<? extends HikariConfigMXBean> config,
      Supplier<? extends Optional<Snapshot>> observations) {
    Objects.requireNonNull(pool, "borrowed pool supplier");
    Objects.requireNonNull(config, "borrowed pool configuration supplier");
    Objects.requireNonNull(observations, "borrowed outbox snapshot supplier");
    return new ApiMetricContext<ApiServiceMetricBinding>(
        mode,
        registry ->
            new ApiServiceMetricBinding(
                Objects.requireNonNull(pool.get(), "borrowed pool observation"),
                Objects.requireNonNull(config.get(), "borrowed pool configuration observation"),
                registry,
                mode,
                observations),
        ApiServiceMetricBinding::refresh);
  }

  private ApiServiceMetricBinding(
      HikariPoolMXBean pool,
      HikariConfigMXBean config,
      MeterRegistry registry,
      String mode,
      Supplier<? extends Optional<Snapshot>> observations) {
    database = new ApiDbPoolMetricBinding(pool, config, registry, mode);
    rows = new OutboxRowsMetricRecorder(registry, mode);
    ages = new OutboxAgeMetricRecorder(registry, mode);
    this.observations = observations;
  }

  /** Invoked only under the caller-owned context lock; performs no I/O or lifecycle operation. */
  private void refresh() {
    boolean complete = false;
    try {
      database.refresh();
      Optional<Snapshot> supplied =
          Objects.requireNonNull(observations.get(), "borrowed outbox snapshot");
      if (supplied.isPresent()) {
        var value = supplied.orElseThrow();
        rows.record(value.counts());
        ages.record(value.ages());
        lastObservation.set(supplied);
      } else {
        missing();
      }
      complete = true;
    } finally {
      // Preserve the original throwable without catch/normalization, including null-contract
      // faults.
      if (!complete) missing();
    }
  }

  private void missing() {
    rows.missing();
    ages.missing();
    lastObservation.set(Optional.empty());
  }

  /** Immutable last observation only, not cross-family scrape atomicity, health or freshness. */
  public Optional<Snapshot> snapshot() {
    return lastObservation.get();
  }
}
