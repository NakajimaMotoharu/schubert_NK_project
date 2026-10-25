package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.Closeable;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** NATIVE-OUTER001: real separate JVM retains an UNKNOWN frame, including after interrupt. */
final class ServiceNativeReleaseTest {
  @TempDir Path root;

  @Test
  void outer001UnknownNeverClosesDownstreamOrManufacturesNormalExit() throws Exception {
    assertThrows(NullPointerException.class, () -> ServiceProcessResources.release(null, true));
    for (String kind : new String[] {"io", "runtime", "fatal"}) {
      var command = new ArrayList<String>();
      command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
      // Same instrumented production bytes. Child SIGTERM agent output appends to this run,
      // but this component fixture is never ordinary service/native admission acceptance.
      ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
          .filter(value -> value.startsWith("-javaagent:"))
          .forEach(command::add);
      command.add("-cp");
      command.add(
          System.getProperty("surefire.test.class.path", System.getProperty("java.class.path")));
      command.add(Probe.class.getName());
      command.add(kind);
      var output = root.resolve(kind + ".log");
      var child =
          new ProcessBuilder(command)
              .redirectErrorStream(true)
              .redirectOutput(output.toFile())
              .start();
      try {
        long deadline = System.nanoTime() + Duration.ofSeconds(8).toNanos();
        while (child.isAlive()
            && System.nanoTime() < deadline
            && !Files.readString(output).contains("RETAINED attempts=1 downstream=0"))
          Thread.sleep(10);
        assertTrue(child.isAlive(), "UNKNOWN must not become a successful process return");
        assertTrue(Files.readString(output).contains("RETAINED attempts=1 downstream=0"));
        child.destroy(); // Test fixture terminates synthetically; not confirmed provider cleanup.
        assertTrue(child.waitFor(5, java.util.concurrent.TimeUnit.SECONDS));
        assertEquals(143, child.exitValue());
      } finally {
        if (child.isAlive()) {
          child.destroyForcibly();
          child.waitFor();
        }
      }
    }
  }

  public static final class Probe {
    private Probe() {}

    public static void main(String[] arguments) throws Exception {
      var attempts = new AtomicInteger();
      var downstream = new AtomicInteger();
      Thread owner = Thread.currentThread();
      Closeable unknown =
          () -> {
            attempts.incrementAndGet();
            switch (arguments[0]) {
              case "io" -> throw new IOException("synthetic private");
              case "runtime" -> throw new IllegalStateException("synthetic private");
              case "fatal" -> throw new LinkageError("synthetic private");
              default -> throw new AssertionError("invalid independent fixture");
            }
          };
      Thread.ofPlatform()
          .daemon(true)
          .start(
              () -> {
                long end = System.nanoTime() + Duration.ofSeconds(5).toNanos();
                while ((attempts.get() != 1 || owner.getState() != Thread.State.TIMED_WAITING)
                    && System.nanoTime() < end) Thread.onSpinWait();
                try {
                  Thread.sleep(1100);
                } catch (InterruptedException unexpected) {
                  throw new AssertionError(unexpected);
                }
                owner.interrupt();
                while ((owner.isInterrupted() || owner.getState() != Thread.State.TIMED_WAITING)
                    && System.nanoTime() < end) Thread.onSpinWait();
                System.out.println(
                    "RETAINED attempts=" + attempts.get() + " downstream=" + downstream.get());
              });
      ResourceScope.use(
          downstream::incrementAndGet,
          () -> {
            if (arguments.length == 2 && arguments[1].equals("owned"))
              ServiceProcessResources.<Closeable>ownedRelease(Closeable::close, true)
                  .close(unknown);
            else ServiceProcessResources.release(unknown, true).close();
            throw new AssertionError("UNKNOWN unexpectedly returned");
          });
    }
  }
}
