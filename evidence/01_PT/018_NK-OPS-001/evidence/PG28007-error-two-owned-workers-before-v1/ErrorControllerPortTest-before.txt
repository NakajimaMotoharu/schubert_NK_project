package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.controller.ErrorController;
import dev.codex.schubert.nk.web.error.ProblemViewFactory;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.ErrorViewModel;
import jakarta.servlet.DispatcherType;
import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.lang.reflect.Proxy;
import java.security.Principal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.ui.Model;

/** WEB-ERROR-PORT-001..008; UI222/SS313SSC047; memory Servlet/Model, no server/session/graph. */
final class ErrorControllerPortTest {
  private static final UUID REQUEST_ID = new UUID(0, 123);
  private static final ErrorController CONTROLLER = new ErrorController(new ProblemViewFactory());
  private static final String PAGE = "page";
  private static final String VIEW = "error/error";
  private static final String ALLOW = "Allow";
  private static final String GET_HEAD = "GET, HEAD";
  private static final String GET = "GET";
  private static final String POST = "POST";
  private static final String READ_CONTEXT = "read-context";
  private static final String READ_DISPLAY = "read-display";
  private static final String READ_STATUS = "read-status";
  private static final String SET_STATUS = "set-status";
  private static final String SET_HEADER = "set-header";
  private static final String SET_MODEL = "set-model";
  private static final String PUBLIC_CANARY = "PUBLIC-DIAGNOSTIC-CANARY";
  // UI222 exact normative messages; other closed status text is required
  // stable/nonblank/value-free.
  private static final Map<Integer, String> FIXED_UI =
      Map.of(
          403,
          "この操作を実行する権限がありません。",
          404,
          "対象が見つかりません。",
          409,
          "状態が更新されたため操作できません。再表示してください。",
          503,
          "現在処理できません。しばらくしてから再操作してください。");

  @Test
  void allClosedStatusesAndUnknownValuesProduceMatchingHttpAndOnlyFixedPageData() {
    for (int status : new int[] {400, 401, 403, 404, 405, 409, 416, 429, 503}) {
      Fixture f = new Fixture(REQUEST_ID);
      f.attributes.put(RequestDispatcher.ERROR_STATUS_CODE, status);
      ErrorViewModel page = invoke(f);
      assertEquals(status, page.getStatus());
      assertEquals(status, f.status);
      assertEquals(REQUEST_ID.toString(), page.getRequestId());
      assertTrue(page.getTopBar().isEmpty());
      assertFalse(page.getMessage().isBlank());
      if (FIXED_UI.containsKey(status)) assertEquals(FIXED_UI.get(status), page.getMessage());
      assertEquals(Map.of(), f.headers);
      assertEquals(Set.of(PAGE), f.modelValues.keySet());
      assertEquals("ErrorViewModel[REDACTED]", page.toString());
    }
    for (Object raw : List.of(0, 200, 500, 999, "404", Boolean.TRUE, new ForeignDiagnostic())) {
      Fixture f = new Fixture(REQUEST_ID);
      f.attributes.put(RequestDispatcher.ERROR_STATUS_CODE, raw);
      assertEquals(503, invoke(f).getStatus());
      assertEquals(503, f.status);
    }
    Fixture absent = new Fixture(REQUEST_ID);
    assertEquals(404, invoke(absent).getStatus());
    assertEquals(404, absent.status);
  }

  @Test
  void dispatcherAndMethodGoldenMatrixDistinguishesInternalErrorFromPublicGetHead() {
    DispatcherType[] types = {
      DispatcherType.ERROR,
      DispatcherType.REQUEST,
      DispatcherType.FORWARD,
      DispatcherType.INCLUDE,
      DispatcherType.ASYNC,
      null
    };
    String[] methods = {GET, "HEAD", POST, null};
    int[][] expected = {
      {404, 404, 404, 404},
      {404, 404, 405, 405},
      {404, 404, 405, 405},
      {404, 404, 405, 405},
      {404, 404, 405, 405},
      {404, 404, 405, 405}
    };
    for (int i = 0; i < types.length; i++)
      for (int j = 0; j < methods.length; j++) {
        Fixture f = new Fixture(REQUEST_ID);
        f.dispatcher = types[i];
        f.method = methods[j];
        f.attributes.put(RequestDispatcher.ERROR_STATUS_CODE, 404);
        var page = invoke(f);
        assertEquals(expected[i][j], page.getStatus());
        assertEquals(expected[i][j], f.status);
        assertEquals(expected[i][j] == 405 ? Map.of(ALLOW, GET_HEAD) : Map.of(), f.headers);
      }
  }

