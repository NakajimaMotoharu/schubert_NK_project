package dev.codex.schubert.nk.batch.cleanup;

import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.query;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import java.nio.file.Path;
import java.sql.SQLDataException;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-BAT-MGUARD001..003, independent PG set_config projection/rollback oracle. SSC119. */
final class MaintenanceMutationGuardTest {
  @TempDir static Path root;
  private static BatchDatabaseFixture db;

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void pgTimeoutIsFlooredBoundedAndTransactionLocal() throws Exception {
    for (long remaining :
        List.of(1_999_999_999L, 2_999_999_999L, 5_999_999_999L, 30_000_000_000L)) {
      try (var c = db.open("schubert_batch")) {
        var expected = remaining < 2_000_000_000L ? "1s" : remaining < 3_000_000_000L ? "2s" : "5s";
        c.setAutoCommit(false);
        new MaintenanceMutationGuard(() -> remaining).bind(c);
        assertEquals(expected, query(c, "show statement_timeout"));
        c.rollback();
        c.setAutoCommit(true);
        assertEquals(
            "30min", query(c, "show statement_timeout")); // SS role's original session default.
      }
    }
    assertThrows(NullPointerException.class, () -> new MaintenanceMutationGuard(null));
    try (var c = db.open("schubert_batch")) {
      assertThrows(
          SQLDataException.class, () -> new MaintenanceMutationGuard(() -> 2_000_000_000L).bind(c));
      assertThrows(NullPointerException.class, () -> new MaintenanceMutationGuard().bind(null));
      c.setAutoCommit(false);
      var failure =
          assertThrows(
              CleanupStoppedException.class,
              () -> new MaintenanceMutationGuard(() -> 999_999_999L).bind(c));
      assertEquals(CleanupStopReason.TIME_LIMIT, failure.reason());
      c.rollback();
    }
  }

  @Test
  void malformedReadbackAndIoNeverBecomeMutationAuthority() throws Exception {
    for (String projection : List.of("5000", "4s", "", "none")) {
      try (var c = db.open("schubert_batch")) {
        c.setAutoCommit(false);
        var probe = new ServiceJdbcProbe();
        probe.columns.put("timeout.bound_timeout", projection.equals("none") ? null : projection);
        assertThrows(
            SQLDataException.class,
            () -> new MaintenanceMutationGuard(() -> 10_000_000_000L).bind(probe.wrap(c)));
        assertEquals(1, probe.seen.getOrDefault("timeout.resultClose", 0));
        assertEquals(1, probe.seen.getOrDefault("timeout.statementClose", 0));
        c.rollback();
      }
    }
    var known =
        new MaintenanceMutationGuard(
            () -> {
              throw new java.io.IOException("PRIVATE");
            });
    var failure = assertThrows(CleanupStoppedException.class, known::check);
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    var unknown = new AssertionError("PUBLIC_PROGRAMMING");
    assertSame(
        unknown,
        assertThrows(
            AssertionError.class,
            () ->
                new MaintenanceMutationGuard(
                        () -> {
                          throw unknown;
                        })
                    .check()));
  }

  /** MG541001: public JDBC cardinality fault, independently verified real TX effects. */
  @Test
  void mg541001TimeoutProjectionRequiresExactlyOneRowWithoutTakingTransactionOwnership()
      throws Exception {
    for (boolean duplicate : List.of(false, true)) {
      try (var c = db.open("schubert_batch")) {
        c.setAutoCommit(false);
        var probe = new ServiceJdbcProbe();
        if (duplicate) probe.duplicate.add("timeout");
        else probe.empty.add("timeout");
        var error =
            assertThrows(
                SQLDataException.class,
                () -> new MaintenanceMutationGuard(() -> 10_000_000_000L).bind(probe.wrap(c)));
        assertEquals("maintenance timeout unavailable", error.getMessage());
        assertNull(error.getCause());
        assertEquals(duplicate ? 2 : 1, probe.seen.get("timeout.next"));
        assertEquals(1, probe.seen.get("timeout.resultClose"));
        assertEquals(1, probe.seen.get("timeout.statementClose"));
        assertEquals(0, probe.commits);
        assertEquals(0, probe.rollbacks);
        assertEquals(0, probe.closes);
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        // Real set_config ran even though its public result cardinality was corrupted.
        assertEquals("5s", query(c, "show statement_timeout"));
        c.rollback();
        c.setAutoCommit(true);
        assertEquals("30min", query(c, "show statement_timeout"));
      }
    }
  }
}
