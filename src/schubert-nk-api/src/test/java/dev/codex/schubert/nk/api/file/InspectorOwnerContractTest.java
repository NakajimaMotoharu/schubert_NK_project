package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.maintenance.InspectionExecution;
import dev.codex.schubert.nk.api.maintenance.InspectionProgress;
import dev.codex.schubert.nk.api.maintenance.InspectionRun;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** Literal internal vectors; synthetic parents confer no Unit/start authority. */
final class InspectorOwnerContractTest {
  private static final UUID BOOT = new UUID(0, 1);
  private static final InspectionRun RUN =
      new InspectionRun(new UUID(0, 2), Instant.parse("2026-10-09T00:00:00.123456Z"));
  private static final InspectionExecution RESULT =
      new InspectionExecution(
          InspectionExecution.Status.SUCCESS,
          Optional.of(new InspectionProgress(RUN, Optional.empty(), 0, 0, 0, true)));

  private static MaintenanceOwnerFrame owner(UUID boot, UUID run, Instant cutoff, boolean cleanup) {
    return new MaintenanceOwnerFrame(
        boot,
        run,
        new UUID(0, 3),
        cutoff,
        new UUID(0, 4),
        new MaintenanceOwnerFrame.Parent("11111111111111111111111111111111", 21, 101),
        cleanup
            ? Optional.of(
                new MaintenanceOwnerFrame.Parent("22222222222222222222222222222222", 22, 102))
            : Optional.empty(),
        500);
  }

  @Test
  void exactOwnerAndEachMismatch() throws Exception {
    InspectorApplication.validateOwner(
        RUN, BOOT.toString(), owner(BOOT, RUN.id(), RUN.cutoff(), true));
    for (var invalid :
        List.of(
            owner(new UUID(0, 5), RUN.id(), RUN.cutoff(), true),
            owner(BOOT, new UUID(0, 6), RUN.cutoff(), true),
            owner(BOOT, RUN.id(), RUN.cutoff().plusNanos(1000), true),
            owner(BOOT, RUN.id(), RUN.cutoff(), false))) {
      assertEquals(
          "maintenance owner unavailable",
          assertThrows(
                  IOException.class,
                  () -> InspectorApplication.validateOwner(RUN, BOOT.toString(), invalid))
              .getMessage());
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            InspectorApplication.validateOwner(
                null, BOOT.toString(), owner(BOOT, RUN.id(), RUN.cutoff(), true)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            InspectorApplication.validateOwner(
                RUN, null, owner(BOOT, RUN.id(), RUN.cutoff(), true)));
    assertThrows(
        IllegalArgumentException.class,
        () -> InspectorApplication.validateOwner(RUN, BOOT.toString(), null));
  }

  @Test
  void checksBeforeDuringAfterAndReturnsSameResult() throws Exception {
    var events = new ArrayList<String>();
    var actual =
        InspectorApplication.executeGuarded(
            RUN,
            () -> {
              events.add("parent");
              return 500;
            },
            () -> {
              events.add("inspector");
              return true;
            },
            (run, held) -> {
              assertSame(RUN, run);
              assertTrue(held.isPresent());
              events.add("work");
              assertEquals(500, held.orElseThrow().remainingNanos());
              return RESULT;
            });
    assertSame(RESULT, actual);
    assertEquals(
        List.of(
            "parent",
            "inspector",
            "parent",
            "work",
            "parent",
            "inspector",
            "parent",
            "parent",
            "inspector",
            "parent"),
        events);
  }

  @Test
  void expiredOrLostParentPreventsProbeAndWork() {
    for (boolean throwFailure : List.of(false, true)) {
      var events = new ArrayList<String>();
      var original = new IOException("private parent detail");
      var actual =
          assertThrows(
              IOException.class,
              () ->
                  InspectorApplication.executeGuarded(
                      RUN,
                      () -> {
                        events.add("parent");
                        if (throwFailure) throw original;
                        return 0;
                      },
                      () -> {
                        fail("probe before live parent");
                        return true;
                      },
                      (run, guard) -> {
                        fail("work before live parent");
                        return RESULT;
                      }));
      if (throwFailure) assertSame(original, actual);
      else assertEquals("maintenance owner unavailable", actual.getMessage());
      assertEquals(List.of("parent"), events);
    }
  }

  @Test
  void inspectorChangeOrReadFailurePreventsWork() {
    for (boolean throwFailure : List.of(false, true)) {
      var events = new ArrayList<String>();
      var original = new IOException("private inspector detail");
      var actual =
          assertThrows(
              IOException.class,
              () ->
                  InspectorApplication.executeGuarded(
                      RUN,
                      () -> {
                        events.add("parent");
                        return 500;
                      },
                      () -> {
                        events.add("inspector");
                        if (throwFailure) throw original;
                        return false;
                      },
                      (run, guard) -> {
                        fail("work after changed inspector");
                        return RESULT;
                      }));
      if (throwFailure) assertSame(original, actual);
      else assertEquals("maintenance owner unavailable", actual.getMessage());
      assertEquals(List.of("parent", "inspector"), events);
    }
  }

  @Test
  void postWorkExpiryAndTypedFailureNeverReturnResult() {
    var events = new ArrayList<String>();
    assertEquals(
        "maintenance owner unavailable",
        assertThrows(
                IOException.class,
                () ->
                    InspectorApplication.executeGuarded(
                        RUN,
                        () -> {
                          events.add("parent");
                          return events.contains("work") ? 0 : 500;
                        },
                        () -> {
                          events.add("inspector");
                          return true;
                        },
                        (run, guard) -> {
                          events.add("work");
                          return RESULT;
                        }))
            .getMessage());
    assertEquals(List.of("parent", "inspector", "parent", "work", "parent"), events);
    for (boolean crypto : List.of(false, true)) {
      events.clear();
      var io = new IOException("operation IO");
      var hash = new NoSuchAlgorithmException("operation hash");
      var actual =
          assertThrows(
              Exception.class,
              () ->
                  InspectorApplication.executeGuarded(
                      RUN,
                      () -> {
                        events.add("parent");
                        return 500;
                      },
                      () -> {
                        events.add("inspector");
                        return true;
                      },
                      (run, guard) -> {
                        events.add("work");
                        if (crypto) throw hash;
                        throw io;
                      }));
      assertSame(crypto ? hash : io, actual);
      assertEquals(List.of("parent", "inspector", "parent", "work"), events);
    }
  }

  @Test
  void nullDependenciesDoNoObservationOrWork() {
    MaintenanceOwnerFrame.Guard parents =
        () -> {
          fail("unexpected observation");
          return 500;
        };
    InspectorApplication.InspectorProbe probe =
        () -> {
          fail("unexpected probe");
          return true;
        };
    InspectorApplication.OwnedOperation operation =
        (run, guard) -> {
          fail("unexpected work");
          return RESULT;
        };
    assertThrows(
        IllegalArgumentException.class,
        () -> InspectorApplication.executeGuarded(null, parents, probe, operation));
    assertThrows(
        IllegalArgumentException.class,
        () -> InspectorApplication.executeGuarded(RUN, null, probe, operation));
    assertThrows(
        IllegalArgumentException.class,
        () -> InspectorApplication.executeGuarded(RUN, parents, null, operation));
    assertThrows(
        IllegalArgumentException.class,
        () -> InspectorApplication.executeGuarded(RUN, parents, probe, null));
  }
}
