package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * Independent SS343 literal bytes, never production-generated expectations. PT-OPS-ENV-001..004.
 */
final class InspectorRunEnvironmentTest {
  private static final int UUID_WORD_BITS = 64;

  private static final UUID ID = UUID.fromString("00000000-0000-0000-0000-00000000005e");
  private static final BatchRun RUN = new BatchRun(ID, Instant.parse("2026-09-17T00:00:00Z"));
  private static final String GOLDEN =
      "NK_INSPECTOR_RUN_ID=00000000-0000-0000-0000-00000000005e\n"
          + "NK_INSPECTOR_CUTOFF=2026-09-17T00:00:00Z\n";

  @Test
  void independentGolden() {
    byte[] literal = bytes(GOLDEN);
    assertArrayEquals(literal, InspectorRunEnvironment.encode(RUN));
    assertDoesNotThrow(() -> InspectorRunEnvironment.requireMatches(RUN, literal));
    assertArrayEquals(bytes(GOLDEN), literal);
    assertEquals(ID, RUN.id());
    assertEquals(Instant.parse("2026-09-17T00:00:00Z"), RUN.cutoff());
  }

  @Test
  void mutationAndRunBinding() {
    byte[] literal = bytes(GOLDEN);
    for (int position = 0; position < literal.length; position++) {
      for (int value = 0; value <= 255; value++) {
        if ((byte) value == literal[position]) continue;
        byte[] altered = literal.clone();
        altered[position] = (byte) value;
        reject(RUN, altered);
      }
    }
    for (int length = 0; length < literal.length; length++)
      reject(RUN, Arrays.copyOf(literal, length));
    for (String wrong :
        List.of(
            GOLDEN + "\n",
            GOLDEN + "\0",
            GOLDEN + GOLDEN,
            GOLDEN.replace("\n", "\r\n"),
            GOLDEN.replace("RUN_ID=", "RUN_ID=\""),
            GOLDEN.replace("RUN_ID=", "RUN_ID= "),
            GOLDEN.replace("RUN_ID", "run_id"),
            GOLDEN.replace("CUTOFF=", "UNKNOWN="),
            GOLDEN.replace("00005e", "00005E"),
            "NK_INSPECTOR_CUTOFF=2026-09-17T00:00:00Z\n"
                + "NK_INSPECTOR_RUN_ID=00000000-0000-0000-0000-00000000005e\n"))
      reject(RUN, bytes(wrong));
    for (int bit = 0; bit < 128; bit++) {
      long high = ID.getMostSignificantBits();
      long low = ID.getLeastSignificantBits();
      if (bit < UUID_WORD_BITS) high ^= 1L << bit;
      else low ^= 1L << (bit - 64);
      reject(new BatchRun(new UUID(high, low), RUN.cutoff()), literal);
    }
    for (long nanos : List.of(-1000L, 1000L))
      reject(new BatchRun(ID, RUN.cutoff().plusNanos(nanos)), literal);
    assertArrayEquals(bytes(GOLDEN), literal);
    InspectorRunEnvironment.requireMatches(RUN, literal);
  }

  @Test
  void boundariesNullAndOwnership() {
    for (String timestamp : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      var run = new BatchRun(ID, Instant.parse(timestamp));
      byte[] expected =
          bytes(
              "NK_INSPECTOR_RUN_ID=00000000-0000-0000-0000-00000000005e\n"
                  + "NK_INSPECTOR_CUTOFF="
                  + timestamp
                  + "\n");
      assertArrayEquals(expected, InspectorRunEnvironment.encode(run));
      InspectorRunEnvironment.requireMatches(run, expected);
    }
    assertThrows(NullPointerException.class, () -> InspectorRunEnvironment.encode(null));
    assertThrows(
        NullPointerException.class,
        () -> InspectorRunEnvironment.requireMatches(null, bytes(GOLDEN)));
    assertThrows(
        NullPointerException.class, () -> InspectorRunEnvironment.requireMatches(RUN, null));
    byte[] first = InspectorRunEnvironment.encode(RUN);
    byte[] second = InspectorRunEnvironment.encode(RUN);
    assertNotSame(first, second);
    first[0] = 0;
    assertArrayEquals(bytes(GOLDEN), second);
    assertArrayEquals(bytes(GOLDEN), InspectorRunEnvironment.encode(RUN));
    reject(RUN, first);
  }

  @Test
  void concurrentUse() throws Exception {
    Set<byte[]> identities = Collections.newSetFromMap(new IdentityHashMap<>());
    var executor = Executors.newFixedThreadPool(16);
    try {
      var tasks = new ArrayList<Callable<byte[]>>();
      for (int i = 0; i < 64; i++)
        tasks.add(
            () -> {
              reject(RUN, new byte[0]);
              InspectorRunEnvironment.requireMatches(RUN, bytes(GOLDEN));
              return InspectorRunEnvironment.encode(RUN);
            });
      for (var result : executor.invokeAll(tasks, 5, TimeUnit.SECONDS)) {
        byte[] value = result.get(5, TimeUnit.SECONDS);
        assertArrayEquals(bytes(GOLDEN), value);
        assertTrue(identities.add(value));
      }
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS), "fixture workers not stopped");
    }
    assertEquals(64, identities.size());
  }

  private static byte[] bytes(String text) {
    return text.getBytes(StandardCharsets.US_ASCII);
  }

  private static void reject(BatchRun run, byte[] observed) {
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> InspectorRunEnvironment.requireMatches(run, observed));
    assertEquals("inspector run environment mismatch", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
