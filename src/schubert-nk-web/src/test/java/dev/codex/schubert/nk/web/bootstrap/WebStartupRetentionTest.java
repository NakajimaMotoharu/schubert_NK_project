package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS313342354/SSC324; BUG1574/YKT1329; dummy scopes only, never actual Web/Root ownership. */
final class WebStartupRetentionTest {
  @TempDir Path temporary;

  @Test
  void start324001NormalOrderNullableWorkerAndNullBoundary() {
    var order = new ArrayList<String>();
    var startup = new IllegalStateException("public startup fixture");
    WebLogApplicationRuntime.closeAfterFailure(
        startup, () -> order.add("worker"), () -> order.add("replies"));
    assertEquals(List.of("worker", "replies"), order);
    order.clear();
    WebLogApplicationRuntime.closeAfterFailure(startup, null, () -> order.add("replies"));
    assertEquals(List.of("replies"), order);
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            WebLogApplicationRuntime.closeAfterFailure(
                null, calls::incrementAndGet, calls::incrementAndGet));
    assertThrows(
        NullPointerException.class,
        () -> WebLogApplicationRuntime.closeAfterFailure(startup, calls::incrementAndGet, null));
    assertEquals(0, calls.get());
    assertEquals(0, startup.getSuppressed().length);
  }

  @Test
  void start324002UnknownCleanupRetainsDummyOwnersAcrossInterruptInOwnedJvm() throws Exception {
    assertOwnedRetention(temporary, List.of());
  }

  /** Shared independent fixture; legacy cases select only their original failure conditions. */
  static void assertOwnedRetention(Path temporary, List<String> variants) throws Exception {
    var command = new ArrayList<String>();
    command.add(
        Path.of(Objects.requireNonNull(System.getProperty("java.home")), "bin/java").toString());
    var agents =
        ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .filter(value -> value.startsWith("-javaagent:") && value.contains("jacoco"))
            .toList();
    assertFalse(agents.isEmpty(), "same-run real child probes required");
    command.addAll(agents);
    command.addAll(
        List.of(
            "-cp",
            Objects.requireNonNull(System.getProperty("surefire.test.class.path")),
            Driver.class.getName()));
    command.addAll(variants);
    Path out = Files.createTempFile(temporary, "startup-", ".out");
    Path err = Files.createTempFile(temporary, "startup-", ".err");
    var builder =
        new ProcessBuilder(command).redirectOutput(out.toFile()).redirectError(err.toFile());
    builder.environment().clear();
    Process child = builder.start();
    try {
      assertTrue(
          child.waitFor(20, TimeUnit.SECONDS),
          "only dummy fixture must complete its bounded observation");
      assertEquals(0, child.exitValue());
      int cases = variants.isEmpty() ? 5 : variants.size();
      assertEquals(
          "STARTUP_FIXTURE_RETAINED cases=" + cases + " returns=0 outerClosed=0\n",
          Files.readString(out));
      assertEquals("service resource release unconfirmed\n".repeat(cases), Files.readString(err));
    } finally {
      if (child.isAlive()) {
        child.destroyForcibly();
        assertTrue(
            child.waitFor(5, TimeUnit.SECONDS), "cleanup is restricted to this owned fixture");
      }
    }
  }

  /** Process exit discards only inert dummy daemons; it does not prove any real cleanup. */
  public static final class Driver {
    private Driver() {}

    public static void main(String[] arguments) throws Exception {
      int cases;
      if (arguments.length == 0) {
        for (int variant = 0; variant < 5; variant++) observe(variant);
        cases = 5;
      } else {
        for (String argument : arguments) observe(Integer.parseInt(argument));
        cases = arguments.length;
      }
      System.out.println("STARTUP_FIXTURE_RETAINED cases=" + cases + " returns=0 outerClosed=0");
    }

    private static void observe(int variant) throws Exception {
      var worker = new AtomicInteger();
      var replies = new AtomicInteger();
      var returned = new AtomicInteger();
      var outer = new AtomicInteger();
      var startup = new IllegalStateException("public startup fixture");
      AutoCloseable replay =
          () -> {
            worker.incrementAndGet();
            switch (variant) {
              case 0 -> throw new IOException("public checked fixture");
              case 1 -> throw new IllegalArgumentException("public runtime fixture");
              case 2 -> throw new AssertionError("public fatal fixture");
              case 3 -> throw startup;
              case 4 -> {
                /* Worker confirmed; reply cleanup is the first UNKNOWN. */
              }
              default -> throw new AssertionError("public fixture mode");
            }
          };
      AutoCloseable reply =
          () -> {
            replies.incrementAndGet();
            throw new IOException("public reply fixture");
          };
      Thread owner =
          Thread.ofPlatform()
              .daemon(true)
              .name("dummy-startup-owner")
              .start(
                  () -> {
                    try {
                      WebLogApplicationRuntime.closeAfterFailure(startup, replay, reply);
                      returned.incrementAndGet();
                    } finally {
                      outer.incrementAndGet();
                    }
                  });
      long until = System.nanoTime() + Duration.ofSeconds(3).toNanos();
      while (worker.get() == 0 && owner.isAlive() && System.nanoTime() < until) Thread.sleep(1);
      Thread.sleep(1100);
      retained(owner, worker, replies, returned, outer, variant);
      owner.interrupt();
      Thread.sleep(1100);
      retained(owner, worker, replies, returned, outer, variant);
      if (owner.isInterrupted())
        throw new AssertionError("interrupt must not spin or release the owner");
      if (startup.getSuppressed().length != 0)
        throw new AssertionError("retention must not mutate startup or self-suppress");
    }

    private static void retained(
        Thread owner,
        AtomicInteger worker,
        AtomicInteger replies,
        AtomicInteger returned,
        AtomicInteger outer,
        int variant)
        throws Exception {
      if (!owner.isAlive()
          || worker.get() != 1
          || replies.get() != (variant == 4 ? 1 : 0)
          || returned.get() != 0
          || outer.get() != 0)
        throw new AssertionError("startup UNKNOWN released or retried an inert fixture owner");
      long until = System.nanoTime() + Duration.ofSeconds(3).toNanos();
      while (System.nanoTime() < until) {
        if (owner.getState() == Thread.State.TIMED_WAITING
            && java.util.Arrays.stream(owner.getStackTrace())
                .anyMatch(
                    frame ->
                        frame.getClassName().equals(WebLogApplicationRuntime.class.getName())
                            && frame.getMethodName().equals("closeAfterFailure"))) return;
        Thread.sleep(1);
      }
      throw new AssertionError("same startup frame must remain held without busy wait");
    }
  }
}
