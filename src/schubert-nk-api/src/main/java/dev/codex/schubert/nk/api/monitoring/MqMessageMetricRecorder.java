package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;

/** Supplied MQ observation events only; RD171/UI252/SS321323351/1718, never delivery authority. */
public final class MqMessageMetricRecorder {
  private static final String SEND_DIRECTION = "SEND";
  private static final String RECEIVE_DIRECTION = "RECEIVE";

  public enum Stage {
    SEND_SUCCESS(SEND_DIRECTION, "SUCCESS"),
    SEND_FAILURE(SEND_DIRECTION, "FAILURE"),
    RECEIVE_SUCCESS(RECEIVE_DIRECTION, "SUCCESS"),
    RECEIVE_FAILURE(RECEIVE_DIRECTION, "FAILURE"),
    ACK(RECEIVE_DIRECTION, "ACK"),
    RETRY(RECEIVE_DIRECTION, "RETRY"),
    DLQ(SEND_DIRECTION, "DLQ");

    private final String encodedDirection;
    private final String encodedOutcome;

    Stage(String direction, String outcome) {
      encodedDirection = direction;
      encodedOutcome = outcome;
    }

    public String direction() {
      return encodedDirection;
    }

    public String outcome() {
      return encodedOutcome;
    }

    public static Stage parse(String value) {
      Objects.requireNonNull(value, "MQ observation stage");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid MQ observation stage");
    }
  }

  private final boolean detailed;
  private final Map<Stage, Counter> counters;

  /** Layout/address labels are immutable. Namespace validation is not routing or send admission. */
  public MqMessageMetricRecorder(
      MeterRegistry registry, String mode, LayoutId layout, BrokerTopology destination) {
    Objects.requireNonNull(registry, "meter registry");
    var definition =
        LayoutRegistry.standard().require(Objects.requireNonNull(layout, "MQ metric layout"), 1);
    Objects.requireNonNull(destination, "MQ metric destination");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var installed = new EnumMap<Stage, Counter>(Stage.class);
    if (detailed)
      for (var stage : Stage.values())
        installed.put(
            stage,
            Counter.builder("nk_mq_messages_total")
                .baseUnit("messages")
                .tags(
                    "direction",
                    stage.direction(),
                    "address",
                    destination.address(),
                    "layout",
                    definition.id().value(),
                    "outcome",
                    stage.outcome())
                .register(registry));
    counters = Map.copyOf(installed);
  }

  /** One validated supplied event, one increment. No deduplication, replay or broker operation. */
  public void record(Stage stage) {
    Objects.requireNonNull(stage, "MQ observation stage");
    if (detailed)
      Objects.requireNonNull(counters.get(stage), "registered MQ observation").increment();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
