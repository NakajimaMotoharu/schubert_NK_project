package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SS341/343/SSC092/105/106 fixed-argv, intent and unknown-owner vectors; no real Unit start. */
final class BackupUnitStartClientTest {
  @Test
  void monitor001CallerLockCannotBlockOwnedStartStatus() throws Exception {
    var process = child();
    var attempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> process).start();
    dev.codex.schubert.nk.bootstrap.CallerMonitorProbe.requireIndependent(
        attempt,
        () -> assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.status()));
    process.allClosed();
  }

  private static InspectorUnitProbeFixture.Child child() {
    var child = new InspectorUnitProbeFixture.Child(new byte[0]);
    child.waitSeconds = 120;
    return child;
  }

  @Test
  void rootownerfd001CloseOnlyPreservesIntentAndCannotGrantRetirement() throws Exception {
    for (var unit : List.of(MaintenanceUnit.API, MaintenanceUnit.WEB, MaintenanceUnit.CADDY)) {
      var closes = new java.util.concurrent.atomic.AtomicInteger();
      var retires = new java.util.concurrent.atomic.AtomicInteger();
      var process = child();
      var starter =
          new BackupUnitStartClient(
              () -> {},
              () -> {},
              command -> {
                assertEquals(unit.serviceName(), command.getLast());
                return process;
              },
              () ->
                  new BackupUnitStartClient.MarkerLease() {
                    public void retire() {
                      retires.incrementAndGet();
                    }

                    public void closeObservation() {
                      closes.incrementAndGet();
                    }
                  },
              unit,
              java.util.Optional.empty());
      var attempt = starter.start();
      assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.status());
      attempt.preserveObservation();
      assertEquals(1, closes.get());
      assertEquals(0, retires.get());
      assertThrows(IOException.class, attempt::preserveObservation);
      assertThrows(
          IOException.class, () -> attempt.retireAfter(() -> fail("close-only is not retirement")));
      assertEquals(1, closes.get());
      assertEquals(0, retires.get());
      process.allClosed();
    }
  }

  @Test
  void caddy457001BorrowedFenceCloseVerifiesWithoutReleasingAnyServiceOwner() throws Exception {
    var events = new ArrayList<String>();
    var marker = BackupUnitStartClient.caddyFence(() -> events.add("same-live-API-WEB-fence"));
    assertTrue(events.isEmpty());
    marker.requireRetained();
    marker.closeObservation();
    marker.retire();
    assertEquals(
        List.of("same-live-API-WEB-fence", "same-live-API-WEB-fence", "same-live-API-WEB-fence"),
        events);
    assertThrows(NullPointerException.class, () -> BackupUnitStartClient.caddyFence(null));
    for (Throwable failure :
        List.of(
            new IOException("fixed IO"),
            new IllegalStateException("fixed unknown"),
            new AssertionError("fixed fatal"))) {
      var broken =
          BackupUnitStartClient.caddyFence(
              () -> {
                if (failure instanceof IOException io) throw io;
                if (failure instanceof RuntimeException unknown) throw unknown;
                throw (Error) failure;
              });
      assertSame(failure, assertThrows(failure.getClass(), broken::requireRetained));
      assertSame(failure, assertThrows(failure.getClass(), broken::closeObservation));
      assertSame(failure, assertThrows(failure.getClass(), broken::retire));
    }
  }

  @Test
  void caddy457002WorkerRolesCannotCloseServiceObservation() throws Exception {
    for (var unit : MaintenanceUnit.values()) {
      if (List.of(MaintenanceUnit.API, MaintenanceUnit.WEB, MaintenanceUnit.CADDY).contains(unit))
        continue;
      var process = child();
      var attempt =
          new BackupUnitStartClient(
                  () -> {},
                  () -> {},
                  command -> process,
                  () ->
                      new BackupUnitStartClient.MarkerLease() {
                        public void retire() {
                          fail("no retirement");
                        }

                        public void closeObservation() {
                          fail("worker cannot use service close");
                        }
                      },
                  unit,
                  java.util.Optional.empty())
              .start();
      assertThrows(IOException.class, attempt::preserveObservation);
      process.allClosed();
    }
  }

  @Test
  void rootownerfd002UnknownCloseKeepsIdentityAndNeverRetriesConsumedOwner() throws Exception {
    for (Throwable failure :
        List.of(
            new IOException("PUBLIC_IO"),
            new IllegalStateException("PUBLIC_UNKNOWN"),
            new AssertionError("PUBLIC_FATAL"))) {
      var closes = new java.util.concurrent.atomic.AtomicInteger();
      var process = child();
      var starter =
          new BackupUnitStartClient(
              () -> {},
              () -> {},
              command -> process,
              () ->
                  new BackupUnitStartClient.MarkerLease() {
                    public void retire() {
                      fail("preservation never removes marker");
                    }

                    public void closeObservation() throws IOException {
                      closes.incrementAndGet();
                      if (failure instanceof IOException io) throw io;
                      if (failure instanceof RuntimeException unknown) throw unknown;
                      throw (Error) failure;
                    }
                  },
              MaintenanceUnit.API,
              java.util.Optional.empty());
      var attempt = starter.start();
      assertSame(failure, assertThrows(failure.getClass(), attempt::preserveObservation));
      assertThrows(IOException.class, attempt::preserveObservation);
      assertEquals(1, closes.get());
      process.allClosed();
    }
    var ordinary = new BackupUnitStartClient(() -> {}, () -> {}, command -> child()).start();
    assertThrows(IOException.class, ordinary::preserveObservation);
  }

  @Test
  void bstart009IntentPrecedesClientAndUncertainDeliveryPreservesIt() throws Exception {
    var sequence = new ArrayList<String>();
    var process = child();
    var success =
        new BackupUnitStartClient(
            () -> sequence.add("root"),
            () -> sequence.add("policy"),
            command -> {
              sequence.add("client");
              return process;
            },
            () -> {
              sequence.add("intent");
              return () -> sequence.add("retire");
            });
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, success.start().status());
    assertEquals(List.of("root", "policy", "root", "intent", "client", "root", "root"), sequence);
    process.allClosed();

    sequence.clear();
    var failedPublication =
        new BackupUnitStartClient(
            () -> sequence.add("root"),
            () -> sequence.add("policy"),
            command -> fail("no start after uncertain intent publication"),
            () -> {
              sequence.add("intent-unknown");
              throw new IOException("test-only publication uncertainty");
            });
    assertThrows(IOException.class, failedPublication::start);
    assertEquals(List.of("root", "policy", "root", "intent-unknown"), sequence);

    sequence.clear();
    var uncertainStart =
        new BackupUnitStartClient(
            () -> sequence.add("root"),
            () -> sequence.add("policy"),
            command -> {
              sequence.add("client-unknown");
              throw new IOException("test-only unknown delivery");
            },
            () -> {
              sequence.add("intent");
              return () -> sequence.add("retire");
            });
    assertEquals(BackupUnitStartClient.Status.UNKNOWN, uncertainStart.start().status());
    assertEquals(List.of("root", "policy", "root", "intent", "client-unknown"), sequence);
    assertThrows(
        NullPointerException.class,
        () -> new BackupUnitStartClient(() -> {}, () -> {}, command -> child(), null));
  }

  @Test
  void bstart010RetainedMarkerRequiresCompleteParentProof() throws Exception {
    var sequence = new ArrayList<String>();
    var process = child();
    var attempt =
        new BackupUnitStartClient(
                () -> sequence.add("root"),
                () -> {},
                command -> process,
                () -> {
                  sequence.add("publish");
                  return () -> sequence.add("retire");
                })
            .start();
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.status());
    assertEquals(List.of("root", "root", "publish", "root", "root"), sequence);
    assertThrows(
        IOException.class,
        () ->
            attempt.retireAfter(
                () -> {
                  sequence.add("not-complete");
                  throw new IOException("worker not terminal");
                }));
    assertFalse(sequence.contains("retire"));
    attempt.retireAfter(() -> sequence.add("full-parent-proof"));
    assertEquals("retire", sequence.getLast());
    assertEquals(1, sequence.stream().filter("retire"::equals).count());
    assertThrows(IOException.class, () -> attempt.retireAfter(() -> fail("cannot repeat")));
    process.allClosed();

    var unknown =
        new BackupUnitStartClient(
                () -> {},
                () -> {},
                command -> {
                  throw new IOException("uncertain delivery");
                },
                () -> () -> fail("unknown marker must remain"))
            .start();
    assertEquals(BackupUnitStartClient.Status.UNKNOWN, unknown.status());
    assertThrows(IOException.class, () -> unknown.retireAfter(() -> fail("no proof on unknown")));
    var nonzero = child();
    nonzero.code = 1;
    var rejected = new BackupUnitStartClient(() -> {}, () -> {}, command -> nonzero).start();
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_NONZERO, rejected.status());
    assertThrows(IOException.class, () -> rejected.retireAfter(() -> fail("no proof on nonzero")));
    nonzero.allClosed();
  }

  @Test
  void bstart011PostPublicationInterruptRetainsMarkerWithoutClient() throws Exception {
    int[] starts = {0};
    int[] retires = {0};
    try {
      var attempt =
          new BackupUnitStartClient(
                  () -> {},
                  () -> {},
                  command -> {
                    starts[0]++;
                    return child();
                  },
                  () -> {
                    Thread.currentThread().interrupt();
                    return () -> retires[0]++;
                  })
              .start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(0, starts[0]);
      assertEquals(0, retires[0]);
      assertThrows(
          IOException.class, () -> attempt.retireAfter(() -> fail("unknown cannot retire")));
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void bstart012ProofDriftReentryAndRetireFailureStayFailClosed() throws Exception {
    int[] rootChecks = {0};
    int[] retires = {0};
    var process = child();
    var attempt =
        new BackupUnitStartClient(
                () -> rootChecks[0]++, () -> {}, command -> process, () -> () -> retires[0]++)
            .start();
    assertThrows(NullPointerException.class, () -> attempt.retireAfter(null));
    assertThrows(
        IOException.class,
        () -> attempt.retireAfter(() -> attempt.retireAfter(() -> fail("reentry"))));
    assertEquals(0, retires[0]);
    int before = rootChecks[0];
    attempt.retireAfter(() -> assertEquals(before + 1, rootChecks[0]));
    assertEquals(1, retires[0]);
    process.allClosed();

    var failed = child();
    int[] failedRetires = {0};
    var failedAttempt =
        new BackupUnitStartClient(
                () -> {},
                () -> {},
                command -> failed,
                () ->
                    () -> {
                      failedRetires[0]++;
                      throw new IOException("retire storage uncertainty");
                    })
            .start();
    assertThrows(IOException.class, () -> failedAttempt.retireAfter(() -> {}));
    assertThrows(IOException.class, () -> failedAttempt.retireAfter(() -> {}));
    assertEquals(1, failedRetires[0]);
    failed.allClosed();
  }

  @Test
  void bstart001FixedCommandAndOwnerOrder() throws Exception {
    var process = child();
    var sequence = new ArrayList<String>();
    var client =
        new BackupUnitStartClient(
            () -> sequence.add("root"),
            () -> sequence.add("policy"),
            command -> {
              assertEquals(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "--no-block",
                      "start",
                      "schubert-nk-backup.service"),
                  command);
              sequence.add("client");
              return process;
            });
    var attempt = client.start();
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.status());
    assertEquals(List.of("root", "policy", "root", "client", "root", "root"), sequence);
    process.allClosed();
    assertEquals(0, process.destroyed);
    assertEquals(1, process.counts.get("wait"));
  }

  @Test
  void bstart002PreStartPolicyRootAndInterruptRefuseWithoutClient() {
    int[] launched = {0};
    var policy =
        new BackupUnitStartClient(
            () -> {},
            () -> {
              throw new StopGateException(StopGateFailure.MALFORMED_STATE);
            },
            command -> {
              launched[0]++;
              return child();
            });
    assertEquals(
        StopGateFailure.MALFORMED_STATE,
        assertThrows(StopGateException.class, policy::start).reason());
    for (int failureAt : List.of(1, 2)) {
      int[] checks = {0};
      var changed =
          new BackupUnitStartClient(
              () -> {
                if (++checks[0] == failureAt) throw new IOException("public changed root");
              },
              () -> {},
              command -> {
                launched[0]++;
                return child();
              });
      assertThrows(IOException.class, changed::start);
      assertEquals(failureAt, checks[0]);
    }
    try {
      Thread.currentThread().interrupt();
      assertEquals(
          StopGateFailure.INTERRUPTED,
          assertThrows(StopGateException.class, policy::start).reason());
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    assertEquals(0, launched[0]);
  }

  @Test
  void bstart003NonzeroIsNotWorkerSuccess() throws Exception {
    var process = child();
    process.code = 1;
    var attempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> process).start();
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_NONZERO, attempt.status());
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_NONZERO, attempt.awaitClient());
    process.allClosed();
    assertEquals(0, process.destroyed);
  }

  @Test
  void bstart004TimeoutRetainsSameChildUntilActualReap() throws Exception {
    var process = child();
    process.completed = false;
    int[] starts = {0};
    var attempt =
        new BackupUnitStartClient(
                () -> {},
                () -> {},
                command -> {
                  starts[0]++;
                  return process;
                })
            .start();
    assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status());
    assertTrue(process.alive);
    assertEquals(0, process.destroyed);
    assertEquals(1, process.input.closed);
    assertEquals(0, process.output.closed);
    process.completed = true;
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
    assertEquals(1, starts[0]);
    assertEquals(2, process.counts.get("wait"));
    process.allClosed();
  }

  @Test
  void bstart005CloseGetterAndSpawnUnknownNeverUpgrade() throws Exception {
    for (String fault : List.of("stdin.close", "stdout.close", "stderr.close")) {
      var process = child();
      process.ioFailures.add(fault);
      var attempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> process).start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status(), fault);
      process.ioFailures.clear();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.awaitClient(), fault);
      assertEquals(0, process.destroyed);
    }
    for (String missing : List.of("stdin", "stdout", "stderr")) {
      var process = child();
      process.missing = missing;
      var attempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> process).start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status(), missing);
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.awaitClient(), missing);
      assertEquals(0, process.destroyed);
    }
    for (Throwable failure :
        List.of(
            new IOException("public uncertain delivery"),
            new IllegalStateException("public runtime"),
            new AssertionError("public error"))) {
      var attempt =
          new BackupUnitStartClient(
                  () -> {},
                  () -> {},
                  command -> {
                    if (failure instanceof IOException io) throw io;
                    if (failure instanceof RuntimeException runtime) throw runtime;
                    throw (Error) failure;
                  })
              .start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status());
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.awaitClient());
    }
    var nullAttempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> null).start();
    assertEquals(BackupUnitStartClient.Status.UNKNOWN, nullAttempt.awaitClient());
  }

  @Test
  void bstart006InterruptAndPostStartContextUnknownRetainOwner() throws Exception {
    var process = child();
    process.waitInterrupt = true;
    try {
      var attempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> process).start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status());
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(0, process.destroyed);
      Thread.interrupted();
      process.waitInterrupt = false;
      assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
      process.allClosed();
    } finally {
      Thread.interrupted();
    }
    var beforeStdin = child();
    int[] checks = {0};
    try {
      var attempt =
          new BackupUnitStartClient(
                  () -> {
                    if (++checks[0] == 3) Thread.currentThread().interrupt();
                  },
                  () -> {},
                  command -> beforeStdin)
              .start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status());
      assertEquals(0, beforeStdin.input.closed);
      Thread.interrupted();
      assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
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
      var attempt = new BackupUnitStartClient(() -> {}, () -> {}, command -> afterWait).start();
      assertEquals(BackupUnitStartClient.Status.UNKNOWN, attempt.status());
      assertEquals(0, afterWait.output.closed);
      Thread.interrupted();
      assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
      afterWait.allClosed();
    } finally {
      Thread.interrupted();
    }
    var changed = child();
    int[] roots = {0};
    var poisoned =
        new BackupUnitStartClient(
                () -> {
                  if (++roots[0] == 4) throw new IOException("public root drift");
                },
                () -> {},
                command -> changed)
            .start();
    assertEquals(BackupUnitStartClient.Status.UNKNOWN, poisoned.status());
    assertEquals(BackupUnitStartClient.Status.UNKNOWN, poisoned.awaitClient());
    changed.allClosed();
  }

  @Test
  void bstart007FactoryNullWrongActorAndNativePort() throws Exception {
    assertThrows(
        NullPointerException.class, () -> new BackupUnitStartClient(null, () -> {}, c -> child()));
    assertThrows(
        NullPointerException.class, () -> new BackupUnitStartClient(() -> {}, null, c -> child()));
    assertThrows(
        NullPointerException.class, () -> new BackupUnitStartClient(() -> {}, () -> {}, null));
    var root = new RootStartupContextTest.Fixture();
    root.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    root.unit = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = root.context();
    var expected = context.capture(RootStartupContext.Service.MORNING);
    var safePolicy =
        new MaintenanceUnitStopPolicy(
            unit -> {
              assertSame(MaintenanceUnit.BACKUP, unit);
              return ("Id=schubert-nk-backup.service\n"
                      + "LoadState=loaded\nKillMode=control-group\nSendSIGKILL=no\n")
                  .getBytes(StandardCharsets.US_ASCII);
            });
    assertThrows(NullPointerException.class, () -> BackupUnitStartClient.create(null, expected));
    assertThrows(NullPointerException.class, () -> BackupUnitStartClient.create(context, null));
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitStartClient.create(context, expected, null, c -> child()));
    assertThrows(
        NullPointerException.class,
        () -> BackupUnitStartClient.create(context, expected, safePolicy, null));
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
        () -> BackupUnitStartClient.create(context, wrong, safePolicy, c -> child()));
    assertNotNull(BackupUnitStartClient.create(context, expected));
    var child = child();
    var injected = BackupUnitStartClient.create(context, expected, safePolicy, c -> child);
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, injected.start().status());
    child.allClosed();
    Process harmless =
        new MaintenanceUnitStopClient.NativeStart().execute(List.of("/usr/bin/true"));
    assertTrue(harmless.waitFor(5, TimeUnit.SECONDS));
    assertEquals(0, harmless.exitValue());
    harmless.getOutputStream().close();
    harmless.getInputStream().close();
    harmless.getErrorStream().close();
  }

  @Test
  void bstart008TerminalMonotonicAndNoWorkerReceipt() throws Exception {
    var child = child();
    int[] spawns = {0};
    var attempt =
        new BackupUnitStartClient(
                () -> {},
                () -> {},
                command -> {
                  spawns[0]++;
                  return child;
                })
            .start();
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.status());
    assertEquals(BackupUnitStartClient.Status.CLIENT_EXITED_ZERO, attempt.awaitClient());
    assertEquals(1, spawns[0]);
    assertEquals(1, child.counts.get("wait"));
    child.allClosed();
    // No Unit state or backup artifact is present in this fixture. The client exposes only an
    // opaque command result, and parent fresh-Invocation/full-process/archive gates remain open.
  }
}
