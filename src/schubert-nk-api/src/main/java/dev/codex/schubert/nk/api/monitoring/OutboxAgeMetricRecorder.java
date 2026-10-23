package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.OutboxRowsMetricRecorder.Status;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/** SS351 supplied API outbox ages only, not a clock/SQL/dispatcher. PG-D546/1660. */
public final class OutboxAgeMetricRecorder {
  public record Ages(Duration pending, Duration sent, Duration error) {
    public Ages {
      Objects.requireNonNull(pending, "pending age");
      Objects.requireNonNull(sent, "sent age");
      Objects.requireNonNull(error, "error age");
      if (pending.isNegative() || sent.isNegative() || error.isNegative())
        throw new IllegalArgumentException("invalid outbox age");
    }

    public Duration value(Status status) {
      Objects.requireNonNull(status, "outbox metric status");
      if (status == Status.PENDING) return pending;
      if (status == Status.SENT) return sent;
      return error;
    }
  }

  private final boolean detailed;
  private final AtomicReference<Optional<Ages>> observedAges =
      new AtomicReference<>(Optional.empty());

  /** Caller owns registry and supplies a complete observation; unknown is never implied zero. */
  public OutboxAgeMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    if (detailed)
      for (var status : Status.values())
        Gauge.builder(
                "nk_outbox_oldest_seconds",
                observedAges,
                snapshot ->
                    snapshot.get().map(ages -> seconds(ages.value(status))).orElse(Double.NaN))
            .tag("store", "API")
            .tag("status", status.name())
            .register(registry);
  }

  private static double seconds(Duration age) {
    // Never multiply seconds into long millis/nanos: Duration's full range must not overflow.
    return age.getSeconds() + age.getNano() / 1_000_000_000d;
  }

  public void record(Ages supplied) {
    Objects.requireNonNull(supplied, "outbox metric ages");
    if (detailed) observedAges.set(Optional.of(supplied));
  }

  public void missing() {
    observedAges.set(Optional.empty());
  }

  public Optional<Ages> snapshot() {
    return observedAges.get();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
