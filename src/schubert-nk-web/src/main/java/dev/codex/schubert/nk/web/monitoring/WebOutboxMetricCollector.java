package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Observation;
import io.micrometer.core.instrument.MeterRegistry;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;

/**
 * Private-owner readonly acquisition through complete publication; no real DB or scheduler
 * admission.
 */
public final class WebOutboxMetricCollector {
  private final Object lock = new Object();
  private final WebOutboxObservationRepository repository;
  private final WebOutboxMetricRecorder metrics;

  public WebOutboxMetricCollector(
      WebOutboxObservationRepository repository, MeterRegistry registry, String mode) {
    this.repository = Objects.requireNonNull(repository, "Web outbox repository");
    metrics = new WebOutboxMetricRecorder(registry, mode);
  }

  public Optional<Observation> collect(Connection connection, Instant asOf) throws SQLException {
    Objects.requireNonNull(connection, "borrowed Web metrics connection");
    Objects.requireNonNull(asOf, "Web outbox observation instant");
    synchronized (lock) {
      if (!metrics.detailedMetricsRequested()) return Optional.empty();
      try {
        Observation value = repository.read(connection, asOf);
        metrics.record(value);
        return Optional.of(value);
      } catch (SQLException | RuntimeException | Error unavailableObservation) {
        metrics.missing();
        throw unavailableObservation;
      }
    }
  }

  public Optional<Observation> snapshot() {
    return metrics.snapshot();
  }
}
