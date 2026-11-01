package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Collections;
import java.util.Enumeration;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;

/** Independent SS314/342 literal proxy boundaries; no filter, audit, session or real network. */
final class CaddyAddressBoundaryContractTest {
  private static final CaddyClientAddressResolver RESOLVER = new CaddyClientAddressResolver();

  @Test
  void proxyBoundary001LoopbackAndNumericForwardedLiteralAreAccepted() {
    for (String peer : List.of("127.0.0.1", "::1"))
      for (String client : List.of("203.0.113.27", "2001:db8::9")) {
        var request = request();
        request.setRemoteAddr(peer);
        request.removeHeader("X-Forwarded-For");
        request.addHeader("X-Forwarded-For", client);
        assertEquals(client, RESOLVER.resolve(request).value());
      }
  }

  @Test
  void proxyBoundary002NullInvalidOrNonLoopbackPeerAndForwardedHeaderAreDenied() {
    for (String peer : new String[] {null, "", "not-an-ip", "192.0.2.1", "2001:db8::1"}) {
      var request = request();
      request.setRemoteAddr(peer);
      denied(request);
    }
    denied(headers("Forwarded", () -> null));
    var forwarded = request();
    forwarded.addHeader("Forwarded", "for=203.0.113.27;proto=https");
    denied(forwarded);
  }

  @Test
  void proxyBoundary003ExactlyOneLowercaseHttpsProtocolIsRequired() {
    denied(headers("X-Forwarded-Proto", () -> null));
    denied(headers("X-Forwarded-Proto", Collections::emptyEnumeration));
    denied(headers("X-Forwarded-Proto", () -> Collections.enumeration(Collections.singletonList(null))));
    for (List<String> values :
        List.of(List.of("http"), List.of("HTTPS"), List.of("https "), List.of("https", "https"))) {
      denied(headers("X-Forwarded-Proto", () -> Collections.enumeration(values)));
    }
  }

  @Test
  void proxyBoundary004ExactlyOneValidNumericClientFieldIsRequired() {
    denied(headers("X-Forwarded-For", () -> null));
    denied(headers("X-Forwarded-For", Collections::emptyEnumeration));
    denied(headers("X-Forwarded-For", () -> Collections.enumeration(Collections.singletonList(null))));
    for (List<String> values :
        List.of(List.of(""), List.of("example.invalid"), List.of("203.0.113.1, 192.0.2.1"),
            List.of("203.0.113.27", "203.0.113.28"))) {
      denied(headers("X-Forwarded-For", () -> Collections.enumeration(values)));
    }
  }

  @Test
  void proxyBoundary005ServletAndEnumerationFailuresUseFixedRedactedCatalog() {
    denied(
        configure(
            new MockHttpServletRequest() {
              @Override
              public String getRemoteAddr() {
                throw new IllegalStateException("PUBLIC_UNTRUSTED_RAW");
              }
            }));
    denied(
        headers(
            "Forwarded",
            () -> {
              throw new IllegalArgumentException("PUBLIC_UNTRUSTED_RAW");
            }));
    denied(
        headers(
            "X-Forwarded-Proto",
            () ->
                new Enumeration<String>() {
                  public boolean hasMoreElements() {
                    return true;
                  }

                  public String nextElement() {
                    throw new NoSuchElementException("PUBLIC_UNTRUSTED_RAW");
                  }
                }));
  }

  @Test
  void proxyBoundary006NullRequestIsRejectedAtTheApiBoundary() {
    assertThrows(NullPointerException.class, () -> RESOLVER.resolve(null));
  }

  private static MockHttpServletRequest request() {
    return configure(new MockHttpServletRequest());
  }

  private static MockHttpServletRequest configure(MockHttpServletRequest request) {
    request.setRemoteAddr("127.0.0.1");
    request.addHeader("X-Forwarded-Proto", "https");
    request.addHeader("X-Forwarded-For", "203.0.113.27");
    return request;
  }

  private static MockHttpServletRequest headers(
      String selected, Supplier<Enumeration<String>> values) {
    return configure(
        new MockHttpServletRequest() {
          @Override
          public Enumeration<String> getHeaders(String name) {
            return selected.equals(name) ? values.get() : super.getHeaders(name);
          }
        });
  }

  private static void denied(MockHttpServletRequest request) {
    var failure = assertThrows(CaddyRequestRejectedException.class, () -> RESOLVER.resolve(request));
    assertEquals("request proxy is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
