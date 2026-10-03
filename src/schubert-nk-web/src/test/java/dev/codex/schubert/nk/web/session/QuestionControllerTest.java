package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.*;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import dev.codex.schubert.nk.web.config.QuestionMvcConfiguration;
import dev.codex.schubert.nk.web.controller.QuestionController;
import dev.codex.schubert.nk.web.form.QuestionSearchForm;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.*;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.*;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.*;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** Independent UI224236 wholebyte/DOM/HTTP oracles; PG-D350/016063/PT-QRY-HTTP001..012. */
class QuestionControllerTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-03T00:00:00Z"), ZoneOffset.UTC);
  private static final Instant SUBMITTED = Instant.parse("2026-10-02T23:58:00Z"),
      ANSWERED = Instant.parse("2026-10-02T23:59:00Z");
  private static final String RECEIPT = "0123456789ABCDEFGHJKMNPQRS";
  private static WebLogDatabaseFixture db;
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("DELETE FROM schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        "reader", role, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static LinkedMultiValueMap<String, String> params(String... pairs) {
    var result = new LinkedMultiValueMap<String, String>();
    for (int i = 0; i < pairs.length; i += 2) result.add(pairs[i], pairs[i + 1]);
    return result;
  }

  private static MockHttpServletRequest raw() {
    return new MockHttpServletRequest("GET", "/questions");
  }

  private static CsrfToken csrf() {
    return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      QuestionWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(QuestionMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        f -> {
          f.registerSingleton("questionWireClient", client);
          f.registerSingleton("apiSessionInvalidHandler", invalid);
        });
  }

  @Test
  void qry001IndependentSearchWireAndRoles() throws Exception {
    for (UserRole role : UserRole.values())
      for (String code : List.of("0000", "0200"))
        try (var f = new Fixture()) {
          f.code = code;
          var input =
              params(
                  "keyword",
                  " e\u0301 &+ ",
                  "state",
                  "ANSWERED",
                  "from",
                  "2026-10-03",
                  "to",
                  "2026-10-03",
                  "page",
                  "000001");
          if (role == UserRole.ADMIN) input.add("username", "reader");
          var model = new ExtendedModelMap();
          var response = new MockHttpServletResponse();
          assertEquals(
              "questions/list", f.controller.list(input, actor(role), model, raw(), response));
          assertEquals(200, response.getStatus());
          var page = assertInstanceOf(QuestionListViewModel.class, model.get("page"));
          assertEquals("é &+", page.getFilters().getValues().get("keyword"));
          assertEquals("回答済み", page.getRows().getFirst().get("stateLabel"));
          byte[] expected = request("QSSREQ01", 384, "a".repeat(64), new UUID(0, 1));
          put(expected, 256, 256, "é &+");
          if (role == UserRole.ADMIN) put(expected, 512, 64, "reader");
          put(expected, 576, 12, "ANSWERED");
          put(expected, 588, 17, "20261003000000000");
          put(expected, 605, 17, "20261003235959999");
          number(expected, 622, 6, 1);
          number(expected, 628, 3, 50);
          assertArrayEquals(expected, f.requests.getFirst());
          f.erased();
        }
  }

  @Test
  void qry002ClosedNullAndByteBoundaries() throws Exception {
    for (UserRole role : UserRole.values()) {
      assertTrue(QuestionSearchForm.bind(params("keyword", "x".repeat(256)), role).isValid());
      assertTrue(QuestionSearchForm.bind(params("keyword", "界".repeat(85) + "x"), role).isValid());
      for (var input :
          List.of(
              params("keyword", "x".repeat(257)),
              params("keyword", "界".repeat(85) + "xx"),
              params("state", "UNKNOWN"),
              params("state", "answered"),
              params("owner", "reader"),
              params("role", "ADMIN"),
              params("keyword", "x", "keyword", "y"))) invalid(input, role);
      for (String field : List.of("keyword", "state", "from", "to", "page"))
        for (String raw : List.of("\r", "\n", "\t", "\0", "\u001f", "\u0085", "\ud800", "\udfff"))
          invalid(params(field, raw), role);
      var empty = params();
      empty.put("keyword", List.of());
      invalid(empty, role);
    }
    assertTrue(
        QuestionSearchForm.bind(params("username", "x".repeat(64)), UserRole.ADMIN).isValid());
    invalid(params("username", "x".repeat(65)), UserRole.ADMIN);
    invalid(params("username", "\r"), UserRole.ADMIN);
    for (String name : List.of("", "reader", "other")) {
      var input = params("username", name);
      invalid(input, UserRole.USER);
      assertEquals("", QuestionSearchForm.bind(input, UserRole.USER).getValues().get("username"));
    }
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(null, UserRole.USER));
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(params(), null));
    var bad = new HashMap<String, List<String>>();
    bad.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(bad, UserRole.USER));
    bad.clear();
    bad.put("keyword", null);
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(bad, UserRole.USER));
    bad.put("keyword", Arrays.asList((String) null));
    assertThrows(NullPointerException.class, () -> QuestionSearchForm.bind(bad, UserRole.USER));
    var good = QuestionSearchForm.bind(params("keyword", "x"), UserRole.USER);
    assertEquals("QuestionSearchForm[REDACTED]", good.toString());
    assertThrows(
        UnsupportedOperationException.class, () -> good.getValues().put("keyword", "changed"));
    assertThrows(
        UnsupportedOperationException.class, () -> good.getIssues().put("keyword", "changed"));
  }

  private static void invalid(LinkedMultiValueMap<String, String> input, UserRole role)
      throws Exception {
    var form = QuestionSearchForm.bind(input, role);
    assertFalse(form.isValid());
    assertFalse(form.getIssues().isEmpty());
    assertThrows(IllegalArgumentException.class, form::toRequest);
    try (var f = new Fixture()) {
      var reply = new MockHttpServletResponse();
      var model = new ExtendedModelMap();
      assertEquals("questions/list", f.controller.list(input, actor(role), model, raw(), reply));
      assertEquals(400, reply.getStatus());
      assertTrue(f.requests.isEmpty());
      assertTrue(
          assertInstanceOf(QuestionListViewModel.class, model.get("page")).getPage().isEmpty());
      f.erased();
    }
  }

  @Test
  void qry003CalendarAndPageBounds() throws Exception {
    for (String day : List.of("0001-01-01", "9999-12-31", "2024-02-29")) {
      var value = QuestionSearchForm.bind(params("from", day, "to", day), UserRole.USER);
      assertTrue(value.isValid());
      assertEquals(
          LocalDate.parse(day).atStartOfDay().toInstant(ZoneOffset.ofHours(9)),
          value.toRequest().submittedFrom().orElseThrow());
      assertEquals(
          LocalDate.parse(day).atTime(23, 59, 59, 999_000_000).toInstant(ZoneOffset.ofHours(9)),
          value.toRequest().submittedTo().orElseThrow());
    }
    for (String name : List.of("from", "to"))
      for (String day :
          List.of(
              "0000-01-01",
              "2023-02-29",
              "2024-02-30",
              "2024-13-01",
              "2024-01-00",
              "2024-1-01",
              "2024-01-01T00:00",
              "2024-01-01Z",
              "2024-01-01+09:00")) invalid(params(name, day), UserRole.USER);
    assertTrue(
        QuestionSearchForm.bind(params("from", "2024-01-01", "to", "2024-12-31"), UserRole.USER)
            .isValid());
    invalid(params("from", "2024-01-01", "to", "2025-01-01"), UserRole.USER);
    invalid(params("from", "2024-02-01", "to", "2024-01-31"), UserRole.USER);
    assertTrue(QuestionSearchForm.bind(params("from", "2026-10-03"), UserRole.USER).isValid());
    assertTrue(QuestionSearchForm.bind(params("to", "2026-10-03"), UserRole.USER).isValid());
    for (String page : List.of("", "0", "-1", "-2147483648", "0001", "999999")) {
      var form = QuestionSearchForm.bind(params("page", page), UserRole.USER);
      assertTrue(form.isValid());
      assertEquals(page.equals("999999") ? 999999 : 1, form.getPage());
      assertEquals(form.getPage(), form.toRequest().page());
      assertEquals(50, form.toRequest().pageSize());
    }
    for (String page :
        List.of("1000000", "2147483648", "-2147483649", "+1", "1.0", "1e1", "１", "1 1", "-"))
      invalid(params("page", page), UserRole.USER);
  }

  @Test
  void qry004ImmutableListsStatesPages() throws Exception {
    for (UserRole role : UserRole.values())
      for (String state : List.of("ANSWERED", "UNANSWERED", "ERROR"))
        for (int count : List.of(0, 1, 50))
          try (var f = new Fixture()) {
            f.count = count;
            f.total = count;
            var model = new ExtendedModelMap();
            var reply = new MockHttpServletResponse();
            assertEquals(
                "questions/list",
                f.controller.list(params("state", state), actor(role), model, raw(), reply));
            var page = assertInstanceOf(QuestionListViewModel.class, model.get("page"));
            assertEquals(count, page.getRows().size());
            assertEquals(count, page.getRows().stream().map(r -> r.get("id")).distinct().count());
            assertEquals(role == UserRole.ADMIN, page.getFilters().isAdmin());
            assertEquals(role.wireValue(), page.getTopBar().getRole());
            for (var row : page.getRows()) {
              assertEquals(state, row.get("state"));
              assertEquals(
                  Map.of("ANSWERED", "回答済み", "UNANSWERED", "未回答", "ERROR", "エラー").get(state),
                  row.get("stateLabel"));
              assertEquals("reader", row.get("username"));
              assertEquals("2026-10-03 08:58:00", row.get("submittedAt"));
              assertEquals(
                  state.equals("ANSWERED") ? "2026-10-03 08:59:00" : "", row.get("answeredAt"));
              assertThrows(
                  UnsupportedOperationException.class, () -> row.put("summary", "changed"));
            }
            assertThrows(UnsupportedOperationException.class, () -> page.getRows().add(Map.of()));
            assertEquals("QuestionListViewModel[REDACTED]", page.toString());
            f.erased();
          }
    var input = new ArrayList<>(List.of(summary(1, "reader", AnswerState.UNANSWERED, SUBMITTED)));
    var page =
        QuestionListViewModel.success(
            actor(UserRole.USER),
            QuestionSearchForm.bind(params(), UserRole.USER),
            paged(1, 1),
            input);
    input.clear();
    assertEquals(1, page.getRows().size());
  }

  @Test
  void qry005ProjectionDamage() {
    var user = actor(UserRole.USER);
    var form = QuestionSearchForm.bind(params(), UserRole.USER);
    var one = summary(1, "reader", AnswerState.UNANSWERED, SUBMITTED);
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.success(user, form, paged(1, 1), List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.success(user, form, paged(2, 1), List.of(one, one)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                user,
                form,
                paged(1, 1),
                List.of(summary(1, "other", AnswerState.UNANSWERED, SUBMITTED))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                user,
                form,
                paged(2, 1),
                List.of(one, summary(2, "reader", AnswerState.UNANSWERED, SUBMITTED))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                user,
                form,
                paged(2, 1),
                List.of(
                    one, summary(2, "reader", AnswerState.UNANSWERED, SUBMITTED.plusMillis(1)))));
    var longSummary =
        new QuestionSummaryRecord(
            new QuestionId(1),
            RECEIPT,
            "reader",
            "x".repeat(101),
            AnswerState.UNANSWERED,
            SUBMITTED,
            Optional.empty());
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.success(user, form, paged(1, 1), List.of(longSummary)));
    var stateDamage =
        new QuestionSummaryRecord(
            new QuestionId(1),
            RECEIPT,
            "reader",
            "q",
            AnswerState.UNANSWERED,
            SUBMITTED,
            Optional.of(ANSWERED));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionListViewModel.success(user, form, paged(1, 1), List.of(stateDamage)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                user,
                QuestionSearchForm.bind(params("page", "2"), UserRole.USER),
                paged(51, 1),
                List.of(one)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                user,
                QuestionSearchForm.bind(params("state", "bad"), UserRole.USER),
                paged(1, 1),
                List.of(one)));
    assertThrows(IllegalArgumentException.class, () -> QuestionListViewModel.invalid(user, form));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.invalid(
                user, QuestionSearchForm.bind(params("state", "bad"), UserRole.ADMIN)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionListViewModel.success(
                user,
                QuestionSearchForm.bind(params(), UserRole.ADMIN),
                paged(1, 1),
                List.of(one)));
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(null, form, paged(1, 1), List.of(one)));
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(user, null, paged(1, 1), List.of(one)));
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(user, form, null, List.of(one)));
    assertThrows(
        NullPointerException.class,
        () -> QuestionListViewModel.success(user, form, paged(1, 1), null));
    assertThrows(
        NullPointerException.class,
        () ->
            QuestionListViewModel.success(
                user, form, paged(1, 1), Arrays.asList((QuestionSummaryRecord) null)));
    assertThrows(
        NullPointerException.class,
        () ->
            QuestionListViewModel.invalid(
                null, QuestionSearchForm.bind(params("state", "bad"), UserRole.USER)));
    assertThrows(NullPointerException.class, () -> QuestionListViewModel.invalid(user, null));
  }

  private static PagedResponseData paged(int count, int page) {
    return new PagedResponseData(
        page,
        50,
        count,
        Math.max(1, (count + 49) / 50),
        count == 0 ? 0 : (page - 1L) * 50 + 1,
        count == 0 ? 0 : Math.min(page * 50L, count));
  }

  private static QuestionSummaryRecord summary(
      long id, String owner, AnswerState state, Instant submitted) {
    return new QuestionSummaryRecord(
        new QuestionId(id),
        RECEIPT,
        owner,
        "question",
        state,
        submitted,
        state == AnswerState.ANSWERED ? Optional.of(ANSWERED) : Optional.empty());
  }

  private static QuestionDetailResponseData detail(
      long id, String owner, AnswerState state, String answer) {
    return new QuestionDetailResponseData(
        new QuestionId(id),
        RECEIPT,
        owner,
        state,
        "question",
        answer.isEmpty() ? Optional.empty() : Optional.of(answer),
        SUBMITTED,
        state == AnswerState.ANSWERED ? Optional.of(ANSWERED) : Optional.empty());
  }

  @Test
  void qry006DetailWholeWireAndDisplay() throws Exception {
    for (UserRole role : UserRole.values())
      for (String code : List.of("0000", "0200"))
        for (AnswerState state : AnswerState.values())
          for (long id : List.of(1L, 999999999999L))
            try (var f = new Fixture()) {
              f.code = code;
              f.state = state.wireValue();
              f.answer = state == AnswerState.ANSWERED ? "answer<>界" : "";
              var model = new ExtendedModelMap();
              var reply = new MockHttpServletResponse();
              assertEquals(
                  "questions/detail",
                  f.controller.detail(Long.toString(id), actor(role), model, raw(), reply));
              assertEquals(200, reply.getStatus());
              var page = assertInstanceOf(QuestionDetailViewModel.class, model.get("page"));
              assertEquals(id, page.getValues().get("id"));
              assertEquals(
                  id == 1 ? RECEIPT : String.format(Locale.ROOT, "%026d", id),
                  page.getValues().get("receiptId"));
              assertEquals("reader", page.getValues().get("username"));
              assertEquals("question", page.getValues().get("question"));
              assertEquals(
                  Map.of("ANSWERED", "回答済み", "UNANSWERED", "未回答", "ERROR", "エラー")
                      .get(state.wireValue()),
                  page.getValues().get("stateLabel"));
              assertEquals(
                  state == AnswerState.ANSWERED ? "2026-10-03 08:59:00" : "",
                  page.getValues().get("answeredAt"));
              assertEquals(f.answer, page.getValues().get("answer"));
              assertEquals(state == AnswerState.ANSWERED, page.getValues().get("answerAvailable"));
              assertEquals("2026-10-03 08:58:00", page.getValues().get("submittedAt"));
              assertEquals(role == UserRole.ADMIN, page.getValues().get("admin"));
              assertEquals("QuestionDetailViewModel[REDACTED]", page.toString());
              assertThrows(
                  UnsupportedOperationException.class,
                  () -> page.getValues().put("answer", "changed"));
              byte[] expected = request("QSDREQ01", 12, "a".repeat(64), new UUID(0, 1));
              number(expected, 256, 12, id);
              assertArrayEquals(expected, f.requests.getFirst());
              f.erased();
            }
    var user = actor(UserRole.USER);
    var target = new QuestionId(1);
    var data = detail(1, "reader", AnswerState.ANSWERED, "");
    assertEquals("", QuestionDetailViewModel.from(user, target, data).getValues().get("answer"));
    assertEquals(
        true, QuestionDetailViewModel.from(user, target, data).getValues().get("answerAvailable"));
    assertThrows(
        IllegalArgumentException.class,
        () -> QuestionDetailViewModel.from(user, new QuestionId(2), data));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionDetailViewModel.from(
                user, target, detail(1, "other", AnswerState.UNANSWERED, "")));
    assertEquals(
        "other",
        QuestionDetailViewModel.from(
                actor(UserRole.ADMIN), target, detail(1, "other", AnswerState.UNANSWERED, ""))
            .getValues()
            .get("username"));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            QuestionDetailViewModel.from(
                user, target, detail(1, "reader", AnswerState.UNANSWERED, "unexpected answer")));
    assertThrows(
        NullPointerException.class, () -> QuestionDetailViewModel.from(null, target, data));
    assertThrows(NullPointerException.class, () -> QuestionDetailViewModel.from(user, null, data));
    assertThrows(
        NullPointerException.class, () -> QuestionDetailViewModel.from(user, target, null));
    for (String id : List.of("0", "-1", "1000000000000", "bad", "9999999999999999999999"))
      try (var f = new Fixture()) {
        var reply = new MockHttpServletResponse();
        assertNull(f.controller.detail(id, user, new ExtendedModelMap(), raw(), reply));
        assertEquals(404, reply.getStatus());
        assertTrue(f.requests.isEmpty());
      }
    try (var f = new Fixture()) {
      f.replyId = 2;
      var reply = new MockHttpServletResponse();
      assertNull(f.controller.detail("1", user, new ExtendedModelMap(), raw(), reply));
      assertEquals(503, reply.getStatus());
      f.erased();
    }
  }

  @Test
  void qry007AllErrorsWireFaultsAnd0102() throws Exception {
    var codes = List.of("0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001");
    var statuses = List.of(400, 401, 403, 404, 409, 429, 409, 503, 503);
    for (boolean detail : List.of(false, true))
      for (int i = 0; i < codes.size(); i++)
        try (var f = new Fixture()) {
          f.code = codes.get(i);
          var reply = new MockHttpServletResponse();
          assertNull(call(f, detail, reply));
          assertEquals(statuses.get(i), reply.getStatus());
          f.erased();
        }
    for (boolean detail : List.of(false, true))
      for (int offset : List.of(0, 60, 113, 212))
        try (var f = new Fixture()) {
          f.responder =
              (id, request) -> {
                var reply = f.standard(id, request);
                reply[offset] = '?';
                return reply;
              };
          var reply = new MockHttpServletResponse();
          assertNull(call(f, detail, reply));
          assertEquals(503, reply.getStatus());
          f.erased();
        }
    for (boolean detail : List.of(false, true))
      try (var f = new Fixture()) {
        f.responder =
            (id, request) -> {
              throw new JMSRuntimeException("synthetic private diagnostic");
            };
        var reply = new MockHttpServletResponse();
        assertNull(call(f, detail, reply));
        assertEquals(503, reply.getStatus());
        assertFalse(reply.getContentAsString().contains("private"));
        f.erased();
        var failure = new AssertionError("synthetic unknown");
        f.responder =
            (id, request) -> {
              throw failure;
            };
        assertSame(
            failure,
            assertThrows(
                AssertionError.class, () -> call(f, detail, new MockHttpServletResponse())));
        f.erased();
        var client =
            new QuestionWireClient(
                f.wire,
                (id, bytes) -> f.buffers.add(bytes),
                CLOCK,
                () -> new UUID(0, 999),
                Duration.ofMillis(10));
        var controller = new QuestionController(client, f.security.handler);
        var timeout = new MockHttpServletResponse();
        assertNull(
            detail
                ? controller.detail(
                    "1", actor(UserRole.USER), new ExtendedModelMap(), raw(), timeout)
                : controller.list(
                    params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), timeout));
        assertEquals(503, timeout.getStatus());
        f.erased();
      }
    for (boolean detail : List.of(false, true))
      try (var f = new Fixture()) {
        f.code = "0102";
        var reply = new MockHttpServletResponse();
        var request = f.security.mock("GET", detail ? "/questions/1" : "/questions");
        assertNull(
            detail
                ? f.controller.detail(
                    "1", actor(UserRole.USER), new ExtendedModelMap(), request, reply)
                : f.controller.list(
                    params(), actor(UserRole.USER), new ExtendedModelMap(), request, reply));
        assertEquals(302, reply.getStatus());
        assertEquals("/login?session-expired", reply.getRedirectedUrl());
        f.erased();
      }
  }

  private static String call(Fixture f, boolean detail, MockHttpServletResponse reply)
      throws Exception {
    return detail
        ? f.controller.detail("1", actor(UserRole.USER), new ExtendedModelMap(), raw(), reply)
        : f.controller.list(params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), reply);
  }

  @Test
  void qry008MvcEscapeRolesStatesAndMethods() throws Exception {
    for (UserRole role : UserRole.values())
      for (AnswerState state : AnswerState.values())
        try (var f = new Fixture();
            var context = f.mvc()) {
          f.state = state.wireValue();
          f.summary = "<script>alert(1)</script>&界";
          f.answer = "";
          var mvc = MockMvcBuilders.webAppContextSetup(context).build();
          var list =
              mvc.perform(
                      get("/questions")
                          .principal(actor(role))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse();
          assertEquals(200, list.getStatus());
          var dom = Jsoup.parse(list.getContentAsString());
          assertEquals("質問回答", dom.title());
          assertEquals(f.summary, dom.select(".question-summary").text());
          assertEquals(
              Map.of("ANSWERED", "回答済み", "UNANSWERED", "未回答", "ERROR", "エラー")
                  .get(state.wireValue()),
              dom.select(".question-row .state").text());
          assertTrue(dom.select(".question-summary script").isEmpty());
          assertEquals(role == UserRole.ADMIN, !dom.select("input[name=username]").isEmpty());
          assertEquals(role == UserRole.ADMIN, !dom.select(".owner-heading,.owner").isEmpty());
          assertEquals("/questions/1", dom.select(".question-row .detail").attr("href"));
          var detail =
              mvc.perform(
                      get("/questions/1")
                          .principal(actor(role))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse();
          assertEquals(200, detail.getStatus());
          var detailDom = Jsoup.parse(detail.getContentAsString());
          assertEquals("質問回答明細", detailDom.title());
          assertEquals(f.summary, detailDom.select(".question-body").text());
          assertEquals(
              Map.of("ANSWERED", "回答済み", "UNANSWERED", "未回答", "ERROR", "エラー")
                  .get(state.wireValue()),
              detailDom.select(".state").text());
          assertTrue(detailDom.select(".question-body script,.answer-body script").isEmpty());
          assertEquals(
              state == AnswerState.ANSWERED ? "（空の回答）" : "",
              detailDom.select(".answer-body").text());
          assertEquals(role == UserRole.ADMIN, !detailDom.select(".owner").isEmpty());
          assertTrue(detailDom.select("form[method=post] input[name=operation_token]").isEmpty());
          assertEquals(
              200,
              mvc.perform(
                      head("/questions/1")
                          .principal(actor(role))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getStatus());
          assertEquals(
              405,
              mvc.perform(post("/questions/1").principal(actor(role)))
                  .andReturn()
                  .getResponse()
                  .getStatus());
          assertEquals(
              404,
              mvc.perform(get("/questions/abc").principal(actor(role)))
                  .andReturn()
                  .getResponse()
                  .getStatus());
          var invalid =
              mvc.perform(
                      get("/questions")
                          .param("state", "bad")
                          .principal(actor(role))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse();
          assertEquals(400, invalid.getStatus());
          assertFalse(
              Jsoup.parse(invalid.getContentAsString()).select("#question-errors li").isEmpty());
          f.erased();
        }
    try (var f = new Fixture();
        var context = f.mvc()) {
      f.count = 0;
      f.total = 0;
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var empty =
          Jsoup.parse(
              mvc.perform(
                      get("/questions")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("該当するデータはありません", empty.select(".empty-results").text());
      assertTrue(empty.select(".previous,.next,.question-row").isEmpty());
      f.erased();
    }
    try (var f = new Fixture();
        var context = f.mvc()) {
      f.state = "ANSWERED";
      f.answer = "<img src=x onerror=alert(1)>&界";
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var answer =
          Jsoup.parse(
              mvc.perform(
                      get("/questions/1")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(f.answer, answer.select(".answer-body").text());
      assertTrue(answer.select(".answer-body img,.answer-body script").isEmpty());
      f.erased();
    }
  }

  @Test
  void qry009RealSecurityAnd0102() throws Exception {
    for (String role : List.of("USER", "ADMIN"))
      for (String path : List.of("/questions", "/questions/1")) {
        reset();
        var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
        try (var f = new Fixture();
            var web =
                new EmbeddedWebSecurityTest.Server(
                    Files.createTempDirectory(root, "question-http-"),
                    false,
                    db,
                    Optional.of(api.provider),
                    true,
                    true,
                    (mvc, invalid) -> configure(mvc, f.client, invalid))) {
          var loginPage = web.send("GET", "/login", null, null, true);
          String initial =
              loginPage.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
          String token = loginPage.body().substring(6);
          var login =
              web.send(
                  "POST", "/login", initial, "username=reader&password=p&_csrf=" + token, true);
          String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
          var page = web.send("GET", path, cookie, null, true);
          assertEquals(200, page.statusCode());
          assertTrue(page.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
          assertEquals(
              path.equals("/questions") ? "質問回答" : "質問回答明細", Jsoup.parse(page.body()).title());
          var head = web.send("HEAD", path, cookie, null, true);
          assertEquals(200, head.statusCode());
          assertEquals("", head.body());
          assertEquals(302, web.send("GET", path, null, null, true).statusCode());
          f.code = "0102";
          var expired = web.send("GET", path, cookie, null, true);
          assertEquals(302, expired.statusCode());
          assertEquals(
              "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
          assertTrue(
              expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
          int before = f.requests.size();
          assertEquals(302, web.send("GET", path, cookie, null, true).statusCode());
          assertEquals(before, f.requests.size());
          f.erased();
          api.erased();
        }
      }
  }

  @Test
  void qry010ConcurrentTargetsContextsAndMessages() throws Exception {
    try (var f = new Fixture();
        var pool = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 1; i <= 100; i++) {
        final int target = i;
        futures.add(
            pool.submit(
                () -> {
                  var principal =
                      new SessionPrincipal(
                          "reader",
                          UserRole.USER,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", target)),
                          Instant.EPOCH);
                  var model = new ExtendedModelMap();
                  var reply = new MockHttpServletResponse();
                  assertEquals(
                      "questions/detail",
                      f.controller.detail(
                          Integer.toString(target), principal, model, raw(), reply));
                  assertEquals(200, reply.getStatus());
                  assertEquals(
                      (long) target,
                      assertInstanceOf(QuestionDetailViewModel.class, model.get("page"))
                          .getValues()
                          .get("id"));
                  return null;
                }));
      }
      for (var future : futures) future.get(10, TimeUnit.SECONDS);
      assertEquals(100, f.requests.size());
      assertEquals(100, f.requests.stream().map(r -> ascii(r, 24, 36)).distinct().count());
      for (var request : f.requests) {
        long id = Long.parseLong(ascii(request, 256, 12));
        assertEquals(String.format(Locale.ROOT, "%064x", id), ascii(request, 113, 64));
      }
      f.erased();
    }
  }

  @Test
  void qry011FactoryControllerNullAndIntegrity() throws Exception {
    for (AnswerState state : AnswerState.values()) {
      var values =
          QuestionDetailViewModel.from(
              actor(UserRole.ADMIN),
              new QuestionId(1),
              detail(1, "other", state, state == AnswerState.ANSWERED ? "answer" : ""));
      assertEquals(state.wireValue(), values.getValues().get("state"));
      assertEquals("ADMIN", values.getTopBar().getRole());
    }
    var form = QuestionSearchForm.bind(params(), UserRole.ADMIN);
    var older = summary(1, "other", AnswerState.UNANSWERED, SUBMITTED.minusSeconds(1));
    var newer = summary(2, "reader", AnswerState.ANSWERED, SUBMITTED);
    assertEquals(
        2,
        QuestionListViewModel.success(
                actor(UserRole.ADMIN), form, paged(2, 1), List.of(newer, older))
            .getRows()
            .size());
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class, () -> new QuestionController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new QuestionController(f.client, null));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.list(
                  params(),
                  () -> "reader",
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.detail(
                  "1",
                  () -> "reader",
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  null,
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  params(), null, new ExtendedModelMap(), raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  params(), actor(UserRole.USER), null, raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  params(),
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  null,
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.list(
                  params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), null));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  null,
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  "1", null, new ExtendedModelMap(), raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  "1", actor(UserRole.USER), null, raw(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail(
                  "1",
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  null,
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.detail("1", actor(UserRole.USER), new ExtendedModelMap(), raw(), null));
      assertTrue(f.requests.isEmpty());
    }
    for (boolean detail : List.of(false, true))
      try (var f = new Fixture()) {
        f.owner = "other";
        var reply = new MockHttpServletResponse();
        assertNull(call(f, detail, reply));
        assertEquals(503, reply.getStatus());
        f.erased();
      }
    try (var f = new Fixture()) {
      f.summary = "x".repeat(101);
      var reply = new MockHttpServletResponse();
      assertNull(call(f, false, reply));
      assertEquals(503, reply.getStatus());
      f.erased();
    }
    try (var f = new Fixture()) {
      f.responder =
          (id, request) -> {
            var reply = f.standard(id, request);
            number(reply, 280, 9, 9);
            return reply;
          };
      var reply = new MockHttpServletResponse();
      assertNull(call(f, false, reply));
      assertEquals(503, reply.getStatus());
      f.erased();
    }
  }

  @Test
  void qry012PaginationQueryAndOwnerShape() {
    for (UserRole role : UserRole.values()) {
      var input =
          params("keyword", "é &+", "state", "ANSWERED", "from", "2026-10-03", "to", "2026-10-03");
      if (role == UserRole.ADMIN) input.add("username", "reader");
      var form = QuestionSearchForm.bind(input, role);
      var rows = new ArrayList<QuestionSummaryRecord>();
      for (int i = 50; i >= 1; i--) rows.add(summary(i, "reader", AnswerState.ANSWERED, SUBMITTED));
      var first = QuestionListViewModel.success(actor(role), form, paged(51, 1), rows);
      assertTrue(first.getPreviousHref().isEmpty());
      String prefix =
          "/questions?keyword=%C3%A9%20%26%2B&state=ANSWERED&from=2026-10-03&to=2026-10-03"
              + (role == UserRole.ADMIN ? "&username=reader" : "")
              + "&page=";
      assertEquals(prefix + "2", first.getNextHref().orElseThrow());
      input.add("page", "2");
      var second =
          QuestionListViewModel.success(
              actor(role),
              QuestionSearchForm.bind(input, role),
              paged(51, 2),
              List.of(summary(1, "reader", AnswerState.ANSWERED, SUBMITTED)));
      assertEquals(prefix + "1", second.getPreviousHref().orElseThrow());
      assertTrue(second.getNextHref().isEmpty());
      var empty =
          QuestionListViewModel.success(
              actor(role),
              QuestionSearchForm.bind(params("page", "999999"), role),
              paged(0, 1),
              List.of());
      assertTrue(empty.getPreviousHref().isEmpty());
      assertTrue(empty.getNextHref().isEmpty());
      assertEquals(1, empty.getPage().orElseThrow().getTotalPages());
    }
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicLong ids = new AtomicLong();
    final List<byte[]> requests = new CopyOnWriteArrayList<>(),
        buffers = new CopyOnWriteArrayList<>();
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    volatile String code = "0000", state = "", summary = "question", answer = "", owner = "reader";
    volatile int count = 1, total = 1;
    volatile long replyId;
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final QuestionWireClient client =
        new QuestionWireClient(
            wire,
            (id, bytes) -> {
              requests.add(bytes.clone());
              buffers.add(bytes);
              assertTrue(wire.onReply(id, responder.apply(id, bytes)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final QuestionController controller = new QuestionController(client, security.handler);

    byte[] standard(UUID id, byte[] request) {
      boolean detail = ascii(request, 11, 8).equals("QSDREQ01"),
          success = code.equals("0000") || code.equals("0200");
      String selected = detail ? "" : text(request, 576, 12);
      String normalState = state.isEmpty() ? (selected.isEmpty() ? "UNANSWERED" : selected) : state;
      int page =
          detail
              ? 1
              : Math.min(Integer.parseInt(ascii(request, 622, 6)), Math.max(1, (total + 49) / 50));
      int rows = success && !detail ? count : 0;
      byte[] bytes = new byte[detail ? 8608 : 304 + 672 * rows];
      Arrays.fill(bytes, (byte) ' ');
      put(bytes, 0, 8, "SCHBNK01");
      put(bytes, 8, 3, "001");
      put(bytes, 11, 8, detail ? "QSDRSP01" : "QSSRSP01");
      put(bytes, 19, 3, "001");
      put(bytes, 22, 1, "S");
      put(bytes, 23, 1, "S");
      put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
      put(bytes, 60, 36, id.toString());
      put(bytes, 96, 17, "20261003090000000");
      put(bytes, 113, 64, ascii(request, 113, 64));
      number(bytes, 177, 4, 256);
      number(bytes, 181, 6, detail ? 8352 : 48);
      number(bytes, 187, 6, detail ? 0 : 672);
      number(bytes, 193, 6, rows);
      number(bytes, 199, 9, bytes.length);
      put(bytes, 208, 4, code);
      if (detail) {
        number(bytes, 256, 12, 0);
        number(bytes, 8562, 17, 0);
        if (success) {
          long target = replyId == 0 ? Long.parseLong(ascii(request, 256, 12)) : replyId;
          number(bytes, 256, 12, target);
          put(bytes, 268, 26, target == 1 ? RECEIPT : String.format(Locale.ROOT, "%026d", target));
          put(bytes, 294, 64, owner);
          put(bytes, 358, 12, normalState);
          put(bytes, 370, 4096, summary);
          put(bytes, 4466, 4096, answer);
          put(bytes, 8562, 17, "20261003085800000");
          if (normalState.equals("ANSWERED")) put(bytes, 8579, 17, "20261003085900000");
        }
      } else {
        number(bytes, 256, 6, success ? page : 0);
        number(bytes, 262, 3, success ? 50 : 0);
        number(bytes, 265, 9, success ? total : 0);
        number(bytes, 274, 6, success ? Math.max(1, (total + 49) / 50) : 0);
        number(bytes, 280, 9, rows == 0 ? 0 : (page - 1L) * 50 + 1);
        number(bytes, 289, 9, rows == 0 ? 0 : (page - 1L) * 50 + rows);
        String requestedOwner = text(request, 512, 64);
        String normalOwner = requestedOwner.isEmpty() ? owner : requestedOwner;
        String keyword = text(request, 256, 256);
        String normalSummary =
            summary.equals("question") && !keyword.isEmpty() ? "question " + keyword : summary;
        for (int i = 0; i < rows; i++) {
          int at = 304 + 672 * i;
          long target = rows - i;
          number(bytes, at, 12, target);
          put(
              bytes,
              at + 12,
              26,
              target == 1 ? RECEIPT : String.format(Locale.ROOT, "%026d", target));
          put(bytes, at + 38, 64, normalOwner);
          put(bytes, at + 102, 512, normalSummary);
          put(bytes, at + 614, 12, normalState);
          put(bytes, at + 626, 17, "20261003085800000");
          if (normalState.equals("ANSWERED")) put(bytes, at + 643, 17, "20261003085900000");
        }
      }
      return bytes;
    }

    AnnotationConfigWebApplicationContext mvc() {
      var context = new AnnotationConfigWebApplicationContext();
      context.setServletContext(new MockServletContext());
      configure(context, client, security.handler);
      context.refresh();
      return context;
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (var bytes : buffers) assertArrayEquals(new byte[bytes.length], bytes);
    }

    @Override
    public void close() {
      for (var bytes : requests) Arrays.fill(bytes, (byte) 0);
      security.close();
    }
  }

  private static byte[] request(String layout, int length, String context, UUID id) {
    byte[] bytes = new byte[256 + length];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, 8, "SCHBNK01");
    put(bytes, 8, 3, "001");
    put(bytes, 11, 8, layout);
    put(bytes, 19, 3, "001");
    put(bytes, 22, 1, "Q");
    put(bytes, 23, 1, "S");
    put(bytes, 24, 36, id.toString());
    put(bytes, 60, 36, id.toString());
    put(bytes, 96, 17, "20261003090000000");
    put(bytes, 113, 64, context);
    number(bytes, 177, 4, 256);
    number(bytes, 181, 6, length);
    number(bytes, 187, 6, 0);
    number(bytes, 193, 6, 0);
    number(bytes, 199, 9, bytes.length);
    return bytes;
  }

  private static void put(byte[] bytes, int at, int length, String value) {
    byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(encoded.length <= length);
    Arrays.fill(bytes, at, at + length, (byte) ' ');
    System.arraycopy(encoded, 0, bytes, at, encoded.length);
  }

  private static void number(byte[] bytes, int at, int length, long value) {
    put(bytes, at, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }

  private static String ascii(byte[] bytes, int at, int length) {
    return new String(bytes, at, length, StandardCharsets.US_ASCII);
  }

  private static String text(byte[] bytes, int at, int length) {
    return new String(bytes, at, length, StandardCharsets.UTF_8).stripTrailing();
  }
}
