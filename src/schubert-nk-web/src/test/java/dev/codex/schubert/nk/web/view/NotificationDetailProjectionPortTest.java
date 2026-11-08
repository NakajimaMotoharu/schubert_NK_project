package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationErrorCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SCR021/UI236/SS313/PT-WEB-NDETAIL001..008. Pure record projection, no MVC or store. */
final class NotificationDetailProjectionPortTest {
  private static final String READER = "reader";
  private static final String BODY = "質問é😀";
  private static final String ANSWER = "回答";
  private static final String RECEIPT = "0".repeat(26);
  private static final String STARTED_DISPLAY = "1970-01-01 09:00:01";
  private static final String ERROR_TEXT = "処理を完了できませんでした。";
  private static final String K_QUESTION = "question";
  private static final String K_ANSWER = "answer";
  private static final String K_AVAILABLE = "answerAvailable";
  private static final String K_HREF = "questionHref";
  private static final String K_LABEL = "stateLabel";
  private static final String K_STARTED = "startedAt";
  private static final String K_COMPLETED = "completedAt";
  private static final String K_ERROR = "errorAt";
  private static final String K_CANCELLED = "cancelledAt";
  private static final NotificationId ID = new NotificationId(12);
  private static final Instant AT = Instant.EPOCH;
  private static final List<Vector> VECTORS =
      List.of(
          new Vector(NotificationState.RECEIVED, "受付中", "", "", "", ""),
          new Vector(NotificationState.PROCESSING, "処理中", STARTED_DISPLAY, "", "", ""),
          new Vector(
              NotificationState.COMPLETED, "処理完了", STARTED_DISPLAY, "1970-01-01 09:00:02", "", ""),
          new Vector(
              NotificationState.ERROR, "エラー", STARTED_DISPLAY, "", "1970-01-01 09:00:03", ""),
          new Vector(NotificationState.CANCELLED, "取消済み", "", "", "", "1970-01-01 09:00:04"));

  private record Vector(
      NotificationState state,
      String label,
      String started,
      String completed,
      String error,
      String cancelled) {}

  private static SessionPrincipal actor(String name) {
    return new SessionPrincipal(name, UserRole.USER, AuthenticationContext.of("b".repeat(64)), AT);
  }

  private static NotificationDetailResponseData data(
      NotificationState state, boolean deleted, Optional<String> answer) {
    boolean started =
        List.of(NotificationState.PROCESSING, NotificationState.COMPLETED, NotificationState.ERROR)
            .contains(state);
    return new NotificationDetailResponseData(
        ID,
        RECEIPT,
        state == NotificationState.COMPLETED
            ? NotificationType.COMPLETED
            : state == NotificationState.ERROR ? NotificationType.ERROR : NotificationType.ACCEPTED,
        state,
        AT,
        started ? Optional.of(AT.plusSeconds(1)) : Optional.empty(),
        state == NotificationState.COMPLETED ? Optional.of(AT.plusSeconds(2)) : Optional.empty(),
        state == NotificationState.ERROR ? Optional.of(AT.plusSeconds(3)) : Optional.empty(),
        state == NotificationState.CANCELLED ? Optional.of(AT.plusSeconds(4)) : Optional.empty(),
        deleted,
        deleted ? Optional.empty() : Optional.of(BODY),
        !deleted && state == NotificationState.COMPLETED ? answer : Optional.empty(),
        state == NotificationState.ERROR
            ? Optional.of(NotificationErrorCode.SYSTEM_UNAVAILABLE)
            : Optional.empty(),
        state == NotificationState.ERROR ? Optional.of(ERROR_TEXT) : Optional.empty(),
        deleted ? Optional.empty() : Optional.of(new QuestionId(99)));
  }

  private static NotificationDetailViewModel page(NotificationState state, boolean deleted) {
    return NotificationDetailViewModel.from(
        actor(READER), ID, data(state, deleted, Optional.of(ANSWER)));
  }

  @Test
  void completedHasExactFields() {
    assertEquals(
        Map.ofEntries(
            Map.entry("id", 12L),
            Map.entry("receiptId", RECEIPT),
            Map.entry("state", "COMPLETED"),
            Map.entry(K_LABEL, "処理完了"),
            Map.entry("submittedAt", "1970-01-01 09:00:00"),
            Map.entry(K_STARTED, STARTED_DISPLAY),
            Map.entry(K_COMPLETED, "1970-01-01 09:00:02"),
            Map.entry(K_ERROR, ""),
            Map.entry(K_CANCELLED, ""),
            Map.entry("deleted", false),
            Map.entry(K_QUESTION, BODY),
            Map.entry(K_AVAILABLE, true),
            Map.entry(K_ANSWER, ANSWER),
            Map.entry("errorCode", ""),
            Map.entry("userFacingError", ""),
            Map.entry(K_HREF, "/questions/99")),
        page(NotificationState.COMPLETED, false).getValues());
  }

