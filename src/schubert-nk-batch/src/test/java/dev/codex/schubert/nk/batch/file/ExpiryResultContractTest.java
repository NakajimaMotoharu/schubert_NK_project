package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeClient;
import dev.codex.schubert.nk.batch.mq.ArtemisExpiryPurgeException;
import dev.codex.schubert.nk.batch.mq.ArtemisManagementReadinessException;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** EXP711: literal MQ outcomes + genuine isolated SQL; never a native admission claim. */
final class ExpiryResultContractTest {
  private static final String FIXTURE_HEALTH_69B7C75B = "health";
  private static final String FIXTURE_OBSERVE_584F9502 = "observe";
  private static final String FIXTURE_PURGE_B6F2C785 = "purge";
  @TempDir static Path root;
  static BatchDatabaseFixture db;
  static final UUID RUN = UUID.fromString("71100000-2222-4333-8444-555555555555");
  static final Instant CUTOFF = Instant.parse("2026-09-30T00:00:00Z");
  static final Instant ENDED = Instant.parse("2026-09-30T00:00:02Z");
  static final MaintenanceOwnerFrame.Guard OWNER = () -> 10_000_000_000L;

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
    try (var admin = db.admin();
        var sql = admin.createStatement()) {
      sql.execute("delete from schubert.batch_runs");
      sql.execute(
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,status,target_count,success_count,failure_count,byte_count) values (42,'71100000-2222-4333-8444-555555555555','2026-09-30','CLEAN_EXPIRY',1,'2026-09-30T00:00:01Z','RUNNING',0,0,0,0)");
    }
  }

  static CleanupWorkerRequest.Expiry request() {
    return new CleanupWorkerRequest.Expiry(
        RUN,
        UUID.fromString("71100000-6666-4777-8888-999999999999"),
        CUTOFF,
        UUID.fromString("71100000-3333-4333-8444-555555555555"),
        UUID.fromString("71100000-4444-4333-8444-555555555555"),
        "1".repeat(32),
        42,
        1,
        Instant.parse("2026-09-30T00:00:01Z"),
        false,
        Optional.empty());
  }

  static Connection locked() throws Exception {
    var c = db.open("schubert_batch");
    try (var s = c.createStatement();
        var r = s.executeQuery("select pg_try_advisory_lock(71419602)")) {
      assertTrue(r.next());
      assertTrue(r.getBoolean(1));
      assertFalse(r.next());
    }
    return c;
  }

  static String audit() throws Exception {
    try (var c = db.admin();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select status||'|'||coalesce(expiry_before_count::text,'NULL')||'|'||coalesce(expiry_after_count::text,'NULL')||'|'||target_count||'|'||success_count||'|'||failure_count||'|'||byte_count||'|'||coalesce(error_code,'NULL') from schubert.batch_runs where id=42")) {
      assertTrue(r.next());
      var value = r.getString(1);
      assertNotNull(value);
      assertFalse(r.next());
      return value;
    }
  }

  static final class Work implements CleanupExpiryExecution.ExpiryWork {
    final List<String> calls = new ArrayList<>();
    boolean purgeFails;
    boolean unhealthy;
    boolean healthFails;
    boolean noSelected;
    RuntimeException unknown;
    int healthCalls;

    @Override
    public boolean healthy() {
      calls.add(FIXTURE_HEALTH_69B7C75B);
      if (healthCalls++ > 0 && healthFails) throw new ArtemisManagementReadinessException();
      return !unhealthy;
    }

    @Override
    public ArtemisExpiryPurgeClient.Observation observe(BatchRun run) {
      calls.add(FIXTURE_OBSERVE_584F9502);
      assertEquals(RUN, run.id());
      assertEquals(CUTOFF, run.cutoff());
      return new ArtemisExpiryPurgeClient.Observation(
          1790121600000L, 3, noSelected ? 0 : 2, 300, noSelected ? 0 : 200);
    }

    @Override
    public ArtemisExpiryPurgeClient.Result purge(
        BatchRun run, ArtemisExpiryPurgeClient.Observation observed) {
      calls.add(FIXTURE_PURGE_B6F2C785);
      assertEquals(RUN, run.id());
      assertEquals(
          new ArtemisExpiryPurgeClient.Observation(1790121600000L, 3, 2, 300, 200), observed);
      try {
        assertEquals("RUNNING|3|NULL|2|0|0|200|NULL", audit());
      } catch (Exception failure) {
        throw new AssertionError(failure);
      }
      if (unknown != null) throw unknown;
      if (purgeFails) throw new ArtemisExpiryPurgeException();
      return new ArtemisExpiryPurgeClient.Result(1790121600000L, 3, 2, 2, 1, 300, 200, 200, 100);
    }

    @Override
    public Instant now() {
      calls.add("now");
      return ENDED;
    }
  }

  @Test
  void exp711001SuccessPersistsLiteralStageBeforePurgeAndFinalAfterHealth() throws Exception {
    var work = new Work();
    try (var c = locked()) {
      assertEquals(0, CleanupExpiryExecution.executeAuthenticated(c, request(), OWNER, work));
      assertFalse(c.isClosed());
      assertTrue(c.getAutoCommit());
    }
    assertEquals(
        List.of(
            FIXTURE_HEALTH_69B7C75B,
            FIXTURE_OBSERVE_584F9502,
            FIXTURE_PURGE_B6F2C785,
            FIXTURE_HEALTH_69B7C75B,
            "now"),
        work.calls);
    assertEquals("SUCCESS|3|1|2|2|0|200|NULL", audit());
  }

  @Test
  void exp711002DeclaredPurgeFailureWarnsWithoutInventedAfterCount() throws Exception {
    var work = new Work();
    work.purgeFails = true;
    try (var c = locked()) {
      assertEquals(10, CleanupExpiryExecution.executeAuthenticated(c, request(), OWNER, work));
      assertTrue(c.getAutoCommit());
    }
    assertEquals("WARNING|3|NULL|2|0|2|200|COMMAND_FAILURE", audit());
    assertEquals(
        List.of(
            FIXTURE_HEALTH_69B7C75B,
            FIXTURE_OBSERVE_584F9502,
            FIXTURE_PURGE_B6F2C785,
            FIXTURE_HEALTH_69B7C75B,
            "now"),
        work.calls);
  }

  @Test
  void exp711003CriticalPressureFailsEvenAfterSuccessfulPurge() throws Exception {
    var work = new Work();
    work.unhealthy = true;
    try (var c = locked()) {
      assertEquals(30, CleanupExpiryExecution.executeAuthenticated(c, request(), OWNER, work));
    }
    assertEquals("FAILED|3|1|2|2|0|200|SAFETY_FAILURE", audit());
  }

  @Test
  void exp711004DeclaredHealthFailureFailsWithoutLeakingProviderDetail() throws Exception {
    var work = new Work();
    work.healthFails = true;
    work.purgeFails = true;
    try (var c = locked()) {
      assertEquals(30, CleanupExpiryExecution.executeAuthenticated(c, request(), OWNER, work));
    }
    assertEquals("FAILED|3|NULL|2|0|2|200|SAFETY_FAILURE", audit());
  }

  @Test
  void exp711005MissingInputsRejectBeforeAnyOwnedWorkOrSql() throws Exception {
    var work = new Work();
    var before = audit();
    try (var c = locked()) {
      assertThrows(
          IllegalArgumentException.class,
          () -> CleanupExpiryExecution.executeAuthenticated(null, request(), OWNER, work));
      assertThrows(
          IllegalArgumentException.class,
          () -> CleanupExpiryExecution.executeAuthenticated(c, null, OWNER, work));
      assertThrows(
          IllegalArgumentException.class,
          () -> CleanupExpiryExecution.executeAuthenticated(c, request(), null, work));
      assertThrows(
          IllegalArgumentException.class,
          () -> CleanupExpiryExecution.executeAuthenticated(c, request(), OWNER, null));
      assertTrue(c.getAutoCommit());
    }
    assertEquals(before, audit());
    assertTrue(work.calls.isEmpty());
  }

  @Test
  void exp711006ExpiredOwnerRejectsBeforeBrokerAndDbMutation() throws Exception {
    var work = new Work();
    var before = audit();
    var expected = new IOException("owned deadline");
    try (var c = locked()) {
      assertSame(
          expected,
          assertThrows(
              IOException.class,
              () ->
                  CleanupExpiryExecution.executeAuthenticated(
                      c,
                      request(),
                      () -> {
                        throw expected;
                      },
                      work)));
      assertTrue(c.getAutoCommit());
    }
    assertTrue(work.calls.isEmpty());
    assertEquals(before, audit());
  }

  @Test
  void exp711007UnknownPurgeCannotPublishFabricatedTerminal() throws Exception {
    var work = new Work();
    work.unknown = new IllegalStateException("untrusted provider");
    try (var c = locked()) {
      assertSame(
          work.unknown,
          assertThrows(
              IllegalStateException.class,
              () -> CleanupExpiryExecution.executeAuthenticated(c, request(), OWNER, work)));
      assertFalse(c.isClosed());
      assertTrue(c.getAutoCommit());
    }
    assertEquals("RUNNING|3|NULL|2|0|0|200|NULL", audit());
    assertEquals(
        List.of(FIXTURE_HEALTH_69B7C75B, FIXTURE_OBSERVE_584F9502, FIXTURE_PURGE_B6F2C785),
        work.calls);
  }

  @Test
  void exp711008SkipPreservesOriginalAndCurrentRowsAndNeverPurges() throws Exception {
    try (var admin = db.admin();
        var sql = admin.createStatement()) {
      sql.execute(
          "update schubert.batch_runs set status='SUCCESS',ended_at='2026-09-30T00:00:02Z',target_count=2,success_count=2,byte_count=200,expiry_cutoff_at='2026-09-23T00:00:00Z',expiry_before_count=3,expiry_after_count=1 where id=42");
      sql.execute(
          "insert into schubert.batch_runs(id,run_id,business_date,step,attempt,started_at,ended_at,status,target_count,success_count,failure_count,byte_count,error_code,error_summary) values(43,'71100000-2222-4333-8444-555555555555','2026-09-30','CLEAN_EXPIRY',2,'2026-09-30T00:00:03Z','2026-09-30T00:00:03Z','SKIPPED',0,0,0,0,'ALREADY_SUCCESSFUL','step already successful for business date')");
    }
    var original = request();
    var skipped =
        new CleanupWorkerRequest.Expiry(
            original.run(),
            original.activation(),
            original.cutoff(),
            original.boot(),
            original.epoch(),
            original.brokerInvocation(),
            43,
            2,
            Instant.parse("2026-09-30T00:00:03Z"),
            true,
            Optional.of(
                new CleanupWorkerRequest.Expiry.PriorExpiry(
                    RUN, CUTOFF, 42, 1, Instant.parse("2026-09-30T00:00:01Z"), ENDED)));
    String before = allRows();
    for (boolean critical : List.of(false, true)) {
      var work = new Work();
      work.noSelected = true;
      work.unhealthy = critical;
      try (var c = locked()) {
        if (critical)
          assertThrows(
              IOException.class,
              () -> CleanupExpiryExecution.executeAuthenticated(c, skipped, OWNER, work));
        else assertEquals(0, CleanupExpiryExecution.executeAuthenticated(c, skipped, OWNER, work));
        assertTrue(c.getAutoCommit());
      }
      assertEquals(
          List.of(FIXTURE_HEALTH_69B7C75B, FIXTURE_OBSERVE_584F9502, FIXTURE_HEALTH_69B7C75B),
          work.calls);
      assertEquals(before, allRows());
    }
  }

  static String allRows() throws Exception {
    try (var c = db.admin();
        var sql = c.createStatement();
        var rows =
            sql.executeQuery(
                "select jsonb_agg(to_jsonb(t) order by id)::text from schubert.batch_runs t")) {
      assertTrue(rows.next());
      var result = rows.getString(1);
      assertNotNull(result);
      assertFalse(rows.next());
      return result;
    }
  }

  @Test
  void exp711009OwnerLossAfterActualPurgeCannotInventTerminal() throws Exception {
    var work = new Work();
    var expected = new IOException("owner lost after purge");
    try (var c = locked()) {
      assertSame(
          expected,
          assertThrows(
              IOException.class,
              () ->
                  CleanupExpiryExecution.executeAuthenticated(
                      c,
                      request(),
                      () -> {
                        if (work.calls.contains(FIXTURE_PURGE_B6F2C785)) throw expected;
                        return 10_000_000_000L;
                      },
                      work)));
      assertFalse(c.isClosed());
    }
    assertEquals("RUNNING|3|NULL|2|0|0|200|NULL", audit());
    assertEquals(
        List.of(FIXTURE_HEALTH_69B7C75B, FIXTURE_OBSERVE_584F9502, FIXTURE_PURGE_B6F2C785),
        work.calls);
  }

  @Test
  void exp711010IndependentStageDriftMustPreventDestructivePurge() throws Exception {
    var work = new Work();
    var once = new java.util.concurrent.atomic.AtomicBoolean();
    try (var c = locked()) {
      assertThrows(
          IOException.class,
          () ->
              CleanupExpiryExecution.executeAuthenticated(
                  c,
                  request(),
                  () -> {
                    try {
                      if (audit().equals("RUNNING|3|NULL|2|0|0|200|NULL")
                          && once.compareAndSet(false, true)) {
                        try (var admin = db.admin();
                            var sql = admin.createStatement()) {
                          assertEquals(
                              1,
                              sql.executeUpdate(
                                  "update schubert.batch_runs set expiry_before_count=4 where id=42"));
                        }
                      }
                    } catch (Exception failure) {
                      throw new AssertionError(failure);
                    }
                    return 10_000_000_000L;
                  },
                  work));
    }
    assertTrue(once.get());
    assertEquals(List.of(FIXTURE_HEALTH_69B7C75B, FIXTURE_OBSERVE_584F9502), work.calls);
    assertEquals("RUNNING|4|NULL|2|0|0|200|NULL", audit());
  }

  @Test
  void exp711011IndependentTerminalDriftCannotReturnSuccess() throws Exception {
    var work = new Work();
    var once = new java.util.concurrent.atomic.AtomicBoolean();
    try (var c = locked()) {
      assertThrows(
          IOException.class,
          () ->
              CleanupExpiryExecution.executeAuthenticated(
                  c,
                  request(),
                  () -> {
                    try {
                      if (audit().equals("SUCCESS|3|1|2|2|0|200|NULL")
                          && once.compareAndSet(false, true)) {
                        try (var admin = db.admin();
                            var sql = admin.createStatement()) {
                          assertEquals(
                              1,
                              sql.executeUpdate(
                                  "update schubert.batch_runs set byte_count=201 where id=42"));
                        }
                      }
                    } catch (Exception failure) {
                      throw new AssertionError(failure);
                    }
                    return 10_000_000_000L;
                  },
                  work));
    }
    assertTrue(once.get());
    assertEquals("SUCCESS|3|1|2|2|0|201|NULL", audit());
  }
}
