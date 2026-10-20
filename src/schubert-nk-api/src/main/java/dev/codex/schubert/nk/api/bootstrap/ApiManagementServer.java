package dev.codex.schubert.nk.api.bootstrap;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;

/** Fixed loopback management only. SS342 §5.2/SSC158/PG-D334/PT-OPS-API-READY001..008. */
final class ApiManagementServer implements AutoCloseable {
  private static final String INFORMATION_PATH = "/actuator/info";
  private static final String METRICS_PATH = "/actuator/prometheus";
  private static final int JSON_OPENING_DELIMITER_LENGTH = 1;

  @FunctionalInterface
  interface Factory {
    HttpServer create(InetSocketAddress address, int backlog) throws IOException;
  }

  private final HttpServer server;
  private final ThreadPoolExecutor executor;
  private final BooleanSupplier healthy;
  private final String information;
  private final AtomicBoolean promoted = new AtomicBoolean();
  private final AtomicBoolean promotionAttempted = new AtomicBoolean();
  private final AtomicBoolean closed = new AtomicBoolean();

  static ApiManagementServer open(Map<String, String> information, BooleanSupplier healthy)
      throws IOException {
    return open(information, healthy, 8091);
  }

  // Package-local ephemeral-port component PT; production caller always uses fixed overload.
  static ApiManagementServer open(
      Map<String, String> information, BooleanSupplier healthy, int port) throws IOException {
    return open(information, healthy, port, HttpServer::create);
  }

  static ApiManagementServer open(
      Map<String, String> information, BooleanSupplier healthy, int port, Factory factory)
      throws IOException {
    Objects.requireNonNull(information, "public information");
    Objects.requireNonNull(healthy, "runtime health");
    Objects.requireNonNull(factory, "management factory");
    String json = publicJson(information);
    var server =
        Objects.requireNonNull(
            factory.create(new InetSocketAddress("127.0.0.1", port), 32), "management server");
    var executor =
        new ThreadPoolExecutor(
            1,
            1,
            0,
            TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(32),
            task -> {
              var thread = new Thread(task, "api-management");
              thread.setDaemon(true);
              return thread;
            });
    var result = new ApiManagementServer(server, executor, healthy, json);
    try {
      server.setExecutor(executor);
      server.createContext("/", result::respond);
      server.start();
      return result;
    } catch (RuntimeException | Error failure) {
      result.close();
      throw failure;
    }
  }

  private ApiManagementServer(
      HttpServer server, ThreadPoolExecutor executor, BooleanSupplier healthy, String information) {
    this.server = server;
    this.executor = executor;
    this.healthy = healthy;
    this.information = information;
  }

  private static String publicJson(Map<String, String> information) {
    var keys = List.of("commit", "app", "config", "schema", "protocol");
    if (!information.keySet().equals(java.util.Set.copyOf(keys)))
      throw new IllegalArgumentException("invalid public information");
    if (!Objects.requireNonNull(information.get("commit"), "release commit")
        .matches("[0-9a-f]{40}")) throw new IllegalArgumentException("invalid public commit");
    var json = new StringBuilder("{");
    for (String key : keys) {
      String value = Objects.requireNonNull(information.get(key), "public version");
      if (!value.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,127}"))
        throw new IllegalArgumentException("invalid public version");
      if (json.length() > JSON_OPENING_DELIMITER_LENGTH) json.append(',');
      json.append('"').append(key).append("\":\"").append(value).append('"');
    }
    return json.append('}').toString();
  }

  void promote(ServiceStartupAdmission.Ready ready) throws IOException {
    Objects.requireNonNull(ready, "admission ready");
    if (closed.get() || !promotionAttempted.compareAndSet(false, true) || !healthy.getAsBoolean())
      throw new IOException("API readiness unavailable");
    ready.release();
    if (closed.get() || !healthy.getAsBoolean()) throw new IOException("API readiness unavailable");
    promoted.set(true);
  }

  boolean ready() {
    return !closed.get() && promoted.get() && healthy.getAsBoolean();
  }

  int port() {
    return server.getAddress().getPort();
  }

  private void respond(HttpExchange exchange) throws IOException {
    try (exchange) {
      String path = exchange.getRequestURI().getRawPath();
      int status;
      String body;
      String contentType = "application/json; charset=utf-8";
      if (!exchange.getRequestMethod().equals("GET")) {
        status = 405;
        body = "{}";
      } else if ("/actuator/health".equals(path) || "/actuator/health/readiness".equals(path)) {
        boolean up = ready();
        status = up ? 200 : 503;
        body = up ? "{\"status\":\"UP\"}" : "{\"status\":\"DOWN\"}";
      } else if (INFORMATION_PATH.equals(path)) {
        status = 200;
        body = information;
      } else if (METRICS_PATH.equals(path)) {
        status = 200;
        contentType = "text/plain; version=0.0.4; charset=utf-8";
        body =
            "# TYPE schubert_nk_api_ready gauge\nschubert_nk_api_ready "
                + (ready() ? "1\n" : "0\n");
      } else {
        status = 404;
        body = "{}";
      }
      byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
      exchange.getResponseHeaders().set("Content-Type", contentType);
      exchange.getResponseHeaders().set("Cache-Control", "no-store");
      exchange.sendResponseHeaders(status, bytes.length);
      exchange.getResponseBody().write(bytes);
    }
  }

  @Override
  public void close() {
    if (closed.compareAndSet(false, true)) {
      promoted.set(false);
      boolean interrupted = Thread.currentThread().isInterrupted();
      try {
        server.stop(0);
      } finally {
        if (interrupted) Thread.currentThread().interrupt();
      }
      executor.shutdownNow();
    }
  }
}
