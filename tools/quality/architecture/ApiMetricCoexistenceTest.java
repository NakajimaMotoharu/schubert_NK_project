package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.simple.SimpleConfig;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** APICOEX001..002/1797: standard and custom source coexistence, independent full-wire golden. */
class ApiMetricCoexistenceTest {
  private static final String INITIAL =
      "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 7.5\n# TYPE nk_inbox_replays_total counter\nnk_inbox_replays_total{layout=\"LGNREQ01\",result=\"0000\"} 2.5\n";
  private static final String UPDATED =
      "# TYPE nk_db_pool_connections gauge\nnk_db_pool_connections{service=\"API\",state=\"active\"} 9.5\n# TYPE nk_inbox_replays_total counter\nnk_inbox_replays_total{layout=\"LGNREQ01\",result=\"0000\"} 3.5\n";

  private static final class Bundle implements AutoCloseable {
    final ExactDurationMeterRegistry source =
        new ExactDurationMeterRegistry(SimpleConfig.DEFAULT, new MockClock());
    final List<JvmGcMetrics> gcs = new ArrayList<>();
    final double[] value = {7.5};

    Counter supplied(boolean standardFirst) {
      if (standardFirst) new ApiStandardMetrics().bind(source, "DEBUG", gcs::add);
      Gauge.builder("nk_db_pool_connections", value, values -> values[0])
          .tags("service", "API", "state", "active")
          .register(source);
      var counter =
          Counter.builder("nk_inbox_replays_total")
              .tags("layout", "LGNREQ01", "result", "0000")
              .register(source);
      counter.increment(2.5);
      if (!standardFirst) new ApiStandardMetrics().bind(source, "DEBUG", gcs::add);
      return counter;
    }

    String text(String mode) {
      try {
        return new ApiMetricScrape().scrape(source, mode);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      try {
        gcs.forEach(JvmGcMetrics::close);
      } finally {
        source.close();
      }
    }
  }

  @Test
  void apicoex001StandardFirstKeepsIndependentCustomWire() {
    try (var bundle = new Bundle()) {
      bundle.supplied(true);
      assertEquals(INITIAL, bundle.text("DEBUG"));
      assertEquals(1, bundle.gcs.size());
      assertNotNull(bundle.source.get("jvm.classes.loaded").gauge());
      assertEquals(
          Runtime.getRuntime().availableProcessors(),
          bundle.source.get("system.cpu.count").gauge().value());
      assertFalse(bundle.source.isClosed());
    }
  }

  @Test
  void apicoex002CustomFirstKeepsUpdatedValuesAndStandardModeEmpty() {
    try (var bundle = new Bundle()) {
      var counter = bundle.supplied(false);
      counter.increment(1.0);
      bundle.value[0] = 9.5;
      assertEquals("", bundle.text("STANDARD"));
      assertEquals(UPDATED, bundle.text("DEBUG"));
      assertEquals(1, bundle.gcs.size());
      assertNotNull(bundle.source.get("jvm.classes.loaded").gauge());
      assertFalse(bundle.source.isClosed());
    }
  }
}
