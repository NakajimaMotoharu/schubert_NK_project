package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NK-WEB-002/NK-OPS-001; SS342352; PG-D377; PT-OPS-NWEB-UNKNOWN001. */
final class WebUnknownRetentionTest {
  @TempDir Path temporary;

  @Test
  void unknownOwnerNeverReturnsOrUnwindsAfterInterruptInIsolatedFixtureJvm() throws Exception {
    var command = new ArrayList<String>();
    command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
    ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
        .filter(value -> value.startsWith("-javaagent:") && value.contains("jacoco"))
        .forEach(command::add);
    command.addAll(List.of("-cp", System.getProperty("java.class.path"), Probe.class.getName()));
    Path out = Files.createTempFile(temporary, "retention-", ".out");
    Path err = Files.createTempFile(temporary, "retention-", ".err");
    var builder =
        new ProcessBuilder(command).redirectOutput(out.toFile()).redirectError(err.toFile());
    builder.environment().clear();
    Process child = builder.start();
    try {
      assertTrue(child.waitFor(15, TimeUnit.SECONDS), "isolated fixture completes its observation");
      assertEquals(0, child.exitValue());
      assertEquals(
          "UNKNOWN_FIXTURE_RETAINED interruptConsumed=true scopesClosed=0\n",
          Files.readString(out));
      assertEquals("", Files.readString(err));
    } finally {
      if (child.isAlive()) {
        child.destroyForcibly();
        assertTrue(child.waitFor(5, TimeUnit.SECONDS));
      }
    }
  }

  /** No real providers/credentials are borrowed. JVM exit terminates this daemon test only. */
  public static final class Probe {
    private Probe() {}

    public static void main(String[] arguments) throws Exception {
      var closed = new AtomicInteger();
      Thread owner =
          Thread.ofPlatform()
              .daemon(true)
              .start(
                  () -> {
                    try {
                      WebProcessLifetime.retainUnknown();
                    } finally {
                      closed.incrementAndGet();
                    }
                  });
      awaitRetained(owner, closed);
      // Observe ownership after a complete normal hold interval, not only initial suspension.
      Thread.sleep(1200);
      awaitRetained(owner, closed);
      owner.interrupt();
      long until = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
      while (owner.isInterrupted() && System.nanoTime() < until) Thread.sleep(1);
      if (owner.isInterrupted()) throw new AssertionError("interrupt not consumed");
      awaitRetained(owner, closed);
      Thread.sleep(1200);
      awaitRetained(owner, closed);
      System.out.println("UNKNOWN_FIXTURE_RETAINED interruptConsumed=true scopesClosed=0");
    }

    private static void awaitRetained(Thread owner, AtomicInteger closed) throws Exception {
      long until = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
      while (System.nanoTime() < until) {
        if (!owner.isAlive() || closed.get() != 0)
          throw new AssertionError("UNKNOWN scope unwound");
        if (owner.getState() == Thread.State.TIMED_WAITING
            && java.util.Arrays.stream(owner.getStackTrace())
                .anyMatch(
                    frame ->
                        frame.getClassName().equals(WebProcessLifetime.class.getName())
                            && frame.getMethodName().equals("retainUnknown"))) return;
        Thread.sleep(1);
      }
      throw new AssertionError("UNKNOWN owner not observably retained");
    }
  }
}
