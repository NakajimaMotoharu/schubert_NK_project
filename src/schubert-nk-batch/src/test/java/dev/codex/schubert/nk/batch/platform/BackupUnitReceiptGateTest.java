package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS341/343 fixed 18-field vectors; no real Unit start or fabricated kernel acceptance. */
final class BackupUnitReceiptGateTest {
  @Test
  void isscomp009StoppedGcRetainsRealZeroAndNonZeroButRejectsPartialAndForeignState()
      throws Exception {
    String cold =
        "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
    for (int code : List.of(0, 30)) {
      var actual = new java.util.concurrent.atomic.AtomicReference<>(oldState());
      var kernel =
          new java.util.concurrent.atomic.AtomicReference<Optional<InspectorUnitSnapshot>>();
      var drift = new java.util.concurrent.atomic.AtomicBoolean();
      var reads = new java.util.concurrent.atomic.AtomicInteger();
      var unknown = new java.util.concurrent.atomic.AtomicReference<RuntimeException>();
      var gate =
          new BackupUnitReceiptGate(
              () -> {},
              () -> {
                if (unknown.get() != null) throw unknown.get();
                return Optional.of(
                    drift.get() && reads.incrementAndGet() > 1 ? oldState() : actual.get());
              },
              () -> kernel.get() == null ? Optional.of(actual.get()) : kernel.get());
      var baseline = gate.capture();
      actual.set(
          state(
              FRESH,
              code == 0 ? "active" : "failed",
              code == 0 ? "exited" : "failed",
              "",
              "0",
              "1",
              Integer.toString(code),
              code == 0 ? "success" : "exit-code"));
      var receipt = gate.observeResult(baseline).orElseThrow();
      actual.set(
          InspectorUnitSnapshot.parse(
              cold.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP));
      gate.requireStoppedResult(baseline, receipt);
      assertEquals(code, receipt.exitCode());
      assertEquals(FRESH, receipt.invocation().toString().replace("-", ""));
      actual.set(
          state(
              FRESH,
              "inactive",
              "dead",
              "",
              "0",
              "1",
              Integer.toString(code),
              code == 0 ? "success" : "exit-code"));
      gate.requireStoppedResult(baseline, receipt);
      List<String> corrupt =
          List.of(
              cold.replace(
                  "ActiveState=inactive\nSubState=dead", "ActiveState=active\nSubState=exited"),
              cold.replace("InvocationID=\n", "InvocationID=" + OTHER + "\n"),
              cold.replace("ExecMainCode=0", "ExecMainCode=1"),
              cold.replace("ExecMainStatus=0", "ExecMainStatus=1"),
              cold.replace(
                  "ExecMainStartTimestampMonotonic=0", "ExecMainStartTimestampMonotonic=1"),
              cold.replace("ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=1"),
              cold.replace("Result=success", "Result=timeout"),
              cold.replace("MainPID=0", "MainPID=99"),
              cold.replace("Job=\n", "Job=99\n"));
      for (String wire : corrupt) {
        actual.set(
            InspectorUnitSnapshot.parse(
                wire.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP));
        assertThrows(IOException.class, () -> gate.requireStoppedResult(baseline, receipt));
      }
      String retained =
          cold.replace("InvocationID=\n", "InvocationID=" + FRESH + "\n")
              .replace("ExecMainCode=0", "ExecMainCode=1")
              .replace("ExecMainStatus=0", "ExecMainStatus=" + code)
              .replace(
                  "ExecMainStartTimestampMonotonic=0", "ExecMainStartTimestampMonotonic=1234567")
              .replace(
                  "ExecMainExitTimestampMonotonic=0", "ExecMainExitTimestampMonotonic=2345678");
      for (String wire :
          List.of(
              retained.replace(FRESH, OTHER),
              retained.replace("ExecMainCode=1", "ExecMainCode=2"),
              retained.replace("ExecMainStatus=" + code, "ExecMainStatus=" + (code + 1)),
              retained.replace(
                  "ExecMainStartTimestampMonotonic=1234567",
                  "ExecMainStartTimestampMonotonic=1234568"),
              retained.replace(
                  "ExecMainExitTimestampMonotonic=2345678",
                  "ExecMainExitTimestampMonotonic=2345679"),
              retained.replace("Result=success", "Result=signal"),
              retained.replace(
                  "ActiveState=inactive\nSubState=dead", "ActiveState=active\nSubState=exited"))) {
        actual.set(
            InspectorUnitSnapshot.parse(
                wire.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP));
        assertThrows(IOException.class, () -> gate.requireStoppedResult(baseline, receipt));
      }
      actual.set(
          InspectorUnitSnapshot.parse(
              cold.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP));
      String foreignTarget =
          cold.replace("schubert-nk-backup.service", "schubert-nk-expiry-cleanup.service");
      actual.set(
          InspectorUnitSnapshot.parse(
              foreignTarget.getBytes(StandardCharsets.US_ASCII),
              InspectorUnitSnapshot.Target.EXPIRY));
      assertThrows(IOException.class, () -> gate.requireStoppedResult(baseline, receipt));
      actual.set(
          InspectorUnitSnapshot.parse(
              cold.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP));
      kernel.set(Optional.empty());
      assertThrows(IOException.class, () -> gate.requireStoppedResult(baseline, receipt));
      kernel.set(Optional.of(oldState()));
      assertThrows(IOException.class, () -> gate.requireStoppedResult(baseline, receipt));
      kernel.set(null);
      drift.set(true);
      reads.set(0);
      assertThrows(IOException.class, () -> gate.requireStoppedResult(baseline, receipt));
      drift.set(false);
      var changedBaseline = gate.capture();
      assertThrows(IOException.class, () -> gate.requireStoppedResult(changedBaseline, receipt));
      var otherGate =
          new BackupUnitReceiptGate(
              () -> {}, () -> Optional.of(oldState()), () -> Optional.of(oldState()));
      assertThrows(
          IOException.class, () -> gate.requireStoppedResult(otherGate.capture(), receipt));
      assertThrows(IOException.class, () -> otherGate.requireStoppedResult(baseline, receipt));
      var cleanupGate =
          new BackupUnitReceiptGate(
              () -> {},
              () -> Optional.of(oldState()),
              () -> Optional.of(oldState()),
              BackupUnitStartClient.Target.CLEANUP);
      assertThrows(IOException.class, () -> cleanupGate.requireStoppedResult(baseline, receipt));
      assertThrows(
          IOException.class,
          () -> gate.requireStoppedResult(baseline, ExpiryReceiptFixture.receipt(0)));
      assertThrows(NullPointerException.class, () -> gate.requireStoppedResult(null, receipt));
      assertThrows(NullPointerException.class, () -> gate.requireStoppedResult(baseline, null));
      var failure = new NullPointerException("PRIVATE_PROGRAMMING");
      unknown.set(failure);
      assertSame(
          failure,
          assertThrows(
              NullPointerException.class, () -> gate.requireStoppedResult(baseline, receipt)));
    }
  }

