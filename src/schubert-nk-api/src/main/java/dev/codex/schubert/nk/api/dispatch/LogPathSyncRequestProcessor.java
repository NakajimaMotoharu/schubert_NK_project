package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.util.Objects;

/**
 * The three connected synchronous layouts needed by the initial Login→Log path. A structurally
 * valid but unregistered layout is a deployment gap, not a malformed wire: roll back for retry
 * rather than committing it to the protocol DLQ. The outer API process must register the remaining
 * layouts before full readiness. Trace: NK-MSG-001/NK-AUT-001/NK-ADM-001; RD FUN-001/008,
 * AUT-001/002,MQ-003/006/008; UI225/226/231/232/235; SS311/312/314/321/323/324; PG232/PT-JMS-017.
 */
public final class LogPathSyncRequestProcessor implements SyncRequestProcessor {
  private final SyncRequestProcessor login;
  private final SyncRequestProcessor gameContext;
  private final SyncRequestProcessor logSearch;

  public LogPathSyncRequestProcessor(
      SyncRequestProcessor login,
      SyncRequestProcessor gameContext,
      SyncRequestProcessor logSearch) {
    this.login = Objects.requireNonNull(login, "login");
    this.gameContext = Objects.requireNonNull(gameContext, "gameContext");
    this.logSearch = Objects.requireNonNull(logSearch, "logSearch");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    SyncRequestProcessor selected =
        switch (request.header().layoutId().value()) {
          case "LGNREQ01" -> login;
          case "GAMREQ01" -> gameContext;
          case "LGSREQ01" -> logSearch;
          default -> throw new TemporaryInfrastructureException();
        };
    return Objects.requireNonNull(selected.process(request), "encoded reply");
  }
}
