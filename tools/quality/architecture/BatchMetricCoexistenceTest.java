package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.lang.ref.Reference;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BATCHCOEX001..002/1797: standard and custom source coexistence, independent full-wire golden. */
class BatchMetricCoexistenceTest {
  private static final String INITIAL =
      "# HELP nk_batch_runs_total Supplied Batch technical observation.\n# TYPE nk_batch_runs_total counter\nnk_batch_runs_total{status=\"SUCCESS\",step=\"BACKUP_DB\"} 2.5\n# HELP nk_file_transfer_files Supplied Batch technical observation.\n# TYPE nk_file_transfer_files gauge\nnk_file_transfer_files{suffix=\".part\"} 7.5\n";
  private static final String UPDATED =
      "# HELP nk_batch_runs_total Supplied Batch technical observation.\n# TYPE nk_batch_runs_total counter\nnk_batch_runs_total{status=\"SUCCESS\",step=\"BACKUP_DB\"} 3.5\n# HELP nk_file_transfer_files Supplied Batch technical observation.\n# TYPE nk_file_transfer_files gauge\nnk_file_transfer_files{suffix=\".part\"} 9.5\n";

  private static final class Bundle implements AutoCloseable {
    final SimpleMeterRegistry source =
        new SimpleMeterRegistry(SimpleConfig.DEFAULT, new MockClock());
    final List<JvmGcMetrics> gcs = new ArrayList<>();
    final double[] value = {7.5};

    Counter supplied(boolean standardFirst) {
      if (standardFirst) new BatchStandardMetrics().bind(source, "DEBUG", gcs::add);
      Gauge.builder("nk_file_transfer_files", value, values -> values[0])
          .tags("suffix", ".part")
          .register(source);
      var counter =
          Counter.builder("nk_batch_runs_total")
              .tags("status", "SUCCESS", "step", "BACKUP_DB")
              .register(source);
      counter.increment(2.5);
      if (!standardFirst) new BatchStandardMetrics().bind(source, "DEBUG", gcs::add);
      return counter;
    }

    String text(String mode) {
      try {
        return new BatchMetricText().scrape(source, mode);
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
  void batchcoex001StandardFirstKeepsIndependentCustomWire() {
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
  void batchcoex002CustomFirstKeepsUpdatedValuesAndStandardModeEmpty() {
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
