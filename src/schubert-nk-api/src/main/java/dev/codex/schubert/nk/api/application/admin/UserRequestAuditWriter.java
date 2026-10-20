package dev.codex.schubert.nk.api.application.admin;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Types;
import java.text.Normalizer;
import java.time.Instant;
import java.util.Optional;

/**
 * Same-transaction critical admission/replay audit, closed catalog and no request body/secrets.
 * NK-ADM-001; MON-004/MQ-006..010; UI226/236; SS312/351 §4/352 §12;
 * SSC-034/PG-D-087/PT-ADM-034..039.
 */
final class UserRequestAuditWriter {
  private static final int EXPECTED_AFFECTED_ROWS = 1;

  enum Event {
    SESSION_INVALID,
    ROLE_DENIED,
    TOKEN_MISMATCH,
    MESSAGE_MISMATCH,
    REPLAY
  }

  void write(
      Connection connection,
      Optional<AuthenticatedActor> actor,
      UserMutationRequest request,
      Event event,
      Instant at)
      throws SQLException {
    String action =
        switch (event) {
          case SESSION_INVALID, ROLE_DENIED -> "AUTHORIZATION_DENIED";
          case TOKEN_MISMATCH -> UserAuditWriter.action(request.mutation());
          case MESSAGE_MISMATCH -> "PROTOCOL_REJECTED";
          case REPLAY -> "INBOX_REPLAYED";
        };
    var details = new JsonObject();
    details.addProperty("outcome", event == Event.REPLAY ? "REPLAY" : "DENIED");
    details.addProperty("reason", event.name());
    details.addProperty("layout", request.header().layoutId().value());
    details.addProperty("operation", request.mutation().name());
    details.addProperty("targetType", "USER");
    request.targetUserId().ifPresent(id -> details.addProperty("targetUserId", id));
    actor.ifPresent(value -> details.addProperty("actorRole", value.role().name()));
    String resultField =
        switch (event) {
          case SESSION_INVALID, ROLE_DENIED, TOKEN_MISMATCH -> "resultCode";
          case MESSAGE_MISMATCH -> "step";
          case REPLAY -> "count";
        };
    JsonPrimitive resultValue =
        switch (event) {
          case SESSION_INVALID -> new JsonPrimitive("0102");
          case ROLE_DENIED -> new JsonPrimitive("0103");
          case TOKEN_MISMATCH -> new JsonPrimitive("0105");
          case MESSAGE_MISMATCH -> new JsonPrimitive("MESSAGE_IDENTITY");
          case REPLAY -> new JsonPrimitive(1);
        };
    details.add(resultField, resultValue);
    // All JSON values are closed enums, an eight-byte layout, or N12 identifiers; < 400 bytes.
    // Username is a separate bounded column. No unbounded value or secret enters details.
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
        throw new SQLException("critical user admission audit did not create one row");
    }
  }
}
