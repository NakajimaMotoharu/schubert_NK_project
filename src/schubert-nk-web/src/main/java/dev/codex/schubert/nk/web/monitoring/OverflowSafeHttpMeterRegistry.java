package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.AbstractTimer;
import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.HistogramGauges;
import io.micrometer.core.instrument.distribution.TimeWindowMax;
import io.micrometer.core.instrument.distribution.pause.PauseDetector;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.micrometer.core.instrument.util.TimeUtils;
import java.util.Arrays;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.DoubleAdder;
import java.util.concurrent.atomic.LongAdder;

/** SS351/1725/BUG1681: standard cumulative HTTP Timer with overflow-safe scalar total. */
public final class OverflowSafeHttpMeterRegistry extends SimpleMeterRegistry
    implements AutoCloseable, OverflowSafeDurationSupport {
  private static final String DURATION_NAME = "nk_http_request_duration_seconds";
  private static final double[] BOUNDARIES = {
    50000000,
    100000000,
    250000000,
    500000000,
    1000000000,
    1500000000,
    2000000000,
    2500000000L,
    5000000000L
  };

  public OverflowSafeHttpMeterRegistry() {
    this(Clock.SYSTEM);
  }

  public OverflowSafeHttpMeterRegistry(Clock clock) {
    super(SimpleConfig.DEFAULT, Objects.requireNonNull(clock, "clock"));
  }

  static void requireCompatible(MeterRegistry registry) {
    if (!(registry instanceof OverflowSafeDurationSupport))
      throw new IllegalArgumentException("CONFIG_INVALID");
  }

  @Override
  protected Timer newTimer(Meter.Id id, DistributionStatisticConfig config, PauseDetector pause) {
    if (!DURATION_NAME.equals(id.getName())) return super.newTimer(id, config, pause);
    return durationTimer(this, id, config, pause);
  }

  static Timer durationTimer(
      MeterRegistry owner, Meter.Id id, DistributionStatisticConfig config, PauseDetector pause) {
    if (Boolean.TRUE.equals(config.isPercentileHistogram())
        || !Arrays.equals(new double[0], config.getPercentiles())
        || !Arrays.equals(BOUNDARIES, config.getServiceLevelObjectiveBoundaries()))
      throw new IllegalArgumentException("CONFIG_INVALID");
    var timer = new OverflowSafeTimer(id, owner.config().clock(), config, pause);
    HistogramGauges.registerWithCommonFormat(timer, owner);
    return timer;
  }

  /** SDK integer histogram/wrappers/window max; only the cumulative total changes to binary64. */
  private static final class OverflowSafeTimer extends AbstractTimer {
    private final LongAdder sampleCount = new LongAdder();
    private final DoubleAdder totalNanoseconds = new DoubleAdder();
    private final TimeWindowMax maximumWindow;

    private OverflowSafeTimer(
        Meter.Id id, Clock clock, DistributionStatisticConfig config, PauseDetector pause) {
      super(id, clock, config, pause, TimeUnit.SECONDS, false);
      maximumWindow = new TimeWindowMax(clock, config);
    }

    @Override
    protected void recordNonNegative(long amount, TimeUnit unit) {
      long nanoseconds = unit.toNanos(amount);
      sampleCount.increment();
      totalNanoseconds.add(nanoseconds);
      maximumWindow.record(nanoseconds, TimeUnit.NANOSECONDS);
    }

    @Override
    public long count() {
      return sampleCount.longValue();
    }

    @Override
    public double totalTime(TimeUnit unit) {
      return TimeUtils.nanosToUnit(totalNanoseconds.doubleValue(), unit);
    }

    @Override
    public double max(TimeUnit unit) {
      return maximumWindow.poll(unit);
    }
  }
}
