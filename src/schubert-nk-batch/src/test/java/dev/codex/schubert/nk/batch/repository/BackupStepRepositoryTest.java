package dev.codex.schubert.nk.batch.repository;

import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.COLUMNS;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.CONTENT;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.END;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.Probe;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.RUNNING;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.START;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.SUCCEEDED;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.failed;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.inventory;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.locked;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.manifest;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.query;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.reset;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.seedSuccess;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.sql;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.state;
import static dev.codex.schubert.nk.batch.repository.BackupStepFixture.trace;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.sql.Connection;
import java.time.Instant;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/BAK/BKO/OPS009/UI251/SS331 8.3/341 6.6; PG168/SSC061; BAT210..217. */
final class BackupStepRepositoryTest {
  private static final String FIXTURE_RUNNING_294BDBF9 = "RUNNING";
  private static final String FIXTURE_STATUS_CFC31BCC = "status";
  private static final String FIXTURE_ENDED_AT_E151E393 = "ended_at";
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

  @BeforeEach
  void seed() throws Exception {
    reset(db);
  }

  @Test
  void runningAndCommittedPair() throws Exception {
    for (boolean reverse : new boolean[] {false, true}) {
      reset(db, reverse);
      try (var c = locked(db, false)) {
        var probe = new Probe();
        var repo = new BackupStepRepository(probe.wrap(c));
        assertTrue(repo.inspect(manifest(reverse), END).isEmpty());
        assertEquals(inventory(false, false), probe.seen);
        assertEquals(70, probe.seen.values().stream().mapToInt(Integer::intValue).sum());
        assertEquals(new TreeSet<>(COLUMNS), probe.columns);
        probe.closed();
        seedSuccess(c);
        assertEquals(
            Optional.of(END),
            new BackupStepRepository(c).inspect(manifest(reverse), END.plusSeconds(1)));
        // BUG191/YKT151: the oracle is UTC microseconds, independent of JDBC session display.
        for (String zone : List.of("UTC", "Asia/Tokyo")) {
          try (var statement = c.createStatement()) {
            statement.execute("set time zone '" + zone + "'");
          }
          assertEquals(SUCCEEDED, state(c));
          assertEquals(
              Optional.of(END),
              new BackupStepRepository(c).inspect(manifest(reverse), END.plusSeconds(1)));
        }
        c.rollback();
      }
    }
  }

  @Test
  void fullHandleAndMissingRows() throws Exception {
    Map<String, Object> bad =
        Map.of(
            "id",
            99999L,
            "run_id",
            new UUID(0, 99),
            "business_date",
            LocalDate.of(2026, 9, 14),
            "step",
            "CLEAN_SESSION",
            "attempt",
            2,
            "started_at",
            START.plusSeconds(1).atOffset(ZoneOffset.UTC));
    try (var c = locked(db, false)) {
      for (int row : new int[] {1, 2})
        for (var entry : bad.entrySet()) {
          var p = new Probe();
          p.change(row, entry.getKey(), entry.getValue());
          failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
          p.closed();
          c.rollback();
          assertEquals(RUNNING, state(c));
        }
      var duplicate = new Probe();
      duplicate.change(2, "id", 90001L);
      failed(() -> new BackupStepRepository(duplicate.wrap(c)).inspect(manifest(), END));
      duplicate.closed();
      c.rollback();
      for (String shape : List.of("empty", "one", "extra")) {
        var p = new Probe();
        p.anomaly = shape;
        failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
        p.closed();
        c.rollback();
      }
    }
  }

