package dev.codex.schubert.nk.web.session;

import java.time.Clock;
import java.util.Objects;
import org.jspecify.annotations.Nullable;
import org.springframework.session.SessionRepository;

/**
 * Closed Spring Session bridge. NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.5/331/352;
 * SSC-042/PG-D-099/PT-WEB-044..049.
 */
public final class SpringEncryptedSessionRepository implements SessionRepository<SpringWebSession> {
  private final EncryptedWebSessionRepository lifecycle;
  private final Clock clock;

  public SpringEncryptedSessionRepository(EncryptedWebSessionRepository lifecycle, Clock clock) {
    this.lifecycle = Objects.requireNonNull(lifecycle, "lifecycle");
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  @Override
  public SpringWebSession createSession() {
    return new SpringWebSession(this, lifecycle, clock, lifecycle.create());
  }

  @Override
  public void save(SpringWebSession session) {
    Objects.requireNonNull(session, "session").save(this);
  }

  @Override
  public @Nullable SpringWebSession findById(String id) {
    Objects.requireNonNull(id, "id");
    WebSessionId parsed;
    try {
      parsed = WebSessionId.parse(id);
    } catch (IllegalArgumentException malformed) {
      return null;
    }
    return lifecycle
        .find(parsed)
        .map(value -> new SpringWebSession(this, lifecycle, clock, value))
        .orElse(null);
  }

  @Override
  public void deleteById(String id) {
    Objects.requireNonNull(id, "id");
    WebSessionId parsed;
    try {
      parsed = WebSessionId.parse(id);
    } catch (IllegalArgumentException malformed) {
      return;
    }
    lifecycle.invalidate(parsed);
  }
}
