package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;

import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS333 §10.1, SSC-476, PT-MED-RANGE-BOUND-001. */
final class HttpByteRangeDecimalLimitTest {
  @Test
  void acceptsTheMaximumDecimalEndAndRejectsTheNextInsteadOfClampingIt() {
    var bounded =
        assertInstanceOf(
            HttpByteRangeParser.Partial.class,
            HttpByteRangeParser.parseFirst(Optional.of("bytes=0-9223372036854775807"), 3));
    assertEquals(0, bounded.start());
    assertEquals(2, bounded.end());
    assertEquals(3, bounded.length());
    assertSame(
        HttpByteRangeParser.Unsatisfiable.INSTANCE,
        HttpByteRangeParser.parseFirst(Optional.of("bytes=0-9223372036854775808"), 3));
  }
}
