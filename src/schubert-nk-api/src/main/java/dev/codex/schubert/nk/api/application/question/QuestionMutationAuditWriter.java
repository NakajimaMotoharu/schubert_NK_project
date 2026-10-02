package dev.codex.schubert.nk.api.application.question;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import java.sql.*;
import java.text.Normalizer;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;

/**
 * Critical mutation denial/replay/capacity audit; no body/context/token. SS351/352,
 * NK-QRY-001/NTF-001; PG-D332; PT-QRY039..045. Borrowed transaction only.
 */
final class QuestionMutationAuditWriter {
  enum Event {
    SESSION_INVALID,
    OWNER_DENIED,
    TOKEN_MISMATCH,
    MESSAGE_MISMATCH,
    REPLAY,
    CAPACITY
  }

  void write(
      Connection c,
      Optional<AuthenticatedActor> actor,
      QuestionMutationRequest request,
      Event event,
      Instant at)
      throws SQLException {
    String action =
        switch (event) {
          case SESSION_INVALID, TOKEN_MISMATCH -> "AUTHORIZATION_DENIED";
          case OWNER_DENIED -> "OWNER_SCOPE_DENIED";
          case MESSAGE_MISMATCH -> "PROTOCOL_REJECTED";
          case REPLAY -> "INBOX_REPLAYED";
          case CAPACITY -> "RESOURCE_LIMIT_REACHED";
        };
    var details = new JsonObject();
    details.addProperty("layout", request.header().layoutId().value());
    details.addProperty("reason", event.name());
    details.addProperty("targetType", request.cancellation() ? "NOTIFICATION" : "QUESTION");
    actor.ifPresent(value -> details.addProperty("actorRole", value.role().name()));
    if (event == Event.CAPACITY) {
      details.addProperty("resource", "N9_VERSION");
      details.addProperty("errorCode", "9001");
    }
    try (var s =
        c.prepareStatement(
            "insert into schubert.app_logs(logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,actor_username,details) values (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))")) {
      s.setObject(1, at.atOffset(ZoneOffset.UTC));
      s.setString(
          2,
          event == Event.CAPACITY
              ? "SYSTEM"
              : event == Event.REPLAY || event == Event.MESSAGE_MISMATCH ? "MQ" : "SECURITY");
      s.setString(
          3,
          event == Event.CAPACITY
              ? "ERROR"
              : event == Event.REPLAY || event == Event.SESSION_INVALID ? "INFO" : "WARN");
      s.setString(4, action);
      s.setString(5, action);
      s.setObject(6, request.header().messageId());
      s.setObject(7, request.header().correlationId());
      if (actor.isPresent()) {
        var value = actor.orElseThrow();
        s.setLong(8, value.userId());
        s.setString(
            9,
            Normalizer.normalize(value.username(), Normalizer.Form.NFC)
                .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
      } else {
        s.setNull(8, Types.BIGINT);
        s.setNull(9, Types.VARCHAR);
      }
      s.setString(10, details.toString());
      if (s.executeUpdate() != 1)
        throw new SQLException("critical question mutation audit count is invalid");
    }
  }
}
