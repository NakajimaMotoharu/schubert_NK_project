package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Independent clock/empty-answer vectors; PG190, SS312 section8.1, 012001. */
class StubAnswerProviderTest {
  private static final String PUBLIC_QUESTION = "public";
  private static final String PUBLIC_ANSWER_BODY = "public body";
  private static final Instant NOW = Instant.parse("2026-09-20T00:00:00.123456789Z");

  @Test
  @DisplayName("PT-ASY-STB001 empty answer and exact clock")
  void emptyAnswerAndClock() {
    for (Instant value : Set.of(NOW, Instant.parse("1582-10-10T00:00:00Z"))) {
      AtomicInteger calls = new AtomicInteger();
      AnswerProvider provider =
          new StubAnswerProvider(
              clock(
                  () -> {
                    calls.incrementAndGet();
                    return value;
                  }));
      for (String question : Set.of("q", "q".repeat(4096))) {
        AnswerResult answer = provider.answer(question);
        assertEquals("", answer.body());
        assertEquals(value, answer.answeredAt());
      }
      assertEquals(2, calls.get());
    }
  }

  @Test
  @DisplayName("PT-ASY-STB002 null contracts")
  void nullContracts() {
    assertThrows(NullPointerException.class, () -> new StubAnswerProvider(null));
    AtomicInteger calls = new AtomicInteger();
    var provider =
        new StubAnswerProvider(
            clock(
                () -> {
                  calls.incrementAndGet();
                  return NOW;
                }));
    assertThrows(NullPointerException.class, () -> provider.answer(null));
    assertEquals(0, calls.get());
    assertThrows(NullPointerException.class, () -> new AnswerResult(null, NOW));
    assertThrows(NullPointerException.class, () -> new AnswerResult("", null));
  }

  @Test
  @DisplayName("PT-ASY-STB003 clock failures never become success")
  void clockFailures() {
    var runtime = new IllegalStateException("synthetic clock failure");
    var error = new AssertionError("synthetic clock failure");
    var first =
        new StubAnswerProvider(
            clock(
                () -> {
                  throw runtime;
                }));
    var second =
        new StubAnswerProvider(
            clock(
                () -> {
                  throw error;
                }));
    assertSame(
        runtime, assertThrows(IllegalStateException.class, () -> first.answer(PUBLIC_QUESTION)));
    assertSame(error, assertThrows(AssertionError.class, () -> second.answer(PUBLIC_QUESTION)));
    var missing = new StubAnswerProvider(clock(() -> null));
    assertThrows(NullPointerException.class, () -> missing.answer(PUBLIC_QUESTION));
  }

  @Test
  @DisplayName("PT-ASY-STB004 value and redaction")
  void resultValueAndRedaction() {
    var first = new AnswerResult(PUBLIC_ANSWER_BODY, NOW);
    var same = new AnswerResult(PUBLIC_ANSWER_BODY, NOW);
    assertEquals(PUBLIC_ANSWER_BODY, first.body());
    assertEquals(NOW, first.answeredAt());
    assertEquals(first, same);
    assertEquals(first.hashCode(), same.hashCode());
    assertNotEquals(first, new AnswerResult("", NOW));
    assertNotEquals(first, new AnswerResult(PUBLIC_ANSWER_BODY, NOW.plusSeconds(1)));
    assertEquals("AnswerResult[REDACTED]", first.toString());
  }

  @Test
  @DisplayName("PT-ASY-STB005 concurrent calls and public evidence")
  void concurrentCallsAndEvidence() throws IOException, InterruptedException, ExecutionException {
    AtomicInteger calls = new AtomicInteger();
    var provider = new StubAnswerProvider(clock(() -> NOW.plusSeconds(calls.getAndIncrement())));
    Set<Instant> expected = new HashSet<>();
    for (int i = 0; i < 64; i++) expected.add(NOW.plusSeconds(i));
    Set<Instant> actual = new HashSet<>();
    var executor = Executors.newFixedThreadPool(8);
    try {
      java.util.List<Callable<AnswerResult>> tasks = new java.util.ArrayList<>();
      for (int i = 0; i < 64; i++) tasks.add(() -> provider.answer(PUBLIC_QUESTION));
      for (var future : executor.invokeAll(tasks, 5, TimeUnit.SECONDS)) {
        AnswerResult answer = future.get();
        assertEquals("", answer.body());
        assertTrue(actual.add(answer.answeredAt()));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS), "stub test executor terminated");
    }
    assertEquals(expected, actual);
    assertEquals(64, calls.get());
    Path directory = Path.of("target/question-stub-traces");
    Files.createDirectories(directory);
    Files.writeString(
        directory.resolve("PT-ASY-STB005.txt"),
        "provider=STUB\n"
            + "answerLength=0\n"
            + "clockReadsPerCall=1\n"
            + "concurrentCalls=64\n"
            + "uniqueClockValues=64\n"
            + "externalCalls=0\n"
            + "rawBodySaved=false\n");
  }

  @Test
  @DisplayName("PT-ASY-STB006 expected failure contains only the fixed diagnostic")
  void fixedBusinessFailureValue() {
    var failure = new AnswerBusinessException();
    assertEquals("answer could not be produced", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Clock clock(Supplier<Instant> source) {
    return new Clock() {
      @Override
      public ZoneId getZone() {
        return ZoneOffset.UTC;
      }

      @Override
      public Clock withZone(ZoneId zone) {
        return this;
      }

      @Override
      public Instant instant() {
        return source.get();
      }
    };
  }
}
