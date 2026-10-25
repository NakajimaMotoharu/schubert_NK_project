package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.management.ManagementFactory;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/** SSC316 self-owned finite JVM fixture, never a Root/VM/admission/ownedstop substitute. */
public final class OwnedRetentionProcess {
  private OwnedRetentionProcess() {}

  public static void assertHeld(Class<?> driver, List<String> output, String... arguments)
      throws Exception {
    assertHeld(driver, output, List.of(), true, arguments);
  }

  /** Only for a deliberately unavailable child diagnostic; final stderr EOF remains mandatory. */
  public static void assertHeldWhenDiagnosticUnavailable(
      Class<?> driver, List<String> output, String... arguments) throws Exception {
    assertHeld(driver, output, List.of(), false, arguments);
  }

  /** Exact SLF4J 2.0.18 NOP fallback literals, not an arbitrary diagnostic filter. */
  public static void assertFactoryHeld(Class<?> driver, List<String> output, String... arguments)
      throws Exception {
    assertHeld(
        driver,
        output,
        List.of(
            "SLF4J(W): No SLF4J providers were found.",
            "SLF4J(W): Defaulting to no-operation (NOP) logger implementation",
            "SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details."),
        true,
        arguments);
  }

  private static void assertHeld(
      Class<?> driver,
      List<String> output,
      List<String> preamble,
      boolean diagnostic,
      String... arguments)
      throws Exception {
    var command = new ArrayList<String>();
    command.add(Path.of(System.getProperty("java.home"), "bin", "java").toString());
    for (String option : ManagementFactory.getRuntimeMXBean().getInputArguments())
      if (option.startsWith("-javaagent:")) command.add(option);
    command.add("-cp");
    command.add(System.getProperty("surefire.test.class.path"));
    command.add(driver.getName());
    command.addAll(List.of(arguments));
    var process = new ProcessBuilder(command).start();
    try (var stdout = process.inputReader();
        var stderr = process.errorReader()) {
      var executor = Executors.newSingleThreadExecutor();
      try {
        for (String expected : preamble)
          assertEquals(expected, executor.submit(stderr::readLine).get(5, TimeUnit.SECONDS));
        if (diagnostic)
          assertEquals(
              "service resource release unconfirmed",
              executor.submit(stderr::readLine).get(5, TimeUnit.SECONDS));
        for (String expected : output)
          assertEquals(expected, executor.submit(stdout::readLine).get(5, TimeUnit.SECONDS));
        assertFalse(process.waitFor(100, TimeUnit.MILLISECONDS));
        // Signal the exact new process generation without closing our verification readers.
        assertTrue(process.toHandle().destroy());
        assertTrue(process.waitFor(5, TimeUnit.SECONDS));
        assertEquals(
            143, process.exitValue(), "fixture TERM is not a normal/native cleanup receipt");
        assertNull(stdout.readLine(), "outer release marker must never appear");
        assertNull(stderr.readLine(), "no raw exception diagnostics");
      } finally {
        // End the owned child before joining a reader: an absent marker must not deadlock teardown.
        try {
          terminate(process);
        } finally {
          executor.shutdownNow();
          assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
        }
      }
    } finally {
      terminate(process);
    }
  }

  private static void terminate(Process process) throws InterruptedException {
    if (process.isAlive()) {
      process.destroy();
      if (!process.waitFor(5, TimeUnit.SECONDS)) {
        process.destroyForcibly();
        assertTrue(process.waitFor(5, TimeUnit.SECONDS));
      }
    }
  }

  /** Bound even an orphaned test child; timeout124 is a failed fixture, never a successful PT. */
  public static void deadline() {
    var watchdog =
        new Thread(
            () -> {
              try {
                Thread.sleep(20_000);
              } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
              }
              Runtime.getRuntime().halt(124);
            },
            "self-owned-retention-deadline");
    watchdog.setDaemon(true);
    watchdog.start();
  }

  /** The owner must remain in timed observation after a real interval, including a cleared IRQ. */
  public static void observeInterval(Thread owner) {
    var observer =
        new Thread(
            () -> {
              try {
                long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
                while (owner.getState() != Thread.State.TIMED_WAITING
                    && System.nanoTime() - deadline < 0) Thread.sleep(1);
                Thread.sleep(1200);
                System.out.println(
                    owner.getState() == Thread.State.TIMED_WAITING && !owner.isInterrupted()
                        ? "INTERVAL_CONFIRMED"
                        : "INTERVAL_NOT_CONFIRMED");
              } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
                System.out.println("OBSERVER_INTERRUPTED");
              }
            },
            "self-owned-retention-interval");
    observer.setDaemon(true);
    observer.start();
  }
}
