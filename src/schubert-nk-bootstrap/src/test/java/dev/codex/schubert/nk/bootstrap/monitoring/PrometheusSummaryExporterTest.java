package dev.codex.schubert.nk.bootstrap.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.ValueAtPercentile;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.prometheus.metrics.config.EscapingScheme;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import io.prometheus.metrics.model.snapshots.MetricSnapshots;
import java.io.IOException;
import java.io.OutputStream;
import java.io.UncheckedIOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SUMENC001..024/1753: literal independent snapshots, no application/SDK expected generator. */
class PrometheusSummaryExporterTest {
  private static final String NAME = "nk_fixture_duration_seconds";
  private static final Map<String, Set<String>> SPACE = Map.of(NAME, Set.of("outcome"));
  private final PrometheusSummaryExporter exporter = new PrometheusSummaryExporter();

  private abstract static class FixtureWriter implements ExpositionFormatWriter {
    public boolean accepts(String accept) {
      throw new AssertionError("no content negotiation");
    }

    public String getContentType() {
      throw new AssertionError("not an HTTP endpoint");
    }
  }

  private static HistogramSnapshot snapshot(long count, double total, CountAtBucket... buckets) {
    return new HistogramSnapshot(count, total, 0, new ValueAtPercentile[0], buckets, null);
  }

  private static HistogramSnapshot valid() {
    return snapshot(3, 1.002, new CountAtBucket(.001, 1), new CountAtBucket(1.0, 2));
  }

  // A provider double, not an expected-value implementation. The exporter must takeSnapshot once.
  private static class Summary implements DistributionSummary {
    final HistogramSnapshot snapshot;
    final Meter.Id id;
    final AtomicInteger calls = new AtomicInteger();

    Summary(HistogramSnapshot snapshot, Meter.Id id) {
      this.snapshot = snapshot;
      this.id = id;
    }

    public Meter.Id getId() {
      return id;
    }

    public HistogramSnapshot takeSnapshot() {
      calls.incrementAndGet();
      return snapshot;
    }

    public void record(double value) {
      throw new AssertionError("export must not record");
    }

    public long count() {
      throw new AssertionError("non-atomic count forbidden");
    }

    public double totalAmount() {
      throw new AssertionError("non-atomic sum forbidden");
    }

    public double max() {
      throw new AssertionError("max not exported");
    }
  }

  private static Meter.Id id(String name, String value) {
    return new Meter.Id(
        name, Tags.of("outcome", value), "seconds", "", Meter.Type.DISTRIBUTION_SUMMARY);
  }

  private static class CloseableRegistry extends SimpleMeterRegistry implements AutoCloseable {}

  private static class Registry extends CloseableRegistry {
    final List<Meter> supplied;

    Registry(Meter... meters) {
      supplied = List.of(meters);
    }

    public List<Meter> getMeters() {
      return supplied;
    }
  }

  private String text(HistogramSnapshot snapshot) {
    try (var source = new Registry(new Summary(snapshot, id(NAME, "SUCCESS")))) {
      return exporter.scrape(source, SPACE);
    }
  }

  private void rejects(HistogramSnapshot snapshot) {
    assertThrows(IllegalArgumentException.class, () -> text(snapshot));
  }

  @Test
  void sumenc001LiteralCdfBecomesClassicHistogram() {
    assertEquals(
        Set.copyOf(
            """
        # TYPE nk_fixture_duration_seconds histogram
        nk_fixture_duration_seconds_bucket{outcome="SUCCESS",le="0.001"} 1
        nk_fixture_duration_seconds_bucket{outcome="SUCCESS",le="1.0"} 2
        nk_fixture_duration_seconds_bucket{outcome="SUCCESS",le="+Inf"} 3
        nk_fixture_duration_seconds_count{outcome="SUCCESS"} 3
        nk_fixture_duration_seconds_sum{outcome="SUCCESS"} 1.002
        """
                .lines()
                .toList()),
        Set.copyOf(text(valid()).lines().toList()));
  }

  @Test
  void sumenc002ZeroAndNanosecondSumAreNotIntegerTruncated() {
    String zero = text(snapshot(0, 0, new CountAtBucket(.001, 0)));
    assertTrue(zero.contains("_sum{outcome=\"SUCCESS\"} 0.0\n"));
    assertTrue(zero.contains("le=\"+Inf\"} 0\n"));
    assertTrue(
        text(snapshot(1, .000000001, new CountAtBucket(.001, 1)))
            .contains("_sum{outcome=\"SUCCESS\"} 1.0E-9\n"));
  }

  @Test
  void sumenc003LabelsAreEscapedByOfficialWriter() {
    try (var source = new Registry(new Summary(valid(), id(NAME, "a\"b\\c\nd")))) {
      assertTrue(exporter.scrape(source, SPACE).contains("outcome=\"a\\\"b\\\\c\\nd\""));
    }
  }

