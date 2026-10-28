package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
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
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/BAK001/UI251/SS341/343/SSC089/092/094/104/105; MBSTAGE001-004. */
final class MorningBackupStageTest {
  private static final String FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930 =
      "M/A/DB/original-enter;INVALID";
  private static final String FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF =
      "both-backup-begins-committed";
  private static final String FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74 = "M/A/DB/original-close";
  private static final String FIXTURE_REQUEST_PUBLISHED_B66E103F = "request-published";
  private static final String FIXTURE_PUBLICATION_REFUSED_38D9B6DA = "publication-refused";
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("11111111-1111-4111-8111-111111111111"),
          Instant.parse("2026-09-28T01:00:00Z"));
  private static final UUID PART = UUID.fromString("33333333-3333-4333-8333-333333333333");
  private static final Instant NOW = Instant.parse("2026-09-28T01:00:01Z");
  private static final MaintenanceRunState STATE =
      new MaintenanceRunState(
          new MaintenanceActivation(RUN, UUID.fromString("22222222-2222-4222-8222-222222222222")),
          Optional.empty());

  @Test
  void mbstage009SameOwnedEpochAndNoPublicationOnWrongGeneration() throws Exception {
    var epoch =
        new StartupPermitRecords.Epoch(
            StartupPermitRecords.State.INVALID,
            UUID.fromString("44444444-4444-4444-8444-444444444444"),
            UUID.fromString("55555555-5555-4555-8555-555555555555"),
            STATE.activation(),
            Optional.empty());
    for (var observed :
        List.of(
            epoch,
            epoch.issued("a".repeat(64)),
            new StartupPermitRecords.Epoch(
                StartupPermitRecords.State.INVALID,
                epoch.boot(),
                epoch.epoch(),
                new MaintenanceActivation(RUN, PART),
                Optional.empty()))) {
      var events = new ArrayList<String>();
      var owner = new OwnedScope(events);
      MorningBackupStage.EpochScope scope =
          new MorningBackupStage.EpochScope() {
            public <T> T execute(MorningControlScope.OwnedEpochWork<T> work) throws IOException {
              return owner.execute((state, database) -> work.execute(state, database, observed));
            }
          };
      java.util.concurrent.Callable<Boolean> execute =
          () ->
              MorningBackupStage.executeOwnedEpoch(
                  scope,
                  (request, part) -> {
                    assertTrue(owner.held.get());
                    events.add("request");
                  },
                  Clock.fixed(NOW, ZoneOffset.UTC),
                  false,
                  PART,
                  (state, database, current, request, begins, part) -> {
                    assertTrue(owner.held.get());
                    assertSame(STATE, state);
                    assertSame(owner.database, database);
                    assertSame(epoch, current);
                    assertEquals(PART, part);
                    assertEquals(RUN.id(), request.run());
                    assertEquals(41, begins.database().id());
                    events.add("same-epoch-work");
                    return true;
                  });
      if (observed == epoch) {
        assertTrue(execute.call());
        assertEquals(
            List.of(
                FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
                FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF,
                "request",
                "same-epoch-work",
                FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
            events);
      } else {
        assertThrows(IOException.class, execute::call);
        assertEquals(
            List.of(
                FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
                FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
            events);
      }
    }
  }

  private static final class OwnedScope implements MorningBackupStage.Scope {
    final List<String> events;
    final AtomicBoolean held = new AtomicBoolean();
    final Db database;

    OwnedScope(List<String> events) {
      this.events = events;
      database = new Db(events, held);
    }

    @Override
    public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation)
        throws IOException {
      events.add(FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930);
      held.set(true);
      try {
        return continuation.execute(STATE, database);
      } finally {
        held.set(false);
        events.add(FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74);
      }
    }
  }

  private static final class Db implements MorningDatabaseSession.Access {
    final List<String> events;
    final AtomicBoolean held;
    boolean recover;
    IOException error;

    Db(List<String> events, AtomicBoolean held) {
      this.events = events;
      this.held = held;
    }

    @Override
    public void requireUnused(BatchRun run) {
      fail("prior original admission owns reference check");
    }

    @Override
    public void requireConsistent(BatchRun run) {
      fail("prior original admission owns reference check");
    }

    @Override
    public MorningDatabaseSession.BackupBegins beginBackup(
        BatchRun run, Instant now, boolean recoverAbandoned) throws IOException {
      assertTrue(held.get());
      assertEquals(RUN, run);
      assertEquals(NOW, now);
      recover = recoverAbandoned;
      events.add(FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF);
      if (error != null) throw error;
      return new MorningDatabaseSession.BackupBegins(
          new BatchStepAttempt(41, RUN, BatchStep.BACKUP_DB, 1, NOW, false),
          new BatchStepAttempt(42, RUN, BatchStep.BACKUP_CONFIG, 1, NOW, false));
    }

    @Override
    public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> operation) {
      return fail("cleanup is downstream");
    }
  }

  @Test
  void mbstage001RetainsAllParentOwnersThroughRequestAndWork() throws Exception {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    var result =
        MorningBackupStage.execute(
            scope,
            (request, part) -> {
              assertTrue(scope.held.get());
              assertEquals(RUN.id(), request.run());
              assertEquals(PART, part);
              events.add(FIXTURE_REQUEST_PUBLISHED_B66E103F);
            },
            Clock.fixed(NOW, ZoneOffset.UTC),
            false,
            PART,
            (request, begins) -> {
              assertTrue(scope.held.get());
              assertEquals(BatchStep.BACKUP_DB, begins.database().step());
              assertEquals(BatchStep.BACKUP_CONFIG, begins.configuration().step());
              events.add("worker-boundary");
              return "ready-for-worker";
            });
    assertEquals("ready-for-worker", result);
    assertFalse(scope.database.recover);
    assertFalse(scope.held.get());
    assertEquals(
        List.of(
            FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
            FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF,
            FIXTURE_REQUEST_PUBLISHED_B66E103F,
            "worker-boundary",
            FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
        events);
  }

  @Test
  void mbstage002ExplicitResumePreservesOriginalAndRecoveryFlag() throws Exception {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    UUID observed =
        MorningBackupStage.execute(
            scope,
            (request, part) -> {},
            Clock.fixed(NOW, ZoneOffset.UTC),
            true,
            PART,
            (request, begins) -> request.run());
    assertEquals(RUN.id(), observed);
    assertTrue(scope.database.recover);
  }

  @Test
  void mbstage003DbOrPublishFailureClosesScopeWithoutWorkerSuccess() {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    scope.database.error = new IOException("raw commit unknown");
    assertSame(
        scope.database.error,
        assertThrows(
            IOException.class,
            () ->
                MorningBackupStage.execute(
                    scope,
                    (request, part) -> fail("no publication"),
                    Clock.fixed(NOW, ZoneOffset.UTC),
                    false,
                    PART,
                    (request, begins) -> fail("no worker"))));
    assertEquals(
        List.of(
            FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
            FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF,
            FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
        events);
    events.clear();
    scope.database.error = null;
    assertThrows(
        IOException.class,
        () ->
            MorningBackupStage.execute(
                scope,
                (request, part) -> {
                  events.add(FIXTURE_PUBLICATION_REFUSED_38D9B6DA);
                  throw new IOException("new-only conflict");
                },
                Clock.fixed(NOW, ZoneOffset.UTC),
                false,
                PART,
                (request, begins) -> fail("no worker")));
    assertEquals(
        List.of(
            FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
            FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF,
            FIXTURE_PUBLICATION_REFUSED_38D9B6DA,
            FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
        events);
  }

  @Test
  void mbstage004NullContractAndNullWorkerResult() {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    MorningBackupPreparation.Publisher publisher = (request, part) -> {};
    MorningBackupPreparation.Continuation<String> work = (request, begins) -> "ok";
    var clock = Clock.fixed(NOW, ZoneOffset.UTC);
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.execute(null, publisher, clock, false, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.execute(scope, null, clock, false, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.execute(scope, publisher, null, false, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.execute(scope, publisher, clock, false, null, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.execute(scope, publisher, clock, false, PART, null));
    assertTrue(events.isEmpty());
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupStage.execute(
                scope, publisher, clock, false, PART, (request, begins) -> null));
    assertFalse(scope.held.get());
    assertEquals(FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74, events.getLast());
  }

  @Test
  void mbstage005PassesExactOwnedValuesOnlyDuringScope() throws Exception {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    String result =
        MorningBackupStage.executeOwned(
            scope,
            (request, part) -> {
              assertTrue(scope.held.get());
              assertEquals(RUN.id(), request.run());
              assertEquals(PART, part);
              events.add(FIXTURE_REQUEST_PUBLISHED_B66E103F);
            },
            Clock.fixed(NOW, ZoneOffset.UTC),
            false,
            PART,
            (state, database, request, begins, part) -> {
              assertTrue(scope.held.get());
              assertSame(STATE, state);
              assertSame(scope.database, database);
              assertEquals(RUN.id(), request.run());
              assertEquals(NOW, request.started());
              assertEquals(PART, part);
              assertEquals(BatchStep.BACKUP_DB, begins.database().step());
              assertEquals(BatchStep.BACKUP_CONFIG, begins.configuration().step());
              events.add("owned-worker-boundary");
              return "owned";
            });
    assertEquals("owned", result);
    assertFalse(scope.held.get());
    assertEquals(
        List.of(
            FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
            FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF,
            FIXTURE_REQUEST_PUBLISHED_B66E103F,
            "owned-worker-boundary",
            FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
        events);
  }

  @Test
  void mbstage006ResumeFlagAndLegacyWorkRemainStable() throws Exception {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    assertSame(
        STATE,
        MorningBackupStage.executeOwned(
            scope,
            (request, part) -> assertEquals(PART, part),
            Clock.fixed(NOW, ZoneOffset.UTC),
            true,
            PART,
            (state, database, request, begins, part) -> {
              assertTrue(scope.held.get());
              assertSame(scope.database, database);
              assertEquals(PART, part);
              return state;
            }));
    assertTrue(scope.database.recover);
    assertEquals(
        RUN.id(),
        MorningBackupStage.execute(
            scope,
            (request, part) -> assertEquals(PART, part),
            Clock.fixed(NOW, ZoneOffset.UTC),
            false,
            PART,
            (request, begins) -> request.run()));
    assertFalse(scope.database.recover);
    assertFalse(scope.held.get());
  }

  @Test
  void mbstage007PreWorkFailureNeverInvokesBorrowedWork() {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    scope.database.error = new IOException("test-only begin failure");
    assertSame(
        scope.database.error,
        assertThrows(
            IOException.class,
            () ->
                MorningBackupStage.executeOwned(
                    scope,
                    (request, part) -> fail("no request"),
                    Clock.fixed(NOW, ZoneOffset.UTC),
                    false,
                    PART,
                    (state, database, request, begins, part) -> fail("no work"))));
    assertFalse(scope.held.get());
    events.clear();
    scope.database.error = null;
    assertThrows(
        IOException.class,
        () ->
            MorningBackupStage.executeOwned(
                scope,
                (request, part) -> {
                  events.add(FIXTURE_PUBLICATION_REFUSED_38D9B6DA);
                  throw new IOException("test-only publication failure");
                },
                Clock.fixed(NOW, ZoneOffset.UTC),
                false,
                PART,
                (state, database, request, begins, part) -> fail("no work")));
    assertFalse(scope.held.get());
    assertEquals(
        List.of(
            FIXTURE_M_A_DB_ORIGINAL_ENTER_INVALID_FA4E0930,
            FIXTURE_BOTH_BACKUP_BEGINS_COMMITTED_AF100AAF,
            FIXTURE_PUBLICATION_REFUSED_38D9B6DA,
            FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74),
        events);
  }

  @Test
  void mbstage008NullContractAndNullResultAreNotSuccess() {
    var events = new ArrayList<String>();
    var scope = new OwnedScope(events);
    MorningBackupPreparation.Publisher publisher = (request, part) -> {};
    MorningBackupStage.OwnedWork<String> work = (state, database, request, begins, part) -> "ok";
    var clock = Clock.fixed(NOW, ZoneOffset.UTC);
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.executeOwned(null, publisher, clock, false, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.executeOwned(scope, null, clock, false, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.executeOwned(scope, publisher, null, false, PART, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.executeOwned(scope, publisher, clock, false, null, work));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupStage.executeOwned(scope, publisher, clock, false, PART, null));
    assertTrue(events.isEmpty());
    assertThrows(
        NullPointerException.class,
        () ->
            MorningBackupStage.executeOwned(
                scope,
                publisher,
                clock,
                false,
                PART,
                (state, database, request, begins, part) -> null));
    assertFalse(scope.held.get());
    assertEquals(FIXTURE_M_A_DB_ORIGINAL_CLOSE_92A6AD74, events.getLast());
  }
}
