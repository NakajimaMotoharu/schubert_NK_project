package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
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

/** SCR023/UI236/SS313/PT-WEB-QDETAIL001..008. Pure projection; no session store or MVC. */
final class QuestionDetailProjectionPortTest {
  private static final String READER = "reader";
  private static final String OTHER = "other";
  private static final String BODY = "質問本文";
  private static final String ANSWER = "answer";
  private static final String ANSWER_AVAILABLE = "answerAvailable";
  private static final String RECEIPT = "0".repeat(26);
  private static final QuestionId ID = new QuestionId(12);
  private static final Instant SUBMITTED = Instant.EPOCH;
  private static final Instant ANSWERED = Instant.parse("1970-01-01T00:01:00Z");

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(name, role, AuthenticationContext.of("a".repeat(64)), SUBMITTED);
  }

  private static QuestionDetailResponseData data(
      String owner, AnswerState state, String body, Optional<String> answer) {
    return new QuestionDetailResponseData(
        ID,
        RECEIPT,
        owner,
        state,
        body,
        answer,
        SUBMITTED,
        state == AnswerState.ANSWERED ? Optional.of(ANSWERED) : Optional.empty());
  }

  private static QuestionDetailViewModel model(AnswerState state) {
    return QuestionDetailViewModel.from(
        actor(READER, UserRole.USER),
        ID,
        data(
            READER,
            state,
            BODY,
            state == AnswerState.ANSWERED ? Optional.of("回答") : Optional.empty()));
  }

  @Test
  void answeredProjectionHasExactFields() {
    var page = model(AnswerState.ANSWERED);
    assertEquals(
        Map.ofEntries(
            Map.entry("id", 12L),
            Map.entry("receiptId", RECEIPT),
            Map.entry("admin", false),
            Map.entry("username", READER),
            Map.entry("state", "ANSWERED"),
            Map.entry("stateLabel", "回答済み"),
            Map.entry("submittedAt", "1970-01-01 09:00:00"),
            Map.entry("answeredAt", "1970-01-01 09:01:00"),
            Map.entry("question", BODY),
            Map.entry("summary", BODY),
            Map.entry(ANSWER, "回答"),
            Map.entry(ANSWER_AVAILABLE, true)),
        page.getValues());
    assertEquals("schubert NK", page.getTopBar().getBrand());
    assertEquals(READER, page.getTopBar().getUsername());
    assertEquals("USER", page.getTopBar().getRole());
  }

  @Test
  void unansweredAndErrorHaveNoAnswer() {
    for (AnswerState state : List.of(AnswerState.UNANSWERED, AnswerState.ERROR)) {
      var values = model(state).getValues();
      assertEquals(state == AnswerState.UNANSWERED ? "未回答" : "エラー", values.get("stateLabel"));
      assertEquals("", values.get(ANSWER));
      assertEquals("", values.get("answeredAt"));
      assertEquals(false, values.get(ANSWER_AVAILABLE));
    }
    var blank =
        QuestionDetailViewModel.from(
            actor(READER, UserRole.USER),
            ID,
            data(READER, AnswerState.ANSWERED, BODY, Optional.empty()));
    assertEquals("", blank.getValues().get(ANSWER));
    assertEquals(true, blank.getValues().get(ANSWER_AVAILABLE));
  }

  @Test
  void adminMayViewAnotherOwner() {
    var page =
        QuestionDetailViewModel.from(
            actor(READER, UserRole.ADMIN),
            ID,
            data(OTHER, AnswerState.UNANSWERED, BODY, Optional.empty()));
    assertEquals(OTHER, page.getValues().get("username"));
    assertEquals(true, page.getValues().get("admin"));
    assertEquals(READER, page.getTopBar().getUsername());
    assertEquals("ADMIN", page.getTopBar().getRole());
  }

  @Test
  void summaryUsesOneHundredCodePoints() {
    String[][] vectors = {
      {"😀".repeat(98) + "é", "😀".repeat(98) + "é"},
      {"😀".repeat(99) + "é", "😀".repeat(99) + "é"},
      {"😀".repeat(100) + "é", "😀".repeat(100)}
    };
    for (String[] vector : vectors) {
      var page =
          QuestionDetailViewModel.from(
              actor(READER, UserRole.USER),
              ID,
              data(READER, AnswerState.UNANSWERED, vector[0], Optional.empty()));
      assertEquals(vector[0], page.getValues().get("question"));
      assertEquals(vector[1], page.getValues().get("summary"));
    }
  }

  @Test
  void targetOwnerAndBodyReject() {
    var user = actor(READER, UserRole.USER);
    var good = data(READER, AnswerState.UNANSWERED, BODY, Optional.empty());
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionDetailViewModel.from(user, new QuestionId(13), good));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionDetailViewModel.from(
                user, ID, data(OTHER, AnswerState.UNANSWERED, BODY, Optional.empty())));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionDetailViewModel.from(
                user, ID, data(READER, AnswerState.UNANSWERED, "", Optional.empty())));
    assertThrows(
        LayoutValidationException.class,
        () ->
            QuestionDetailViewModel.from(
                user, ID, data(READER, AnswerState.UNANSWERED, BODY, Optional.of("unexpected"))));
    var invalidTime =
        new QuestionDetailResponseData(
            ID,
            RECEIPT,
            READER,
            AnswerState.ANSWERED,
            BODY,
            Optional.of("回答"),
            SUBMITTED,
            Optional.empty());
    assertThrows(
        LayoutValidationException.class, () -> QuestionDetailViewModel.from(user, ID, invalidTime));
  }

  @Test
  void nullBoundaryRejects() {
    var user = actor(READER, UserRole.USER);
    var good = data(READER, AnswerState.UNANSWERED, BODY, Optional.empty());
    assertThrows(NullPointerException.class, () -> QuestionDetailViewModel.from(null, ID, good));
    assertThrows(NullPointerException.class, () -> QuestionDetailViewModel.from(user, null, good));
    assertThrows(NullPointerException.class, () -> QuestionDetailViewModel.from(user, ID, null));
  }

  @Test
  void immutableRedactedProjection() {
    var page = model(AnswerState.ANSWERED);
    assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
    assertEquals("QuestionDetailViewModel[REDACTED]", page.toString());
    assertEquals("TopBarViewModel[REDACTED]", page.getTopBar().toString());
    assertFalse(page.getValues().containsKey("authenticationContext"));
    assertFalse(page.getValues().containsKey("principal"));
  }

  @Test
  void parallelProjectionDoesNotLeakOwners() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var pending = new ArrayList<Future<QuestionDetailViewModel>>();
      for (int i = 0; i < 8; i++) {
        String owner = READER + i;
        pending.add(
            workers.submit(
                () ->
                    QuestionDetailViewModel.from(
                        actor(owner, UserRole.USER),
                        ID,
                        data(owner, AnswerState.UNANSWERED, owner, Optional.empty()))));
      }
      for (int i = 0; i < 8; i++) {
        var page = pending.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(READER + i, page.getValues().get("username"));
        assertEquals(READER + i, page.getValues().get("summary"));
        assertEquals(READER + i, page.getTopBar().getUsername());
        assertEquals("1970-01-01 09:00:00", page.getValues().get("submittedAt"));
        assertTrue(page.getValues().get(ANSWER_AVAILABLE).equals(false));
      }
    }
  }
}
