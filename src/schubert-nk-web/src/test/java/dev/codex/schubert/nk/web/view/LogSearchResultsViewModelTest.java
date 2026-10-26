package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.LogRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.LogId;
import dev.codex.schubert.nk.protocol.layout.semantic.LogLevel;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.beans.Introspector;
import java.lang.reflect.Modifier;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.thymeleaf.context.Context;
import org.thymeleaf.spring6.SpringTemplateEngine;
import org.thymeleaf.templateresolver.StringTemplateResolver;

/** PG212/PT-WEB262..269/FUN008/AUT/MON/UI225,235/SS311,313,323,352. */
class LogSearchResultsViewModelTest {
  private static final String READER_USERNAME = "reader";
  private static final String LOG_MESSAGE_TEXT = "message";
  private static final Instant TIME = Instant.parse("2026-09-20T01:02:03.004Z");
  private static final UUID REQUEST = new UUID(0, 1);
  private static final UUID MESSAGE = new UUID(0, 2);
  private static final UUID CORRELATION = new UUID(0, 3);

  private static SessionPrincipal actor(String name, UserRole role) {
    return new SessionPrincipal(name, role, AuthenticationContext.of("a".repeat(64)), TIME);
  }

  private static SessionPrincipal admin() {
    return actor(READER_USERNAME, UserRole.ADMIN);
  }

  private static <T> Optional<T> value(int mask, int bit, T value) {
    return (mask & (1 << bit)) == 0 ? Optional.empty() : Optional.of(value);
  }

  private static LogRecord record(long id, Instant time, int mask, String text) {
    return new LogRecord(
        new LogId(id),
        time,
        LogType.REQUEST,
        LogLevel.INFO,
        value(mask, 0, "search"),
        text,
        value(mask, 1, REQUEST),
        value(mask, 2, MESSAGE),
        value(mask, 3, CORRELATION),
        value(mask, 4, "GET"),
        value(mask, 5, "/search"),
        value(mask, 6, new HttpStatusCode(200)),
        value(mask, 7, new ElapsedMilliseconds(123)),
        value(mask, 8, "127.0.0.1"),
        value(mask, 9, "{\"safe\":\"value\"}"));
  }

  private static PagedResponseData one() {
    return new PagedResponseData(1, 100, 1, 1, 1, 1);
  }

  private static LogSearchResultsViewModel model(LogRecord r) {
    return LogSearchResultsViewModel.from(admin(), one(), List.of(r));
  }

  @Test
  void web262CompleteRow() {
    var p = model(record(999999999999L, TIME, 1023, LOG_MESSAGE_TEXT));
    var r = p.getRows().getFirst();
    assertEquals(READER_USERNAME, p.getTopBar().getUsername());
    assertEquals("ADMIN", p.getTopBar().getRole());
    assertEquals(1, p.getPage().getTotalCount());
    assertEquals(100, p.getPage().getPageSize());
    assertEquals(999999999999L, r.getId());
    assertEquals("2026-09-20T01:02:03.004Z", r.getLoggedAt());
    assertEquals("REQUEST", r.getLogType());
    assertEquals("INFO", r.getLevel());
    assertEquals("search", r.getAction());
    assertEquals(LOG_MESSAGE_TEXT, r.getMessage());
    assertEquals("00000000-0000-0000-0000-000000000001", r.getRequestId());
    assertEquals("00000000-0000-0000-0000-000000000002", r.getMessageId());
    assertEquals("00000000-0000-0000-0000-000000000003", r.getCorrelationId());
    assertEquals("GET", r.getMethod());
    assertEquals("/search", r.getPath());
    assertEquals(Optional.of(200), r.getStatus());
    assertEquals(Optional.of(123), r.getElapsedMs());
    assertEquals("127.0.0.1", r.getRemoteAddr());
    assertEquals("{\"safe\":\"value\"}", r.getDetails());
    for (var pair :
        List.of(
            List.of("2026-09-19T15:00:00Z", "2026-09-19T15:00Z"),
            List.of("2026-09-20T01:02:03Z", "2026-09-20T01:02:03Z"),
            List.of("2026-09-20T01:02:03.120Z", "2026-09-20T01:02:03.120Z")))
      assertEquals(
          pair.get(1),
          model(record(1, Instant.parse(pair.get(0)), 0, "x")).getRows().getFirst().getLoggedAt());
  }

