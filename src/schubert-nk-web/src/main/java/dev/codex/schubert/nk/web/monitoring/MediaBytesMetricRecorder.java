package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.protocol.file.MediaType;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/** Supplied terminal media byte counts only, not delivery/HTTP success. SS333351;1706. */
public final class MediaBytesMetricRecorder {
  public enum Mode {
    INLINE,
    DOWNLOAD,
    RANGE;

    public static Mode parse(String value) {
      Objects.requireNonNull(value, "media byte mode");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid media byte mode");
    }
  }

  private static final List<Integer> ACCEPTED_STATUSES = List.of(200, 206, 416, 503);
  private final boolean detailed;
  private final Map<MediaType, Map<Mode, Map<Integer, Counter>>> counters;

  /** Borrowed dedicated registry; caller owns partial construction and final cleanup. */
  public MediaBytesMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed = new HttpMetricContract().detailedMetricsEnabled(mode);
    var types = new EnumMap<MediaType, Map<Mode, Map<Integer, Counter>>>(MediaType.class);
    if (detailed)
      for (var type : MediaType.values()) {
        var modes = new EnumMap<Mode, Map<Integer, Counter>>(Mode.class);
        for (var delivery : Mode.values()) {
          var statuses = new HashMap<Integer, Counter>();
          for (int status : ACCEPTED_STATUSES)
            statuses.put(
                status,
                Counter.builder("nk_media_bytes_total")
                    .tag("media_type", type.name())
                    .tag("mode", delivery.name())
                    .tag("status", Integer.toString(status))
                    .register(registry));
          modes.put(delivery, Map.copyOf(statuses));
        }
        types.put(type, Map.copyOf(modes));
      }
    counters = Map.copyOf(types);
  }

  /** One supplied byte increment, including zero; never infer application/transport outcome. */
  public void record(MediaType type, Mode mode, int status, long bytes) {
    Objects.requireNonNull(type, "media type");
    Objects.requireNonNull(mode, "media byte mode");
    if (!ACCEPTED_STATUSES.contains(status))
      throw new IllegalArgumentException("invalid media byte status");
    if (bytes < 0) throw new IllegalArgumentException("invalid media byte count");
    if (detailed) {
      var modes = Objects.requireNonNull(counters.get(type), "registered media type");
      var statuses = Objects.requireNonNull(modes.get(mode), "registered media byte mode");
      Objects.requireNonNull(statuses.get(status), "registered media byte counter")
          .increment((double) bytes);
    }
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }

  public static List<Integer> statuses() {
    return ACCEPTED_STATUSES;
  }
}
