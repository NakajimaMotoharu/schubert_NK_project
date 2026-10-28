package dev.codex.schubert.nk.web.session;

import static dev.codex.schubert.nk.web.session.SessionSecurityContextTest.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.CaddyClientAddressResolver;
import dev.codex.schubert.nk.web.security.CaddyRequestRejectedException;
import dev.codex.schubert.nk.web.security.EncryptedSessionCsrfTokenRepository;
import dev.codex.schubert.nk.web.security.EncryptedSessionRequestCache;
import dev.codex.schubert.nk.web.security.EncryptedSessionSecurityContextRepository;
import dev.codex.schubert.nk.web.security.LoginClientAddress;
import dev.codex.schubert.nk.web.security.LoginFormAuthenticationConverter;
import dev.codex.schubert.nk.web.security.LoginFormRejectedException;
import dev.codex.schubert.nk.web.security.MqAuthenticationProvider;
import dev.codex.schubert.nk.web.security.MqFormLoginFilterFactory;
import dev.codex.schubert.nk.web.security.MqLoginClient;
import dev.codex.schubert.nk.web.security.MqLoginContextProbe;
import dev.codex.schubert.nk.web.security.MqLoginLockedException;
import dev.codex.schubert.nk.web.security.WebCsrfFilterFactory;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepositoryTest.Fixture;
import jakarta.jms.JMSException;
import jakarta.servlet.Filter;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;
import jakarta.servlet.http.HttpServletResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.SecureRandom;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;
import java.util.Locale;
import java.util.NoSuchElementException;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
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
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.security.web.authentication.session.SessionAuthenticationException;
import org.springframework.security.web.context.SecurityContextHolderFilter;

