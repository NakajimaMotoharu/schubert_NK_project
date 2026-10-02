package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import com.google.gson.JsonObject;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import java.sql.*;
import java.text.Normalizer;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/**
 * Borrowed write transaction, after current authentication and Inbox NEW. No commit, rollback,
 * token/HMAC grant or JMS ownership. NK-QRY-001/NK-NTF-001; UI213/224/236; SS312§8/10,
 * 323/324/332§8..10/351; PG-D-331; PT-QRY028..032/NTF012..016.
 */
public final class QuestionCommandService {
  private static final String QUESTION_ADMIN =
      "select id,owner_user_id,is_deleted,deleted_at,deleted_by,version from schubert.questions where id=? for update";
  private static final String QUESTION_USER =
      "select id,owner_user_id,is_deleted,deleted_at,deleted_by,version from schubert.questions where id=? and owner_user_id=? for update";
  private static final String DELETE_ADMIN =
      "update schubert.questions set is_deleted=true,deleted_at=?,deleted_by=?,version=version+1 where id=? and is_deleted=false and version=?";
  private static final String DELETE_USER =
      "update schubert.questions set is_deleted=true,deleted_at=?,deleted_by=?,version=version+1 where id=? and is_deleted=false and version=? and owner_user_id=?";

  /** Empty reference means definite NOT_FOUND; success keeps original DB microseconds. */
  public record CancelResult(
      ResultCode code,
      OptionalLong jobId,
      Optional<NotificationState> state,
      Optional<Instant> cancelledAt) {
    public CancelResult {
      Objects.requireNonNull(code, "code");
      Objects.requireNonNull(jobId, "jobId");
      Objects.requireNonNull(state, "state");
      Objects.requireNonNull(cancelledAt, "cancelledAt");
      if (jobId.isPresent() && (jobId.getAsLong() < 1 || jobId.getAsLong() > 999_999_999_999L))
        throw new IllegalArgumentException("cancel result job is outside N12");
      boolean success = code.usesSuccessProfile();
      if (success) {
        if (jobId.isEmpty()
            || !state.equals(Optional.of(NotificationState.CANCELLED))
            || cancelledAt.isEmpty())
          throw new IllegalArgumentException("cancel success is inconsistent");
      } else if (code == ResultCode.NOT_CANCELLABLE) {
        if (jobId.isEmpty()
            || state.isEmpty()
            || cancelledAt.isPresent()
            || state.orElseThrow() == NotificationState.RECEIVED
            || state.orElseThrow() == NotificationState.CANCELLED)
          throw new IllegalArgumentException("cancel conflict is inconsistent");
      } else if ((code != ResultCode.NOT_FOUND && code != ResultCode.RESOURCE_LIMIT)
          || jobId.isPresent()
          || state.isPresent()
          || cancelledAt.isPresent()) {
        throw new IllegalArgumentException("cancel rejection is inconsistent");
      }
    }

    @Override
    public String toString() {
      return "CancelResult[REDACTED]";
    }
  }

  public record DeleteResult(ResultCode code, Optional<Instant> deletedAt) {
    public DeleteResult {
      Objects.requireNonNull(code, "code");
      Objects.requireNonNull(deletedAt, "deletedAt");
      if (code.usesSuccessProfile() != deletedAt.isPresent()
          || (!code.usesSuccessProfile()
              && code != ResultCode.NOT_FOUND
              && code != ResultCode.RESOURCE_LIMIT))
        throw new IllegalArgumentException("delete result is inconsistent");
    }

    @Override
    public String toString() {
      return "DeleteResult[REDACTED]";
    }
  }

