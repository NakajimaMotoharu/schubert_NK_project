package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.Clock;
import io.micrometer.core.instrument.Meter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import io.micrometer.core.instrument.distribution.DistributionStatisticConfig;
import io.micrometer.core.instrument.distribution.HistogramSnapshot;
import io.micrometer.core.instrument.distribution.pause.NoPauseDetector;
import io.micrometer.core.instrument.distribution.pause.PauseDetector;
import io.micrometer.core.instrument.simple.SimpleConfig;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import io.micrometer.core.instrument.util.TimeUtils;
import java.util.Arrays;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.DoubleAdder;
import java.util.function.Supplier;
import org.jspecify.annotations.Nullable;

/** SS351/1725/BUG16811683: public Timer composition, no optional protected SDK hierarchy. */
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
    return durationTimer(this, config, pause, () -> super.newTimer(id, config, pause));
  }

  static Timer durationTimer(
      MeterRegistry owner,
      DistributionStatisticConfig config,
      PauseDetector pause,
      Supplier<Timer> factory) {
    if (!(pause instanceof NoPauseDetector)
        || Boolean.TRUE.equals(config.isPercentileHistogram())
        || !Arrays.equals(new double[0], config.getPercentiles())
        || !Arrays.equals(BOUNDARIES, config.getServiceLevelObjectiveBoundaries()))
      throw new IllegalArgumentException("CONFIG_INVALID");
    return new OverflowSafeTimer(
        Objects.requireNonNull(factory.get(), "HTTP timer delegate"), owner.config().clock());
  }

  /**
   * The private standard delegate supplies count/max/finite integer buckets only. Its wrapping long
   * total never escapes: every public sum, mean, measurement and snapshot uses our binary64 total.
   * Cross-counter atomic scrape is not promised, as with the original SDK timer.
   */
  private static final class OverflowSafeTimer implements Timer {
    private final Timer delegate;
    private final Clock clock;
    private final DoubleAdder totalNanoseconds = new DoubleAdder();

    private OverflowSafeTimer(Timer delegate, Clock clock) {
      this.delegate = delegate;
      this.clock = clock;
    }

    @Override
    public Meter.Id getId() {
      return delegate.getId();
    }

    @Override
    public void record(long amount, TimeUnit unit) {
      Objects.requireNonNull(unit, "timer unit");
      delegate.record(amount, unit);
      if (amount >= 0) totalNanoseconds.add(unit.toNanos(amount));
    }

    @Override
    public <T extends @Nullable Object> T record(Supplier<T> action) {
      Objects.requireNonNull(action, "timer supplier");
      long started = clock.monotonicTime();
      try {
        return action.get();
      } finally {
        record(clock.monotonicTime() - started, TimeUnit.NANOSECONDS);
      }
    }

    @Override
    public <T extends @Nullable Object> T recordCallable(Callable<T> action) throws Exception {
      Objects.requireNonNull(action, "timer callable");
      long started = clock.monotonicTime();
      try {
        return action.call();
      } finally {
        record(clock.monotonicTime() - started, TimeUnit.NANOSECONDS);
      }
    }

    @Override
    public void record(Runnable action) {
      Objects.requireNonNull(action, "timer runnable");
      long started = clock.monotonicTime();
      try {
        action.run();
      } finally {
        record(clock.monotonicTime() - started, TimeUnit.NANOSECONDS);
      }
    }

    @Override
    public long count() {
      return delegate.count();
    }

    @Override
    public double totalTime(TimeUnit unit) {
      return TimeUtils.nanosToUnit(totalNanoseconds.doubleValue(), unit);
    }

    @Override
    public double max(TimeUnit unit) {
      return delegate.max(unit);
    }

    @Override
    public TimeUnit baseTimeUnit() {
      return delegate.baseTimeUnit();
    }

    @Override
    public HistogramSnapshot takeSnapshot() {
      var snapshot = delegate.takeSnapshot();
      return new HistogramSnapshot(
          snapshot.count(),
          totalTime(TimeUnit.NANOSECONDS),
          snapshot.max(),
          snapshot.percentileValues(),
          snapshot.histogramCounts(),
          null);
    }

    @Override
    public void close() {
      delegate.close();
    }
  }
}
