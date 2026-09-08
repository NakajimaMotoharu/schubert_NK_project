package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.api.database.RequiredColumn;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.media.*;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.IntFunction;

/**
 * Stored media menu/list queries, never filesystem enumeration or pair inference. Caller owns a
 * read-only transaction and supplies an API-verified actor. No commit/connection close or idle
 * update. NK-MED-001; FUN-006/007/AUT-001..004; UI223/235; SS312/332 §4.3/333; PG-D-071;
 * PT-MED-008..014. Descriptor/manifest/physical verification and final authentication are separate.
 */
public final class MediaRepository {
  /** PT-MED-008: count each stored VIDEO category once; reject unknown or duplicate opening. */
  public TypedPayloadValues animationMenu(Connection connection, AuthenticatedActor actor) {
    return query(
        connection,
        actor,
        """
        select count(*) filter(where category in ('MAIN','SUBTRACK')) as main_count,
               count(*) filter(where category='OVA') as ova_count,
               count(*) filter(where category='OPENING') as opening_count,
               count(*) filter(where category not in ('MAIN','SUBTRACK','OVA','OPENING')) as unknown_count,
               count(*) as total_count
          from schubert.media_assets where media_type='VIDEO'
        """,
        List.of(),
        1,
        r -> {
          if (number(r, "unknown_count") != 0 || number(r, "opening_count") > 1)
            throw new MediaQueryException(false);
          return new AnimationMenuResponseData(
              bounded(r, "main_count", 999),
              bounded(r, "ova_count", 999),
              bounded(r, "opening_count", 1) == 1,
              bounded(r, "total_count", 999));
        },
        rows -> {
          if (rows.size() != 1) throw new MediaQueryException(false);
          return payload("ANMRSP01", rows.getFirst(), List.of());
        });
  }

  /** PT-MED-009: MAIN includes SUBTRACK; the parent must actually be a stored MAIN video. */
  public TypedPayloadValues animationList(
      Connection connection, AuthenticatedActor actor, AnimationListRequestData request) {
    input("ANLREQ01", request);
    String category = request.category().wireValue();
    return rows(
        connection,
        actor,
        """
        select m.logical_id,m.title,m.category,m.display_path,m.byte_size,m.parent_logical_id,
               m.display_order,p.logical_id as verified_parent
          from schubert.media_assets m
          left join schubert.media_assets p on p.logical_id=m.parent_logical_id
               and p.media_type='VIDEO' and p.category='MAIN'
         where m.media_type='VIDEO' and (m.category=? or (?='MAIN' and m.category='SUBTRACK'))
         order by m.display_order,m.logical_id collate "C" limit 51
        """,
        List.of(category, category),
        "ANLRSP01",
        50,
        AnimationListResponseData::new,
        r -> {
          var kind = AnimationCategory.valueOf(text(r, "category"));
          if (kind == AnimationCategory.SUBTRACK && r.getString("verified_parent") == null)
            throw new SQLException("invalid animation parent metadata");
          return new AnimationRecord(
              text(r, "logical_id"),
              text(r, "title"),
              kind,
              DisplayPath.of(text(r, "display_path")),
              number(r, "byte_size"),
              Optional.ofNullable(r.getString("parent_logical_id")),
              integer(r, "display_order"));
        });
  }

  /** PT-MED-010: UI223 explicit category rank, then code-point name order. */
  public TypedPayloadValues musicCategories(Connection connection, AuthenticatedActor actor) {
    return rows(
        connection,
        actor,
        """
        select category,count(*) as track_count from schubert.media_assets where media_type='MUSIC'
         group by category
         order by case category when '曲' then 0 when 'BGM' then 1 else 2 end,
                  category collate "C" limit 21
        """,
        List.of(),
        "MCTRSP01",
        20,
        MusicCategoryResponseData::new,
        r -> new MusicCategoryRecord(text(r, "category"), bounded(r, "track_count", 999999)));
  }

  /** PT-MED-010: exact category bind; no SQL interpolation, normalization or filesystem scan. */
  public TypedPayloadValues musicSections(
      Connection connection, AuthenticatedActor actor, MusicSectionRequestData request) {
    input("MCSREQ01", request);
    return rows(
        connection,
        actor,
        """
        select section,count(*) as track_count from schubert.media_assets
         where media_type='MUSIC' and category=? group by section
         order by case section when 'ゲーム' then 0 when 'アニメ' then 1
                  when 'キャラクターソング' then 2 else 3 end, section collate "C" limit 101
        """,
        List.of(request.category()),
        "MCSRSP01",
        100,
        MusicSectionResponseData::new,
        r -> new MusicSectionRecord(text(r, "section"), bounded(r, "track_count", 999999)));
  }

