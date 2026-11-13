package dev.codex.schubert.nk.batch.repository;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed parent transaction for V022 Expiry audit. The caller commits the stage before broker
 * removal and the terminal after actual observation; this class never commits or closes the
 * connection. NK-BAT-001/DAT-009/OPS-009; UI251; SS331 §8.2/8.3,341 §9;
 * SSC-077/078/BUG-237/238/YKT-188/189; PG249/PT-BAT-284..287.
 */
@NullMarked
public final class ExpiryAuditRepository {
  private static final java.lang.String LITERAL_SUCCESS = "SUCCESS";

  private static final String HANDLE =
      "id=? and run_id=? and business_date=? and step='CLEAN_EXPIRY' and attempt=? and started_at=?";

  public record Stage(Instant cutoff, long before, long target, long estimatedBytes) {
    public Stage {
      Objects.requireNonNull(cutoff, "exact Expiry cutoff");
      if (before < 0 || target < 0 || target > before || estimatedBytes < 0)
        throw new IllegalArgumentException("invalid Expiry stage");
    }

    @Override
    public String toString() {
      return "ExpiryAuditStage[observation=<redacted>]";
    }
  }

  public record Snapshot(
      String status,
      @Nullable Instant cutoff,
      @Nullable Long before,
      @Nullable Long after,
      long target,
      long success,
      long failure,
      long estimatedBytes,
      @Nullable Instant ended,
      @Nullable String errorCode,
      @Nullable String errorSummary) {
    @Override
    public String toString() {
      return "ExpiryAuditSnapshot[observation=<redacted>]";
    }
  }

  private final Connection connection;
  private final RunReferenceRepository references;

