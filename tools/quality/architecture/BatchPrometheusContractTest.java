package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.BatchPrometheusTextFixture.Key;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** BATCHPROM001..008/1749. Supplied synthetic observations, never backup/file/control authority. */
class BatchPrometheusContractTest {
  private static final String FILES = "nk_file_transfer_files";
  private static final String BYTES = "nk_file_transfer_bytes";
  private static final String INTEGRITY = "nk_integrity_failures_total";
  private static final String RUNS = "nk_batch_runs_total";
  private static final String LAST = "nk_batch_last_success_timestamp_seconds";
  private static final String RESTART = "nk_process_restarts_total";
  private static final Map<String, String> TYPES =
      Map.of(
          FILES, "gauge", BYTES, "gauge", INTEGRITY, "counter", RUNS, "counter", LAST, "gauge",
          RESTART, "counter");
  private static final List<String> STEPS =
      List.of(
          "BACKUP_DB",
          "BACKUP_CONFIG",
          "CLEAN_NOTIFICATION",
          "CLEAN_QUESTION",
          "CLEAN_SESSION",
          "CLEAN_INBOX_OUTBOX",
          "CLEAN_LOG",
          "CLEAN_BATCH_RUN",
          "CLEAN_TRANSFER",
          "CLEAN_EXPIRY");
  private static final List<String> STATUSES = List.of("SUCCESS", "WARNING", "FAILED", "SKIPPED");
  private static final List<String> SERVICES =
      List.of("WEB", "API", "BATCH", "BROKER", "DB", "CADDY");
  private static final List<String> REASONS =
      List.of("NONZERO_EXIT", "SIGNAL_EXIT", "OOM", "UNKNOWN");
  private static final Instant AT = Instant.parse("1970-01-01T00:00:07.500000Z");

  private static final class Bundle implements AutoCloseable {
    final BatchPrometheusTextFixture registry = new BatchPrometheusTextFixture();
    final TransferMetricRecorder transfer;
    final IntegrityFailureMetricRecorder integrity;
    final BatchMetricRecorder batch;
    final ProcessRestartMetricRecorder restart;
    final boolean debug;

    Bundle(String mode) {
      debug = mode.equals("DEBUG");
      transfer = new TransferMetricRecorder(registry, mode);
      integrity = new IntegrityFailureMetricRecorder(registry, mode);
      batch = new BatchMetricRecorder(registry, mode);
      restart = new ProcessRestartMetricRecorder(registry, mode);
    }

    Map<Key, Double> text() {
      var actual =
          registry.text(List.of(transfer, integrity, batch, restart), debug ? TYPES : Map.of());
      if (debug) assertEquals(keys(), actual.keySet());
      else assertTrue(actual.isEmpty());
      return actual;
    }

    @Override
    public void close() {
      registry.close();
    }
  }

  private static Set<Key> keys() {
    var keys = new HashSet<Key>();
    for (String suffix : List.of(".part", ".ready")) {
      keys.add(new Key(FILES, Map.of("suffix", suffix)));
      keys.add(new Key(BYTES, Map.of("suffix", suffix)));
    }
    for (String area : List.of("HASH", "PATH", "CONFIG"))
      for (String step : STEPS) keys.add(new Key(INTEGRITY, Map.of("area", area, "step", step)));
    for (String step : STEPS) {
      for (String status : STATUSES)
        keys.add(new Key(RUNS, Map.of("step", step, "status", status)));
      keys.add(new Key(LAST, Map.of("step", step)));
    }
    for (String service : SERVICES)
      for (String reason : REASONS)
        keys.add(new Key(RESTART, Map.of("service", service, "reason", reason)));
    return Set.copyOf(keys);
  }

  private static double value(Map<Key, Double> actual, String name, Map<String, String> labels) {
    var result = actual.get(new Key(name, labels));
    assertNotNull(result);
    return result;
  }

  private static void supply(Bundle b) {
    b.transfer.record(
        new TransferMetricRecorder.Usage(
            new TransferMetricRecorder.Counts(3, 11), new TransferMetricRecorder.Counts(5, 13)));
    b.integrity.record(IntegrityFailureMetricRecorder.Area.CONFIG, BatchStep.BACKUP_DB);
    b.batch.record(BatchMetricContract.Step.BACKUP_DB, BatchMetricContract.Status.SUCCESS, AT);
    b.restart.record(ProcessRestartMetricRecorder.Reason.UNKNOWN, AlertLifecycle.Service.BATCH);
  }

