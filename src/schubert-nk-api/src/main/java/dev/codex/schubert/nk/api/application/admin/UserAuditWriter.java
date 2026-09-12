package dev.codex.schubert.nk.api.application.admin;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.SQLException;
import java.text.Normalizer;

/** Critical allowlist audit in the same transaction. NK-ADM-001; SS351/352; PT-ADM-014..023. */
final class UserAuditWriter {
  void write(
      Connection c,
      AuthenticatedActor actor,
      Mutation kind,
      UserCommandService.Change change,
      UserCommandMetadata metadata)
      throws SQLException {
    String action = action(kind);
    boolean success = change.result().resultCode().usesSuccessProfile();
    var details = new JsonObject();
    details.addProperty("outcome", success ? "SUCCESS" : "DENIED");
    details.addProperty("resultCode", change.result().resultCode().wireValue());
    change.target().ifPresent(id -> details.addProperty("targetUserId", id.value()));
    change.before().ifPresent(state -> details.add("before", state(state, metadata)));
    change.after().ifPresent(state -> details.add("after", state(state, metadata)));
    var known = change.after().or(change::before);
    known.ifPresent(state -> details.addProperty("targetUsername", safe(state.username())));
    String json = details.toString();
    if (json.getBytes(StandardCharsets.UTF_8).length > 1024)
      throw new SQLException("user audit exceeds limit");
    if (success && kind != Mutation.RESET_PASSWORD && kind != Mutation.UNLOCK)
      insert(c, actor, metadata, action, "ACTION", json, success);
    insert(c, actor, metadata, action, "SECURITY", json, success);
  }

  private static JsonObject state(UserCommandService.State state, UserCommandMetadata metadata) {
    var json = new JsonObject();
    json.addProperty("role", state.role().wireValue());
    json.addProperty("status", state.enabled() ? "ACTIVE" : "DISABLED");
    json.addProperty("version", state.version());
    json.addProperty("failedCount", state.failedCount());
    json.addProperty(
        "locked", state.lockedUntil().map(time -> time.isAfter(metadata.at())).orElse(false));
    return json;
  }

  /** Shared closed action catalog for business and pre-business token denial audit. PG-D-087. */
  static String action(Mutation kind) {
    return switch (kind) {
      case CREATE -> "USER_CREATED";
      case ENABLE, DISABLE -> "USER_STATUS_CHANGED";
      case PROMOTE, DEMOTE -> "USER_ROLE_CHANGED";
      case RESET_PASSWORD -> "USER_PASSWORD_RESET";
      case UNLOCK -> "USER_UNLOCKED";
    };
  }

  private static void insert(
      Connection c,
      AuthenticatedActor actor,
      UserCommandMetadata metadata,
      String action,
      String category,
      String details,
      boolean success)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            """
        insert into schubert.app_logs(logged_at,service,category,level,action,message,
          message_id,correlation_id,actor_user_id,actor_username,details)
        values (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))
        """)) {
      s.setObject(1, metadata.at().atOffset(java.time.ZoneOffset.UTC));
      s.setString(2, category);
      s.setString(3, success ? "INFO" : "WARN");
      s.setString(4, action);
      s.setString(5, action);
      s.setObject(6, metadata.messageId());
      s.setObject(7, metadata.correlationId());
      s.setLong(8, actor.userId());
      s.setString(9, safe(actor.username()));
      s.setString(10, details);
      if (s.executeUpdate() != 1)
        throw new SQLException("critical user audit did not create one row");
    }
  }

  private static String safe(String name) {
    return Normalizer.normalize(name, Normalizer.Form.NFC)
        .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " ");
  }
}
