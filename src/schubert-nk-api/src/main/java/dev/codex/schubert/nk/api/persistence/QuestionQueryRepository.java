package dev.codex.schubert.nk.api.persistence;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.question.NotificationSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationErrorCode;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * Four bounded query projections in a borrowed read-only transaction; no auth grant, commit or JMS.
 * NK-QRY-001/NK-NTF-001; FUN011..013/QST005..010/NTF001..012; UI224236241; SS312§10/323/332;
 * SSC157/PG-D-330; PT-QRY001..005/PT-NTF001..005. Notification scope is always the actor, including
 * ADMIN. Deleted notification text is SQL NULL.
 */
public final class QuestionQueryRepository {
  private static final java.lang.String LITERAL_WITH_PROJECTED_AS = "with projected as (";

  private static final java.lang.String LITERAL_QUESTION_BODY = "question_body";

  private static final String QUESTION_COLUMNS =
      "id,receipt_id,owner_user_id,username,question_body,answer_body,submitted_at,answered_at,"
          + "question_deleted,answer_state";
  private static final String QUESTION =
      """
      select q.id,q.receipt_id,q.owner_user_id,u.username,q.body as question_body,
        case when j.state='COMPLETED' and not a.is_deleted then a.body end as answer_body,
        q.submitted_at,
        case when j.state='COMPLETED' and not a.is_deleted then a.answered_at end as answered_at,
        q.is_deleted as question_deleted,
        case when j.state='ERROR' then 'ERROR' when j.state='COMPLETED' then 'ANSWERED'
             else 'UNANSWERED' end as answer_state
        from schubert.questions q join schubert.app_users u on u.id=q.owner_user_id
        join schubert.async_jobs j on j.question_id=q.id and j.owner_user_id=q.owner_user_id
        left join schubert.answers a on a.question_id=q.id
      """;
  private static final String NOTICE_COLUMNS =
      "id,receipt_id,owner_user_id,notification_type,state,submitted_at,updated_at,"
          + "question_deleted,question_body,answer_body,question_id,started_at,completed_at,"
          + "error_at,cancelled_at,error_code,error_message";
  private static final String NOTICE =
      """
      select n.id,q.receipt_id,n.owner_user_id,n.notification_type,n.state,
        n.accepted_at as submitted_at,n.state_changed_at as updated_at,q.is_deleted as question_deleted,
        case when not q.is_deleted then q.body end as question_body,
        case when not q.is_deleted and n.state='COMPLETED' and not a.is_deleted then a.body end as answer_body,
        case when not q.is_deleted then q.id end as question_id,
        j.started_at,j.completed_at,j.error_at,j.cancelled_at,n.error_code,n.error_message
        from schubert.notifications n
        join schubert.questions q on q.id=n.question_id and q.owner_user_id=n.owner_user_id
        join schubert.async_jobs j on j.id=n.job_id and j.question_id=q.id
          and j.owner_user_id=n.owner_user_id and j.state=n.state
        left join schubert.answers a on a.question_id=q.id
      """;

