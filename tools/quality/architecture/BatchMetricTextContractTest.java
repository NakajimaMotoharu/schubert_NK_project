package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.repository.BatchStep;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.io.OutputStream;
import java.lang.ref.Reference;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** BATCHWIRE001..008/1777: real supplied memory observations, fixed public syntax parser only. */
class BatchMetricTextContractTest {
  private static final String RUNS = "nk_batch_runs_total",
      SUCCESS = "nk_batch_last_success_timestamp_seconds",
      FILES = "nk_file_transfer_files",
      BYTES = "nk_file_transfer_bytes",
      INTEGRITY = "nk_integrity_failures_total",
      RESTARTS = "nk_process_restarts_total";
  private static final Path PROMTOOL =
      Path.of("/home/mini/codex/project1/work/toolchain/promtool-3.13.5-linux-amd64/promtool");
  private static final Path PREPARATION =
      Path.of(
          "/home/mini/codex/project1/work/pgpt-foundation/evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG8162-promtool-prepare-v1/manifest.json");
  private final BatchMetricText formatter = new BatchMetricText();

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    Registry() {
      super(SimpleConfig.DEFAULT, new MockClock());
    }
  }

  private static final class Bundle implements AutoCloseable {
    final Registry registry = new Registry();
    final BatchMetricRecorder batch = new BatchMetricRecorder(registry, "DEBUG");
    final TransferMetricRecorder transfer = new TransferMetricRecorder(registry, "DEBUG");
    final IntegrityFailureMetricRecorder integrity =
        new IntegrityFailureMetricRecorder(registry, "DEBUG");
    final ProcessRestartMetricRecorder restart =
        new ProcessRestartMetricRecorder(registry, "DEBUG");

    void supplied() {
      batch.record(
          BatchMetricContract.Step.BACKUP_DB,
          BatchMetricContract.Status.SUCCESS,
          Instant.ofEpochSecond(10, 500_000_000));
      batch.record(
          BatchMetricContract.Step.BACKUP_DB,
          BatchMetricContract.Status.WARNING,
          Instant.ofEpochSecond(11));
      transfer.record(
          new TransferMetricRecorder.Usage(
              new TransferMetricRecorder.Counts(3, 100),
              new TransferMetricRecorder.Counts(5, 200)));
      integrity.record(IntegrityFailureMetricRecorder.Area.HASH, BatchStep.BACKUP_DB);
      restart.record(ProcessRestartMetricRecorder.Reason.OOM, AlertLifecycle.Service.API);
      restart.record(ProcessRestartMetricRecorder.Reason.OOM, AlertLifecycle.Service.API);
    }

    String text(BatchMetricText target, String mode) {
      try {
        return target.scrape(registry, mode);
      } finally {
        Reference.reachabilityFence(this);
      }
    }

    public void close() {
      registry.close();
    }
  }

  private static double value(String text, String name, Map<String, String> labels) {
    var rows =
        text.lines()
            .filter(line -> line.startsWith(name + "{"))
            .filter(
                line ->
                    labels.entrySet().stream()
                        .allMatch(e -> line.contains(e.getKey() + "=\"" + e.getValue() + "\"")))
            .toList();
    assertEquals(1, rows.size());
    String row = rows.getFirst();
    return Double.parseDouble(row.substring(row.lastIndexOf(' ') + 1));
  }

  private static void catalog(String text) {
    var expected =
        Map.of(
            RUNS, "counter", SUCCESS, "gauge", FILES, "gauge", BYTES, "gauge", INTEGRITY, "counter",
            RESTARTS, "counter");
    var types = text.lines().filter(line -> line.startsWith("# TYPE ")).toList();
    assertEquals(6, types.size());
    expected.forEach((name, type) -> assertTrue(types.contains("# TYPE " + name + " " + type)));
    assertEquals(6, text.lines().filter(line -> line.startsWith("# HELP ")).count());
    assertEquals(108, text.lines().filter(line -> !line.startsWith("#")).count());
    assertFalse(text.contains("_total_total"));
    assertFalse(text.contains("nk_inbox_replays_total"));
  }

  private static void supplied(String text) {
    catalog(text);
    assertEquals(1, value(text, RUNS, Map.of("step", "BACKUP_DB", "status", "SUCCESS")));
    assertEquals(1, value(text, RUNS, Map.of("step", "BACKUP_DB", "status", "WARNING")));
    assertEquals(10.5, value(text, SUCCESS, Map.of("step", "BACKUP_DB")));
    assertEquals(3, value(text, FILES, Map.of("suffix", ".part")));
    assertEquals(5, value(text, FILES, Map.of("suffix", ".ready")));
    assertEquals(100, value(text, BYTES, Map.of("suffix", ".part")));
    assertEquals(200, value(text, BYTES, Map.of("suffix", ".ready")));
    assertEquals(1, value(text, INTEGRITY, Map.of("area", "HASH", "step", "BACKUP_DB")));
    assertEquals(2, value(text, RESTARTS, Map.of("service", "API", "reason", "OOM")));
    assertEquals(9, text.lines().filter(line -> line.endsWith("} NaN")).count());
  }

  @Test
  void batchwire001RealSimpleInitialSixFamilies108Samples() {
    try (var b = new Bundle()) {
      String result = b.text(formatter, "DEBUG");
      catalog(result);
      assertEquals(14, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(94, result.lines().filter(line -> line.endsWith("} 0.0")).count());
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void batchwire002LiteralSuppliedSixFamilyValues() {
    try (var b = new Bundle()) {
      b.supplied();
      supplied(b.text(formatter, "DEBUG"));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void batchwire003StandardDoesNotClearOrCloseDetailedObservations() {
    try (var b = new Bundle()) {
      b.supplied();
      supplied(b.text(formatter, "DEBUG"));
      assertEquals("", b.text(formatter, "STANDARD"));
      supplied(b.text(formatter, "DEBUG"));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void batchwire004MissingAndKnownZeroAreDistinct() {
    try (var b = new Bundle()) {
      b.supplied();
      b.transfer.missing();
      String missing = b.text(formatter, "DEBUG");
      assertTrue(Double.isNaN(value(missing, FILES, Map.of("suffix", ".part"))));
      assertTrue(Double.isNaN(value(missing, BYTES, Map.of("suffix", ".ready"))));
      b.transfer.record(
          new TransferMetricRecorder.Usage(
              new TransferMetricRecorder.Counts(0, 0), new TransferMetricRecorder.Counts(0, 0)));
      String zero = b.text(formatter, "DEBUG");
      assertEquals(0, value(zero, FILES, Map.of("suffix", ".part")));
      assertEquals(0, value(zero, BYTES, Map.of("suffix", ".ready")));
      catalog(zero);
    }
  }

  @Test
  void batchwire005NonSuccessAndOldSuccessNeverAdvanceTimestamp() {
    try (var b = new Bundle()) {
      var step = BatchMetricContract.Step.BACKUP_DB;
      b.batch.record(
          step, BatchMetricContract.Status.SUCCESS, Instant.ofEpochSecond(10, 500_000_000));
      b.batch.record(step, BatchMetricContract.Status.WARNING, Instant.ofEpochSecond(11));
      b.batch.record(step, BatchMetricContract.Status.FAILED, Instant.ofEpochSecond(12));
      b.batch.record(step, BatchMetricContract.Status.SKIPPED, Instant.ofEpochSecond(13));
      String first = b.text(formatter, "DEBUG");
      assertEquals(10.5, value(first, SUCCESS, Map.of("step", "BACKUP_DB")));
      for (String status : List.of("SUCCESS", "WARNING", "FAILED", "SKIPPED"))
        assertEquals(1, value(first, RUNS, Map.of("step", "BACKUP_DB", "status", status)));
      b.batch.record(
          step, BatchMetricContract.Status.SUCCESS, Instant.ofEpochSecond(9, 500_000_000));
      String old = b.text(formatter, "DEBUG");
      assertEquals(10.5, value(old, SUCCESS, Map.of("step", "BACKUP_DB")));
      assertEquals(2, value(old, RUNS, Map.of("step", "BACKUP_DB", "status", "SUCCESS")));
    }
  }

  @Test
  void batchwire006FiniteConcurrentSuppliedEventsAndScrapes() throws Exception {
    try (var b = new Bundle();
        var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++)
        jobs.add(
            workers.submit(
                () ->
                    b.restart.record(
                        ProcessRestartMetricRecorder.Reason.OOM, AlertLifecycle.Service.API)));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      String result = b.text(formatter, "DEBUG");
      catalog(result);
      assertEquals(64, value(result, RESTARTS, Map.of("service", "API", "reason", "OOM")));
      assertFalse(b.registry.isClosed());
    }
  }

  @Test
  void batchwire007SeparateOwnersAndUnknownProvidersRemainIndependent() {
    try (var first = new Bundle();
        var other = new Bundle()) {
      first.supplied();
      var reads = new AtomicInteger();
      Gauge.builder(
              "nk_unknown_fixture",
              reads,
              ref -> {
                ref.incrementAndGet();
                throw new AssertionError("unselected");
              })
          .register(other.registry);
      supplied(first.text(formatter, "DEBUG"));
      String result = other.text(formatter, "DEBUG");
      catalog(result);
      assertEquals(0, value(result, RESTARTS, Map.of("service", "API", "reason", "OOM")));
      assertEquals(14, result.lines().filter(line -> line.endsWith("} NaN")).count());
      assertEquals(0, reads.get());
      assertFalse(result.contains("nk_unknown_fixture"));
      assertFalse(other.registry.isClosed());
    }
  }

  private static String digest(Path path) throws Exception {
    var md = MessageDigest.getInstance("SHA-256");
    try (var stream = new DigestInputStream(Files.newInputStream(path), md)) {
      stream.transferTo(OutputStream.nullOutputStream());
    }
    return HexFormat.of().formatHex(md.digest());
  }

  private static int parser(String input) throws Exception {
    byte[] bytes = input.getBytes(StandardCharsets.UTF_8);
    var builder =
        new ProcessBuilder(PROMTOOL.toString(), "check", "metrics").redirectErrorStream(true);
    builder.environment().clear();
    builder.environment().put("PATH", "/usr/bin:/bin");
    builder.environment().put("LANG", "C.UTF-8");
    var process = builder.start();
    try {
      try (var stdin = process.getOutputStream()) {
        stdin.write(bytes);
      }
      boolean done = process.waitFor(30, TimeUnit.SECONDS);
      if (!done) {
        process.destroyForcibly();
        assertTrue(process.waitFor(10, TimeUnit.SECONDS));
        fail("owned parser timeout, never PASS");
      }
      byte[] output = process.getInputStream().readNBytes(16384);
      assertTrue(output.length < 16384, "bounded own public parser output");
      int code = process.exitValue();
      var md = MessageDigest.getInstance("SHA-256");
      System.out.println(
          "BATCHWIRE008 command=promtool check metrics; stdinSHA256="
              + HexFormat.of().formatHex(md.digest(bytes))
              + "; actualExit="
              + code
              + "; outputSHA256="
              + HexFormat.of().formatHex(md.digest(output))
              + "; timeUTC="
              + Instant.now());
      return code;
    } finally {
      if (process.isAlive()) {
        process.destroyForcibly();
        assertTrue(process.waitFor(10, TimeUnit.SECONDS));
      }
      process.getInputStream().close();
      process.getErrorStream().close();
    }
  }

  @Test
  void batchwire008OfficialPinnedParserAcceptsActualTextAndRejectsIndependentMalformedLiteral()
      throws Exception {
    assertFalse(Files.isSymbolicLink(PROMTOOL));
    assertTrue(Files.isRegularFile(PROMTOOL, LinkOption.NOFOLLOW_LINKS));
    assertEquals(
        "4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff", digest(PROMTOOL));
    assertEquals(
        "ca3c93186503b91ff14183b1759b7c8b1e0e33fc73d16685974a8ebd2a01ecae", digest(PREPARATION));
    try (var b = new Bundle()) {
      b.supplied();
      String valid = b.text(formatter, "DEBUG");
      supplied(valid);
      assertEquals(0, parser(valid));
      assertNotEquals(
          0,
          parser(
              "# HELP fixture Invalid numeric literal.\n# TYPE fixture gauge\nfixture definitely_not_a_number\n"));
      assertFalse(b.registry.isClosed());
    }
    assertEquals(
        "4e84296dc89ef03d856674d76d387f5ccc54a698136c2f0dc30ceef2286908ff", digest(PROMTOOL));
  }
}
