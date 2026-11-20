package dev.codex.schubert.nk.api.monitoring;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.function.BooleanSupplier;
import org.jspecify.annotations.Nullable;

/**
 * NK-OPS-001/RD171/UI252/SS342351/1817/PG-D618: borrowed metric HTTP boundary. No socket,
 * lifecycle, health authority or implicit context initialization.
 */
public final class ApiMetricHttpHandler implements HttpHandler {
  private static final String PATH = "/actuator/prometheus";
  private static final String METRIC_TYPE = "text/plain; version=0.0.4; charset=utf-8";
  private static final String JSON_TYPE = "application/json; charset=utf-8";
  private final ApiMetricContext<?> context;
  private final BooleanSupplier ready;

  public ApiMetricHttpHandler(ApiMetricContext<?> context, BooleanSupplier ready) {
    this.context = Objects.requireNonNull(context, "metric context");
    this.ready = Objects.requireNonNull(ready, "runtime readiness");
  }

  /**
   * Caller registers this handler on its already owned loopback server; exchange is closed here.
   */
  @Override
  public void handle(HttpExchange exchange) throws IOException {
    Objects.requireNonNull(exchange, "metric exchange");
    @Nullable Throwable primary = null;
    try {
      write(exchange);
    } catch (Throwable failure) {
      primary = failure;
      throw failure;
    } finally {
      closeOwnedExchange(exchange, primary);
    }
  }

  private static void closeOwnedExchange(HttpExchange exchange, @Nullable Throwable primary) {
    // The accepted exchange is owned here. Keep JDK primary and self-suppression semantics.
    try {
      exchange.close();
    } catch (Throwable cleanup) {
      if (primary == null) throw cleanup;
      primary.addSuppressed(cleanup);
    }
  }

  /** Borrowed exchange: caller closes it after both successful and failed writes. */
  public void write(HttpExchange exchange) throws IOException {
    Objects.requireNonNull(exchange, "metric exchange");
    int status;
    String body;
    String type = JSON_TYPE;
    if (!"GET".equals(exchange.getRequestMethod())) {
      status = 405;
      body = "{}";
    } else if (!PATH.equals(exchange.getRequestURI().getRawPath())) {
      status = 404;
      body = "{}";
    } else {
      // Complete both views first: a source failure must never publish a partial success body.
      body = context.render(ready.getAsBoolean());
      status = 200;
      type = METRIC_TYPE;
    }
    byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
    exchange.getResponseHeaders().set("Content-Type", type);
    exchange.getResponseHeaders().set("Cache-Control", "no-store");
    exchange.sendResponseHeaders(status, bytes.length);
    exchange.getResponseBody().write(bytes);
  }
}