  private static final String OLD = "123456789abcdef08123456789abcdef";
  private static final String FRESH = "fedcba98765432100123456789abcdef";
  private static final String OTHER = "102030405060708090a0b0c0d0e0f001";

  private static InspectorUnitSnapshot state(
      String invocation,
      String active,
      String sub,
      String job,
      String main,
      String code,
      String status,
      String result) {
    String wire =
        "Id=schubert-nk-backup.service\n"
            + "LoadState=loaded\n"
            + "ActiveState="
            + active
            + "\n"
            + "SubState="
            + sub
            + "\n"
            + "Job="
            + job
            + "\n"
            + "MainPID="
            + main
            + "\n"
            + "ControlPID=0\n"
            + "InvocationID="
            + invocation
            + "\n"
            + "ExecMainCode="
            + code
            + "\n"
            + "ExecMainStatus="
            + status
            + "\n"
            + "ExecMainStartTimestampMonotonic=1234567\n"
            + "ExecMainExitTimestampMonotonic=2345678\n"
            + "Result="
            + result
            + "\n"
            + "Type=oneshot\n"
            + "Restart=no\n"
            + "RemainAfterExit=yes\n"
            + "KillMode=control-group\n"
            + "SendSIGKILL=no\n";
    return InspectorUnitSnapshot.parse(
        wire.getBytes(StandardCharsets.US_ASCII), InspectorUnitSnapshot.Target.BACKUP);
  }

  private static InspectorUnitSnapshot oldState() {
    return state(OLD, "inactive", "dead", "", "0", "1", "0", "success");
  }

  private static InspectorUnitSnapshot fresh() {
    return state(FRESH, "active", "exited", "", "0", "1", "0", "success");
  }

