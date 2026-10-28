package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.bootstrap.RootEntryCheckpointFixture;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.lang.reflect.Modifier;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

/** SSC299/BUG1380/YKT1146; MAIN-TERM001..008 data/control-flow only, never native authority. */
final class MainTerminationPortTest {
  private static final String FIXTURE_EXIT_61090B57 = "exit:";
  private static final String FIXTURE_PUBLIC_IO_5EF2F93D = "PUBLIC_IO";
  private static final String FIXTURE_PUBLIC_UNKNOWN_E86C45C2 = "PUBLIC_UNKNOWN";
  private static final String FIXTURE_PUBLIC_FATAL_93D0542B = "PUBLIC_FATAL";
  private static final String FIXTURE_ADMISSION_5F37BB96 = "admission";
  private final Thread.UncaughtExceptionHandler originalHandler =
      Thread.currentThread().getUncaughtExceptionHandler();

  @AfterEach
  void restoreFixtureThreadHandler() {
    Thread.currentThread().setUncaughtExceptionHandler(originalHandler);
  }

  @Test
  void morningRequestsLiteralSuccessWarningOnlyAfterTypedBusinessReturn() {
    for (var outcome : MaintenanceCompletion.Outcome.values())
      for (boolean resume : List.of(false, true)) {
        var order = new ArrayList<String>();
        var entry =
            new MorningProcessMain(
                (budget, run) -> {
                  budget.requireWithin();
                  assertEquals(
                      resume ? Optional.of(MorningCompletedMainTest.RUN) : Optional.empty(), run);
                  order.add("completed");
                  return new MaintenanceCompletion(
                      MorningCompletedMainTest.ACTIVATION,
                      Instant.parse("2026-10-04T09:01:00Z"),
                      outcome);
                },
                status -> order.add(FIXTURE_EXIT_61090B57 + status));
        entry.main(
            resume
                ? new String[] {"--resume", MorningCompletedMainTest.RUN.toString()}
                : new String[0]);
        assertEquals(
            List.of(
                "completed",
                outcome == MaintenanceCompletion.Outcome.SUCCESS ? "exit:0" : "exit:10"),
            order);
      }
  }

