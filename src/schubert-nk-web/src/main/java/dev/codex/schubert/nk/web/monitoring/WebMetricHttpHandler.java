package dev.codex.schubert.nk.web.monitoring;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import java.util.function.BooleanSupplier;

/**
 * NK-OPS-001/RD171/UI252/SS342351/1817/PG-D618: borrowed metric HTTP boundary. No socket,
 * lifecycle, health authority or implicit context initialization.
 */
public final class WebMetricHttpHandler implements HttpHandler {
  private static final String PATH = "/actuator/prometheus";
  private static final String METRIC_TYPE = "text/plain; version=0.0.4; charset=utf-8";
  private static final String JSON_TYPE = "application/json; charset=utf-8";
  private final WebMetricContext<?> context;
  private final BooleanSupplier ready;

  public WebMetricHttpHandler(WebMetricContext<?> context, BooleanSupplier ready) {
    this.context = Objects.requireNonNull(context, "metric context");
    this.ready = Objects.requireNonNull(ready, "runtime readiness");
  }

  /**
   * Caller registers this handler on its already owned loopback server; exchange is closed here.
   */
  @Override
  public void handle(HttpExchange exchange) throws IOException {
    Objects.requireNonNull(exchange, "metric exchange");
    try (exchange) {
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
}
