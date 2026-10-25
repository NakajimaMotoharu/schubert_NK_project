package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/**
 * PG363/365/366; PT-OPS-BUCYCLE-001..006. Synthetic ports never claim real worker/archive
 * admission.
 */
final class MorningBackupUnitCycleTest {
  /** SS343/SSC136/PT-OPS-BUCYCLE3244001: completed proof is read-only, never a new start. */
  @Test
  void bucycle3244001CompletedBackupRequiresSameBaselineReceiptAndQuiescentTerminal()
      throws Exception {
    for (String fault :
        List.of("NONE", "OTHER_INVOCATION", "NOT_QUIESCENT", "MISSING_BASELINE", "MISSING_TYPED")) {
      var actual = ExpiryReceiptFixture.backupReceipt(0);
      var fixture = new Cycle3244(BackupUnitStartClient.Target.BACKUP, actual, false);
      var cycle = fixture.subject();
      assertThrows(IOException.class, cycle::completedReceipt);
      assertThrows(IOException.class, cycle::recheckCompletedBackup);
      assertEquals(0, fixture.starts);
      assertEquals(0, fixture.stops);
      assertEquals(0, fixture.start.retire);
      if (fault.equals("MISSING_TYPED")) {
        fixture.delivered = Optional.empty();
        assertThrows(
            Retained.class,
            () -> cycle.executeObserved(fixture::originalProof, fixture::completed));
        assertEquals(1, fixture.starts);
        assertEquals(1, fixture.stops);
        assertEquals(0, fixture.completions);
        assertEquals(0, fixture.proofs);
        assertEquals(0, fixture.start.retire);
        assertTrue(fixture.retains > 0);
        continue;
      }
      if (fault.equals("MISSING_BASELINE")) {
        assertEquals(
            MorningBackupUnitCycle.Outcome.SUCCESS,
            cycle.execute(
                fixture::originalProof,
                result -> {
                  assertEquals(MorningBackupUnitCycle.Outcome.SUCCESS, result);
                  fixture.completions++;
                }));
      } else {
        assertEquals(
            MorningBackupUnitCycle.Outcome.SUCCESS,
            cycle.executeObserved(fixture::originalProof, fixture::completed));
      }
      assertSame(actual, cycle.completedReceipt());
      if (fault.equals("OTHER_INVOCATION"))
        fixture.stopped = ExpiryReceiptFixture.backupReceipt(0, "8".repeat(32));
      if (fault.equals("NOT_QUIESCENT")) fixture.quiet = false;
      if (fault.equals("NONE")) {
        cycle.recheckCompletedBackup();
        cycle.recheckCompletedBackup();
        assertThrows(Retained.class, cycle::retainUnresolvedOwner);
        assertEquals(1, fixture.retains);
      } else {
        var refused = assertThrows(IOException.class, cycle::recheckCompletedBackup);
        assertNull(refused.getCause());
        assertEquals(0, fixture.retains);
      }
      assertEquals(1, fixture.captures);
      assertEquals(1, fixture.starts);
      assertEquals(1, fixture.stops);
      assertEquals(1, fixture.completions);
      assertEquals(1, fixture.proofs);
      assertEquals(1, fixture.start.retire);
    }
  }

