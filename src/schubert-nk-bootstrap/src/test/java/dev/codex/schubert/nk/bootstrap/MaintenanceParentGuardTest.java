package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-COWNER678001..006: independent monotonic/parent vectors, no actual Unit authority. */
final class MaintenanceParentGuardTest {
  private static MaintenanceOwnerFrame frame(boolean cleanup) {
    return new MaintenanceOwnerFrame(
        new UUID(0, 1),
        new UUID(0, 2),
        new UUID(0, 3),
        Instant.parse("2026-10-09T00:00:00Z"),
        new UUID(0, 4),
        new MaintenanceOwnerFrame.Parent("11111111111111111111111111111111", 41, 101),
        cleanup
            ? Optional.of(
                new MaintenanceOwnerFrame.Parent("22222222222222222222222222222222", 42, 102))
            : Optional.empty(),
        500);
  }

  @Test
  void twoClockObservationsBracketExactBorrowedParents() throws Exception {
    for (boolean cleanup : List.of(false, true)) {
      var owner = frame(cleanup);
      var events = new ArrayList<String>();
      var reads = new AtomicInteger();
      var guard =
          owner.parentsGuard(
              () -> {
                int index = reads.getAndIncrement();
                events.add("clock" + index);
                return index == 0 ? 100 : 200;
              },
              (kind, observed) -> {
                assertSame(owner, observed);
                events.add(kind.name());
              });
      assertEquals(300, guard.remainingNanos());
      assertEquals(
          cleanup
              ? List.of("clock0", "MORNING", "CLEANUP", "clock1")
              : List.of("clock0", "MORNING", "clock1"),
          events);
      assertEquals(2, reads.get());
    }
  }

  @Test
  void deadlineEqualityAndPastRejectBeforeParentObservation() {
    for (long before : new long[] {500, 501}) {
      var reads = new AtomicInteger();
      var guard =
          frame(true)
              .parentsGuard(
                  () -> {
                    reads.incrementAndGet();
                    return before;
                  },
                  (kind, owner) -> fail("parent after expiry"));
      assertEquals(
          "maintenance owner unavailable",
          assertThrows(IOException.class, guard::remainingNanos).getMessage());
      assertEquals(1, reads.get());
    }
    var original = new IOException("clock read failure");
    assertSame(
        original,
        assertThrows(
            IOException.class,
            frame(true)
                    .parentsGuard(
                        () -> {
                          throw original;
                        },
                        (kind, owner) -> fail("parent after read failure"))
                ::remainingNanos));
  }

  @Test
  void backwardEqualityDeadlineAndExpiredPostClockNeverReturnBudget() {
    for (long after : new long[] {99, 500, 501}) {
      var events = new ArrayList<String>();
      var reads = new AtomicInteger();
      var guard =
          frame(true)
              .parentsGuard(
                  () -> {
                    events.add("clock");
                    return reads.getAndIncrement() == 0 ? 100 : after;
                  },
                  (kind, owner) -> events.add(kind.name()));
      assertEquals(
          "maintenance owner unavailable",
          assertThrows(IOException.class, guard::remainingNanos).getMessage());
      assertEquals(List.of("clock", "MORNING", "CLEANUP", "clock"), events);
      assertEquals(2, reads.get());
    }
    var reads = new AtomicInteger();
    assertEquals(
        400,
        assertDoesNotThrow(
            () ->
                frame(false)
                    .parentsGuard(
                        () -> {
                          reads.incrementAndGet();
                          return 100;
                        },
                        (kind, owner) -> {})
                    .remainingNanos()));
    assertEquals(2, reads.get());
  }

  @Test
  void eachParentFailureAndSecondReadFailurePropagateSameException() {
    for (var failed : ChildStartupContext.MaintenanceParent.values()) {
      var calls = new ArrayList<String>();
      var original = new IOException("parent private detail");
      var actual =
          assertThrows(
              IOException.class,
              frame(true)
                      .parentsGuard(
                          () -> {
                            calls.add("clock");
                            return 100;
                          },
                          (kind, owner) -> {
                            calls.add(kind.name());
                            if (kind == failed) throw original;
                          })
                  ::remainingNanos);
      assertSame(original, actual);
      assertEquals(
          failed == ChildStartupContext.MaintenanceParent.MORNING
              ? List.of("clock", "MORNING")
              : List.of("clock", "MORNING", "CLEANUP"),
          calls);
    }
    var reads = new AtomicInteger();
    var original = new IOException("second read failure");
    assertSame(
        original,
        assertThrows(
            IOException.class,
            frame(false)
                    .parentsGuard(
                        () -> {
                          if (reads.getAndIncrement() == 1) throw original;
                          return 100;
                        },
                        (kind, owner) -> {})
                ::remainingNanos));
    assertEquals(2, reads.get());
  }

  @Test
  void preAndPostInterruptAreRetainedUntilCallerClearsThem() {
    assertFalse(Thread.currentThread().isInterrupted());
    Thread.currentThread().interrupt();
    try {
      assertThrows(
          IOException.class,
          frame(true)
                  .parentsGuard(
                      () -> {
                        fail("clock before interrupted guard");
                        return 100;
                      },
                      (kind, owner) -> fail("parent before interrupted guard"))
              ::remainingNanos);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    var reads = new AtomicInteger();
    try {
      assertThrows(
          IOException.class,
          frame(true)
                  .parentsGuard(
                      () -> {
                        reads.incrementAndGet();
                        return 100;
                      },
                      (kind, owner) -> {
                        if (kind == ChildStartupContext.MaintenanceParent.CLEANUP)
                          Thread.currentThread().interrupt();
                      })
              ::remainingNanos);
      assertTrue(Thread.currentThread().isInterrupted());
      assertEquals(2, reads.get());
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void nullObservationPortsNeverReadOrProbe() {
    MaintenanceOwnerFrame.Clock clock =
        () -> {
          fail("unexpected clock");
          return 100;
        };
    MaintenanceOwnerFrame.ParentProbe probe = (kind, owner) -> fail("unexpected parent");
    assertThrows(IllegalArgumentException.class, () -> frame(true).parentsGuard(null, probe));
    assertThrows(IllegalArgumentException.class, () -> frame(true).parentsGuard(clock, null));
  }
}
