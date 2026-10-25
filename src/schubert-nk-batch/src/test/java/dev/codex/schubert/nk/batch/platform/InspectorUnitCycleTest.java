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
  /** PT-OPS-IUC3246001/SS343: unknown client is not a worker receipt or advisory return. */
  @Test
  void iuc3246001UnknownStartAndStopMustReapBeforeParentReacquire() throws Exception {
    for (int code : List.of(0, 10)) {
      for (String fault : List.of("startUnknown", "stopUnknown", "stopUnknownFailed")) {
        var f = new Fixture(code, fault);
        if (fault.equals("stopUnknownFailed")) {
          assertThrows(Retained.class, f::run);
          assertFalse(f.events.contains("reacquire"));
          assertFalse(f.events.contains("DB-END"));
          assertFalse(f.events.contains("env-owner-retire"));
          assertFalse(f.events.contains("intent-retire"));
          assertTrue(f.events.contains("retain"));
          assertThrows(IOException.class, f.cycle::completedReceipt);
        } else {
          var receipt = f.run();
          assertEquals(code, receipt.exitCode());
          assertSame(receipt, f.cycle.completedReceipt());
          assertEquals(1, Collections.frequency(f.events, "intent-retire"));
          assertFalse(f.events.contains("retain"));
          if (fault.equals("startUnknown"))
            assertTrue(f.events.indexOf("start-reaped") < f.events.indexOf("stop"));
          else assertTrue(f.events.indexOf("stop-reaped") < f.events.indexOf("reacquire"));
        }
        assertEquals(1, Collections.frequency(f.events, "start"));
        assertEquals(1, Collections.frequency(f.events, "stop"));
        assertEquals(1, Collections.frequency(f.events, "wait"));
        assertEquals(
            1,
            Collections.frequency(
                f.events, fault.equals("startUnknown") ? "start-reaped" : "stop-reaped"));
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
      assertTrue(f.events.indexOf("stop") < f.events.indexOf("reacquire"));
      assertTrue(f.events.indexOf("terminal") < f.events.indexOf("reacquire"));
      assertTrue(f.events.indexOf("reacquire") < f.events.indexOf("DB-END"));
      assertTrue(f.events.indexOf("DB-END") < f.events.indexOf("env-owner-retire"));
      assertTrue(f.events.indexOf("env-owner-retire") < f.events.indexOf("intent-retire"));
      assertEquals(1, Collections.frequency(f.events, "start"));
      assertEquals(1, Collections.frequency(f.events, "stop"));
      assertFalse(f.events.contains("retain"));
      assertThrows(
          IOException.class, () -> f.cycle.executeHandoff(w -> w.execute(), r -> {}, () -> {}));
      assertThrows(IOException.class, () -> f.cycle.execute(() -> {}));
    }
  }

  @Test
  void uncertainStopOrTerminalCannotReturnToReacquireAndLaterFailuresKeepIntent() throws Exception {
    for (String fault : List.of("stop", "terminal", "DB", "env")) {
      var f = new Fixture(0, fault);
      assertThrows(Retained.class, f::run);
      assertTrue(f.events.contains("retain"));
      assertFalse(f.events.contains("intent-retire"));
      assertEquals(fault.equals("DB") || fault.equals("env"), f.events.contains("reacquire"));
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
                    return fault.equals("startUnknown")
                        ? BackupUnitStartClient.Status.UNKNOWN
                        : BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public BackupUnitStartClient.Status awaitClient() {
                    assertEquals("startUnknown", fault);
                    assertFalse(events.contains("stop"));
                    assertFalse(events.contains("reacquire"));
                    events.add("start-reaped");
                    return BackupUnitStartClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public void retireAfter(MorningBackupUnitCycle.ParentProof proof)
                      throws IOException {
                    proof.verify();
                    events.add("intent-retire");
                  }
                };
              },
              () -> {
                events.add("stop");
                state = parse(BASE); // Genuine receipt may be GC'd after the explicit stop.
                return new MorningBackupUnitCycle.StopAttempt() {
                  public MaintenanceUnitStopClient.Status status() {
                    if (fault.equals("stopUnknown") || fault.equals("stopUnknownFailed"))
                      return MaintenanceUnitStopClient.Status.UNKNOWN;
                    return fault.equals("stop")
                        ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO
                        : MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                  }

                  public MaintenanceUnitStopClient.Status awaitClient() {
                    assertTrue(fault.equals("stopUnknown") || fault.equals("stopUnknownFailed"));
                    assertFalse(events.contains("reacquire"));
                    assertFalse(events.contains("DB-END"));
                    events.add("stop-reaped");
                    return fault.equals("stopUnknownFailed")
                        ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO
                        : MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                  }
                };
              },
              () -> {
                events.add("terminal");
                return !fault.equals("terminal");
              },
              () -> {
                assertTrue(
                    List.of("startUnknown", "stopUnknown", "stopUnknownFailed").contains(fault));
                assertFalse(events.contains("reacquire"));
                events.add("wait");
              },
              () -> {
                events.add("retain");
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
            events.add("reacquire");
            return value;
          },
          r -> {
            events.add("DB-END");
            if (fault.equals("DB")) throw new IOException("fixed DB unavailable");
          },
          () -> {
            events.add("env-owner-retire");
            if (fault.equals("env")) throw new IOException("fixed env unavailable");
          });
    }
  }
}