  public ExpiryAuditRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "borrowed parent connection");
    references = new RunReferenceRepository(connection);
  }

  /**
   * Immutable retained SUCCESS identity + complete audit, never the current SKIP handle.
   * SSC125/200.
   */
  public record Prior(BatchStepAttempt handle, Snapshot audit) {
    public Prior {
      Objects.requireNonNull(handle);
      Objects.requireNonNull(audit);
    }
  }

  public Optional<Prior> successful(
      BatchRun run,
      Instant observed,
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner)
      throws IOException {
    Objects.requireNonNull(run);
    return successful(
        run,
        observed,
        owner,
        (id, time) -> {
          if (!id.equals(run.id())) throw new IOException("Expiry original unavailable");
          return run;
        });
  }

  /** EXP200001: day-based SKIP resolves the actual retained anchor, never a DB-derived cutoff. */
  public Optional<Prior> successful(
      BatchRun run,
      Instant observed,
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner,
      SuccessRunLookup originals)
      throws IOException {
    Objects.requireNonNull(run);
    Objects.requireNonNull(observed);
    Objects.requireNonNull(owner);
    Objects.requireNonNull(originals);
    BatchStepAttempt.time(run, observed);
    owner.check();
    guarded(run);
    try {
      return usingJdbc(
          () ->
              connection.prepareStatement(
                  "select id,run_id,attempt,started_at from schubert.batch_runs where"
                      + " business_date=? and step='CLEAN_EXPIRY' and status='SUCCESS' order by"
                      + " attempt desc limit 2"),
          PreparedStatement::close,
          statement -> {
            statement.setQueryTimeout(owner.queryTimeoutSeconds());
            var day = run.cutoff().atZone(ZoneId.of("Asia/Tokyo")).toLocalDate();
            statement.setObject(1, day);
            return usingJdbc(
                statement::executeQuery,
                ResultSet::close,
                rows -> {
                  if (!rows.next()) {
                    owner.check();
                    return Optional.empty();
                  }
                  var priorId = required(rows.getObject("run_id", java.util.UUID.class));
                  var priorRun = Objects.requireNonNull(originals.resolve(priorId, observed));
                  if (!priorId.equals(priorRun.id())
                      || !day.equals(
                          priorRun.cutoff().atZone(ZoneId.of("Asia/Tokyo")).toLocalDate()))
                    throw new BatchRepositoryException();
                  guarded(priorRun);
                  var handle =
                      new BatchStepAttempt(
                          required(rows.getObject("id", Long.class)),
                          priorRun,
                          BatchStep.CLEAN_EXPIRY,
                          required(rows.getObject("attempt", Integer.class)),
                          required(rows.getObject("started_at", OffsetDateTime.class)).toInstant(),
                          false);
                  if (rows.next()) throw new BatchRepositoryException();
                  var audit = read(handle).orElseThrow(BatchRepositoryException::new);
                  verifySuccessfulAudit(audit, observed);
                  owner.check();
                  guarded(run);
                  return Optional.of(new Prior(handle, audit));
                });
          });
    } catch (SQLException known) {
      throw new BatchRepositoryException();
    }
  }

  public Stage stage(BatchStepAttempt attempt, long before, long target, long estimatedBytes) {
    validAttempt(attempt);
    Stage stage =
        new Stage(attempt.run().cutoff().minus(7, ChronoUnit.DAYS), before, target, estimatedBytes);
    guarded(attempt.run());
    try (PreparedStatement statement =
        required(
            connection.prepareStatement(
                "update schubert.batch_runs set expiry_cutoff_at=?,expiry_before_count=?,"
                    + "target_count=?,byte_count=? where "
                    + HANDLE
                    + " and status='RUNNING' and ended_at is null"
                    + " and expiry_cutoff_at is null and expiry_before_count is null"
                    + " and expiry_after_count is null and target_count=0 and success_count=0"
                    + " and failure_count=0 and byte_count=0"))) {
      statement.setQueryTimeout(5);
      statement.setObject(1, stage.cutoff().atOffset(ZoneOffset.UTC));
      statement.setLong(2, stage.before());
      statement.setLong(3, stage.target());
      statement.setLong(4, stage.estimatedBytes());
      bindHandle(statement, 5, attempt);
      int changed = statement.executeUpdate();
      // id is the table PK, so a real UPDATE can affect only zero or one row.
      if (changed == 0 && !matchesStage(read(attempt), stage)) throw new BatchRepositoryException();
    } catch (SQLException | RuntimeException failure) {
      throw new BatchRepositoryException();
    }
    guarded(attempt.run());
    return stage;
  }

  public void finish(
      BatchStepAttempt attempt,
      Stage stage,
      Instant ended,
      @Nullable Long actualAfter,
      BatchStepResult result) {
    validAttempt(attempt);
    Objects.requireNonNull(stage, "durably committed stage");
    Objects.requireNonNull(ended, "terminal time");
    Objects.requireNonNull(result, "terminal result");
    BatchStepAttempt.time(attempt.run(), ended);
    if (ended.isBefore(attempt.startedAt())
        || !stage.cutoff().equals(attempt.run().cutoff().minus(7, ChronoUnit.DAYS))
        || result.status() == BatchStepResult.Status.SKIPPED
        || result.target() != stage.target()
        || result.bytes() != stage.estimatedBytes()
        || (actualAfter == null
            && (result.status() == BatchStepResult.Status.SUCCESS || result.success() != 0))
        || (actualAfter != null
            && (actualAfter < 0
                || actualAfter > stage.before()
                || result.success() != stage.before() - actualAfter
                || (result.status() == BatchStepResult.Status.SUCCESS
                    && result.success() != stage.target()))))
      throw new IllegalArgumentException("invalid Expiry terminal");
    guarded(attempt.run());
    try (PreparedStatement statement =
        required(
            connection.prepareStatement(
                "update schubert.batch_runs set"
                    + " ended_at=?,status=?,success_count=?,failure_count=?,error_code=?,error_summary=?,expiry_after_count=?"
                    + " where "
                    + HANDLE
                    + " and status='RUNNING' and ended_at is null"
                    + " and expiry_cutoff_at=? and expiry_before_count=?"
                    + " and target_count=? and byte_count=? and expiry_after_count is null"))) {
      statement.setQueryTimeout(5);
      statement.setObject(1, ended.atOffset(ZoneOffset.UTC));
      statement.setString(2, result.status().name());
      statement.setLong(3, result.success());
      statement.setLong(4, result.failure());
      statement.setString(5, result.reason().code());
      statement.setString(6, result.reason().summary());
      statement.setObject(7, actualAfter);
      bindHandle(statement, 8, attempt);
      statement.setObject(13, stage.cutoff().atOffset(ZoneOffset.UTC));
      statement.setLong(14, stage.before());
      statement.setLong(15, stage.target());
      statement.setLong(16, stage.estimatedBytes());
      int changed = statement.executeUpdate();
      if (changed == 0 && !matchesTerminal(read(attempt), stage, ended, actualAfter, result))
        throw new BatchRepositoryException();
    } catch (SQLException | RuntimeException failure) {
      throw new BatchRepositoryException();
    }
    guarded(attempt.run());
  }

  public Optional<Snapshot> read(BatchStepAttempt attempt) {
    validAttempt(attempt);
    guarded(attempt.run());
    try {
      PreparedStatement statement =
          connection.prepareStatement(
              "select status,expiry_cutoff_at,expiry_before_count,expiry_after_count,"
                  + "target_count,success_count,failure_count,byte_count,ended_at,error_code,"
                  + "error_summary from schubert.batch_runs where "
                  + HANDLE);
      @Nullable Throwable statementFailure = null;
      try {
        var query = presentRead(statement);
        query.setQueryTimeout(5);
        bindHandle(query, 1, attempt);
        ResultSet rows = query.executeQuery();
        @Nullable Throwable rowFailure = null;
        try {
          var values = presentRead(rows);
          if (!values.next()) {
            guarded(attempt.run());
            return Optional.empty();
          }
          OffsetDateTime cutoff = values.getObject("expiry_cutoff_at", OffsetDateTime.class);
          OffsetDateTime ended = values.getObject("ended_at", OffsetDateTime.class);
          Snapshot value =
              new Snapshot(
                  presentRead(values.getString("status")),
                  cutoff == null ? null : cutoff.toInstant(),
                  values.getObject("expiry_before_count", Long.class),
                  values.getObject("expiry_after_count", Long.class),
                  presentRead(values.getObject("target_count", Long.class)),
                  presentRead(values.getObject("success_count", Long.class)),
                  presentRead(values.getObject("failure_count", Long.class)),
                  presentRead(values.getObject("byte_count", Long.class)),
                  ended == null ? null : ended.toInstant(),
                  values.getString("error_code"),
                  values.getString("error_summary"));
          // id is the primary key; no second row exists for this exact handle.
          if (!validSnapshot(attempt, value))
            throw new SQLDataException("Expiry projection invalid");
          guarded(attempt.run());
          return Optional.of(value);
        } catch (SQLException | RuntimeException | Error failure) {
          rowFailure = failure;
          throw failure;
        } finally {
          if (rows != null)
            try {
              rows.close();
            } catch (SQLException | RuntimeException | Error secondary) {
              if (JdbcResourceFailures.replace(rowFailure, secondary)) throw secondary;
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
    } catch (SQLException failure) {
      throw new BatchRepositoryException();
    }
  }

  /** SSC310: malformed mandatory DB values are known SQL failures, not provider Runtime. */
  private static <T> T presentRead(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("Expiry projection missing");
    return value;
  }

  static boolean validSnapshot(BatchStepAttempt attempt, Snapshot value) {
    boolean running = value.status().equals("RUNNING");
    @Nullable Instant cutoff = value.cutoff();
    @Nullable Long beforeValue = value.before();
    if (!running
        && !value.status().equals(LITERAL_SUCCESS)
        && !value.status().equals("WARNING")
        && !value.status().equals("FAILED")) return false;
    if (running != (value.ended() == null)
        || value.target() < 0
        || value.success() < 0
        || value.failure() < 0
        || value.estimatedBytes() < 0
        || (cutoff == null) != (beforeValue == null)) return false;
    if (cutoff == null) return value.after() == null && !value.status().equals(LITERAL_SUCCESS);
    long before = required(beforeValue);
    if (!cutoff.equals(attempt.run().cutoff().minus(7, ChronoUnit.DAYS))
        || before < 0
        || value.target() > before) return false;
    if (value.after() == null)
      return !value.status().equals(LITERAL_SUCCESS) && value.success() == 0;
    long after = required(value.after());
    return after >= 0
        && after <= before
        && before - after == value.success()
        && (!value.status().equals(LITERAL_SUCCESS)
            || (value.success() == value.target() && value.failure() == 0));
  }

  static boolean matchesStage(Optional<Snapshot> read, Stage stage) {
    return read.isPresent()
        && read.get().status().equals("RUNNING")
        && read.get().after() == null
        && Objects.equals(read.get().cutoff(), stage.cutoff())
        && Objects.equals(read.get().before(), stage.before())
        && read.get().target() == stage.target()
        && read.get().success() == 0
        && read.get().failure() == 0
        && read.get().estimatedBytes() == stage.estimatedBytes();
  }

  static boolean matchesTerminal(
      Optional<Snapshot> read,
      Stage stage,
      Instant ended,
      @Nullable Long actualAfter,
      BatchStepResult result) {
    return read.isPresent()
        && Objects.equals(read.get().cutoff(), stage.cutoff())
        && Objects.equals(read.get().before(), stage.before())
        && Objects.equals(read.get().after(), actualAfter)
        && read.get().target() == result.target()
        && read.get().success() == result.success()
        && read.get().failure() == result.failure()
        && read.get().estimatedBytes() == result.bytes()
        && read.get().status().equals(result.status().name())
        && Objects.equals(read.get().ended(), ended)
        && Objects.equals(read.get().errorCode(), result.reason().code())
        && Objects.equals(read.get().errorSummary(), result.reason().summary());
  }

  private static void bindHandle(PreparedStatement statement, int offset, BatchStepAttempt attempt)
      throws SQLException {
    statement.setLong(offset, attempt.id());
    statement.setObject(offset + 1, attempt.run().id());
    statement.setObject(offset + 2, attempt.businessDate());
    statement.setInt(offset + 3, attempt.attempt());
    statement.setObject(offset + 4, attempt.startedAt().atOffset(ZoneOffset.UTC));
  }

  private static void validAttempt(BatchStepAttempt attempt) {
    Objects.requireNonNull(attempt, "Expiry attempt");
    if (attempt.step() != BatchStep.CLEAN_EXPIRY || attempt.skipped())
      throw new IllegalArgumentException("invalid Expiry attempt");
  }

  private void guarded(BatchRun run) {
    if (!references.read(run).identityConsistent()) throw new BatchRepositoryException();
  }

  static <T> T required(@Nullable T value) {
    if (value == null) throw new BatchRepositoryException();
    return value;
  }

  /** SSC304: the same late predicate, independently testable without weakening read/DDL. */
  static void verifySuccessfulAudit(Snapshot audit, Instant observed) {
    Objects.requireNonNull(audit, "retained audit");
    Objects.requireNonNull(observed, "observation time");
    @Nullable Instant ended = audit.ended();
    if (!LITERAL_SUCCESS.equals(audit.status())
        || ended == null
        || ended.isAfter(observed)
        || audit.errorCode() != null
        || audit.errorSummary() != null) throw new BatchRepositoryException();
  }

  @FunctionalInterface
  interface JdbcAcquire<T> {
    @Nullable T open() throws SQLException;
  }

  @FunctionalInterface
  interface JdbcRelease<T> {
    void close(T resource) throws SQLException;
  }

  @FunctionalInterface
  interface JdbcRead<T> {
    Optional<Prior> read(T resource) throws SQLException, IOException;
  }

  /** SSC304: lexical ownership of admitted nonnull JDBC resources; exact Java TWR semantics. */
  static <T> Optional<Prior> usingJdbc(
      JdbcAcquire<T> acquire, JdbcRelease<T> release, JdbcRead<T> read)
      throws SQLException, IOException {
    Objects.requireNonNull(acquire, "owned JDBC acquisition");
    Objects.requireNonNull(release, "owned JDBC close");
    Objects.requireNonNull(read, "owned JDBC body");
    T resource = required(acquire.open());
    final Optional<Prior> value;
    try {
      value = read.read(resource);
    } catch (Throwable primary) {
      try {
        release.close(resource);
      } catch (Throwable secondary) {
        primary.addSuppressed(secondary);
      }
      throw primary;
    }
    release.close(resource);
    return value;
  }
}
