package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.Tag;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.prometheus.metrics.expositionformats.ExpositionFormatWriter;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** COUNTENC001..016/1759: literal independent values and wire text, no reflection. */
class WebCounterMetricExporterTest {
  private static final String NAME = "nk_http_requests_total";
  private static final Map<String, Set<String>> SPACE = Map.of(NAME, Set.of("route", "service"));
  private final WebCounterMetricExporter exporter = new WebCounterMetricExporter();

  private static class FixedCounter implements Counter {
    final double value;
    final Meter.Id id;
    final AtomicInteger reads = new AtomicInteger();

    FixedCounter(double value, String route) {
      this.value = value;
      id =
          new Meter.Id(
              NAME, Tags.of("route", route, "service", "WEB"), "requests", "", Meter.Type.COUNTER);
    }

    public Meter.Id getId() {
      return id;
    }

    public double count() {
      reads.incrementAndGet();
      return value;
    }

    public void increment(double amount) {
      throw new AssertionError("read only");
    }
  }

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final List<Meter> supplied;

    Registry(Meter... supplied) {
      this.supplied = List.of(supplied);
    }

    public List<Meter> getMeters() {
      return supplied;
    }
  }

  private static class OrdinaryRegistry extends SimpleMeterRegistry implements AutoCloseable {}

  private String text(double value) {
    try (var source = new Registry(new FixedCounter(value, "/login"))) {
      return exporter.scrapeCounters(source, SPACE);
    }
  }

  @Test
  void countenc001LiteralCounterNameAndFractionAreUnchanged() {
    assertEquals(
        "# TYPE nk_http_requests_total counter\nnk_http_requests_total{route=\"/login\",service=\"WEB\"} 2.5\n",
        text(2.5));
  }

  @Test
  void countenc002ZeroAndFiniteExtremesDoNotBecomeUnknown() {
    assertTrue(text(0).endsWith("} 0.0\n"));
    assertTrue(text(Double.MAX_VALUE).endsWith("} 1.7976931348623157E308\n"));
    assertTrue(text(Double.MIN_VALUE).endsWith("} 4.9E-324\n"));
  }

  @Test
  void countenc003InvalidValuesAreNotClamped() {
    for (double value :
        new double[] {
          -Double.MIN_VALUE, -1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY
        }) assertThrows(IllegalArgumentException.class, () -> text(value));
  }

  @Test
  void countenc004MultipleSeriesAndEscapingRetainMeaning() {
    try (var source =
        new Registry(new FixedCounter(2, "/login"), new FixedCounter(3, "a\"b\\c\nd"))) {
      String result = exporter.scrapeCounters(source, SPACE);
      assertEquals(3, result.lines().count());
      assertTrue(result.contains("route=\"a\\\"b\\\\c\\nd\""));
      assertTrue(result.contains("service=\"WEB\"} 3.0\n"));
    }
  }

  @Test
  void countenc005NameDoesNotTurnAnotherMeterTypeIntoCounter() {
    try (var source = new OrdinaryRegistry()) {
      source.gauge(NAME, 1);
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeCounters(source, SPACE));
    }
    try (var source = new OrdinaryRegistry()) {
      source.timer(NAME);
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeCounters(source, SPACE));
    }
    try (var source = new OrdinaryRegistry()) {
      source.summary(NAME);
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeCounters(source, SPACE));
    }
  }

  @Test
  void countenc006NullContractsFailAtBoundary() {
    assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(null, SPACE));
    try (var source = new Registry(new FixedCounter(1, "/login"))) {
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, null));
      var invalid = new HashMap<String, Set<String>>();
      invalid.put(null, Set.of());
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, invalid));
      invalid.clear();
      invalid.put(NAME, null);
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, invalid));
      var keys = new HashSet<String>();
      keys.add(null);
      invalid.put(NAME, keys);
      assertThrows(NullPointerException.class, () -> exporter.scrapeCounters(source, invalid));
    }
  }

  @Test
  void countenc007InvalidNamesAndExactLabelSetsAreRejected() {
    try (var source = new Registry(new FixedCounter(1, "/login"))) {
      for (String name : List.of("nk_wrong_seconds", "bad_total", "nk_BAD_total"))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeCounters(source, Map.of(name, Set.of())));
      for (var keys :
          List.of(
              Set.of("le"),
              Set.of("bad-key"),
              Set.of("service"),
              Set.of("service", "route", "extra")))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeCounters(source, Map.of(NAME, keys)));
    }
  }

  @Test
  void countenc008DuplicateProviderTagsFail() {
    var duplicatedId =
        new Meter.Id(NAME, Tags.empty(), "", "", Meter.Type.COUNTER) {
          public List<Tag> getTags() {
            return List.of(
                Tag.of("route", "/login"), Tag.of("route", "/logout"), Tag.of("service", "WEB"));
          }
        };
    var counter =
        new FixedCounter(1, "/login") {
          public Meter.Id getId() {
            return duplicatedId;
          }
        };
    assertSame(duplicatedId, counter.getId());
    assertEquals(
        List.of("route", "route", "service"),
        counter.getId().getTags().stream().map(Tag::getKey).toList());
    try (var source = new Registry(counter)) {
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeCounters(source, SPACE));
    }
  }

  @Test
  void countenc009EmptyAndUnselectedNeverFabricateZero() {
    try (var source = new OrdinaryRegistry()) {
      assertEquals("", exporter.scrapeCounters(source, SPACE));
      source.gauge("unselected", 42);
      assertEquals("", exporter.scrapeCounters(source, SPACE));
    }
    try (var source = new Registry(new FixedCounter(1, "/login"))) {
      assertEquals("", exporter.scrapeCounters(source, Map.of()));
    }
  }

  @Test
  void countenc010BorrowedOwnerRemainsOpenAndClosedOwnerFails() {
    var source = new Registry(new FixedCounter(1, "/login"));
    try {
      exporter.scrapeCounters(source, SPACE);
      assertFalse(source.isClosed());
    } finally {
      source.close();
    }
    assertThrows(IllegalStateException.class, () -> exporter.scrapeCounters(source, SPACE));
  }

  @Test
  void countenc011ExactlyOneProviderRead() {
    var counter = new FixedCounter(7, "/login");
    try (var source = new Registry(counter)) {
      assertTrue(exporter.scrapeCounters(source, SPACE).endsWith("} 7.0\n"));
      assertEquals(1, counter.reads.get());
    }
  }

  @Test
  void countenc012ProviderRuntimeFailureIdentityRetained() {
    var failure = new IllegalStateException("fixture");
    var counter =
        new FixedCounter(1, "/login") {
          public double count() {
            throw failure;
          }
        };
    try (var source = new Registry(counter)) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> exporter.scrapeCounters(source, SPACE)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void countenc013ProviderErrorIsNotSuccess() {
    var failure = new AssertionError("fixture");
    var counter =
        new FixedCounter(1, "/login") {
          public double count() {
            throw failure;
          }
        };
    try (var source = new Registry(counter)) {
      assertSame(
          failure,
          assertThrows(AssertionError.class, () -> exporter.scrapeCounters(source, SPACE)));
    }
  }

  @Test
  void countenc014NamespaceCopiesPrecedeProviderMutation() {
    var keys = new HashSet<>(Set.of("route", "service"));
    var space = new HashMap<String, Set<String>>();
    space.put(NAME, keys);
    var counter =
        new FixedCounter(3, "/login") {
          public double count() {
            space.clear();
            keys.clear();
            return 3;
          }
        };
    try (var source = new Registry(counter)) {
      assertTrue(exporter.scrapeCounters(source, space).endsWith("} 3.0\n"));
      assertTrue(space.isEmpty());
      assertTrue(keys.isEmpty());
    }
  }

  @Test
  void countenc015CheckedWriterFailureRetainsCauseAndOwner() {
    var failure = new java.io.IOException("fixture");
    var writer =
        new ExpositionFormatWriter() {
          public boolean accepts(String accept) {
            throw new AssertionError("no negotiation");
          }

          public String getContentType() {
            throw new AssertionError("no endpoint");
          }

          public void write(
              java.io.OutputStream output,
              io.prometheus.metrics.model.snapshots.MetricSnapshots snapshots,
              io.prometheus.metrics.config.EscapingScheme scheme)
              throws java.io.IOException {
            throw failure;
          }
        };
    try (var source = new Registry(new FixedCounter(1, "/login"))) {
      var actual =
          assertThrows(
              java.io.UncheckedIOException.class,
              () -> WebCounterMetricExporter.encode(source, SPACE, writer));
      assertSame(failure, actual.getCause());
      assertEquals("counter encoding failed", actual.getMessage());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void countenc016InvalidConfigurationFailsBeforeProviderRead() {
    var counter = new FixedCounter(1, "/login");
    try (var source = new Registry(counter)) {
      assertThrows(
          NullPointerException.class, () -> WebCounterMetricExporter.encode(source, SPACE, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> exporter.scrapeCounters(source, Map.of("wrong", Set.of())));
      assertEquals(0, counter.reads.get());
    }
  }
}
