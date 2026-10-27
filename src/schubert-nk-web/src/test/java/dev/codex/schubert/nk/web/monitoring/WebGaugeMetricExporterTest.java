package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Gauge;
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

/** GAUGEENC001..016/1761: literal independent values and wire text, no reflection. */
class WebGaugeMetricExporterTest {
  private static final String STATE_LABEL = "state";
  private static final String SERVICE_LABEL = "service";
  private static final String ACTIVE_STATE = "active";
  private static final String NAME = "nk_db_pool_connections";
  private static final Map<String, Set<String>> SPACE =
      Map.of(NAME, Set.of(STATE_LABEL, SERVICE_LABEL));
  private final WebGaugeMetricExporter exporter = new WebGaugeMetricExporter();

  private static class FixedGauge implements Gauge {
    final double suppliedReading;
    final Meter.Id id;
    final AtomicInteger reads = new AtomicInteger();

    FixedGauge(double value, String state) {
      this.suppliedReading = value;
      id =
          new Meter.Id(
              NAME,
              Tags.of(STATE_LABEL, state, SERVICE_LABEL, "WEB"),
              "connections",
              "",
              Meter.Type.GAUGE);
    }

    public Meter.Id getId() {
      return id;
    }

    public double value() {
      reads.incrementAndGet();
      return suppliedReading;
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
    try (var source = new Registry(new FixedGauge(value, ACTIVE_STATE))) {
      return exporter.scrapeGauges(source, SPACE);
    }
  }

  @Test
  void gaugeenc001LiteralGaugeNameAndFractionAreUnchanged() {
    assertEquals(
        "# TYPE nk_db_pool_connections gauge\n"
            + "nk_db_pool_connections{service=\"WEB\",state=\"active\"} 2.5\n",
        text(2.5));
  }

  @Test
  void gaugeenc002ZeroAndFiniteExtremesDoNotBecomeUnknown() {
    assertTrue(text(0).endsWith("} 0.0\n"));
    assertTrue(text(Double.MAX_VALUE).endsWith("} 1.7976931348623157E308\n"));
    assertTrue(text(Double.MIN_VALUE).endsWith("} 4.9E-324\n"));
  }

  @Test
  void gaugeenc003UnknownAndSpecialGaugeValuesStayDistinct() {
    assertTrue(text(Double.NaN).endsWith("} NaN\n"));
    assertTrue(text(Double.POSITIVE_INFINITY).endsWith("} +Inf\n"));
    assertTrue(text(Double.NEGATIVE_INFINITY).endsWith("} -Inf\n"));
    assertTrue(text(-1).endsWith("} -1.0\n"));
    assertTrue(text(-Double.MIN_VALUE).endsWith("} -4.9E-324\n"));
    assertTrue(text(-Double.MAX_VALUE).endsWith("} -1.7976931348623157E308\n"));
  }

  @Test
  void gaugeenc004MultipleSeriesAndEscapingRetainMeaning() {
    try (var source =
        new Registry(new FixedGauge(2, ACTIVE_STATE), new FixedGauge(3, "a\"b\\c\nd"))) {
      String result = exporter.scrapeGauges(source, SPACE);
      assertEquals(3, result.lines().count());
      assertTrue(result.contains("state=\"a\\\"b\\\\c\\nd\""));
      assertTrue(
          result.contains(
              "nk_db_pool_connections{service=\"WEB\",state=\"a\\\"b\\\\c\\nd\"} 3.0\n"));
    }
  }