  /** Lock job before notification, competing with the actual RECEIVED→PROCESSING worker. */
  public CancelResult cancel(
      Connection c,
      AuthenticatedActor actor,
      long notificationId,
      QuestionCommandMetadata metadata) {
    boundary(c, actor, notificationId, metadata);
    try {
      requireWrite(c);
      OptionalLong foundJob;
      try (var s =
          c.prepareStatement(
              "select job_id from schubert.notifications where id=? and owner_user_id=?")) {
        s.setLong(1, notificationId);
        s.setLong(2, actor.userId());
        try (var r = s.executeQuery()) {
          if (r.next()) {
            foundJob = OptionalLong.of(number(r, "job_id"));
            require(!r.next());
          } else {
            foundJob = OptionalLong.empty();
          }
        }
      }
      if (foundJob.isEmpty()) return absentCancel();
      long job = foundJob.orElseThrow();
      long question;
      NotificationState state;
      Optional<Instant> cancelled;
      Instant changed;
      long version;
      try (var s =
          c.prepareStatement(
              "select question_id,state,cancelled_at,state_changed_at,version from schubert.async_jobs where id=? and owner_user_id=? for update")) {
        s.setLong(1, job);
        s.setLong(2, actor.userId());
        try (var r = s.executeQuery()) {
          require(r.next());
          question = number(r, "question_id");
          state = NotificationState.valueOf(requireValue(r.getString("state")));
          cancelled = timestamp(r, "cancelled_at");
          changed = timestamp(r, "state_changed_at").orElseThrow();
          version = requireValue(r.getObject("version", Long.class));
          require(!r.next());
        }
      }
      try (var s =
          c.prepareStatement(
              "select job_id,question_id,state,state_changed_at from schubert.notifications where id=? and owner_user_id=? for update")) {
        s.setLong(1, notificationId);
        s.setLong(2, actor.userId());
        try (var r = s.executeQuery()) {
          require(
              r.next()
                  && number(r, "job_id") == job
                  && number(r, "question_id") == question
                  && state.name().equals(r.getString("state"))
                  && timestamp(r, "state_changed_at").equals(Optional.of(changed)));
          require(!r.next());
        }
      }
      require((state == NotificationState.CANCELLED) == cancelled.isPresent());
      if (state == NotificationState.CANCELLED)
        return new CancelResult(
            ResultCode.IDEMPOTENT_SUCCESS, OptionalLong.of(job), Optional.of(state), cancelled);
      if (state != NotificationState.RECEIVED)
        return new CancelResult(
            ResultCode.NOT_CANCELLABLE, OptionalLong.of(job), Optional.of(state), Optional.empty());
      if (version == 999_999_999L)
        return new CancelResult(
            ResultCode.RESOURCE_LIMIT, OptionalLong.empty(), Optional.empty(), Optional.empty());
      require(!metadata.at().isBefore(changed));
      try (var s =
          c.prepareStatement(
              "update schubert.async_jobs set state='CANCELLED',cancelled_at=?,state_changed_at=?,version=version+1 where id=? and owner_user_id=? and state='RECEIVED' and version=?")) {
        s.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
        s.setObject(2, metadata.at().atOffset(ZoneOffset.UTC));
        s.setLong(3, job);
        s.setLong(4, actor.userId());
        s.setLong(5, version);
        require(s.executeUpdate() == 1);
      }
      try (var s =
          c.prepareStatement(
              "update schubert.notifications set state='CANCELLED',state_changed_at=?,updated_at=? where id=? and owner_user_id=? and job_id=? and state='RECEIVED'")) {
        s.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
        s.setObject(2, metadata.at().atOffset(ZoneOffset.UTC));
        s.setLong(3, notificationId);
        s.setLong(4, actor.userId());
        s.setLong(5, job);
        require(s.executeUpdate() == 1);
      }
      audit(c, actor, metadata, "QUESTION_CANCELLED", question, OptionalLong.of(job), "CANCELLED");
      return new CancelResult(
          ResultCode.SUCCESS,
          OptionalLong.of(job),
          Optional.of(NotificationState.CANCELLED),
          Optional.of(metadata.at()));
    } catch (SQLException | RuntimeException failure) {
      throw new TemporaryInfrastructureException();
    }
  }