  @Test
  void bgate010ColdProjectionNeverQueriesGcProcessListButKernelStillRequired() throws Exception {
    assertThrows(NullPointerException.class, () -> BackupUnitReceiptGate.stateProjection(null));
    String cold =
        "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nInvocationID=\nExecMainCode=0\nExecMainStatus=0\nExecMainStartTimestampMonotonic=0\nExecMainExitTimestampMonotonic=0\nResult=success\nType=oneshot\nRestart=no\nRemainAfterExit=yes\nKillMode=control-group\nSendSIGKILL=no\n";
    var wire = new java.util.concurrent.atomic.AtomicReference<>(cold);
    var reads = new java.util.concurrent.atomic.AtomicInteger();
    var probe =
        new InspectorUnitProbe(
            new InspectorUnitProbe.Reader() {
              public byte[] readState() {
                reads.incrementAndGet();
                return wire.get().getBytes(StandardCharsets.US_ASCII);
              }

              public byte[] readProcesses() {
                throw new AssertionError("cold GC query must not replace host terminal");
              }
            },
            InspectorUnitSnapshot.Target.BACKUP);
    var projection = BackupUnitReceiptGate.stateProjection(probe);
    var state = projection.quiescent().orElseThrow();
    assertTrue(state.invocationId().isEmpty());
    var kernelCalls = new java.util.concurrent.atomic.AtomicInteger();
    var gate =
        new BackupUnitReceiptGate(
            () -> {},
            projection,
            () -> {
              kernelCalls.incrementAndGet();
              return Optional.of(state);
            });
    assertNotNull(gate.capture());
    assertEquals(1, kernelCalls.get());
    assertEquals(3, reads.get());
    assertThrows(
        IOException.class,
        new BackupUnitReceiptGate(() -> {}, projection, Optional::empty)::capture);
    wire.set(
        cold.replace("ActiveState=inactive", "ActiveState=activating")
            .replace("SubState=dead", "SubState=start")
            .replace("MainPID=0", "MainPID=123"));
    assertTrue(projection.quiescent().isEmpty());
    wire.set(cold.replace("LoadState=loaded", "LoadState=not-found"));
    assertThrows(StopGateException.class, projection::quiescent);
  }

  @Test
  void bgate009FreshFailureIsTerminalButNeverSuccessOrUnknown() throws Exception {
    for (String status : List.of("1", "255")) {
      var failed = state(FRESH, "failed", "failed", "", "0", "1", status, "exit-code");
      var script = new Script(oldState(), failed);
      var gate = script.gate();
      var terminal = gate.observeTerminal(gate.capture()).orElseThrow();
      assertEquals(
          Optional.of(MorningBackupUnitCycle.Outcome.FAILED),
          terminal.backupTerminalAfter(Optional.empty()));
      assertEquals(2, script.k);
      var oldApi = new Script(oldState(), failed);
      var success = oldApi.gate();
      assertTrue(success.observe(success.capture()).isEmpty());
      assertEquals(1, oldApi.k);
    }
    var success = new Script(oldState(), fresh());
    var gate = success.gate();
    assertEquals(
        Optional.of(MorningBackupUnitCycle.Outcome.SUCCESS),
        gate.observeTerminal(gate.capture()).orElseThrow().backupTerminalAfter(Optional.empty()));
    for (var candidate :
        List.of(
            oldState(),
            state("", "inactive", "dead", "", "0", "1", "1", "exit-code"),
            state(FRESH, "activating", "start", "1", "123", "1", "1", "exit-code"),
            state(FRESH, "failed", "failed", "", "0", "2", "15", "signal"),
            state(FRESH, "failed", "failed", "", "0", "1", "1", "timeout"),
            state(FRESH, "failed", "failed", "", "0", "1", "0", "exit-code"),
            state(FRESH, "active", "exited", "", "0", "1", "1", "exit-code"),
            state(FRESH, "failed", "dead", "", "0", "1", "1", "exit-code"))) {
      var script = new Script(oldState(), candidate);
      var unknown = script.gate();
      assertTrue(unknown.observeTerminal(unknown.capture()).isEmpty());
    }
    var drift =
        new Script(oldState(), state(FRESH, "failed", "failed", "", "0", "1", "1", "exit-code"));
    drift.kernel = List.of(Optional.of(oldState()), Optional.of(fresh()));
    var changed = drift.gate();
    assertTrue(changed.observeTerminal(changed.capture()).isEmpty());
    assertTrue(
        InspectorUnitSnapshot.parse(
                InspectorUnitSnapshotTest.GOLDEN.getBytes(StandardCharsets.US_ASCII))
            .backupTerminalAfter(Optional.empty())
            .isEmpty());
    assertThrows(NullPointerException.class, () -> fresh().backupTerminalAfter(null));
  }

