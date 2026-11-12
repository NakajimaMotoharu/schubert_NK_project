package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import java.security.ProviderException;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

/** OPS-CADDY-FATAL001..005; BUG2707/SS314342352, only memory Servlet and public IP literals. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class CaddyContextFatalContractTest {
  private static final String FORWARDED_PROTO = "X-Forwarded-Proto";
  private static final String FORWARDED_FOR = "X-Forwarded-For";
  private static final String CONTEXT = WebRequestContext.class.getName();
  private static final String ID = CONTEXT + ".requestId";
  private static final UUID SERVER_ID = new UUID(0, 31);
  private static final String UNAVAILABLE = "web request context is unavailable";

  @Test
  void fatal001ResolverClosedForwardingVectorsAndProviderGraph() {
    for (int kind = 0; kind < 3; kind++) {
      var fatal = new AssertionError("PUBLIC resolver fatal");
      var failure = graph(kind, fatal);
      var request =
          new MockHttpServletRequest() {
            @Override
            public String getRemoteAddr() {
              throw failure;
            }
          };
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class, () -> new CaddyClientAddressResolver().resolve(request)));
    }
    for (String peer : List.of("127.0.0.1", "::1")) {
      for (String client : List.of("203.0.113.9", "2001:db8::3")) {
        var request = trusted(new MockHttpServletRequest());
        request.setRemoteAddr(peer);
        request.removeHeader(FORWARDED_FOR);
        request.addHeader(FORWARDED_FOR, client);
        assertEquals(client, new CaddyClientAddressResolver().resolve(request).value());
      }
    }
    List<Consumer<MockHttpServletRequest>> invalid =
        List.of(
            r -> r.setRemoteAddr(null),
            r -> r.setRemoteAddr("host.invalid"),
            r -> r.setRemoteAddr("203.0.113.2"),
            r -> r.addHeader("Forwarded", "for=203.0.113.1"),
            r -> r.removeHeader(FORWARDED_PROTO),
            r -> r.addHeader(FORWARDED_PROTO, "https"),
            r -> {
              r.removeHeader(FORWARDED_PROTO);
              r.addHeader(FORWARDED_PROTO, "http");
            },
            r -> r.removeHeader(FORWARDED_FOR),
            r -> r.addHeader(FORWARDED_FOR, "203.0.113.2"),
            r -> {
              r.removeHeader(FORWARDED_FOR);
              r.addHeader(FORWARDED_FOR, "host.invalid");
            });
    for (var alter : invalid) {
      var request = trusted(new MockHttpServletRequest());
      alter.accept(request);
      rejected(request);
    }
    for (String header : List.of("Forwarded", FORWARDED_PROTO, FORWARDED_FOR)) {
      rejected(trusted(special(header, null)));
    }
    for (String header : List.of(FORWARDED_PROTO, FORWARDED_FOR)) {
      rejected(trusted(special(header, Collections.enumeration(Arrays.asList((String) null)))));
    }
    assertThrows(NullPointerException.class, () -> new CaddyClientAddressResolver().resolve(null));
  }

  @Test
  void fatal002FilterContextSaveKeepsFatalAndNeverDispatches() {
    for (int kind = 0; kind < 2; kind++) {
      var fatal = new AssertionError("PUBLIC context save fatal");
      var request = trusted(fault(CONTEXT, true, graph(kind, fatal)));
      var response = new MockHttpServletResponse();
      var downstream = new AtomicInteger();
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  filter().doFilter(request, response, (in, out) -> downstream.incrementAndGet())));
      assertEquals(0, downstream.get());
      assertFalse(response.isCommitted());
      assertNull(request.getAttribute(CONTEXT));
      assertEquals(SERVER_ID, request.getAttribute(ID));
    }
    var request = trusted(fault(CONTEXT, true, cycle()));
    fixed(() -> filter().doFilter(request, new MockHttpServletResponse(), (in, out) -> {}));
    var fatal = new AssertionError("PUBLIC direct save");
    var direct = trusted(fault(CONTEXT, true, fatal));
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> filter().doFilter(direct, new MockHttpServletResponse(), (in, out) -> {})));
  }

  @Test
  void fatal003ExistingContextReadGraphAndForeignMetadataNeverStringifies() {
    for (int kind = 0; kind < 2; kind++) {
      var fatal = new AssertionError("PUBLIC context read fatal");
      var request = fault(CONTEXT, false, graph(kind, fatal));
      assertSame(
          fatal, assertThrows(AssertionError.class, () -> WebRequestContext.existing(request)));
    }
    fixed(() -> WebRequestContext.existing(fault(CONTEXT, false, cycle())));
    var fatal = new AssertionError("PUBLIC direct read");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> WebRequestContext.existing(fault(CONTEXT, false, fatal))));
    var request = new MockHttpServletRequest();
    var foreign =
        new Object() {
          @Override
          public String toString() {
            throw new AssertionError("foreign diagnostics must not be formatted");
          }
        };
    request.setAttribute(CONTEXT, foreign);
    fixed(() -> WebRequestContext.existing(request));
  }

  @Test
  void fatal004IdentifyIdReadGraphAndStableServerIdentity() {
    for (int kind = 0; kind < 2; kind++) {
      var fatal = new AssertionError("PUBLIC identity read fatal");
      var request = fault(ID, false, graph(kind, fatal));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class, () -> WebRequestContext.identify(request, () -> SERVER_ID)));
    }
    fixed(() -> WebRequestContext.identify(fault(ID, false, cycle()), () -> SERVER_ID));
    var fatal = new AssertionError("PUBLIC direct identity read");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> WebRequestContext.identify(fault(ID, false, fatal), () -> SERVER_ID)));
    var request = new MockHttpServletRequest();
    request.addHeader("X-Request-ID", "untrusted-client-value");
    var generated = new AtomicInteger();
    assertEquals(
        SERVER_ID,
        WebRequestContext.identify(
            request,
            () -> {
              generated.incrementAndGet();
              return SERVER_ID;
            }));
    assertEquals(
        SERVER_ID,
        WebRequestContext.identify(
            request,
            () -> {
              throw new AssertionError("must not regenerate stable server ID");
            }));
    assertEquals(1, generated.get());
  }

  @Test
  void fatal005IdentifyIdWriteGraphAndNoFallbackAfterFailure() {
    for (int kind = 0; kind < 2; kind++) {
      var fatal = new AssertionError("PUBLIC identity write fatal");
      var request = fault(ID, true, graph(kind, fatal));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class, () -> WebRequestContext.identify(request, () -> SERVER_ID)));
      assertNull(request.getAttribute(ID));
    }
    fixed(() -> WebRequestContext.identify(fault(ID, true, cycle()), () -> SERVER_ID));
    var fatal = new AssertionError("PUBLIC direct identity write");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> WebRequestContext.identify(fault(ID, true, fatal), () -> SERVER_ID)));
  }

  private static MockHttpServletRequest trusted(MockHttpServletRequest request) {
    request.setRemoteAddr("127.0.0.1");
    request.addHeader(FORWARDED_PROTO, "https");
    request.addHeader(FORWARDED_FOR, "203.0.113.9");
    return request;
  }

  private static MockHttpServletRequest special(String header, Enumeration<String> values) {
    return new MockHttpServletRequest() {
      @Override
      public Enumeration<String> getHeaders(String name) {
        return header.equals(name) ? values : super.getHeaders(name);
      }
    };
  }

  private static RuntimeException graph(int kind, Error fatal) {
    RuntimeException failure =
        switch (kind) {
          case 0 -> new IllegalArgumentException("PUBLIC provider");
          case 1 -> new IllegalStateException("PUBLIC provider");
          default -> new NoSuchElementException("PUBLIC provider");
        };
    var sql = new SQLException("PUBLIC SQL");
    sql.setNextException(new SQLException("PUBLIC next", fatal));
    failure.addSuppressed(sql);
    return failure;
  }

  private static IllegalStateException cycle() {
    var first = new IllegalStateException("PUBLIC cycle");
    var second = new ProviderException("PUBLIC alias", first);
    first.initCause(second);
    first.addSuppressed(second);
    second.addSuppressed(first);
    return first;
  }

  private static MockHttpServletRequest fault(String attribute, boolean write, Throwable failure) {
    return new MockHttpServletRequest() {
      @Override
      public Object getAttribute(String name) {
        if (!write && attribute.equals(name)) fail();
        return super.getAttribute(name);
      }

      @Override
      public void setAttribute(String name, Object value) {
        if (write && attribute.equals(name)) fail();
        super.setAttribute(name, value);
      }

      private void fail() {
        if (failure instanceof Error fatal) throw fatal;
        throw (RuntimeException) failure;
      }
    };
  }

  private static CaddyTransportContextFilter filter() {
    var audit =
        new WebSecurityAudit(
            System.getLogger("PUBLIC-CADDY-UNIT"),
            Clock.fixed(Instant.EPOCH, ZoneOffset.UTC),
            "fixture",
            "fixture");
    return new CaddyTransportContextFilter(
        () -> SERVER_ID, new CaddyClientAddressResolver(), audit);
  }

  private static void rejected(MockHttpServletRequest request) {
    var failure =
        assertThrows(
            CaddyRequestRejectedException.class,
            () -> new CaddyClientAddressResolver().resolve(request));
    assertEquals("request proxy is invalid", failure.getMessage());
    assertNull(failure.getCause());
  }

  private static void fixed(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(IllegalStateException.class, action);
    assertEquals(UNAVAILABLE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
