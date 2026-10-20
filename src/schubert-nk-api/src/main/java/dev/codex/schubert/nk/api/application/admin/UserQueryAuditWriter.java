package dev.codex.schubert.nk.api.application.admin;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Types;
import java.text.Normalizer;
import java.time.Instant;
import java.util.Optional;

/**
 * Critical User query denial/replay audit in the final caller transaction. No search fields.
 * NK-ADM-001/MON-004/MQ-006..010; UI226/236; SS351 §4/352 §12; PG-D-089/PT-ADM-049/050/052..054.
 * Only a currently verified actor may be supplied.
 */
final class UserQueryAuditWriter {
  private static final int EXPECTED_AFFECTED_ROWS = 1;

  enum Event {
    SESSION_INVALID,
    ROLE_DENIED,
    MESSAGE_MISMATCH,
    REPLAY
  }

  void write(
      Connection connection,
      Optional<AuthenticatedActor> actor,
      UserQueryRequest request,
      Event event,
      Instant at)
      throws SQLException {
    String action =
        switch (event) {
          case SESSION_INVALID, ROLE_DENIED -> "AUTHORIZATION_DENIED";
          case MESSAGE_MISMATCH -> "PROTOCOL_REJECTED";
          case REPLAY -> "INBOX_REPLAYED";
        };
    var details = new JsonObject();
    details.addProperty("layout", request.header().layoutId().value());
    details.addProperty("reason", event.name());
    details.addProperty("targetType", "USER");
    details.addProperty("outcome", event == Event.REPLAY ? "REPLAY" : "DENIED");
    actor.ifPresent(value -> details.addProperty("actorRole", value.role().name()));
    details.addProperty(
        "step",
        switch (event) {
          case SESSION_INVALID -> "AUTH_CONTEXT";
          case ROLE_DENIED -> "ADMIN_ROLE";
          case MESSAGE_MISMATCH -> "MESSAGE_IDENTITY";
          case REPLAY -> "SAVED_RESULT";
        });
    // Closed enums/layout only, under 300 bytes. No query prefix, body, key, context or token.
    try (var statement =
        connection.prepareStatement(
            """
        insert into schubert.app_logs(logged_at,service,category,level,action,message,
          message_id,correlation_id,actor_user_id,actor_username,details)
        values (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))
        """)) {
      statement.setObject(1, at.atOffset(java.time.ZoneOffset.UTC));
      statement.setString(
          2, event == Event.REPLAY || event == Event.MESSAGE_MISMATCH ? "MQ" : "SECURITY");
      statement.setString(
          3, event == Event.REPLAY || event == Event.SESSION_INVALID ? "INFO" : "WARN");
      statement.setString(4, action);
      statement.setString(5, action);
      statement.setObject(6, request.header().messageId());
      statement.setObject(7, request.header().correlationId());
      if (actor.isPresent()) {
        var value = actor.orElseThrow();
        statement.setLong(8, value.userId());
        statement.setString(
            9,
            Normalizer.normalize(value.username(), Normalizer.Form.NFC)
                .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
      } else {
        statement.setNull(8, Types.BIGINT);
        statement.setNull(9, Types.VARCHAR);
      }
      statement.setString(10, details.toString());
      if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS)
        throw new SQLException("critical user query audit did not create one row");
    }
  }
}
