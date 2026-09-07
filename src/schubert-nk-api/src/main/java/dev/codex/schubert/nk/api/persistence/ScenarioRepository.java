package dev.codex.schubert.nk.api.persistence;

import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.*;
import dev.codex.schubert.nk.protocol.layout.semantic.*;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.Normalizer;
import java.util.*;
import java.util.function.IntFunction;

/**
 * Caller-owned, read-only queries; actor must come from the API verifier, never request identity.
 * No commit, connection close, idle extension or file I/O. SQL/row and wire invariants are checked
 * before returning an immutable projection. Trace: NK-SCN-001, FUN-003/004, AUT-001/003; UI223/234;
 * SS311/312/332, SSC-017; PT-SCN-001..007. Authentication/Inbox service connects this repository
 * later.
 */
public final class ScenarioRepository {
  private static final String FROM =
      """
       from schubert.script_entries e
       join schubert.script_files f on f.id=e.script_file_id
       join schubert.games g on g.id=e.game_id
       left join schubert.speakers s on s.id=e.speaker_id
      """;
  private static final String VOICE =
      """
      exists (select 1 from schubert.entry_audio_links v
               where v.entry_id=e.id and v.link_type='voice')
      """;
  private static final Map<Integer, String> FIRST_ROUTES =
      Map.of(1, "共通ルート", 2, "奈々瀬ルート", 3, "ヒナミルート", 4, "美岬ルート", 5, "文乃ルート");
  private static final Map<Integer, String> SECOND_ROUTES =
      Map.ofEntries(
          Map.entry(1, "共通ルート"),
          Map.entry(2, "共通ルート"),
          Map.entry(3, "桐香ルート"),
          Map.entry(4, "礼ルート"),
          Map.entry(5, "郁子ルート"),
          Map.entry(6, "麻沙音ルート"),
          Map.entry(7, "奈々瀬ルート"),
          Map.entry(8, "ヒナミルート"),
          Map.entry(9, "美岬ルート"),
          Map.entry(10, "文乃ルート"),
          Map.entry(12, "スス子ルート"));

  /** PT-SCN-001: immutable game projection in display order, including zero rows. */
  public TypedPayloadValues games(Connection connection, AuthenticatedActor actor) {
    return rows(
        connection,
        actor,
        "select code,title,display_order from schubert.games order by display_order,id limit 11",
        List.of(),
        "GAMRSP01",
        10,
        GameListResponseData::new,
        r ->
            new GameRecord(
                game(required(r, "code")), required(r, "title"), integer(r, "display_order")));
  }

  /** PT-SCN-002: same-name aggregation across the selected games, not per-ID duplicates. */
  public TypedPayloadValues speakers(
      Connection connection, AuthenticatedActor actor, SpeakerListRequestData request) {
    Objects.requireNonNull(request, "request");
    List<String> parameters = request.gameCode().map(g -> List.of(g.wireValue())).orElse(List.of());
    String filter = parameters.isEmpty() ? "" : " where g.code=?";
    return rows(
        connection,
        actor,
        """
        select min(s.id) as id,s.name,count(e.id) as occurrences
          from schubert.speakers s join schubert.games g on g.id=s.game_id
          join schubert.script_entries e on e.speaker_id=s.id
        """
            + filter
            + " group by s.name order by count(e.id) desc,s.name limit 501",
        parameters,
        "SPKRSP01",
        500,
        SpeakerListResponseData::new,
        r ->
            new SpeakerRecord(
                new SpeakerId(number(r, "id")), required(r, "name"), number(r, "occurrences")));
  }

