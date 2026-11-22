package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.noop.NoopCounter;
import io.micrometer.core.instrument.noop.NoopDistributionSummary;
import io.micrometer.core.instrument.noop.NoopGauge;
import io.micrometer.core.instrument.noop.NoopTimer;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SCALAR001..024/1771: literal vectors and public SDK stubs, no hidden source/clock/network. */
class ApiScalarMetricExporterTest {
  private static final String LAYOUT_LABEL = "layout";
  private static final String RESULT_LABEL = "result";
  private static final String STORE_LABEL = "store";
  private static final String STATUS_LABEL = "status";
  private static final String SUCCESS_RESULT_CODE = "0000";
  private static final String API_SERVICE_VALUE = "API";
  private static final String PROVIDER_FAILURE_MARKER = "fixture";
  private static final String C = "nk_inbox_replays_total";
  private static final String G = "nk_outbox_rows";
  private static final Map<String, Set<String>> CS = Map.of(C, Set.of(LAYOUT_LABEL, RESULT_LABEL));
  private static final Map<String, Set<String>> GS = Map.of(G, Set.of(STORE_LABEL, STATUS_LABEL));
  private final ApiScalarMetricExporter exporter = new ApiScalarMetricExporter();

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<Meter> supplied;

    Registry(Meter... meters) {
      super(SimpleConfig.DEFAULT, new MockClock());
      supplied = List.of(meters);
    }

