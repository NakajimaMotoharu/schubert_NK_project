package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** SCR022/UI224236/SS313/PT-WEB-QLIST001..016: pure display; not HTTP/DB acceptance. */
final class QuestionListProjectionPortTest {
  private static final String READER = "reader";
  private static final String ADMIN = "admin";
  private static final String BODY = "é &+ 質問概要";
  private static final String RECEIPT = "0".repeat(26);
  private static final String K_ID = "id";
  private static final String K_SUMMARY = "summary";
  private static final String K_USERNAME = "username";
  private static final String K_KEYWORD = "keyword";
  private static final String K_STATE = "state";
  private static final String K_PAGE = "page";
  private static final String K_FROM = "from";
  private static final String K_TO = "to";
  private static final String EMPTY_QUERY = "/questions?keyword=&state=&from=&to=&page=";
  private static final String FILTERED_QUERY =
      "/questions?keyword=%C3%A9%20%26%2B&state=ANSWERED&from=2026-11-01&to=2026-11-02";
  private static final Instant AT = Instant.EPOCH;
  private static final Instant FILTER_AT = Instant.parse("2026-11-01T00:00:00Z");
  private static final PagedResponseData EMPTY = new PagedResponseData(1, 50, 0, 1, 0, 0);
  private static final PagedResponseData ONE = new PagedResponseData(1, 50, 1, 1, 1, 1);
  private static final PagedResponseData TWO = new PagedResponseData(1, 50, 2, 1, 1, 2);

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(name, role, AuthenticationContext.of("c".repeat(64)), AT);
  }

  private static SessionPrincipal displayReader() {
    return actor(READER, UserRole.USER);
  }

  private static QuestionSearchForm form(int page, UserRole role) {
    return QuestionSearchForm.bind(Map.of(K_PAGE, List.of(Integer.toString(page))), role);
  }

  private static QuestionSummaryRecord row(
      long id, String username, AnswerState state, Instant submitted, String summary) {
    return new QuestionSummaryRecord(
        new QuestionId(id),
        RECEIPT,
        username,
        summary,
        state,
        submitted,
        state == AnswerState.ANSWERED ? Optional.of(submitted.plusSeconds(1)) : Optional.empty());
  }

  private static QuestionSummaryRecord row(long id) {
    return row(id, READER, AnswerState.UNANSWERED, AT, BODY);
  }

  private static QuestionListViewModel single(QuestionSummaryRecord row) {
    return QuestionListViewModel.success(
        displayReader(), form(1, UserRole.USER), ONE, List.of(row));
  }

  private static List<QuestionSummaryRecord> fifty(boolean filtered) {
    var rows = new ArrayList<QuestionSummaryRecord>();
    for (int i = 0; i < 50; i++)
      rows.add(
          filtered ? row(200 - i, READER, AnswerState.ANSWERED, FILTER_AT, BODY) : row(200 - i));
    return rows;
  }

  @Test
  void emptyReturnsPlainView() {
    var filters = form(1, UserRole.USER);
    var page = QuestionListViewModel.success(displayReader(), filters, EMPTY, List.of());
    assertSame(filters, page.getFilters());
    assertTrue(page.getPage().orElseThrow().isEmpty());
    assertEquals(List.of(), page.getRows());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    assertEquals(READER, page.getTopBar().getUsername());
    assertEquals("USER", page.getTopBar().getRole());
    assertEquals("schubert NK", page.getTopBar().getBrand());
    assertEquals("QuestionListViewModel[REDACTED]", page.toString());
  }

  @Test
  void allStatesHaveIndependentRows() {
    Map<AnswerState, String> labels =
        Map.of(
            AnswerState.UNANSWERED, "未回答", AnswerState.ANSWERED, "回答済み", AnswerState.ERROR, "エラー");
    for (var entry : labels.entrySet()) {
      var page = single(row(12, READER, entry.getKey(), AT, BODY));
      assertEquals(
          Map.ofEntries(
              Map.entry(K_ID, 12L),
              Map.entry("receiptId", RECEIPT),
              Map.entry(K_USERNAME, READER),
              Map.entry(K_SUMMARY, BODY),
              Map.entry(K_STATE, entry.getKey().name()),
              Map.entry("stateLabel", entry.getValue()),
              Map.entry("submittedAt", "1970-01-01 09:00:00"),
              Map.entry(
                  "answeredAt",
                  entry.getKey() == AnswerState.ANSWERED ? "1970-01-01 09:00:01" : ""),
              Map.entry("detailHref", "/questions/12"),
              Map.entry("deleteHref", "/questions/12#delete-confirm")),
          page.getRows().getFirst());
    }
  }

  @Test
  void userPagingLinksAndClamp() {
    var first =
        QuestionListViewModel.success(
            displayReader(),
            form(1, UserRole.USER),
            new PagedResponseData(1, 50, 51, 2, 1, 50),
            fifty(false));
    assertTrue(first.getPreviousHref().isEmpty());
    assertEquals(Optional.of(EMPTY_QUERY + "2"), first.getNextHref());
    var last =
        QuestionListViewModel.success(
            displayReader(),
            form(2, UserRole.USER),
            new PagedResponseData(2, 50, 51, 2, 51, 51),
            List.of(row(12)));
    assertEquals(Optional.of(EMPTY_QUERY + "1"), last.getPreviousHref());
    assertTrue(last.getNextHref().isEmpty());
    var clamped =
        QuestionListViewModel.success(
            displayReader(),
            form(999, UserRole.USER),
            new PagedResponseData(3, 50, 101, 3, 101, 101),
            List.of(row(12)));
    assertEquals(3, clamped.getPage().orElseThrow().getEffectivePage());
    assertEquals(Optional.of(EMPTY_QUERY + "2"), clamped.getPreviousHref());
    assertTrue(clamped.getNextHref().isEmpty());
  }

  @Test
  void adminAndUserFilteredLinksAreLiteral() {
    for (var role : List.of(UserRole.USER, UserRole.ADMIN)) {
      var values =
          new java.util.HashMap<String, List<String>>(
              Map.of(
                  K_PAGE,
                  List.of("2"),
                  K_KEYWORD,
                  List.of("e\u0301 &+"),
                  K_STATE,
                  List.of("ANSWERED"),
                  K_FROM,
                  List.of("2026-11-01"),
                  K_TO,
                  List.of("2026-11-02")));
      if (role == UserRole.ADMIN) values.put(K_USERNAME, List.of(READER));
      var filters = QuestionSearchForm.bind(values, role);
      assertTrue(filters.isValid());
      var page =
          QuestionListViewModel.success(
              actor(role == UserRole.ADMIN ? ADMIN : READER, role),
              filters,
              new PagedResponseData(2, 50, 101, 3, 51, 100),
              fifty(true));
      String prefix =
          FILTERED_QUERY + (role == UserRole.ADMIN ? "&username=reader" : "") + "&page=";
      assertEquals(Optional.of(prefix + "1"), page.getPreviousHref());
      assertEquals(Optional.of(prefix + "3"), page.getNextHref());
      assertEquals(50, page.getRows().size());
      assertTrue(
          page.getRows().stream()
              .allMatch(
                  value ->
                      value.get(K_USERNAME).equals(READER)
                          && value.get(K_STATE).equals("ANSWERED")
                          && value.get("submittedAt").equals("2026-11-01 09:00:00")
                          && value.get(K_SUMMARY).toString().contains("é &+")));
    }
  }

  @Test
  void invalidFormsStayUnpaginated() {
    var invalid = QuestionSearchForm.bind(Map.of(K_STATE, List.of("BAD")), UserRole.USER);
    assertFalse(invalid.isValid());
    var page = QuestionListViewModel.invalid(displayReader(), invalid);
    assertSame(invalid, page.getFilters());
    assertTrue(page.getPage().isEmpty());
    assertTrue(page.getRows().isEmpty());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.success(displayReader(), invalid, EMPTY, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.invalid(displayReader(), form(1, UserRole.USER)));
  }

  @Test
  void roleMismatchRejectsBothDirections() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(), form(1, UserRole.ADMIN), EMPTY, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                actor(ADMIN, UserRole.ADMIN), form(1, UserRole.USER), EMPTY, List.of()));
    var invalidAdmin = QuestionSearchForm.bind(Map.of(K_STATE, List.of("BAD")), UserRole.ADMIN);
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.invalid(displayReader(), invalidAdmin));
  }

  @Test
  void wrongEffectivePageRejects() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(),
                form(1, UserRole.USER),
                new PagedResponseData(2, 50, 51, 2, 51, 51),
                List.of(row(12))));
  }

  @Test
  void rowCountMismatchRejects() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(), form(1, UserRole.USER), TWO, List.of(row(12))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(), form(1, UserRole.USER), EMPTY, List.of(row(12))));
  }

  @Test
  void duplicateIdsReject() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(), form(1, UserRole.USER), TWO, List.of(row(12), row(12))));
  }

  @Test
  void ownerScopeAndSummaryLimitReject() {
    assertThrows(
        IllegalArgumentException.class,
        () -> single(row(12, ADMIN, AnswerState.UNANSWERED, AT, BODY)));
    assertThrows(
        IllegalArgumentException.class,
        () -> single(row(12, READER, AnswerState.UNANSWERED, AT, "😀".repeat(101))));
  }

  @Test
  void inconsistentAnswerTimestampRejects() {
    var missing =
        new QuestionSummaryRecord(
            new QuestionId(12), RECEIPT, READER, BODY, AnswerState.ANSWERED, AT, Optional.empty());
    var extra =
        new QuestionSummaryRecord(
            new QuestionId(12), RECEIPT, READER, BODY, AnswerState.UNANSWERED, AT, Optional.of(AT));
    assertThrows(IllegalArgumentException.class, () -> single(missing));
    assertThrows(IllegalArgumentException.class, () -> single(extra));
  }

  @Test
  void orderRulesAreIndependent() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(),
                form(1, UserRole.USER),
                TWO,
                List.of(row(2), row(1, READER, AnswerState.UNANSWERED, AT.plusSeconds(1), BODY))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(), form(1, UserRole.USER), TWO, List.of(row(1), row(2))));
    var tied =
        QuestionListViewModel.success(
            displayReader(), form(1, UserRole.USER), TWO, List.of(row(2), row(1)));
    assertEquals(List.of(2L, 1L), tied.getRows().stream().map(x -> x.get(K_ID)).toList());
    var descending =
        QuestionListViewModel.success(
            displayReader(),
            form(1, UserRole.USER),
            TWO,
            List.of(row(1, READER, AnswerState.UNANSWERED, AT.plusSeconds(1), BODY), row(2)));
    assertEquals(List.of(1L, 2L), descending.getRows().stream().map(x -> x.get(K_ID)).toList());
  }

  @Test
  void nullBoundariesReject() {
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(null, form(1, UserRole.USER), EMPTY, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(displayReader(), null, EMPTY, List.of()));
    assertThrows(
        NullPointerException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(), form(1, UserRole.USER), null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(displayReader(), form(1, UserRole.USER), EMPTY, null));
    assertThrows(
        NullPointerException.class,
        () ->
            QuestionListViewModel.success(
                displayReader(),
                form(1, UserRole.USER),
                ONE,
                Arrays.asList((QuestionSummaryRecord) null)));
    assertThrows(
        NullPointerException.class, () -> QuestionListViewModel.invalid(displayReader(), null));
    var invalid = QuestionSearchForm.bind(Map.of(K_STATE, List.of("BAD")), UserRole.USER);
    assertThrows(NullPointerException.class, () -> QuestionListViewModel.invalid(null, invalid));
  }

  @Test
  void outputSnapshotIsImmutable() {
    var supplied = new ArrayList<>(List.of(row(12)));
    var page =
        QuestionListViewModel.success(displayReader(), form(1, UserRole.USER), ONE, supplied);
    supplied.clear();
    supplied.add(row(99));
    assertEquals(1, page.getRows().size());
    assertEquals(12L, page.getRows().getFirst().get(K_ID));
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().clear());
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().getFirst().clear());
  }

  @Test
  void unicodeBoundaryAndAdminCrossOwnerAreValid() {
    for (String summary : List.of("😀".repeat(99), "😀".repeat(100))) {
      assertEquals(
          summary,
          single(row(12, READER, AnswerState.UNANSWERED, AT, summary))
              .getRows()
              .getFirst()
              .get(K_SUMMARY));
    }
    var page =
        QuestionListViewModel.success(
            actor(ADMIN, UserRole.ADMIN), form(1, UserRole.ADMIN), ONE, List.of(row(12)));
    assertEquals(READER, page.getRows().getFirst().get(K_USERNAME));
    assertEquals(ADMIN, page.getTopBar().getUsername());
  }

  @Test
  void parallelViewsKeepActorsSeparate() throws Exception {
    var workers = Executors.newFixedThreadPool(2);
    try {
      var pending = new ArrayList<Future<QuestionListViewModel>>();
      for (int i = 0; i < 8; i++) {
        String name = READER + i;
        pending.add(
            workers.submit(
                () ->
                    QuestionListViewModel.success(
                        actor(name, UserRole.USER),
                        form(1, UserRole.USER),
                        ONE,
                        List.of(row(12, name, AnswerState.UNANSWERED, AT, BODY)))));
      }
      for (int i = 0; i < 8; i++) {
        var page = pending.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(READER + i, page.getTopBar().getUsername());
        assertEquals(READER + i, page.getRows().getFirst().get(K_USERNAME));
        assertTrue(page.getNextHref().isEmpty());
      }
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
