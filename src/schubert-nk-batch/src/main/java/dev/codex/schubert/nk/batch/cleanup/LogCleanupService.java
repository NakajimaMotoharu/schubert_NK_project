package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupKind;
import dev.codex.schubert.nk.batch.repository.CleanupReason;
import dev.codex.schubert.nk.batch.repository.CleanupRepository;
import dev.codex.schubert.nk.batch.repository.LogCleanupProgress;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.Connection;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * NK-BAT-001; OPS-009/DAT-009; UI251; SS341§3/7.2; SSC-051; PG-D-138; PT-BAT-018..029. Borrows the
 * parent's single-owner connection; caller MUST discard/close it after any failure. Does not
 * certify OS flock, actual backup files, inactive applications or whole morning sequence.
 * SSC337/BUG2317/YKT2062: borrowed transaction compounds, PT-BAT-LOGTX337001..019, spec709.
 */
@NullMarked
public final class LogCleanupService {
  private static final long LIMIT_NANOS = 1_800_000_000_000L;
  private final LongSupplier clock;
  private final MaintenanceMutationGuard mutation;

  public LogCleanupService() {
    this(System::nanoTime);
  }

  LogCleanupService(LongSupplier clock) {
    this.clock = Objects.requireNonNull(clock, "clock");
    mutation = new MaintenanceMutationGuard();
  }

  public static LogCleanupService withOwner(
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) {
    return new LogCleanupService(new MaintenanceMutationGuard(owner));
  }

  private LogCleanupService(MaintenanceMutationGuard mutation) {
    clock = System::nanoTime;
    this.mutation = mutation;
  }

