package dev.codex.schubert.nk.api.security;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.InetAddress;
import java.util.Optional;
import java.util.UUID;
import java.time.Instant;
import org.jspecify.annotations.NullMarked;
@NullMarked
final class SessionAuditNonnullCaller {
  static void check(SessionAuditWriter writer, Connection connection,
      Optional<InetAddress> client, UUID messageId, UUID correlationId, Instant at,
      SessionRevocationReason reason, ResultCode result) throws SQLException {
    writer.write(connection, 17, 41, client, messageId, correlationId, at, reason, result);
  }
}