  @Test
  void sumenc004FamiliesAndMultipleSeriesAreNotLost() {
    try (var source =
        new Registry(
            new Summary(valid(), id(NAME, "SUCCESS")),
            new Summary(valid(), id(NAME, "FAILURE")),
            new Summary(valid(), id("nk_other_seconds", "ONE")))) {
      String result =
          exporter.scrape(
              source, Map.of(NAME, Set.of("outcome"), "nk_other_seconds", Set.of("outcome")));
      assertEquals(3, result.lines().filter(line -> line.contains("_sum{")).count());
      assertEquals(2, result.lines().filter(line -> line.startsWith("# TYPE")).count());
    }
  }

  @Test
  void sumenc005EmptyAndUnselectedMetersAreNotFabricated() {
    try (var source = new Registry(new Summary(valid(), id("nk_other_seconds", "ONE")))) {
      assertEquals("", exporter.scrape(source, SPACE));
      assertEquals("", exporter.scrape(source, Map.of()));
    }
    try (var source = new CloseableRegistry()) {
      assertEquals("", exporter.scrape(source, SPACE));
    }
  }

  @Test
  void sumenc006SelectedWrongMeterTypeFails() {
    try (var source = new CloseableRegistry()) {
      source.counter(NAME, "outcome", "SUCCESS");
      assertThrows(IllegalArgumentException.class, () -> exporter.scrape(source, SPACE));
    }
  }

