package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.ValueAtPercentile;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** TIMERENC001..016/1757: literal ns snapshots, independent wire values and no private access. */
class WebDurationMetricExporterTest {
  private static final String NAME = "nk_http_request_duration_seconds";
  private static final Map<String, Set<String>> SPACE = Map.of(NAME, Set.of("service", "route"));
  private final WebDurationMetricExporter exporter = new WebDurationMetricExporter();

  private static HistogramSnapshot snapshot(long count, double total, CountAtBucket... buckets) {
    return new HistogramSnapshot(count, total, 0, new ValueAtPercentile[0], buckets, null);
  }

  private static HistogramSnapshot valid() {
    return snapshot(
        2, 50_000_001, new CountAtBucket(50_000_000.0, 2), new CountAtBucket(1_000_000_000.0, 2));
  }

  private static class FixedTimer implements Timer {
    final HistogramSnapshot snapshot;
    final Meter.Id id;
    final AtomicInteger reads = new AtomicInteger();

    FixedTimer(HistogramSnapshot snapshot, String route) {
      this.snapshot = snapshot;
      id =
          new Meter.Id(
              NAME, Tags.of("service", "WEB", "route", route), "seconds", "", Meter.Type.TIMER);
    }

    public Meter.Id getId() {
      return id;
    }

    public HistogramSnapshot takeSnapshot() {
      reads.incrementAndGet();
      return snapshot;
    }

    public void record(long amount, TimeUnit unit) {
      throw new AssertionError("no record");
    }

    public <T> T record(Supplier<T> action) {
      throw new AssertionError("no supplier");
    }

    public <T> T recordCallable(Callable<T> action) {
      throw new AssertionError("no callable");
    }

    public void record(Runnable action) {
      throw new AssertionError("no runnable");
    }

    public long count() {
      throw new AssertionError("non-atomic count forbidden");
    }

    public double totalTime(TimeUnit unit) {
      throw new AssertionError("non-atomic total forbidden");
    }

    public double max(TimeUnit unit) {
      throw new AssertionError("max not exported");
    }

    public TimeUnit baseTimeUnit() {
      return TimeUnit.NANOSECONDS;
    }
  }

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<Meter> supplied;

    Registry(Meter... meters) {
      supplied = List.of(meters);
    }

