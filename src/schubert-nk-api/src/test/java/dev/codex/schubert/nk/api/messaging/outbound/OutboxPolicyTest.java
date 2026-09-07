package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.Test;

/** PT-IDEM-009/010 destination allowlist and application retry boundaries. */
class OutboxPolicyTest {
  @Test
  void destinationMappingIsClosedToTwoPhysicalAddresses() {
    assertEquals("nk.async.work", OutboxDestination.ASYNC_WORK.address());
    assertEquals("nk.dead.letter", OutboxDestination.DLQ.address());
    assertEquals(OutboxDestination.ASYNC_WORK, OutboxDestination.fromAddress("nk.async.work"));
    assertEquals(OutboxDestination.DLQ, OutboxDestination.fromAddress("nk.dead.letter"));
    assertThrows(NullPointerException.class, () -> OutboxDestination.fromAddress(null));
    assertThrows(
        IllegalArgumentException.class, () -> OutboxDestination.fromAddress("nk.sync.request"));
  }

  @Test
  void retryScheduleUsesOneFiveThirtySixtyAndFiveMinuteCap() {
    assertEquals(Duration.ofSeconds(1), OutboxRetrySchedule.INSTANCE.delayAfterFailure(1));
    assertEquals(Duration.ofSeconds(5), OutboxRetrySchedule.INSTANCE.delayAfterFailure(2));
    assertEquals(Duration.ofSeconds(30), OutboxRetrySchedule.INSTANCE.delayAfterFailure(3));
    assertEquals(Duration.ofMinutes(1), OutboxRetrySchedule.INSTANCE.delayAfterFailure(4));
    assertEquals(Duration.ofMinutes(5), OutboxRetrySchedule.INSTANCE.delayAfterFailure(5));
    assertEquals(Duration.ofMinutes(5), OutboxRetrySchedule.INSTANCE.delayAfterFailure(100));
    assertThrows(
        IllegalArgumentException.class, () -> OutboxRetrySchedule.INSTANCE.delayAfterFailure(0));
    assertThrows(
        IllegalArgumentException.class, () -> OutboxRetrySchedule.INSTANCE.delayAfterFailure(101));
  }

  @Test
  void nextAttemptIsCalculatedFromExplicitFailureTime() {
    Instant failedAt = Instant.parse("2026-09-03T00:00:00Z");
    assertEquals(
        Instant.parse("2026-09-03T00:00:30Z"),
        OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, 3, 0));
    assertThrows(
        NullPointerException.class, () -> OutboxRetrySchedule.INSTANCE.nextAttemptAt(null, 1, 0));
  }

  @Test
  void retryJitterUsesIndependentExactBoundaryVectorsAfterCappingTheBase() {
    Instant failedAt = Instant.parse("2026-09-05T00:00:03Z");
    int[] attempts = {1, 2, 3, 4, 5, 100};
    long[] lowerMillis = {900, 4_500, 27_000, 54_000, 270_000, 270_000};
    long[] middleMillis = {1_000, 5_000, 30_000, 60_000, 300_000, 300_000};
    long[] upperMillis = {1_100, 5_500, 33_000, 66_000, 330_000, 330_000};
    for (int index = 0; index < attempts.length; index++) {
      assertEquals(
          failedAt.plusMillis(lowerMillis[index]),
          OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, attempts[index], -100));
      assertEquals(
          failedAt.plusMillis(middleMillis[index]),
          OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, attempts[index], 0));
      assertEquals(
          failedAt.plusMillis(upperMillis[index]),
          OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, attempts[index], 100));
    }
    assertEquals(
        Instant.parse("2026-09-05T00:00:04.001Z"),
        OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, 1, 1));
    assertThrows(
        IllegalArgumentException.class,
        () -> OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, 1, -101));
    assertThrows(
        IllegalArgumentException.class,
        () -> OutboxRetrySchedule.INSTANCE.nextAttemptAt(failedAt, 1, 101));
  }
}
