package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;

/** Supplied delivery-count observations only, no JMS/read/retry. RD171/UI252/SS321351;1695. */
public final class MqRedeliveryMetricRecorder {
  private final boolean detailed;
  private final Map<BrokerTopology, Map<Integer, Counter>> counters;

  /**
   * Borrowed registry; six fixed queues times three redelivery attempts, initial delivery excluded.
   */
  public MqRedeliveryMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var installed = new EnumMap<BrokerTopology, Map<Integer, Counter>>(BrokerTopology.class);
    if (detailed)
      for (var destination : BrokerTopology.values()) {
        var row = new LinkedHashMap<Integer, Counter>();
        for (int delivery = 2; delivery <= 4; delivery++) {
          var counter =
              Counter.builder("nk_mq_redeliveries_total")
                  .tag("queue", destination.queue())
                  .tag("delivery_count", Integer.toString(delivery))
                  .register(registry);
          row.put(delivery, Objects.requireNonNull(counter, "registered redelivery counter"));
        }
        installed.put(destination, Map.copyOf(row));
      }
    counters = Map.copyOf(installed);
  }

  /** Initial1 is not redelivery; supplied2..4 increments once, never issues or infers a retry. */
  public void recordDelivery(BrokerTopology destination, int deliveryCount) {
    Objects.requireNonNull(destination, "MQ destination");
    if (deliveryCount < 1 || deliveryCount > 4)
      throw new IllegalArgumentException("invalid MQ delivery count");
    if (detailed && deliveryCount > 1) {
      var row = Objects.requireNonNull(counters.get(destination), "registered MQ destination");
      Objects.requireNonNull(row.get(deliveryCount), "registered redelivery attempt").increment();
    }
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
