package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.EncryptedSessionAuthenticationStrategy;
import dev.codex.schubert.nk.web.security.EncryptedSessionSecurityContextRepository;
import dev.codex.schubert.nk.web.security.LoginClientAddress;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.TestingAuthenticationToken;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.context.SecurityContextImpl;
import org.springframework.security.web.authentication.session.SessionAuthenticationException;
import org.springframework.security.web.context.HttpRequestResponseHolder;
import org.springframework.security.web.context.SecurityContextHolderFilter;
import org.springframework.session.web.http.SessionRepositoryFilter;

/** NK-WEB-001/PT-WEB-068..075; FUN-001/AUT-001..004; UI226/232/234; SS314/331/352; SSC-044. */
class SessionSecurityContextTest {
  private static WebLogDatabaseFixture db;
  private static final Instant LOGIN = Instant.parse("2026-09-08T00:00:00.123Z");
  private static final SessionPrincipal USER = principal("reader", UserRole.USER, "a");
  private static final SessionPrincipal ADMIN = principal("operator", UserRole.ADMIN, "b");

  @BeforeAll
  static void start(@TempDir Path root) throws Exception {
    db = new WebLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    SecurityContextHolder.clearContext();
    try (var c = db.web();
        var s = c.createStatement()) {
      s.executeUpdate("delete from schubert_web_session.web_http_sessions");
    }
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  @Test
  void web068ClosedProjectionRejectsForeignAuthentication() throws Exception {
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      // Public Servlet doubles only for impossible/corrupt container contracts. Positive DB below.
      var request = marked(adapter, new MockHttpSession());
      var response = new MockHttpServletResponse();
      for (var p : List.of(USER, ADMIN)) {
        request.getSession().setAttribute("principal", p);
        contexts.saveContext(context(auth(p)), request, response);
        assertIdentity(p, contexts.loadDeferredContext(request).get().getAuthentication());
      }
      var invalid = new ArrayList<Authentication>();
      invalid.add(new TestingAuthenticationToken(USER, null, "ROLE_USER"));
      invalid.add(UsernamePasswordAuthenticationToken.unauthenticated(USER, null));
      invalid.add(
          UsernamePasswordAuthenticationToken.authenticated("reader", null, roles("ROLE_USER")));
      invalid.add(
          UsernamePasswordAuthenticationToken.authenticated(
              USER, new char[] {'p'}, roles("ROLE_USER")));
      var details = auth(USER);
      details.setDetails("private-detail");
      invalid.add(details);
      invalid.add(UsernamePasswordAuthenticationToken.authenticated(USER, null, List.of()));
      invalid.add(
          UsernamePasswordAuthenticationToken.authenticated(
              USER, null, roles("ROLE_USER", "ROLE_ADMIN")));
      invalid.add(
          UsernamePasswordAuthenticationToken.authenticated(USER, null, roles("ROLE_ADMIN")));
      GrantedAuthority noText = () -> null;
      invalid.add(UsernamePasswordAuthenticationToken.authenticated(USER, null, List.of(noText)));
      request.getSession().setAttribute("principal", USER);
      for (var value : invalid)
        unavailable(() -> contexts.saveContext(context(value), request, response));
      request.getSession().removeAttribute("principal");
      contexts.saveContext(context(null), request, response);
      contexts.saveContext(context(anonymous()), request, response);
      for (Object value : List.of("bad-principal", context(auth(USER)), 42)) {
        request.getSession().setAttribute("principal", value);
        unavailable(() -> contexts.containsContext(request));
        unavailable(() -> contexts.loadDeferredContext(request).get());
      }
      assertEquals(0, count());
    }
  }

