package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.Closeable;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-NHOLD316001; literal release/outer-frame oracles, no DB/Root/service credentials. */
final class ServiceResourceRetentionTest {
  @Test
  void hold316001NormalAndNullPortsNeverManufactureAnUnknownRelease() throws Exception {
    var calls = new AtomicInteger();
    ResourceScope.Release<Object> release = ignored -> calls.incrementAndGet();
    assertSame(release, ServiceProcessResources.ownedRelease(release, false));
    ServiceProcessResources.ownedRelease(release, true).close(new Object());
    assertEquals(1, calls.get());
    for (boolean retained : List.of(false, true))
      assertThrows(
          NullPointerException.class, () -> ServiceProcessResources.ownedRelease(null, retained));
    var marker = new IOException("public fixture");
    ResourceScope.Release<Object> failing =
        ignored -> {
          throw marker;
        };
    assertSame(
        marker,
        assertThrows(
            IOException.class,
            () -> ServiceProcessResources.ownedRelease(failing, false).close(new Object())));
    var seen = new java.util.concurrent.atomic.AtomicReference<Throwable>();
    assertSame(
        marker,
        assertThrows(
            IOException.class,
            () -> ServiceProcessResources.ownedRelease(failing, seen::set).close(new Object())));
    assertSame(marker, seen.get());
    assertThrows(
        NullPointerException.class,
        () ->
            ServiceProcessResources.ownedRelease(
                release, (java.util.function.Consumer<Throwable>) null));
    assertThrows(
        NullPointerException.class, () -> ServiceProcessResources.retainUnknownRelease(null));
    assertThrows(
        NullPointerException.class,
        () -> ServiceProcessResources.unknownReleasePolicy().accept(null));
    Runnable observe = calls::incrementAndGet;
    int before = calls.get();
    assertThrows(
        NullPointerException.class,
        () -> ServiceProcessResources.retainUnknownRelease(null, observe, observe));
    assertThrows(
        NullPointerException.class,
        () -> ServiceProcessResources.retainUnknownRelease(marker, null, observe));
    assertThrows(
        NullPointerException.class,
        () -> ServiceProcessResources.retainUnknownRelease(marker, observe, null));
    assertEquals(before, calls.get(), "invalid keeper ports cannot start observation");
  }

  @Test
  void hold316002UnknownIoRuntimeErrorKeepOuterFrameAndDoNotRetry() throws Exception {
    for (int style = 0; style < 2; style++)
      for (int failure = 0; failure < 3; failure++)
        OwnedRetentionProcess.assertHeld(
            Driver.class,
            List.of("CLOSE", "INTERVAL_CONFIRMED"),
            Integer.toString(style),
            Integer.toString(failure),
            Boolean.toString(failure != 0));
  }

  @Test
  void hold318001DiagnosticFailureDoesNotUnwindTheOriginalFrame() throws Exception {
    for (String kind : List.of("runtime", "error"))
      OwnedRetentionProcess.assertHeldWhenDiagnosticUnavailable(
          DiagnosticDriver.class,
          List.of("CLOSE", "DIAGNOSTIC_FAILED", "INTERVAL_CONFIRMED"),
          kind);
  }

  @Test
  void hold318002TickFailureWaitsAFullFallbackIntervalDespiteInterrupts() throws Exception {
    for (String kind : List.of("runtime", "error"))
      OwnedRetentionProcess.assertHeld(
          ObservationDriver.class,
          List.of("CLOSE", "TICK_FAILED", "TICK_RETRY_DELAY_CONFIRMED", "INTERVAL_CONFIRMED"),
          "tick",
          kind);
  }

  @Test
  void hold318003FallbackFailureStillCannotReleaseTheOuterOwner() throws Exception {
    for (String kind : List.of("runtime", "error"))
      OwnedRetentionProcess.assertHeld(
          ObservationDriver.class,
          List.of("CLOSE", "TICK_FAILED", "FALLBACK_FAILED", "INTERVAL_CONFIRMED"),
          "fallback",
          kind);
  }