  private static final class Script {
    final List<String> calls = new ArrayList<>();
    List<Optional<InspectorUnitSnapshot>> bus;
    List<Optional<InspectorUnitSnapshot>> kernel;
    int b;
    int k;
    int roots;
    int rootFailureAt;
    boolean kernelFailure;

    Script(InspectorUnitSnapshot before, InspectorUnitSnapshot after) {
      bus =
          List.of(Optional.of(before), Optional.of(before), Optional.of(after), Optional.of(after));
      kernel = List.of(Optional.of(before), Optional.of(after));
    }

    void root() throws IOException {
      calls.add("root");
      if (++roots == rootFailureAt) throw new IOException("public changed root");
    }

    Optional<InspectorUnitSnapshot> bus() {
      calls.add("bus");
      return this.bus.get(b++);
    }

    Optional<InspectorUnitSnapshot> kernel() throws IOException {
      calls.add("kernel");
      if (kernelFailure) throw new IOException("public kernel fault");
      return this.kernel.get(k++);
    }

    BackupUnitReceiptGate gate() {
      return new BackupUnitReceiptGate(this::root, this::bus, this::kernel);
    }
  }

  @Test
  void bgate001FreshReceiptRequiresSameKernelAndSecondBus() throws Exception {
    var s = new Script(oldState(), fresh());
    var gate = s.gate();
    var before = gate.capture();
    assertEquals(List.of("root", "bus", "kernel", "bus", "root"), s.calls);
    assertTrue(gate.observe(before).isPresent());
    assertEquals(
        List.of("root", "bus", "kernel", "bus", "root", "root", "bus", "kernel", "bus", "root"),
        s.calls);
  }

  @Test
  void bgate002CaptureRefusesMissingMismatchAbaAndRootDrift() throws Exception {
    for (int missing : List.of(0, 1, 2)) {
      var s = new Script(oldState(), fresh());
      if (missing == 0) s.bus = List.of(Optional.empty(), Optional.of(oldState()));
      else if (missing == 1) s.kernel = List.of(Optional.empty());
      else s.bus = List.of(Optional.of(oldState()), Optional.empty());
      assertThrows(IOException.class, s.gate()::capture);
    }
    for (int mismatch : List.of(1, 2)) {
      var s = new Script(oldState(), fresh());
      if (mismatch == 1) s.kernel = List.of(Optional.of(fresh()));
      else s.bus = List.of(Optional.of(oldState()), Optional.of(fresh()));
      assertThrows(IOException.class, s.gate()::capture);
    }
    for (int at : List.of(1, 2)) {
      var s = new Script(oldState(), fresh());
      s.rootFailureAt = at;
      assertThrows(IOException.class, s.gate()::capture);
    }
  }

  @Test
  void bgate003RunningOldInvocationAndFailedReceiptStayEmpty() throws Exception {
    var running = state(FRESH, "activating", "start", "1", "123", "1", "0", "success");
    var noNew = oldState();
    var status10 = state(FRESH, "active", "exited", "", "0", "1", "10", "success");
    var failed = state(FRESH, "failed", "failed", "", "0", "1", "1", "exit-code");
    for (var candidate : List.of(running, noNew, status10, failed)) {
      var s = new Script(oldState(), candidate);
      var gate = s.gate();
      assertTrue(gate.observe(gate.capture()).isEmpty());
      assertEquals(1, s.k, "no post-start kernel query on missing receipt");
    }
    var absent = new Script(oldState(), fresh());
    absent.bus = List.of(Optional.of(oldState()), Optional.of(oldState()), Optional.empty());
    var gate = absent.gate();
    assertTrue(gate.observe(gate.capture()).isEmpty());
  }

  @Test
  void bgate004KernelAndBusAbaCannotEstablishReceipt() throws Exception {
    var none = new Script(oldState(), fresh());
    none.kernel = List.of(Optional.of(oldState()), Optional.empty());
    var g1 = none.gate();
    assertTrue(g1.observe(g1.capture()).isEmpty());
    var changedKernel = new Script(oldState(), fresh());
    changedKernel.kernel =
        List.of(
            Optional.of(oldState()),
            Optional.of(state(OTHER, "active", "exited", "", "0", "1", "0", "success")));
    var g2 = changedKernel.gate();
    assertTrue(g2.observe(g2.capture()).isEmpty());
    for (Optional<InspectorUnitSnapshot> after :
        List.of(Optional.<InspectorUnitSnapshot>empty(), Optional.of(oldState()))) {
      var s = new Script(oldState(), fresh());
      s.bus =
          List.of(Optional.of(oldState()), Optional.of(oldState()), Optional.of(fresh()), after);
      var gate = s.gate();
      assertTrue(gate.observe(gate.capture()).isEmpty());
    }
  }

