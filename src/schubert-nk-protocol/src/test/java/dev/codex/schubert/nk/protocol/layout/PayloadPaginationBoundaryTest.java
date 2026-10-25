package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Direct semantic component fixtures, not named-mapper or business integration acceptance. Trace:
 * NK-PRO-002; MSG001-011; UI234/SS322 section 9; Program002/006; PAGE001-003.
 */
final class PayloadPaginationBoundaryTest {
  @Test
  void page001SecondPageHasIndependentExpectedBounds() {
    // UI234: ceil(101/100)=2, first=(2-1)*100+1=101, last=min(200,101)=101.
    assertDoesNotThrow(() -> PayloadSemanticValidator.validate(page(2, 101, 2, 101, 101, 1)));
  }

  @Test
  void page002MaximumEffectivePageKeepsExactNineDigitArithmetic() {
    // Fixed UI boundary: 999999*100=99999900; first is last-99, not a production calculation.
    assertDoesNotThrow(
        () ->
            PayloadSemanticValidator.validate(
                page(999_999, 99_999_900, 999_999, 99_999_801, 99_999_900, 100)));
  }

  @Test
  void page003RejectsIndependentRangeAndOneFieldArithmeticChanges() {
    for (TypedPayloadValues invalid :
        List.of(
            page(0, 101, 2, 101, 101, 1),
            page(1_000_000, 99_999_900, 999_999, 99_999_801, 99_999_900, 100),
            page(2, 101, 2, 100, 101, 1),
            page(2, 101, 2, 101, 102, 1),
            page(2, 101, 2, 101, 101, 0),
            page(2, 101, 3, 101, 101, 1))) {
      assertThrows(
          LayoutValidationException.class, () -> PayloadSemanticValidator.validate(invalid));
    }
  }

  private static TypedPayloadValues page(
      long effectivePage,
      long totalCount,
      long totalPages,
      long firstResult,
      long lastResult,
      int recordCount) {
    FieldValueSet data =
        new FieldValueSet(
            Map.of(
                "Page size", new FieldValue.Numeric(100),
                "Effective page", new FieldValue.Numeric(effectivePage),
                "Total count", new FieldValue.Numeric(totalCount),
                "Total pages", new FieldValue.Numeric(totalPages),
                "First result", new FieldValue.Numeric(firstResult),
                "Last result", new FieldValue.Numeric(lastResult)));
    FieldValueSet recordFields =
        new FieldValueSet(
            Map.of("Line番号", new FieldValue.Numeric(1), "Audio有無", new FieldValue.Flag(false)));
    PayloadData payload = () -> data;
    PayloadRecord record = () -> recordFields;
    return new TypedPayloadValues(
        new LayoutId("SRCRSP01"), payload, Collections.nCopies(recordCount, record));
  }
}
