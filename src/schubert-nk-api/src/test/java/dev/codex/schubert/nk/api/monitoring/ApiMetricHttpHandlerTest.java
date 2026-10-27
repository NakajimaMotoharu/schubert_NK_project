package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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

/** 1817 APIMHTTP001..016: memory exchanges only, independent literal/byte oracle. */
final class ApiMetricHttpHandlerTest {
  private static final String GET_METHOD = "GET";
  private static final String READY_TRUE_SUFFIX = "1\n";
  private static final String READY_FALSE_SUFFIX = "0\n";
  private static final String DEBUG_MODE = "DEBUG";
  private static final String CONTENT_TYPE_HEADER = "Content-Type";
  private static final String NO_STORE_VALUE = "no-store";
  private static final String CACHE_CONTROL_HEADER = "Cache-Control";
  private static final String STANDARD_MODE = "STANDARD";
  private static final String PATH = "/actuator/prometheus";
  private static final String READY = "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready ";
  private static final String METRIC = "text/plain; version=0.0.4; charset=utf-8";

  @Test
  void apimhttp001() throws IOException {
    try (var context = standard()) {
      var calls = new AtomicInteger();
      var handler =
          new ApiMetricHttpHandler(
              context,
              () -> {
                calls.incrementAndGet();
                return true;
              });
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        handler.handle(exchange);
        response(exchange, 200, READY + READY_TRUE_SUFFIX, METRIC);
        assertEquals(1, calls.get());
        assertEquals(READY + READY_FALSE_SUFFIX, context.render(false));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp002() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        new ApiMetricHttpHandler(context, () -> false).handle(exchange);
        response(exchange, 200, READY + READY_FALSE_SUFFIX, METRIC);

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp003() throws IOException {
    try (var context =
        new ApiMetricContext<>(
            DEBUG_MODE,
            registry -> {
              var value = new double[] {7.5};
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "API", "state", "active")
                  .register(registry);
              return value;
            })) {
      context.initialize();
      var handler = new ApiMetricHttpHandler(context, () -> true);
      var first = new Exchange(GET_METHOD, PATH);
      try {

        handler.handle(first);
        String body = first.output.toString(StandardCharsets.UTF_8);
        assertTrue(body.startsWith(READY + READY_TRUE_SUFFIX));
        assertTrue(body.contains("nk_db_pool_connections{service=\"API\",state=\"active\"} 7.5\n"));
        assertTrue(body.contains("jvm_memory_used_bytes"));
        assertEquals(body.getBytes(StandardCharsets.UTF_8).length, first.length);
        assertEquals(200, first.status);
        assertEquals(METRIC, first.headers.getFirst(CONTENT_TYPE_HEADER));
        assertEquals(NO_STORE_VALUE, first.headers.getFirst(CACHE_CONTROL_HEADER));
        assertTrue(first.closed);
        context.bindings().orElseThrow()[0] = 9.5;
        var second = new Exchange(GET_METHOD, PATH);
        try {

          handler.handle(second);
          assertTrue(
              second
                  .output
                  .toString(StandardCharsets.UTF_8)
                  .contains("nk_db_pool_connections{service=\"API\",state=\"active\"} 9.5\n"));
          assertEquals(9.5, context.bindings().orElseThrow()[0]);

        } finally {
          if (!second.closed) second.close();
        }

      } finally {
        if (!first.closed) first.close();
      }
    }
  }

  @Test
  void apimhttp004() throws IOException {
    try (var context = new ApiMetricContext<>(STANDARD_MODE, registry -> "unused")) {
      var calls = new AtomicInteger();
      var handler =
          new ApiMetricHttpHandler(
              context,
              () -> {
                calls.incrementAndGet();
                return true;
              });
      for (String method : new String[] {"POST", "HEAD", "get", "OPTIONS"}) {
        var exchange = new Exchange(method, PATH);
        try {

          handler.handle(exchange);
          response(exchange, 405, "{}", "application/json; charset=utf-8");

        } finally {
          if (!exchange.closed) exchange.close();
        }
      }
      assertEquals(0, calls.get());
      context.initialize();
      assertEquals(READY + READY_TRUE_SUFFIX, context.render(true));
    }
  }

  @Test
  void apimhttp005() throws IOException {
    try (var context = new ApiMetricContext<>(STANDARD_MODE, registry -> "unused")) {
      var calls = new AtomicInteger();
      var handler =
          new ApiMetricHttpHandler(
              context,
              () -> {
                calls.incrementAndGet();
                return true;
              });
      for (String path :
          new String[] {"/actuator/prometheus/", "/actuator/%70rometheus", "/actuator/info"}) {
        var exchange = new Exchange(GET_METHOD, path);
        try {

          handler.handle(exchange);
          response(exchange, 404, "{}", "application/json; charset=utf-8");

        } finally {
          if (!exchange.closed) exchange.close();
        }
      }
      assertEquals(0, calls.get());
    }
  }

  @Test
  void apimhttp006() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange(GET_METHOD, PATH + "?unused=public");
      try {

        new ApiMetricHttpHandler(context, () -> true).handle(exchange);
        response(exchange, 200, READY + READY_TRUE_SUFFIX, METRIC);

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp007() {
    try (var context = standard()) {
      assertThrows(NullPointerException.class, () -> new ApiMetricHttpHandler(null, () -> true));
      assertThrows(NullPointerException.class, () -> new ApiMetricHttpHandler(context, null));
      var handler = new ApiMetricHttpHandler(context, () -> true);
      assertThrows(NullPointerException.class, () -> handler.handle(null));
      assertEquals(READY + READY_TRUE_SUFFIX, context.render(true));
    }
  }

  @Test
  void apimhttp008() {
    try (var context = new ApiMetricContext<>(STANDARD_MODE, registry -> "unused")) {
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        var handler = new ApiMetricHttpHandler(context, () -> true);
        assertThrows(IllegalStateException.class, () -> handler.handle(exchange));
        unpublished(exchange);
        context.initialize();
        assertEquals(READY + READY_FALSE_SUFFIX, context.render(false));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp009() {
    var context = standard();
    context.close();
    var exchange = new Exchange(GET_METHOD, PATH);
    try {

      assertThrows(
          IllegalStateException.class,
          () -> new ApiMetricHttpHandler(context, () -> true).handle(exchange));
      unpublished(exchange);

    } finally {
      if (!exchange.closed) exchange.close();
    }
  }

  @Test
  void apimhttp010() {
    try (var context = standard()) {
      var failure = new IllegalStateException("fixed fixture");
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        var handler =
            new ApiMetricHttpHandler(
                context,
                () -> {
                  throw failure;
                });
        assertSame(
            failure, assertThrows(IllegalStateException.class, () -> handler.handle(exchange)));
        unpublished(exchange);
        assertEquals(READY + READY_TRUE_SUFFIX, context.render(true));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp011() {
    try (var context = standard()) {
      var failure = new AssertionError("fixed fixture");
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        var handler =
            new ApiMetricHttpHandler(
                context,
                () -> {
                  throw failure;
                });
        assertSame(failure, assertThrows(AssertionError.class, () -> handler.handle(exchange)));
        unpublished(exchange);
        assertEquals(READY + READY_TRUE_SUFFIX, context.render(true));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp012() {
    try (var context = standard()) {
      var failure = new IOException("fixed headers");
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        exchange.headerFailure = failure;
        var handler = new ApiMetricHttpHandler(context, () -> true);
        assertSame(failure, assertThrows(IOException.class, () -> handler.handle(exchange)));
        assertEquals(1, exchange.headerCalls);
        assertTrue(exchange.closed);
        assertEquals(0, exchange.output.size());
        assertEquals(READY + READY_TRUE_SUFFIX, context.render(true));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp013() {
    try (var context = standard()) {
      var failure = new IOException("fixed output");
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        exchange.bodyFailure = failure;
        var handler = new ApiMetricHttpHandler(context, () -> false);
        assertSame(failure, assertThrows(IOException.class, () -> handler.handle(exchange)));
        assertEquals(200, exchange.status);
        assertTrue(exchange.closed);
        assertEquals(0, exchange.output.size());
        assertEquals(READY + READY_FALSE_SUFFIX, context.render(false));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp014() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange("POST", "/unknown");
      try {

        new ApiMetricHttpHandler(
                context,
                () -> {
                  throw new AssertionError("must not read");
                })
            .handle(exchange);
        response(exchange, 405, "{}", "application/json; charset=utf-8");

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp015() throws IOException {
    try (var context = standard()) {
      var next = new AtomicInteger();
      BooleanSupplier ready = () -> next.getAndIncrement() == 0;
      var handler = new ApiMetricHttpHandler(context, ready);
      var first = new Exchange(GET_METHOD, PATH);
      try {

        var second = new Exchange(GET_METHOD, PATH);
        try {

          handler.handle(first);
          handler.handle(second);
          response(first, 200, READY + READY_TRUE_SUFFIX, METRIC);
          response(second, 200, READY + READY_FALSE_SUFFIX, METRIC);
          assertEquals(2, next.get());

        } finally {
          if (!second.closed) second.close();
        }

      } finally {
        if (!first.closed) first.close();
      }
    }
  }

  @Test
  void apimhttp016() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        exchange.headers.set(CONTENT_TYPE_HEADER, "stale");
        exchange.headers.set(CACHE_CONTROL_HEADER, "public");
        new ApiMetricHttpHandler(context, () -> true).handle(exchange);
        response(exchange, 200, READY + READY_TRUE_SUFFIX, METRIC);
        assertEquals(1, exchange.headers.get(CONTENT_TYPE_HEADER).size());
        assertEquals(1, exchange.headers.get(CACHE_CONTROL_HEADER).size());
        assertEquals(READY + READY_FALSE_SUFFIX, context.render(false));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp017() throws IOException {
    try (var context = standard()) {
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        var handler = new ApiMetricHttpHandler(context, () -> true);
        handler.write(exchange);
        assertFalse(exchange.closed);
        assertEquals(0, exchange.closeCalls);
        assertEquals(200, exchange.status);
        assertEquals(READY + READY_TRUE_SUFFIX, exchange.output.toString(StandardCharsets.UTF_8));
        assertEquals(
            (READY + READY_TRUE_SUFFIX).getBytes(StandardCharsets.UTF_8).length, exchange.length);
        assertEquals(METRIC, exchange.headers.getFirst(CONTENT_TYPE_HEADER));
        assertEquals(NO_STORE_VALUE, exchange.headers.getFirst(CACHE_CONTROL_HEADER));
        exchange.close();
        response(exchange, 200, READY + READY_TRUE_SUFFIX, METRIC);
        assertEquals(READY + READY_FALSE_SUFFIX, context.render(false));
        assertThrows(NullPointerException.class, () -> handler.write(null));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp018() {
    try (var context = standard()) {
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        var failure = new IllegalStateException("fixed borrowed write");
        var handler =
            new ApiMetricHttpHandler(
                context,
                () -> {
                  throw failure;
                });
        assertSame(
            failure, assertThrows(IllegalStateException.class, () -> handler.write(exchange)));
        assertFalse(exchange.closed);
        assertEquals(0, exchange.closeCalls);
        assertEquals(0, exchange.headerCalls);
        assertEquals(0, exchange.output.size());
        assertTrue(exchange.headers.isEmpty());
        exchange.close();
        assertEquals(1, exchange.closeCalls);
        assertEquals(READY + READY_TRUE_SUFFIX, context.render(true));

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  @Test
  void apimhttp019SampledBindingUpdatesActualHttpBodyWithoutLifecycleTransfer() throws IOException {
    double[] value = {7.5};
    var samples = new AtomicInteger();
    var readiness = new AtomicInteger();
    try (var context =
        new ApiMetricContext<double[]>(
            DEBUG_MODE,
            registry -> {
              Gauge.builder("nk_db_pool_connections", value, state -> state[0])
                  .tags("service", "API", "state", "active")
                  .register(registry);
              return value;
            },
            binding -> {
              assertSame(value, binding);
              samples.incrementAndGet();
              binding[0] += 2;
            })) {
      context.initialize();
      var handler = new ApiMetricHttpHandler(context, () -> readiness.getAndIncrement() == 0);
      var first = new Exchange(GET_METHOD, PATH);
      try {

        var second = new Exchange(GET_METHOD, PATH);
        try {

          handler.handle(first);
          handler.handle(second);
          String firstText = first.output.toString(StandardCharsets.UTF_8);
          String secondText = second.output.toString(StandardCharsets.UTF_8);
          assertTrue(firstText.startsWith(READY + READY_TRUE_SUFFIX));
          assertTrue(secondText.startsWith(READY + READY_FALSE_SUFFIX));
          assertTrue(
              firstText.contains("nk_db_pool_connections{service=\"API\",state=\"active\"} 9.5\n"));
          assertTrue(
              secondText.contains(
                  "nk_db_pool_connections{service=\"API\",state=\"active\"} 11.5\n"));
          assertEquals(200, first.status);
          assertEquals(200, second.status);
          assertEquals(firstText.getBytes(StandardCharsets.UTF_8).length, first.length);
          assertEquals(secondText.getBytes(StandardCharsets.UTF_8).length, second.length);
          assertEquals(METRIC, first.headers.getFirst(CONTENT_TYPE_HEADER));
          assertEquals(NO_STORE_VALUE, second.headers.getFirst(CACHE_CONTROL_HEADER));
          assertEquals(1, first.closeCalls);
          assertEquals(1, second.closeCalls);
          assertSame(value, context.bindings().orElseThrow());
          assertEquals(11.5, value[0]);
          assertEquals(2, samples.get());
          assertEquals(2, readiness.get());

        } finally {
          if (!second.closed) second.close();
        }

      } finally {
        if (!first.closed) first.close();
      }
    }
  }

  @Test
  void apimhttp020TypedBorrowedPoolRefreshesIntoActualResponseWithoutControlOperations()
      throws IOException {
    var f = new DbPoolMetricObservationTest.Fixture();
    f.active = 3;
    f.idle = 5;
    f.pending = 2;
    f.maximum = 8;
    try (var context =
        new ApiMetricContext<ApiDbPoolMetricBinding>(
            DEBUG_MODE,
            registry -> new ApiDbPoolMetricBinding(f.pool(), f.config(), registry, DEBUG_MODE),
            ApiDbPoolMetricBinding::refresh)) {
      context.initialize();
      assertTrue(f.calls.isEmpty());
      var handler = new ApiMetricHttpHandler(context, () -> true);
      var first = new Exchange(GET_METHOD, PATH);
      try {

        handler.handle(first);
        String body = first.output.toString(StandardCharsets.UTF_8);
        assertTrue(body.startsWith(READY + READY_TRUE_SUFFIX));
        assertTrue(body.contains("nk_db_pool_connections{service=\"API\",state=\"active\"} 3.0\n"));
        assertTrue(body.contains("nk_db_pool_connections{service=\"API\",state=\"max\"} 8.0\n"));
        assertEquals(200, first.status);
        assertEquals(body.getBytes(StandardCharsets.UTF_8).length, first.length);
        assertEquals(METRIC, first.headers.getFirst(CONTENT_TYPE_HEADER));
        assertEquals(NO_STORE_VALUE, first.headers.getFirst(CACHE_CONTROL_HEADER));
        assertEquals(1, first.closeCalls);
        f.complete();
        f.calls.clear();
        f.maximum = 0;
        var missing = new Exchange(GET_METHOD, PATH);
        try {

          handler.handle(missing);
          String missingText = missing.output.toString(StandardCharsets.UTF_8);
          assertTrue(
              missingText.contains(
                  "nk_db_pool_connections{service=\"API\",state=\"active\"} NaN\n"));
          assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
          assertEquals(200, missing.status);
          assertEquals(1, missing.closeCalls);
          f.complete();

        } finally {
          if (!missing.closed) missing.close();
        }

      } finally {
        if (!first.closed) first.close();
      }
    }
    f.complete();
  }

  @Test
  void apimhttp021DeferredFactoryReachesHttpWithoutReacquiringBorrowedReferences()
      throws IOException {
    var f = new DbPoolMetricObservationTest.Fixture();
    f.active = 3;
    f.idle = 5;
    f.pending = 2;
    f.maximum = 8;
    var poolReads = new AtomicInteger();
    var configReads = new AtomicInteger();
    try (var context =
        ApiDbPoolMetricBinding.prepareContext(
            DEBUG_MODE,
            () -> {
              poolReads.incrementAndGet();
              return f.pool();
            },
            () -> {
              configReads.incrementAndGet();
              return f.config();
            })) {
      assertEquals(0, poolReads.get());
      assertEquals(0, configReads.get());
      context.initialize();
      assertTrue(f.calls.isEmpty());
      var handler = new ApiMetricHttpHandler(context, () -> true);
      for (int sample = 0; sample < 2; sample++) {
        f.active = sample == 0 ? 3 : 0;
        var exchange = new Exchange(GET_METHOD, PATH);
        try {

          handler.handle(exchange);
          String body = exchange.output.toString(StandardCharsets.UTF_8);
          assertTrue(body.startsWith(READY + READY_TRUE_SUFFIX));
          assertTrue(
              body.contains(
                  "nk_db_pool_connections{service=\"API\",state=\"active\"} "
                      + (sample == 0 ? "3.0" : "0.0")
                      + "\n"));
          assertTrue(body.contains("nk_db_pool_connections{service=\"API\",state=\"max\"} 8.0\n"));
          assertEquals(200, exchange.status);
          assertEquals(body.getBytes(StandardCharsets.UTF_8).length, exchange.length);
          assertEquals(METRIC, exchange.headers.getFirst(CONTENT_TYPE_HEADER));
          assertEquals(NO_STORE_VALUE, exchange.headers.getFirst(CACHE_CONTROL_HEADER));
          assertEquals(1, exchange.closeCalls);
          f.complete();
          f.calls.clear();

        } finally {
          if (!exchange.closed) exchange.close();
        }
      }
      assertEquals(1, poolReads.get());
      assertEquals(1, configReads.get());
    }
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void apimhttp022ServiceDefaultSourceIsExplicitlyMissingAtHttpBoundary() throws IOException {
    var f = new DbPoolMetricObservationTest.Fixture();
    try (var context = ApiServiceMetricBinding.prepareContext(DEBUG_MODE, f::pool, f::config)) {
      context.initialize();
      var exchange = new Exchange(GET_METHOD, PATH);
      try {

        new ApiMetricHttpHandler(context, () -> true).handle(exchange);
        String body = exchange.output.toString(StandardCharsets.UTF_8);
        assertTrue(body.startsWith(READY + READY_TRUE_SUFFIX));
        assertTrue(body.contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} NaN\n"));
        assertTrue(body.contains("nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} NaN\n"));
        assertTrue(context.bindings().orElseThrow().snapshot().isEmpty());
        assertEquals(200, exchange.status);
        assertEquals(body.getBytes(StandardCharsets.UTF_8).length, exchange.length);
        assertEquals(METRIC, exchange.headers.getFirst(CONTENT_TYPE_HEADER));
        assertEquals(NO_STORE_VALUE, exchange.headers.getFirst(CACHE_CONTROL_HEADER));
        assertEquals(1, exchange.closeCalls);
        f.complete();

      } finally {
        if (!exchange.closed) exchange.close();
      }
    }
  }

  private static ApiMetricContext<String> standard() {
    var context =
        new ApiMetricContext<String>(
            STANDARD_MODE,
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
    assertEquals(type, exchange.headers.getFirst(CONTENT_TYPE_HEADER));
    assertEquals(NO_STORE_VALUE, exchange.headers.getFirst(CACHE_CONTROL_HEADER));
    assertEquals(1, exchange.headerCalls);
    assertTrue(exchange.closed);
    assertEquals(1, exchange.closeCalls);
  }

  private static void unpublished(Exchange exchange) {
    assertTrue(exchange.closed);
    assertEquals(1, exchange.closeCalls);
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
    private int closeCalls;
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
      closeCalls++;
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

  @Test
  void apimhttp023CallerFailureStillCleansOnceAndCompletedCloseIsNotRepeated() {
    var exchange = new Exchange(GET_METHOD, PATH);
    try {
      var failure = new AssertionError("caller cleanup fixture");
      assertFalse(exchange.closed);
      assertSame(
          failure,
          assertThrows(
              AssertionError.class,
              () -> {
                try {
                  throw failure;
                } finally {
                  if (!exchange.closed) exchange.close();
                }
              }));
      assertTrue(exchange.closed);
      assertEquals(1, exchange.closeCalls);
      if (!exchange.closed) exchange.close();
      assertEquals(1, exchange.closeCalls);
    } finally {
      if (!exchange.closed) exchange.close();
    }
  }
}
