package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** PT-OPS-MTERM001..008; public literal ports, never synthetic root authorization. */
final class MaintenanceUnitTerminationTest {
  private static final String COLD =
      "Id=schubert-nk-backup.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\nJob=\nMainPID=0\nControlPID=0\nSlice=system.slice\nDelegate=no\nControlGroup=\nInvocationID=\nStateChangeTimestampMonotonic=0\n";
  private static final List<String> NAMES =
      List.of(
          "caddy.service",
          "schubert-nk-web.service",
          "schubert-nk-api.service",
          "schubert-nk-cleanup.service",
          "schubert-nk-inbox-inspector.service",
          "schubert-nk-expiry-cleanup.service",
          "schubert-nk-backup.service",
          "artemis.service");

  static final class Fixture implements MaintenanceUnitTermination.Observations {
    final BackupUnitTerminationTest.Fixture kernel = new BackupUnitTerminationTest.Fixture();
    final List<byte[]> delivered = new ArrayList<>();
    MaintenanceUnit target = MaintenanceUnit.BACKUP;
    String name = "schubert-nk-backup.service";
    String state = COLD;
    String processes = "a(sus) 0\n";
    int reads;
    int processReads;
    boolean drift;
    boolean nullState;
    boolean nullProcesses;
    boolean wrongUnit;
    boolean emptyPresentGroup;

    public MaintenanceStopSnapshot read() throws IOException {
      reads++;
      kernel.event("manager-state");
      if (nullState) return null;
      String observed = state.replace("schubert-nk-backup.service", name);
      if (kernel.present && !emptyPresentGroup)
        observed = observed.replace("ControlGroup=\n", "ControlGroup=/system.slice/" + name + "\n");
      if (drift && reads > 1)
        observed =
            observed.replace("StateChangeTimestampMonotonic=0", "StateChangeTimestampMonotonic=1");
      if (wrongUnit)
        return MaintenanceStopSnapshot.parse(
            MaintenanceUnit.WEB,
            COLD.replace("schubert-nk-backup.service", "schubert-nk-web.service")
                .getBytes(StandardCharsets.US_ASCII));
      return MaintenanceStopSnapshot.parse(target, observed.getBytes(StandardCharsets.US_ASCII));
    }

    public byte[] processes() throws IOException {
      processReads++;
      kernel.event("manager-processes");
      if (nullProcesses) return null;
      byte[] bytes = processes.getBytes(StandardCharsets.US_ASCII);
      delivered.add(bytes);
      return bytes;
    }

    FixedUnitCgroupNamespace namespace() {
      DirectoryCalls delegate = kernel.calls();
      DirectoryCalls fixed =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  DirectoryCalls.class.getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, arguments) -> {
                    Object[] forwarded = arguments == null ? null : arguments.clone();
                    if (method.getName().equals("openDirectory") && name.equals(forwarded[1])) {
                      assertEquals(NAMES.get(target.ordinal()), forwarded[1], "fixed leaf only");
                      forwarded[1] = "schubert-nk-backup.service";
                    }
                    try {
                      return method.invoke(delegate, forwarded);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                  });
      return new FixedUnitCgroupNamespace(
          () -> kernel.event("namespace-context"), fixed, kernel.security(), kernel);
    }

    MaintenanceUnitTermination adapter() {
      return new MaintenanceUnitTermination(
          () -> kernel.event("parent-context"), target, this, namespace());
    }