  @Test
  void allStatesHaveLiteralLabelsAndTimes() {
    for (Vector vector : VECTORS) {
      var values = page(vector.state(), false).getValues();
      assertEquals(vector.label(), values.get(K_LABEL));
      assertEquals(vector.started(), values.get(K_STARTED));
      assertEquals(vector.completed(), values.get(K_COMPLETED));
      assertEquals(vector.error(), values.get(K_ERROR));
      assertEquals(vector.cancelled(), values.get(K_CANCELLED));
    }
    var error = page(NotificationState.ERROR, false).getValues();
    assertEquals("SYSTEM_UNAVAIL", error.get("errorCode"));
    assertEquals(ERROR_TEXT, error.get("userFacingError"));
    assertEquals("", error.get(K_HREF));
    assertEquals(false, error.get(K_AVAILABLE));
  }

  @Test
  void deletedQuestionsRetireAnswerAndLink() {
    for (Vector vector : VECTORS) {
      var values = page(vector.state(), true).getValues();
      assertEquals(true, values.get("deleted"));
      assertEquals("", values.get(K_QUESTION));
      assertEquals("", values.get(K_ANSWER));
      assertEquals("", values.get(K_HREF));
      assertEquals(false, values.get(K_AVAILABLE));
      assertEquals(vector.label(), values.get(K_LABEL));
    }
  }

  @Test
  void completedMayHaveEmptyAnswer() {
    for (Optional<String> value : List.of(Optional.<String>empty(), Optional.of(""))) {
      var page =
          NotificationDetailViewModel.from(
              actor(READER), ID, data(NotificationState.COMPLETED, false, value));
      assertEquals("", page.getValues().get(K_ANSWER));
      assertEquals(true, page.getValues().get(K_AVAILABLE));
      assertEquals("/questions/99", page.getValues().get(K_HREF));
    }
  }

  @Test
  void targetNullAndSemanticMismatchReject() {
    var actor = actor(READER);
    var good = data(NotificationState.RECEIVED, false, Optional.empty());
    assertThrows(
        NullPointerException.class, () -> NotificationDetailViewModel.from(null, ID, good));
    assertThrows(
        NullPointerException.class, () -> NotificationDetailViewModel.from(actor, null, good));
    assertThrows(
        NullPointerException.class, () -> NotificationDetailViewModel.from(actor, ID, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationDetailViewModel.from(actor, new NotificationId(13), good));
    var badType =
        new NotificationDetailResponseData(
            ID,
            RECEIPT,
            NotificationType.ERROR,
            NotificationState.RECEIVED,
            AT,
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            false,
            Optional.of(BODY),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.of(new QuestionId(99)));
    assertThrows(
        LayoutValidationException.class,
        () -> NotificationDetailViewModel.from(actor, ID, badType));
    var badDeleted =
        new NotificationDetailResponseData(
            ID,
            RECEIPT,
            NotificationType.ACCEPTED,
            NotificationState.RECEIVED,
            AT,
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            true,
            Optional.of(BODY),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.of(new QuestionId(99)));
    assertThrows(
        LayoutValidationException.class,
        () -> NotificationDetailViewModel.from(actor, ID, badDeleted));
  }

  @Test
  void immutableRedactedProjection() {
    var page = page(NotificationState.COMPLETED, false);
    assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
    assertEquals("NotificationDetailViewModel[REDACTED]", page.toString());
    assertEquals("schubert NK", page.getTopBar().getBrand());
    assertEquals(READER, page.getTopBar().getUsername());
    assertEquals("USER", page.getTopBar().getRole());
    assertFalse(page.getValues().containsKey("authenticationContext"));
  }

  @Test
  void unicodeAndMarkupStayText() {
    var text = "<strong>é😀</strong>";
    var good =
        new NotificationDetailResponseData(
            ID,
            RECEIPT,
            NotificationType.COMPLETED,
            NotificationState.COMPLETED,
            AT,
            Optional.of(AT.plusSeconds(1)),
            Optional.of(AT.plusSeconds(2)),
            Optional.empty(),
            Optional.empty(),
            false,
            Optional.of(text),
            Optional.of(text),
            Optional.empty(),
            Optional.empty(),
            Optional.of(new QuestionId(99)));
    var values = NotificationDetailViewModel.from(actor(READER), ID, good).getValues();
    assertEquals("<strong>é😀</strong>", values.get(K_QUESTION));
    assertEquals("<strong>é😀</strong>", values.get(K_ANSWER));
  }

  @Test
  void parallelProjectionKeepsActorsSeparate() throws Exception {
    var workers = Executors.newFixedThreadPool(2);
    try {
      var pending = new ArrayList<Future<NotificationDetailViewModel>>();
      for (int i = 0; i < 8; i++) {
        String name = READER + i;
        Vector vector = VECTORS.get(i % VECTORS.size());
        pending.add(
            workers.submit(
                () ->
                    NotificationDetailViewModel.from(
                        actor(name), ID, data(vector.state(), false, Optional.of(ANSWER)))));
      }
      for (int i = 0; i < 8; i++) {
        var page = pending.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(READER + i, page.getTopBar().getUsername());
        assertEquals(VECTORS.get(i % VECTORS.size()).label(), page.getValues().get(K_LABEL));
      }
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
