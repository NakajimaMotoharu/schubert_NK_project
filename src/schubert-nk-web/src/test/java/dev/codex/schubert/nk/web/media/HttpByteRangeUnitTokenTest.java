package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;

import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SS333 §10.1; the Range unit is an ASCII token with case-insensitive spelling. */
class HttpByteRangeUnitTokenTest {
  @Test
  void rejectsNonAsciiCaseEquivalentInTheUnit() {
    // PT-MED-RANGE-UNIT-001; U+017F is outside the HTTP token alphabet.
    assertSame(
        HttpByteRangeParser.Unsatisfiable.INSTANCE,
        HttpByteRangeParser.parseFirst(Optional.of("byte\u017F=0-0"), 3));
  }

  @Test
  void acceptsMixedAsciiCaseAndSelectsTheFirstInterval() {
    // PT-MED-RANGE-UNIT-002; inclusive offsets 1 through 2 have length two.
    var selected =
        assertInstanceOf(
            HttpByteRangeParser.Partial.class,
            HttpByteRangeParser.parseFirst(Optional.of("bYtEs=1-2,0-0"), 3));
    assertEquals(1, selected.start());
    assertEquals(2, selected.end());
    assertEquals(2, selected.length());
  }
}
