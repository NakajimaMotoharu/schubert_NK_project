package dev.codex.schubert.nk.batch.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.HashMap;
import java.util.Objects;
import java.util.TreeMap;
import java.util.stream.Collectors;

/**
 * NK-OPS-001/RD171/UI252/SS351/1777 BATCHTEXT: closed six-family scalar text, not a general-purpose
 * exporter or resource owner. Labels are fixed ASCII enums/suffixes, never arbitrary text to
 * escape.
 */
public final class BatchMetricText {
  private static final String HELP = "Supplied Batch technical observation.";
  private final BatchMetricLabelPolicy labels = new BatchMetricLabelPolicy();

  public BatchMetricText() {}

  /** 1833/PG-D624: both sources remain caller-owned; custom before standard, never partial text. */
  public String scrape(MeterRegistry source, String mode, BatchStandardMetricSource standard) {
    Objects.requireNonNull(standard, "standard metric owner");
    String custom = scrape(source, mode);
    if ("STANDARD".equals(mode)) return custom;
    return custom + Objects.requireNonNull(standard.scrape(mode), "standard metric text");
  }

  /**
   * STANDARD reads no detailed source; DEBUG returns no partial text after any provider failure.
   */
  public String scrape(MeterRegistry source, String mode) {
    Objects.requireNonNull(source, "meter registry");
    if (!MonitoringModePolicy.parse(mode).detailedMetricsEnabled()) return "";
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var types = new HashMap<String, MetricContract.Kind>();
    for (String name : labels.names(MetricContract.Kind.COUNTER).keySet())
      types.put(name, MetricContract.Kind.COUNTER);
    for (String name : labels.names(MetricContract.Kind.GAUGE).keySet())
      types.put(name, MetricContract.Kind.GAUGE);
    var groups = new TreeMap<String, TreeMap<String, String>>();
    for (var meter : Objects.requireNonNull(source.getMeters(), "source meters")) {
      var id =
          Objects.requireNonNull(Objects.requireNonNull(meter, "meter").getId(), "metric identity");
      String name = Objects.requireNonNull(id.getName(), "metric name");
      var kind = types.get(name);
      if (kind == null) continue;
      var values = labels.labels(name, id.getTags());
      String copiedLabels =
          new TreeMap<>(values)
              .entrySet().stream()
                  .map(entry -> entry.getKey() + "=\"" + entry.getValue() + "\"")
                  .collect(Collectors.joining(","));
      String key = name + "{" + copiedLabels + "}";
      String value = number(read(meter, kind));
      if (groups.computeIfAbsent(name, unused -> new TreeMap<>()).putIfAbsent(key, value) != null)
        throw new IllegalArgumentException("duplicate Batch metric series");
    }
    var result = new StringBuilder();
    groups.forEach(
        (name, samples) -> {
          result.append("# HELP ").append(name).append(' ').append(HELP).append('\n');
          result
              .append("# TYPE ")
              .append(name)
              .append(' ')
              .append(types.get(name) == MetricContract.Kind.COUNTER ? "counter" : "gauge")
              .append('\n');
          samples.forEach(
              (key, value) -> result.append(key).append(' ').append(value).append('\n'));
        });
    return result.toString();
  }

  private static double read(Meter meter, MetricContract.Kind kind) {
    if (kind == MetricContract.Kind.COUNTER) {
      if (!(meter instanceof Counter counter))
        throw new IllegalArgumentException("selected Batch metric is not a counter");
      double value = counter.count();
      if (!Double.isFinite(value) || value < 0)
        throw new IllegalArgumentException("invalid Batch counter value");
      return value;
    }
    if (!(meter instanceof Gauge gauge))
      throw new IllegalArgumentException("selected Batch metric is not a gauge");
    return gauge.value();
  }

  private static String number(double value) {
    if (Double.isNaN(value)) return "NaN";
    if (value == Double.POSITIVE_INFINITY) return "+Inf";
    if (value == Double.NEGATIVE_INFINITY) return "-Inf";
    return Double.toString(value);
  }
}
