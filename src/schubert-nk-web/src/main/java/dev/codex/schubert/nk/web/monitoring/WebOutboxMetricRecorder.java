package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/** Complete supplied Web technical-outbox observation only; RD171/UI252/SS332351/1721. */
public final class WebOutboxMetricRecorder {
  public enum Status {
    PENDING,
    SENT,
    ERROR;

    public static Status parse(String value) {
      Objects.requireNonNull(value, "Web outbox status");
      for (var candidate : values()) if (candidate.name().equals(value)) return candidate;
      throw new IllegalArgumentException("invalid Web outbox status");
    }
  }

  public record Observation(
      long pending,
      long sent,
      long error,
      Duration pendingAge,
      Duration sentAge,
      Duration errorAge) {
    public Observation {
      Objects.requireNonNull(pendingAge, "pending age");
      Objects.requireNonNull(sentAge, "sent age");
      Objects.requireNonNull(errorAge, "error age");
      if (pending < 0 || sent < 0 || error < 0)
        throw new IllegalArgumentException("invalid Web outbox counts");
      if (pendingAge.isNegative() || sentAge.isNegative() || errorAge.isNegative())
        throw new IllegalArgumentException("invalid Web outbox ages");
      if ((pending == 0 && !pendingAge.isZero())
          || (sent == 0 && !sentAge.isZero())
          || (error == 0 && !errorAge.isZero()))
        throw new IllegalArgumentException("age requires a Web outbox row");
    }

    public long count(Status status) {
      Objects.requireNonNull(status, "Web outbox status");
      if (status == Status.PENDING) return pending;
      if (status == Status.SENT) return sent;
      return error;
    }

    public Duration age(Status status) {
      Objects.requireNonNull(status, "Web outbox status");
      if (status == Status.PENDING) return pendingAge;
      if (status == Status.SENT) return sentAge;
      return errorAge;
    }

    public double ageSeconds(Status status) {
      Duration value = age(status);
      return value.getSeconds() + value.getNano() / 1_000_000_000.0;
    }
  }

  private final boolean detailed;
  private final AtomicReference<Optional<Observation>> observed =
      new AtomicReference<>(Optional.empty());

  /**
   * Borrowed registry; one immutable publication, not a transaction across separate gauge scrapes.
   */
  public WebOutboxMetricRecorder(MeterRegistry registry, String mode) {
    Objects.requireNonNull(registry, "meter registry");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    if (detailed)
      for (var status : Status.values()) {
        Gauge.builder(
                "nk_outbox_rows",
                observed,
                current ->
                    current.get().map(value -> (double) value.count(status)).orElse(Double.NaN))
            .tags("store", "WEB", "status", status.name())
            .register(registry);
        Gauge.builder(
                "nk_outbox_oldest_seconds",
                observed,
                current -> current.get().map(value -> value.ageSeconds(status)).orElse(Double.NaN))
            .tags("store", "WEB", "status", status.name())
            .register(registry);
      }
  }

  public void record(Observation value) {
    Objects.requireNonNull(value, "Web outbox observation");
    if (detailed) observed.set(Optional.of(value));
  }

  public void missing() {
    observed.set(Optional.empty());
  }

  public Optional<Observation> snapshot() {
    return observed.get();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
