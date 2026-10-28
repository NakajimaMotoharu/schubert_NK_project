package dev.codex.schubert.nk.batch.backup;

import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.CONTENT;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.END;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.Probe;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.RUNNING;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.SUCCEEDED;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.failed;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.inventory;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.locked;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.manifest;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.query;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.reset;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.sql;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.state;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.trace;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/BAK/BKO/OPS009/UI251/SS341 6.6; PG168/SSC061; BAT218..225. */
final class BackupCommitServiceTest {
  private static final String FIXTURE_PAIR_ROW_NEXT_29F9C13D = "pair.row.next";
  private static final String FIXTURE_CONNECTION_ROLLBACK_9F978A8C = "connection.rollback";
  private static final String FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D =
      "connection.setAutoCommit";
  private static final String FIXTURE_CONNECTION_COMMIT_37C1B216 = "connection.commit";
  private static final String FIXTURE_PUBLIC_B7853257 = "public";
  @TempDir static Path root;
  static BatchDatabaseFixture db;

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  // BUG193/YKT152: declared, unknown and same-object cleanup failures.
  private static void unknownCleanupMatrix() throws Exception {
    for (int main = 0; main < 5; main++)
      for (int other = 0; other < 6; other++)
        for (boolean restore : new boolean[] {false, true}) {
          reset(db);
          try (var c = locked(db, true)) {
            Throwable primary = cleanupFault(main);
            Throwable secondary = other == 5 ? primary : cleanupFault(other);
            var p = new Probe();
            int[] injected = {0, 0};
            p.before =
                (key, count) -> {
                  if (key.equals(FIXTURE_PAIR_ROW_NEXT_29F9C13D) && count == 1) {
                    injected[0]++;
                    throw primary;
                  }
                  if ((!restore && key.equals(FIXTURE_CONNECTION_ROLLBACK_9F978A8C) && count == 1)
                      || (restore
                          && key.equals(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D)
                          && count == 2)) {
                    injected[1]++;
                    throw secondary;
                  }
                };
            boolean primaryUnknown = main >= 2;
            boolean secondaryUnknown = other >= 2 && other <= 4 || other == 5 && main >= 2;
            if (primaryUnknown || secondaryUnknown) {
              Throwable expected = primaryUnknown ? primary : secondary;
              assertSame(
                  expected,
                  assertThrows(
                      expected.getClass(),
                      () -> new BackupCommitService().complete(p.wrap(c), manifest(), END)));
              assertEquals(primaryUnknown ? 1 : 0, expected.getSuppressed().length);
              if (primaryUnknown) {
                var fixed =
                    assertInstanceOf(BatchRepositoryException.class, expected.getSuppressed()[0]);
                assertNull(fixed.getCause());
                assertEquals("batch repository operation failed", fixed.getMessage());
              }
            } else {
              failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
            }
            assertArrayEquals(new int[] {1, 1}, injected);
            assertEquals(restore ? 2 : 1, p.seen.get(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D));
            assertFalse(c.getAutoCommit());
            p.closed();
            c.rollback();
          }
        }
  }

  private static Throwable cleanupFault(int kind) {
    return switch (kind) {
      case 0 -> new SQLException("public SQL");
      case 1 -> new BatchRepositoryException();
      case 2 -> new IllegalStateException("public runtime");
      case 3 -> new NullPointerException("public null");

      default -> new AssertionError("public fatal");
    };
  }

  @BeforeEach
  void seed() throws Exception {
    reset(db);
  }

  @Test
  void commitAndExistingReceipt() throws Exception {
    try (var c = locked(db, true);
        var admin = db.admin()) {
      var service = new BackupCommitService();
      var p = new Probe();
      assertEquals(END, service.complete(p.wrap(c), manifest(), END));
      assertEquals(inventory(true, true), p.seen);
      assertEquals(246, p.seen.values().stream().mapToInt(Integer::intValue).sum());
      p.closed();
      assertTrue(c.getAutoCommit());
      assertFalse(c.isClosed());
      assertEquals(SUCCEEDED, state(admin));
      var again = new Probe();
      assertEquals(END, service.complete(again.wrap(c), manifest(), END.plusSeconds(99)));
      assertEquals(inventory(false, true), again.seen);
      again.closed();
      assertEquals(SUCCEEDED, state(admin));
      trace(
          "PT-BAT-218-commit.txt",
          "fresh_jdbc="
              + p.seen.values().stream().mapToInt(Integer::intValue).sum()
              + "\nreplay_jdbc="
              + again.seen.values().stream().mapToInt(Integer::intValue).sum()
              + "\n"
              + state(admin)
              + "\n");
    }
  }

