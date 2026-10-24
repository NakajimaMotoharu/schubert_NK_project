package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.ApiDurationMetricExporter;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.MockClock;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.ValueAtPercentile;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** MIDNAME001..004/1765: independent approved-name snapshot fixtures, no target/network/DB. */
class MetricIdentitySnapshotContractTest {
  private static final String COUNTER = "nk_http_requests_total";
  private static final String GAUGE = "nk_db_pool_connections";
  private static final String TIMER = "nk_http_request_duration_seconds";
  private static final String SUMMARY = "nk_db_query_duration_seconds";
  private static final String UNKNOWN = "nk_unapproved_fixture_seconds";

  private static Meter.Id identity(
      String approved, Tags tags, Meter.Type type, AtomicInteger reads) {
    var result =
        new Meter.Id("safe_fixture", tags, "", "", type) {
          public String getName() {
            return reads.incrementAndGet() == 1 ? approved : UNKNOWN;
          }
        };
    reads.set(0);
    return result;
  }

  private static final class Registry extends SimpleMeterRegistry implements AutoCloseable {
    final Meter meter;

    Registry(Meter meter) {
      super(SimpleConfig.DEFAULT, new MockClock());
      this.meter = meter;
    }

    public List<Meter> getMeters() {
      return List.of(meter);
    }
  }

  private static void expected(
      Meter meter,
      AtomicInteger reads,
      String name,
      String type,
      Function<MeterRegistry, String> scrape) {
    try (var source = new Registry(meter)) {
      String result = scrape.apply(source);
      assertFalse(result.contains(UNKNOWN));
      assertTrue(result.contains("# TYPE " + name + " " + type + "\n"));
      assertEquals(1, reads.get());
      assertFalse(source.isClosed());
    }
  }

  private static class HistogramMeter {
    final Meter.Id meterIdentity;
    final double total;
    final double bound;

    HistogramMeter(Meter.Id meterIdentity, double total, double bound) {
      this.meterIdentity = meterIdentity;
      this.total = total;
      this.bound = bound;
    }

    public Meter.Id getId() {
      return meterIdentity;
    }

    public HistogramSnapshot takeSnapshot() {
      return new HistogramSnapshot(
          1,
          total,
          0,
          new ValueAtPercentile[0],
          new CountAtBucket[] {new CountAtBucket(bound, 1)},
          null);
    }
  }

  private static final class Summary extends HistogramMeter implements DistributionSummary {
    Summary(Meter.Id meterIdentity) {
      super(meterIdentity, .5, 1);
    }

    public void record(double value) {
      throw new AssertionError("read only");
    }

    public long count() {
      throw new AssertionError("atomic snapshot only");
    }

    public double totalAmount() {
      throw new AssertionError("atomic snapshot only");
    }

    public double max() {
      throw new AssertionError("no max export");
    }
  }

  private static final class DurationMeter extends HistogramMeter implements Timer {
    DurationMeter(Meter.Id meterIdentity) {
      super(meterIdentity, 1, 1_000_000_000);
    }

    public void record(long value, TimeUnit unit) {
      throw new AssertionError("read only");
    }

    public <T> T record(Supplier<T> action) {
      throw new AssertionError("no callbacks");
    }

    public <T> T recordCallable(Callable<T> action) {
      throw new AssertionError("no callbacks");
    }

    public void record(Runnable action) {
      throw new AssertionError("no callbacks");
    }

    public long count() {
      throw new AssertionError("atomic snapshot only");
    }

    public double totalTime(TimeUnit unit) {
      throw new AssertionError("atomic snapshot only");
    }

    public double max(TimeUnit unit) {
      throw new AssertionError("no max export");
    }

    public TimeUnit baseTimeUnit() {
      return TimeUnit.NANOSECONDS;
    }
  }

  @Test
  void midname001CounterUsesApprovedNameExactlyOnce() {
    var reads = new AtomicInteger();
    var meterIdentity =
        identity(COUNTER, Tags.of("service", "WEB", "route", "/login"), Meter.Type.COUNTER, reads);
    Counter meter =
        new Counter() {
          public Meter.Id getId() {
            return meterIdentity;
          }

          public double count() {
            return 1;
          }

          public void increment(double amount) {
            throw new AssertionError("read only");
          }
        };
    expected(
        meter,
        reads,
        COUNTER,
        "counter",
        source ->
            new WebCounterMetricExporter()
                .scrapeCounters(source, Map.of(COUNTER, Set.of("service", "route"))));
  }

  @Test
  void midname002GaugeUsesApprovedNameExactlyOnce() {
    var reads = new AtomicInteger();
    var meterIdentity =
        identity(GAUGE, Tags.of("service", "WEB", "state", "active"), Meter.Type.GAUGE, reads);
    Gauge meter =
        new Gauge() {
          public Meter.Id getId() {
            return meterIdentity;
          }

          public double value() {
            return 1;
          }
        };
    expected(
        meter,
        reads,
        GAUGE,
        "gauge",
        source ->
            new WebGaugeMetricExporter()
                .scrapeGauges(source, Map.of(GAUGE, Set.of("service", "state"))));
  }

  @Test
  void midname003TimerUsesApprovedNameExactlyOnce() {
    var reads = new AtomicInteger();
    var meterIdentity =
        identity(TIMER, Tags.of("service", "WEB", "route", "/login"), Meter.Type.TIMER, reads);
    expected(
        new DurationMeter(meterIdentity),
        reads,
        TIMER,
        "histogram",
        source ->
            new WebDurationMetricExporter()
                .scrapeTimers(source, Map.of(TIMER, Set.of("service", "route"))));
  }

  @Test
  void midname004ApiSummaryUsesApprovedNameExactlyOnce() {
    var reads = new AtomicInteger();
    var meterIdentity =
        identity(
            SUMMARY,
            Tags.of("query_id", "FIXED", "outcome", "SUCCESS"),
            Meter.Type.DISTRIBUTION_SUMMARY,
            reads);
    expected(
        new Summary(meterIdentity),
        reads,
        SUMMARY,
        "histogram",
        source ->
            new ApiDurationMetricExporter()
                .scrape(source, Map.of(SUMMARY, Set.of("query_id", "outcome"))));
  }
}
