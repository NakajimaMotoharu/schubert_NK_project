package dev.codex.schubert.nk.api.application.scenario;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import java.sql.Connection;
import java.sql.SQLException;
import java.text.Normalizer;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Objects;

/**
 * NK-SCN-001; RD FUN003..005/MON003004; UI234237; SS323324332351352;
 * BUG742/YKT523/PT-SCN-AUD469001..008. Called only inside the new-success Inbox callback: the
 * caller owns authentication, transaction and rollback. Saved replay never writes it again.
 */
final class ScenarioAuditWriter {
  void write(
      Connection connection,
      AuthenticatedActor actor,
      ScenarioRequest request,
      TypedPayloadValues response,
      Instant at)
      throws SQLException {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(at, "at");
    String action;
    long count;
    switch (request.header().layoutId().value()) {
      case "SRCREQ01" -> {
        action = "SCENARIO_SEARCHED";
        count = ((PagedResponseData) response.data()).totalCount();
      }
      case "SCNREQ01" -> {
        action = "SCENARIO_VIEWED";
        var detail = (ScenarioDetailResponseData) response.data();
        count =
            detail.deliveryMode() == DeliveryMode.FILE
                ? detail.fileRecordCount()
                : response.records().size();
      }
      default -> {
        return;
      } // No unapproved action for games/speakers/routes/file-list.
    }
    var details = new JsonObject();
    details.addProperty("layout", request.header().layoutId().value());
    details.addProperty("resultCount", count);
    // Closed kind + count only. Never serialize request conditions or response content/path.
    try (var statement =
        connection.prepareStatement(
            """
        insert into schubert.app_logs(logged_at,service,category,level,action,message,
          message_id,correlation_id,actor_user_id,actor_username,details)
        values (?,'API','ACTION','INFO',?,?,?,?,?,?,cast(? as jsonb))
        """)) {
      statement.setObject(1, at.atOffset(ZoneOffset.UTC));
      statement.setString(2, action);
      statement.setString(3, action);
      statement.setObject(4, request.header().messageId());
      statement.setObject(5, request.header().correlationId());
      statement.setLong(6, actor.userId());
      statement.setString(
          7,
          Normalizer.normalize(actor.username(), Normalizer.Form.NFC)
              .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
      statement.setString(8, details.toString());
      if (statement.executeUpdate() != 1)
        throw new SQLException("critical scenario audit did not create one row");
    }
  }
}
