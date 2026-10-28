package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/**
 * SSC119/018-289 CINSPECT: stop/reap before reacquire, env/owner before intent, real typed gate.
 */
final class InspectorUnitCycleTest {
  private static final String FIXTURE_STARTUNKNOWN_39B1DE60 = "startUnknown";
  private static final String FIXTURE_STOPUNKNOWN_2C8CAD74 = "stopUnknown";
  private static final String FIXTURE_STOPUNKNOWNFAILED_88F559C9 = "stopUnknownFailed";
  private static final String FIXTURE_REACQUIRE_1B9DD03F = "reacquire";
  private static final String FIXTURE_DB_END_74A61FC0 = "DB-END";
  private static final String FIXTURE_ENV_OWNER_RETIRE_B469EF0E = "env-owner-retire";
  private static final String FIXTURE_INTENT_RETIRE_881B807B = "intent-retire";
  private static final String FIXTURE_RETAIN_689680EF = "retain";
  private static final String FIXTURE_STOP_6F2BE2FE = "stop";
  private static final String FIXTURE_TERMINAL_C34E20C4 = "terminal";

  /** PT-OPS-IUC3246001/SS343: unknown client is not a worker receipt or advisory return. */
  @Test
  void iuc3246001UnknownStartAndStopMustReapBeforeParentReacquire() throws Exception {
    for (int code : List.of(0, 10)) {
      for (String fault :
          List.of(
              FIXTURE_STARTUNKNOWN_39B1DE60,
              FIXTURE_STOPUNKNOWN_2C8CAD74,
              FIXTURE_STOPUNKNOWNFAILED_88F559C9)) {
        var f = new Fixture(code, fault);
        if (fault.equals(FIXTURE_STOPUNKNOWNFAILED_88F559C9)) {
          assertThrows(Retained.class, f::run);
          assertFalse(f.events.contains(FIXTURE_REACQUIRE_1B9DD03F));
          assertFalse(f.events.contains(FIXTURE_DB_END_74A61FC0));
          assertFalse(f.events.contains(FIXTURE_ENV_OWNER_RETIRE_B469EF0E));
          assertFalse(f.events.contains(FIXTURE_INTENT_RETIRE_881B807B));
          assertTrue(f.events.contains(FIXTURE_RETAIN_689680EF));
          assertThrows(IOException.class, f.cycle::completedReceipt);
        } else {
          var receipt = f.run();
          assertEquals(code, receipt.exitCode());
          assertSame(receipt, f.cycle.completedReceipt());
          assertEquals(1, Collections.frequency(f.events, FIXTURE_INTENT_RETIRE_881B807B));
          assertFalse(f.events.contains(FIXTURE_RETAIN_689680EF));
          if (fault.equals(FIXTURE_STARTUNKNOWN_39B1DE60))
            assertTrue(f.events.indexOf("start-reaped") < f.events.indexOf(FIXTURE_STOP_6F2BE2FE));
          else
            assertTrue(
                f.events.indexOf("stop-reaped") < f.events.indexOf(FIXTURE_REACQUIRE_1B9DD03F));
        }
        assertEquals(1, Collections.frequency(f.events, "start"));
        assertEquals(1, Collections.frequency(f.events, FIXTURE_STOP_6F2BE2FE));
        assertEquals(1, Collections.frequency(f.events, "wait"));
        assertEquals(
            1,
            Collections.frequency(
                f.events,
                fault.equals(FIXTURE_STARTUNKNOWN_39B1DE60) ? "start-reaped" : "stop-reaped"));
      }
    }
  }

  private static final String BASE =
      """
      Id=schubert-nk-inbox-inspector.service
      LoadState=loaded
      ActiveState=inactive
      SubState=dead
      Job=
      MainPID=0
      ControlPID=0
      InvocationID=
      ExecMainCode=0
      ExecMainStatus=0
      ExecMainStartTimestampMonotonic=0
      ExecMainExitTimestampMonotonic=0
      Result=success
      Type=oneshot
      Restart=no
      RemainAfterExit=yes
      KillMode=control-group
      SendSIGKILL=no
      """;

