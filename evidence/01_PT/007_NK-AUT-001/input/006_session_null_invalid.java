package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

@NullMarked
final class SessionAuditNonnullCaller {
  static void check(
      SessionAuditWriter writer,
      Connection connection,
      Optional<InetAddress> client,
      UUID messageId,
      UUID correlationId,
      Instant at,
      SessionRevocationReason reason,
      ResultCode result)
      throws SQLException {
    writer.write(null, 17, 41, client, messageId, correlationId, at, reason, result);
    writer.write(connection, 17, 41, null, messageId, correlationId, at, reason, result);
    writer.write(connection, 17, 41, client, null, correlationId, at, reason, result);
    writer.write(connection, 17, 41, client, messageId, null, at, reason, result);
    writer.write(connection, 17, 41, client, messageId, correlationId, null, reason, result);
    writer.write(connection, 17, 41, client, messageId, correlationId, at, null, result);
    writer.write(connection, 17, 41, client, messageId, correlationId, at, reason, null);
  }
}
