package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;

/** Supplied replay events only, never Inbox/DB/JMS/dedup authority. RD171/UI252/SS351;1691. */
public final class InboxReplayMetricRecorder {
  private final boolean detailed;
  private final Map<LayoutId, Map<ResultCode, Counter>> counters;

  /**
   * Borrowed registry; all64 approved layout IDs and12 results form a fixed768-series namespace.
   */
  public InboxReplayMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    var installed = new LinkedHashMap<LayoutId, Map<ResultCode, Counter>>();
    if (detailed) {
      for (var definition : LayoutRegistry.standard().all()) {
        var row = new EnumMap<ResultCode, Counter>(ResultCode.class);
        for (var result : ResultCode.values()) {
          var counter =
              Counter.builder("nk_inbox_replays_total")
                  .tag("layout", definition.id().value())
                  .tag("result", result.wireValue())
                  .register(registry);
          row.put(result, Objects.requireNonNull(counter, "registered replay counter"));
        }
        installed.put(definition.id(), Map.copyOf(row));
      }
    }
    counters = Map.copyOf(installed);
  }

  /** One validated supplied event, one increment; no inferred replay, retry or compensation. */
  public void record(LayoutId layout, ResultCode result) {
    Objects.requireNonNull(layout, "replay layout");
    Objects.requireNonNull(result, "replay result");
    LayoutRegistry.standard().require(layout, 1);
    if (detailed) {
      var row = Objects.requireNonNull(counters.get(layout), "registered replay layout");
      Objects.requireNonNull(row.get(result), "registered replay result").increment();
    }
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
