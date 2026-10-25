package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-ESKIP001: literal SQL oracle, genuine isolated PostgreSQL, SSC117/BUG351/YKT280. */
final class CleanupExpiryExecutionTest {
  @TempDir Path root;

  @Test
  void exactCurrentSkipAndOriginalAuditAreIndependentlyReadWithoutMutation() throws Exception {
    var db = new BatchDatabaseFixture(root);
    try {
      try (var admin = db.admin()) {
        execute(
            admin,
            """
          insert into schubert.batch_runs
          (id,run_id,business_date,step,attempt,started_at,ended_at,status,
           target_count,success_count,failure_count,byte_count,error_code,error_summary,
           expiry_cutoff_at,expiry_before_count,expiry_after_count)
          values
          (42,'38100000-2222-4333-8444-555555555555','2026-09-30','CLEAN_EXPIRY',1,
           '2026-09-30T00:00:01Z','2026-09-30T00:00:02Z','SUCCESS',2,2,0,200,null,null,
           '2026-09-23T00:00:00Z',3,1),
          (43,'38100000-2222-4333-8444-555555555555','2026-09-30','CLEAN_EXPIRY',2,
           '2026-09-30T00:00:03Z','2026-09-30T00:00:03Z','SKIPPED',0,0,0,0,
           'ALREADY_SUCCESSFUL','step already successful for business date',null,null,null)
          """);
      }
      var request =
          new CleanupWorkerRequest.Expiry(
              UUID.fromString("38100000-2222-4333-8444-555555555555"),
              UUID.fromString("38100000-6666-4777-8888-999999999999"),
              Instant.parse("2026-09-30T00:00:00Z"),
              UUID.fromString("38100000-3333-4333-8444-555555555555"),
              UUID.fromString("38100000-4444-4333-8444-555555555555"),
              "1".repeat(32),
              43,
              2,
              Instant.parse("2026-09-30T00:00:03Z"),
              true,
              Optional.of(
                  new CleanupWorkerRequest.Expiry.PriorExpiry(
                      UUID.fromString("38100000-2222-4333-8444-555555555555"),
                      Instant.parse("2026-09-30T00:00:00Z"),
                      42,
                      1,
                      Instant.parse("2026-09-30T00:00:01Z"),
                      Instant.parse("2026-09-30T00:00:02Z"))));
      try (var connection = db.open("schubert_batch")) {
        execute(connection, "select pg_advisory_lock(71419602)");
        connection.setAutoCommit(false);
        String before = rows(connection);
        CleanupExpiryExecution.verifyPriorExpiry(connection, request, 0);
        assertEquals(before, rows(connection));
        assertThrows(
            IOException.class,
            () -> CleanupExpiryExecution.verifyPriorExpiry(connection, request, 1));
        connection.rollback();
        for (String assignment :
            new String[] {
              "byte_count=1", "error_code='BACKUP_UNAVAILABLE'", "ended_at='2026-09-30T00:00:04Z'"
            }) {
          try (var admin = db.admin()) {
            execute(admin, "update schubert.batch_runs set " + assignment + " where id=43");
          }
          assertThrows(
              BatchRepositoryException.class,
              () -> CleanupExpiryExecution.verifyPriorExpiry(connection, request, 0));
          connection.rollback();
          try (var admin = db.admin()) {
            execute(
                admin,
                "update schubert.batch_runs set byte_count=0,error_code='ALREADY_SUCCESSFUL',ended_at='2026-09-30T00:00:03Z' where id=43");
          }
        }
        for (String assignment :
            new String[] {
              "ended_at='2026-09-30T00:00:03Z'",
              "expiry_cutoff_at='2026-09-22T00:00:00Z'",
              "status='WARNING'"
            }) {
          try (var admin = db.admin()) {
            execute(admin, "update schubert.batch_runs set " + assignment + " where id=42");
          }
          if (assignment.startsWith("expiry_cutoff_at=")) {
            assertThrows(
                BatchRepositoryException.class,
                () -> CleanupExpiryExecution.verifyPriorExpiry(connection, request, 0));
          } else {
            assertThrows(
                IOException.class,
                () -> CleanupExpiryExecution.verifyPriorExpiry(connection, request, 0));
          }
          connection.rollback();
          try (var admin = db.admin()) {
            execute(
                admin,
                "update schubert.batch_runs set ended_at='2026-09-30T00:00:02Z',expiry_cutoff_at='2026-09-23T00:00:00Z',status='SUCCESS' where id=42");
          }
        }
        assertEquals(before, rows(connection));
        connection.rollback();
      }
    } finally {
      db.stop();
    }
  }

  private static void execute(Connection connection, String sql) throws Exception {
    try (var statement = connection.createStatement()) {
      statement.execute(sql);
    }
  }

  private static String rows(Connection connection) throws Exception {
    try (var statement = connection.createStatement();
        var result =
            statement.executeQuery(
                "select string_agg(row_to_json(b)::text,E'\\n' order by id) from schubert.batch_runs b")) {
      assertTrue(result.next());
      return result.getString(1);
    }
  }
}
