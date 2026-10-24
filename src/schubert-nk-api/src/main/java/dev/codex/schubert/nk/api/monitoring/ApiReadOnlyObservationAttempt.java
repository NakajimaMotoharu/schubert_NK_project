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
      boolean transactionAttempted = false;
      @Nullable Snapshot result = null;
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
        result =
            repository.read(supplied, Objects.requireNonNull(clock.instant(), "observation time"));
      } catch (SQLException | RuntimeException | Error failure) {
        failures.add(failure);
      }
      @Nullable Connection owned = retained;
      if (owned != null) {
        if (transactionAttempted) {
          try {
            owned.rollback();
          } catch (SQLException | RuntimeException | Error rollback) {
            failures.add(rollback);
          }
        }
        try {
          owned.close();
          retained = null;
        } catch (SQLException | RuntimeException | Error close) {
          // Keep the exact Connection and failure frame; no implicit reclose/recheckout/clean
          // return.
          failures.add(close);
          unconfirmed.set(true);
          try {
            onUnconfirmed.accept(close);
          } catch (RuntimeException | Error diagnostic) {
            failures.add(diagnostic);
          }
        }
      }
      rethrowFailure();
      return Objects.requireNonNull(result, "successful readonly observation");
    }
  }

  private void rethrowFailure() throws SQLException {
    if (failures.isEmpty()) return;
    Throwable primary = failures.getFirst();
    for (Throwable secondary : failures)
      TemporaryInfrastructureException.attachSecondary(primary, secondary);
    TemporaryInfrastructureException.preserveFatal(primary);
    if (primary instanceof SQLException sql) throw sql;
    // The captured domain is SQLException/RuntimeException/Error; preserveFatal already throws
    // Error.
    throw (RuntimeException) primary;
  }

  /** Nonblocking status only; no resource, provider text or lifecycle handle is exposed. */
  public boolean hasUnconfirmedResource() {
    return unconfirmed.get();
  }
}
