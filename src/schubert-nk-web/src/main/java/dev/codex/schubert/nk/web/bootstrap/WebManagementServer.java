package dev.codex.schubert.nk.web.bootstrap;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import dev.codex.schubert.nk.bootstrap.ServiceStartupAdmission;
import dev.codex.schubert.nk.web.monitoring.WebMetricContext;
import dev.codex.schubert.nk.web.monitoring.WebMetricHttpHandler;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;

/**
 * Loopback Web management; NK-WEB-002/NK-OPS-001; SYS002004/MON003; UI243253; SS342
 * §5.2/SS343/SS352; PG-D369; NATIVE-READY001..006. A requested stop is not termination. Native
 * assembly retains this owner before calling start().
 */
final class WebManagementServer implements AutoCloseable {
  private static final String INFORMATION_PATH = "/actuator/info";
  private static final String METRICS_PATH = "/actuator/prometheus";
  private static final String STOP_UNCONFIRMED = "Web management stop unconfirmed";
  private static final int JSON_OPENING_DELIMITER_LENGTH = 1;

  @FunctionalInterface
  interface Factory {
    HttpServer create(InetSocketAddress address, int backlog) throws IOException;
  }

  private final HttpServer server;
  private final ThreadPoolExecutor executor;
  private final BooleanSupplier healthy;
  private final String information;
  private final Optional<WebMetricHttpHandler> metricHandler;
  private final AtomicBoolean promoted = new AtomicBoolean();
  private final AtomicBoolean promotionAttempted = new AtomicBoolean();
  private final AtomicBoolean closed = new AtomicBoolean();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final java.util.concurrent.locks.ReentrantLock stopLock =
      new java.util.concurrent.locks.ReentrantLock();
  private boolean serverStopped;
  private boolean startAttempted;
  private volatile boolean started;

  static WebManagementServer open(Map<String, String> information, BooleanSupplier healthy)
      throws IOException {
    return open(information, healthy, 8081);
  }

  // Package-local ephemeral-port component PT; production caller always uses fixed overload.
  static WebManagementServer open(
      Map<String, String> information, BooleanSupplier healthy, int port) throws IOException {
    return open(information, healthy, port, HttpServer::create);
  }

  static WebManagementServer open(
      Map<String, String> information, BooleanSupplier healthy, int port, Factory factory)
      throws IOException {
    // PG-D471/PT-WEB-READY007: fixed secondary exists before acquiring the bound owner.
    var cleanupDiagnostic = new IOException(STOP_UNCONFIRMED);
    var closing = Optional.<IOException>empty();
    var result = bind(information, healthy, port, factory);
    try {
      result.start();
      return result;
    } catch (RuntimeException | Error failure) {
      try {
        closing = result.stopFailure(java.time.Duration.ofSeconds(30));
      } catch (RuntimeException | Error unconfirmed) {
        if (unconfirmed instanceof Error && !(failure instanceof Error)) throw unconfirmed;
        if (unconfirmed != failure) failure.addSuppressed(cleanupDiagnostic);
      }
      closing.ifPresent(failure::addSuppressed);
      throw failure;
    }
  }

  static WebManagementServer bind(Map<String, String> information, BooleanSupplier healthy)
      throws IOException {
    return bind(information, healthy, 8081, HttpServer::create);
  }

  static WebManagementServer bind(
      Map<String, String> information, BooleanSupplier healthy, int port, Factory factory)
      throws IOException {
    Objects.requireNonNull(information, "public information");
    Objects.requireNonNull(healthy, "runtime health");
    Objects.requireNonNull(factory, "management factory");
    String json = publicJson(information);
    return new WebManagementServer(healthy, json, port, factory, Optional.empty());
  }

  // PG-D619/1819: caller retains/initializes context outside this bound server owner.
  static WebManagementServer bind(
      Map<String, String> information, BooleanSupplier healthy, WebMetricContext<?> context)
      throws IOException {
    return bind(information, healthy, 8081, HttpServer::create, context);
  }

  static WebManagementServer bind(
      Map<String, String> information,
      BooleanSupplier healthy,
      int port,
      Factory factory,
      WebMetricContext<?> context)
      throws IOException {
    Objects.requireNonNull(information, "public information");
    Objects.requireNonNull(healthy, "runtime health");
    Objects.requireNonNull(factory, "management factory");
    var borrowed = Optional.of(Objects.requireNonNull(context, "borrowed metric context"));
    String json = publicJson(information);
    return new WebManagementServer(healthy, json, port, factory, borrowed);
  }