    public List<Meter> getMeters() {
      return supplied;
    }
  }

  private static class OrdinaryRegistry extends SimpleMeterRegistry implements AutoCloseable {}

  private String text(HistogramSnapshot snapshot) {
    try (var source = new Registry(new FixedTimer(snapshot, "/login"))) {
      return exporter.scrapeTimers(source, SPACE);
    }
  }

  private void invalid(HistogramSnapshot snapshot) {
    assertThrows(IllegalArgumentException.class, () -> text(snapshot));
  }

  @Test
  void timerenc001LiteralNanosecondsBecomeSecondsNotSummaryUnit() {
    String text = text(valid());
    assertTrue(text.contains("# TYPE " + NAME + " histogram\n"));
    assertTrue(text.contains("le=\"0.05\"} 2\n"));
    assertTrue(text.contains("le=\"1.0\"} 2\n"));
    assertTrue(text.contains("le=\"+Inf\"} 2\n"));
    assertTrue(text.contains("_sum{route=\"/login\",service=\"WEB\"} 0.050000001\n"));
    assertEquals(6, text.lines().count());
  }

  @Test
  void timerenc002OneNanosecondAndTwoLongMaximumSumStayPositive() {
    assertTrue(
        text(snapshot(1, 1, new CountAtBucket(50_000_000.0, 1)))
            .contains("_sum{route=\"/login\",service=\"WEB\"} 1.0E-9\n"));
    String large = text(snapshot(2, 1.8446744073709552E19, new CountAtBucket(50_000_000.0, 0)));
    assertTrue(large.contains("_sum{route=\"/login\",service=\"WEB\"} 1.8446744073709553E10\n"));
    assertTrue(large.contains("le=\"+Inf\"} 2\n"));
  }

  @Test
  void timerenc003NineLiteralBoundariesAreSecondsOnWire() {
    var buckets =
        new CountAtBucket[] {
          new CountAtBucket(50_000_000.0, 0),
          new CountAtBucket(100_000_000.0, 0),
          new CountAtBucket(250_000_000.0, 0),
          new CountAtBucket(500_000_000.0, 0),
          new CountAtBucket(1_000_000_000.0, 0),
          new CountAtBucket(1_500_000_000.0, 0),
          new CountAtBucket(2_000_000_000.0, 0),
          new CountAtBucket(2_500_000_000.0, 0),
          new CountAtBucket(5_000_000_000.0, 0)
        };
    String result = text(snapshot(0, 0, buckets));
    for (String bound :
        List.of("0.05", "0.1", "0.25", "0.5", "1.0", "1.5", "2.0", "2.5", "5.0", "+Inf"))
      assertTrue(result.contains("le=\"" + bound + "\"} 0\n"));
    assertEquals(13, result.lines().count());
  }

  @Test
  void timerenc004MultipleSeriesRetainLabelsAndEscaping() {
    try (var source =
        new Registry(new FixedTimer(valid(), "/login"), new FixedTimer(valid(), "a\"b\\c\nd"))) {
      String result = exporter.scrapeTimers(source, SPACE);
      assertEquals(2, result.lines().filter(line -> line.startsWith(NAME + "_sum{")).count());
      assertTrue(result.contains("route=\"a\\\"b\\\\c\\nd\""));
    }
  }

  @Test
  void timerenc005SummaryAndCounterCannotBecomeTimerByNaming() {
    try (var source = new OrdinaryRegistry()) {
      source.summary(NAME, "service", "WEB", "route", "/login");
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeTimers(source, SPACE));
    }
    try (var source = new OrdinaryRegistry()) {
      source.counter(NAME, "service", "WEB", "route", "/login");
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeTimers(source, SPACE));
    }
  }

  @Test
  void timerenc006NullRegistryNamespaceAndSnapshotFail() {
    assertThrows(NullPointerException.class, () -> exporter.scrapeTimers(null, SPACE));
    try (var source = new Registry(new FixedTimer(valid(), "/login"))) {
      assertThrows(NullPointerException.class, () -> exporter.scrapeTimers(source, null));
    }
    assertThrows(NullPointerException.class, () -> text(null));
  }

  @Test
  void timerenc007RawNegativeAndNonFiniteTotalsAreNotNormalizedAfterConversion() {
    invalid(snapshot(-1, 0, new CountAtBucket(1.0, 0)));
    for (double total :
        new double[] {
          -Double.MIN_VALUE, -1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY
        }) invalid(snapshot(1, total, new CountAtBucket(1.0, 0)));
  }

  @Test
  void timerenc008ConvertedZeroInvalidOrderOrNonFiniteBoundFails() {
    for (double bound :
        new double[] {Double.MIN_VALUE, 0, -1, Double.NaN, Double.POSITIVE_INFINITY})
      invalid(snapshot(1, 1, new CountAtBucket(bound, 0)));
    invalid(snapshot(1, 1, new CountAtBucket(2.0, 0), new CountAtBucket(1.0, 0)));
    invalid(snapshot(1, 1));
    assertThrows(
        NullPointerException.class, () -> text(snapshot(1, 1, new CountAtBucket[] {null})));
  }

  @Test
  void timerenc009CountUnitsAreNeverScaledAndInvalidCdfFails() {
    for (double count :
        new double[] {-1, .5, Double.NaN, Double.POSITIVE_INFINITY, 3, 9007199254740992.0})
      invalid(snapshot(2, 1, new CountAtBucket(1_000_000_000.0, count)));
    invalid(snapshot(2, 1, new CountAtBucket(1.0, 2), new CountAtBucket(2.0, 1)));
  }

  @Test
  void timerenc010EmptyNamespaceUnknownGaugeAndZeroTimerAreDistinct() {
    try (var source = new OrdinaryRegistry()) {
      source.gauge("unselected", 42);
      assertEquals("", exporter.scrapeTimers(source, SPACE));
    }
    try (var source = new Registry(new FixedTimer(valid(), "/login"))) {
      assertEquals("", exporter.scrapeTimers(source, Map.of()));
    }
    assertTrue(
        text(snapshot(0, 0, new CountAtBucket(1_000_000_000.0, 0))).contains("le=\"+Inf\"} 0\n"));
  }

  @Test
  void timerenc011BorrowedOwnerNotClosedAndClosedRegistryRejected() {
    var source = new Registry(new FixedTimer(valid(), "/login"));
    try {
      exporter.scrapeTimers(source, SPACE);
      assertFalse(source.isClosed());
    } finally {
      source.close();
    }
    assertThrows(IllegalStateException.class, () -> exporter.scrapeTimers(source, SPACE));
  }

  @Test
  void timerenc012ExactlyOneAtomicSnapshotNoOtherTimerScalarReads() {
    var timer = new FixedTimer(valid(), "/login");
    try (var source = new Registry(timer)) {
      assertTrue(exporter.scrapeTimers(source, SPACE).contains("le=\"+Inf\"} 2\n"));
      assertEquals(1, timer.reads.get());
    }
  }

  @Test
  void timerenc013RuntimeFailureIdentityAndOwnerAreRetained() {
    var failure = new IllegalStateException("fixture");
    var timer =
        new FixedTimer(valid(), "/login") {
          public HistogramSnapshot takeSnapshot() {
            throw failure;
          }
        };
    try (var source = new Registry(timer)) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> exporter.scrapeTimers(source, SPACE)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void timerenc014ProviderErrorIsNotCaughtAsSuccess() {
    var failure = new AssertionError("fixture");
    var timer =
        new FixedTimer(valid(), "/login") {
          public HistogramSnapshot takeSnapshot() {
            throw failure;
          }
        };
    try (var source = new Registry(timer)) {
      assertSame(
          failure, assertThrows(AssertionError.class, () -> exporter.scrapeTimers(source, SPACE)));
    }
  }

  @Test
  void timerenc015CallerNamespaceAndKeysAreCopiedBeforeProviderRead() {
    var keys = new HashSet<>(Set.of("service", "route"));
    var space = new HashMap<String, Set<String>>();
    space.put(NAME, keys);
    var timer =
        new FixedTimer(valid(), "/login") {
          public HistogramSnapshot takeSnapshot() {
            keys.clear();
            space.clear();
            return valid();
          }
        };
    try (var source = new Registry(timer)) {
      assertTrue(exporter.scrapeTimers(source, space).contains("le=\"+Inf\"} 2\n"));
      assertTrue(space.isEmpty());
      assertTrue(keys.isEmpty());
    }
  }

  @Test
  void timerenc016CheckedWriterFailureRetainsCauseAndBorrowedOwner() {
    var failure = new java.io.IOException("fixture");
    var writer =
        new io.prometheus.metrics.expositionformats.ExpositionFormatWriter() {
          public boolean accepts(String accept) {
            throw new AssertionError("no content negotiation");
          }

          public String getContentType() {
            throw new AssertionError("no HTTP endpoint");
          }

          public void write(
              java.io.OutputStream output,
              io.prometheus.metrics.model.snapshots.MetricSnapshots snapshots,
              io.prometheus.metrics.config.EscapingScheme scheme)
              throws java.io.IOException {
            throw failure;
          }
        };
    try (var source = new Registry(new FixedTimer(valid(), "/login"))) {
      var actual =
          assertThrows(
              java.io.UncheckedIOException.class,
              () -> WebDurationMetricExporter.encode(source, SPACE, writer));
      assertSame(failure, actual.getCause());
      assertEquals("timer encoding failed", actual.getMessage());
      assertFalse(source.isClosed());
    }
  }
}
