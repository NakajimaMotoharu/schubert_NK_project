package dev.codex.schubert.nk.web.monitoring;

import dev.codex.schubert.nk.web.bootstrap.WebStartupException;
import dev.codex.schubert.nk.web.logging.WebRequestTrace;
import jakarta.servlet.ServletException;
import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import org.apache.catalina.AccessLog;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.jspecify.annotations.Nullable;

/**
 * Borrowed terminal metric observer, after the existing request trace valve; no HTTP/registry
 * owner. NK-OPS-001/P018-09; RD171/UI252/SS312351; PG-D528/HTTPTERM001..008/spec1577.
 */
public final class HttpMetricValve extends ValveBase implements AccessLog {
  private static final String ATTRIBUTE = HttpMetricValve.class.getName();
  private final HttpMetricRecorder recorder;
  private final Runnable onTerminal;

  public HttpMetricValve(HttpMetricRecorder recorder, Runnable onTerminal) {
    super(true);
    this.recorder = Objects.requireNonNull(recorder, "metric recorder");
    this.onTerminal = Objects.requireNonNull(onTerminal, "metric terminal signal");
  }

  /**
   * Request-owned state survives ASYNC/ERROR redispatch, and container recycle owns its removal.
   */
  @Override
  public void invoke(Request request, Response response) throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Object retained = request.getAttribute(ATTRIBUTE);
    if (retained == null) request.setAttribute(ATTRIBUTE, new Completion());
    else if (!(retained instanceof Completion))
      throw new IllegalStateException("HTTP metric observation is unavailable");
    Objects.requireNonNull(getNext(), "next valve").invoke(request, response);
  }

  /** Native terminal nanoseconds, not Servlet-finally or an inferred successful response. */
  @Override
  public void log(@Nullable Request request, @Nullable Response response, long elapsedNanos) {
    if (request == null || response == null) {
      onTerminal.run();
      return;
    }
    final String route;
    final String method;
    final int status;
    try {
      Object retained = request.getAttribute(ATTRIBUTE);
      if (!(retained instanceof Completion completion)) {
        throw new IllegalArgumentException("HTTP metric observation is unavailable");
      }
      if (!completion.claim()) return;
      var trace = WebRequestTrace.existing(request);
      @Nullable String observedMethod = request.getMethod();
      status = response.getStatus();
      if (trace.isEmpty()
          || observedMethod == null
          || status < 100
          || status > 599
          || elapsedNanos < 0) {
        throw new IllegalArgumentException("HTTP metric metadata is unavailable");
      }
      route = trace.orElseThrow().route();
      method = observedMethod;
    } catch (IllegalArgumentException | IllegalStateException malformed) {
      if (!signalFailure(malformed))
        throw new IllegalStateException("HTTP metric terminal signal failed");
      return;
    }
    try {
      recorder.record(route, method, status, elapsedNanos);
    } catch (RuntimeException | Error failure) {
      signalFailure(failure);
      throw failure;
    }
  }

  /** Never format a provider graph; preserve the original fatal even if the owner signal fails. */
  private boolean signalFailure(Throwable failure) {
    try {
      onTerminal.run();
    } catch (RuntimeException | Error signalFailure) {
      WebStartupException.attachSecondary(failure, signalFailure);
      WebStartupException.preserveFatal(failure);
      return false;
    }
    WebStartupException.preserveFatal(failure);
    return true;
  }

  @Override
  public boolean getRequestAttributesEnabled() {
    return false;
  }

  @Override
  public void setRequestAttributesEnabled(boolean enabled) {
    if (enabled)
      throw new IllegalArgumentException("HTTP metric attribute overrides are forbidden");
  }

  private static final class Completion {
    private final AtomicBoolean claimed = new AtomicBoolean();

    boolean claim() {
      return claimed.compareAndSet(false, true);
    }
  }
}
