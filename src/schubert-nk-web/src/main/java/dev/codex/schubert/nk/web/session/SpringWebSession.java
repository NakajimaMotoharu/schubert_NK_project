package dev.codex.schubert.nk.web.session;

import dev.codex.schubert.nk.web.security.SavedRequestTarget;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.springframework.session.Session;

/**
 * Request-scoped closed attributes with immediate short database transactions. NK-WEB-001;
 * FUN-001/AUT-001..004; UI226; SS314 §7.2.5/331/352; SSC-042/PG-D-099/PT-WEB-044..049. Never bind a
 * principal from HTTP parameters.
 */
public final class SpringWebSession implements Session {
  public static final String PRINCIPAL = "principal";
  public static final String CSRF = "csrfToken";
  public static final String SAVED_REQUEST = "savedRequest";
  public static final String OPERATION_TOKENS = "operationTokens";
  private final java.util.concurrent.locks.ReentrantLock lock =
      new java.util.concurrent.locks.ReentrantLock();
  private final SpringEncryptedSessionRepository owner;
  private final EncryptedWebSessionRepository lifecycle;
  private final Clock clock;
  private WebSessionSnapshot snapshot;

  SpringWebSession(
      SpringEncryptedSessionRepository owner,
      EncryptedWebSessionRepository lifecycle,
      Clock clock,
      WebSessionSnapshot snapshot) {
    this.owner = Objects.requireNonNull(owner, "owner");
    this.lifecycle = Objects.requireNonNull(lifecycle, "lifecycle");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.snapshot = Objects.requireNonNull(snapshot, "snapshot");
  }

  @Override
  public String getId() {
    lock.lock();
    try {
      return snapshot.sessionId().cookieValue();
    } finally {
      lock.unlock();
    }
  }

  @Override
  public String changeSessionId() {
    lock.lock();
    try {
      snapshot = lifecycle.rotate(snapshot.sessionId()).orElseThrow(SessionStoreException::new);
      return snapshot.sessionId().cookieValue();
    } finally {
      lock.unlock();
    }
  }

  // SSC-042/PT-WEB-045: Session's generic contract requires this one cast; values come only
  // from the closed immutable projection. Owner: NK-WEB-001; recheck on Spring API upgrades.
  @SuppressWarnings("unchecked")
  @Override
  public <T> @Nullable T getAttribute(String name) {
    Objects.requireNonNull(name, "name");
    lock.lock();
    try {
      var attributes = snapshot.attributes();
      return (T)
          switch (name) {
            case PRINCIPAL -> attributes.principal().orElse(null);
            case CSRF -> attributes.csrfToken().orElse(null);
            case SAVED_REQUEST ->
                attributes.savedRequest().map(SavedRequestTarget::location).orElse(null);
            case OPERATION_TOKENS -> attributes.operationTokens();
            default -> null;
          };
    } finally {
      lock.unlock();
    }
  }

  @Override
  public Set<String> getAttributeNames() {
    lock.lock();
    try {
      var names = new LinkedHashSet<String>();
      var attributes = snapshot.attributes();
      if (attributes.principal().isPresent()) names.add(PRINCIPAL);
      if (attributes.csrfToken().isPresent()) names.add(CSRF);
      if (attributes.savedRequest().isPresent()) names.add(SAVED_REQUEST);
      names.add(OPERATION_TOKENS);
      return Set.copyOf(names);
    } finally {
      lock.unlock();
    }
  }

