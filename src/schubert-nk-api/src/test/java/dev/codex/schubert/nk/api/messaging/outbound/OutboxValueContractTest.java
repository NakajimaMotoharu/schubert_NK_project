package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-OUTBOX-VALUE001..003; SS324/332 application-Outbox, no send/lease/DB or WebLog schedule. */
final class OutboxValueContractTest {
  @Test
  void value001ReportEqualityRetainsEveryConsistentCountAndOrdinaryPublicRendering() {
    OutboxDispatchReport value = new OutboxDispatchReport(3, 1, 1, 1);
    OutboxDispatchReport equal = new OutboxDispatchReport(3, 1, 1, 1);
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "different type");
    for (OutboxDispatchReport other :
        List.of(
            new OutboxDispatchReport(4, 2, 1, 1),
            new OutboxDispatchReport(3, 0, 2, 1),
            new OutboxDispatchReport(3, 1, 0, 2))) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
    assertEquals(
        "OutboxDispatchReport[claimed=3, sent=1, failed=1, leaseLost=1]", value.toString());
  }

  @Test
  void value002DestinationKeepsExactlyTwoFixedAddressesAndDefensiveClosedEnumFactories() {
    String[] names = {"ASYNC_WORK", "DLQ"};
    String[] addresses = {"nk.async.work", "nk.dead.letter"};
    OutboxDestination[] values = OutboxDestination.values();
    assertArrayEquals(names, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, values[i].ordinal());
      assertEquals(addresses[i], values[i].address());
      assertSame(values[i], OutboxDestination.valueOf(names[i]));
      assertSame(values[i], OutboxDestination.fromAddress(addresses[i]));
    }
    OutboxDestination[] copy = OutboxDestination.values();
    assertNotSame(values, copy);
    copy[0] = null;
    assertSame(OutboxDestination.ASYNC_WORK, OutboxDestination.values()[0]);
    for (String unknown : List.of("", "NK.ASYNC.WORK", "nk.async.work ", "unknown")) {
      IllegalArgumentException failure =
          assertThrows(
              IllegalArgumentException.class, () -> OutboxDestination.fromAddress(unknown));
      assertEquals("outbox destination is not allowed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    assertEquals(
        "address",
        assertThrows(NullPointerException.class, () -> OutboxDestination.fromAddress(null))
            .getMessage());
    assertThrows(IllegalArgumentException.class, () -> OutboxDestination.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> OutboxDestination.valueOf(null));
  }

  @Test
  void value003ApplicationRetryUsesIndependentFiveByThreeGoldenOffsetsAndAllHundredAttempts() {
    OutboxRetrySchedule schedule = OutboxRetrySchedule.INSTANCE;
    assertArrayEquals(
        new String[] {"INSTANCE"},
        Arrays.stream(OutboxRetrySchedule.values()).map(Enum::name).toArray(String[]::new));
    assertSame(schedule, OutboxRetrySchedule.valueOf("INSTANCE"));
    assertThrows(IllegalArgumentException.class, () -> OutboxRetrySchedule.valueOf("unknown"));
    assertThrows(NullPointerException.class, () -> OutboxRetrySchedule.valueOf(null));
    OutboxRetrySchedule[] copy = OutboxRetrySchedule.values();
    assertNotSame(copy, OutboxRetrySchedule.values());
    copy[0] = null;
    assertSame(schedule, OutboxRetrySchedule.values()[0]);
    long[] bases = {1000, 5000, 30000, 60000, 300000};
    long[][] offsets = {
      {900, 1000, 1100},
      {4500, 5000, 5500},
      {27000, 30000, 33000},
      {54000, 60000, 66000},
      {270000, 300000, 330000}
    };
    int[] jitters = {-100, 0, 100};
    for (int attempt = 1; attempt <= 100; attempt++) {
      int row = Math.min(attempt - 1, 4);
      assertEquals(Duration.ofMillis(bases[row]), schedule.delayAfterFailure(attempt));
      for (int i = 0; i < jitters.length; i++) {
        assertEquals(
            Instant.ofEpochMilli(offsets[row][i]),
            schedule.nextAttemptAt(Instant.EPOCH, attempt, jitters[i]));
      }
    }
    for (int invalid : new int[] {Integer.MIN_VALUE, -1, 0, 101, Integer.MAX_VALUE}) {
      assertThrows(IllegalArgumentException.class, () -> schedule.delayAfterFailure(invalid));
      assertThrows(
          IllegalArgumentException.class, () -> schedule.nextAttemptAt(Instant.EPOCH, invalid, 0));
    }
    for (int invalid : new int[] {Integer.MIN_VALUE, -101, 101, Integer.MAX_VALUE}) {
      assertThrows(
          IllegalArgumentException.class, () -> schedule.nextAttemptAt(Instant.EPOCH, 1, invalid));
    }
    assertThrows(NullPointerException.class, () -> schedule.nextAttemptAt(null, 1, 0));
    assertThrows(DateTimeException.class, () -> schedule.nextAttemptAt(Instant.MAX, 1, 0));
  }
}
