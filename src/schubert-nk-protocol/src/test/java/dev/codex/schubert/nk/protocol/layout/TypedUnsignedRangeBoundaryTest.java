package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigInteger;
import org.junit.jupiter.api.Test;

/**
 * SS323 section 2 / NK-PRO-001: independent full-width numeric boundaries. BigInteger powers,
 * rather than Production's decimal accumulation, determine every expected upper bound.
 */
final class TypedUnsignedRangeBoundaryTest {
  private static final String FIELD = "quantity";

  @Test // PT-PRO-001-RANGE18-001
  void zeroAndMaximumAreAcceptedAtEverySupportedWidth() {
    for (int digits = 1; digits <= 18; digits++) {
      int width = digits;
      long maximum = BigInteger.TEN.pow(width).subtract(BigInteger.ONE).longValueExact();
      assertDoesNotThrow(() -> TypedFieldValues.requireUnsignedRange(FIELD, 0, width));
      assertDoesNotThrow(() -> TypedFieldValues.requireUnsignedRange(FIELD, maximum, width));
    }
  }

  @Test // PT-PRO-001-RANGE18-002
  void negativeAndFirstOverflowAreRejectedAtEverySupportedWidth() {
    for (int digits = 1; digits <= 18; digits++) {
      int width = digits;
      long overflow = BigInteger.TEN.pow(width).longValueExact();
      for (long invalid : new long[] {-1, overflow, Long.MIN_VALUE, Long.MAX_VALUE}) {
        var failure =
            assertThrows(
                LayoutValidationException.class,
                () -> TypedFieldValues.requireUnsignedRange(FIELD, invalid, width));
        assertEquals("typed numeric field is out of range: quantity", failure.getMessage());
      }
    }
  }

  @Test // PT-PRO-001-RANGE18-003
  void unsupportedWidthsAreRejectedBeforeNumericRangeEvaluation() {
    for (int width : new int[] {Integer.MIN_VALUE, 0, 19, Integer.MAX_VALUE}) {
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> TypedFieldValues.requireUnsignedRange(FIELD, Long.MIN_VALUE, width));
      assertEquals("numeric digit count must be between 1 and 18", failure.getMessage());
    }
  }

  @Test // PT-PRO-001-RANGE18-004
  void nullNameIsRejectedBeforeWidthAndValueValidation() {
    var failure =
        assertThrows(
            NullPointerException.class,
            () -> TypedFieldValues.requireUnsignedRange(null, Long.MIN_VALUE, Integer.MIN_VALUE));
    assertEquals("name", failure.getMessage());
  }
}
