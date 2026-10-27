package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import jakarta.servlet.http.HttpServletRequestWrapper;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/**
 * NK-WEB-001 / SS313314342352/SSC172 / PT-WEB-IDENT-CONSIST001. Internal server attributes may not
 * bind two request identities; no HTTP/session fallback.
 */
final class WebRequestIdentityConsistencyTest {
  private static final String REQUEST_ID_ATTRIBUTE_SUFFIX = ".requestId";

  @Test
  void contextSuppliesMissingInternalIdWithoutGeneratingAnother() {
    var request = new MockHttpServletRequest();
    var original = UUID.fromString("00000000-0000-4000-8000-000000000003");
    var context = new WebRequestContext(original, new LoginClientAddress("203.0.113.1"));
    request.setAttribute(WebRequestContext.class.getName(), context);
    assertEquals(
        original,
        WebRequestContext.identify(
            request,
            () -> {
              throw new AssertionError("verified context is the only identity");
            }));
    assertEquals(
        original,
        request.getAttribute(WebRequestContext.class.getName() + REQUEST_ID_ATTRIBUTE_SUFFIX));
    assertSame(context, WebRequestContext.require(request));
  }

  @Test
  void transportContextSaveFailureStopsBeforeDownstreamWithoutCauseOrFallback() {
    for (boolean stateFailure : new boolean[] {false, true}) {
      var underlying = new MockHttpServletRequest();
      underlying.setRemoteAddr("127.0.0.1");
      underlying.addHeader("X-Forwarded-For", "203.0.113.1");
      underlying.addHeader("X-Forwarded-Proto", "https");
      var request =
          new HttpServletRequestWrapper(underlying) {
            @Override
            public void setAttribute(String name, Object value) {
              if (name.equals(WebRequestContext.class.getName())) {
                if (stateFailure) throw new IllegalStateException("untrusted attribute detail");
                throw new IllegalArgumentException("untrusted attribute detail");
              }
              super.setAttribute(name, value);
            }
          };
      var expected = UUID.fromString("00000000-0000-4000-8000-000000000004");
      var audit =
          new WebSecurityAudit(
              System.getLogger("synthetic-context"),
              Clock.fixed(Instant.parse("2026-10-06T00:00:00Z"), ZoneOffset.UTC),
              "fixture",
              "1");
      var filter =
          new CaddyTransportContextFilter(() -> expected, new CaddyClientAddressResolver(), audit);
      var failure =
          assertThrows(
              IllegalStateException.class,
              () ->
                  filter.doFilter(
                      request,
                      new MockHttpServletResponse(),
                      (in, out) -> {
                        throw new AssertionError("untrusted context must not dispatch");
                      }));
      assertEquals("web request context is unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertNull(underlying.getAttribute(WebRequestContext.class.getName()));
      assertEquals(
          expected,
          underlying.getAttribute(WebRequestContext.class.getName() + REQUEST_ID_ATTRIBUTE_SUFFIX));
    }
  }

  @Test
  void existingVerifiedContextCannotBeReboundToAnotherServerIdentity() {
    var request = new MockHttpServletRequest();
    var original = UUID.fromString("00000000-0000-4000-8000-000000000001");
    var foreign = UUID.fromString("00000000-0000-4000-8000-000000000002");
    var context = new WebRequestContext(original, new LoginClientAddress("203.0.113.1"));
    request.setAttribute(WebRequestContext.class.getName(), context);
    request.setAttribute(WebRequestContext.class.getName() + REQUEST_ID_ATTRIBUTE_SUFFIX, foreign);
    var failure =
        assertThrows(
            IllegalStateException.class,
            () ->
                WebRequestContext.identify(
                    request,
                    () -> {
                      throw new AssertionError("must not mint replacement");
                    }));
    assertEquals("web request identity is unavailable", failure.getMessage());
    assertSame(context, WebRequestContext.require(request));
    assertEquals(
        foreign,
        request.getAttribute(WebRequestContext.class.getName() + REQUEST_ID_ATTRIBUTE_SUFFIX));
    request.setAttribute(WebRequestContext.class.getName() + REQUEST_ID_ATTRIBUTE_SUFFIX, original);
    assertEquals(
        original,
        WebRequestContext.identify(
            request,
            () -> {
              throw new AssertionError("must not remint");
            }));
  }
}
