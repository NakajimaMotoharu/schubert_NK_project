package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-QST-RNGREC-001..004; SS331 public identifier only, memory-supplied failure/recovery. */
final class QuestionReceiptRecoveryTest {
  private static final int PARTIAL_FAILURE_DRAW = 13;
  private static final int LAST_FAILURE_DRAW = 25;
  private static final String ZERO_VECTOR = "00000000000000000000000000";
  private static final String LAST_VECTOR = "ZZZZZZZZZZZZZZZZZZZZZZZZZZ";

  @Test
  void everyFailedDrawReleasesTheGeneratorForAnotherThread() throws Exception {
    for (int position = 0; position < 26; position++) {
      int failureAt = position;
      AtomicInteger draws = new AtomicInteger();
      IllegalStateException failure = new IllegalStateException("public fixture");
      QuestionReceiptIdGenerator generator =
          new QuestionReceiptIdGenerator(
              bound -> {
                assertEquals(32, bound);
                if (draws.getAndIncrement() == failureAt) {
                  throw failure;
                }
                return 0;
              });
      assertSame(failure, assertThrows(IllegalStateException.class, generator::generate));
      assertEquals(position + 1, draws.get());
      assertEquals(ZERO_VECTOR, fromAnotherThread(generator).value());
      assertEquals(position + 27, draws.get());
    }
  }

  @Test
  void invalidIndicesDoNotPoisonTheNextCandidate() throws Exception {
    for (int invalid : new int[] {-1, 32, Integer.MIN_VALUE, Integer.MAX_VALUE}) {
      AtomicInteger draws = new AtomicInteger();
      QuestionReceiptIdGenerator generator =
          new QuestionReceiptIdGenerator(
              bound -> {
                assertEquals(32, bound);
                return draws.getAndIncrement() == 0 ? invalid : 31;
              });
      IllegalStateException failure =
          assertThrows(IllegalStateException.class, generator::generate);
      assertEquals("receipt randomness is unavailable", failure.getMessage());
      assertEquals(1, draws.get());
      assertEquals(LAST_VECTOR, fromAnotherThread(generator).value());
      assertEquals(27, draws.get());
    }
  }

  @Test
  void discardedPartialAlphabetDoesNotPrefixTheNextCandidate() throws Exception {
    AtomicInteger draws = new AtomicInteger();
    IllegalStateException failure = new IllegalStateException("public fixture");
    QuestionReceiptIdGenerator generator =
        new QuestionReceiptIdGenerator(
            bound -> {
              assertEquals(32, bound);
              int draw = draws.getAndIncrement();
              if (draw == PARTIAL_FAILURE_DRAW) {
                throw failure;
              }
              return draw % 32;
            });
    assertSame(failure, assertThrows(IllegalStateException.class, generator::generate));
    assertEquals(14, draws.get());
    assertEquals("EFGHJKMNPQRSTVWXYZ01234567", fromAnotherThread(generator).value());
    assertEquals(40, draws.get());
  }

  @Test
  void lastDrawErrorKeepsIdentityAndStillUnlocks() throws Exception {
    AtomicInteger draws = new AtomicInteger();
    AssertionError failure = new AssertionError("public fixture");
    QuestionReceiptIdGenerator generator =
        new QuestionReceiptIdGenerator(
            bound -> {
              assertEquals(32, bound);
              if (draws.getAndIncrement() == LAST_FAILURE_DRAW) {
                throw failure;
              }
              return 31;
            });
    assertSame(failure, assertThrows(AssertionError.class, generator::generate));
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(26, draws.get());
    assertEquals(LAST_VECTOR, fromAnotherThread(generator).value());
    assertEquals(52, draws.get());
  }

  private static QuestionReceiptId fromAnotherThread(QuestionReceiptIdGenerator generator)
      throws Exception {
    try (ExecutorService worker = Executors.newSingleThreadExecutor()) {
      return worker.submit(generator::generate).get(5, TimeUnit.SECONDS);
    }
  }
}
