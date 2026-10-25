package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

/** PT-IDEM-REPORT-OVF001..003; SS324/332; BUG1760/YKT1511. Pure exact integer counts only. */
final class OutboxDispatchReportBoundaryTest {
  private static final int MAX = Integer.MAX_VALUE;

  @Test
  void acceptsZeroAndExactMaximumWithoutNarrowingValidCounts() {
    int[][] vectors = {
      {0, 0, 0, 0},
      {MAX, MAX, 0, 0},
      {MAX, 0, MAX, 0},
      {MAX, 0, 0, MAX},
      {MAX, MAX - 2, 1, 1},
      {MAX, 1, MAX - 2, 1},
      {MAX, 1, 1, MAX - 2}
    };
    for (int[] v : vectors) {
      var actual = assertDoesNotThrow(() -> new OutboxDispatchReport(v[0], v[1], v[2], v[3]));
      assertEquals(v[0], actual.claimed());
      assertEquals(v[1], actual.sent());
      assertEquals(v[2], actual.failed());
      assertEquals(v[3], actual.leaseLost());
      assertEquals((long) v[0], (long) v[1] + v[2] + v[3]);
    }
  }

  @Test
  void rejectsWrappedSumsInEveryComponentPosition() {
    int[][] vectors = {
      {0, MAX, MAX, 2},
      {0, MAX, 2, MAX},
      {0, 2, MAX, MAX},
      {1, MAX, MAX, 3},
      {1, MAX, 3, MAX},
      {1, 3, MAX, MAX},
      {MAX - 2, MAX, MAX, MAX}
    };
    long[] mathematicalSums = {
      4_294_967_296L,
      4_294_967_296L,
      4_294_967_296L,
      4_294_967_297L,
      4_294_967_297L,
      4_294_967_297L,
      6_442_450_941L
    };
    for (int i = 0; i < vectors.length; i++) {
      int[] v = vectors[i];
      assertEquals(mathematicalSums[i], (long) v[1] + v[2] + v[3]);
      assertThrows(
          IllegalArgumentException.class, () -> new OutboxDispatchReport(v[0], v[1], v[2], v[3]));
    }
  }

  @Test
  void rejectsEveryNegativeComponentAndNonWrappingMismatch() {
    int[][] vectors = {
      {-1, 0, 0, 0},
      {0, -1, 0, 0},
      {0, 0, -1, 0},
      {0, 0, 0, -1},
      {Integer.MIN_VALUE, 0, 0, 0},
      {0, Integer.MIN_VALUE, 0, 0},
      {0, 0, Integer.MIN_VALUE, 0},
      {0, 0, 0, Integer.MIN_VALUE},
      {1, 0, 0, 0},
      {0, 1, 0, 0},
      {MAX, MAX - 1, 0, 0},
      {MAX, MAX, 1, 0},
      {MAX, 0, MAX, 1},
      {MAX, 1, 0, MAX}
    };
    for (int[] v : vectors) {
      assertThrows(
          IllegalArgumentException.class, () -> new OutboxDispatchReport(v[0], v[1], v[2], v[3]));
    }
  }
}