  @Test
  void statusCounterAndTimeMatrix() throws Exception {
    List<String> statuses =
        List.of(FIXTURE_RUNNING_294BDBF9, "SUCCESS", "WARNING", "FAILED", "SKIPPED", "UNKNOWN", "");
    try (var c = locked(db, false)) {
      for (String left : statuses)
        for (String right : statuses) {
          var p = new Probe();
          p.change(1, FIXTURE_STATUS_CFC31BCC, left);
          p.change(2, FIXTURE_STATUS_CFC31BCC, right);
          if (left.equals(FIXTURE_RUNNING_294BDBF9) && right.equals(FIXTURE_RUNNING_294BDBF9))
            assertTrue(new BackupStepRepository(p.wrap(c)).inspect(manifest(), END).isEmpty());
          else failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
          p.closed();
          c.rollback();
        }
      for (String col : List.of("target_count", "success_count", "failure_count", "byte_count"))
        for (long bad : new long[] {-1, 1, Long.MAX_VALUE}) {
          var p = new Probe();
          p.change(1, col, bad);
          failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
          p.closed();
          c.rollback();
        }
      for (String col : List.of(FIXTURE_ENDED_AT_E151E393, "error_code", "error_summary")) {
        var p = new Probe();
        p.change(
            1,
            col,
            col.equals(FIXTURE_ENDED_AT_E151E393) ? END.atOffset(ZoneOffset.UTC) : "PUBLIC");
        failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
        p.closed();
        c.rollback();
      }
      seedSuccess(c);
      c.commit();
      for (int row : new int[] {1, 2})
        for (String col : List.of("target_count", "success_count", "failure_count", "byte_count")) {
          var p = new Probe();
          p.change(row, col, -1L);
          failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
          p.closed();
          c.rollback();
        }
      for (OffsetDateTime wrong :
          List.of(
              CONTENT.minusNanos(1000).atOffset(ZoneOffset.UTC),
              END.plusSeconds(1).atOffset(ZoneOffset.UTC),
              CONTENT.plusNanos(1).atOffset(ZoneOffset.UTC))) {
        var p = new Probe();
        p.change(1, FIXTURE_ENDED_AT_E151E393, wrong);
        failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
        p.closed();
        c.rollback();
      }
      var split = new Probe();
      split.change(1, FIXTURE_ENDED_AT_E151E393, CONTENT.atOffset(ZoneOffset.UTC));
      failed(() -> new BackupStepRepository(split.wrap(c)).inspect(manifest(), END));
      split.closed();
      c.rollback();
      for (String status :
          List.of(FIXTURE_RUNNING_294BDBF9, "FAILED", "WARNING", "SKIPPED", "UNKNOWN")) {
        var p = new Probe();
        p.change(1, FIXTURE_STATUS_CFC31BCC, status);
        failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
        p.closed();
        c.rollback();
      }
    }
  }

  @Test
  void atomicPairAndReplay() throws Exception {
    try (var c = locked(db, false);
        var admin = db.admin()) {
      var p = new Probe();
      var repo = new BackupStepRepository(p.wrap(c));
      assertEquals(END, repo.complete(manifest(), END));
      assertEquals(inventory(true, false), p.seen);
      assertEquals(240, p.seen.values().stream().mapToInt(Integer::intValue).sum());
      p.closed();
      assertEquals(SUCCEEDED, state(c));
      assertEquals(RUNNING, state(admin));
      c.rollback();
      assertEquals(RUNNING, state(c));
      assertEquals(END, new BackupStepRepository(c).complete(manifest(), END));
      c.commit();
      var replay = new Probe();
      assertEquals(
          END, new BackupStepRepository(replay.wrap(c)).complete(manifest(), END.plusSeconds(60)));
      assertEquals(inventory(false, false), replay.seen);
      replay.closed();
      assertEquals(SUCCEEDED, state(admin));
      c.rollback();
      trace("PT-BAT-213-pair.txt", state(admin) + "\n");
    }
    reset(db);
    for (boolean pending : new boolean[] {false, true}) {
      try (var c = locked(db, false)) {
        var p = new Probe();
        p.overrideSequence = 2;
        for (int row : new int[] {1, 2}) {
          p.change(
              row, FIXTURE_ENDED_AT_E151E393, pending ? null : CONTENT.atOffset(ZoneOffset.UTC));
          if (pending) {
            p.change(row, FIXTURE_STATUS_CFC31BCC, FIXTURE_RUNNING_294BDBF9);
            for (String col :
                List.of("target_count", "success_count", "failure_count", "byte_count"))
              p.change(row, col, 0L);
          }
        }
        failed(() -> new BackupStepRepository(p.wrap(c)).complete(manifest(), END));
        p.closed();
        c.rollback();
        assertEquals(RUNNING, state(c));
      }
    }
  }

