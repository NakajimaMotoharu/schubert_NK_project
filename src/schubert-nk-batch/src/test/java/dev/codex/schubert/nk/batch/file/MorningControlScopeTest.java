package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

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

/** NK-OPS-001/OPS009/UI251/SS341/343/SSC089/094/105/106; PT-OPS-MCTRL001-014. */
final class MorningControlScopeTest {
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
}
