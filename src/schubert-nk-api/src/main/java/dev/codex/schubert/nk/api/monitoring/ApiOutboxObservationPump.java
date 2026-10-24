package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.LongSupplier;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS311332342351/1862/PG-D634: caller-scheduled sampling/stop state. No
 * thread, scheduler, pool or clock acquisition. Caller retains worker lifetime and original stop
 * budget; factory only constructs resource-free one-shot owners before this pump holds them.
 */
public final class ApiOutboxObservationPump implements Supplier<Optional<Snapshot>> {
  private final Object lock = new Object();
  private final boolean detailed;
  private final long intervalNanos;
  private final LongSupplier nanos;
  private final Supplier<? extends ApiReadOnlyObservationAttempt> attempts;
  private final ApiOutboxObservationSource source;
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final AtomicBoolean active = new AtomicBoolean();
  private final AtomicBoolean unconfirmed = new AtomicBoolean();
  private final AtomicReference<Optional<ApiReadOnlyObservationAttempt>> retained =
      new AtomicReference<>(Optional.empty());
  private boolean previouslyClaimed;
  private long lastClaim;

  public ApiOutboxObservationPump(
      String mode,
      Duration interval,
      LongSupplier nanos,
      Supplier<? extends ApiReadOnlyObservationAttempt> attempts,
      OutboxObservationRepository repository) {
    this.nanos = Objects.requireNonNull(nanos, "observation monotonic time");
    this.attempts = Objects.requireNonNull(attempts, "resource-free observation attempt factory");
    intervalNanos = Objects.requireNonNull(interval, "observation interval").toNanos();
    if (intervalNanos <= 0)
      throw new IllegalArgumentException("positive observation interval required");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    source = new ApiOutboxObservationSource(repository, mode);
  }

  /** Internal sampling cadence, not business retry, scrape timeout or a new shutdown deadline. */
  public static ApiOutboxObservationPump create(
      String mode,
      LongSupplier nanos,
      Supplier<? extends ApiReadOnlyObservationAttempt> attempts,
      OutboxObservationRepository repository) {
    return new ApiOutboxObservationPump(mode, Duration.ofSeconds(15), nanos, attempts, repository);
  }

  /** Caller schedules; only one claimed attempt, no I/O under this pump's claim monitor. */
  public void sampleIfDue() throws SQLException {
    synchronized (lock) {
      if (!detailed || stopping.get() || unconfirmed.get() || active.get()) return;
      long now;
      try {
        now = nanos.getAsLong();
      } catch (RuntimeException | Error failure) {
        source.missing();
        throw failure;
      }
      // System.nanoTime subtraction is wrap-safe within the positive interval's signed horizon.
      if (previouslyClaimed && now - lastClaim < intervalNanos) return;
      lastClaim = now;
      previouslyClaimed = true;
      source.missing();
      active.set(true);
    }
    try {
      ApiReadOnlyObservationAttempt attempt =
          Objects.requireNonNull(attempts.get(), "prepared observation attempt");
      retained.set(Optional.of(attempt));
      if (!stopping.get()) source.observe(attempt);
    } finally {
      if (retained.get().map(ApiReadOnlyObservationAttempt::hasUnconfirmedResource).orElse(false)) {
        unconfirmed.set(true);
        source.missing();
      } else {
        retained.set(Optional.empty());
      }
      if (stopping.get()) source.missing();
      active.set(false);
    }
  }

  /** Nonblocking request only, never proof of worker exit or resource release. */
  public void requestStop() {
    stopping.set(true);
    source.missing();
  }

  /** Caller must also prove its worker's termination before closing its borrowed pool. */
  public boolean isQuiescent() {
    return !active.get() && !unconfirmed.get();
  }

  @Override
  public Optional<Snapshot> get() {
    if (stopping.get() || unconfirmed.get()) return Optional.empty();
    return source.get();
  }
}
