package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.expositionformats.PrometheusTextFormatWriter;
import io.prometheus.metrics.model.snapshots.ClassicHistogramBuckets;
import io.prometheus.metrics.model.snapshots.Exemplars;
import io.prometheus.metrics.model.snapshots.HistogramSnapshot.HistogramDataPointSnapshot;
import io.prometheus.metrics.model.snapshots.Labels;
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
 * NK-OPS-001/RD171/UI252/SS351/1757/BUG1697: app-owned atomic Timer/ns snapshots to standard
 * histogram text. A borrowed source is never closed. No global exporter configuration, clock, file
 * or network reads.
 */
public final class WebDurationMetricExporter {
  /** No resources acquired; the official writer is explicitly configured per scrape. */
  public WebDurationMetricExporter() {}

  /**
   * Exports only approved seconds names with exact label keys; caller supplies approved label
   * values. Null/invalid contracts or inconsistent snapshots fail, never become fabricated zero
   * observations. Unselected meters are ignored. Empty namespaces/registries produce empty standard
   * text.
   */
  public String scrapeTimers(MeterRegistry source, Map<String, Set<String>> approvedNameLabelKeys) {
    return encode(
        source,
        approvedNameLabelKeys,
        PrometheusTextFormatWriter.builder().setIncludeCreatedTimestamps(false).build());
  }

  // Package-private checked-writer seam for SUMENC023/024, no retained injected mutable resource.
  static String encode(
      MeterRegistry source,
      Map<String, Set<String>> approvedNameLabelKeys,
      ExpositionFormatWriter writer) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(writer, "text writer");
    var support = new WebMetricText();
    var namespace = support.namespace(approvedNameLabelKeys, "nk_[a-z][a-z0-9_]*_seconds", "timer");
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var groups = new TreeMap<String, List<HistogramDataPointSnapshot>>();
    for (var meter : source.getMeters()) {
      var id = Objects.requireNonNull(meter, "meter").getId();
      String name = Objects.requireNonNull(id.getName(), "metric name");
      var keys = namespace.get(name);
      if (keys == null) continue;
      if (!(meter instanceof Timer timer))
        throw new IllegalArgumentException("selected meter is not a timer");
      groups
          .computeIfAbsent(name, unused -> new ArrayList<>())
          .add(point(timer, support.labels(id, keys)));
    }
    var families =
        groups.entrySet().stream()
            .<MetricSnapshot>map(
                entry ->
                    new io.prometheus.metrics.model.snapshots.HistogramSnapshot(
                        new MetricMetadata(entry.getKey()), entry.getValue()))
            .toList();
    return support.write(writer, new MetricSnapshots(families), "timer encoding failed");
  }

  private static HistogramDataPointSnapshot point(Timer timer, Labels labels) {
    HistogramSnapshot snapshot = Objects.requireNonNull(timer.takeSnapshot(), "summary snapshot");
    if (snapshot.count() < 0 || !Double.isFinite(snapshot.total()) || snapshot.total() < 0)
      throw new IllegalArgumentException("invalid timer totals");
    var cumulative = Objects.requireNonNull(snapshot.histogramCounts(), "summary buckets");
    if (cumulative.length == 0) throw new IllegalArgumentException("missing summary buckets");
    var bounds = new double[cumulative.length + 1];
    var intervals = new long[cumulative.length + 1];
    double previousBound = 0;
    long previousCount = 0;
    for (int index = 0; index < cumulative.length; index++) {
      var bucket = Objects.requireNonNull(cumulative[index], "summary bucket");
      double bound = bucket.bucket() / 1_000_000_000.;
      double count = bucket.count();
      // CDF counts are binary64. Reject ambiguous integer precision, never round/clamp it silently.
      if (!Double.isFinite(bound)
          || bound <= previousBound
          || !Double.isFinite(count)
          || count < previousCount
          || Double.compare(count, Math.rint(count)) != 0
          || count >= 0x1.0p53
          || count > snapshot.count())
        throw new IllegalArgumentException("invalid cumulative summary bucket");
      long exactCount = (long) count;
      bounds[index] = bound;
      intervals[index] = exactCount - previousCount;
      previousBound = bound;
      previousCount = exactCount;
    }
    bounds[cumulative.length] = Double.POSITIVE_INFINITY;
    intervals[cumulative.length] = snapshot.count() - previousCount;
    return new HistogramDataPointSnapshot(
        ClassicHistogramBuckets.of(bounds, intervals),
        snapshot.total() / 1_000_000_000.,
        labels,
        Exemplars.EMPTY,
        0);
  }
}
