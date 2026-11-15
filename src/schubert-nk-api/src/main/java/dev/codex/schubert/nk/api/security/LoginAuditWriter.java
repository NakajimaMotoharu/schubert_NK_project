package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Types;
import java.text.Normalizer;
import java.time.Instant;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * Critical Login audit in the caller transaction. No passwords/contexts, no independent commit.
 * NK-AUT-001; AUT-001/MON-004; UI226/252; SS314 §12/351 §3..4; PT-AUT-004-01..04.
 */
public final class LoginAuditWriter {
  private static final int EXPECTED_AFFECTED_ROWS = 1;

  void write(
      Connection connection,
      LoginResult result,
      LoginAuditReason reason,
      String usernameKey,
      InetAddress client,
      UUID messageId,
      UUID correlationId,
      Instant now)
      throws SQLException {
    boolean success = result instanceof LoginResult.Success;
    String action =
        success
            ? "LOGIN_SUCCEEDED"
            : result.resultCode() == ResultCode.LOCKED ? "LOGIN_LOCKED" : "LOGIN_FAILED";
    JsonObject details = new JsonObject();
    details.addProperty("resultCode", result.resultCode().wireValue());
    details.addProperty("reason", reason.name());
    details.addProperty("retryAfterSeconds", result.retryAfterSeconds());
    details.addProperty("outcome", success ? "SUCCESS" : "DENIED");
    String safeUsername =
        Normalizer.normalize(usernameKey, Normalizer.Form.NFC)
            .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " ");
    {
      var statement =
          requireValue(
              connection.prepareStatement(
                  "insert into schubert.app_logs"
                      + " (logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,actor_username,remote_address,details)"
                      + " values(?,'API','SECURITY',?,?,?,?,?,?,?,cast(? as inet),cast(? as jsonb))"));
      @Nullable Throwable jdbcFailure1 = null;
      try {
        statement.setObject(1, now.atOffset(java.time.ZoneOffset.UTC));
        statement.setString(2, success ? "INFO" : "WARN");
        statement.setString(3, action);
        statement.setString(4, action);
        statement.setObject(5, messageId);
        statement.setObject(6, correlationId);
        if (result instanceof LoginResult.Success accepted)
          statement.setLong(7, accepted.actor().userId());
        else statement.setNull(7, Types.BIGINT);
        statement.setString(8, safeUsername);
        statement.setString(9, client.getHostAddress());
        statement.setString(10, details.toString());
        if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS)
          throw new SQLException("critical login audit did not create one row", "40001");
      } catch (SQLException | RuntimeException | Error failure) {
        jdbcFailure1 = failure;
        throw failure;
      } finally {
        JdbcResourceCleanup.closeStatement(jdbcFailure1, statement);
      }
    }
  }
}
