package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** Independent UI224/236 and SS331 26-character alphabet vectors; PG188, NK-QST-001. */
final class QuestionReceiptIdTest {
  private static final String ALLOWED = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
  private static final String FORWARD = "0123456789ABCDEFGHJKMNPQRS";
  private static final String REVERSE = "ZYXWVTSRQPNMKJHGFEDCBA9876";

  @Test
  @DisplayName("PT-QST-RID001 full alphabet without ULID leading restriction")
  void exactAlphabet() {
    for (char character : ALLOWED.toCharArray()) {
      String value = String.valueOf(character).repeat(26);
      assertEquals(value, new QuestionReceiptId(value).value());
    }
    assertEquals(FORWARD, new QuestionReceiptId(FORWARD).value());
    assertEquals(REVERSE, new QuestionReceiptId(REVERSE).value());
  }

  @Test
  @DisplayName("PT-QST-RID002 exact length and no padding")
  void lengthBoundaries() {
    for (int length : new int[] {0, 1, 25, 27, 4096}) {
      var error =
          assertThrows(
              IllegalArgumentException.class, () -> new QuestionReceiptId("A".repeat(length)));
      assertEquals("invalid receipt ID", error.getMessage());
    }
    assertEquals(26, new QuestionReceiptId("A".repeat(26)).value().length());
  }

  @Test
  @DisplayName("PT-QST-RID003 all ASCII forbidden characters at every position")
  void characterBoundaries() {
    List<Character> invalid = new ArrayList<>();
    for (char value = 0; value < 128; value++) if (ALLOWED.indexOf(value) < 0) invalid.add(value);
    invalid.addAll(List.of('\u00e9', '\uff21', '\ud800', '\udc00', '\u3000'));
    for (int position = 0; position < 26; position++) {
      for (char character : invalid) {
        char[] input = "A".repeat(26).toCharArray();
        input[position] = character;
        assertThrows(
            IllegalArgumentException.class, () -> new QuestionReceiptId(new String(input)));
      }
    }
  }

  @Test
  @DisplayName("PT-QST-RID004 independent forward and reverse random vectors")
  void independentRandomVector() {
    AtomicInteger calls = new AtomicInteger();
    var generator =
        new QuestionReceiptIdGenerator(
            bound -> {
              assertEquals(32, bound);
              int call = calls.getAndIncrement();
              return call < 26 ? call : 57 - call;
            });
    assertEquals(FORWARD, generator.generate().value());
    assertEquals(REVERSE, generator.generate().value());
    assertEquals(52, calls.get());
  }

  @Test
  @DisplayName("PT-QST-RID005 every randomness failure boundary, no fallback")
  void randomFailure() {
    for (int position = 0; position < 26; position++) {
      final int failureAt = position;
      AtomicInteger calls = new AtomicInteger();
      var failure = new IllegalStateException("public fixture");
      var generator =
          new QuestionReceiptIdGenerator(
              bound -> {
                assertEquals(32, bound);
                if (calls.getAndIncrement() == failureAt) throw failure;
                return 0;
              });
      assertSame(failure, assertThrows(IllegalStateException.class, generator::generate));
      assertEquals(position + 1, calls.get());
    }
    for (int invalid : new int[] {-1, 32, Integer.MIN_VALUE, Integer.MAX_VALUE}) {
      AtomicInteger calls = new AtomicInteger();
      var generator =
          new QuestionReceiptIdGenerator(
              bound -> {
                calls.incrementAndGet();
                return invalid;
              });
      assertEquals(
          "receipt randomness is unavailable",
          assertThrows(IllegalStateException.class, generator::generate).getMessage());
      assertEquals(1, calls.get());
    }
  }

  @Test
  @DisplayName("PT-QST-RID006 null contracts and production SecureRandom factory")
  void nullAndFactory() {
    assertThrows(NullPointerException.class, () -> new QuestionReceiptId(null));
    assertThrows(NullPointerException.class, () -> new QuestionReceiptIdGenerator(null));
    String candidate = QuestionReceiptIdGenerator.create().generate().value();
    assertEquals(26, candidate.length());
    for (char character : candidate.toCharArray()) assertTrue(ALLOWED.indexOf(character) >= 0);
  }