  void start() {
    stopLock.lock();
    try {
      if (stopping.get() || startAttempted)
        throw new IllegalStateException("Web management start unavailable");
      startAttempted = true;
      server.setExecutor(executor);
      server.createContext("/", this::respond);
      server.start();
      started = true;
    } finally {
      stopLock.unlock();
    }
  }

  private WebManagementServer(
      BooleanSupplier healthy,
      String information,
      int port,
      Factory factory,
      Optional<WebMetricContext<?>> context)
      throws IOException {
    this.healthy = healthy;
    this.information = information;
    // Resource-free handler is captured before acquisition; context remains caller-owned.
    this.metricHandler = context.map(value -> new WebMetricHttpHandler(value, this::ready));
    var address = new InetSocketAddress("127.0.0.1", port);
    this.executor =
        new ThreadPoolExecutor(
            1,
            1,
            0,
            TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(32),
            task -> {
              var thread = new Thread(task, "web-management");
              thread.setDaemon(true);
              return thread;
            });
    // SSC312/PG-D461/PT-HTTP-OWN002: all locks/flags/executor precede bound server.
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
    if (!started
        || stopping.get()
        || !promotionAttempted.compareAndSet(false, true)
        || !healthy.getAsBoolean()) throw new IOException("Web readiness unavailable");
    ready.release();
    if (stopping.get() || !healthy.getAsBoolean())
      throw new IOException("Web readiness unavailable");
    promoted.set(true);
  }

  boolean ready() {
    return started && !stopping.get() && promoted.get() && healthy.getAsBoolean();
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
            "# TYPE schubert_nk_web_ready gauge\nschubert_nk_web_ready "
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
  public void close() throws IOException {
    closeWithin(java.time.Duration.ofSeconds(30));
  }

  void closeWithin(java.time.Duration remaining) throws IOException {
    var failure = stopFailure(remaining);
    if (failure.isPresent()) throw failure.orElseThrow();
  }

  // PG-D504: internal cleanup consumes a result; the public close boundary keeps checked IO.
  private Optional<IOException> stopFailure(java.time.Duration remaining) {
    Objects.requireNonNull(remaining, "management stop budget");
    if (remaining.isNegative() || remaining.compareTo(java.time.Duration.ofSeconds(30)) > 0)
      throw new IllegalArgumentException("invalid stop budget");
    // SSC335/PG-D509: a zero remainder must not become an unbounded lock wait.
    long deadline = System.nanoTime() + remaining.toNanos();
    stopping.set(true);
    promoted.set(false);
    boolean entryInterrupted = Thread.interrupted();
    try {
      try {
        if (!stopLock.tryLock(Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS))
          return Optional.of(new IOException(STOP_UNCONFIRMED));
      } catch (InterruptedException notification) {
        Thread.currentThread().interrupt();
        return Optional.of(new IOException(STOP_UNCONFIRMED));
      }
      // Web's existing vendor/await contract sees an entry notification, unlike API SSC313.
      if (entryInterrupted) Thread.currentThread().interrupt();
      try {
        if (closed.get()) return Optional.empty();
        if (!serverStopped) {
          boolean interrupted = Thread.currentThread().isInterrupted();
          try {
            server.stop(0);
            // SSC317: normal stop return does not prove unstarted selector/socket release.
            if (started) serverStopped = true;
          } finally {
            if (interrupted) Thread.currentThread().interrupt();
          }
        }
        executor.shutdownNow();
        try {
          if (!executor.awaitTermination(
              Math.max(0, deadline - System.nanoTime()), TimeUnit.NANOSECONDS))
            return Optional.of(new IOException(STOP_UNCONFIRMED));
        } catch (InterruptedException interrupted) {
          Thread.currentThread().interrupt();
          return Optional.of(new IOException(STOP_UNCONFIRMED));
        }
        if (!started) return Optional.of(new IOException(STOP_UNCONFIRMED));
        closed.set(true);
        return Optional.empty();
      } finally {
        stopLock.unlock();
      }
    } finally {
      if (entryInterrupted) Thread.currentThread().interrupt();
    }
  }
}
