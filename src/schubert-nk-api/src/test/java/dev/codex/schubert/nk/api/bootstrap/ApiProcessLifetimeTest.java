package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.DeliveryMetadata;
import dev.codex.schubert.nk.api.messaging.inbound.InternalEventProcessor;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** Component owner/stop tests, not native main invocation or authority. READY004..006. */
final class ApiProcessLifetimeTest {
  /** Actual JVM TERM of this component, not a substitute for admitted ApiProcessMain. */
  public static final class HookDriver {
    public static void main(String[] arguments) throws Exception {
      var dumped = new CountDownLatch(1);
      Runtime.getRuntime()
          .addShutdownHook(
              new Thread(
                  () -> {
                    try {
                      dumped.await();
                    } catch (InterruptedException interrupted) {
                      Thread.currentThread().interrupt();
                    }
                  },
                  "component-coverage-drain"));
      try {
        try (var lifetime = new ApiProcessLifetime()) {
          lifetime.install();
          System.out.println("LIFETIME_START");
          lifetime.await(() -> true);
          System.out.println("LIFETIME_WHOLE_OWNER_RETURNED");
        }
        // Agent's automatic hook can run before application cleanup. Capture real late counters,
        // not a fabricated native Main invocation; only this test driver references agent runtime.
        Object agent = Class.forName("org.jacoco.agent.rt.RT").getMethod("getAgent").invoke(null);
        Class.forName("org.jacoco.agent.rt.IAgent")
            .getMethod("dump", boolean.class)
            .invoke(agent, false);
      } finally {
        dumped.countDown();
      }
    }
  }

  @Test
  void ready006ActualJvmTermWaitsMainOwnerAndNeverSelfExits() throws Exception {
    var command = new java.util.ArrayList<String>();
    command.add(java.nio.file.Path.of(System.getProperty("java.home"), "bin", "java").toString());
    for (String option :
        java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments())
      if (option.startsWith("-javaagent:")) command.add(option);
    command.add("-cp");
    command.add(System.getProperty("surefire.test.class.path"));
    command.add(HookDriver.class.getName());
    var process = new ProcessBuilder(command).start();
    try (var reader = process.inputReader();
        var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {
      assertEquals("LIFETIME_START", executor.submit(reader::readLine).get(5, TimeUnit.SECONDS));
      var term = new ProcessBuilder("/usr/bin/kill", "-TERM", Long.toString(process.pid())).start();
      assertTrue(term.waitFor(5, TimeUnit.SECONDS));
      assertEquals(0, term.exitValue());
      assertTrue(process.waitFor(5, TimeUnit.SECONDS));
      assertEquals(143, process.exitValue());
      assertEquals("LIFETIME_WHOLE_OWNER_RETURNED", reader.readLine());
      assertNull(reader.readLine());
      assertEquals(
          "",
          new String(
              process.getErrorStream().readAllBytes(), java.nio.charset.StandardCharsets.UTF_8));
    } finally {
      if (process.isAlive()) {
        process.destroyForcibly();
        assertTrue(process.waitFor(5, TimeUnit.SECONDS));
      }
    }
  }

  private static WireMessage<FixedPayload> event() {
    return new WireMessage<>(
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("QWKREQ01"),
            1,
            MessageKind.EVENT,
            InteractionKind.INTERNAL,
            UUID.fromString("00000000-0000-0000-0000-000000000001"),
            UUID.fromString("00000000-0000-0000-0000-000000000002"),
            Instant.parse("2026-10-02T00:00:00Z"),
            Optional.empty(),
            256,
            64,
            0,
            0,
            320,
            Optional.empty()),
        new FixedPayload(new byte[64], 0, List.of()));
  }

  @Test
  void ready004BorrowedDelegatesStopGuardAndActualDeliveryPreserved() {
    var calls = new AtomicInteger();
    var event = event();
    var metadata = new DeliveryMetadata(4, "ID:independent", Instant.parse("2026-10-02T00:00:00Z"));
    try (var lifetime = new ApiProcessLifetime()) {
      var sync =
          lifetime.guardSync(
              (dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor)
                  request -> {
                    assertSame(event, request);
                    calls.incrementAndGet();
                    return new byte[] {1, 2};
                  });
      var internal =
          lifetime.guardEvent(
              new InternalEventProcessor() {
                public void process(WireMessage<FixedPayload> value) {
                  assertSame(event, value);
                  calls.incrementAndGet();
                }

                public void process(WireMessage<FixedPayload> value, DeliveryMetadata delivery) {
                  assertSame(event, value);
                  assertSame(metadata, delivery);
                  calls.incrementAndGet();
                }
              });
      assertFalse(lifetime.stopping());
      assertArrayEquals(new byte[] {1, 2}, sync.process(event));
      internal.process(event);
      internal.process(event, metadata);
      assertEquals(3, calls.get());
      assertThrows(
          NullPointerException.class, () -> lifetime.guardEvent((InternalEventProcessor) null));
      assertThrows(
          NullPointerException.class,
          () ->
              lifetime.guardSync(
                  (dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor) null));
      lifetime.stop();
      assertThrows(TemporaryInfrastructureException.class, () -> sync.process(event));
      assertThrows(TemporaryInfrastructureException.class, () -> internal.process(event));
      assertThrows(TemporaryInfrastructureException.class, () -> internal.process(event, metadata));
      assertEquals(3, calls.get());
    }
  }

  @Test
  void ready005HealthFailureInterruptedAndNormalStopDistinct() throws Exception {
    try (var lifetime = new ApiProcessLifetime()) {
      assertThrows(NullPointerException.class, () -> lifetime.await(null));
      assertThrows(IOException.class, () -> lifetime.await(() -> false));
      assertTrue(lifetime.stopping());
    }
    try (var lifetime = new ApiProcessLifetime()) {
      Thread.currentThread().interrupt();
      assertThrows(IOException.class, () -> lifetime.await(() -> true));
      assertTrue(Thread.interrupted());
    }
    try (var lifetime = new ApiProcessLifetime()) {
      var checks = new AtomicInteger();
      lifetime.await(
          () -> {
            if (checks.incrementAndGet() == 2) lifetime.stop();
            return true;
          });
      assertEquals(2, checks.get());
    }
    try (var lifetime = new ApiProcessLifetime()) {
      lifetime.shutdown(); // Same owner never waits for itself.
      lifetime.await(
          () -> {
            throw new AssertionError("stopped health must not run");
          });
    }
  }

  @Test
  void ready006HookWaitsOuterOwnerAndRestoresInterrupt() throws Exception {
    var lifetime = new ApiProcessLifetime();
    var entered = new CountDownLatch(1);
    var returned = new CountDownLatch(1);
    var thread =
        new Thread(
            () -> {
              Thread.currentThread().interrupt();
              entered.countDown();
              lifetime.shutdown();
              assertTrue(Thread.interrupted());
              returned.countDown();
            });
    thread.start();
    assertTrue(entered.await(3, TimeUnit.SECONDS));
    assertFalse(returned.await(30, TimeUnit.MILLISECONDS));
    lifetime.close();
    assertTrue(returned.await(3, TimeUnit.SECONDS));
    thread.join(3000);
    assertFalse(thread.isAlive());
    lifetime.close();
    try (var installed = new ApiProcessLifetime()) {
      installed.install(); // Actual native Runtime registration/removal without VM termination.
    }
  }
}
