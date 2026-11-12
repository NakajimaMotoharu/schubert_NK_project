package dev.codex.schubert.nk.batch.backup;

import dev.codex.schubert.nk.batch.repository.BackupStepRepository;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Atomic two-step completion only. Caller supplies verified root artifact/continuous OS lock and
 * disposes borrowed connection on any failure. Never authenticates an arbitrary manifest value.
 * NK-BAT-001/BAK/BKO/OPS009/UI251/SS331 8.3/341 6.6/343; SSC061/PG168; BAT218..225.
 */
@NullMarked
public final class BackupCommitService {
  public Instant complete(Connection connection, BackupManifest manifest, Instant endedAt) {
    Objects.requireNonNull(connection, "parent connection");
    Objects.requireNonNull(manifest, "genuine backup manifest");
    Objects.requireNonNull(endedAt, "completion observation");
    try {
      interrupted();
      if (!connection.getAutoCommit()
          || connection.isReadOnly()
          || connection.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED)
        throw new BatchRepositoryException();
      Instant stored;
      try {
        connection.setAutoCommit(false);
        stored = new BackupStepRepository(connection).complete(manifest, endedAt);
        interrupted();
        connection.commit();
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          connection.rollback();
          connection.setAutoCommit(true);
        } catch (SQLException | RuntimeException | Error cleanupFailure) {
          if (failure instanceof Error
              || (failure instanceof RuntimeException
                  && !(failure instanceof BatchRepositoryException))) {
            failure.addSuppressed(new BatchRepositoryException());
            throw failure;
          }
          if (cleanupFailure instanceof Error fatal) throw fatal;
          if (cleanupFailure instanceof RuntimeException
              && !(cleanupFailure instanceof BatchRepositoryException)) throw cleanupFailure;
          StorageIoException.preserveFatal(failure);
          StorageIoException.preserveFatal(cleanupFailure);
          throw new BatchRepositoryException();
        }
        throw failure;
      }
      connection.setAutoCommit(true);
      interrupted();
      return stored;
    } catch (SQLException | BatchRepositoryException failure) {
      StorageIoException.preserveFatal(failure);
      throw new BatchRepositoryException();
    }
  }

  private static void interrupted() {
    if (Thread.currentThread().isInterrupted()) throw new BatchRepositoryException();
  }
}