  @Test
  void existingDisplaySnapshotSuppliesOnlyApprovedBrandUsernameAndRole() {
    for (UserRole role : List.of(UserRole.USER, UserRole.ADMIN)) {
      Fixture f = new Fixture(REQUEST_ID);
      f.prepareDisplay(role);
      var page = invoke(f);
      var bar = page.getTopBar().orElseThrow();
      assertEquals("schubert NK", bar.getBrand());
      assertEquals("public-view", bar.getUsername());
      assertEquals(role == UserRole.USER ? "USER" : "ADMIN", bar.getRole());
      assertEquals("TopBarViewModel[REDACTED]", bar.toString());
      assertEquals(Set.of(PAGE), f.modelValues.keySet());
      assertFalse(f.reads.contains(CsrfToken.class.getName()));
    }
  }

  @Test
  void constructorAndAllThreeNullArgumentsRejectBeforeReadingPorts() {
    assertThrows(NullPointerException.class, () -> new ErrorController(null));
    Fixture f = new Fixture(REQUEST_ID);
    assertThrows(NullPointerException.class, () -> CONTROLLER.error(null, f.response, f.model));
    assertThrows(NullPointerException.class, () -> CONTROLLER.error(f.request, null, f.model));
    assertThrows(NullPointerException.class, () -> CONTROLLER.error(f.request, f.response, null));
    assertEquals(List.of(), f.reads);
    assertEquals(Map.of(), f.modelValues);
    assertEquals(0, f.status);
  }

  @Test
  void missingOrMistypedInternalContextsNeverBecomeASuccessfulPage() {
    for (Object invalid : java.util.Arrays.asList(null, PUBLIC_CANARY)) {
      Fixture f = new Fixture(REQUEST_ID);
      f.attributes.put(WebRequestContext.ATTRIBUTE, invalid);
      var failure = assertThrows(IllegalStateException.class, () -> invoke(f));
      assertEquals("web request context is unavailable", failure.getMessage());
      assertEquals(Map.of(), f.modelValues);
      assertEquals(0, f.status);
    }
    Fixture display = new Fixture(REQUEST_ID);
    display.attributes.put(WebDisplayContext.class.getName(), PUBLIC_CANARY);
    var failure = assertThrows(SessionStoreException.class, () -> invoke(display));
    assertEquals("session storage is unavailable", failure.getMessage());
    assertEquals(Map.of(), display.modelValues);
    assertEquals(0, display.status);
  }

  @Test
  void unknownRuntimeAndErrorAtEveryExternalPortPreserveIdentity() {
    for (String point :
        List.of(
            READ_STATUS,
            "getDispatcherType",
            "getMethod",
            READ_CONTEXT,
            READ_DISPLAY,
            SET_HEADER,
            SET_STATUS,
            SET_MODEL)) {
      for (Throwable fault :
          List.of(
              new UnsupportedOperationException(PUBLIC_CANARY),
              new AssertionError(PUBLIC_CANARY))) {
        Fixture f = new Fixture(REQUEST_ID);
        if (point.equals(SET_HEADER)) f.method = POST;
        f.faults.put(point, fault);
        assertSame(fault, assertThrows(fault.getClass(), () -> invoke(f)));
        assertEquals(Map.of(), f.modelValues);
      }
    }
  }

  @Test
  void throwableMessageUriQueryHeadersBodyAndSessionAreNeverReadOrStringified() {
    Fixture f = new Fixture(REQUEST_ID);
    f.attributes.put(RequestDispatcher.ERROR_STATUS_CODE, new ForeignDiagnostic());
    f.attributes.put(RequestDispatcher.ERROR_EXCEPTION, new IllegalStateException(PUBLIC_CANARY));
    f.attributes.put(RequestDispatcher.ERROR_MESSAGE, PUBLIC_CANARY);
    f.attributes.put(
        RequestDispatcher.ERROR_REQUEST_URI, "/private-fixture?value=" + PUBLIC_CANARY);
    var page = invoke(f);
    assertEquals(503, page.getStatus());
    assertEquals(FIXED_UI.get(503), page.getMessage());
    assertEquals(
        Set.of(
            RequestDispatcher.ERROR_STATUS_CODE,
            WebRequestContext.ATTRIBUTE,
            WebDisplayContext.class.getName()),
        Set.copyOf(f.reads));
    assertEquals(Set.of(PAGE), f.modelValues.keySet());
    assertTrue(page.getTopBar().isEmpty());
  }

