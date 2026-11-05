package dev.codex.schubert.nk.web.logging;

import dev.codex.schubert.nk.web.security.WebRequestContext;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import dev.codex.schubert.nk.web.view.TopBarViewModel;
import jakarta.servlet.http.HttpServletRequest;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/** Request-only safe audit metadata; MON/AUT/UI235252/SS312351/SSC172/PG-D354/REQ001..016. */
@NullMarked
public final class WebRequestTrace {
  private static final String ATTRIBUTE = WebRequestTrace.class.getName();
  private static final String UNKNOWN_ROUTE = "/**";
  private static final ThreadLocal<Scope> CURRENT = new ThreadLocal<>();
  private static final Set<String> ROUTES =
      Set.of(
          "/",
          "/login",
          "/logout",
          "/search",
          "/logs",
          "/error",
          "/scenarios",
          "/scenarios/{id:[0-9]{1,12}}",
          "/scenarios/{game:NUKITASHI[12]}",
          "/scenarios/{game:NUKITASHI[12]}/{prefix:[0-9]{2}}",
          "/animation",
          "/animation/main",
          "/animation/ova",
          "/animation/opening",
          "/animation/videos/{id}",
          "/animation/media/{id}",
          "/music",
          "/music/{category}",
          "/music/{category}/{section}",
          "/music/media/{id}",
          "/music/download/{id}",
          "/audio/{id}",
          "/audio/{id}/download",
          "/admin/users",
          "/admin/users/new",
          "/admin/users/{id:[0-9]{1,12}}",
          "/questions",
          "/questions/new",
          "/questions/accepted/{receiptId}",
          "/questions/{id:[0-9]{1,12}}",
          "/notifications",
          "/notifications/{id:[0-9]{1,12}}",
          "/css/**",
          "/js/**");
  private final UUID retainedRequestId;
  private final UUID retainedEventId;
  private final AtomicReference<Optional<UUID>> messageId = new AtomicReference<>(Optional.empty());
  private final AtomicReference<String> retainedRoute = new AtomicReference<>(UNKNOWN_ROUTE);
  private volatile Optional<TopBarViewModel> retainedActor = Optional.empty();
  private final AtomicBoolean completed = new AtomicBoolean();
  private final AtomicBoolean retainedMenuViewCandidate = new AtomicBoolean();

  private WebRequestTrace(UUID requestId, UUID eventId) {
    this.retainedRequestId = requestId;
    this.retainedEventId = eventId;
  }

  public static WebRequestTrace ensure(HttpServletRequest request, Supplier<UUID> identifiers) {
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(identifiers, "identifiers");
    UUID requestId = WebRequestContext.identify(request, identifiers);
    var old = existing(request);
    if (old.isPresent()) {
      if (!old.orElseThrow().retainedRequestId.equals(requestId))
        throw new IllegalStateException("request audit identity mismatch");
      return old.orElseThrow();
    }
    var trace =
        new WebRequestTrace(requestId, Objects.requireNonNull(identifiers.get(), "eventId"));
    try {
      request.setAttribute(ATTRIBUTE, trace);
    } catch (IllegalArgumentException | IllegalStateException attributeFailure) {
      throw new IllegalStateException("request audit metadata is unavailable");
    }
    return trace;
  }

  public static Optional<WebRequestTrace> existing(HttpServletRequest request) {
    Objects.requireNonNull(request, "request");
    Object value;
    try {
      value = request.getAttribute(ATTRIBUTE);
    } catch (IllegalArgumentException | IllegalStateException attributeFailure) {
      throw new IllegalStateException("request audit metadata is unavailable");
    }
    if (value == null) return Optional.empty();
    if (value instanceof WebRequestTrace trace) return Optional.of(trace);
    throw new IllegalStateException("request audit metadata is unavailable");
  }

  /** Only a previously authenticated closed principal is projected; never retained. */
  public static void captureActor(HttpServletRequest request, Optional<SessionPrincipal> actor) {
    Objects.requireNonNull(actor, "actor");
    existing(request).ifPresent(trace -> trace.retainedActor = actor.map(TopBarViewModel::from));
  }

  /** Called by actual MVC mapping, never a raw URI/header or arbitrary pattern formatter. */
  public void captureRoute(String pattern) {
    Objects.requireNonNull(pattern, "pattern");
    if (ROUTES.contains(pattern)) retainedRoute.compareAndSet(UNKNOWN_ROUTE, pattern);
  }

  /** Business-only supplier: event/request UUID generators must not use this wrapper. */
  public static Supplier<UUID> businessIdentifiers(Supplier<UUID> identifiers) {
    Objects.requireNonNull(identifiers, "identifiers");
    return () -> {
      UUID id = Objects.requireNonNull(identifiers.get(), "messageId");
      Scope scope = CURRENT.get();
      if (scope != null) {
        WebRequestTrace trace = scope.trace;
        var old = Objects.requireNonNull(trace.messageId.get(), "messageId slot");
        if (old.isEmpty()) trace.messageId.compareAndSet(old, Optional.of(id));
      }
      return id;
    };
  }

  /** Controller marks successful model construction; terminal status still decides success. */
  public static void markMenuViewed() {
    Scope scope = CURRENT.get();
    if (scope != null) scope.trace.retainedMenuViewCandidate.set(true);
    // Missing trace is already reported by the terminal hook; logging must not change HTTP.
  }

  public boolean menuViewCandidate() {
    return retainedMenuViewCandidate.get();
  }

  public UUID requestId() {
    return retainedRequestId;
  }

  public UUID eventId() {
    return retainedEventId;
  }

  public UUID correlationId() {
    return correlationIdFor(retainedEventId);
  }

  /** No business MQ means each projection event correlates to its own event Message ID. */
  public UUID correlationIdFor(UUID eventId) {
    Objects.requireNonNull(eventId, "eventId");
    return messageId.get().orElse(eventId);
  }

  public String route() {
    return retainedRoute.get();
  }

  public Optional<TopBarViewModel> actor() {
    return retainedActor;
  }

  /** One terminal REQUEST observation even if container dispatch completion is repeated. */
  boolean claimCompletion() {
    return completed.compareAndSet(false, true);
  }

  /** Lexical thread ownership, reentered for each dispatch; no inheritance to worker threads. */
  public Scope enter() {
    return new Scope(this);
  }

  @Override
  public String toString() {
    return "WebRequestTrace[REDACTED]";
  }

  public static final class Scope implements AutoCloseable {
    private final Thread owner;
    private final @Nullable Scope previous;
    private final WebRequestTrace trace;
    private boolean closed;

    private Scope(WebRequestTrace trace) {
      owner = Thread.currentThread();
      this.trace = trace;
      previous = CURRENT.get();
      CURRENT.set(this);
    }

    @Override
    public void close() {
      if (owner != Thread.currentThread())
        throw new IllegalStateException("request audit scope owner mismatch");
      if (closed) return;
      if (CURRENT.get() != this)
        throw new IllegalStateException("request audit scope order mismatch");
      closed = true;
      if (previous == null) CURRENT.remove();
      else CURRENT.set(previous);
    }
  }
}
