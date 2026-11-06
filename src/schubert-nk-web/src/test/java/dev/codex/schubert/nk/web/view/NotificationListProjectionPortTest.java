package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
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

/** SCR020/UI236/SS313/PT-WEB-NLIST001..014: pure display, not HTTP/owner/DB acceptance. */
final class NotificationListProjectionPortTest {
  private static final String READER = "reader";
  private static final String BODY = "質問概要";
  private static final String DELETED = "削除済み";
  private static final String RECEIPT = "0".repeat(26);
  private static final String K_ID = "id";
  private static final String K_SUMMARY = "summary";
  private static final String K_TYPE = "type";
  private static final String K_FROM = "from";
  private static final String K_TO = "to";
  private static final String K_PAGE = "page";
  private static final String EMPTY_QUERY = "/notifications?type=&from=&to=&page=";
  private static final String FILTERED_QUERY =
      "/notifications?type=ERROR&from=2026-11-01&to=2026-11-02&page=";
  private static final Instant AT = Instant.EPOCH;
  private static final PagedResponseData EMPTY = new PagedResponseData(1, 50, 0, 1, 0, 0);
  private static final PagedResponseData ONE = new PagedResponseData(1, 50, 1, 1, 1, 1);
  private static final PagedResponseData TWO = new PagedResponseData(1, 50, 2, 1, 1, 2);

  private static SessionPrincipal actor(String name) {
    return new SessionPrincipal(name, UserRole.USER, AuthenticationContext.of("c".repeat(64)), AT);
  }

  private static NotificationSearchForm form(int page) {
    return NotificationSearchForm.bind(Map.of(K_PAGE, List.of(Integer.toString(page))));
  }

  private static NotificationRecord row(
      long id, NotificationState state, Instant updated, String summary, boolean deleted) {
    NotificationType type =
        switch (state) {
          case COMPLETED -> NotificationType.COMPLETED;
          case ERROR -> NotificationType.ERROR;
          default -> NotificationType.ACCEPTED;
        };
    return new NotificationRecord(
        new NotificationId(id), RECEIPT, type, state, AT, updated, summary, deleted);
  }

  private static NotificationRecord row(long id) {
    return row(id, NotificationState.RECEIVED, AT.plusSeconds(1), BODY, false);
  }

  private static NotificationListViewModel single(NotificationRecord row) {
    return NotificationListViewModel.success(actor(READER), form(1), ONE, List.of(row));
  }

  private static List<NotificationRecord> fifty() {
    var rows = new ArrayList<NotificationRecord>();
    for (int i = 0; i < 50; i++) rows.add(row(200 - i));
    return rows;
  }

  @Test
  void emptyReturnsPlainView() {
    var filters = form(1);
    var page = NotificationListViewModel.success(actor(READER), filters, EMPTY, List.of());
    assertSame(filters, page.getFilters());
    assertTrue(page.getPage().orElseThrow().isEmpty());
    assertEquals(List.of(), page.getRows());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    assertEquals(READER, page.getTopBar().getUsername());
    assertEquals("USER", page.getTopBar().getRole());
    assertEquals("schubert NK", page.getTopBar().getBrand());
    assertEquals("NotificationListViewModel[REDACTED]", page.toString());
  }

  @Test
  void allStatesProduceApprovedLabels() {
    Map<NotificationState, String> labels =
        Map.of(
            NotificationState.RECEIVED,
            "受付通知",
            NotificationState.PROCESSING,
            "受付通知",
            NotificationState.CANCELLED,
            "受付通知",
            NotificationState.COMPLETED,
            "処理済通知",
            NotificationState.ERROR,
            "エラー通知");
    for (var entry : labels.entrySet()) {
      var page = single(row(12, entry.getKey(), AT.plusSeconds(1), BODY, false));
      var actual = page.getRows().getFirst();
      assertEquals(entry.getValue(), actual.get(K_TYPE));
      assertEquals(
          Map.ofEntries(
              Map.entry(K_ID, 12L),
              Map.entry("receiptId", RECEIPT),
              Map.entry(K_TYPE, entry.getValue()),
              Map.entry("state", entry.getKey().name()),
              Map.entry("submittedAt", "1970-01-01 09:00:00"),
              Map.entry("lastUpdatedAt", "1970-01-01 09:00:01"),
              Map.entry(K_SUMMARY, BODY),
              Map.entry("deleted", false),
              Map.entry("detailHref", "/notifications/12")),
          actual);
    }
  }