  @Test
  void sharedControllerHasIndependentConcurrentRequestAndModelState() throws Exception {
    try (var executor = Executors.newFixedThreadPool(2)) {
      var first =
          executor.submit(
              () -> {
                Fixture f = new Fixture(new UUID(0, 1));
                f.attributes.put(RequestDispatcher.ERROR_STATUS_CODE, 403);
                return invoke(f);
              });
      var second =
          executor.submit(
              () -> {
                Fixture f = new Fixture(new UUID(0, 2));
                f.method = POST;
                return invoke(f);
              });
      var a = first.get(5, TimeUnit.SECONDS);
      var b = second.get(5, TimeUnit.SECONDS);
      assertEquals(new UUID(0, 1).toString(), a.getRequestId());
      assertEquals(403, a.getStatus());
      assertEquals(FIXED_UI.get(403), a.getMessage());
      assertEquals(new UUID(0, 2).toString(), b.getRequestId());
      assertEquals(405, b.getStatus());
    }
  }

  private static ErrorViewModel invoke(Fixture f) {
    assertEquals(VIEW, CONTROLLER.error(f.request, f.response, f.model));
    return (ErrorViewModel) f.modelValues.get(PAGE);
  }

  private static final class ForeignDiagnostic {
    @Override
    public String toString() {
      throw new AssertionError("foreigndiagnostic must never be stringified");
    }
  }

  private static final class Fixture {
    final Map<String, Object> attributes = new HashMap<>();
    final Map<String, Object> modelValues = new HashMap<>();
    final Map<String, String> headers = new HashMap<>();
    final Map<String, Throwable> faults = new HashMap<>();
    final List<String> reads = new ArrayList<>();
    String method = GET;
    DispatcherType dispatcher = DispatcherType.REQUEST;
    int status;
    boolean preparingDisplay;
    Principal principal;
    final HttpServletRequest request =
        proxy(
            HttpServletRequest.class,
            (receiver, name, args) ->
                switch (name) {
                  case "getAttribute" -> {
                    String key = (String) args[0];
                    if (preparingDisplay) {
                      yield attributes.get(key);
                    }
                    reads.add(key);
                    String point =
                        key.equals(RequestDispatcher.ERROR_STATUS_CODE)
                            ? READ_STATUS
                            : key.equals(WebRequestContext.ATTRIBUTE)
                                ? READ_CONTEXT
                                : key.equals(WebDisplayContext.class.getName())
                                    ? READ_DISPLAY
                                    : null;
                    if (point == null) throw new AssertionError("forbidden request attribute");
                    at(point);
                    yield attributes.get(key);
                  }
                  case "getDispatcherType" -> {
                    at(name);
                    yield dispatcher;
                  }
                  case "getMethod" -> {
                    at(name);
                    yield method;
                  }
                  case "getUserPrincipal" -> {
                    if (!preparingDisplay)
                      throw new AssertionError("controller must not readprincipal");
                    yield principal;
                  }
                  case "setAttribute" -> {
                    if (!preparingDisplay)
                      throw new AssertionError("controller must not mutate request");
                    attributes.put((String) args[0], args[1]);
                    yield null;
                  }
                  default -> throw new AssertionError("forbidden request operation " + name);
                });
    final HttpServletResponse response =
        proxy(
            HttpServletResponse.class,
            (receiver, name, args) ->
                switch (name) {
                  case "setHeader" -> {
                    at(SET_HEADER);
                    headers.put((String) args[0], (String) args[1]);
                    yield null;
                  }
                  case "setStatus" -> {
                    at(SET_STATUS);
                    status = (Integer) args[0];
                    yield null;
                  }
                  default -> throw new AssertionError("forbidden response operation " + name);
                });
    final Model model =
        proxy(
            Model.class,
            (receiver, name, args) -> {
              if (!name.equals("addAttribute") || args.length != 2)
                throw new AssertionError("forbidden model operation");
              at(SET_MODEL);
              modelValues.put((String) args[0], args[1]);
              return receiver;
            });

    Fixture(UUID id) {
      attributes.put(
          WebRequestContext.ATTRIBUTE,
          new WebRequestContext(id, new LoginClientAddress("203.0.113.1")));
    }

    void at(String point) throws Throwable {
      Throwable fault = faults.get(point);
      if (fault != null) throw fault;
    }

    void prepareDisplay(UserRole role) {
      // Known synthetic zero bytes only; no real context/key/session/token is read or emitted.
      String dummy = HexFormat.of().formatHex(new byte[32]);
      principal =
          new SessionPrincipal("public-view", role, AuthenticationContext.of(dummy), Instant.EPOCH);
      attributes.put(
          CsrfToken.class.getName(), new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", dummy));
      preparingDisplay = true;
      try {
        WebDisplayContext.capture(request);
      } finally {
        preparingDisplay = false;
        principal = null;
      }
      attributes.remove(CsrfToken.class.getName());
    }
  }

  @FunctionalInterface
  private interface Call {
    Object invoke(Object receiver, String method, Object[] args) throws Throwable;
  }

  private static <T> T proxy(Class<T> type, Call call) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (object, method, args) ->
                call.invoke(object, method.getName(), args == null ? new Object[0] : args)));
  }
}
