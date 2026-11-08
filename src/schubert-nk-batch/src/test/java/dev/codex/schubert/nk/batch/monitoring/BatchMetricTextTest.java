package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.micrometer.core.instrument.Counter;
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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** BATCHTEXT001..024/1777: literal vectors/borrowed memory providers only. */
class BatchMetricTextTest {
  private static final String SUFFIX_LABEL = "suffix";
  private static final String PART_SUFFIX = ".part";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String COUNTER_SAMPLE_LINE = "2.5\n";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String FAILURE_FIXTURE = "fixture";
  private static final String C = "nk_batch_runs_total";
  private static final String G = "nk_file_transfer_files";
  private static final String C_HEADER =
      "# HELP nk_batch_runs_total Supplied Batch technical observation.\n"
          + "# TYPE nk_batch_runs_total counter\n";
  private static final String G_HEADER =
      "# HELP nk_file_transfer_files Supplied Batch technical observation.\n"
          + "# TYPE nk_file_transfer_files gauge\n";
  private static final String C_ROW = "nk_batch_runs_total{status=\"SUCCESS\",step=\"BACKUP_DB\"} ";
  private static final String G_ROW = "nk_file_transfer_files{suffix=\".part\"} ";
  private final BatchMetricText formatter = new BatchMetricText();

  private static class Registry extends SimpleMeterRegistry implements AutoCloseable {
    List<Meter> meters;
    final AtomicInteger reads = new AtomicInteger();

    Registry(Meter... values) {
      super(SimpleConfig.DEFAULT, new MockClock());
      meters = Arrays.asList(values);
    }

    public List<Meter> getMeters() {
      reads.incrementAndGet();
      return meters;
    }

    public boolean isClosed() {
      reads.incrementAndGet();
      return super.isClosed();
    }