  @Test
  void gaugeenc005NameDoesNotTurnAnotherMeterTypeIntoGauge() {
    try (var source = new OrdinaryRegistry()) {
      source.counter(NAME);
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeGauges(source, SPACE));
    }
    try (var source = new OrdinaryRegistry()) {
      source.timer(NAME);
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeGauges(source, SPACE));
    }
    try (var source = new OrdinaryRegistry()) {
      source.summary(NAME);
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeGauges(source, SPACE));
    }
  }

  @Test
  void gaugeenc006NullContractsFailAtBoundary() {
    assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(null, SPACE));
    try (var source = new Registry(new FixedGauge(1, ACTIVE_STATE))) {
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, null));
      var invalid = new HashMap<String, Set<String>>();
      invalid.put(null, Set.of());
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, invalid));
      invalid.clear();
      invalid.put(NAME, null);
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, invalid));
      var keys = new HashSet<String>();
      keys.add(null);
      invalid.put(NAME, keys);
      assertThrows(NullPointerException.class, () -> exporter.scrapeGauges(source, invalid));
    }
  }

  @Test
  void gaugeenc007InvalidNamesAndExactLabelSetsAreRejected() {
    try (var source = new Registry(new FixedGauge(1, ACTIVE_STATE))) {
      for (String name : List.of("nk_WRONG_seconds", "bad_total", "nk_BAD_total"))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeGauges(source, Map.of(name, Set.of())));
      for (var keys :
          List.of(
              Set.of("le"),
              Set.of("bad-key"),
              Set.of(SERVICE_LABEL),
              Set.of(SERVICE_LABEL, STATE_LABEL, "extra")))
        assertThrows(
            IllegalArgumentException.class,
            () -> exporter.scrapeGauges(source, Map.of(NAME, keys)));
    }
  }

  @Test
  void gaugeenc008DuplicateProviderTagsFail() {
    var duplicatedId =
        new Meter.Id(NAME, Tags.empty(), "", "", Meter.Type.GAUGE) {
          public List<Tag> getTags() {
            return List.of(
                Tag.of(STATE_LABEL, ACTIVE_STATE),
                Tag.of(STATE_LABEL, "idle"),
                Tag.of(SERVICE_LABEL, "WEB"));
          }
        };
    var gauge =
        new FixedGauge(1, ACTIVE_STATE) {
          public Meter.Id getId() {
            return duplicatedId;
          }
        };
    assertSame(duplicatedId, gauge.getId());
    assertEquals(
        List.of(STATE_LABEL, STATE_LABEL, SERVICE_LABEL),
        gauge.getId().getTags().stream().map(Tag::getKey).toList());
    try (var source = new Registry(gauge)) {
      assertThrows(IllegalArgumentException.class, () -> exporter.scrapeGauges(source, SPACE));
    }
  }

  @Test
  void gaugeenc009EmptyAndUnselectedNeverFabricateZero() {
    try (var source = new OrdinaryRegistry()) {
      assertEquals("", exporter.scrapeGauges(source, SPACE));
      source.gauge("unselected", 42);
      assertEquals("", exporter.scrapeGauges(source, SPACE));
    }
    try (var source = new Registry(new FixedGauge(1, ACTIVE_STATE))) {
      assertEquals("", exporter.scrapeGauges(source, Map.of()));
    }
  }

  @Test
  void gaugeenc010BorrowedOwnerRemainsOpenAndClosedOwnerFails() {
    var source = new Registry(new FixedGauge(1, ACTIVE_STATE));
    try {
      exporter.scrapeGauges(source, SPACE);
      assertFalse(source.isClosed());
    } finally {
      source.close();
    }
    assertThrows(IllegalStateException.class, () -> exporter.scrapeGauges(source, SPACE));
  }

  @Test
  void gaugeenc011ExactlyOneProviderRead() {
    var gauge = new FixedGauge(7, ACTIVE_STATE);
    try (var source = new Registry(gauge)) {
      assertTrue(exporter.scrapeGauges(source, SPACE).endsWith("} 7.0\n"));
      assertEquals(1, gauge.reads.get());
    }
  }

  @Test
  void gaugeenc012ProviderRuntimeFailureIdentityRetained() {
    var failure = new IllegalStateException("fixture");
    var gauge =
        new FixedGauge(1, ACTIVE_STATE) {
          public double value() {
            throw failure;
          }
        };
    try (var source = new Registry(gauge)) {
      assertSame(
          failure,
          assertThrows(IllegalStateException.class, () -> exporter.scrapeGauges(source, SPACE)));
      assertFalse(source.isClosed());
    }
  }

  @Test
  void gaugeenc013ProviderErrorIsNotSuccess() {
    var failure = new AssertionError("fixture");
    var gauge =
        new FixedGauge(1, ACTIVE_STATE) {
          public double value() {
            throw failure;
          }
        };
    try (var source = new Registry(gauge)) {
      assertSame(
          failure, assertThrows(AssertionError.class, () -> exporter.scrapeGauges(source, SPACE)));
    }
  }

  @Test
  void gaugeenc014NamespaceCopiesPrecedeProviderMutation() {
    var keys = new HashSet<>(Set.of(STATE_LABEL, SERVICE_LABEL));
    var space = new HashMap<String, Set<String>>();
    space.put(NAME, keys);
    var gauge =
        new FixedGauge(3, ACTIVE_STATE) {
          public double value() {
            space.clear();
            keys.clear();
            return 3;
          }
        };
    try (var source = new Registry(gauge)) {
      assertTrue(exporter.scrapeGauges(source, space).endsWith("} 3.0\n"));
      assertTrue(space.isEmpty());
      assertTrue(keys.isEmpty());
    }
  }

  @Test
  void gaugeenc015CheckedWriterFailureRetainsCauseAndOwner() {
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
    try (var source = new Registry(new FixedGauge(1, ACTIVE_STATE))) {
      var actual =
          assertThrows(
              java.io.UncheckedIOException.class,
              () -> WebGaugeMetricExporter.encode(source, SPACE, writer));
      assertSame(failure, actual.getCause());
      assertEquals("gauge encoding failed", actual.getMessage());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void gaugeenc016InvalidConfigurationFailsBeforeProviderRead() {
    var gauge = new FixedGauge(1, ACTIVE_STATE);
    try (var source = new Registry(gauge)) {
      assertThrows(
          NullPointerException.class, () -> WebGaugeMetricExporter.encode(source, SPACE, null));
      assertThrows(
          IllegalArgumentException.class,
          () -> exporter.scrapeGauges(source, Map.of("wrong", Set.of())));
      assertEquals(0, gauge.reads.get());
    }
  }
}
