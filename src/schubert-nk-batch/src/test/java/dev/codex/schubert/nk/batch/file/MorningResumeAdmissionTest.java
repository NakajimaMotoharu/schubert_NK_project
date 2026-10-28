package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** OPS009/UI251/SS341§11/343§6.15/SSC055/094/BUG317; PG345/346/PT-OPS-MRESUME001-010. */
final class MorningResumeAdmissionTest {
  private static final String FIXTURE_ROOT_956E6E33 = "root";
  private static final String FIXTURE_DB_ENTER_26938A52 = "DB-enter";
  private static final String FIXTURE_REFERENCES_3C0C408A = "references";
  private static final String FIXTURE_DB_CLOSE_FA8A29FA = "DB-close";
  private static final String FIXTURE_FILE_ENTER_A7A9047E = "file-enter";
  private static final String FIXTURE_RESUME_D1C375C5 = "resume";
  private static final String FIXTURE_FILE_CLOSE_C39730AD = "file-close";

  @Test
  void mresume011VerifiedOriginalIsBoundToSameHeldOwnerThreadAndLifetime() throws Exception {
    var h = new Harness();
    var leaked =
        new java.util.concurrent.atomic.AtomicReference<MorningNewRunAdmission.OriginalProof>();
    assertEquals(
        "verified",
        h.admission()
            .executeVerified(
                RUN,
                (state, database, proof) -> {
                  assertTrue(h.dbHeld.get() && h.fileHeld.get());
                  assertEquals(CUTOFF, state.activation().run().cutoff());
                  proof.verify();
                  leaked.set(proof);
                  try (var threads = Executors.newSingleThreadExecutor()) {
                    assertInstanceOf(
                        IOException.class,
                        threads
                            .submit(
                                () -> {
                                  try {
                                    proof.verify();
                                    return new AssertionError("foreign thread accepted");
                                  } catch (IOException rejected) {
                                    return rejected;
                                  }
                                })
                            .get());
                  } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new IOException("test interrupted");
                  } catch (java.util.concurrent.ExecutionException failure) {
                    throw new IOException("test execution failed");
                  }
                  proof.verify();
                  return "verified";
                }));
    assertFalse(h.dbHeld.get() || h.fileHeld.get());
    assertThrows(IOException.class, leaked.get()::verify);
    assertEquals(2, h.events.stream().filter("original-proof"::equals).count());
    assertThrows(
        NullPointerException.class,
        () -> h.admission().executeVerified(null, (s, d, p) -> "unused"));
    assertThrows(NullPointerException.class, () -> h.admission().executeVerified(RUN, null));
  }

  private static final UUID RUN = UUID.fromString("00000000-0000-0000-0000-000000000345");
  private static final UUID ACTIVE = UUID.fromString("00000000-0000-0000-0000-000000000346");
  private static final UUID NEXT = UUID.fromString("00000000-0000-0000-0000-000000000347");
  private static final Instant CUTOFF = Instant.parse("2026-09-27T15:00:00.123456Z");
  private static final MaintenanceRunState ORIGINAL =
      new MaintenanceRunState(
          new MaintenanceActivation(new BatchRun(RUN, CUTOFF), ACTIVE), Optional.empty());

  private static final class Harness {
    final List<String> events = new ArrayList<>();
    final AtomicBoolean fileHeld = new AtomicBoolean();
    final AtomicBoolean dbHeld = new AtomicBoolean();
    IOException originalFailure;
    IOException referencesFailure;
    IOException databaseFailure;
    MaintenanceRunState returned = ORIGINAL;

    MorningResumeAdmission admission() {
      return new MorningResumeAdmission(
          () -> events.add(FIXTURE_ROOT_956E6E33),
          new MorningResumeAdmission.Database() {
            @Override
            public <T> T execute(MorningResumeAdmission.DatabaseWork<T> work) throws IOException {
              events.add(FIXTURE_DB_ENTER_26938A52);
              if (databaseFailure != null) throw databaseFailure;
              dbHeld.set(true);
              try {
                return work.execute(
                    new MorningDatabaseSession.Access() {
                      public void requireUnused(BatchRun run) {
                        fail("resume must not require absent history");
                      }

                      public void requireConsistent(BatchRun run) throws IOException {
                        events.add(FIXTURE_REFERENCES_3C0C408A);
                        assertEquals(RUN, run.id());
                        assertEquals(CUTOFF, run.cutoff());
                        if (referencesFailure != null) throw referencesFailure;
                      }

                      public MorningDatabaseSession.BackupBegins beginBackup(
                          BatchRun run, Instant now, boolean recoverAbandoned) {
                        events.add("begin-backup");
                        assertTrue(dbHeld.get() && fileHeld.get());
                        assertEquals(RUN, run.id());
                        assertEquals(CUTOFF, run.cutoff());
                        assertTrue(recoverAbandoned);
                        return new MorningDatabaseSession.BackupBegins(
                            new BatchStepAttempt(1, run, BatchStep.BACKUP_DB, 1, now, false),
                            new BatchStepAttempt(2, run, BatchStep.BACKUP_CONFIG, 1, now, false));
                      }

                      public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work)
                          throws IOException {
                        events.add("handoff");
                        assertTrue(dbHeld.get() && fileHeld.get());
                        return work.execute();
                      }
                    });
              } finally {
                dbHeld.set(false);
                events.add(FIXTURE_DB_CLOSE_FA8A29FA);
              }
            }
          },
          new MorningResumeAdmission.Originals() {
            @Override
            public <T> T execute(MorningResumeAdmission.FileWork<T> work) throws IOException {
              events.add(FIXTURE_FILE_ENTER_A7A9047E);
              fileHeld.set(true);
              try {
                return work.execute(
                    new MorningResumeAdmission.Files() {
                      public MaintenanceRunState resume(UUID run, UUID next) throws IOException {
                        events.add(FIXTURE_RESUME_D1C375C5);
                        assertTrue(dbHeld.get(), "DB advisory must be owned before durable resume");
                        assertEquals(RUN, run);
                        assertEquals(NEXT, next);
                        if (originalFailure != null) throw originalFailure;
                        return returned;
                      }

                      public void verify(MaintenanceActivation activation) {
                        assertTrue(dbHeld.get() && fileHeld.get());
                        assertEquals(returned.activation(), activation);
                        events.add("original-proof");
                      }
                    });
              } finally {
                fileHeld.set(false);
                events.add(FIXTURE_FILE_CLOSE_C39730AD);
              }
            }
          },
          () -> NEXT);
    }
  }

  @Test
  void mresume001DbBeforeDurableResumeAndBothOwnersThroughContinuation() throws Exception {
    var h = new Harness();
    String result =
        h.admission()
            .execute(
                RUN,
                state -> {
                  assertSame(ORIGINAL, state);
                  assertTrue(h.fileHeld.get() && h.dbHeld.get());
                  h.events.add("continuation");
                  return "same-run";
                });
    assertEquals("same-run", result);
    assertEquals(
        List.of(
            FIXTURE_ROOT_956E6E33,
            FIXTURE_DB_ENTER_26938A52,
            FIXTURE_ROOT_956E6E33,
            FIXTURE_FILE_ENTER_A7A9047E,
            FIXTURE_ROOT_956E6E33,
            FIXTURE_RESUME_D1C375C5,
            FIXTURE_ROOT_956E6E33,
            FIXTURE_REFERENCES_3C0C408A,
            FIXTURE_ROOT_956E6E33,
            "continuation",
            FIXTURE_ROOT_956E6E33,
            FIXTURE_FILE_CLOSE_C39730AD,
            FIXTURE_DB_CLOSE_FA8A29FA,
            FIXTURE_ROOT_956E6E33),
        h.events);
    assertFalse(h.fileHeld.get());
    assertFalse(h.dbHeld.get());
  }

  @Test
  void mresume002DurableOriginalFailureClosesDbAndStartsNoStop() {
    var h = new Harness();
    h.originalFailure = new IOException("durable graph unavailable");
    assertSame(
        h.originalFailure,
        assertThrows(
            IOException.class, () -> h.admission().execute(RUN, state -> fail("no continuation"))));
    assertEquals(
        List.of(
            FIXTURE_ROOT_956E6E33,
            FIXTURE_DB_ENTER_26938A52,
            FIXTURE_ROOT_956E6E33,
            FIXTURE_FILE_ENTER_A7A9047E,
            FIXTURE_ROOT_956E6E33,
            FIXTURE_RESUME_D1C375C5,
            FIXTURE_FILE_CLOSE_C39730AD,
            FIXTURE_DB_CLOSE_FA8A29FA),
        h.events);
  }

  @Test
  void mresume003DbReferenceConflictStartsNoStopAndPreservesOriginal() {
    var h = new Harness();
    h.referencesFailure = new IOException("reference mismatch");
    assertSame(
        h.referencesFailure,
        assertThrows(
            IOException.class, () -> h.admission().execute(RUN, state -> fail("no continuation"))));
    assertEquals(
        List.of(FIXTURE_FILE_CLOSE_C39730AD, FIXTURE_DB_CLOSE_FA8A29FA),
        h.events.subList(h.events.size() - 2, h.events.size()));
    assertTrue(h.events.contains(FIXTURE_RESUME_D1C375C5));
    assertFalse(h.fileHeld.get() || h.dbHeld.get());
  }

  @Test
  void mresume004WrongReturnedRunIdCannotCheckReferences() {
    var h = new Harness();
    h.returned =
        new MaintenanceRunState(
            new MaintenanceActivation(new BatchRun(NEXT, CUTOFF), ACTIVE), Optional.empty());
    assertEquals(
        "Morning same-run resume unavailable",
        assertThrows(IOException.class, () -> h.admission().execute(RUN, state -> fail("no work")))
            .getMessage());
    assertFalse(h.events.contains(FIXTURE_REFERENCES_3C0C408A));
    assertEquals(FIXTURE_DB_CLOSE_FA8A29FA, h.events.getLast());
  }

  @Test
  void mresume005CompletedOriginalIsPassedWithoutForgingNewSuccess() throws Exception {
    var h = new Harness();
    h.returned =
        new MaintenanceRunState(
            ORIGINAL.activation(),
            Optional.of(
                new MaintenanceCompletion(
                    ORIGINAL.activation(),
                    CUTOFF.plusSeconds(1),
                    MaintenanceCompletion.Outcome.SUCCESS)));
    boolean completed =
        h.admission()
            .execute(
                RUN,
                state -> {
                  assertEquals(h.returned, state);
                  assertTrue(state.completion().isPresent());
                  return true;
                });
    assertTrue(completed);
    assertTrue(h.events.contains(FIXTURE_REFERENCES_3C0C408A));
  }

  @Test
  void mresume006NullAndDuplicateIdContracts() {
    var h = new Harness();
    assertThrows(NullPointerException.class, () -> h.admission().execute(null, state -> true));
    assertThrows(NullPointerException.class, () -> h.admission().execute(RUN, null));
    assertTrue(h.events.isEmpty());
    var duplicate =
        new MorningResumeAdmission(
            () -> {},
            new MorningResumeAdmission.Database() {
              @Override
              public <T> T execute(MorningResumeAdmission.DatabaseWork<T> work) {
                return fail("no DB for duplicate identity");
              }
            },
            new MorningResumeAdmission.Originals() {
              @Override
              public <T> T execute(MorningResumeAdmission.FileWork<T> work) {
                return fail("no file for duplicate identity");
              }
            },
            () -> RUN);
    assertThrows(IOException.class, () -> duplicate.execute(RUN, state -> true));
    assertTrue(h.events.isEmpty());
  }

  @Test
  void mresume007ConcurrentContinuationKeepsBothOwners() throws Exception {
    var h = new Harness();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var workers = Executors.newSingleThreadExecutor()) {
      var future =
          workers.submit(
              () ->
                  h.admission()
                      .execute(
                          RUN,
                          state -> {
                            entered.countDown();
                            try {
                              assertTrue(release.await(2, TimeUnit.SECONDS));
                            } catch (InterruptedException interrupted) {
                              Thread.currentThread().interrupt();
                              throw new IOException("test interrupted");
                            }
                            return true;
                          }));
      try {
        assertTrue(entered.await(2, TimeUnit.SECONDS));
        assertTrue(h.fileHeld.get() && h.dbHeld.get());
        assertFalse(future.isDone());
      } finally {
        release.countDown();
      }
      assertTrue(future.get(2, TimeUnit.SECONDS));
      assertFalse(h.fileHeld.get() || h.dbHeld.get());
    }
  }

  @Test
  void mresume008NativeFactoryRejectsWrongActorAndMissingIdentity() {
    var context = RootStartupContext.create();
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.CLEANUP, "PUBLIC", "PUBLIC", 2, 1, 1, "PUBLIC");
    assertThrows(IOException.class, () -> MorningResumeAdmission.create(context, wrong));
    assertThrows(NullPointerException.class, () -> MorningResumeAdmission.create(null, wrong));
    assertThrows(NullPointerException.class, () -> MorningResumeAdmission.create(context, null));
    assertThrows(
        NullPointerException.class, () -> MorningControlScope.executeResume(null, state -> true));
    assertThrows(NullPointerException.class, () -> MorningControlScope.executeResume(RUN, null));
  }

  @Test
  void mresume009UnavailableDbNeverMutatesOriginal() {
    var h = new Harness();
    h.databaseFailure = new IOException("advisory unavailable");
    assertSame(
        h.databaseFailure,
        assertThrows(
            IOException.class, () -> h.admission().execute(RUN, state -> fail("no continuation"))));
    assertEquals(List.of(FIXTURE_ROOT_956E6E33, FIXTURE_DB_ENTER_26938A52), h.events);
    assertFalse(h.events.contains(FIXTURE_FILE_ENTER_A7A9047E));
    assertFalse(h.events.contains(FIXTURE_RESUME_D1C375C5));
  }

  @Test
  void mresume010BackupCapabilityUsesOriginalCutoffInsideBothOwners() throws Exception {
    var h = new Harness();
    boolean completed =
        h.admission()
            .executeOwned(
                RUN,
                (state, database) -> {
                  var run = state.activation().run();
                  var backup = database.beginBackup(run, CUTOFF.plusSeconds(1), true);
                  assertEquals(BatchStep.BACKUP_DB, backup.database().step());
                  assertEquals(BatchStep.BACKUP_CONFIG, backup.configuration().step());
                  return database.handoffCleanup(
                      () -> {
                        h.events.add("cleanup-child");
                        assertTrue(h.dbHeld.get() && h.fileHeld.get());
                        return true;
                      });
                });
    assertTrue(completed);
    assertTrue(h.events.indexOf(FIXTURE_REFERENCES_3C0C408A) < h.events.indexOf("begin-backup"));
    assertTrue(h.events.indexOf("begin-backup") < h.events.indexOf("handoff"));
    assertEquals(
        List.of(FIXTURE_FILE_CLOSE_C39730AD, FIXTURE_DB_CLOSE_FA8A29FA, FIXTURE_ROOT_956E6E33),
        h.events.subList(h.events.size() - 3, h.events.size()));
  }
}
