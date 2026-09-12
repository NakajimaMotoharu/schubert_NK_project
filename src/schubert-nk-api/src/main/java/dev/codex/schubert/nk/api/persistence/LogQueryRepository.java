package dev.codex.schubert.nk.api.persistence;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationService;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.log.*;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.Normalizer;
import java.time.temporal.ChronoUnit;
import java.util.*;

/**
 * One-statement ADMIN Log projection from caller-owned read-only transaction.
 * NK-ADM-001/FUN-008/AUT-002/003/MON; UI225 §2/235 §11/241; SS311/312/323/331/332/351;
 * SSC-036/PG-D-090/PT-ADM-055..060. No authentication grant, DB mutation, transaction ownership,
 * raw query or secret projection.
 */
public final class LogQueryRepository {
  private static final String COLUMNS =
      "id,logged_at,category,level,action,message,request_id,message_id,correlation_id,http_method,request_uri,status_code,duration_ms,remote_address,details";

  public TypedPayloadValues search(
      Connection connection, AuthenticatedActor actor, LogSearchRequestData request) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(request, "request");
    new AuthorizationService().requireAdmin(actor);
    validate(new TypedPayloadValues(new LayoutId("LGSREQ01"), request, List.of()));
    List<String> predicates = new ArrayList<>(List.of("level in ('INFO','WARN','ERROR')"));
    List<Object> parameters = new ArrayList<>();
    clean(request.keyword())
        .ifPresent(
            value -> {
              predicates.add("(message ilike ? escape '\\' or details::text ilike ? escape '\\')");
              String pattern = pattern(value);
              parameters.add(pattern);
              parameters.add(pattern);
            });
    request
        .logType()
        .ifPresent(
            value -> {
              predicates.add("category=?");
              parameters.add(value.wireValue());
            });
    clean(request.action())
        .ifPresent(
            value -> {
              predicates.add("action=?");
              parameters.add(value);
            });
    clean(request.path())
        .ifPresent(
            value -> {
              predicates.add("request_uri ilike ? escape '\\'");
              parameters.add(pattern(value));
            });
    request
        .level()
        .ifPresent(
            value -> {
              predicates.add("level=?");
              parameters.add(value.wireValue());
            });
    request
        .fromAt()
        .ifPresent(
            value -> {
              predicates.add("logged_at>=?");
              parameters.add(value.atOffset(java.time.ZoneOffset.UTC));
            });
    request
        .toAt()
        .ifPresent(
            value -> {
              predicates.add("logged_at<=?");
              parameters.add(value.atOffset(java.time.ZoneOffset.UTC));
            });
    String sql =
        "with filtered as materialized (select "
            + COLUMNS
            + " from schubert.app_logs where "
            + String.join(" and ", predicates)
            + ")"
            + """
        , totals as (select count(*) as total from filtered), page as (
          select total,greatest(1,(total+99)/100) as pages,
                 least(cast(? as bigint),greatest(1,(total+99)/100)) as effective from totals)
        select p.total,p.pages,p.effective,x.id,x.logged_at,x.category,x.level,x.action,x.message,
               x.request_id,x.message_id,x.correlation_id,x.http_method,x.request_uri,x.status_code,
               x.duration_ms,host(x.remote_address) as remote_address,x.details::text as details
          from page p left join lateral (
            select id,logged_at,category,level,action,message,request_id,message_id,correlation_id,
                   http_method,request_uri,status_code,duration_ms,remote_address,details
              from filtered order by logged_at desc,id desc
             limit 100 offset (p.effective-1)*100
          ) x on true order by x.logged_at desc,x.id desc
        """;
    try {
      require(!connection.getAutoCommit() && connection.isReadOnly());
      TypedPayloadValues response;
      try (var statement = connection.prepareStatement(sql)) {
        for (int i = 0; i < parameters.size(); i++) statement.setObject(i + 1, parameters.get(i));
        statement.setInt(parameters.size() + 1, request.page());
        try (var rows = statement.executeQuery()) {
          require(rows.next());
          long total = number(rows, "total");
          if (total > 99999900) throw new LogQueryException(true);
          int pages = Math.toIntExact(number(rows, "pages")),
              effective = Math.toIntExact(number(rows, "effective"));
          require(
              total >= 0
                  && pages == Math.max(1, (total + 99) / 100)
                  && effective == Math.min(request.page(), pages));
          List<PayloadRecord> records = new ArrayList<>();
          do {
            require(
                total == number(rows, "total")
                    && pages == number(rows, "pages")
                    && effective == number(rows, "effective"));
            if (rows.getObject("id") != null) records.add(record(rows));
          } while (rows.next());
          long first = total == 0 ? 0 : (effective - 1L) * 100 + 1,
              last = Math.min(effective * 100L, total);
          require(records.size() == (total == 0 ? 0 : last - first + 1));
          response =
              validate(
                  new TypedPayloadValues(
                      new LayoutId("LGSRSP01"),
                      new PagedResponseData(effective, 100, total, pages, first, last),
                      records));
        }
      }
      return response;
    } catch (LogQueryException failure) {
      throw new LogQueryException(failure.getSuppressed().length == 0);
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException failure) {
      throw new LogQueryException(false);
    }
  }

  private static LogRecord record(ResultSet row) throws SQLException {
    return new LogRecord(
        new LogId(number(row, "id")),
        requireValue(row.getObject("logged_at", java.time.OffsetDateTime.class))
            .toInstant()
            .truncatedTo(ChronoUnit.MILLIS),
        LogType.valueOf(requireValue(row.getString("category"))),
        LogLevel.valueOf(requireValue(row.getString("level"))),
        Optional.of(requireValue(row.getString("action"))),
        requireValue(row.getString("message")),
        Optional.ofNullable(row.getObject("request_id", UUID.class)),
        Optional.ofNullable(row.getObject("message_id", UUID.class)),
        Optional.ofNullable(row.getObject("correlation_id", UUID.class)),
        Optional.ofNullable(row.getString("http_method")),
        Optional.ofNullable(row.getString("request_uri")),
        Optional.ofNullable(row.getObject("status_code", Integer.class)).map(HttpStatusCode::new),
        Optional.ofNullable(row.getObject("duration_ms", Long.class))
            .map(value -> new ElapsedMilliseconds(Math.toIntExact(value))),
        Optional.ofNullable(row.getString("remote_address")),
        Optional.of(requireValue(row.getString("details"))));
  }

  private static Optional<String> clean(Optional<String> value) {
    return value
        .map(s -> Normalizer.normalize(s, Normalizer.Form.NFC).trim())
        .filter(s -> !s.isEmpty());
  }

  private static String pattern(String value) {
    return "%" + value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%";
  }

  private static long number(ResultSet row, String name) throws SQLException {
    long value = row.getLong(name);
    require(!row.wasNull());
    return value;
  }

  private static TypedPayloadValues validate(TypedPayloadValues value) {
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(value), false);
    return value;
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("log projection is inconsistent");
  }
}
