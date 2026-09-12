package dev.codex.schubert.nk.batch.repository;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import java.sql.*;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed single-owner parent connection; no commit/rollback/close or new connection. NK-BAT-001;
 * DAT-009/OPS-009; UI251; SS311§7/332§11/341§3/7; SSC-051; PG-D-137; PT-BAT-005..016. Caller holds
 * OS/session advisory gates and MUST rollback failed chunks. Returned values remain uncommitted
 * until the caller commits. Never share this connection concurrently.
 */
@NullMarked
public final class CleanupRepository {
  private final Connection connection;

  public CleanupRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "connection");
  }

  public CleanupChunk execute(BatchRun run, CleanupKind kind, int maximumRows) {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(kind, "kind");
    if (maximumRows < 1 || maximumRows > kind.maximumRows())
      throw new IllegalArgumentException("cleanup limit is invalid");
    try {
      requireTransaction();
      try (var statement = prepare(kind)) {
        bind(statement, run);
        statement.setInt(3, maximumRows);
        try (var row = statement.executeQuery()) {
          if (!row.next()) throw new SQLDataException("cleanup result is missing");
          CleanupCounts counts = counts(row);
          if (counts.target() > maximumRows)
            throw new SQLDataException("cleanup result exceeds chunk bound");
          var result =
              new CleanupChunk(
                  counts, CleanupReason.valueOf(required(row.getString("reason_code"))));
          if (row.next()) throw new SQLDataException("cleanup result is ambiguous");
          return result;
        }
      }
    } catch (SQLException | IllegalArgumentException failure) {
      throw new BatchRepositoryException();
    }
  }

  public LogCleanupProgress readLogProgress(BatchRun run) {
    Objects.requireNonNull(run, "run");
    try {
      requireTransaction();
      try (var statement =
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,complete from schubert.maintenance_read_log_cleanup_progress(?,?)")) {
        bind(statement, run);
        try (var row = statement.executeQuery()) {
          if (!row.next()) throw new SQLDataException("log progress is missing");
          var result =
              new LogCleanupProgress(
                  run, counts(row), required(row.getObject("complete", Boolean.class)));
          if (row.next()) throw new SQLDataException("log progress is ambiguous");
          return result;
        }
      }
    } catch (SQLException | IllegalArgumentException failure) {
      throw new BatchRepositoryException();
    }
  }

  private PreparedStatement prepare(CleanupKind kind) throws SQLException {
    return switch (kind) {
      case NOTIFICATIONS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_notifications(?,?,?)");
      case QUESTIONS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_questions(?,?,?)");
      case SESSIONS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_sessions(?,?,?)");
      case OUTBOX ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_message_stores(?,?,?)");
      case LOGS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_logs(?,?,?)");
      case BATCH_RUNS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_batch_runs(?,?,?)");
      case INBOX_PROGRESS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_inbox_progress(?,?,?)");
      case LOG_PROGRESS ->
          connection.prepareStatement(
              "select target_count,deleted_count,skipped_count,reason_code from schubert.maintenance_cleanup_log_progress(?,?,?)");
    };
  }

  private void requireTransaction() throws SQLException {
    if (connection.getAutoCommit())
      throw new SQLDataException("explicit parent transaction required");
  }

  private static void bind(PreparedStatement statement, BatchRun run) throws SQLException {
    statement.setObject(1, run.id());
    statement.setObject(2, run.cutoff().atOffset(java.time.ZoneOffset.UTC));
  }

  private static CleanupCounts counts(ResultSet row) throws SQLException {
    return new CleanupCounts(
        required(row.getObject("target_count", Long.class)),
        required(row.getObject("deleted_count", Long.class)),
        required(row.getObject("skipped_count", Long.class)));
  }

  private static <T> T required(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("required cleanup column is missing");
    return value;
  }
}