    public List<Meter> getMeters() {
      return supplied;
    }
  }

  private static Meter.Id raw(String capturedName, List<Tag> capturedTags) {
    return new Meter.Id("safe_fixture", Tags.empty(), "", "", Meter.Type.GAUGE) {
      public String getName() {
        return capturedName;
      }

      public List<Tag> getTags() {
        return capturedTags;
      }
    };
  }

  private static Meter.Id cid() {
    return raw(
        C, List.of(Tag.of(LAYOUT_LABEL, "LGNREQ01"), Tag.of(RESULT_LABEL, SUCCESS_RESULT_CODE)));
  }

  private static Meter.Id gid() {
    return raw(G, List.of(Tag.of(STORE_LABEL, API_SERVICE_VALUE), Tag.of(STATUS_LABEL, "PENDING")));
  }

  private static Tag nullableTag(String capturedKey, String capturedValue) {
    return new Tag() {
      public String getKey() {
        return capturedKey;
      }

      public String getValue() {
        return capturedValue;
      }

      public int compareTo(Tag other) {
        throw new AssertionError("no provider sort");
      }
    };
  }

  private static NoopCounter counter(double value) {
    return new NoopCounter(cid()) {
      public double count() {
        return value;
      }
    };
  }

  private static NoopGauge gauge(double value) {
    return new NoopGauge(gid()) {
      public double value() {
        return value;
      }
    };
  }

  private String counterText(double value) {
    try (var source = new Registry(counter(value))) {
      return exporter.scrapeCounters(source, CS);
    }
  }

  private String gaugeText(double value) {
    try (var source = new Registry(gauge(value))) {
      return exporter.scrapeGauges(source, GS);
    }
  }

  private static ExpositionFormatWriter broken(IOException failure) {
    return new ExpositionFormatWriter() {
      public boolean accepts(String accept) {
        throw new AssertionError("no content negotiation");
      }

      public String getContentType() {
        throw new AssertionError("no endpoint");
      }

      public void write(
          java.io.OutputStream output,
          io.prometheus.metrics.model.snapshots.MetricSnapshots snapshots,
          io.prometheus.metrics.config.EscapingScheme scheme)
          throws IOException {
        throw failure;
      }
    };
  }

  @Test
  void scalar001LiteralCounterNameAndFraction() {
    assertEquals(
        "# TYPE nk_inbox_replays_total counter\n"
            + "nk_inbox_replays_total{layout=\"LGNREQ01\",result=\"0000\"} 2.5\n",
        counterText(2.5));
  }

  @Test
  void scalar002GaugeUnknownZeroNegativeAndInfinityArePreserved() {
    assertTrue(gaugeText(Double.NaN).endsWith("} NaN\n"));
    assertTrue(gaugeText(0).endsWith("} 0.0\n"));
    assertTrue(gaugeText(-1).endsWith("} -1.0\n"));
    assertTrue(gaugeText(Double.POSITIVE_INFINITY).endsWith("} +Inf\n"));
    assertTrue(gaugeText(Double.NEGATIVE_INFINITY).endsWith("} -Inf\n"));
  }

  @Test
  void scalar003FiniteCounterExtremesRemainExact() {
    assertTrue(counterText(0).endsWith("} 0.0\n"));
    assertTrue(counterText(Double.MIN_VALUE).endsWith("} 4.9E-324\n"));
    assertTrue(counterText(Double.MAX_VALUE).endsWith("} 1.7976931348623157E308\n"));
  }

  @Test
  void scalar004InvalidCounterIsNeverClamped() {
    for (double value :
        new double[] {
          -Double.MIN_VALUE, -1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY
        }) assertThrows(IllegalArgumentException.class, () -> counterText(value));
  }

  @Test
  void scalar005EmptyAndUnselectedAreNotFabricatedZero() {
    try (var source = new Registry()) {
      assertEquals("", exporter.scrapeCounters(source, CS));
      assertEquals("", exporter.scrapeGauges(source, GS));
    }
    var unknown =
        new NoopGauge(raw("nk_unknown", List.of())) {
          public double value() {
            throw new AssertionError("not selected");
          }
        };
    try (var source = new Registry(unknown)) {
      assertEquals("", exporter.scrapeCounters(source, CS));
      assertEquals("", exporter.scrapeGauges(source, GS));
    }
    try (var source = new Registry(counter(1), gauge(1))) {
      assertEquals("", exporter.scrapeCounters(source, Map.of()));
      assertEquals("", exporter.scrapeGauges(source, Map.of()));
    }
  }

  @Test
  void scalar006SelectedWrongMeterTypesFailBothPaths() {
    for (Meter meter :
        List.of(new NoopGauge(cid()), new NoopTimer(cid()), new NoopDistributionSummary(cid())))
      try (var source = new Registry(meter)) {
        assertThrows(IllegalArgumentException.class, () -> exporter.scrapeCounters(source, CS));
      }
    for (Meter meter :
        List.of(new NoopCounter(gid()), new NoopTimer(gid()), new NoopDistributionSummary(gid())))
      try (var source = new Registry(meter)) {
        assertThrows(IllegalArgumentException.class, () -> exporter.scrapeGauges(source, GS));
      }
  }

  @Test
  void scalar007NullApiBoundariesAreNotUnknownObservations() {
    assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(null, CS));
    assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(null, GS));
    try (var source = new Registry()) {
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, null));
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, null));
      assertThrows(
          NullPointerException.class,
          () -> ApiScalarMetricExporter.encodeCounters(source, CS, null));
      assertThrows(
          NullPointerException.class, () -> ApiScalarMetricExporter.encodeGauges(source, GS, null));
    }
  }

  @Test
  void scalar008NullNamespaceNameSetOrElementFails() {
    try (var source = new Registry()) {
      var invalid = new HashMap<String, Set<String>>();
      invalid.put(null, Set.of());
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, invalid));
      invalid.clear();
      invalid.put(C, null);
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, invalid));
      var keys = new HashSet<String>();
      keys.add(null);
      invalid.put(C, keys);
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, invalid));
    }
    try (var source = new Registry(new NoopGauge(raw(null, List.of())))) {
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, GS));
    }
  }

  @Test
  void scalar009InvalidNamesAndCounterSuffixFail() {
    try (var source = new Registry()) {
      for (String name : List.of("bad_total", "nk_BAD_total", "nk_wrong_seconds"))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeCounters(source, Map.of(name, Set.of())));
      for (String name : List.of("bad", "nk_BAD"))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeGauges(source, Map.of(name, Set.of())));
    }
  }

  @Test
  void scalar010InvalidMissingExtraLabelsFail() {
    try (var source = new Registry(counter(1), gauge(1))) {
      for (String key : List.of("le", "bad-key"))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeCounters(source, Map.of(C, Set.of(key))));
      assertThrows(
          IllegalArgumentException.class,
          () -> exporter.scrapeCounters(source, Map.of(C, Set.of(LAYOUT_LABEL))));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              exporter.scrapeGauges(source, Map.of(G, Set.of(STORE_LABEL, STATUS_LABEL, "extra"))));
    }
    var nullTags = new ArrayList<Tag>();
    nullTags.add(null);
    try (var source = new Registry(new NoopGauge(raw(G, nullTags)))) {
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, GS));
    }
    for (var tag : List.of(nullableTag(null, API_SERVICE_VALUE), nullableTag(STORE_LABEL, null)))
      try (var source = new Registry(new NoopGauge(raw(G, List.of(tag))))) {
        assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, GS));
      }
  }

  @Test
  void scalar011DuplicateTagFixtureActuallyContainsDuplicate() {
    var tags =
        List.of(
            Tag.of(LAYOUT_LABEL, "LGNREQ01"),
            Tag.of(LAYOUT_LABEL, "LGNRSP01"),
            Tag.of(RESULT_LABEL, SUCCESS_RESULT_CODE));
    var duplicateIdentity = raw(C, tags);
    assertSame(tags, duplicateIdentity.getTags());
    assertEquals(
        List.of(LAYOUT_LABEL, LAYOUT_LABEL, RESULT_LABEL),
        duplicateIdentity.getTags().stream().map(Tag::getKey).toList());
    try (var source = new Registry(new NoopCounter(duplicateIdentity))) {
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeCounters(source, CS));
    }
  }

  @Test
  void scalar012LiteralLabelEscapingRemainsLossless() {
    var encoded =
        new NoopGauge(
            raw(
                G,
                List.of(
                    Tag.of(STORE_LABEL, API_SERVICE_VALUE), Tag.of(STATUS_LABEL, "a\"b\\c\nd"))));
    try (var source = new Registry(encoded)) {
      assertTrue(exporter.scrapeGauges(source, GS).contains("status=\"a\\\"b\\\\c\\nd\""));
    }
  }

  @Test
  void scalar013BorrowedSourceIsNotClosedAndClosedSourceFails() {
    var source = new Registry(counter(1), gauge(1));
    try {
      exporter.scrapeCounters(source, CS);
      exporter.scrapeGauges(source, GS);
      assertFalse(source.isClosed());
      source.close();
      assertThrows(IllegalStateException.class, () -> exporter.scrapeCounters(source, CS));
      assertThrows(IllegalStateException.class, () -> exporter.scrapeGauges(source, GS));
    } finally {
      source.close();
    }
  }

  @Test
  void scalar014NamespaceDeepCopyPrecedesProviderMutation() {
    var keys = new HashSet<>(Set.of(LAYOUT_LABEL, RESULT_LABEL));
    var space = new HashMap<String, Set<String>>();
    space.put(C, keys);
    var first =
        new NoopCounter(cid()) {
          public double count() {
            space.clear();
            keys.clear();
            return 2;
          }
        };
    var second =
        new NoopCounter(
            raw(
                C,
                List.of(
                    Tag.of(LAYOUT_LABEL, "LGNRSP01"), Tag.of(RESULT_LABEL, SUCCESS_RESULT_CODE)))) {
          public double count() {
            return 3;
          }
        };
    try (var source = new Registry(first, second)) {
      String text = exporter.scrapeCounters(source, space);
      assertEquals(3, text.lines().count());
      assertTrue(text.contains("layout=\"LGNRSP01\",result=\"0000\"} 3.0\n"));
      assertTrue(space.isEmpty());
      assertTrue(keys.isEmpty());
    }
  }

  @Test
  void scalar015CounterRuntimeIdentityRetained() {
    var failure = new IllegalStateException(PROVIDER_FAILURE_MARKER);
    var meter =
        new NoopCounter(cid()) {
          public double count() {
            throw failure;
          }
        };
    try (var source = new Registry(meter)) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> exporter.scrapeCounters(source, CS)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scalar016GaugeRuntimeIdentityRetained() {
    var failure = new IllegalStateException(PROVIDER_FAILURE_MARKER);
    var meter =
        new NoopGauge(gid()) {
          public double value() {
            throw failure;
          }
        };
    try (var source = new Registry(meter)) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> exporter.scrapeGauges(source, GS)));
    }
  }

  @Test
  void scalar017CounterErrorIsNotSuccess() {
    var failure = new AssertionError(PROVIDER_FAILURE_MARKER);
    var meter =
        new NoopCounter(cid()) {
          public double count() {
            throw failure;
          }
        };
    try (var source = new Registry(meter)) {
      assertSame(
          failure, assertThrows(AssertionError.class, () -> exporter.scrapeCounters(source, CS)));
    }
  }

  @Test
  void scalar018GaugeErrorIsNotSuccess() {
    var failure = new AssertionError(PROVIDER_FAILURE_MARKER);
    var meter =
        new NoopGauge(gid()) {
          public double value() {
            throw failure;
          }
        };
    try (var source = new Registry(meter)) {
      assertSame(
          failure, assertThrows(AssertionError.class, () -> exporter.scrapeGauges(source, GS)));
    }
  }

  @Test
  void scalar019CounterCheckedIoCauseAndOwnerRetained() {
    var failure = new IOException(PROVIDER_FAILURE_MARKER);
    try (var source = new Registry(counter(1))) {
      var actual =
          assertThrows(
              UncheckedIOException.class,
              () -> ApiScalarMetricExporter.encodeCounters(source, CS, broken(failure)));
      assertSame(failure, actual.getCause());
      assertEquals("scalar encoding failed", actual.getMessage());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scalar020GaugeCheckedIoCauseAndOwnerRetained() {
    var failure = new IOException(PROVIDER_FAILURE_MARKER);
    try (var source = new Registry(gauge(1))) {
      var actual =
          assertThrows(
              UncheckedIOException.class,
              () -> ApiScalarMetricExporter.encodeGauges(source, GS, broken(failure)));
      assertSame(failure, actual.getCause());
      assertEquals("scalar encoding failed", actual.getMessage());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void scalar021CounterNameAndValueEachReadOnce() {
    var names = new AtomicInteger();
    var values = new AtomicInteger();
    var meterIdentity =
        new Meter.Id(
            C,
            Tags.of(LAYOUT_LABEL, "LGNREQ01", RESULT_LABEL, SUCCESS_RESULT_CODE),
            "",
            "",
            Meter.Type.COUNTER) {
          public String getName() {
            return names.incrementAndGet() == 1 ? C : "nk_unapproved_total";
          }
        };
    var meter =
        new NoopCounter(meterIdentity) {
          public double count() {
            values.incrementAndGet();
            return 1;
          }
        };
    names.set(0);
    try (var source = new Registry(meter)) {
      String text = exporter.scrapeCounters(source, CS);
      assertTrue(text.contains("# TYPE " + C + " counter\n"));
      assertFalse(text.contains("unapproved"));
      assertEquals(1, names.get());
      assertEquals(1, values.get());
    }
  }

  @Test
  void scalar022GaugeNameAndValueEachReadOnce() {
    var names = new AtomicInteger();
    var values = new AtomicInteger();
    var meterIdentity =
        new Meter.Id(
            G,
            Tags.of(STORE_LABEL, API_SERVICE_VALUE, STATUS_LABEL, "PENDING"),
            "",
            "",
            Meter.Type.GAUGE) {
          public String getName() {
            return names.incrementAndGet() == 1 ? G : "nk_unapproved";
          }
        };
    var meter =
        new NoopGauge(meterIdentity) {
          public double value() {
            values.incrementAndGet();
            return 7;
          }
        };
    names.set(0);
    try (var source = new Registry(meter)) {
      String text = exporter.scrapeGauges(source, GS);
      assertTrue(text.contains("# TYPE " + G + " gauge\n"));
      assertFalse(text.contains("unapproved"));
      assertEquals(1, names.get());
      assertEquals(1, values.get());
    }
  }

  @Test
  void scalar023MultipleFamiliesAndSeriesKeepSeparateMetadata() {
    var other =
        new NoopCounter(
            raw("nk_operation_token_mismatch_total", List.of(Tag.of("operation", "UCRREQ01")))) {
          public double count() {
            return 3;
          }
        };
    try (var source = new Registry(counter(2), other)) {
      String text =
          exporter.scrapeCounters(
              source,
              Map.of(C, CS.get(C), "nk_operation_token_mismatch_total", Set.of("operation")));
      assertEquals(2, text.lines().filter(line -> line.startsWith("# TYPE ")).count());
      assertEquals(4, text.lines().count());
      assertTrue(text.contains("operation=\"UCRREQ01\"} 3.0\n"));
    }
    var second =
        new NoopGauge(
            raw(G, List.of(Tag.of(STORE_LABEL, API_SERVICE_VALUE), Tag.of(STATUS_LABEL, "SENT")))) {
          public double value() {
            return 3;
          }
        };
    try (var source = new Registry(gauge(2), second)) {
      String text = exporter.scrapeGauges(source, GS);
      assertEquals(3, text.lines().count());
      assertTrue(text.contains("status=\"SENT\",store=\"API\"} 3.0\n"));
    }
  }

  @Test
  void scalar024ConcurrentCallsAndOtherSourcesDoNotShareState()
      throws InterruptedException, ExecutionException, TimeoutException {
    try (var first = new Registry(counter(2), gauge(5));
        var second = new Registry(counter(3), gauge(7));
        var workers = Executors.newFixedThreadPool(4)) {
      var jobs = new ArrayList<Future<?>>();
      for (int index = 0; index < 64; index++)
        jobs.add(
            workers.submit(
                () -> {
                  assertTrue(exporter.scrapeCounters(first, CS).endsWith("} 2.0\n"));
                  assertTrue(exporter.scrapeGauges(first, GS).endsWith("} 5.0\n"));
                  assertTrue(exporter.scrapeCounters(second, CS).endsWith("} 3.0\n"));
                  assertTrue(exporter.scrapeGauges(second, GS).endsWith("} 7.0\n"));
                }));
      for (var job : jobs) job.get(10, TimeUnit.SECONDS);
      assertFalse(first.isClosed());
      assertFalse(second.isClosed());
    }
  }
}
