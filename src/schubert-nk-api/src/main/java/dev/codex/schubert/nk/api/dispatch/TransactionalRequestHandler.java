package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;

/**
 * Application dispatch port; no JDBC commit/close or JMS operations in the handler.
 * NK-AUT-001/NK-MSG-002; MQ-003/006/008; UI212/231; SS311/312/324; PT-AUT-TX-001..004.
 */
@FunctionalInterface
public interface TransactionalRequestHandler {
  /**
   * Returns a complete encoded success or definite business error; any thrown failure rolls back.
   */
  byte[] handle(Connection connection, WireMessage<FixedPayload> request, Instant receivedAt)
      throws SQLException;
}
