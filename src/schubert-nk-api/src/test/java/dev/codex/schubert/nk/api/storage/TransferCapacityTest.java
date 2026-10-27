package dev.codex.schubert.nk.api.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Decimal byte/explicit counter oracle, no physical capacity test claimed. PT-SCN-008-C01..C03. */
class TransferCapacityTest {
  private static final long CRITICAL_BYTE_GATE = 4_500_000_000L;
  private static final long CRITICAL_FILE_GATE = 9_000;
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
              : bytes >= 3_500_000_000L ? "WARNING" : "NORMAL";
      assertEquals(bytes, capacity.snapshot().bytes());
      assertEquals(100, capacity.snapshot().files());
      assertEquals(expected, capacity.snapshot().level().name());
      if (bytes >= CRITICAL_BYTE_GATE) assertCapacity(capacity);
    }
    for (long files : new long[] {0, 4_999, 5_000, 5_001, 8_999, 9_000, 9_001, Long.MAX_VALUE}) {
      var capacity = new TransferCapacity(0, files);
      String expected =
          files >= 9_000 ? CRITICAL_CAPACITY_LEVEL : files >= 5_000 ? "WARNING" : "NORMAL";
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
      assertEquals(bytes, capacity.snapshot().bytes());
      assertEquals(1, capacity.snapshot().files());
      reservation.close();
    }
  }

  @Test
  void c02RetainAndReleaseAreExactlyOnceIncludingUndeletedPartialFile() {
    var capacity = new TransferCapacity(4800, 1);
    var first = capacity.reserve(9600);
    var second = capacity.reserve(4800);
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
    assertEquals(14400, capacity.snapshot().bytes());
    assertEquals(2, capacity.snapshot().files());
    assertEquals("NORMAL", capacity.snapshot().level().name());
    var snapshot = capacity.snapshot();
    capacity.reserve(4800).retain();
    assertEquals(14400, snapshot.bytes());
    assertEquals(19200, capacity.snapshot().bytes());
  }

  @Test
  void c02InFlightAdmissionCanReachCriticalButNeverExhaustTheFiveGbDesignBudget() {
    var capacity = new TransferCapacity(4_499_999_999L, 100);
    var reservation = capacity.reserve(48_000_000);
    assertEquals(4_547_999_999L, capacity.snapshot().bytes());
    assertEquals(101, capacity.snapshot().files());
    assertEquals(CRITICAL_CAPACITY_LEVEL, capacity.snapshot().level().name());
    assertCapacity(capacity);
    reservation.close();
    assertEquals(4_499_999_999L, capacity.snapshot().bytes());
    assertEquals("WARNING", capacity.snapshot().level().name());
    capacity.reserve(1).retain();
    assertEquals(4_500_000_000L, capacity.snapshot().bytes());
    assertCapacity(capacity);
  }

  @Test
  void c03OnlyOneOf100SimultaneousReservationsCanCrossEachCriticalBoundary() throws Exception {
    for (var capacity :
        List.of(new TransferCapacity(0, 8999), new TransferCapacity(4_499_999_999L, 100))) {
      var before = capacity.snapshot();
      try (var executor = Executors.newFixedThreadPool(16)) {
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
        for (var future : executor.invokeAll(tasks)) {
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
  void c03CallerMonitorsCannotBlockReservationMetricsRetainOrClose() throws Exception {
    var capacity = new TransferCapacity(0, 0);
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      TransferCapacity.Reservation reservation;
      synchronized (capacity) {
        reservation =
            executor
                .submit(
                    () -> {
                      var result = capacity.reserve(4800);
                      assertEquals(4800, capacity.snapshot().bytes());
                      return result;
                    })
                .get(5, TimeUnit.SECONDS);
      }
      synchronized (reservation) {
        executor
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
    }
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