/** NK-WEB-001/PT-WEB-082..089; FUN-001/AUT-001..004; UI226/232/234; SS313/314/342/352. */
class SessionFormLoginTest {
  private static final String FIXTURE_203_0_113_1_9BB16FDC = "203.0.113.1";
  private static final String FIXTURE_READER_F734AAEA = "reader";
  private static final String FIXTURE_X_FORWARDED_FOR_BECAABD0 = "X-Forwarded-For";
  private static final String FIXTURE_X_FORWARDED_PROTO_6D975CE8 = "X-Forwarded-Proto";
  private static final String FIXTURE_NULL_61DEF1DB = "NULL";
  private static final String FIXTURE_ELEMENT_EECFA3AA = "ELEMENT";
  private static final String FIXTURE_STATE_053339C0 = "STATE";
  private static final String FIXTURE_ARGUMENT_DFF41B69 = "ARGUMENT";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_PASSWORD_FF2BEA10 = "password";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_CSRFTOKEN_CF3CFD11 = "csrfToken";
  private static final String FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF = "SCHUBERT_NK_SESSION";
  private static final String FIXTURE_UNUSED_5A9D5965 = "unused";
  private static final String FIXTURE_LOCK900_8CB1A8F9 = "LOCK900";
  private static final String FIXTURE_JMS_1AEA59D9 = "JMS";
  private static final String FIXTURE_REVOKED_303CE38D = "REVOKED";
  private static final String FIXTURE_FORM_0339FF30 = "FORM";
  private static final String FIXTURE_PROXY_F127C282 = "PROXY";
  private static final String FIXTURE_PRIVATE_PARAMETER_840BC11E = "private-parameter";
  private static WebLogDatabaseFixture db;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-08T00:00:00.123Z"), ZoneOffset.UTC);

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
  void web082OnlyDirectLoopbackCaddyHeadersSupplyClientAddress() {
    var resolver = new CaddyClientAddressResolver();
    for (String peer : List.of("127.0.0.1", "127.255.0.1", "::1", "::ffff:127.0.0.1")) {
      for (String client :
          List.of(
              FIXTURE_203_0_113_1_9BB16FDC,
              "2001:db8::1",
              "0:0:0:0:0:0:0:1",
              "ffff:ffff:ffff:ffff:ffff:ffff:255.255.255.255")) {
        var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
        r.setRemoteAddr(peer);
        r.removeHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0);
        r.addHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0, client);
        assertEquals(client, resolver.resolve(r).value());
        assertNull(r.getSession(false));
      }
    }
    for (String peer :
        List.of(
            FIXTURE_203_0_113_1_9BB16FDC,
            "2001:db8::1",
            "localhost",
            "",
            "::1%1",
            "127.0.0.1, 203.0.113.1")) {
      var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
      r.setRemoteAddr(peer);
      proxyRejected(() -> resolver.resolve(r));
    }
    for (String client :
        List.of(
            "",
            "localhost",
            "203.0.113.1, 203.0.113.2",
            " 203.0.113.1",
            "fe80::1%1",
            "203.0.113.999")) {
      var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
      r.removeHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0);
      r.addHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0, client);
      proxyRejected(() -> resolver.resolve(r));
    }
    for (String header :
        List.of(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_X_FORWARDED_PROTO_6D975CE8)) {
      var missing = form(null, null, FIXTURE_READER_F734AAEA, "p");
      missing.removeHeader(header);
      proxyRejected(() -> resolver.resolve(missing));
      var duplicate = form(null, null, FIXTURE_READER_F734AAEA, "p");
      duplicate.addHeader(header, "synthetic");
      proxyRejected(() -> resolver.resolve(duplicate));
    }
    for (String proto : List.of("", "http", "HTTPS", "https,http")) {
      var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
      r.removeHeader(FIXTURE_X_FORWARDED_PROTO_6D975CE8);
      r.addHeader(FIXTURE_X_FORWARDED_PROTO_6D975CE8, proto);
      proxyRejected(() -> resolver.resolve(r));
    }
    var forwarded = form(null, null, FIXTURE_READER_F734AAEA, "p");
    forwarded.addHeader("Forwarded", "for=203.0.113.9;proto=https");
    proxyRejected(() -> resolver.resolve(forwarded));
  }

  @Test
  void web083ProxyNullFaultsAndConcurrentRequestsAreIsolated() throws Exception {
    var resolver = new CaddyClientAddressResolver();
    assertThrows(NullPointerException.class, () -> resolver.resolve(null));
    var noPeer =
        new MockHttpServletRequest() {
          @Override
          public String getRemoteAddr() {
            return null;
          }
        };
    proxyRejected(() -> resolver.resolve(noPeer));
    for (String header :
        List.of(
            "Forwarded", FIXTURE_X_FORWARDED_PROTO_6D975CE8, FIXTURE_X_FORWARDED_FOR_BECAABD0)) {
      for (String fault :
          List.of(
              FIXTURE_NULL_61DEF1DB,
              FIXTURE_ELEMENT_EECFA3AA,
              FIXTURE_STATE_053339C0,
              FIXTURE_ARGUMENT_DFF41B69,
              "ENUMERATION")) {
        var r =
            new MockHttpServletRequest() {
              @Override
              public Enumeration<String> getHeaders(String name) {
                if (!name.equals(header)) return super.getHeaders(name);
                return switch (fault) {
                  case FIXTURE_NULL_61DEF1DB -> null;
                  case FIXTURE_ELEMENT_EECFA3AA ->
                      Collections.enumeration(Arrays.asList((String) null));
                  case FIXTURE_STATE_053339C0 -> throw new IllegalStateException("private-header");
                  case FIXTURE_ARGUMENT_DFF41B69 ->
                      throw new IllegalArgumentException("private-header");
                  default ->
                      new Enumeration<>() {
                        @Override
                        public boolean hasMoreElements() {
                          return true;
                        }

                        @Override
                        public String nextElement() {
                          throw new NoSuchElementException("private-header");
                        }
                      };
                };
              }
            };
        trusted(r);
        proxyRejected(() -> resolver.resolve(r));
        assertNull(r.getSession(false));
      }
    }
    try (var pool = Executors.newFixedThreadPool(8)) {
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        String client = "203.0.113." + i;
        jobs.add(
            () -> {
              var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
              r.removeHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0);
              r.addHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0, client);
              assertEquals(client, resolver.resolve(r).value());
              assertNull(r.getSession(false));
              return null;
            });
      }
      synchronized (resolver) {
        for (var job : pool.invokeAll(jobs)) job.get(10, TimeUnit.SECONDS);
      }
    }
  }

  @Test
  void web084FormCreatesOnlyConsumableUntrustedCredentials() {
    var converter = new LoginFormAuthenticationConverter(new CaddyClientAddressResolver());
    var api = new Api(FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
    for (String username : List.of(FIXTURE_READER_F734AAEA, " e\u0301 ", "İ".repeat(32))) {
      for (String password : List.of("p", "p".repeat(256), "e\u0301")) {
        for (String type :
            List.of(
                "application/x-www-form-urlencoded",
                "application/x-www-form-urlencoded;charset=UTF-8")) {
          var r = form(null, null, username, password);
          r.setContentType(type);
          r.setQueryString("");
          var input = converter.convert(r);
          assertEquals(UsernamePasswordAuthenticationToken.class, input.getClass());
          assertFalse(input.isAuthenticated());
          assertEquals(username, input.getPrincipal());
          char[] consumed = assertInstanceOf(char[].class, input.getCredentials());
          assertArrayEquals(password.toCharArray(), consumed);
          assertEquals(
              FIXTURE_203_0_113_1_9BB16FDC,
              assertInstanceOf(LoginClientAddress.class, input.getDetails()).value());
          assertNull(r.getSession(false));
          var result = api.provider.authenticate(input);
          assertTrue(result.isAuthenticated());
          assertEquals(
              java.text.Normalizer.normalize(username, java.text.Normalizer.Form.NFC).trim(),
              result.getName());
          assertArrayEquals(new char[consumed.length], consumed);
          assertNull(input.getCredentials());
        }
      }
    }
    // Semantic byte/password rejection remains the client's established independent contract.
    for (String password : List.of("p".repeat(257), "p ", "p\n")) {
      var input = converter.convert(form(null, null, FIXTURE_READER_F734AAEA, password));
      char[] consumed = assertInstanceOf(char[].class, input.getCredentials());
      int before = api.sends.get();
      assertThrows(BadCredentialsException.class, () -> api.provider.authenticate(input));
      assertEquals(before, api.sends.get());
      assertArrayEquals(new char[consumed.length], consumed);
      assertNull(input.getCredentials());
    }
    api.erased();
  }

  @Test
  void web085MalformedAmbiguousFormsNeverReachAuthentication() {
    var converter = new LoginFormAuthenticationConverter(new CaddyClientAddressResolver());
    assertThrows(NullPointerException.class, () -> new LoginFormAuthenticationConverter(null));
    assertThrows(NullPointerException.class, () -> converter.convert(null));
    for (String name : List.of("username", FIXTURE_PASSWORD_FF2BEA10)) {
      for (String[] value :
          Arrays.asList(
              null,
              new String[0],
              new String[] {null},
              new String[] {""},
              new String[] {"one", "two"})) {
        var r =
            new MockHttpServletRequest() {
              @Override
              public String[] getParameterValues(String key) {
                return name.equals(key) ? value : super.getParameterValues(key);
              }
            };
        configureForm(r, FIXTURE_READER_F734AAEA, "p");
        formRejected(() -> converter.convert(r));
        assertNull(r.getSession(false));
      }
    }
    for (String key :
        List.of(
            "username",
            "USERNAME",
            "%75sername",
            FIXTURE_PASSWORD_FF2BEA10,
            "PaSsWoRd",
            "_csrf",
            "%5fcsrf",
            "%GG")) {
      var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
      r.setQueryString("q=other&" + key + "=synthetic");
      formRejected(() -> converter.convert(r));
    }
    for (String type :
        Arrays.asList(
            null,
            "",
            "application/json",
            "text/x-www-form-urlencoded",
            "application/*",
            "bad",
            "application/x-www-form-urlencoded;charset=ISO-8859-1",
            "application/x-www-form-urlencoded;charset=NO_SUCH_CHARSET")) {
      var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
      // Override rather than Mock's eager MediaType parsing, to exercise the public boundary.
      var wrapped =
          new HttpServletRequestWrapper(r) {
            @Override
            public String getContentType() {
              return type;
            }
          };
      formRejected(() -> converter.convert(wrapped));
    }
    for (String encoding : Arrays.asList(null, "ISO-8859-1")) {
      var r =
          new HttpServletRequestWrapper(form(null, null, FIXTURE_READER_F734AAEA, "p")) {
            @Override
            public String getCharacterEncoding() {
              return encoding;
            }
          };
      formRejected(() -> converter.convert(r));
    }
    for (String method : List.of(FIXTURE_GET_04F32A7E, "PUT", "post")) {
      var r = form(null, null, FIXTURE_READER_F734AAEA, "p");
      r.setMethod(method);
      formRejected(() -> converter.convert(r));
    }
    var wrong = form(null, null, FIXTURE_READER_F734AAEA, "p");
    wrong.setRequestURI("/elsewhere");
    formRejected(() -> converter.convert(wrong));
    for (boolean state : new boolean[] {false, true}) {
      var r =
          new HttpServletRequestWrapper(form(null, null, FIXTURE_READER_F734AAEA, "p")) {
            @Override
            public String[] getParameterValues(String name) {
              if (state) throw new IllegalStateException("private-body");
              throw new IllegalArgumentException("private-body");
            }
          };
      formRejected(() -> converter.convert(r));
    }
    var proxy = form(null, null, FIXTURE_READER_F734AAEA, "p");
    proxy.setRemoteAddr("203.0.113.9");
    proxyRejected(() -> converter.convert(proxy));
  }

  @Test
  void web086ActualCsrfProviderFixationAndHolderChainSucceeds() throws Exception {
    for (String code : List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC)) {
      for (String role : List.of(FIXTURE_USER_2DED8884, "ADMIN")) {
        reset();
        try (var f = new Fixture(db)) {
          var adapter = adapter(f);
          var contexts = new EncryptedSessionSecurityContextRepository(adapter);
          var cache = new EncryptedSessionRequestCache(adapter);
          var initial = adapter.createSession();
          initial.setAttribute("savedRequest", "/search?q=abc");
          initial.setAttribute("operationTokens", SessionAttributeCodecTest.tokens(2));
          String oldId = initial.getId();
          var api = new Api(code, role, FIXTURE_0000_876EEFE0, 0);
          var successes = new AtomicInteger();
          var login =
              new MqFormLoginFilterFactory()
                  .create(
                      api.provider,
                      contexts,
                      (r, s, auth) -> {
                        successes.incrementAndGet();
                        assertSame(auth, SecurityContextHolder.getContext().getAuthentication());
                        assertEquals(FIXTURE_READER_F734AAEA, auth.getName());
                        assertEquals(
                            List.of("ROLE_" + role),
                            auth.getAuthorities().stream().map(a -> a.getAuthority()).toList());
                        assertEquals(
                            "04".repeat(32),
                            r.getSession().getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11));
                        assertEquals(2, f.ids.get());
                        assertEquals(
                            SessionAttributeCodecTest.tokens(2),
                            r.getSession().getAttribute("operationTokens"));
                        s.setStatus(302);
                        s.setHeader(
                            "Location",
                            Objects.requireNonNull(cache.getRequest(r, s)).getRedirectUrl());
                      },
                      (r, s, e) -> fail("unexpected authentication failure"));
          var response = new MockHttpServletResponse();
          run(
              adapter,
              login,
              form(
                  new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, oldId),
                  "02".repeat(32),
                  FIXTURE_READER_F734AAEA,
                  "p"),
              response,
              (r, s) -> fail("login should finish at the success handler"));
          assertEquals(302, response.getStatus());
          assertEquals("/search?q=abc", response.getHeader("Location"));
          assertEquals(1, successes.get());
          assertEquals(1, api.sends.get());
          assertEquals(code.equals(FIXTURE_0200_FC9DB3AC) ? 1 : 0, api.probes.get());
          var cookie =
              Objects.requireNonNull(response.getCookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF));
          assertNotEquals(oldId, cookie.getValue());
          assertTrue(cookie.getSecure());
          assertTrue(cookie.isHttpOnly());
          assertEquals("Lax", cookie.getAttribute("SameSite"));
          assertNull(adapter.findById(oldId));
          assertEquals(1, count());
          assertNull(SecurityContextHolder.getContext().getAuthentication());
          var next = form(cookie, null, FIXTURE_UNUSED_5A9D5965, FIXTURE_UNUSED_5A9D5965);
          next.setMethod(FIXTURE_GET_04F32A7E);
          next.setRequestURI("/search");
          next.setQueryString("q=abc");
          run(
              adapter,
              login,
              next,
              new MockHttpServletResponse(),
              (r, s) -> {
                var auth = SecurityContextHolder.getContext().getAuthentication();
                assertNotNull(auth);
                assertEquals(FIXTURE_READER_F734AAEA, auth.getName());
                assertEquals(
                    List.of("ROLE_" + role),
                    auth.getAuthorities().stream().map(a -> a.getAuthority()).toList());
                assertSame(
                    r, cache.getMatchingRequest((HttpServletRequest) r, (HttpServletResponse) s));
              });
          assertNull(SecurityContextHolder.getContext().getAuthentication());
          api.erased();
        }
      }
    }
  }

  @Test
  void web087CsrfAndAuthenticationFailuresNeverGrantOrReplay() throws Exception {
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var api = new Api(FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
      var initial = adapter.createSession();
      var other = adapter.createSession();
      var filter =
          new MqFormLoginFilterFactory()
              .create(
                  api.provider,
                  new EncryptedSessionSecurityContextRepository(adapter),
                  (r, s, a) -> fail("unexpected success"),
                  SessionFormLoginTest::failure);
      String otherToken = other.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11);
      for (String token : Arrays.asList(null, "", "z".repeat(64), otherToken)) {
        var response = new MockHttpServletResponse();
        run(
            adapter,
            filter,
            form(
                new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, initial.getId()),
                token,
                FIXTURE_READER_F734AAEA,
                "p"),
            response,
            (r, s) -> fail("CSRF must reject before downstream"));
        assertEquals(403, response.getStatus());
        assertEquals(0, api.sends.get());
        assertNull(response.getCookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
      }
    }
    for (String condition :
        List.of(
            "0101",
            "LOCK0",
            FIXTURE_LOCK900_8CB1A8F9,
            "9000",
            FIXTURE_JMS_1AEA59D9,
            FIXTURE_REVOKED_303CE38D,
            "PROBE_JMS",
            FIXTURE_FORM_0339FF30,
            FIXTURE_PROXY_F127C282,
            "DB")) {
      reset();
      try (var f = new Fixture(db)) {
        var adapter = adapter(f);
        var initial = adapter.createSession();
        String id = initial.getId();
        String code =
            condition.startsWith("LOCK")
                ? "0106"
                : switch (condition) {
                  case FIXTURE_REVOKED_303CE38D, "PROBE_JMS" -> FIXTURE_0200_FC9DB3AC;
                  case FIXTURE_FORM_0339FF30, FIXTURE_PROXY_F127C282, "DB" -> FIXTURE_0000_876EEFE0;
                  default -> condition;
                };
        var api =
            new Api(
                code,
                FIXTURE_USER_2DED8884,
                condition.equals(FIXTURE_REVOKED_303CE38D)
                    ? "0102"
                    : condition.equals("PROBE_JMS") ? FIXTURE_JMS_1AEA59D9 : FIXTURE_0000_876EEFE0,
                condition.equals(FIXTURE_LOCK900_8CB1A8F9) ? 900 : 0);
        if (condition.equals("DB")) api.afterReply = () -> f.failure = "connection.commit";
        var failures = new AtomicInteger();
        var filter =
            new MqFormLoginFilterFactory()
                .create(
                    api.provider,
                    new EncryptedSessionSecurityContextRepository(adapter),
                    (r, s, a) -> fail("must not grant"),
                    (r, s, e) -> {
                      failures.incrementAndGet();
                      failure(r, s, e);
                    });
        var request =
            form(
                new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, id),
                "02".repeat(32),
                FIXTURE_READER_F734AAEA,
                "p");
        if (condition.equals(FIXTURE_FORM_0339FF30))
          request.addParameter(FIXTURE_PASSWORD_FF2BEA10, "second");
        if (condition.equals(FIXTURE_PROXY_F127C282)) request.setRemoteAddr("203.0.113.9");
        var response = new MockHttpServletResponse();
        Executable action =
            () -> run(adapter, filter, request, response, (r, s) -> fail("login handled here"));
        if (condition.equals("DB")) assertThrows(SessionStoreException.class, action);
        else assertDoesNotThrow(action);
        int expected =
            switch (condition) {
              case "0101", FIXTURE_REVOKED_303CE38D -> 401;
              case "LOCK0", FIXTURE_LOCK900_8CB1A8F9 -> 429;
              case FIXTURE_FORM_0339FF30 -> 400;
              case FIXTURE_PROXY_F127C282 -> 403;
              default -> 503;
            };
        assertEquals(expected, response.getStatus());
        assertEquals(1, failures.get());
        if (condition.startsWith("LOCK"))
          assertEquals(
              condition.equals(FIXTURE_LOCK900_8CB1A8F9) ? "900" : "0",
              response.getHeader("Retry-After"));
        else assertNull(response.getHeader("Retry-After"));
        assertNull(response.getCookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF));
        assertNull(SecurityContextHolder.getContext().getAuthentication());
        assertEquals(
            condition.equals(FIXTURE_FORM_0339FF30) || condition.equals(FIXTURE_PROXY_F127C282)
                ? 0
                : 1,
            api.sends.get());
        f.failure = "";
        var retained = Objects.requireNonNull(adapter.findById(id));
        assertNull(retained.getAttribute("principal"));
        assertNull(retained.getAttribute("SPRING_SECURITY_LAST_EXCEPTION"));
        assertEquals("02".repeat(32), retained.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11));
        assertEquals(1, count());
        api.erased();
      }
    }
  }

  @Test
  void web088FactoryNullMatchingAndExceptionalLifecycleAreBounded() throws Exception {
    try (var f = new Fixture(db)) {
      var adapter = adapter(f);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var api = new Api(FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
      var factory = new MqFormLoginFilterFactory();
      AuthenticationSuccessHandler success = (r, s, a) -> s.setStatus(204);
      AuthenticationFailureHandler failure = SessionFormLoginTest::failure;
      assertThrows(
          NullPointerException.class, () -> factory.create(null, contexts, success, failure));
      assertThrows(
          NullPointerException.class, () -> factory.create(api.provider, null, success, failure));
      assertThrows(
          NullPointerException.class, () -> factory.create(api.provider, contexts, null, failure));
      assertThrows(
          NullPointerException.class, () -> factory.create(api.provider, contexts, success, null));
      var login = factory.create(api.provider, contexts, success, failure);
      login.afterPropertiesSet();
      var initial = adapter.createSession();
      var cookie = new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, initial.getId());
      var nextCalls = new AtomicInteger();
      for (String method : List.of(FIXTURE_GET_04F32A7E, "HEAD", "POST")) {
        var request =
            form(cookie, "02".repeat(32), FIXTURE_UNUSED_5A9D5965, FIXTURE_UNUSED_5A9D5965);
        request.setMethod(method);
        request.setRequestURI(method.equals("POST") ? "/questions/new" : "/login");
        run(
            adapter,
            login,
            request,
            new MockHttpServletResponse(),
            (r, s) -> nextCalls.incrementAndGet());
      }
      assertEquals(3, nextCalls.get());
      assertEquals(0, api.sends.get());
      var request = form(cookie, null, FIXTURE_UNUSED_5A9D5965, FIXTURE_UNUSED_5A9D5965);
      request.setMethod(FIXTURE_GET_04F32A7E);
      request.setRequestURI("/search");
      assertThrows(
          ServletException.class,
          () ->
              run(
                  adapter,
                  login,
                  request,
                  new MockHttpServletResponse(),
                  (r, s) -> {
                    throw new ServletException("synthetic-controller");
                  }));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      var throwingSuccess =
          factory.create(
              api.provider,
              contexts,
              (r, s, a) -> {
                assertNotNull(SecurityContextHolder.getContext().getAuthentication());
                throw new ServletException("synthetic-handler");
              },
              failure);
      assertThrows(
          ServletException.class,
          () ->
              run(
                  adapter,
                  throwingSuccess,
                  form(cookie, "02".repeat(32), FIXTURE_READER_F734AAEA, "p"),
                  new MockHttpServletResponse(),
                  (r, s) -> fail("not reached")));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      var another = adapter.createSession();
      String csrf = another.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11);
      var rejected = new Api("0101", FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
      var throwingFailure =
          factory.create(
              rejected.provider,
              contexts,
              success,
              (r, s, e) -> {
                assertNull(SecurityContextHolder.getContext().getAuthentication());
                throw new ServletException("synthetic-failure-handler");
              });
      assertThrows(
          ServletException.class,
          () ->
              run(
                  adapter,
                  throwingFailure,
                  form(
                      new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, another.getId()),
                      csrf,
                      FIXTURE_READER_F734AAEA,
                      "p"),
                  new MockHttpServletResponse(),
                  (r, s) -> fail("not reached")));
      assertNull(SecurityContextHolder.getContext().getAuthentication());
      api.erased();
      rejected.erased();
    }
  }

  @Test
  void web089ConcurrentLoginChainsKeepPrincipalsAndCookiesSeparate() throws Exception {
    try (var f = new Fixture(db);
        var pool = Executors.newFixedThreadPool(8)) {
      f.clock.value = Instant.now();
      // Real random avoids wrapping the byte-sized deterministic sequence after200 issued IDs.
      var lifecycle =
          new EncryptedWebSessionRepository(
              f.source, f.codec, f.clock, new SecureRandom(), UUID::randomUUID);
      var adapter = new SpringEncryptedSessionRepository(lifecycle, f.clock);
      var contexts = new EncryptedSessionSecurityContextRepository(adapter);
      var api = new Api(FIXTURE_0000_876EEFE0, "DYNAMIC", FIXTURE_0000_876EEFE0, 0);
      var login =
          new MqFormLoginFilterFactory()
              .create(
                  api.provider,
                  contexts,
                  (r, s, auth) -> {
                    assertSame(auth, SecurityContextHolder.getContext().getAuthentication());
                    s.setStatus(204);
                  },
                  (r, s, e) -> fail("concurrent Login must succeed"));
      var newCookies = ConcurrentHashMap.<String>newKeySet();
      var jobs = new ArrayList<Callable<Void>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        var initial = adapter.createSession();
        String id = initial.getId();
        String csrf = initial.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11);
        jobs.add(
            () -> {
              var response = new MockHttpServletResponse();
              run(
                  adapter,
                  login,
                  form(
                      new Cookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF, id),
                      csrf,
                      "user" + n,
                      "password-user" + n),
                  response,
                  (r, s) -> fail("not reached"));
              assertEquals(204, response.getStatus());
              assertNull(SecurityContextHolder.getContext().getAuthentication());
              String current =
                  Objects.requireNonNull(response.getCookie(FIXTURE_SCHUBERT_NK_SESSION_DD9EE5FF))
                      .getValue();
              assertNotEquals(id, current);
              assertTrue(newCookies.add(current));
              assertNull(adapter.findById(id));
              var restored = Objects.requireNonNull(adapter.findById(current));
              SessionPrincipal p = restored.getAttribute("principal");
              assertNotNull(p);
              assertEquals("user" + n, p.username());
              assertEquals(n % 2 == 0 ? FIXTURE_USER_2DED8884 : "ADMIN", p.role().wireValue());
              assertEquals(
                  String.format(Locale.ROOT, "%064x", n + 1),
                  p.authenticationContext().wireValue());
              assertNotEquals(csrf, restored.getAttribute(FIXTURE_CSRFTOKEN_CF3CFD11));
              return null;
            });
      }
      synchronized (login) {
        for (var job : pool.invokeAll(jobs)) job.get(30, TimeUnit.SECONDS);
      }
      assertEquals(100, newCookies.size());
      assertEquals(100, api.sends.get());
      assertEquals(0, api.probes.get());
      assertEquals(100, count());
      api.erased();
    }
  }

  @Test
  void web090UnknownFormNamesAndEnumerationFaultsNeverAuthenticate() {
    var converter = new LoginFormAuthenticationConverter(new CaddyClientAddressResolver());
    var api = new Api(FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, 0);
    for (String name : List.of("role", "", "Username", "Password", "_CSRF", "unknown", "q")) {
      var request = form(null, "01".repeat(32), FIXTURE_READER_F734AAEA, "p");
      request.addParameter(name, "synthetic");
      // Servlet merges decoded query and body parameter names; Mock setQueryString alone does not.
      if (name.equals("q")) request.setQueryString("q=synthetic");
      formRejected(() -> api.provider.authenticate(converter.convert(request)));
      assertNull(request.getSession(false));
      assertEquals(0, api.sends.get());
    }
    for (String fault :
        List.of(
            FIXTURE_NULL_61DEF1DB,
            FIXTURE_ELEMENT_EECFA3AA,
            "HAS",
            "NEXT",
            FIXTURE_STATE_053339C0,
            FIXTURE_ARGUMENT_DFF41B69)) {
      var request =
          new HttpServletRequestWrapper(form(null, null, FIXTURE_READER_F734AAEA, "p")) {
            @Override
            public Enumeration<String> getParameterNames() {
              if (fault.equals(FIXTURE_NULL_61DEF1DB)) return null;
              if (fault.equals(FIXTURE_ELEMENT_EECFA3AA))
                return Collections.enumeration(Arrays.asList((String) null));
              if (fault.equals(FIXTURE_STATE_053339C0))
                throw new IllegalStateException(FIXTURE_PRIVATE_PARAMETER_840BC11E);
              if (fault.equals(FIXTURE_ARGUMENT_DFF41B69))
                throw new IllegalArgumentException(FIXTURE_PRIVATE_PARAMETER_840BC11E);
              return new Enumeration<>() {
                @Override
                public boolean hasMoreElements() {
                  if (fault.equals("HAS"))
                    throw new NoSuchElementException(FIXTURE_PRIVATE_PARAMETER_840BC11E);
                  return true;
                }

                @Override
                public String nextElement() {
                  throw new NoSuchElementException(FIXTURE_PRIVATE_PARAMETER_840BC11E);
                }
              };
            }
          };
      formRejected(() -> api.provider.authenticate(converter.convert(request)));
      assertNull(request.getSession(false));
      assertEquals(0, api.sends.get());
    }
  }

  private static void trusted(MockHttpServletRequest r) {
    r.setRemoteAddr("127.0.0.1");
    r.addHeader(FIXTURE_X_FORWARDED_FOR_BECAABD0, FIXTURE_203_0_113_1_9BB16FDC);
    r.addHeader(FIXTURE_X_FORWARDED_PROTO_6D975CE8, "https");
  }

  private static void configureForm(MockHttpServletRequest r, String username, String password) {
    r.setMethod("POST");
    r.setRequestURI("/login");
    r.setCharacterEncoding(StandardCharsets.UTF_8);
    r.setContentType("application/x-www-form-urlencoded");
    trusted(r);
    r.addParameter("username", username);
    r.addParameter(FIXTURE_PASSWORD_FF2BEA10, password);
  }

  private static MockHttpServletRequest form(
      Cookie cookie, String csrf, String username, String password) {
    var r = new MockHttpServletRequest();
    configureForm(r, username, password);
    if (cookie != null) r.setCookies(cookie);
    if (csrf != null) r.addParameter("_csrf", csrf);
    return r;
  }

  private static void proxyRejected(Executable action) {
    var e = assertThrows(CaddyRequestRejectedException.class, action);
    assertEquals("request proxy is invalid", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static void formRejected(Executable action) {
    var e = assertThrows(LoginFormRejectedException.class, action);
    assertEquals("login form is invalid", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  private static SpringEncryptedSessionRepository adapter(Fixture f) {
    f.clock.value = Instant.now();
    return new SpringEncryptedSessionRepository(f.repository, f.clock);
  }

  private static void failure(
      HttpServletRequest request, HttpServletResponse response, AuthenticationException failure) {
    if (failure instanceof CaddyRequestRejectedException) response.setStatus(403);
    else if (failure instanceof LoginFormRejectedException) response.setStatus(400);
    else if (failure instanceof MqLoginLockedException locked) {
      response.setStatus(429);
      response.setHeader("Retry-After", Integer.toString(locked.retryAfterSeconds()));
    } else if (failure instanceof BadCredentialsException) response.setStatus(401);
    else {
      assertTrue(
          failure instanceof AuthenticationServiceException
              || failure instanceof SessionAuthenticationException);
      response.setStatus(503);
    }
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void run(
      SpringEncryptedSessionRepository adapter,
      Filter login,
      MockHttpServletRequest request,
      MockHttpServletResponse response,
      FilterChain business)
      throws Exception {
    var holder =
        new SecurityContextHolderFilter(new EncryptedSessionSecurityContextRepository(adapter));
    var csrf =
        new WebCsrfFilterFactory()
            .create(new EncryptedSessionCsrfTokenRepository(), (r, s, e) -> s.setStatus(403));
    new WebSessionFilterFactory()
        .create(adapter)
        .doFilter(
            request,
            response,
            (r, s) ->
                holder.doFilter(
                    r,
                    s,
                    (r2, s2) ->
                        csrf.doFilter(r2, s2, (r3, s3) -> login.doFilter(r3, s3, business))));
  }

  private static int count() throws Exception {
    try (var c = db.web();
        var s = c.createStatement();
        var r = s.executeQuery("select count(*) from schubert_web_session.web_http_sessions")) {
      assertTrue(r.next());
      return r.getInt(1);
    }
  }

  static final class Api {
    Runnable afterReply = () -> {};
    final AtomicInteger ids = new AtomicInteger();
    final AtomicInteger sends = new AtomicInteger();
    final AtomicInteger probes = new AtomicInteger();
    final List<byte[]> buffers = Collections.synchronizedList(new ArrayList<>());
    final JmsRequestReplyClient client =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final MqAuthenticationProvider provider;

    Api(String code, String role, String probeCode, int retry) {
      var login =
          new MqLoginClient(
              client,
              (id, body) -> {
                sends.incrementAndGet();
                buffers.add(body);
                if (code.equals(FIXTURE_JMS_1AEA59D9)) throw new JMSException("synthetic-private");
                String username = new String(body, 256, 64, StandardCharsets.UTF_8).stripTrailing();
                String context = "a".repeat(64);
                String assignedRole = role;
                if (role.equals("DYNAMIC")) {
                  int n = Integer.parseInt(username.substring(4));
                  context = String.format(Locale.ROOT, "%064x", n + 1);
                  assignedRole = n % 2 == 0 ? FIXTURE_USER_2DED8884 : "ADMIN";
                  assertEquals(
                      "password-" + username,
                      new String(body, 320, 256, StandardCharsets.UTF_8).stripTrailing());
                }
                byte[] reply = SessionSecurityContextTest.reply(id, "LGNRSP01", code, null);
                Arrays.fill(reply, 256, 389, (byte) ' ');
                if (code.equals(FIXTURE_0000_876EEFE0) || code.equals(FIXTURE_0200_FC9DB3AC)) {
                  put(reply, 256, username);
                  put(reply, 320, assignedRole);
                  put(reply, 325, context);
                } else {
                  Arrays.fill(reply, 389, 423, (byte) ' ');
                  put(reply, 423, String.format(Locale.ROOT, "%06d000", retry));
                }
                try {
                  assertTrue(client.onReply(id, reply));
                  afterReply.run();
                } finally {
                  Arrays.fill(reply, (byte) 0);
                }
              },
              CLOCK,
              () -> new UUID(0, ids.incrementAndGet()),
              Duration.ofSeconds(2));
      var probe =
          new MqLoginContextProbe(
              client,
              (id, body) -> {
                probes.incrementAndGet();
                buffers.add(body);
                if (probeCode.equals(FIXTURE_JMS_1AEA59D9))
                  throw new JMSException("synthetic-private");
                String context = new String(body, 113, 64, StandardCharsets.US_ASCII);
                byte[] reply = SessionSecurityContextTest.reply(id, "GAMRSP01", probeCode, context);
                try {
                  assertTrue(client.onReply(id, reply));
                } finally {
                  Arrays.fill(reply, (byte) 0);
                }
              },
              CLOCK,
              () -> new UUID(0, ids.incrementAndGet()),
              Duration.ofSeconds(2));
      provider = new MqAuthenticationProvider(login, probe);
    }

    void erased() {
      assertEquals(0, client.pendingCount());
      assertEquals(0, client.lateReplyCount());
      for (byte[] body : buffers) assertArrayEquals(new byte[body.length], body);
    }
  }
}
