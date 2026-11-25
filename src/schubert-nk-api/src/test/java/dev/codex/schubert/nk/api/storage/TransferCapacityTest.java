package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** Decimal byte and counter oracle for logical capacity. PT-SCN-008-C01..C05. */
class TransferCapacityTest {
  private static final long CRITICAL_BYTE_GATE = 4_500_000_000L;
  private static final long CRITICAL_FILE_GATE = 9_000;
  private static final String NORMAL_CAPACITY_LEVEL = "NORMAL";
  private static final String CRITICAL_CAPACITY_LEVEL = "CRITICAL";

  @Test
  void c01EveryByteAndFileAlertBoundaryMatchesFixedThresholds() {
    for (long bytes :
        new long[] {
          0,
          3_499_999_999L,
          3_500_000_000L,
          3_500_000_001L,
          4_499_999_999L,
          4_500_000_000L,
          4_500_000_001L,
          Long.MAX_VALUE
        }) {
      var capacity = new TransferCapacity(bytes, 100);
      String expected =
          bytes >= 4_500_000_000L
              ? CRITICAL_CAPACITY_LEVEL
              : bytes >= 3_500_000_000L ? "WARNING" : NORMAL_CAPACITY_LEVEL;
      assertEquals(bytes, capacity.snapshot().bytes());
      assertEquals(100, capacity.snapshot().files());
      assertEquals(expected, capacity.snapshot().level().name());
      if (bytes >= CRITICAL_BYTE_GATE) assertCapacity(capacity);
    }
    for (long files : new long[] {0, 4_999, 5_000, 5_001, 8_999, 9_000, 9_001, Long.MAX_VALUE}) {
      var capacity = new TransferCapacity(0, files);
      String expected =
          files >= 9_000
              ? CRITICAL_CAPACITY_LEVEL
              : files >= 5_000 ? "WARNING" : NORMAL_CAPACITY_LEVEL;
      assertEquals(files, capacity.snapshot().files());
      assertEquals(expected, capacity.snapshot().level().name());
      if (files >= CRITICAL_FILE_GATE) assertCapacity(capacity);
    }
    assertThrows(IllegalArgumentException.class, () -> new TransferCapacity(-1, 0));
    assertThrows(IllegalArgumentException.class, () -> new TransferCapacity(0, -1));
    var capacity = new TransferCapacity(0, 0);
    for (long bytes : new long[] {-1, 0, 48_000_001, Long.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> capacity.reserve(bytes));
      assertEquals(0, capacity.snapshot().bytes());
      assertEquals(0, capacity.snapshot().files());
    }
    for (long bytes : new long[] {1, 4800, 48_000_000}) {
      var reservation = capacity.reserve(bytes);
      try {
        assertEquals(bytes, capacity.snapshot().bytes());
        assertEquals(1, capacity.snapshot().files());
      } finally {
        reservation.close();
      }
    }
  }

  @Test
  void c02RetainAndReleaseAreExactlyOnceIncludingUndeletedPartialFile() {
    var capacity = new TransferCapacity(4800, 1);
    var first = capacity.reserve(9600);
    try {
      var second = capacity.reserve(4800);
      try {
        assertEquals(19200, capacity.snapshot().bytes());
        assertEquals(3, capacity.snapshot().files());
        // Ready or undeleted partial files conservatively keep their full reservation.
        first.retain();
        first.close();
        assertEquals(19200, capacity.snapshot().bytes());
        assertThrows(IllegalStateException.class, first::retain);
        second.close();
        second.close();
        assertThrows(IllegalStateException.class, second::retain);
      } finally {
        second.close();
      }
    } finally {
      first.close();
    }
    assertEquals(14400, capacity.snapshot().bytes());
    assertEquals(2, capacity.snapshot().files());
    assertEquals(NORMAL_CAPACITY_LEVEL, capacity.snapshot().level().name());
    var snapshot = capacity.snapshot();
    capacity.reserve(4800).retain();
    assertEquals(14400, snapshot.bytes());
    assertEquals(19200, capacity.snapshot().bytes());
  }

  @Test
  void c02InFlightAdmissionCanReachCriticalButNeverExhaustTheFiveGbDesignBudget() {
    var capacity = new TransferCapacity(4_499_999_999L, 100);
    var reservation = capacity.reserve(48_000_000);
    try {
      assertEquals(4_547_999_999L, capacity.snapshot().bytes());
      assertEquals(101, capacity.snapshot().files());
      assertEquals(CRITICAL_CAPACITY_LEVEL, capacity.snapshot().level().name());
      assertCapacity(capacity);
    } finally {
      reservation.close();
    }
    assertEquals(4_499_999_999L, capacity.snapshot().bytes());
    assertEquals("WARNING", capacity.snapshot().level().name());
    capacity.reserve(1).retain();
    assertEquals(4_500_000_000L, capacity.snapshot().bytes());
    assertCapacity(capacity);
  }