  @Test
  void sumenc007NamespaceAndLabelContractsRejectUnknownValues() {
    try (var source = new Registry(new Summary(valid(), id(NAME, "SUCCESS")))) {
      for (String name : List.of("", "nk_bad_total", "x_seconds", "nk_X_seconds"))
        assertThrows(
            IllegalArgumentException.class, () -> exporter.scrape(source, Map.of(name, Set.of())));
      for (String key : List.of("", "le", "Bad", "bad-key"))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrape(source, Map.of(NAME, Set.of(key))));
      assertThrows(
          IllegalArgumentException.class, () -> exporter.scrape(source, Map.of(NAME, Set.of())));
      assertThrows(
          IllegalArgumentException.class,
          () -> exporter.scrape(source, Map.of(NAME, Set.of("extra", "outcome"))));
    }
  }

  @Test
  void sumenc008NullBoundaryAndCollectionElementsFail() {
    try (var source = new CloseableRegistry()) {
      assertThrows(NullPointerException.class, () -> exporter.scrape(null, SPACE));
      assertThrows(NullPointerException.class, () -> exporter.scrape(source, null));
      assertThrows(
          NullPointerException.class, () -> PrometheusSummaryExporter.encode(source, SPACE, null));
      var space = new HashMap<String, Set<String>>();
      space.put(null, Set.of());
      assertThrows(NullPointerException.class, () -> exporter.scrape(source, space));
      space.clear();
      space.put(NAME, null);
      assertThrows(NullPointerException.class, () -> exporter.scrape(source, space));
      var keys = new HashSet<String>();
      keys.add(null);
      space.put(NAME, keys);
      assertThrows(NullPointerException.class, () -> exporter.scrape(source, space));
    }
  }

  @Test
  void sumenc009NegativeTotalCountAndInvalidSumFail() {
    rejects(snapshot(-1, 0, new CountAtBucket(1.0, 0)));
    for (double sum :
        new double[] {-1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY})
      rejects(snapshot(1, sum, new CountAtBucket(1.0, 0)));
  }

  @Test
  void sumenc010EmptyBucketsFail() {
    rejects(snapshot(0, 0));
  }

  @Test
  void sumenc011NonFiniteAndNonPositiveBoundsFail() {
    for (double bound :
        new double[] {0, -1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY})
      rejects(snapshot(0, 0, new CountAtBucket(bound, 0)));
  }

  @Test
  void sumenc012UnsortedAndDuplicateBoundsFail() {
    rejects(snapshot(1, 1, new CountAtBucket(1.0, 0), new CountAtBucket(.5, 0)));
    rejects(snapshot(1, 1, new CountAtBucket(1.0, 0), new CountAtBucket(1.0, 0)));
  }

  @Test
  void sumenc013NonFiniteNegativeAndFractionalCdfFail() {
    for (double count :
        new double[] {-1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY, .5})
      rejects(snapshot(2, 1, new CountAtBucket(1.0, count)));
  }

  @Test
  void sumenc014DecreasingAndAboveTotalCdfFail() {
    rejects(snapshot(2, 1, new CountAtBucket(.5, 2), new CountAtBucket(1.0, 1)));
    rejects(snapshot(2, 1, new CountAtBucket(1.0, 3)));
  }

  @Test
  void sumenc015Binary64FiniteCdfAmbiguityFailsWithoutClamping() {
    rejects(snapshot(Long.MAX_VALUE, 1, new CountAtBucket(1.0, 9007199254740992.0)));
    assertTrue(
        text(snapshot(9007199254740991L, 1, new CountAtBucket(1.0, 9007199254740991.0)))
            .contains("le=\"1.0\"} 9007199254740991\n"));
  }

  @Test
  void sumenc016LongTotalCountAndExtremePositiveSumRemainPositive() {
    String result =
        text(snapshot(Long.MAX_VALUE, 1.8446744073709553E10, new CountAtBucket(1.0, 0)));
    assertTrue(result.contains("_count{outcome=\"SUCCESS\"} 9223372036854775807\n"));
    assertTrue(result.contains("le=\"+Inf\"} 9223372036854775807\n"));
    assertTrue(result.contains("_sum{outcome=\"SUCCESS\"} 1.8446744073709553E10\n"));
  }

  @Test
  void sumenc017SnapshotIsTakenExactlyOnce() {
    var summary = new Summary(valid(), id(NAME, "SUCCESS"));
    try (var source = new Registry(summary)) {
      assertTrue(exporter.scrape(source, SPACE).contains("_count{outcome=\"SUCCESS\"} 3\n"));
      assertEquals(1, summary.calls.get());
    }
  }

  @Test
  void sumenc018BorrowedRegistryNeverClosedAndClosedInputRejected() {
    var source = new Registry(new Summary(valid(), id(NAME, "SUCCESS")));
    try {
      exporter.scrape(source, SPACE);
      assertFalse(source.isClosed());
    } finally {
      source.close();
    }
    assertThrows(IllegalStateException.class, () -> exporter.scrape(source, SPACE));
  }

  @Test
  void sumenc019ProviderRuntimeFailureIdentityIsPreserved() {
    var failure = new IllegalStateException("fixture");
    var summary =
        new Summary(valid(), id(NAME, "SUCCESS")) {
          public HistogramSnapshot takeSnapshot() {
            throw failure;
          }
        };
    try (var source = new Registry(summary)) {
      assertSame(
          failure, assertThrows(IllegalStateException.class, () -> exporter.scrape(source, SPACE)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void sumenc020NullSnapshotAndBucketRejected() {
    assertThrows(NullPointerException.class, () -> text(null));
    assertThrows(
        NullPointerException.class, () -> text(snapshot(1, 1, new CountAtBucket[] {null})));
  }

  @Test
  void sumenc021EmptyLabelSetAndMutableCallerNamespace() {
    var map = new HashMap<String, Set<String>>();
    var labels = new HashSet<String>();
    map.put(NAME, labels);
    var summary =
        new Summary(
            valid(),
            new Meter.Id(NAME, Tags.empty(), "seconds", "", Meter.Type.DISTRIBUTION_SUMMARY));
    try (var source = new Registry(summary)) {
      assertTrue(exporter.scrape(source, map).contains("_count 3\n"));
      assertTrue(map.get(NAME).isEmpty());
      labels.add("outcome");
      assertThrows(IllegalArgumentException.class, () -> exporter.scrape(source, map));
    }
  }

  @Test
  void sumenc022DuplicateProviderLabelRejected() {
    Meter.Id duplicate =
        new Meter.Id(NAME, Tags.empty(), "seconds", "", Meter.Type.DISTRIBUTION_SUMMARY) {
          public List<Tag> getTags() {
            return List.of(Tag.of("outcome", "SUCCESS"), Tag.of("outcome", "FAILURE"));
          }
        };
    try (var source = new Registry(new Summary(valid(), duplicate))) {
      assertThrows(IllegalArgumentException.class, () -> exporter.scrape(source, SPACE));
    }
  }

  @Test
  void sumenc023CheckedWriterFailureRetainsCauseAndConstantMessage() {
    var failure = new IOException("fixture");
    var writer =
        new FixtureWriter() {
          public void write(OutputStream output, MetricSnapshots metrics, EscapingScheme scheme)
              throws IOException {
            throw failure;
          }
        };
    try (var source = new Registry(new Summary(valid(), id(NAME, "SUCCESS")))) {
      var actual =
          assertThrows(
              UncheckedIOException.class,
              () -> PrometheusSummaryExporter.encode(source, SPACE, writer));
      assertSame(failure, actual.getCause());
      assertEquals("summary encoding failed", actual.getMessage());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void sumenc024WriterErrorIsNotCaughtOrNormalized() {
    var failure = new AssertionError("fixture");
    var writer =
        new FixtureWriter() {
          public void write(OutputStream output, MetricSnapshots metrics, EscapingScheme scheme) {
            throw failure;
          }
        };
    try (var source = new Registry(new Summary(valid(), id(NAME, "SUCCESS")))) {
      assertSame(
          failure,
          assertThrows(
              AssertionError.class, () -> PrometheusSummaryExporter.encode(source, SPACE, writer)));
    }
  }
}
