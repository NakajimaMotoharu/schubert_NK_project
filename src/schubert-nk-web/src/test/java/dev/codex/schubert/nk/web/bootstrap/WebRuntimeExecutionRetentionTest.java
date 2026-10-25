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
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SSC325/EXEC325001/BUG1578/YKT1320: inert owned child only, not a real native lifetime. */
final class WebRuntimeExecutionRetentionTest {
  @TempDir Path temporary;

  @Test
  void exec325001UnknownCloseAndDiagnosticFailuresNeverUnwindOrRetry() throws Exception {
    var command = new ArrayList<String>();
    command.add(
        Path.of(Objects.requireNonNull(System.getProperty("java.home")), "bin/java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(value -> value.startsWith("-javaagent:") && value.contains("jacoco"))
            .toList();
    assertFalse(agents.isEmpty(), "actual same-run child probes, not copied coverage");
    command.addAll(agents);
    command.addAll(
        List.of(
            "-cp",
            Objects.requireNonNull(System.getProperty("surefire.test.class.path")),
            Driver.class.getName()));
    Path out = Files.createTempFile(temporary, "frame-", ".out");
    Path err = Files.createTempFile(temporary, "frame-", ".err");
    var builder =
        new ProcessBuilder(command).redirectOutput(out.toFile()).redirectError(err.toFile());
    builder.environment().clear();
    Process child = builder.start();
    try {
      assertTrue(child.waitFor(40, TimeUnit.SECONDS), "bounded inert fixture only");
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
      assertEquals(
          "WEB_FRAME_HELD cases=9 actions=1,1,1,1 diagnostic=1 escaped=0 finally=0\n",
          Files.readString(out));
      assertEquals("", Files.readString(err));
    } finally {
      if (child.isAlive()) {
        child.destroyForcibly();
        assertTrue(child.waitFor(5, TimeUnit.SECONDS), "only this self-owned dummy child");
      }
    }
  }

  /** Returning discards only inert daemon callbacks; no live service/DB/broker is held. */
  public static final class Driver {
    private Driver() {}

    public static void main(String[] arguments) throws Exception {
      PrintStream original = System.err;
      try {
        for (int mode = 0; mode < 9; mode++) observe(mode);
        System.out.println(
            "WEB_FRAME_HELD cases=9 actions=1,1,1,1 diagnostic=1 escaped=0 finally=0");
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
      int diagnosticKind = mode % 3;
      System.setErr(
          new PrintStream(OutputStream.nullOutputStream()) {
            @Override
            public void println(String text) {
              assertEquals("WEB cleanup unconfirmed", text);
              diagnostics.incrementAndGet();
              if (diagnosticKind == 1) throw new IllegalStateException("synthetic diagnostic");
              if (diagnosticKind == 2) throw new AssertionError("synthetic diagnostic");
            }
          });
      Thread worker =
          new Thread(
              () -> {
                try {
                  WebRuntimeExecution.execute(
                      starts::incrementAndGet,
                      awaits::incrementAndGet,
                      stops::incrementAndGet,
                      () -> {
                        closes.incrementAndGet();
                        attempted.countDown();
                        switch (mode / 3) {
                          case 0 -> throw new IOException("synthetic close");
                          case 1 -> throw new IllegalStateException("synthetic close");
                          case 2 -> throw new AssertionError("synthetic close");
                          default -> throw new AssertionError("synthetic mode");
                        }
                      });
                  escaped.incrementAndGet();
                } catch (Throwable returnedFailure) {
                  escaped.incrementAndGet();
                } finally {
                  outer.incrementAndGet();
                }
              },
              "inert-web-frame-" + mode);
      worker.setDaemon(true);
      worker.start();
      assertTrue(attempted.await(3, TimeUnit.SECONDS), "must reach exact dummy close");
      Thread.sleep(1200);
      assertHeld(worker, starts, awaits, stops, closes, diagnostics, escaped, outer);
      worker.interrupt();
      Thread.sleep(1200);
      assertHeld(worker, starts, awaits, stops, closes, diagnostics, escaped, outer);
    }

    private static void assertHeld(
        Thread worker,
        AtomicInteger starts,
        AtomicInteger awaits,
        AtomicInteger stops,
        AtomicInteger closes,
        AtomicInteger diagnostics,
        AtomicInteger escaped,
        AtomicInteger outer) {
      assertTrue(worker.isAlive(), "inert owner frame must not return after UNKNOWN");
      assertEquals(1, starts.get());
      assertEquals(1, awaits.get());
      assertEquals(1, stops.get());
      assertEquals(1, closes.get());
      assertEquals(1, diagnostics.get());
      assertEquals(0, escaped.get());
      assertEquals(0, outer.get());
    }
  }
}
