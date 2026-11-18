package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.ZoneOffset;
import java.util.Objects;
import java.util.Optional;
import javax.annotation.WillClose;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed transaction; only caller commits/rolls back the atomic DELETE plus stored step counts.
 * NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT162..169.
 */
@NullMarked
public final class CleanupStepRepository {
  private final Connection connection;
  private final RunReferenceRepository references;

  public CleanupStepRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "parent connection");
    references = new RunReferenceRepository(connection);
  }

  public CleanupStepChunk execute(BatchStepAttempt attempt, CleanupKind kind, int limit) {
    CleanupStepChunk.requireMapping(attempt, kind);
    if (limit < 1 || limit > 1000) throw new IllegalArgumentException("invalid step cleanup limit");
    try {
      require(references.read(attempt.run()).identityConsistent());
      CleanupStepChunk result;
      var statement =
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,step_target_count,step_success_count,complete,reason_code"
                  + " from schubert.maintenance_execute_cleanup_step(?,?,?,?,?,?,?)");
      @Nullable Throwable statementFailure = null;
      try {
        var query = present(statement);
        query.setQueryTimeout(5);
        query.setObject(1, attempt.run().id());
        query.setObject(2, attempt.run().cutoff().atOffset(ZoneOffset.UTC));
        query.setLong(3, attempt.id());
        query.setInt(4, attempt.attempt());
        query.setObject(5, attempt.startedAt().atOffset(ZoneOffset.UTC));
        query.setString(6, kind.name());
        query.setInt(7, limit);
        var rows = query.executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          var row = present(rows);
          require(row.next());
          var counts =
              counts(
                  present(row.getObject("target_count", Long.class)),
                  present(row.getObject("deleted_count", Long.class)),
                  present(row.getObject("skipped_count", Long.class)));
          require(counts.target() <= limit);
          Long target = row.getObject("step_target_count", Long.class);
          Long deleted = row.getObject("step_success_count", Long.class);
          require((target == null) == (deleted == null));
          Optional<CleanupCounts> total =
              target == null ? Optional.empty() : Optional.of(counts(target, present(deleted), 0));
          boolean complete = present(row.getObject("complete", Boolean.class));
          String reasonCode = present(row.getString("reason_code"));
          try {
            var reason = CleanupStepChunk.Reason.valueOf(reasonCode);
            result = new CleanupStepChunk(attempt, kind, counts, total, complete, reason);
          } catch (IllegalArgumentException invalid) {
            throw new SQLDataException("step cleanup projection invalid");
          }
          require(!row.next());
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          closeRows(rows, rowFailure);
        }
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        closeStatement(statement, statementFailure);
      }
      require(references.read(attempt.run()).identityConsistent());
      return result;
    } catch (SQLException failure) {
      JdbcFailureGraph.preserveFatal(failure);
      throw new BatchRepositoryException();
    }
  }

  private static void closeRows(@WillClose @Nullable ResultSet rows, @Nullable Throwable primary)
      throws SQLException {
    if (rows == null) return;
    try {
      rows.close();
    } catch (SQLException | RuntimeException | Error secondary) {
      if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
    }
  }

  private static void closeStatement(
      @WillClose @Nullable PreparedStatement statement, @Nullable Throwable primary)
      throws SQLException {
    if (statement == null) return;
    try {
      statement.close();
    } catch (SQLException | RuntimeException | Error secondary) {
      if (JdbcResourceFailures.replace(primary, secondary)) throw secondary;
    }
  }

  private static CleanupCounts counts(long target, long deleted, long skipped)
      throws SQLDataException {
    try {
      return new CleanupCounts(target, deleted, skipped);
    } catch (IllegalArgumentException invalid) {
      throw new SQLDataException("step cleanup counts invalid");
    }
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("step cleanup projection missing");
    return value;
  }

  private static void require(boolean good) throws SQLDataException {
    if (!good) throw new SQLDataException("step cleanup contract failed");
  }
}
