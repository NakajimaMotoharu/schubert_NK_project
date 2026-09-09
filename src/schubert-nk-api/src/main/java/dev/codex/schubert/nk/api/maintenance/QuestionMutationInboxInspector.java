package dev.codex.schubert.nk.api.maintenance;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.idempotency.*;
import dev.codex.schubert.nk.protocol.codec.*;
import dev.codex.schubert.nk.protocol.header.*;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.question.*;
import java.sql.*;
import java.time.*;
import java.time.temporal.ChronoUnit;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only saved mutation verification; never authorizes deletion or current authentication.
 * Caller owns explicit transaction/reference locks and borrowed key lifetime. NK-DAT-001;
 * QST-001..010/NTF-001..012/DAT-009/OPS-009/MQ-008; UI232/236/241/251; SS324 12.9/331 3.11/332
 * 6,8,10,11; QA-046/SSC-049/052/PG-D-141; PT-DB-INBOX-177..192.
 */
@NullMarked
public final class QuestionMutationInboxInspector {
  private static final Map<String, Set<String>> CODES =
      Map.of(
          "QSBRSP01", Set.of("0000", "0200", "0100", "9001"),
          "NTCRSP01", Set.of("0000", "0200", "0104", "0107", "9001"),
          "QDLRSP01", Set.of("0000", "0200", "0104", "9001"));
  private static final String QUESTION =
      "select id,owner_user_id,operation_token,receipt_id,"
          + "submitted_at,is_deleted,deleted_at,deleted_by,version from schubert.questions where id=?";
  private static final String JOB =
      "select id,question_id,owner_user_id,message_id,correlation_id,"
          + "received_at,state,state_changed_at,cancelled_at,version from schubert.async_jobs where ";
  private final ResponseSnapshotCodec snapshots;
  private final ResultBoundResponseSnapshotCodec bound;

  public QuestionMutationInboxInspector(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    bound = new ResultBoundResponseSnapshotCodec(snapshots);
  }

