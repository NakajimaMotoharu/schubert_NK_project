package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/BAK001/UI251/SS331/341/343/SSC092/094/104; PT-OPS-MBPREP001-006. */
final class MorningBackupPreparationTest {
  private static final UUID RUN_ID = UUID.fromString("11111111-1111-4111-8111-111111111111");
  private static final UUID ACTIVATION = UUID.fromString("22222222-2222-4222-8222-222222222222");
  private static final UUID PART = UUID.fromString("33333333-3333-4333-8333-333333333333");
  private static final Instant CUTOFF = Instant.parse("2026-09-28T01:00:00Z");
  private static final Instant START = Instant.parse("2026-09-28T01:00:01.123456Z");
  private static final BatchRun RUN = new BatchRun(RUN_ID, CUTOFF);
  private static final MaintenanceActivation ACTIVE = new MaintenanceActivation(RUN, ACTIVATION);
  private static final MaintenanceRunState STATE =
      new MaintenanceRunState(ACTIVE, Optional.empty());

  private static Clock clock(Instant now) {
    return Clock.fixed(now, ZoneOffset.UTC);
  }

  private static BatchStepAttempt attempt(
      long id, BatchRun run, BatchStep step, Instant started, boolean skipped) {
    return new BatchStepAttempt(id, run, step, 1, started, skipped);
  }

  private static MorningDatabaseSession.BackupBegins valid() {
    return new MorningDatabaseSession.BackupBegins(
        attempt(41, RUN, BatchStep.BACKUP_DB, START, false),
        attempt(42, RUN, BatchStep.BACKUP_CONFIG, START, false));
  }

  private static final class Database implements MorningDatabaseSession.Access {
    final List<String> events;
    MorningDatabaseSession.BackupBegins begins = valid();
    IOException failure;
    BatchRun suppliedRun;
    Instant suppliedTime;
    boolean suppliedRecover;

    Database(List<String> events) {
      this.events = events;
    }

    @Override
    public void requireUnused(BatchRun run) {
      fail("no independent reference query here");
    }

    @Override
    public void requireConsistent(BatchRun run) {
      fail("no independent reference query here");
    }

    @Override
    public MorningDatabaseSession.BackupBegins beginBackup(
        BatchRun run, Instant now, boolean recoverAbandoned) throws IOException {
      events.add("DB-both-committed");
      suppliedRun = run;
      suppliedTime = now;
      suppliedRecover = recoverAbandoned;
      if (failure != null) throw failure;
      return begins;
    }

