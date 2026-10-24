package dev.codex.schubert.nk.api.bootstrap;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import dev.codex.schubert.nk.api.monitoring.ApiMetricContext;
import dev.codex.schubert.nk.api.monitoring.ApiMetricHttpHandler;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.BooleanSupplier;

/** Fixed loopback management only. SS342 §5.2/SSC158/PG-D334/PT-OPS-API-READY001..008. */
final class ApiManagementServer implements AutoCloseable {
  private static final String INFORMATION_PATH = "/actuator/info";
  private static final String METRICS_PATH = "/actuator/prometheus";
  private static final int JSON_OPENING_DELIMITER_LENGTH = 1;
  private static final Duration CLOSE_TIMEOUT = Duration.ofSeconds(30);
  private static final String STOP_UNCONFIRMED = "API management stop unconfirmed";

  @FunctionalInterface
  interface Factory {
    HttpServer create(InetSocketAddress address, int backlog) throws IOException;
  }

  private final HttpServer server;
  private final ThreadPoolExecutor executor;
  private final BooleanSupplier healthy;
  private final String information;
  private final Optional<ApiMetricHttpHandler> metricHandler;
  private final AtomicBoolean promoted = new AtomicBoolean();
  private final AtomicBoolean promotionAttempted = new AtomicBoolean();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final AtomicBoolean started = new AtomicBoolean();
  private final ReentrantLock stopLock = new ReentrantLock();
  private boolean closed;
  private boolean serverStopped;
  private boolean startAttempted;

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
    var cleanupDiagnostic = new IllegalStateException(STOP_UNCONFIRMED);
    var closing = Optional.<IllegalStateException>empty();
    var result = bind(information, healthy, port, factory);
    try {
      result.start();
      return result;
    } catch (RuntimeException | Error failure) {
      try {
        closing = result.stopFailure(CLOSE_TIMEOUT);
      } catch (RuntimeException | Error unconfirmed) {
        if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;
        if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);
      }
      closing.ifPresent(ignored -> failure.addSuppressed(cleanupDiagnostic));
      throw failure;
    }
  }

  // SSC316: native caller registers the bound owner before any fallible start operation.
  static ApiManagementServer bind(Map<String, String> information, BooleanSupplier healthy)
      throws IOException {
    return bind(information, healthy, 8091, HttpServer::create);
  }

  static ApiManagementServer bind(
      Map<String, String> information, BooleanSupplier healthy, int port, Factory factory)
      throws IOException {
    Objects.requireNonNull(information, "public information");
    Objects.requireNonNull(healthy, "runtime health");
    Objects.requireNonNull(factory, "management factory");
    String json = publicJson(information);
    return new ApiManagementServer(healthy, json, port, factory, Optional.empty());
  }

  // PG-D619/1819: caller retains/initializes context outside this bound server owner.
  static ApiManagementServer bind(
      Map<String, String> information, BooleanSupplier healthy, ApiMetricContext<?> context)
      throws IOException {
    return bind(information, healthy, 8091, HttpServer::create, context);
  }

  static ApiManagementServer bind(
      Map<String, String> information,
      BooleanSupplier healthy,
      int port,
      Factory factory,
      ApiMetricContext<?> context)
      throws IOException {
    Objects.requireNonNull(information, "public information");
    Objects.requireNonNull(healthy, "runtime health");
    Objects.requireNonNull(factory, "management factory");
    var borrowed = Optional.of(Objects.requireNonNull(context, "borrowed metric context"));
    String json = publicJson(information);
    return new ApiManagementServer(healthy, json, port, factory, borrowed);
  }

  void start() {
    stopLock.lock();
    try {
      if (stopping.get() || startAttempted)
        throw new IllegalStateException("API management start unavailable");
      startAttempted = true;
      server.setExecutor(executor);
      server.createContext("/", this::respond);
      server.start();
      started.set(true);
    } finally {
      stopLock.unlock();
    }
  }

  private ApiManagementServer(
      BooleanSupplier healthy,
      String information,
      int port,
      Factory factory,
      Optional<ApiMetricContext<?>> context)
      throws IOException {
    this.healthy = healthy;
    this.information = information;
    // Resource-free handler is captured before acquisition; context remains caller-owned.
    this.metricHandler = context.map(value -> new ApiMetricHttpHandler(value, this::ready));
    var address = new InetSocketAddress("127.0.0.1", port);
    this.executor =
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
    // SSC312/PG-D461/PT-HTTP-OWN001: no owner/state allocation after server acquisition.
    this.server = Objects.requireNonNull(factory.create(address, 32), "management server");
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
    if (!started.get()
        || stopping.get()
        || !promotionAttempted.compareAndSet(false, true)
        || !healthy.getAsBoolean()) throw new IOException("API readiness unavailable");
    ready.release();
    if (stopping.get() || !healthy.getAsBoolean())
      throw new IOException("API readiness unavailable");
    promoted.set(true);
  }

  boolean ready() {
    return started.get() && !stopping.get() && promoted.get() && healthy.getAsBoolean();
  }

  int port() {
    return server.getAddress().getPort();
  }

  private void respond(HttpExchange exchange) throws IOException {
    try (exchange) {
      String path = exchange.getRequestURI().getRawPath();
      if (metricHandler.isPresent() && METRICS_PATH.equals(path)) {
        metricHandler.orElseThrow().write(exchange);
        return;
      }
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
    closeWithin(CLOSE_TIMEOUT);
  }

  /** SSC313/PG-D462/PT-API-STOP001..004: requested stop is not confirmed termination. */
  void closeWithin(Duration remaining) {
    var failure = stopFailure(remaining);
    if (failure.isPresent()) throw failure.orElseThrow();
  }

  // PG-D506: ordinary close throws at its boundary; startup consumes the same fixed result.
  private Optional<IllegalStateException> stopFailure(Duration remaining) {
    Objects.requireNonNull(remaining, "API management stop budget");
    if (remaining.isNegative() || remaining.compareTo(CLOSE_TIMEOUT) > 0)
      throw new IllegalArgumentException("invalid API stop budget");
    long deadline = System.nanoTime() + remaining.toNanos();
    stopping.set(true);
    promoted.set(false);
    // READY005: preserve a notification already present on entry while checking actual join.
    boolean interrupted = Thread.interrupted();
    try {
      try {
        if (!stopLock.tryLock(Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS))
          return Optional.of(new IllegalStateException(STOP_UNCONFIRMED));
      } catch (InterruptedException notification) {
        Thread.currentThread().interrupt();
        return Optional.of(new IllegalStateException(STOP_UNCONFIRMED));
      }
      try {
        if (closed) return Optional.empty();
        if (!serverStopped) {
          server.stop(0);
          // SSC317: unstarted JDK stop can return with a bound selector/socket retained.
          if (started.get()) serverStopped = true;
        }
        executor.shutdownNow();
        try {
          if (!executor.awaitTermination(
              Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS))
            return Optional.of(new IllegalStateException(STOP_UNCONFIRMED));
        } catch (InterruptedException notification) {
          Thread.currentThread().interrupt();
          return Optional.of(new IllegalStateException(STOP_UNCONFIRMED));
        }
        if (!started.get()) return Optional.of(new IllegalStateException(STOP_UNCONFIRMED));
        closed = true;
        return Optional.empty();
      } finally {
        stopLock.unlock();
      }
    } finally {
      if (interrupted) Thread.currentThread().interrupt();
    }
  }
}
