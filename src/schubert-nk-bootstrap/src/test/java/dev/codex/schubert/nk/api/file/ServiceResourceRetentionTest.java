package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTimeoutPreemptively;

import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.Closeable;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-NHOLD316001; literal release/outer-frame oracles, no DB/Root/service credentials. */
final class ServiceResourceRetentionTest {
  private static final String FIXTURE_PUBLIC_FIXTURE_49B9B929 = "public fixture";
  private static final String FIXTURE_CLOSE_3CA44CAE = "CLOSE";
  private static final String FIXTURE_INTERVAL_CONFIRMED_54BC4400 = "INTERVAL_CONFIRMED";
  private static final String FIXTURE_RUNTIME_2D52CD90 = "runtime";

  @Test
  @org.junit.jupiter.api.parallel.ResourceLock(org.junit.jupiter.api.parallel.Resources.SYSTEM_ERR)
  void hold318004PreparedDiagnosticUsesLiteralAndChecksNullBeforeSink() throws Exception {
    var original = System.err;
    var bytes = new java.io.ByteArrayOutputStream();
    try (var output =
        new java.io.PrintStream(bytes, true, java.nio.charset.StandardCharsets.UTF_8)) {
      try {
        System.setErr(output);
        var diagnostic = ServiceProcessResources.unknownReleaseDiagnosticPolicy();
        diagnostic.accept(new IOException("synthetic non-public IO detail"));
        diagnostic.accept(new AssertionError("synthetic non-public fatal detail"));
        var absent = assertThrows(NullPointerException.class, () -> diagnostic.accept(null));
        assertEquals("unconfirmed release", absent.getMessage());
      } finally {
        System.setErr(original);
      }
      String line = "service resource release unconfirmed" + System.lineSeparator();
      assertEquals(line + line, bytes.toString(java.nio.charset.StandardCharsets.UTF_8));
    }
  }

  @Test
  @org.junit.jupiter.api.parallel.ResourceLock(org.junit.jupiter.api.parallel.Resources.SYSTEM_ERR)
  void hold318005PreparedDiagnosticContainsRuntimeAndFatalSinkFailures() throws Exception {
    var original = System.err;
    for (boolean fatal : List.of(false, true)) {
      var messages = new java.util.ArrayList<String>();
      try (var output =
          new java.io.PrintStream(
              new java.io.ByteArrayOutputStream(), true, java.nio.charset.StandardCharsets.UTF_8) {
            @Override
            public void println(String message) {
              messages.add(message);
              if (fatal) throw new AssertionError("synthetic sink fatal");
              throw new IllegalStateException("synthetic sink runtime");
            }
          }) {
        try {
          System.setErr(output);
          assertDoesNotThrow(
              () ->
                  ServiceProcessResources.unknownReleaseDiagnosticPolicy()
                      .accept(new IOException("synthetic primary retained elsewhere")));
        } finally {
          System.setErr(original);
        }
        // Assertions are outside the callback protected by the Production catch.
        assertEquals(List.of("service resource release unconfirmed"), messages);
      }
    }
  }

  @Test
  void hold318006PreparedObservationIsFiniteAndConsumesNotificationOnly() {
    assertTimeoutPreemptively(
        java.time.Duration.ofSeconds(5),
        () -> {
          var observation = ServiceProcessResources.unknownReleaseObservationPolicy();
          try {
            observation.run();
            assertFalse(Thread.currentThread().isInterrupted());
            Thread.currentThread().interrupt();
            observation.run();
            assertFalse(Thread.currentThread().isInterrupted());
          } finally {
            Thread.interrupted();
          }
        });
  }