  // BUG459/YKT349: every SQL token is compile-time constant; optional inputs are typed binds.
  private static final String PAGE =
      ",totals as (select count(*) as total from filtered),page as (select total,"
          + "greatest(1,(total+49)/50) as pages,least(cast(? as bigint),greatest(1,(total+49)/50)) as effective from totals)";
  private static final String QUESTION_START =
      LITERAL_WITH_PROJECTED_AS
          + QUESTION
          + "),filtered as materialized (select "
          + QUESTION_COLUMNS
          + " from projected where not question_deleted";
  private static final String QUESTION_FILTER =
      " and (cast(? as text) is null or username=?)"
          + " and (cast(? as text) is null or answer_state=?)"
          + " and (cast(? as text) is null or question_body ilike ? escape '\\' or answer_body ilike ? escape '\\')"
          + " and (cast(? as timestamptz) is null or submitted_at>=?)"
          + " and (cast(? as timestamptz) is null or submitted_at<=?))"
          + PAGE
          + " select p.total,p.pages,p.effective,x.id,x.receipt_id,x.owner_user_id,x.username,"
          + "x.question_body,x.answer_body,x.submitted_at,x.answered_at,x.question_deleted,x.answer_state"
          + " from page p left join lateral (select "
          + QUESTION_COLUMNS
          + " from filtered order by submitted_at desc,id desc limit 50 offset (p.effective-1)*50) x"
          + " on true order by x.submitted_at desc,x.id desc";
  // SS332§9/BUG469: USER and ADMIN have distinct query IDs, no SQL authorization OR.
  private static final String QUESTION_USER_PAGE =
      QUESTION_START + " and owner_user_id=?" + QUESTION_FILTER;
  private static final String QUESTION_ADMIN_PAGE = QUESTION_START + QUESTION_FILTER;
  private static final String NOTICE_PAGE =
      LITERAL_WITH_PROJECTED_AS
          + NOTICE
          + "),filtered as materialized (select "
          + NOTICE_COLUMNS
          + " from projected where owner_user_id=?"
          + " and (cast(? as text) is null or notification_type=?)"
          + " and (cast(? as timestamptz) is null or submitted_at>=?)"
          + " and (cast(? as timestamptz) is null or submitted_at<=?))"
          + PAGE
          + " select p.total,p.pages,p.effective,x.id,x.receipt_id,x.owner_user_id,x.notification_type,"
          + "x.state,x.submitted_at,x.updated_at,x.question_deleted,x.question_body,x.answer_body,"
          + "x.question_id,x.started_at,x.completed_at,x.error_at,x.cancelled_at,x.error_code,x.error_message"
          + " from page p left join lateral (select "
          + NOTICE_COLUMNS
          + " from filtered order by updated_at desc,id desc limit 50 offset (p.effective-1)*50) x"
          + " on true order by x.updated_at desc,x.id desc";
  private static final String QUESTION_ADMIN_DETAIL =
      LITERAL_WITH_PROJECTED_AS
          + QUESTION
          + ") select "
          + QUESTION_COLUMNS
          + " from projected where id=? and not question_deleted";
  private static final String QUESTION_USER_DETAIL = QUESTION_ADMIN_DETAIL + " and owner_user_id=?";
  private static final String NOTICE_DETAIL =
      LITERAL_WITH_PROJECTED_AS
          + NOTICE
          + ") select "
          + NOTICE_COLUMNS
          + " from projected where id=? and owner_user_id=?";

