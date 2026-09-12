package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.batch.repository.*;
import java.sql.*;
import java.util.Objects;
import java.util.Optional;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * NK-BAT-001; OPS-009/DAT-009; UI251; SS341§3/7.2; SSC-051; PG-D-138; PT-BAT-018..029. Borrows the
 * parent's single-owner connection; caller MUST discard/close it after any failure. Does not
 * certify OS flock, actual backup files, inactive applications or whole morning sequence.
 */
@NullMarked
public final class LogCleanupService {
  private static final long LIMIT_NANOS = 1_800_000_000_000L;
  private final LongSupplier clock;

  public LogCleanupService() {
    this(System::nanoTime);
  }

  LogCleanupService(LongSupplier clock) {
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  public LogCleanupSummary execute(Connection connection, BatchRun run) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(run, "run");
    long start = clock.getAsLong();
    check(start);
    try {
      if (!connection.getAutoCommit())
        throw new IllegalArgumentException("parent connection must be between transactions");
      try (var lease = new SessionLease(connection)) {
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
      }
    } catch (CleanupStoppedException failure) {
      // BUG-145/YKT-113: resource closure can append raw JDBC suppressed diagnostics.
      throw new CleanupStoppedException(failure.reason());
    } catch (SQLException | BatchRepositoryException failure) {
      throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
    }
  }

  private void check(long start) {
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

  private static ChunkProgress transaction(
      Connection c, BatchRun run, Optional<CleanupCounts> expectedBefore) throws SQLException {
    c.setAutoCommit(false);
    ChunkProgress result;
    try {
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
      c.commit();
    } catch (SQLException | RuntimeException failure) {
      try {
        c.rollback();
      } catch (SQLException rollbackFailure) {
        throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
      }
      c.setAutoCommit(true);
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
      try (var statement =
              connection.prepareStatement("select pg_try_advisory_lock(71419602) as held");
          var row = statement.executeQuery()) {
        if (!row.next()) throw new SQLDataException("lock result is missing");
        Boolean held = row.getObject("held", Boolean.class);
        if (held == null) throw new SQLDataException("lock result is missing");
        acquired = held;
        if (row.next()) throw new SQLDataException("lock result is ambiguous");
        if (!acquired) throw new CleanupStoppedException(CleanupStopReason.LOCK_BUSY);
      }
    }

    @Override
    public void close() {
      if (!acquired) return;
      try {
        if (!connection.getAutoCommit())
          throw new SQLDataException("failed transaction requires connection disposal");
        try (var statement =
                connection.prepareStatement("select pg_advisory_unlock(71419602) as released");
            var row = statement.executeQuery()) {
          if (!row.next()
              || !Boolean.TRUE.equals(row.getObject("released", Boolean.class))
              || row.next()) throw new SQLDataException("lock release is unconfirmed");
        }
      } catch (SQLException failure) {
        throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
      }
    }
  }
}