  @Override
  public void setAttribute(String name, @Nullable Object value) {
    Objects.requireNonNull(name, "name");
    lock.lock();
    try {
      var attributes = snapshot.attributes();
      switch (name) {
        case PRINCIPAL -> {
          if (value == null && attributes.principal().isEmpty()) return;
          if (!(value instanceof SessionPrincipal principal)) throw invalid();
          snapshot =
              lifecycle
                  .authenticate(snapshot.sessionId(), principal)
                  .orElseThrow(SessionStoreException::new);
        }
        case CSRF -> {
          if (!Objects.equals(attributes.csrfToken().orElse(null), value)) throw invalid();
        }
        case SAVED_REQUEST -> {
          Optional<SavedRequestTarget> target;
          if (value == null) target = Optional.empty();
          else if (value instanceof String location)
            target = Optional.of(SavedRequestTarget.fromGet("GET", location));
          else throw invalid();
          snapshot =
              lifecycle
                  .mutate(
                      snapshot.sessionId(),
                      current ->
                          new SessionAttributes(
                              current.principal(),
                              current.csrfToken(),
                              target,
                              current.operationTokens()))
                  .orElseThrow(SessionStoreException::new);
        }
        case OPERATION_TOKENS -> {
          var desired = tokenList(value);
          var previous = attributes.operationTokens();
          // QA049/BUG602/TOKV208: completion requires a verified reply and dedicated lifecycle.
          for (var next : desired)
            if (next.completedAt().isPresent() && !previous.contains(next)) throw invalid();
          for (var old : previous)
            for (var next : desired)
              if (old.token().equals(next.token()) && !old.equals(next)) throw invalid();
          snapshot =
              lifecycle
                  .mutate(
                      snapshot.sessionId(),
                      current ->
                          new SessionAttributes(
                              current.principal(),
                              current.csrfToken(),
                              current.savedRequest(),
                              merge(current.operationTokens(), previous, desired)))
                  .orElseThrow(SessionStoreException::new);
        }
        default -> throw invalid();
      }
    } finally {
      lock.unlock();
    }
  }

  @Override
  public void removeAttribute(String name) {
    setAttribute(name, null);
  }

  @Override
  public Instant getCreationTime() {
    lock.lock();
    try {
      return snapshot.row().identity().createdAt();
    } finally {
      lock.unlock();
    }
  }

  @Override
  public void setLastAccessedTime(Instant accessedAt) {
    Objects.requireNonNull(accessedAt, "accessedAt");
    lock.lock();
    try {
      snapshot =
          lifecycle.touch(snapshot.sessionId(), accessedAt).orElseThrow(SessionStoreException::new);
    } finally {
      lock.unlock();
    }
  }

  @Override
  public Instant getLastAccessedTime() {
    lock.lock();
    try {
      return snapshot.row().lastAccessedAt();
    } finally {
      lock.unlock();
    }
  }

  @Override
  public void setMaxInactiveInterval(Duration interval) {
    Objects.requireNonNull(interval, "interval");
    lock.lock();
    try {
      if (!Duration.ofSeconds(snapshot.row().maxInactiveSeconds()).equals(interval))
        throw invalid();
    } finally {
      lock.unlock();
    }
  }

  @Override
  public Duration getMaxInactiveInterval() {
    lock.lock();
    try {
      return Duration.ofSeconds(snapshot.row().maxInactiveSeconds());
    } finally {
      lock.unlock();
    }
  }

  @Override
  public boolean isExpired() {
    lock.lock();
    try {
      return !snapshot.row().expiresAt().isAfter(Objects.requireNonNull(clock.instant(), "clock"));
    } finally {
      lock.unlock();
    }
  }

  void save(SpringEncryptedSessionRepository repository) {
    if (owner != repository) throw invalid();
    lock.lock();
    try {
      snapshot = lifecycle.find(snapshot.sessionId()).orElseThrow(SessionStoreException::new);
    } finally {
      lock.unlock();
    }
  }

  @Override
  public String toString() {
    return "SpringWebSession[REDACTED]";
  }

  private static List<SessionOperationToken> tokenList(@Nullable Object value) {
    if (value == null) return List.of();
    if (!(value instanceof List<?> entries)) throw invalid();
    var tokens = new ArrayList<SessionOperationToken>();
    for (Object entry : entries) {
      if (!(entry instanceof SessionOperationToken token)) throw invalid();
      tokens.add(token);
    }
    return new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), tokens)
        .operationTokens();
  }

  private static List<SessionOperationToken> merge(
      List<SessionOperationToken> current,
      List<SessionOperationToken> previous,
      List<SessionOperationToken> desired) {
    var merged = new LinkedHashMap<UUID, SessionOperationToken>();
    for (var token : current) merged.put(token.token(), token);
    for (var token : previous) {
      if (!desired.contains(token)) {
        var existing = merged.get(token.token());
        // QA049: only an explicit new-form issue may retire a consumed token.
        // An already retired entry from a stale snapshot stays absent, never resurrected.
        if (existing != null) throw invalid();
      }
    }
    for (var token : desired) {
      if (!previous.contains(token)) {
        var existing = merged.putIfAbsent(token.token(), token);
        if (existing != null && !existing.equals(token)) throw invalid();
      }
    }
    return List.copyOf(merged.values());
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("session attribute is not writable");
  }
}
