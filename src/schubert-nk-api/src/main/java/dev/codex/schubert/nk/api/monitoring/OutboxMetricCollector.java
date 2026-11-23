package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import io.micrometer.core.instrument.MeterRegistry;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;

/** Owner-local read/close/publication, not actual source or outer deadline. PG-D548/1668. */
public final class OutboxMetricCollector {
  private final ReentrantLock lock = new ReentrantLock();
  private final OutboxObservationRepository repository;
  private final OutboxRowsMetricRecorder rows;
  private final OutboxAgeMetricRecorder ages;
  private final AtomicReference<Optional<Snapshot>> lastObservation =
      new AtomicReference<>(Optional.empty());

  public OutboxMetricCollector(
      OutboxObservationRepository repository, MeterRegistry registry, String mode) {
    this.repository = Objects.requireNonNull(repository, "outbox observation repository");
    rows = new OutboxRowsMetricRecorder(registry, mode);
    ages = new OutboxAgeMetricRecorder(registry, mode);
  }

  /** Caller owns connection/transaction/asOf; no cross-family atomic exporter scrape implied. */
  public Optional<Snapshot> collect(Connection connection, Instant asOf) throws SQLException {
    Objects.requireNonNull(connection, "borrowed metrics connection");
    Objects.requireNonNull(asOf, "outbox observation instant");
    lock.lock();
    try {
      if (!rows.detailedMetricsRequested()) return Optional.empty();
      try {
        Snapshot supplied = repository.read(connection, asOf);
        rows.record(supplied.counts());
        ages.record(supplied.ages());
        lastObservation.set(Optional.of(supplied));
        return Optional.of(supplied);
      } catch (SQLException | RuntimeException | Error failedObservation) {
        rows.missing();
        ages.missing();
        lastObservation.set(Optional.empty());
        throw failedObservation;
      }
    } finally {
      lock.unlock();
    }
  }

  public Optional<Snapshot> snapshot() {
    return lastObservation.get();
  }
}
