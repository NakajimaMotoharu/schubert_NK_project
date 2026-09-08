package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Owns one API JDBC transaction, completes it before returning to the JMS send/ACK owner.
 * NK-AUT-001/NK-MSG-002; MQ-003/006/008; UI212/226/231/234; SS311/312 sections 3,12/324 section 7;
 * PG-D-050, PT-AUT-TX-001..004. No XA, automatic JDBC retry, JMS call or connection reuse here.
 */
public final class JdbcSyncRequestProcessor implements SyncRequestProcessor {
  private final DataSource database;
  private final TransactionalRequestHandler handler;
  private final Clock clock;

  public JdbcSyncRequestProcessor(
      DataSource database, TransactionalRequestHandler handler, Clock clock) {
    this.database = Objects.requireNonNull(database, "database");
    this.handler = Objects.requireNonNull(handler, "handler");
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  /** Definite business errors commit; infrastructure failures never produce a reply from here. */
  @Override
  public byte[] process(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    try (Connection connection =
        Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      try {
        byte[] response =
            Objects.requireNonNull(
                handler.handle(connection, request, clock.instant()), "encoded response");
        connection.commit();
        return response;
      } catch (SQLException | RuntimeException failure) {
        try {
          connection.rollback();
        } catch (SQLException rollbackFailure) {
          // Retained only within this scope to distinguish an unconfirmed permanent rejection.
          failure.addSuppressed(rollbackFailure);
        }
        throw failure;
      }
    } catch (PermanentProtocolException failure) {
      if (failure.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
      throw new PermanentProtocolException("request transaction rejected invalid protocol");
    } catch (SQLException | RuntimeException failure) {
      // Includes uncertain commit/close; Inbox makes subsequent delivery safe in either outcome.
      throw new TemporaryInfrastructureException();
    }
  }
}
