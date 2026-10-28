package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import jakarta.servlet.Filter;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.catalina.LifecycleException;
import org.apache.catalina.connector.Connector;
import org.apache.catalina.startup.Tomcat;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

/** PG220/PT-SCR109..111; actual loopback Tomcat/MVC, not API/JMS or NK CHR. */
class WebHttpServerTest {
  private static final String FIXTURE_SYNTHETIC_ACQUISITION_5736B45C = "synthetic acquisition";
  private static final String FIXTURE_LOGIN_F843C044 = "/login";
  private static final String FIXTURE_GET_04F32A7E = "GET";
  @TempDir Path root;

  /** SS313/342/SSC312/PG-D461/PT-HTTP-OWN003; no container/owner notification on failed get. */
  @Test
  void httpOwn003FailedSupplierIdentityAndNullNeverNotifyOwner() {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    for (Throwable primary :
        java.util.List.of(
            new IllegalArgumentException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new IllegalStateException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new NullPointerException(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C),
            new AssertionError(FIXTURE_SYNTHETIC_ACQUISITION_5736B45C))) {
      var calls = new AtomicInteger();
      var notifications = new AtomicInteger();
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () ->
                  WebHttpServer.startWithOwner(
                      root,
                      0,
                      security,
                      Map.of(),
                      () -> {
                        assertEquals(1, calls.incrementAndGet());
                        if (primary instanceof RuntimeException unchecked) throw unchecked;
                        throw (Error) primary;
                      },
                      server -> notifications.incrementAndGet())));
      assertEquals(1, calls.get());
      assertEquals(0, notifications.get());
    }
    var nullCalls = new AtomicInteger();
    var notifications = new AtomicInteger();
    assertEquals(
        "tomcatFactory result",
        assertThrows(
                NullPointerException.class,
                () ->
                    WebHttpServer.startWithOwner(
                        root,
                        0,
                        security,
                        Map.of(),
                        () -> {
                          nullCalls.incrementAndGet();
                          return null;
                        },
                        server -> notifications.incrementAndGet()))
            .getMessage());
    assertEquals(1, nullCalls.get());
    assertEquals(0, notifications.get());
  }

  @Test
  void nativeOwner001CapturePrecedesVendorStartAndFatalKeepsRetryableOwner() throws Exception {
    var captured = new java.util.concurrent.atomic.AtomicReference<WebHttpServer>();
    var stops = new AtomicInteger();
    var destroys = new AtomicInteger();
    Error fatal = new LinkageError("synthetic startup fatal");
    var container =
        new Tomcat() {
          @Override
          public void start() throws LifecycleException {
            assertNotNull(captured.get());
            assertThrows(IllegalStateException.class, captured.get()::port);
            assertThrows(IllegalStateException.class, captured.get()::mappedPaths);
            super.start();
            throw fatal;
          }

          @Override
          public void stop() throws LifecycleException {
            if (stops.incrementAndGet() == 1) throw new LifecycleException("synthetic UNKNOWN");
            super.stop();
          }

          @Override
          public void destroy() throws LifecycleException {
            destroys.incrementAndGet();
            super.destroy();
          }
        };
    assertSame(
        fatal,
        assertThrows(
            LinkageError.class,
            () ->
                WebHttpServer.startWithOwner(
                    root,
                    0,
                    (r, s, c) -> c.doFilter(r, s),
                    Map.of(),
                    () -> container,
                    captured::set)));
    int bound = container.getConnector().getLocalPort();
    assertTrue(bound > 0);
    assertEquals(0, destroys.get());
    try {
      assertThrows(LifecycleException.class, captured.get()::close);
      assertEquals(0, destroys.get());
      captured.get().close();
      assertEquals(2, stops.get());
      assertEquals(1, destroys.get());
      captured.get().close();
      assertEquals(1, destroys.get());
      try (var listener = new java.net.ServerSocket(bound)) {
        assertEquals(bound, listener.getLocalPort());
      }
    } finally {
      captured.get().close();
    }
  }

  @Test
  void nativeOwner002ActualOwnedSuccessAndNullRefusal() throws Exception {
    Filter security = (r, s, c) -> c.doFilter(r, s);
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.startOwned(root, 0, security, Map.of(), null));
    var captured = new java.util.concurrent.atomic.AtomicReference<WebHttpServer>();
    var server = WebHttpServer.startOwned(root, 0, security, Map.of(), captured::set);
    try (var client = HttpClient.newHttpClient()) {
      assertSame(server, captured.get());
      assertTrue(server.mappedPaths().contains(FIXTURE_LOGIN_F843C044));
      assertEquals(
          200,
          send(client, server.port(), FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044).statusCode());
    } finally {
      server.close();
    }
  }

  @Test
  void nativeOwner003LegacyFatalCleanupPreservesIdentityAndSelfSuppression() {
    for (int mode : new int[] {0, 1, 2}) {
      Error primary = new LinkageError("synthetic primary");
      Error secondary = new AssertionError("synthetic cleanup");
      var closes = new AtomicInteger();
      var vendor =
          new Tomcat() {
            @Override
            public void start() {
              throw primary;
            }

            @Override
            public void destroy() throws LifecycleException {
              closes.incrementAndGet();
              super.destroy();
              if (mode == 1) throw secondary;
              if (mode == 2) throw primary;
            }
          };
      assertSame(
          primary,
          assertThrows(
              LinkageError.class,
              () ->
                  WebHttpServer.startWithFactory(
                      root, 0, (r, s, c) -> c.doFilter(r, s), () -> vendor)));
      assertEquals(1, closes.get());
      assertEquals(mode == 1 ? 1 : 0, primary.getSuppressed().length);
      if (mode == 1) assertSame(secondary, primary.getSuppressed()[0]);
    }
  }

  @Test
  void rerun008UnknownHttpStopAndDestroyRemainRetryableWithoutSkippingPhase() throws Exception {
    for (boolean stopFails : new boolean[] {true, false}) {
      var stops = new AtomicInteger();
      var destroys = new AtomicInteger();
      var container =
          new Tomcat() {
            @Override
            public void stop() throws LifecycleException {
              if (stops.incrementAndGet() == 1 && stopFails)
                throw new LifecycleException("synthetic unknown stop");
              super.stop();
            }

            @Override
            public void destroy() throws LifecycleException {
              if (destroys.incrementAndGet() == 1 && !stopFails)
                throw new LifecycleException("synthetic unknown destroy");
              super.destroy();
            }
          };
      var server =
          WebHttpServer.startWithFactory(root, 0, (r, s, c) -> c.doFilter(r, s), () -> container);
      assertThrows(LifecycleException.class, server::close);
      assertThrows(IllegalStateException.class, server::port);
      assertEquals(stopFails ? 0 : 1, destroys.get());
      server.close();
      assertEquals(stopFails ? 2 : 1, stops.get());
      assertEquals(stopFails ? 1 : 2, destroys.get());
      server.close();
      assertEquals(stopFails ? 1 : 2, destroys.get());
    }
  }

  @Test
  void scr109ActualLoopbackLoginAndClosedRoutes() throws Exception {
    var admissions = new AtomicInteger();
    Filter security =
        (request, response, chain) -> {
          admissions.incrementAndGet();
          request.setAttribute(
              CsrfToken.class.getName(), new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "fixture"));
          chain.doFilter(request, response);
        };
    try (var server = WebHttpServer.start(root, 0, security);
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      var login = send(client, server.port(), FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044);
      assertEquals(200, login.statusCode());
      var document = Jsoup.parse(login.body());
      assertEquals("schubert NK - ログイン", document.title());
      assertEquals("schubert NK", document.selectFirst("h1").text());
      assertEquals("fixture", document.selectFirst("input[name=_csrf]").val());
      assertEquals(
          404, send(client, server.port(), FIXTURE_GET_04F32A7E, "/no-such-route").statusCode());
      assertEquals(200, send(client, server.port(), "HEAD", FIXTURE_LOGIN_F843C044).statusCode());
      assertEquals(3, admissions.get());
    }
  }

  @Test
  void scr110InvalidStartupFailsBeforeBinding() throws Exception {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    assertThrows(NullPointerException.class, () -> WebHttpServer.start(null, 0, security));
    assertThrows(NullPointerException.class, () -> WebHttpServer.start(root, 0, null));
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.start(root, 0, security, (Class<?>[]) null));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebHttpServer.start(root.resolve("missing"), 0, security));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebHttpServer.start(Files.createFile(root.resolve("file")), 0, security));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            WebHttpServer.start(Files.createSymbolicLink(root.resolve("link"), root), 0, security));
    assertThrows(IllegalArgumentException.class, () -> WebHttpServer.start(root, -1, security));
    assertThrows(IllegalArgumentException.class, () -> WebHttpServer.start(root, 65536, security));
    assertThrows(
        IllegalArgumentException.class,
        () -> WebHttpServer.start(root, 0, security, (Class<?>) null));
    assertThrows(
        Exception.class, () -> WebHttpServer.start(root, 0, security, BrokenConfiguration.class));
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.startWithFactory(root, 0, security, null, BrokenConfiguration.class));
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.startWithFactory(root, 0, security, () -> null));
    assertThrows(
        IllegalStateException.class,
        () ->
            WebHttpServer.startWithFactory(
                root,
                0,
                security,
                () ->
                    new Tomcat() {
                      @Override
                      public Connector getConnector() {
                        return new Connector() {
                          @Override
                          public boolean setProperty(String name, String value) {
                            if ("address".equals(name)) return false;
                            return super.setProperty(name, value);
                          }
                        };
                      }
                    }));
  }

  @Test
  void scr112StartupWithoutStartedContextAndCleanupFailureAreVisible() {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    assertThrows(
        LifecycleException.class,
        () ->
            WebHttpServer.startWithFactory(
                root,
                0,
                security,
                () ->
                    new Tomcat() {
                      @Override
                      public void start() {}
                    }));
    var failure =
        assertThrows(
            LifecycleException.class,
            () ->
                WebHttpServer.startWithFactory(
                    root,
                    0,
                    security,
                    () ->
                        new Tomcat() {
                          @Override
                          public void start() throws LifecycleException {
                            throw new LifecycleException("synthetic startup failure");
                          }

                          @Override
                          public void destroy() throws LifecycleException {
                            throw new LifecycleException("synthetic cleanup failure");
                          }
                        }));
    assertEquals("synthetic startup failure", failure.getMessage());
    assertEquals(1, failure.getSuppressed().length);
    assertEquals("synthetic cleanup failure", failure.getSuppressed()[0].getMessage());
  }

  @Test
  void scr111CloseIsIdempotentAndPortBecomesUnavailable() throws Exception {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    var server = WebHttpServer.start(root, 0, security);
    int port = server.port();
    assertTrue(port > 0);
    try (var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      assertEquals(
          200, send(client, port, FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044).statusCode());
      server.close();
      server.close();
      assertThrows(IllegalStateException.class, server::port);
      assertThrows(
          Exception.class, () -> send(client, port, FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044));
    } finally {
      server.close();
    }
  }

  @Test
  void scr120CallerOwnedPortReachesRealFeatureController() throws Exception {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    var supplied = new InjectedPort("PG227-PORT");
    try (var server =
            WebHttpServer.start(
                root,
                0,
                security,
                Map.of(InjectedPort.class, supplied),
                InjectedConfiguration.class);
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      var response = send(client, server.port(), FIXTURE_GET_04F32A7E, "/pt-port");
      assertEquals(200, response.statusCode());
      assertEquals("PG227-PORT", response.body());
    }
  }

  @Test
  void scr121InvalidPortRegistrationFailsBeforeTomcatCreation() {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    var starts = new AtomicInteger();
    java.util.function.Supplier<Tomcat> factory =
        () -> {
          starts.incrementAndGet();
          return new Tomcat();
        };
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.startWithFactory(root, 0, security, null, factory));
    var nullKey = new HashMap<Class<?>, Object>();
    nullKey.put(null, new InjectedPort("x"));
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.startWithFactory(root, 0, security, nullKey, factory));
    var nullValue = new HashMap<Class<?>, Object>();
    nullValue.put(InjectedPort.class, null);
    assertThrows(
        NullPointerException.class,
        () -> WebHttpServer.startWithFactory(root, 0, security, nullValue, factory));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            WebHttpServer.startWithFactory(
                root, 0, security, Map.of(String.class, new InjectedPort("x")), factory));
    assertEquals(0, starts.get());
  }

  @Test
  void scr123LegacyFactoryOverloadReturnsStartedServer() throws Exception {
    Filter security = (request, response, chain) -> chain.doFilter(request, response);
    try (var server = WebHttpServer.startWithFactory(root, 0, security, Tomcat::new);
        var client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build()) {
      assertEquals(
          200,
          send(client, server.port(), FIXTURE_GET_04F32A7E, FIXTURE_LOGIN_F843C044).statusCode());
    }
  }

  private static HttpResponse<String> send(HttpClient client, int port, String method, String path)
      throws Exception {
    var request =
        HttpRequest.newBuilder(URI.create("http://127.0.0.1:" + port + path))
            .timeout(Duration.ofSeconds(3))
            .method(method, HttpRequest.BodyPublishers.noBody())
            .build();
    return client.send(request, HttpResponse.BodyHandlers.ofString());
  }

  @Configuration(proxyBeanMethods = false)
  static class BrokenConfiguration {
    @Bean
    String broken() {
      throw new IllegalStateException("synthetic startup failure");
    }
  }

  record InjectedPort(String value) {}

  @Controller
  static class InjectedController {
    private final InjectedPort port;

    InjectedController(InjectedPort port) {
      this.port = port;
    }

    @GetMapping("/pt-port")
    @ResponseBody
    String text() {
      return port.value();
    }
  }

  @Configuration(proxyBeanMethods = false)
  static class InjectedConfiguration {
    @Bean
    InjectedController injectedController(InjectedPort port) {
      return new InjectedController(port);
    }
  }
}
