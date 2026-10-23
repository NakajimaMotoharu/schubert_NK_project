package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Supplied API outbox row counts only, no SQL/dispatch/oldest-age/Web-store access. PG-D545/1647.
 */
public final class OutboxRowsMetricRecorder {
  public enum Status {
    PENDING,
    SENT,
    ERROR
  }

  public record Counts(long pending, long sent, long error) {
    public Counts {
      if (pending < 0 || sent < 0 || error < 0)
        throw new IllegalArgumentException("invalid outbox counts");
    }

    public long value(Status status) {
      Objects.requireNonNull(status, "outbox metric status");
      if (status == Status.PENDING) return pending;
      if (status == Status.SENT) return sent;
      return error;
    }
  }

  private final boolean detailed;
  private final AtomicReference<Optional<Counts>> observedCounts =
      new AtomicReference<>(Optional.empty());

  /** One instance owns the API store family; caller retains registry lifetime/partial resources. */
  public OutboxRowsMetricRecorder(MeterRegistry registry, String mode) {
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
                "nk_outbox_rows",
                observedCounts,
                snapshot ->
                    snapshot.get().map(counts -> (double) counts.value(status)).orElse(Double.NaN))
            .tag("store", "API")
            .tag("status", status.name())
            .register(registry);
  }

  public static Status status(String supplied) {
    Objects.requireNonNull(supplied, "outbox metric status");
    for (var status : Status.values()) if (status.name().equals(supplied)) return status;
    throw new IllegalArgumentException("CONFIG_INVALID");
  }

  public void record(Counts supplied) {
    Objects.requireNonNull(supplied, "outbox metric counts");
    if (detailed) observedCounts.set(Optional.of(supplied));
  }

  public void missing() {
    observedCounts.set(Optional.empty());
  }

  public Optional<Counts> snapshot() {
    return observedCounts.get();
  }

  public boolean detailedMetricsRequested() {
    return detailed;
  }
}