  @Test
  void morningMalformedKnownAndUnknownFailuresNeverInventSuccessfulExit() {
    var exits = new ArrayList<Integer>();
    new MorningProcessMain(
            (budget, run) -> {
              throw new AssertionError("invalid argv entered work");
            },
            exits::add)
        .main(new String[] {"--unknown"});
    assertEquals(List.of(70), exits);
    exits.clear();
    new MorningProcessMain(
            (budget, run) -> {
              throw new IOException(FIXTURE_PUBLIC_IO_5EF2F93D);
            },
            exits::add)
        .main(new String[0]);
    assertEquals(List.of(30), exits);
    for (var failure :
        List.of(
            new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_E86C45C2),
            new AssertionError(FIXTURE_PUBLIC_FATAL_93D0542B))) {
      exits.clear();
      var entry =
          new MorningProcessMain(
              (budget, run) -> {
                throwUnknown(failure);
                return null;
              },
              exits::add);
      assertSame(failure, assertThrows(failure.getClass(), () -> entry.main(new String[0])));
      assertTrue(exits.isEmpty());
    }
    exits.clear();
    var entry = new MorningProcessMain((budget, run) -> null, exits::add);
    assertThrows(NullPointerException.class, () -> entry.main(null));
    assertTrue(exits.isEmpty());
  }

  @Test
  void rootRetainsSameMeasurementThroughAdmissionTerminalThenNonReadyExit() throws Exception {
    for (var service : ServiceConfigFiles.Service.values())
      for (boolean measured : List.of(false, true))
        for (boolean knownFailure : List.of(false, true)) {
          var order = new ArrayList<String>();
          var checkpoint =
              measured
                  ? Optional.of(RootEntryCheckpointFixture.create(service, order, null))
                  : Optional.<dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint>empty();
          var entry =
              new RootServiceLauncher(
                  actual -> {
                    assertEquals(service, actual);
                    order.add("open");
                    return checkpoint;
                  },
                  (actual, held) -> {
                    assertEquals(service, actual);
                    assertSame(checkpoint, held);
                    order.add(FIXTURE_ADMISSION_5F37BB96);
                    if (knownFailure) throw new IOException(FIXTURE_PUBLIC_IO_5EF2F93D);
                  },
                  status -> order.add(FIXTURE_EXIT_61090B57 + status));
          entry.main(new String[] {service.name()});
          assertEquals(
              measured
                  ? List.of("open", FIXTURE_ADMISSION_5F37BB96, "terminal", "exit:30")
                  : List.of("open", FIXTURE_ADMISSION_5F37BB96, "exit:30"),
              order);
        }
  }

  @Test
  void rootBadArgsAndUnavailableMeasurementCannotReachNativeAdmission() throws Exception {
    var exits = new ArrayList<Integer>();
    var entry =
        new RootServiceLauncher(
            service -> {
              throw new AssertionError("bad argv selected measurement");
            },
            (service, held) -> fail("bad argv selected admission"),
            exits::add);
    entry.main(new String[] {"OTHER"});
    assertEquals(List.of(70), exits);
    exits.clear();
    assertThrows(NullPointerException.class, () -> entry.main(null));
    for (var failure :
        List.of(
            new IOException(FIXTURE_PUBLIC_IO_5EF2F93D),
            new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_E86C45C2),
            new AssertionError(FIXTURE_PUBLIC_FATAL_93D0542B))) {
      var refused =
          new RootServiceLauncher(
              service -> {
                throwAny(failure);
                return Optional.empty();
              },
              (service, held) -> fail("failed measurement selected admission"),
              exits::add);
      assertSame(
          failure, assertThrows(failure.getClass(), () -> refused.main(new String[] {"API"})));
      assertTrue(exits.isEmpty());
    }
    var missing =
        new RootServiceLauncher(
            service -> null,
            (service, held) -> fail("null measurement selected admission"),
            exits::add);
    assertThrows(NullPointerException.class, () -> missing.main(new String[] {"WEB"}));
    assertTrue(exits.isEmpty());
  }

  @Test
  void rootCaptureAndUnknownAdmissionFailureNeverBecomeExitRequest() {
    var order = new ArrayList<String>();
    var failure = new IOException("PUBLIC_CAPTURE");
    var checkpoint =
        RootEntryCheckpointFixture.create(ServiceConfigFiles.Service.API, order, failure);
    var entry =
        new RootServiceLauncher(
            service -> Optional.of(checkpoint),
            (service, held) -> order.add(FIXTURE_ADMISSION_5F37BB96),
            status -> fail("capture failure must not request exit"));
    assertSame(failure, assertThrows(IOException.class, () -> entry.main(new String[] {"API"})));
    assertEquals(List.of(FIXTURE_ADMISSION_5F37BB96, "terminal"), order);
    for (var unknown :
        List.of(
            new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_E86C45C2),
            new AssertionError(FIXTURE_PUBLIC_FATAL_93D0542B))) {
      var refused =
          new RootServiceLauncher(
              service -> Optional.empty(),
              (service, held) -> throwUnknown(unknown),
              status -> fail("unknown admission failure must propagate"));
      assertSame(
          unknown, assertThrows(unknown.getClass(), () -> refused.main(new String[] {"WEB"})));
    }
  }

  @Test
  void cleanupSelectsOnlyExactExpiryAndRequestsLiteralNormalizedStatusOnce() {
    for (boolean expiry : List.of(false, true))
      for (int status : new int[] {0, 10, 30, 71}) {
        var order = new ArrayList<String>();
        var entry =
            new CleanupProcessMain(
                () -> {
                  assertFalse(expiry);
                  order.add("cleanup");
                  return status;
                },
                () -> {
                  assertTrue(expiry);
                  order.add("expiry");
                  return status;
                },
                value -> order.add(FIXTURE_EXIT_61090B57 + value));
        entry.main(expiry ? new String[] {"--expiry"} : new String[0]);
        assertEquals(
            List.of(
                expiry ? "expiry" : "cleanup",
                FIXTURE_EXIT_61090B57 + (status == 71 ? 30 : status)),
            order);
      }
  }

  @Test
  void cleanupInvalidKnownUnknownAndNullArgumentsPreserveFailureContract() {
    var exits = new ArrayList<Integer>();
    var invalid =
        new CleanupProcessMain(
            () -> {
              throw new AssertionError("invalid argv selected cleanup");
            },
            () -> {
              throw new AssertionError("invalid argv selected expiry");
            },
            exits::add);
    invalid.main(new String[] {"--unexpected"});
    assertEquals(List.of(70), exits);
    exits.clear();
    assertThrows(NullPointerException.class, () -> invalid.main(null));
    assertTrue(exits.isEmpty());
    var io =
        new CleanupProcessMain(
            () -> {
              throw new IOException(FIXTURE_PUBLIC_IO_5EF2F93D);
            },
            () -> {
              throw new IOException(FIXTURE_PUBLIC_IO_5EF2F93D);
            },
            exits::add);
    io.main(new String[0]);
    io.main(new String[] {"--expiry"});
    assertEquals(List.of(30, 30), exits);
    for (var unknown :
        List.of(
            new IllegalStateException(FIXTURE_PUBLIC_UNKNOWN_E86C45C2),
            new AssertionError(FIXTURE_PUBLIC_FATAL_93D0542B))) {
      exits.clear();
      var entry =
          new CleanupProcessMain(
              () -> {
                throwUnknown(unknown);
                return 0;
              },
              () -> {
                throwUnknown(unknown);
                return 0;
              },
              exits::add);
      assertSame(unknown, assertThrows(unknown.getClass(), () -> entry.main(new String[0])));
      assertSame(
          unknown, assertThrows(unknown.getClass(), () -> entry.main(new String[] {"--expiry"})));
      assertTrue(exits.isEmpty());
    }
  }

  @Test
  void constructorNullsAndTerminationFailuresNeverEnableAlternatePublicEntry() throws Exception {
    assertThrows(NullPointerException.class, () -> new MorningProcessMain(null, status -> {}));
    assertThrows(
        NullPointerException.class, () -> new MorningProcessMain((budget, run) -> null, null));
    assertThrows(
        NullPointerException.class,
        () -> new RootServiceLauncher(null, (service, held) -> {}, status -> {}));
    assertThrows(
        NullPointerException.class,
        () -> new RootServiceLauncher(service -> Optional.empty(), null, status -> {}));
    assertThrows(
        NullPointerException.class,
        () -> new RootServiceLauncher(service -> Optional.empty(), (service, held) -> {}, null));
    assertThrows(
        NullPointerException.class, () -> new CleanupProcessMain(null, () -> 0, status -> {}));
    assertThrows(
        NullPointerException.class, () -> new CleanupProcessMain(() -> 0, null, status -> {}));
    assertThrows(NullPointerException.class, () -> new CleanupProcessMain(() -> 0, () -> 0, null));
    for (var type :
        List.of(MorningProcessMain.class, RootServiceLauncher.class, CleanupProcessMain.class)) {
      assertEquals(1, type.getConstructors().length);
      assertEquals(0, type.getConstructors()[0].getParameterCount());
      assertFalse(Modifier.isStatic(type.getMethod("main", String[].class).getModifiers()));
    }
    var unknown = new IllegalStateException("PUBLIC_EXIT_FAILURE");
    var entry =
        new MorningProcessMain(
            (budget, run) -> null,
            status -> {
              assertEquals(70, status);
              throw unknown;
            });
    assertSame(
        unknown,
        assertThrows(IllegalStateException.class, () -> entry.main(new String[] {"OTHER"})));
  }

  private static void throwUnknown(Throwable failure) {
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }

  private static void throwAny(Throwable failure) throws IOException {
    if (failure instanceof IOException io) throw io;
    throwUnknown(failure);
  }
}
