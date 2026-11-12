package dev.codex.schubert.nk.batch.cleanup;

import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupKind;
import dev.codex.schubert.nk.batch.repository.CleanupStepChunk;
import dev.codex.schubert.nk.batch.repository.CleanupStepRepository;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.Connection;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;
import java.util.function.LongSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Bounded committed chunks under caller's continuous OS/session lock and verified backups. Failure
 * requires connection disposal; no implicit restart, no parent finish or guessed counts.
 * NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT170..177.
 */
@NullMarked
public final class StepCleanupService {
  private static final long LIMIT_NANOS = 1_800_000_000_000L;
  private final LongSupplier clock;
  private final MaintenanceMutationGuard mutation;

  public StepCleanupService() {
    this(System::nanoTime);
  }

  StepCleanupService(LongSupplier clock) {
    this.clock = Objects.requireNonNull(clock, "clock");
    mutation = new MaintenanceMutationGuard();
  }

  public static StepCleanupService withOwner(
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner) {
    return new StepCleanupService(new MaintenanceMutationGuard(owner));
  }

  private StepCleanupService(MaintenanceMutationGuard mutation) {
    clock = System::nanoTime;
    this.mutation = mutation;
  }

  public StepCleanupSummary execute(
      Connection connection, BatchStepAttempt attempt, CleanupKind kind) {
    Objects.requireNonNull(connection, "parent connection");
    CleanupStepChunk.requireMapping(attempt, kind);
    long start = clock.getAsLong();
    check(start);
    try {
      if (!connection.getAutoCommit()
          || connection.isReadOnly()
          || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED)
        throw new IllegalArgumentException("invalid parent connection state");
      Optional<CleanupCounts> expected = Optional.empty();
      Optional<CleanupCounts> initial = Optional.empty();
      while (true) {
        check(start);
        CleanupStepChunk chunk = transaction(connection, attempt, kind, expected);
        check(start);
        CleanupCounts before = chunk.beforeCounts().orElseThrow();
        CleanupCounts after = chunk.stepCounts().orElseThrow();
        if (initial.isEmpty()) initial = Optional.of(before);
        boolean deferred = chunk.reason() == CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT;
        if (chunk.complete() || deferred)
          return new StepCleanupSummary(attempt, kind, initial.orElseThrow(), after, deferred);
        expected = Optional.of(after);
      }
    } catch (CleanupStoppedException failure) {
      StorageIoException.preserveFatal(failure);
      throw new CleanupStoppedException(failure.reason());
    } catch (SQLException | BatchRepositoryException failure) {
      StorageIoException.preserveFatal(failure);
      throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
    }
  }

  private CleanupStepChunk transaction(
      Connection c, BatchStepAttempt attempt, CleanupKind kind, Optional<CleanupCounts> expected)
      throws SQLException {
    CleanupStepChunk chunk;
    boolean committed = false;
    mutation.check(); // BUG363: no transaction exists yet; refusal must never attempt rollback.
    try {
      c.setAutoCommit(false);
      mutation.bind(c);
      mutation.check();
      chunk = new CleanupStepRepository(c).execute(attempt, kind, 1000);
      if (chunk.reason() == CleanupStepChunk.Reason.LOCK_BUSY)
        throw new CleanupStoppedException(CleanupStopReason.LOCK_BUSY);
      if (chunk.reason() == CleanupStepChunk.Reason.BACKUP_GATE)
        throw new CleanupStoppedException(CleanupStopReason.BACKUP_GATE);
      if (expected.isPresent() && !expected.equals(chunk.beforeCounts()))
        throw new SQLDataException("step cleanup counters changed unexpectedly");
      mutation.check();
      c.commit();
      committed = true;
      mutation.check();
    } catch (SQLException | RuntimeException | Error failure) {
      if (committed) throw failure; // Durable chunks are NOT represented as rolled back.
      try {
        c.rollback();
        c.setAutoCommit(true);
      } catch (SQLException | RuntimeException | Error cleanupFailure) {
        // BUG181/YKT142: classify without replacing/narrowing the original rethrow identity.
        if (failure instanceof Error
            || (failure instanceof RuntimeException
                && !(failure instanceof BatchRepositoryException)
                && !(failure instanceof CleanupStoppedException))) {
          failure.addSuppressed(new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE));
          throw failure;
        }
        if (cleanupFailure instanceof Error fatal) throw fatal;
        if (cleanupFailure instanceof RuntimeException
            && !(cleanupFailure instanceof BatchRepositoryException)
            && !(cleanupFailure instanceof CleanupStoppedException)) throw cleanupFailure;
        StorageIoException.preserveFatal(failure);
        StorageIoException.preserveFatal(cleanupFailure);
        throw new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
      }
      throw failure;
    }
    c.setAutoCommit(true);
    return chunk;
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
}