    @Override
    public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> operation) {
      return fail("no cleanup handoff here");
    }
  }

  @Test
  void mbprep001CommitBothBeforeRequestAndContinuation() throws Exception {
    var events = new ArrayList<String>();
    var db = new Database(events);
    var result =
        MorningBackupPreparation.execute(
            STATE,
            db,
            clock(START),
            false,
            (request, part) -> {
              assertEquals(RUN_ID, request.run());
              assertEquals(START, request.started());
              assertEquals(PART, part);
              events.add("publish-new-only");
            },
            PART,
            (request, begins) -> {
              assertEquals(RUN_ID, request.run());
              assertEquals(41L, begins.database().id());
              assertEquals(42L, begins.configuration().id());
              events.add("worker-continuation");
              return "prepared";
            });
    assertEquals("prepared", result);
    assertEquals(List.of("DB-both-committed", "publish-new-only", "worker-continuation"), events);
    assertSame(RUN, db.suppliedRun);
    assertEquals(START, db.suppliedTime);
    assertFalse(db.suppliedRecover);
  }

  @Test
  void mbprep002ResumeKeepsOriginalRunAndSetsRecovery() throws Exception {
    var events = new ArrayList<String>();
    var db = new Database(events);
    Instant oneSecond = CUTOFF.plusSeconds(1);
    db.begins =
        new MorningDatabaseSession.BackupBegins(
            attempt(71, RUN, BatchStep.BACKUP_DB, oneSecond, false),
            attempt(72, RUN, BatchStep.BACKUP_CONFIG, oneSecond, false));
    BackupWorkerRequest request =
        MorningBackupPreparation.execute(
            STATE,
            db,
            clock(oneSecond),
            true,
            (published, part) -> events.add("publish"),
            PART,
            (published, begins) -> published);
    assertEquals(RUN_ID, request.run());
    assertEquals(oneSecond, request.started());
    assertSame(RUN, db.suppliedRun);
    assertTrue(db.suppliedRecover);
    assertEquals(List.of("DB-both-committed", "publish"), events);
  }

  @Test
  void mbprep003DbFailureAndBadHandlesNeverPublish() {
    var events = new ArrayList<String>();
    var db = new Database(events);
    db.failure = new IOException("commit unknown");
    assertSame(
        db.failure,
        assertThrows(
            IOException.class,
            () ->
                MorningBackupPreparation.execute(
                    STATE,
                    db,
                    clock(START),
                    false,
                    (request, part) -> fail("no publish"),
                    PART,
                    (request, begins) -> fail("no work"))));
    db.failure = null;
    var other = new BatchRun(UUID.fromString("44444444-4444-4444-8444-444444444444"), CUTOFF);
    var bad =
        List.of(
            new MorningDatabaseSession.BackupBegins(
                attempt(41, other, BatchStep.BACKUP_DB, START, false), valid().configuration()),
            new MorningDatabaseSession.BackupBegins(
                attempt(41, RUN, BatchStep.BACKUP_CONFIG, START, false), valid().configuration()),
            new MorningDatabaseSession.BackupBegins(
                attempt(41, RUN, BatchStep.BACKUP_DB, START, true), valid().configuration()),
            new MorningDatabaseSession.BackupBegins(
                attempt(41, RUN, BatchStep.BACKUP_DB, START.plusSeconds(1), false),
                valid().configuration()),
            new MorningDatabaseSession.BackupBegins(
                valid().database(), attempt(42, other, BatchStep.BACKUP_CONFIG, START, false)),
            new MorningDatabaseSession.BackupBegins(
                valid().database(), attempt(42, RUN, BatchStep.BACKUP_DB, START, false)),
            new MorningDatabaseSession.BackupBegins(
                valid().database(), attempt(42, RUN, BatchStep.BACKUP_CONFIG, START, true)),
            new MorningDatabaseSession.BackupBegins(
                valid().database(),
                attempt(42, RUN, BatchStep.BACKUP_CONFIG, START.plusSeconds(1), false)),
            new MorningDatabaseSession.BackupBegins(
                valid().database(), attempt(41, RUN, BatchStep.BACKUP_CONFIG, START, false)));
    for (var handle : bad) {
      db.begins = handle;
      assertEquals(
          "Morning backup preparation unavailable",
          assertThrows(
                  IOException.class,
                  () ->
                      MorningBackupPreparation.execute(
                          STATE,
                          db,
                          clock(START),
                          false,
                          (request, part) -> fail("no publish"),
                          PART,
                          (request, begins) -> fail("no work")))
              .getMessage());
    }
    db.begins = null;
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE,
                db,
                clock(START),
                false,
                (request, part) -> fail("no publish"),
                PART,
                (request, begins) -> fail("no work")));
    assertEquals(11, events.size()); // one failed begin, nine invalid handles, one null handle
  }

  @Test
  void mbprep004PublishFailureNeverInvokesWorker() {
    var events = new ArrayList<String>();
    var db = new Database(events);
    var error = new IOException("request create failed");
    assertSame(
        error,
        assertThrows(
            IOException.class,
            () ->
                MorningBackupPreparation.execute(
                    STATE,
                    db,
                    clock(START),
                    false,
                    (request, part) -> {
                      events.add("publish-failed");
                      throw error;
                    },
                    PART,
                    (request, begins) -> fail("no worker"))));
    assertEquals(List.of("DB-both-committed", "publish-failed"), events);
  }

  @Test
  void mbprep005InvalidPrecommitInputsDoNoDbOrIo() {
    var events = new ArrayList<String>();
    var db = new Database(events);
    var completed =
        new MaintenanceRunState(
            ACTIVE,
            Optional.of(
                new MaintenanceCompletion(ACTIVE, START, MaintenanceCompletion.Outcome.SUCCESS)));
    for (var state : List.of(completed, STATE)) {
      UUID part = state == completed ? PART : RUN_ID;
      assertThrows(
          IOException.class,
          () ->
              MorningBackupPreparation.execute(
                  state,
                  db,
                  clock(START),
                  false,
                  (request, id) -> fail("no publish"),
                  part,
                  (request, begins) -> fail("no work")));
    }
    assertThrows(
        IOException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE,
                db,
                clock(START),
                false,
                (request, id) -> fail("no publish"),
                new UUID(0, 0),
                (request, begins) -> fail("no work")));
    assertThrows(
        IOException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE,
                db,
                clock(CUTOFF.minusSeconds(1)),
                false,
                (request, id) -> fail("no publish"),
                PART,
                (request, begins) -> fail("no work")));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE,
                db,
                clock(Instant.parse("9999-12-31T23:59:59.999999Z")),
                false,
                (request, id) -> fail("no publish"),
                PART,
                (request, begins) -> fail("no work")));
    assertTrue(events.isEmpty());
  }

  @Test
  void mbprep006NullContractBeforeIoAndNullResultAfterPublish() throws Exception {
    var events = new ArrayList<String>();
    var db = new Database(events);
    MorningBackupPreparation.Publisher publisher = (request, part) -> events.add("publish");
    MorningBackupPreparation.Continuation<String> work = (request, begins) -> "ok";
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupPreparation.execute(null, db, clock(START), false, publisher, PART, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE, null, clock(START), false, publisher, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupPreparation.execute(STATE, db, null, false, publisher, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupPreparation.execute(STATE, db, clock(START), false, null, PART, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE, db, clock(START), false, publisher, null, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE, db, clock(START), false, publisher, PART, null));
    assertTrue(events.isEmpty());
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupPreparation.execute(
                STATE, db, clock(START), false, publisher, PART, (request, begins) -> null));
    assertEquals(List.of("DB-both-committed", "publish"), events);
  }
}