  /** PT-SCN-003: two-digit prefix; no synthetic prefix for missing/invalid master metadata. */
  public TypedPayloadValues routes(
      Connection connection, AuthenticatedActor actor, RouteListRequestData request) {
    Objects.requireNonNull(request, "request");
    return rows(
        connection,
        actor,
        """
        select left(f.section_code,2) as prefix,count(*) as files
          from schubert.script_files f join schubert.games g on g.id=f.game_id
         where g.code=? group by left(f.section_code,2) order by prefix limit 51
        """,
        List.of(request.gameCode().wireValue()),
        "RTERSP01",
        50,
        RouteListResponseData::new,
        r -> {
          String prefix = required(r, "prefix");
          if (!prefix.matches("[0-9]{2}")) throw new SQLException("invalid route metadata");
          int value = Integer.parseInt(prefix);
          return new RouteRecord(value, routeName(request.gameCode(), value), integer(r, "files"));
        });
  }

  /** PT-SCN-004: display order and first nonempty title, count entries before any audio join. */
  public TypedPayloadValues files(
      Connection connection, AuthenticatedActor actor, ScenarioFileListRequestData request) {
    Objects.requireNonNull(request, "request");
    return rows(
        connection,
        actor,
        """
        select f.id,f.chapter_title,f.section_code,f.file_name,f.display_path,count(e.id) as entries
          from schubert.script_files f join schubert.games g on g.id=f.game_id
          left join schubert.script_entries e on e.script_file_id=f.id
         where g.code=? and left(f.section_code,2)=?
         group by f.id order by f.display_order,f.id limit 501
        """,
        List.of(
            request.gameCode().wireValue(), String.format(Locale.ROOT, "%02d", request.prefix())),
        "SCFRSP01",
        500,
        n ->
            new ScenarioFileListResponseData(
                request.gameCode(),
                request.prefix(),
                routeName(request.gameCode(), request.prefix()),
                n),
        r ->
            new ScenarioFileRecord(
                new ScriptFileId(number(r, "id")),
                title(r, ""),
                DisplayPath.of(required(r, "display_path")),
                integer(r, "entries")));
  }

