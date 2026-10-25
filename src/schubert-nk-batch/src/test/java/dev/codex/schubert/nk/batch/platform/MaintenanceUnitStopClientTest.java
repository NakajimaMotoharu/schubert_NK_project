package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SS341/343/SSC102 independent argv/status/ownership vectors; no real stop in host PT. */
final class MaintenanceUnitStopClientTest {
  @Test
  void monitor002CallerLockCannotBlockOwnedStopStatus() throws Exception {
    var process = child();
    var attempt =
        new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> process)
            .stop(MaintenanceUnit.API);
    dev.codex.schubert.nk.bootstrap.CallerMonitorProbe.requireIndependent(
        attempt,
        () -> assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, attempt.status()));
    process.allClosed();
  }

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

  private static InspectorUnitProbeFixture.Child child() {
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    return child;
  }

  @Test
  void mclient001FixedEightNamesPolicyBeforeExactCommand() throws Exception {
    assertEquals(8, MaintenanceUnit.values().length);
    for (int index = 0; index < 8; index++) {
      final int subject = index;
      var unit = MaintenanceUnit.values()[index];
      var process = child();
      var sequence = new java.util.ArrayList<String>();
      var client =
          new MaintenanceUnitStopClient(
              () -> sequence.add("root"),
              current -> {
                assertSame(unit, current);
                sequence.add("policy");
              },
              command -> {
                assertEquals(
                    List.of(
                        "/usr/bin/systemctl",
                        "--system",
                        "--no-pager",
                        "--no-ask-password",
                        "stop",
                        NAMES.get(subject)),
                    command);
                sequence.add("start");
                return process;
              });
      var result = client.stop(unit);
      assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, result.status());
      assertSame(unit, result.unit());
      assertEquals(List.of("root", "policy", "root", "start", "root", "root"), sequence);
      process.allClosed();
      assertEquals(0, process.destroyed);
      assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, result.awaitClient());
      assertEquals(1, process.counts.get("wait"));
    }
  }

  @Test
  void mclient002PolicyAndRootRefusalIssueNoClient() {
    int[] starts = {0};
    var wrongPolicy =
        new MaintenanceUnitStopClient(
            () -> {},
            unit -> {
              throw new StopGateException(StopGateFailure.MALFORMED_STATE);
            },
            command -> {
              starts[0]++;
              return child();
            });
    assertEquals(
        StopGateFailure.MALFORMED_STATE,
        assertThrows(StopGateException.class, () -> wrongPolicy.stop(MaintenanceUnit.CADDY))
            .reason());
    assertEquals(0, starts[0]);
    for (int at : List.of(1, 2)) {
      int[] checks = {0};
      int[] policy = {0};
      var wrongRoot =
          new MaintenanceUnitStopClient(
              () -> {
                if (++checks[0] == at) throw new IOException("public root changed");
              },
              unit -> policy[0]++,
              command -> {
                starts[0]++;
                return child();
              });
      assertThrows(IOException.class, () -> wrongRoot.stop(MaintenanceUnit.CADDY));
      assertEquals(at == 1 ? 0 : 1, policy[0]);
      assertEquals(0, starts[0]);
    }
  }

  @Test
  void mclient003ClientNonzeroAndOwnerCloseNeverSucceeds() throws Exception {
    var process = child();
    process.code = 1;
    var result =
        new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> process)
            .stop(MaintenanceUnit.API);
    assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO, result.status());
    process.allClosed();
    assertEquals(0, process.destroyed);
    assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO, result.awaitClient());
  }

  @Test
  void mclient004TimeoutRetainsLiveProcessAndReapsSameOwner() throws Exception {
    var process = child();
    process.completed = false;
    var result =
        new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> process)
            .stop(MaintenanceUnit.CADDY);
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status());
    assertTrue(process.alive);
    assertEquals(0, process.destroyed);
    assertEquals(1, process.input.closed);
    assertEquals(0, process.output.closed);
    assertEquals(0, process.error.closed);
    process.completed = true;
    assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, result.awaitClient());
    process.allClosed();
    assertEquals(2, process.counts.get("wait"));
    assertEquals(0, process.destroyed);
  }

  @Test
  void mclient005EveryCloseGetterAndUnknownFailurePoisoned() throws Exception {
    for (String fault : List.of("stdin.close", "stdout.close", "stderr.close")) {
      var process = child();
      process.ioFailures.add(fault);
      var result =
          new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> process)
              .stop(MaintenanceUnit.BACKUP);
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status(), fault);
      assertEquals(0, process.destroyed);
      process.ioFailures.clear();
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.awaitClient(), fault);
      assertEquals(1, process.input.closed);
      if (!fault.equals("stdin.close")) {
        assertEquals(1, process.output.closed);
        assertEquals(1, process.error.closed);
      }
    }
    for (String missing : List.of("stdin", "stdout", "stderr")) {
      var process = child();
      process.missing = missing;
      var result =
          new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> process)
              .stop(MaintenanceUnit.BACKUP);
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status(), missing);
      if (missing.equals("stderr")) assertEquals(1, process.output.closed);
      assertEquals(0, process.destroyed);
    }
    var unknown = child();
    var sentinel = new AssertionError("public unknown");
    unknown.hook =
        (name, count) -> {
          if (name.equals("wait")) throw sentinel;
        };
    var result =
        new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> unknown)
            .stop(MaintenanceUnit.BACKUP);
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status());
    assertEquals(0, unknown.destroyed);
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.awaitClient());
  }

  @Test
  void mclient006StartAndPostContextUnknownAreNotStopSuccess() throws Exception {
    var refusal =
        new MaintenanceUnitStopClient(
            () -> {},
            unit -> {},
            command -> {
              throw new IOException("public start failure");
            });
    var startUnknown = refusal.stop(MaintenanceUnit.CADDY);
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, startUnknown.status());
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, startUnknown.awaitClient());
    var nullChild = new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> null);
    var nullUnknown = nullChild.stop(MaintenanceUnit.CADDY);
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, nullUnknown.status());
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, nullUnknown.awaitClient());
    var process = child();
    int[] checks = {0};
    var result =
        new MaintenanceUnitStopClient(
                () -> {
                  if (++checks[0] == 4) throw new IOException("public changed root");
                },
                unit -> {},
                command -> process)
            .stop(MaintenanceUnit.API);
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status());
    process.allClosed();
    assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.awaitClient());
  }

  @Test
  void mclient012EveryPostInvocationStartFailureRemainsOpaqueUnknown() throws Exception {
    for (Throwable fault :
        List.of(new IllegalStateException("public runtime"), new AssertionError("public error"))) {
      int[] starts = {0};
      var client =
          new MaintenanceUnitStopClient(
              () -> {},
              unit -> {},
              command -> {
                starts[0]++;
                if (fault instanceof RuntimeException runtime) throw runtime;
                throw (Error) fault;
              });
      var result = client.stop(MaintenanceUnit.CADDY);
      assertEquals(1, starts[0]);
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status());
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.awaitClient());
    }
  }

  @Test
  void mclient007InterruptionKeepsOwnerWithoutAutomaticKill() throws Exception {
    var process = child();
    process.waitInterrupt = true;
    var client = new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> process);
    try {
      var result = client.stop(MaintenanceUnit.CADDY);
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, result.status());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(0, process.destroyed);
      Thread.interrupted();
      process.waitInterrupt = false;
      assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, result.awaitClient());
      process.allClosed();
    } finally {
      Thread.interrupted();
    }
    var beforeStdin = child();
    int[] checks = {0};
    try {
      var attempt =
          new MaintenanceUnitStopClient(
                  () -> {
                    if (++checks[0] == 3) Thread.currentThread().interrupt();
                  },
                  unit -> {},
                  command -> beforeStdin)
              .stop(MaintenanceUnit.CADDY);
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, attempt.status());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(0, beforeStdin.input.closed);
      assertEquals(0, beforeStdin.destroyed);
      Thread.interrupted();
      assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
      beforeStdin.allClosed();
    } finally {
      Thread.interrupted();
    }
    var afterWait = child();
    afterWait.hook =
        (name, count) -> {
          if (name.equals("wait") && count == 1) Thread.currentThread().interrupt();
        };
    try {
      var attempt =
          new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> afterWait)
              .stop(MaintenanceUnit.CADDY);
      assertEquals(MaintenanceUnitStopClient.Status.UNKNOWN, attempt.status());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(1, afterWait.input.closed);
      assertEquals(0, afterWait.output.closed);
      assertEquals(0, afterWait.destroyed);
      Thread.interrupted();
      assertEquals(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
      afterWait.allClosed();
    } finally {
      Thread.interrupted();
    }
    int[] starts = {0};
    try {
      Thread.currentThread().interrupt();
      var refusal =
          new MaintenanceUnitStopClient(
              () -> {},
              unit -> {},
              command -> {
                starts[0]++;
                return child();
              });
      assertEquals(
          StopGateFailure.INTERRUPTED,
          assertThrows(StopGateException.class, () -> refusal.stop(MaintenanceUnit.CADDY))
              .reason());
      assertEquals(0, starts[0]);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void mclient008FactoryNullActorAndHarmlessNativeProcessPort() throws Exception {
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitStopClient(null, unit -> {}, command -> child()));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitStopClient(() -> {}, null, command -> child()));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitStopClient(() -> {}, unit -> {}, null));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitStopClient(() -> {}, unit -> {}, command -> child()).stop(null));
    var root = new RootStartupContextTest.Fixture();
    root.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    root.unit = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = root.context();
    var expected = context.capture(RootStartupContext.Service.MORNING);
    assertThrows(
        NullPointerException.class, () -> MaintenanceUnitStopClient.create(null, expected));
    assertThrows(NullPointerException.class, () -> MaintenanceUnitStopClient.create(context, null));
    var wrong =
        new RootStartupContext.Snapshot(
            RootStartupContext.Service.API,
            expected.boot(),
            expected.invocation(),
            expected.pid(),
            expected.startTicks(),
            expected.initStartTicks(),
            expected.controlGroup());
    assertThrows(IOException.class, () -> MaintenanceUnitStopClient.create(context, wrong));
    assertNotNull(MaintenanceUnitStopClient.create(context, expected));
    var child = child();
    var injected =
        MaintenanceUnitStopClient.create(context, expected, unit -> {}, command -> child);
    assertEquals(
        MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO,
        injected.stop(MaintenanceUnit.BACKUP).status());
    child.allClosed();
    // NativeStart is an internal process port; the public stop method always provides fixed
    // systemctl argv. This harmless test never invokes systemctl stop.
    Process process = new MaintenanceUnitStopClient.NativeStart().execute(List.of("/usr/bin/true"));
    assertTrue(process.waitFor(5, TimeUnit.SECONDS));
    assertEquals(0, process.exitValue());
    process.getOutputStream().close();
    process.getInputStream().close();
    process.getErrorStream().close();
  }

  @Test
  void mclient009WholeFixedPolicyPreflightCompletesBeforeAnyStop() throws Exception {
    var sequence = new java.util.ArrayList<String>();
    int[] starts = {0};
    var client =
        new MaintenanceUnitStopClient(
            () -> sequence.add("root"),
            unit -> sequence.add(unit.serviceName()),
            command -> {
              starts[0]++;
              return child();
            });
    client.preflightAll();
    assertEquals(0, starts[0]);
    assertEquals(17, sequence.size());
    assertEquals("root", sequence.getFirst());
    for (int index = 0; index < NAMES.size(); index++) {
      assertEquals(NAMES.get(index), sequence.get(1 + index * 2));
      assertEquals("root", sequence.get(2 + index * 2));
    }
  }

  @Test
  void mclient010MissingLaterUnitRefusesWithoutPartialStop() {
    for (int missing : List.of(0, 3, 7)) {
      int[] checked = {0};
      int[] starts = {0};
      var client =
          new MaintenanceUnitStopClient(
              () -> {},
              unit -> {
                if (checked[0]++ == missing)
                  throw new StopGateException(StopGateFailure.MALFORMED_STATE);
              },
              command -> {
                starts[0]++;
                return child();
              });
      assertEquals(
          StopGateFailure.MALFORMED_STATE,
          assertThrows(StopGateException.class, client::preflightAll).reason());
      assertEquals(missing + 1, checked[0]);
      assertEquals(0, starts[0]);
    }
  }

  @Test
  void mclient011RootFailureAndInterruptRefuseWithoutPolicyOrStop() {
    int[] roots = {0};
    int[] policies = {0};
    int[] starts = {0};
    var client =
        new MaintenanceUnitStopClient(
            () -> {
              if (++roots[0] == 4) throw new IOException("public root changed");
            },
            unit -> policies[0]++,
            command -> {
              starts[0]++;
              return child();
            });
    assertThrows(IOException.class, client::preflightAll);
    assertEquals(4, roots[0]);
    assertEquals(3, policies[0]);
    assertEquals(0, starts[0]);
    try {
      Thread.currentThread().interrupt();
      assertEquals(
          StopGateFailure.INTERRUPTED,
          assertThrows(StopGateException.class, client::preflightAll).reason());
      assertEquals(4, roots[0]);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }
}