  public static final class ObservationDriver {
    public static void main(String[] arguments) throws Exception {
      OwnedRetentionProcess.deadline();
      boolean fallbackFailure = arguments[0].equals("fallback");
      Throwable marker =
          arguments[1].equals("runtime")
              ? new IllegalStateException("fixture observation")
              : new AssertionError("fixture observation");
      var attempts = new AtomicInteger();
      var firstAt = new java.util.concurrent.atomic.AtomicLong();
      Runnable observation =
          () -> {
            int attempt = attempts.incrementAndGet();
            if (attempt == 1) {
              firstAt.set(System.nanoTime());
              System.out.println("TICK_FAILED");
              fail(marker);
            }
            if (attempt == 2 && !fallbackFailure)
              System.out.println(
                  System.nanoTime() - firstAt.get() >= 1_000_000_000L
                      ? "TICK_RETRY_DELAY_CONFIRMED"
                      : "EARLY_TICK");
            try {
              Thread.sleep(1000);
            } catch (InterruptedException notification) {
              // One notification cannot release an UNKNOWN owner.
            }
          };
      Runnable fallback =
          fallbackFailure
              ? () -> {
                System.out.println("FALLBACK_FAILED");
                fail(marker);
              }
              : ServiceProcessResources::waitUnknownInterval;
      java.util.function.Consumer<Throwable> policy =
          unconfirmed ->
              ServiceProcessResources.retainUnknownRelease(unconfirmed, observation, fallback);
      Thread owner = Thread.currentThread();
      var wake =
          new Thread(
              () -> {
                try {
                  Thread.sleep(100);
                } catch (InterruptedException interrupted) {
                  Thread.currentThread().interrupt();
                }
                owner.interrupt();
              },
              "self-owned-observer-interrupt");
      wake.setDaemon(true);
      wake.start();
      try {
        ServiceProcessResources.ownedRelease(
                (Object ignored) -> {
                  System.out.println("CLOSE");
                  OwnedRetentionProcess.observeInterval(owner);
                  owner.interrupt();
                  throw new IOException("fixture release");
                },
                policy)
            .close(new Object());
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }

    private static void fail(Throwable marker) {
      if (marker instanceof RuntimeException runtime) throw runtime;
      throw (Error) marker;
    }
  }

  public static final class DiagnosticDriver {
    public static void main(String[] arguments) throws Exception {
      OwnedRetentionProcess.deadline();
      var original = System.err;
      try (var unavailable =
          new java.io.PrintStream(
              java.io.OutputStream.nullOutputStream(),
              false,
              java.nio.charset.StandardCharsets.UTF_8) {
            @Override
            public void println(String message) {
              assertEquals("service resource release unconfirmed", message);
              System.out.println("DIAGNOSTIC_FAILED");
              if (arguments[0].equals("runtime"))
                throw new IllegalStateException("fixture diagnostic");
              throw new AssertionError("fixture diagnostic");
            }
          }) {
        System.setErr(unavailable);
        try {
          ServiceProcessResources.ownedRelease(
                  (Object ignored) -> {
                    System.out.println("CLOSE");
                    OwnedRetentionProcess.observeInterval(Thread.currentThread());
                    throw new IOException("fixture release");
                  },
                  true)
              .close(new Object());
        } finally {
          System.setErr(original);
          System.out.println("OUTER_RELEASED");
        }
      }
    }
  }

  public static final class Driver {
    public static void main(String[] arguments) throws Exception {
      OwnedRetentionProcess.deadline();
      int style = Integer.parseInt(arguments[0]);
      int kind = Integer.parseInt(arguments[1]);
      boolean interrupted = Boolean.parseBoolean(arguments[2]);
      Closeable failing =
          () -> {
            System.out.println("CLOSE");
            OwnedRetentionProcess.observeInterval(Thread.currentThread());
            if (interrupted) Thread.currentThread().interrupt();
            switch (kind) {
              case 0 -> throw new IOException("public fixture");
              case 1 -> throw new IllegalStateException("public fixture");
              default -> throw new AssertionError("public fixture");
            }
          };
      try {
        if (style == 0)
          ServiceProcessResources.ownedRelease((Object ignored) -> failing.close(), true)
              .close(new Object());
        else ServiceProcessResources.release(failing, true).close();
      } finally {
        System.out.println("OUTER_RELEASED");
      }
    }
  }
}