  @Test
  void rollbackBothSteps() throws Exception {
    try (var c = locked(db, true);
        var admin = db.admin()) {
      var p = new Probe();
      p.fail("update.statement.executeUpdate", 2);
      failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
      assertEquals(1, p.hits);
      p.closed();
      assertEquals(RUNNING, state(admin));
      assertTrue(c.getAutoCommit());
      assertEquals(1, p.seen.get(FIXTURE_CONNECTION_ROLLBACK_9F978A8C));
      assertFalse(p.seen.containsKey(FIXTURE_CONNECTION_COMMIT_37C1B216));
      // The old other run remains untouched by either rollback or a later successful retry.
      sql(
          admin,
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,byte_count) values "
              + "(80000,'00000000-0000-0000-0000-000000000001','2026-09-12','BACKUP_DB',1,'2026-09-12T01:00:00Z','2026-09-12T01:00:01Z','SUCCESS',1,1,7)");
      assertEquals(END, new BackupCommitService().complete(c, manifest(), END));
      assertEquals(
          "SUCCESS|7",
          query(admin, "select status||'|'||byte_count from schubert.batch_runs where id=80000"));
    }
  }

  @Test
  void uncertainCommitReplay() throws Exception {
    for (boolean committed : new boolean[] {false, true}) {
      reset(db);
      try (var c = locked(db, true);
          var admin = db.admin()) {
        var p = new Probe();
        if (committed)
          p.after =
              (key, n) -> {
                if (key.equals(FIXTURE_CONNECTION_COMMIT_37C1B216))
                  throw new SQLException("PUBLIC_DIAGNOSTIC_CANARY");
              };
        else p.fail(FIXTURE_CONNECTION_COMMIT_37C1B216, 1);
        failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
        p.closed();
        assertEquals(committed ? SUCCEEDED : RUNNING, state(admin));
      }
      try (var retry = locked(db, true);
          var admin = db.admin()) {
        var p = new Probe();
        Instant requested = committed ? END.plusSeconds(1) : END;
        assertEquals(END, new BackupCommitService().complete(p.wrap(retry), manifest(), requested));
        assertEquals(inventory(!committed, true), p.seen);
        p.closed();
        assertEquals(SUCCEEDED, state(admin));
        trace(
            "PT-BAT-220-uncertain-" + committed + ".txt",
            "committed_before_failure="
                + committed
                + "\nretry_updates="
                + p.seen.getOrDefault("update.statement.executeUpdate", 0)
                + "\n"
                + state(admin)
                + "\n");
      }
    }
  }

  @Test
  void connectionContract() throws Exception {
    var service = new BackupCommitService();
    assertThrows(NullPointerException.class, () -> service.complete(null, manifest(), END));
    try (var c = locked(db, true)) {
      assertThrows(NullPointerException.class, () -> service.complete(c, null, END));
      assertThrows(NullPointerException.class, () -> service.complete(c, manifest(), null));
      c.setAutoCommit(false);
      failed(() -> service.complete(c, manifest(), END));
      c.rollback();
      c.setAutoCommit(true);
      c.setReadOnly(true);
      failed(() -> service.complete(c, manifest(), END));
      c.setReadOnly(false);
      c.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
      failed(() -> service.complete(c, manifest(), END));
      c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      for (Instant wrong :
          List.of(
              CONTENT.minusNanos(1000),
              END.plusNanos(1),
              Instant.parse("+10000-01-01T00:00:00Z"))) {
        assertThrows(IllegalArgumentException.class, () -> service.complete(c, manifest(), wrong));
        assertTrue(c.getAutoCommit());
        assertEquals(RUNNING, state(c));
      }
    }
    var closed = locked(db, true);
    closed.close();
    failed(() -> service.complete(closed, manifest(), END));
  }

  @Test
  void everyBoundaryFailure() throws Exception {
    int count = 0;
    for (var entry : inventory(true, true).entrySet())
      for (int occurrence = 1; occurrence <= entry.getValue(); occurrence++) {
        reset(db);
        try (var c = locked(db, true);
            var admin = db.admin()) {
          var p = new Probe();
          p.fail(entry.getKey(), occurrence);
          failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
          assertEquals(1, p.hits, entry.getKey() + "#" + occurrence);
          p.closed();
          boolean committed =
              entry.getKey().equals(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D) && occurrence == 2;
          assertEquals(committed ? SUCCEEDED : RUNNING, state(admin));
          count++;
          if (!c.getAutoCommit()) c.rollback();
        }
      }
    assertEquals(246, count);
    for (boolean rollbackFails : new boolean[] {false, true}) {
      reset(db);
      try (var c = locked(db, true);
          var admin = db.admin()) {
        var p = new Probe();
        p.fail("update.statement.executeUpdate", 2);
        p.fail(
            rollbackFails
                ? FIXTURE_CONNECTION_ROLLBACK_9F978A8C
                : FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D,
            rollbackFails ? 1 : 2);
        failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
        p.closed();
        assertEquals(2, p.hits);
        assertEquals(rollbackFails ? 1 : 2, p.seen.get(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D));
        assertFalse(c.getAutoCommit());
        assertEquals(RUNNING, state(admin));
        c.rollback();
      }
    }
  }

  @Test
  void interruptionAfterCommit() throws Exception {
    int interrupted = 0;
    for (var entry : inventory(true, true).entrySet())
      for (int occurrence = 1; occurrence <= entry.getValue(); occurrence++) {
        reset(db);
        final int at = occurrence;
        try (var c = locked(db, true);
            var admin = db.admin()) {
          var p = new Probe();
          boolean[] injected = {false};
          p.before =
              (key, n) -> {
                if (key.equals(entry.getKey()) && n == at) {
                  injected[0] = true;
                  Thread.currentThread().interrupt();
                }
              };
          try {
            failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
            assertTrue(injected[0]);
            assertTrue(Thread.currentThread().isInterrupted());
            p.closed();
            interrupted++;
          } finally {
            Thread.interrupted();
          }
          boolean committed =
              entry.getKey().equals(FIXTURE_CONNECTION_COMMIT_37C1B216)
                  || entry.getKey().equals(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D) && at == 2;
          assertEquals(committed ? SUCCEEDED : RUNNING, state(admin));
          if (!c.getAutoCommit()) c.rollback();
        } finally {
          Thread.interrupted();
        }
      }
    assertEquals(246, interrupted);
    try (var c = locked(db, true)) {
      var p = new Probe();
      Thread.currentThread().interrupt();
      try {
        failed(() -> new BackupCommitService().complete(p.wrap(c), manifest(), END));
        assertTrue(p.seen.isEmpty());
      } finally {
        Thread.interrupted();
      }
    }
  }

  @Test
  void unknownPrimaryAndCleanup() throws Exception {
    unknownCleanupMatrix();
    // BUG193: a provider-contract failure during rollback must not erase the primary.
    try (var c = locked(db, true)) {
      var primary = new IllegalStateException("public primary");
      var p = new Probe();
      p.unknown.put(FIXTURE_PAIR_ROW_NEXT_29F9C13D, primary);
      p.unknown.put(
          FIXTURE_CONNECTION_ROLLBACK_9F978A8C, new NullPointerException("public secondary"));
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class,
              () -> new BackupCommitService().complete(p.wrap(c), manifest(), END)));
      p.closed();
      assertEquals(1, primary.getSuppressed().length);
      c.rollback();
    }
    for (Throwable primary :
        List.of(
            new IllegalStateException(FIXTURE_PUBLIC_B7853257),
            new IllegalArgumentException(FIXTURE_PUBLIC_B7853257),
            new NullPointerException(FIXTURE_PUBLIC_B7853257),
            new AssertionError(FIXTURE_PUBLIC_B7853257)))
      for (int cleanup = 0; cleanup < 3; cleanup++) {
        reset(db);
        try (var c = locked(db, true)) {
          var p = new Probe();
          p.unknown.put(FIXTURE_PAIR_ROW_NEXT_29F9C13D, primary);
          if (cleanup == 1) p.fail(FIXTURE_CONNECTION_ROLLBACK_9F978A8C, 1);
          if (cleanup == 2) p.fail(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D, 2);
          // Each crossing uses a new throwable so earlier suppressed failures cannot leak into this
          // case.
          Throwable unique;
          if (primary instanceof AssertionError)
            unique = new AssertionError(FIXTURE_PUBLIC_B7853257);
          else if (primary instanceof NullPointerException)
            unique = new NullPointerException(FIXTURE_PUBLIC_B7853257);
          else if (primary instanceof IllegalArgumentException)
            unique = new IllegalArgumentException(FIXTURE_PUBLIC_B7853257);
          else unique = new IllegalStateException(FIXTURE_PUBLIC_B7853257);
          p.unknown.put(FIXTURE_PAIR_ROW_NEXT_29F9C13D, unique);
          assertSame(
              unique,
              assertThrows(
                  unique.getClass(),
                  () -> new BackupCommitService().complete(p.wrap(c), manifest(), END)));
          p.closed();
          assertEquals(cleanup == 0 ? 0 : 1, unique.getSuppressed().length);
          if (cleanup != 0) {
            assertEquals(1, p.hits);
            var second =
                assertInstanceOf(BatchRepositoryException.class, unique.getSuppressed()[0]);
            assertEquals("batch repository operation failed", second.getMessage());
            assertNull(second.getCause());
          }
          if (!c.getAutoCommit()) c.rollback();
        }
      }
  }

  @Test
  void independentConnections() throws Exception {
    try (var pool = Executors.newFixedThreadPool(8)) {
      List<Future<Instant>> tasks = new ArrayList<>();
      for (int i = 0; i < 16; i++)
        tasks.add(
            pool.submit(
                () -> {
                  try (var c = locked(db, true)) {
                    return new BackupCommitService().complete(c, manifest(), END);
                  }
                }));
      for (var task : tasks) assertEquals(END, task.get(20, TimeUnit.SECONDS));
    }
    try (var c = db.admin()) {
      assertEquals(SUCCEEDED, state(c));
      assertEquals("2", query(c, "select count(*) from schubert.batch_runs"));
    }
  }
}
