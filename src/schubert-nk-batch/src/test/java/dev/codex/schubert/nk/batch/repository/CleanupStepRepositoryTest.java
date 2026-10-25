package dev.codex.schubert.nk.batch.repository;

import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.COLS;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.KINDS;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.Probe;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.RUN;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.START;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.attempt;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.locked;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.query;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.repositoryInventory;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.reset;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.sql;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.totals;
import static dev.codex.schubert.nk.batch.repository.CleanupStepFixture.trace;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Path;
import java.sql.Connection;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.TreeSet;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT162..169. */
final class CleanupStepRepositoryTest {
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
  void actualSevenKindsAndStepTotals() throws Exception {
    long[] deltas = {1, 1, 3, 2, 1, 1, 1};
    long[] totals = {1, 1, 3, 2, 1, 2, 3};
    StringBuilder trace = new StringBuilder();
    try (var c = locked(db, false)) {
      var repo = new CleanupStepRepository(c);
      for (int i = 0; i < KINDS.size(); i++) {
        var k = KINDS.get(i);
        var a = attempt(k);
        var r = repo.execute(a, k, 1000);
        assertEquals(new CleanupCounts(deltas[i], deltas[i], 0), r.counts());
        assertEquals(Optional.of(new CleanupCounts(totals[i], totals[i], 0)), r.stepCounts());
        assertEquals(
            Optional.of(new CleanupCounts(totals[i] - deltas[i], totals[i] - deltas[i], 0)),
            r.beforeCounts());
        assertFalse(r.complete());
        assertEquals(CleanupStepChunk.Reason.OK, r.reason());
        assertEquals("RUNNING|" + totals[i] + "|" + totals[i] + "|0|0|true", totals(c, a.id()));
        c.commit();
        var end = repo.execute(a, k, 1000);
        assertTrue(end.complete());
        assertEquals(new CleanupCounts(0, 0, 0), end.counts());
        trace
            .append(k.name())
            .append('=')
            .append(r.stepCounts().orElseThrow().target())
            .append('|')
            .append(r.counts().deleted())
            .append('|')
            .append(end.complete() ? "END" : "OPEN")
            .append('\n');
        c.commit();
      }
    }
    trace("PT-BAT-162-seven-kinds.txt", trace.toString());
  }

