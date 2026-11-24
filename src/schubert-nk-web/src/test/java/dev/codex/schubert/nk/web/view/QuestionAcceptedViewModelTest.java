package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.receipt.ReceiptReference;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

/** SCR019 and QA048. Uses only a fixed in-memory response, principal and technical reference. */
class QuestionAcceptedViewModelTest {
  private static final String RECEIPT = "01K00000000000000000000000";
  private static final String OTHER_RECEIPT = "01K00000000000000000000001";
  private static final String OWNER = "fixture-reader";
  private static final String QUESTION_FIELD = "question";
  private static final long QUESTION = 19L;
  private static final Instant REFERENCE_AT = Instant.parse("2026-11-24T15:04:05.123Z");
  private static final Instant RESPONSE_AT = Instant.parse("2026-11-24T15:04:05.123Z");
  private static final ReceiptReference REFERENCE =
      new ReceiptReference(RECEIPT, QUESTION, REFERENCE_AT);
  private static final SessionPrincipal ACTOR =
      new SessionPrincipal(
          OWNER, UserRole.USER, AuthenticationContext.of("0".repeat(64)), REFERENCE_AT);

  /** PT-WEB-SCR019-VM001. */
  @Test
  void accepted001RendersOnlyTheApprovedFieldsAndJstTime() {
    var model = model(fresh(QUESTION, RECEIPT, OWNER, "見本の質問", RESPONSE_AT));
    assertEquals(
        Map.of("receiptId", RECEIPT, "submittedAt", "2026-11-25 00:04:05", QUESTION_FIELD, "見本の質問"),
        model.getValues());
    assertEquals("schubert NK", model.getTopBar().getBrand());
    assertEquals(OWNER, model.getTopBar().getUsername());
    assertEquals("USER", model.getTopBar().getRole());
    assertEquals("QuestionAcceptedViewModel[REDACTED]", model.toString());
    assertThrows(UnsupportedOperationException.class, () -> model.getValues().put("extra", "text"));
  }

  /** PT-WEB-SCR019-VM002. */
  @Test
  void accepted002KeepsTheWhole200thCodePointAndDropsLaterCharacters() {
    String below = "a".repeat(199);
    String exactly = below + "𠮷";
    assertEquals(
        below,
        model(fresh(QUESTION, RECEIPT, OWNER, below, RESPONSE_AT)).getValues().get(QUESTION_FIELD));
    assertEquals(
        exactly,
        model(fresh(QUESTION, RECEIPT, OWNER, exactly, RESPONSE_AT))
            .getValues()
            .get(QUESTION_FIELD));
    var longResponse = fresh(QUESTION, RECEIPT, OWNER, exactly + "後", RESPONSE_AT);
    assertEquals(exactly, model(longResponse).getValues().get(QUESTION_FIELD));
  }

  /** PT-WEB-SCR019-VM003. */
  @Test
  void accepted003RejectsEachFixedReferenceMismatchIndependently() {
    var wrongTime = Instant.parse("2026-11-24T15:04:05.124Z");
    assertMismatch(fresh(20, RECEIPT, OWNER, "質問", RESPONSE_AT));
    assertMismatch(fresh(QUESTION, OTHER_RECEIPT, OWNER, "質問", RESPONSE_AT));
    assertMismatch(fresh(QUESTION, RECEIPT, OWNER, "質問", wrongTime));
    assertMismatch(fresh(QUESTION, RECEIPT, "other-reader", "質問", RESPONSE_AT));
  }

  /** PT-WEB-SCR019-VM004. */
  @Test
  void accepted004RejectsMissingInputAndEmptyQuestionSeparately() {
    var data = fresh(QUESTION, RECEIPT, OWNER, "質問", RESPONSE_AT);
    assertThrows(
        NullPointerException.class, () -> QuestionAcceptedViewModel.from(null, REFERENCE, data));
    assertThrows(
        NullPointerException.class, () -> QuestionAcceptedViewModel.from(ACTOR, null, data));
    assertThrows(
        NullPointerException.class, () -> QuestionAcceptedViewModel.from(ACTOR, REFERENCE, null));
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> model(fresh(QUESTION, RECEIPT, OWNER, "", RESPONSE_AT)));
    assertEquals("question projection body is absent", failure.getMessage());
  }

  /** PT-WEB-SCR019-VM005. */
  @Test
  void accepted005DoesNotProjectAnInconsistentAnswerState() {
    var invalid =
        new QuestionDetailResponseData(
            new QuestionId(QUESTION),
            RECEIPT,
            OWNER,
            AnswerState.UNANSWERED,
            "質問",
            Optional.empty(),
            RESPONSE_AT,
            Optional.of(RESPONSE_AT));
    assertThrows(LayoutValidationException.class, () -> model(invalid));
  }

  /** PT-WEB-SCR019-VM006. */
  @Test
  void accepted006RejectsFinerPrecisionThanTheResponseWireFormat() {
    var invalidTime = Instant.parse("2026-11-24T15:04:05.123456Z");
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> model(fresh(QUESTION, RECEIPT, OWNER, "質問", invalidTime)));
    assertEquals("wire timestamp requires millisecond precision", failure.getMessage());
  }

  private static void assertMismatch(QuestionDetailResponseData data) {
    var failure = assertThrows(IllegalArgumentException.class, () -> model(data));
    assertEquals("invalid acceptance projection", failure.getMessage());
  }

  private static QuestionAcceptedViewModel model(QuestionDetailResponseData data) {
    return QuestionAcceptedViewModel.from(ACTOR, REFERENCE, data);
  }

  private static QuestionDetailResponseData fresh(
      long question, String receipt, String owner, String body, Instant time) {
    return new QuestionDetailResponseData(
        new QuestionId(question),
        receipt,
        owner,
        AnswerState.UNANSWERED,
        body,
        Optional.empty(),
        time,
        Optional.empty());
  }
}