  @Test
  void c03OnlyOneOf100SimultaneousReservationsCanCrossEachCriticalBoundary()
      throws InterruptedException, ExecutionException, TimeoutException {
    for (var capacity :
        List.of(new TransferCapacity(0, 8999), new TransferCapacity(4_499_999_999L, 100))) {
      var before = capacity.snapshot();
      try (var workers = new TransferFixtureWorkers(Executors.newFixedThreadPool(16))) {
        List<Callable<Optional<TransferCapacity.Reservation>>> tasks = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
          tasks.add(
              () -> {
                try {
                  return Optional.of(capacity.reserve(4800));
                } catch (CapacityExceededException ex) {
                  assertEquals(ResultCode.RESOURCE_LIMIT, ex.resultCode());
                  return Optional.empty();
                }
              });
        }
        int accepted = 0;
        for (var future : workers.executor().invokeAll(tasks, 10, TimeUnit.SECONDS)) {
          var result = future.get(10, TimeUnit.SECONDS);
          if (result.isPresent()) {
            accepted++;
            result.orElseThrow().retain();
          }
        }
        assertEquals(1, accepted);
      }
      assertEquals(before.bytes() + 4800, capacity.snapshot().bytes());
      assertEquals(before.files() + 1, capacity.snapshot().files());
      assertEquals(CRITICAL_CAPACITY_LEVEL, capacity.snapshot().level().name());
    }
  }

  @Test
  void c03CallerMonitorsCannotBlockReservationMetricsRetainOrClose()
      throws InterruptedException, ExecutionException, TimeoutException {
    var capacity = new TransferCapacity(0, 0);
    var acquired = new AtomicReference<TransferCapacity.Reservation>();
    try (var workers = new TransferFixtureWorkers(Executors.newVirtualThreadPerTaskExecutor())) {
      synchronized (capacity) {
        workers
            .executor()
            .submit(
                () -> {
                  acquired.set(capacity.reserve(4800));
                  assertEquals(4800, capacity.snapshot().bytes());
                })
            .get(5, TimeUnit.SECONDS);
      }
      var reservation = acquired.get();
      synchronized (reservation) {
        workers
            .executor()
            .submit(
                () -> {
                  reservation.retain();
                  reservation.close();
                  return 0;
                })
            .get(5, TimeUnit.SECONDS);
      }
      assertEquals(4800, capacity.snapshot().bytes());
      assertEquals(1, capacity.snapshot().files());
    } finally {
      var reservation = acquired.get();
      if (reservation != null) {
        reservation.close();
      }
    }
  }

  /** PT-SCN-008-C03-RACE; SS333 §13 and PG-D-057. */
  @Test
  void c03CompetingCloseAndRetainDischargeTheSameReservationOnce()
      throws InterruptedException, ExecutionException, TimeoutException {
    try (var workers = new TransferFixtureWorkers(Executors.newFixedThreadPool(2))) {
      var executor = workers.executor();
      for (int trial = 0; trial < 8; trial++) {
        var capacity = new TransferCapacity(128, 7);
        var reservation = capacity.reserve(4800);
        try {
          var start = new CyclicBarrier(2);
          var retain =
              executor.submit(
                  () -> {
                    start.await(5, TimeUnit.SECONDS);
                    try {
                      reservation.retain();
                      return true;
                    } catch (IllegalStateException alreadyClosed) {
                      return false;
                    }
                  });
          var close =
              executor.submit(
                  () -> {
                    start.await(5, TimeUnit.SECONDS);
                    reservation.close();
                    return null;
                  });
          boolean retained = retain.get(5, TimeUnit.SECONDS);
          close.get(5, TimeUnit.SECONDS);

          var after = capacity.snapshot();
          assertEquals(retained ? 4928 : 128, after.bytes());
          assertEquals(retained ? 8 : 7, after.files());
          assertEquals(NORMAL_CAPACITY_LEVEL, after.level().name());
          assertThrows(IllegalStateException.class, reservation::retain);
          reservation.close();
          assertEquals(after, capacity.snapshot());
        } finally {
          reservation.close();
        }
      }
    }
  }

  @Test
  void c04SnapshotsRetainValueIdentityAcrossReservations() {
    var capacity = new TransferCapacity(8_192, 7);
    var before = capacity.snapshot();
    var expected = new TransferCapacity.Snapshot(8_192, 7, TransferCapacity.Level.NORMAL);
    assertEquals(expected, before);
    assertEquals(before, expected);
    assertNotEquals(new TransferCapacity.Snapshot(8_193, 7, TransferCapacity.Level.NORMAL), before);
    assertNotEquals(new TransferCapacity.Snapshot(8_192, 8, TransferCapacity.Level.NORMAL), before);
    assertNotEquals(
        new TransferCapacity.Snapshot(8_192, 7, TransferCapacity.Level.WARNING), before);
    var observed = new HashMap<TransferCapacity.Snapshot, String>();
    observed.put(before, "before");
    assertEquals("before", observed.get(expected));
    assertEquals("Snapshot[bytes=8192, files=7, level=NORMAL]", before.toString());

    var reservation = capacity.reserve(4_800);
    try {
      assertEquals(
          new TransferCapacity.Snapshot(12_992, 8, TransferCapacity.Level.NORMAL),
          capacity.snapshot());
      assertEquals(expected, before);
    } finally {
      reservation.close();
    }
    assertEquals(expected, capacity.snapshot());
  }

  @Test
  void c05MetricLevelVocabularyIsClosedAndIndependentOfTheReturnedArray() {
    var levels = TransferCapacity.Level.values();
    var expected =
        Set.of(
            TransferCapacity.Level.NORMAL,
            TransferCapacity.Level.WARNING,
            TransferCapacity.Level.CRITICAL);
    assertEquals(expected, Set.of(levels));
    levels[0] = levels[1];
    assertEquals(expected, Set.of(TransferCapacity.Level.values()));
    assertSame(TransferCapacity.Level.CRITICAL, TransferCapacity.Level.valueOf("CRITICAL"));
    assertThrows(IllegalArgumentException.class, () -> TransferCapacity.Level.valueOf("UNKNOWN"));
  }

  private static void assertCapacity(TransferCapacity capacity) {
    var before = capacity.snapshot();
    var ex = assertThrows(CapacityExceededException.class, () -> capacity.reserve(4800));
    assertEquals(ResultCode.RESOURCE_LIMIT, ex.resultCode());
    assertEquals("resource capacity limit exceeded", ex.getMessage());
    assertNull(ex.getCause());
    assertEquals(0, ex.getSuppressed().length);
    assertEquals(before, capacity.snapshot());
  }
}
