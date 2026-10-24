package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.prometheus.metrics.config.EscapingScheme;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.expositionformats.PrometheusTextFormatWriter;
import io.prometheus.metrics.model.snapshots.CounterSnapshot;
import io.prometheus.metrics.model.snapshots.CounterSnapshot.CounterDataPointSnapshot;
import io.prometheus.metrics.model.snapshots.GaugeSnapshot;
import io.prometheus.metrics.model.snapshots.GaugeSnapshot.GaugeDataPointSnapshot;
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

/** NK-OPS-001/RD171/UI252/SS351/1771: API-owned scalar text, never a registry/resource owner. */
public final class ApiScalarMetricExporter {
  public ApiScalarMetricExporter() {}

  /** Caller supplies approved names/keys/values; borrowed source is never closed. */
  public String scrapeCounters(MeterRegistry source, Map<String, Set<String>> approved) {
    return encodeCounters(
        source,
        approved,
        PrometheusTextFormatWriter.builder().setIncludeCreatedTimestamps(false).build());
  }

  /** Gauge NaN is an explicit unknown observation, not a substitute for null or failure. */
  public String scrapeGauges(MeterRegistry source, Map<String, Set<String>> approved) {
    return encodeGauges(
        source,
        approved,
        PrometheusTextFormatWriter.builder().setIncludeCreatedTimestamps(false).build());
  }

  // SCALAR019/020: package-private checked-writer seams, no injected resource retained.
  static String encodeCounters(
      MeterRegistry source, Map<String, Set<String>> approved, ExpositionFormatWriter writer) {
    var namespace = prepare(source, approved, writer, "nk_[a-z][a-z0-9_]*_total");
    var groups = new TreeMap<String, List<CounterDataPointSnapshot>>();
    for (var meter : source.getMeters()) {
      var id = Objects.requireNonNull(meter, "meter").getId();
      String name = Objects.requireNonNull(id.getName(), "metric name");
      var keys = namespace.get(name);
      if (keys == null) continue;
      if (!(meter instanceof Counter counter))
        throw new IllegalArgumentException("selected meter is not a counter");
      var labels = labels(id, keys);
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
    return write(writer, families);
  }

  static String encodeGauges(
      MeterRegistry source, Map<String, Set<String>> approved, ExpositionFormatWriter writer) {
    var namespace = prepare(source, approved, writer, "nk_[a-z][a-z0-9_]*");
    var groups = new TreeMap<String, List<GaugeDataPointSnapshot>>();
    for (var meter : source.getMeters()) {
      var id = Objects.requireNonNull(meter, "meter").getId();
      String name = Objects.requireNonNull(id.getName(), "metric name");
      var keys = namespace.get(name);
      if (keys == null) continue;
      if (!(meter instanceof Gauge gauge))
        throw new IllegalArgumentException("selected meter is not a gauge");
      var labels = labels(id, keys);
      double value = gauge.value();
      groups
          .computeIfAbsent(name, unused -> new ArrayList<>())
          .add(GaugeDataPointSnapshot.builder().value(value).labels(labels).build());
    }
    var families =
        groups.entrySet().stream()
            .<MetricSnapshot>map(
                entry -> new GaugeSnapshot(new MetricMetadata(entry.getKey()), entry.getValue()))
            .toList();
    return write(writer, families);
  }

  private static Map<String, Set<String>> prepare(
      MeterRegistry source,
      Map<String, Set<String>> approved,
      ExpositionFormatWriter writer,
      String pattern) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(writer, "text writer");
    var result = new HashMap<String, Set<String>>();
    Objects.requireNonNull(approved, "approved metric namespace")
        .forEach(
            (name, keys) -> {
              if (!Objects.requireNonNull(name, "metric name").matches(pattern))
                throw new IllegalArgumentException("invalid scalar namespace");
              var copy = Set.copyOf(keys);
              for (var key : copy)
                if (!key.matches("[a-z][a-z0-9_]*") || "le".equals(key))
                  throw new IllegalArgumentException("invalid scalar label namespace");
              result.put(name, copy);
            });
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    return result;
  }

  private static Labels labels(Meter.Id id, Set<String> keys) {
    var result = new TreeMap<String, String>();
    for (var tag : id.getTags()) {
      Objects.requireNonNull(tag, "metric tag");
      String key = Objects.requireNonNull(tag.getKey(), "metric label key");
      String value = Objects.requireNonNull(tag.getValue(), "metric label value");
      if (result.put(key, value) != null)
        throw new IllegalArgumentException("duplicate scalar label");
    }
    if (!result.keySet().equals(keys))
      throw new IllegalArgumentException("scalar label contract mismatch");
    return Labels.of(new ArrayList<>(result.keySet()), new ArrayList<>(result.values()));
  }

  private static String write(ExpositionFormatWriter writer, List<MetricSnapshot> families) {
    var output = new ByteArrayOutputStream();
    try {
      writer.write(output, new MetricSnapshots(families), EscapingScheme.UNDERSCORE_ESCAPING);
    } catch (IOException failure) {
      throw new UncheckedIOException("scalar encoding failed", failure);
    }
    return output.toString(StandardCharsets.UTF_8);
  }
}
