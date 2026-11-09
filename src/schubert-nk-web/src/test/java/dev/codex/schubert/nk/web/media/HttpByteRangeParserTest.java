package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-MED-001..004; independent SS333 §10 literal intervals. */
class HttpByteRangeParserTest {
  private static final long TOTAL = 2_097_155;

  @Test
  void literalRangesPreserveFirstSpecAndOneMebibyteCap() {
    assertEquals(
        new HttpByteRangeParser.Full(TOTAL),
        HttpByteRangeParser.parseFirst(Optional.empty(), TOTAL));
    Object[][] vectors = {
      {"bytes=0-0", 0L, 0L},
      {"bytes=0-1048575", 0L, 1_048_575L},
      {"bytes=0-1048576", 0L, 1_048_575L},
      {"bytes=1048576-", 1_048_576L, 2_097_151L},
      {"bytes=-1", 2_097_154L, 2_097_154L},
      {"bytes=-1048576", 1_048_579L, 2_097_154L},
      {"bytes=-2097155", 0L, 1_048_575L},
      {"bytes=-2097156", 0L, 1_048_575L},
      {"bytes=2097154-999999999999", 2_097_154L, 2_097_154L},
      {"bytes=0002-0004", 2L, 4L},
      {"bYtEs= \t2-4 \t,not-a-range", 2L, 4L},
      {"bytes=0-0,", 0L, 0L},
      {"bytes=2-4,99999999999999999999999999-", 2L, 4L}
    };
    for (Object[] vector : vectors) {
      var selected =
          assertInstanceOf(
              HttpByteRangeParser.Partial.class,
              HttpByteRangeParser.parseFirst(Optional.of((String) vector[0]), TOTAL));
      assertEquals(vector[1], selected.start(), (String) vector[0]);
      assertEquals(vector[2], selected.end());
      assertEquals((long) vector[2] - (long) vector[1] + 1, selected.length());
    }
    assertEquals(
        new HttpByteRangeParser.Partial(0, 0),
        HttpByteRangeParser.parseFirst(Optional.of("bytes=-99"), 1));
  }

  @Test
  void invalidGrammarBoundsAndArithmeticNeverSelectBytes() {
    for (String value :
        List.of(
            "",
            "bytes",
            "items=0-1",
            " bytes=0-1",
            "bytes=",
            "bytes=-",
            "bytes=1",
            "bytes=0--1",
            "bytes=--1",
            "bytes=+1-2",
            "bytes=1-+2",
            "bytes=0-1.5",
            "bytes=０-１",
            "bytes=1 -2",
            "bytes=1- 2",
            "bytes=2097155-",
            "bytes=3-2",
            "bytes=-0",
            "bytes=9223372036854775808-",
            "bytes=0-18446744073709551616",
            "bytes=-9223372036854775808",
            "bytes=invalid,0-1",
            "bytes=,0-1",
            "bytes=1-2-3")) {
      assertSame(
          HttpByteRangeParser.Unsatisfiable.INSTANCE,
          HttpByteRangeParser.parseFirst(Optional.of(value), TOTAL),
          value);
    }
    for (long size : new long[] {0, -1, Long.MIN_VALUE}) {
      assertSame(
          HttpByteRangeParser.Unsatisfiable.INSTANCE,
          HttpByteRangeParser.parseFirst(Optional.empty(), size));
      assertSame(
          HttpByteRangeParser.Unsatisfiable.INSTANCE,
          HttpByteRangeParser.parseFirst(Optional.of("bytes=0-0"), size));
    }
    assertSame(
        HttpByteRangeParser.Unsatisfiable.INSTANCE,
        HttpByteRangeParser.parseFirst(Optional.of("bytes=9223372036854775806-"), Long.MAX_VALUE));
  }

  @Test
  void nullAndConstructedSelectionsKeepInvariants() {
    assertThrows(NullPointerException.class, () -> HttpByteRangeParser.parseFirst(null, 1));
    assertThrows(IllegalArgumentException.class, () -> new HttpByteRangeParser.Full(0));
    assertThrows(IllegalArgumentException.class, () -> new HttpByteRangeParser.Full(-1));
    assertThrows(IllegalArgumentException.class, () -> new HttpByteRangeParser.Partial(-1, 0));
    assertThrows(IllegalArgumentException.class, () -> new HttpByteRangeParser.Partial(1, 0));
    assertThrows(
        IllegalArgumentException.class, () -> new HttpByteRangeParser.Partial(0, 1_048_576));
    assertEquals(1, new HttpByteRangeParser.Partial(Long.MAX_VALUE, Long.MAX_VALUE).length());
    assertEquals(1_048_576, new HttpByteRangeParser.Partial(0, 1_048_575).length());
    assertEquals(Long.MAX_VALUE, new HttpByteRangeParser.Full(Long.MAX_VALUE).length());
  }

  @Test
  void oneHundredConcurrentParsesHaveNoSharedState() throws Exception {
    var workers = Executors.newFixedThreadPool(8);
    try {
      List<Callable<HttpByteRangeParser.Selection>> tasks = new ArrayList<>();
      for (int index = 0; index < 100; index++) {
        int value = index;
        tasks.add(
            () ->
                HttpByteRangeParser.parseFirst(
                    Optional.of(value % 2 == 0 ? "bytes=" + value + "-" + value : "bytes=-0"),
                    TOTAL));
      }
      var results = workers.invokeAll(tasks, 10, TimeUnit.SECONDS);
      for (int index = 0; index < 100; index++)
        assertEquals(
            index % 2 == 0
                ? new HttpByteRangeParser.Partial(index, index)
                : HttpByteRangeParser.Unsatisfiable.INSTANCE,
            results.get(index).get(10, TimeUnit.SECONDS));
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
