package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.servlet.DispatcherType;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.security.web.csrf.CsrfToken;

/** PT-WEB-CSRF-FILTER001..008 / UI226 SS3148.1/352. Real SDK, supplied Servlet ports only. */
final class CsrfFilterFactoryPortTest {
  private static final String CANARY = "A".repeat(64);
  private static final String OTHER = "B".repeat(64);
  private static final String PARAMETER = "_csrf";
  private static final String POST = "POST";
  private static final String GET = "GET";
  private static final String FIXTURE_PATH = "/public-fixture";
  private static final String LOGGER_NAME = "org.springframework.security.web.csrf.CsrfFilter";
  private static final Logger CHILD_LOGGER = Logger.getLogger(LOGGER_NAME);
  private Level previousLevel;
  private final WebCsrfFilterFactory factory = new WebCsrfFilterFactory();
  private final EncryptedSessionCsrfTokenRepository repository =
      new EncryptedSessionCsrfTokenRepository();

  @BeforeEach
  void warningOnlyInThisChildJvm() {
    previousLevel = CHILD_LOGGER.getLevel();
    CHILD_LOGGER.setLevel(Level.WARNING);
  }

  @AfterEach
  void restoreOnlyChildLoggerLevel() {
    CHILD_LOGGER.setLevel(previousLevel);
  }

  @Test
  void factoryRejectsNullDependenciesAndReturnsIndependentFilterInstances() {
    var frame = new Frame(GET, CANARY, null);
    assertThrows(NullPointerException.class, () -> factory.create(null, frame.denied));
    assertThrows(NullPointerException.class, () -> factory.create(repository, null));
    assertNotSame(
        factory.create(repository, frame.denied), factory.create(repository, frame.denied));
    assertEquals(0, frame.sessionReads);
    assertEquals(0, frame.denials);
  }

  @Test
  void safeMethodsExposeSuppliedUnmaskedFormTokenWithoutCreatingSession() throws Exception {
    for (String method : List.of(GET, "HEAD", "OPTIONS", "TRACE")) {
      var frame = new Frame(method, CANARY, null);
      factory.create(repository, frame.denied).doFilter(frame.request, frame.response, frame.chain);
      assertEquals(1, frame.chainCalls);
      assertEquals(0, frame.denials);
      assertToken(frame);
      assertEquals(0, frame.headerReads);
    }
  }

  @Test
  void unsafeMethodsAcceptOnlySingleMatchingFormValueAndIgnoreHeaderValue() throws Exception {
    for (String method : List.of(POST, "PUT", "PATCH", "DELETE", "BREW")) {
      var frame = new Frame(method, CANARY, new String[] {CANARY});
      frame.header = OTHER;
      factory.create(repository, frame.denied).doFilter(frame.request, frame.response, frame.chain);
      assertEquals(1, frame.chainCalls);
      assertEquals(0, frame.denials);
      assertEquals(0, frame.headerReads);
      assertToken(frame);
    }
  }

  @Test
  void missingMalformedWrongAndDuplicateFormValuesAreDeniedWithoutChain() throws Exception {
    String[][] values = {
      null,
      new String[0],
      new String[] {null},
      new String[] {""},
      new String[] {OTHER},
      new String[] {CANARY, CANARY},
      new String[] {"bad"}
    };
    for (String[] submitted : values) {
      var frame = new Frame(POST, CANARY, submitted);
      frame.header = CANARY;
      factory.create(repository, frame.denied).doFilter(frame.request, frame.response, frame.chain);
      assertEquals(0, frame.chainCalls);
      assertEquals(1, frame.denials);
      assertEquals(403, frame.status);
      assertEquals(0, frame.headerReads);
    }
  }

  @Test
  void reservedQueryKeyRejectsEvenWithValidFormAndEncodedKey() throws Exception {
    for (String query : List.of("_csrf=public-unissued", "%5fcsrf=public-unissued")) {
      var frame = new Frame(POST, CANARY, new String[] {CANARY});
      frame.query = query;
      factory.create(repository, frame.denied).doFilter(frame.request, frame.response, frame.chain);
      assertEquals(1, frame.denials);
      assertEquals(0, frame.chainCalls);
      assertEquals(403, frame.status);
    }
    var frame = new Frame(POST, CANARY, new String[] {CANARY});
    frame.query = "q=public";
    factory.create(repository, frame.denied).doFilter(frame.request, frame.response, frame.chain);
    assertEquals(1, frame.chainCalls);
    assertEquals(0, frame.denials);
  }

  @Test
  void suppliedDeniedHandlerReceivesExactPortsAndItsIoFailureIsNotReplaced() {
    var frame = new Frame(POST, CANARY, null);
    var calls = new AtomicInteger();
    var failure = new IOException("public denied callback failure");
    AccessDeniedHandler denied =
        (request, response, exception) -> {
          assertSame(frame.request, request);
          assertSame(frame.response, response);
          calls.incrementAndGet();
          throw failure;
        };
    var filter = factory.create(repository, denied);
    assertSame(
        failure,
        assertThrows(
            IOException.class, () -> filter.doFilter(frame.request, frame.response, frame.chain)));
    assertEquals(1, calls.get());
    assertEquals(0, frame.chainCalls);
    assertMarkerRemoved(frame);
  }

