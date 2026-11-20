package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;

import java.util.Optional;
import org.junit.jupiter.api.Test;

/** PT-MED-RANGE-LONG-001; SS333 §10.1–10.2. */
final class HttpByteRangeLongBoundaryTest {
  @Test
  void distinguishesTheLastRepresentableCapFromTheFirstOverflow() {
    var lastRepresentable =
        assertInstanceOf(
            HttpByteRangeParser.Partial.class,
            HttpByteRangeParser.parseFirst(
                Optional.of("bytes=9223372036853727232-"), Long.MAX_VALUE));
    assertEquals(9_223_372_036_853_727_232L, lastRepresentable.start());
    assertEquals(9_223_372_036_854_775_806L, lastRepresentable.end());
    assertEquals(1_048_575L, lastRepresentable.length());

    assertSame(
        HttpByteRangeParser.Unsatisfiable.INSTANCE,
        HttpByteRangeParser.parseFirst(Optional.of("bytes=9223372036853727233-"), Long.MAX_VALUE));
  }
}
