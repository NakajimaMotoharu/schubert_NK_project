package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
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
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** UI236/SS323 literal plain contracts; NK-QRY-001/NK-NTF-001; PT-QRY-PLAIN001..008; spec2015. */
class QuestionQueryPlainContractTest {
  private static final String USERNAME = "unit7";
  private static final String FROM_FIELD = "submittedFrom";
  private static final String TO_FIELD = "submittedTo";
  private static final String ORIGINAL_PAGE = "999999";
  private static final String QUESTION_SEARCH = "QSSREQ01";
  private static final String NOTIFICATION_SEARCH = "NTSREQ01";
  private static final String QUESTION_DETAIL = "QSDREQ01";
  private static final String NOTIFICATION_DETAIL = "NTDREQ01";
  private static final String QUESTION_RESPONSE = "QSSRSP01";
  private static final String NOTIFICATION_RESPONSE = "NTSRSP01";
  private static final String QUESTION_DETAIL_RESPONSE = "QSDRSP01";
  private static final String NOTIFICATION_DETAIL_RESPONSE = "NTDRSP01";
  private static final Instant NOW = Instant.parse("2026-10-01T00:00:00.123Z");
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(7, USERNAME, Role.ADMIN);

  @Test
  void plain001AbsentSearchFieldsAndOriginalPageAreRetained() {
    for (String layout : List.of(QUESTION_SEARCH, NOTIFICATION_SEARCH)) {
      var wire = wire(layout, searchBytes(layout, false));
      var request = QuestionQueryRequest.decode(wire);
      assertSame(wire.header(), request.header());
      assertFalse(request.detailRequest());
      assertFalse(request.usernameSpecified());
      assertEquals("QuestionQueryRequest[REDACTED]", request.toString());
      try (var canonical = request.canonical(ACTOR)) {
        assertEquals("7", canonical.ownerScope());
        assertEquals(layout, canonical.layoutId());
        assertEquals("001", canonical.layoutVersion());
        assertEquals("REQUEST:" + layout, canonical.target());
        var names =
            layout.equals(QUESTION_SEARCH)
                ? List.of("keyword", "username", "answerState", FROM_FIELD, TO_FIELD)
                : List.of("notificationType", FROM_FIELD, TO_FIELD);
        assertEquals(names.size() + 2, canonical.fields().size());
        for (int i = 0; i < names.size(); i++) {
          assertEquals(names.get(i), canonical.fields().get(i).name());
          assertEquals(
              names.get(i).startsWith("submitted") ? "T1" : "X1",
              canonical.fields().get(i).typeVersion());
          assertNull(canonical.fields().get(i).value());
        }
        assertEquals("page", canonical.fields().get(names.size()).name());
        assertEquals("N1", canonical.fields().get(names.size()).typeVersion());
        assertArrayEquals(
            ORIGINAL_PAGE.getBytes(StandardCharsets.US_ASCII),
            canonical.fields().get(names.size()).value());
        assertEquals("pageSize", canonical.fields().get(names.size() + 1).name());
        assertArrayEquals(
            "50".getBytes(StandardCharsets.US_ASCII),
            canonical.fields().get(names.size() + 1).value());
      }
    }
  }

  @Test
  void plain002QuestionFilledFieldsUseInterfaceOffsetsAndLiteralUtc() {
    var request =
        QuestionQueryRequest.decode(wire(QUESTION_SEARCH, searchBytes(QUESTION_SEARCH, true)));
    assertTrue(request.questionScope());
    assertTrue(request.usernameSpecified());
    assertEquals(QUESTION_RESPONSE, request.responseLayoutId().value());
    try (var canonical = request.canonical(ACTOR)) {
      var names =
          List.of("keyword", "username", "answerState", FROM_FIELD, TO_FIELD, "page", "pageSize");
      var types = List.of("X1", "X1", "X1", "T1", "T1", "N1", "N1");
      var values =
          List.of(
              "é_%",
              USERNAME,
              "ANSWERED",
              "2026-10-01T00:00:00.123Z",
              "2026-10-01T00:00:01.123Z",
              ORIGINAL_PAGE,
              "50");
      for (int i = 0; i < names.size(); i++) {
        assertEquals(names.get(i), canonical.fields().get(i).name());
        assertEquals(types.get(i), canonical.fields().get(i).typeVersion());
        assertArrayEquals(
            values.get(i).getBytes(StandardCharsets.UTF_8), canonical.fields().get(i).value());
      }
    }
  }

