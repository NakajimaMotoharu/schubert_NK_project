package dev.codex.schubert.nk.api.persistence;

import static dev.codex.schubert.nk.api.error.TemporaryInfrastructureException.preserveFatal;
// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationService;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRecord;
import dev.codex.schubert.nk.protocol.layout.admin.UserSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserState;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.Normalizer;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * ADMIN-only projection from a caller-owned read-only transaction and API-verified actor.
 * NK-ADM-001; FUN-009/AUT-002/003/DAT-003; UI225/236/241; SS312/323/331/332;
 * PG-D-081/PT-ADM-001..007. Never selects credentials, commits, updates or closes the connection.
 * Current authentication and Inbox orchestration must precede registration.
 */
public final class UserQueryRepository {
  private static final int MAXIMUM_PAGED_TOTAL_RECORDS = 49_999_950;

  private static final String PROJECTION =
      """
      with projected as (
        select u.id,u.username,u.role,u.locked_until,u.last_login_at,u.created_at,u.updated_at,
               u.version,
               case when u.status='DISABLED' then 'DISABLED'
                    when u.status='ACTIVE' and u.locked_until > ? then 'LOCKED'
                    when u.status='ACTIVE' then 'ACTIVE' else 'INVALID' end as state
          from schubert.app_users u
      )
      """;