  @Test
  void borrowedStateAndMapping() throws Exception {
    assertThrows(NullPointerException.class, () -> new CleanupStepRepository(null));
    for (String mode : List.of("auto", "readonly", "repeatable", "serializable", "noLock")) {
      try (var c = db.open("schubert_batch")) {
        if (!mode.equals("noLock")) sql(c, "select pg_advisory_lock(71419602)");
        if (mode.equals("readonly")) c.setReadOnly(true);
        if (mode.equals("repeatable"))
          c.setTransactionIsolation(Connection.TRANSACTION_REPEATABLE_READ);
        if (mode.equals("serializable"))
          c.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
        c.setAutoCommit(mode.equals("auto"));
        var p = new Probe();
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000)));
        p.closed();
        assertFalse(p.seen.containsKey("connection.commit"));
        assertFalse(p.seen.containsKey("connection.setAutoCommit"));
        if (!c.getAutoCommit()) c.rollback();
      }
    }
    try (var c = locked(db, false)) {
      var p = new Probe();
      var repo = new CleanupStepRepository(p.wrap(c));
      var a = attempt(CleanupKind.QUESTIONS);
      for (int limit : new int[] {Integer.MIN_VALUE, 0, 1001, Integer.MAX_VALUE})
        assertThrows(
            IllegalArgumentException.class, () -> repo.execute(a, CleanupKind.QUESTIONS, limit));
      assertThrows(NullPointerException.class, () -> repo.execute(null, CleanupKind.QUESTIONS, 1));
      assertThrows(NullPointerException.class, () -> repo.execute(a, null, 1));
      assertThrows(IllegalArgumentException.class, () -> repo.execute(a, CleanupKind.OUTBOX, 1));
      assertThrows(
          IllegalArgumentException.class,
          () -> repo.execute(attempt(CleanupKind.LOGS), CleanupKind.LOGS, 1));
      assertTrue(p.seen.isEmpty());
      c.rollback();
    }
  }

  @Test
  void nullAndProjection() throws Exception {
    for (String anomaly : List.of("nullStatement", "nullRows", "empty", "extra")) {
      try (var c = locked(db, false)) {
        var p = new Probe();
        p.anomaly = anomaly;
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000),
                anomaly));
        p.closed();
        c.rollback();
      }
    }
    for (String col : COLS) {
      try (var c = locked(db, false)) {
        var p = new Probe();
        p.overrides.put(col, null);
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000),
                col));
        p.closed();
        c.rollback();
      }
    }
    var corrupt =
        List.<Map<String, Object>>of(
            Map.of("target_count", -1L),
            Map.of("deleted_count", -1L),
            Map.of("skipped_count", -1L),
            Map.of(
                "target_count",
                1001L,
                "deleted_count",
                1001L,
                "step_target_count",
                1001L,
                "step_success_count",
                1001L),
            Map.of("deleted_count", 2L),
            Map.of("skipped_count", 1L),
            Map.of("reason_code", "UNKNOWN"),
            Map.of("step_target_count", 0L, "step_success_count", 0L),
            Map.of("step_target_count", -1L),
            Map.of("step_success_count", 2L),
            Map.of("complete", true),
            Map.of("reason_code", "LOCK_BUSY"),
            Map.of("step_target_count", 1L, "step_success_count", 0L));
    for (var override : corrupt)
      try (var c = locked(db, false)) {
        var p = new Probe();
        p.overrides.putAll(override);
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000)));
        p.closed();
        c.rollback();
      }
    for (int refs : new int[] {1, 2})
      try (var c = locked(db, false)) {
        var p = new Probe();
        p.badRefs = refs;
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000)));
        p.closed();
        c.rollback();
      }
  }

  @Test
  void allJdbcFailures() throws Exception {
    var inventory = repositoryInventory();
    int observed;
    assertEquals(53, inventory.values().stream().mapToInt(Integer::intValue).sum());
    try (var c = locked(db, false)) {
      var p = new Probe();
      new CleanupStepRepository(p.wrap(c))
          .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000);
      assertEquals(inventory, p.seen);
      observed = p.seen.values().stream().mapToInt(Integer::intValue).sum();
      assertEquals(new TreeSet<>(COLS), p.columns);
      p.closed();
      c.rollback();
    }
    int tried = 0;
    for (var e : inventory.entrySet())
      for (int i = 1; i <= e.getValue(); i++) {
        try (var c = locked(db, false)) {
          var p = new Probe();
          p.fail(e.getKey(), i);
          redacted(
              assertThrows(
                  BatchRepositoryException.class,
                  () ->
                      new CleanupStepRepository(p.wrap(c))
                          .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000),
                  e.getKey() + ":" + i));
          assertEquals(1, p.failures);
          p.closed();
          assertFalse(c.getAutoCommit());
          c.rollback();
          try (var admin = db.admin()) {
            assertEquals("1", query(admin, "select count(*) from schubert.questions where id=2"));
            assertEquals("RUNNING|0|0|0|0|true", totals(admin, 90011));
          }
          tried++;
        }
      }
    int pairs = 0;
    for (int close : new int[] {1, 2, 3})
      try (var c = locked(db, false)) {
        var p = new Probe();
        p.fail("row.close", close);
        p.fail("statement.close", close);
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000)));
        assertEquals(2, p.failures);
        pairs++;
        p.closed();
        c.rollback();
      }
    assertEquals(53, tried);
    trace(
        "PT-BAT-165-jdbc.txt",
        "repository="
            + observed
            + "\nfault_positions="
            + tried
            + "\ndouble_close_pairs="
            + pairs
            + "\n");
  }

  @Test
  void rejectionReasonsAndUnknownTotals() throws Exception {
    try (var admin = db.admin()) {
      sql(admin, "update schubert.batch_runs set status='FAILED' where id=90000");
      try (var c = locked(db, false)) {
        var p = new Probe();
        var r =
            new CleanupStepRepository(p.wrap(c))
                .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000);
        assertEquals(CleanupStepChunk.Reason.BACKUP_GATE, r.reason());
        assertEquals(Optional.empty(), r.stepCounts());
        assertEquals(Optional.empty(), r.beforeCounts());
        assertFalse(r.complete());
        assertEquals(repositoryInventory(), p.seen);
        p.closed();
        c.rollback();
      }
      sql(admin, "update schubert.batch_runs set status='SUCCESS' where id=90000");
      admin.setAutoCommit(false);
      sql(admin, "select id from schubert.batch_runs where id=90011 for update");
      try (var c = locked(db, false)) {
        var r =
            new CleanupStepRepository(c)
                .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000);
        assertEquals(CleanupStepChunk.Reason.LOCK_BUSY, r.reason());
        assertTrue(r.stepCounts().isEmpty());
        c.rollback();
      }
      admin.rollback();
      admin.setAutoCommit(true);
      sql(
          admin,
          "create table public.pg164_repo_fk(id bigint references schubert.questions(id));insert into public.pg164_repo_fk values(2)");
      try (var c = locked(db, false)) {
        var r =
            new CleanupStepRepository(c)
                .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1000);
        assertEquals(CleanupStepChunk.Reason.FOREIGN_KEY_CONFLICT, r.reason());
        assertEquals(Optional.of(new CleanupCounts(0, 0, 0)), r.stepCounts());
        assertFalse(r.complete());
        c.rollback();
      } finally {
        sql(admin, "drop table public.pg164_repo_fk");
      }
    }
  }

  @Test
  void utcFullHandle() throws Exception {
    // Independent SQL timestamp literals, not a production bind used to build its own oracle.
    for (String[] vector :
        List.of(
            new String[] {"0001-01-01T00:00:00Z", "0001-01-01T00:00:01.000001Z"},
            new String[] {"1582-10-04T00:00:00Z", "1582-10-04T00:00:01.000001Z"},
            new String[] {"1582-10-15T00:00:00Z", "1582-10-15T00:00:01.000001Z"},
            new String[] {"1900-01-01T00:00:00Z", "1900-01-01T00:00:01.000001Z"},
            new String[] {"1970-01-01T00:00:00Z", "1970-01-01T00:00:01.000001Z"},
            new String[] {"9999-12-31T14:59:58Z", "9999-12-31T14:59:59.999999Z"}))
      for (String zone : List.of("UTC", "Asia/Tokyo", "America/New_York")) {
        reset(db);
        try (var admin = db.admin();
            var c = locked(db, false)) {
          sql(admin, "delete from schubert.questions where id=2");
          sql(
              admin,
              "update schubert.batch_runs set business_date=(timestamptz '"
                  + vector[0]
                  + "' at time zone 'Asia/Tokyo')::date,started_at='"
                  + vector[0]
                  + "',ended_at=case when status='SUCCESS' then timestamptz '"
                  + vector[0]
                  + "' else null end where run_id='12345678-9abc-def0-8123-456789abcdef'");
          sql(
              admin,
              "update schubert.batch_runs set started_at='" + vector[1] + "' where id=90011");
          sql(c, "set timezone='" + zone + "'");
          var historical =
              new BatchStepAttempt(
                  90011,
                  new BatchRun(RUN.id(), Instant.parse(vector[0])),
                  BatchStep.CLEAN_QUESTION,
                  1,
                  Instant.parse(vector[1]),
                  false);
          var p = new Probe();
          var result =
              new CleanupStepRepository(p.wrap(c)).execute(historical, CleanupKind.QUESTIONS, 1);
          assertTrue(result.complete());
          assertEquals(Optional.of(new CleanupCounts(0, 0, 0)), result.stepCounts());
          assertEquals(OffsetDateTime.parse(vector[0]), p.cleanupBinds.getFirst().get(2));
          assertEquals(OffsetDateTime.parse(vector[1]), p.cleanupBinds.getFirst().get(5));
          p.closed();
          c.rollback();
        }
      }
    reset(db);
    try (var c = locked(db, false)) {
      sql(c, "set timezone='Asia/Tokyo'");
      var p = new Probe();
      new CleanupStepRepository(p.wrap(c))
          .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1);
      assertEquals(
          List.of(
              Map.of(
                  1,
                  UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
                  2,
                  OffsetDateTime.parse("2026-09-12T15:00:00Z"),
                  3,
                  90011L,
                  4,
                  1,
                  5,
                  OffsetDateTime.parse("2026-09-13T02:00:00Z"),
                  6,
                  "QUESTIONS",
                  7,
                  1)),
          p.cleanupBinds);
      c.rollback();
      for (var a :
          List.of(
              new BatchStepAttempt(90010, RUN, BatchStep.CLEAN_QUESTION, 1, START, false),
              new BatchStepAttempt(90011, RUN, BatchStep.CLEAN_QUESTION, 2, START, false),
              new BatchStepAttempt(
                  90011,
                  RUN,
                  BatchStep.CLEAN_QUESTION,
                  1,
                  Instant.parse("2026-09-13T02:00:00.000001Z"),
                  false))) {
        redacted(
            assertThrows(
                BatchRepositoryException.class,
                () -> new CleanupStepRepository(c).execute(a, CleanupKind.QUESTIONS, 1)));
        c.rollback();
      }
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new BatchStepAttempt(
                90011, RUN, BatchStep.CLEAN_QUESTION, 1, START.plusNanos(1), false));
  }

  @Test
  void interruptRuntimeAndResourceOwnership() throws Exception {
    cleanupResourceCompounds();
    assertAll(() -> cleanupOriginalFailure(false), () -> cleanupOriginalFailure(true));
    try (var c = locked(db, false)) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(
            BatchRepositoryException.class,
            () ->
                new CleanupStepRepository(c)
                    .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
        c.rollback();
      }
      for (Throwable t :
          List.of(
              new NullPointerException("public NPE"),
              new UnsupportedOperationException("public runtime"),
              new AssertionError("public error"))) {
        var p = new Probe();
        p.unknown.put("statement.executeQuery", t);
        assertSame(
            t,
            assertThrows(
                t.getClass(),
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1)));
        p.closed();
        c.rollback();
      }
      var p = new Probe();
      p.after =
          (k, n) -> {
            if (k.equals("row.close") && n == 3) Thread.currentThread().interrupt();
          };
      try {
        assertThrows(
            BatchRepositoryException.class,
            () ->
                new CleanupStepRepository(p.wrap(c))
                    .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1));
        assertTrue(Thread.currentThread().isInterrupted());
        p.closed();
      } finally {
        Thread.interrupted();
        c.rollback();
      }
    }
  }

  private void cleanupOriginalFailure(boolean compound) throws Exception {
    try (var c = locked(db, false)) {
      var p = new Probe();
      Throwable primary =
          compound
              ? new IllegalStateException("public same cleanup fixture")
              : new IllegalArgumentException("public provider fixture");
      p.cleanupFaults.put(compound ? "row.next" : "row.getObject", primary);
      if (compound) p.cleanupFaults.put("row.close", primary);
      try {
        assertSame(
            primary,
            assertThrows(
                Throwable.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1)));
        assertEquals(compound ? 2 : 1, p.cleanupInjected);
        p.closed();
      } finally {
        c.rollback();
      }
    }
  }

  private void cleanupResourceCompounds() throws Exception {
    try (var c = locked(db, false);
        var admin = db.admin()) {
      String before = totals(c, 90011);
      String questions = query(admin, "select count(*) from schubert.questions");
      c.rollback();
      for (var sample : JdbcResourceCases.all()) {
        var p = new Probe();
        sample.install(p.cleanupFaults);
        sample.verify(
            assertThrows(
                Throwable.class,
                () ->
                    new CleanupStepRepository(p.wrap(c))
                        .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1)));
        assertEquals(sample.primary() == null ? 1 : 2, p.cleanupInjected);
        assertEquals(1, p.cleanupSeen.get("statement.close"));
        assertEquals(
            sample.body().equals("statement.executeQuery") && sample.primary() != null ? 0 : 1,
            p.cleanupSeen.getOrDefault("row.close", 0));
        p.closed();
        for (String key :
            List.of(
                "connection.commit",
                "connection.rollback",
                "connection.close",
                "connection.setAutoCommit")) assertFalse(p.seen.containsKey(key));
        assertFalse(c.getAutoCommit());
        c.rollback();
        assertEquals(before, totals(c, 90011));
        assertEquals(questions, query(admin, "select count(*) from schubert.questions"));
        c.rollback();
      }
    }
  }

  @Test
  void concurrentTransactionsAndRollback() throws Exception {
    try (var first = locked(db, false);
        var admin = db.admin()) {
      var r =
          new CleanupStepRepository(first)
              .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1);
      assertEquals(new CleanupCounts(1, 1, 0), r.counts());
      assertEquals("1", query(admin, "select count(*) from schubert.questions where id=2"));
      assertEquals("RUNNING|0|0|0|0|true", totals(admin, 90011));
      try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
        var result =
            pool.submit(
                () -> {
                  try (var other = db.open("schubert_batch")) {
                    other.setAutoCommit(false);
                    var e =
                        assertThrows(
                            BatchRepositoryException.class,
                            () ->
                                new CleanupStepRepository(other)
                                    .execute(
                                        attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1));
                    other.rollback();
                    return e.getCause() == null;
                  }
                });
        assertEquals(Boolean.TRUE, result.get(5, TimeUnit.SECONDS));
      }
      first.rollback();
      assertEquals("1", query(admin, "select count(*) from schubert.questions where id=2"));
      new CleanupStepRepository(first)
          .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1);
      first.commit();
      assertEquals("0", query(admin, "select count(*) from schubert.questions where id=2"));
      assertEquals("RUNNING|1|1|0|0|true", totals(admin, 90011));
      var end =
          new CleanupStepRepository(first)
              .execute(attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS, 1);
      assertTrue(end.complete());
      assertEquals(Optional.of(new CleanupCounts(1, 1, 0)), end.stepCounts());
      first.rollback();
    }
  }

  static void redacted(BatchRepositoryException e) {
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
    assertEquals(new BatchRepositoryException().getMessage(), e.getMessage());
  }
}
