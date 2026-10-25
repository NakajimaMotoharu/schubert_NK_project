package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.Duration;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-OPS-RETAIN3396-001; OPS009/UI251/SS341343/SSC137. Isolated OS component, not Root authority.
 * Actual caller-owned lock must outlive interruption until this exact child terminates.
 */
final class MorningStartupRetainOwnerTest {
  @TempDir Path temporary;

  @Test
  void retainsCallerLockAcrossInterruptUntilOwnedTermination() throws Exception {
    Path lock = temporary.resolve("caller-owned.lock");
    Path output = temporary.resolve("retain-output.txt");
    Path error = temporary.resolve("retain-error.txt");
    var arguments = new ArrayList<String>();
    arguments.add(Path.of(System.getProperty("java.home"), "bin", "java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(
                argument ->
                    argument.startsWith("-javaagent:") && argument.contains("org.jacoco.agent"))
            .toList();
    assertEquals(1, agents.size(), "this component must retain actual JaCoCo instrumentation");
    assertFalse(agents.getFirst().contains("append=false"));
    arguments.add(agents.getFirst());
    arguments.add("-Dfile.encoding=UTF-8");
    arguments.add("-cp");
    arguments.add(
        System.getProperty("surefire.test.class.path", System.getProperty("java.class.path")));
    arguments.add(RetainChild.class.getName());
    arguments.add(lock.toString());
    var child =
        new ProcessBuilder(arguments)
            .redirectOutput(output.toFile())
            .redirectError(error.toFile())
            .start();
    try {
      awaitMarker(child, output, "INTERRUPT_CLEARED_STILL_HELD", Duration.ofSeconds(30));
      String observed = Files.readString(output);
      assertEquals("CALLER_LOCK_HELD\nINTERRUPT_CLEARED_STILL_HELD\n", observed);
      try (var contender = FileChannel.open(lock, StandardOpenOption.WRITE)) {
        assertNull(contender.tryLock(), "interrupt must never release the real caller's lock");
        assertFalse(child.waitFor(200, TimeUnit.MILLISECONDS), "unresolved owner cannot return");
        assertNull(contender.tryLock(), "caller still owns the lock throughout retention");
      }
      child.destroy(); // Only our returned exact Process object; no lookup or historical PID.
      assertTrue(
          child.waitFor(10, TimeUnit.SECONDS), "owned TERM must complete before postconditions");
      assertEquals(143, child.exitValue(), "expected isolated fixture TERM, not a Root success");
      assertEquals(observed, Files.readString(output), "retain never unwinds the caller normally");
      assertEquals("", Files.readString(error));
      try (var contender = FileChannel.open(lock, StandardOpenOption.WRITE);
          var acquired = contender.tryLock()) {
        assertNotNull(acquired, "only actual child termination releases the OS owner");
        assertTrue(acquired.isValid());
      }
    } finally {
      if (child.isAlive()) {
        child.destroy();
        if (!child.waitFor(10, TimeUnit.SECONDS)) {
          child.destroyForcibly();
          assertTrue(child.waitFor(10, TimeUnit.SECONDS), "never abandon the owned fixture");
        }
      }
    }
  }

  private static void awaitMarker(Process child, Path output, String marker, Duration limit)
      throws Exception {
    long deadline = System.nanoTime() + limit.toNanos();
    while (System.nanoTime() - deadline < 0) {
      if (Files.exists(output) && Files.readString(output).contains(marker)) return;
      if (!child.isAlive()) throw new IOException("owned retain fixture exited before observation");
      Thread.sleep(10); // Explicit bounded real-process component, not a pure timing mock.
    }
    throw new IOException("owned retain fixture observation deadline elapsed");
  }

  public static final class RetainChild {
    private RetainChild() {}

    public static void main(String[] args) throws Exception {
      if (args.length != 1) throw new IllegalArgumentException("one private fixture lock required");
      try (var channel =
              FileChannel.open(
                  Path.of(args[0]), StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
          var held = channel.lock()) {
        if (!held.isValid()) throw new AssertionError("caller lock acquisition failed");
        var owner = Thread.currentThread();
        var interrupted = new CountDownLatch(1);
        var witness =
            new Thread(
                () -> {
                  try {
                    interrupted.await();
                    while (owner.isInterrupted()) Thread.sleep(10);
                    System.out.println("INTERRUPT_CLEARED_STILL_HELD");
                  } catch (InterruptedException failure) {
                    Thread.currentThread().interrupt();
                    throw new AssertionError(failure);
                  }
                },
                "retention-interrupt-witness");
        witness.setDaemon(true);
        witness.start();
        System.out.println("CALLER_LOCK_HELD");
        owner.interrupt();
        interrupted.countDown();
        MorningStartupLaunchOwner.retain();
        System.out.println("UNEXPECTED_NORMAL_RETURN");
      }
    }
  }
}
