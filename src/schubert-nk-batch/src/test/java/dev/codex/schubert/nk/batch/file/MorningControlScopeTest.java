package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.file.StartupPermitRecords.Epoch;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords.State;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.LinuxFileLock;
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

/** NK-OPS-001/OPS009/UI251/SS341/343/SSC089/094/105/106/108; PT-OPS-MCTRL001-018. */
final class MorningControlScopeTest {

  /** PT-OPS-MCTRL019: no null may select a new run or reach native ownership work. */
  @Test
  void mctrl019NativeEntryNullContractsNeverReachTrustedWork() throws Exception {
    var called = new java.util.concurrent.atomic.AtomicInteger();
    MorningNewRunAdmission.Continuation<String> work =
        state -> {
          called.incrementAndGet();
          throw new AssertionError("trusted work must not execute");
        };
    MorningNewRunAdmission.OwnedContinuation<String> owned =
        (state, database) -> {
          called.incrementAndGet();
          throw new AssertionError("owned work must not execute");
        };
    MorningControlScope.OwnedEpochWork<String> epoch =
        (state, database, generation) -> {
          called.incrementAndGet();
          throw new AssertionError("epoch work must not execute");
        };
    MorningControlScope.VerifiedEpochWork<String> verified =
        (state, database, generation, original, stop, publication) -> {
          called.incrementAndGet();
          throw new AssertionError("verified work must not execute");
        };
    MorningControlScope.VerifiedEpochWork<MorningCompletionEvidence> complete =
        (state, database, generation, original, stop, publication) -> {
          called.incrementAndGet();
          throw new AssertionError("completion work must not execute");
        };
    var budget = dev.codex.schubert.nk.batch.platform.MorningParentBudget.create();
    UUID run = UUID.fromString("00000000-0000-4000-8000-000000003366");
    List<org.junit.jupiter.api.function.Executable> rejected =
        List.of(
            () -> MorningControlScope.execute(null),
            () -> MorningControlScope.executeOwned(null),
            () -> MorningControlScope.executeOwnedEpoch(null),
            () -> MorningControlScope.executeResume(null, work),
            () -> MorningControlScope.executeResume(run, null),
            () -> MorningControlScope.executeResumeOwned(null, owned),
            () -> MorningControlScope.executeResumeOwned(run, null),
            () -> MorningControlScope.executeResumeOwnedEpoch(null, epoch),
            () -> MorningControlScope.executeResumeOwnedEpoch(run, null),
            () -> MorningControlScope.executeVerifiedEpoch(null, verified),
            () -> MorningControlScope.executeVerifiedEpoch(budget, null),
            () -> MorningControlScope.executeResumeVerifiedEpoch(null, run, verified),
            () -> MorningControlScope.executeResumeVerifiedEpoch(budget, null, verified),
            () -> MorningControlScope.executeResumeVerifiedEpoch(budget, run, null),
            () -> MorningControlScope.executeCompletedEpoch(null, Optional.empty(), complete),
            () -> MorningControlScope.executeCompletedEpoch(budget, null, complete),
            () -> MorningControlScope.executeCompletedEpoch(budget, Optional.empty(), null));
    for (var action : rejected) {
      assertThrows(NullPointerException.class, action);
      assertEquals(0, called.get());
    }
  }

  private static final class HeldM implements MorningControlScope.Exclusive {
    final List<String> events;
    final AtomicBoolean held = new AtomicBoolean();
    boolean available = true;

    HeldM(List<String> events) {
      this.events = events;
    }

    @Override
    public <T> Optional<T> execute(LinuxFileLock.Operation<T> operation) throws IOException {
      events.add("M-enter");
      if (!available) return Optional.empty();
      held.set(true);
      try {
        return Optional.of(operation.execute());
      } finally {
        held.set(false);
        events.add("M-close");
      }
    }
  }

  private static final class HeldA implements MorningControlScope.StartupExclusive {
    final List<String> events;
    final AtomicBoolean held = new AtomicBoolean();
    boolean available = true;

