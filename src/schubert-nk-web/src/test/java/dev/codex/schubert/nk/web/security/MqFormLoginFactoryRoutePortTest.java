package dev.codex.schubert.nk.web.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.springframework.security.web.authentication.AuthenticationFailureHandler;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;

/** UI226/SS313,314,352; PT-WEB-LGNROUTE001..004. No credentials or authentication. */
final class MqFormLoginFactoryRoutePortTest {
  private static final String POST_METHOD = "POST";
  private static final String LOGIN_URI = "/login";
  private static final AuthenticationSuccessHandler NEVER_SUCCESS =
      (request, response, authentication) -> {
        throw new AssertionError("authentication success forbidden");
      };
  private static final AuthenticationFailureHandler NEVER_FAILURE =
      (request, response, failure) -> {
        throw new AssertionError("unexpected failure callback");
      };

  @Test
  void fourMissingPortsAreRejectedAndFactoryReturnsFreshFilters() {
    try (var ports = new Ports()) {
      var factory = new MqFormLoginFilterFactory();
      assertEquals(
          "provider",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(null, ports.contexts, NEVER_SUCCESS, NEVER_FAILURE))
              .getMessage());
      assertEquals(
          "contexts",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(ports.provider, null, NEVER_SUCCESS, NEVER_FAILURE))
              .getMessage());
      assertEquals(
          "success",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(ports.provider, ports.contexts, null, NEVER_FAILURE))
              .getMessage());
      assertEquals(
          "failure",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.create(ports.provider, ports.contexts, NEVER_SUCCESS, null))
              .getMessage());
      var first = factory.create(ports.provider, ports.contexts, NEVER_SUCCESS, NEVER_FAILURE);
      var second = factory.create(ports.provider, ports.contexts, NEVER_SUCCESS, NEVER_FAILURE);
      assertNotSame(first, second);
      assertEquals(first.getClass(), second.getClass());
    }
  }

  @Test
  void unmatchedMethodAndExactPathDelegateOnceWithoutReadingForm() throws Exception {
    try (var ports = new Ports()) {
      var filter =
          new MqFormLoginFilterFactory()
              .create(ports.provider, ports.contexts, NEVER_SUCCESS, NEVER_FAILURE);
      String[][] routes = {
        {"GET", LOGIN_URI}, {"HEAD", LOGIN_URI}, {"post", LOGIN_URI},
        {POST_METHOD, "/other"}, {POST_METHOD, "/login/"}, {POST_METHOD, null}
      };
      for (String[] route : routes) {
        var request = request(route[0], route[1], false);
        var response = response();
        var calls = new AtomicInteger();
        filter.doFilter(
            request,
            response,
            (actualRequest, actualResponse) -> {
              assertSame(request, actualRequest);
              assertSame(response, actualResponse);
              calls.incrementAndGet();
            });
        assertEquals(1, calls.get());
      }
    }
  }

  @Test
  void matchingPostRejectsEncodingBeforeFormAndUsesOnlySuppliedFailureHandler() throws Exception {
    try (var ports = new Ports()) {
      var request = request(POST_METHOD, LOGIN_URI, true);
      var response = response();
      var failures = new AtomicInteger();
      var filter =
          new MqFormLoginFilterFactory()
              .create(
                  ports.provider,
                  ports.contexts,
                  NEVER_SUCCESS,
                  (actualRequest, actualResponse, failure) -> {
                    assertSame(request, actualRequest);
                    assertSame(response, actualResponse);
                    assertEquals(LoginFormRejectedException.class, failure.getClass());
                    assertEquals("login form is invalid", failure.getMessage());
                    assertNull(failure.getCause());
                    failures.incrementAndGet();
                  });
      filter.doFilter(
          request,
          response,
          (ignoredRequest, ignoredResponse) -> {
            throw new AssertionError("rejected login must not continue");
          });
      assertEquals(1, failures.get());
    }
  }

  @Test
  void failureHandlerIOExceptionKeepsIdentityWithoutContinuing() {
    try (var ports = new Ports()) {
      var expected = new IOException("public fixture failure");
      var calls = new AtomicInteger();
      var filter =
          new MqFormLoginFilterFactory()
              .create(
                  ports.provider,
                  ports.contexts,
                  NEVER_SUCCESS,
                  (request, response, failure) -> {
                    calls.incrementAndGet();
                    throw expected;
                  });
      assertSame(
          expected,
          assertThrows(
              IOException.class,
              () ->
                  filter.doFilter(
                      request(POST_METHOD, LOGIN_URI, true),
                      response(),
                      (request, response) -> {
                        throw new AssertionError("failure must not continue");
                      })));
      assertEquals(1, calls.get());
    }
  }

  private static HttpServletRequest request(
      String method, @Nullable String uri, boolean encodingReadable) {
    return (HttpServletRequest)
        Proxy.newProxyInstance(
            HttpServletRequest.class.getClassLoader(),
            new Class<?>[] {HttpServletRequest.class},
            (proxy, call, arguments) -> {
              if (call.getName().equals("getMethod")) return method;
              if (call.getName().equals("getRequestURI")) return uri;
              if (call.getName().equals("getCharacterEncoding") && encodingReadable)
                return "ISO-8859-1";
              throw new AssertionError("form, session or address access forbidden: " + call.getName());
            });
  }

  private static HttpServletResponse response() {
    return (HttpServletResponse)
        Proxy.newProxyInstance(
            HttpServletResponse.class.getClassLoader(),
            new Class<?>[] {HttpServletResponse.class},
            (proxy, call, arguments) -> {
              throw new AssertionError("response access forbidden: " + call.getName());
            });
  }

  private static final class Ports implements AutoCloseable {
    private final SecurityContextOwnerPortFixture owner = new SecurityContextOwnerPortFixture();
    private final EncryptedSessionSecurityContextRepository contexts =
        new EncryptedSessionSecurityContextRepository(owner.sessions());
    private final MqAuthenticationProvider provider;

    Ports() {
      var clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
      var requester = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 1);
      JmsRequestSender sender =
          (id, bytes) -> {
            throw new AssertionError("JMS send forbidden");
          };
      Supplier<UUID> identifiers =
          () -> {
            throw new AssertionError("identifier generation forbidden");
          };
      provider =
          new MqAuthenticationProvider(
              new MqLoginClient(requester, sender, clock, identifiers, Duration.ofNanos(1)),
              new MqLoginContextProbe(requester, sender, clock, identifiers, Duration.ofNanos(1)));
    }

    @Override
    public void close() {
      owner.close();
    }
  }
}
