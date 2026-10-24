package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.MockClock;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import io.prometheus.metrics.model.registry.PrometheusRegistry;
import java.lang.ref.Reference;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Properties;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;
import org.jspecify.annotations.Nullable;

/** Test-only actual-text reader. Never builds expected values from product/SDK state. */
final class BatchPrometheusTextFixture extends PrometheusMeterRegistry implements AutoCloseable {
  final AtomicInteger closes = new AtomicInteger();
  private static final Pattern LINE = Pattern.compile("([a-z_]+)\\{([^{}]+)\\} (NaN|[-+0-9.eE]+)");
  private static final Pattern LABEL = Pattern.compile("([a-z_]+)=\"([A-Za-z0-9_.]+)\"");
  private static final PrometheusConfig CONFIG =
      new PrometheusConfig() {
        @Override
        public @Nullable String get(String key) {
          return null;
        }

        @Override
        public Properties prometheusProperties() {
          var p = new Properties();
          p.setProperty("io.prometheus.exporter.include_created_timestamps", "false");
          p.setProperty("io.prometheus.exporter.exemplars_on_all_metric_types", "false");
          return p;
        }
      };

  record Key(String name, Map<String, String> labels) {
    Key {
      name = Objects.requireNonNull(name);
      labels = Map.copyOf(labels);
    }
  }

  BatchPrometheusTextFixture() {
    super(CONFIG, new PrometheusRegistry(), new MockClock());
  }

  Map<Key, Double> text(List<Object> owners, Map<String, String> expectedTypes) {
    try {
      var actual = new HashMap<Key, Double>();
      var types = new HashMap<String, String>();
      for (String line : scrape().split("\n")) {
        if (line.isEmpty() || line.startsWith("# HELP ")) continue;
        if (line.startsWith("# TYPE ")) {
          var fields = line.split(" ");
          assertEquals(4, fields.length);
          assertNull(types.put(fields[2], fields[3]));
          continue;
        }
        var match = LINE.matcher(line);
        assertTrue(match.matches(), "closed label text without timestamp/exemplar");
        var labels = new HashMap<String, String>();
        for (String field : match.group(2).split(",")) {
          var label = LABEL.matcher(field);
          assertTrue(label.matches());
          assertNull(labels.put(label.group(1), label.group(2)));
        }
        assertNull(actual.put(new Key(match.group(1), labels), Double.valueOf(match.group(3))));
      }
      assertEquals(expectedTypes, types);
      return Map.copyOf(actual);
    } finally {
      Reference.reachabilityFence(owners);
    }
  }

  @Override
  public void close() {
    closes.incrementAndGet();
    super.close();
  }
}