  /** PT-MED-011: stored pair and order are authoritative; no title-based inference at request. */
  public TypedPayloadValues musicTracks(
      Connection connection, AuthenticatedActor actor, MusicTrackRequestData request) {
    input("MTRREQ01", request);
    return rows(
        connection,
        actor,
        """
        select logical_id,title,category,section,display_path,byte_size,pair_key,pair_role,display_order
          from schubert.media_assets where media_type='MUSIC' and category=? and section=?
         order by display_order,logical_id collate "C" limit 201
        """,
        List.of(request.category(), request.section()),
        "MTRRSP01",
        200,
        MusicTrackResponseData::new,
        r ->
            new MusicTrackRecord(
                text(r, "logical_id"),
                text(r, "title"),
                text(r, "category"),
                text(r, "section"),
                DisplayPath.of(text(r, "display_path")),
                number(r, "byte_size"),
                Optional.ofNullable(r.getString("pair_key")),
                pairRole(text(r, "pair_role")),
                integer(r, "display_order")));
  }

  private static TypedPayloadValues rows(
      Connection connection,
      AuthenticatedActor actor,
      String sql,
      List<String> parameters,
      String layout,
      int maximum,
      IntFunction<PayloadData> data,
      RowMapper<PayloadRecord> mapper) {
    return query(
        connection,
        actor,
        sql,
        parameters,
        maximum,
        mapper,
        rows -> payload(layout, data.apply(rows.size()), rows));
  }

  private static <R> TypedPayloadValues query(
      Connection connection,
      AuthenticatedActor actor,
      String sql,
      List<String> parameters,
      int maximum,
      RowMapper<R> mapper,
      Function<List<R>, TypedPayloadValues> finish) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    try {
      if (connection.getAutoCommit() || !connection.isReadOnly())
        throw new SQLException("read-only media transaction required");
      List<R> records = new ArrayList<>();
      try (PreparedStatement statement = connection.prepareStatement(sql)) {
        for (int index = 0; index < parameters.size(); index++)
          statement.setString(index + 1, parameters.get(index));
        try (ResultSet result = statement.executeQuery()) {
          while (result.next()) {
            if (records.size() == maximum) throw new MediaQueryException(true);
            records.add(mapper.read(result));
          }
        }
      }
      return finish.apply(List.copyOf(records));
    } catch (MediaQueryException failure) {
      throw new MediaQueryException(
          failure.resultCode() == ResultCode.RESOURCE_LIMIT && failure.getSuppressed().length == 0);
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException failure) {
      throw new MediaQueryException(false);
    }
  }

  private static void input(String layout, PayloadData request) {
    Objects.requireNonNull(request, "request");
    payload(layout, request, List.of());
  }

  private static TypedPayloadValues payload(
      String layout, PayloadData data, List<? extends PayloadRecord> records) {
    var value = new TypedPayloadValues(new LayoutId(layout), data, List.copyOf(records));
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(value), false);
    return value;
  }

  private static String text(ResultSet result, String column) throws SQLException {
    return RequiredColumn.requireValue(result.getString(column));
  }

  private static long number(ResultSet result, String column) throws SQLException {
    long value = result.getLong(column);
    if (result.wasNull()) throw new SQLException("required media numeric metadata is missing");
    return value;
  }

  private static int integer(ResultSet result, String column) throws SQLException {
    return Math.toIntExact(number(result, column));
  }

  private static int bounded(ResultSet result, String column, int maximum) throws SQLException {
    long value = number(result, column);
    if (value < 0) throw new SQLException("media count is negative");
    if (value > maximum) throw new MediaQueryException(true);
    return (int) value;
  }

  private static PairRole pairRole(String value) throws SQLException {
    return switch (value) {
      case "M" -> PairRole.MAIN;
      case "I" -> PairRole.INSTRUMENTAL;
      case "N" -> PairRole.NONE;
      default -> throw new SQLException("unknown stored pair role");
    };
  }

  @FunctionalInterface
  private interface RowMapper<R> {
    R read(ResultSet result) throws SQLException;
  }
}
