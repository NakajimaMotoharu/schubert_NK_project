package dev.codex.schubert.nk.web.form;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;

/**
 * PT-WEB-QFORM001 through QFORM009. The form is evaluated without HTTP, a broker, or a database.
 */
final class QuestionSearchFormTest {
  private static final String KEYWORD = "keyword";
  private static final String USERNAME = "username";
  private static final String STATE = "state";
  private static final String PAGE = "page";
  private static final String FROM = "from";
  private static final String TO = "to";

  @Test
  void qform001MissingAndEmptyFiltersUseTheDefaultPage() {
    for (var parameters : List.of(Map.<String, List<String>>of(), Map.of(KEYWORD, List.of("")))) {
      var form = QuestionSearchForm.bind(parameters, UserRole.USER);
      assertTrue(form.isValid());
      assertFalse(form.isAdmin());
      assertEquals(1, form.getPage());
      assertEquals(Map.of(), form.getIssues());
      var request = form.toRequest();
      assertEquals(Optional.empty(), request.keyword());
      assertEquals(Optional.empty(), request.username());
      assertEquals(Optional.empty(), request.answerState());
      assertEquals(Optional.empty(), request.submittedFrom());
      assertEquals(Optional.empty(), request.submittedTo());
      assertEquals(1, request.page());
      assertEquals(50, request.pageSize());
    }
  }

  @Test
  void qform002Utf8LimitsApplyAfterNfcWithoutTruncation() {
    String decomposed = "e\u0301".repeat(128);
    String composed = "é".repeat(128);
    String username = "山".repeat(21) + "a";
    var boundary =
        QuestionSearchForm.bind(
            Map.of(KEYWORD, List.of(decomposed), USERNAME, List.of(username)), UserRole.ADMIN);
    assertTrue(boundary.isAdmin());
    assertTrue(boundary.isValid());
    assertEquals(Optional.of(composed), boundary.toRequest().keyword());
    assertEquals(Optional.of(username), boundary.toRequest().username());
    invalid(
        Map.of(KEYWORD, List.of(decomposed + "é"), USERNAME, List.of(username + "b")),
        UserRole.ADMIN,
        Set.of(KEYWORD, USERNAME));
  }

  @Test
  void qform003RejectedParametersStayOutsideTheTypedRequest() {
    invalid(Map.of(USERNAME, List.of("reader")), UserRole.USER, Set.of(USERNAME));
    invalid(Map.of("unregistered", List.of("value")), UserRole.ADMIN, Set.of("form"));
    invalid(Map.of(KEYWORD, List.of()), UserRole.USER, Set.of(KEYWORD));
    invalid(Map.of(KEYWORD, List.of("alpha", "beta")), UserRole.USER, Set.of(KEYWORD));
  }

  @Test
  void qform004OnlyTheThreeDocumentedStatesAreMapped() {
    Map<String, AnswerState> states =
        Map.of(
            "ANSWERED",
            AnswerState.ANSWERED,
            "UNANSWERED",
            AnswerState.UNANSWERED,
            "ERROR",
            AnswerState.ERROR);
    states.forEach(
        (label, expected) ->
            assertEquals(
                Optional.of(expected),
                QuestionSearchForm.bind(Map.of(STATE, List.of(label)), UserRole.USER)
                    .toRequest()
                    .answerState()));
    invalid(Map.of(STATE, List.of("UNKNOWN")), UserRole.USER, Set.of(STATE));
  }

  @Test
  void qform005ThePageFitsTheSixDecimalPlacesOfTheWireLayout() {
    var last = QuestionSearchForm.bind(Map.of(PAGE, List.of("999999")), UserRole.USER);
    assertEquals(999_999, last.getPage());
    assertEquals(999_999, last.toRequest().page());
    for (String page : List.of("1000000", "2147483648", "+1", "1.0", "1e1", "１")) {
      invalid(Map.of(PAGE, List.of(page)), UserRole.USER, Set.of(PAGE));
    }
  }

