package dev.codex.schubert.nk.batch.repository;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed parent transaction. Caller retains OS/root/child safety and commits only after return.
 * NK-BAT-001/OPS009/DAT009/UI251/SS331 8.3/332/341; SSC055/PG163; BAT138..153.
 * PG-D-160/SSC056/BUG167/YKT128: UTC JDBC4.2, no legacy calendar conversion.
 */
@NullMarked
public final class BatchRunRepository {
  private static final java.lang.String LITERAL_RUNNING = "RUNNING";

  private static final String RETAINED_HISTORY =
      "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count from schubert.batch_runs"
          + " where business_date=? and step=? order by attempt limit 100 for update";
  private static final String HANDLE =
      "id=? and run_id=? and business_date=? and step=? and attempt=? and started_at=?";
  private final Connection connection;
  private final RunReferenceRepository references;

  public BatchRunRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "parent connection");
    references = new RunReferenceRepository(connection);
  }

  public BatchStepAttempt begin(
      BatchRun run, BatchStep step, Instant now, boolean recoverAbandoned) {
    return begin(run, step, now, recoverAbandoned, false, false);
  }

  /** SSC116: normal resume, not SSC054 manual Backup regeneration. */
  public BatchStepAttempt beginMorningResume(
      BatchRun run, BatchStep step, Instant now, boolean recoverAbandoned) {
    return begin(run, step, now, recoverAbandoned, true, false);
  }

  /** SSC124: actual SKIP insertion for six fixed deletions; caller authenticates failed Backup. */
  public BatchStepAttempt beginBackupUnavailable(
      BatchRun run, BatchStep step, Instant now, boolean recoverAbandoned) {
    Objects.requireNonNull(step, "fixed deletion step");
    if (!Set.of(
            BatchStep.CLEAN_NOTIFICATION,
            BatchStep.CLEAN_QUESTION,
            BatchStep.CLEAN_SESSION,
            BatchStep.CLEAN_INBOX_OUTBOX,
            BatchStep.CLEAN_LOG,
            BatchStep.CLEAN_BATCH_RUN)
        .contains(step)) throw new IllegalArgumentException("backup-dependent deletion required");
    return begin(run, step, now, recoverAbandoned, false, true);
  }

  private BatchStepAttempt begin(
      BatchRun run,
      BatchStep step,
      Instant now,
      boolean recoverAbandoned,
      boolean morningResume,
      boolean backupUnavailable) {
    Objects.requireNonNull(run, "fixed run");
    Objects.requireNonNull(step, "step");
    Objects.requireNonNull(now, "step time");
    BatchStepAttempt.time(run, now);
    try {
      guarded(run);
      LocalDate day = run.cutoff().atZone(ZoneId.of("Asia/Tokyo")).toLocalDate();
      List<History> history = history(run, step, day, now);
      int maximum = history.isEmpty() ? 0 : history.getLast().attempt();
      require(maximum < 99);
      List<History> running =
          history.stream().filter(h -> h.status().equals(LITERAL_RUNNING)).toList();
      require(running.isEmpty() || recoverAbandoned);
      for (History row : running) require(row.runId().equals(run.id()));
      long successes = history.stream().filter(h -> h.status().equals("SUCCESS")).count();
      require(step.backup() || successes <= 1);
      // Validate the whole set before changing any old attempt.
      for (History row : running) abandon(row, now);
      // Backup's multi-SUCCESS manual history is retained. Normal resume may only reuse
      // the exact original run; the caller independently verifies the complete bundle pair.
      boolean skipped =
          backupUnavailable
              || (!step.backup() && successes != 0)
              || (morningResume
                  && step.backup()
                  && history.stream()
                      .anyMatch(h -> h.status().equals("SUCCESS") && h.runId().equals(run.id())));
      BatchStepAttempt result =
          insert(
              run,
              step,
              day,
              maximum + 1,
              now,
              skipped,
              backupUnavailable
                  ? BatchStepResult.Reason.BACKUP_UNAVAILABLE
                  : skipped
                      ? BatchStepResult.Reason.ALREADY_SUCCESSFUL
                      : BatchStepResult.Reason.NONE);
      guarded(run);
      return result;
    } catch (SQLException failure) {
      throw new BatchRepositoryException();
    }
  }

  public void finish(BatchStepAttempt attempt, Instant endedAt, BatchStepResult result) {
    Objects.requireNonNull(attempt, "step attempt");
    Objects.requireNonNull(endedAt, "step end");
    Objects.requireNonNull(result, "step result");
    BatchStepAttempt.time(attempt.run(), endedAt);
    if (attempt.skipped() || endedAt.isBefore(attempt.startedAt()))
      throw new IllegalArgumentException("invalid batch step completion");
    try {
      guarded(attempt.run());
      int changed;
      var query =
          connection.prepareStatement(
              "update schubert.batch_runs set ended_at=?,status=?,target_count=?,success_count=?,"
                  + "failure_count=?,byte_count=?,error_code=?,error_summary=? where "
                  + HANDLE
                  + " and status='RUNNING' and ended_at is null");
      if (query == null) throw missingProjection();
      @Nullable Throwable statementFailure = null;
      try {
        query.setQueryTimeout(5);
        bindResult(query, endedAt, result);
        bindHandle(query, 9, attempt);
        changed = query.executeUpdate();
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        closeStatement(query, statementFailure);
      }
      require(changed == 0 || changed == 1);
      if (changed == 0) require(replayed(attempt, endedAt, result));
      guarded(attempt.run());
    } catch (SQLException failure) {
      throw new BatchRepositoryException();
    }
  }

  /** Independent readback only; never updates a RUNNING row to make a check pass. PG379. */
  public void verifyFinished(BatchStepAttempt attempt, Instant endedAt, BatchStepResult result) {
    Objects.requireNonNull(attempt, "step attempt");
    Objects.requireNonNull(endedAt, "step end");
    Objects.requireNonNull(result, "step result");
    BatchStepAttempt.time(attempt.run(), endedAt);
    if (attempt.skipped() || endedAt.isBefore(attempt.startedAt()))
      throw new IllegalArgumentException("invalid batch step observation");
    try {
      guarded(attempt.run());
      require(replayed(attempt, endedAt, result));
      guarded(attempt.run());
    } catch (SQLException failure) {
      throw new BatchRepositoryException();
    }
  }

  /** Exact independent current SKIP readback; never reads the prior SUCCESS as this result. */
  public void verifyAlreadySuccessful(BatchStepAttempt attempt) {
    Objects.requireNonNull(attempt, "current skipped attempt");
    if (!attempt.skipped()) throw new IllegalArgumentException("current skip required");
    try {
      guarded(attempt.run());
      require(
          replayed(
              attempt,
              attempt.startedAt(),
              new BatchStepResult(
                  BatchStepResult.Status.SKIPPED,
                  0,
                  0,
                  0,
                  0,
                  BatchStepResult.Reason.ALREADY_SUCCESSFUL)));
      guarded(attempt.run());
    } catch (SQLException failure) {
      throw new BatchRepositoryException();
    }
  }

  /** Current saved SKIP only; no previous SUCCESS or simulated producer is substituted. */
  public void verifyBackupUnavailable(BatchStepAttempt attempt) {
    Objects.requireNonNull(attempt, "actual skipped deletion");
    if (!attempt.skipped()) throw new IllegalArgumentException("current skip required");
    try {
      guarded(attempt.run());
      require(
          replayed(
              attempt,
              attempt.startedAt(),
              new BatchStepResult(
                  BatchStepResult.Status.SKIPPED,
                  0,
                  0,
                  0,
                  0,
                  BatchStepResult.Reason.BACKUP_UNAVAILABLE)));
      guarded(attempt.run());
    } catch (SQLException invalid) {
      throw new BatchRepositoryException();
    }
  }

  private List<History> history(BatchRun run, BatchStep step, LocalDate day, Instant now)
      throws SQLException {
    List<History> result = new ArrayList<>();
    Set<Long> ids = new HashSet<>();
    int previous = 0;
    var query = connection.prepareStatement(RETAINED_HISTORY);
    if (query == null) throw missingProjection();
    @Nullable Throwable statementFailure = null;
    try {
      query.setQueryTimeout(5);
      query.setObject(1, day);
      query.setString(2, step.name());
      var row = query.executeQuery();
      if (row == null) throw missingProjection();
      @Nullable Throwable rowFailure = null;
      try {
        while (row.next()) {
          require(result.size() < 99);
          long id = present(row.getObject("id", Long.class));
          UUID runId = present(row.getObject("run_id", UUID.class));
          LocalDate date = present(row.getObject("business_date", LocalDate.class));
          String rowStep = present(row.getString("step"));
          int number = present(row.getObject("attempt", Integer.class));
          Instant start = present(row.getObject("started_at", OffsetDateTime.class)).toInstant();
          OffsetDateTime endValue = row.getObject("ended_at", OffsetDateTime.class);
          @Nullable Instant end = endValue == null ? null : endValue.toInstant();
          String status = present(row.getString("status"));
          long target = present(row.getObject("target_count", Long.class));
          long success = present(row.getObject("success_count", Long.class));
          long failure = present(row.getObject("failure_count", Long.class));
          long bytes = present(row.getObject("byte_count", Long.class));
          require(id >= 1 && id <= 999999999999L && ids.add(id));
          require(date.equals(day) && rowStep.equals(step.name()));
          require(number > previous && number <= 99);
          require(
              Set.of(LITERAL_RUNNING, "SUCCESS", "WARNING", "FAILED", "SKIPPED").contains(status));
          require(target >= 0 && success >= 0 && failure >= 0 && bytes >= 0);
          validStoredTime(start, now);
          if (runId.equals(run.id())) require(!start.isBefore(run.cutoff()));
          if (status.equals(LITERAL_RUNNING)) {
            require(end == null);
          } else {
            require(end != null);
            Instant checkedEnd = present(end);
            validStoredTime(checkedEnd, now);
            require(!checkedEnd.isBefore(start));
          }
          result.add(new History(id, runId, number, start, status));
          previous = number;
        }
      } catch (SQLException | RuntimeException | Error failure) {
        rowFailure = failure;
        throw failure;
      } finally {
        closeRows(row, rowFailure);
      }
    } catch (SQLException | RuntimeException | Error failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(query, statementFailure);
    }
    return List.copyOf(result);
  }

  private void abandon(History row, Instant now) throws SQLException {
    var query =
        connection.prepareStatement(
            "update schubert.batch_runs set status='FAILED',ended_at=?,error_code=?,error_summary=?"
                + " where id=? and run_id=? and started_at=? and status='RUNNING' and ended_at is null");
    if (query == null) throw missingProjection();
    @Nullable Throwable statementFailure = null;
    try {
      query.setQueryTimeout(5);
      query.setObject(1, now.atOffset(ZoneOffset.UTC));
      query.setString(2, BatchStepResult.Reason.ABANDONED.code());
      query.setString(3, BatchStepResult.Reason.ABANDONED.summary());
      query.setLong(4, row.id());
      query.setObject(5, row.runId());
      query.setObject(6, row.started().atOffset(ZoneOffset.UTC));
      require(query.executeUpdate() == 1);
    } catch (SQLException | RuntimeException | Error failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(query, statementFailure);
    }
  }

  private BatchStepAttempt insert(
      BatchRun run,
      BatchStep step,
      LocalDate day,
      int attempt,
      Instant now,
      boolean skipped,
      BatchStepResult.Reason reason)
      throws SQLException {
    BatchStepAttempt result;
    var query =
        connection.prepareStatement(
            "insert into schubert.batch_runs(run_id,business_date,step,attempt,started_at,ended_at,"
                + "status,target_count,success_count,failure_count,byte_count,error_code,error_summary)"
                + " values(?,?,?,?,?,?,?,0,0,0,0,?,?) returning id");
    if (query == null) throw missingProjection();
    @Nullable Throwable statementFailure = null;
    try {
      query.setQueryTimeout(5);
      query.setObject(1, run.id());
      query.setObject(2, day);
      query.setString(3, step.name());
      query.setInt(4, attempt);
      query.setObject(5, now.atOffset(ZoneOffset.UTC));
      query.setObject(6, skipped ? now.atOffset(ZoneOffset.UTC) : null);
      query.setString(7, skipped ? "SKIPPED" : LITERAL_RUNNING);
      query.setString(8, reason.code());
      query.setString(9, reason.summary());
      var row = query.executeQuery();
      if (row == null) throw missingProjection();
      @Nullable Throwable rowFailure = null;
      try {
        require(row.next());
        long id = present(row.getObject("id", Long.class));
        try {
          result = new BatchStepAttempt(id, run, step, attempt, now, skipped);
        } catch (IllegalArgumentException invalid) {
          throw new SQLDataException("batch step projection invalid");
        }
        require(!row.next());
      } catch (SQLException | RuntimeException | Error failure) {
        rowFailure = failure;
        throw failure;
      } finally {
        closeRows(row, rowFailure);
      }
    } catch (SQLException | RuntimeException | Error failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(query, statementFailure);
    }
    return result;
  }

  private boolean replayed(BatchStepAttempt attempt, Instant ended, BatchStepResult result)
      throws SQLException {
    boolean matches;
    var query =
        connection.prepareStatement(
            "select exists(select 1 from schubert.batch_runs where ended_at=? and status=?"
                + " and target_count=? and success_count=? and failure_count=? and byte_count=?"
                + " and error_code is not distinct from ? and error_summary is not distinct from ?"
                + " and "
                + HANDLE
                + ") as matches");
    if (query == null) throw missingProjection();
    @Nullable Throwable statementFailure = null;
    try {
      query.setQueryTimeout(5);
      bindResult(query, ended, result);
      bindHandle(query, 9, attempt);
      var row = query.executeQuery();
      if (row == null) throw missingProjection();
      @Nullable Throwable rowFailure = null;
      try {
        require(row.next());
        matches = present(row.getObject("matches", Boolean.class));
        require(!row.next());
      } catch (SQLException | RuntimeException | Error failure) {
        rowFailure = failure;
        throw failure;
      } finally {
        closeRows(row, rowFailure);
      }
    } catch (SQLException | RuntimeException | Error failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      closeStatement(query, statementFailure);
    }
    return matches;
  }

  private static void closeStatement(PreparedStatement query, @Nullable Throwable primary)
      throws SQLException {
    try {
      query.close();
    } catch (SQLException | RuntimeException | Error cleanup) {
      if (JdbcResourceFailures.replace(primary, cleanup)) throw cleanup;
    }
  }

  private static void closeRows(ResultSet rows, @Nullable Throwable primary) throws SQLException {
    try {
      rows.close();
    } catch (SQLException | RuntimeException | Error cleanup) {
      if (JdbcResourceFailures.replace(primary, cleanup)) throw cleanup;
    }
  }

  private static void bindResult(PreparedStatement query, Instant ended, BatchStepResult result)
      throws SQLException {
    query.setObject(1, ended.atOffset(ZoneOffset.UTC));
    query.setString(2, result.status().name());
    query.setLong(3, result.target());
    query.setLong(4, result.success());
    query.setLong(5, result.failure());
    query.setLong(6, result.bytes());
    query.setString(7, result.reason().code());
    query.setString(8, result.reason().summary());
  }

  private static void bindHandle(PreparedStatement query, int offset, BatchStepAttempt attempt)
      throws SQLException {
    query.setLong(offset, attempt.id());
    query.setObject(offset + 1, attempt.run().id());
    query.setObject(offset + 2, attempt.businessDate());
    query.setString(offset + 3, attempt.step().name());
    query.setInt(offset + 4, attempt.attempt());
    query.setObject(offset + 5, attempt.startedAt().atOffset(ZoneOffset.UTC));
  }

  private void guarded(BatchRun run) throws SQLDataException {
    require(references.read(run).identityConsistent());
  }

  private static void validStoredTime(Instant value, Instant now) throws SQLDataException {
    require(!value.isBefore(Instant.parse("0001-01-01T00:00:00Z")));
    require(!value.isAfter(now));
    require(value.getNano() % 1000 == 0);
  }

  private static void require(boolean accepted) throws SQLDataException {
    if (!accepted) throw new SQLDataException("batch step contract failed");
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw missingProjection();
    return value;
  }

  private static SQLDataException missingProjection() {
    return new SQLDataException("batch step projection missing");
  }

  private record History(long id, UUID runId, int attempt, Instant started, String status) {
    @Override
    public String toString() {
      return "BatchStepHistory[identity/time=<redacted>]";
    }
  }
}
