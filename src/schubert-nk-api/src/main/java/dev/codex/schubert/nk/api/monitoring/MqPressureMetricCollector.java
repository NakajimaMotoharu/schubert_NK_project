package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.MqPressureMetricRecorder.Snapshot;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;

/**
 * Owner-local supplied observation publication, no actual broker/management connection. SS351;1697.
 */
public final class MqPressureMetricCollector {
  private final ReentrantLock lock = new ReentrantLock();
  private final Function<BrokerTopology, Optional<Snapshot>> observation;
  private final MqPressureMetricRecorder metrics;

  /** Borrowed source and registry; no source read/close/retry during assembly. */
  public MqPressureMetricCollector(
      Function<BrokerTopology, Optional<Snapshot>> observation,
      MeterRegistry registry,
      String mode) {
    this.observation = Objects.requireNonNull(observation, "MQ pressure observation source");
    metrics = new MqPressureMetricRecorder(registry, mode);
  }

  /** One complete result before publication; unknown/failure clears only this destination. */
  public Optional<Snapshot> collect(BrokerTopology destination) {
    Objects.requireNonNull(destination, "MQ destination");
    lock.lock();
    try {
      if (!metrics.detailedMetricsRequested()) return Optional.empty();
      try {
        var supplied =
            Objects.requireNonNull(observation.apply(destination), "MQ pressure observation");
        if (supplied.isPresent()) metrics.record(destination, supplied.orElseThrow());
        else metrics.missing(destination);
        return supplied;
      } catch (RuntimeException | Error unavailableObservation) {
        metrics.missing(destination);
        throw unavailableObservation;
      }
    } finally {
      lock.unlock();
    }
  }

  public Optional<Snapshot> snapshot(BrokerTopology destination) {
    return metrics.snapshot(destination);
  }
}