  public TypedPayloadValues questionSearch(
      Connection c, AuthenticatedActor actor, QuestionSearchRequestData request) {
    boundary(c, actor, request);
    validateRequest("QSSREQ01", request);
    if (actor.role() == Role.USER && request.username().isPresent())
      throw new QuestionQueryException(ResultCode.VALIDATION_ERROR);
    var username = request.username();
    var state = request.answerState().map(AnswerState::wireValue);
    var pattern =
        request
            .keyword()
            .map(v -> "%" + v.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%");
    var from = request.submittedFrom().map(v -> v.atOffset(ZoneOffset.UTC));
    var to = request.submittedTo().map(v -> v.atOffset(ZoneOffset.UTC));
    var parameters = new ArrayList<Optional<?>>();
    if (actor.role() == Role.USER) parameters.add(Optional.of(actor.userId()));
    parameters.addAll(
        List.of(username, username, state, state, pattern, pattern, pattern, from, from, to, to));
    return paged(
        c,
        true,
        actor.role() == Role.ADMIN,
        parameters,
        request.page(),
        "QSSRSP01",
        QuestionQueryRepository::questionRecord);
  }

  public TypedPayloadValues notificationSearch(
      Connection c, AuthenticatedActor actor, NotificationSearchRequestData request) {
    boundary(c, actor, request);
    validateRequest("NTSREQ01", request);
    var type = request.notificationType().map(NotificationType::wireValue);
    var from = request.submittedFrom().map(v -> v.atOffset(ZoneOffset.UTC));
    var to = request.submittedTo().map(v -> v.atOffset(ZoneOffset.UTC));
    return paged(
        c,
        false,
        false,
        List.of(Optional.of(actor.userId()), type, type, from, from, to, to),
        request.page(),
        "NTSRSP01",
        QuestionQueryRepository::notificationRecord);
  }

  public Optional<TypedPayloadValues> questionDetail(
      Connection c, AuthenticatedActor actor, QuestionDetailRequestData request) {
    boundary(c, actor, request);
    validateRequest("QSDREQ01", request);
    var parameters = new ArrayList<Optional<?>>();
    parameters.add(Optional.of(request.questionId().value()));
    if (actor.role() == Role.USER) parameters.add(Optional.of(actor.userId()));
    return detail(
        c,
        true,
        actor.role() == Role.ADMIN,
        parameters,
        "QSDRSP01",
        r -> {
          var record = questionRecord(r);
          return new QuestionDetailResponseData(
              record.questionId(),
              record.receiptId(),
              record.username(),
              record.answerState(),
              text(r, LITERAL_QUESTION_BODY),
              optionalText(r, "answer_body"),
              record.submittedAt(),
              record.answeredAt());
        });
  }

  public Optional<TypedPayloadValues> notificationDetail(
      Connection c, AuthenticatedActor actor, NotificationDetailRequestData request) {
    boundary(c, actor, request);
    validateRequest("NTDREQ01", request);
    return detail(
        c,
        false,
        false,
        List.of(Optional.of(request.notificationId().value()), Optional.of(actor.userId())),
        "NTDRSP01",
        r -> {
          var record = notificationRecord(r);
          Optional<QuestionId> question =
              Optional.ofNullable(r.getObject("question_id", Long.class)).map(QuestionId::new);
          Optional<NotificationErrorCode> error =
              optionalText(r, "error_code")
                  .map(
                      v -> {
                        for (var code : NotificationErrorCode.values())
                          if (code.wireValue().equals(v)) return code;
                        throw new IllegalArgumentException("notification error code is invalid");
                      });
          return new NotificationDetailResponseData(
              record.notificationId(),
              record.receiptId(),
              record.notificationType(),
              record.internalState(),
              record.submittedAt(),
              optionalTime(r, "started_at"),
              optionalTime(r, "completed_at"),
              optionalTime(r, "error_at"),
              optionalTime(r, "cancelled_at"),
              record.questionDeleted(),
              optionalText(r, LITERAL_QUESTION_BODY),
              optionalText(r, "answer_body"),
              error,
              optionalText(r, "error_message"),
              question);
        });
  }

  private static TypedPayloadValues paged(
      Connection c,
      boolean question,
      boolean admin,
      List<? extends Optional<?>> parameters,
      int requested,
      String layout,
      RowMapper<PayloadRecord> mapper) {
    try {
      requireRead(c);
      try (var s =
          question
              ? (admin
                  ? c.prepareStatement(QUESTION_ADMIN_PAGE)
                  : c.prepareStatement(QUESTION_USER_PAGE))
              : c.prepareStatement(NOTICE_PAGE)) {
        bind(s, parameters);
        s.setInt(parameters.size() + 1, requested);
        try (var r = s.executeQuery()) {
          require(r.next());
          long total = number(r, "total");
          if (total > 49_999_950) throw new QuestionQueryException(ResultCode.RESOURCE_LIMIT);
          int pages = Math.toIntExact(number(r, "pages"));
          int effective = Math.toIntExact(number(r, "effective"));
          require(
              total >= 0
                  && pages == Math.max(1, (total + 49) / 50)
                  && effective == Math.min(requested, pages));
          var records = new ArrayList<PayloadRecord>();
          do {
            require(
                total == number(r, "total")
                    && pages == number(r, "pages")
                    && effective == number(r, "effective"));
            if (r.getObject("id") != null) records.add(mapper.read(r));
          } while (r.next());
          long first = total == 0 ? 0 : (effective - 1L) * 50 + 1;
          long last = Math.min(effective * 50L, total);
          require(records.size() == (total == 0 ? 0 : last - first + 1));
          return validate(
              new TypedPayloadValues(
                  new LayoutId(layout),
                  new PagedResponseData(effective, 50, total, pages, first, last),
                  records));
        }
      }
    } catch (QuestionQueryException failure) {
      if (failure.getSuppressed().length == 0) throw failure;
      throw new QuestionQueryException(ResultCode.TEMPORARY_FAILURE);
    } catch (SQLException | RuntimeException failure) {
      throw new QuestionQueryException(ResultCode.TEMPORARY_FAILURE);
    }
  }

  private static Optional<TypedPayloadValues> detail(
      Connection c,
      boolean question,
      boolean admin,
      List<? extends Optional<?>> parameters,
      String layout,
      RowMapper<PayloadData> mapper) {
    try {
      requireRead(c);
      try (var s =
          question
              ? (admin
                  ? c.prepareStatement(QUESTION_ADMIN_DETAIL)
                  : c.prepareStatement(QUESTION_USER_DETAIL))
              : c.prepareStatement(NOTICE_DETAIL)) {
        bind(s, parameters);
        try (var r = s.executeQuery()) {
          Optional<TypedPayloadValues> result = Optional.empty();
          if (r.next()) {
            result =
                Optional.of(
                    validate(
                        new TypedPayloadValues(new LayoutId(layout), mapper.read(r), List.of())));
            require(!r.next());
          }
          return result;
        }
      }
    } catch (SQLException | RuntimeException failure) {
      throw new QuestionQueryException(ResultCode.TEMPORARY_FAILURE);
    }
  }

  private static QuestionSummaryRecord questionRecord(ResultSet r) throws SQLException {
    return new QuestionSummaryRecord(
        new QuestionId(number(r, "id")),
        text(r, "receipt_id"),
        text(r, "username"),
        summary(text(r, LITERAL_QUESTION_BODY)),
        AnswerState.valueOf(text(r, "answer_state")),
        time(r, "submitted_at"),
        optionalTime(r, "answered_at"));
  }

  private static NotificationRecord notificationRecord(ResultSet r) throws SQLException {
    boolean deleted = requireValue(r.getObject("question_deleted", Boolean.class));
    return new NotificationRecord(
        new NotificationId(number(r, "id")),
        text(r, "receipt_id"),
        NotificationType.valueOf(text(r, "notification_type")),
        NotificationState.valueOf(text(r, "state")),
        time(r, "submitted_at"),
        time(r, "updated_at"),
        deleted ? "削除済み" : summary(text(r, LITERAL_QUESTION_BODY)),
        deleted);
  }

  private static String summary(String value) {
    return value.substring(
        0, value.offsetByCodePoints(0, Math.min(100, value.codePointCount(0, value.length()))));
  }

  private static String text(ResultSet r, String name) throws SQLException {
    return requireValue(r.getString(name));
  }

  private static Optional<String> optionalText(ResultSet r, String name) throws SQLException {
    return Optional.ofNullable(r.getString(name));
  }

  private static long number(ResultSet r, String name) throws SQLException {
    return requireValue(r.getObject(name, Long.class));
  }

  private static Instant time(ResultSet r, String name) throws SQLException {
    return requireValue(r.getObject(name, OffsetDateTime.class))
        .toInstant()
        .truncatedTo(ChronoUnit.MILLIS);
  }

  private static Optional<Instant> optionalTime(ResultSet r, String name) throws SQLException {
    return Optional.ofNullable(r.getObject(name, OffsetDateTime.class))
        .map(v -> v.toInstant().truncatedTo(ChronoUnit.MILLIS));
  }

  private static void bind(PreparedStatement s, List<? extends Optional<?>> parameters)
      throws SQLException {
    for (int i = 0; i < parameters.size(); i++) s.setObject(i + 1, parameters.get(i).orElse(null));
  }

  private static void requireRead(Connection c) throws SQLException {
    require(!c.getAutoCommit() && c.isReadOnly());
  }

  private static void boundary(Connection c, AuthenticatedActor actor, PayloadData request) {
    Objects.requireNonNull(c, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(request, "request");
  }

  private static void validateRequest(String layout, PayloadData request) {
    PayloadCodec.standard()
        .encode(
            PayloadTypeCatalog.encode(
                new TypedPayloadValues(new LayoutId(layout), request, List.of())),
            false);
  }

  private static TypedPayloadValues validate(TypedPayloadValues values) {
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false);
    return values;
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("question query result is inconsistent");
  }

  @FunctionalInterface
  private interface RowMapper<T> {
    T read(ResultSet r) throws SQLException;
  }
}
