package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.OptionalLong;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;

/**
 * Borrowed supplied stream observation, not a real stream/admission or HTTP adapter.
 * RD171/UI252/SS333351;1704/MEDIACONN001..008.
 */
public final class MediaStreamsMetricCollector {
  private final ReentrantLock lock = new ReentrantLock();
  private final Function<MediaType, OptionalLong> source;
  private final MediaStreamsMetricRecorder metrics;

  /** No source calls or source/registry close during construction. */
  public MediaStreamsMetricCollector(
      Function<MediaType, OptionalLong> source, MeterRegistry registry, String mode) {
    this.source = Objects.requireNonNull(source, "media stream observation source");
    metrics = new MediaStreamsMetricRecorder(registry, mode);
  }

  /** Serialize this owner's read/publication; unknown and failure affect only the selected type. */
  public OptionalLong collect(MediaType type) {
    Objects.requireNonNull(type, "media type");
    lock.lock();
    try {
      if (!metrics.detailedMetricsRequested()) return OptionalLong.empty();
      try {
        var supplied = Objects.requireNonNull(source.apply(type), "media stream observation");
        if (supplied.isPresent()) metrics.record(type, supplied.orElseThrow());
        else metrics.missing(type);
        return supplied;
      } catch (RuntimeException | Error unavailableObservation) {
        metrics.missing(type);
        throw unavailableObservation;
      }
    } finally {
      lock.unlock();
    }
  }

  public OptionalLong snapshot(MediaType type) {
    return metrics.snapshot(type);
  }
}