  @Test
  void batchprom001SixFamiliesAndAllOneHundredEightClosedSamplesAreIndependent() {
    try (var b = new Bundle("DEBUG")) {
      var actual = b.text();
      assertEquals(108, actual.size());
      assertEquals(14, actual.values().stream().filter(v -> Double.isNaN(v)).count());
      assertEquals(94, actual.values().stream().filter(v -> v == 0).count());
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void batchprom002TransferKnownZeroMissingAndMaximumNeverWalkOrDeleteFiles() {
    try (var b = new Bundle("DEBUG")) {
      supply(b);
      var actual = b.text();
      assertEquals(3, value(actual, FILES, Map.of("suffix", ".part")));
      assertEquals(11, value(actual, BYTES, Map.of("suffix", ".part")));
      assertEquals(5, value(actual, FILES, Map.of("suffix", ".ready")));
      assertEquals(13, value(actual, BYTES, Map.of("suffix", ".ready")));
      b.transfer.record(
          new TransferMetricRecorder.Usage(
              new TransferMetricRecorder.Counts(0, 0), new TransferMetricRecorder.Counts(0, 0)));
      assertEquals(0, value(b.text(), FILES, Map.of("suffix", ".part")));
      b.transfer.missing();
      assertTrue(Double.isNaN(value(b.text(), FILES, Map.of("suffix", ".part"))));
      b.transfer.record(
          new TransferMetricRecorder.Usage(
              new TransferMetricRecorder.Counts(Long.MAX_VALUE, 0),
              new TransferMetricRecorder.Counts(0, 0)));
      assertEquals(9.223372036854776E18, value(b.text(), FILES, Map.of("suffix", ".part")));
    }
  }

  @Test
  void batchprom003ThirtySuppliedIntegrityPairsEachCountExactlyOnce() {
    try (var b = new Bundle("DEBUG")) {
      for (String area : List.of("HASH", "PATH", "CONFIG"))
        for (String step : STEPS)
          b.integrity.record(
              IntegrityFailureMetricRecorder.Area.valueOf(area), BatchStep.valueOf(step));
      var actual = b.text();
      for (String area : List.of("HASH", "PATH", "CONFIG"))
        for (String step : STEPS)
          assertEquals(1, value(actual, INTEGRITY, Map.of("area", area, "step", step)));
      assertEquals(0, value(actual, RUNS, Map.of("step", "BACKUP_DB", "status", "SUCCESS")));
    }
  }

  @Test
  void batchprom004FortyTerminalCountsAndTenSuccessTimesHaveLiteralEpochs() {
    try (var b = new Bundle("DEBUG")) {
      for (String step : STEPS)
        for (String status : STATUSES)
          b.batch.record(
              BatchMetricContract.Step.valueOf(step),
              BatchMetricContract.Status.valueOf(status),
              AT);
      var actual = b.text();
      for (String step : STEPS) {
        for (String status : STATUSES)
          assertEquals(1, value(actual, RUNS, Map.of("step", step, "status", status)));
        assertEquals(7.5, value(actual, LAST, Map.of("step", step)));
      }
      b.batch.record(
          BatchMetricContract.Step.BACKUP_DB,
          BatchMetricContract.Status.FAILED,
          Instant.ofEpochSecond(100));
      b.batch.record(
          BatchMetricContract.Step.BACKUP_DB,
          BatchMetricContract.Status.SUCCESS,
          Instant.ofEpochSecond(1));
      assertEquals(7.5, value(b.text(), LAST, Map.of("step", "BACKUP_DB")));
      b.batch.record(
          BatchMetricContract.Step.BACKUP_DB,
          BatchMetricContract.Status.SUCCESS,
          Instant.parse("1970-01-01T00:00:13.000001Z"));
      assertEquals(13.000001, value(b.text(), LAST, Map.of("step", "BACKUP_DB")));
      try (var boundary = new Bundle("DEBUG")) {
        boundary.batch.record(
            BatchMetricContract.Step.BACKUP_CONFIG,
            BatchMetricContract.Status.SUCCESS,
            Instant.parse("0001-01-01T00:00:00Z"));
        assertEquals(-62135596800.0, value(boundary.text(), LAST, Map.of("step", "BACKUP_CONFIG")));
      }
      b.batch.record(
          BatchMetricContract.Step.BACKUP_DB,
          BatchMetricContract.Status.SUCCESS,
          Instant.parse("9999-12-31T23:59:59.999999Z"));
      assertEquals(253402300800.0, value(b.text(), LAST, Map.of("step", "BACKUP_DB")));
    }
  }

  @Test
  void batchprom005TwentyFourSuppliedRestartsNeverOperateAProcess() {
    try (var b = new Bundle("DEBUG")) {
      for (String service : SERVICES)
        for (String reason : REASONS)
          b.restart.record(
              ProcessRestartMetricRecorder.Reason.valueOf(reason),
              AlertLifecycle.Service.valueOf(service));
      var actual = b.text();
      for (String service : SERVICES)
        for (String reason : REASONS)
          assertEquals(1, value(actual, RESTART, Map.of("service", service, "reason", reason)));
      assertEquals(0, value(actual, INTEGRITY, Map.of("area", "CONFIG", "step", "BACKUP_DB")));
    }
  }

  @Test
  void batchprom006StandardPublishesRetainsAndClosesNothing() {
    try (var b = new Bundle("STANDARD")) {
      supply(b);
      b.transfer.missing();
      assertTrue(b.text().isEmpty());
      assertTrue(b.transfer.snapshot().isEmpty());
      assertTrue(b.registry.getMeters().isEmpty());
      assertEquals(0, b.registry.closes.get());
    }
  }

  @Test
  void batchprom007FiniteOwnedWorkersHaveExactCountsAndSeparateOwners() throws Exception {
    try (var b = new Bundle("DEBUG");
        var other = new Bundle("DEBUG")) {
      var pool = Executors.newFixedThreadPool(4);
      try {
        var futures = new ArrayList<java.util.concurrent.Future<?>>();
        for (int n = 0; n < 64; n++) futures.add(pool.submit(() -> supply(b)));
        for (var f : futures) f.get(5, TimeUnit.SECONDS);
        var actual = b.text();
        assertEquals(64, value(actual, INTEGRITY, Map.of("area", "CONFIG", "step", "BACKUP_DB")));
        assertEquals(64, value(actual, RUNS, Map.of("step", "BACKUP_DB", "status", "SUCCESS")));
        assertEquals(64, value(actual, RESTART, Map.of("service", "BATCH", "reason", "UNKNOWN")));
        assertEquals(7.5, value(actual, LAST, Map.of("step", "BACKUP_DB")));
        assertEquals(108, b.registry.getMeters().size());
        assertEquals(
            0, value(other.text(), RUNS, Map.of("step", "BACKUP_DB", "status", "SUCCESS")));
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void batchprom008GeneratedValuesUseIndependentTypedVectorsHashAndText() {
    var actual = new TransferMetricRecorder.Counts(3, 11);
    Object absent = null;
    Object other = "not counts";
    assertTrue(actual.equals(actual));
    assertTrue(actual.equals(new TransferMetricRecorder.Counts(3, 11)));
    assertFalse(actual.equals(absent));
    assertFalse(actual.equals(other));
    assertFalse(actual.equals(new TransferMetricRecorder.Counts(4, 11)));
    assertFalse(actual.equals(new TransferMetricRecorder.Counts(3, 12)));
    assertEquals(3, actual.files());
    assertEquals(11, actual.bytes());
    assertEquals(104, actual.hashCode());
    assertEquals("Counts[files=3, bytes=11]", actual.toString());
    assertEquals(TransferMetricRecorder.Suffix.PART, TransferMetricRecorder.Suffix.valueOf("PART"));
    assertEquals(
        TransferMetricRecorder.Suffix.READY, TransferMetricRecorder.Suffix.valueOf("READY"));
    assertThrows(NullPointerException.class, () -> TransferMetricRecorder.Suffix.valueOf(null));
    assertThrows(
        IllegalArgumentException.class, () -> TransferMetricRecorder.Suffix.valueOf("unknown"));
    var suffixCopy = TransferMetricRecorder.Suffix.values();
    suffixCopy[0] = TransferMetricRecorder.Suffix.READY;
    assertEquals(TransferMetricRecorder.Suffix.PART, TransferMetricRecorder.Suffix.values()[0]);
    var expectedSteps =
        List.of(
            BatchMetricContract.Step.BACKUP_DB,
            BatchMetricContract.Step.BACKUP_CONFIG,
            BatchMetricContract.Step.CLEAN_NOTIFICATION,
            BatchMetricContract.Step.CLEAN_QUESTION,
            BatchMetricContract.Step.CLEAN_SESSION,
            BatchMetricContract.Step.CLEAN_INBOX_OUTBOX,
            BatchMetricContract.Step.CLEAN_LOG,
            BatchMetricContract.Step.CLEAN_BATCH_RUN,
            BatchMetricContract.Step.CLEAN_TRANSFER,
            BatchMetricContract.Step.CLEAN_EXPIRY);
    for (int n = 0; n < 10; n++)
      assertEquals(expectedSteps.get(n), BatchMetricContract.Step.valueOf(STEPS.get(n)));
    var expectedStatuses =
        List.of(
            BatchMetricContract.Status.SUCCESS,
            BatchMetricContract.Status.WARNING,
            BatchMetricContract.Status.FAILED,
            BatchMetricContract.Status.SKIPPED);
    for (int n = 0; n < 4; n++)
      assertEquals(expectedStatuses.get(n), BatchMetricContract.Status.valueOf(STATUSES.get(n)));
    assertThrows(NullPointerException.class, () -> BatchMetricContract.Step.valueOf(null));
    assertThrows(IllegalArgumentException.class, () -> BatchMetricContract.Step.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> BatchMetricContract.Status.valueOf(null));
    assertThrows(
        IllegalArgumentException.class, () -> BatchMetricContract.Status.valueOf("unknown"));
    var steps = BatchMetricContract.Step.values();
    steps[0] = BatchMetricContract.Step.CLEAN_LOG;
    var statuses = BatchMetricContract.Status.values();
    statuses[0] = BatchMetricContract.Status.SKIPPED;
    assertEquals(BatchMetricContract.Step.BACKUP_DB, BatchMetricContract.Step.values()[0]);
    assertEquals(BatchMetricContract.Status.SUCCESS, BatchMetricContract.Status.values()[0]);
  }
}
