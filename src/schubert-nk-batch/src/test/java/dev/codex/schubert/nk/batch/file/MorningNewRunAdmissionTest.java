package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** NK-BAT-001/NK-OPS-001; OPS009/UI251/SS341/343/SSC055/094/PG343/346; PT-OPS-MNEW001-011. */
final class MorningNewRunAdmissionTest {
  private static final UUID RUN = UUID.fromString("00000000-0000-0000-0000-000000000341");
  private static final UUID ACTIVATION = UUID.fromString("00000000-0000-0000-0000-000000000342");
  private static final Instant CLOCK = Instant.parse("2026-09-28T05:00:00.123456789Z");

  private static final class Harness {
    final List<String> events = new ArrayList<>();
    final AtomicBoolean dbHeld = new AtomicBoolean();
    final AtomicBoolean fileHeld = new AtomicBoolean();
    IOException referenceFailure;
    IOException startFailure;
    int originalVariant;
    int ids;
    boolean proofAvailable;

    MorningNewRunAdmission admission() {
      return new MorningNewRunAdmission(
          () -> events.add("root"),
          new MorningNewRunAdmission.Database() {
            @Override
            public <T> T execute(MorningNewRunAdmission.DatabaseWork<T> work) throws IOException {
              events.add("db-enter");
              dbHeld.set(true);
              try {
                return work.execute(
                    new MorningDatabaseSession.Access() {
                      public void requireUnused(BatchRun run) throws IOException {
                        events.add("references");
                        if (referenceFailure != null) throw referenceFailure;
                      }

                      public void requireConsistent(BatchRun run) {
                        fail("new run must not inspect resume references");
                      }

                      public MorningDatabaseSession.BackupBegins beginBackup(
                          BatchRun run, Instant now, boolean recoverAbandoned) {
                        events.add("begin-backup");
                        assertTrue(dbHeld.get() && fileHeld.get());
                        assertFalse(recoverAbandoned);
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
                events.add("db-close");
              }
            }
          },
          new MorningNewRunAdmission.Originals() {
            @Override
            public <T> T execute(MorningNewRunAdmission.FileWork<T> work) throws IOException {
              events.add("file-enter");
              fileHeld.set(true);
              try {
                MorningNewRunAdmission.Files original =
                    (run, activation) -> {
                      events.add("original-start");
                      if (startFailure != null) throw startFailure;
                      BatchRun stored =
                          originalVariant == 1 ? new BatchRun(ACTIVATION, run.cutoff()) : run;
                      var actual =
                          new MaintenanceActivation(
                              stored, originalVariant == 2 ? RUN : activation);
                      return new MaintenanceRunState(
                          actual,
                          originalVariant == 3
                              ? Optional.of(
                                  new MaintenanceCompletion(
                                      actual,
                                      run.cutoff().plusSeconds(1),
                                      MaintenanceCompletion.Outcome.SUCCESS))
                              : Optional.empty());
                    };
                if (proofAvailable)
                  return work.execute(
                      new MorningNewRunAdmission.Files() {
                        public MaintenanceRunState start(BatchRun run, UUID activation)
                            throws IOException {
                          return original.start(run, activation);
                        }

                        public void verify(MaintenanceActivation expected) throws IOException {
                          assertTrue(dbHeld.get() && fileHeld.get());
                          assertEquals(
                              new MaintenanceActivation(
                                  new BatchRun(RUN, Instant.parse("2026-09-28T05:00:00.123456Z")),
                                  ACTIVATION),
                              expected);
                          events.add("original-proof");
                        }
                      });
                return work.execute(original);
              } finally {
                fileHeld.set(false);
                events.add("file-close");
              }
            }
          },
          Clock.fixed(CLOCK, ZoneOffset.UTC),
          () -> ids++ == 0 ? RUN : ACTIVATION);
    }
  }

  @Test
  void mnew012OriginalProofIsSameOwnerThreadAndLifetime() throws Exception {
    var h = new Harness();
    h.proofAvailable = true;
    var held =
        new java.util.concurrent.atomic.AtomicReference<MorningNewRunAdmission.OriginalProof>();
    assertEquals(
        "verified",
        h.admission()
            .executeVerified(
                (state, database, original) -> {
                  original.verify();
                  held.set(original);
                  try (var other = Executors.newSingleThreadExecutor()) {
                    assertEquals(
                        "Morning new-run admission unavailable",
                        assertDoesNotThrow(
                            () ->
                                other
                                    .submit(
                                        () ->
                                            assertThrows(IOException.class, original::verify)
                                                .getMessage())
                                    .get(5, TimeUnit.SECONDS)));
                  }
                  assertTrue(h.dbHeld.get() && h.fileHeld.get());
                  return "verified";
                }));
    assertEquals(1, h.events.stream().filter("original-proof"::equals).count());
    assertThrows(IOException.class, held.get()::verify);
    var absent = new Harness();
    assertThrows(
        IOException.class,
        () ->
            absent
                .admission()
                .executeVerified(
                    (state, database, proof) -> {
                      proof.verify();
                      return fail("unassembled proof must not pass");
                    }));
  }

  @Test
  void mnew001ReferencesBeforeOriginalAndContinuationWithinBothOwners() throws Exception {
    var h = new Harness();
    String result =
        h.admission()
            .execute(
                state -> {
                  assertTrue(h.dbHeld.get());
                  assertTrue(h.fileHeld.get());
                  assertEquals(RUN, state.activation().run().id());
                  assertEquals(ACTIVATION, state.activation().id());
                  assertEquals(
                      Instant.parse("2026-09-28T05:00:00.123456Z"),
                      state.activation().run().cutoff());
                  h.events.add("continuation");
                  return "held";
                });
    assertEquals("held", result);
    assertEquals(
        List.of(
            "root",
            "db-enter",
            "root",
            "references",
            "root",
            "file-enter",
            "root",
            "original-start",
            "root",
            "continuation",
            "root",
            "file-close",
            "db-close",
            "root"),
        h.events);
    assertFalse(h.dbHeld.get());
    assertFalse(h.fileHeld.get());
  }

  @Test
  void mnew002DbReferenceFailureNeverOpensOriginal() {
    var h = new Harness();
    h.referenceFailure = new IOException("reference unknown");
    assertSame(
        h.referenceFailure,
        assertThrows(IOException.class, () -> h.admission().execute(state -> fail("no stop"))));
    assertEquals(List.of("root", "db-enter", "root", "references", "db-close"), h.events);
    assertFalse(h.dbHeld.get());
  }

  @Test
  void mnew003OriginalFailureNeverEntersContinuation() {
    var h = new Harness();
    h.startFailure = new IOException("durable start unknown");
    assertSame(
        h.startFailure,
        assertThrows(IOException.class, () -> h.admission().execute(state -> fail("no stop"))));
    assertEquals("original-start", h.events.get(7));
    assertEquals(List.of("file-close", "db-close"), h.events.subList(8, 10));
    assertFalse(h.dbHeld.get());
    assertFalse(h.fileHeld.get());
  }

  @Test
  void mnew004ReturnedOriginalIdentityAndCompletionMustMatchNewRun() {
    for (int variant = 1; variant <= 3; variant++) {
      var h = new Harness();
      h.originalVariant = variant;
      assertEquals(
          "Morning new-run admission unavailable",
          assertThrows(IOException.class, () -> h.admission().execute(state -> fail("no stop")))
              .getMessage());
      assertEquals(List.of("file-close", "db-close"), h.events.subList(8, 10));
    }
  }

  @Test
  void mnew005ContinuationFailurePreservesIdentityAndClosesBothOwners() {
    var h = new Harness();
    var failure = new IOException("trusted failure");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                h.admission()
                    .execute(
                        state -> {
                          throw failure;
                        })));
    assertEquals(
        List.of("file-close", "db-close"), h.events.subList(h.events.size() - 2, h.events.size()));
    assertFalse(h.dbHeld.get());
    assertFalse(h.fileHeld.get());
  }

