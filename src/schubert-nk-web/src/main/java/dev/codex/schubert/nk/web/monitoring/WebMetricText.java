package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.Meter;
import io.prometheus.metrics.config.EscapingScheme;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.model.snapshots.Labels;
import io.prometheus.metrics.model.snapshots.MetricSnapshots;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;

/** NK-OPS-001/RD171/UI252/SS351/1759: stateless text support owned only by Web. */
final class WebMetricText {
  WebMetricText() {}

  Map<String, Set<String>> namespace(
      Map<String, Set<String>> approved, String namePattern, String kind) {
    var namespace = new HashMap<String, Set<String>>();
    Objects.requireNonNull(approved, "approved metric namespace")
        .forEach(
            (name, keys) -> {
              if (!Objects.requireNonNull(name, "metric name").matches(namePattern))
                throw new IllegalArgumentException("invalid " + kind + " namespace");
              var copy = Set.copyOf(keys);
              for (var key : copy)
                if (!key.matches("[a-z][a-z0-9_]*") || "le".equals(key))
                  throw new IllegalArgumentException("invalid " + kind + " label namespace");
              namespace.put(name, copy);
            });
    return namespace;
  }

  Labels labels(Meter.Id id, Set<String> expectedKeys) {
    var labels = new TreeMap<String, String>();
    for (var tag : id.getTags())
      if (labels.put(tag.getKey(), tag.getValue()) != null)
        throw new IllegalArgumentException("duplicate summary label");
    if (!labels.keySet().equals(expectedKeys))
      throw new IllegalArgumentException("summary label contract mismatch");
    return Labels.of(new ArrayList<>(labels.keySet()), new ArrayList<>(labels.values()));
  }

  String write(ExpositionFormatWriter writer, MetricSnapshots families, String failureMessage) {
    var output = new ByteArrayOutputStream();
    try {
      writer.write(output, families, EscapingScheme.UNDERSCORE_ESCAPING);
    } catch (IOException failure) {
      throw new UncheckedIOException(failureMessage, failure);
    }
    return output.toString(StandardCharsets.UTF_8);
  }
}
