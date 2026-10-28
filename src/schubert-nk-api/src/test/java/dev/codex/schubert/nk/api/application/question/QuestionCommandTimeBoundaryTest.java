package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** New UTC microsecond/year-boundary oracles; SS332/351, PT-CMD-TIMEBOUND-001..003. */
class QuestionCommandTimeBoundaryTest {
  private static final UUID MESSAGE = new UUID(1711, 1);
  private static final UUID CORRELATION = new UUID(1711, 2);
  private static final Instant LOWER = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant UPPER = Instant.parse("9999-12-31T23:59:59.999999Z");

  @Test
  void lowerBoundPreservesFloorWithoutRounding() {
    assertEquals(LOWER, metadata(LOWER).at());
    assertEquals(LOWER, metadata(LOWER.plusNanos(999)).at());
    assertThrows(IllegalArgumentException.class, () -> metadata(LOWER.minusNanos(1)));
  }

  @Test
  void upperBoundAcceptsSubmicrosecondTailOnly() {
    assertEquals(UPPER, metadata(UPPER).at());
    assertEquals(UPPER, metadata(UPPER.plusNanos(999)).at());
    assertThrows(IllegalArgumentException.class, () -> metadata(UPPER.plusNanos(1000)));
  }

  @Test
  void preEpochTruncationUsesUtcFloor() {
    var before = metadata(Instant.parse("1969-12-31T23:59:59.999999999Z"));
    var after = metadata(Instant.parse("1970-01-01T00:00:00.000000001Z"));
    assertEquals(Instant.parse("1969-12-31T23:59:59.999999Z"), before.at());
    assertEquals(Instant.EPOCH, after.at());
    assertEquals(MESSAGE, before.messageId());
    assertEquals(CORRELATION, before.correlationId());
    assertEquals(MESSAGE, after.messageId());
    assertEquals(CORRELATION, after.correlationId());
  }

  private static QuestionCommandMetadata metadata(Instant at) {
    return new QuestionCommandMetadata(MESSAGE, CORRELATION, at);
  }
}
