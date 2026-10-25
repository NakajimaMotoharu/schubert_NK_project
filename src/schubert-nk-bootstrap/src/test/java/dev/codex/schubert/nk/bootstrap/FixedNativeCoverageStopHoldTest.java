package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTimeoutPreemptively;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * Independent shutdown/capture ordering, including a real host TERM143 child; not app native PT.
 */
final class FixedNativeCoverageStopHoldTest {
  @Test
  void nhold194001NullDuplicateAndClosedInstallNeverIssueTwice() throws Exception {
    assertThrows(IllegalArgumentException.class, () -> new FixedNativeCoverageStopHold(null));
    var calls = new Calls();
    var hold = new FixedNativeCoverageStopHold(calls);
    assertThrows(IllegalStateException.class, hold::verifyOwner);
    hold.shutdown(); // Owner thread must not wait on itself.
    hold.install();
    assertDoesNotThrow(hold::verifyOwner);
    try (var foreign = Executors.newSingleThreadExecutor()) {
      foreign
          .submit(() -> assertThrows(IllegalStateException.class, hold::verifyOwner))
          .get(2, TimeUnit.SECONDS);
    }
    assertThrows(IllegalStateException.class, hold::install);
    hold.close();
    hold.close();
    assertThrows(IllegalStateException.class, hold::verifyOwner);
    assertEquals(1, calls.adds);
    assertEquals(1, calls.removes);
    assertThrows(IllegalStateException.class, hold::install);
    var untouched = new Calls();
    var closed = new FixedNativeCoverageStopHold(untouched);
    closed.close();
    assertThrows(IllegalStateException.class, closed::install);
    assertEquals(0, untouched.adds);
    assertEquals(0, untouched.removes);
  }

  @Test
  void nhold194002OldApplicationFinishCannotReleaseOuterCaptureHold() throws Exception {
    var calls = new Calls();
    var hold = new FixedNativeCoverageStopHold(calls);
    hold.install();
    var completed = new CountDownLatch(1);
    var waiter =
        new Thread(
            () -> {
              hold.shutdown();
              completed.countDown();
            });
    waiter.start();
    try {
      waiting(waiter);
      var oldApplicationFinished = new CountDownLatch(1);
      oldApplicationFinished.countDown();
      assertEquals(0, oldApplicationFinished.getCount());
      assertFalse(
          completed.await(50, TimeUnit.MILLISECONDS), "old finished must not release capture");
      calls.removal = FixedNativeCoverageStopHold.Removal.SHUTTING_DOWN;
      hold.close();
      assertTrue(completed.await(2, TimeUnit.SECONDS));
      waiter.join(2000);
      assertFalse(waiter.isAlive());
      assertEquals(1, calls.removes);
    } finally {
      hold.close();
      waiter.join(2000);
    }
  }

  @Test
  void nhold194003InterruptedHookKeepsWaitingAndRestoresInterrupt() throws Exception {
    var hold = new FixedNativeCoverageStopHold(new Calls());
    hold.install();
    var restored = new AtomicBoolean();
    var waiter =
        new Thread(
            () -> {
              hold.shutdown();
              restored.set(Thread.currentThread().isInterrupted());
            });
    waiter.start();
    try {
      waiting(waiter);
      waiter.interrupt();
      long end = System.nanoTime() + TimeUnit.SECONDS.toNanos(2);
      while (waiter.isInterrupted() && System.nanoTime() < end) Thread.yield();
      assertFalse(waiter.isInterrupted());
      waiting(waiter);
      hold.close();
      waiter.join(2000);
      assertFalse(waiter.isAlive());
      assertTrue(restored.get());
    } finally {
      hold.close();
      waiter.join(2000);
    }
  }

  @Test
  void nhold194004RemoveNullNotOwnedUnknownAndAddFailureAreNotNormalizedOrRetried() {
    for (var result : Arrays.asList(null, FixedNativeCoverageStopHold.Removal.NOT_OWNED)) {
      var calls = new Calls();
      calls.removal = result;
      var hold = new FixedNativeCoverageStopHold(calls);
      hold.install();
      assertThrows(IllegalStateException.class, hold::close);
      hold.close();
      assertEquals(1, calls.removes);
    }
    var original = new UnsupportedOperationException("synthetic hook unknown");
    var add = new Calls();
    add.failure = original;
    var failed = new FixedNativeCoverageStopHold(add);
    assertSame(original, assertThrows(UnsupportedOperationException.class, failed::install));
    assertThrows(IllegalStateException.class, failed::install);
    assertEquals(1, add.adds);
    add.failure = null;
    failed.close();
    var remove = new Calls();
    var hold = new FixedNativeCoverageStopHold(remove);
    hold.install();
    remove.failure = original;
    assertSame(original, assertThrows(UnsupportedOperationException.class, hold::close));
    hold.close();
    assertEquals(1, remove.removes);
  }

