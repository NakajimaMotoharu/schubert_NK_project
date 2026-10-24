package dev.codex.schubert.nk.web.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpContext;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpPrincipal;
import io.micrometer.core.instrument.Gauge;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BooleanSupplier;
import org.junit.jupiter.api.Test;

/** 1817 WEBMHTTP001..016: memory exchanges only, independent literal/byte oracle. */
final class WebMetricHttpHandlerTest {
  private static final String PATH = "/actuator/prometheus";
  private static final String READY = "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready ";
  private static final String METRIC = "text/plain; version=0.0.4; charset=utf-8";

  @Test
  void webmhttp001() throws IOException {
    try (var context = standard()) {
      var calls = new AtomicInteger();
      var handler =
          new WebMetricHttpHandler(
              context,
              () -> {
                calls.incrementAndGet();
                return true;
              });
      var exchange = new Exchange("GET", PATH);
      handler.handle(exchange);
      response(exchange, 200, READY + "1\n", METRIC);
      assertEquals(1, calls.get());
      assertEquals(READY + "0\n", context.render(false));
    }
  }

  @Test
  void webmhttp002() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange("GET", PATH);
      new WebMetricHttpHandler(context, () -> false).handle(exchange);
      response(exchange, 200, READY + "0\n", METRIC);
    }
  }

  @Test
  void webmhttp003() throws IOException {
    try (var context =
        new WebMetricContext<>(
            "DEBUG",
            registry -> {
              var value = new double[] {7.5};
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "WEB", "state", "active")
                  .register(registry);
              return value;
            })) {
      context.initialize();
      var handler = new WebMetricHttpHandler(context, () -> true);
      var first = new Exchange("GET", PATH);
      handler.handle(first);
      String body = first.output.toString(StandardCharsets.UTF_8);
      assertTrue(body.startsWith(READY + "1\n"));
      assertTrue(body.contains("nk_db_pool_connections{service=\"WEB\",state=\"active\"} 7.5\n"));
      assertTrue(body.contains("jvm_memory_used_bytes"));
      assertEquals(body.getBytes(StandardCharsets.UTF_8).length, first.length);
      assertEquals(200, first.status);
      assertEquals(METRIC, first.headers.getFirst("Content-Type"));
      assertEquals("no-store", first.headers.getFirst("Cache-Control"));
      assertTrue(first.closed);
      context.bindings().orElseThrow()[0] = 9.5;
      var second = new Exchange("GET", PATH);
      handler.handle(second);
      assertTrue(
          second
              .output
              .toString(StandardCharsets.UTF_8)
              .contains("nk_db_pool_connections{service=\"WEB\",state=\"active\"} 9.5\n"));
      assertEquals(9.5, context.bindings().orElseThrow()[0]);
    }
  }

  @Test
  void webmhttp004() throws IOException {
    try (var context = new WebMetricContext<>("STANDARD", registry -> "unused")) {
      var calls = new AtomicInteger();
      var handler =
          new WebMetricHttpHandler(
              context,
              () -> {
                calls.incrementAndGet();
                return true;
              });
      for (String method : new String[] {"POST", "HEAD", "get", "OPTIONS"}) {
        var exchange = new Exchange(method, PATH);
        handler.handle(exchange);
        response(exchange, 405, "{}", "application/json; charset=utf-8");
      }
      assertEquals(0, calls.get());
      context.initialize();
      assertEquals(READY + "1\n", context.render(true));
    }
  }

  @Test
  void webmhttp005() throws IOException {
    try (var context = new WebMetricContext<>("STANDARD", registry -> "unused")) {
      var calls = new AtomicInteger();
      var handler =
          new WebMetricHttpHandler(
              context,
              () -> {
                calls.incrementAndGet();
                return true;
              });
      for (String path :
          new String[] {"/actuator/prometheus/", "/actuator/%70rometheus", "/actuator/info"}) {
        var exchange = new Exchange("GET", path);
        handler.handle(exchange);
        response(exchange, 404, "{}", "application/json; charset=utf-8");
      }
      assertEquals(0, calls.get());
    }
  }

  @Test
  void webmhttp006() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange("GET", PATH + "?unused=public");
      new WebMetricHttpHandler(context, () -> true).handle(exchange);
      response(exchange, 200, READY + "1\n", METRIC);
    }
  }

  @Test
  void webmhttp007() {
    try (var context = standard()) {
      assertThrows(NullPointerException.class, () -> new WebMetricHttpHandler(null, () -> true));
      assertThrows(NullPointerException.class, () -> new WebMetricHttpHandler(context, null));
      var handler = new WebMetricHttpHandler(context, () -> true);
      assertThrows(NullPointerException.class, () -> handler.handle(null));
      assertEquals(READY + "1\n", context.render(true));
    }
  }

  @Test
  void webmhttp008() {
    try (var context = new WebMetricContext<>("STANDARD", registry -> "unused")) {
      var exchange = new Exchange("GET", PATH);
      var handler = new WebMetricHttpHandler(context, () -> true);
      assertThrows(IllegalStateException.class, () -> handler.handle(exchange));
      unpublished(exchange);
      context.initialize();
      assertEquals(READY + "0\n", context.render(false));
    }
  }

  @Test
  void webmhttp009() {
    var context = standard();
    context.close();
    var exchange = new Exchange("GET", PATH);
    assertThrows(
        IllegalStateException.class,
        () -> new WebMetricHttpHandler(context, () -> true).handle(exchange));
    unpublished(exchange);
  }

  @Test
  void webmhttp010() {
    try (var context = standard()) {
      var failure = new IllegalStateException("fixed fixture");
      var exchange = new Exchange("GET", PATH);
      var handler =
          new WebMetricHttpHandler(
              context,
              () -> {
                throw failure;
              });
      assertSame(
          failure, assertThrows(IllegalStateException.class, () -> handler.handle(exchange)));
      unpublished(exchange);
      assertEquals(READY + "1\n", context.render(true));
    }
  }

  @Test
  void webmhttp011() {
    try (var context = standard()) {
      var failure = new AssertionError("fixed fixture");
      var exchange = new Exchange("GET", PATH);
      var handler =
          new WebMetricHttpHandler(
              context,
              () -> {
                throw failure;
              });
      assertSame(failure, assertThrows(AssertionError.class, () -> handler.handle(exchange)));
      unpublished(exchange);
      assertEquals(READY + "1\n", context.render(true));
    }
  }

  @Test
  void webmhttp012() {
    try (var context = standard()) {
      var failure = new IOException("fixed headers");
      var exchange = new Exchange("GET", PATH);
      exchange.headerFailure = failure;
      var handler = new WebMetricHttpHandler(context, () -> true);
      assertSame(failure, assertThrows(IOException.class, () -> handler.handle(exchange)));
      assertEquals(1, exchange.headerCalls);
      assertTrue(exchange.closed);
      assertEquals(0, exchange.output.size());
      assertEquals(READY + "1\n", context.render(true));
    }
  }

  @Test
  void webmhttp013() {
    try (var context = standard()) {
      var failure = new IOException("fixed output");
      var exchange = new Exchange("GET", PATH);
      exchange.bodyFailure = failure;
      var handler = new WebMetricHttpHandler(context, () -> false);
      assertSame(failure, assertThrows(IOException.class, () -> handler.handle(exchange)));
      assertEquals(200, exchange.status);
      assertTrue(exchange.closed);
      assertEquals(0, exchange.output.size());
      assertEquals(READY + "0\n", context.render(false));
    }
  }

  @Test
  void webmhttp014() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange("POST", "/unknown");
      new WebMetricHttpHandler(
              context,
              () -> {
                throw new AssertionError("must not read");
              })
          .handle(exchange);
      response(exchange, 405, "{}", "application/json; charset=utf-8");
    }
  }

  @Test
  void webmhttp015() throws IOException {
    try (var context = standard()) {
      var next = new AtomicInteger();
      BooleanSupplier ready = () -> next.getAndIncrement() == 0;
      var handler = new WebMetricHttpHandler(context, ready);
      var first = new Exchange("GET", PATH);
      var second = new Exchange("GET", PATH);
      handler.handle(first);
      handler.handle(second);
      response(first, 200, READY + "1\n", METRIC);
      response(second, 200, READY + "0\n", METRIC);
      assertEquals(2, next.get());
    }
  }

  @Test
  void webmhttp016() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange("GET", PATH);
      exchange.headers.set("Content-Type", "stale");
      exchange.headers.set("Cache-Control", "public");
      new WebMetricHttpHandler(context, () -> true).handle(exchange);
      response(exchange, 200, READY + "1\n", METRIC);
      assertEquals(1, exchange.headers.get("Content-Type").size());
      assertEquals(1, exchange.headers.get("Cache-Control").size());
      assertEquals(READY + "0\n", context.render(false));
    }
  }

  private static WebMetricContext<String> standard() {
    var context =
        new WebMetricContext<String>(
            "STANDARD",
            registry -> {
              throw new AssertionError("STD setup");
            });
    context.initialize();
    return context;
  }

  private static void response(Exchange exchange, int status, String body, String type) {
    assertEquals(status, exchange.status);
    assertEquals(body, exchange.output.toString(StandardCharsets.UTF_8));
    assertEquals(body.getBytes(StandardCharsets.UTF_8).length, exchange.length);
    assertEquals(type, exchange.headers.getFirst("Content-Type"));
    assertEquals("no-store", exchange.headers.getFirst("Cache-Control"));
    assertEquals(1, exchange.headerCalls);
    assertTrue(exchange.closed);
  }

  private static void unpublished(Exchange exchange) {
    assertTrue(exchange.closed);
    assertEquals(0, exchange.headerCalls);
    assertEquals(0, exchange.output.size());
    assertTrue(exchange.headers.isEmpty());
  }

  private static final class Exchange extends HttpExchange {
    private final String method;
    private final URI uri;
    private final Headers headers = new Headers();
    private final ByteArrayOutputStream output = new ByteArrayOutputStream();
    private IOException headerFailure;
    private IOException bodyFailure;
    private boolean closed;
    private int status;
    private long length;
    private int headerCalls;

    private Exchange(String method, String path) {
      this.method = method;
      this.uri = URI.create(path);
    }

    @Override
    public Headers getRequestHeaders() {
      return new Headers();
    }

    @Override
    public Headers getResponseHeaders() {
      return headers;
    }

    @Override
    public URI getRequestURI() {
      return uri;
    }

    @Override
    public String getRequestMethod() {
      return method;
    }

    @Override
    public HttpContext getHttpContext() {
      throw new UnsupportedOperationException();
    }

    @Override
    public void close() {
      closed = true;
    }

    @Override
    public InputStream getRequestBody() {
      return new ByteArrayInputStream(new byte[0]);
    }

    @Override
    public OutputStream getResponseBody() {
      return new OutputStream() {
        @Override
        public void write(int value) throws IOException {
          if (bodyFailure != null) throw bodyFailure;
          output.write(value);
        }

        @Override
        public void write(byte[] bytes, int offset, int count) throws IOException {
          if (bodyFailure != null) throw bodyFailure;
          output.write(bytes, offset, count);
        }
      };
    }

    @Override
    public void sendResponseHeaders(int code, long size) throws IOException {
      headerCalls++;
      if (headerFailure != null) throw headerFailure;
      status = code;
      length = size;
    }

    @Override
    public InetSocketAddress getRemoteAddress() {
      throw new UnsupportedOperationException();
    }

    @Override
    public int getResponseCode() {
      return status;
    }

    @Override
    public InetSocketAddress getLocalAddress() {
      throw new UnsupportedOperationException();
    }

    @Override
    public String getProtocol() {
      return "HTTP/1.1";
    }

    @Override
    public Object getAttribute(String name) {
      throw new UnsupportedOperationException();
    }

    @Override
    public void setAttribute(String name, Object value) {
      throw new UnsupportedOperationException();
    }

    @Override
    public void setStreams(InputStream input, OutputStream stream) {
      throw new UnsupportedOperationException();
    }

    @Override
    public HttpPrincipal getPrincipal() {
      throw new UnsupportedOperationException();
    }
  }
}
