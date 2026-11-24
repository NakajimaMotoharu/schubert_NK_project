package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import java.time.Instant;
import java.util.stream.IntStream;
import org.junit.jupiter.api.Test;

/** PT-PRO-002-NPAGE001..003; NTSRSP01, UI224/236 and SS322/323/332. */
final class NotificationPaginationContractTest {
  private static final LayoutId NOTIFICATIONS = new LayoutId("NTSRSP01");
  private static final Instant TIME = Instant.parse("2026-11-01T00:00:00Z");

  @Test
  void fiftyRecordsFillTheFirstPageAndTheNextStartsAtFiftyOne() {
    assertDoesNotThrow(() -> validate(new PagedResponseData(1, 50, 51, 2, 1, 50), 50));
    assertDoesNotThrow(() -> validate(new PagedResponseData(2, 50, 51, 2, 51, 51), 1));
  }

  @Test
  void largestSixDigitPageUsesTheNotificationBound() {
    // 999999 * 50 = 49999950. The final full page starts 49 records before that.
    assertDoesNotThrow(
        () ->
            validate(
                new PagedResponseData(999_999, 50, 49_999_950, 999_999, 49_999_901, 49_999_950),
                50));
    assertThrows(
        LayoutValidationException.class,
        () ->
            validate(
                new PagedResponseData(999_999, 50, 49_999_951, 999_999, 49_999_901, 49_999_950),
                50));
  }

  @Test
  void rejectsSearchPageSizeAndNotificationOffsetOrRecordMismatch() {
    // This would be an internally consistent 100-item search page.
    assertThrows(
        LayoutValidationException.class,
        () -> validate(new PagedResponseData(1, 100, 51, 1, 1, 51), 51));
    assertThrows(
        LayoutValidationException.class,
        () -> validate(new PagedResponseData(2, 50, 51, 2, 50, 51), 1));
    assertThrows(
        LayoutValidationException.class,
        () -> validate(new PagedResponseData(2, 50, 51, 2, 51, 51), 0));
  }

  private static void validate(PagedResponseData data, int recordCount) {
    var rows =
        IntStream.rangeClosed(1, recordCount)
            .<PayloadRecord>mapToObj(
                id ->
                    new NotificationRecord(
                        new NotificationId(id),
                        "0".repeat(26),
                        NotificationType.ACCEPTED,
                        NotificationState.RECEIVED,
                        TIME,
                        TIME,
                        "fixture",
                        false))
            .toList();
    PayloadSemanticValidator.validate(new TypedPayloadValues(NOTIFICATIONS, data, rows));
  }
}
