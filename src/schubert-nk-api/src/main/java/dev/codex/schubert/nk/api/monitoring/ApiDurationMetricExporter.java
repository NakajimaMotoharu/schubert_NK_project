package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.prometheus.metrics.config.EscapingScheme;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.expositionformats.PrometheusTextFormatWriter;
import io.prometheus.metrics.model.snapshots.ClassicHistogramBuckets;
import io.prometheus.metrics.model.snapshots.Exemplars;
import io.prometheus.metrics.model.snapshots.HistogramSnapshot.HistogramDataPointSnapshot;
import io.prometheus.metrics.model.snapshots.Labels;
import io.prometheus.metrics.model.snapshots.MetricMetadata;
import io.prometheus.metrics.model.snapshots.MetricSnapshot;
import io.prometheus.metrics.model.snapshots.MetricSnapshots;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;

/**
 * NK-OPS-001/RD171/UI252/SS351/1753/1757/BUG1697: app-owned atomic summary snapshots to standard
 * histogram text. A borrowed source is never closed. No global exporter configuration, clock, file
 * or network reads.
 */
public final class ApiDurationMetricExporter {
  /** No resources acquired; the official writer is explicitly configured per scrape. */
  public ApiDurationMetricExporter() {}

  /**
   * Exports only approved seconds names with exact label keys; caller supplies approved label
   * values. Null/invalid contracts or inconsistent snapshots fail, never become fabricated zero
   * observations. Unselected meters are ignored. Empty namespaces/registries produce empty standard
   * text.
   */
  public String scrape(MeterRegistry source, Map<String, Set<String>> approvedNameLabelKeys) {
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
    var namespace = new HashMap<String, Set<String>>();
    Objects.requireNonNull(approvedNameLabelKeys, "approved metric namespace")
        .forEach(
            (name, keys) -> {
              if (!Objects.requireNonNull(name, "metric name")
                  .matches("nk_[a-z][a-z0-9_]*_seconds"))
                throw new IllegalArgumentException("invalid summary namespace");
              var copy = Set.copyOf(keys);
              for (var key : copy)
                if (!key.matches("[a-z][a-z0-9_]*") || "le".equals(key))
                  throw new IllegalArgumentException("invalid summary label namespace");
              namespace.put(name, copy);
            });
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var groups = new TreeMap<String, List<HistogramDataPointSnapshot>>();
    for (var meter : source.getMeters()) {
      var id = Objects.requireNonNull(meter, "meter").getId();
      String name = Objects.requireNonNull(id.getName(), "metric name");
      var keys = namespace.get(name);
      if (keys == null) continue;
      if (!(meter instanceof DistributionSummary summary))
        throw new IllegalArgumentException("selected meter is not a summary");
      groups
          .computeIfAbsent(name, unused -> new ArrayList<>())
          .add(point(summary, labels(id, keys)));
    }
    var families =
        groups.entrySet().stream()
            .<MetricSnapshot>map(
                entry ->
                    new io.prometheus.metrics.model.snapshots.HistogramSnapshot(
                        new MetricMetadata(entry.getKey()), entry.getValue()))
            .toList();
    var output = new ByteArrayOutputStream();
    try {
      writer.write(output, new MetricSnapshots(families), EscapingScheme.UNDERSCORE_ESCAPING);
    } catch (IOException failure) {
      throw new UncheckedIOException("summary encoding failed", failure);
    }
    return output.toString(StandardCharsets.UTF_8);
  }

  private static Labels labels(Meter.Id id, Set<String> expectedKeys) {
    var labels = new TreeMap<String, String>();
    for (var tag : id.getTags())
      if (labels.put(tag.getKey(), tag.getValue()) != null)
        throw new IllegalArgumentException("duplicate summary label");
    if (!labels.keySet().equals(expectedKeys))
      throw new IllegalArgumentException("summary label contract mismatch");
    return Labels.of(new ArrayList<>(labels.keySet()), new ArrayList<>(labels.values()));
  }

  private static HistogramDataPointSnapshot point(DistributionSummary summary, Labels labels) {
    HistogramSnapshot snapshot = Objects.requireNonNull(summary.takeSnapshot(), "summary snapshot");
    if (snapshot.count() < 0 || !Double.isFinite(snapshot.total()) || snapshot.total() < 0)
      throw new IllegalArgumentException("invalid summary totals");
    var cumulative = Objects.requireNonNull(snapshot.histogramCounts(), "summary buckets");
    if (cumulative.length == 0) throw new IllegalArgumentException("missing summary buckets");
    var bounds = new double[cumulative.length + 1];
    var intervals = new long[cumulative.length + 1];
    double previousBound = 0;
    long previousCount = 0;
    for (int index = 0; index < cumulative.length; index++) {
      var bucket = Objects.requireNonNull(cumulative[index], "summary bucket");
      double bound = bucket.bucket();
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
        snapshot.total(),
        labels,
        Exemplars.EMPTY,
        0);
  }
}
