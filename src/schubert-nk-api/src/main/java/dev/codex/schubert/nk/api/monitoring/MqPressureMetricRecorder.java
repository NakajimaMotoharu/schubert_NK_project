package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.ToDoubleFunction;

/** Supplied MQ pressure only; no Artemis management/JMS/control. RD171/UI252/SS321351;1693. */
public final class MqPressureMetricRecorder {
  private static final String QUEUE_LABEL = "queue";
  private static final String ADDRESS_LABEL = "address";

  /** Caller-supplied current sample, no inferred capacity or cross-measurement invariant. */
  public record Snapshot(
      long messages,
      long queueBytes,
      long addressMemoryBytes,
      long addressPagedBytes,
      boolean pagingActive,
      long pageFiles) {
    public Snapshot {
      if (messages < 0
          || queueBytes < 0
          || addressMemoryBytes < 0
          || addressPagedBytes < 0
          || pageFiles < 0) throw new IllegalArgumentException("invalid MQ pressure sample");
    }
  }

  private final boolean detailed;
  private final Map<BrokerTopology, AtomicReference<Optional<Snapshot>>> observations;

  /** Borrowed registry; one assembly owns six fixed gauge families, never runtime authority. */
  public MqPressureMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var rows =
        new EnumMap<BrokerTopology, AtomicReference<Optional<Snapshot>>>(BrokerTopology.class);
    if (detailed) {
      for (var destination : BrokerTopology.values()) {
        var row = new AtomicReference<Optional<Snapshot>>(Optional.empty());
        rows.put(destination, row);
        install(
            registry,
            "nk_mq_queue_messages",
            QUEUE_LABEL,
            destination.queue(),
            row,
            Snapshot::messages);
        install(
            registry,
            "nk_mq_queue_bytes",
            QUEUE_LABEL,
            destination.queue(),
            row,
            Snapshot::queueBytes);
        install(
            registry,
            "nk_mq_address_memory_bytes",
            ADDRESS_LABEL,
            destination.address(),
            row,
            Snapshot::addressMemoryBytes);
        install(
            registry,
            "nk_mq_address_paged_bytes",
            ADDRESS_LABEL,
            destination.address(),
            row,
            Snapshot::addressPagedBytes);
        install(
            registry,
            "nk_mq_paging_active",
            ADDRESS_LABEL,
            destination.address(),
            row,
            sample -> sample.pagingActive() ? 1 : 0);
        install(
            registry,
            "nk_mq_page_files",
            ADDRESS_LABEL,
            destination.address(),
            row,
            Snapshot::pageFiles);
      }
    }
    observations = Map.copyOf(rows);
  }

  private static void install(
      MeterRegistry registry,
      String name,
      String label,
      String value,
      AtomicReference<Optional<Snapshot>> row,
      ToDoubleFunction<Snapshot> measure) {
    Gauge.builder(
            name, row, current -> current.get().map(measure::applyAsDouble).orElse(Double.NaN))
        .tag(label, value)
        .register(registry);
  }

  public void record(BrokerTopology destination, Snapshot sample) {
    Objects.requireNonNull(destination, "MQ destination");
    Objects.requireNonNull(sample, "MQ pressure sample");
    if (detailed) row(destination).set(Optional.of(sample));
  }

  public void missing(BrokerTopology destination) {
    Objects.requireNonNull(destination, "MQ destination");
    if (detailed) row(destination).set(Optional.empty());
  }

  public Optional<Snapshot> snapshot(BrokerTopology destination) {
    Objects.requireNonNull(destination, "MQ destination");
    return detailed ? row(destination).get() : Optional.empty();
  }

  private AtomicReference<Optional<Snapshot>> row(BrokerTopology destination) {
    return Objects.requireNonNull(observations.get(destination), "registered MQ destination");
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
