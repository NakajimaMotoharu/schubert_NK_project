package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;
import java.util.OptionalLong;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Supplied active-stream observations only, not media open/close/admission.
 * RD171/UI252/SS333351;1702.
 */
public final class MediaStreamsMetricRecorder {
  private final boolean detailed;
  private final Map<MediaType, AtomicReference<OptionalLong>> observations;

  /**
   * Borrowed registry, three fixed media-type series; real lifetime/source remains caller-owned.
   */
  public MediaStreamsMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed = new HttpMetricContract().detailedMetricsEnabled(mode);
    var rows = new EnumMap<MediaType, AtomicReference<OptionalLong>>(MediaType.class);
    if (detailed)
      for (var type : MediaType.values()) {
        var row = new AtomicReference<>(OptionalLong.empty());
        rows.put(type, row);
        Gauge.builder("nk_media_streams", row, current -> value(current.get()))
            .tag("media_type", type.name())
            .register(registry);
      }
    observations = Map.copyOf(rows);
  }

  private static double value(OptionalLong current) {
    return current.isPresent() ? (double) current.getAsLong() : Double.NaN;
  }

  public void record(MediaType type, long streams) {
    Objects.requireNonNull(type, "media type");
    if (streams < 0) throw new IllegalArgumentException("invalid media stream count");
    if (detailed) row(type).set(OptionalLong.of(streams));
  }

  public void missing(MediaType type) {
    Objects.requireNonNull(type, "media type");
    if (detailed) row(type).set(OptionalLong.empty());
  }

  public OptionalLong snapshot(MediaType type) {
    Objects.requireNonNull(type, "media type");
    return detailed ? row(type).get() : OptionalLong.empty();
  }

  private AtomicReference<OptionalLong> row(MediaType type) {
    return Objects.requireNonNull(observations.get(type), "registered media type");
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