  @Test
  void hold316001NormalAndNullPortsNeverManufactureAnUnknownRelease() throws Exception {
    var closeCalls = new AtomicInteger();
    Closeable closeable = closeCalls::incrementAndGet;
    assertSame(closeable, ServiceProcessResources.release(closeable, false));
    ServiceProcessResources.release(closeable, false).close();
    ServiceProcessResources.release(closeable, true).close();
    assertEquals(2, closeCalls.get(), "normal close executes once per explicit release");
    for (boolean retained : List.of(false, true))
      assertThrows(
          NullPointerException.class, () -> ServiceProcessResources.release(null, retained));
    var calls = new AtomicInteger();
    ResourceScope.Release<Object> release = ignored -> calls.incrementAndGet();
    assertSame(release, ServiceProcessResources.ownedRelease(release, false));
    ServiceProcessResources.ownedRelease(release, true).close(new Object());
    assertEquals(1, calls.get());
    for (boolean retained : List.of(false, true))
      assertThrows(
          NullPointerException.class, () -> ServiceProcessResources.ownedRelease(null, retained));
    var marker = new IOException(FIXTURE_PUBLIC_FIXTURE_49B9B929);
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
            List.of(FIXTURE_CLOSE_3CA44CAE, FIXTURE_INTERVAL_CONFIRMED_54BC4400),
            Integer.toString(style),
            Integer.toString(failure),
            Boolean.toString(failure != 0));
  }

  @Test
  void hold318001DiagnosticFailureDoesNotUnwindTheOriginalFrame() throws Exception {
    for (String kind : List.of(FIXTURE_RUNTIME_2D52CD90, "error"))
      OwnedRetentionProcess.assertHeldWhenDiagnosticUnavailable(
          DiagnosticDriver.class,
          List.of(FIXTURE_CLOSE_3CA44CAE, "DIAGNOSTIC_FAILED", FIXTURE_INTERVAL_CONFIRMED_54BC4400),
          kind);
  }

  @Test
  void hold318002TickFailureWaitsAFullFallbackIntervalDespiteInterrupts() throws Exception {
    for (String kind : List.of(FIXTURE_RUNTIME_2D52CD90, "error"))
      OwnedRetentionProcess.assertHeld(
          ObservationDriver.class,
          List.of(
              FIXTURE_CLOSE_3CA44CAE,
              "TICK_FAILED",
              "TICK_RETRY_DELAY_CONFIRMED",
              FIXTURE_INTERVAL_CONFIRMED_54BC4400),
          "tick",
          kind);
  }

  @Test
  void hold318003FallbackFailureStillCannotReleaseTheOuterOwner() throws Exception {
    for (String kind : List.of(FIXTURE_RUNTIME_2D52CD90, "error"))
      OwnedRetentionProcess.assertHeld(
          ObservationDriver.class,
          List.of(
              FIXTURE_CLOSE_3CA44CAE,
              "TICK_FAILED",
              "FALLBACK_FAILED",
              FIXTURE_INTERVAL_CONFIRMED_54BC4400),
          "fallback",
          kind);
  }

  public static final class ObservationDriver {
    public static void main(String[] arguments) throws Exception {
      OwnedRetentionProcess.deadline();
      boolean fallbackFailure = arguments[0].equals("fallback");
      Throwable marker =
          arguments[1].equals(FIXTURE_RUNTIME_2D52CD90)
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
                  System.out.println(FIXTURE_CLOSE_3CA44CAE);
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
              if (arguments[0].equals(FIXTURE_RUNTIME_2D52CD90))
                throw new IllegalStateException("fixture diagnostic");
              throw new AssertionError("fixture diagnostic");
            }
          }) {
        System.setErr(unavailable);
        try {
          ServiceProcessResources.ownedRelease(
                  (Object ignored) -> {
                    System.out.println(FIXTURE_CLOSE_3CA44CAE);
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
            System.out.println(FIXTURE_CLOSE_3CA44CAE);
            OwnedRetentionProcess.observeInterval(Thread.currentThread());
            if (interrupted) Thread.currentThread().interrupt();
            switch (kind) {
              case 0 -> throw new IOException(FIXTURE_PUBLIC_FIXTURE_49B9B929);
              case 1 -> throw new IllegalStateException(FIXTURE_PUBLIC_FIXTURE_49B9B929);
              default -> throw new AssertionError(FIXTURE_PUBLIC_FIXTURE_49B9B929);
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