  public boolean isConsistent(
      Connection connection,
      ResponseSnapshotIdentity identity,
      InboxCompletion completion,
      UUID operationToken) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(identity, "identity");
    Objects.requireNonNull(completion, "completion");
    Objects.requireNonNull(operationToken, "operationToken");
    var codes = CODES.get(identity.responseLayoutId());
    if (codes == null
        || identity.ownerUserId().isEmpty()
        || !identity.responseLayoutId().equals(completion.responseLayoutId())
        || !identity.responseVersion().equals(completion.responseVersion())
        || !identity.responseVersion().equals("001")
        || completion.responseSnapshot().isEmpty()) return false;
    try {
      if (connection.getAutoCommit()) return false;
      byte[] wire =
          completion.state() == InboxCompletionState.COMPLETED
              ? bound.decrypt(
                  identity,
                  completion.resultReference(),
                  operationToken,
                  completion.responseSnapshot().orElseThrow())
              : snapshots.decrypt(identity, completion.responseSnapshot().orElseThrow());
      try {
        if (!InboxResponseInspector.inspect(identity, completion, wire)) return false;
        var header = HeaderCodec.standard().peek(wire);
        var code = header.resultCode().orElseThrow();
        if (!codes.contains(code.wireValue())) return false;
        if (!code.usesSuccessProfile())
          return completion.resultReference().equals(InboxResultReference.none());
        var data = PayloadTypeCatalog.decode(decode(header, wire)).data();
        long id = completion.resultReference().numericId().orElseThrow();
        long owner = identity.ownerUserId().orElseThrow();
        return switch (identity.responseLayoutId()) {
          case "QSBRSP01" ->
              submit(
                  connection,
                  identity,
                  completion.completedAt(),
                  operationToken,
                  id,
                  owner,
                  (QuestionSubmitResponseData) data);
          case "NTCRSP01" ->
              cancel(
                  connection,
                  id,
                  owner,
                  completion.completedAt(),
                  (NotificationCancelResponseData) data);
          default ->
              delete(
                  connection,
                  id,
                  owner,
                  completion.completedAt(),
                  code.wireValue(),
                  (QuestionDeleteResponseData) data);
        };
      } finally {
        Arrays.fill(wire, (byte) 0);
      }
    } catch (SQLException
        | ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException
        | DateTimeException failure) {
      return false;
    }
  }

  private static boolean submit(
      Connection c,
      ResponseSnapshotIdentity identity,
      Instant completed,
      UUID token,
      long id,
      long owner,
      QuestionSubmitResponseData data)
      throws SQLException {
    if (data.questionId().value() != id) return false;
    return single(
        c,
        QUESTION,
        id,
        q -> {
          Instant submitted = time(q, "submitted_at");
          if (number(q, "id") != id
              || number(q, "owner_user_id") != owner
              || !token.equals(requireValue(q.getObject("operation_token", UUID.class)))
              || !data.receiptId().equals(requireValue(q.getString("receipt_id")))
              || !data.submittedAt().equals(submitted.truncatedTo(ChronoUnit.MILLIS))
              || submitted.isAfter(completed)) return false;
          return single(
              c,
              JOB + "question_id=?",
              id,
              j -> {
                long job = number(j, "id");
                if (number(j, "question_id") != id
                    || number(j, "owner_user_id") != owner
                    || !identity
                        .requestMessageId()
                        .equals(requireValue(j.getObject("message_id", UUID.class)))
                    || !identity
                        .requestMessageId()
                        .equals(requireValue(j.getObject("correlation_id", UUID.class)))
                    || !submitted.equals(time(j, "received_at"))) return false;
                return work(c, identity.requestMessageId(), id, job, data.receiptId(), completed);
              });
        });
  }

  private static boolean work(
      Connection c, UUID source, long question, long job, String receipt, Instant completed)
      throws SQLException {
    return single(
        c,
        "select message_id,correlation_id,body,status,sent_at,leased"
            + " from schubert.maintenance_read_question_work(?)",
        source,
        r -> {
          UUID message = requireValue(r.getObject("message_id", UUID.class));
          if (message.equals(source)
              || !source.equals(requireValue(r.getObject("correlation_id", UUID.class)))
              || !requireValue(r.getString("status")).equals("SENT")
              || requireValue(r.getObject("leased", Boolean.class))
              || time(r, "sent_at").isBefore(completed)) return false;
          byte[] wire = requireValue(r.getBytes("body"));
          try {
            if (wire.length != 320) return false;
            var h = HeaderCodec.standard().peek(wire);
            // HeaderCodec already enforces layout-specific kind/interaction/context/length.
            // Select the one allowed layout before comparing its authenticated DB identities.
            if (!h.layoutId().value().equals("QWKREQ01")
                || !h.messageId().equals(message)
                || !h.correlationId().equals(source)) return false;
            var data = (QuestionWorkData) PayloadTypeCatalog.decode(decode(h, wire)).data();
            return data.questionId().value() == question
                && data.asyncJobId().value() == job
                && data.receiptId().equals(receipt);
          } finally {
            Arrays.fill(wire, (byte) 0);
          }
        });
  }

  private static boolean cancel(
      Connection c, long id, long owner, Instant completed, NotificationCancelResponseData data)
      throws SQLException {
    return single(
        c,
        JOB + "id=?",
        id,
        j -> {
          Instant cancelled = time(j, "cancelled_at");
          long question = number(j, "question_id");
          if (number(j, "id") != id
              || number(j, "owner_user_id") != owner
              || !requireValue(j.getString("state")).equals("CANCELLED")
              || !version(j)
              || !cancelled.equals(time(j, "state_changed_at"))
              || cancelled.isAfter(completed)
              || !data.cancelledAt().orElseThrow().equals(cancelled.truncatedTo(ChronoUnit.MILLIS)))
            return false;
          boolean valid;
          try (var s =
              c.prepareStatement(
                  "select job_id,question_id,owner_user_id,state,state_changed_at"
                      + " from schubert.notifications where job_id=?")) {
            s.setLong(1, id);
            try (var n = s.executeQuery()) {
              // Legitimate prior notification retention cleanup leaves no child row.
              valid =
                  !n.next()
                      || (number(n, "job_id") == id
                          && number(n, "question_id") == question
                          && number(n, "owner_user_id") == owner
                          && requireValue(n.getString("state")).equals("CANCELLED")
                          && cancelled.equals(time(n, "state_changed_at"))
                          && !n.next());
            }
          }
          return valid;
        });
  }

  private static boolean delete(
      Connection c,
      long id,
      long owner,
      Instant completed,
      String code,
      QuestionDeleteResponseData data)
      throws SQLException {
    return single(
        c,
        QUESTION,
        id,
        q -> {
          Instant deleted = time(q, "deleted_at");
          long actor = number(q, "deleted_by");
          if (number(q, "id") != id
              || !requireValue(q.getObject("is_deleted", Boolean.class))
              || !version(q)
              || (code.equals("0000") && actor != owner)
              || deleted.isAfter(completed)
              || !data.deletedAt().equals(deleted.truncatedTo(ChronoUnit.MILLIS))) return false;
          boolean valid;
          try (var s =
              c.prepareStatement(
                  "select question_id,is_deleted,deleted_at,deleted_by"
                      + " from schubert.answers where question_id=?")) {
            s.setLong(1, id);
            try (var a = s.executeQuery()) {
              valid =
                  !a.next()
                      || (number(a, "question_id") == id
                          && requireValue(a.getObject("is_deleted", Boolean.class))
                          && actor == number(a, "deleted_by")
                          && deleted.equals(time(a, "deleted_at"))
                          && !a.next());
            }
          }
          return valid;
        });
  }

  private static PayloadValues decode(CommonHeader header, byte[] wire) {
    byte[] data = Arrays.copyOfRange(wire, 256, wire.length);
    try {
      // BUG-121/YKT-101: EVENT has no result; never pass null to response-only overload.
      return header.messageKind() == MessageKind.EVENT
          ? PayloadCodec.standard().decode(header.layoutId(), data, List.of(), false)
          : PayloadCodec.standard()
              .decode(header.layoutId(), data, List.of(), header.resultCode().orElseThrow());
    } finally {
      Arrays.fill(data, (byte) 0);
    }
  }

  private static long number(ResultSet row, String column) throws SQLException {
    long value = requireValue(row.getObject(column, Long.class));
    if (value < 1 || value > 999_999_999_999L)
      throw new SQLDataException("invalid reference number");
    return value;
  }

  private static boolean version(ResultSet row) throws SQLException {
    long value = requireValue(row.getObject("version", Long.class));
    return value >= 1 && value <= 999_999_999L;
  }

  private static Instant time(ResultSet row, String column) throws SQLException {
    Instant value = requireValue(row.getObject(column, OffsetDateTime.class)).toInstant();
    int year = value.atZone(ZoneOffset.UTC).getYear();
    if (year < 1 || year > 9999) throw new SQLDataException("invalid reference time");
    return value;
  }

  @FunctionalInterface
  private interface RowCheck {
    boolean check(ResultSet row) throws SQLException;
  }

  private static boolean single(Connection c, String sql, Object key, RowCheck check)
      throws SQLException {
    boolean valid;
    try (var statement = c.prepareStatement(sql)) {
      statement.setObject(1, key);
      try (var row = statement.executeQuery()) {
        valid = row.next() && check.check(row) && !row.next();
      }
    }
    return valid;
  }

  @Override
  public String toString() {
    return "QuestionMutationInboxInspector[REDACTED]";
  }
}
