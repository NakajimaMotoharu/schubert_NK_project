package dev.codex.schubert.nk.web.revocation;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException;
import dev.codex.schubert.nk.web.session.EncryptedWebSessionRepository;
import dev.codex.schubert.nk.web.session.SessionStoreException;
import dev.codex.schubert.nk.web.session.WebSessionId;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * Initial authenticated Logout, existing API facade then atomic encrypted retry/local deletion.
 * NK-WEB-002/AUT004/UI226232234/SS312314331352/QA050/SSC171/PG-D362/RERUN006. Captured trusted
 * context only, never an HTTP-bound String or inferred API expiry. Borrowed owners.
 */
public final class LocalLogoutCoordinator {
  public enum Outcome {
    CONFIRMED,
    QUEUED
  }

  private final EncryptedWebSessionRepository sessions;
  private final RevocationPayloadCodec codec;
  private final LogoutWireClient wire;
  private final Clock clock;

  public LocalLogoutCoordinator(
      EncryptedWebSessionRepository sessions,
      RevocationPayloadCodec codec,
      LogoutWireClient wire,
      Clock clock) {
    this.sessions = Objects.requireNonNull(sessions, "local sessions");
    this.codec = Objects.requireNonNull(codec, "revocation codec");
    this.wire = Objects.requireNonNull(wire, "Logout facade");
    this.clock = Objects.requireNonNull(clock, "Logout clock");
  }

  public Outcome logout(WebSessionId id, AuthenticationContext context) {
    Objects.requireNonNull(id, "local session identity");
    Objects.requireNonNull(context, "authenticated context");
    try {
      Instant requested =
          Objects.requireNonNull(clock.instant(), "Logout clock instant")
              .truncatedTo(ChronoUnit.MICROS);
      RevocationFailureCode reason;
      try {
        String code =
            wire.exchange(
                    new TypedPayloadValues(
                        new LayoutId("LOGREQ01"), new LogoutRequestData(), List.of()),
                    context)
                .resultCode()
                .wireValue();
        if (code.equals("0000") || code.equals("0200")) {
          sessions.invalidate(id);
          return Outcome.CONFIRMED;
        }
        reason =
            code.equals("0102")
                ? RevocationFailureCode.SESSION_INVALID
                : RevocationFailureCode.API_REJECTED;
      } catch (ProtectedReadWireException failure) {
        reason =
            failure.reason() == ProtectedReadWireException.Reason.INVALID_RESPONSE
                ? RevocationFailureCode.INVALID_RESPONSE
                : RevocationFailureCode.UNAVAILABLE;
      }
      var identity = new RevocationPayloadIdentity(UUID.randomUUID(), requested);
      var payload = codec.encrypt(identity, context);
      sessions.invalidateAndRetain(id, identity, payload, reason);
      return Outcome.QUEUED;
    } catch (RuntimeException | Error failure) {
      try {
        sessions.invalidate(id);
      } catch (RuntimeException | Error cleanup) {
        if (failure != cleanup) failure.addSuppressed(cleanup);
      }
      RevocationRetryCoordinator.preserveFatal(failure);
      throw new SessionStoreException();
    }
  }
}
