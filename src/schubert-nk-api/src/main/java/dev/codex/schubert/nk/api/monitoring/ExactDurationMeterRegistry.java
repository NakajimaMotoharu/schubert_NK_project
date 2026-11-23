package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.distribution.CountAtBucket;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.HistogramGauges;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.ValueAtPercentile;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import java.util.Arrays;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.locks.ReentrantLock;

/** SS351/1723/BUG1678: exact cumulative finite SLO counts, without HDR range quantization. */
public final class ExactDurationMeterRegistry extends SimpleMeterRegistry
    implements AutoCloseable, ExactDurationSupport {
  private static final Set<String> DURATION_NAMES =
      Set.of("nk_db_query_duration_seconds", "nk_mq_processing_duration_seconds");
  private static final double[] BOUNDARIES = {.001, .01, .1, 1., 1.5};

  public ExactDurationMeterRegistry() {
    this(SimpleConfig.DEFAULT, Clock.SYSTEM);
  }

  public ExactDurationMeterRegistry(SimpleConfig config, Clock clock) {
    super(
        Objects.requireNonNull(config, "registry config"), Objects.requireNonNull(clock, "clock"));
  }

  static void requireCompatible(MeterRegistry registry) {
    if (!(registry instanceof ExactDurationSupport))
      throw new IllegalArgumentException("CONFIG_INVALID");
  }

  @Override
  protected DistributionSummary newDistributionSummary(
      Meter.Id id, DistributionStatisticConfig config, double scale) {
    if (!DURATION_NAMES.contains(id.getName()))
      return super.newDistributionSummary(id, config, scale);
    return exactDurationSummary(this, id, config, scale);
  }

  static DistributionSummary exactDurationSummary(
      MeterRegistry owner, Meter.Id id, DistributionStatisticConfig config, double scale) {
    if (scale != 1
        || !"seconds".equals(id.getBaseUnit())
        || !Boolean.TRUE.equals(config.isPercentileHistogram())
        || !Arrays.equals(new double[0], config.getPercentiles())
        || !Arrays.equals(BOUNDARIES, config.getServiceLevelObjectiveBoundaries()))
      throw new IllegalArgumentException("CONFIG_INVALID");
    var summary = new ExactSummary(id);
    HistogramGauges.registerWithCommonFormat(summary, owner);
    return summary;
  }

  /** Constant memory; one private lock makes count/total/max/all buckets a single observation. */
  private static final class ExactSummary implements DistributionSummary {
    private final Meter.Id id;
    private final ReentrantLock stateLock = new ReentrantLock();
    private final long[] buckets = new long[BOUNDARIES.length];
    private long sampleCount;
    private double total;
    private double maximum;

    private ExactSummary(Meter.Id id) {
      this.id = id;
    }

    @Override
    public Meter.Id getId() {
      return id;
    }

    @Override
    public void record(double amount) {
      stateLock.lock();
      try {
        // All accepted inputs are finite nonnegative scalar nanoseconds converted to seconds.
        if (!(amount >= 0 && amount <= 9.223372036854776E9))
          throw new IllegalArgumentException("invalid duration");
        sampleCount++;
        total += amount;
        maximum = Math.max(maximum, amount);
        for (int i = 0; i < BOUNDARIES.length; i++) if (amount <= BOUNDARIES[i]) buckets[i]++;
      } finally {
        stateLock.unlock();
      }
    }

    @Override
    public long count() {
      return takeSnapshot().count();
    }

    @Override
    public double totalAmount() {
      return takeSnapshot().total();
    }

    @Override
    public double max() {
      return takeSnapshot().max();
    }

    @Override
    public HistogramSnapshot takeSnapshot() {
      stateLock.lock();
      try {
        var counts = new CountAtBucket[BOUNDARIES.length];
        for (int i = 0; i < counts.length; i++)
          counts[i] = new CountAtBucket(BOUNDARIES[i], buckets[i]);
        return new HistogramSnapshot(
            sampleCount, total, maximum, new ValueAtPercentile[0], counts, null);
      } finally {
        stateLock.unlock();
      }
    }
  }
}
