package dev.codex.schubert.nk.api.security;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.sql.Types;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/**
 * Critical session audit, no session identifier. NK-AUT-001; MON-004/AUT-004; UI226/252; SS314
 * §12/351 §4/352 §12, SSC-010; PT-AUT-006-03/008-R.
 */
public final class SessionAuditWriter {
  void write(
      Connection connection,
      long actorId,
      long targetId,
      Optional<InetAddress> client,
      UUID messageId,
      UUID correlationId,
      Instant at,
      SessionRevocationReason reason,
      ResultCode result)
      throws SQLException {
    var details = new JsonObject();
    details.addProperty("targetUserId", targetId);
    details.addProperty("reason", reason.name());
    details.addProperty("resultCode", result.wireValue());
    try (var statement =
        connection.prepareStatement(
            "insert into schubert.app_logs"
                + " (logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,remote_address,details)"
                + " values(?,'API','SECURITY','INFO','SESSION_REVOKED','SESSION_REVOKED',?,?,?,cast(?"
                + " as inet),cast(? as jsonb))")) {
      statement.setTimestamp(1, Timestamp.from(at));
      statement.setObject(2, messageId);
      statement.setObject(3, correlationId);
      statement.setLong(4, actorId);
      if (client.isPresent()) statement.setString(5, client.orElseThrow().getHostAddress());
      else statement.setNull(5, Types.VARCHAR);
      statement.setString(6, details.toString());
      if (statement.executeUpdate() != 1)
        throw new SQLException("critical session audit did not create one row", "40001");
    }
  }
}