  @Test
  void web263OptionalFields() {
    String[] expected = {
      "search",
      "00000000-0000-0000-0000-000000000001",
      "00000000-0000-0000-0000-000000000002",
      "00000000-0000-0000-0000-000000000003",
      "GET",
      "/search",
      "200",
      "123",
      "127.0.0.1",
      "{\"safe\":\"value\"}"
    };
    for (int mask = 0; mask < 1024; mask++) {
      var r = model(record(1, TIME, mask, LOG_MESSAGE_TEXT)).getRows().getFirst();
      var actual =
          List.of(
              r.getAction(),
              r.getRequestId(),
              r.getMessageId(),
              r.getCorrelationId(),
              r.getMethod(),
              r.getPath(),
              r.getStatus().map(Object::toString).orElse(""),
              r.getElapsedMs().map(Object::toString).orElse(""),
              r.getRemoteAddr(),
              r.getDetails());
      for (int bit = 0; bit < 10; bit++)
        assertEquals((mask & (1 << bit)) == 0 ? "" : expected[bit], actual.get(bit));
    }
  }

  @Test
  void web264PageBounds() {
    var empty =
        LogSearchResultsViewModel.from(
            admin(), new PagedResponseData(1, 100, 0, 1, 0, 0), List.of());
    assertTrue(empty.getPage().isEmpty());
    assertTrue(empty.getRows().isEmpty());
    var records = new ArrayList<LogRecord>();
    for (int i = 100; i > 0; i--) records.add(record(i, TIME, 0, "m" + i));
    var page =
        LogSearchResultsViewModel.from(
            admin(), new PagedResponseData(2, 100, 300, 3, 101, 200), records);
    assertEquals(100, page.getRows().size());
    assertEquals(101, page.getPage().getFirstResult());
    assertEquals(200, page.getPage().getLastResult());
    var last =
        LogSearchResultsViewModel.from(
            admin(),
            new PagedResponseData(2, 100, 101, 2, 101, 101),
            List.of(record(1, TIME, 0, "x")));
    assertEquals(101, last.getPage().getTotalCount());
    assertEquals(1, last.getRows().size());
    assertEquals(
        999999,
        LogSearchResultsViewModel.from(
                admin(),
                new PagedResponseData(999999, 100, 99999900, 999999, 99999801, 99999900),
                records)
            .getPage()
            .getEffectivePage());
    var extra = new ArrayList<>(records);
    extra.add(record(101, TIME.minusSeconds(1), 0, "extra"));
    for (var data :
        List.of(
            new PagedResponseData(1, 50, 1, 1, 1, 1), new PagedResponseData(1, 100, 1, 1, 1, 0)))
      assertThrows(
          IllegalArgumentException.class,
          () -> LogSearchResultsViewModel.from(admin(), data, List.of(record(1, TIME, 0, "x"))));
    assertThrows(
        IllegalArgumentException.class,
        () -> LogSearchResultsViewModel.from(admin(), one(), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            LogSearchResultsViewModel.from(
                admin(), new PagedResponseData(1, 100, 100, 1, 1, 100), extra));
  }

  @Test
  void web265OrderingAndIdentity() {
    var data = new PagedResponseData(1, 100, 2, 1, 1, 2);
    for (var list :
        List.of(
            List.of(record(1, TIME, 0, "new"), record(2, TIME.minusMillis(1), 0, "old")),
            List.of(record(2, TIME, 0, "higher"), record(1, TIME, 0, "lower")))) {
      var p = LogSearchResultsViewModel.from(admin(), data, list);
      assertEquals(list.get(0).message(), p.getRows().getFirst().getMessage());
      assertEquals(list.get(1).message(), p.getRows().getLast().getMessage());
    }
    for (var list :
        List.of(
            List.of(record(1, TIME, 0, "same"), record(1, TIME, 0, "same")),
            List.of(record(1, TIME, 0, "low"), record(2, TIME, 0, "high")),
            List.of(record(1, TIME, 0, "old"), record(2, TIME.plusMillis(1), 0, "new")),
            List.of(record(1, TIME, 0, "new"), record(1, TIME.minusMillis(1), 0, "old"))))
      assertThrows(
          IllegalArgumentException.class,
          () -> LogSearchResultsViewModel.from(admin(), data, list));
  }

  @Test
  void web266NullRoleAndOwnership() {
    var r = record(1, TIME, 0, "x");
    assertThrows(
        NullPointerException.class, () -> LogSearchResultsViewModel.from(null, one(), List.of(r)));
    assertThrows(
        NullPointerException.class,
        () -> LogSearchResultsViewModel.from(admin(), null, List.of(r)));
    assertThrows(
        NullPointerException.class, () -> LogSearchResultsViewModel.from(admin(), one(), null));
    var nullItem = new ArrayList<LogRecord>();
    nullItem.add(null);
    assertThrows(
        NullPointerException.class, () -> LogSearchResultsViewModel.from(admin(), one(), nullItem));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            LogSearchResultsViewModel.from(
                actor(READER_USERNAME, UserRole.USER), one(), List.of(r)));
    var original = new ArrayList<>(List.of(r));
    var p = LogSearchResultsViewModel.from(admin(), one(), original);
    original.clear();
    assertEquals(1, p.getRows().size());
    assertEquals("x", p.getRows().getFirst().getMessage());
    assertThrows(UnsupportedOperationException.class, () -> p.getRows().clear());
  }

