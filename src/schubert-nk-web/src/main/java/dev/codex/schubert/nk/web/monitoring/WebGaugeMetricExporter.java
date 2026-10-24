package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.expositionformats.PrometheusTextFormatWriter;
import io.prometheus.metrics.model.snapshots.GaugeSnapshot;
import io.prometheus.metrics.model.snapshots.GaugeSnapshot.GaugeDataPointSnapshot;
import io.prometheus.metrics.model.snapshots.MetricMetadata;
import io.prometheus.metrics.model.snapshots.MetricSnapshot;
import io.prometheus.metrics.model.snapshots.MetricSnapshots;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;

/**
 * NK-OPS-001/RD171/UI252/SS351/1761 GAUGEENC: Web-owned standard Gauge text, including explicit
 * unknown NaN.
 */
public final class WebGaugeMetricExporter {
  /** No source or mutable configuration retained. */
  public WebGaugeMetricExporter() {}

  /** Exact approved gauge names and tag keys only; borrowed registry is never closed. */
  public String scrapeGauges(MeterRegistry source, Map<String, Set<String>> approvedNameLabelKeys) {
    return encode(
        source,
        approvedNameLabelKeys,
        PrometheusTextFormatWriter.builder().setIncludeCreatedTimestamps(false).build());
  }

  // GAUGEENC015/016: checked-writer seam, not a retained resource or public endpoint.
  static String encode(
      MeterRegistry source,
      Map<String, Set<String>> approvedNameLabelKeys,
      ExpositionFormatWriter writer) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(writer, "text writer");
    var support = new WebMetricText();
    var namespace = support.namespace(approvedNameLabelKeys, "nk_[a-z][a-z0-9_]*", "gauge");
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var groups = new TreeMap<String, List<GaugeDataPointSnapshot>>();
    for (var meter : source.getMeters()) {
      var id = Objects.requireNonNull(meter, "meter").getId();
      var keys = namespace.get(id.getName());
      if (keys == null) continue;
      if (!(meter instanceof Gauge gauge))
        throw new IllegalArgumentException("selected meter is not a gauge");
      var labels = support.labels(id, keys);
      double value = gauge.value();
      groups
          .computeIfAbsent(id.getName(), unused -> new ArrayList<>())
          .add(GaugeDataPointSnapshot.builder().value(value).labels(labels).build());
    }
    var families =
        groups.entrySet().stream()
            .<MetricSnapshot>map(
                entry -> new GaugeSnapshot(new MetricMetadata(entry.getKey()), entry.getValue()))
            .toList();
    return support.write(writer, new MetricSnapshots(families), "gauge encoding failed");
  }
}
