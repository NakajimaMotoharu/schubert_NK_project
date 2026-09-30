package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.sql.*;
import java.time.*;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Independent seven-step full-column readback after genuine Cleanup receipt and DB reacquisition.
 * Data only, never Unit/OS/root/Epoch authority. NK-BAT-001/OPS009/DAT009/UI251/SS331/341/343/
 * SSC119; PT-OPS-CEXEC001. Borrowed transaction is never committed/closed/configured here.
 */
@NullMarked
public final class CleanupTerminalRepository {
  public static final List<BatchStep> STEPS =
      List.of(
          BatchStep.CLEAN_NOTIFICATION,
          BatchStep.CLEAN_QUESTION,
          BatchStep.CLEAN_SESSION,
          BatchStep.CLEAN_INBOX_OUTBOX,
          BatchStep.CLEAN_LOG,
          BatchStep.CLEAN_BATCH_RUN,
          BatchStep.CLEAN_TRANSFER);
  private static final String SQL =
      "select distinct on(step) id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
          + " from schubert.batch_runs where run_id=? and business_date=? and step in"
          + " ('CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX',"
          + "'CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER') order by step,attempt desc";

  public record Entry(BatchStepAttempt attempt, Instant endedAt, BatchStepResult result) {
    public Entry {
      Objects.requireNonNull(attempt, "current step");
      Objects.requireNonNull(endedAt, "actual terminal time");
      Objects.requireNonNull(result, "actual terminal result");
      if (!STEPS.contains(attempt.step())
          || endedAt.isBefore(attempt.startedAt())
          || endedAt.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
          || endedAt.getNano() % 1000 != 0
          || result.status() == BatchStepResult.Status.FAILED)
        throw new IllegalArgumentException("Cleanup terminal invalid");
    }
  }

  public record Snapshot(List<Entry> entries) {
    public Snapshot {
      entries = List.copyOf(entries);
      if (entries.size() != STEPS.size())
        throw new IllegalArgumentException("Cleanup terminal incomplete");
      var ids = new HashSet<Long>();
      var run = entries.getFirst().attempt().run();
      for (int index = 0; index < STEPS.size(); index++) {
        var attempt = entries.get(index).attempt();
        if (attempt.step() != STEPS.get(index)
            || !attempt.run().equals(run)
            || !ids.add(attempt.id()))
          throw new IllegalArgumentException("Cleanup terminal inconsistent");
      }
    }

    public int exitCode() {
      return entries.stream()
              .anyMatch(row -> row.result().status() == BatchStepResult.Status.WARNING)
          ? 10
          : 0;
    }

    @Override
    public String toString() {
      return "CleanupTerminalSnapshot[data=<redacted>]";
    }
  }

  private final Connection connection;
  private final MaintenanceOwnerFrame.Guard guard;

  public CleanupTerminalRepository(Connection connection, MaintenanceOwnerFrame.Guard guard) {
    this.connection = Objects.requireNonNull(connection, "reacquired parent transaction");
    this.guard = Objects.requireNonNull(guard, "actual parent deadline");
  }

  public Snapshot read(BatchRun run, Instant observedAt) {
    Objects.requireNonNull(run, "same original run");
    Objects.requireNonNull(observedAt, "actual UTC readback time");
    BatchStepAttempt.time(run, observedAt);
    try {
      check(run);
      var values = new EnumMap<BatchStep, Entry>(BatchStep.class);
      try (var statement = connection.prepareStatement(SQL)) {
        var query = present(statement);
        query.setQueryTimeout(seconds());
        query.setObject(1, run.id());
        query.setObject(2, run.cutoff().atZone(ZoneId.of("Asia/Tokyo")).toLocalDate());
        try (var rows = query.executeQuery()) {
          var row = present(rows);
          while (row.next()) {
            require(values.size() < STEPS.size());
            var step = BatchStep.valueOf(present(row.getString("step")));
            require(STEPS.contains(step));
            var started = present(row.getObject("started_at", OffsetDateTime.class)).toInstant();
            var ended = present(row.getObject("ended_at", OffsetDateTime.class)).toInstant();
            require(
                !ended.isAfter(observedAt)
                    && run.id().equals(row.getObject("run_id", UUID.class))
                    && run.cutoff()
                        .atZone(ZoneId.of("Asia/Tokyo"))
                        .toLocalDate()
                        .equals(row.getObject("business_date", LocalDate.class)));
            var status = BatchStepResult.Status.valueOf(present(row.getString("status")));
            var code = row.getString("error_code");
            var reason =
                code == null ? BatchStepResult.Reason.NONE : BatchStepResult.Reason.valueOf(code);
            var result =
                new BatchStepResult(
                    status,
                    present(row.getObject("target_count", Long.class)),
                    present(row.getObject("success_count", Long.class)),
                    present(row.getObject("failure_count", Long.class)),
                    present(row.getObject("byte_count", Long.class)),
                    reason);
            require(Objects.equals(result.reason().summary(), row.getString("error_summary")));
            var attempt =
                new BatchStepAttempt(
                    present(row.getObject("id", Long.class)),
                    run,
                    step,
                    present(row.getObject("attempt", Integer.class)),
                    started,
                    reason == BatchStepResult.Reason.ALREADY_SUCCESSFUL);
            var entry = new Entry(attempt, ended, result);
            require(values.put(step, entry) == null);
          }
        }
      }
      var ordered = new ArrayList<Entry>();
      for (var step : STEPS) ordered.add(present(values.get(step)));
      var snapshot = new Snapshot(ordered);
      check(run);
      return snapshot;
    } catch (SQLException | IllegalArgumentException known) {
      throw new BatchRepositoryException();
    }
  }

  private void check(BatchRun run) throws SQLException {
    seconds();
    require(
        !connection.getAutoCommit()
            && !connection.isReadOnly()
            && connection.getTransactionIsolation() == Connection.TRANSACTION_READ_COMMITTED
            && new RunReferenceRepository(connection).read(run).identityConsistent());
    seconds();
  }

  private int seconds() throws SQLException {
    try {
      return guard.queryTimeoutSeconds();
    } catch (IOException known) {
      throw new SQLDataException("Cleanup readback owner unavailable");
    }
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("Cleanup terminal projection missing");
    return value;
  }

  private static void require(boolean valid) throws SQLDataException {
    if (!valid) throw new SQLDataException("Cleanup terminal projection unavailable");
  }
}
