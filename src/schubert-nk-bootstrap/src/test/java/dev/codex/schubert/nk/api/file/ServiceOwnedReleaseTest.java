package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.Closeable;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SSC308/BUG1414/YKT1178; PT-OPS-SERVICEOWN001..004, no production credentials/VM. */
final class ServiceOwnedReleaseTest {
  @TempDir Path temporary;

  @Test
  void serviceown001PortsExistBeforeResourceAndNormalReleaseIsOnce() throws Exception {
    var calls = new AtomicInteger();
    Object expected = new Object();
    ResourceScope.Release<Object> release =
        resource -> {
          assertSame(expected, resource);
          calls.incrementAndGet();
        };
    assertSame(release, ServiceProcessResources.ownedRelease(release, false));
    var retaining = ServiceProcessResources.ownedRelease(release, true);
    assertEquals(0, calls.get());
    retaining.close(expected);
    assertEquals(1, calls.get());
    var legacyCalls = new AtomicInteger();
    Closeable legacy = legacyCalls::incrementAndGet;
    assertSame(legacy, ServiceProcessResources.release(legacy, false));
    ServiceProcessResources.release(legacy, false).close();
    ServiceProcessResources.release(legacy, true).close();
    assertEquals(2, legacyCalls.get());
  }

  @Test
  void serviceown002NullPortsAndFailedOrNullFactoriesNeverRelease() {
    assertThrows(
        NullPointerException.class, () -> ServiceProcessResources.ownedRelease(null, false));
    assertThrows(
        NullPointerException.class, () -> ServiceProcessResources.ownedRelease(null, true));
    var releases = new AtomicInteger();
    var bodies = new AtomicInteger();
    ResourceScope.Release<Object> release =
        ServiceProcessResources.ownedRelease(resource -> releases.incrementAndGet(), true);
    var failure = new LinkageError("synthetic factory failure");
    assertSame(
        failure,
        assertThrows(
            LinkageError.class,
            () ->
                ResourceScope.acquire(
                    () -> {
                      throw failure;
                    },
                    release,
                    resource -> bodies.incrementAndGet())));
    assertThrows(
        NullPointerException.class,
        () -> ResourceScope.acquire(() -> null, release, resource -> bodies.incrementAndGet()));
    assertEquals(0, releases.get());
    assertEquals(0, bodies.get());
  }

  @Test
  void serviceown003NonRetainedReleaseKeepsAllOriginalFailureIdentities() {
    var calls = new AtomicInteger();
    Throwable[] failures = {
      new StorageIoException(StorageIoException.Reason.MISSING),
      new IOException("synthetic"),
      new IllegalStateException("synthetic"),
      new LinkageError("synthetic")
    };
    for (Throwable failure : failures) {
      ResourceScope.Release<Object> release =
          resource -> {
            calls.incrementAndGet();
            if (failure instanceof IOException io) throw io;
            if (failure instanceof RuntimeException runtime) throw runtime;
            throw (Error) failure;
          };
      var port = ServiceProcessResources.ownedRelease(release, false);
      assertSame(failure, assertThrows(failure.getClass(), () -> port.close(new Object())));
    }
    assertEquals(4, calls.get());
  }

  @Test
  void serviceown004UnknownIoRuntimeAndFatalRetainOuterOwnerAfterInterrupt() throws Exception {
    for (String kind : new String[] {"io", "runtime", "fatal"}) {
      var command = new ArrayList<String>();
      command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
      ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
          .filter(value -> value.startsWith("-javaagent:"))
          .forEach(command::add);
      command.add("-cp");
      command.add(
          System.getProperty("surefire.test.class.path", System.getProperty("java.class.path")));
      command.add(ServiceNativeReleaseTest.Probe.class.getName());
      command.add(kind);
      command.add("owned");
      Path output = temporary.resolve(kind + ".log");
      Process child =
          new ProcessBuilder(command)
              .redirectErrorStream(true)
              .redirectOutput(output.toFile())
              .start();
      try {
        long end = System.nanoTime() + Duration.ofSeconds(8).toNanos();
        while (child.isAlive()
            && System.nanoTime() < end
            && !Files.readString(output).contains("RETAINED attempts=1 downstream=0"))
          Thread.sleep(10);
        assertTrue(child.isAlive());
        String actual = Files.readString(output);
        assertTrue(actual.contains("RETAINED attempts=1 downstream=0"));
        assertFalse(actual.contains("synthetic private"));
        child.destroy();
        assertTrue(child.waitFor(5, TimeUnit.SECONDS));
        assertEquals(143, child.exitValue());
      } finally {
        if (child.isAlive()) {
          child.destroyForcibly();
          child.waitFor();
        }
      }
    }
  }
}