    void closed() {
      kernel.released();
      for (byte[] bytes : delivered) assertArrayEquals(new byte[bytes.length], bytes);
    }
  }

  private static void rejected(Fixture fixture) {
    IOException failure = assertThrows(IOException.class, fixture.adapter()::quiescent);
    assertEquals("maintenance termination unavailable", failure.getMessage());
    assertNull(failure.getCause());
    fixture.closed();
  }

  @Test
  void issuerGate002PreservesActualTwelveFieldsAndSeparateKernelIdentities() throws Exception {
    for (boolean present : List.of(false, true)) {
      var f = new Fixture();
      f.kernel.present = present;
      var actual = f.adapter().quiescentObservation().orElseThrow();
      assertEquals(
          List.of(
              "schubert-nk-backup.service",
              "loaded",
              "inactive",
              "dead",
              "",
              "0",
              "0",
              "system.slice",
              "no",
              present ? "/system.slice/schubert-nk-backup.service" : "",
              "",
              "0"),
          actual.manager().observedValues());
      assertEquals(present, actual.leafPresent());
      assertEquals(
          List.of(
              new MaintenanceUnitTermination.KernelDirectory(040755, 0, 0, 1, 10),
              new MaintenanceUnitTermination.KernelDirectory(040555, 0, 0, 2, 11),
              new MaintenanceUnitTermination.KernelDirectory(040755, 0, 0, 2, 12),
              new MaintenanceUnitTermination.KernelDirectory(040555, 0, 0, 3, 13),
              new MaintenanceUnitTermination.KernelDirectory(040755, 0, 0, 3, 14)),
          actual.directories().subList(0, 5));
      if (present)
        assertEquals(
            new MaintenanceUnitTermination.KernelDirectory(040755, 0, 0, 3, 15),
            actual.directories().get(5));
      assertThrows(UnsupportedOperationException.class, () -> actual.directories().clear());
      assertThrows(
          UnsupportedOperationException.class, () -> actual.manager().observedValues().clear());
      assertEquals("MaintenanceTerminationObservation[actual=<redacted>]", actual.toString());
      f.closed();
    }
  }

  @Test
  void mterm001AllFixedColdAndPresentLeaves() throws Exception {
    for (int index = 0; index < 8; index++) {
      for (boolean present : List.of(false, true)) {
        var f = new Fixture();
        f.target = MaintenanceUnit.values()[index];
        f.name = NAMES.get(index);
        f.kernel.present = present;
        assertTrue(f.adapter().quiescent().orElseThrow().quiescent());
        assertEquals(3, f.reads);
        assertEquals(present ? 1 : 0, f.processReads);
        assertEquals(present ? 12 : 10, f.kernel.closes);
        f.closed();
      }
    }
  }

  @Test
  void mterm002UnboundBusyAndNestedProcessRefused() throws Exception {
    var unbound = new Fixture();
    unbound.kernel.present = true;
    unbound.emptyPresentGroup = true;
    rejected(unbound);
    assertEquals(0, unbound.processReads);
    var busy = new Fixture();
    busy.state = COLD.replace("MainPID=0", "MainPID=42");
    assertTrue(busy.adapter().quiescent().isEmpty());
    assertEquals(0, busy.kernel.closes);
    busy.closed();
    for (String vector :
        List.of(
            "", "a(sus) 1 42 \"nested/subgroup\" \"java\"\n", "a(sus) 00\n", "a(sus) 0\nextra")) {
      var populated = new Fixture();
      populated.kernel.present = true;
      populated.processes = vector;
      assertTrue(populated.adapter().quiescent().isEmpty());
      assertEquals(1, populated.processReads);
      populated.closed();
    }
  }

  @Test
  void mterm003AbaCurrentNamespaceAndWrongActor() {
    var aba = new Fixture();
    aba.drift = true;
    rejected(aba);
    var exchanged = new Fixture();
    exchanged.kernel.inodeDrift = true;
    rejected(exchanged);
    var wrong = new Fixture();
    wrong.wrongUnit = true;
    rejected(wrong);
    assertEquals(0, wrong.kernel.closes);
    var absentAncestor = new Fixture();
    absentAncestor.kernel.missingRole = "system.slice";
    rejected(absentAncestor);
    var notLoaded = new Fixture();
    notLoaded.state = COLD.replace("LoadState=loaded", "LoadState=not-found");
    assertThrows(StopGateException.class, notLoaded.adapter()::quiescent);
    notLoaded.closed();
  }

  @Test
  void mterm004EveryIoUnknownAndClosePosition() throws Exception {
    var baseline = new Fixture();
    baseline.kernel.present = true;
    baseline.adapter().quiescent();
    baseline.closed();
    for (int position = 1; position <= baseline.kernel.position; position++) {
      for (Throwable fault :
          List.of(
              new StorageIoException(StorageIoException.Reason.UNAVAILABLE),
              new IllegalStateException("public unknown"),
              new AssertionError("public fatal"))) {
        var f = new Fixture();
        f.kernel.present = true;
        f.kernel.faultPosition = position;
        f.kernel.fault = fault;
        Throwable actual = assertThrows(Throwable.class, f.adapter()::quiescent);
        if (fault instanceof RuntimeException || fault instanceof Error) assertSame(fault, actual);
        else assertInstanceOf(IOException.class, actual);
        f.closed();
      }
    }
  }

  @Test
  void mterm005NullContractsAndAllOwnedMaterials() {
    var f = new Fixture();
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitTermination(null, f.target, f, f.namespace()));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitTermination(() -> {}, null, f, f.namespace()));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitTermination(() -> {}, f.target, null, f.namespace()));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitTermination(() -> {}, f.target, f, null));
    for (int kind = 0; kind < 2; kind++) {
      var missing = new Fixture();
      missing.kernel.present = true;
      missing.nullState = kind == 0;
      missing.nullProcesses = kind == 1;
      assertThrows(NullPointerException.class, missing.adapter()::quiescent);
      missing.closed();
    }
    assertThrows(
        NullPointerException.class,
        () -> new FixedUnitCgroupNamespace(null, f.kernel.calls(), f.kernel.security(), f.kernel));
    assertThrows(
        NullPointerException.class,
        () -> new FixedUnitCgroupNamespace(() -> {}, null, f.kernel.security(), f.kernel));
    assertThrows(
        NullPointerException.class,
        () -> new FixedUnitCgroupNamespace(() -> {}, f.kernel.calls(), null, f.kernel));
    assertThrows(
        NullPointerException.class,
        () -> new FixedUnitCgroupNamespace(() -> {}, f.kernel.calls(), f.kernel.security(), null));
    assertThrows(NullPointerException.class, () -> f.namespace().observe(null));
    f.closed();
  }

  @Test
  void mterm006InterruptAndIndependentParallel() throws Exception {
    try {
      Thread.currentThread().interrupt();
      var f = new Fixture();
      rejected(f);
      assertEquals(0, f.reads);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    var baseline = new Fixture();
    baseline.adapter().quiescent();
    for (int position = 1; position <= baseline.kernel.position; position++) {
      var f = new Fixture();
      f.kernel.interrupt = true;
      f.kernel.faultPosition = position;
      try {
        rejected(f);
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
    try (var workers = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              var f = new Fixture();
              var result = f.adapter().quiescent();
              f.closed();
              return result.isPresent();
            });
      for (var future : workers.invokeAll(tasks)) assertTrue(future.get());
    }
  }

  @Test
  void mterm007NativeFixedQueriesAndMaterials() {
    for (int index = 0; index < 8; index++) {
      MaintenanceUnit unit = MaintenanceUnit.values()[index];
      String name = NAMES.get(index);
      for (boolean processes : List.of(false, true)) {
        byte[] expected =
            (processes ? "a(sus) 0\n" : COLD.replace("schubert-nk-backup.service", name))
                .getBytes(StandardCharsets.US_ASCII);
        var child = new InspectorUnitProbeFixture.Child(expected);
        var reader =
            new InspectorUnitProbe.NativeReader(
                command -> {
                  assertEquals(name, command.getLast());
                  assertEquals(
                      processes ? "/usr/bin/busctl" : "/usr/bin/systemctl", command.getFirst());
                  if (!processes)
                    assertEquals(
                        "--property=Id,LoadState,ActiveState,SubState,Job,MainPID,ControlPID,Slice,Delegate,ControlGroup,InvocationID,StateChangeTimestampMonotonic",
                        command.get(5));
                  else
                    assertEquals(
                        List.of(
                            "/usr/bin/busctl",
                            "--system",
                            "--timeout=5s",
                            "--no-pager",
                            "call",
                            "org.freedesktop.systemd1",
                            "/org/freedesktop/systemd1",
                            "org.freedesktop.systemd1.Manager",
                            "GetUnitProcesses",
                            "s",
                            name),
                        command);
                  return child;
                });
        var observations = new MaintenanceUnitTermination.NativeObservations(unit, reader);
        if (processes) {
          byte[] actual = observations.processes();
          assertArrayEquals(expected, actual);
          Arrays.fill(actual, (byte) 0);
        } else assertTrue(observations.read().quiescent());
        child.allClosed();
        child.wiped();
        assertThrows(
            NullPointerException.class,
            () -> new MaintenanceUnitTermination.NativeObservations(null, reader));
        assertThrows(
            NullPointerException.class,
            () -> new MaintenanceUnitTermination.NativeObservations(unit, null));
      }
    }
    var bad =
        new InspectorUnitProbeFixture.Child(
            "not a projection\n".getBytes(StandardCharsets.US_ASCII));
    var obs =
        new MaintenanceUnitTermination.NativeObservations(
            MaintenanceUnit.BACKUP, new InspectorUnitProbe.NativeReader(command -> bad));
    assertThrows(StopGateException.class, obs::read);
    bad.allClosed();
    bad.wiped();
  }

  @Test
  void mterm008NativeFactoryAndOrdinaryHostRefusal() throws Exception {
    var root = new RootStartupContextTest.Fixture();
    root.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    root.unit = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = root.context();
    var expected = context.capture(RootStartupContext.Service.MORNING);
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceUnitTermination.create(null, expected, MaintenanceUnit.BACKUP));
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceUnitTermination.create(context, null, MaintenanceUnit.BACKUP));
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceUnitTermination.create(context, expected, null));
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.API,
            expected.boot(),
            expected.invocation(),
            expected.pid(),
            expected.startTicks(),
            expected.initStartTicks(),
            expected.controlGroup());
    assertThrows(
        IOException.class,
        () -> MaintenanceUnitTermination.create(context, wrong, MaintenanceUnit.BACKUP));
    var adapter = MaintenanceUnitTermination.create(context, expected, MaintenanceUnit.BACKUP);
    if (LinuxInodeSecurity.create().effectiveUid() != 0)
      assertThrows(IOException.class, adapter::quiescent);
    // Literal context port is not genuine root/kernel acceptance; actual native success remains
    // required.
  }

  @Test
  void mterm009CleanupActorCanObserveOnlyWebAndApi() throws Exception {
    var root = new RootStartupContextTest.Fixture();
    root.group = "0::/system.slice/schubert-nk-cleanup.service\n";
    root.unit = RootStartupContextTest.unit(RootStartupContext.Service.CLEANUP);
    var context = root.context();
    var expected = context.capture(RootStartupContext.Service.CLEANUP);
    int baselineReads = root.reads;
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceUnitTermination.createCleanup(null, expected, MaintenanceUnit.WEB));
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceUnitTermination.createCleanup(context, null, MaintenanceUnit.WEB));
    assertThrows(
        NullPointerException.class,
        () -> MaintenanceUnitTermination.createCleanup(context, expected, null));
    for (MaintenanceUnit other : MaintenanceUnit.values()) {
      if (other == MaintenanceUnit.WEB || other == MaintenanceUnit.API) continue;
      assertThrows(
          IOException.class,
          () -> MaintenanceUnitTermination.createCleanup(context, expected, other));
    }
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.MORNING,
            expected.boot(),
            expected.invocation(),
            expected.pid(),
            expected.startTicks(),
            expected.initStartTicks(),
            expected.controlGroup());
    assertThrows(
        IOException.class,
        () -> MaintenanceUnitTermination.createCleanup(context, wrong, MaintenanceUnit.WEB));
    assertEquals(baselineReads, root.reads, "refused targets must not query the manager");
    for (MaintenanceUnit unit : List.of(MaintenanceUnit.WEB, MaintenanceUnit.API)) {
      var child = MaintenanceUnitTermination.createCleanup(context, expected, unit);
      if (LinuxInodeSecurity.create().effectiveUid() != 0)
        assertThrows(IOException.class, child::quiescent);
    }
  }
}