  @Test
  void nativeReceiptRejectsOldNoRemainButGenericProjectionStillParsesIt() throws Exception {
    var state =
        new java.util.concurrent.atomic.AtomicReference<>(
            parse(BASE.replace("RemainAfterExit=yes", "RemainAfterExit=no")));
    var gate =
        new BackupUnitReceiptGate(
            () -> {},
            () -> Optional.of(state.get()),
            () -> Optional.of(state.get()),
            BackupUnitStartClient.Target.INSPECTOR);
    assertThrows(IOException.class, gate::capture); // Cold profile fails before any start/intent.
    state.set(parse(BASE));
    var before = gate.capture();
    state.set(
        parse(
            BASE.replace("ActiveState=inactive", "ActiveState=active")
                .replace("SubState=dead", "SubState=exited")
                .replace("RemainAfterExit=yes", "RemainAfterExit=no")
                .replace("InvocationID=\n", "InvocationID=" + "1".repeat(32) + "\n")
                .replace("ExecMainCode=0", "ExecMainCode=1")
                .replace("ExecMainStatus=0", "ExecMainStatus=10")
                .replace(
                    "ExecMainStartTimestampMonotonic=0", "ExecMainStartTimestampMonotonic=12345")
                .replace(
                    "ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=23456")));
    assertEquals(
        java.util.OptionalInt.of(10),
        state.get().receiptAfter(Optional.empty())); // Observation, not native authority.
    assertEquals(Optional.empty(), gate.observeResult(before));
  }

  @Test
  void genuineFreshZeroAndWarningSurviveGcOnlyAfterExplicitWholeStop() throws Exception {
    for (int code : List.of(0, 10)) {
      var f = new Fixture(code, "");
      var actual = f.run();
      assertEquals(code, actual.exitCode());
      assertEquals(BackupUnitStartClient.Target.INSPECTOR, actual.target());
      assertSame(actual, f.cycle.completedReceipt());
      assertTrue(
          f.events.indexOf(FIXTURE_STOP_6F2BE2FE) < f.events.indexOf(FIXTURE_REACQUIRE_1B9DD03F));
      assertTrue(
          f.events.indexOf(FIXTURE_TERMINAL_C34E20C4)
              < f.events.indexOf(FIXTURE_REACQUIRE_1B9DD03F));
      assertTrue(
          f.events.indexOf(FIXTURE_REACQUIRE_1B9DD03F) < f.events.indexOf(FIXTURE_DB_END_74A61FC0));
      assertTrue(
          f.events.indexOf(FIXTURE_DB_END_74A61FC0)
              < f.events.indexOf(FIXTURE_ENV_OWNER_RETIRE_B469EF0E));
      assertTrue(
          f.events.indexOf(FIXTURE_ENV_OWNER_RETIRE_B469EF0E)
              < f.events.indexOf(FIXTURE_INTENT_RETIRE_881B807B));
      assertEquals(1, Collections.frequency(f.events, "start"));
      assertEquals(1, Collections.frequency(f.events, FIXTURE_STOP_6F2BE2FE));
      assertFalse(f.events.contains(FIXTURE_RETAIN_689680EF));
      assertThrows(
          IOException.class, () -> f.cycle.executeHandoff(w -> w.execute(), r -> {}, () -> {}));
      assertThrows(IOException.class, () -> f.cycle.execute(() -> {}));
    }
  }

  @Test
  void uncertainStopOrTerminalCannotReturnToReacquireAndLaterFailuresKeepIntent() throws Exception {
    for (String fault : List.of(FIXTURE_STOP_6F2BE2FE, FIXTURE_TERMINAL_C34E20C4, "DB", "env")) {
      var f = new Fixture(0, fault);
      assertThrows(Retained.class, f::run);
      assertTrue(f.events.contains(FIXTURE_RETAIN_689680EF));
      assertFalse(f.events.contains(FIXTURE_INTENT_RETIRE_881B807B));
      assertEquals(
          fault.equals("DB") || fault.equals("env"), f.events.contains(FIXTURE_REACQUIRE_1B9DD03F));
      assertThrows(IOException.class, f.cycle::completedReceipt);
    }
    assertTrue(BackupUnitStartClient.Target.INSPECTOR.ownedBy(RootStartupContext.Service.CLEANUP));
    assertFalse(BackupUnitStartClient.Target.INSPECTOR.ownedBy(RootStartupContext.Service.MORNING));
    assertFalse(BackupUnitStartClient.Target.CLEANUP.ownedBy(RootStartupContext.Service.CLEANUP));
    assertEquals("inspector-start.intent", BackupUnitStartClient.Target.INSPECTOR.marker());
  }