  @Test
  void qform006LiteralJstBoundariesAndTheLeapYearInterval() {
    var range =
        QuestionSearchForm.bind(
                Map.of(FROM, List.of("2024-01-01"), TO, List.of("2024-12-31")), UserRole.USER)
            .toRequest();
    assertEquals(Optional.of(Instant.parse("2023-12-31T15:00:00Z")), range.submittedFrom());
    assertEquals(Optional.of(Instant.parse("2024-12-31T14:59:59.999Z")), range.submittedTo());
    var fromOnly =
        QuestionSearchForm.bind(Map.of(FROM, List.of("2024-02-29")), UserRole.USER).toRequest();
    assertEquals(Optional.of(Instant.parse("2024-02-28T15:00:00Z")), fromOnly.submittedFrom());
    assertEquals(Optional.empty(), fromOnly.submittedTo());
    var toOnly =
        QuestionSearchForm.bind(Map.of(TO, List.of("2024-02-29")), UserRole.USER).toRequest();
    assertEquals(Optional.empty(), toOnly.submittedFrom());
    assertEquals(Optional.of(Instant.parse("2024-02-29T14:59:59.999Z")), toOnly.submittedTo());
    invalid(
        Map.of(FROM, List.of("2024-01-01"), TO, List.of("2025-01-01")), UserRole.USER, Set.of(TO));
    invalid(
        Map.of(FROM, List.of("2024-02-02"), TO, List.of("2024-02-01")), UserRole.USER, Set.of(TO));
  }

  @Test
  void qform007DatesRequireOneStrictCalendarDay() {
    for (String date : List.of("2023-02-29", "0000-01-01", "2024-2-9", "2024-13-01")) {
      invalid(Map.of(FROM, List.of(date)), UserRole.USER, Set.of(FROM));
      invalid(Map.of(TO, List.of(date)), UserRole.USER, Set.of(TO));
    }
    invalid(Map.of(FROM, List.of("2024-02-28", "2024-02-29")), UserRole.USER, Set.of(FROM));
  }

  @Test
  void qform008RejectsControlAndUnpairedSurrogatesButAcceptsSupplementaryText() {
    for (String invalid :
        List.of("\r", "\n", "\t", "\0", String.valueOf(Character.MIN_HIGH_SURROGATE))) {
      invalid(Map.of(KEYWORD, List.of("text" + invalid)), UserRole.USER, Set.of(KEYWORD));
    }
    String supplementary = "字😀";
    var form = QuestionSearchForm.bind(Map.of(KEYWORD, List.of(supplementary)), UserRole.USER);
    assertEquals(Optional.of(supplementary), form.toRequest().keyword());
  }

  @Test
  void qform009SnapshotAndJavaNullContractsKeepInputBoundariesExplicit() {
    var original = new ArrayList<>(List.of("fixture-query"));
    Map<String, List<String>> parameters = new HashMap<>();
    parameters.put(KEYWORD, original);
    var form = QuestionSearchForm.bind(parameters, UserRole.USER);
    original.set(0, "changed");
    parameters.clear();
    assertEquals(Optional.of("fixture-query"), form.toRequest().keyword());
    assertThrows(
        UnsupportedOperationException.class, () -> form.getValues().put(KEYWORD, "changed"));
    assertThrows(UnsupportedOperationException.class, () -> form.getIssues().put(TO, "changed"));
    assertFalse(form.toString().contains("fixture-query"));
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(null, UserRole.USER));
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(Map.of(), null));
    parameters.put(null, List.of("value"));
    assertThrows(
        NullPointerException.class, () -> QuestionSearchForm.bind(parameters, UserRole.USER));
    parameters.clear();
    parameters.put(KEYWORD, null);
    assertThrows(
        NullPointerException.class, () -> QuestionSearchForm.bind(parameters, UserRole.USER));
    var nullElement = new ArrayList<String>();
    nullElement.add(null);
    parameters.put(KEYWORD, nullElement);
    assertThrows(
        NullPointerException.class, () -> QuestionSearchForm.bind(parameters, UserRole.USER));
  }

  private static void invalid(
      Map<String, List<String>> parameters, UserRole role, Set<String> expectedKeys) {
    var form = QuestionSearchForm.bind(parameters, role);
    assertFalse(form.isValid());
    assertEquals(expectedKeys, form.getIssues().keySet());
    assertThrows(IllegalArgumentException.class, form::toRequest);
  }
}