  @Test
  void plain003NotificationFilledFieldsKeepTypeAndDates() {
    var request =
        QuestionQueryRequest.decode(
            wire(NOTIFICATION_SEARCH, searchBytes(NOTIFICATION_SEARCH, true)));
    assertFalse(request.questionScope());
    assertFalse(request.usernameSpecified());
    assertEquals(NOTIFICATION_RESPONSE, request.responseLayoutId().value());
    try (var canonical = request.canonical(ACTOR)) {
      var names = List.of("notificationType", FROM_FIELD, TO_FIELD, "page", "pageSize");
      var types = List.of("X1", "T1", "T1", "N1", "N1");
      var values =
          List.of(
              "COMPLETED",
              "2026-10-01T00:00:00.123Z",
              "2026-10-01T00:00:01.123Z",
              ORIGINAL_PAGE,
              "50");
      for (int i = 0; i < names.size(); i++) {
        assertEquals(names.get(i), canonical.fields().get(i).name());
        assertEquals(types.get(i), canonical.fields().get(i).typeVersion());
        assertArrayEquals(
            values.get(i).getBytes(StandardCharsets.UTF_8), canonical.fields().get(i).value());
      }
    }
  }

  @Test
  void plain004DetailIdsHaveDistinctCanonicalNamesAndResponseLayouts() {
    var question = detail(QUESTION_DETAIL);
    var notification = detail(NOTIFICATION_DETAIL);
    assertTrue(question.questionScope());
    assertFalse(notification.questionScope());
    assertTrue(question.detailRequest());
    assertTrue(notification.detailRequest());
    assertFalse(question.usernameSpecified());
    assertEquals(QUESTION_DETAIL_RESPONSE, question.responseLayoutId().value());
    assertEquals(NOTIFICATION_DETAIL_RESPONSE, notification.responseLayoutId().value());
    try (var q = question.canonical(ACTOR);
        var n = notification.canonical(ACTOR)) {
      assertEquals(1, q.fields().size());
      assertEquals(1, n.fields().size());
      assertEquals("questionId", q.fields().getFirst().name());
      assertEquals("notificationId", n.fields().getFirst().name());
      assertEquals("N1", q.fields().getFirst().typeVersion());
      assertEquals("N1", n.fields().getFirst().typeVersion());
      assertArrayEquals("3".getBytes(StandardCharsets.US_ASCII), q.fields().getFirst().value());
      assertArrayEquals("3".getBytes(StandardCharsets.US_ASCII), n.fields().getFirst().value());
    }
  }

  @Test
  void plain005SearchResponseUsesEffectivePageWithoutChangingOriginal() {
    var question =
        QuestionQueryRequest.decode(wire(QUESTION_SEARCH, searchBytes(QUESTION_SEARCH, false)));
    var notification =
        QuestionQueryRequest.decode(
            wire(NOTIFICATION_SEARCH, searchBytes(NOTIFICATION_SEARCH, false)));
    assertDoesNotThrow(() -> question.validateResponse(page(QUESTION_RESPONSE, 1, 50, 0)));
    assertDoesNotThrow(() -> notification.validateResponse(page(NOTIFICATION_RESPONSE, 1, 50, 0)));
    // Original page 999999 and effective page 1 intentionally differ (empty result).
    try (var canonical = question.canonical(ACTOR)) {
      assertArrayEquals(
          ORIGINAL_PAGE.getBytes(StandardCharsets.US_ASCII), canonical.fields().get(5).value());
    }
  }

  @Test
  void plain006SearchWrongPageTypeLayoutSizeAndCountAreRejected() {
    var question =
        QuestionQueryRequest.decode(wire(QUESTION_SEARCH, searchBytes(QUESTION_SEARCH, false)));
    var notification =
        QuestionQueryRequest.decode(
            wire(NOTIFICATION_SEARCH, searchBytes(NOTIFICATION_SEARCH, false)));
    assertThrows(
        IllegalArgumentException.class,
        () -> question.validateResponse(page(QUESTION_RESPONSE, 0, 50, 0)));
    assertThrows(
        IllegalArgumentException.class,
        () -> notification.validateResponse(page(NOTIFICATION_RESPONSE, 0, 50, 0)));
    assertThrows(
        IllegalArgumentException.class,
        () -> question.validateResponse(page(NOTIFICATION_RESPONSE, 1, 50, 0)));
    var wrongType =
        new TypedPayloadValues(new LayoutId(QUESTION_RESPONSE), questionData(3), List.of());
    assertThrows(IllegalArgumentException.class, () -> question.validateResponse(wrongType));
    assertThrows(
        LayoutValidationException.class,
        () -> question.validateResponse(page(QUESTION_RESPONSE, 1, 49, 0)));
    assertThrows(
        LayoutValidationException.class,
        () -> notification.validateResponse(page(NOTIFICATION_RESPONSE, 1, 50, 1)));
  }

