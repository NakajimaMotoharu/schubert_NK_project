package dev.codex.schubert.nk.web.logging;

import dev.codex.schubert.nk.web.security.WebRequestContext;
import jakarta.servlet.ServletException;
import java.io.IOException;
import java.util.Objects;
import java.util.Optional;
import org.apache.catalina.AccessLog;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/** Tomcat terminal callback, not Servlet finally; SS312351/SSC172/PG-D354/REQ001..016. */
@NullMarked
public final class HttpRequestLoggingValve extends ValveBase implements AccessLog {
  private final WebRequestLogProducer producer;

  public HttpRequestLoggingValve(WebRequestLogProducer producer) {
    super(true);
    this.producer = Objects.requireNonNull(producer, "producer");
  }

  @Override
  public void invoke(Request request, Response response) throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    var trace = WebRequestTrace.ensure(request, producer.identifiers());
    // The registered authentication filter consumes this POST before MVC mapping.
    if ("POST".equals(request.getMethod()) && "/login".equals(request.getRequestURI()))
      trace.captureRoute("/login");
    var scope = trace.enter();
    try {
      Objects.requireNonNull(getNext(), "next valve").invoke(request, response);
    } finally {
      scope.close();
    }
  }

  /** Tomcat 11 supplies ns; Coyote counts origin content bytes, not chunk framing/Servlet chars. */
  @Override
  public void log(@Nullable Request request, @Nullable Response response, long elapsedNanos) {
    if (request == null || response == null) {
      producer.metadataInvalid();
      return;
    }
    final Optional<WebRequestTrace> observed;
    final @Nullable String method;
    try {
      observed = WebRequestTrace.existing(request);
      method = request.getMethod();
    } catch (IllegalArgumentException | IllegalStateException metadataFailure) {
      producer.metadataInvalid();
      return;
    }
    if (observed.isEmpty() || method == null) {
      producer.metadataInvalid();
      return;
    }
    var trace = observed.orElseThrow();
    if (!trace.claimCompletion()) return;
    final Optional<String> address;
    final int status;
    final long bytes;
    try {
      address = WebRequestContext.existing(request).map(c -> c.clientAddress().value());
      status = response.getStatus();
      bytes = response.getCoyoteResponse().getContentWritten();
    } catch (IllegalArgumentException | IllegalStateException metadataFailure) {
      producer.metadataInvalid();
      return;
    }
    // Owner/projection faults are not a malformed-request retry or a second terminal signal.
    producer.complete(trace, status, elapsedNanos, bytes, method, address);
  }

  @Override
  public boolean getRequestAttributesEnabled() {
    return false;
  }

  /** No remote address/header override attributes may replace the verified transport contract. */
  @Override
  public void setRequestAttributesEnabled(boolean enabled) {
    if (enabled)
      throw new IllegalArgumentException("request audit address overrides are forbidden");
  }
}
