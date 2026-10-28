package dev.codex.schubert.nk.batch.cleanup;

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
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupKind;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-BAT-001/OPS009/DAT009/UI251/SS331 3.14/332/341; SSC057/PG164; BAT170..177. */
final class StepCleanupServiceTest {
  private static final String FIXTURE_CONNECTION_ROLLBACK_9F978A8C = "connection.rollback";
  private static final String FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D =
      "connection.setAutoCommit";
  private static final String FIXTURE_CONNECTION_COMMIT_37C1B216 = "connection.commit";
  private static final String FIXTURE_NONE_30A0924A = "none";

  @Test
  void sharedOwnerBoundaryRejectsBeforeCommitButNeverClaimsDurableChunkRollback() throws Exception {
    assertThrows(NullPointerException.class, () -> StepCleanupService.withOwner(null));
    for (int rejected = 1; rejected <= 10; rejected++) {
      reset(db);
      int boundary = rejected;
      var calls = new AtomicInteger();
      dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame.Guard owner =
          () -> {
            if (calls.incrementAndGet() == boundary) throw new java.io.IOException("PRIVATE_OWNER");
            return 10_000_000_000L;
          };
      try (var c = locked(db, true);
          var admin = db.admin()) {
        var probe = new ServiceJdbcProbe();
        var failure =
            assertThrows(
                CleanupStoppedException.class,
                () ->
                    StepCleanupService.withOwner(owner)
                        .execute(
                            probe.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertEquals(CleanupStopReason.TIME_LIMIT, failure.reason(), "owner boundary=" + boundary);
        assertNull(failure.getCause());
        assertFalse(failure.toString().contains("PRIVATE_OWNER"));
        boolean durable = boundary >= 9;
        assertEquals(
            durable ? "RUNNING|1|1|0|0|true" : "RUNNING|0|0|0|0|true", totals(admin, 90011));
        assertEquals(durable ? 1 : 0, probe.commits);
        if (durable) assertEquals(0, probe.rollbacks);
        assertEquals(0, probe.closes);
      }
    }
    reset(db);
    try (var c = locked(db, true);
        var admin = db.admin()) {
      var result =
          StepCleanupService.withOwner(() -> 10_000_000_000L)
              .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS);
      assertEquals(new CleanupCounts(1, 1, 0), result.after());
      assertEquals("RUNNING|1|1|0|0|true", totals(admin, 90011));
    }
  }

  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static final long LIMIT = 1_800_000_000_000L;

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
      for (int other = 0; other < 7; other++)
        for (boolean restore : new boolean[] {false, true}) {
          reset(db);
          try (var c = locked(db, true)) {
            Throwable primary = cleanupFault(main);
            Throwable secondary = other == 5 ? primary : cleanupFault(other);
            var p = new Probe();
            int[] injected = {0, 0};
            p.before =
                (key, count) -> {
                  if (key.equals("statement.executeQuery") && count == 1) {
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
                      () ->
                          new StepCleanupService(() -> 0)
                              .execute(
                                  p.wrap(c),
                                  attempt(CleanupKind.QUESTIONS),
                                  CleanupKind.QUESTIONS)));
              assertEquals(primaryUnknown ? 1 : 0, expected.getSuppressed().length);
              if (primaryUnknown) {
                var fixed =
                    assertInstanceOf(CleanupStoppedException.class, expected.getSuppressed()[0]);
                assertNull(fixed.getCause());
                assertEquals(CleanupStopReason.DATABASE_FAILURE, fixed.reason());
              }
            } else {
              stopped(
                  CleanupStopReason.DATABASE_FAILURE,
                  () ->
                      new StepCleanupService(() -> 0)
                          .execute(
                              p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
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
      case 1 -> new CleanupStoppedException(CleanupStopReason.DATABASE_FAILURE);
      case 2 -> new IllegalStateException("public runtime");
      case 3 -> new NullPointerException("public null");
      case 6 -> new BatchRepositoryException();
      default -> new AssertionError("public fatal");
    };
  }

  @BeforeEach
  void seed() throws Exception {
    reset(db);
  }

  @Test
  void allKindsCompleteAndPersistedCounts() throws Exception {
    long[] delta = {1, 1, 3, 2, 1, 1, 1};
    long[] total = {1, 1, 3, 2, 1, 2, 3};
    try (var c = locked(db, true);
        var admin = db.admin()) {
      for (int i = 0; i < KINDS.size(); i++) {
        var k = KINDS.get(i);
        var p = new Probe();
        var s = new StepCleanupService().execute(p.wrap(c), attempt(k), k);
        assertEquals(new CleanupCounts(delta[i], delta[i], 0), s.callCounts());
        assertEquals(new CleanupCounts(total[i], total[i], 0), s.after());
        assertTrue(s.complete());
        assertFalse(s.deferred());
        assertEquals(
            "RUNNING|" + total[i] + "|" + total[i] + "|0|0|true", totals(admin, attempt(k).id()));
        assertEquals(inventory(2), p.seen);
        p.closed();
        assertTrue(c.getAutoCommit());
        assertFalse(c.isClosed());
      }
    }
  }

  @Test
  void multiChunkResumeAndSharedStep() throws Exception {
    try (var admin = db.admin()) {
      sql(
          admin,
          "insert into schubert.login_ip_attempts select ('10.0.'||(n/256)||'.'||(n%256))::inet,1,'2026-09-01T00:00:00Z',null,'2026-09-01T00:00:00Z' from generate_series(1,998) n");
      // Existing three session-table rows + 998 added IP rows = 1001, independently of production.
      try (var c = locked(db, true)) {
        var p = new Probe();
        var s =
            new StepCleanupService(() -> 0)
                .execute(p.wrap(c), attempt(CleanupKind.SESSIONS), CleanupKind.SESSIONS);
        assertEquals(new CleanupCounts(1001, 1001, 0), s.after());
        assertEquals(new CleanupCounts(1001, 1001, 0), s.callCounts());
        assertEquals(inventory(3), p.seen);
        assertEquals(171, p.seen.values().stream().mapToInt(Integer::intValue).sum());
        p.closed();
        assertEquals("RUNNING|1001|1001|0|0|true", totals(admin, 90012));
        var again =
            new StepCleanupService(() -> 0)
                .execute(c, attempt(CleanupKind.SESSIONS), CleanupKind.SESSIONS);
        assertEquals(new CleanupCounts(1001, 1001, 0), again.before());
        assertEquals(new CleanupCounts(0, 0, 0), again.callCounts());
        trace(
            "PT-BAT-171-chunks.txt",
            "sessions="
                + s.after().target()
                + "\nchunks="
                + p.deletedCounts.stream()
                    .map(Object::toString)
                    .collect(java.util.stream.Collectors.joining("|"))
                + "\nservice_jdbc="
                + p.seen.values().stream().mapToInt(Integer::intValue).sum()
                + "\nresume_delta="
                + again.callCounts().deleted()
                + "\n");
      }
      sql(admin, "update schubert.batch_runs set target_count=7,success_count=7 where id=90014");
      try (var c = locked(db, true)) {
        var service = new StepCleanupService(() -> 0);
        var a = service.execute(c, attempt(CleanupKind.BATCH_RUNS), CleanupKind.BATCH_RUNS);
        assertEquals(new CleanupCounts(7, 7, 0), a.before());
        assertEquals(new CleanupCounts(8, 8, 0), a.after());
        var b = service.execute(c, attempt(CleanupKind.INBOX_PROGRESS), CleanupKind.INBOX_PROGRESS);
        assertEquals(new CleanupCounts(8, 8, 0), b.before());
        assertEquals(new CleanupCounts(9, 9, 0), b.after());
        var d = service.execute(c, attempt(CleanupKind.LOG_PROGRESS), CleanupKind.LOG_PROGRESS);
        assertEquals(new CleanupCounts(9, 9, 0), d.before());
        assertEquals(new CleanupCounts(10, 10, 0), d.after());
        assertEquals(new CleanupCounts(1, 1, 0), d.callCounts());
      }
    }
  }

  @Test
  void lockBackupAndForeignKeyDeferral() throws Exception {
    try (var admin = db.admin()) {
      sql(admin, "update schubert.batch_runs set status='FAILED' where id=90000");
      try (var c = locked(db, true)) {
        var p = new Probe();
        stopped(
            CleanupStopReason.BACKUP_GATE,
            () ->
                new StepCleanupService(() -> 0)
                    .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        var expected = new TreeMap<>(inventory(1));
        expected.remove(FIXTURE_CONNECTION_COMMIT_37C1B216);
        expected.put(FIXTURE_CONNECTION_ROLLBACK_9F978A8C, 1);
        assertEquals(expected, p.seen);
        p.closed();
        assertTrue(c.getAutoCommit());
      }
      sql(admin, "update schubert.batch_runs set status='SUCCESS' where id=90000");
      admin.setAutoCommit(false);
      sql(admin, "select id from schubert.questions where id=2 for update");
      try (var c = locked(db, true)) {
        stopped(
            CleanupStopReason.LOCK_BUSY,
            () ->
                new StepCleanupService(() -> 0)
                    .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertEquals("RUNNING|0|0|0|0|true", totals(admin, 90011));
      }
      admin.rollback();
      admin.setAutoCommit(true);
      sql(
          admin,
          "create table public.pg164_service_fk(id bigint references schubert.questions(id));insert into public.pg164_service_fk values(2)");
      try (var c = locked(db, true)) {
        var p = new Probe();
        var s =
            new StepCleanupService(() -> 0)
                .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS);
        assertTrue(s.deferred());
        assertFalse(s.complete());
        assertEquals(new CleanupCounts(0, 0, 0), s.callCounts());
        assertEquals(inventory(1), p.seen);
        p.closed();
        assertEquals("1", query(admin, "select count(*) from schubert.questions where id=2"));
      } finally {
        sql(admin, "drop table public.pg164_service_fk");
      }
      try (var c = locked(db, true)) {
        var p = new Probe();
        p.after =
            (k, n) -> {
              if (k.equals(FIXTURE_CONNECTION_COMMIT_37C1B216) && n == 1)
                sql(admin, "update schubert.batch_runs set status='FAILED' where id=90000");
            };
        stopped(
            CleanupStopReason.BACKUP_GATE,
            () ->
                new StepCleanupService(() -> 0)
                    .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertEquals("RUNNING|1|1|0|0|true", totals(admin, 90011));
        p.closed();
      }
    }
  }

  @Test
  void transactionFaultsAndUnknownCommit() throws Exception {
    var expected = inventory(2);
    assertEquals(115, expected.values().stream().mapToInt(Integer::intValue).sum());
    int observed;
    try (var c = locked(db, true)) {
      var normal = new Probe();
      new StepCleanupService(() -> 0)
          .execute(normal.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS);
      assertEquals(expected, normal.seen);
      observed = normal.seen.values().stream().mapToInt(Integer::intValue).sum();
      normal.closed();
    }
    int cases = 0;
    for (var e : expected.entrySet())
      for (int i = 1; i <= e.getValue(); i++) {
        reset(db);
        try (var c = locked(db, true);
            var admin = db.admin()) {
          var p = new Probe();
          p.fail(e.getKey(), i);
          stopped(
              CleanupStopReason.DATABASE_FAILURE,
              () ->
                  new StepCleanupService(() -> 0)
                      .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
          assertEquals(1, p.failures, e.getKey() + ":" + i);
          p.closed();
          long committed = committedBeforeFault(e.getKey(), i);
          assertEquals(
              "RUNNING|" + committed + "|" + committed + "|0|0|true",
              totals(admin, 90011),
              e.getKey() + ":" + i);
          assertEquals(
              Long.toString(1 - committed),
              query(admin, "select count(*) from schubert.questions where id=2"));
          cases++;
        }
      }
    assertEquals(115, cases);
    reset(db);
    try (var c = locked(db, true);
        var admin = db.admin()) {
      var p = new Probe();
      p.after =
          (k, n) -> {
            if (k.equals(FIXTURE_CONNECTION_COMMIT_37C1B216) && n == 1)
              throw new SQLException("public unknown commit outcome", "08006");
          };
      stopped(
          CleanupStopReason.DATABASE_FAILURE,
          () ->
              new StepCleanupService(() -> 0)
                  .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
      assertEquals("RUNNING|1|1|0|0|true", totals(admin, 90011));
      p.closed();
      var resumed =
          new StepCleanupService(() -> 0)
              .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS);
      assertEquals(new CleanupCounts(1, 1, 0), resumed.before());
      assertEquals(new CleanupCounts(0, 0, 0), resumed.callCounts());
      assertTrue(resumed.complete());
      trace(
          "PT-BAT-173-jdbc.txt",
          "positive_end="
              + observed
              + "\nfault_positions="
              + cases
              + "\ncommit_response_unknown=stored"
              + resumed.before().target()
              + "|resume_delta"
              + resumed.callCounts().deleted()
              + "\n");
    }
  }

  @Test
  void timeoutInterruptAndClockWrap() throws Exception {
    // BUG186/YKT146: start, preflight, two before/after chunk clock pairs (six calls).
    for (int point = 1; point <= 6; point++) {
      reset(db);
      int selected = point;
      AtomicInteger calls = new AtomicInteger();
      try (var c = locked(db, true);
          var admin = db.admin()) {
        LongSupplier time =
            () -> {
              if (calls.incrementAndGet() == selected) Thread.currentThread().interrupt();
              return 0;
            };
        try {
          stopped(
              CleanupStopReason.INTERRUPTED,
              () ->
                  new StepCleanupService(time)
                      .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
          assertTrue(Thread.currentThread().isInterrupted());
          assertEquals(selected, calls.get());
        } finally {
          Thread.interrupted();
        }
        long n = point <= 3 ? 0 : 1;
        assertEquals("RUNNING|" + n + "|" + n + "|0|0|true", totals(admin, 90011));
        assertTrue(c.getAutoCommit());
        assertFalse(c.isClosed());
      }
    }
    for (long elapsed : new long[] {LIMIT, LIMIT + 1, -1}) {
      AtomicInteger calls = new AtomicInteger();
      LongSupplier time = () -> calls.getAndIncrement() == 0 ? 0 : elapsed;
      try (var c = locked(db, true)) {
        var p = new Probe();
        stopped(
            CleanupStopReason.TIME_LIMIT,
            () ->
                new StepCleanupService(time)
                    .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertTrue(p.seen.isEmpty());
      }
    }
    for (int at : new int[] {2, 3, 4, 5, 6}) {
      reset(db);
      AtomicInteger calls = new AtomicInteger();
      int point = at;
      try (var c = locked(db, true);
          var admin = db.admin()) {
        LongSupplier time = () -> calls.incrementAndGet() < point ? 0 : LIMIT;
        stopped(
            CleanupStopReason.TIME_LIMIT,
            () ->
                new StepCleanupService(time)
                    .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        long n = at <= 3 ? 0 : 1;
        assertEquals("RUNNING|" + n + "|" + n + "|0|0|true", totals(admin, 90011));
        assertTrue(c.getAutoCommit());
      }
    }
    reset(db);
    try (var c = locked(db, true)) {
      AtomicInteger calls = new AtomicInteger();
      var s =
          new StepCleanupService(
                  () -> calls.getAndIncrement() == 0 ? Long.MAX_VALUE - 5 : Long.MIN_VALUE + 4)
              .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS);
      assertTrue(s.complete());
      assertEquals(new CleanupCounts(1, 1, 0), s.callCounts());
      AtomicInteger near = new AtomicInteger();
      assertTrue(
          new StepCleanupService(() -> near.getAndIncrement() == 0 ? 0 : LIMIT - 1)
              .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS)
              .complete());
      Thread.currentThread().interrupt();
      try {
        stopped(
            CleanupStopReason.INTERRUPTED,
            () ->
                new StepCleanupService(() -> 0)
                    .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    for (int at : new int[] {1, 2}) {
      reset(db);
      try (var c = locked(db, true);
          var admin = db.admin()) {
        int point = at;
        var p = new Probe();
        p.after =
            (k, n) -> {
              if (k.equals(FIXTURE_CONNECTION_COMMIT_37C1B216) && n == point)
                Thread.currentThread().interrupt();
            };
        try {
          stopped(
              CleanupStopReason.INTERRUPTED,
              () ->
                  new StepCleanupService(() -> 0)
                      .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
          assertTrue(Thread.currentThread().isInterrupted());
          p.closed();
        } finally {
          Thread.interrupted();
        }
        assertEquals("RUNNING|1|1|0|0|true", totals(admin, 90011));
        assertTrue(c.getAutoCommit());
      }
    }
  }

  @Test
  void counterContinuityAndOverflow() throws Exception {
    for (long changed : new long[] {0, 2, Long.MAX_VALUE}) {
      reset(db);
      try (var c = locked(db, true);
          var admin = db.admin()) {
        var p = new Probe();
        p.after =
            (k, n) -> {
              if (k.equals(FIXTURE_CONNECTION_COMMIT_37C1B216) && n == 1)
                sql(
                    admin,
                    "update schubert.batch_runs set target_count="
                        + changed
                        + ",success_count="
                        + changed
                        + " where id=90011");
            };
        stopped(
            CleanupStopReason.DATABASE_FAILURE,
            () ->
                new StepCleanupService(() -> 0)
                    .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertEquals("RUNNING|" + changed + "|" + changed + "|0|0|true", totals(admin, 90011));
        assertEquals(1, p.seen.get(FIXTURE_CONNECTION_ROLLBACK_9F978A8C));
        p.closed();
      }
    }
    reset(db);
    try (var admin = db.admin()) {
      sql(
          admin,
          "update schubert.batch_runs set target_count=9223372036854775807,success_count=9223372036854775807 where id=90011");
      try (var c = locked(db, true)) {
        stopped(
            CleanupStopReason.DATABASE_FAILURE,
            () ->
                new StepCleanupService(() -> 0)
                    .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
        assertEquals("1", query(admin, "select count(*) from schubert.questions where id=2"));
        assertEquals(
            "RUNNING|9223372036854775807|9223372036854775807|0|0|true", totals(admin, 90011));
        sql(admin, "delete from schubert.questions where id=2");
        var s =
            new StepCleanupService(() -> 0)
                .execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS);
        assertEquals(new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0), s.after());
        assertEquals(new CleanupCounts(0, 0, 0), s.callCounts());
        assertTrue(s.complete());
      }
    }
  }

  @Test
  void connectionStateRestorationAndNulls() throws Exception {
    unknownCleanupMatrix();
    // BUG193/YKT152: this borrowed-transaction owner has the same masking boundary.
    try (var c = locked(db, true)) {
      var primary = new IllegalStateException("public primary");
      var p = new Probe();
      p.unknown.put("statement.executeQuery", primary);
      p.unknown.put(
          FIXTURE_CONNECTION_ROLLBACK_9F978A8C, new NullPointerException("public secondary"));
      assertSame(
          primary,
          assertThrows(
              IllegalStateException.class,
              () ->
                  new StepCleanupService(() -> 0)
                      .execute(p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS)));
      p.closed();
      assertEquals(1, primary.getSuppressed().length);
      c.rollback();
    }
    assertThrows(NullPointerException.class, () -> new StepCleanupService(null));
    var service = new StepCleanupService(() -> 0);
    assertThrows(
        NullPointerException.class,
        () -> service.execute(null, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
    try (var c = locked(db, true)) {
      assertThrows(
          NullPointerException.class, () -> service.execute(c, null, CleanupKind.QUESTIONS));
      assertThrows(
          NullPointerException.class,
          () -> service.execute(c, attempt(CleanupKind.QUESTIONS), null));
      assertThrows(
          IllegalArgumentException.class,
          () -> service.execute(c, attempt(CleanupKind.LOGS), CleanupKind.LOGS));
      assertThrows(
          IllegalArgumentException.class,
          () -> service.execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.NOTIFICATIONS));
      var skipped = new BatchStepAttempt(90011, RUN, BatchStep.CLEAN_QUESTION, 1, START, true);
      assertThrows(
          IllegalArgumentException.class, () -> service.execute(c, skipped, CleanupKind.QUESTIONS));
      c.setAutoCommit(false);
      assertThrows(
          IllegalArgumentException.class,
          () -> service.execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
      c.rollback();
      c.setAutoCommit(true);
      c.setReadOnly(true);
      assertThrows(
          IllegalArgumentException.class,
          () -> service.execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
      c.setReadOnly(false);
      c.setTransactionIsolation(Connection.TRANSACTION_SERIALIZABLE);
      assertThrows(
          IllegalArgumentException.class,
          () -> service.execute(c, attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
    }
    for (String cleanup : List.of(FIXTURE_NONE_30A0924A, "rollback", "restore"))
      for (String primary : List.of("SQL", "REPOSITORY", "STOP", "RUNTIME", "NPE", "ERROR")) {
        reset(db);
        try (var c = locked(db, true)) {
          var p = new Probe();
          Throwable failure =
              switch (primary) {
                case "SQL" -> new SQLException("public provider");
                case "REPOSITORY" -> new BatchRepositoryException();
                case "STOP" -> new CleanupStoppedException(CleanupStopReason.LOCK_BUSY);
                case "RUNTIME" -> new UnsupportedOperationException("public unsupported");
                case "NPE" -> new NullPointerException("public NPE");
                default -> new AssertionError("public error");
              };
          // Inject after false configuration succeeds, before query ownership; failure remains
          // actual JDBC-boundary failure.
          p.before =
              (k, n) -> {
                if (k.equals("connection.prepareStatement") && n == 1) throw failure;
              };
          if (cleanup.equals("rollback")) p.fail(FIXTURE_CONNECTION_ROLLBACK_9F978A8C, 1);
          if (cleanup.equals("restore")) p.fail(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D, 2);
          if (Set.of("RUNTIME", "NPE", "ERROR").contains(primary)) {
            var thrown =
                assertThrows(
                    failure.getClass(),
                    () ->
                        service.execute(
                            p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
            assertSame(failure, thrown);
            assertEquals(
                cleanup.equals(FIXTURE_NONE_30A0924A) ? 0 : 1, thrown.getSuppressed().length);
            if (!cleanup.equals(FIXTURE_NONE_30A0924A)) {
              var extra =
                  assertInstanceOf(CleanupStoppedException.class, thrown.getSuppressed()[0]);
              assertEquals(CleanupStopReason.DATABASE_FAILURE, extra.reason());
              assertNull(extra.getCause());
              assertEquals(0, extra.getSuppressed().length);
            }
          } else {
            var reason =
                primary.equals("STOP") && cleanup.equals(FIXTURE_NONE_30A0924A)
                    ? CleanupStopReason.LOCK_BUSY
                    : CleanupStopReason.DATABASE_FAILURE;
            stopped(
                reason,
                () ->
                    service.execute(
                        p.wrap(c), attempt(CleanupKind.QUESTIONS), CleanupKind.QUESTIONS));
          }
          p.closed();
          assertFalse(c.isClosed());
          assertEquals(
              cleanup.equals("rollback") ? 1 : 2,
              p.seen.get(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D));
          assertEquals(cleanup.equals(FIXTURE_NONE_30A0924A), c.getAutoCommit());
          if (!c.getAutoCommit()) c.rollback();
        }
      }
  }

  @Test
  void concurrencyAndIndependentTrace() throws Exception {
    StringBuilder result = new StringBuilder();
    long[] totals = {1, 1, 3, 2, 1, 2, 3};
    try (var c = locked(db, true);
        var admin = db.admin();
        var pool = Executors.newVirtualThreadPerTaskExecutor()) {
      var competing =
          pool.submit(
              () -> {
                try (var other = db.open("schubert_batch")) {
                  var e =
                      assertThrows(
                          CleanupStoppedException.class,
                          () ->
                              new StepCleanupService(() -> 0)
                                  .execute(
                                      other,
                                      attempt(CleanupKind.QUESTIONS),
                                      CleanupKind.QUESTIONS));
                  return e.reason();
                }
              });
      assertEquals(CleanupStopReason.DATABASE_FAILURE, competing.get(5, TimeUnit.SECONDS));
      assertEquals("1", query(admin, "select count(*) from schubert.questions where id=2"));
      for (int i = 0; i < KINDS.size(); i++) {
        var k = KINDS.get(i);
        var s = new StepCleanupService(() -> 0).execute(c, attempt(k), k);
        String actual = totals(admin, attempt(k).id());
        assertEquals("RUNNING|" + totals[i] + "|" + totals[i] + "|0|0|true", actual);
        assertTrue(s.complete());
        result.append(k.name()).append('=').append(actual).append('\n');
      }
    }
    trace("PT-BAT-177-service.txt", result.toString());
  }

  /** Three initial checks + 56 calls per committed chunk, independently specified in PT030. */
  static Map<String, Integer> inventory(int chunks) {
    var m = new TreeMap<String, Integer>();
    repositoryInventory().forEach((k, v) -> m.put(k, v * chunks));
    for (String k :
        List.of(
            "connection.getAutoCommit",
            "connection.isReadOnly",
            "connection.getTransactionIsolation")) m.merge(k, 1, Integer::sum);
    m.put(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D, chunks * 2);
    m.put(FIXTURE_CONNECTION_COMMIT_37C1B216, chunks);
    return m;
  }

  /**
   * First deletion is durable only once first commit completed; fault positions are from the fixed
   * PT inventory.
   */
  static long committedBeforeFault(String key, int position) {
    if (key.equals(FIXTURE_CONNECTION_SETAUTOCOMMIT_D9B0AF8D)) return position >= 2 ? 1 : 0;
    if (key.equals(FIXTURE_CONNECTION_COMMIT_37C1B216)) return position >= 2 ? 1 : 0;
    int threshold = repositoryInventory().get(key);
    if (Set.of(
            "connection.getAutoCommit",
            "connection.isReadOnly",
            "connection.getTransactionIsolation")
        .contains(key)) threshold++;
    return position > threshold ? 1 : 0;
  }

  static void stopped(CleanupStopReason reason, org.junit.jupiter.api.function.Executable action) {
    var e = assertThrows(CleanupStoppedException.class, action);
    assertEquals(reason, e.reason());
    assertEquals("cleanup did not complete", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }
}
