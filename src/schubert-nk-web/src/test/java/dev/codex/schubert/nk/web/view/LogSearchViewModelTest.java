package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.LogId;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.form.LogSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.Introspector;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.IntStream;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** PG215/015030/PT-WEB286..293. Independent literals, no production-generated expected. */
class LogSearchViewModelTest {
  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(
        name, role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static SessionPrincipal admin() {
    return actor("reader", UserRole.ADMIN);
  }

  private static LogSearchForm form(String q, String page) {
    return LogSearchForm.bind(Map.of("q", List.of(q), "page", List.of(page)));
  }

  private static LogRecord row(long id, String text) {
    return new LogRecord(
        new LogId(id),
        Instant.parse("2026-09-20T01:02:03Z"),
        LogType.REQUEST,
        LogLevel.INFO,
        Optional.empty(),
        text,
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty(),
        Optional.empty());
  }

  private static PagedResponseData data(int page, int total) {
    return new PagedResponseData(
        page,
        100,
        total,
        Math.max(1, (total + 99) / 100),
        total == 0 ? 0 : (page - 1L) * 100 + 1,
        Math.min(page * 100L, total));
  }

  private static List<LogRecord> rows(int page, int total) {
    int count = Math.min(100, Math.max(0, total - (page - 1) * 100));
    return IntStream.range(0, count).mapToObj(i -> row(100 - i, "body-" + i)).toList();
  }

  private static LogSearchViewModel view(LogSearchForm form, int page, int total) {
    return LogSearchViewModel.success(admin(), form, data(page, total), rows(page, total));
  }

  @Test
  void web286SuccessfulSnapshot() {
    var f =
        LogSearchForm.bind(
            Map.of(
                "q",
                List.of("本文"),
                "log_type",
                List.of("MQ"),
                "action",
                List.of("search"),
                "path",
                List.of("/search"),
                "level",
                List.of("WARN"),
                "from",
                List.of("2026-09-01T09:00"),
                "to",
                List.of("2026-09-20T10:02:03.120")));
    var v =
        LogSearchViewModel.success(
            admin(), f, data(1, 2), List.of(row(9, "first"), row(3, "second")));
    assertEquals("reader", v.getTopBar().getUsername());
    assertEquals("ADMIN", v.getTopBar().getRole());
    assertEquals("schubert NK", v.getTopBar().getBrand());
    var filters = v.getFilters();
    assertEquals("本文", filters.getQ());
    assertEquals("MQ", filters.getLogType());
    assertEquals("search", filters.getAction());
    assertEquals("/search", filters.getPath());
    assertEquals("WARN", filters.getLevel());
    assertEquals("2026-09-01T09:00", filters.getFrom());
    assertEquals("2026-09-20T10:02:03.120", filters.getTo());
    assertTrue(v.getErrors().isEmpty());
    assertEquals(
        List.of(9L, 3L),
        v.getResults().orElseThrow().getRows().stream()
            .map(LogSearchResultsViewModel.Row::getId)
            .toList());
    assertEquals(
        List.of("first", "second"),
        v.getResults().orElseThrow().getRows().stream()
            .map(LogSearchResultsViewModel.Row::getMessage)
            .toList());
  }

  @Test
  void web287Pagination() {
    String prefix = "/logs?q=&log_type=&action=&path=&level=&from=&to=&page=";
    for (int total : new int[] {0, 1, 100}) {
      var v = view(form("", "1"), 1, total);
      assertTrue(v.getPreviousHref().isEmpty());
      assertTrue(v.getNextHref().isEmpty());
      assertEquals(total, v.getResults().orElseThrow().getPage().getTotalCount());
    }
    for (int total : new int[] {101, 201}) {
      var first = view(form("", "1"), 1, total);
      assertTrue(first.getPreviousHref().isEmpty());
      assertEquals(Optional.of(prefix + "2"), first.getNextHref());
    }
    var middle = view(form("", "2"), 2, 201);
    assertEquals(Optional.of(prefix + "1"), middle.getPreviousHref());
    assertEquals(Optional.of(prefix + "3"), middle.getNextHref());
    var last = view(form("", "999999"), 3, 201);
    assertEquals(Optional.of(prefix + "2"), last.getPreviousHref());
    assertTrue(last.getNextHref().isEmpty());
  }

  @Test
  void web288QueryEncoding() {
    var f =
        LogSearchForm.bind(
            Map.of(
                "q",
                List.of("a +&=\"#%日本😀"),
                "log_type",
                List.of("SYSTEM"),
                "action",
                List.of("A&B"),
                "path",
                List.of("x/y?"),
                "level",
                List.of("ERROR"),
                "from",
                List.of("2026-09-01T09:00:00.001"),
                "to",
                List.of("2026-09-02T10:00"),
                "page",
                List.of("2")));
    String prefix =
        "/logs?q=a%20%2B%26%3D%22%23%25%E6%97%A5%E6%9C%AC%F0%9F%98%80"
            + "&log_type=SYSTEM&action=A%26B&path=x%2Fy%3F&level=ERROR&from=2026-09-01T09%3A00%3A00.001&to=2026-09-02T10%3A00&page=";
    var v = view(f, 2, 201);
    assertEquals(Optional.of(prefix + "1"), v.getPreviousHref());
    assertEquals(Optional.of(prefix + "3"), v.getNextHref());
  }

  @Test
  void web289ResponseBinding() {
    assertThrows(IllegalArgumentException.class, () -> view(form("", "1"), 2, 101));
    assertThrows(IllegalArgumentException.class, () -> view(form("", "2"), 1, 101));
    assertThrows(IllegalArgumentException.class, () -> view(form("", "+1"), 1, 0));
    assertThrows(
        IllegalArgumentException.class,
        () -> LogSearchViewModel.success(admin(), form("", "1"), data(1, 1), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            LogSearchViewModel.success(
                admin(), form("", "1"), data(1, 2), List.of(row(1, "a"), row(2, "b"))));
    assertThrows(
        IllegalArgumentException.class, () -> LogSearchViewModel.invalid(admin(), form("", "1")));
  }

  @Test
  void web290InvalidFields() {
    var f =
        LogSearchForm.bind(
            Map.of(
                "q",
                List.of("a".repeat(257)),
                "log_type",
                List.of("wrong"),
                "action",
                List.of("b".repeat(65)),
                "path",
                List.of("c".repeat(257)),
                "level",
                List.of("bad"),
                "from",
                List.of("bad"),
                "to",
                List.of("bad"),
                "page",
                List.of("+1"),
                "unknown-private",
                List.of("private")));
    var v = LogSearchViewModel.invalid(admin(), f);
    assertEquals(
        List.of("form", "q", "log_type", "action", "path", "level", "from", "to", "page"),
        v.getErrors().stream().map(LogSearchViewModel.FieldError::getName).toList());
    assertEquals(
        List.of(
            "入力項目を確認してください。",
            "メッセージはUTF-8で256 byte以内にしてください。",
            "入力値を確認してください。",
            "アクションはUTF-8で64 byte以内にしてください。",
            "パスはUTF-8で256 byte以内にしてください。",
            "入力値を確認してください。",
            "入力値を確認してください。",
            "入力値を確認してください。",
            "入力値を確認してください。"),
        v.getErrors().stream().map(LogSearchViewModel.FieldError::getMessage).toList());
    assertEquals("a".repeat(257), v.getFilters().getQ());
    assertTrue(v.getResults().isEmpty());
    assertTrue(v.getPreviousHref().isEmpty());
    assertTrue(v.getNextHref().isEmpty());
    var control = LogSearchViewModel.invalid(admin(), form("\n", "1"));
    assertEquals("", control.getFilters().getQ());
    assertEquals("使用できない文字が含まれています。", control.getErrors().getFirst().getMessage());
    var range =
        LogSearchViewModel.invalid(
            admin(),
            LogSearchForm.bind(
                Map.of(
                    "from",
                    List.of("2026-09-01T00:00"),
                    "to",
                    List.of("2026-10-02T00:00:00.001"))));
    assertEquals("to", range.getErrors().getFirst().getName());
    assertEquals("From/Toは順序を確認し、31日以内にしてください。", range.getErrors().getFirst().getMessage());
    var duplicate =
        LogSearchViewModel.invalid(admin(), LogSearchForm.bind(Map.of("q", List.of("a", "b"))));
    assertEquals("q", duplicate.getErrors().getFirst().getName());
    assertEquals("入力項目を確認してください。", duplicate.getErrors().getFirst().getMessage());
  }

  @Test
  void web291NullRoleOwnership() {
    var actor = admin();
    var f = form("", "1");
    var d = data(1, 1);
    var r = List.of(row(1, "original"));
    assertThrows(NullPointerException.class, () -> LogSearchViewModel.success(null, f, d, r));
    assertThrows(NullPointerException.class, () -> LogSearchViewModel.success(actor, null, d, r));
    assertThrows(NullPointerException.class, () -> LogSearchViewModel.success(actor, f, null, r));
    assertThrows(NullPointerException.class, () -> LogSearchViewModel.success(actor, f, d, null));
    assertThrows(
        NullPointerException.class,
        () -> LogSearchViewModel.success(actor, f, d, Arrays.asList((LogRecord) null)));
    assertThrows(NullPointerException.class, () -> LogSearchViewModel.invalid(actor, null));
    assertThrows(
        NullPointerException.class, () -> LogSearchViewModel.invalid(null, form("", "+1")));
    var user = actor("user", UserRole.USER);
    assertThrows(IllegalArgumentException.class, () -> LogSearchViewModel.success(user, f, d, r));
    assertThrows(
        IllegalArgumentException.class, () -> LogSearchViewModel.invalid(user, form("", "+1")));
    var mutable = new ArrayList<>(r);
    var v = LogSearchViewModel.success(actor, f, d, mutable);
    mutable.clear();
    assertEquals("original", v.getResults().orElseThrow().getRows().getFirst().getMessage());
    assertThrows(UnsupportedOperationException.class, () -> v.getErrors().clear());
    assertThrows(
        UnsupportedOperationException.class, () -> v.getResults().orElseThrow().getRows().clear());
  }

  private static Set<String> properties(Class<?> type) throws Exception {
    var result = new TreeSet<String>();
    for (var descriptor : Introspector.getBeanInfo(type, Object.class).getPropertyDescriptors()) {
      assertNull(descriptor.getWriteMethod());
      result.add(descriptor.getName());
    }
    return result;
  }

  @Test
  void web292ClosedBeanAndEscaping() throws Exception {
    assertEquals(
        Set.of("topBar", "filters", "errors", "results", "previousHref", "nextHref"),
        properties(LogSearchViewModel.class));
    assertEquals(
        Set.of("q", "logType", "action", "path", "level", "from", "to"),
        properties(LogSearchViewModel.Filters.class));
    assertEquals(Set.of("name", "message"), properties(LogSearchViewModel.FieldError.class));
    String text = "<script>\"&'😀";
    var v = view(form(text, "1"), 1, 0);
    assertEquals("LogSearchViewModel[REDACTED]", v.toString());
    assertEquals("LogFilters[REDACTED]", v.getFilters().toString());
    var invalid = LogSearchViewModel.invalid(admin(), form("\n", "1"));
    assertEquals("LogFieldError[REDACTED]", invalid.getErrors().getFirst().toString());
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(new StringTemplateResolver());
    var context = new Context();
    context.setVariable("view", v);
    var html = Jsoup.parse(engine.process("<p th:text='${view.filters.q}'></p>", context));
    assertEquals(text, html.selectFirst("p").text());
    assertTrue(html.select("script").isEmpty());
    assertFalse(html.html().contains("a".repeat(64)));
  }

  @Test
  void web293ConcurrentViews() throws Exception {
    var shared = List.of(row(2, "shared"), row(1, "second"));
    try (var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<LogSearchViewModel>>();
      for (int i = 0; i < 64; i++) {
        final int index = i;
        futures.add(
            pool.submit(
                () ->
                    LogSearchViewModel.success(
                        actor("r" + index, UserRole.ADMIN),
                        form("q" + index, "1"),
                        data(1, 2),
                        shared)));
      }
      for (int i = 0; i < 64; i++) {
        var v = futures.get(i).get(10, TimeUnit.SECONDS);
        assertEquals("r" + i, v.getTopBar().getUsername());
        assertEquals("q" + i, v.getFilters().getQ());
        assertEquals(
            List.of(2L, 1L),
            v.getResults().orElseThrow().getRows().stream()
                .map(LogSearchResultsViewModel.Row::getId)
                .toList());
        assertTrue(v.getErrors().isEmpty());
        assertTrue(v.getPreviousHref().isEmpty());
        assertTrue(v.getNextHref().isEmpty());
      }
    }
    assertEquals(List.of(2L, 1L), shared.stream().map(r -> r.logId().value()).toList());
  }
}