  @Test
  void pagingLinksKeepFiltersAndClamp() {
    var first =
        NotificationListViewModel.success(
            actor(READER), form(1), new PagedResponseData(1, 50, 51, 2, 1, 50), fifty());
    assertTrue(first.getPreviousHref().isEmpty());
    assertEquals(Optional.of(EMPTY_QUERY + "2"), first.getNextHref());
    var last =
        NotificationListViewModel.success(
            actor(READER), form(2), new PagedResponseData(2, 50, 51, 2, 51, 51), List.of(row(12)));
    assertEquals(Optional.of(EMPTY_QUERY + "1"), last.getPreviousHref());
    assertTrue(last.getNextHref().isEmpty());
    var filters =
        NotificationSearchForm.bind(
            Map.of(
                K_PAGE,
                List.of("2"),
                K_TYPE,
                List.of("ERROR"),
                K_FROM,
                List.of("2026-11-01"),
                K_TO,
                List.of("2026-11-02")));
    var middle =
        NotificationListViewModel.success(
            actor(READER), filters, new PagedResponseData(2, 50, 101, 3, 51, 100), fifty());
    assertEquals(Optional.of(FILTERED_QUERY + "1"), middle.getPreviousHref());
    assertEquals(Optional.of(FILTERED_QUERY + "3"), middle.getNextHref());
    assertEquals(50, middle.getRows().size());
    var clamped =
        NotificationListViewModel.success(
            actor(READER),
            form(999),
            new PagedResponseData(3, 50, 101, 3, 101, 101),
            List.of(row(12)));
    assertEquals(3, clamped.getPage().orElseThrow().getEffectivePage());
    assertEquals(Optional.of(EMPTY_QUERY + "2"), clamped.getPreviousHref());
    assertTrue(clamped.getNextHref().isEmpty());
  }

  @Test
  void invalidFormsStayUnpaginated() {
    var invalid = NotificationSearchForm.bind(Map.of(K_TYPE, List.of("BAD")));
    assertFalse(invalid.isValid());
    var page = NotificationListViewModel.invalid(actor(READER), invalid);
    assertSame(invalid, page.getFilters());
    assertTrue(page.getPage().isEmpty());
    assertTrue(page.getRows().isEmpty());
    assertTrue(page.getPreviousHref().isEmpty());
    assertTrue(page.getNextHref().isEmpty());
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.success(actor(READER), invalid, EMPTY, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.invalid(actor(READER), form(1)));
  }

