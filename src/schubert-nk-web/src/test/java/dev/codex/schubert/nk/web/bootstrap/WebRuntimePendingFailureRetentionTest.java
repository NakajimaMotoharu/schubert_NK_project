package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.catalina.LifecycleException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SSC325/EXEC325002: exceptional-completion finally, inert callback owners only. */
final class WebRuntimePendingFailureRetentionTest {
  @TempDir Path temporary;

  @Test
  void exec325002PendingStartOrAwaitFailureKeepsTheExceptionalFinallyFrame() throws Exception {
    var command = new ArrayList<String>();
    command.add(
        Path.of(Objects.requireNonNull(System.getProperty("java.home")), "bin/java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(value -> value.startsWith("-javaagent:") && value.contains("jacoco"))
            .toList();
    assertFalse(agents.isEmpty(), "same-run child probes required");
    command.addAll(agents);
    command.addAll(
        List.of(
            "-cp",
            Objects.requireNonNull(System.getProperty("surefire.test.class.path")),
            Driver.class.getName()));
    Path out = Files.createTempFile(temporary, "pending-frame-", ".out");
    Path err = Files.createTempFile(temporary, "pending-frame-", ".err");
    var builder =
        new ProcessBuilder(command).redirectOutput(out.toFile()).redirectError(err.toFile());
    builder.environment().clear();
    Process child = builder.start();
    try {
      assertTrue(child.waitFor(20, TimeUnit.SECONDS), "bounded inert fixture only");
      assertEquals(
          0,
          child.exitValue(),
          () -> {
            try {
              return Files.readString(err);
            } catch (IOException unavailable) {
              return "fixture diagnostic unavailable";
            }
          });
      assertEquals("PENDING_WEB_FRAME_HELD cases=3 escaped=0 outer=0\n", Files.readString(out));
      assertEquals("", Files.readString(err));
    } finally {
      if (child.isAlive()) {
        child.destroyForcibly();
        assertTrue(child.waitFor(5, TimeUnit.SECONDS), "only this owned dummy child");
      }
    }
  }

  /** No real service resource is owned by these discarded daemon callbacks. */
  public static final class Driver {
    private Driver() {}

    public static void main(String[] arguments) throws Exception {
      PrintStream original = System.err;
      try {
        for (int mode = 0; mode < 3; mode++) observe(mode);
        System.out.println("PENDING_WEB_FRAME_HELD cases=3 escaped=0 outer=0");
      } finally {
        System.setErr(original);
      }
    }

    private static void observe(int mode) throws Exception {
      var starts = new AtomicInteger();
      var awaits = new AtomicInteger();
      var stops = new AtomicInteger();
      var closes = new AtomicInteger();
      var diagnostics = new AtomicInteger();
      var escaped = new AtomicInteger();
      var outer = new AtomicInteger();
      var attempted = new CountDownLatch(1);
      System.setErr(
          new PrintStream(OutputStream.nullOutputStream()) {
            @Override
            public void println(String text) {
              assertEquals("WEB cleanup unconfirmed", text);
              diagnostics.incrementAndGet();
              if (mode == 0) throw new AssertionError("synthetic diagnostic");
              if (mode == 1) throw new IllegalStateException("synthetic diagnostic");
            }
          });
      Thread worker =
          new Thread(
              () -> {
                try {
                  WebRuntimeExecution.execute(
                      () -> {
                        starts.incrementAndGet();
                        if (mode == 0) throw new LifecycleException("synthetic startup");
                        if (mode == 2) throw new IOException("synthetic startup");
                      },
                      () -> {
                        awaits.incrementAndGet();
                        throw new AssertionError("synthetic await");
                      },
                      stops::incrementAndGet,
                      () -> {
                        closes.incrementAndGet();
                        attempted.countDown();
                        if (mode == 0) throw new IOException("synthetic close");
                        if (mode == 1) throw new IllegalStateException("synthetic close");
                        throw new AssertionError("synthetic close");
                      });
                  escaped.incrementAndGet();
                } catch (Throwable returnedFailure) {
                  escaped.incrementAndGet();
                } finally {
                  outer.incrementAndGet();
                }
              },
              "inert-pending-web-frame-" + mode);
      worker.setDaemon(true);
      worker.start();
      assertTrue(
          attempted.await(3, TimeUnit.SECONDS), "must reach dummy close after pending failure");
      Thread.sleep(1200);
      assertHeld(mode, worker, starts, awaits, stops, closes, diagnostics, escaped, outer);
      worker.interrupt();
      Thread.sleep(1200);
      assertHeld(mode, worker, starts, awaits, stops, closes, diagnostics, escaped, outer);
    }

    private static void assertHeld(
        int mode,
        Thread worker,
        AtomicInteger starts,
        AtomicInteger awaits,
        AtomicInteger stops,
        AtomicInteger closes,
        AtomicInteger diagnostics,
        AtomicInteger escaped,
        AtomicInteger outer) {
      assertTrue(worker.isAlive(), "pending failure must not unwind an UNKNOWN close frame");
      assertEquals(1, starts.get());
      assertEquals(mode == 1 ? 1 : 0, awaits.get());
      assertEquals(1, stops.get());
      assertEquals(1, closes.get());
      assertEquals(1, diagnostics.get());
      assertEquals(0, escaped.get());
      assertEquals(0, outer.get());
    }
  }
}
