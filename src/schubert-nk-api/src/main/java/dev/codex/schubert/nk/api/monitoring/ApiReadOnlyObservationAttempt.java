package dev.codex.schubert.nk.api.monitoring;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository.Snapshot;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;

/**
 * NK-OPS-001/RD171/UI252/SS311332342351/1858/PG-D632: a single readonly observation checkout.
 * Borrowed pool/clock and a prebuilt UNKNOWN-retaining policy; no worker, SDK or publication.
 * Actual callers must retain this owner before read, and retain the failed release frame on
 * UNKNOWN.
 */
public final class ApiReadOnlyObservationAttempt {
  private final Object lock = new Object();
  private final DataSource pool;
  private final Clock clock;
  private final OutboxObservationRepository repository;
  private final Consumer<Throwable> onUnconfirmed;
  private final List<Throwable> failures = new ArrayList<>(4);
  private final AtomicBoolean unconfirmed = new AtomicBoolean();
  private @Nullable Connection retained;
  private boolean attempted;
  private boolean transactionAttempted;
  private boolean rollbackAttempted;
  private boolean closeAttempted;

  /** Resource-free: prepare all ports/state before checkout, never mutate or close the pool. */
  public ApiReadOnlyObservationAttempt(
      DataSource pool,
      Clock clock,
      OutboxObservationRepository repository,
      Consumer<Throwable> onUnconfirmed) {
    this.pool = Objects.requireNonNull(pool, "borrowed observation pool");
    this.clock = Objects.requireNonNull(clock, "observation clock");
    this.repository = Objects.requireNonNull(repository, "outbox observation repository");
    this.onUnconfirmed = Objects.requireNonNull(onUnconfirmed, "unconfirmed connection policy");
  }

  /** One checkout and one cleanup attempt only; no successful result before confirmed close. */
  public Snapshot read() throws SQLException {
    synchronized (lock) {
      if (attempted) throw new IllegalStateException("observation attempt already used");
      attempted = true;
      try {
        @Nullable Connection supplied = pool.getConnection();
        if (supplied == null) throw new SQLException("observation connection unavailable");
        retained = supplied;
        if (!supplied.getAutoCommit())
          throw new SQLException("observation connection already transactional");
        supplied.setReadOnly(true);
        supplied.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        transactionAttempted = true;
        supplied.setAutoCommit(false);
        Snapshot result =
            repository.read(supplied, Objects.requireNonNull(clock.instant(), "observation time"));
        rollbackAttempted = true;
        supplied.rollback();
        closeOwned(supplied);
        return result;
      } catch (SQLException | RuntimeException | Error primary) {
        failures.add(primary);
        cleanup();
        for (Throwable secondary : failures)
          TemporaryInfrastructureException.attachSecondary(primary, secondary);
        TemporaryInfrastructureException.preserveFatal(primary);
        throw primary;
      }
    }
  }

  private void cleanup() {
    @Nullable Connection owned = retained;
    if (owned == null) return;
    if (transactionAttempted && !rollbackAttempted) {
      rollbackAttempted = true;
      try {
        owned.rollback();
      } catch (SQLException | RuntimeException | Error rollback) {
        failures.add(rollback);
      }
    }
    if (!closeAttempted) {
      try {
        closeOwned(owned);
      } catch (SQLException | RuntimeException | Error close) {
        failures.add(close);
      }
    }
  }

  private void closeOwned(Connection owned) throws SQLException {
    closeAttempted = true;
    try {
      owned.close();
      retained = null;
    } catch (SQLException | RuntimeException | Error close) {
      // Keep the exact Connection and failure frame; no implicit reclose/recheckout/clean return.
      unconfirmed.set(true);
      try {
        onUnconfirmed.accept(close);
      } catch (RuntimeException | Error diagnostic) {
        failures.add(diagnostic);
      }
      throw close;
    }
  }

  /** Nonblocking status only; no resource, provider text or lifecycle handle is exposed. */
  public boolean hasUnconfirmedResource() {
    return unconfirmed.get();
  }
}
