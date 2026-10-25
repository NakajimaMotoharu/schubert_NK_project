package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.Test;

/** NK-OPS-001; PT-OPS-MBUDGET001..002; literal SS341 30-minute oracle. */
final class MorningParentBudgetTest {
  private static final long THIRTY_MINUTES = 1_800_000_000_000L;

  @Test
  void nativeBorrowNeverRestartsParentDeadline() throws Exception {
    var clock = dev.codex.schubert.nk.storage.LinuxMonotonicClock.create();
    long fixed = clock.nowNanos() + 10_000_000_000L;
    var borrowed = MorningParentBudget.borrow(fixed);
    assertEquals(fixed, borrowed.deadlineNanos());
    assertTrue(borrowed.remainingNanos() > 0);
    assertTrue(borrowed.remainingNanos() <= 10_000_000_000L);
    assertThrows(IOException.class, () -> MorningParentBudget.borrow(0));
    assertThrows(IOException.class, () -> MorningParentBudget.borrow(-1));
    assertThrows(IOException.class, () -> MorningParentBudget.borrow(1));
    assertThrows(IOException.class, () -> MorningParentBudget.borrow(Long.MAX_VALUE));
  }

  @Test
  void mbudget001BoundaryIsFromFirstParentObservation() throws Exception {
    var now = new AtomicLong(7);
    var budget = new MorningParentBudget(now::get);
    assertEquals(THIRTY_MINUTES, budget.remainingNanos());
    assertEquals(1_800_000_000_007L, budget.deadlineNanos());
    budget.requireWithin();
    assertEquals(1_800_000_000_007L, budget.deadlineNanos());
    now.set(7 + THIRTY_MINUTES - 1);
    assertEquals(1, budget.remainingNanos());
    budget.requireWithin();
    now.incrementAndGet();
    assertEquals(
        "Morning parent budget unavailable",
        assertThrows(IOException.class, budget::requireWithin).getMessage());
    now.incrementAndGet();
    assertThrows(IOException.class, budget::requireWithin);
    assertThrows(NullPointerException.class, () -> new MorningParentBudget(null));
    MorningParentBudget.create()
        .requireWithin(); // Real monotonic factory, no resettable wall clock.
  }

  @Test
  void mbudget002SignedWrapAndBackwardClockDoNotRestartBudget() throws Exception {
    var now = new AtomicLong(Long.MAX_VALUE - 10);
    var budget = new MorningParentBudget(now::get);
    assertThrows(IOException.class, budget::deadlineNanos);
    now.set(Long.MIN_VALUE + 4); // 15 ns elapsed across signed nanoTime wrap.
    budget.requireWithin();
    now.set(Long.MAX_VALUE - 11);
    assertThrows(IOException.class, budget::requireWithin);
    now.set(Long.MAX_VALUE - 10);
    budget.requireWithin();
    now.set(Long.MAX_VALUE - 10 + THIRTY_MINUTES);
    assertThrows(IOException.class, budget::requireWithin);
  }
}
