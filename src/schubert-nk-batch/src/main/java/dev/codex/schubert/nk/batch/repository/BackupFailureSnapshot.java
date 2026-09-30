package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Data only, not an issuer/lock/worker certificate. Full latest failed pair observation.
 * NK-OPS-001/NK-BAT-001/BAK001/OPS009/UI251/SS331/341/343 SSC124; CFDB001..004.
 */
@NullMarked
public record BackupFailureSnapshot(
    BatchStepAttempt database, BatchStepAttempt configuration, Instant endedAt) {
  public BackupFailureSnapshot {
    Objects.requireNonNull(database);
    Objects.requireNonNull(configuration);
    Objects.requireNonNull(endedAt);
    BatchStepAttempt.time(database.run(), endedAt);
    if (database.step() != BatchStep.BACKUP_DB
        || configuration.step() != BatchStep.BACKUP_CONFIG
        || database.id() == configuration.id()
        || database.skipped()
        || configuration.skipped()
        || !database.run().equals(configuration.run())
        || !database.startedAt().equals(configuration.startedAt())
        || endedAt.isBefore(database.startedAt()))
      throw new IllegalArgumentException("failed backup pair invalid");
  }

  /** Guard must be the base owner/environment, not a recursive guard that calls this method. */
  public void verifyLatest(Connection connection, MaintenanceOwnerFrame.Guard guard)
      throws java.io.IOException {
    Objects.requireNonNull(connection);
    Objects.requireNonNull(guard);
    guard.check();
    if (!new RunReferenceRepository(connection).read(database.run()).identityConsistent())
      throw new java.io.IOException("failed backup run identity unavailable");
    verifyRow(connection, database, guard);
    verifyRow(connection, configuration, guard);
    guard.check();
    if (!new RunReferenceRepository(connection).read(database.run()).identityConsistent())
      throw new java.io.IOException("failed backup run identity unavailable");
    guard.check();
  }

  private void verifyRow(Connection c, BatchStepAttempt expected, MaintenanceOwnerFrame.Guard guard)
      throws java.io.IOException {
    guard.check();
    String sql =
        "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
            + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
            + " from schubert.batch_runs where run_id=? and step=? order by attempt desc limit 1";
    try (var statement = c.prepareStatement(sql)) {
      if (statement == null) throw new SQLException("missing statement");
      statement.setQueryTimeout(guard.queryTimeoutSeconds());
      statement.setObject(1, expected.run().id());
      statement.setString(2, expected.step().name());
      try (var row = statement.executeQuery()) {
        if (row == null
            || !row.next()
            || !Long.valueOf(expected.id()).equals(row.getObject("id", Long.class))
            || !expected.run().id().equals(row.getObject("run_id", java.util.UUID.class))
            || !expected
                .businessDate()
                .equals(row.getObject("business_date", java.time.LocalDate.class))
            || !expected.step().name().equals(row.getObject("step", String.class))
            || !Integer.valueOf(expected.attempt()).equals(row.getObject("attempt", Integer.class))
            || !expected
                .startedAt()
                .atOffset(java.time.ZoneOffset.UTC)
                .equals(row.getObject("started_at", OffsetDateTime.class))
            || !endedAt
                .atOffset(java.time.ZoneOffset.UTC)
                .equals(row.getObject("ended_at", OffsetDateTime.class))
            || !"FAILED".equals(row.getObject("status", String.class))
            || !Long.valueOf(1).equals(row.getObject("target_count", Long.class))
            || !Long.valueOf(0).equals(row.getObject("success_count", Long.class))
            || !Long.valueOf(1).equals(row.getObject("failure_count", Long.class))
            || !Long.valueOf(0).equals(row.getObject("byte_count", Long.class))
            || !"COMMAND_FAILURE".equals(row.getObject("error_code", String.class))
            || !"batch command failed".equals(row.getObject("error_summary", String.class))
            || row.next()) throw new SQLException("failed backup projection mismatch");
      }
      guard.check();
    } catch (SQLException failure) {
      throw new java.io.IOException("failed backup observation unavailable");
    }
    guard.check();
  }

  @Override
  public String toString() {
    return "BackupFailureSnapshot[data=<redacted>]";
  }
}
