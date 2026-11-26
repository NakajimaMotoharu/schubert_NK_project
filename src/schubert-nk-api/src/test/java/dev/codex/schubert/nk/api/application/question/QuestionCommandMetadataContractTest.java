package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-CMD-META001..003: non-null trace invariants and closed redaction; no backend resource. */
final class QuestionCommandMetadataContractTest {
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID CORRELATION = new UUID(0, 2);

  @Test
  void everyMissingTraceFieldRejectsAtConstructionWithoutNullNormalization() {
    assertEquals(
        "messageId",
        assertThrows(
                NullPointerException.class,
                () -> new QuestionCommandMetadata(null, CORRELATION, Instant.EPOCH))
            .getMessage());
    assertEquals(
        "correlationId",
        assertThrows(
                NullPointerException.class,
                () -> new QuestionCommandMetadata(MESSAGE, null, Instant.EPOCH))
            .getMessage());
    assertEquals(
        "at",
        assertThrows(
                NullPointerException.class,
                () -> new QuestionCommandMetadata(MESSAGE, CORRELATION, null))
            .getMessage());
  }

  @Test
  void renderingIsConstantForDistinctTraceValuesAndCannotExposeIdentityOrTime() {
    var first = new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.EPOCH);
    var second =
        new QuestionCommandMetadata(
            CORRELATION, MESSAGE, Instant.parse("9999-12-31T23:59:59.999999Z"));
    assertEquals("QuestionCommandMetadata[REDACTED]", first.toString());
    assertEquals("QuestionCommandMetadata[REDACTED]", second.toString());
    assertEquals(MESSAGE, first.messageId());
    assertEquals(CORRELATION, first.correlationId());
    assertEquals(Instant.EPOCH, first.at());
    assertEquals(CORRELATION, second.messageId());
    assertEquals(MESSAGE, second.correlationId());
    assertEquals(Instant.parse("9999-12-31T23:59:59.999999Z"), second.at());
  }

  @Test
  void equalityAndLookupUseBothIdentifiersAndTheNormalizedTimestamp() {
    Instant floor = Instant.parse("2000-01-01T00:00:00.123456Z");
    var stored = new QuestionCommandMetadata(MESSAGE, CORRELATION, floor);
    var canonicalEquivalent =
        new QuestionCommandMetadata(
            new UUID(0, 1), new UUID(0, 2), Instant.parse("2000-01-01T00:00:00.123456999Z"));

    assertEquals(floor, canonicalEquivalent.at());
    assertEquals(stored, canonicalEquivalent);
    assertEquals(canonicalEquivalent, stored);
    var owners = Map.of(stored, "fixture owner");
    assertEquals("fixture owner", owners.get(canonicalEquivalent));
    for (var different :
        List.of(
            new QuestionCommandMetadata(new UUID(0, 3), CORRELATION, floor),
            new QuestionCommandMetadata(MESSAGE, new UUID(0, 4), floor),
            new QuestionCommandMetadata(
                MESSAGE, CORRELATION, Instant.parse("2000-01-01T00:00:00.123457Z")))) {
      assertNotEquals(stored, different);
      assertNull(owners.get(different));
    }
    assertNotEquals(stored, null);
    assertNotEquals(stored, floor);
  }
}