  public LogCleanupSummary execute(Connection connection, BatchRun run) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(run, "run");
    long start = clock.getAsLong();
    check(start);
    try {
      if (!connection.getAutoCommit())
        throw new IllegalArgumentException("parent connection must be between transactions");
      var lease = new SessionLease(connection);
      return owned(
          lease::close,
          () -> {
            lease.acquire();
            var initial = transaction(connection, run, Optional.empty());
            check(start);
            var progress = initial.progress();
            while (!progress.complete()) {
              check(start);
              progress = transaction(connection, run, Optional.of(progress.counts())).progress();
              check(start);
            }
            return new LogCleanupSummary(run, initial.before(), progress);
          });
    } catch (CleanupStoppedException failure) {
      StorageIoException.preserveFatal(failure);
      // BUG-145/YKT-113: resource closure can append raw JDBC suppressed diagnostics.
      throw new CleanupStoppedException(failure.reason());
    } catch (SQLException | BatchRepositoryException failure) {
      StorageIoException.preserveFatal(failure);
      throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
    }
  }

  private void check(long start) {
    mutation.check();
    if (Thread.currentThread().isInterrupted())
      throw new CleanupStoppedException(CleanupStopReason.INTERRUPTED);
    long elapsed = clock.getAsLong() - start;
    // BUG186/YKT146: interruption may arrive while the clock boundary executes.
    if (Thread.currentThread().isInterrupted())
      throw new CleanupStoppedException(CleanupStopReason.INTERRUPTED);
    if (elapsed < 0 || elapsed >= LIMIT_NANOS)
      throw new CleanupStoppedException(CleanupStopReason.TIME_LIMIT);
  }

  private record ChunkProgress(CleanupCounts before, LogCleanupProgress progress) {}

  @FunctionalInterface
  private interface SqlRelease {
    void close() throws SQLException;
  }

  @FunctionalInterface
  private interface SqlAction<T extends @Nullable Object> {
    T run() throws SQLException;
  }

  /** SSC063/PG178/BAT026,029: one release, fixed secondary, never TWR self-suppression. */
  private static <T extends @Nullable Object> T owned(SqlRelease release, SqlAction<T> action)
      throws SQLException {
    T result;
    try {
      result = action.run();
    } catch (SQLException | RuntimeException | Error primary) {
      try {
        release.close();
      } catch (SQLException | RuntimeException | Error secondary) {
        if (replace(primary, secondary)) throw secondary;
      }
      throw primary;
    }
    release.close();
    return result;
  }

  private static boolean replace(@Nullable Throwable primary, Throwable secondary) {
    if (primary == null || (known(primary) && !known(secondary))) return true;
    if (!known(primary))
      primary.addSuppressed(new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE));
    else {
      StorageIoException.preserveFatal(primary);
      StorageIoException.preserveFatal(secondary);
    }
    return false;
  }

  private static boolean known(Throwable failure) {
    return failure instanceof SQLException
        || failure instanceof BatchRepositoryException
        || failure instanceof CleanupStoppedException;
  }

  private ChunkProgress transaction(
      Connection c, BatchRun run, Optional<CleanupCounts> expectedBefore) throws SQLException {
    mutation.check();
    c.setAutoCommit(false);
    ChunkProgress result;
    boolean committed = false;
    try {
      mutation.bind(c);
      mutation.check();
      var repository = new CleanupRepository(c);
      var chunk = repository.execute(run, CleanupKind.LOGS, 10000);
      if (chunk.reason() == CleanupReason.LOCK_BUSY)
        throw new CleanupStoppedException(CleanupStopReason.LOCK_BUSY);
      if (chunk.reason() == CleanupReason.BACKUP_GATE)
        throw new CleanupStoppedException(CleanupStopReason.BACKUP_GATE);
      var progress = repository.readLogProgress(run);
      CleanupCounts before;
      try {
        before =
            new CleanupCounts(
                progress.counts().target() - chunk.counts().target(),
                progress.counts().deleted() - chunk.counts().deleted(),
                progress.counts().skipped() - chunk.counts().skipped());
      } catch (IllegalArgumentException inconsistent) {
        throw new SQLDataException("chunk counters are inconsistent");
      }
      if (expectedBefore.isPresent() && !expectedBefore.orElseThrow().equals(before))
        throw new SQLDataException("chunk progress changed unexpectedly");
      result = new ChunkProgress(before, progress);
      mutation.check();
      c.commit();
      committed = true;
      mutation.check();
    } catch (SQLException | RuntimeException | Error failure) {
      if (committed) throw failure; // Caller disposes the connection; the chunk remains durable.
      try {
        c.rollback();
        c.setAutoCommit(true);
      } catch (SQLException | RuntimeException | Error cleanupFailure) {
        // SSC337/BUG2317: retain unknown primary identity, including a repeated same object.
        // Only fresh fixed diagnostics cross this borrowed-transaction recovery boundary.
        if (!known(failure)) {
          failure.addSuppressed(new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE));
          throw failure;
        }
        if (!known(cleanupFailure)) throw cleanupFailure;
        StorageIoException.preserveFatal(failure);
        StorageIoException.preserveFatal(cleanupFailure);
        throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
      }
      throw failure;
    }
    c.setAutoCommit(true);
    return result;
  }

  private static final class SessionLease implements AutoCloseable {
    private final Connection connection;
    private boolean acquired;

    SessionLease(Connection connection) {
      this.connection = connection;
    }

    void acquire() throws SQLException {
      var statement = connection.prepareStatement("select pg_try_advisory_lock(71419602) as held");
      @Nullable Throwable statementFailure = null;
      try {
        var row = statement.executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          if (!row.next()) throw new SQLDataException("lock result is missing");
          Boolean held = row.getObject("held", Boolean.class);
          if (held == null) throw new SQLDataException("lock result is missing");
          acquired = held;
          if (row.next()) throw new SQLDataException("lock result is ambiguous");
          if (!acquired) throw new CleanupStoppedException(CleanupStopReason.LOCK_BUSY);
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          try {
            row.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (replace(rowFailure, secondary)) throw secondary;
          }
        }
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        try {
          statement.close();
        } catch (SQLException | RuntimeException | Error secondary) {
          if (replace(statementFailure, secondary)) throw secondary;
        }
      }
    }

    @Override
    public void close() {
      if (!acquired) return;
      try {
        if (!connection.getAutoCommit())
          throw new SQLDataException("failed transaction requires connection disposal");
        var statement =
            connection.prepareStatement("select pg_advisory_unlock(71419602) as released");
        @Nullable Throwable statementFailure = null;
        try {
          var row = statement.executeQuery();
          @Nullable Throwable rowFailure = null;
          try {
            if (!row.next()
                || !Boolean.TRUE.equals(row.getObject("released", Boolean.class))
                || row.next()) throw new SQLDataException("lock release is unconfirmed");
          } catch (SQLException | RuntimeException | Error failure) {
            rowFailure = failure;
            throw failure;
          } finally {
            try {
              row.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (replace(rowFailure, secondary)) throw secondary;
            }
          }
        } catch (SQLException | RuntimeException | Error failure) {
          statementFailure = failure;
          throw failure;
        } finally {
          try {
            statement.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (replace(statementFailure, secondary)) throw secondary;
          }
        }
      } catch (SQLException failure) {
        StorageIoException.preserveFatal(failure);
        throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
      }
    }
  }
}
