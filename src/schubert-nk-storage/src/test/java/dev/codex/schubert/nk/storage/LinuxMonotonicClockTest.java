package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.lang.foreign.Linker;
import java.lang.foreign.ValueLayout;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SSC119/289 COWNER: independently specified CLOCK_MONOTONIC timespec and overflow vectors. */
class LinuxMonotonicClockTest {
  @Test
  void literalTimespecAndExactSignedLongBoundary() throws Exception {
    assertEquals(0L, clock(0, 0).nowNanos());
    assertEquals(2_999_999_999L, clock(2, 999_999_999).nowNanos());
    assertEquals(9_223_372_036_854_775_807L, clock(9_223_372_036L, 854_775_807).nowNanos());
  }

  @Test
  void negativeAndOverflowNeverWrapOrUseAnotherClock() {
    for (long[] pair :
        new long[][] {
          {-1, 0}, {0, -1}, {0, 1_000_000_000L}, {9_223_372_036L, 854_775_808}, {9_223_372_037L, 0}
        }) {
      var failure = assertThrows(IOException.class, () -> clock(pair[0], pair[1]).nowNanos());
      assertEquals("shared monotonic clock unavailable", failure.getMessage());
      assertNull(failure.getCause());
    }
    var failed = new LinuxMonotonicClock((id, result) -> -1);
    assertThrows(IOException.class, failed::nowNanos);
    assertThrows(NullPointerException.class, () -> new LinuxMonotonicClock(null));
  }

  @Test
  void fixedAbiPlatformAndSymbolFailures() throws Exception {
    var symbols = Linker.nativeLinker().defaultLookup();
    assertThrows(
        NullPointerException.class, () -> LinuxMonotonicClock.create(null, "amd64", symbols));
    assertThrows(
        NullPointerException.class, () -> LinuxMonotonicClock.create("Linux", null, symbols));
    assertThrows(
        NullPointerException.class, () -> LinuxMonotonicClock.create("Linux", "amd64", null));
    assertThrows(
        IllegalStateException.class, () -> LinuxMonotonicClock.create("Windows", "amd64", symbols));
    assertThrows(
        IllegalStateException.class, () -> LinuxMonotonicClock.create("Linux", "unknown", symbols));
    assertThrows(
        IllegalStateException.class,
        () -> LinuxMonotonicClock.create("Linux", "amd64", name -> Optional.empty()));
    for (String architecture : new String[] {"amd64", "x86_64", "aarch64"}) {
      long time = LinuxMonotonicClock.create("Linux", architecture, symbols).nowNanos();
      assertTrue(time > 0, "host uptime must be a positive monotonic observation");
    }
    var actual = LinuxMonotonicClock.create();
    long before = actual.nowNanos();
    long after = actual.nowNanos();
    assertTrue(after >= before, "CLOCK_MONOTONIC must never move backward within this boot");
  }

  private static LinuxMonotonicClock clock(long seconds, long nanos) {
    return new LinuxMonotonicClock(
        (id, result) -> {
          assertEquals(1, id, "only Linux CLOCK_MONOTONIC is selected");
          assertEquals(16, result.byteSize());
          result.set(ValueLayout.JAVA_LONG, 0, seconds);
          result.set(ValueLayout.JAVA_LONG, 8, nanos);
          return 0;
        });
  }
}