  @Test
  void mnew006UnknownRuntimeAndNullResultDoNotBecomeSuccess() {
    var runtime = new IllegalStateException("unknown");
    var a = new Harness();
    assertSame(
        runtime,
        assertThrows(
            IllegalStateException.class,
            () ->
                a.admission()
                    .execute(
                        state -> {
                          throw runtime;
                        })));
    assertEquals(
        List.of("file-close", "db-close"), a.events.subList(a.events.size() - 2, a.events.size()));
    var b = new Harness();
    assertThrows(NullPointerException.class, () -> b.admission().execute(state -> null));
    assertFalse(b.dbHeld.get());
    assertFalse(b.fileHeld.get());
  }

  @Test
  void mnew007NullContractAndDuplicateIdsRejectBeforeDb() {
    var h = new Harness();
    assertThrows(NullPointerException.class, () -> h.admission().execute(null));
    assertTrue(h.events.isEmpty());
    var duplicate =
        new MorningNewRunAdmission(
            () -> h.events.add("root"),
            new MorningNewRunAdmission.Database() {
              @Override
              public <T> T execute(MorningNewRunAdmission.DatabaseWork<T> work) {
                return fail("DB must not open");
              }
            },
            new MorningNewRunAdmission.Originals() {
              @Override
              public <T> T execute(MorningNewRunAdmission.FileWork<T> work) {
                return fail("file must not open");
              }
            },
            Clock.fixed(CLOCK, ZoneOffset.UTC),
            () -> RUN);
    assertEquals(
        "Morning new-run admission unavailable",
        assertThrows(IOException.class, () -> duplicate.execute(state -> fail("no work")))
            .getMessage());
    assertEquals(List.of("root"), h.events);
  }

