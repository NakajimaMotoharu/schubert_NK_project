package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import org.junit.jupiter.api.Test;

/** SS342 SSC186/PT-OPS-CADDYFENCE004: literals are independent of production arithmetic. */
final class CaddyParentRemainingBudgetTest {
  @Test
  void caddyfence004SingleParentDomainWindowAndExactBoundaryNeverRenew() throws Exception {
    long floor = MorningStartupLaunchOwner.caddyRemainingFloor(100_000_000_000L);
    assertEquals(70_000_000_000L, floor);
    // The SAME floor survives preflight, await and login time; there is no new clock origin.
    assertTrue(95_000_000_000L > floor);
    assertTrue(80_000_000_000L > floor);
    assertTrue(70_000_000_001L > floor); // 29,999,999,999ns
    assertFalse(70_000_000_000L > floor); // 30,000,000,000ns
    assertFalse(69_999_999_999L > floor);
    assertEquals(0, MorningStartupLaunchOwner.caddyRemainingFloor(18_000_000_000L));
    assertEquals(0, MorningStartupLaunchOwner.caddyRemainingFloor(30_000_000_000L));
    assertEquals(1, MorningStartupLaunchOwner.caddyRemainingFloor(30_000_000_001L));
    assertEquals(
        1_770_000_000_000L, MorningStartupLaunchOwner.caddyRemainingFloor(1_800_000_000_000L));
    for (long invalid : new long[] {0, -1, Long.MIN_VALUE, 1_800_000_000_001L, Long.MAX_VALUE})
      assertThrows(IOException.class, () -> MorningStartupLaunchOwner.caddyRemainingFloor(invalid));
  }
}
