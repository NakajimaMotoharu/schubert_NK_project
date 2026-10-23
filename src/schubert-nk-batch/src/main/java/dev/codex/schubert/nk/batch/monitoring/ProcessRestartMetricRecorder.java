package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.EnumMap;
import java.util.Map;
import java.util.Objects;

/** Supplied restart events only, never process observation or restart permission. SS351;1710. */
public final class ProcessRestartMetricRecorder {
  public enum Reason {
    NONZERO_EXIT,
    SIGNAL_EXIT,
    OOM,
    UNKNOWN;

    public static Reason parse(String value) {
      Objects.requireNonNull(value, "restart metric reason");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid restart metric reason");
    }
  }

  private final boolean detailed;
  private final Map<Reason, Map<Service, Counter>> counters;

  /** Caller supplies a dedicated borrowed namespace and owns partial registration cleanup. */
  public ProcessRestartMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed = MonitoringModePolicy.parse(mode).detailedMetricsEnabled();
    var reasons = new EnumMap<Reason, Map<Service, Counter>>(Reason.class);
    if (detailed)
      for (var reason : Reason.values()) {
        var services = new EnumMap<Service, Counter>(Service.class);
        for (var service : Service.values())
          services.put(
              service,
              Counter.builder("nk_process_restarts_total")
                  .tag("service", service.name())
                  .tag("reason", reason.name())
                  .register(registry));
        reasons.put(reason, Map.copyOf(services));
      }
    counters = Map.copyOf(reasons);
  }

  /** One supplied restart; UNKNOWN is an unknown cause, never evidence that restart occurred. */
  public void record(Reason reason, Service service) {
    Objects.requireNonNull(reason, "restart metric reason");
    Objects.requireNonNull(service, "metric service");
    if (detailed) {
      var services = Objects.requireNonNull(counters.get(reason), "registered restart reason");
      Objects.requireNonNull(services.get(service), "registered restart service").increment();
    }
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
