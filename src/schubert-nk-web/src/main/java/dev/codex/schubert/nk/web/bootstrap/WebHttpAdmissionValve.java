package dev.codex.schubert.nk.web.bootstrap;

import jakarta.servlet.ServletException;
import java.io.IOException;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;
import org.apache.catalina.AccessLog;
import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.Response;
import org.apache.catalina.valves.ValveBase;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Installed after REQUEST logging in the access-log list: DB projection finishes before the
 * terminal lease release. Not Servlet-finally or an ASYNC dispatch counter. SS313342352;
 * PG-D369/NATIVE-STOP001..008; NK-WEB-002/SYS004/AUT002/MON003/UI243253.
 */
@NullMarked
final class WebHttpAdmissionValve extends ValveBase implements AccessLog {
  private static final String ATTRIBUTE = WebHttpAdmissionValve.class.getName() + ".lease";
  private final WebHttpAdmission admission;

  private final class Lease {
    private final AtomicBoolean finished = new AtomicBoolean();

    boolean ownedBy(WebHttpAdmission candidate) {
      return admission == candidate;
    }

    void complete() {
      if (finished.compareAndSet(false, true)) admission.completed();
    }
  }

  WebHttpAdmissionValve(WebHttpAdmission admission) {
    super(true);
    this.admission = Objects.requireNonNull(admission, "HTTP admission");
  }

  @Override
  public void invoke(Request request, Response response) throws IOException, ServletException {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Object lease = request.getAttribute(ATTRIBUTE);
    if (lease == null) {
      if (!admission.acquire()) {
        response.setStatus(503);
        response.setHeader("Cache-Control", "no-store");
        return;
      }
      request.setAttribute(ATTRIBUTE, new Lease());
    } else if (!(lease instanceof WebHttpAdmissionValve.Lease owned) || !owned.ownedBy(admission)) {
      throw new ServletException("Web HTTP lease unavailable");
    }
    Objects.requireNonNull(getNext(), "next valve").invoke(request, response);
  }

  @Override
  public void log(@Nullable Request request, @Nullable Response response, long elapsedNanos) {
    // Missing terminal metadata must never manufacture confirmation of an outstanding lease.
    if (request == null || response == null) return;
    Object lease = request.getAttribute(ATTRIBUTE);
    if (lease instanceof WebHttpAdmissionValve.Lease owned && owned.ownedBy(admission))
      owned.complete();
  }

  @Override
  public boolean getRequestAttributesEnabled() {
    return false;
  }

  @Override
  public void setRequestAttributesEnabled(boolean enabled) {
    if (enabled) throw new IllegalArgumentException("HTTP admission overrides are forbidden");
  }
}
