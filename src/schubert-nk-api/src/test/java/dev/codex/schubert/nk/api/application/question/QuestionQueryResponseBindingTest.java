package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/**
 * PT-QRY-BIND001..004; UI236 IF027/029/030, SS323/332. Literal request IDs/page offsets,
 * independently specified response records; no repository, DB, service, or external IO.
 */
final class QuestionQueryResponseBindingTest {
  private static final String QUESTION_DETAIL = "QSDREQ01";
  private static final String NOTIFICATION_DETAIL = "NTDREQ01";
  private static final String QUESTION_SEARCH = "QSSREQ01";
  private static final String NOTIFICATION_SEARCH = "NTSREQ01";
  private static final String QUESTION_RESPONSE = "QSDRSP01";
  private static final String NOTIFICATION_RESPONSE = "NTDRSP01";
  private static final String PUBLIC_RECEIPT = "0123456789ABCDEFGHJKMNPQRS";
  private static final long ORIGINAL_ID = 999_999_999_999L;
  private static final long OTHER_ID = 999_999_999_998L;
  private static final int QUESTION_PAGE_OFFSET = 366;
  private static final int NOTIFICATION_PAGE_OFFSET = 46;

  @Test
  void qryBind001QuestionDetailRequiresOriginalId() {
    var request = request(QUESTION_DETAIL);
    assertDoesNotThrow(() -> request.validateResponse(question(ORIGINAL_ID)));
    assertThrows(
        IllegalArgumentException.class, () -> request.validateResponse(question(OTHER_ID)));
    assertDoesNotThrow(() -> request.validateResponse(question(ORIGINAL_ID)));
  }

  @Test
  void qryBind002NotificationDetailRequiresOriginalId() {
    var request = request(NOTIFICATION_DETAIL);
    assertDoesNotThrow(() -> request.validateResponse(notification(ORIGINAL_ID)));
    assertThrows(
        IllegalArgumentException.class, () -> request.validateResponse(notification(OTHER_ID)));
    assertDoesNotThrow(() -> request.validateResponse(notification(ORIGINAL_ID)));
  }

  @Test
  void qryBind003CorrectLayoutDoesNotAdmitWrongDataFamily() {
    for (String layout : List.of(QUESTION_DETAIL, NOTIFICATION_DETAIL)) {
      var request = request(layout);
      var body = new PagedResponseData(1, 50, 0, 1, 0, 0);
      var malformed = new TypedPayloadValues(request.responseLayoutId(), body, List.of());
      assertThrows(IllegalArgumentException.class, () -> request.validateResponse(malformed));
    }
    for (String layout : List.of(QUESTION_SEARCH, NOTIFICATION_SEARCH)) {
      var request = request(layout);
      var malformed =
          new TypedPayloadValues(
              request.responseLayoutId(), question(ORIGINAL_ID).data(), List.of());
      assertThrows(IllegalArgumentException.class, () -> request.validateResponse(malformed));
    }
  }

  @Test
  void qryBind004EmptySearchClampsEveryRequestedBoundaryToOne() {
    for (String layout : List.of(QUESTION_SEARCH, NOTIFICATION_SEARCH)) {
      for (String page : List.of("000001", "000002", "999999")) {
        byte[] bytes = QuestionQueryRequestTest.data(layout, false);
        int offset =
            layout.equals(QUESTION_SEARCH) ? QUESTION_PAGE_OFFSET : NOTIFICATION_PAGE_OFFSET;
        byte[] literal = page.getBytes(StandardCharsets.US_ASCII);
        System.arraycopy(literal, 0, bytes, offset, literal.length);
        var request = QuestionQueryRequest.decode(QuestionQueryRequestTest.message(layout, bytes));
        var correct =
            new TypedPayloadValues(
                request.responseLayoutId(), new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
        assertDoesNotThrow(() -> request.validateResponse(correct));
        var incorrect =
            new TypedPayloadValues(
                request.responseLayoutId(), new PagedResponseData(2, 50, 0, 1, 0, 0), List.of());
        assertThrows(IllegalArgumentException.class, () -> request.validateResponse(incorrect));
        assertDoesNotThrow(() -> request.validateResponse(correct));
      }
    }
  }

  private static QuestionQueryRequest request(String layout) {
    return QuestionQueryRequest.decode(
        QuestionQueryRequestTest.message(layout, QuestionQueryRequestTest.data(layout, false)));
  }

  private static TypedPayloadValues question(long id) {
    return new TypedPayloadValues(
        new LayoutId(QUESTION_RESPONSE),
        new QuestionDetailResponseData(
            new QuestionId(id),
            PUBLIC_RECEIPT,
            "u1",
            AnswerState.UNANSWERED,
            "question",
            Optional.empty(),
            Instant.parse("2026-10-01T00:00:00Z"),
            Optional.empty()),
        List.of());
  }

  private static TypedPayloadValues notification(long id) {
    return new TypedPayloadValues(
        new LayoutId(NOTIFICATION_RESPONSE),
        new NotificationDetailResponseData(
            new NotificationId(id),
            PUBLIC_RECEIPT,
            NotificationType.ACCEPTED,
            NotificationState.RECEIVED,
            Instant.parse("2026-10-01T00:00:00Z"),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            false,
            Optional.of("question"),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.of(new QuestionId(ORIGINAL_ID))),
        List.of());
  }
}
