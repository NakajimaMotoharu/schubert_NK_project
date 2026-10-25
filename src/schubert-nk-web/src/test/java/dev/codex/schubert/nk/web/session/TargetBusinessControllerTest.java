package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.application.question.QuestionCommandService;
import dev.codex.schubert.nk.api.application.question.QuestionMutationApplicationService;
import dev.codex.schubert.nk.api.application.question.QuestionQueryApplicationService;
import dev.codex.schubert.nk.api.application.question.QuestionQueryReplayService;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.protocol.codec.ExpectedRoute;
import dev.codex.schubert.nk.protocol.codec.FixedWidthDecoder;
import dev.codex.schubert.nk.protocol.codec.TransportBodyType;
import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.controller.NotificationController;
import dev.codex.schubert.nk.web.controller.QuestionController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepository;
import dev.codex.schubert.nk.web.view.NotificationDetailViewModel;
import dev.codex.schubert.nk.web.view.QuestionDetailViewModel;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;

/** Independent UI224236 304/288/280/9152/8608 vectors; PG-D368/NTC-BIZ/QDL-BIZ. */
class TargetBusinessControllerTest {
  private static final Instant NOW = Instant.parse("2026-10-04T00:00:00Z");
  private static final Clock CLOCK = Clock.fixed(NOW, ZoneOffset.UTC);
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
      s.executeUpdate("DELETE FROM schubert_web_session.web_receipt_references");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "reader", UserRole.USER, AuthenticationContext.of("a".repeat(64)), Instant.EPOCH);
  }

  private static LinkedMultiValueMap<String, String> input(boolean cancel, UUID token) {
    var result = new LinkedMultiValueMap<String, String>();
    result.add("operation", cancel ? "CANCEL" : "DELETE");
    result.add("id", "1");
    result.add("confirm", "true");
    result.add("operation_token", token.toString());
    return result;
  }

  @Test
  void ntc001OnlyReceivedVisibleFormIssuesOneCurrentToken() throws Exception {
    for (String state : List.of("RECEIVED", "PROCESSING", "COMPLETED", "ERROR", "CANCELLED")) {
      reset();
      try (var f = new Fixture()) {
        f.state = state;
        var model = new ExtendedModelMap();
        var response = new MockHttpServletResponse();
        assertEquals(
            "notifications/detail",
            f.notifications.detail("1", actor(), model, f.request("GET"), response));
        assertEquals(200, response.getStatus());
        assertEquals(state.equals("RECEIVED") ? 1 : 0, f.tokenIds.get());
        assertEquals(state.equals("RECEIVED"), model.containsAttribute("action"));
        assertEquals(
            state, ((NotificationDetailViewModel) model.get("page")).getValues().get("state"));
        assertEquals(1, f.sent.size());
        assertEquals("NTDREQ01", ascii(f.sent.getFirst(), 11, 8));
        f.erased();
      }
    }
  }

  @Test
  void ntc002AndQdl002IndependentWholeRequestAndCompletionFirstWrite() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      reset();
      try (var f = new Fixture()) {
        UUID token = f.issue(cancel);
        for (String code : List.of("0000", "0200")) {
          f.code = code;
          f.security.f.clock.value = NOW.plusSeconds(code.equals("0200") ? 1 : 0);
          var response = new MockHttpServletResponse();
          assertNull(
              f.post(
                  cancel,
                  input(cancel, token),
                  new ExtendedModelMap(),
                  f.request("POST"),
                  response));
          assertEquals(302, response.getStatus());
          assertEquals(cancel ? "/notifications/1" : "/questions", response.getHeader("Location"));
          assertEquals(1, f.tokenIds.get());
          assertEquals(NOW, f.retained().getFirst().completedAt().orElseThrow());
          byte[] expected =
              header(
                  cancel ? "NTCREQ01" : "QDLREQ01", 48, new UUID(0, f.messages.get()), false, "");
          put(expected, 256, "000000000001");
          put(expected, 268, token.toString());
          assertArrayEquals(expected, f.sent.getLast());
          f.erased();
        }
      }
    }
  }

  @Test
  void qdl001OnlyVerifiedDetailIssuesOneAndInputRetryNeverIssuesReplacement() throws Exception {
    try (var f = new Fixture()) {
      var model = new ExtendedModelMap();
      var response = new MockHttpServletResponse();
      assertEquals(
          "questions/detail", f.questions.detail("1", actor(), model, f.request("GET"), response));
      assertEquals(200, response.getStatus());
      assertEquals(1, f.retained().size());
      assertEquals("QDLREQ01", f.retained().getFirst().purpose());
      UUID token = f.retained().getFirst().token();
      var p = input(false, token);
      p.set("confirm", "false");
      response = new MockHttpServletResponse();
      assertEquals("questions/detail", f.post(false, p, model, f.request("POST"), response));
      assertEquals(400, response.getStatus());
      assertEquals(1, f.tokenIds.get());
      assertTrue(f.sent.stream().allMatch(b -> ascii(b, 11, 8).equals("QSDREQ01")));
      assertTrue(f.retained().getFirst().completedAt().isEmpty());
      assertTrue(model.get("action").toString().contains(token.toString()));
      f.erased();
    }
  }

  @Test
  void ntc003AndQdl003AllPendingCapacityFreshRefusalHasNoUuidOrMutation() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      reset();
      try (var f = new Fixture()) {
        for (int n = 0; n < 10; n++) f.issue(cancel);
        var original = f.retained();
        var response = new MockHttpServletResponse();
        assertNull(f.detail(cancel, new ExtendedModelMap(), f.request("GET"), response));
        assertEquals(409, response.getStatus());
        assertEquals(10, f.tokenIds.get());
        assertEquals(original, f.retained());
        assertEquals(1, f.sent.size());
        assertEquals(cancel ? "NTDREQ01" : "QSDREQ01", ascii(f.sent.getFirst(), 11, 8));
        f.erased();
      }
    }
  }

  @Test
  void ntc004AndQdl004CurrentRetainedPurposeAndSessionRequiredBeforeMutation() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      for (String variant : List.of("absent", "purpose", "session", "malformed-session")) {
        reset();
        try (var f = new Fixture()) {
          UUID token =
              variant.equals("absent")
                  ? new UUID(9, 9)
                  : f.issue(variant.equals("purpose") ? !cancel : cancel);
          var request = f.request("POST");
          if (variant.equals("session")) request.setSession(null);
          if (variant.equals("malformed-session"))
            request.setSession(new MockHttpSession(null, "malformed"));
          var response = new MockHttpServletResponse();
          assertNull(
              f.post(cancel, input(cancel, token), new ExtendedModelMap(), request, response));
          assertEquals(409, response.getStatus());
          assertTrue(f.sent.isEmpty());
          f.erased();
        }
      }
    }
  }

  @Test
  void ntc005AndQdl005FailureCodesKeepSameTokenOrTerminalAndRefreshOnlyReads() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      for (String code :
          List.of("0100", "0101", "0102", "0103", "0104", "0105", "0106", "0107", "9000", "9001")) {
        if (!cancel && code.equals("0107")) continue;
        reset();
        try (var f = new Fixture()) {
          UUID token = f.issue(cancel);
          f.code = code;
          f.state = code.equals("0107") ? "PROCESSING" : "RECEIVED";
          var request = f.request("POST");
          var response = new MockHttpServletResponse();
          var model = new ExtendedModelMap();
          var priorSession = request.getSession(false);
          String result = f.post(cancel, input(cancel, token), model, request, response);
          int expected =
              switch (code) {
                case "0100" -> 400;
                case "0101", "0102" -> 401;
                case "0103" -> 403;
                case "0104" -> 404;
                case "0105", "0107" -> 409;
                case "0106" -> 429;
                default -> 503;
              };
          assertEquals(expected, response.getStatus());
          assertEquals(1, f.tokenIds.get());
          if (code.equals("0102")) {
            assertNull(result);
            assertTrue(((MockHttpSession) priorSession).isInvalid());
            assertEquals(1, f.security.log.events.size());
          } else {
            assertTrue(f.retained().getFirst().completedAt().isEmpty());
            boolean redisplay = Set.of("0100", "0105", "0107", "9000", "9001").contains(code);
            assertEquals(
                redisplay ? (cancel ? "notifications/detail" : "questions/detail") : null, result);
            assertEquals(redisplay ? 2 : 1, f.sent.size());
            if (code.equals("0107")) {
              assertFalse(model.containsAttribute("action"));
              assertEquals("現在の状態では取り消せません。", model.get("notice"));
            }
          }
          f.erased();
        }
      }
    }
  }

  @Test
  void ntc007AndQdl007ActualApiOneChangeAndRetainedReplayWithoutPreRead() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      reset();
      try (var f = new Fixture();
          var api = new RealApi(f)) {
        UUID token = f.issue(cancel);
        for (int attempt = 0; attempt < 2; attempt++) {
          var response = new MockHttpServletResponse();
          assertNull(
              f.post(
                  cancel,
                  input(cancel, token),
                  new ExtendedModelMap(),
                  f.request("POST"),
                  response));
          assertEquals(302, response.getStatus());
          assertEquals(cancel ? "/notifications/1" : "/questions", response.getHeader("Location"));
          assertEquals(
              1,
              api.scalar(
                  cancel
                      ? "SELECT count(*) FROM schubert.async_jobs WHERE id=1 AND state='CANCELLED' AND version=1 AND cancelled_at='2026-10-04T00:00:00Z'"
                      : "SELECT count(*) FROM schubert.questions WHERE id=1 AND is_deleted AND version=1 AND deleted_by=1 AND deleted_at='2026-10-04T00:00:00Z'"));
          assertEquals(
              cancel ? 0 : 1, api.scalar("SELECT version FROM schubert.questions WHERE id=1"));
          assertEquals(
              cancel ? 1 : 0, api.scalar("SELECT version FROM schubert.async_jobs WHERE id=1"));
          assertEquals(1, f.tokenIds.get());
          assertEquals(NOW, f.retained().getFirst().completedAt().orElseThrow());
        }
        assertEquals(
            1, api.scalar("SELECT count(*) FROM schubert.app_logs WHERE action='INBOX_REPLAYED'"));
        assertEquals(
            cancel ? 50 : 51,
            api.scalar("SELECT count(*) FROM schubert.notifications WHERE state='RECEIVED'"));
        if (!cancel) {
          var response = new MockHttpServletResponse();
          assertNull(
              f.questions.detail("1", actor(), new ExtendedModelMap(), f.request("GET"), response));
          assertEquals(404, response.getStatus());
          assertEquals(1, f.tokenIds.get());
        }
        f.erased();
      }
    }
  }

  @Test
  void ntc008AndQdl008OneHundredRealApiCallsKeepOneMutationAndNinetyNineReplays() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      reset();
      try (var f = new Fixture();
          var api = new RealApi(f)) {
        UUID token = f.issue(cancel);
        var futures = new ArrayList<Future<?>>();
        try (var executor = Executors.newFixedThreadPool(8)) {
          for (int n = 0; n < 100; n++)
            futures.add(
                executor.submit(
                    () -> {
                      var response = new MockHttpServletResponse();
                      assertNull(
                          f.post(
                              cancel,
                              input(cancel, token),
                              new ExtendedModelMap(),
                              f.request("POST"),
                              response));
                      assertEquals(302, response.getStatus());
                      return null;
                    }));
          for (var future : futures) future.get(20, TimeUnit.SECONDS);
        }
        assertEquals(100, f.messages.get());
        assertEquals(1, f.tokenIds.get());
        assertEquals(
            1,
            api.scalar(
                cancel
                    ? "SELECT version FROM schubert.async_jobs WHERE id=1"
                    : "SELECT version FROM schubert.questions WHERE id=1"));
        assertEquals(
            99, api.scalar("SELECT count(*) FROM schubert.app_logs WHERE action='INBOX_REPLAYED'"));
        assertEquals(1, f.retained().size());
        assertTrue(f.retained().getFirst().completedAt().isPresent());
        f.erased();
      }
    }
  }

  @Test
  void ntc006AndQdl006UnknownTransportAndStoreCompletionNeverFakeSuccess() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      for (String fault :
          List.of("transport", "open", "connection.commit", "connection.close", "deleted")) {
        reset();
        try (var f = new Fixture()) {
          UUID token = f.issue(cancel);
          f.responder =
              (id, bytes) -> {
                String layout = ascii(bytes, 11, 8);
                boolean mutation = Set.of("NTCREQ01", "QDLREQ01").contains(layout);
                if (mutation && fault.equals("transport"))
                  throw new jakarta.jms.JMSRuntimeException("private-mq-marker");
                byte[] reply = f.reply(id, bytes);
                if (mutation) {
                  if (fault.equals("deleted"))
                    f.security.f.repository.invalidate(f.session.sessionId());
                  else if (!fault.equals("open")) f.security.f.failure = fault;
                }
                return reply;
              };
          var request = f.request("POST");
          if (fault.equals("open")) f.security.f.failure = "open";
          var response = new MockHttpServletResponse();
          var model = new ExtendedModelMap();
          var result = f.post(cancel, input(cancel, token), model, request, response);
          assertEquals(fault.equals("deleted") ? 409 : 503, response.getStatus());
          assertNull(response.getHeader("Location"));
          assertEquals(
              fault.equals("deleted")
                  ? null
                  : (cancel ? "notifications/detail" : "questions/detail"),
              result);
          assertEquals(1, f.tokenIds.get());
          f.security.f.failure = "";
          if (!fault.equals("deleted"))
            assertEquals(
                fault.equals("connection.close"),
                f.retained().getFirst().completedAt().isPresent());
          f.erased();
        }
      }
      for (String variant : List.of("missing-session", "malformed-session", "open")) {
        reset();
        try (var f = new Fixture()) {
          var request = f.request("GET");
          if (variant.equals("missing-session")) request.setSession(null);
          if (variant.equals("malformed-session"))
            request.setSession(new MockHttpSession(null, "bad"));
          if (variant.equals("open")) f.security.f.failure = "open";
          var response = new MockHttpServletResponse();
          assertNull(f.detail(cancel, new ExtendedModelMap(), request, response));
          assertEquals(variant.equals("open") ? 503 : 409, response.getStatus());
          assertEquals(0, f.tokenIds.get());
          f.security.f.failure = "";
          f.erased();
        }
      }
    }
  }

  @Test
  void targetBoundaryAndLegacyAssemblyRemainClosed() throws Exception {
    try (var f = new Fixture()) {
      var model = new ExtendedModelMap();
      var request = f.request("POST");
      var boundaryResponse = new MockHttpServletResponse();
      var parameters = input(true, new UUID(0, 99));
      assertThrows(
          NullPointerException.class,
          () -> new NotificationController(f.notificationClient, f.security.handler, null));
      assertThrows(
          NullPointerException.class,
          () -> new NotificationController(null, f.security.handler, f.tokens));
      assertThrows(
          NullPointerException.class,
          () -> new NotificationController(f.notificationClient, null, f.tokens));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.notifications.cancel(
                  "1", parameters, () -> "foreign", model, request, boundaryResponse));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.questions.delete(
                  "1", parameters, () -> "foreign", model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () ->
              f.notifications.cancel(null, parameters, actor(), model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.notifications.cancel("1", null, actor(), model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.notifications.cancel("1", parameters, null, model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.notifications.cancel("1", parameters, actor(), null, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.notifications.cancel("1", parameters, actor(), model, null, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.notifications.cancel("1", parameters, actor(), model, request, null));
      assertThrows(
          NullPointerException.class,
          () -> f.questions.delete(null, parameters, actor(), model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.questions.delete("1", null, actor(), model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.questions.delete("1", parameters, null, model, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.questions.delete("1", parameters, actor(), null, request, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.questions.delete("1", parameters, actor(), model, null, boundaryResponse));
      assertThrows(
          NullPointerException.class,
          () -> f.questions.delete("1", parameters, actor(), model, request, null));
      for (String target : List.of("0", "-1", "bad", "999999999999999999999999")) {
        var response = new MockHttpServletResponse();
        assertNull(f.notifications.cancel(target, parameters, actor(), model, request, response));
        assertEquals(404, response.getStatus());
        response = new MockHttpServletResponse();
        assertNull(f.questions.delete(target, parameters, actor(), model, request, response));
        assertEquals(404, response.getStatus());
      }
      var response = new MockHttpServletResponse();
      assertNull(
          new NotificationController(f.notificationClient, f.security.handler)
              .cancel("1", parameters, actor(), model, request, response));
      assertEquals(503, response.getStatus());
      response = new MockHttpServletResponse();
      assertNull(
          new QuestionController(f.questionClient, f.security.handler)
              .delete("1", parameters, actor(), model, request, response));
      assertEquals(503, response.getStatus());
      assertTrue(f.sent.isEmpty());
    }
  }

  @Test
  void qdl009OwnerIsolationAndLiteralCodePointSummary() throws Exception {
    for (String text :
        List.of(
            "a",
            "a".repeat(99),
            "a".repeat(100),
            "a".repeat(99) + "😀" + "b",
            "<script>".repeat(30))) {
      reset();
      try (var f = new Fixture()) {
        f.question = text;
        var model = new ExtendedModelMap();
        assertEquals(
            "questions/detail",
            f.questions.detail(
                "1", actor(), model, f.request("GET"), new MockHttpServletResponse()));
        String expected =
            text.equals("a".repeat(99) + "😀" + "b")
                ? "a".repeat(99) + "😀"
                : text.startsWith("<script>") ? "<script>".repeat(12) + "<scr" : text;
        assertEquals(
            expected, ((QuestionDetailViewModel) model.get("page")).getValues().get("summary"));
        assertEquals(1, f.tokenIds.get());
      }
    }
    for (boolean cancel : List.of(true, false)) {
      reset();
      try (var f = new Fixture();
          var api = new RealApi(f)) {
        UUID token = f.issue(cancel);
        var parameters = input(cancel, token);
        parameters.set("id", "51");
        var response = new MockHttpServletResponse();
        if (cancel)
          assertNull(
              f.notifications.cancel(
                  "51", parameters, actor(), new ExtendedModelMap(), f.request("POST"), response));
        else
          assertNull(
              f.questions.delete(
                  "51", parameters, actor(), new ExtendedModelMap(), f.request("POST"), response));
        assertEquals(404, response.getStatus());
        assertEquals(0, api.scalar("SELECT version FROM schubert.questions WHERE id=51"));
        assertEquals(0, api.scalar("SELECT version FROM schubert.async_jobs WHERE id=51"));
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
        assertEquals(1, f.sent.size());
        f.erased();
      }
    }
  }

  @Test
  void ntc006AndQdl006RealHttpSameCoreActualApiCsrfListAndReplay() throws Exception {
    try (var f = new Fixture();
        var api = new RealApi(f)) {
      reset();
      try (var connection = db.admin();
          var statement =
              connection.prepareStatement("UPDATE schubert.questions SET body=? WHERE id=1")) {
        statement.setString(1, "a".repeat(99) + "😀<script>alert(1)</script>");
        assertEquals(1, statement.executeUpdate());
      }
      var loginApi = new SessionFormLoginTest.Api("0000", "USER", "0000", 0);
      try (var server =
          new EmbeddedWebSecurityTest.Server(
              root,
              false,
              db,
              Optional.of(loginApi.provider),
              true,
              false,
              (mvc, invalid) -> {
                mvc.register(
                    dev.codex.schubert.nk.web.config.NotificationBusinessMvcConfiguration.class,
                    dev.codex.schubert.nk.web.config.QuestionAcceptanceMvcConfiguration.class);
                mvc.addBeanFactoryPostProcessor(
                    factory -> {
                      factory.registerSingleton("notificationWireClient", f.notificationClient);
                      factory.registerSingleton("questionWireClient", f.questionClient);
                      factory.registerSingleton("apiSessionInvalidHandler", invalid);
                      factory.registerSingleton(
                          "receiptReferenceRepository",
                          new ReceiptReferenceRepository(f.security.f.source));
                    });
              },
              (mvc, core) ->
                  mvc.addBeanFactoryPostProcessor(
                      factory ->
                          factory.registerSingleton(
                              "sessionOperationTokenLifecycle",
                              new SessionOperationTokenLifecycle(core, Clock.systemUTC()))))) {
        var previous = f.responder;
        f.responder =
            (id, bytes) -> {
              assertEquals(0, server.f.threadLive.getOrDefault(Thread.currentThread(), 0));
              return previous.apply(id, bytes);
            };
        var page = server.send("GET", "/login", null, null, true);
        assertTrue(page.body().startsWith("TOKEN:"));
        String cookie = page.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        var login =
            server.send(
                "POST",
                "/login",
                cookie,
                "username=reader&password=longpassword1&_csrf=" + page.body().substring(6),
                true);
        assertEquals(302, login.statusCode());
        cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
        page = server.send("GET", "/questions", cookie, null, true);
        assertEquals(200, page.statusCode());
        var dom = org.jsoup.Jsoup.parse(page.body());
        assertEquals(50, dom.select("a.delete").size());
        var expectedLinks = new ArrayList<String>();
        // UI224: same submitted_at means ID descending; derive every expected href independently.
        for (int id = 50; id >= 1; id--) expectedLinks.add("/questions/" + id + "#delete-confirm");
        assertEquals(expectedLinks, dom.select("a.delete").eachAttr("href"));
        assertTrue(dom.select("input[name=operation_token]").isEmpty());
        for (boolean cancel : List.of(true, false)) {
          String path = cancel ? "/notifications/1" : "/questions/1";
          page = server.send("GET", path, cookie, null, true);
          assertEquals(200, page.statusCode());
          dom = org.jsoup.Jsoup.parse(page.body());
          if (!cancel) {
            assertEquals("a".repeat(99) + "😀", dom.select(".delete-summary").text());
            assertTrue(page.body().contains("&lt;script&gt;alert(1)&lt;/script&gt;"));
            assertTrue(dom.select(".question-body script,.delete-summary script").isEmpty());
          }
          var form = dom.select(cancel ? "form.cancel-form" : "form.delete-form");
          assertEquals(1, form.size());
          assertTrue(form.hasAttr("data-operation-submit"));
          assertEquals(
              List.of("/js/operation-post-submit.js"),
              dom.select("script[src][defer]").eachAttr("src"));
          String token = form.select("input[name=operation_token]").attr("value");
          String csrf = form.select("input[name=_csrf]").attr("value");
          String body =
              "operation="
                  + (cancel ? "CANCEL" : "DELETE")
                  + "&id=1&confirm=true&operation_token="
                  + token;
          int sent = f.sent.size();
          assertEquals(
              403, server.send("POST", path, cookie, body + "&_csrf=bad", true).statusCode());
          assertEquals(sent, f.sent.size());
          for (int n = 0; n < 2; n++) {
            var changed = server.send("POST", path, cookie, body + "&_csrf=" + csrf, true);
            assertEquals(302, changed.statusCode());
            assertEquals(
                cancel ? "/notifications/1" : "/questions",
                changed.headers().firstValue("location").orElseThrow());
            assertEquals(
                1,
                api.scalar(
                    cancel
                        ? "SELECT version FROM schubert.async_jobs WHERE id=1"
                        : "SELECT version FROM schubert.questions WHERE id=1"));
          }
          assertEquals(0, server.f.live.get());
        }
        assertEquals(404, server.send("GET", "/questions/1", cookie, null, true).statusCode());
        assertEquals(
            2, api.scalar("SELECT count(*) FROM schubert.app_logs WHERE action='INBOX_REPLAYED'"));
        f.erased();
      }
    }
  }

  @Test
  void ntc004AndQdl004InvalidBindingReadsFreshStateWithoutMutationOrReplacement() throws Exception {
    for (boolean cancel : List.of(true, false))
      for (String invalid : List.of("confirm", "target", "token", "unknown", "null")) {
        reset();
        try (var f = new Fixture()) {
          UUID token = f.issue(cancel);
          var parameters = input(cancel, token);
          switch (invalid) {
            case "confirm" -> parameters.remove("confirm");
            case "target" -> parameters.set("id", "2");
            case "token" -> parameters.set("operation_token", "not-a-uuid");
            case "unknown" -> parameters.set("owner", "other");
            default -> parameters.put("confirm", Arrays.asList((String) null));
          }
          var response = new MockHttpServletResponse();
          var model = new ExtendedModelMap();
          assertEquals(
              cancel ? "notifications/detail" : "questions/detail",
              f.post(cancel, parameters, model, f.request("POST"), response));
          assertEquals(400, response.getStatus());
          assertNull(response.getHeader("Location"));
          assertEquals(1, f.sent.size());
          assertEquals(cancel ? "NTDREQ01" : "QSDREQ01", ascii(f.sent.getFirst(), 11, 8));
          assertEquals(1, f.tokenIds.get());
          assertEquals(token, f.retained().getFirst().token());
          assertTrue(f.retained().getFirst().completedAt().isEmpty());
          assertTrue(model.containsAttribute("action"));
          f.erased();
        }
      }
  }

  @Test
  void ntc006AndQdl006FatalIdentityIsNeverConvertedToRetryOrSuccess() throws Exception {
    for (boolean cancel : List.of(true, false)) {
      reset();
      try (var f = new Fixture()) {
        UUID token = f.issue(cancel);
        var fatal = new LinkageError("synthetic-terminal");
        f.responder =
            (id, bytes) -> {
              throw fatal;
            };
        var response = new MockHttpServletResponse();
        var request = f.request("POST");
        assertSame(
            fatal,
            assertThrows(
                LinkageError.class,
                () ->
                    f.post(
                        cancel, input(cancel, token), new ExtendedModelMap(), request, response)));
        assertNull(response.getHeader("Location"));
        assertEquals(1, f.sent.size());
        assertEquals(cancel ? "NTCREQ01" : "QDLREQ01", ascii(f.sent.getFirst(), 11, 8));
        assertEquals(1, f.tokenIds.get());
        assertTrue(f.retained().getFirst().completedAt().isEmpty());
        f.erased();
      }
    }
  }

  static final class RealApi implements AutoCloseable {
    final FingerprintKeyRing fingerprints = new FingerprintKeyRing("pt", new byte[32], null, null);
    final ResponseSnapshotCodec snapshots =
        new ResponseSnapshotCodec("pt", new byte[32], null, null);

    RealApi(Fixture fixture) throws Exception {
      try (var c = db.admin();
          var s = c.createStatement()) {
        s.execute(
            "TRUNCATE schubert.app_users,schubert.mq_outbox,schubert.app_logs RESTART IDENTITY CASCADE");
        s.execute(
            "INSERT INTO schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) VALUES(1,'reader','reader','unusable-synthetic','USER','ACTIVE','2026-10-03T00:00:00Z','2026-10-03T00:00:00Z','2026-10-03T00:00:00Z'),(2,'other','other','unusable-synthetic','USER','ACTIVE','2026-10-03T00:00:00Z','2026-10-03T00:00:00Z','2026-10-03T00:00:00Z')");
        s.execute(
            "INSERT INTO schubert.questions(id,receipt_id,owner_user_id,body,operation_token,submitted_at) SELECT i,lpad(i::text,26,'0'),CASE WHEN i=51 THEN 2 ELSE 1 END,'question'||i,('00000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,'2026-10-04T00:00:00Z' FROM generate_series(1,51)i");
        s.execute(
            "INSERT INTO schubert.async_jobs(id,question_id,owner_user_id,state,message_id,correlation_id,received_at,state_changed_at) SELECT i,i,CASE WHEN i=51 THEN 2 ELSE 1 END,'RECEIVED',('10000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,('20000000-0000-4000-8000-'||lpad(i::text,12,'0'))::uuid,'2026-10-04T00:00:00Z','2026-10-04T00:00:00Z' FROM generate_series(1,51)i");
        s.execute(
            "INSERT INTO schubert.notifications(id,job_id,question_id,owner_user_id,notification_type,state,accepted_at,state_changed_at,created_at,updated_at) SELECT i,i,i,CASE WHEN i=51 THEN 2 ELSE 1 END,'ACCEPTED','RECEIVED','2026-10-04T00:00:00Z','2026-10-04T00:00:00Z','2026-10-04T00:00:00Z','2026-10-04T00:00:00Z' FROM generate_series(1,51)i");
      }
      try (var c = db.api();
          var s =
              c.prepareStatement(
                  "INSERT INTO schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) VALUES(?,1,?,?,'pt',?,?,?,'192.0.2.99',?)")) {
        s.setObject(1, new UUID(951, 1));
        s.setString(
            2,
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest("a".repeat(64).getBytes(StandardCharsets.US_ASCII))));
        s.setBytes(3, new byte[29]);
        s.setObject(4, NOW.minusSeconds(60).atOffset(ZoneOffset.UTC));
        s.setObject(5, NOW.minusSeconds(60).atOffset(ZoneOffset.UTC));
        s.setObject(6, NOW.plusSeconds(28800).atOffset(ZoneOffset.UTC));
        s.setObject(7, new UUID(952, 1));
        assertEquals(1, s.executeUpdate());
      }
      DataSource source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("getConnection"))
                      throw new AssertionError("unexpected datasource call");
                    return db.api();
                  });
      var queries =
          new QuestionQueryApplicationService(
              source,
              new AuthenticationContextVerifier(new ContextHash()),
              new QuestionQueryRepository(),
              new JdbcInboxCoordinator(fingerprints),
              new QuestionQueryReplayService(snapshots),
              CLOCK);
      var changes =
          new QuestionMutationApplicationService(
              source,
              new AuthenticationContextVerifier(new ContextHash()),
              new JdbcInboxCoordinator(fingerprints),
              new QuestionCommandService(),
              snapshots,
              CLOCK);
      fixture.responder =
          (id, bytes) -> {
            var layout = new LayoutId(ascii(bytes, 11, 8));
            var metadata =
                new TransportMetadata(
                    TransportBodyType.BYTES,
                    "ID:synthetic-" + id,
                    id,
                    Optional.of("nk.sync.reply.web"),
                    NOW.plusSeconds(5).toEpochMilli(),
                    2,
                    1,
                    id,
                    layout,
                    "001",
                    "nk.sync.request");
            var route =
                new ExpectedRoute(
                    MessageKind.REQUEST,
                    InteractionKind.SYNCHRONOUS,
                    "nk.sync.request",
                    Optional.of("nk.sync.reply.web"),
                    true);
            var message = FixedWidthDecoder.standard().decode(bytes, metadata, route);
            return Set.of("NTCREQ01", "QDLREQ01").contains(layout.value())
                ? changes.process(message)
                : queries.process(message);
          };
    }

    long scalar(String sql) throws Exception {
      try (var c = db.admin();
          var s = c.createStatement();
          var r = s.executeQuery(sql)) {
        assertTrue(r.next());
        return r.getLong(1);
      }
    }

    @Override
    public void close() {
      snapshots.close();
      fingerprints.close();
    }
  }

  static final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final WebSessionSnapshot session;
    final AtomicLong tokenIds = new AtomicLong();
    final AtomicLong messages = new AtomicLong();
    final SessionOperationTokenLifecycle tokens;
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final List<byte[]> sent = new CopyOnWriteArrayList<>();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    final NotificationWireClient notificationClient;
    final QuestionWireClient questionClient;
    final NotificationController notifications;
    final QuestionController questions;
    String code = "0000";
    String state = "RECEIVED";
    String question = "question";
    String owner = "reader";
    BiFunction<UUID, byte[], byte[]> responder = this::reply;

    Fixture() throws Exception {
      security.f.clock.value = NOW;
      session = security.authenticated(actor());
      tokens =
          new SessionOperationTokenLifecycle(
              security.f.repository,
              security.f.clock,
              () -> new UUID(0, 100 + tokenIds.incrementAndGet()));
      JmsRequestSender sender =
          (id, bytes) -> {
            sent.add(bytes.clone());
            buffers.add(bytes);
            assertEquals(0, security.f.threadLive.getOrDefault(Thread.currentThread(), 0));
            assertTrue(wire.onReply(id, responder.apply(id, bytes)));
          };
      notificationClient =
          new NotificationWireClient(
              wire,
              sender,
              CLOCK,
              () -> new UUID(0, messages.incrementAndGet()),
              Duration.ofSeconds(1));
      questionClient =
          new QuestionWireClient(
              wire,
              sender,
              CLOCK,
              () -> new UUID(0, messages.incrementAndGet()),
              Duration.ofSeconds(1));
      notifications = new NotificationController(notificationClient, security.handler, tokens);
      questions =
          new QuestionController(
              questionClient,
              security.handler,
              new ReceiptReferenceRepository(security.f.source),
              tokens);
    }

    UUID issue(boolean cancel) {
      return tokens.issue(session.sessionId(), cancel ? "NTCREQ01" : "QDLREQ01").token();
    }

    List<SessionOperationToken> retained() {
      return security
          .f
          .repository
          .find(session.sessionId())
          .orElseThrow()
          .attributes()
          .operationTokens();
    }

    MockHttpServletRequest request(String method) throws Exception {
      var request = security.mock(method, "/questions/1");
      request.setSession(new MockHttpSession(null, session.sessionId().cookieValue()));
      return request;
    }

    String post(
        boolean cancel,
        LinkedMultiValueMap<String, String> parameters,
        ExtendedModelMap model,
        MockHttpServletRequest request,
        MockHttpServletResponse response)
        throws IOException {
      return cancel
          ? notifications.cancel("1", parameters, actor(), model, request, response)
          : questions.delete("1", parameters, actor(), model, request, response);
    }

    String detail(
        boolean cancel,
        ExtendedModelMap model,
        MockHttpServletRequest request,
        MockHttpServletResponse response)
        throws IOException {
      return cancel
          ? notifications.detail("1", actor(), model, request, response)
          : questions.detail("1", actor(), model, request, response);
    }

    byte[] reply(UUID id, byte[] request) {
      String layout = ascii(request, 11, 8);
      boolean notification = layout.startsWith("NT");
      boolean read = layout.equals("NTDREQ01") || layout.equals("QSDREQ01");
      int size = read ? (notification ? 8896 : 8352) : (notification ? 32 : 24);
      byte[] result = header(layout.replace("REQ", "RSP"), size, id, true, read ? "0000" : code);
      if (read && notification) {
        put(result, 256, "000000000001");
        put(result, 268, "0123456789ABCDEFGHJKMNPQRS");
        put(
            result,
            294,
            state.equals("COMPLETED") ? "COMPLETED" : state.equals("ERROR") ? "ERROR" : "ACCEPTED");
        put(result, 306, state);
        put(result, 318, "20261004085800000");
        if (Set.of("PROCESSING", "COMPLETED", "ERROR").contains(state))
          put(result, 335, "20261004085900000");
        if (state.equals("COMPLETED")) put(result, 352, "20261004085930000");
        if (state.equals("ERROR")) {
          put(result, 369, "20261004085930000");
          put(result, 8596, "PROCESS_FAILED");
          put(result, 8612, "処理を完了できませんでした。");
        }
        if (state.equals("CANCELLED")) put(result, 386, "20261004085900000");
        put(result, 403, "0");
        put(result, 404, question);
        put(result, 9124, "000000000001");
      } else if (read) {
        put(result, 256, "000000000001");
        put(result, 268, "0123456789ABCDEFGHJKMNPQRS");
        put(result, 294, owner);
        put(result, 358, "UNANSWERED");
        put(result, 370, question);
        put(result, 8562, "20261004085800000");
      } else if (notification) {
        if (Set.of("0000", "0200").contains(code)) {
          put(result, 256, "CANCELLED");
          put(result, 268, "20261004090000000");
        } else if (code.equals("0107")) put(result, 256, "PROCESSING");
      } else
        put(
            result,
            256,
            Set.of("0000", "0200").contains(code) ? "20261004090000000" : "00000000000000000");
      return result;
    }

    void erased() {
      for (var bytes : buffers) assertArrayEquals(new byte[bytes.length], bytes);
      assertEquals(0, security.f.live.get());
    }

    @Override
    public void close() {
      for (var bytes : sent) Arrays.fill(bytes, (byte) 0);
      security.close();
    }
  }

  static byte[] header(String layout, int size, UUID message, boolean response, String code) {
    byte[] bytes = new byte[256 + size];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, "SCHBNK01");
    put(bytes, 8, "001");
    put(bytes, 11, layout);
    put(bytes, 19, "001");
    put(bytes, 22, response ? "S" : "Q");
    put(bytes, 23, "S");
    put(
        bytes,
        24,
        (response ? new UUID(1, message.getLeastSignificantBits()) : message).toString());
    put(bytes, 60, message.toString());
    put(bytes, 96, "20261004090000000");
    put(bytes, 113, "a".repeat(64));
    put(bytes, 177, "0256");
    put(bytes, 181, String.format(Locale.ROOT, "%06d", size));
    put(bytes, 187, "000000");
    put(bytes, 193, "000000");
    put(bytes, 199, String.format(Locale.ROOT, "%09d", bytes.length));
    if (response) put(bytes, 208, code);
    return bytes;
  }

  static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }

  static String ascii(byte[] bytes, int offset, int length) {
    return new String(bytes, offset, length, StandardCharsets.US_ASCII);
  }
}
