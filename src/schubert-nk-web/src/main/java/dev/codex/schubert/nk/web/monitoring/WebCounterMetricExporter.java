package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.expositionformats.PrometheusTextFormatWriter;
import io.prometheus.metrics.model.snapshots.CounterSnapshot;
import io.prometheus.metrics.model.snapshots.CounterSnapshot.CounterDataPointSnapshot;
import io.prometheus.metrics.model.snapshots.MetricMetadata;
import io.prometheus.metrics.model.snapshots.MetricSnapshot;
import io.prometheus.metrics.model.snapshots.MetricSnapshots;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;

/** NK-OPS-001/RD171/UI252/SS351/1759 COUNTENC: Web-owned finite Counter text. */
public final class WebCounterMetricExporter {
  /** No source or mutable configuration retained. */
  public WebCounterMetricExporter() {}

  /** Exact approved total names and tag keys only; borrowed registry is never closed. */
  public String scrapeCounters(
      MeterRegistry source, Map<String, Set<String>> approvedNameLabelKeys) {
    return encode(
        source,
        approvedNameLabelKeys,
        PrometheusTextFormatWriter.builder().setIncludeCreatedTimestamps(false).build());
  }

  /** SS351/1767: fixed Web names and closed label values, copied directly into each model. */
  public String scrapeApprovedCounters(MeterRegistry source) {
    var catalog = new WebMetricCatalog();
    return encode(
        source,
        catalog.counters(),
        PrometheusTextFormatWriter.builder().setIncludeCreatedTimestamps(false).build(),
        Optional.of(catalog));
  }

  // COUNTENC015/016: checked-writer seam, not a retained resource or public endpoint.
  static String encode(
      MeterRegistry source,
      Map<String, Set<String>> approvedNameLabelKeys,
      ExpositionFormatWriter writer) {
    return encode(source, approvedNameLabelKeys, writer, Optional.empty());
  }

  private static String encode(
      MeterRegistry source,
      Map<String, Set<String>> approvedNameLabelKeys,
      ExpositionFormatWriter writer,
      Optional<WebMetricCatalog> catalog) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(writer, "text writer");
    var support = new WebMetricText();
    var namespace = support.namespace(approvedNameLabelKeys, "nk_[a-z][a-z0-9_]*_total", "counter");
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var groups = new TreeMap<String, List<CounterDataPointSnapshot>>();
    for (var meter : source.getMeters()) {
      var id = Objects.requireNonNull(meter, "meter").getId();
      String name = Objects.requireNonNull(id.getName(), "metric name");
      var keys = namespace.get(name);
      if (keys == null) continue;
      if (!(meter instanceof Counter counter))
        throw new IllegalArgumentException("selected meter is not a counter");
      var labels =
          catalog.isPresent()
              ? catalog.orElseThrow().labels(name, id.getTags())
              : support.labels(id, keys);
      double value = counter.count();
      if (!Double.isFinite(value) || value < 0)
        throw new IllegalArgumentException("invalid counter value");
      groups
          .computeIfAbsent(name, unused -> new ArrayList<>())
          .add(CounterDataPointSnapshot.builder().value(value).labels(labels).build());
    }
    var families =
        groups.entrySet().stream()
            .<MetricSnapshot>map(
                entry -> new CounterSnapshot(new MetricMetadata(entry.getKey()), entry.getValue()))
            .toList();
    return support.write(writer, new MetricSnapshots(families), "counter encoding failed");
  }
}
