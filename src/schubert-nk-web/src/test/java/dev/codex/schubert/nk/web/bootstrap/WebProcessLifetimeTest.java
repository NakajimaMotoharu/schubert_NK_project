package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NATIVE-LIFE001..004: notification never substitutes for confirmed resource completion. */
final class WebProcessLifetimeTest {
  @TempDir Path temporary;

  @Test
  void life004OwnedJvmTermClosesWhileShutdownIsInProgress() throws Exception {
    var command = new ArrayList<String>();
    command.add(
        Path.of(Objects.requireNonNull(System.getProperty("java.home")), "bin/java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(value -> value.startsWith("-javaagent:") && value.contains("jacoco"))
            .toList();
    assertFalse(agents.isEmpty(), "same-run child coverage agent is mandatory, not skipped");
    command.addAll(agents);
    command.addAll(
        List.of(
            "-cp",
            Objects.requireNonNull(System.getProperty("surefire.test.class.path")),
            HookDriver.class.getName()));
    Path out = Files.createTempFile(temporary, "lifetime-", ".out");
    Path err = Files.createTempFile(temporary, "lifetime-", ".err");
    var builder =
        new ProcessBuilder(command).redirectOutput(out.toFile()).redirectError(err.toFile());
    builder.environment().clear();
    Process child = builder.start();
    try {
      long until = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
      while (!Files.readString(out).contains("WEB_COMPONENT_READY\n")
          && child.isAlive()
          && System.nanoTime() < until) Thread.sleep(5);
      assertEquals("WEB_COMPONENT_READY\n", Files.readString(out));
      assertTrue(child.isAlive());
      child.destroy(); // Only this ProcessBuilder-owned fixture; never a service or numeric PID.
      assertTrue(
          child.waitFor(5, TimeUnit.SECONDS), "owned fixture must finish within its deadline");
      assertEquals(143, child.exitValue(), "actual Linux SIGTERM; not a Root success code");
      assertEquals("WEB_COMPONENT_READY\nWEB_COMPONENT_CLOSED\n", Files.readString(out));
      assertEquals("", Files.readString(err));
      assertFalse(child.isAlive());
    } finally {
      if (child.isAlive()) {
        child.destroyForcibly();
        assertTrue(child.waitFor(5, TimeUnit.SECONDS), "only owned fixture cleanup");
      }
    }
  }

  /** No application Main, providers, network, credentials, VM or borrowed scope. */
  public static final class HookDriver {
    private HookDriver() {}

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
                  "fixture-coverage-drain"));
      try {
        try (var lifetime = new WebProcessLifetime()) {
          lifetime.install();
          System.out.println("WEB_COMPONENT_READY");
          lifetime.await(() -> true);
        }
        System.out.println("WEB_COMPONENT_CLOSED");
        // Public agent API captures real post-close probes if its automatic hook ran early.
        // This instrumentation barrier is not proof of native provider ownership or cleanup.
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
  void monitor004CallerLockCannotBlockConfirmedLifetimeClose() throws Exception {
    var lifetime = new WebProcessLifetime();
    try {
      dev.codex.schubert.nk.bootstrap.CallerMonitorProbe.requireIndependent(
          lifetime, lifetime::close);
      assertTrue(lifetime.stopping());
    } finally {
      lifetime.close();
    }
  }

  @Test
  void life001StopFailureInterruptNullAndHookInstallation() throws Exception {
    try (var lifetime = new WebProcessLifetime()) {
      assertFalse(lifetime.stopping());
      lifetime.install();
      assertThrows(IllegalStateException.class, lifetime::install);
      assertThrows(NullPointerException.class, () -> lifetime.await(null));
      lifetime.shutdown(); // Owner notification returns; it does not close borrowed resources.
      assertTrue(lifetime.stopping());
      lifetime.await(() -> fail("stopped owner must not poll providers"));
    }
    try (var lifetime = new WebProcessLifetime()) {
      var error = assertThrows(IOException.class, () -> lifetime.await(() -> false));
      assertEquals("Web runtime unavailable", error.getMessage());
      assertTrue(lifetime.stopping());
    }
    try (var lifetime = new WebProcessLifetime()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(IOException.class, () -> lifetime.await(() -> true));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
    }
  }

  @Test
  void life002ForeignHookWaitsForActualOwnerNotificationAndPreservesInterrupt() throws Exception {
    var lifetime = new WebProcessLifetime();
    var finished = new AtomicBoolean();
    var interrupted = new AtomicBoolean();
    var thread =
        Thread.ofPlatform()
            .start(
                () -> {
                  Thread.currentThread().interrupt();
                  lifetime.shutdown();
                  interrupted.set(Thread.currentThread().isInterrupted());
                  finished.set(true);
                });
    try {
      long end = System.nanoTime() + Duration.ofSeconds(3).toNanos();
      while (!lifetime.stopping() && System.nanoTime() < end) Thread.sleep(1);
      assertTrue(lifetime.stopping());
      assertFalse(finished.get());
      assertTrue(thread.isAlive());
    } finally {
      lifetime.close();
    }
    assertTrue(thread.join(Duration.ofSeconds(3)));
    assertTrue(finished.get());
    assertTrue(interrupted.get());
    lifetime.close();
  }

  @Test
  void life003HealthyOwnerAwaitsIndependentStop() throws Exception {
    var polls = new CountDownLatch(1);
    var observed = new AtomicReference<Throwable>();
    var lifetime = new WebProcessLifetime();
    var thread =
        Thread.ofPlatform()
            .start(
                () -> {
                  try {
                    lifetime.await(
                        () -> {
                          polls.countDown();
                          return true;
                        });
                  } catch (Throwable failure) {
                    observed.set(failure);
                  }
                });
    try {
      assertTrue(polls.await(3, TimeUnit.SECONDS));
      lifetime.stop();
      assertTrue(thread.join(Duration.ofSeconds(3)));
      assertNull(observed.get());
    } finally {
      lifetime.close();
    }
  }
}