  @Test
  void plain007DetailTargetAndTypeAreBoundToEachOriginalRequest() {
    var question = detail(QUESTION_DETAIL);
    var notification = detail(NOTIFICATION_DETAIL);
    assertDoesNotThrow(
        () -> question.validateResponse(typed(QUESTION_DETAIL_RESPONSE, questionData(3))));
    assertDoesNotThrow(
        () ->
            notification.validateResponse(
                typed(NOTIFICATION_DETAIL_RESPONSE, notificationData(3))));
    assertThrows(
        IllegalArgumentException.class,
        () -> question.validateResponse(typed(QUESTION_DETAIL_RESPONSE, questionData(4))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            notification.validateResponse(
                typed(NOTIFICATION_DETAIL_RESPONSE, notificationData(4))));
    assertThrows(
        IllegalArgumentException.class,
        () -> question.validateResponse(typed(QUESTION_DETAIL_RESPONSE, notificationData(3))));
    assertThrows(
        IllegalArgumentException.class,
        () -> notification.validateResponse(typed(NOTIFICATION_DETAIL_RESPONSE, questionData(3))));
  }

  @Test
  void plain008MalformedAndNullBoundariesNeverDelegateToRepository() {
    assertThrows(NullPointerException.class, () -> QuestionQueryRequest.decode(null));
    for (String layout :
        List.of(QUESTION_SEARCH, NOTIFICATION_SEARCH, QUESTION_DETAIL, NOTIFICATION_DETAIL)) {
      byte[] valid =
          layout.equals(QUESTION_SEARCH) || layout.equals(NOTIFICATION_SEARCH)
              ? searchBytes(layout, false)
              : "000000000003".getBytes(StandardCharsets.US_ASCII);
      var request = QuestionQueryRequest.decode(wire(layout, valid));
      assertThrows(NullPointerException.class, () -> request.canonical(null));
      assertThrows(NullPointerException.class, () -> request.validateResponse(null));
      assertThrows(NullPointerException.class, () -> request.query(null, null, null));
      byte[] bad = valid.clone();
      bad[0] = 0;
      assertThrows(
          PermanentProtocolException.class, () -> QuestionQueryRequest.decode(wire(layout, bad)));
      byte[] shortened = Arrays.copyOf(valid, valid.length - 1);
      assertThrows(
          PermanentProtocolException.class,
          () -> QuestionQueryRequest.decode(wire(layout, shortened)));
    }
    var failure =
        assertThrows(
            PermanentProtocolException.class,
            () -> QuestionQueryRequest.decode(wire("ZZZREQ01", new byte[12])));
    assertEquals("question query request is invalid", failure.getMessage());
    assertNull(failure.getCause());
  }

  private static QuestionQueryRequest detail(String layout) {
    return QuestionQueryRequest.decode(
        wire(layout, "000000000003".getBytes(StandardCharsets.US_ASCII)));
  }

  private static TypedPayloadValues page(String layout, int effective, int size, int count) {
    return typed(layout, new PagedResponseData(effective, size, count, 1, count, count));
  }

  private static TypedPayloadValues typed(String layout, PayloadData value) {
    return new TypedPayloadValues(new LayoutId(layout), value, List.of());
  }

  private static QuestionDetailResponseData questionData(long id) {
    return new QuestionDetailResponseData(
        new QuestionId(id),
        "00000000000000000000000001",
        USERNAME,
        AnswerState.UNANSWERED,
        "question",
        Optional.empty(),
        NOW,
        Optional.empty());
  }

  private static NotificationDetailResponseData notificationData(long id) {
    return new NotificationDetailResponseData(
        new NotificationId(id),
        "00000000000000000000000001",
        NotificationType.ACCEPTED,
        NotificationState.RECEIVED,
        NOW,
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        false,
        Optional.of("question"),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.of(new QuestionId(3)));
  }

  private static byte[] searchBytes(String layout, boolean filled) {
    boolean question = layout.equals(QUESTION_SEARCH);
    byte[] bytes = new byte[question ? 384 : 64];
    Arrays.fill(bytes, (byte) 32);
    if (filled) {
      if (question) {
        put(bytes, 0, "é_%");
        put(bytes, 256, USERNAME);
        put(bytes, 320, "ANSWERED");
      } else {
        put(bytes, 0, "COMPLETED");
      }
      put(bytes, question ? 332 : 12, "20261001090000123");
      put(bytes, question ? 349 : 29, "20261001090001123");
    }
    put(bytes, question ? 366 : 46, "999999050");
    return bytes;
  }

  private static void put(byte[] data, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, data, offset, bytes.length);
  }

  private static WireMessage<FixedPayload> wire(String layout, byte[] data) {
    UUID id = new UUID(2015, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }
}
