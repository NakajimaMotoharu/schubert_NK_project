package dev.codex.schubert.nk.web.security;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Objects;
import org.springframework.security.web.header.HeaderWriter;

/**
 * Fixed browser policy; no request or exception values enter headers. NK-WEB-001;
 * SYS-006/FUN-001/AUT-004; UI222/226; SS313/342/352 §7.2; PG-D-106/PT-WEB-091..094. Invoke before
 * response commit through WebSecurityHeaderFilterFactory.
 */
public final class WebSecurityHeaderWriter implements HeaderWriter {
  @Override
  public void writeHeaders(HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    response.setHeader(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'");
    response.setHeader("Strict-Transport-Security", "max-age=31536000");
    response.setHeader("X-Content-Type-Options", "nosniff");
    response.setHeader("X-Frame-Options", "DENY");
    response.setHeader("Referrer-Policy", "same-origin");
    response.setHeader(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()");
    response.setHeader("Cache-Control", "no-store");
  }
}
