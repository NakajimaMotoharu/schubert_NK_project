package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.api.database.RequiredColumn;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationRecord;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MediaDescriptorData;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicCategoryResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.MediaMimeType;
import dev.codex.schubert.nk.protocol.layout.semantic.PairRole;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.VideoCategory;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.IntFunction;

/**
 * Stored media menu/list queries, never filesystem enumeration or pair inference. Caller owns a
 * read-only transaction and supplies an API-verified actor. No commit/connection close or idle
 * update. NK-MED-001; FUN-006/007/AUT-001..004; UI223/235; SS312/332 §4.3/333; PG-D-071;
 * PT-MED-008..017. Manifest/physical verification and final authentication are separate; metadata
 * projections alone must never authorize a file response.
 */
public final class MediaRepository {
  private static final int EXPECTED_RESULT_ROWS = 1;

  private static final java.lang.String LITERAL_CATEGORY = "category";

  /** PT-MED-015/017: canonical N12 identity and SS333 Audio OGG mapping, not file admission. */
  public Optional<TypedPayloadValues> audioMetadata(
      Connection connection, AuthenticatedActor actor, AudioDescriptorRequestData request) {
    input("AUDREQ01", request);
    String id = Long.toString(request.audioId().value());
    return metadata(
        connection,
        actor,
        """
        select id::text as logical_id,storage_relative_path,file_name,byte_size,sha256,
               'audio/ogg' as mime_type from schubert.audio_files where id=cast(? as bigint)
        """,
        id,
        "AUDRSP01",
        r -> descriptor(r, MediaType.AUDIO, id, request.disposition()));
  }

  /** PT-MED-015/017: logical ID and MUSIC type are both scoped in the prepared lookup. */
  public Optional<TypedPayloadValues> musicMetadata(
      Connection connection, AuthenticatedActor actor, MusicDescriptorRequestData request) {
    input("MEDREQ01", request);
    return metadata(
        connection,
        actor,
        """
        select logical_id,storage_relative_path,file_name,byte_size,sha256,mime_type
          from schubert.media_assets where logical_id=? and media_type='MUSIC'
        """,
        request.trackId(),
        "MEDRSP01",
        r -> descriptor(r, MediaType.MUSIC, request.trackId(), request.disposition()));
  }

  /** PT-MED-016/017: includes standalone OPENING display metadata and fixes inline disposition. */
  public Optional<TypedPayloadValues> videoMetadata(
      Connection connection, AuthenticatedActor actor, VideoDescriptorRequestData request) {
    input("VIDREQ01", request);
    return metadata(
        connection,
        actor,
        """
        select logical_id,storage_relative_path,file_name,byte_size,sha256,mime_type,title,category,display_path
          from schubert.media_assets where logical_id=? and media_type='VIDEO'
        """,
        request.videoId(),
        "VIDRSP01",
        r -> {
          var base = descriptor(r, MediaType.VIDEO, request.videoId(), ContentDisposition.INLINE);
          return new VideoDescriptorResponseData(
              base.mediaLogicalId(),
              base.storageRelativePath(),
              base.fileName(),
              base.fileByteLength(),
              base.sha256(),
              base.mimeType(),
              base.contentDisposition(),
              text(r, "title"),
              VideoCategory.valueOf(text(r, LITERAL_CATEGORY)),
              DisplayPath.of(text(r, "display_path")));
        });
  }

  private static Optional<TypedPayloadValues> metadata(
      Connection connection,
      AuthenticatedActor actor,
      String sql,
      String id,
      String layout,
      RowMapper<PayloadData> mapper) {
    return query(
        connection,
        actor,
        sql,
        List.of(id),
        1,
        mapper,
        rows ->
            rows.isEmpty()
                ? Optional.empty()
                : Optional.of(payload(layout, rows.getFirst(), List.of())));
  }

  private static MediaDescriptorData descriptor(
      ResultSet result, MediaType type, String expectedId, ContentDisposition disposition)
      throws SQLException {
    String id = text(result, "logical_id");
    if (!id.equals(expectedId)) throw new SQLException("media identity differs from lookup");
    var checked =
        new MediaDescriptor(
            type,
            id,
            text(result, "storage_relative_path"),
            text(result, "file_name"),
            number(result, "byte_size"),
            text(result, "sha256"),
            text(result, "mime_type"),
            dev.codex.schubert.nk.protocol.file.ContentDisposition.valueOf(disposition.name()));
    return new MediaDescriptorData(
        checked.logicalId(),
        RelativePath.of(checked.storageRelativePath()),
        checked.fileName(),
        checked.byteLength(),
        Sha256Hex.of(checked.sha256()),
        MediaMimeType.valueOf(checked.mimeType().toUpperCase(Locale.ROOT).replace('/', '_')),
        disposition);
  }

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
          if (rows.size() != EXPECTED_RESULT_ROWS) throw new MediaQueryException(false);
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
          var kind = AnimationCategory.valueOf(text(r, LITERAL_CATEGORY));
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
        r -> new MusicCategoryRecord(text(r, LITERAL_CATEGORY), bounded(r, "track_count", 999999)));
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
                text(r, LITERAL_CATEGORY),
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

  private static <R, T> T query(
      Connection connection,
      AuthenticatedActor actor,
      String sql,
      List<String> parameters,
      int maximum,
      RowMapper<R> mapper,
      Function<List<R>, T> finish) {
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
