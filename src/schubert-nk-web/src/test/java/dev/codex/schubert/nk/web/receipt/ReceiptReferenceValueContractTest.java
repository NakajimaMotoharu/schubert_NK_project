package dev.codex.schubert.nk.web.receipt;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS331 §9.4 and SS351; RCPT001 synthetic value contracts, BUG-3216. */
final class ReceiptReferenceValueContractTest {
  private static final String ID = "0123456789ABCDEFGHJKMNPQRS";
  private static final String OTHER_ID = "ZTTVWXYZ0123456789ABCDEFGH";
  private static final String REDACTED = "ReceiptReference[redacted]";
  private static final Instant TIME = Instant.parse("2026-10-01T00:00:00.031Z");
  private static final long MAX_QUESTION_ID = 999999999999L;

  @Test
  void boundaryLiteralsAndAccessorsFollowApprovedProjection() {
    var minimum = new ReceiptReference(ID, 1L, Instant.EPOCH);
    assertEquals(ID, minimum.receiptId());
    assertEquals(1L, minimum.questionId());
    assertEquals(Instant.EPOCH, minimum.submittedAt());
    var maximum = new ReceiptReference(OTHER_ID, MAX_QUESTION_ID, TIME);
    assertEquals(OTHER_ID, maximum.receiptId());
    assertEquals(MAX_QUESTION_ID, maximum.questionId());
    assertEquals(TIME, maximum.submittedAt());
    assertEquals(REDACTED, maximum.toString());
  }

  @Test
  void missingAndInvalidValuesFailWithFixedDiagnostic() {
    assertThrows(NullPointerException.class, () -> ReceiptReference.requireReceiptId(null));
    assertThrows(NullPointerException.class, () -> new ReceiptReference(ID, 1L, null));
    for (String invalid :
        List.of(
            "",
            ID.substring(1),
            ID + "Q",
            "I" + ID.substring(1),
            "O" + ID.substring(1),
            "a" + ID.substring(1),
            " " + ID.substring(1),
            "日" + ID.substring(1))) {
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> ReceiptReference.requireReceiptId(invalid));
      assertEquals("receipt identifier is invalid", failure.getMessage());
    }
    for (long questionId : List.of(0L, MAX_QUESTION_ID + 1)) {
      var failure =
          assertThrows(
              IllegalArgumentException.class, () -> new ReceiptReference(ID, questionId, TIME));
      assertEquals("receipt reference is invalid", failure.getMessage());
    }
    var failure =
        assertThrows(
            IllegalArgumentException.class, () -> new ReceiptReference(ID, 1L, TIME.plusNanos(1L)));
    assertEquals("receipt reference is invalid", failure.getMessage());
  }

  @Test
  void equalityAndCollectionIdentityUseEveryComponent() {
    var value = new ReceiptReference(ID, 1L, TIME);
    var equal = new ReceiptReference(ID, 1L, Instant.ofEpochSecond(1790812800L, 31000000));
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertFalse(value.equals(null));
    assertFalse(value.equals(ID));
    var items = new HashSet<ReceiptReference>();
    assertTrue(items.add(value));
    assertFalse(items.add(equal));
    for (var other :
        List.of(
            new ReceiptReference(OTHER_ID, 1L, TIME),
            new ReceiptReference(ID, 2L, TIME),
            new ReceiptReference(ID, 1L, TIME.plusMillis(1L)))) {
      assertNotEquals(value, other);
      assertTrue(items.add(other));
      assertEquals(REDACTED, other.toString());
    }
    assertEquals(4, items.size());
  }
}