    HeldA(List<String> events) {
      this.events = events;
    }

    @Override
    public <T> Optional<T> execute(LinuxFileLock.StartupOperation<T> operation) throws IOException {
      events.add("A-enter");
      if (!available) return Optional.empty();
      held.set(true);
      try {
        return Optional.of(operation.execute(128));
      } finally {
        held.set(false);
        events.add("A-close");
      }
    }
  }

  @Test
  void mctrl014ResidualIntentRefusesBeforeOriginalUnderM() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    MorningControlScope.OwnedOriginal original =
        new MorningControlScope.OwnedOriginal() {
          @Override
          public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> ignored)
              throws IOException {
            assertTrue(m.held.get());
            events.add("original");
            throw new IOException("test-only original");
          }
        };
    var blocked =
        MorningControlScope.withClearIntent(
            original,
            () -> {
              assertTrue(m.held.get());
              events.add("intent-reject");
              throw new IOException("test-only residual intent");
            });
    assertThrows(
        IOException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {},
                m,
                blocked,
                () -> fail("no stop"),
                new HeldA(events),
                () -> fail("no terminal"),
                state -> fail("no invalidation"),
                (state, database) -> fail("no work")));
    assertEquals(List.of("M-enter", "intent-reject", "M-close"), events);

    events.clear();
    var clear =
        MorningControlScope.withClearIntent(
            original,
            () -> {
              assertTrue(m.held.get());
              events.add("intent-clear");
            });
    assertThrows(
        IOException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {},
                m,
                clear,
                () -> fail("no stop"),
                new HeldA(events),
                () -> fail("no terminal"),
                state -> fail("no invalidation"),
                (state, database) -> fail("no work")));
    assertEquals(List.of("M-enter", "intent-clear", "original", "M-close"), events);
    assertThrows(
        NullPointerException.class, () -> MorningControlScope.withClearIntent(null, () -> {}));
    assertThrows(
        NullPointerException.class, () -> MorningControlScope.withClearIntent(original, null));
  }

  @Test
  void mctrl001StopsUnderMThenFreshObservesInsideA() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    int result =
        MorningControlScope.execute(
            () -> events.add("root"),
            m,
            () -> {
              assertTrue(m.held.get());
              assertFalse(a.held.get());
              events.add("stop-eight");
            },
            a,
            () -> {
              assertTrue(m.held.get());
              assertTrue(a.held.get());
              events.add("fresh-eight");
            },
            () -> {
              assertTrue(m.held.get());
              assertTrue(a.held.get());
              events.add("trusted-work");
              return 7;
            });
    assertEquals(7, result);
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "fresh-eight",
            "root",
            "trusted-work",
            "root",
            "A-close",
            "root",
            "M-close",
            "root"),
        events);
    assertFalse(m.held.get());
    assertFalse(a.held.get());
  }

  @Test
  void mctrl002BusyMStartsNoStopOrA() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    m.available = false;
    assertEquals(
        "Morning control scope unavailable",
        assertThrows(
                IOException.class,
                () ->
                    MorningControlScope.execute(
                        () -> events.add("root"),
                        m,
                        () -> fail("no stop"),
                        new HeldA(events),
                        () -> fail("no terminals"),
                        () -> fail("no work")))
            .getMessage());
    assertEquals(List.of("root", "M-enter"), events);
  }

  @Test
  void mctrl003StopRefusalNeverAcquiresAAndClosesM() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var failure = new IOException("public stop refused");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.execute(
                    () -> events.add("root"),
                    m,
                    () -> {
                      assertTrue(m.held.get());
                      throw failure;
                    },
                    new HeldA(events),
                    () -> fail("no terminals"),
                    () -> fail("no work"))));
    assertEquals(List.of("root", "M-enter", "root", "M-close"), events);
    assertFalse(m.held.get());
  }

  @Test
  void mctrl004BusyAAfterStopStartsNoWork() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    a.available = false;
    assertEquals(
        "Morning control scope unavailable",
        assertThrows(
                IOException.class,
                () ->
                    MorningControlScope.execute(
                        () -> events.add("root"),
                        m,
                        () -> events.add("stop-eight"),
                        a,
                        () -> fail("no A terminal observation"),
                        () -> fail("no work")))
            .getMessage());
    assertEquals(
        List.of("root", "M-enter", "root", "stop-eight", "root", "A-enter", "M-close"), events);
    assertFalse(m.held.get());
    assertFalse(a.held.get());
  }

  @Test
  void mctrl005PostARecheckFailurePreventsWorkAndClosesBoth() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var failure = new IOException("public fresh terminal failed");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.execute(
                    () -> events.add("root"),
                    m,
                    () -> events.add("stop-eight"),
                    a,
                    () -> {
                      assertTrue(m.held.get() && a.held.get());
                      throw failure;
                    },
                    () -> fail("no change before fresh eight"))));
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "A-close",
            "M-close"),
        events);
  }

  @Test
  void mctrl006WorkFailureAndNullContractsDoNotBecomeSuccess() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var failure = new IllegalStateException("public work failure");
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class,
            () ->
                MorningControlScope.execute(
                    () -> {},
                    m,
                    () -> {},
                    a,
                    () -> {},
                    () -> {
                      throw failure;
                    })));
    assertFalse(m.held.get());
    assertFalse(a.held.get());
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.execute(() -> {}, m, () -> {}, a, () -> {}, () -> null));
    assertThrows(NullPointerException.class, () -> MorningControlScope.execute(null));
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.execute(() -> {}, m, () -> {}, a, () -> {}, null));
    assertThrows(
        NullPointerException.class,
        () -> MorningControlScope.execute(null, m, () -> {}, a, () -> {}, () -> true));
  }

  @Test
  void mctrl007UnresolvedStopKeepsMAndNeverAcquiresA() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    try (var workers = Executors.newSingleThreadExecutor()) {
      var result =
          workers.submit(
              () ->
                  MorningControlScope.execute(
                      () -> {},
                      m,
                      () -> {
                        entered.countDown();
                        try {
                          assertTrue(release.await(2, TimeUnit.SECONDS));
                        } catch (InterruptedException interrupted) {
                          Thread.currentThread().interrupt();
                          throw new IOException("test stop interrupted");
                        }
                      },
                      a,
                      () -> {},
                      () -> true));
      try {
        assertTrue(entered.await(2, TimeUnit.SECONDS));
        assertTrue(m.held.get());
        assertFalse(a.held.get());
        assertFalse(result.isDone());
      } finally {
        release.countDown();
      }
      assertTrue(result.get(2, TimeUnit.SECONDS));
      assertFalse(m.held.get());
      assertFalse(a.held.get());
    }
  }

  @Test
  void mctrl008NewOriginalAndDbStayHeldAcrossStopAAndWork() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var originalHeld = new AtomicBoolean();
    var run =
        new BatchRun(
            UUID.fromString("00000000-0000-0000-0000-000000000341"),
            Instant.parse("2026-09-28T05:00:00Z"));
    var state =
        new MaintenanceRunState(
            new MaintenanceActivation(run, UUID.fromString("00000000-0000-0000-0000-000000000342")),
            Optional.empty());
    MorningControlScope.Original original =
        new MorningControlScope.Original() {
          @Override
          public <T> T execute(MorningNewRunAdmission.Continuation<T> continuation)
              throws IOException {
            assertTrue(m.held.get());
            events.add("DB-original-enter");
            originalHeld.set(true);
            try {
              return continuation.execute(state);
            } finally {
              originalHeld.set(false);
              events.add("DB-original-close");
            }
          }
        };
    int value =
        MorningControlScope.execute(
            () -> events.add("root"),
            m,
            original,
            () -> {
              assertTrue(m.held.get());
              assertTrue(originalHeld.get());
              assertFalse(a.held.get());
              events.add("stop-eight");
            },
            a,
            () -> {
              assertTrue(originalHeld.get());
              events.add("fresh-eight");
            },
            observed -> {
              assertSame(state, observed);
              assertTrue(m.held.get());
              assertTrue(a.held.get());
              assertTrue(originalHeld.get());
              events.add("same-run-work");
              return 7;
            });
    assertEquals(7, value);
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "DB-original-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "fresh-eight",
            "root",
            "same-run-work",
            "root",
            "A-close",
            "DB-original-close",
            "root",
            "M-close",
            "root"),
        events);
    assertFalse(originalHeld.get());
  }

  @Test
  void mctrl009OriginalFailureIssuesNoStopOrA() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var failure = new IOException("DB reference unavailable");
    MorningControlScope.Original original =
        new MorningControlScope.Original() {
          @Override
          public <T> T execute(MorningNewRunAdmission.Continuation<T> continuation)
              throws IOException {
            assertTrue(m.held.get());
            events.add("DB-reference-refused");
            throw failure;
          }
        };
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.execute(
                    () -> events.add("root"),
                    m,
                    original,
                    () -> fail("no stop"),
                    a,
                    () -> fail("no fresh"),
                    state -> fail("no work"))));
    assertEquals(List.of("root", "M-enter", "root", "DB-reference-refused", "M-close"), events);
    assertFalse(m.held.get());
    assertFalse(a.held.get());
  }

  @Test
  void mctrl010InvalidatesOnlyAfterFreshEightAndBeforeTrustedWork() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var run =
        new BatchRun(
            UUID.fromString("00000000-0000-0000-0000-000000000344"),
            Instant.parse("2026-09-28T05:00:00Z"));
    var state =
        new MaintenanceRunState(
            new MaintenanceActivation(run, UUID.fromString("00000000-0000-0000-0000-000000000345")),
            Optional.empty());
    MorningControlScope.Original original =
        new MorningControlScope.Original() {
          @Override
          public <T> T execute(MorningNewRunAdmission.Continuation<T> continuation)
              throws IOException {
            events.add("original-enter");
            try {
              return continuation.execute(state);
            } finally {
              events.add("original-close");
            }
          }
        };
    int value =
        MorningControlScope.execute(
            () -> events.add("root"),
            m,
            original,
            () -> events.add("stop-eight"),
            a,
            () -> events.add("fresh-eight"),
            observed -> {
              assertSame(state, observed);
              assertTrue(m.held.get() && a.held.get());
              events.add("INVALID");
            },
            observed -> {
              assertSame(state, observed);
              assertTrue(m.held.get() && a.held.get());
              events.add("trusted-work");
              return 7;
            });
    assertEquals(7, value);
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "original-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "fresh-eight",
            "root",
            "INVALID",
            "trusted-work",
            "root",
            "A-close",
            "original-close",
            "root",
            "M-close",
            "root"),
        events);
  }

  @Test
  void mctrl011InvalidationFailureDoesNotRunDownstreamWork() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var run =
        new BatchRun(
            UUID.fromString("00000000-0000-0000-0000-000000000344"),
            Instant.parse("2026-09-28T05:00:00Z"));
    var state =
        new MaintenanceRunState(
            new MaintenanceActivation(run, UUID.fromString("00000000-0000-0000-0000-000000000345")),
            Optional.empty());
    var failure = new IOException("current write unavailable");
    MorningControlScope.Original original =
        new MorningControlScope.Original() {
          @Override
          public <T> T execute(MorningNewRunAdmission.Continuation<T> continuation)
              throws IOException {
            return continuation.execute(state);
          }
        };
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningControlScope.execute(
                    () -> events.add("root"),
                    m,
                    original,
                    () -> events.add("stop-eight"),
                    a,
                    () -> events.add("fresh-eight"),
                    observed -> {
                      events.add("INVALID-fail");
                      throw failure;
                    },
                    observed -> fail("no trusted work after failed INVALID"))));
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "fresh-eight",
            "root",
            "INVALID-fail",
            "A-close",
            "M-close"),
        events);
    assertFalse(m.held.get());
    assertFalse(a.held.get());
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.execute(
                () -> {}, m, original, () -> {}, a, () -> {}, null, state1 -> 7));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.execute(
                () -> {}, m, original, () -> {}, a, () -> {}, observed -> {}, null));
  }

  @Test
  void mctrl012OwnedDatabaseReachesPostInvalidationWorkWithinAllOwners() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var dbHeld = new AtomicBoolean();
    var run =
        new BatchRun(
            UUID.fromString("00000000-0000-0000-0000-000000000346"),
            Instant.parse("2026-09-28T05:00:00Z"));
    var state =
        new MaintenanceRunState(
            new MaintenanceActivation(run, UUID.fromString("00000000-0000-0000-0000-000000000347")),
            Optional.empty());
    MorningControlScope.OwnedOriginal original =
        new MorningControlScope.OwnedOriginal() {
          @Override
          public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation)
              throws IOException {
            assertTrue(m.held.get());
            dbHeld.set(true);
            events.add("DB-original-enter");
            try {
              return continuation.execute(
                  state,
                  new MorningDatabaseSession.Access() {
                    public void requireUnused(BatchRun selected) {
                      fail("reference admission precedes this callback");
                    }

                    public void requireConsistent(BatchRun selected) {
                      fail("reference admission precedes this callback");
                    }

                    public MorningDatabaseSession.BackupBegins beginBackup(
                        BatchRun selected, Instant now, boolean recoverAbandoned) {
                      assertTrue(m.held.get() && a.held.get() && dbHeld.get());
                      assertEquals(run, selected);
                      assertEquals(run.cutoff(), now);
                      assertFalse(recoverAbandoned);
                      events.add("backup-begin");
                      return new MorningDatabaseSession.BackupBegins(
                          new BatchStepAttempt(1, run, BatchStep.BACKUP_DB, 1, now, false),
                          new BatchStepAttempt(2, run, BatchStep.BACKUP_CONFIG, 1, now, false));
                    }

                    public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
                      return fail("cleanup outside this test");
                    }
                  });
            } finally {
              dbHeld.set(false);
              events.add("DB-original-close");
            }
          }
        };
    int value =
        MorningControlScope.executeOwned(
            () -> events.add("root"),
            m,
            original,
            () -> events.add("stop-eight"),
            a,
            () -> events.add("fresh-eight"),
            observed -> {
              assertSame(state, observed);
              events.add("INVALID");
            },
            (observed, database) -> {
              assertSame(state, observed);
              var begins = database.beginBackup(run, run.cutoff(), false);
              assertEquals(BatchStep.BACKUP_DB, begins.database().step());
              return 7;
            });
    assertEquals(7, value);
    assertTrue(events.indexOf("stop-eight") < events.indexOf("fresh-eight"));
    assertTrue(events.indexOf("fresh-eight") < events.indexOf("INVALID"));
    assertTrue(events.indexOf("INVALID") < events.indexOf("backup-begin"));
    assertTrue(events.indexOf("backup-begin") < events.indexOf("DB-original-close"));
    assertFalse(m.held.get() || a.held.get() || dbHeld.get());
  }

  @Test
  void mctrl013OwnedNullContractsRejectBeforeMaintenanceLock() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    MorningControlScope.OwnedOriginal original =
        new MorningControlScope.OwnedOriginal() {
          @Override
          public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> continuation) {
            return fail("no original should open");
          }
        };
    MorningControlScope.StopPass stop = () -> fail("no stop");
    MorningControlScope.Terminals terminals = () -> fail("no terminals");
    MorningControlScope.Invalidation invalidation = state -> fail("no invalidation");
    MorningNewRunAdmission.OwnedContinuation<Boolean> work = (state, db) -> true;
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {}, m, null, stop, a, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {}, m, original, null, a, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {}, m, original, stop, null, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {}, m, original, stop, a, null, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {}, m, original, stop, a, terminals, null, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwned(
                () -> {}, m, original, stop, a, terminals, invalidation, null));
    assertTrue(events.isEmpty());
  }

  private static MaintenanceRunState epochState() {
    var run =
        new BatchRun(
            UUID.fromString("00000000-0000-0000-0000-000000000378"),
            Instant.parse("2026-09-29T05:00:00Z"));
    return new MaintenanceRunState(
        new MaintenanceActivation(run, UUID.fromString("00000000-0000-0000-0000-000000000379")),
        Optional.empty());
  }

  private static Epoch invalidEpoch(MaintenanceRunState state) {
    return new Epoch(
        State.INVALID,
        UUID.fromString("00000000-0000-0000-0000-000000000380"),
        UUID.fromString("00000000-0000-0000-0000-000000000381"),
        state.activation(),
        Optional.empty());
  }

  private static MorningDatabaseSession.Access epochDatabase() {
    return new MorningDatabaseSession.Access() {
      public void requireUnused(BatchRun selected) {
        fail("no unused check after original");
      }

      public void requireConsistent(BatchRun selected) {
        fail("no consistency check after original");
      }

      public MorningDatabaseSession.BackupBegins beginBackup(
          BatchRun selected, Instant now, boolean recoverAbandoned) {
        return fail("no backup start in epoch handoff");
      }

      public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> work) {
        return fail("no cleanup in epoch handoff");
      }
    };
  }

  private static MorningControlScope.OwnedOriginal epochOriginal(
      List<String> events,
      HeldM m,
      HeldA a,
      AtomicBoolean dbHeld,
      MaintenanceRunState state,
      MorningDatabaseSession.Access database) {
    return new MorningControlScope.OwnedOriginal() {
      @Override
      public <T> T execute(MorningNewRunAdmission.OwnedContinuation<T> work) throws IOException {
        assertTrue(m.held.get());
        assertFalse(a.held.get());
        dbHeld.set(true);
        events.add("original-enter");
        try {
          return work.execute(state, database);
        } finally {
          dbHeld.set(false);
          events.add("original-close");
        }
      }
    };
  }

  @Test
  void mctrl015BorrowedInvalidEpochIsSameObjectInsideAllOwners() throws Exception {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var dbHeld = new AtomicBoolean();
    var state = epochState();
    var database = epochDatabase();
    var epoch = invalidEpoch(state);
    int result =
        MorningControlScope.executeOwnedEpoch(
            () -> events.add("root"),
            m,
            epochOriginal(events, m, a, dbHeld, state, database),
            () -> events.add("stop-eight"),
            a,
            () -> events.add("fresh-eight"),
            observed -> {
              assertSame(state, observed);
              events.add("INVALID");
              return epoch;
            },
            (observed, borrowedDatabase, borrowedEpoch) -> {
              assertTrue(m.held.get() && a.held.get() && dbHeld.get());
              assertSame(state, observed);
              assertSame(database, borrowedDatabase);
              assertSame(epoch, borrowedEpoch);
              assertEquals(State.INVALID, borrowedEpoch.state());
              assertTrue(borrowedEpoch.permitDigest().isEmpty());
              events.add("work");
              return 7;
            });
    assertEquals(7, result);
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "original-enter",
            "root",
            "stop-eight",
            "root",
            "A-enter",
            "root",
            "fresh-eight",
            "root",
            "INVALID",
            "work",
            "root",
            "A-close",
            "original-close",
            "root",
            "M-close",
            "root"),
        events);
    assertFalse(m.held.get() || a.held.get() || dbHeld.get());
  }

  @Test
  void mctrl016InvalidationFailureOrNullNeverCallsWork() {
    for (boolean nullResult : new boolean[] {false, true}) {
      var events = new ArrayList<String>();
      var m = new HeldM(events);
      var a = new HeldA(events);
      var dbHeld = new AtomicBoolean();
      var state = epochState();
      var failure = new IOException("fixed INVALID refusal");
      MorningControlScope.EpochInvalidation invalidation =
          observed -> {
            assertSame(state, observed);
            events.add("INVALID-refused");
            if (nullResult) return null;
            throw failure;
          };
      if (nullResult) {
        assertThrows(
            NullPointerException.class,
            () ->
                MorningControlScope.executeOwnedEpoch(
                    () -> {},
                    m,
                    epochOriginal(events, m, a, dbHeld, state, epochDatabase()),
                    () -> {},
                    a,
                    () -> {},
                    invalidation,
                    (s, d, e) -> fail("no work")));
      } else {
        assertSame(
            failure,
            assertThrows(
                IOException.class,
                () ->
                    MorningControlScope.executeOwnedEpoch(
                        () -> {},
                        m,
                        epochOriginal(events, m, a, dbHeld, state, epochDatabase()),
                        () -> {},
                        a,
                        () -> {},
                        invalidation,
                        (s, d, e) -> fail("no work"))));
      }
      assertEquals(1, events.stream().filter("A-close"::equals).count());
      assertEquals(1, events.stream().filter("original-close"::equals).count());
      assertEquals(1, events.stream().filter("M-close"::equals).count());
      assertFalse(m.held.get() || a.held.get() || dbHeld.get());
    }
  }

  @Test
  void mctrl017WrongOrIssuedEpochCannotBecomeBorrowedAuthority() {
    var state = epochState();
    var other =
        new MaintenanceActivation(
            state.activation().run(), UUID.fromString("00000000-0000-0000-0000-000000000382"));
    var invalid = invalidEpoch(state);
    var wrong = new Epoch(State.INVALID, invalid.boot(), invalid.epoch(), other, Optional.empty());
    var issued = invalid.issued("a".repeat(64));
    for (Epoch candidate : List.of(wrong, issued)) {
      var events = new ArrayList<String>();
      var m = new HeldM(events);
      var a = new HeldA(events);
      var dbHeld = new AtomicBoolean();
      assertThrows(
          IOException.class,
          () ->
              MorningControlScope.executeOwnedEpoch(
                  () -> {},
                  m,
                  epochOriginal(events, m, a, dbHeld, state, epochDatabase()),
                  () -> {},
                  a,
                  () -> {},
                  s -> candidate,
                  (s, d, e) -> fail("no work")));
      assertEquals(1, events.stream().filter("A-close"::equals).count());
      assertEquals(1, events.stream().filter("original-close"::equals).count());
      assertEquals(1, events.stream().filter("M-close"::equals).count());
      assertFalse(m.held.get() || a.held.get() || dbHeld.get());
    }
  }

  @Test
  void mctrl018NullDependenciesAndWorkResultFailClosed() {
    var events = new ArrayList<String>();
    var m = new HeldM(events);
    var a = new HeldA(events);
    var dbHeld = new AtomicBoolean();
    var state = epochState();
    var original = epochOriginal(events, m, a, dbHeld, state, epochDatabase());
    MorningControlScope.StopPass stop = () -> {};
    MorningControlScope.Terminals terminals = () -> {};
    MorningControlScope.EpochInvalidation invalidation = s -> invalidEpoch(state);
    MorningControlScope.OwnedEpochWork<Boolean> work = (s, d, e) -> true;
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                null, m, original, stop, a, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, null, original, stop, a, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, null, stop, a, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, original, null, a, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, original, stop, null, terminals, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, original, stop, a, null, invalidation, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, original, stop, a, terminals, null, work));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, original, stop, a, terminals, invalidation, null));
    assertTrue(events.isEmpty());
    assertThrows(
        NullPointerException.class,
        () ->
            MorningControlScope.executeOwnedEpoch(
                () -> {}, m, original, stop, a, terminals, invalidation, (s, d, e) -> null));
    assertEquals(1, events.stream().filter("A-close"::equals).count());
    assertEquals(1, events.stream().filter("original-close"::equals).count());
    assertEquals(1, events.stream().filter("M-close"::equals).count());
    assertFalse(m.held.get() || a.held.get() || dbHeld.get());
  }
}
