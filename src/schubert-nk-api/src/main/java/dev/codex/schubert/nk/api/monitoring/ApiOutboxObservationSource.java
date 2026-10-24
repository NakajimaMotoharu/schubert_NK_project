package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS311332342351/1854/PG-D631: SDK-independent metadata source. Caller owns
 * RO transaction, connection, clock and producer lifetime; no implicit worker or SQL from
 * get/missing. A completed query is not an actual-source or freshness certificate.
 */
public final class ApiOutboxObservationSource implements Supplier<Optional<Snapshot>> {
  private final Object writerLock = new Object();
  private final OutboxObservationRepository repository;
  private final boolean detailed;
  private final AtomicReference<Entry> current = new AtomicReference<>(new Entry(Optional.empty()));

  private static final class Entry {
    private final Optional<Snapshot> observation;

    private Entry(Optional<Snapshot> observation) {
      this.observation = observation;
    }
  }

  /** Resource-free, with the same strict monitoring-mode boundary as the recorders. */
  public ApiOutboxObservationSource(OutboxObservationRepository repository, String mode) {
    this.repository = Objects.requireNonNull(repository, "outbox observation repository");
    detailed =
        switch (Objects.requireNonNull(mode, "monitoring mode")) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
  }

  /**
   * Publishes only after repository resource cleanup; never closes/mutates the borrowed connection.
   */
  public Optional<Snapshot> observe(Connection connection, Instant asOf) throws SQLException {
    Objects.requireNonNull(connection, "borrowed metrics connection");
    Objects.requireNonNull(asOf, "outbox observation instant");
    synchronized (writerLock) {
      if (!detailed) return Optional.empty();
      // Fresh identity per attempt/invalidation prevents Optional.empty's singleton ABA.
      Entry pending = new Entry(Optional.empty());
      current.set(pending);
      Optional<Snapshot> supplied = Optional.of(repository.read(connection, asOf));
      if (current.compareAndSet(pending, new Entry(supplied))) return supplied;
      return Optional.empty();
    }
  }

  /**
   * 1860/PG-D633: publishes only a one-shot owner's cleanup-confirmed result, never its connection.
   */
  public Optional<Snapshot> observe(ApiReadOnlyObservationAttempt attempt) throws SQLException {
    Objects.requireNonNull(attempt, "owned readonly observation attempt");
    synchronized (writerLock) {
      if (!detailed) return Optional.empty();
      Entry pending = new Entry(Optional.empty());
      current.set(pending);
      Optional<Snapshot> supplied = Optional.of(attempt.read());
      if (current.compareAndSet(pending, new Entry(supplied))) return supplied;
      return Optional.empty();
    }
  }

  /** Nonblocking invalidation: an already-running read cannot republish after this returns. */
  public void missing() {
    current.set(new Entry(Optional.empty()));
  }

  /** Immutable data only: no JDBC, SDK, locks, lifecycle callbacks or transaction operations. */
  @Override
  public Optional<Snapshot> get() {
    return current.get().observation;
  }
}