  @Test
  void databaseGuardsAndLocks() throws Exception {
    try (var c = db.open("schubert_batch")) {
      c.setAutoCommit(false);
      failed(() -> new BackupStepRepository(c).inspect(manifest(), END));
      c.rollback();
    }
    try (var c = locked(db, true)) {
      failed(() -> new BackupStepRepository(c).inspect(manifest(), END));
      c.setAutoCommit(false);
      c.setReadOnly(true);
      failed(() -> new BackupStepRepository(c).inspect(manifest(), END));
      c.setReadOnly(false);
      c.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
      failed(() -> new BackupStepRepository(c).inspect(manifest(), END));
      c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      var p = new Probe();
      p.badReferences = 1;
      failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
      p.closed();
      c.rollback();
      try (var admin = db.admin()) {
        admin.setAutoCommit(false);
        sql(admin, "select id from schubert.batch_runs where id=90002 for update");
        failed(() -> new BackupStepRepository(c).inspect(manifest(), END));
        c.rollback();
        admin.rollback();
      }
    }
    // Existing independent migration inventory and hashes are enforced in every fixture
    // startup/full reactor.
    try (var admin = db.admin()) {
      assertEquals(
          "28",
          query(
              admin,
              "select count(*) from schubert_meta.flyway_schema_history where success and version is not null and type='SQL'"));
      assertEquals(
          "1",
          query(
              admin,
              "select count(*) from schubert_meta.flyway_schema_history where success and version is null and type='SCHEMA'"));
    }
  }

  @Test
  void everyJdbcFault() throws Exception {
    int failures = 0;
    for (int mode = 0; mode < 3; mode++) {
      reset(db);
      if (mode == 2)
        try (var admin = db.admin()) {
          seedSuccess(admin);
        }
      final int selected = mode;
      Map<String, Integer> expected = inventory(mode == 1, false);
      try (var c = locked(db, false)) {
        for (var entry : expected.entrySet())
          for (int occurrence = 1; occurrence <= entry.getValue(); occurrence++) {
            var p = new Probe();
            p.fail(entry.getKey(), occurrence);
            failed(
                () -> {
                  var repo = new BackupStepRepository(p.wrap(c));
                  if (selected == 0) repo.inspect(manifest(), END);
                  else repo.complete(manifest(), END);
                });
            assertEquals(1, p.hits, entry.getKey() + "#" + occurrence);
            p.closed();
            failures++;
            c.rollback();
            assertEquals(mode == 2 ? SUCCEEDED : RUNNING, state(c));
          }
      }
    }
    assertEquals(380, failures);
    trace("PT-BAT-215-jdbc.txt", "read=70\nnew=240\nreplay=70\ninjected=" + failures + "\n");
  }