  @Test
  void callerChainIoFailureIsPreservedAndRequestMarkerIsAlwaysRemoved() {
    var frame = new Frame(POST, CANARY, new String[] {CANARY});
    var failure = new IOException("public chain callback failure");
    var calls = new AtomicInteger();
    FilterChain chain =
        (request, response) -> {
          assertSame(frame.request, request);
          assertSame(frame.response, response);
          calls.incrementAndGet();
          throw failure;
        };
    var filter = factory.create(repository, frame.denied);
    assertSame(
        failure,
        assertThrows(
            IOException.class, () -> filter.doFilter(frame.request, frame.response, chain)));
    assertEquals(1, calls.get());
    assertEquals(0, frame.denials);
    assertMarkerRemoved(frame);
  }

  @Test
  void sharedConfiguredFilterKeepsEightConcurrentSuppliedTokensRequestLocal() throws Exception {
    var filter =
        factory.create(
            repository,
            (request, response, exception) -> {
              throw new AssertionError("valid supplied form must not be denied");
            });
    try (var workers = Executors.newFixedThreadPool(2)) {
      var jobs = new ArrayList<java.util.concurrent.Future<?>>();
      for (int index = 0; index < 8; index++) {
        String value = index % 2 == 0 ? CANARY : OTHER;
        jobs.add(
            workers.submit(
                () -> {
                  var frame = new Frame(POST, value, new String[] {value});
                  filter.doFilter(frame.request, frame.response, frame.chain);
                  assertEquals(1, frame.chainCalls);
                  assertEquals(0, frame.denials);
                  assertToken(frame);
                  return null;
                }));
      }
      for (var job : jobs) job.get();
    }
  }

  private static void assertToken(Frame frame) {
    Object supplied = frame.attributes.get(CsrfToken.class.getName());
    assertTrue(supplied instanceof CsrfToken);
    var token = (CsrfToken) supplied;
    assertEquals(PARAMETER, token.getParameterName());
    assertEquals("X-CSRF-TOKEN", token.getHeaderName());
    // Boolean assertion deliberately keeps public canary/masked values out of failure artifacts.
    assertTrue(
        frame.stored.equals(token.getToken()), "factory must expose only supplied unmasked value");
    assertSame(supplied, frame.attributes.get(PARAMETER));
    assertMarkerRemoved(frame);
  }

  private static void assertMarkerRemoved(Frame frame) {
    assertFalse(frame.attributes.keySet().stream().anyMatch(key -> key.endsWith(".FILTERED")));
  }

  private static final class Frame {
    private final Map<String, Object> attributes = new HashMap<>();
    private final HttpServletRequest request;
    private final HttpServletResponse response;
    private final AccessDeniedHandler denied;
    private final FilterChain chain;
    private final String stored;
    private String header;
    private String query;
    private int sessionReads;
    private int headerReads;
    private int chainCalls;
    private int denials;
    private int status;

    Frame(String method, String stored, String[] submitted) {
      this.stored = stored;
      HttpSession session =
          (HttpSession)
              Proxy.newProxyInstance(
                  HttpSession.class.getClassLoader(),
                  new Class<?>[] {HttpSession.class},
                  (proxy, invoked, args) -> {
                    assertEquals("getAttribute", invoked.getName());
                    assertEquals("csrfToken", args[0]);
                    return stored;
                  });
      request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, invoked, args) -> {
                    return switch (invoked.getName()) {
                      case "getAttribute" -> attributes.get(args[0]);
                      case "setAttribute" -> {
                        attributes.put((String) args[0], args[1]);
                        yield null;
                      }
                      case "removeAttribute" -> {
                        attributes.remove(args[0]);
                        yield null;
                      }
                      case "getDispatcherType" -> DispatcherType.REQUEST;
                      case "isAsyncStarted" -> false;
                      case "getMethod" -> method;
                      case "getQueryString" -> query;
                      case "getParameterValues" -> {
                        assertEquals(PARAMETER, args[0]);
                        yield submitted;
                      }
                      case "getSession" -> {
                        assertEquals(Boolean.FALSE, args[0]);
                        sessionReads++;
                        yield session;
                      }
                      case "getHeader" -> {
                        headerReads++;
                        yield header;
                      }
                      case "getRequestURI", "getServletPath" -> FIXTURE_PATH;
                      case "getContextPath" -> "";
                      case "getPathInfo" -> null;
                      case "getScheme" -> "https";
                      case "getServerName" -> "public.invalid";
                      case "getServerPort" -> 443;
                      default ->
                          throw new AssertionError(
                              "unapproved Servlet request operation: " + invoked.getName());
                    };
                  });
      response =
          (HttpServletResponse)
              Proxy.newProxyInstance(
                  HttpServletResponse.class.getClassLoader(),
                  new Class<?>[] {HttpServletResponse.class},
                  (proxy, invoked, args) -> {
                    assertEquals("setStatus", invoked.getName());
                    assertEquals(403, args[0]);
                    status = (Integer) args[0];
                    return null;
                  });
      denied =
          (req, resp, exception) -> {
            assertSame(request, req);
            assertSame(response, resp);
            denials++;
            resp.setStatus(403);
          };
      chain =
          (req, resp) -> {
            assertSame(request, req);
            assertSame(response, resp);
            chainCalls++;
          };
    }
  }
}