  /** Question→answer locks; notification/job never mutated. Separate role SQL, no role OR. */
  public DeleteResult logicalDelete(
      Connection c, AuthenticatedActor actor, long questionId, QuestionCommandMetadata metadata) {
    boundary(c, actor, questionId, metadata);
    try {
      requireWrite(c);
      boolean admin = actor.role() == Role.ADMIN;
      Optional<QuestionRow> found;
      try (var s = admin ? c.prepareStatement(QUESTION_ADMIN) : c.prepareStatement(QUESTION_USER)) {
        s.setLong(1, questionId);
        if (!admin) s.setLong(2, actor.userId());
        try (var r = s.executeQuery()) {
          if (r.next()) {
            boolean deleted = requireValue(r.getObject("is_deleted", Boolean.class));
            var deletedAt = timestamp(r, "deleted_at");
            var deletedBy = optionalNumber(r, "deleted_by");
            long version = requireValue(r.getObject("version", Long.class));
            require(deleted == deletedAt.isPresent() && deleted == deletedBy.isPresent());
            found = Optional.of(new QuestionRow(deleted, deletedAt, deletedBy, version));
            require(!r.next());
          } else {
            found = Optional.empty();
          }
        }
      }
      if (found.isEmpty()) return new DeleteResult(ResultCode.NOT_FOUND, Optional.empty());
      var row = found.orElseThrow();
      boolean deleted = row.deleted();
      var deletedAt = row.deletedAt();
      var deletedBy = row.deletedBy();
      long version = row.version();
      boolean answer;
      try (var s =
          c.prepareStatement(
              "select is_deleted,deleted_at,deleted_by from schubert.answers where question_id=? for update")) {
        s.setLong(1, questionId);
        try (var r = s.executeQuery()) {
          answer = r.next();
          if (answer) {
            require(
                deleted == requireValue(r.getObject("is_deleted", Boolean.class))
                    && deletedAt.equals(timestamp(r, "deleted_at"))
                    && deletedBy.equals(optionalNumber(r, "deleted_by")));
            require(!r.next());
          }
        }
      }
      if (deleted) return new DeleteResult(ResultCode.IDEMPOTENT_SUCCESS, deletedAt);
      if (version == 999_999_999L)
        return new DeleteResult(ResultCode.RESOURCE_LIMIT, Optional.empty());
      try (var s = admin ? c.prepareStatement(DELETE_ADMIN) : c.prepareStatement(DELETE_USER)) {
        s.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
        s.setLong(2, actor.userId());
        s.setLong(3, questionId);
        s.setLong(4, version);
        if (!admin) s.setLong(5, actor.userId());
        require(s.executeUpdate() == 1);
      }
      if (answer) {
        try (var s =
            c.prepareStatement(
                "update schubert.answers set is_deleted=true,deleted_at=?,deleted_by=?,updated_at=? where question_id=? and is_deleted=false")) {
          s.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
          s.setLong(2, actor.userId());
          s.setObject(3, metadata.at().atOffset(ZoneOffset.UTC));
          s.setLong(4, questionId);
          require(s.executeUpdate() == 1);
        }
      }
      audit(
          c,
          actor,
          metadata,
          "QUESTION_DELETE_MARKED",
          questionId,
          OptionalLong.empty(),
          "DELETED");
      return new DeleteResult(ResultCode.SUCCESS, Optional.of(metadata.at()));
    } catch (SQLException | RuntimeException failure) {
      throw new TemporaryInfrastructureException();
    }
  }

  private static void boundary(
      Connection c, AuthenticatedActor actor, long id, QuestionCommandMetadata metadata) {
    Objects.requireNonNull(c, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(metadata, "metadata");
    if (id < 1 || id > 999_999_999_999L) throw new IllegalArgumentException("target outside N12");
  }

  private record QuestionRow(
      boolean deleted, Optional<Instant> deletedAt, OptionalLong deletedBy, long version) {}

  private static void requireWrite(Connection c) throws SQLException {
    require(!c.getAutoCommit() && !c.isReadOnly());
  }

  private static CancelResult absentCancel() {
    return new CancelResult(
        ResultCode.NOT_FOUND, OptionalLong.empty(), Optional.empty(), Optional.empty());
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("question mutation invariant failed");
  }

  private static long number(ResultSet r, String column) throws SQLException {
    long n = requireValue(r.getObject(column, Long.class));
    require(n >= 1 && n <= 999_999_999_999L);
    return n;
  }

  private static OptionalLong optionalNumber(ResultSet r, String column) throws SQLException {
    Long value = r.getObject(column, Long.class);
    return value == null ? OptionalLong.empty() : OptionalLong.of(value);
  }

  private static Optional<Instant> timestamp(ResultSet r, String column) throws SQLException {
    return Optional.ofNullable(r.getObject(column, OffsetDateTime.class))
        .map(OffsetDateTime::toInstant);
  }

  private static void audit(
      Connection c,
      AuthenticatedActor actor,
      QuestionCommandMetadata metadata,
      String action,
      long question,
      OptionalLong job,
      String state)
      throws SQLException {
    var details = new JsonObject();
    try (var s = c.prepareStatement("select receipt_id from schubert.questions where id=?")) {
      s.setLong(1, question);
      try (var r = s.executeQuery()) {
        require(r.next());
        String receipt = requireValue(r.getString("receipt_id"));
        require(receipt.matches("[0-9A-HJKMNP-TV-Z]{26}") && !r.next());
        details.addProperty("receiptId", receipt);
      }
    }
    details.addProperty("questionId", question);
    job.ifPresent(value -> details.addProperty("jobId", value));
    details.addProperty("actorRole", actor.role().name());
    details.addProperty("state", state);
    details.addProperty("resultCode", "0000");
    try (var s =
        c.prepareStatement(
            "insert into schubert.app_logs(logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,actor_username,details) values (?,'API','ACTION','INFO',?,?,?,?,?,?,cast(? as jsonb))")) {
      s.setObject(1, metadata.at().atOffset(ZoneOffset.UTC));
      s.setString(2, action);
      s.setString(3, action);
      s.setObject(4, metadata.messageId());
      s.setObject(5, metadata.correlationId());
      s.setLong(6, actor.userId());
      s.setString(
          7,
          Normalizer.normalize(actor.username(), Normalizer.Form.NFC)
              .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
      s.setString(8, details.toString());
      require(s.executeUpdate() == 1);
    }
  }
}
