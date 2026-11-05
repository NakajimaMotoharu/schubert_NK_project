package dev.codex.schubert.nk.api.logging;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.InternalEventProcessor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.log.WebLogEventData;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Types;
import java.util.Objects;
import javax.sql.DataSource;

/**
 * Commits API log projection before returning to the JMS ACK owner. Trace: NK-MSG-002; RD
 * MON-003/MON-004/MQ-008; UI235/252; SS312 section 11, SS324 section 9, SS331/351; SSC-008;
 * PT-IDEM-012. No Web DB/key access. Username/Role are display metadata, never authorization.
 */
public final class WebLogIngestService implements InternalEventProcessor {
  private final DataSource database;

  public WebLogIngestService(DataSource database) {
    this.database = Objects.requireNonNull(database, "database");
  }

  @Override
  public void process(WireMessage<FixedPayload> event) {
    ingest(event);
  }

  /** Returns true only for a new row; a duplicate keeps all original columns unchanged. */
  public boolean ingest(WireMessage<FixedPayload> event) {
    WebLogEventData data = decode(event);
    String details = RequestLogDetails.normalize(data.details(), data.role());
    String address;
    try {
      address = InetAddress.ofLiteral(data.remoteAddress()).getHostAddress();
    } catch (IllegalArgumentException invalidAddress) {
      throw new PermanentProtocolException("REQUEST log IP literal is invalid");
    }
    try (Connection connection =
        Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      try {
        boolean inserted = insert(connection, event, data, details, address);
        connection.commit();
        return inserted;
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException | Error rollbackFailure) {
          TemporaryInfrastructureException.attachSecondary(failure, rollbackFailure);
        }
        throw failure;
      }
    } catch (SQLException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      // SQL error messages may embed bound JSON/IP values; the listener needs only a retry signal.
      throw new LogProjectionDatabaseException();
    }
  }

  private static WebLogEventData decode(WireMessage<FixedPayload> event) {
    Objects.requireNonNull(event, "event");
    if (!event.header().layoutId().value().equals("WLGEVT01")) {
      throw new PermanentProtocolException("REQUEST log layout is invalid");
    }
    WebLogEventData data;
    try {
      event
          .header()
          .validateAgainst(
              LayoutRegistry.standard()
                  .require(event.header().layoutId(), event.header().layoutVersion()));
      data =
          (WebLogEventData)
              PayloadTypeCatalog.decode(
                      PayloadCodec.standard()
                          .decode(
                              event.header().layoutId(),
                              event.payload().copyData(),
                              event.payload().copyRecords(),
                              false))
                  .data();
    } catch (LayoutValidationException failure) {
      throw new PermanentProtocolException("REQUEST log payload semantics are invalid");
    }
    // QA054/SSC336: named decode already enforces REQUEST/HTTP_REQUEST_COMPLETED or
    // ACTION/MENU_VIEWED, rejecting all other category/action pairs before JDBC access.
    if (data.path().startsWith("//")
        || data.path().contains("#")
        || data.remoteAddress().contains("%")) {
      throw new PermanentProtocolException("REQUEST log metadata violate the projection contract");
    }
    return data;
  }

  private static boolean insert(
      Connection connection,
      WireMessage<FixedPayload> event,
      WebLogEventData data,
      String details,
      String address)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            "insert into schubert.app_logs"
                + " (logged_at,service,category,level,action,message,request_id,"
                + "message_id,correlation_id,source_message_id,actor_username,http_method,request_uri,status_code,remote_address,duration_ms,details)"
                + " values(?,'WEB',?,?,?,?,?,?,?,?,?,?,?,?,cast(? as inet),?,cast(? as jsonb)) on"
                + " conflict(source_message_id) do nothing")) {
      statement.setObject(1, data.occurredAt().atOffset(java.time.ZoneOffset.UTC));
      statement.setString(2, data.logType().wireValue());
      statement.setString(3, data.level().name());
      statement.setString(4, data.action().orElse("HTTP_REQUEST_COMPLETED"));
      statement.setString(5, data.message());
      statement.setObject(6, data.httpRequestId());
      statement.setObject(7, event.header().messageId());
      statement.setObject(8, event.header().correlationId());
      statement.setObject(9, event.header().messageId());
      if (data.username().isPresent()) {
        statement.setString(10, data.username().orElseThrow());
      } else {
        statement.setNull(10, Types.VARCHAR);
      }
      statement.setString(11, data.httpMethod());
      statement.setString(12, data.path());
      statement.setInt(13, data.httpStatus().value());
      statement.setString(14, address);
      statement.setInt(15, data.elapsedMs().value());
      statement.setString(16, details);
      return statement.executeUpdate() == 1;
    }
  }
}
