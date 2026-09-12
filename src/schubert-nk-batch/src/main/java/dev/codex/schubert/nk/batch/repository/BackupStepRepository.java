package dev.codex.schubert.nk.batch.repository;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import java.sql.*;
import java.time.*;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed transaction and genuine root manifest required; not artifact authentication.
 * NK-BAT-001/BAK/BKO/OPS009/UI251/SS331 8.3/341 6.6/343; SSC061/PG168; BAT210..217.
 */
@NullMarked
public final class BackupStepRepository {
  private static final String PAIR =
      "select id,run_id,business_date,step,attempt,started_at,ended_at,status,"
          + "target_count,success_count,failure_count,byte_count,error_code,error_summary"
          + " from schubert.batch_runs where id in (?,?) order by id for update";
  private final Connection connection;
  private final RunReferenceRepository references;
  private final BatchRunRepository steps;

  public BackupStepRepository(Connection connection) {
    this.connection = Objects.requireNonNull(connection, "parent connection");
    references = new RunReferenceRepository(connection);
    steps = new BatchRunRepository(connection);
  }

  public Optional<Instant> inspect(BackupManifest manifest, Instant observedAt) {
    validTime(manifest, observedAt);
    try {
      guarded(manifest);
      List<Optional<Instant>> states = new ArrayList<>();
      Set<Long> seen = new HashSet<>();
      try (var statement = connection.prepareStatement(PAIR)) {
        var query = present(statement);
        query.setQueryTimeout(5);
        query.setLong(1, manifest.databaseStep().id());
        query.setLong(2, manifest.configurationStep().id());
        try (var rows = query.executeQuery()) {
          var row = present(rows);
          while (row.next()) {
            require(states.size() < 2);
            long id = present(row.getObject("id", Long.class));
            require(seen.add(id));
            BatchStepAttempt attempt;
            if (id == manifest.databaseStep().id()) attempt = manifest.databaseStep();
            else {
              require(id == manifest.configurationStep().id());
              attempt = manifest.configurationStep();
            }
            states.add(readRow(row, attempt, manifest, observedAt));
          }
        }
      }
      require(states.size() == 2 && states.get(0).equals(states.get(1)));
      guarded(manifest);
      return states.getFirst();
    } catch (SQLException failure) {
      throw new BatchRepositoryException();
    }
  }

  public Instant complete(BackupManifest manifest, Instant endedAt) {
    var existing = inspect(manifest, endedAt);
    if (existing.isPresent()) return existing.orElseThrow();
    steps.finish(manifest.databaseStep(), endedAt, success(1, manifest.dump().size()));
    steps.finish(manifest.configurationStep(), endedAt, success(2, manifest.configurationBytes()));
    var actual = inspect(manifest, endedAt);
    if (!actual.equals(Optional.of(endedAt))) throw new BatchRepositoryException();
    return actual.orElseThrow();
  }

  private static Optional<Instant> readRow(
      ResultSet row, BatchStepAttempt attempt, BackupManifest manifest, Instant observedAt)
      throws SQLException {
    require(present(row.getObject("run_id", UUID.class)).equals(attempt.run().id()));
    require(
        present(row.getObject("business_date", LocalDate.class)).equals(attempt.businessDate()));
    require(present(row.getString("step")).equals(attempt.step().name()));
    require(present(row.getObject("attempt", Integer.class)) == attempt.attempt());
    require(
        present(row.getObject("started_at", OffsetDateTime.class))
            .toInstant()
            .equals(attempt.startedAt()));
    String status = present(row.getString("status"));
    OffsetDateTime ended = row.getObject("ended_at", OffsetDateTime.class);
    long target = present(row.getObject("target_count", Long.class));
    long success = present(row.getObject("success_count", Long.class));
    long failure = present(row.getObject("failure_count", Long.class));
    long bytes = present(row.getObject("byte_count", Long.class));
    require(row.getString("error_code") == null && row.getString("error_summary") == null);
    if (status.equals("RUNNING")) {
      require(ended == null && target == 0 && success == 0 && failure == 0 && bytes == 0);
      return Optional.empty();
    }
    require(status.equals("SUCCESS"));
    Instant time = present(ended).toInstant();
    require(
        !time.isBefore(manifest.contentFinishedAt())
            && !time.isAfter(observedAt)
            && time.getNano() % 1000 == 0);
    boolean database = attempt.step() == BatchStep.BACKUP_DB;
    require(
        target == (database ? 1 : 2)
            && success == target
            && failure == 0
            && bytes == (database ? manifest.dump().size() : manifest.configurationBytes()));
    return Optional.of(time);
  }

  private void guarded(BackupManifest manifest) throws SQLDataException {
    require(references.read(manifest.run()).identityConsistent());
  }

  private static BatchStepResult success(long files, long bytes) {
    return new BatchStepResult(
        BatchStepResult.Status.SUCCESS, files, files, 0, bytes, BatchStepResult.Reason.NONE);
  }

  private static void validTime(BackupManifest manifest, Instant value) {
    Objects.requireNonNull(manifest, "genuine backup manifest");
    Objects.requireNonNull(value, "backup observation time");
    if (value.isBefore(manifest.contentFinishedAt())
        || value.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || value.getNano() % 1000 != 0)
      throw new IllegalArgumentException("invalid backup observation time");
  }

  private static <T> T present(@Nullable T value) throws SQLDataException {
    if (value == null) throw new SQLDataException("backup projection missing");
    return value;
  }

  private static void require(boolean value) throws SQLDataException {
    if (!value) throw new SQLDataException("backup step binding failed");
  }
}
