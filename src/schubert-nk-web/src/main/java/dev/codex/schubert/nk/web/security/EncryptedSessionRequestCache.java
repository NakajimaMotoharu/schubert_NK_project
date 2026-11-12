package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.SpringEncryptedSessionRepository;
import dev.codex.schubert.nk.web.session.SpringWebSession;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.util.Collection;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.jspecify.annotations.Nullable;
import org.springframework.security.web.savedrequest.RequestCache;
import org.springframework.security.web.savedrequest.SavedRequest;
import org.springframework.session.web.http.SessionRepositoryFilter;

/**
 * Stores only a validated relative screen GET String in the encrypted session. NK-WEB-001;
 * FUN-001/AUT-001..004; UI221/226; SS313 §4/9,314 §3/7.2,352; PG-D-104/PT-WEB-076..081. No
 * cookie/header/body replay, arbitrary Security object serialization, or authorization grant.
 */
public final class EncryptedSessionRequestCache implements RequestCache {
  private static final String AJAX_REQUEST_VALUE = "XMLHttpRequest";

  private final SpringEncryptedSessionRepository sessions;

  public EncryptedSessionRequestCache(SpringEncryptedSessionRepository sessions) {
    this.sessions = Objects.requireNonNull(sessions, "sessions");
  }

  @Override
  public void saveRequest(HttpServletRequest request, HttpServletResponse response) {
    requireConfigured(request, response);
    var target = candidate(request);
    if (target.isEmpty()) return;
    try {
      request
          .getSession()
          .setAttribute(SpringWebSession.SAVED_REQUEST, target.orElseThrow().location());
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  @Override
  public @Nullable SavedRequest getRequest(
      HttpServletRequest request, HttpServletResponse response) {
    requireConfigured(request, response);
    try {
      var session = request.getSession(false);
      if (session == null) return null;
      Object value = session.getAttribute(SpringWebSession.SAVED_REQUEST);
      if (value == null) return null;
      if (!(value instanceof String location)) throw new SessionStoreException();
      return new SavedGet(SavedScreenTarget.fromGet("GET", location).location());
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  @Override
  public @Nullable HttpServletRequest getMatchingRequest(
      HttpServletRequest request, HttpServletResponse response) {
    var saved = getRequest(request, response);
    if (saved == null) return null;
    var target = candidate(request);
    if (target.isEmpty() || !saved.getRedirectUrl().equals(target.orElseThrow().location()))
      return null;
    removeRequest(request, response);
    // Browser already reissued exactly this GET URL. Do not restore headers/parameters/body.
    return request;
  }

  @Override
  public void removeRequest(HttpServletRequest request, HttpServletResponse response) {
    requireConfigured(request, response);
    try {
      var session = request.getSession(false);
      if (session != null) session.removeAttribute(SpringWebSession.SAVED_REQUEST);
    } catch (IllegalArgumentException | IllegalStateException failure) {
      SessionStoreException.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }

  private void requireConfigured(HttpServletRequest request, HttpServletResponse response) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    if (request.getAttribute(SessionRepositoryFilter.SESSION_REPOSITORY_ATTR) != sessions)
      throw new SessionStoreException();
  }

  private static Optional<SavedScreenTarget> candidate(HttpServletRequest request) {
    if (AJAX_REQUEST_VALUE.equalsIgnoreCase(request.getHeader("X-Requested-With")))
      return Optional.empty();
    String query = request.getQueryString();
    String location = request.getRequestURI() + (query == null ? "" : "?" + query);
    try {
      return Optional.of(SavedScreenTarget.fromGet(request.getMethod(), location));
    } catch (IllegalArgumentException invalid) {
      return Optional.empty();
    }
  }

  /** Ephemeral API projection only; never put this Serializable framework type into the session. */
  private static final class SavedGet implements SavedRequest {
    private static final long serialVersionUID = 1L;
    private final String location;

    private SavedGet(String location) {
      this.location = location;
    }

    @Override
    public String getRedirectUrl() {
      return location;
    }

    @Override
    public String getMethod() {
      return "GET";
    }

    @Override
    public List<Cookie> getCookies() {
      return List.of();
    }

    @Override
    public List<String> getHeaderValues(String name) {
      Objects.requireNonNull(name, "name");
      return List.of();
    }

    @Override
    public Collection<String> getHeaderNames() {
      return List.of();
    }

    @Override
    public List<Locale> getLocales() {
      return List.of();
    }

    @Override
    public String @Nullable [] getParameterValues(String name) {
      Objects.requireNonNull(name, "name");
      // BUG-064/PT078: Spring's absent-value contract is map.get(name), not an empty array.
      return getParameterMap().get(name);
    }

    @Override
    public Map<String, String[]> getParameterMap() {
      return Map.of();
    }

    @Override
    public String toString() {
      return "SavedGet[REDACTED]";
    }
  }
}