  /** PT-SCN-005/006: one statement snapshot for six predicates, count, corrected page and rows. */
  public TypedPayloadValues search(
      Connection connection, AuthenticatedActor actor, ScenarioSearchRequestData request) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(request, "request");
    // BUG-032: UI223 normalization precedes wire-size/padding checks; receiver codec stays strict.
    request =
        new ScenarioSearchRequestData(
            text(request.bodyKeyword()),
            request.gameCode(),
            text(request.speakerName()),
            text(request.chapterTitle()),
            request.entryType(),
            request.voiceCondition(),
            request.page(),
            request.pageSize());
    // Validate the request wire contract before any database access. Web page normalization is
    // separate.
    validate(new TypedPayloadValues(new LayoutId("SRCREQ01"), request, List.of()));
    List<String> filters = new ArrayList<>(), parameters = new ArrayList<>();
    add(
        filters,
        parameters,
        "e.body_search like ?",
        text(request.bodyKeyword()).map(s -> "%" + s.toLowerCase(Locale.ROOT) + "%"));
    add(filters, parameters, "g.code=?", request.gameCode().map(GameCode::wireValue));
    add(filters, parameters, "s.name=?", text(request.speakerName()));
    add(
        filters,
        parameters,
        "f.chapter_title ilike ?",
        text(request.chapterTitle()).map(s -> "%" + s + "%"));
    add(filters, parameters, "e.entry_type=?", request.entryType().map(EntryType::wireValue));
    request
        .voiceCondition()
        .ifPresent(v -> filters.add(v == VoiceCondition.PRESENT ? VOICE : "not " + VOICE));
    String predicate = filters.isEmpty() ? "" : " where " + String.join(" and ", filters);
    String sql =
        """
        with filtered as materialized (
          select e.id,e.display_order
        """
            + FROM
            + predicate
            + """
        ), totals as (select count(*) as total from filtered), page as (
          select total,greatest(1,(total+99)/100) as pages,
                 least(cast(? as bigint),greatest(1,(total+99)/100)) as effective from totals)
        select p.total,p.pages,p.effective,x.id,x.script_file_id,x.code,x.chapter_title,
               x.line_number,x.entry_type,x.speaker_name,x.body,x.display_path,
               a.audio_file_id,a.audio_path
          from page p left join lateral (
            select z.id,e.script_file_id,g.code,f.chapter_title,e.line_number,e.entry_type,
                   sp.name as speaker_name,e.body,f.display_path,z.display_order
              from (select id,display_order from filtered order by display_order,id
                    limit 100 offset (p.effective-1)*100) z
              join schubert.script_entries e on e.id=z.id
              join schubert.script_files f on f.id=e.script_file_id
              join schubert.games g on g.id=e.game_id
              left join schubert.speakers sp on sp.id=e.speaker_id
          ) x on true left join lateral (
            select l.audio_file_id,af.display_path as audio_path
              from schubert.entry_audio_links l join schubert.audio_files af on af.id=l.audio_file_id
             where l.entry_id=x.id and l.link_type='voice'
             order by l.display_order,l.audio_file_id limit 1
          ) a on true order by x.display_order,x.id
        """;
    parameters.add(Integer.toString(request.page()));
    try {
      requireReadTransaction(connection);
      try (PreparedStatement statement = connection.prepareStatement(sql)) {
        bind(statement, parameters);
        try (ResultSet result = statement.executeQuery()) {
          if (!result.next()) throw new SQLException("missing page aggregate");
          long total = number(result, "total");
          if (total > 99_999_900) throw new ScenarioQueryException(true);
          int effective = integer(result, "effective"), pages = integer(result, "pages");
          List<PayloadRecord> records = new ArrayList<>();
          do {
            if (result.getObject("id") != null) records.add(searchRecord(result));
          } while (result.next());
          long first = total == 0 ? 0 : ((long) effective - 1) * 100 + 1;
          return validate(
              new TypedPayloadValues(
                  new LayoutId("SRCRSP01"),
                  new PagedResponseData(
                      effective, 100, total, pages, first, Math.min((long) effective * 100, total)),
                  records));
        }
      }
    } catch (ScenarioQueryException failure) {
      // BUG-031: a close failure can attach raw SQL to the resource-scope capacity exception.
      throw new ScenarioQueryException(failure.getSuppressed().length == 0);
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException failure) {
      throw new ScenarioQueryException(false);
    }
  }

  /**
   * PT-SCN-008-D01..004: one snapshot for global navigation, ordered entries and all voice rows.
   * Missing file returns empty (service maps 0104). More than 10000 expanded rows fails 9001.
   * Caller commits/releases the read transaction before any transfer-file writer is invoked.
   */
  public Optional<ScenarioDetailSnapshot> detail(
      Connection connection, AuthenticatedActor actor, ScenarioDetailRequestData request) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(request, "request");
    String sql =
        """
        with files as (
          select f.id,g.code,f.chapter_title,f.section_code,f.file_name,f.display_path,
            lag(f.id) over w as previous_id,lead(f.id) over w as next_id,
            lag(f.chapter_title) over w as previous_chapter_title,
            lag(f.section_code) over w as previous_section_code,
            lag(f.file_name) over w as previous_file_name,
            lead(f.chapter_title) over w as next_chapter_title,
            lead(f.section_code) over w as next_section_code,
            lead(f.file_name) over w as next_file_name
          from schubert.script_files f join schubert.games g on g.id=f.game_id
          window w as (order by g.display_order,f.display_order,f.id)
        ), entries as (
          select e.id,e.line_number,e.entry_type,s.name as speaker_name,e.body,
            row_number() over(order by e.entry_index,e.display_order,e.id) as sequence
          from schubert.script_entries e left join schubert.speakers s on s.id=e.speaker_id
          where e.script_file_id=?
        )
        select f.id as file_id,f.code,f.chapter_title,f.section_code,f.file_name,f.display_path,
          f.previous_id,f.next_id,f.previous_chapter_title,f.previous_section_code,f.previous_file_name,
          f.next_chapter_title,f.next_section_code,f.next_file_name,
          e.id,e.sequence,e.line_number,e.entry_type,e.speaker_name,e.body,
          a.audio_file_id,a.audio_path,a.audio_sequence
        from files f left join entries e on true left join lateral (
          select l.audio_file_id,af.display_path as audio_path,
            row_number() over(order by l.display_order,l.audio_file_id) as audio_sequence
          from schubert.entry_audio_links l join schubert.audio_files af on af.id=l.audio_file_id
          where l.entry_id=e.id and l.link_type='voice'
        ) a on true where f.id=? order by e.sequence,a.audio_sequence limit 10001
        """;
    try {
      requireReadTransaction(connection);
      try (PreparedStatement statement = connection.prepareStatement(sql)) {
        statement.setLong(1, request.scriptFileId().value());
        statement.setLong(2, request.scriptFileId().value());
        try (ResultSet result = statement.executeQuery()) {
          Optional<ScenarioDetailSnapshot> snapshot = Optional.empty();
          if (result.next()) {
            Optional<ScriptFileId> previous =
                Optional.ofNullable(result.getObject("previous_id", Long.class))
                    .map(ScriptFileId::new);
            Optional<ScriptFileId> next =
                Optional.ofNullable(result.getObject("next_id", Long.class)).map(ScriptFileId::new);
            ScenarioDetailResponseData metadata =
                new ScenarioDetailResponseData(
                    new ScriptFileId(number(result, "file_id")),
                    game(required(result, "code")),
                    title(result, ""),
                    DisplayPath.of(required(result, "display_path")),
                    previous,
                    previous.isPresent()
                        ? Optional.of(title(result, "previous_"))
                        : Optional.empty(),
                    next,
                    next.isPresent() ? Optional.of(title(result, "next_")) : Optional.empty(),
                    DeliveryMode.INLINE,
                    Optional.empty(),
                    Optional.empty(),
                    0,
                    Optional.empty(),
                    0,
                    0);
            List<ScenarioEntryRecord> records = new ArrayList<>();
            do {
              if (result.getObject("id") != null) {
                if (records.size() == 10000) throw new ScenarioQueryException(true);
                Optional<AudioId> audio =
                    Optional.ofNullable(result.getObject("audio_file_id", Long.class))
                        .map(AudioId::new);
                records.add(
                    new ScenarioEntryRecord(
                        new EntryId(number(result, "id")),
                        integer(result, "sequence"),
                        integer(result, "line_number"),
                        entryType(required(result, "entry_type")),
                        Optional.ofNullable(result.getString("speaker_name")),
                        required(result, "body"),
                        audio.isPresent() ? integer(result, "audio_sequence") : 0,
                        audio,
                        Optional.ofNullable(result.getString("audio_path")).map(DisplayPath::of)));
              }
            } while (result.next());
            snapshot = Optional.of(new ScenarioDetailSnapshot(metadata, records));
          }
          return snapshot;
        }
      }
    } catch (ScenarioQueryException failure) {
      throw new ScenarioQueryException(failure.getSuppressed().length == 0);
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException failure) {
      throw new ScenarioQueryException(false);
    }
  }

  private static ScenarioSearchRecord searchRecord(ResultSet r) throws SQLException {
    Optional<AudioId> audio =
        Optional.ofNullable(r.getObject("audio_file_id", Long.class)).map(AudioId::new);
    return new ScenarioSearchRecord(
        new EntryId(number(r, "id")),
        new ScriptFileId(number(r, "script_file_id")),
        game(required(r, "code")),
        Optional.ofNullable(r.getString("chapter_title")),
        integer(r, "line_number"),
        entryType(required(r, "entry_type")),
        Optional.ofNullable(r.getString("speaker_name")),
        required(r, "body"),
        audio.isPresent(),
        audio,
        DisplayPath.of(required(r, "display_path")),
        Optional.ofNullable(r.getString("audio_path")).map(DisplayPath::of));
  }

  private static TypedPayloadValues rows(
      Connection connection,
      AuthenticatedActor actor,
      String sql,
      List<String> parameters,
      String layout,
      int maximum,
      IntFunction<PayloadData> data,
      RowMapper mapper) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    try {
      requireReadTransaction(connection);
      List<PayloadRecord> records = new ArrayList<>();
      try (PreparedStatement statement = connection.prepareStatement(sql)) {
        bind(statement, parameters);
        try (ResultSet result = statement.executeQuery()) {
          while (result.next()) {
            if (records.size() == maximum) throw new ScenarioQueryException(true);
            records.add(mapper.read(result));
          }
        }
      }
      return validate(
          new TypedPayloadValues(new LayoutId(layout), data.apply(records.size()), records));
    } catch (ScenarioQueryException failure) {
      throw new ScenarioQueryException(failure.getSuppressed().length == 0);
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException failure) {
      throw new ScenarioQueryException(false);
    }
  }

  private static void requireReadTransaction(Connection connection) throws SQLException {
    if (connection.getAutoCommit() || !connection.isReadOnly())
      throw new SQLException("read transaction required");
  }

  private static void bind(PreparedStatement statement, List<String> parameters)
      throws SQLException {
    for (int i = 0; i < parameters.size(); i++) statement.setString(i + 1, parameters.get(i));
  }

  private static TypedPayloadValues validate(TypedPayloadValues values) {
    PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false);
    return values;
  }

  /** BUG-035/SSC-018: preserve Current's isBlank semantics, not SQL empty-string-only fallback. */
  private static String title(ResultSet result, String prefix) throws SQLException {
    String chapter = result.getString(prefix + "chapter_title");
    if (chapter != null && !chapter.isBlank()) return chapter;
    String section = result.getString(prefix + "section_code");
    if (section != null && !section.isBlank()) return section;
    return required(result, prefix + "file_name");
  }

  private static String required(ResultSet result, String column) throws SQLException {
    String value = result.getString(column);
    if (value == null) throw new SQLException("required scenario text is missing");
    return value;
  }

  private static long number(ResultSet result, String column) throws SQLException {
    // BUG-030/YKT-027: getObject(Long.class) only accepts PostgreSQL bigint, not int2/int4.
    long value = result.getLong(column);
    if (result.wasNull()) throw new SQLException("required scenario number is missing");
    return value;
  }

  private static int integer(ResultSet result, String column) throws SQLException {
    return Math.toIntExact(number(result, column));
  }

  private static EntryType entryType(String code) throws SQLException {
    return switch (code) {
      case "dialogue" -> EntryType.DIALOGUE;
      case "narration" -> EntryType.NARRATION;
      default -> throw new SQLException("invalid entry metadata");
    };
  }

  private static GameCode game(String code) throws SQLException {
    return switch (code) {
      case "NUKITASHI1" -> GameCode.NUKITASHI_1;
      case "NUKITASHI2" -> GameCode.NUKITASHI_2;
      default -> throw new SQLException("invalid game metadata");
    };
  }

  private static String routeName(GameCode game, int prefix) {
    return (game == GameCode.NUKITASHI_1 ? FIRST_ROUTES : SECOND_ROUTES)
        .getOrDefault(prefix, "未分類");
  }

  private static Optional<String> text(Optional<String> value) {
    return value
        .map(s -> Normalizer.normalize(s, Normalizer.Form.NFC).trim())
        .filter(s -> !s.isEmpty());
  }

  private static void add(
      List<String> filters, List<String> parameters, String sql, Optional<String> value) {
    value.ifPresent(
        v -> {
          filters.add(sql);
          parameters.add(v);
        });
  }

  @FunctionalInterface
  private interface RowMapper {
    PayloadRecord read(ResultSet result) throws SQLException;
  }
}