  @Test
  void nullAndUnknownFailures() throws Exception {
    pairResourceCompounds();
    try (var c = locked(db, false)) {
      var p = new Probe();
      var original = new IllegalStateException("public same backup fixture");
      p.compound.put("pair.row.next", original);
      p.compound.put("pair.row.close", original);
      try {
        assertSame(
            original,
            assertThrows(
                Throwable.class,
                () -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END)));
        assertEquals(2, p.compoundInjected);
        p.closed();
      } finally {
        c.rollback();
      }
    }
    assertThrows(NullPointerException.class, () -> new BackupStepRepository(null));
    try (var c = locked(db, false)) {
      var repo = new BackupStepRepository(c);
      assertThrows(NullPointerException.class, () -> repo.inspect(null, END));
      assertThrows(NullPointerException.class, () -> repo.complete(manifest(), null));
      for (Instant wrong :
          List.of(
              CONTENT.minusNanos(1000), END.plusNanos(1), Instant.parse("+10000-01-01T00:00:00Z")))
        assertThrows(IllegalArgumentException.class, () -> repo.inspect(manifest(), wrong));
      for (String anomaly : List.of("nullStatement", "nullRows")) {
        var p = new Probe();
        p.anomaly = anomaly;
        failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
        p.closed();
        c.rollback();
      }
      for (String col : COLUMNS) {
        if (Set.of(FIXTURE_ENDED_AT_E151E393, "error_code", "error_summary").contains(col))
          continue;
        var p = new Probe();
        p.change(1, col, null);
        failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
        p.closed();
        c.rollback();
      }
      seedSuccess(c);
      c.commit();
      var nilEnd = new Probe();
      nilEnd.change(1, FIXTURE_ENDED_AT_E151E393, null);
      failed(() -> new BackupStepRepository(nilEnd.wrap(c)).inspect(manifest(), END));
      nilEnd.closed();
      c.rollback();
      for (Throwable primary :
          List.of(
              new IllegalStateException("public"),
              new NullPointerException("public"),
              new AssertionError("public"))) {
        var p = new Probe();
        p.unknown.put("pair.row.next", primary);
        assertSame(
            primary,
            assertThrows(
                primary.getClass(),
                () -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END)));
        p.closed();
        c.rollback();
      }
      for (boolean early : new boolean[] {false, true}) {
        var p = new Probe();
        p.after =
            (key, n) -> {
              if (!early && key.equals("pair.statement.close")) Thread.currentThread().interrupt();
            };
        if (early) Thread.currentThread().interrupt();
        try {
          failed(() -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END));
          assertTrue(Thread.currentThread().isInterrupted());
          p.closed();
        } finally {
          Thread.interrupted();
          c.rollback();
        }
      }
    }
  }

  private void pairResourceCompounds() throws Exception {
    try (var c = locked(db, false)) {
      for (var sample : JdbcResourceCases.all()) {
        var p = new Probe();
        if (sample.primary() != null) p.compound.put("pair." + sample.body(), sample.primary());
        p.compound.put("pair." + sample.close(), sample.secondary());
        sample.verify(
            assertThrows(
                Throwable.class,
                () -> new BackupStepRepository(p.wrap(c)).inspect(manifest(), END)));
        assertEquals(sample.primary() == null ? 1 : 2, p.compoundInjected);
        assertEquals(1, p.seen.get("pair.statement.close"));
        assertEquals(
            sample.body().equals("statement.executeQuery") && sample.primary() != null ? 0 : 1,
            p.seen.getOrDefault("pair.row.close", 0));
        p.closed();
        for (String key :
            List.of(
                "connection.commit",
                "connection.rollback",
                "connection.close",
                "connection.setAutoCommit")) assertFalse(p.seen.containsKey(key));
        assertFalse(c.getAutoCommit());
        c.rollback();
        assertEquals(RUNNING, state(c));
        c.rollback();
      }
    }
  }

  @Test
  void concurrentBindings() throws Exception {
    try (var pool = Executors.newFixedThreadPool(8)) {
      List<Future<Instant>> futures = new ArrayList<>();
      for (int i = 0; i < 16; i++)
        futures.add(
            pool.submit(
                () -> {
                  try (var c = locked(db, false)) {
                    var end = new BackupStepRepository(c).complete(manifest(), END);
                    c.commit();
                    return end;
                  }
                }));
      for (var f : futures) assertEquals(END, f.get(20, TimeUnit.SECONDS));
    }
    try (var admin = db.admin()) {
      assertEquals(SUCCEEDED, state(admin));
      assertEquals("2", query(admin, "select count(*) from schubert.batch_runs"));
    }
  }
}
