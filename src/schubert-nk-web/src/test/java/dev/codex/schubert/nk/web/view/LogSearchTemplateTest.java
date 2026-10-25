package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogId;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.form.LogSearchForm;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.DispatcherServlet;
import org.thymeleaf.spring6.view.ThymeleafViewResolver;

/** PG216/016019/PT-SCR084..091. Actual resolver with independent DOM literals. */
class LogSearchTemplateTest {
  private static SessionPrincipal actor(String name) {
    return new SessionPrincipal(
        name, UserRole.ADMIN, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static LogSearchForm form(Map<String, String> fields) {
    return LogSearchForm.bind(
        fields.entrySet().stream()
            .collect(Collectors.toMap(Map.Entry::getKey, e -> List.of(e.getValue()))));
  }

  private static LogRecord row(long id, boolean full, String text) {
    return new LogRecord(
        new LogId(id),
        Instant.parse("2026-09-20T01:02:03.004Z"),
        LogType.REQUEST,
        LogLevel.INFO,
        full ? Optional.of("search") : Optional.empty(),
        text,
        full ? Optional.of(new UUID(0, 1)) : Optional.empty(),
        full ? Optional.of(new UUID(0, 2)) : Optional.empty(),
        full ? Optional.of(new UUID(0, 3)) : Optional.empty(),
        full ? Optional.of("GET") : Optional.empty(),
        full ? Optional.of("/search") : Optional.empty(),
        full ? Optional.of(new HttpStatusCode(200)) : Optional.empty(),
        full ? Optional.of(new ElapsedMilliseconds(123)) : Optional.empty(),
        full ? Optional.of("127.0.0.1") : Optional.empty(),
        full ? Optional.of(text) : Optional.empty());
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

  private static LogSearchViewModel page(Map<String, String> fields, int page, int total) {
    var rows =
        IntStream.range(0, Math.min(100, Math.max(0, total - (page - 1) * 100)))
            .mapToObj(i -> row(100 - i, false, "body" + i))
            .toList();
    return LogSearchViewModel.success(actor("reader"), form(fields), data(page, total), rows);
  }

  private static AnnotationConfigWebApplicationContext context() {
    var c = new AnnotationConfigWebApplicationContext();
    c.setServletContext(new MockServletContext());
    c.register(WebMvcConfiguration.class);
    c.refresh();
    return c;
  }

  private static Document render(
      AnnotationConfigWebApplicationContext c, LogSearchViewModel page, String csrf, int status)
      throws Exception {
    var view = c.getBean(ThymeleafViewResolver.class).resolveViewName("logs", Locale.JAPAN);
    assertNotNull(view);
    var request = new MockHttpServletRequest(c.getServletContext());
    request.setAttribute(DispatcherServlet.WEB_APPLICATION_CONTEXT_ATTRIBUTE, c);
    request.setMethod("GET");
    request.setRequestURI("/logs");
    request.setScheme("https");
    request.setSecure(true);
    request.setAttribute(CsrfToken.class.getName(), new DefaultCsrfToken("unused", "_csrf", csrf));
    var response = new MockHttpServletResponse();
    response.setStatus(status);
    view.render(Map.of("page", page), request, response);
    assertEquals(status, response.getStatus());
    assertEquals("UTF-8", response.getCharacterEncoding());
    return Jsoup.parse(response.getContentAsString());
  }

  private static Document render(AnnotationConfigWebApplicationContext c, LogSearchViewModel page)
      throws Exception {
    return render(c, page, "public-csrf", 200);
  }

  @Test
  void log084LayoutAndFilters() throws Exception {
    try (var c = context()) {
      var fields =
          Map.of(
              "q",
              "本文",
              "log_type",
              "MQ",
              "action",
              "search",
              "path",
              "/search",
              "level",
              "WARN",
              "from",
              "2026-09-01T09:00",
              "to",
              "2026-09-20T10:02:03.120");
      var d = render(c, page(fields, 1, 1));
      assertEquals("Logs", d.title());
      assertEquals("Logs", d.selectFirst("h1").text());
      assertEquals("ja", d.selectFirst("html").attr("lang"));
      assertEquals(1, d.select("a[href=/]").size());
      assertEquals(List.of("検索", "一覧"), d.select("nav[aria-label=ログナビゲーション] a").eachText());
      assertEquals("1 logs / page 1 of 1", d.selectFirst(".count").text());
      assertEquals(
          List.of("メッセージ", "種別", "アクション", "パス", "レベル", "From", "To"),
          d.select(".log-filters label > span").eachText());
      assertEquals("get", d.selectFirst(".log-filters").attr("method"));
      assertEquals("/logs", d.selectFirst(".log-filters").attr("action"));
      for (var e : fields.entrySet()) {
        var input = d.selectFirst("[name=" + e.getKey() + "]");
        assertNotNull(input);
        assertEquals(
            e.getValue(),
            input.tagName().equals("select")
                ? input.selectFirst("option[selected]").attr("value")
                : input.attr("value"));
        assertEquals("log-errors", input.attr("aria-describedby"));
      }
      assertEquals(
          List.of("", "ACTION", "REQUEST", "SECURITY", "MQ", "SYSTEM", "BATCH"),
          d.select("select[name=log_type] option").eachAttr("value"));
      assertEquals(
          List.of("", "INFO", "WARN", "ERROR"),
          d.select("select[name=level] option").eachAttr("value"));
      for (String name : List.of("from", "to")) {
        assertEquals("datetime-local", d.selectFirst("[name=" + name + "]").attr("type"));
        assertEquals("0.001", d.selectFirst("[name=" + name + "]").attr("step"));
      }
      assertEquals("キーワード", d.selectFirst("[name=q]").attr("placeholder"));
      assertEquals("search", d.selectFirst("[name=action]").attr("placeholder"));
      assertEquals("/search", d.selectFirst("[name=path]").attr("placeholder"));
      assertTrue(d.selectFirst("#log-errors").hasAttr("hidden"));
      assertEquals("検索", d.selectFirst(".log-filters button").text());
    }
  }

  @Test
  void log085RowsAndOptional() throws Exception {
    try (var c = context()) {
      var v =
          LogSearchViewModel.success(
              actor("reader"),
              form(Map.of()),
              data(1, 2),
              List.of(row(9, true, "message"), row(3, false, "empty")));
      var d = render(c, v);
      var rows = d.select(".log-row");
      assertEquals(2, rows.size());
      assertEquals(
          List.of("2026-09-20T01:02:03.004Z", "REQUEST", "INFO", "search"),
          rows.get(0).select(".log-main > *").eachText());
      assertEquals("message", rows.get(0).selectFirst("p").text());
      assertEquals(
          List.of(
              "ID",
              "Request",
              "Message",
              "Correlation",
              "Method",
              "Path",
              "Status",
              "Elapsed",
              "Remote"),
          rows.get(0).select("dt").eachText());
      assertEquals(
          List.of(
              "9",
              "00000000-0000-0000-0000-000000000001",
              "00000000-0000-0000-0000-000000000002",
              "00000000-0000-0000-0000-000000000003",
              "GET",
              "/search",
              "200",
              "123ms",
              "127.0.0.1"),
          rows.get(0).select("dd").eachText());
      assertEquals(List.of("ID"), rows.get(1).select("dt").eachText());
      assertEquals(List.of("3"), rows.get(1).select("dd").eachText());
      assertEquals(3, rows.get(1).select(".log-main > *").size());
      for (var r : rows) {
        assertFalse(r.selectFirst("details").hasAttr("open"));
        assertEquals("details", r.selectFirst("summary").text());
      }
      assertEquals("message", rows.get(0).selectFirst("pre").text());
      assertEquals("", rows.get(1).selectFirst("pre").text());
    }
  }

  @Test
  void log086Pagination() throws Exception {
    try (var c = context()) {
      String prefix = "/logs?q=%E6%97%A5%E6%9C%AC&log_type=&action=&path=&level=&from=&to=&page=";
      for (int total : new int[] {0, 1, 100, 101, 201}) {
        var d = render(c, page(Map.of("q", "日本"), 1, total));
        if (total == 0) {
          assertEquals("該当するデータはありません", d.selectFirst(".empty-results").text());
          assertTrue(d.select(".pagination").isEmpty());
          assertTrue(d.select(".log-row").isEmpty());
        } else {
          assertTrue(d.select(".empty-results").isEmpty());
          assertEquals(2, d.select(".pagination").size());
          for (var nav : d.select(".pagination")) {
            assertEquals("前の100件", nav.children().getFirst().text());
            assertEquals("span", nav.children().getFirst().tagName());
            assertEquals(
                "1 - " + Math.min(total, 100) + " / " + total, nav.selectFirst("div").text());
            if (total > 100) assertEquals(prefix + "2", nav.selectFirst("a").attr("href"));
            else assertTrue(nav.select("a").isEmpty());
          }
        }
      }
      var middle = render(c, page(Map.of("q", "日本", "page", "2"), 2, 201));
      for (var nav : middle.select(".pagination"))
        assertEquals(List.of(prefix + "1", prefix + "3"), nav.select("a").eachAttr("href"));
      var last = render(c, page(Map.of("q", "日本", "page", "999999"), 3, 201));
      assertEquals("201 logs / page 3 of 3", last.selectFirst(".count").text());
      for (var nav : last.select(".pagination")) {
        assertEquals(List.of(prefix + "2"), nav.select("a").eachAttr("href"));
        assertEquals("201 - 201 / 201", nav.selectFirst("div").text());
        assertEquals("span", nav.children().getLast().tagName());
      }
      assertEquals(
          List.of("log pagination", "log pagination bottom"),
          last.select(".pagination").eachAttr("aria-label"));
    }
  }

  @Test
  void log087Escaping() throws Exception {
    try (var c = context()) {
      String text = "<script>\"&'😀";
      var v =
          LogSearchViewModel.success(
              actor(text), form(Map.of("q", text)), data(1, 1), List.of(row(1, true, text)));
      var d = render(c, v);
      assertEquals(text, d.selectFirst(".login-user").text());
      assertEquals(text, d.selectFirst("[name=q]").attr("value"));
      assertEquals(text, d.selectFirst(".log-row > p").text());
      assertEquals(text, d.selectFirst("pre").text());
      assertTrue(d.select("script:not([src]),img,iframe").isEmpty());
      var pages = render(c, page(Map.of("q", "A&B +%"), 1, 101));
      assertEquals(
          "/logs?q=A%26B%20%2B%25&log_type=&action=&path=&level=&from=&to=&page=2",
          pages.selectFirst(".pagination a").attr("href"));
      var invalid =
          LogSearchViewModel.invalid(
              actor("reader"), form(Map.of("log_type", text, "level", text)));
      var bad = render(c, invalid, "public", 400);
      for (String name : List.of("log_type", "level"))
        assertEquals(
            text, bad.selectFirst("select[name=" + name + "] option[selected]").attr("value"));
      assertTrue(bad.select("script:not([src]),img,iframe").isEmpty());
    }
  }

  @Test
  void log088InvalidDisplay() throws Exception {
    try (var c = context()) {
      var v =
          LogSearchViewModel.invalid(
              actor("reader"),
              form(
                  Map.of(
                      "q",
                      "x".repeat(257),
                      "log_type",
                      "invalid",
                      "action",
                      "y".repeat(65),
                      "path",
                      "z".repeat(257),
                      "level",
                      "bad",
                      "from",
                      "bad-date",
                      "to",
                      "bad-date",
                      "page",
                      "+1")));
      var d = render(c, v, "public", 400);
      assertFalse(d.selectFirst("#log-errors").hasAttr("hidden"));
      assertEquals("alert", d.selectFirst("#log-errors").attr("role"));
      assertEquals(
          List.of(
              "error-q",
              "error-log_type",
              "error-action",
              "error-path",
              "error-level",
              "error-from",
              "error-to",
              "error-page"),
          d.select("#log-errors li").eachAttr("id"));
      assertEquals("メッセージはUTF-8で256 byte以内にしてください。", d.selectFirst("#error-q").text());
      assertEquals("x".repeat(257), d.selectFirst("[name=q]").attr("value"));
      assertEquals("bad-date", d.selectFirst("[name=from]").attr("value"));
      assertEquals("invalid", d.selectFirst("[name=log_type] option[selected]").text());
      assertTrue(d.select(".count,.log-results,.pagination").isEmpty());
      var empty = render(c, page(Map.of(), 1, 0));
      assertEquals("", empty.selectFirst("[name=log_type] option[selected]").attr("value"));
      assertEquals("", empty.selectFirst("[name=level] option[selected]").attr("value"));
    }
  }

  @Test
  void log089CsrfAndClosedSurface() throws Exception {
    try (var c = context()) {
      var d = render(c, page(Map.of(), 1, 0), "public-log-csrf", 200);
      assertEquals(1, d.select("form[method=post]").size());
      assertEquals("/logout", d.selectFirst("form[method=post]").attr("action"));
      assertEquals(
          "public-log-csrf", d.selectFirst("form[method=post] input[name=_csrf]").attr("value"));
      assertTrue(d.select(".log-filters input[type=hidden]").isEmpty());
      assertEquals("ADMIN", d.selectFirst(".login-role").text());
      assertFalse(d.html().contains("a".repeat(64)));
      assertTrue(d.select("input[type=password],audio,video,script:not([src])").isEmpty());
      assertEquals(
          List.of("/js/log-search-validation.js"), d.select("script[src]").eachAttr("src"));
    }
  }

  @Test
  void log090StylesAndResources() throws Exception {
    try (var c = context()) {
      var resolver = c.getBean(ThymeleafViewResolver.class);
      assertNotNull(resolver.resolveViewName("logs", Locale.JAPAN));
      for (String name :
          List.of(
              "unknown", "fragments/log-pagination", "../logs", "redirect:/logs", "forward:/logs"))
        assertNull(resolver.resolveViewName(name, Locale.JAPAN));
      var response =
          MockMvcBuilders.webAppContextSetup(c)
              .build()
              .perform(get("/css/schubert.css"))
              .andReturn()
              .getResponse();
      assertEquals(200, response.getStatus());
      assertTrue(response.getContentType().startsWith("text/css"));
      String css = response.getContentAsString();
      for (String literal :
          List.of(
              ".log-page .log-row { display: grid; gap: 8px;",
              ".log-page .log-main { display: flex; flex-wrap: wrap;",
              ".log-page .log-fields dt { font-weight: 700; }",
              ".log-page .log-fields dd { margin: 0; }",
              ".log-page .log-details pre { overflow: auto;",
              ".log-page .log-filters label:nth-child(6), .log-page .log-filters label:nth-child(7) { grid-column: span 3; }",
              ".log-page .log-filters label:nth-child(n), .log-page .log-filters button { grid-column: 1 / -1; }",
              ".log-page .pagination.bottom-nav { margin-top: 12px; margin-bottom: 0; }"))
        assertTrue(css.contains(literal), literal);
      String template = Files.readString(Path.of("src/main/resources/templates/logs.html"));
      assertFalse(template.contains("th:utext"));
      assertFalse(template.contains("<script>") || template.contains("onerror="));
      assertTrue(template.contains("th:src=\"@{/js/log-search-validation.js}\""));
      var script =
          MockMvcBuilders.webAppContextSetup(c)
              .build()
              .perform(get("/js/log-search-validation.js"))
              .andReturn()
              .getResponse();
      assertEquals(200, script.getStatus());
      assertTrue(script.getContentType().startsWith("text/javascript"));
      assertEquals(
          Files.readString(Path.of("src/main/resources/static/js/log-search-validation.js")),
          script.getContentAsString(java.nio.charset.StandardCharsets.UTF_8));
      assertTrue(template.contains("aria-describedby=\"log-errors\""));
    }
  }

  @Test
  void log091ConcurrentRendering() throws Exception {
    try (var c = context();
        var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<Document>>();
      for (int i = 0; i < 64; i++) {
        final int index = i;
        futures.add(
            pool.submit(
                () ->
                    render(
                        c,
                        LogSearchViewModel.success(
                            actor("reader" + index),
                            form(Map.of("q", "q" + index)),
                            data(1, 1),
                            List.of(row(index + 1, false, "body" + index))),
                        "public-csrf-" + index,
                        200)));
      }
      for (int i = 0; i < 64; i++) {
        var d = futures.get(i).get(10, TimeUnit.SECONDS);
        assertEquals("reader" + i, d.selectFirst(".login-user").text());
        assertEquals("q" + i, d.selectFirst("[name=q]").attr("value"));
        assertEquals("body" + i, d.selectFirst(".log-row > p").text());
        assertEquals(Integer.toString(i + 1), d.selectFirst(".log-fields dd").text());
        assertEquals("public-csrf-" + i, d.selectFirst("input[name=_csrf]").attr("value"));
        assertTrue(d.select(".pagination a").isEmpty());
      }
    }
  }
}