  @Test
  void bgate005NullAndForeignBaselineAreRejected() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitReceiptGate(null, () -> Optional.empty(), () -> Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitReceiptGate(() -> {}, null, () -> Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitReceiptGate(() -> {}, () -> Optional.empty(), null));
    var s = new Script(oldState(), fresh());
    var gate = s.gate();
    assertThrows(NullPointerException.class, () -> gate.observe(null));
    var token = gate.capture();
    assertThrows(IOException.class, () -> new Script(oldState(), fresh()).gate().observe(token));
    var nullBus = new BackupUnitReceiptGate(() -> {}, () -> null, () -> Optional.of(oldState()));
    assertThrows(IOException.class, nullBus::capture);
    var nullKernel = new BackupUnitReceiptGate(() -> {}, () -> Optional.of(oldState()), () -> null);
    assertThrows(IOException.class, nullKernel::capture);
  }

  @Test
  void bgate006PostStartObservationFailureAndInterruptCannotPass() throws Exception {
    var fault = new Script(oldState(), fresh());
    var g1 = fault.gate();
    var token = g1.capture();
    fault.kernelFailure = true;
    assertThrows(IOException.class, () -> g1.observe(token));
    var nullBus = new Script(oldState(), fresh());
    var g2 = nullBus.gate();
    var before = g2.capture();
    nullBus.bus =
        new ArrayList<>(
            List.of(Optional.of(oldState()), Optional.of(oldState()), Optional.of(fresh())));
    nullBus.bus.set(2, null);
    assertThrows(IOException.class, () -> g2.observe(before));
    var managerFailure =
        new BackupUnitReceiptGate(
            () -> {},
            () -> {
              throw new StopGateException(StopGateFailure.COMMAND_FAILURE);
            },
            () -> Optional.of(oldState()));
    assertEquals(
        StopGateFailure.COMMAND_FAILURE,
        assertThrows(StopGateException.class, managerFailure::capture).reason());
    var drift = new Script(oldState(), fresh());
    var g3 = drift.gate();
    var baseline = g3.capture();
    drift.rootFailureAt = 4;
    assertThrows(IOException.class, () -> g3.observe(baseline));
    var interrupted = new Script(oldState(), fresh());
    var g4 = interrupted.gate();
    var held = g4.capture();
    try {
      Thread.currentThread().interrupt();
      assertThrows(IOException.class, () -> g4.observe(held));
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void bgate007FactoryRequiresSameMorningActor() throws Exception {
    var root = new RootStartupContextTest.Fixture();
    root.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    root.unit = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = root.context();
    var expected = context.capture(RootStartupContext.Service.MORNING);
    assertThrows(NullPointerException.class, () -> BackupUnitReceiptGate.create(null, expected));
    assertThrows(NullPointerException.class, () -> BackupUnitReceiptGate.create(context, null));
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.API,
            expected.boot(),
            expected.invocation(),
            expected.pid(),
            expected.startTicks(),
            expected.initStartTicks(),
            expected.controlGroup());
    assertThrows(IOException.class, () -> BackupUnitReceiptGate.create(context, wrong));
    assertNotNull(BackupUnitReceiptGate.create(context, expected));
    var script = new Script(oldState(), fresh());
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitReceiptGate.create(context, expected, null, script::kernel));
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitReceiptGate.create(context, expected, script::bus, null));
    assertThrows(
        IOException.class,
        () -> BackupUnitReceiptGate.create(context, wrong, script::bus, script::kernel));
    var injected = BackupUnitReceiptGate.create(context, expected, script::bus, script::kernel);
    assertNotNull(injected.capture());
    assertEquals(List.of("bus", "kernel", "bus"), script.calls);
  }

  @Test
  void bgate008StaleInvocationAndLateBusReplacementRemainUnaccepted() throws Exception {
    var stale = new Script(oldState(), oldState());
    var g1 = stale.gate();
    assertTrue(g1.observe(g1.capture()).isEmpty());
    var late = new Script(oldState(), fresh());
    late.bus =
        List.of(
            Optional.of(oldState()),
            Optional.of(oldState()),
            Optional.of(fresh()),
            Optional.of(state(OTHER, "active", "exited", "", "0", "1", "0", "success")));
    var g2 = late.gate();
    assertTrue(g2.observe(g2.capture()).isEmpty());
  }
}