  @Test
  void mnew008UnfinishedContinuationRetainsDbAndOriginalOwners() throws Exception {
    var h = new Harness();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var executor = Executors.newSingleThreadExecutor()) {
      var future =
          executor.submit(
              () ->
                  h.admission()
                      .execute(
                          state -> {
                            entered.countDown();
                            try {
                              if (!release.await(5, TimeUnit.SECONDS))
                                throw new IOException("test timeout");
                            } catch (InterruptedException interrupted) {
                              Thread.currentThread().interrupt();
                              throw new IOException("test interrupted");
                            }
                            return Boolean.TRUE;
                          }));
      assertTrue(entered.await(5, TimeUnit.SECONDS));
      assertTrue(h.dbHeld.get());
      assertTrue(h.fileHeld.get());
      assertFalse(future.isDone());
      release.countDown();
      assertTrue(future.get(5, TimeUnit.SECONDS));
      assertFalse(h.dbHeld.get());
      assertFalse(h.fileHeld.get());
    } finally {
      release.countDown();
    }
  }

  @Test
  void mnew009WrongRootActorIsRejectedBeforeNativeAdmission() {
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.CLEANUP,
            "test-boot",
            "test-invocation",
            1,
            1,
            1,
            "/system.slice/schubert-nk-cleanup.service");
    assertEquals(
        "Morning new-run admission unavailable",
        assertThrows(
                IOException.class,
                () -> MorningNewRunAdmission.create(RootStartupContext.create(), wrong))
            .getMessage());
  }

  @Test
  void mnew010FactoryNullContractRejectsBeforeRootIo() {
    assertThrows(NullPointerException.class, () -> MorningNewRunAdmission.create(null, null));
    assertThrows(
        NullPointerException.class,
        () -> MorningNewRunAdmission.create(RootStartupContext.create(), null));
  }

  @Test
  void mnew011BackupAndHandoffCapabilityRemainInsideBothOwners() throws Exception {
    var h = new Harness();
    boolean completed =
        h.admission()
            .executeOwned(
                (state, database) -> {
                  var run = state.activation().run();
                  var backup = database.beginBackup(run, run.cutoff(), false);
                  assertEquals(BatchStep.BACKUP_DB, backup.database().step());
                  assertEquals(BatchStep.BACKUP_CONFIG, backup.configuration().step());
                  return database.handoffCleanup(
                      () -> {
                        assertTrue(h.dbHeld.get() && h.fileHeld.get());
                        h.events.add("cleanup-child");
                        return true;
                      });
                });
    assertTrue(completed);
    assertTrue(h.events.indexOf("references") < h.events.indexOf("begin-backup"));
    assertTrue(h.events.indexOf("begin-backup") < h.events.indexOf("handoff"));
    assertEquals(
        List.of("file-close", "db-close", "root"),
        h.events.subList(h.events.size() - 3, h.events.size()));
  }
}
