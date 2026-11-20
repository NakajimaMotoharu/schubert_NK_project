package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.util.Objects;

/**
 * Pure evaluation of caller-owned observations, never a collector/controller. NK-OPS-001/P018-09;
 * MON005..009/013; UI252 §6; SS351 §7; PG-D520/PT-OPS-THRESH-001..014.
 */
public final class AlertThresholds {
  private static final int MAX_PERCENTAGE = 100;
  private static final String INVALID = "invalid alert observation";
  private static final Duration ONE_MINUTE = Duration.ofMinutes(1);
  private static final Duration FIVE_MINUTES = Duration.ofMinutes(5);
  private static final Duration TEN_MINUTES = Duration.ofMinutes(10);
  private static final Duration THIRTY_MINUTES = Duration.ofMinutes(30);

  public Severity filesystem(double percent, Duration above80, Duration above90) {
    percentage(percent);
    durations(above80, above90);
    return level(
        percent >= 90 && atLeast(above90, ONE_MINUTE),
        filesystemAboveWarning(percent) && atLeast(above80, FIVE_MINUTES));
  }

  public Severity transfer(long bytes, long files) {
    nonnegative(bytes);
    nonnegative(files);
    return level(
        bytes >= 4_500_000_000L || files >= 9_000, bytes >= 3_500_000_000L || files >= 5_000);
  }

  /** SS351/SS321: message count and total storage bytes are independent dimensions. */
  public Severity asyncQueue(long queued, long usedBytes, long capacityBytes) {
    nonnegative(queued);
    nonnegative(usedBytes);
    if (capacityBytes <= 0) throw new IllegalArgumentException(INVALID);
    BigInteger numerator = BigInteger.valueOf(usedBytes).multiply(BigInteger.valueOf(100));
    BigInteger denominator = BigInteger.valueOf(capacityBytes);
    return level(
        queued >= 9_000 || numerator.compareTo(denominator.multiply(BigInteger.valueOf(90))) >= 0,
        queued >= 5_000 || numerator.compareTo(denominator.multiply(BigInteger.valueOf(70))) >= 0);
  }

  public Severity webLog(long queued, Duration oldest) {
    nonnegative(queued);
    duration(oldest);
    return level(
        queued >= 9_000 || atLeast(oldest, THIRTY_MINUTES),
        queued >= 5_000 || atLeast(oldest, FIVE_MINUTES));
  }

  public Severity dlq(long messages, boolean increasing, boolean uninvestigated) {
    nonnegative(messages);
    return level(messages >= 1 && (increasing || uninvestigated), messages >= 1);
  }

  public Severity expiry(long messages) {
    nonnegative(messages);
    return level(messages >= 5_000, messages >= 1_000);
  }

  public Severity dbPool(double percent, Duration above80, long pending, long timeouts) {
    percentage(percent);
    duration(above80);
    nonnegative(pending);
    nonnegative(timeouts);
    return level(
        pending >= 1 || timeouts >= 1,
        dbPoolAboveWarning(percent) && atLeast(above80, FIVE_MINUTES));
  }

  public Severity jvmHeap(double percent, Duration above75, boolean outOfMemory) {
    percentage(percent);
    duration(above75);
    return level(
        percent >= 90 || outOfMemory, heapAboveWarning(percent) && atLeast(above75, TEN_MINUTES));
  }

  public Severity syncP95(double seconds, Duration above2, Duration above2Point5) {
    nonnegativeFinite(seconds);
    durations(above2, above2Point5);
    return level(
        seconds > 2.5 && atLeast(above2Point5, FIVE_MINUTES),
        syncLatencyAboveWarning(seconds) && atLeast(above2, FIVE_MINUTES));
  }

  static boolean filesystemAboveWarning(double percent) {
    return percent >= 80;
  }

  static boolean dbPoolAboveWarning(double percent) {
    return percent >= 80;
  }

  static boolean heapAboveWarning(double percent) {
    return percent >= 75;
  }

  static boolean syncLatencyAboveWarning(double seconds) {
    return seconds > 2.0;
  }

  public Severity backup(
      boolean scheduledRunPassed, boolean todaySuccess, long consecutiveFailures) {
    nonnegative(consecutiveFailures);
    return level(consecutiveFailures >= 2, scheduledRunPassed && !todaySuccess);
  }

  public Severity restarts(long lastTenMinutes, boolean rateLimited) {
    nonnegative(lastTenMinutes);
    return level(lastTenMinutes >= 5 || rateLimited, lastTenMinutes >= 1);
  }

  public Severity integrity(long failures) {
    nonnegative(failures);
    return level(failures >= 1, false);
  }

  private static Severity level(boolean critical, boolean warning) {
    if (critical) return Severity.CRITICAL;
    return warning ? Severity.WARNING : Severity.NORMAL;
  }

  private static void nonnegative(long value) {
    if (value < 0) throw new IllegalArgumentException(INVALID);
  }

  private static void nonnegativeFinite(double value) {
    if (!Double.isFinite(value) || value < 0) throw new IllegalArgumentException(INVALID);
  }

  private static void percentage(double value) {
    nonnegativeFinite(value);
    if (value > MAX_PERCENTAGE) throw new IllegalArgumentException(INVALID);
  }

  private static void duration(Duration value) {
    Objects.requireNonNull(value, "observed duration");
    if (value.isNegative()) throw new IllegalArgumentException(INVALID);
  }

  private static void durations(Duration warning, Duration critical) {
    duration(warning);
    duration(critical);
    if (critical.compareTo(warning) > 0) throw new IllegalArgumentException(INVALID);
  }

  private static boolean atLeast(Duration actual, Duration required) {
    return actual.compareTo(required) >= 0;
  }
}
