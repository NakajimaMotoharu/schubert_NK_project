package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.api.bootstrap.JdbcFailureGraph;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
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
import java.util.EnumMap;
import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Independent seven-step full-column readback after genuine Cleanup receipt and DB reacquisition.
 * Data only, never Unit/OS/root/Epoch authority. NK-BAT-001/OPS009/DAT009/UI251/SS331/341/343/
 * SSC119/199, SS332; PT-OPS-CEXEC001/CTERM006..009. Borrowed transaction is never
 * committed/closed/configured here.
 */
@NullMarked
public final class CleanupTerminalRepository {
  private static final java.lang.String LITERAL_ASIA_TOKYO = "Asia/Tokyo";

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

  public record Entry(
      BatchStepAttempt attempt,
      Instant endedAt,
      BatchStepResult result,
      Optional<String> progressSeal) {
    public Entry(BatchStepAttempt attempt, Instant endedAt, BatchStepResult result) {
      this(attempt, endedAt, result, Optional.empty());
    }

    public Entry {
      Objects.requireNonNull(attempt, "current step");
      Objects.requireNonNull(endedAt, "actual terminal time");
      Objects.requireNonNull(result, "actual terminal result");
      Objects.requireNonNull(progressSeal, "retained progress seal");
      if (progressSeal.isPresent()
          && (!progressSeal.orElseThrow().matches("[0-9a-f]{64}")
              || (attempt.step() != BatchStep.CLEAN_LOG
                  && attempt.step() != BatchStep.CLEAN_INBOX_OUTBOX)
              || attempt.skipped()
              || result.status() != BatchStepResult.Status.SUCCESS))
        throw new IllegalArgumentException("Cleanup progress seal invalid");
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

  /** Actual latest stored row only. Empty terminal means RUNNING with verified all-zero counts. */
  public record RejectedEntry(
      BatchStepAttempt attempt, Optional<Instant> endedAt, Optional<BatchStepResult> result) {
    public RejectedEntry {
      Objects.requireNonNull(attempt);
      Objects.requireNonNull(endedAt);
      Objects.requireNonNull(result);
      if (!STEPS.contains(attempt.step()) || endedAt.isPresent() != result.isPresent())
        throw new IllegalArgumentException("Cleanup rejection row invalid");
      if (endedAt.isPresent()) {
        BatchStepAttempt.time(attempt.run(), endedAt.orElseThrow());
        if (endedAt.orElseThrow().isBefore(attempt.startedAt()))
          throw new IllegalArgumentException("Cleanup rejection time invalid");
      }
      if (attempt.skipped()
          != result.map(value -> value.status() == BatchStepResult.Status.SKIPPED).orElse(false))
        throw new IllegalArgumentException("Cleanup rejection skip invalid");
    }
  }

  /** Fixed seven slots: absence is not a fabricated FAILED/SKIPPED result or startup proof. */
  public record RejectedSnapshot(BatchRun run, List<Optional<RejectedEntry>> entries) {
    public RejectedSnapshot {
      Objects.requireNonNull(run);
      entries = List.copyOf(entries);
      if (entries.size() != STEPS.size())
        throw new IllegalArgumentException("Cleanup rejection slots invalid");
      var ids = new HashSet<Long>();
      for (int index = 0; index < STEPS.size(); index++) {
        var value = entries.get(index);
        if (value.isPresent()) {
          var attempt = value.orElseThrow().attempt();
          if (attempt.step() != STEPS.get(index)
              || !attempt.run().equals(run)
              || !ids.add(attempt.id()))
            throw new IllegalArgumentException("Cleanup rejection identity invalid");
        }
      }
    }

    @Override
    public String toString() {
      return "CleanupRejectedSnapshot[data=<redacted>]";
    }
  }

  public CleanupTerminalRepository(Connection connection, MaintenanceOwnerFrame.Guard guard) {
    this.connection = Objects.requireNonNull(connection, "reacquired parent transaction");
    this.guard = Objects.requireNonNull(guard, "actual parent deadline");
  }

  public Snapshot read(BatchRun run, Instant observedAt) {
    return read(run, observedAt, false);
  }

  /** Only failed-profile callers may accept the six actual BACKUP_UNAVAILABLE rows. */
  public Snapshot readBackupUnavailable(BatchRun run, Instant observedAt) {
    return read(run, observedAt, true);
  }

  private Snapshot read(BatchRun run, Instant observedAt, boolean failedBackup) {
    Objects.requireNonNull(run, "same original run");
    Objects.requireNonNull(observedAt, "actual UTC readback time");
    BatchStepAttempt.time(run, observedAt);
    try {
      check(run);
      var values = new EnumMap<BatchStep, Entry>(BatchStep.class);
      @Nullable PreparedStatement statement = connection.prepareStatement(SQL);
      @Nullable Throwable statementFailure = null;
      try {
        var query = present(statement);
        query.setQueryTimeout(seconds());
        query.setObject(1, run.id());
        query.setObject(2, run.cutoff().atZone(ZoneId.of(LITERAL_ASIA_TOKYO)).toLocalDate());
        @Nullable ResultSet rows = query.executeQuery();
        @Nullable Throwable rowsFailure = null;
        try {
          var row = present(rows);
          while (row.next()) {
            require(values.size() < STEPS.size());
            var entry = entry(projection(row), run, observedAt);
            var step = entry.attempt().step();
            // Entry already establishes the closed allowlist.
            var reason = entry.result().reason();
            if (failedBackup && step != BatchStep.CLEAN_TRANSFER) {
              // Immutable BatchStepResult enforces BACKUP_UNAVAILABLE -> SKIPPED/zero.
              // Independently malformed status/counts still reject during value decoding.
              require(
                  reason == BatchStepResult.Reason.BACKUP_UNAVAILABLE
                      && entry.attempt().startedAt().equals(entry.endedAt()));
            } else require(reason != BatchStepResult.Reason.BACKUP_UNAVAILABLE);
            require(values.put(step, entry) == null);
          }
        } catch (SQLException | RuntimeException | Error failure) {
          rowsFailure = failure;
          throw failure;
        } finally {
          if (rows != null) {
            try {
              rows.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw secondary;
            }
          }
        }
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        if (statement != null) {
          try {
            statement.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
          }
        }
      }
      var ordered = new ArrayList<Entry>();
      for (var step : STEPS) ordered.add(present(values.get(step)));
      var result = snapshot(ordered);
      check(run);
      return result;
    } catch (SQLException known) {
      StorageIoException.preserveFatal(known);
      throw new BatchRepositoryException();
    }
  }

  /** SSC126/ISSSTEP003: separate same-run complete SUCCESS references, never current SKIP data. */
  public List<Optional<Entry>> references(Snapshot current) {
    Objects.requireNonNull(current);
    var run = current.entries().getFirst().attempt().run();
    try {
      return references(
          current,
          (id, observed) -> {
            if (!id.equals(run.id())) throw new IOException("original lookup required");
            return run;
          });
    } catch (IOException known) {
      throw new BatchRepositoryException();
    }
  }

  /** SSC200: same-business-date SUCCESS with exact separately owned original anchor. */
  public List<Optional<Entry>> references(Snapshot current, SuccessRunLookup originals)
      throws IOException {
    Objects.requireNonNull(current, "current complete Cleanup results");
    Objects.requireNonNull(originals, "same live original owner");
    var run = current.entries().getFirst().attempt().run();
    try {
      check(run);
      var references = new ArrayList<Optional<Entry>>();
      for (var currentRow : current.entries()) {
        if (currentRow.result().reason() != BatchStepResult.Reason.ALREADY_SUCCESSFUL) {
          references.add(Optional.empty());
          continue;
        }
        var handle = currentRow.attempt();
        require(handle.skipped() && currentRow.endedAt().equals(handle.startedAt()));
        @Nullable PreparedStatement statement =
            connection.prepareStatement(
                "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
                    + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
                    + " from schubert.batch_runs where business_date=? and step=?"
                    + " and status='SUCCESS' and attempt<? order by attempt desc limit 2");
        @Nullable Throwable statementFailure = null;
        Entry prior;
        try {
          var query = present(statement);
          query.setQueryTimeout(seconds());
          query.setObject(1, run.cutoff().atZone(ZoneId.of(LITERAL_ASIA_TOKYO)).toLocalDate());
          query.setString(2, handle.step().name());
          query.setInt(3, handle.attempt());
          @Nullable ResultSet rows = query.executeQuery();
          @Nullable Throwable rowsFailure = null;
          try {
            var row = present(rows);
            require(row.next());
            var projected = projection(row);
            var priorRun =
                Objects.requireNonNull(
                    originals.resolve(present(projected.runId()), handle.startedAt()));
            require(
                priorRun.id().equals(projected.runId())
                    && priorRun
                        .cutoff()
                        .atZone(ZoneId.of(LITERAL_ASIA_TOKYO))
                        .toLocalDate()
                        .equals(handle.businessDate()));
            check(priorRun);
            prior = entry(projected, priorRun, handle.startedAt());
            require(
                prior.attempt().step() == handle.step()
                    && prior.attempt().id() != handle.id()
                    && prior.attempt().attempt() < handle.attempt()
                    && prior.result().status() == BatchStepResult.Status.SUCCESS
                    && !row.next());
            // BatchStepResult establishes SUCCESS -> Reason.NONE.
          } catch (SQLException | IOException | RuntimeException | Error failure) {
            rowsFailure = failure;
            throw failure;
          } finally {
            if (rows != null) {
              try {
                rows.close();
              } catch (SQLException | RuntimeException | Error secondary) {
                if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw secondary;
              }
            }
          }
        } catch (SQLException | IOException | RuntimeException | Error failure) {
          statementFailure = failure;
          throw failure;
        } finally {
          if (statement != null) {
            try {
              statement.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
            }
          }
        }
        if (prior.attempt().step() == BatchStep.CLEAN_LOG
            || prior.attempt().step() == BatchStep.CLEAN_INBOX_OUTBOX) {
          prior =
              new Entry(
                  prior.attempt(),
                  prior.endedAt(),
                  prior.result(),
                  Optional.of(progressSeal(prior)));
        }
        require(
            prior
                .attempt()
                .run()
                .equals(originals.resolve(prior.attempt().run().id(), handle.startedAt())));
        references.add(Optional.of(prior));
        check(run);
      }
      check(run);
      return List.copyOf(references);
    } catch (SQLException known) {
      JdbcFailureGraph.preserveFatal(known);
      throw new BatchRepositoryException();
    }
  }

  // SSC199/BUG784/CTERM006..009. Provider calls must stay outside pure value catches.
  /** SSC201/REF200001: full private progress stays in DB; caller retains the immutable seal. */
  private String progressSeal(Entry prior) throws SQLException {
    var statement =
        connection.prepareStatement(
            "select proof_sha256 from schubert.maintenance_read_success_progress(?,?,?,?)");
    @Nullable Throwable statementFailure = null;
    try {
      var checked = present(statement);
      checked.setQueryTimeout(seconds());
      checked.setObject(1, prior.attempt().run().id());
      checked.setObject(2, prior.attempt().run().cutoff().atOffset(ZoneOffset.UTC));
      checked.setString(3, prior.attempt().step().name());
      checked.setObject(4, prior.endedAt().atOffset(ZoneOffset.UTC));
      var rows = checked.executeQuery();
      @Nullable Throwable rowsFailure = null;
      try {
        var row = present(rows);
        require(row.next());
        var seal = present(row.getString("proof_sha256"));
        require(seal.matches("[0-9a-f]{64}") && !row.next());
        return seal;
      } catch (SQLException | RuntimeException | Error failure) {
        rowsFailure = failure;
        throw failure;
      } finally {
        if (rows != null)
          try {
            rows.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw secondary;
          }
      }
    } catch (SQLException | RuntimeException | Error failure) {
      statementFailure = failure;
      throw failure;
    } finally {
      if (statement != null)
        try {
          statement.close();
        } catch (SQLException | RuntimeException | Error secondary) {
          if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
        }
    }
  }

  // SSC199 provider calls remain outside pure value catches.
  private record Projection(
      long id,
      @Nullable UUID runId,
      @Nullable LocalDate date,
      String step,
      int attempt,
      Instant started,
      Optional<Instant> ended,
      String status,
      long target,
      long success,
      long failure,
      long bytes,
      @Nullable String code,
      @Nullable String summary) {}

  private static Projection projection(ResultSet row) throws SQLException {
    long id = present(row.getObject("id", Long.class));
    var run = row.getObject("run_id", UUID.class);
    var date = row.getObject("business_date", LocalDate.class);
    var step = present(row.getString("step"));
    int attempt = present(row.getObject("attempt", Integer.class));
    var started = present(row.getObject("started_at", OffsetDateTime.class)).toInstant();
    var ended =
        Optional.ofNullable(row.getObject("ended_at", OffsetDateTime.class))
            .map(OffsetDateTime::toInstant);
    var status = present(row.getString("status"));
    long target = present(row.getObject("target_count", Long.class));
    long success = present(row.getObject("success_count", Long.class));
    long failure = present(row.getObject("failure_count", Long.class));
    long bytes = present(row.getObject("byte_count", Long.class));
    var code = row.getString("error_code");
    var summary = row.getString("error_summary");
    return new Projection(
        id, run, date, step, attempt, started, ended, status, target, success, failure, bytes, code,
        summary);
  }

  private static Entry entry(Projection row, BatchRun run, Instant observedAt) throws SQLException {
    try {
      require(row.ended().isPresent());
      var ended = row.ended().orElseThrow();
      require(
          !ended.isAfter(observedAt)
              && run.id().equals(row.runId())
              && run.cutoff()
                  .atZone(ZoneId.of(LITERAL_ASIA_TOKYO))
                  .toLocalDate()
                  .equals(row.date()));
      var status = BatchStepResult.Status.valueOf(row.status());
      var result = terminal(row, status);
      return new Entry(
          new BatchStepAttempt(
              row.id(),
              run,
              BatchStep.valueOf(row.step()),
              row.attempt(),
              row.started(),
              status == BatchStepResult.Status.SKIPPED),
          ended,
          result);
    } catch (IllegalArgumentException invalidValue) {
      throw new SQLDataException("Cleanup terminal projection invalid");
    }
  }

  private static BatchStepResult terminal(Projection row, BatchStepResult.Status status)
      throws SQLException {
    var reason =
        row.code() == null
            ? BatchStepResult.Reason.NONE
            : BatchStepResult.Reason.valueOf(row.code());
    var result =
        new BatchStepResult(
            status, row.target(), row.success(), row.failure(), row.bytes(), reason);
    require(Objects.equals(reason.summary(), row.summary()));
    return result;
  }

  private static Snapshot snapshot(List<Entry> entries) throws SQLException {
    try {
      return new Snapshot(entries);
    } catch (IllegalArgumentException invalidValue) {
      throw new SQLDataException("Cleanup terminal projection invalid");
    }
  }

  /** SSC120/BUG365: preserve nonexistent/partial/terminal DB facts without writes. */
  public RejectedSnapshot readRejected(BatchRun run, Instant observedAt) {
    Objects.requireNonNull(run, "same rejected run");
    Objects.requireNonNull(observedAt, "actual rejection observation");
    BatchStepAttempt.time(run, observedAt);
    try {
      check(run);
      var values = new EnumMap<BatchStep, RejectedEntry>(BatchStep.class);
      @Nullable PreparedStatement statement = connection.prepareStatement(SQL);
      @Nullable Throwable statementFailure = null;
      try {
        var query = present(statement);
        query.setQueryTimeout(seconds());
        query.setObject(1, run.id());
        query.setObject(2, run.cutoff().atZone(ZoneId.of(LITERAL_ASIA_TOKYO)).toLocalDate());
        @Nullable ResultSet rows = query.executeQuery();
        @Nullable Throwable rowsFailure = null;
        try {
          var row = present(rows);
          while (row.next()) {
            require(values.size() < STEPS.size());
            var value = rejected(projection(row), run, observedAt);
            // RejectedEntry already establishes the closed allowlist.
            require(values.put(value.attempt().step(), value) == null);
          }
        } catch (SQLException | RuntimeException | Error failure) {
          rowsFailure = failure;
          throw failure;
        } finally {
          if (rows != null) {
            try {
              rows.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(rowsFailure, secondary)) throw secondary;
            }
          }
        }
      } catch (SQLException | RuntimeException | Error failure) {
        statementFailure = failure;
        throw failure;
      } finally {
        if (statement != null) {
          try {
            statement.close();
          } catch (SQLException | RuntimeException | Error secondary) {
            if (JdbcResourceFailures.replace(statementFailure, secondary)) throw secondary;
          }
        }
      }
      var ordered = new ArrayList<Optional<RejectedEntry>>();
      for (var step : STEPS) ordered.add(Optional.ofNullable(values.get(step)));
      var result = rejectedSnapshot(run, ordered);
      check(run);
      return result;
    } catch (SQLException known) {
      StorageIoException.preserveFatal(known);
      throw new BatchRepositoryException();
    }
  }

  private static RejectedEntry rejected(Projection row, BatchRun run, Instant observedAt)
      throws SQLException {
    try {
      require(
          !row.started().isAfter(observedAt)
              && run.id().equals(row.runId())
              && run.cutoff()
                  .atZone(ZoneId.of(LITERAL_ASIA_TOKYO))
                  .toLocalDate()
                  .equals(row.date()));
      Optional<BatchStepResult> result;
      if (row.status().equals("RUNNING")) {
        require(
            row.ended().isEmpty()
                && row.target() == 0
                && row.success() == 0
                && row.failure() == 0
                && row.bytes() == 0
                && row.code() == null
                && row.summary() == null);
        result = Optional.empty();
      } else {
        require(row.ended().isPresent() && !row.ended().orElseThrow().isAfter(observedAt));
        result = Optional.of(terminal(row, BatchStepResult.Status.valueOf(row.status())));
      }
      var attempt =
          new BatchStepAttempt(
              row.id(),
              run,
              BatchStep.valueOf(row.step()),
              row.attempt(),
              row.started(),
              result.map(value -> value.status() == BatchStepResult.Status.SKIPPED).orElse(false));
      return new RejectedEntry(attempt, row.ended(), result);
    } catch (IllegalArgumentException invalidValue) {
      throw new SQLDataException("Cleanup rejection projection invalid");
    }
  }

  private static RejectedSnapshot rejectedSnapshot(
      BatchRun run, List<Optional<RejectedEntry>> entries) throws SQLException {
    try {
      return new RejectedSnapshot(run, entries);
    } catch (IllegalArgumentException invalidValue) {
      throw new SQLDataException("Cleanup rejection projection invalid");
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
