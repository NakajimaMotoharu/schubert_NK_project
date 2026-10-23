package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.AsyncJobMetricRecorder.Snapshot;
import dev.codex.schubert.nk.api.monitoring.persistence.AsyncJobCountRepository;
import io.micrometer.core.instrument.MeterRegistry;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;

/**
 * Owner-local collection/publication, not real connection admission, scheduler or outer deadline.
 * RD171/UI252/SS331332351; PG-D541/ASYNCCONN001..008/spec1631.
 */
public final class AsyncJobMetricCollector {
  private final Object lock = new Object();
  private final AsyncJobCountRepository repository;
  private final AsyncJobMetricRecorder metrics;

  public AsyncJobMetricCollector(
      AsyncJobCountRepository repository, MeterRegistry registry, String mode) {
    this.repository = Objects.requireNonNull(repository, "async counts repository");
    metrics = new AsyncJobMetricRecorder(registry, mode);
  }

  /** Caller owns the connection/transaction; serializes read through publication for this owner. */
  public Optional<Snapshot> collect(Connection connection) throws SQLException {
    Objects.requireNonNull(connection, "borrowed metrics connection");
    synchronized (lock) {
      if (!metrics.detailedMetricsRequested()) return Optional.empty();
      try {
        Snapshot supplied = repository.read(connection);
        metrics.record(supplied);
        return Optional.of(supplied);
      } catch (SQLException | RuntimeException | Error failedObservation) {
        metrics.missing();
        throw failedObservation;
      }
    }
  }

  public Optional<Snapshot> snapshot() {
    return metrics.snapshot();
  }
}
