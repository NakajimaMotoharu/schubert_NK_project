package dev.codex.schubert.nk.batch.repository;

import java.sql.*;
import java.time.ZoneOffset;
import java.util.*;
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
      try (var statement =
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,step_target_count,step_success_count,complete,reason_code"
                  + " from schubert.maintenance_execute_cleanup_step(?,?,?,?,?,?,?)")) {
        var query = present(statement);
        query.setQueryTimeout(5);
        query.setObject(1, attempt.run().id());
        query.setObject(2, attempt.run().cutoff().atOffset(ZoneOffset.UTC));
        query.setLong(3, attempt.id());
        query.setInt(4, attempt.attempt());
        query.setObject(5, attempt.startedAt().atOffset(ZoneOffset.UTC));
        query.setString(6, kind.name());
        query.setInt(7, limit);
        try (var rows = query.executeQuery()) {
          var row = present(rows);
          require(row.next());
          var counts =
              new CleanupCounts(
                  present(row.getObject("target_count", Long.class)),
                  present(row.getObject("deleted_count", Long.class)),
                  present(row.getObject("skipped_count", Long.class)));
          require(counts.target() <= limit);
          Long target = row.getObject("step_target_count", Long.class),
              deleted = row.getObject("step_success_count", Long.class);
          require((target == null) == (deleted == null));
          Optional<CleanupCounts> total =
              target == null
                  ? Optional.empty()
                  : Optional.of(new CleanupCounts(target, present(deleted), 0));
          boolean complete = present(row.getObject("complete", Boolean.class));
          var reason = CleanupStepChunk.Reason.valueOf(present(row.getString("reason_code")));
          result = new CleanupStepChunk(attempt, kind, counts, total, complete, reason);
          require(!row.next());
        }
      }
      require(references.read(attempt.run()).identityConsistent());
      return result;
    } catch (SQLException | IllegalArgumentException failure) {
      throw new BatchRepositoryException();
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