  private static final class Retained extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }

  private static InspectorUnitSnapshot parse(String source) {
    return InspectorUnitSnapshot.parse(
        source.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.INSPECTOR);
  }

  private static final class Fixture {
    final List<String> events = new ArrayList<>();
    InspectorUnitSnapshot state = parse(BASE);
    final MorningBackupUnitCycle cycle;
    final String fault;

    Fixture(int code, String fault) throws IOException {
      this.fault = fault;
      var gate =
          new BackupUnitReceiptGate(
              () -> {},
              () -> Optional.of(state),
              () -> Optional.of(state),
              BackupUnitStartClient.Target.INSPECTOR);
      cycle =
          new MorningBackupUnitCycle(
              () -> {},
              new MorningBackupUnitCycle.Receipt() {
                public Object capture() throws IOException {
                  return gate.capture();
                }

                public boolean freshZero(Object b) {
                  fail("typed result required");
                  return false;
                }

                public Optional<MorningBackupUnitCycle.Outcome> terminal(Object b)
                    throws IOException {
                  return gate.observeResult((BackupUnitReceiptGate.Baseline) b)
                      .map(r -> MorningBackupUnitCycle.Outcome.SUCCESS);
                }

                public Optional<BackupUnitReceiptGate.TerminalReceipt> observed(Object b)
                    throws IOException {
                  return gate.observeResult((BackupUnitReceiptGate.Baseline) b);
                }

                public void requirePresent(BackupUnitReceiptGate.TerminalReceipt r)
                    throws IOException {
                  gate.requireStillPresent(r);
                }
              },
              () -> {
                events.add("start");
                state =
                    parse(
                        BASE.replace("ActiveState=inactive", "ActiveState=active")
                            .replace("SubState=dead", "SubState=exited")
                            .replace("InvocationID=\n", "InvocationID=" + "1".repeat(32) + "\n")
                            .replace("ExecMainCode=0", "ExecMainCode=1")
                            .replace("ExecMainStatus=0", "ExecMainStatus=" + code)
                            .replace(
                                "ExecMainStartTimestampMonotonic=0",
                                "ExecMainStartTimestampMonotonic=12345")
                            .replace(
                                "ExecMainExitTimestampMonotonic=0",
                                "ExecMainExitTimestampMonotonic=23456"));
                return new MorningBackupUnitCycle.StartAttempt() {
                  public BackupUnitStartClient.Status status() {
                    return fault.equals(FIXTURE_STARTUNKNOWN_39B1DE60)
                        ? BackupUnitStartClient.Status.UNKNOWN
                        : BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    assertEquals(FIXTURE_STARTUNKNOWN_39B1DE60, fault);
                    assertFalse(events.contains(FIXTURE_STOP_6F2BE2FE));
                    assertFalse(events.contains(FIXTURE_REACQUIRE_1B9DD03F));
                    events.add("start-reaped");
                    return BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof)
                      throws IOException {
                    proof.verify();
                    events.add(FIXTURE_INTENT_RETIRE_881B807B);
                  }
                };
              },
              () -> {
                events.add(FIXTURE_STOP_6F2BE2FE);
                state = parse(BASE); // Genuine receipt may be GC'd after the explicit stop.
                return new MorningBackupUnitCycle.StopAttempt() {
                  public MaintenanceUnitStopClient.Status status() {
                    if (fault.equals(FIXTURE_STOPUNKNOWN_2C8CAD74)
                        || fault.equals(FIXTURE_STOPUNKNOWNFAILED_88F559C9))
                      return MaintenanceUnitStopClient.Status.UNKNOWN;
                    return fault.equals(FIXTURE_STOP_6F2BE2FE)
                        ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO
                        : MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public MaintenanceUnitStopClient.Status awaitClient() {
                    assertTrue(
                        fault.equals(FIXTURE_STOPUNKNOWN_2C8CAD74)
                            || fault.equals(FIXTURE_STOPUNKNOWNFAILED_88F559C9));
                    assertFalse(events.contains(FIXTURE_REACQUIRE_1B9DD03F));
                    assertFalse(events.contains(FIXTURE_DB_END_74A61FC0));
                    events.add("stop-reaped");
                    return fault.equals(FIXTURE_STOPUNKNOWNFAILED_88F559C9)
                        ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO
                        : MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                  }
                };
              },
              () -> {
                events.add(FIXTURE_TERMINAL_C34E20C4);
                return !fault.equals(FIXTURE_TERMINAL_C34E20C4);
              },
              () -> {
                assertTrue(
                    List.of(
                            FIXTURE_STARTUNKNOWN_39B1DE60,
                            FIXTURE_STOPUNKNOWN_2C8CAD74,
                            FIXTURE_STOPUNKNOWNFAILED_88F559C9)
                        .contains(fault));
                assertFalse(events.contains(FIXTURE_REACQUIRE_1B9DD03F));
                events.add("wait");
              },
              () -> {
                events.add(FIXTURE_RETAIN_689680EF);
                throw new Retained();
              },
              MorningParentBudget.create(),
              BackupUnitStartClient.Target.INSPECTOR);
    }

    BackupUnitReceiptGate.TerminalReceipt run() throws IOException {
      return cycle.executeInspectorHandoff(
          work -> {
            events.add("unlock");
            var value = work.execute();
            events.add(FIXTURE_REACQUIRE_1B9DD03F);
            return value;
          },
          r -> {
            events.add(FIXTURE_DB_END_74A61FC0);
            if (fault.equals("DB")) throw new IOException("fixed DB unavailable");
          },
          () -> {
            events.add(FIXTURE_ENV_OWNER_RETIRE_B469EF0E);
            if (fault.equals("env")) throw new IOException("fixed env unavailable");
          });
    }
  }
}