  @Test
  void web267ClosedBeansAndRedaction() throws Exception {
    var p = model(record(1, TIME, 1023, "sensitive-display"));
    assertEquals("LogSearchResultsViewModel[REDACTED]", p.toString());
    assertEquals("LogDisplayRow[REDACTED]", p.getRows().getFirst().toString());
    assertEquals(Set.of("topBar", "page", "rows"), properties(LogSearchResultsViewModel.class));
    assertEquals(
        Set.of(
            "id",
            "loggedAt",
            "logType",
            "level",
            "action",
            LOG_MESSAGE_TEXT,
            "requestId",
            "messageId",
            "correlationId",
            "method",
            "path",
            "status",
            "elapsedMs",
            "remoteAddr",
            "details"),
        properties(LogSearchResultsViewModel.Row.class));
    for (var type : List.of(LogSearchResultsViewModel.class, LogSearchResultsViewModel.Row.class))
      for (var field : type.getDeclaredFields()) {
        if (Modifier.isStatic(field.getModifiers())) continue;
        assertTrue(
            Set.of(
                    TopBarViewModel.class,
                    PageViewModel.class,
                    List.class,
                    String.class,
                    long.class,
                    Optional.class)
                .contains(field.getType()),
            field.getName());
        assertTrue(Modifier.isFinal(field.getModifiers()));
      }
  }

  @Test
  void web268SyntheticHtmlEscaping() {
    String text = "<b>&";
    var record =
        new LogRecord(
            new LogId(1),
            TIME,
            LogType.SYSTEM,
            LogLevel.ERROR,
            Optional.of(text),
            text,
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.of(text),
            Optional.of(text),
            Optional.empty(),
            Optional.empty(),
            Optional.of(text),
            Optional.of(text));
    var p = LogSearchResultsViewModel.from(actor(text, UserRole.ADMIN), one(), List.of(record));
    var engine = new SpringTemplateEngine();
    engine.setTemplateResolver(new StringTemplateResolver());
    var context = new Context(Locale.JAPAN);
    context.setVariable("page", p);
    var dom =
        Jsoup.parse(
            engine.process(
                "<main><h1 th:text=\"${page.topBar.username}\"></h1><article th:each=\"r : ${page.rows}\"><p th:text=\"${r.message}\"></p><span th:text=\"${r.path}\"></span><pre th:text=\"${r.details}\"></pre></article></main>",
                context));
    assertEquals(text, dom.select("h1").text());
    assertEquals(text, dom.select("p").text());
    assertEquals(text, dom.select("span").text());
    assertEquals(text, dom.select("pre").text());
    assertTrue(dom.select("b,script,[onerror]").isEmpty());
    assertFalse(dom.outerHtml().contains("a".repeat(64)));
    assertEquals("SYSTEM", p.getRows().getFirst().getLogType());
    assertEquals("ERROR", p.getRows().getFirst().getLevel());
  }

  @Test
  void web269ConcurrentProjection() throws Exception {
    var input = List.of(record(1, TIME, 1023, "shared"));
    try (var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 64; i++) {
        final int n = i;
        futures.add(
            pool.submit(
                () -> {
                  var p =
                      LogSearchResultsViewModel.from(
                          actor(READER_USERNAME + n, UserRole.ADMIN), one(), input);
                  assertEquals(READER_USERNAME + n, p.getTopBar().getUsername());
                  assertEquals("shared", p.getRows().getFirst().getMessage());
                  assertEquals(1, p.getPage().getTotalCount());
                  assertEquals(1, p.getRows().size());
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
    }
    assertEquals("shared", input.getFirst().message());
    assertEquals(1, input.size());
  }

  private static Set<String> properties(Class<?> type) throws Exception {
    var result = new HashSet<String>();
    for (var property : Introspector.getBeanInfo(type, Object.class).getPropertyDescriptors())
      result.add(property.getName());
    return result;
  }
}
