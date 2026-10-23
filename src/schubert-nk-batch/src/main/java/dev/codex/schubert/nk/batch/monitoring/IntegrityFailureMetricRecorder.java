package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.repository.BatchStep;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;

/**
 * Supplied Batch integrity events, never a probe, repair or alert-retirement authority. SS351;1708.
 */
public final class IntegrityFailureMetricRecorder {
  public enum Area {
    HASH,
    PATH,
    CONFIG;

    public static Area parse(String value) {
      Objects.requireNonNull(value, "integrity metric area");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid integrity metric area");
    }
  }

  private final boolean detailed;
  private final Map<Area, Map<BatchStep, Counter>> counters;

  /** Borrowed registry. Partial registration and final cleanup remain caller-owned. */
  public IntegrityFailureMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed = MonitoringModePolicy.parse(mode).detailedMetricsEnabled();
    var areas = new EnumMap<Area, Map<BatchStep, Counter>>(Area.class);
    if (detailed)
      for (var area : Area.values()) {
        var steps = new EnumMap<BatchStep, Counter>(BatchStep.class);
        for (var step : BatchStep.values())
          steps.put(
              step,
              Counter.builder("nk_integrity_failures_total")
                  .tag("area", area.name())
                  .tag("step", step.name())
                  .register(registry));
        areas.put(area, Map.copyOf(steps));
      }
    counters = Map.copyOf(areas);
  }

  /** One caller-supplied failure event; no retry, compensation, detection or alert side effects. */
  public void record(Area area, BatchStep step) {
    Objects.requireNonNull(area, "integrity metric area");
    Objects.requireNonNull(step, "batch step");
    if (detailed) {
      var steps = Objects.requireNonNull(counters.get(area), "registered integrity area");
      Objects.requireNonNull(steps.get(step), "registered integrity step").increment();
    }
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
