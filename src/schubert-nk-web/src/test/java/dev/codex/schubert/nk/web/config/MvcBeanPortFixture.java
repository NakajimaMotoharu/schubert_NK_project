package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Constructor-only dependency owner for explicit MVC Bean tests; no backend operation is admitted.
 */
final class MvcBeanPortFixture implements AutoCloseable {
  private static final Clock FIXED_CLOCK = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
  private final SecurityContextOwnerPortFixture owner = new SecurityContextOwnerPortFixture();
  private final JmsRequestReplyClient retainedRequester =
      new JmsRequestReplyClient(new ReplyCorrelationRegistry(), FIXED_CLOCK, 1);
  private final ApiSessionInvalidHandler retainedInvalid =
      new ApiSessionInvalidHandler(
          owner.sessions(), new WebSecurityAudit(new NoLog(), FIXED_CLOCK, "fixture", "fixture"));

  JmsRequestReplyClient requester() {
    return retainedRequester;
  }

  ApiSessionInvalidHandler invalid() {
    return retainedInvalid;
  }

  Clock clock() {
    return FIXED_CLOCK;
  }

  JmsRequestSender sender() {
    return (id, bytes) -> {
      throw new AssertionError("wire sender forbidden in constructor-only fixture");
    };
  }

  Supplier<UUID> identifiers() {
    return () -> {
      throw new AssertionError("identifier supplier forbidden in constructor-only fixture");
    };
  }

  @Override
  public void close() {
    owner.close();
  }

  private static final class NoLog implements System.Logger {
    @Override
    public String getName() {
      return "public-fixture";
    }

    @Override
    public boolean isLoggable(Level level) {
      return false;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      throw new AssertionError("audit log forbidden in constructor-only fixture");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      throw new AssertionError("audit log forbidden in constructor-only fixture");
    }
  }
}
