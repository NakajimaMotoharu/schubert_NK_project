package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.head;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationErrorCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.config.NotificationMvcConfiguration;
import dev.codex.schubert.nk.web.controller.NotificationController;
import dev.codex.schubert.nk.web.form.NotificationSearchForm;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.view.NotificationDetailViewModel;
import dev.codex.schubert.nk.web.view.NotificationListViewModel;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** Independent UI224/236 byte/HTTP/DOM oracle, PG-D347/016059/PT-NTF-HTTP001..010. */
class NotificationControllerTest {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-03T00:00:00Z"), ZoneOffset.UTC);
  private static final String RECEIPT = "0123456789ABCDEFGHJKMNPQRS";
  private static WebLogDatabaseFixture db;
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
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
    return new MockHttpServletRequest("GET", "/notifications");
  }

  private static CsrfToken csrf() {
    return new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64));
  }

  private static void configure(
      AnnotationConfigWebApplicationContext context,
      NotificationWireClient client,
      ApiSessionInvalidHandler invalid) {
    context.register(NotificationMvcConfiguration.class);
    context.addBeanFactoryPostProcessor(
        f -> {
          f.registerSingleton("notificationWireClient", client);
          f.registerSingleton("apiSessionInvalidHandler", invalid);
        });
  }

  @Test
  void ntf001IndependentWholeByteAndBothRoles() throws Exception {
    for (UserRole role : UserRole.values())
      for (String code : List.of("0000", "0200"))
        for (int count : List.of(0, 1, 50))
          try (var f = new Fixture()) {
            f.code = code;
            f.count = count;
            f.total = count;
            var model = new ExtendedModelMap();
            var response = new MockHttpServletResponse();
            assertEquals(
                "notifications/list",
                f.controller.list(
                    params("type", "ACCEPTED", "from", "2024-01-01", "to", "2024-12-31"),
                    actor(role),
                    model,
                    raw(),
                    response));
            assertEquals(200, response.getStatus());
            var page = assertInstanceOf(NotificationListViewModel.class, model.get("page"));
            assertEquals(count, page.getRows().size());
            assertEquals(
                count, page.getRows().stream().map(row -> row.get("receiptId")).distinct().count());
            for (var row : page.getRows()) {
              assertEquals("受付通知", row.get("type"));
              assertEquals("2024-01-01 00:00:00", row.get("submittedAt"));
            }
            assertEquals(
                switch (role) {
                  case USER -> "USER";
                  case ADMIN -> "ADMIN";
                },
                page.getTopBar().getRole());
            byte[] expected = new byte[320];
            Arrays.fill(expected, (byte) ' ');
            put(expected, 0, 8, "SCHBNK01");
            put(expected, 8, 3, "001");
            put(expected, 11, 8, "NTSREQ01");
            put(expected, 19, 3, "001");
            put(expected, 22, 1, "Q");
            put(expected, 23, 1, "S");
            put(expected, 24, 36, "00000000-0000-0000-0000-000000000001");
            put(expected, 60, 36, "00000000-0000-0000-0000-000000000001");
            put(expected, 96, 17, "20261003090000000");
            put(expected, 113, 64, "a".repeat(64));
            number(expected, 177, 4, 256);
            number(expected, 181, 6, 64);
            number(expected, 187, 6, 0);
            number(expected, 193, 6, 0);
            number(expected, 199, 9, 320);
            put(expected, 256, 12, "ACCEPTED");
            put(expected, 268, 17, "20240101000000000");
            put(expected, 285, 17, "20241231235959999");
            number(expected, 302, 6, 1);
            number(expected, 308, 3, 50);
            assertArrayEquals(expected, f.requests.getFirst());
            f.erased();
          }
  }

  @Test
  void ntf002DefaultsClosedTypesAndImmutableSnapshot() {
    var form = NotificationSearchForm.bind(Map.of());
    assertTrue(form.isValid());
    assertEquals(1, form.getPage());
    var data = form.toRequest();
    assertEquals(Optional.empty(), data.notificationType());
    assertEquals(Optional.empty(), data.submittedFrom());
    assertEquals(Optional.empty(), data.submittedTo());
    assertEquals(50, data.pageSize());
    for (String type : List.of("ACCEPTED", "COMPLETED", "ERROR"))
      for (String page : List.of("0", "-1", "-2147483648", "0001", "999999")) {
        var value = NotificationSearchForm.bind(params("type", " " + type + " ", "page", page));
        assertTrue(value.isValid());
        assertEquals(
            NotificationType.valueOf(type), value.toRequest().notificationType().orElseThrow());
        assertEquals(page.equals("999999") ? 999999 : 1, value.getPage());
      }
    var input = new HashMap<String, List<String>>();
    var values = new ArrayList<>(List.of("ACCEPTED"));
    input.put("type", values);
    var copy = NotificationSearchForm.bind(input);
    values.set(0, "ERROR");
    input.clear();
    assertEquals("ACCEPTED", copy.getValues().get("type"));
    assertThrows(UnsupportedOperationException.class, () -> copy.getValues().clear());
    assertThrows(UnsupportedOperationException.class, () -> copy.getIssues().put("x", "x"));
    assertEquals("NotificationSearchForm[REDACTED]", copy.toString());
  }

  @Test
  void ntf003StrictDatesInclusive366DayAndYearBounds() {
    var valid = NotificationSearchForm.bind(params("from", "2024-01-01", "to", "2024-12-31"));
    assertTrue(valid.isValid());
    assertEquals(
        Instant.parse("2023-12-31T15:00:00Z"), valid.toRequest().submittedFrom().orElseThrow());
    assertEquals(
        Instant.parse("2024-12-31T14:59:59.999Z"), valid.toRequest().submittedTo().orElseThrow());
    var same = NotificationSearchForm.bind(params("from", "2024-02-29", "to", "2024-02-29"));
    assertTrue(same.isValid());
    assertEquals(
        Instant.parse("2024-02-28T15:00:00Z"), same.toRequest().submittedFrom().orElseThrow());
    assertEquals(
        Instant.parse("2024-02-29T14:59:59.999Z"), same.toRequest().submittedTo().orElseThrow());
    assertFalse(
        NotificationSearchForm.bind(params("from", "2024-01-01", "to", "2025-01-01")).isValid());
    assertFalse(
        NotificationSearchForm.bind(params("from", "2024-01-02", "to", "2024-01-01")).isValid());
    for (String field : List.of("from", "to")) {
      for (String value : List.of("0001-01-01", "9999-12-31", "2024-02-29")) {
        var form = NotificationSearchForm.bind(params(field, value));
        assertTrue(form.isValid());
        assertEquals(field.equals("from"), form.toRequest().submittedFrom().isPresent());
        assertEquals(field.equals("to"), form.toRequest().submittedTo().isPresent());
      }
      for (String value :
          List.of(
              "0000-01-01",
              "10000-01-01",
              "2023-02-29",
              "2024-13-01",
              "2024-01-32",
              "2024-1-1",
              "2024-01-01T00:00",
              "2024-01-01Z",
              "2024-01-01+09:00")) {
        var form = NotificationSearchForm.bind(params(field, value));
        assertFalse(form.isValid());
        assertTrue(form.getIssues().containsKey(field));
        assertThrows(IllegalArgumentException.class, form::toRequest);
      }
    }
  }

  @Test
  void ntf004UnknownOwnerBindingAndNullContracts() throws Exception {
    for (String name : List.of("owner", "username", "role", "context", "unknown", "TYPE", ""))
      try (var f = new Fixture()) {
        var response = new MockHttpServletResponse();
        var model = new ExtendedModelMap();
        assertEquals(
            "notifications/list",
            f.controller.list(
                params(name, "attempted other owner"),
                actor(UserRole.ADMIN),
                model,
                raw(),
                response));
        assertEquals(400, response.getStatus());
        assertTrue(f.requests.isEmpty());
        assertEquals(
            "入力項目を確認してください。",
            ((NotificationListViewModel) model.get("page")).getFilters().getIssues().get("form"));
      }
    for (String name : List.of("type", "from", "to", "page")) {
      for (List<String> list : List.of(List.<String>of(), List.of("a", "b"))) {
        var form = NotificationSearchForm.bind(Map.of(name, list));
        assertFalse(form.isValid());
        assertTrue(form.getIssues().containsKey(name));
      }
      for (String bad : List.of("x\u0000", "x\u007f", "x\u0085", "x\ud800", "x\udfff", "😀"))
        assertFalse(NotificationSearchForm.bind(params(name, bad)).isValid());
    }
    for (String page : List.of("1000000", "2147483648", "-2147483649", "１２", "+1", "1.0"))
      assertFalse(NotificationSearchForm.bind(params("page", page)).isValid());
    assertFalse(NotificationSearchForm.bind(params("type", "UNKNOWN")).isValid());
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(null));
    var nullName = new HashMap<String, List<String>>();
    nullName.put(null, List.of("x"));
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(nullName));
    var nullList = new HashMap<String, List<String>>();
    nullList.put("from", null);
    assertThrows(NullPointerException.class, () -> NotificationSearchForm.bind(nullList));
    assertThrows(
        NullPointerException.class,
        () -> NotificationSearchForm.bind(Map.of("from", Arrays.asList((String) null))));
    try (var f = new Fixture()) {
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
          NullPointerException.class, () -> new NotificationController(null, f.security.handler));
      assertThrows(NullPointerException.class, () -> new NotificationController(f.client, null));
      assertTrue(f.requests.isEmpty());
    }
  }

  @Test
  void ntf005AllErrorsAndClosedWireFailures() throws Exception {
    var codes = List.of("0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001");
    var statuses = List.of(400, 401, 403, 404, 409, 429, 409, 503, 503);
    for (int i = 0; i < codes.size(); i++)
      try (var f = new Fixture()) {
        f.code = codes.get(i);
        var response = new MockHttpServletResponse();
        assertNull(
            f.controller.list(
                params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
        assertEquals(statuses.get(i), response.getStatus());
        f.erased();
      }
    for (int offset : List.of(0, 60, 113, 212, 304 + 609))
      try (var f = new Fixture()) {
        f.responder =
            (id, request) -> {
              var reply = f.standard(id, request);
              reply[offset] = (byte) 'x';
              return reply;
            };
        var response = new MockHttpServletResponse();
        assertNull(
            f.controller.list(
                params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
        assertEquals(503, response.getStatus());
        f.erased();
      }
    try (var f = new Fixture()) {
      f.responder =
          (id, request) -> {
            throw new JMSRuntimeException("synthetic secret canary");
          };
      var response = new MockHttpServletResponse();
      assertNull(
          f.controller.list(
              params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
      assertEquals(503, response.getStatus());
      assertFalse(response.getContentAsString().contains("canary"));
      f.erased();
      f.responder =
          (id, request) -> {
            throw new AssertionError("unexpected error");
          };
      assertThrows(
          AssertionError.class,
          () ->
              f.controller.list(
                  params(),
                  actor(UserRole.USER),
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      f.erased();
    }
    try (var f = new Fixture()) {
      var client =
          new NotificationWireClient(
              f.wire,
              (id, bytes) -> f.buffers.add(bytes),
              CLOCK,
              () -> new UUID(0, 999),
              Duration.ofMillis(10));
      var controller = new NotificationController(client, f.security.handler);
      var response = new MockHttpServletResponse();
      assertNull(
          controller.list(params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
      assertEquals(503, response.getStatus());
      f.erased();
    }
  }

  private static NotificationRecord record(
      long id,
      Instant updated,
      NotificationType type,
      NotificationState state,
      String summary,
      boolean deleted) {
    return new NotificationRecord(
        new NotificationId(id), RECEIPT, type, state, CLOCK.instant(), updated, summary, deleted);
  }

  private static NotificationListViewModel page(List<NotificationRecord> rows) {
    int size = rows.size();
    return NotificationListViewModel.success(
        actor(UserRole.USER),
        NotificationSearchForm.bind(Map.of()),
        new PagedResponseData(1, 50, size, 1, size == 0 ? 0 : 1, size),
        rows);
  }

  @Test
  void ntf006ProjectionCountOrderingAndIndependentFactoryNegatives() throws Exception {
    var a =
        record(
            2,
            CLOCK.instant(),
            NotificationType.ACCEPTED,
            NotificationState.RECEIVED,
            "question",
            false);
    var b =
        record(
            1,
            CLOCK.instant(),
            NotificationType.ACCEPTED,
            NotificationState.RECEIVED,
            "question",
            false);
    assertEquals(
        List.of(2L, 1L), page(List.of(a, b)).getRows().stream().map(row -> row.get("id")).toList());
    assertThrows(IllegalArgumentException.class, () -> page(List.of(b, a)));
    assertThrows(IllegalArgumentException.class, () -> page(List.of(a, a)));
    var later =
        record(
            1,
            CLOCK.instant().plusMillis(1),
            NotificationType.ACCEPTED,
            NotificationState.RECEIVED,
            "q",
            false);
    assertThrows(IllegalArgumentException.class, () -> page(List.of(a, later)));
    assertEquals(2, page(List.of(later, a)).getRows().size());
    for (var bad :
        List.of(
            record(
                1, CLOCK.instant(), NotificationType.ERROR, NotificationState.RECEIVED, "q", false),
            record(
                1,
                CLOCK.instant(),
                NotificationType.ACCEPTED,
                NotificationState.RECEIVED,
                "q".repeat(101),
                false),
            record(
                1,
                CLOCK.instant(),
                NotificationType.ACCEPTED,
                NotificationState.RECEIVED,
                "not deleted caption",
                true))) assertThrows(IllegalArgumentException.class, () -> page(List.of(bad)));
    var form = NotificationSearchForm.bind(Map.of());
    var badForm = NotificationSearchForm.bind(params("owner", "other"));
    var data = new PagedResponseData(1, 50, 1, 1, 1, 1);
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.success(actor(UserRole.USER), form, data, List.of()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            NotificationListViewModel.success(
                actor(UserRole.USER),
                form,
                new PagedResponseData(2, 50, 51, 2, 51, 51),
                List.of(a)));
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.success(actor(UserRole.USER), badForm, data, List.of(a)));
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationListViewModel.invalid(actor(UserRole.USER), form));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(null, form, data, List.of(a)));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(actor(UserRole.USER), null, data, List.of(a)));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(actor(UserRole.USER), form, null, List.of(a)));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.success(actor(UserRole.USER), form, data, null));
    assertThrows(
        NullPointerException.class,
        () ->
            NotificationListViewModel.success(
                actor(UserRole.USER), form, data, Arrays.asList((NotificationRecord) null)));
    assertThrows(
        NullPointerException.class,
        () -> NotificationListViewModel.invalid(actor(UserRole.USER), null));
    for (int kind = 0; kind < 5; kind++)
      try (var f = new Fixture()) {
        if (kind == 0) f.count = 0;
        if (kind == 1) f.replyPage = 2;
        if (kind == 2) f.summary = "q".repeat(101);
        if (kind == 3) f.deleted = true;
        if (kind == 4) f.type = "ERROR";
        var response = new MockHttpServletResponse();
        assertNull(
            f.controller.list(
                params(), actor(UserRole.USER), new ExtendedModelMap(), raw(), response));
        assertEquals(503, response.getStatus());
        f.erased();
      }
  }

  @Test
  void ntf007AllStatesTypesSummaryAndImmutableDisplay() {
    for (NotificationState state : NotificationState.values())
      for (boolean deleted : List.of(true, false)) {
        NotificationType type =
            state == NotificationState.ERROR
                ? NotificationType.ERROR
                : state == NotificationState.COMPLETED
                    ? NotificationType.COMPLETED
                    : NotificationType.ACCEPTED;
        String label =
            type == NotificationType.ERROR
                ? "エラー通知"
                : type == NotificationType.COMPLETED ? "処理済通知" : "受付通知";
        var page =
            page(
                List.of(
                    record(
                        42,
                        CLOCK.instant(),
                        type,
                        state,
                        deleted ? "削除済み" : "😀".repeat(100),
                        deleted)));
        var row = page.getRows().getFirst();
        assertEquals(label, row.get("type"));
        assertEquals(state.wireValue(), row.get("state"));
        assertEquals(RECEIPT, row.get("receiptId"));
        assertEquals(deleted ? "削除済み" : "😀".repeat(100), row.get("summary"));
        assertEquals(deleted, row.get("deleted"));
        assertEquals("2026-10-03 09:00:00", row.get("submittedAt"));
        assertEquals("2026-10-03 09:00:00", row.get("lastUpdatedAt"));
        assertEquals("/notifications/42", row.get("detailHref"));
        assertEquals(42L, row.get("id"));
        assertThrows(UnsupportedOperationException.class, () -> row.clear());
        assertThrows(UnsupportedOperationException.class, () -> page.getRows().clear());
        assertEquals("NotificationListViewModel[REDACTED]", page.toString());
        assertFalse(row.toString().contains("a".repeat(64)));
      }
    var invalid =
        NotificationListViewModel.invalid(
            actor(UserRole.ADMIN), NotificationSearchForm.bind(params("owner", "other")));
    assertTrue(invalid.getPage().isEmpty());
    assertTrue(invalid.getRows().isEmpty());
    assertTrue(invalid.getPreviousHref().isEmpty());
    assertTrue(invalid.getNextHref().isEmpty());
    var empty = page(List.of());
    assertTrue(empty.getRows().isEmpty());
    assertTrue(empty.getPage().orElseThrow().isEmpty());
    assertTrue(empty.getPreviousHref().isEmpty());
    assertTrue(empty.getNextHref().isEmpty());
  }

  @Test
  void ntf008MvcFiltersPaginationAndSafeDom() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var result =
          mvc.perform(
                  get("/notifications")
                      .principal(actor(UserRole.USER))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString());
      assertEquals("通知", dom.title());
      assertEquals(1, dom.select(".notification-row").size());
      assertEquals("/notifications/1", dom.select(".detail").attr("href"));
      assertEquals("2026-10-03 09:00:00", dom.select(".submitted-at").text());
      assertEquals("受付通知", dom.select(".notification-row .type").text());
      assertEquals(
          List.of("", "ACCEPTED", "COMPLETED", "ERROR"),
          dom.select("select[name=type] option").eachAttr("value"));
      assertEquals(2, dom.select("input[type=date]").size());
      assertTrue(
          dom.select("input[name=owner],input[name=username],input[name=role],input[name=context]")
              .isEmpty());
      assertEquals(1, dom.select("input[name=_csrf]").size());
      assertEquals(
          List.of("/", "/notifications"), dom.select(".topbar .nav-links a").eachAttr("href"));
      assertFalse(result.getResponse().getContentAsString().contains("a".repeat(64)));
      assertEquals(
          200,
          mvc.perform(
                  head("/notifications")
                      .principal(actor(UserRole.USER))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn()
              .getResponse()
              .getStatus());
      assertEquals(
          405,
          mvc.perform(post("/notifications").principal(actor(UserRole.USER)))
              .andReturn()
              .getResponse()
              .getStatus());
      f.count = 0;
      f.total = 0;
      dom =
          Jsoup.parse(
              mvc.perform(
                      get("/notifications")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("該当するデータはありません", dom.select(".empty-results").text());
      assertTrue(dom.select(".notification-row,.previous,.next").isEmpty());
      f.count = 50;
      f.total = 51;
      f.summary = "<img src=x onerror=alert(1)>";
      dom =
          Jsoup.parse(
              mvc.perform(
                      get("/notifications")
                          .param("type", "ACCEPTED")
                          .param("from", "2024-01-01")
                          .param("to", "2024-12-31")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals(50, dom.select(".notification-row").size());
      assertEquals(50, dom.select(".receipt").eachText().stream().distinct().count());
      assertEquals(
          Set.of("2024-01-01 00:00:00"), new HashSet<>(dom.select(".submitted-at").eachText()));
      assertTrue(dom.select(".notification-row img,.notification-row script").isEmpty());
      assertEquals(f.summary, dom.select(".notification-summary").first().text());
      assertEquals(
          "/notifications?type=ACCEPTED&from=2024-01-01&to=2024-12-31&page=2",
          dom.select(".next").attr("href"));
      f.count = 1;
      f.replyPage = 2;
      dom =
          Jsoup.parse(
              mvc.perform(
                      get("/notifications")
                          .param("page", "999999")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getContentAsString());
      assertEquals("51 notifications / page 2 of 2", dom.select(".count").text());
      assertEquals("/notifications?type=&from=&to=&page=1", dom.select(".previous").attr("href"));
      assertTrue(dom.select(".next").isEmpty());
      int before = f.requests.size();
      result =
          mvc.perform(
                  get("/notifications")
                      .param("owner", "other")
                      .principal(actor(UserRole.ADMIN))
                      .requestAttr(CsrfToken.class.getName(), csrf()))
              .andReturn();
      assertEquals(400, result.getResponse().getStatus());
      assertEquals(before, f.requests.size());
      assertEquals(
          "入力項目を確認してください。",
          Jsoup.parse(result.getResponse().getContentAsString()).select("#error-form").text());
      f.erased();
    }
    assertTrue(
        Files.readString(
                Path.of(
                    System.getProperty("nk.pt.repository"),
                    "src/schubert-nk-web/src/main/resources/static/css/schubert.css"))
            .contains(".notification-page .notification-summary { white-space: pre-wrap; }"));
  }

  @Test
  void ntf009RealSecurityBothRolesAnd0102() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var f = new Fixture();
          var server =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "notification-http-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        assertEquals(302, server.send("GET", "/notifications", null, null, true).statusCode());
        assertTrue(f.requests.isEmpty());
        var first = server.send("GET", "/login", null, null, true);
        String initial = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var login =
            server.send(
                "POST",
                "/login",
                initial,
                "_csrf=" + first.body().substring(6) + "&username=reader&password=p",
                true);
        assertEquals(302, login.statusCode());
        String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var page = server.send("GET", "/notifications", cookie, null, true);
        assertEquals(200, page.statusCode());
        assertTrue(page.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
        var head = server.send("HEAD", "/notifications", cookie, null, true);
        assertEquals(200, head.statusCode());
        assertEquals("", head.body());
        int before = f.requests.size();
        assertEquals(
            400, server.send("GET", "/notifications?owner=other", cookie, null, true).statusCode());
        assertEquals(before, f.requests.size());
        f.code = "0102";
        var expired = server.send("GET", "/notifications", cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        assertEquals(before + 1, f.requests.size());
        assertEquals(302, server.send("GET", "/notifications", cookie, null, true).statusCode());
        assertEquals(before + 1, f.requests.size());
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void ntf010ConcurrentQueryContextAndRoleIsolation() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var futures = new ArrayList<Future<?>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        futures.add(
            executor.submit(
                () -> {
                  var actor =
                      new SessionPrincipal(
                          "reader" + n,
                          n % 2 == 0 ? UserRole.USER : UserRole.ADMIN,
                          AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n + 1)),
                          Instant.EPOCH);
                  var model = new ExtendedModelMap();
                  String type = n % 2 == 0 ? "ACCEPTED" : "ERROR";
                  assertEquals(
                      "notifications/list",
                      f.controller.list(
                          params("type", type),
                          actor,
                          model,
                          raw(),
                          new MockHttpServletResponse()));
                  var page = (NotificationListViewModel) model.get("page");
                  assertEquals(type, page.getFilters().getValues().get("type"));
                  assertEquals(
                      type.equals("ERROR") ? "エラー通知" : "受付通知",
                      page.getRows().getFirst().get("type"));
                  assertEquals("reader" + n, page.getTopBar().getUsername());
                  return null;
                }));
      }
      for (var future : futures) future.get(15, TimeUnit.SECONDS);
      assertEquals(100, f.requests.size());
      assertEquals(100, f.requests.stream().map(bytes -> ascii(bytes, 24, 36)).distinct().count());
      for (int i = 0; i < 100; i++) {
        String context = String.format(Locale.ROOT, "%064x", i + 1);
        var sent =
            f.requests.stream().filter(bytes -> ascii(bytes, 113, 64).equals(context)).toList();
        assertEquals(1, sent.size());
        assertEquals(
            i % 2 == 0 ? "ACCEPTED" : "ERROR", ascii(sent.getFirst(), 256, 12).stripTrailing());
      }
      f.erased();
    }
  }

  @Test
  void detail001BothRolesStatesAndIndependentWholeRequest() throws Exception {
    for (UserRole role : UserRole.values())
      for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED"))
        for (long target : List.of(1L, 999999999999L))
          try (var f = new Fixture()) {
            f.detailState = state;
            var model = new ExtendedModelMap();
            var reply = new MockHttpServletResponse();
            assertEquals(
                "notifications/detail",
                f.controller.detail(Long.toString(target), actor(role), model, raw(), reply));
            assertEquals(200, reply.getStatus());
            var page = assertInstanceOf(NotificationDetailViewModel.class, model.get("page"));
            assertEquals(target, page.getValues().get("id"));
            assertEquals(state, page.getValues().get("state"));
            assertEquals(
                switch (role) {
                  case USER -> "USER";
                  case ADMIN -> "ADMIN";
                },
                page.getTopBar().getRole());
            byte[] expected = new byte[268];
            Arrays.fill(expected, (byte) ' ');
            put(expected, 0, 8, "SCHBNK01");
            put(expected, 8, 3, "001");
            put(expected, 11, 8, "NTDREQ01");
            put(expected, 19, 3, "001");
            put(expected, 22, 1, "Q");
            put(expected, 23, 1, "S");
            put(expected, 24, 36, "00000000-0000-0000-0000-000000000001");
            put(expected, 60, 36, "00000000-0000-0000-0000-000000000001");
            put(expected, 96, 17, "20261003090000000");
            put(expected, 113, 64, "a".repeat(64));
            number(expected, 177, 4, 256);
            number(expected, 181, 6, 12);
            number(expected, 187, 6, 0);
            number(expected, 193, 6, 0);
            number(expected, 199, 9, 268);
            number(expected, 256, 12, target);
            assertArrayEquals(expected, f.requests.getFirst());
            f.erased();
          }
    try (var f = new Fixture()) {
      f.code = "0200";
      assertEquals(
          "notifications/detail",
          f.controller.detail(
              "1",
              actor(UserRole.USER),
              new ExtendedModelMap(),
              raw(),
              new MockHttpServletResponse()));
      f.erased();
    }
  }

  @Test
  void detail002StateDatesDeletedAndEmptyAnswerProjection() {
    var labels =
        Map.of(
            "RECEIVED",
            "受付中",
            "PROCESSING",
            "処理中",
            "COMPLETED",
            "処理完了",
            "ERROR",
            "エラー",
            "CANCELLED",
            "取消済み");
    for (NotificationState state : NotificationState.values())
      for (boolean deleted : List.of(false, true)) {
        var page =
            NotificationDetailViewModel.from(
                actor(UserRole.USER), new NotificationId(1), detailData(1, state, deleted, ""));
        var values = page.getValues();
        assertEquals(labels.get(state.wireValue()), values.get("stateLabel"));
        assertEquals("2026-10-03 08:58:00", values.get("submittedAt"));
        assertEquals(deleted, values.get("deleted"));
        assertEquals(deleted ? "" : "question", values.get("question"));
        assertEquals(
            state == NotificationState.COMPLETED && !deleted, values.get("answerAvailable"));
        assertEquals(
            state == NotificationState.COMPLETED && !deleted ? "/questions/1" : "",
            values.get("questionHref"));
        assertEquals("", values.get("answer"));
        assertEquals(
            state == NotificationState.ERROR ? "PROCESS_FAILED" : "", values.get("errorCode"));
        assertEquals("NotificationDetailViewModel[REDACTED]", page.toString());
        assertThrows(UnsupportedOperationException.class, () -> values.put("id", 2L));
      }
    var answered =
        NotificationDetailViewModel.from(
            actor(UserRole.ADMIN),
            new NotificationId(1),
            detailData(1, NotificationState.COMPLETED, false, "answer"));
    assertEquals("answer", answered.getValues().get("answer"));
  }

  @Test
  void detail003NullTargetsAndProjectionDisagreement() throws Exception {
    var data = detailData(1, NotificationState.RECEIVED, false, "");
    assertThrows(
        NullPointerException.class,
        () -> NotificationDetailViewModel.from(null, new NotificationId(1), data));
    assertThrows(
        NullPointerException.class,
        () -> NotificationDetailViewModel.from(actor(UserRole.USER), null, data));
    assertThrows(
        NullPointerException.class,
        () -> NotificationDetailViewModel.from(actor(UserRole.USER), new NotificationId(1), null));
    assertThrows(
        IllegalArgumentException.class,
        () -> NotificationDetailViewModel.from(actor(UserRole.USER), new NotificationId(2), data));
    try (var f = new Fixture()) {
      for (String bad : List.of("0", "-1", "1000000000000", "abc", "99999999999999999999")) {
        var reply = new MockHttpServletResponse();
        assertNull(
            f.controller.detail(bad, actor(UserRole.USER), new ExtendedModelMap(), raw(), reply));
        assertEquals(404, reply.getStatus());
      }
      assertTrue(f.requests.isEmpty());
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
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.detail(
                  "1",
                  () -> "foreign",
                  new ExtendedModelMap(),
                  raw(),
                  new MockHttpServletResponse()));
      f.detailReplyId = 2;
      var reply = new MockHttpServletResponse();
      assertNull(
          f.controller.detail("1", actor(UserRole.USER), new ExtendedModelMap(), raw(), reply));
      assertEquals(503, reply.getStatus());
      f.erased();
    }
  }

  @Test
  void detail004ErrorsMalformedAndUnknownTransport() throws Exception {
    var codes = List.of("0100", "0101", "0103", "0104", "0105", "0106", "0107", "9000", "9001");
    var statuses = List.of(400, 401, 403, 404, 409, 429, 409, 503, 503);
    for (int i = 0; i < codes.size(); i++)
      try (var f = new Fixture()) {
        f.code = codes.get(i);
        var reply = new MockHttpServletResponse();
        assertNull(
            f.controller.detail("1", actor(UserRole.USER), new ExtendedModelMap(), raw(), reply));
        assertEquals(statuses.get(i), reply.getStatus());
        f.erased();
      }
    try (var f = new Fixture()) {
      f.responder =
          (id, input) -> {
            var bytes = f.standard(id, input);
            put(bytes, 60, 36, new UUID(2, 2).toString());
            return bytes;
          };
      var reply = new MockHttpServletResponse();
      assertNull(
          f.controller.detail("1", actor(UserRole.USER), new ExtendedModelMap(), raw(), reply));
      assertEquals(503, reply.getStatus());
      f.erased();
      var unknown = new AssertionError("unknown detail transport");
      f.responder =
          (id, input) -> {
            throw unknown;
          };
      assertSame(
          unknown,
          assertThrows(
              AssertionError.class,
              () ->
                  f.controller.detail(
                      "1",
                      actor(UserRole.USER),
                      new ExtendedModelMap(),
                      raw(),
                      new MockHttpServletResponse())));
      f.erased();
    }
  }

  @Test
  void detail005SafeStateDomAndHead() throws Exception {
    for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED"))
      for (boolean deleted : List.of(false, true))
        try (var f = new Fixture();
            var context = f.mvc()) {
          f.detailState = state;
          f.deleted = deleted;
          f.summary = "<script>alert(1)</script> question";
          var mvc = MockMvcBuilders.webAppContextSetup(context).build();
          var result =
              mvc.perform(
                      get("/notifications/1")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn();
          assertEquals(200, result.getResponse().getStatus());
          var dom = Jsoup.parse(result.getResponse().getContentAsString());
          assertEquals("通知明細", dom.title());
          assertEquals("2026-10-03 08:58:00", dom.select(".submitted-at").text());
          assertTrue(dom.select(".question-body script,.answer-body script").isEmpty());
          assertEquals(deleted ? "" : f.summary, dom.select(".question-body").text());
          assertEquals(deleted ? "質問・回答は削除済みです。" : "", dom.select(".deleted").text());
          boolean answer = state.equals("COMPLETED") && !deleted;
          assertEquals(answer ? "（空の回答）" : "", dom.select(".answer-body").text());
          assertEquals(answer ? "/questions/1" : "", dom.select(".question-detail").attr("href"));
          assertEquals(
              state.equals("ERROR") ? "PROCESS_FAILED" : "", dom.select(".error-code").text());
          assertEquals(
              state.equals("CANCELLED") ? "2026-10-03 08:59:00" : "",
              dom.select(".cancelled-at").text());
          assertTrue(dom.select("form[method=post] input[name=operation_token]").isEmpty());
          assertEquals(
              200,
              mvc.perform(
                      head("/notifications/1")
                          .principal(actor(UserRole.USER))
                          .requestAttr(CsrfToken.class.getName(), csrf()))
                  .andReturn()
                  .getResponse()
                  .getStatus());
          assertEquals(
              503,
              mvc.perform(post("/notifications/1").principal(actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getStatus());
          assertEquals(
              404,
              mvc.perform(get("/notifications/abc").principal(actor(UserRole.USER)))
                  .andReturn()
                  .getResponse()
                  .getStatus());
          f.erased();
        }
  }

  @Test
  void detail006RealSecurityAnd0102() throws Exception {
    for (String role : List.of("USER", "ADMIN")) {
      reset();
      var api = new SessionFormLoginTest.Api("0000", role, "0000", 0);
      try (var f = new Fixture();
          var web =
              new EmbeddedWebSecurityTest.Server(
                  Files.createTempDirectory(root, "notification-detail-http-"),
                  false,
                  db,
                  Optional.of(api.provider),
                  true,
                  true,
                  (mvc, invalid) -> configure(mvc, f.client, invalid))) {
        var loginPage = web.send("GET", "/login", null, null, true);
        String initial =
            loginPage.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        String csrf = loginPage.body().substring(6);
        var login =
            web.send("POST", "/login", initial, "username=reader&password=p&_csrf=" + csrf, true);
        String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var page = web.send("GET", "/notifications/1", cookie, null, true);
        assertEquals(200, page.statusCode());
        assertTrue(page.headers().firstValue("cache-control").orElseThrow().contains("no-store"));
        assertEquals("通知明細", Jsoup.parse(page.body()).title());
        var head = web.send("HEAD", "/notifications/1", cookie, null, true);
        assertEquals(200, head.statusCode());
        assertEquals("", head.body());
        assertEquals(302, web.send("GET", "/notifications/1", null, null, true).statusCode());
        f.code = "0102";
        var expired = web.send("GET", "/notifications/1", cookie, null, true);
        assertEquals(302, expired.statusCode());
        assertEquals(
            "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
        assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
        int count = f.requests.size();
        assertEquals(302, web.send("GET", "/notifications/1", cookie, null, true).statusCode());
        assertEquals(count, f.requests.size());
        f.erased();
        api.erased();
      }
    }
  }

  @Test
  void detail007ConcurrentIndependentTargetsAndContexts() throws Exception {
    try (var f = new Fixture();
        var executor = Executors.newFixedThreadPool(8)) {
      var tasks = new ArrayList<Callable<Void>>();
      for (int i = 1; i <= 100; i++) {
        int n = i;
        tasks.add(
            () -> {
              var actor =
                  new SessionPrincipal(
                      "reader" + n,
                      n % 2 == 0 ? UserRole.USER : UserRole.ADMIN,
                      AuthenticationContext.of(String.format(Locale.ROOT, "%064x", n)),
                      Instant.EPOCH);
              var model = new ExtendedModelMap();
              assertEquals(
                  "notifications/detail",
                  f.controller.detail(
                      Integer.toString(n), actor, model, raw(), new MockHttpServletResponse()));
              var page = (NotificationDetailViewModel) model.get("page");
              assertEquals((long) n, page.getValues().get("id"));
              assertEquals("reader" + n, page.getTopBar().getUsername());
              return null;
            });
      }
      for (var future : executor.invokeAll(tasks)) future.get(15, TimeUnit.SECONDS);
      assertEquals(100, f.requests.size());
      assertEquals(100, f.requests.stream().map(b -> ascii(b, 24, 36)).distinct().count());
      for (var bytes : f.requests)
        assertEquals(
            Long.parseLong(ascii(bytes, 256, 12)),
            Long.parseUnsignedLong(ascii(bytes, 113, 64), 16));
      f.erased();
    }
  }

  @Test
  void detail008DeletedAnswerRejectedAtAllBoundaries() throws Exception {
    var invalid =
        new NotificationDetailResponseData(
            new NotificationId(1),
            RECEIPT,
            NotificationType.COMPLETED,
            NotificationState.COMPLETED,
            Instant.EPOCH,
            Optional.of(Instant.EPOCH),
            Optional.of(Instant.EPOCH),
            Optional.empty(),
            Optional.empty(),
            true,
            Optional.empty(),
            Optional.of("must not survive deletion"),
            Optional.empty(),
            Optional.empty(),
            Optional.empty());
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadSemanticValidator.validate(
                new TypedPayloadValues(new LayoutId("NTDRSP01"), invalid, List.of())));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadCodec.standard()
                .encode(
                    PayloadTypeCatalog.encode(
                        new TypedPayloadValues(new LayoutId("NTDRSP01"), invalid, List.of())),
                    ResultCode.SUCCESS));
    try (var f = new Fixture()) {
      f.detailState = "COMPLETED";
      f.deleted = true;
      f.answer = "must not survive deletion";
      f.deletedAnswer = true;
      var reply = new MockHttpServletResponse();
      assertNull(
          f.controller.detail("1", actor(UserRole.USER), new ExtendedModelMap(), raw(), reply));
      assertEquals(503, reply.getStatus());
      f.erased();
      var request = f.requests.getFirst();
      var bytes = f.standard(new UUID(0, 1), request);
      assertThrows(
          LayoutValidationException.class,
          () ->
              PayloadTypeCatalog.decode(
                  PayloadCodec.standard()
                      .decode(
                          new LayoutId("NTDRSP01"),
                          Arrays.copyOfRange(bytes, 256, bytes.length),
                          List.of(),
                          ResultCode.SUCCESS)));
      f.deletedAnswer = false;
      assertEquals(
          "notifications/detail",
          f.controller.detail(
              "1",
              actor(UserRole.USER),
              new ExtendedModelMap(),
              raw(),
              new MockHttpServletResponse()));
      f.erased();
    }
  }

  private static NotificationDetailResponseData detailData(
      long id, NotificationState state, boolean deleted, String answer) {
    var at = Instant.parse("2026-10-02T23:58:00Z");
    boolean started =
        Set.of(NotificationState.PROCESSING, NotificationState.COMPLETED, NotificationState.ERROR)
            .contains(state);
    return new NotificationDetailResponseData(
        new NotificationId(id),
        RECEIPT,
        state == NotificationState.COMPLETED
            ? NotificationType.COMPLETED
            : state == NotificationState.ERROR ? NotificationType.ERROR : NotificationType.ACCEPTED,
        state,
        at,
        started ? Optional.of(at.plusSeconds(60)) : Optional.empty(),
        state == NotificationState.COMPLETED ? Optional.of(at.plusSeconds(90)) : Optional.empty(),
        state == NotificationState.ERROR ? Optional.of(at.plusSeconds(90)) : Optional.empty(),
        state == NotificationState.CANCELLED ? Optional.of(at.plusSeconds(60)) : Optional.empty(),
        deleted,
        deleted ? Optional.empty() : Optional.of("question"),
        state == NotificationState.COMPLETED && !deleted ? Optional.of(answer) : Optional.empty(),
        state == NotificationState.ERROR
            ? Optional.of(NotificationErrorCode.PROCESS_FAILED)
            : Optional.empty(),
        state == NotificationState.ERROR ? Optional.of("処理を完了できませんでした。") : Optional.empty(),
        deleted ? Optional.empty() : Optional.of(new QuestionId(id)));
  }

  private static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicLong ids = new AtomicLong();
    final List<byte[]> requests = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    volatile String code = "0000";
    volatile String type = "ACCEPTED";
    volatile String state = "RECEIVED";
    volatile String summary = "question";
    volatile int count = 1;
    volatile int total = 1;
    volatile int replyPage = 1;
    volatile boolean deleted;
    volatile String detailState = "RECEIVED";
    volatile String answer = "";
    volatile long detailReplyId;
    volatile boolean deletedAnswer;
    volatile BiFunction<UUID, byte[], byte[]> responder = this::standard;
    final NotificationWireClient client =
        new NotificationWireClient(
            wire,
            (id, bytes) -> {
              requests.add(bytes.clone());
              buffers.add(bytes);
              assertTrue(wire.onReply(id, responder.apply(id, bytes)));
            },
            CLOCK,
            () -> new UUID(0, ids.incrementAndGet()),
            Duration.ofSeconds(1));
    final NotificationController controller = new NotificationController(client, security.handler);

    byte[] standard(UUID id, byte[] request) {
      if (ascii(request, 11, 8).equals("NTDREQ01")) return detailResponse(id, request);
      // BUG560: only successful normal fixtures follow literal UI query conditions.
      // Explicit type/state overrides below remain intentional inconsistent negative replies.
      String requestedType = ascii(request, 256, 12).stripTrailing();
      String normalType = requestedType.isEmpty() ? "ACCEPTED" : requestedType;
      String normalState =
          normalType.equals("ERROR")
              ? "ERROR"
              : normalType.equals("COMPLETED") ? "COMPLETED" : "RECEIVED";
      String from = ascii(request, 268, 17).stripTrailing();
      String to = ascii(request, 285, 17).stripTrailing();
      String submitted = !from.isEmpty() ? from : !to.isEmpty() ? to : "20261003090000000";
      return response(
          id,
          ascii(request, 113, 64),
          code,
          replyPage,
          count,
          total,
          type.equals("ACCEPTED") ? normalType : type,
          state.equals("RECEIVED") ? normalState : state,
          submitted,
          summary,
          deleted);
    }

    byte[] detailResponse(UUID id, byte[] request) {
      boolean success = code.equals("0000") || code.equals("0200");
      byte[] bytes = new byte[9152];
      Arrays.fill(bytes, (byte) ' ');
      put(bytes, 0, 8, "SCHBNK01");
      put(bytes, 8, 3, "001");
      put(bytes, 11, 8, "NTDRSP01");
      put(bytes, 19, 3, "001");
      put(bytes, 22, 1, "S");
      put(bytes, 23, 1, "S");
      put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
      put(bytes, 60, 36, id.toString());
      put(bytes, 96, 17, "20261003090000000");
      put(bytes, 113, 64, ascii(request, 113, 64));
      number(bytes, 177, 4, 256);
      number(bytes, 181, 6, 8896);
      number(bytes, 187, 6, 0);
      number(bytes, 193, 6, 0);
      number(bytes, 199, 9, 9152);
      put(bytes, 208, 4, code);
      if (!success) {
        // SS322: N is all zero; B error filler is space, not false.
        number(bytes, 256, 12, 0);
        number(bytes, 318, 17, 0);
        return bytes;
      }
      long target = detailReplyId == 0 ? Long.parseLong(ascii(request, 256, 12)) : detailReplyId;
      number(bytes, 256, 12, target);
      put(bytes, 268, 26, target == 1 ? RECEIPT : String.format(Locale.ROOT, "%026d", target));
      put(
          bytes,
          294,
          12,
          detailState.equals("COMPLETED")
              ? "COMPLETED"
              : detailState.equals("ERROR") ? "ERROR" : "ACCEPTED");
      put(bytes, 306, 12, detailState);
      put(bytes, 318, 17, "20261003085800000");
      if (Set.of("PROCESSING", "COMPLETED", "ERROR").contains(detailState))
        put(bytes, 335, 17, "20261003085900000");
      if (detailState.equals("COMPLETED")) put(bytes, 352, 17, "20261003085930000");
      if (detailState.equals("ERROR")) {
        put(bytes, 369, 17, "20261003085930000");
        put(bytes, 8596, 16, "PROCESS_FAILED");
        put(bytes, 8612, 512, "処理を完了できませんでした。");
      }
      if (detailState.equals("CANCELLED")) put(bytes, 386, 17, "20261003085900000");
      put(bytes, 403, 1, deleted ? "1" : "0");
      if (!deleted) {
        put(bytes, 404, 4096, summary);
        number(bytes, 9124, 12, target);
      }
      if (detailState.equals("COMPLETED") && (!deleted || deletedAnswer))
        put(bytes, 4500, 4096, answer);
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

  // UI236 literal offsets/widths, independent of Production codec and catalog.
  private static byte[] response(
      UUID id,
      String context,
      String code,
      int page,
      int rows,
      int total,
      String type,
      String state,
      String submitted,
      String summary,
      boolean deleted) {
    boolean success = code.equals("0000") || code.equals("0200");
    int count = success ? rows : 0;
    byte[] bytes = new byte[304 + 624 * count];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, 8, "SCHBNK01");
    put(bytes, 8, 3, "001");
    put(bytes, 11, 8, "NTSRSP01");
    put(bytes, 19, 3, "001");
    put(bytes, 22, 1, "S");
    put(bytes, 23, 1, "S");
    put(bytes, 24, 36, new UUID(1, id.getLeastSignificantBits()).toString());
    put(bytes, 60, 36, id.toString());
    put(bytes, 96, 17, "20261003090000000");
    put(bytes, 113, 64, context);
    number(bytes, 177, 4, 256);
    number(bytes, 181, 6, 48);
    number(bytes, 187, 6, 624);
    number(bytes, 193, 6, count);
    number(bytes, 199, 9, bytes.length);
    put(bytes, 208, 4, code);
    number(bytes, 256, 6, success ? page : 0);
    number(bytes, 262, 3, success ? 50 : 0);
    number(bytes, 265, 9, success ? total : 0);
    number(bytes, 274, 6, success ? Math.max(1, (total + 49) / 50) : 0);
    number(bytes, 280, 9, count == 0 ? 0 : (page - 1L) * 50 + 1);
    number(bytes, 289, 9, count == 0 ? 0 : (page - 1L) * 50 + count);
    for (int i = 0; i < count; i++) {
      int at = 304 + 624 * i;
      number(bytes, at, 12, count - i);
      // Decimal suffix digits are also Crockford symbols; each ID is independently unique.
      put(
          bytes,
          at + 12,
          26,
          count == 1 ? RECEIPT : String.format(Locale.ROOT, "%026d", count - i));
      put(bytes, at + 38, 12, type);
      put(bytes, at + 50, 12, state);
      put(bytes, at + 62, 17, submitted);
      put(bytes, at + 79, 17, "20261003090000000");
      put(bytes, at + 96, 512, summary);
      put(bytes, at + 608, 1, deleted ? "1" : "0");
    }
    return bytes;
  }

  private static void put(byte[] bytes, int offset, int length, String value) {
    byte[] encoded = value.getBytes(StandardCharsets.UTF_8);
    assertTrue(encoded.length <= length);
    Arrays.fill(bytes, offset, offset + length, (byte) ' ');
    System.arraycopy(encoded, 0, bytes, offset, encoded.length);
  }

  private static void number(byte[] bytes, int offset, int length, long value) {
    put(bytes, offset, length, String.format(Locale.ROOT, "%0" + length + "d", value));
  }

  private static String ascii(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.US_ASCII);
  }
}