    public void close() {
      meters = List.of();
      super.close();
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

  private static List<Tag> ct() {
    return List.of(Tag.of("step", "BACKUP_DB"), Tag.of("status", "SUCCESS"));
  }

  private static List<Tag> gt() {
    return List.of(Tag.of(SUFFIX_LABEL, PART_SUFFIX));
  }

  private static NoopCounter counter(double value) {
    return new NoopCounter(raw(C, ct())) {
      public double count() {
        return value;
      }
    };
  }

  private static NoopGauge gauge(double value) {
    return new NoopGauge(raw(G, gt())) {
      public double value() {
        return value;
      }
    };
  }

  private String text(Meter... values) {
    try (var source = new Registry(values)) {
      return formatter.scrape(source, DEBUG_MODE);
    }
  }

  private static Tag tag(String key, String value) {
    return new Tag() {
      public String getKey() {
        return key;
      }

      public String getValue() {
        return value;
      }

      public int compareTo(Tag other) {
        throw new AssertionError("no provider sort");
      }
    };
  }

  @Test
  void batchtext001LiteralCounterGoldenAndNoDuplicateSuffix() {
    assertEquals(C_HEADER + C_ROW + COUNTER_SAMPLE_LINE, text(counter(2.5)));
  }

  @Test
  void batchtext002GaugeUnknownInfinityNegativeAndSignedZeroVectors() {
    double[] inputs = {
      Double.NaN,
      Double.POSITIVE_INFINITY,
      Double.NEGATIVE_INFINITY,
      -3,
      0,
      -0.0,
      Double.MIN_VALUE,
      Double.MAX_VALUE
    };
    String[] expected = {
      "NaN", "+Inf", "-Inf", "-3.0", "0.0", "-0.0", "4.9E-324", "1.7976931348623157E308"
    };
    for (int i = 0; i < inputs.length; i++)
      assertEquals(G_HEADER + G_ROW + expected[i] + "\n", text(gauge(inputs[i])));
  }

  @Test
  void batchtext003CounterFiniteNonnegativeBoundaries() {
    double[] inputs = {0, -0.0, Double.MIN_VALUE, Double.MAX_VALUE};
    String[] expected = {"0.0", "-0.0", "4.9E-324", "1.7976931348623157E308"};
    for (int i = 0; i < inputs.length; i++)
      assertEquals(C_HEADER + C_ROW + expected[i] + "\n", text(counter(inputs[i])));
  }

  @Test
  void batchtext004CounterRejectsNegativeNanAndInfinity() {
    for (double value :
        new double[] {
          -Double.MIN_VALUE, -1, Double.NaN, Double.POSITIVE_INFINITY, Double.NEGATIVE_INFINITY
        })
      assertEquals(
          "invalid Batch counter value",
          assertThrows(IllegalArgumentException.class, () -> text(counter(value))).getMessage());
  }

  @Test
  void batchtext005EmptyDoesNotFabricateObservationOrMetadata() {
    assertEquals("", text());
  }

  @Test
  void batchtext006UnknownNamesDoNotReadTagsOrValue() {
    var reads = new AtomicInteger();
    var id =
        new Meter.Id("safe_fixture", Tags.empty(), "", "", Meter.Type.COUNTER) {
          public String getName() {
            return "nk_unapproved_fixture";
          }

          public List<Tag> getTags() {
            throw new AssertionError("not selected");
          }
        };
    var meter =
        new NoopCounter(id) {
          public double count() {
            reads.incrementAndGet();
            throw new AssertionError("not selected");
          }
        };
    assertEquals("", text(meter));
    assertEquals(0, reads.get());
  }

  @Test
  void batchtext007BothSelectedTypesRejectWrongInstrument() {
    for (Meter bad :
        List.of(
            new NoopGauge(raw(C, ct())),
            new NoopTimer(raw(C, ct())),
            new NoopDistributionSummary(raw(C, ct()))))
      assertEquals(
          "selected Batch metric is not a counter",
          assertThrows(IllegalArgumentException.class, () -> text(bad)).getMessage());
    for (Meter bad :
        List.of(
            new NoopCounter(raw(G, gt())),
            new NoopTimer(raw(G, gt())),
            new NoopDistributionSummary(raw(G, gt()))))
      assertEquals(
          "selected Batch metric is not a gauge",
          assertThrows(IllegalArgumentException.class, () -> text(bad)).getMessage());
  }

  @Test
  void batchtext008NullSourceModeAndUnknownModeFail() {
    assertThrows(NullPointerException.class, () -> formatter.scrape(null, STANDARD_MODE));
    try (var source = new Registry()) {
      assertThrows(NullPointerException.class, () -> formatter.scrape(source, null));
      for (String mode : List.of("", "debug", "DEBUG ", "UNKNOWN"))
        assertThrows(IllegalArgumentException.class, () -> formatter.scrape(source, mode));
    }
  }

  @Test
  void batchtext009NullListMeterIdentityAndNameFail() {
    try (var source = new Registry()) {
      source.meters = null;
      assertThrows(NullPointerException.class, () -> formatter.scrape(source, DEBUG_MODE));
    }
    try (var source = new Registry((Meter) null)) {
      assertThrows(NullPointerException.class, () -> formatter.scrape(source, DEBUG_MODE));
    }
    Counter missing =
        new Counter() {
          public Meter.Id getId() {
            return null;
          }

          public double count() {
            throw new AssertionError("no value");
          }

          public void increment(double amount) {
            throw new AssertionError("read only");
          }
        };
    assertThrows(NullPointerException.class, () -> text(missing));
    assertThrows(NullPointerException.class, () -> text(new NoopGauge(raw(null, gt()))));
  }

  @Test
  void batchtext010ClosedDomainRejectsArbitraryEscapingAndNonAsciiInputs() {
    for (String invalid : List.of("UNAPPROVED", "x\"y", "x\\y", "x\ny", "日本語")) {
      var value = new NoopGauge(raw(G, List.of(Tag.of(SUFFIX_LABEL, invalid))));
      assertThrows(IllegalArgumentException.class, () -> text(value));
    }
  }

  @Test
  void batchtext011MissingAndExtraLabelsFailBeforeReadingValue() {
    for (var tags :
        List.of(
            List.<Tag>of(),
            List.of(Tag.of(SUFFIX_LABEL, PART_SUFFIX), Tag.of("actor", "INVALID")))) {
      var meter =
          new NoopGauge(raw(G, tags)) {
            public double value() {
              throw new AssertionError("validate first");
            }
          };
      assertThrows(IllegalArgumentException.class, () -> text(meter));
    }
  }

  @Test
  void batchtext012DuplicateAndNullTagContractsAreNotNormalized() {
    var duplicates = List.of(Tag.of(SUFFIX_LABEL, PART_SUFFIX), Tag.of(SUFFIX_LABEL, PART_SUFFIX));
    assertEquals(
        List.of(SUFFIX_LABEL, SUFFIX_LABEL), duplicates.stream().map(Tag::getKey).toList());
    assertThrows(IllegalArgumentException.class, () -> text(new NoopGauge(raw(G, duplicates))));
    assertThrows(NullPointerException.class, () -> text(new NoopGauge(raw(G, null))));
    var nullTags = new ArrayList<Tag>();
    nullTags.add(null);
    assertThrows(NullPointerException.class, () -> text(new NoopGauge(raw(G, nullTags))));
    for (var invalid : List.of(tag(null, PART_SUFFIX), tag(SUFFIX_LABEL, null)))
      assertThrows(NullPointerException.class, () -> text(new NoopGauge(raw(G, List.of(invalid)))));
  }

  @Test
  void batchtext013StandardReadsNoSourceTypeClosedOrValue() {
    var values = new AtomicInteger();
    var meter =
        new NoopGauge(raw(G, List.of(Tag.of("actor", "INVALID")))) {
          public double value() {
            values.incrementAndGet();
            throw new AssertionError("not read");
          }
        };
    try (var source = new Registry(meter)) {
      source.reads.set(0);
      assertEquals("", formatter.scrape(source, STANDARD_MODE));
      assertEquals(0, source.reads.get());
      assertEquals(0, values.get());
    }
  }

  @Test
  void batchtext014BorrowedSourceClosedDebugFailsAndStandardDoesNotReopen() {
    var source = new Registry(counter(2.5));
    try {
      assertEquals(C_HEADER + C_ROW + COUNTER_SAMPLE_LINE, formatter.scrape(source, DEBUG_MODE));
      assertFalse(source.isClosed());
      source.close();
      source.reads.set(0);
      assertEquals("", formatter.scrape(source, STANDARD_MODE));
      assertEquals(0, source.reads.get());
      assertThrows(IllegalStateException.class, () -> formatter.scrape(source, DEBUG_MODE));
      assertTrue(source.isClosed());
    } finally {
      source.close();
    }
  }

  @Test
  void batchtext015CounterRuntimeAndErrorIdentityRetained() {
    var failure = new IllegalStateException(FAILURE_FIXTURE);
    var broken =
        new NoopCounter(raw(C, ct())) {
          public double count() {
            throw failure;
          }
        };
    assertSame(failure, assertThrows(IllegalStateException.class, () -> text(broken)));
    var fatal = new AssertionError(FAILURE_FIXTURE);
    var bad =
        new NoopCounter(raw(C, ct())) {
          public double count() {
            throw fatal;
          }
        };
    assertSame(fatal, assertThrows(AssertionError.class, () -> text(bad)));
  }

  @Test
  void batchtext016GaugeRuntimeAndErrorIdentityRetained() {
    var failure = new IllegalStateException(FAILURE_FIXTURE);
    var broken =
        new NoopGauge(raw(G, gt())) {
          public double value() {
            throw failure;
          }
        };
    assertSame(failure, assertThrows(IllegalStateException.class, () -> text(broken)));
    var fatal = new AssertionError(FAILURE_FIXTURE);
    var bad =
        new NoopGauge(raw(G, gt())) {
          public double value() {
            throw fatal;
          }
        };
    assertSame(fatal, assertThrows(AssertionError.class, () -> text(bad)));
  }

  private void captured(boolean isCounter) {
    var nameReads = new AtomicInteger();
    var tagsReads = new AtomicInteger();
    var valueReads = new AtomicInteger();
    String approvedName = isCounter ? C : G;
    var original = new ArrayList<>(isCounter ? ct() : gt());
    var id =
        new Meter.Id("safe_fixture", Tags.empty(), "", "", Meter.Type.GAUGE) {
          public String getName() {
            return nameReads.incrementAndGet() == 1 ? approvedName : "nk_unknown_after_capture";
          }

          public List<Tag> getTags() {
            tagsReads.incrementAndGet();
            return original;
          }
        };
    Runnable mutate =
        () -> {
          valueReads.incrementAndGet();
          original.clear();
          original.add(Tag.of("actor", "UNAPPROVED"));
        };
    Meter meter =
        isCounter
            ? new NoopCounter(id) {
              public double count() {
                mutate.run();
                return 2.5;
              }
            }
            : new NoopGauge(id) {
              public double value() {
                mutate.run();
                return 3;
              }
            };
    assertEquals(
        isCounter ? C_HEADER + C_ROW + COUNTER_SAMPLE_LINE : G_HEADER + G_ROW + "3.0\n",
        text(meter));
    assertEquals(1, nameReads.get());
    assertEquals(1, tagsReads.get());
    assertEquals(1, valueReads.get());
  }

  @Test
  void batchtext017CounterCapturedNameAndLabelsMatchSameValueModel() {
    captured(true);
  }

  @Test
  void batchtext018GaugeCapturedNameAndLabelsMatchSameValueModel() {
    captured(false);
  }

  @Test
  void batchtext019SixFamiliesAndSeriesHaveDeterministicOrder() {
    var others =
        Map.of(
            "nk_batch_last_success_timestamp_seconds", List.of(Tag.of("step", "BACKUP_DB")),
            "nk_file_transfer_bytes", List.of(Tag.of(SUFFIX_LABEL, ".ready")));
    var meters = new ArrayList<Meter>();
    meters.add(counter(2.5));
    meters.add(gauge(3));
    others.forEach(
        (name, tags) ->
            meters.add(
                new NoopGauge(raw(name, tags)) {
                  public double value() {
                    return 5;
                  }
                }));
    meters.add(
        new NoopCounter(
            raw(
                "nk_integrity_failures_total",
                List.of(Tag.of("area", "HASH"), Tag.of("step", "BACKUP_DB")))));
    meters.add(
        new NoopCounter(
            raw(
                "nk_process_restarts_total",
                List.of(Tag.of("reason", "OOM"), Tag.of("service", "API")))));
    String text = text(meters.toArray(Meter[]::new));
    assertEquals(
        List.of(
            "nk_batch_last_success_timestamp_seconds",
            "nk_batch_runs_total",
            "nk_file_transfer_bytes",
            "nk_file_transfer_files",
            "nk_integrity_failures_total",
            "nk_process_restarts_total"),
        text.lines().filter(l -> l.startsWith("# TYPE ")).map(l -> l.split(" ")[2]).toList());
    assertEquals(6, text.lines().filter(l -> !l.startsWith("#")).count());
    assertTrue(text.contains("nk_process_restarts_total{reason=\"OOM\",service=\"API\"} 0.0\n"));
  }

  @Test
  void batchtext020LaterFailureDoesNotReturnPartialText() {
    var reads = new AtomicInteger();
    var first =
        new NoopGauge(raw(G, gt())) {
          public double value() {
            reads.incrementAndGet();
            return 3;
          }
        };
    var later =
        new NoopCounter(raw(C, ct())) {
          public double count() {
            throw new IllegalStateException(FAILURE_FIXTURE);
          }
        };
    var returned = new AtomicReference<Optional<String>>(Optional.empty());
    try (var source = new Registry(first, later)) {
      assertThrows(
          IllegalStateException.class,
          () -> returned.set(Optional.of(formatter.scrape(source, DEBUG_MODE))));
      assertEquals(1, reads.get());
      assertTrue(returned.get().isEmpty());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void batchtext021OneMeterListReadAndSortedMultipleSeries() {
    var ready =
        new NoopGauge(raw(G, List.of(Tag.of(SUFFIX_LABEL, ".ready")))) {
          public double value() {
            return 5;
          }
        };
    try (var source = new Registry(ready, gauge(3))) {
      String text = formatter.scrape(source, DEBUG_MODE);
      assertEquals(2, source.reads.get());
      assertEquals(G_HEADER + G_ROW + "3.0\nnk_file_transfer_files{suffix=\".ready\"} 5.0\n", text);
    }
  }

  @Test
  void batchtext022DuplicateSeriesNeverProducesAmbiguousText() {
    assertEquals(
        "duplicate Batch metric series",
        assertThrows(IllegalArgumentException.class, () -> text(gauge(1), gauge(2))).getMessage());
  }

  @Test
  void batchtext023OneFormatterDoesNotRetainPriorSourceOrFailure() {
    try (var first = new Registry(counter(2.5));
        var other = new Registry(gauge(3))) {
      assertEquals(C_HEADER + C_ROW + COUNTER_SAMPLE_LINE, formatter.scrape(first, DEBUG_MODE));
      assertEquals(G_HEADER + G_ROW + "3.0\n", formatter.scrape(other, DEBUG_MODE));
      assertEquals(C_HEADER + C_ROW + COUNTER_SAMPLE_LINE, formatter.scrape(first, DEBUG_MODE));
      assertFalse(first.isClosed());
      assertFalse(other.isClosed());
    }
  }

  @Test
  void batchtext024FiniteConcurrentCallsKeepBorrowedOwner() throws Exception {
    try (var source = new Registry(counter(2.5))) {
      var workers = Executors.newFixedThreadPool(4);
      try {
        var jobs = new ArrayList<Future<?>>();
        for (int i = 0; i < 64; i++)
          jobs.add(
              workers.submit(
                  () ->
                      assertEquals(
                          C_HEADER + C_ROW + COUNTER_SAMPLE_LINE,
                          formatter.scrape(source, DEBUG_MODE))));
        for (var job : jobs) job.get(10, TimeUnit.SECONDS);
        assertFalse(source.isClosed());
      } finally {
        workers.shutdownNow();
        assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  private static final String FULL_STANDARD =
      "# TYPE system_cpu_count gauge\nsystem_cpu_count{service=\"BATCH\"} 42.0\n";

  private static final class FullProbe
      extends io.micrometer.prometheusmetrics.PrometheusMeterRegistry {
    final AtomicInteger scrapes = new AtomicInteger();
    final AtomicInteger closes = new AtomicInteger();
    RuntimeException failure;
    Error fatal;
    boolean nullText;

    FullProbe() {
      super(io.micrometer.prometheusmetrics.PrometheusConfig.DEFAULT);
    }

    @Override
    public String scrape() {
      scrapes.incrementAndGet();
      if (failure != null) throw failure;
      if (fatal != null) throw fatal;
      return nullText ? null : FULL_STANDARD;
    }

    @Override
    public void close() {
      closes.incrementAndGet();
      super.close();
    }
  }

  private static BatchStandardMetricSource fullOwner(FullProbe probe) {
    var owner = new BatchStandardMetricSource(() -> probe, (source, gc) -> {});
    boolean transferred = false;
    try {

      owner.bind(DEBUG_MODE);
      transferred = true;
      return owner;

    } finally {
      if (!transferred) owner.close();
    }
  }

  @Test
  void batchfull001LiteralCustomBeforeStandardAndBothOwnersRemainBorrowed() {
    var probe = new FullProbe();
    try (var source = new Registry(counter(2.5));
        var standard = fullOwner(probe)) {
      assertEquals(
          C_HEADER + C_ROW + COUNTER_SAMPLE_LINE + FULL_STANDARD,
          formatter.scrape(source, DEBUG_MODE, standard));
      assertEquals(1, probe.scrapes.get());
      assertFalse(source.isClosed());
      assertFalse(probe.isClosed());
    }
    assertTrue(probe.isClosed());
  }

  @Test
  void batchfull002StandardNeverAcquiresOrReadsDetailsEvenAfterOwnerClose() {
    var calls = new AtomicInteger();
    var standard =
        new BatchStandardMetricSource(
            () -> {
              calls.incrementAndGet();
              throw new AssertionError("STD cannot acquire");
            },
            (registry, gc) -> {
              throw new AssertionError("STD cannot register");
            });
    try (var source = new Registry(counter(2.5))) {
      assertEquals("", formatter.scrape(source, STANDARD_MODE, standard));
      standard.close();
      assertEquals("", formatter.scrape(source, STANDARD_MODE, standard));
      assertEquals(0, source.reads.get());
      assertEquals(0, calls.get());
    } finally {
      standard.close();
    }
  }

  @Test
  void batchfull003UnboundAndClosedStandardNeverReturnPartialCustom() {
    var standard = new BatchStandardMetricSource();
    try (var source = new Registry(counter(2.5))) {
      assertThrows(
          IllegalStateException.class, () -> formatter.scrape(source, DEBUG_MODE, standard));
      standard.close();
      assertThrows(
          IllegalStateException.class, () -> formatter.scrape(source, DEBUG_MODE, standard));
      assertFalse(source.isClosed());
    } finally {
      standard.close();
    }
  }

  @Test
  void batchfull004NullAndUnknownInputsFailBeforeStandardRead() {
    var probe = new FullProbe();
    try (var source = new Registry(counter(2.5));
        var standard = fullOwner(probe)) {
      assertThrows(NullPointerException.class, () -> formatter.scrape(source, DEBUG_MODE, null));
      assertThrows(NullPointerException.class, () -> formatter.scrape(null, DEBUG_MODE, standard));
      assertThrows(NullPointerException.class, () -> formatter.scrape(source, null, standard));
      assertThrows(
          IllegalArgumentException.class, () -> formatter.scrape(source, "debug", standard));
      assertEquals(0, probe.scrapes.get());
      assertEquals(0, source.reads.get());
    }
  }

  @Test
  void batchfull005CustomRuntimePreservesIdentityAndSkipsFailingStandard() {
    var primary = new IllegalArgumentException("custom runtime fixture");
    var probe = new FullProbe();
    probe.fatal = new AssertionError("standard unreached");
    try (var source =
            new Registry() {
              @Override
              public List<Meter> getMeters() {
                throw primary;
              }
            };
        var standard = fullOwner(probe)) {
      assertSame(
          primary,
          assertThrows(
              IllegalArgumentException.class,
              () -> formatter.scrape(source, DEBUG_MODE, standard)));
      assertEquals(0, probe.scrapes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void batchfull006CustomFatalPreservesIdentityAndSkipsStandard() {
    var primary = new AssertionError("custom fatal fixture");
    var probe = new FullProbe();
    probe.failure = new IllegalStateException("standard unreached");
    try (var source =
            new Registry() {
              @Override
              public List<Meter> getMeters() {
                throw primary;
              }
            };
        var standard = fullOwner(probe)) {
      assertSame(
          primary,
          assertThrows(AssertionError.class, () -> formatter.scrape(source, DEBUG_MODE, standard)));
      assertEquals(0, probe.scrapes.get());
    }
  }

  @Test
  void batchfull007StandardRuntimeIsNotPartialCustomSuccess() {
    var probe = new FullProbe();
    var primary = new IllegalStateException("standard runtime fixture");
    probe.failure = primary;
    try (var source = new Registry(counter(2.5));
        var standard = fullOwner(probe)) {
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class, () -> formatter.scrape(source, DEBUG_MODE, standard)));
      assertEquals(1, probe.scrapes.get());
      assertFalse(source.isClosed());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void batchfull008StandardFatalPreservesIdentityAndOwnership() {
    var probe = new FullProbe();
    var primary = new AssertionError("standard fatal fixture");
    probe.fatal = primary;
    try (var source = new Registry(counter(2.5));
        var standard = fullOwner(probe)) {
      assertSame(
          primary,
          assertThrows(AssertionError.class, () -> formatter.scrape(source, DEBUG_MODE, standard)));
      assertEquals(1, probe.scrapes.get());
      assertFalse(source.isClosed());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void batchfull009NullStandardTextIsRejectedRatherThanStringifiedOrEmptySuccess() {
    var probe = new FullProbe();
    probe.nullText = true;
    try (var source = new Registry(counter(2.5));
        var standard = fullOwner(probe)) {
      assertThrows(
          NullPointerException.class, () -> formatter.scrape(source, DEBUG_MODE, standard));
      assertEquals(1, probe.scrapes.get());
      assertFalse(probe.isClosed());
    }
  }

  @Test
  void batchfull010EmptyCustomAndNextSourceDoNotRetainHistory() {
    var probe = new FullProbe();
    try (var source = new Registry();
        var standard = fullOwner(probe)) {
      assertEquals(FULL_STANDARD, formatter.scrape(source, DEBUG_MODE, standard));
      source.meters = List.of(counter(1.5));
      assertEquals(
          C_HEADER + C_ROW + "1.5\n" + FULL_STANDARD,
          formatter.scrape(source, DEBUG_MODE, standard));
      assertEquals(2, probe.scrapes.get());
    }
  }

  @Test
  void batchfull011ConcurrentBorrowedSourcesNeverMixOrClose() throws Exception {
    var firstProbe = new FullProbe();
    var secondProbe = new FullProbe();
    try (var first = new Registry(counter(1.5));
        var second = new Registry(counter(2.5));
        var firstStandard = fullOwner(firstProbe);
        var secondStandard = fullOwner(secondProbe)) {
      var workers = Executors.newFixedThreadPool(2);
      try {
        var firstJob =
            workers.submit(
                () -> {
                  for (int i = 0; i < 16; i++)
                    assertEquals(
                        C_HEADER + C_ROW + "1.5\n" + FULL_STANDARD,
                        formatter.scrape(first, DEBUG_MODE, firstStandard));
                });
        var secondJob =
            workers.submit(
                () -> {
                  for (int i = 0; i < 16; i++)
                    assertEquals(
                        C_HEADER + C_ROW + COUNTER_SAMPLE_LINE + FULL_STANDARD,
                        formatter.scrape(second, DEBUG_MODE, secondStandard));
                });
        firstJob.get(10, TimeUnit.SECONDS);
        secondJob.get(10, TimeUnit.SECONDS);
        assertEquals(16, firstProbe.scrapes.get());
        assertEquals(16, secondProbe.scrapes.get());
        assertFalse(first.isClosed());
        assertFalse(second.isClosed());
        assertFalse(firstProbe.isClosed());
        assertFalse(secondProbe.isClosed());
      } finally {
        workers.shutdownNow();
        assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void batchfull012ActualStandardSdkUsesIndependentOwnJvmCpuOracle() {
    try (var source = new Registry(counter(2.5));
        var standard = new BatchStandardMetricSource()) {
      standard.bind(DEBUG_MODE);
      String text = formatter.scrape(source, DEBUG_MODE, standard);
      assertTrue(text.startsWith(C_HEADER + C_ROW + COUNTER_SAMPLE_LINE));
      String cpu =
          "system_cpu_count{service=\"BATCH\"} "
              + (double) Runtime.getRuntime().availableProcessors();
      assertTrue(text.lines().anyMatch(cpu::equals));
      assertTrue(text.contains("# TYPE system_cpu_count gauge\n"));
      assertTrue(text.contains("jvm_memory_used_bytes{"));
      var types = text.lines().filter(line -> line.startsWith("# TYPE ")).toList();
      assertEquals(types.size(), types.stream().distinct().count());
      assertFalse(source.isClosed());
    }
  }

  @Test
  void batchfull013HelperReleasesRejectedCandidateBeforeReturningOwner() {
    var probe = new FullProbe();
    try {
      probe.close();
      assertEquals(1, probe.closes.get());
      var failure = assertThrows(IllegalStateException.class, () -> fullOwner(probe));
      assertEquals("standard metric registry closed", failure.getMessage());
      assertEquals(2, probe.closes.get());
      assertEquals(0, probe.scrapes.get());
      assertTrue(probe.isClosed());
    } finally {
      probe.close();
    }
  }
}
