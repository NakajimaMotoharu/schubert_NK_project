package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;

/** One approved layout's supplied MQ durations; RD171/UI252/SS321323351/1716, no JMS or clock. */
public final class MqProcessingDurationMetricRecorder {
  public enum Outcome {
    SUCCESS,
    FAILURE;

    public static Outcome parse(String value) {
      Objects.requireNonNull(value, "MQ duration outcome");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid MQ duration outcome");
    }
  }

  private final boolean detailed;
  private final Map<Outcome, DistributionSummary> observations;

  /** Immutable layout/flow binding; caller owns registry and any partial registration. */
  public MqProcessingDurationMetricRecorder(MeterRegistry registry, String mode, LayoutId layout) {
    Objects.requireNonNull(registry, "meter registry");
    var definition =
        LayoutRegistry.standard().require(Objects.requireNonNull(layout, "MQ duration layout"), 1);
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var installed = new EnumMap<Outcome, DistributionSummary>(Outcome.class);
    if (detailed)
      for (var outcome : Outcome.values())
        installed.put(
            outcome,
            DistributionSummary.builder("nk_mq_processing_duration_seconds")
                .baseUnit("seconds")
                .tags(
                    "flow",
                    definition.interactionKind().name(),
                    "layout",
                    definition.id().value(),
                    "outcome",
                    outcome.name())
                .publishPercentileHistogram()
                .publishPercentiles(.95)
                .serviceLevelObjectives(.001, .01, .1, 1., 1.5)
                .register(registry));
    observations = Map.copyOf(installed);
  }

  /** Complete supplied event only; neither elapsed time nor JMS success is inferred here. */
  public void record(Outcome outcome, long elapsedNanoseconds) {
    Objects.requireNonNull(outcome, "MQ duration outcome");
    if (elapsedNanoseconds < 0) throw new IllegalArgumentException("invalid MQ duration");
    if (detailed)
      Objects.requireNonNull(observations.get(outcome), "registered MQ duration")
          .record(elapsedNanoseconds / 1_000_000_000.0);
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