  @Test
  @DisplayName("PT-QST-RID007 private atomic generator state across64 callers")
  void concurrentCalls() throws InterruptedException, ExecutionException, TimeoutException {
    AtomicInteger calls = new AtomicInteger();
    var generator =
        new QuestionReceiptIdGenerator(
            bound -> {
              assertEquals(32, bound);
              return calls.getAndIncrement() % 32;
            });
    List<String> literalCycles =
        List.of(
            "0123456789ABCDEFGHJKMNPQRS", "TVWXYZ0123456789ABCDEFGHJK",
            "MNPQRSTVWXYZ0123456789ABCD", "EFGHJKMNPQRSTVWXYZ01234567",
            "89ABCDEFGHJKMNPQRSTVWXYZ01", "23456789ABCDEFGHJKMNPQRSTV",
            "WXYZ0123456789ABCDEFGHJKMN", "PQRSTVWXYZ0123456789ABCDEF",
            "GHJKMNPQRSTVWXYZ0123456789", "ABCDEFGHJKMNPQRSTVWXYZ0123",
            "456789ABCDEFGHJKMNPQRSTVWX", "YZ0123456789ABCDEFGHJKMNPQ",
            "RSTVWXYZ0123456789ABCDEFGH", "JKMNPQRSTVWXYZ0123456789AB",
            "CDEFGHJKMNPQRSTVWXYZ012345", "6789ABCDEFGHJKMNPQRSTVWXYZ");
    Map<String, Integer> expected = new HashMap<>();
    for (String value : literalCycles) expected.put(value, 4);
    Map<String, Integer> actual = new HashMap<>();
    var executor = Executors.newFixedThreadPool(8);
    try {
      List<Callable<QuestionReceiptId>> tasks = new ArrayList<>();
      for (int i = 0; i < 64; i++) tasks.add(generator::generate);
      // Holding the caller-visible monitor must not block the private generator lock.
      synchronized (generator) {
        var results = tasks.stream().map(executor::submit).toList();
        for (var result : results)
          actual.merge(result.get(5, TimeUnit.SECONDS).value(), 1, Integer::sum);
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(expected, actual);
    assertEquals(1664, calls.get());
  }

  @Test
  @DisplayName("PT-QST-RID008 value semantics and public-only evidence")
  void equalityAndPublicEvidence() throws IOException {
    var first = new QuestionReceiptId(FORWARD);
    var equal = new QuestionReceiptId(FORWARD);
    assertEquals(first, equal);
    assertEquals(first.hashCode(), equal.hashCode());
    assertNotEquals(first, new QuestionReceiptId(REVERSE));
    assertNotEquals(first, null);
    assertNotEquals(first, FORWARD);
    assertEquals("QuestionReceiptId[REDACTED]", first.toString());
    Path directory = Path.of("target/question-receipt-traces");
    Files.createDirectories(directory);
    Files.writeString(
        directory.resolve("PT-QST-RID008.txt"),
        "forward=0123456789ABCDEFGHJKMNPQRS\n"
            + "reverse=ZYXWVTSRQPNMKJHGFEDCBA9876\n"
            + "length=26\n"
            + "alphabetSize=32\n"
            + "randomDrawsPerId=26\n"
            + "ownerOrTimeInput=false\n");
  }

  @Test
  @DisplayName("PT-QST-RID009 provider failure releases private state to another worker")
  void providerFailureReleasesPrivateStateToAnotherWorker()
      throws InterruptedException, ExecutionException, TimeoutException {
    for (boolean fatal : List.of(false, true)) {
      var fatalFailure = new AssertionError("public provider fixture");
      var runtimeFailure = new IllegalStateException("public provider fixture");
      Throwable failure = fatal ? fatalFailure : runtimeFailure;
      var calls = new AtomicInteger();
      var generator =
          new QuestionReceiptIdGenerator(
              bound -> {
                assertEquals(32, bound);
                if (calls.getAndIncrement() == 0) {
                  if (fatal) throw fatalFailure;
                  throw runtimeFailure;
                }
                return 0;
              });
      assertSame(failure, assertThrows(failure.getClass(), generator::generate));
      var worker = Executors.newSingleThreadExecutor();
      try {
        assertEquals(
            "00000000000000000000000000",
            worker.submit(generator::generate).get(5, TimeUnit.SECONDS).value());
        assertEquals(27, calls.get());
      } finally {
        worker.shutdownNow();
        assertTrue(worker.awaitTermination(10, TimeUnit.SECONDS));
      }
    }
  }
}