  /** SS343/PT-OPS-BUCYCLE3244002: a retained child cannot mint a successful parent proof. */
  @Test
  void bucycle3244002ClosedPhaseAndTypedFailedHandoffKeepCompletionAfterReacquire()
      throws Exception {
    for (var target : BackupUnitStartClient.Target.values()) {
      var fixture = new Cycle3244(target, ExpiryReceiptFixture.backupReceipt(0), false);
      var cycle = fixture.subject();
      if (target != BackupUnitStartClient.Target.BACKUP)
        assertThrows(IOException.class, () -> cycle.execute(fixture::originalProof));
      if (target != BackupUnitStartClient.Target.INSPECTOR)
        assertThrows(
            IOException.class,
            () ->
                cycle.executeInspectorHandoff(
                    work -> fail("wrong phase cannot borrow"),
                    receipt -> fail("wrong phase cannot complete"),
                    fixture::originalProof));
      if (target == BackupUnitStartClient.Target.BACKUP
          || target == BackupUnitStartClient.Target.INSPECTOR
          || target == BackupUnitStartClient.Target.BROKER)
        assertThrows(
            IOException.class,
            () ->
                cycle.executeHandoff(
                    work -> fail("wrong phase cannot start"),
                    receipt -> fail("wrong phase cannot complete"),
                    fixture::originalProof));
      assertEquals(0, fixture.starts);
      assertEquals(0, fixture.captures);
      assertEquals(0, fixture.proofs);
      assertEquals(0, fixture.start.retire);
    }
    for (var target :
        List.of(BackupUnitStartClient.Target.CLEANUP, BackupUnitStartClient.Target.EXPIRY)) {
      for (String fault : List.of("NONE", "NULL", "FOREIGN", "DOUBLE", "WRONG_PHASE_RECEIPT")) {
        var actual =
            target == BackupUnitStartClient.Target.CLEANUP
                ? ExpiryReceiptFixture.cleanupReceipt(30)
                : ExpiryReceiptFixture.receipt(30);
        var fixture = new Cycle3244(target, actual, true);
        var cycle = fixture.subject();
        if (fault.equals("WRONG_PHASE_RECEIPT"))
          fixture.delivered = Optional.of(ExpiryReceiptFixture.backupReceipt(0));
        MorningBackupUnitCycle.Handoff handoff =
            work -> {
              fixture.borrowed = true;
              fixture.events.add("borrow");
              try {
                var result = work.execute();
                if (fault.equals("DOUBLE")) return work.execute();
                if (fault.equals("NULL")) return null;
                if (fault.equals("FOREIGN")) return ExpiryReceiptFixture.backupReceipt(0);
                return result;
              } catch (IOException | RuntimeException | Error failed) {
                throw failed;
              } catch (Exception invalidFixture) {
                throw new AssertionError(invalidFixture);
              } finally {
                fixture.borrowed = false;
                fixture.events.add("reacquire");
              }
            };
        MorningBackupUnitCycle.ObservedCompletion complete =
            observed -> {
              assertFalse(fixture.borrowed);
              assertSame(actual, observed);
              assertEquals(30, observed.exitCode());
              fixture.completions++;
              fixture.events.add("completion");
            };
        if (fault.equals("NONE")) {
          assertSame(actual, cycle.executeHandoff(handoff, complete, fixture::originalProof));
          assertSame(actual, cycle.completedReceipt());
          assertEquals(1, fixture.completions);
          assertEquals(1, fixture.proofs);
          assertEquals(1, fixture.start.retire);
          assertEquals(
              List.of("borrow", "start", "reacquire", "completion", "original"), fixture.events);
        } else {
          assertThrows(
              Retained.class,
              () -> cycle.executeHandoff(handoff, complete, fixture::originalProof));
          assertEquals(0, fixture.completions);
          assertEquals(0, fixture.proofs);
          assertEquals(0, fixture.start.retire);
          assertTrue(fixture.retains > 0);
        }
        assertEquals(1, fixture.starts);
        assertEquals(0, fixture.stops);
      }
    }
  }

  /** Independent finite port/counter oracle; no native authority or expected-from-subject. */
  private static final class Cycle3244 {
    final BackupUnitStartClient.Target target;
    final BackupUnitReceiptGate.TerminalReceipt actual;
    final boolean failed;
    final Object baseline = new Object();
    final StartAttempt start = new StartAttempt();
    final List<String> events = new ArrayList<>();
    BackupUnitReceiptGate.TerminalReceipt stopped;
    Optional<BackupUnitReceiptGate.TerminalReceipt> delivered;
    boolean quiet = true;
    boolean borrowed;
    int captures;
    int starts;
    int stops;
    int completions;
    int proofs;
    int retains;

