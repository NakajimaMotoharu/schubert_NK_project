package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.LogType;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.controller.MenuController;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.view.MenuViewModel;
import java.lang.reflect.Proxy;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.ui.ConcurrentModel;
import org.springframework.ui.Model;

/** QA054/SSC336/UI223235/SS312351, PT-WEB-MENU001..005; pure kind/trace/controller only. */
final class MenuAuditContractTest {
  private static final String GET = "GET";
  private static final String ROOT = "/";
  private static final String MENU_VIEW = "menu";
  private static final String PAGE = "page";

  @Test
  void menu001EveryGateAndBoundaryUsesIndependentTruthTable() {
    for (boolean marked : List.of(false, true)) {
      for (String method : List.of(GET, "HEAD", "POST", "get")) {
        for (int status : new int[] {99, 100, 199, 200, 201, 299, 300, 401, 403, 500, 599, 600}) {
          for (String route : List.of(ROOT, "/**", "/logs", "/login")) {
            for (boolean actor : List.of(false, true)) {
              boolean expected =
                  marked && method.equals(GET) && status == 200 && route.equals(ROOT) && actor;
              assertEquals(
                  expected,
                  WebHttpLogKind.MENU_VIEWED.eligible(marked, method, status, route, actor));
              assertFalse(WebHttpLogKind.REQUEST.eligible(marked, method, status, route, actor));
            }
          }
        }
      }
    }
  }

  @Test
  void menu002ClosedKindsHaveLiteralMetadataAndNullContracts() {
    assertEquals(2, WebHttpLogKind.values().length);
    assertEquals(LogType.REQUEST, WebHttpLogKind.REQUEST.category());
    assertEquals("HTTP_REQUEST_COMPLETED", WebHttpLogKind.REQUEST.action());
    assertEquals("HTTP request completed", WebHttpLogKind.REQUEST.message());
    assertEquals(LogType.ACTION, WebHttpLogKind.MENU_VIEWED.category());
    assertEquals("MENU_VIEWED", WebHttpLogKind.MENU_VIEWED.action());
    assertEquals("Menu viewed", WebHttpLogKind.MENU_VIEWED.message());
    for (WebHttpLogKind kind : WebHttpLogKind.values()) {
      assertThrows(NullPointerException.class, () -> kind.eligible(true, null, 200, ROOT, true));
      assertThrows(NullPointerException.class, () -> kind.eligible(true, GET, 200, null, true));
    }
  }

  @Test
  void menu003SuccessfulUserAndAdminModelsMarkOnlyTheirOwnTrace() {
    for (UserRole role : UserRole.values()) {
      var request = new MockHttpServletRequest();
      var trace = WebRequestTraceTest.trace(request, 410);
      var model = new ConcurrentModel();
      assertFalse(trace.menuViewCandidate());
      var scope = trace.enter();
      try {
        assertEquals(MENU_VIEW, new MenuController().show(principal(role), model));
      } finally {
        scope.close();
      }
      assertTrue(trace.menuViewCandidate());
      var page = (MenuViewModel) model.asMap().get(PAGE);
      assertEquals(role == UserRole.ADMIN ? 9 : 7, page.getCards().size());
      assertEquals("schubert NK", page.getTopBar().getBrand());
      assertEquals(role.name(), page.getTopBar().getRole());
      assertTrue(trace.claimCompletion());
      assertFalse(trace.claimCompletion());
    }
  }

  @Test
  void menu004FailedOrMissingScopeDoesNotForgeAMenuSuccess() {
    var trace = WebRequestTraceTest.trace(new MockHttpServletRequest(), 420);
    var controller = new MenuController();
    var model = new ConcurrentModel();
    var scope = trace.enter();
    try {
      assertThrows(NullPointerException.class, () -> controller.show(null, model));
      assertThrows(
          NullPointerException.class, () -> controller.show(principal(UserRole.USER), null));
      assertThrows(SessionStoreException.class, () -> controller.show(() -> "foreign", model));
      var failure = new IllegalStateException("safe model fixture");
      Model broken =
          (Model)
              Proxy.newProxyInstance(
                  Model.class.getClassLoader(),
                  new Class<?>[] {Model.class},
                  (proxy, method, args) -> {
                    throw failure;
                  });
      assertSame(
          failure,
          assertThrows(
              IllegalStateException.class,
              () -> controller.show(principal(UserRole.USER), broken)));
      assertFalse(trace.menuViewCandidate());
    } finally {
      scope.close();
    }
    // No logging request lifetime in a standalone controller caller: preserve its existing view.
    assertEquals(MENU_VIEW, controller.show(principal(UserRole.USER), new ConcurrentModel()));
    assertFalse(trace.menuViewCandidate());
  }

  @Test
  void menu005NestedMarkersDoNotInheritAndEachNoMqEventSelfCorrelates() throws Exception {
    var first = WebRequestTraceTest.trace(new MockHttpServletRequest(), 430);
    var second = WebRequestTraceTest.trace(new MockHttpServletRequest(), 431);
    var ownMenuId = new UUID(7, 430);
    assertEquals(ownMenuId, first.correlationIdFor(ownMenuId));
    assertThrows(NullPointerException.class, () -> first.correlationIdFor(null));
    WebRequestTrace.markMenuViewed();
    assertFalse(first.menuViewCandidate());
    var outer = first.enter();
    try {
      var inner = second.enter();
      try {
        WebRequestTrace.markMenuViewed();
      } finally {
        inner.close();
      }
      assertTrue(second.menuViewCandidate());
      assertFalse(first.menuViewCandidate());
      var workers = Executors.newFixedThreadPool(1);
      try {
        workers.submit(WebRequestTrace::markMenuViewed).get(10, TimeUnit.SECONDS);
      } finally {
        workers.shutdownNow();
        assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
      }
      assertFalse(first.menuViewCandidate());
      WebRequestTrace.markMenuViewed();
      assertTrue(first.menuViewCandidate());
      var businessId = new UUID(8, 430);
      assertEquals(businessId, WebRequestTrace.businessIdentifiers(() -> businessId).get());
      assertEquals(businessId, first.correlationIdFor(ownMenuId));
    } finally {
      outer.close();
    }
    assertEquals(second.eventId(), second.correlationId());
  }

  private static SessionPrincipal principal(UserRole role) {
    return new SessionPrincipal(
        "public-menu-user",
        role,
        AuthenticationContext.of("0".repeat(64)),
        Instant.parse("2026-11-06T00:00:00Z"));
  }
}