  /** PT-ADM-001/003..007: literal prefix, fixed 50 rows, count and page in one SQL snapshot. */
  public TypedPayloadValues search(
      Connection connection, AuthenticatedActor actor, UserSearchRequestData request, Instant now) {
    requireBoundary(connection, actor, now);
    Objects.requireNonNull(request, "request");
    request =
        new UserSearchRequestData(
            request
                .usernamePrefix()
                .map(s -> Normalizer.normalize(s, Normalizer.Form.NFC).trim())
                .filter(s -> !s.isEmpty()),
            request.role(),
            request.state(),
            request.page(),
            request.pageSize());
    validate(new TypedPayloadValues(new LayoutId("USRREQ01"), request, List.of()));
    List<String> filters = new ArrayList<>();
    List<String> parameters = new ArrayList<>();
    request
        .usernamePrefix()
        .ifPresent(
            value -> {
              filters.add("username ilike ? escape '\\'");
              parameters.add(
                  value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%");
            });
    request
        .role()
        .ifPresent(
            value -> {
              filters.add("role=?");
              parameters.add(value.wireValue());
            });
    request
        .state()
        .ifPresent(
            value -> {
              filters.add("state=?");
              parameters.add(value.wireValue());
            });
    String predicate = filters.isEmpty() ? "" : " where " + String.join(" and ", filters);
    String sql =
        PROJECTION
            + ", filtered as materialized (select id,username from projected"
            + predicate
            + ")"
            + """
        , totals as (select count(*) as total from filtered), page as (
          select total,greatest(1,(total+49)/50) as pages,
                 least(cast(? as bigint),greatest(1,(total+49)/50)) as effective from totals)
        select p.total,p.pages,p.effective,x.id,x.username,x.role,x.state,x.locked_until,
               x.last_login_at,x.created_at,x.updated_at,x.version
          from page p left join lateral (
            select u.id,u.username,u.role,u.state,u.locked_until,u.last_login_at,u.created_at,
                   u.updated_at,u.version
              from (select id,username from filtered order by username collate "C",id
                    limit 50 offset (p.effective-1)*50) z
              join projected u on u.id=z.id
          ) x on true order by x.username collate "C",x.id
        """;
    try {
      requireReadTransaction(connection);
      try (PreparedStatement statement = connection.prepareStatement(sql)) {
        statement.setObject(1, now.atOffset(java.time.ZoneOffset.UTC));
        for (int i = 0; i < parameters.size(); i++) statement.setString(i + 2, parameters.get(i));
        statement.setInt(parameters.size() + 2, request.page());
        try (ResultSet result = statement.executeQuery()) {
          require(result.next());
          long total = number(result, "total");
          if (total > MAXIMUM_PAGED_TOTAL_RECORDS) throw new UserQueryException(true);
          int pages = Math.toIntExact(number(result, "pages"));
          int effective = Math.toIntExact(number(result, "effective"));
          require(
              total >= 0
                  && pages == Math.max(1, (total + 49) / 50)
                  && effective == Math.min(request.page(), pages));
          List<PayloadRecord> records = new ArrayList<>();
          do {
            require(
                total == number(result, "total")
                    && pages == number(result, "pages")
                    && effective == number(result, "effective"));
            if (result.getObject("id") != null) records.add(record(result));
          } while (result.next());
          long first = total == 0 ? 0 : ((long) effective - 1) * 50 + 1;
          long last = Math.min((long) effective * 50, total);
          require(records.size() == (total == 0 ? 0 : last - first + 1));
          return validate(
              new TypedPayloadValues(
                  new LayoutId("USRRSP01"),
                  new PagedResponseData(effective, 50, total, pages, first, last),
                  records));
        }
      }
    } catch (UserQueryException failure) {
      preserveFatal(failure);
      throw new UserQueryException(failure.getSuppressed().length == 0);
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException
        | java.time.DateTimeException failure) {
      preserveFatal(failure);
      throw new UserQueryException(false);
    }
  }

  /** PT-ADM-002..005/007: no row is absence; corrupt rows and I/O are never absence. */
  public Optional<TypedPayloadValues> detail(
      Connection connection, AuthenticatedActor actor, UserDetailRequestData request, Instant now) {
    requireBoundary(connection, actor, now);
    Objects.requireNonNull(request, "request");
    try {
      requireReadTransaction(connection);
      try (PreparedStatement statement =
          connection.prepareStatement(
              PROJECTION
                  + """
          select p.id,p.username,p.role,p.state,p.locked_until,p.last_login_at,p.created_at,
                 p.updated_at,p.version,u.password_changed_at,
                 case when u.created_by is null then 'SYSTEM' else c.username end as created_by_name,
                 case when u.updated_by is null then 'SYSTEM' else b.username end as updated_by_name,
                 (select count(*) from schubert.auth_sessions s
                   where s.user_id=p.id and s.revoked=false and s.expires_at > ?) as active_sessions
            from projected p join schubert.app_users u on u.id=p.id
            left join schubert.app_users c on c.id=u.created_by
            left join schubert.app_users b on b.id=u.updated_by
           where p.id=?
          """)) {
        statement.setObject(1, now.atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(2, now.atOffset(java.time.ZoneOffset.UTC));
        statement.setLong(3, request.userId().value());
        try (ResultSet result = statement.executeQuery()) {
          Optional<TypedPayloadValues> found = Optional.empty();
          if (result.next()) {
            var user = record(result);
            int active = Math.toIntExact(number(result, "active_sessions"));
            require(active >= 0 && active <= 2);
            var detail =
                new UserDetailResponseData(
                    user.userId(),
                    user.username(),
                    user.role(),
                    user.state(),
                    user.lockedUntil(),
                    user.lastLogin(),
                    requiredTime(result, "password_changed_at"),
                    user.createdAt(),
                    user.updatedAt(),
                    active,
                    user.version(),
                    text(result, "created_by_name"),
                    text(result, "updated_by_name"));
            require(!result.next());
            found =
                Optional.of(
                    validate(new TypedPayloadValues(new LayoutId("UDTRSP01"), detail, List.of())));
          }
          return found;
        }
      }
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException
        | java.time.DateTimeException failure) {
      preserveFatal(failure);
      throw new UserQueryException(false);
    }
  }

  private static UserRecord record(ResultSet result) throws SQLException {
    return new UserRecord(
        new UserId(number(result, "id")),
        text(result, "username"),
        UserRole.valueOf(text(result, "role")),
        UserState.valueOf(text(result, "state")),
        optionalTime(result, "locked_until"),
        optionalTime(result, "last_login_at"),
        requiredTime(result, "created_at"),
        requiredTime(result, "updated_at"),
        number(result, "version"));
  }

  private static void requireBoundary(
      Connection connection, AuthenticatedActor actor, Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(now, "now");
    new AuthorizationService().requireAdmin(actor);
  }

  private static void requireReadTransaction(Connection connection) throws SQLException {
    require(!connection.getAutoCommit() && connection.isReadOnly());
  }

  private static long number(ResultSet result, String column) throws SQLException {
    long value = result.getLong(column);
    require(!result.wasNull());
    return value;
  }

  private static String text(ResultSet result, String column) throws SQLException {
    String value = result.getString(column);
    if (value == null) throw new SQLException("required user text is missing");
    return value;
  }

  private static Optional<Instant> optionalTime(ResultSet result, String column)
      throws SQLException {
    java.time.OffsetDateTime value = result.getObject(column, java.time.OffsetDateTime.class);
    // BUG641/YKT454: DB comparisons retain microseconds; only this wire projection is millis.
    return value == null
        ? Optional.empty()
        : Optional.of(value.toInstant().truncatedTo(java.time.temporal.ChronoUnit.MILLIS));
  }

  private static Instant requiredTime(ResultSet result, String column) throws SQLException {
    return optionalTime(result, column)
        .orElseThrow(() -> new SQLException("required user time is missing"));
  }

  private static TypedPayloadValues validate(TypedPayloadValues value) {
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(value), false);
    return value;
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("user query invariant failed");
  }
}
