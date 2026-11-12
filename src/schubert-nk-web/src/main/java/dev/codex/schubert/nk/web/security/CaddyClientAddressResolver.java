package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import jakarta.servlet.http.HttpServletRequest;
import java.net.InetAddress;
import java.util.NoSuchElementException;
import java.util.Objects;

/**
 * Resolve before any forwarded wrapper rewrites the transport peer. IP trust only, not Host/origin
 * authorization. NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §3/5,342 §3,352;
 * PG-D-105/PT-WEB-082..089. No DNS lookup or native session access.
 */
public final class CaddyClientAddressResolver {
  public LoginClientAddress resolve(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    try {
      String rawPeer = request.getRemoteAddr();
      if (rawPeer == null) throw new CaddyRequestRejectedException();
      var peer = new LoginClientAddress(rawPeer);
      if (!InetAddress.ofLiteral(peer.value()).isLoopbackAddress())
        throw new CaddyRequestRejectedException();
      var forwarded = request.getHeaders("Forwarded");
      if (forwarded == null || forwarded.hasMoreElements())
        throw new CaddyRequestRejectedException();
      if (!single(request, "X-Forwarded-Proto").equals("https"))
        throw new CaddyRequestRejectedException();
      return new LoginClientAddress(single(request, "X-Forwarded-For"));
    } catch (IllegalArgumentException | IllegalStateException | NoSuchElementException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new CaddyRequestRejectedException();
    }
  }

  private static String single(HttpServletRequest request, String name) {
    var values = request.getHeaders(name);
    if (values == null || !values.hasMoreElements()) throw new CaddyRequestRejectedException();
    String value = values.nextElement();
    if (value == null || values.hasMoreElements()) throw new CaddyRequestRejectedException();
    return value;
  }
}
