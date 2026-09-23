package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

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
  @TempDir Path root;

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
      var login = send(client, server.port(), "GET", "/login");
      assertEquals(200, login.statusCode());
      var document = Jsoup.parse(login.body());
      assertEquals("schubert NK - ログイン", document.title());
      assertEquals("schubert NK", document.selectFirst("h1").text());
      assertEquals("fixture", document.selectFirst("input[name=_csrf]").val());
      assertEquals(404, send(client, server.port(), "GET", "/no-such-route").statusCode());
      assertEquals(200, send(client, server.port(), "HEAD", "/login").statusCode());
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
      assertEquals(200, send(client, port, "GET", "/login").statusCode());
      server.close();
      server.close();
      assertThrows(IllegalStateException.class, server::port);
      assertThrows(Exception.class, () -> send(client, port, "GET", "/login"));
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
      var response = send(client, server.port(), "GET", "/pt-port");
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
      assertEquals(200, send(client, server.port(), "GET", "/login").statusCode());
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
