package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

  /** 1872: new selected methods below do not install hooks or invoke this historical TERM case. */
  @Test
  void lifeBudget001() {
    assertThrows(NullPointerException.class, () -> new ApiProcessLifetime(null));
  }

  @Test
  void lifeBudget002() {
    var reads = new AtomicInteger();
    try (var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return 0;
            })) {
      assertFalse(lifetime.stopping());
      assertThrows(IllegalStateException.class, lifetime::remainingStopNanos);
      assertEquals(0, reads.get());
    }
    assertEquals(1, reads.get());
  }

  @Test
  void lifeBudget003() {
    var time = new java.util.concurrent.atomic.AtomicLong(100);
    var reads = new AtomicInteger();
    try (var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return time.get();
            })) {
      lifetime.stop();
      assertTrue(lifetime.stopping());
      time.set(109);
      lifetime.stop();
      assertEquals(1, reads.get());
      assertEquals(59_999_999_991L, lifetime.remainingStopNanos());
    }
    assertEquals(2, reads.get());
  }

  @Test
  void lifeBudget004() {
    try (var lifetime = new ApiProcessLifetime(() -> 0)) {
      lifetime.fail();
      assertTrue(lifetime.stopping());
      assertEquals(60_000_000_000L, lifetime.remainingStopNanos());
      assertEquals(
          "API runtime unavailable",
          assertThrows(
                  IOException.class,
                  () ->
                      lifetime.await(
                          () -> {
                            throw new AssertionError("stopped health");
                          }))
              .getMessage());
    }
  }

  @Test
  void lifeBudget005() {
    var time = new java.util.concurrent.atomic.AtomicLong();
    var reads = new AtomicInteger();
    var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return time.get();
            });
    try {
      lifetime.close();
      time.set(29);
      lifetime.close();
      lifetime.shutdown(); // Owner itself never waits; no hook is installed.
      assertEquals(59_999_999_971L, lifetime.remainingStopNanos());
      assertEquals(2, reads.get());
    } finally {
      lifetime.close();
    }
  }

  @Test
  void lifeBudget006() {
    for (RuntimeException primary :
        List.of(new IllegalStateException("clock"), new NullPointerException("clock contract"))) {
      var reads = new AtomicInteger();
      try (var lifetime =
          new ApiProcessLifetime(
              () -> {
                reads.incrementAndGet();
                throw primary;
              })) {
        assertSame(primary, assertThrows(primary.getClass(), lifetime::stop));
        assertTrue(lifetime.stopping());
        assertEquals(0, lifetime.remainingStopNanos());
        lifetime.stop();
        assertEquals(1, reads.get());
      }
    }
  }

  @Test
  void lifeBudget007() throws Exception {
    var fatal = new AssertionError("clock");
    var lifetime =
        new ApiProcessLifetime(
            () -> {
              throw fatal;
            });
    assertSame(fatal, assertThrows(AssertionError.class, lifetime::close));
    assertTrue(lifetime.stopping());
    assertEquals(0, lifetime.remainingStopNanos());
    try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {
      var finished = executor.submit(lifetime::shutdown);
      try {
        finished.get(3, TimeUnit.SECONDS); // close's finally must already have notified this owner.
      } finally {
        lifetime.close(); // Fixture-only fallback if the new finally contract fails.
      }
    }
  }

  @Test
  void lifeBudget008() {
    var reads = new AtomicInteger();
    try (var lifetime =
        new ApiProcessLifetime(
            () -> {
              reads.incrementAndGet();
              return 0;
            })) {
      assertEquals(
          "API runtime unavailable",
          assertThrows(IOException.class, () -> lifetime.await(() -> false)).getMessage());
      assertTrue(lifetime.stopping());
      assertEquals(60_000_000_000L, lifetime.remainingStopNanos());
    }
    assertEquals(2, reads.get());
  }

  @Test
  void lifeBudget009() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var reads = new AtomicInteger();
    try (var lifetime =
            new ApiProcessLifetime(
                () -> {
                  reads.incrementAndGet();
                  entered.countDown();
                  try {
                    assertTrue(release.await(5, TimeUnit.SECONDS));
                  } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new AssertionError(interrupted);
                  }
                  return 0;
                });
        var executor = java.util.concurrent.Executors.newFixedThreadPool(2)) {
      var first = executor.submit(lifetime::stop);
      java.util.concurrent.Future<?> second;
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        assertTrue(lifetime.stopping()); // Notification precedes the clock port, not its return.
        second = executor.submit(lifetime::stop);
      } finally {
        release.countDown();
      }
      first.get(5, TimeUnit.SECONDS);
      second.get(5, TimeUnit.SECONDS);
      assertEquals(1, reads.get());
      assertEquals(60_000_000_000L, lifetime.remainingStopNanos());
    }
    assertEquals(2, reads.get());
  }

  @Test
  void lifeBudget010() {
    try (var lifetime = new ApiProcessLifetime()) {
      lifetime.stop();
      long remaining = lifetime.remainingStopNanos();
      assertTrue(remaining >= 0 && remaining <= 60_000_000_000L);
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