  @Test
  void wrongEffectivePageRejects() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            NotificationListViewModel.success(
                actor(READER),
                form(1),
                new PagedResponseData(2, 50, 51, 2, 51, 51),
                List.of(row(12))));
  }

  @Test
  void rowCountMismatchRejects() {
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.success(actor(READER), form(1), TWO, List.of(row(12))));
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.success(actor(READER), form(1), EMPTY, List.of(row(12))));
  }

  @Test
  void duplicateIdsReject() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            NotificationListViewModel.success(
                actor(READER), form(1), TWO, List.of(row(12), row(12))));
  }

  @Test
  void inconsistentStateAndDeletedSummaryReject() {
    var wrongType =
        new NotificationRecord(
            new NotificationId(12),
            RECEIPT,
            NotificationType.ERROR,
            NotificationState.RECEIVED,
            AT,
            AT,
            BODY,
            false);
    assertThrows(IllegalArgumentException.class, () -> single(wrongType));
    assertThrows(
        IllegalArgumentException.class,
        () -> single(row(12, NotificationState.RECEIVED, AT, "😀".repeat(101), false)));
    assertThrows(
        IllegalArgumentException.class,
        () -> single(row(12, NotificationState.COMPLETED, AT, BODY, true)));
  }

  @Test
  void orderRulesAreIndependent() {
    assertThrows(
        IllegalArgumentException.class,
        () ->
            NotificationListViewModel.success(
                actor(READER),
                form(1),
                TWO,
                List.of(row(2, NotificationState.RECEIVED, AT, BODY, false), row(1))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            NotificationListViewModel.success(
                actor(READER), form(1), TWO, List.of(row(1), row(2))));
    var tied =
        NotificationListViewModel.success(actor(READER), form(1), TWO, List.of(row(2), row(1)));
    assertEquals(List.of(2L, 1L), tied.getRows().stream().map(x -> x.get(K_ID)).toList());
    var descendingTime =
        NotificationListViewModel.success(
            actor(READER),
            form(1),
            TWO,
            List.of(row(1, NotificationState.RECEIVED, AT.plusSeconds(2), BODY, false), row(2)));
    assertEquals(List.of(1L, 2L), descendingTime.getRows().stream().map(x -> x.get(K_ID)).toList());
  }

  @Test
  void nullBoundariesReject() {
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(null, form(1), EMPTY, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(actor(READER), null, EMPTY, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(actor(READER), form(1), null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(actor(READER), form(1), EMPTY, null));
    assertThrows(
        NullPointerException.class,
        () ->
            NotificationListViewModel.success(
                actor(READER), form(1), ONE, Arrays.asList((NotificationRecord) null)));
    assertThrows(
        NullPointerException.class, () -> NotificationListViewModel.invalid(actor(READER), null));
    var invalid = NotificationSearchForm.bind(Map.of(K_TYPE, List.of("BAD")));
    assertThrows(
        NullPointerException.class, () -> NotificationListViewModel.invalid(null, invalid));
  }

  @Test
  void outputCollectionsAreImmutable() {
    var page = single(row(12));
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().clear());
    assertThrows(UnsupportedOperationException.class, () -> page.getRows().getFirst().clear());
    assertEquals(12L, page.getRows().getFirst().get(K_ID));
  }

  @Test
  void copiedInputDoesNotChangeRows() {
    var supplied = new ArrayList<>(List.of(row(12)));
    var page = NotificationListViewModel.success(actor(READER), form(1), ONE, supplied);
    supplied.clear();
    supplied.add(row(99));
    assertEquals(1, page.getRows().size());
    assertEquals(12L, page.getRows().getFirst().get(K_ID));
  }

  @Test
  void unicodeSummaryBoundaryAndDeletedLiteral() {
    for (String summary : List.of("😀".repeat(99), "😀".repeat(100))) {
      var page = single(row(12, NotificationState.RECEIVED, AT, summary, false));
      assertEquals(summary, page.getRows().getFirst().get(K_SUMMARY));
    }
    var deleted = single(row(12, NotificationState.COMPLETED, AT, DELETED, true));
    assertEquals(DELETED, deleted.getRows().getFirst().get(K_SUMMARY));
    assertEquals(true, deleted.getRows().getFirst().get("deleted"));
  }

  @Test
  void parallelViewsKeepActorsSeparate() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var pending = new ArrayList<Future<NotificationListViewModel>>();
      for (int i = 0; i < 8; i++) {
        String name = READER + i;
        pending.add(
            workers.submit(
                () ->
                    NotificationListViewModel.success(
                        actor(name), form(1), ONE, List.of(row(12)))));
      }
      for (int i = 0; i < 8; i++) {
        var page = pending.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(READER + i, page.getTopBar().getUsername());
        assertEquals(12L, page.getRows().getFirst().get(K_ID));
        assertTrue(page.getNextHref().isEmpty());
      }
    }
  }
}