  @Test
  void nhold194005RealRuntimeNormalAndNotOwnedRemovalAreDistinct() {
    var hold = FixedNativeCoverageStopHold.open();
    assertDoesNotThrow(hold::verifyOwner);
    hold.close();
    assertDoesNotThrow(hold::close);
    assertThrows(
        IllegalArgumentException.class, () -> FixedNativeCoverageStopHold.removeNative(null));
    var owned = new Thread(() -> fail("ordinary component hook must not run"));
    Runtime.getRuntime().addShutdownHook(owned);
    assertEquals(
        FixedNativeCoverageStopHold.Removal.REMOVED,
        FixedNativeCoverageStopHold.removeNative(owned));
    assertEquals(
        FixedNativeCoverageStopHold.Removal.NOT_OWNED,
        FixedNativeCoverageStopHold.removeNative(owned));
  }

  @Test
  void nhold194006RealHostTermCannotHaltBetweenOldHookAndCapture() {
    assertTimeoutPreemptively(
        Duration.ofSeconds(15),
        () -> {
          String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
          // PG1271 coordinates showed that the already-real TERM probe's child was
          // outside Surefire capture. Preserve its independent behavior oracle;
          // instrument only this newly owned host test JVM with the same agent.
          // This is not app/native evidence or a synthetic call to removeNative.
          var child =
              new ProcessBuilder(
                      java,
                      sameRunCoverageAgent(),
                      "-cp",
                      System.getProperty("java.class.path"),
                      FixedNativeCoverageStopHoldProbe.class.getName())
                  .redirectErrorStream(true)
                  .start();
          try (var input = child.inputReader(StandardCharsets.UTF_8);
              var command = child.getOutputStream()) {
            assertEquals("READY", input.readLine());
            // ProcessHandle sends TERM without Process.destroy's eager stdio closure.
            assertTrue(child.toHandle().destroy()); // Only this new child, never an application/VM.
            var observed = new HashSet<String>();
            for (int n = 0; n < 2; n++) observed.add(input.readLine());
            assertEquals(Set.of("OLD_HOOK_RETURNED", "APPLICATION_SCOPES_RETURNED"), observed);
            assertTrue(child.isAlive(), "real TERM must wait for outer capture, not just old hook");
            command.write('C');
            command.flush();
            assertEquals("CAPTURE_COMPLETE", input.readLine());
            assertTrue(child.waitFor(5, TimeUnit.SECONDS));
            assertEquals(143, child.exitValue(), "143 must not be normalized to zero");
          } finally {
            if (child.isAlive()) {
              child.destroyForcibly();
              child.waitFor(5, TimeUnit.SECONDS);
            }
          }
        });
  }

  @Test
  void nhold194007RealShutdownRefusalIsCapturedAfterTheActualRemoval() {
    assertTimeoutPreemptively(
        Duration.ofSeconds(15),
        () -> {
          String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
          var child =
              new ProcessBuilder(
                      java,
                      sameRunCoverageAgent(),
                      "-cp",
                      System.getProperty("java.class.path"),
                      FixedNativeCoverageRemovalDuringShutdownProbe.class.getName())
                  .redirectErrorStream(true)
                  .start();
          try (var input = child.inputReader(StandardCharsets.UTF_8);
              var command = child.getOutputStream()) {
            assertEquals("READY", input.readLine());
            assertTrue(child.toHandle().destroy());
            assertEquals("SHUTDOWN_STARTED", input.readLine());
            assertTrue(child.isAlive(), "owned witness permits observing real shutdown refusal");
            command.write('C');
            command.flush();
            assertEquals("REMOVAL_SHUTTING_DOWN_CAPTURED", input.readLine());
            assertTrue(child.waitFor(5, TimeUnit.SECONDS));
            assertEquals(143, child.exitValue(), "TERM is not normalized to normal exit");
          } finally {
            if (child.isAlive()) {
              child.destroyForcibly();
              child.waitFor(5, TimeUnit.SECONDS);
            }
          }
        });
  }

  private static String sameRunCoverageAgent() {
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(value -> value.startsWith("-javaagent:") && value.contains("jacoco"))
            .toList();
    assertEquals(1, agents.size(), "same-run Surefire JaCoCo agent required");
    return agents.getFirst();
  }

  private static void waiting(Thread thread) throws Exception {
    long end = System.nanoTime() + TimeUnit.SECONDS.toNanos(2);
    while (thread.getState() != Thread.State.WAITING && System.nanoTime() < end) Thread.yield();
    assertEquals(Thread.State.WAITING, thread.getState());
  }

  private static final class Calls implements FixedNativeCoverageStopHold.Calls {
    FixedNativeCoverageStopHold.@Nullable Removal removal =
        FixedNativeCoverageStopHold.Removal.REMOVED;
    @Nullable RuntimeException failure;
    int adds;
    int removes;

    @Override
    public void add(Thread hook) {
      adds++;
      if (failure != null) throw failure;
    }

    @Override
    public FixedNativeCoverageStopHold.@Nullable Removal remove(Thread hook) {
      removes++;
      if (failure != null) throw failure;
      return removal;
    }
  }
}
