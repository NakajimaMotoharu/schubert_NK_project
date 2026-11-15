package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-CMD-VALUE001..003; SS312/332/351/354: provider result is never persisted completion. */
final class QuestionValueContractTest {
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID CORRELATION = new UUID(0, 2);
  private static final String BODY = "PUBLIC_ANSWER\ne\u0301";

  @Test
  void value001UtcYearAndMicrosecondGoldenBoundsPreserveTraceAndTruncateBeforeRangeCheck() {
    String[][] vectors = {
      {"0001-01-01T00:00:00Z", "0001-01-01T00:00:00Z"},
      {"9999-12-31T23:59:59.999999999Z", "9999-12-31T23:59:59.999999Z"},
      {"2024-01-01T00:00:00.123456789Z", "2024-01-01T00:00:00.123456Z"},
      {"1969-12-31T23:59:59.999999999Z", "1969-12-31T23:59:59.999999Z"}
    };
    for (String[] vector : vectors) {
      QuestionCommandMetadata value =
          new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.parse(vector[0]));
      assertEquals(Instant.parse(vector[1]), value.at());
      assertEquals(MESSAGE, value.messageId());
      assertEquals(CORRELATION, value.correlationId());
      assertEquals("QuestionCommandMetadata[REDACTED]", value.toString());
    }
    for (String outside : List.of("0000-12-31T23:59:59.999999999Z", "+10000-01-01T00:00:00Z")) {
      Instant at = Instant.parse(outside);
      assertEquals(
          "command time is outside UTC range",
          assertThrows(
                  IllegalArgumentException.class,
                  () -> new QuestionCommandMetadata(MESSAGE, CORRELATION, at))
              .getMessage());
    }
  }

  @Test
  void value002EveryTraceComponentDefinesValueIdentityAfterCanonicalMicrosecondTruncation() {
    QuestionCommandMetadata value =
        new QuestionCommandMetadata(MESSAGE, CORRELATION, Instant.EPOCH);
    sameValue(
        value,
        new QuestionCommandMetadata(
            MESSAGE, CORRELATION, Instant.parse("1970-01-01T00:00:00.000000999Z")),
        List.of(
            new QuestionCommandMetadata(CORRELATION, CORRELATION, Instant.EPOCH),
            new QuestionCommandMetadata(MESSAGE, MESSAGE, Instant.EPOCH),
            new QuestionCommandMetadata(
                MESSAGE, CORRELATION, Instant.parse("1970-01-01T00:00:00.000001Z"))));
  }

  @Test
  void value003ProviderAnswerRetainsExactBodyAndTimeWithClosedRenderingAndNonnullComponents() {
    Instant at = Instant.parse("2024-01-01T00:00:00.123456789Z");
    AnswerResult value = new AnswerResult(BODY, at);
    assertEquals(BODY, value.body());
    assertEquals(at, value.answeredAt());
    assertEquals("AnswerResult[REDACTED]", value.toString());
    assertEquals("", new AnswerResult("", Instant.EPOCH).body());
    sameValue(
        value,
        new AnswerResult(BODY, at),
        List.of(new AnswerResult("other", at), new AnswerResult(BODY, Instant.EPOCH)));
    assertEquals(
        "answer body",
        assertThrows(NullPointerException.class, () -> new AnswerResult(null, at)).getMessage());
    assertEquals(
        "answer time",
        assertThrows(NullPointerException.class, () -> new AnswerResult(BODY, null)).getMessage());
  }

  private static <T> void sameValue(T value, T equal, List<T> different) {
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, "different type");
    for (T other : different) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