  @Test
  @SuppressWarnings(
      "deprecation") // PT069: required SecurityContextRepository 7.1.1 compatibility API.
  void web069DeferredLoadAndCompatibilityRemainRequestScoped() throws Exception {
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var calls = new AtomicInteger();
      var request =
          new MockHttpServletRequest() {
            @Override
            public HttpSession getSession(boolean create) {
              calls.incrementAndGet();
              return super.getSession(create);
            }
          };
      request.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
      var deferred = contexts.loadDeferredContext(request);
      assertEquals(0, calls.get());
      assertTrue(deferred.isGenerated());
      var first = deferred.get();
      assertNull(first.getAuthentication());
      assertSame(first, deferred.get());
      assertEquals(1, calls.get());
      first.setAuthentication(auth(ADMIN));
      assertTrue(deferred.isGenerated());
      var second = contexts.loadDeferredContext(request);
      assertNotSame(first, second.get());
      assertNull(second.get().getAuthentication());
      assertEquals(2, calls.get());
      assertNull(
          contexts
              .loadContext(new HttpRequestResponseHolder(request, new MockHttpServletResponse()))
              .getAuthentication());
      assertThrows(NullPointerException.class, () -> contexts.loadContext(null));
      assertThrows(
          NullPointerException.class,
          () ->
              contexts.loadContext(
                  new HttpRequestResponseHolder(null, new MockHttpServletResponse())));
      unavailable(() -> contexts.loadDeferredContext(new MockHttpServletRequest()));
      var wrong = marked(adapter(f), new MockHttpSession());
      unavailable(() -> contexts.containsContext(wrong));
      assertEquals(0, count());
    }
  }

  @Test
  void web070SaveOnlyChecksPersistedIdentityWithoutMutation() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now();
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var filter = new WebSessionFilterFactory().create(adapter);
      filter.doFilter(
          request(null),
          new MockHttpServletResponse(),
          (req, res) -> {
            var r = (HttpServletRequest) req;
            contexts.saveContext(context(null), r, (HttpServletResponse) res);
            contexts.saveContext(context(anonymous()), r, (HttpServletResponse) res);
            assertNull(r.getSession(false));
            unavailable(
                () -> contexts.saveContext(context(auth(USER)), r, (HttpServletResponse) res));
          });
      assertEquals(0, count());
      var session = adapter.createSession();
      session.setAttribute("principal", USER);
      String id = session.getId();
      filter.doFilter(
          request(cookie(id)),
          new MockHttpServletResponse(),
          (req, res) -> {
            var r = (HttpServletRequest) req;
            assertTrue(contexts.containsContext(r));
            int commits = f.commits.get();
            var loaded = contexts.loadDeferredContext(r);
            assertFalse(loaded.isGenerated());
            assertIdentity(USER, loaded.get().getAuthentication());
            contexts.saveContext(loaded.get(), r, (HttpServletResponse) res);
            contexts.saveContext(context(auth(USER)), r, (HttpServletResponse) res);
            assertEquals(commits, f.commits.get());
            for (var mismatch :
                List.of(
                    ADMIN,
                    principal("reader", UserRole.ADMIN, "a"),
                    principal("reader", UserRole.USER, "b"),
                    new SessionPrincipal(
                        "reader",
                        UserRole.USER,
                        USER.authenticationContext(),
                        LOGIN.plusMillis(1)))) {
              unavailable(
                  () ->
                      contexts.saveContext(context(auth(mismatch)), r, (HttpServletResponse) res));
            }
            unavailable(() -> contexts.saveContext(context(null), r, (HttpServletResponse) res));
            unavailable(
                () -> contexts.saveContext(context(anonymous()), r, (HttpServletResponse) res));
          });
      assertEquals(1, count());
      adapter.deleteById(id);
      filter.doFilter(
          request(cookie(id)),
          new MockHttpServletResponse(),
          (req, res) ->
              unavailable(
                  () ->
                      contexts.saveContext(
                          context(auth(USER)),
                          (HttpServletRequest) req,
                          (HttpServletResponse) res)));
      assertEquals(0, count());
    }
  }

  @Test
  void web071StrategyFixatesOncePreservingApprovedAttributes() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now();
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var strategy = new EncryptedSessionAuthenticationStrategy(contexts);
      var initial = adapter.createSession();
      initial.setAttribute("savedRequest", "/logs?q=abc");
      initial.setAttribute("operationTokens", SessionAttributeCodecTest.tokens(2));
      var original = initial.getId();
      assertEquals("02".repeat(32), initial.getAttribute("csrfToken"));
      var response = new MockHttpServletResponse();
      new WebSessionFilterFactory()
          .create(adapter)
          .doFilter(
              request(cookie(original)),
              response,
              (req, res) -> {
                var r = (HttpServletRequest) req;
                strategy.onAuthentication(auth(ADMIN), r, (HttpServletResponse) res);
                var session = r.getSession(false);
                assertNotNull(session);
                assertNotEquals(original, session.getId());
                assertEquals("04".repeat(32), session.getAttribute("csrfToken"));
                assertEquals("/logs?q=abc", session.getAttribute("savedRequest"));
                assertEquals(
                    SessionAttributeCodecTest.tokens(2), session.getAttribute("operationTokens"));
                assertEquals(
                    Set.of("principal", "csrfToken", "savedRequest", "operationTokens"),
                    Collections.list(session.getAttributeNames()).stream()
                        .collect(java.util.stream.Collectors.toSet()));
                contexts.saveContext(context(auth(ADMIN)), r, (HttpServletResponse) res);
                assertEquals(2, f.ids.get());
              });
      Cookie issued = Objects.requireNonNull(response.getCookie("SCHUBERT_NK_SESSION"));
      assertNotEquals(original, issued.getValue());
      assertTrue(issued.getSecure());
      assertTrue(issued.isHttpOnly());
      assertEquals("Lax", issued.getAttribute("SameSite"));
      assertEquals("/", issued.getPath());
      assertNull(issued.getDomain());
      assertEquals(-1, issued.getMaxAge());
      assertNull(adapter.findById(original));
      var persisted = f.repository.find(WebSessionId.parse(issued.getValue())).orElseThrow();
      assertEquals(new UUID(0, 2), persisted.row().identity().id());
      assertEquals(ADMIN, persisted.attributes().principal().orElseThrow());
      assertEquals("04".repeat(32), persisted.attributes().csrfToken().orElseThrow());
      assertEquals(1, count());
      // Independent JSON expected by explicit literal/field values, not production encode.
      var json =
          new String(
              new SessionAttributeCodec().encode(persisted.attributes()), StandardCharsets.UTF_8);
      assertTrue(json.contains("\"username\":\"operator\""));
      assertTrue(json.contains("\"role\":\"ADMIN\""));
      assertTrue(json.contains("\"loginAt\":\"2026-09-08T00:00:00.123Z\""));
      assertFalse(json.contains("SPRING_SECURITY_CONTEXT"));
      assertFalse(json.contains("credentials"));
    }
  }

  @Test
  void web072NullConfigurationAndStorageFaultsFailClosed() throws Exception {
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var strategy = new EncryptedSessionAuthenticationStrategy(contexts);
      var r = marked(adapter, null);
      var response = new MockHttpServletResponse();
      assertThrows(
          NullPointerException.class, () -> new EncryptedSessionSecurityContextRepository(null));
      assertThrows(
          NullPointerException.class, () -> new EncryptedSessionAuthenticationStrategy(null));
      assertThrows(NullPointerException.class, () -> contexts.loadDeferredContext(null));
      assertThrows(NullPointerException.class, () -> contexts.containsContext(null));
      assertThrows(NullPointerException.class, () -> contexts.saveContext(null, r, response));
      assertThrows(
          NullPointerException.class, () -> contexts.saveContext(context(null), null, response));
      assertThrows(NullPointerException.class, () -> contexts.saveContext(context(null), r, null));
      assertThrows(NullPointerException.class, () -> strategy.onAuthentication(null, r, response));
      assertThrows(
          NullPointerException.class, () -> strategy.onAuthentication(auth(USER), null, response));
      assertThrows(
          NullPointerException.class, () -> strategy.onAuthentication(auth(USER), r, null));
      loginUnavailable(() -> strategy.onAuthentication(auth(USER), r, response));
      loginUnavailable(() -> strategy.onAuthentication(anonymous(), r, response));
      loginUnavailable(
          () ->
              strategy.onAuthentication(
                  new TestingAuthenticationToken("x", "secret"), r, response));
      loginUnavailable(
          () -> strategy.onAuthentication(auth(USER), new MockHttpServletRequest(), response));
      for (boolean illegalState : new boolean[] {false, true}) {
        var faulty =
            new MockHttpSession() {
              private RuntimeException fault() {
                return illegalState
                    ? new IllegalStateException("private")
                    : new IllegalArgumentException("private");
              }

              @Override
              public Object getAttribute(String name) {
                throw fault();
              }

              @Override
              public void setAttribute(String name, Object value) {
                throw fault();
              }
            };
        var injected = marked(adapter, faulty);
        unavailable(() -> contexts.containsContext(injected));
        loginUnavailable(() -> strategy.onAuthentication(auth(USER), injected, response));
        var getFailure =
            new MockHttpServletRequest() {
              @Override
              public HttpSession getSession(boolean create) {
                if (illegalState) throw new IllegalStateException("private");
                throw new IllegalArgumentException("private");
              }
            };
        getFailure.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
        unavailable(() -> contexts.containsContext(getFailure));
        loginUnavailable(() -> strategy.onAuthentication(auth(USER), getFailure, response));
      }
      assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
      assertEquals(0, count());
    }
    for (String fault :
        List.of(
            "open", "statement.executeUpdate", "connection.commit", "connection.close", "key")) {
      reset();
      try (var f = new Fixture(db)) {
        f.clock.value = Instant.now();
        var adapter = adapter(f);
        var contexts = new EncryptedSessionSecurityContextRepository(adapter);
        var strategy = new EncryptedSessionAuthenticationStrategy(contexts);
        var session = adapter.createSession();
        var response = new MockHttpServletResponse();
        // Failure after anonymous session was loaded, exactly at authentication persistence.
        unavailable(
            () ->
                new WebSessionFilterFactory()
                    .create(adapter)
                    .doFilter(
                        request(cookie(session.getId())),
                        response,
                        (req, res) -> {
                          var r = (HttpServletRequest) req;
                          assertNotNull(r.getSession(false));
                          if (fault.equals("key")) f.codec.close();
                          else f.failure = fault;
                          loginUnavailable(
                              () ->
                                  strategy.onAuthentication(
                                      auth(USER), r, (HttpServletResponse) res));
                          assertNull(r.getSession(false).getAttribute("principal"));
                          ((HttpServletResponse) res).setStatus(503);
                          // Existing failure remains: filter must also reject committing its old
                          // snapshot.
                        }));
        assertEquals(503, response.getStatus());
        assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
        f.failure = "";
        assertEquals(1, count()); // Commit-close fault may have committed new row; never success.
      }
    }
  }

  @Test
  void web073ConcurrentLoadAndStaleRequestsNeverResurrect() throws Exception {
    try (var f = new Fixture(db);
        var pool = Executors.newFixedThreadPool(8)) {
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var calls = new AtomicInteger();
      var r =
          new MockHttpServletRequest() {
            @Override
            public HttpSession getSession(boolean create) {
              calls.incrementAndGet();
              return super.getSession(create);
            }
          };
      var session = new MockHttpSession();
      session.setAttribute("principal", USER);
      r.setSession(session);
      r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
      var deferred = contexts.loadDeferredContext(r);
      var jobs = new ArrayList<Callable<SecurityContext>>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            () -> {
              assertFalse(deferred.isGenerated());
              return deferred.get();
            });
      synchronized (contexts) {
        synchronized (deferred) {
          for (var result : pool.invokeAll(jobs))
            assertSame(deferred.get(), result.get(10, TimeUnit.SECONDS));
        }
      }
      assertEquals(1, calls.get());
      assertIdentity(USER, deferred.get().getAuthentication());
      var other = new MockHttpSession();
      other.setAttribute("principal", ADMIN);
      assertIdentity(
          ADMIN, contexts.loadDeferredContext(marked(adapter, other)).get().getAuthentication());
      f.clock.value = Instant.now();
      var real = adapter.createSession();
      real.setAttribute("principal", USER);
      String id = real.getId();
      var response = new MockHttpServletResponse();
      unavailable(
          () ->
              new WebSessionFilterFactory()
                  .create(adapter)
                  .doFilter(
                      request(cookie(id)),
                      response,
                      (req, res) -> {
                        var request = (HttpServletRequest) req;
                        var loaded = contexts.loadDeferredContext(request).get();
                        adapter.deleteById(id);
                        contexts.saveContext(loaded, request, (HttpServletResponse) res);
                        loaded.setAuthentication(auth(ADMIN));
                        unavailable(
                            () -> contexts.saveContext(loaded, request, (HttpServletResponse) res));
                      }));
      assertEquals(0, count());
      assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
    }
  }

  @Test
  void web074RealHolderFilterRestoresAndClearsThreadContext() throws Exception {
    try (var f = new Fixture(db)) {
      f.clock.value = Instant.now();
      var adapter = adapter(f);
      for (var p : List.of(USER, ADMIN)) {
        var session = adapter.createSession();
        session.setAttribute("principal", p);
        String id = session.getId();
        for (boolean failure : new boolean[] {false, true}) {
          // New repository/filter instances simulate process-local cache loss with the same DB/key.
          var restarted = adapter(f);
          var contexts = new EncryptedSessionSecurityContextRepository(restarted);
          var holder = new SecurityContextHolderFilter(contexts);
          Executable run =
              () ->
                  new WebSessionFilterFactory()
                      .create(restarted)
                      .doFilter(
                          request(cookie(id)),
                          new MockHttpServletResponse(),
                          (req, res) ->
                              holder.doFilter(
                                  req,
                                  res,
                                  (inner, output) -> {
                                    assertIdentity(
                                        p, SecurityContextHolder.getContext().getAuthentication());
                                    if (failure)
                                      throw new ServletException("synthetic controller failure");
                                  }));
          if (failure) assertThrows(ServletException.class, run);
          else assertDoesNotThrow(run);
          assertNull(SecurityContextHolder.getContext().getAuthentication());
        }
      }
      var expired = adapter.createSession();
      expired.setAttribute("principal", USER);
      String expiredId = expired.getId();
      f.clock.value = f.clock.value.plusSeconds(28801);
      assertAnonymous(adapter, cookie(expiredId));
      var corrupt = adapter.createSession();
      corrupt.setAttribute("principal", ADMIN);
      try (var c = db.web();
          var s = c.createStatement()) {
        assertTrue(
            s.executeUpdate(
                    "update schubert_web_session.web_http_sessions set attributes_ciphertext=decode(repeat('00', 40), 'hex')")
                > 0);
      }
      assertAnonymous(adapter, cookie(corrupt.getId()));
      assertAnonymous(adapter, cookie("bad"));
      assertAnonymous(adapter, null);
    }
  }

  @Test
  void web075ProviderFixationAndRestoreStayBoundAcrossRequests() throws Exception {
    for (String result : List.of("0000", "0200", "REVOKED")) {
      reset();
      try (var f = new Fixture(db)) {
        f.clock.value = Instant.now();
        var adapter = adapter(f);
        var contexts = new EncryptedSessionSecurityContextRepository(adapter);
        var strategy = new EncryptedSessionAuthenticationStrategy(contexts);
        var initial = adapter.createSession();
        var client =
            new JmsRequestReplyClient(
                new ReplyCorrelationRegistry(), Clock.fixed(LOGIN, ZoneOffset.UTC), 12);
        var ids = new AtomicInteger();
        var probes = new AtomicInteger();
        var wireClock = Clock.fixed(LOGIN, ZoneOffset.UTC);
        var login =
            new MqLoginClient(
                client,
                (id, body) -> {
                  assertEquals("LGNREQ01", new String(body, 11, 8, StandardCharsets.US_ASCII));
                  var reply = reply(id, "LGNRSP01", result.equals("0000") ? "0000" : "0200", null);
                  assertTrue(client.onReply(id, reply));
                  Arrays.fill(reply, (byte) 0);
                },
                wireClock,
                () -> new UUID(0, ids.incrementAndGet()),
                Duration.ofSeconds(2));
        var probe =
            new MqLoginContextProbe(
                client,
                (id, body) -> {
                  probes.incrementAndGet();
                  assertEquals(
                      "a".repeat(64), new String(body, 113, 64, StandardCharsets.US_ASCII));
                  var reply =
                      reply(
                          id,
                          "GAMRSP01",
                          result.equals("REVOKED") ? "0102" : "0000",
                          "a".repeat(64));
                  assertTrue(client.onReply(id, reply));
                  Arrays.fill(reply, (byte) 0);
                },
                wireClock,
                () -> new UUID(0, ids.incrementAndGet()),
                Duration.ofSeconds(2));
        var provider = new MqAuthenticationProvider(login, probe);
        var response = new MockHttpServletResponse();
        new WebSessionFilterFactory()
            .create(adapter)
            .doFilter(
                request(cookie(initial.getId())),
                response,
                (req, res) -> {
                  var r = (HttpServletRequest) req;
                  char[] secret = {'p'};
                  var input = UsernamePasswordAuthenticationToken.unauthenticated("reader", secret);
                  input.setDetails(new LoginClientAddress("127.0.0.1"));
                  if (result.equals("REVOKED")) {
                    assertThrows(BadCredentialsException.class, () -> provider.authenticate(input));
                    assertNull(r.getSession().getAttribute("principal"));
                    assertEquals("02".repeat(32), r.getSession().getAttribute("csrfToken"));
                    ((HttpServletResponse) res).setStatus(401);
                  } else {
                    var authenticated = provider.authenticate(input);
                    strategy.onAuthentication(authenticated, r, (HttpServletResponse) res);
                    contexts.saveContext(context(authenticated), r, (HttpServletResponse) res);
                    assertEquals("04".repeat(32), r.getSession().getAttribute("csrfToken"));
                    ((HttpServletResponse) res).setStatus(204);
                  }
                  assertNull(input.getCredentials());
                  assertArrayEquals(new char[1], secret);
                });
        assertEquals(result.equals("0000") ? 0 : 1, probes.get());
        assertEquals(0, client.pendingCount());
        if (result.equals("REVOKED")) {
          assertEquals(401, response.getStatus());
          assertNull(response.getCookie("SCHUBERT_NK_SESSION"));
        } else {
          assertEquals(204, response.getStatus());
          var next = Objects.requireNonNull(response.getCookie("SCHUBERT_NK_SESSION"));
          new WebSessionFilterFactory()
              .create(adapter)
              .doFilter(
                  request(next),
                  new MockHttpServletResponse(),
                  (req, res) -> {
                    assertIdentity(
                        USER,
                        contexts
                            .loadDeferredContext((HttpServletRequest) req)
                            .get()
                            .getAuthentication());
                    assertEquals(
                        "04".repeat(32),
                        ((HttpServletRequest) req).getSession().getAttribute("csrfToken"));
                  });
        }
      }
    }
  }

  private static SessionPrincipal principal(String user, UserRole role, String context) {
    return new SessionPrincipal(user, role, AuthenticationContext.of(context.repeat(64)), LOGIN);
  }

  private static SpringEncryptedSessionRepository adapter(Fixture f) {
    return new SpringEncryptedSessionRepository(f.repository, f.clock);
  }

  private static List<SimpleGrantedAuthority> roles(String... roles) {
    return Arrays.stream(roles).map(SimpleGrantedAuthority::new).toList();
  }

  private static UsernamePasswordAuthenticationToken auth(SessionPrincipal p) {
    return UsernamePasswordAuthenticationToken.authenticated(
        p, null, roles("ROLE_" + p.role().wireValue()));
  }

  private static Authentication anonymous() {
    return new AnonymousAuthenticationToken(
        "synthetic-key", "anonymousUser", roles("ROLE_ANONYMOUS"));
  }

  private static SecurityContext context(Authentication auth) {
    var value = new SecurityContextImpl();
    value.setAuthentication(auth);
    return value;
  }

  private static MockHttpServletRequest marked(
      SpringEncryptedSessionRepository adapter, MockHttpSession session) {
    var r = new MockHttpServletRequest();
    r.setAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR, adapter);
    if (session != null) r.setSession(session);
    return r;
  }

  private static Cookie cookie(String value) {
    return new Cookie("SCHUBERT_NK_SESSION", value);
  }

  private static MockHttpServletRequest request(Cookie cookie) {
    var r = new MockHttpServletRequest("GET", "/logs");
    r.setSecure(true);
    if (cookie != null) r.setCookies(cookie);
    return r;
  }

  private static void assertIdentity(SessionPrincipal p, Authentication actual) {
    assertNotNull(actual);
    assertTrue(actual.isAuthenticated());
    assertEquals(p, actual.getPrincipal());
    assertEquals(p.username(), actual.getName());
    assertEquals(
        List.of("ROLE_" + p.role().wireValue()),
        actual.getAuthorities().stream().map(GrantedAuthority::getAuthority).toList());
    assertNull(actual.getCredentials());
    assertNull(actual.getDetails());
  }

  private static void unavailable(Executable action) {
    var e = assertThrows(SessionStoreException.class, action);
    assertEquals("session storage is unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void loginUnavailable(Executable action) {
    var e = assertThrows(SessionAuthenticationException.class, action);
    assertEquals("login session is unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  private static void assertAnonymous(SpringEncryptedSessionRepository adapter, Cookie cookie)
      throws Exception {
    var contexts = new EncryptedSessionSecurityContextRepository(adapter);
    var holder = new SecurityContextHolderFilter(contexts);
    new WebSessionFilterFactory()
        .create(adapter)
        .doFilter(
            request(cookie),
            new MockHttpServletResponse(),
            (req, res) ->
                holder.doFilter(
                    req,
                    res,
                    (inner, output) ->
                        assertNull(SecurityContextHolder.getContext().getAuthentication())));
    assertNull(SecurityContextHolder.getContext().getAuthentication());
  }

  /** Independent UI232/234 offset oracle. Synthetic in-memory wire only, never evidence body. */
  static byte[] reply(UUID id, String layout, String code, String apiContext) {
    boolean login = layout.equals("LGNRSP01");
    byte[] wire = new byte[login ? 688 : 265];
    Arrays.fill(wire, (byte) ' ');
    put(wire, 0, "SCHBNK01");
    put(wire, 8, "001");
    put(wire, 11, layout);
    put(wire, 19, "001SS");
    put(wire, 24, new UUID(1, 1).toString());
    put(wire, 60, id.toString());
    put(wire, 96, "20260908090000123");
    if (apiContext != null) put(wire, 113, apiContext);
    put(wire, 177, login ? "0256000432000000000000000000688" : "0256000009000272000000000000265");
    put(wire, 208, code);
    if (login) {
      put(wire, 256, "reader");
      put(wire, 320, "USER");
      put(wire, 325, "a".repeat(64));
      put(wire, 389, "2026090809000012320260908170000123000000000");
    } else put(wire, 256, "000000000");
    return wire;
  }

  static void put(byte[] wire, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, wire, offset, text.length);
  }
}