    Cycle3244(
        BackupUnitStartClient.Target target,
        BackupUnitReceiptGate.TerminalReceipt actual,
        boolean failed) {
      this.target = target;
      this.actual = actual;
      this.stopped = actual;
      this.delivered = Optional.of(actual);
      this.failed = failed;
    }

    void originalProof() {
      assertFalse(borrowed);
      proofs++;
      events.add("original");
    }

    void completed(
        MorningBackupUnitCycle.Outcome outcome, BackupUnitReceiptGate.TerminalReceipt observed) {
      assertEquals(MorningBackupUnitCycle.Outcome.SUCCESS, outcome);
      assertSame(actual, observed);
      completions++;
    }

    MorningBackupUnitCycle subject() {
      return new MorningBackupUnitCycle(
          () -> {},
          new MorningBackupUnitCycle.Receipt() {
            public Object capture() {
              captures++;
              return baseline;
            }

            public boolean freshZero(Object observed) {
              assertSame(baseline, observed);
              return !failed;
            }

            public Optional<MorningBackupUnitCycle.Outcome> terminal(Object observed) {
              assertSame(baseline, observed);
              return Optional.of(
                  failed
                      ? MorningBackupUnitCycle.Outcome.FAILED
                      : MorningBackupUnitCycle.Outcome.SUCCESS);
            }

            public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object observed) {
              assertSame(baseline, observed);
              return delivered;
            }

            public BackupUnitReceiptGate.TerminalReceipt stopped(
                Object observed, BackupUnitReceiptGate.TerminalReceipt before) {
              assertSame(baseline, observed);
              assertSame(actual, before);
              return stopped;
            }

            public void requirePresent(BackupUnitReceiptGate.TerminalReceipt observed)
                throws IOException {
              if (observed != actual) throw new IOException("fixture typed identity changed");
            }
          },
          () -> {
            starts++;
            events.add("start");
            return start;
          },
          () -> {
            stops++;
            return new StopAttempt();
          },
          () -> quiet,
          () -> fail("finite fixture must not wait"),
          () -> {
            retains++;
            throw new Retained();
          },
          budget(),
          target);
    }
  }

  @Test
  void isscomp010ChangedStoppedProofBeforeRetirementRetainsOwnership() throws Exception {
    var actual = ExpiryReceiptFixture.backupReceipt(0);
    var changed = ExpiryReceiptFixture.backupReceipt(0, "8".repeat(32));
    var checks = new java.util.concurrent.atomic.AtomicInteger();
    var completed = new java.util.concurrent.atomic.AtomicInteger();
    var start = new StartAttempt();
    var cycle =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                return "baseline";
              }

              public boolean freshZero(Object baseline) {
                return true;
              }

              public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object baseline) {
                return Optional.of(actual);
              }

              public BackupUnitReceiptGate.TerminalReceipt stopped(
                  Object baseline, BackupUnitReceiptGate.TerminalReceipt before) {
                assertSame(actual, before);
                return checks.incrementAndGet() == 1 ? actual : changed;
              }
            },
            () -> start,
            StopAttempt::new,
            () -> true,
            () -> fail("no wait"),
            () -> {
              throw new Retained();
            },
            budget());
    assertThrows(
        Retained.class,
        () ->
            cycle.executeObserved(
                () -> fail("changed proof cannot retire"),
                (outcome, receipt) -> {
                  assertSame(actual, receipt);
                  completed.incrementAndGet();
                }));
    assertEquals(1, completed.get());
    assertEquals(2, checks.get());
    assertEquals(0, start.retire);
  }

  @Test
  void isscomp008ActualGcAfterExplicitStopDoesNotEraseTheObservedResult() throws Exception {
    for (int code : List.of(0, 30)) {
      String cold =
          "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
      var wire = new java.util.concurrent.atomic.AtomicReference<>(cold);
      var state =
          new java.util.concurrent.atomic.AtomicReference<>(
              InspectorUnitSnapshot.parse(
                  cold.getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                  InspectorUnitSnapshot.Target.BACKUP));
      var gate =
          new BackupUnitReceiptGate(
              () -> {}, () -> Optional.of(state.get()), () -> Optional.of(state.get()));
      var start = new StartAttempt();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              new MorningBackupUnitCycle.Receipt() {
                public Object capture() throws IOException {
                  return gate.capture();
                }

                public boolean freshZero(Object b) {
                  throw new AssertionError();
                }

                public Optional<MorningBackupUnitCycle.Outcome> terminal(Object b) {
                  String actual =
                      cold.replace("InvocationID=\n", "InvocationID=" + "9".repeat(32) + "\n")
                          .replace("ExecMainCode=0", "ExecMainCode=1")
                          .replace("ExecMainStatus=0", "ExecMainStatus=" + code)
                          .replace(
                              "ExecMainStartTimestampMonotonic=0",
                              "ExecMainStartTimestampMonotonic=1000000")
                          .replace(
                              "ExecMainExitTimestampMonotonic=0",
                              "ExecMainExitTimestampMonotonic=2000000");
                  if (code != 0)
                    actual =
                        actual
                            .replace("ActiveState=inactive", "ActiveState=failed")
                            .replace("SubState=dead", "SubState=failed")
                            .replace("Result=success", "Result=exit-code");
                  wire.set(actual);
                  state.set(
                      InspectorUnitSnapshot.parse(
                          actual.getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                          InspectorUnitSnapshot.Target.BACKUP));
                  return Optional.of(
                      code == 0
                          ? MorningBackupUnitCycle.Outcome.SUCCESS
                          : MorningBackupUnitCycle.Outcome.FAILED);
                }

                public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object b)
                    throws IOException {
                  return gate.observeResult((BackupUnitReceiptGate.Baseline) b);
                }

                public BackupUnitReceiptGate.TerminalReceipt stopped(
                    Object b, BackupUnitReceiptGate.TerminalReceipt before) throws IOException {
                  gate.requireStoppedResult((BackupUnitReceiptGate.Baseline) b, before);
                  return before;
                }
              },
              () -> start,
              () -> {
                wire.set(cold);
                state.set(
                    InspectorUnitSnapshot.parse(
                        cold.getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                        InspectorUnitSnapshot.Target.BACKUP));
                return new StopAttempt();
              },
              () -> true,
              () -> fail("no wait"),
              () -> {
                throw new Retained();
              },
              budget());
      var calls = new java.util.concurrent.atomic.AtomicInteger();
      assertEquals(
          code == 0
              ? MorningBackupUnitCycle.Outcome.SUCCESS
              : MorningBackupUnitCycle.Outcome.FAILED,
          cycle.executeObserved(
              () -> {},
              (outcome, receipt) -> {
                assertEquals(code, receipt.exitCode());
                calls.incrementAndGet();
              }));
      assertEquals(1, calls.get());
      assertEquals(1, start.retire);
      assertEquals(code, cycle.completedReceipt().exitCode());
    }
  }

  @Test
  void isscomp006StoppedObservedReceiptReachesCompletionBeforeRetirement() throws Exception {
    for (int code : List.of(0, 30)) {
      var actual = ExpiryReceiptFixture.backupReceipt(code);
      var start = new StartAttempt();
      var events = new ArrayList<String>();
      var outcome =
          code == 0
              ? MorningBackupUnitCycle.Outcome.SUCCESS
              : MorningBackupUnitCycle.Outcome.FAILED;
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              new MorningBackupUnitCycle.Receipt() {
                public Object capture() {
                  return "actual-baseline";
                }

                public boolean freshZero(Object b) {
                  throw new AssertionError();
                }

                public Optional<MorningBackupUnitCycle.Outcome> terminal(Object b) {
                  return Optional.of(outcome);
                }

                public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object b) {
                  return Optional.of(actual);
                }

                public BackupUnitReceiptGate.TerminalReceipt stopped(
                    Object b, BackupUnitReceiptGate.TerminalReceipt before) {
                  assertEquals("actual-baseline", b);
                  assertSame(actual, before);
                  events.add("post-stop-actual");
                  return actual;
                }
              },
              () -> start,
              () -> {
                events.add("stop");
                return new StopAttempt();
              },
              () -> true,
              () -> fail("no wait"),
              () -> {
                throw new Retained();
              },
              budget());
      assertEquals(
          outcome,
          cycle.executeObserved(
              () -> events.add("retire-proof"),
              (value, receipt) -> {
                assertEquals(outcome, value);
                assertSame(actual, receipt);
                assertEquals(0, start.retire);
                events.add("parent-config");
              }));
      assertEquals(
          List.of("stop", "post-stop-actual", "parent-config", "post-stop-actual", "retire-proof"),
          events);
      assertSame(actual, cycle.completedReceipt());
      assertEquals(1, start.retire);
      cycle.recheckCompletedBackup();
      assertEquals("post-stop-actual", events.getLast());
      assertThrows(Retained.class, cycle::retainUnresolvedOwner);
      assertThrows(NullPointerException.class, () -> cycle.executeObserved(() -> {}, null));
    }
    for (boolean missing : List.of(true, false)) {
      var start = new StartAttempt();
      var actual = ExpiryReceiptFixture.backupReceipt(0);
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              new MorningBackupUnitCycle.Receipt() {
                public Object capture() {
                  return "baseline";
                }

                public boolean freshZero(Object b) {
                  return true;
                }

                public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object b) {
                  return missing ? Optional.empty() : Optional.of(actual);
                }
              },
              () -> start,
              StopAttempt::new,
              () -> true,
              () -> fail("no wait"),
              () -> {
                throw new Retained();
              },
              budget());
      assertThrows(
          Retained.class,
          () ->
              cycle.executeObserved(
                  () -> fail("no retire"),
                  (value, receipt) -> fail("missing actual stopped receipt")));
      assertEquals(0, start.retire);
    }
  }

  @Test
  void bucycle008KnownFailureCompletesBeforeProofAndMarkerRetirement() throws Exception {
    for (boolean completionFails : List.of(false, true)) {
      var events = new ArrayList<String>();
      var start = new StartAttempt();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              new MorningBackupUnitCycle.Receipt() {
                public Object capture() {
                  return "baseline";
                }

                public boolean freshZero(Object baseline) {
                  fail("typed observation required");
                  return false;
                }

                public Optional<MorningBackupUnitCycle.Outcome> terminal(Object baseline) {
                  assertEquals("baseline", baseline);
                  events.add("failed-receipt");
                  return Optional.of(MorningBackupUnitCycle.Outcome.FAILED);
                }
              },
              () -> start,
              () -> {
                events.add("stop");
                return new StopAttempt();
              },
              () -> {
                events.add("terminal");
                return true;
              },
              () -> fail("known terminal needs no wait"),
              () -> {
                events.add("retain");
                throw new Retained();
              },
              budget());
      MorningBackupUnitCycle.Completion completion =
          result -> {
            assertEquals(MorningBackupUnitCycle.Outcome.FAILED, result);
            assertEquals(0, start.retire);
            events.add("db-failed-request-retired");
            if (completionFails) throw new IOException("unknown commit");
          };
      if (completionFails) {
        assertThrows(Retained.class, () -> cycle.execute(() -> fail("no proof"), completion));
        assertEquals(0, start.retire);
        assertEquals(
            List.of("failed-receipt", "stop", "terminal", "db-failed-request-retired", "retain"),
            events);
      } else {
        assertEquals(
            MorningBackupUnitCycle.Outcome.FAILED,
            cycle.execute(() -> events.add("original-current"), completion));
        assertEquals(1, start.retire);
        assertEquals(
            List.of(
                "failed-receipt",
                "stop",
                "terminal",
                "db-failed-request-retired",
                "original-current",
                "terminal"),
            events);
      }
      assertThrows(NullPointerException.class, () -> cycle.execute(() -> {}, null));
    }
  }

  private static final class Retained extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }

  private static final class StartAttempt implements MorningBackupUnitCycle.StartAttempt {
    BackupUnitStartClient.Status status = BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
    int retire;
    int await;
    MorningBackupUnitCycle.ParentProof retirement = () -> {};

    public BackupUnitStartClient.Status status() {
      return status;
    }

    public BackupUnitStartClient.Status awaitClient() {
      await++;
      return status;
    }

    public void retireAfter(MorningBackupUnitCycle.ParentProof proof) throws IOException {
      retirement.verify();
      proof.verify();
      retire++;
    }
  }

  private static final class StopAttempt implements MorningBackupUnitCycle.StopAttempt {
    MaintenanceUnitStopClient.Status status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
    int await;

    public MaintenanceUnitStopClient.Status status() {
      return status;
    }

    public MaintenanceUnitStopClient.Status awaitClient() {
      await++;
      return status;
    }
  }

  @Test
  void bucycle001ExactParentOrderAndSingleRetirement() throws Exception {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    var stop = new StopAttempt();
    int[] observations = {0};
    var cycle =
        new MorningBackupUnitCycle(
            () -> events.add("root"),
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                events.add("baseline");
                return "pre-start";
              }

              public boolean freshZero(Object baseline) {
                assertEquals("pre-start", baseline);
                events.add("receipt");
                return ++observations[0] == 2;
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> {
              events.add("stop");
              return stop;
            },
            () -> {
              events.add("terminal");
              return true;
            },
            () -> events.add("wait"),
            () -> fail("known complete cycle must not be retained"),
            budget());
    cycle.execute(() -> events.add("original-request"));
    assertEquals(
        List.of(
            "root",
            "baseline",
            "root",
            "start",
            "root",
            "receipt",
            "wait",
            "receipt",
            "root",
            "stop",
            "root",
            "terminal",
            "root",
            "root",
            "original-request",
            "terminal",
            "root",
            "root"),
        events);
    assertEquals(1, start.retire);
    assertEquals(0, start.await);
    assertEquals(0, stop.await);
  }

  @Test
  void bucycle002UnknownStartAndStopNeverAdvanceUntilRealClientResult() throws Exception {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    start.status = BackupUnitStartClient.Status.UNKNOWN;
    var stop = new StopAttempt();
    stop.status = MaintenanceUnitStopClient.Status.UNKNOWN;
    int[] waits = {0};
    var cycle =
        cycle(
            events,
            start,
            stop,
            () -> {
              events.add("wait");
              if (++waits[0] == 2) {
                assertFalse(events.contains("stop"));
                start.status = BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
              }
              if (waits[0] == 4) {
                assertEquals(0, start.retire);
                stop.status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
              }
            },
            () -> fail("eventually reaped attempts must complete"));
    cycle.execute(() -> events.add("original-request"));
    assertEquals(4, waits[0]);
    assertEquals(2, start.await);
    assertEquals(2, stop.await);
    assertEquals(1, start.retire);
    assertTrue(events.indexOf("stop") > events.indexOf("receipt"));
    assertTrue(events.indexOf("original-request") > events.indexOf("terminal"));

    start.status = BackupUnitStartClient.Status.UNKNOWN;
    stop.status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
    int before = start.retire;
    var pendingEvents = new ArrayList<String>();
    var pending =
        cycle(
            pendingEvents,
            start,
            stop,
            () -> {
              if (start.await >= 4) throw new Retained();
            },
            () -> {
              pendingEvents.add("retain");
              throw new Retained();
            });
    assertThrows(Retained.class, () -> pending.execute(() -> fail("no proof")));
    assertEquals(before, start.retire);
    assertEquals("retain", pendingEvents.getLast());
  }

  @Test
  void bucycle003PostStartUncertaintyRetainsAndPreStartFailureDoesNotStart() {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    var stop = new StopAttempt();
    var brokenReceipt =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                return "baseline";
              }

              public boolean freshZero(Object baseline) throws IOException {
                throw new IOException("untrusted receipt");
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> {
              events.add("stop");
              return stop;
            },
            () -> true,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            },
            budget());
    assertThrows(Retained.class, () -> brokenReceipt.execute(() -> fail("no proof")));
    assertEquals(List.of("start", "retain"), events);
    assertEquals(0, start.retire);

    events.clear();
    var beforeStart =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() throws IOException {
                throw new IOException("pre-start unavailable");
              }

              public boolean freshZero(Object baseline) {
                fail("no observe");
                return false;
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> stop,
            () -> true,
            () -> {},
            () -> fail("no retention before start"),
            budget());
    assertThrows(IOException.class, () -> beforeStart.execute(() -> {}));
    assertTrue(events.isEmpty());
  }

  @Test
  void bucycle004NonzeroAndRetireFailureNeverReturnSuccess() {
    var events = new ArrayList<String>();
    var start = new StartAttempt();
    var stop = new StopAttempt();
    start.status = BackupUnitStartClient.Status.CLIENT_EXITED_NONZERO;
    var failed =
        cycle(
            events,
            start,
            stop,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            });
    assertThrows(Retained.class, () -> failed.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "start", "terminal", "retain"), events);
    assertEquals(0, start.retire);

    events.clear();
    start.status = BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
    start.retirement =
        () -> {
          throw new IOException("uncertain marker retirement");
        };
    assertThrows(Retained.class, () -> failed.execute(() -> events.add("original-request")));
    assertEquals(0, start.retire);
    assertTrue(events.contains("stop"));
    assertEquals("retain", events.getLast());
    assertThrows(NullPointerException.class, () -> failed.execute(null));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningBackupUnitCycle(
                null,
                receipt(events),
                () -> start,
                () -> stop,
                () -> true,
                () -> {},
                () -> {},
                budget()));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningBackupUnitCycle(
                () -> {},
                receipt(events),
                () -> start,
                () -> stop,
                () -> true,
                () -> {},
                () -> {},
                null));
  }

  @Test
  void bucycle005UnknownStartFailureAndNullAfterStartCannotUnwindParent() {
    for (Throwable failure :
        List.of(
            new IOException("unresolved start delivery"),
            new StopGateException(StopGateFailure.COMMAND_FAILURE),
            new IllegalStateException("unresolved start delivery"),
            new AssertionError("unresolved start delivery"))) {
      var events = new ArrayList<String>();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              receipt(events),
              () -> {
                events.add("start");
                if (failure instanceof IOException known) throw known;
                if (failure instanceof RuntimeException unknown) throw unknown;
                throw (Error) failure;
              },
              () -> {
                events.add("stop");
                fail("unknown start cannot stop");
                return null;
              },
              () -> true,
              () -> {},
              () -> {
                events.add("retain");
                throw new Retained();
              },
              budget());
      assertThrows(Retained.class, () -> cycle.execute(() -> fail("no proof")));
      assertEquals(List.of("baseline", "start", "retain"), events);
    }
    for (boolean nullAttempt : List.of(true, false)) {
      var events = new ArrayList<String>();
      var cycle =
          new MorningBackupUnitCycle(
              () -> {},
              receipt(events),
              () -> {
                events.add("start");
                if (nullAttempt) return null;
                return new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return null;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    fail("null status is not a pending client");
                    return null;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof) {
                    fail("null status cannot retire");
                  }
                };
              },
              () -> {
                fail("null start cannot stop");
                return null;
              },
              () -> true,
              () -> {},
              () -> {
                events.add("retain");
                throw new Retained();
              },
              budget());
      assertThrows(Retained.class, () -> cycle.execute(() -> fail("no proof")));
      assertEquals(List.of("baseline", "start", "retain"), events);
    }
    var awaitEvents = new ArrayList<String>();
    var nullAwait =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(awaitEvents),
            () ->
                new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return BackupUnitStartClient.Status.UNKNOWN;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    return null;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof) {
                    fail("null await cannot retire");
                  }
                },
            () -> {
              fail("null await cannot stop");
              return null;
            },
            () -> true,
            () -> awaitEvents.add("wait"),
            () -> {
              awaitEvents.add("retain");
              throw new Retained();
            },
            budget());
    assertThrows(Retained.class, () -> nullAwait.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "wait", "retain"), awaitEvents);
  }

  @Test
  void bucycle006OneParentBudgetRejectsBeforeStartAndRetainsAfterStart() {
    final long deadline = 1_800_000_000_000L; // SS341: 30 * 60 * 10^9 ns.
    long[] now = {0};
    var parentBudget = new MorningParentBudget(() -> now[0]);
    var events = new ArrayList<String>();
    var before =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(events),
            () -> {
              events.add("start");
              return new StartAttempt();
            },
            StopAttempt::new,
            () -> true,
            () -> {},
            () -> fail("no start, no retention"),
            parentBudget);
    now[0] = deadline;
    assertThrows(IOException.class, () -> before.execute(() -> fail("no proof")));
    assertTrue(events.isEmpty());

    now[0] = 0;
    var start = new StartAttempt();
    var stop = new StopAttempt();
    events.clear();
    var afterStart =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(events),
            () -> {
              events.add("start");
              now[0] = deadline;
              return start;
            },
            () -> {
              fail("expired start cannot stop");
              return stop;
            },
            () -> true,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> afterStart.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "start", "retain"), events);
    assertEquals(0, start.retire);

    now[0] = 0;
    events.clear();
    var duringReceipt =
        new MorningBackupUnitCycle(
            () -> {},
            new MorningBackupUnitCycle.Receipt() {
              public Object capture() {
                events.add("baseline");
                return "baseline";
              }

              public boolean freshZero(Object baseline) {
                assertEquals("baseline", baseline);
                now[0] = deadline;
                return false;
              }
            },
            () -> {
              events.add("start");
              return start;
            },
            () -> {
              fail("expired receipt cannot stop");
              return stop;
            },
            () -> true,
            () -> {},
            () -> {
              events.add("retain");
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> duringReceipt.execute(() -> fail("no proof")));
    assertEquals(List.of("baseline", "start", "retain"), events);
    assertEquals(0, start.retire);

    now[0] = 0;
    stop.status = MaintenanceUnitStopClient.Status.UNKNOWN;
    var duringStop =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(new ArrayList<>()),
            () -> start,
            () -> {
              now[0] = deadline;
              return stop;
            },
            () -> true,
            () -> fail("expired stop must not await client"),
            () -> {
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> duringStop.execute(() -> fail("no proof")));
    assertEquals(0, start.retire);

    now[0] = 0;
    stop.status = MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
    start.retirement = () -> now[0] = deadline;
    var beforeRetire =
        new MorningBackupUnitCycle(
            () -> {},
            receipt(new ArrayList<>()),
            () -> start,
            () -> stop,
            () -> true,
            () -> {},
            () -> {
              throw new Retained();
            },
            parentBudget);
    assertThrows(Retained.class, () -> beforeRetire.execute(() -> fail("no proof")));
    assertEquals(0, start.retire);
  }

  private static MorningBackupUnitCycle.Receipt receipt(List<String> events) {
    return new MorningBackupUnitCycle.Receipt() {
      public Object capture() {
        events.add("baseline");
        return "baseline";
      }

      public boolean freshZero(Object baseline) {
        events.add("receipt");
        assertEquals("baseline", baseline);
        return true;
      }
    };
  }

  private static MorningBackupUnitCycle cycle(
      List<String> events,
      StartAttempt start,
      StopAttempt stop,
      MorningBackupUnitCycle.Wait wait,
      MorningBackupUnitCycle.Retain retain) {
    return new MorningBackupUnitCycle(
        () -> {},
        receipt(events),
        () -> {
          events.add("start");
          return start;
        },
        () -> {
          events.add("stop");
          return stop;
        },
        () -> {
          events.add("terminal");
          return true;
        },
        wait,
        retain,
        budget());
  }

  private static MorningParentBudget budget() {
    return new MorningParentBudget(() -> 0L);
  }
}
