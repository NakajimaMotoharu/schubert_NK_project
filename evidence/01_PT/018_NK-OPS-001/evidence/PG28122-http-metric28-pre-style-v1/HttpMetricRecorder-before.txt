package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Labels;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Method;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Metric;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Route;
import dev.codex.schubert.nk.web.monitoring.HttpMetricContract.Status;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.Timer;
import java.time.Duration;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

/**
 * Borrowed dedicated registry; actual HTTP/source/owner and exposition are not proven here.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D527/HTTPREC001..009/spec1573.
 */
public final class HttpMetricRecorder {
  private final HttpMetricContract contract = new HttpMetricContract();
  private final boolean collectDetailed;
  private final Map<Labels, Counter> counters;
  private final Map<Route, Timer> durations;

  /** Owner must close the registry after all callbacks, including after a failed construction. */
  public HttpMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    collectDetailed = contract.detailedMetricsEnabled(mode);
    if (collectDetailed) OverflowSafeHttpMeterRegistry.requireCompatible(registry);
    var requests = new HashMap<Labels, Counter>();
    var timers = new EnumMap<Route, Timer>(Route.class);
    if (collectDetailed) {
      for (var route : Route.values()) {
        var labels = new Labels(route, Method.GET, Status.SUCCESS);
        timers.put(
            route,
            Timer.builder(Metric.DURATION.externalName())
                .publishPercentiles()
                .tags(tags(labels.durationLabels()))
                .serviceLevelObjectives(contract.durationBuckets().toArray(Duration[]::new))
                .register(registry));
        for (var method : Method.values())
          for (var status : Status.values()) {
            var key = new Labels(route, method, status);
            requests.put(
                key,
                Counter.builder(Metric.REQUESTS.externalName())
                    .tags(tags(key.requestLabels()))
                    .register(registry));
          }
      }
    }
    counters = Map.copyOf(requests);
    durations = Map.copyOf(timers);
  }

  /**
   * One completion, no retry; a provider failure may leave a partial sample and propagates
   * unchanged.
   */
  public void record(String route, String method, int status, long elapsedNanoseconds) {
    if (elapsedNanoseconds < 0) throw new IllegalArgumentException("invalid HTTP elapsed time");
    Labels labels = contract.labels(route, method, status);
    if (!collectDetailed) return;
    Objects.requireNonNull(counters.get(labels), "closed HTTP counter").increment();
    Objects.requireNonNull(durations.get(labels.route()), "closed HTTP timer")
        .record(elapsedNanoseconds, TimeUnit.NANOSECONDS);
  }

  public boolean detailedMetricsRequested() {
    return collectDetailed;
  }

  private static Tags tags(Map<String, String> labels) {
    Tags tags = Tags.empty();
    for (var entry : labels.entrySet()) tags = tags.and(entry.getKey(), entry.getValue());
    return tags;
  }
}
