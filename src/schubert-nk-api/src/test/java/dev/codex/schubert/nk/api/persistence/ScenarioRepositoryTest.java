package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.application.scenario.ScenarioQuerySnapshot;
import dev.codex.schubert.nk.api.application.scenario.ScenarioRequest;
import dev.codex.schubert.nk.api.application.scenario.ScenarioRequestFixture;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadSemanticValidator;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.RouteRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioEntryRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioFileListRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRecord;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioSearchRequestData;
import dev.codex.schubert.nk.protocol.layout.scenario.SpeakerListRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.EntryType;
import dev.codex.schubert.nk.protocol.layout.semantic.GameCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ScriptFileId;
import dev.codex.schubert.nk.protocol.layout.semantic.VoiceCondition;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-SCN-001..007: synthetic real PostgreSQL, literal ID sets and independent UI234 byte offsets.
 */
final class ScenarioRepositoryTest {
  private static final String FIXTURE_01_A_D193F9D6 = "01_A";
  private static final String FIXTURE_CHAPTER_A_E3A27D05 = "Chapter A";
  private static final String FIXTURE_BOB_2ABF6B98 = "Bob";
  private static final String FIXTURE_ALICE_1EA1F9A4 = "Alice";
  private static final String FIXTURE_NUKITASHI1_F97F2EAE = "NUKITASHI1";
  private static final String FIXTURE_NUKITASHI2_3B3D052F = "NUKITASHI2";
  private static final String FIXTURE_TRUNCATE_SCHUBERT_SCRIPT_FILES_CASCADE_B7F22DE8 =
      "truncate schubert.script_files cascade";
  private static final String FIXTURE_NARRATION_320AF5F0 = "narration";
  private static final String FIXTURE_DIALOGUE_37AC104E = "dialogue";
  private static final String FIXTURE_GETLONG_7D3C0BFE = "getLong";
  private static final String FIXTURE_GETSTRING_B3B802ED = "getString";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String FIXTURE_SYNTHETIC_SQL_MUST_NOT_ESCAPE_6962B758 =
      "synthetic SQL must not escape";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static final ScenarioRepository REPOSITORY = new ScenarioRepository();
  private static final AuthenticatedActor USER = new AuthenticatedActor(7, "reader", Role.USER);
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(8, "admin", Role.ADMIN);
  private static final GameCode G1 = GameCode.NUKITASHI_1;
  private static final GameCode G2 = GameCode.NUKITASHI_2;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void seed() throws Exception {
    sql("truncate schubert.script_files,schubert.speakers,schubert.audio_files cascade");
    sql("update schubert.games set title=code");
    file(30, 1, 1, FIXTURE_01_A_D193F9D6, FIXTURE_CHAPTER_A_E3A27D05);
    file(10, 1, 2, "02_B", null);
    file(20, 2, 1, "01_C", "chapter B");
    sql(
        """
        insert into schubert.speakers(id,game_id,name,normalized_name,created_at) values
        (1,1,'Alice','alice','2026-09-01Z'),(2,1,'Bob','bob','2026-09-01Z'),
        (3,2,'Alice','alice','2026-09-01Z'),(4,1,'Unused','unused','2026-09-01Z')
        """);
    entry(100, 1, 30, 3, 0, 11, 1, "Alice label", "Alpha 100% x_y \\ tail");
    entry(200, 1, 30, 1, 1, 22, 2, FIXTURE_BOB_2ABF6B98, "Beta O'Reilly");
    entry(300, 1, 10, 2, 0, 33, null, null, "alpha xy");
    entry(400, 2, 20, 4, 0, 44, 3, FIXTURE_ALICE_1EA1F9A4, "ALPHA abc");
    sql(
        """
        insert into schubert.audio_files(id,game_id,storage_relative_path,display_path,file_name,basename,
          audio_role,byte_size,sha256,created_at)
        select id,1,'scenario/a'||id||'.ogg','voice/a'||id||'.ogg','a'||id||'.ogg','a'||id,
          'voice',1,repeat('a',64),'2026-09-01Z' from (values(700),(800),(900)) t(id);
        insert into schubert.entry_audio_links(entry_id,audio_file_id,game_id,link_type,display_order,created_at)
        values(100,700,1,'voice',2,'2026-09-01Z'),(100,800,1,'voice',1,'2026-09-01Z'),
              (200,900,1,'se',1,'2026-09-01Z')
        """);
  }

  @Test
  void ptScn001GamesHaveIndependentBytesAndDoNotOwnTransaction() throws Exception {
    try (Connection c = read()) {
      TypedPayloadValues values = REPOSITORY.games(c, USER);
      assertPayload(
          values,
          numeric(9, 2),
          List.of(
              game(FIXTURE_NUKITASHI1_F97F2EAE, FIXTURE_NUKITASHI1_F97F2EAE, 1),
              game(FIXTURE_NUKITASHI2_3B3D052F, FIXTURE_NUKITASHI2_3B3D052F, 2)));
      assertPayload(
          REPOSITORY.games(c, ADMIN),
          numeric(9, 2),
          List.of(
              game(FIXTURE_NUKITASHI1_F97F2EAE, FIXTURE_NUKITASHI1_F97F2EAE, 1),
              game(FIXTURE_NUKITASHI2_3B3D052F, FIXTURE_NUKITASHI2_3B3D052F, 2)));
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertTrue(c.isReadOnly());
      assertThrows(UnsupportedOperationException.class, () -> values.records().clear());
    }
    // Fresh isolated master: IDs no longer determine game display order.
    sql("truncate schubert.games cascade");
    sql(
        "insert into schubert.games values(1,'NUKITASHI1','One',2,'2026-09-01Z'),(2,'NUKITASHI2','Two',1,'2026-09-01Z')");
    try (Connection c = read()) {
      assertPayload(
          REPOSITORY.games(c, USER),
          numeric(9, 2),
          List.of(
              game(FIXTURE_NUKITASHI2_3B3D052F, "Two", 1),
              game(FIXTURE_NUKITASHI1_F97F2EAE, "One", 2)));
    }
    sql("truncate schubert.games cascade");
    try (Connection c = read()) {
      assertPayload(REPOSITORY.games(c, USER), numeric(9, 0), List.of());
    }
    sql(
        "insert into schubert.games values(1,'NUKITASHI1','NUKITASHI1',1,'2026-09-01Z'),(2,'NUKITASHI2','NUKITASHI2',2,'2026-09-01Z')");
  }

  @Test
  void ptScn009AllRequestRoutesUseIndependentDatabaseOutcomes() throws Exception {
    try (Connection c = read()) {
      var games =
          (ScenarioQuerySnapshot.Inline)
              ScenarioRequest.decode(ScenarioRequestFixture.message("GAMREQ01", new byte[0]))
                  .query(REPOSITORY, c, USER);
      assertPayload(
          games.value(),
          numeric(9, 2),
          List.of(
              game(FIXTURE_NUKITASHI1_F97F2EAE, FIXTURE_NUKITASHI1_F97F2EAE, 1),
              game(FIXTURE_NUKITASHI2_3B3D052F, FIXTURE_NUKITASHI2_3B3D052F, 2)));
      var speakers =
          (ScenarioQuerySnapshot.Inline)
              ScenarioRequest.decode(
                      ScenarioRequestFixture.message("SPKREQ01", ScenarioRequestFixture.spaces(12)))
                  .query(REPOSITORY, c, USER);
      assertPayload(
          speakers.value(),
          numeric(9, 2),
          List.of(speaker(1, FIXTURE_ALICE_1EA1F9A4, 2), speaker(2, FIXTURE_BOB_2ABF6B98, 1)));
      byte[] game = ScenarioRequestFixture.spaces(12);
      ScenarioRequestFixture.put(game, 0, FIXTURE_NUKITASHI1_F97F2EAE);
      var routes =
          (ScenarioQuerySnapshot.Inline)
              ScenarioRequest.decode(ScenarioRequestFixture.message("RTEREQ01", game))
                  .query(REPOSITORY, c, USER);
      assertPayload(
          routes.value(), numeric(9, 2), List.of(route(1, "共通ルート", 1), route(2, "奈々瀬ルート", 1)));
      byte[] files = ScenarioRequestFixture.spaces(14);
      ScenarioRequestFixture.put(files, 0, FIXTURE_NUKITASHI1_F97F2EAE);
      ScenarioRequestFixture.put(files, 12, "01");
      var fileList =
          (ScenarioQuerySnapshot.Inline)
              ScenarioRequest.decode(ScenarioRequestFixture.message("SCFREQ01", files))
                  .query(REPOSITORY, c, USER);
      assertPayload(
          fileList.value(),
          fileData(FIXTURE_NUKITASHI1_F97F2EAE, 1, "共通ルート", 1),
          List.of(fileRecord(30, FIXTURE_CHAPTER_A_E3A27D05, 2)));
      var search =
          (ScenarioQuerySnapshot.Inline)
              ScenarioRequest.decode(
                      ScenarioRequestFixture.message("SRCREQ01", ScenarioRequestFixture.search()))
                  .query(REPOSITORY, c, USER);
      assertEquals(
          List.of(200L, 300L, 100L, 400L),
          search.value().records().stream()
              .map(r -> ((ScenarioSearchRecord) r).entryId().value())
              .toList());
      var detail =
          (ScenarioQuerySnapshot.Detail)
              ScenarioRequest.decode(
                      ScenarioRequestFixture.message(
                          "SCNREQ01", "000000000030".getBytes(StandardCharsets.US_ASCII)))
                  .query(REPOSITORY, c, USER);
      var snapshot = detail.value().orElseThrow();
      assertEquals(30, snapshot.metadata().scriptFileId().value());
      assertEquals(
          List.of(100L, 100L, 200L),
          snapshot.records().stream().map(r -> r.entryId().value()).toList());
      assertEquals(
          List.of(1, 1, 2),
          snapshot.records().stream().map(ScenarioEntryRecord::entrySequence).toList());
      assertEquals(
          List.of(Optional.of(new AudioId(800)), Optional.of(new AudioId(700)), Optional.empty()),
          snapshot.records().stream().map(ScenarioEntryRecord::audioId).toList());
      var missing =
          (ScenarioQuerySnapshot.Detail)
              ScenarioRequest.decode(
                      ScenarioRequestFixture.message(
                          "SCNREQ01", "000000009999".getBytes(StandardCharsets.US_ASCII)))
                  .query(REPOSITORY, c, ADMIN);
      assertTrue(missing.value().isEmpty());
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertTrue(c.isReadOnly());
      c.commit();
    }
  }

  @Test
  void ptScn002SpeakerAggregationIsByNameAndScopedBeforeCounting() throws Exception {
    try (Connection c = read()) {
      assertPayload(
          REPOSITORY.speakers(c, USER, new SpeakerListRequestData(Optional.empty())),
          numeric(9, 2),
          List.of(speaker(1, FIXTURE_ALICE_1EA1F9A4, 2), speaker(2, FIXTURE_BOB_2ABF6B98, 1)));
      assertPayload(
          REPOSITORY.speakers(c, USER, new SpeakerListRequestData(Optional.of(G1))),
          numeric(9, 2),
          List.of(speaker(1, FIXTURE_ALICE_1EA1F9A4, 1), speaker(2, FIXTURE_BOB_2ABF6B98, 1)));
      assertPayload(
          REPOSITORY.speakers(c, ADMIN, new SpeakerListRequestData(Optional.of(G2))),
          numeric(9, 1),
          List.of(speaker(3, FIXTURE_ALICE_1EA1F9A4, 1)));
    }
    sql("delete from schubert.script_entries where game_id=2");
    try (Connection c = read()) {
      assertPayload(
          REPOSITORY.speakers(c, USER, new SpeakerListRequestData(Optional.of(G2))),
          numeric(9, 0),
          List.of());
    }
  }

  @Test
  void ptScn003EveryRouteMapAndUnknownPrefixHaveIndependentBytes() throws Exception {
    sql(FIXTURE_TRUNCATE_SCHUBERT_SCRIPT_FILES_CASCADE_B7F22DE8);
    int[][] prefixes = {{0, 1, 2, 3, 4, 5, 99}, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 99}};
    String[][] names = {
      {"未分類", "共通ルート", "奈々瀬ルート", "ヒナミルート", "美岬ルート", "文乃ルート", "未分類"},
      {
        "未分類", "共通ルート", "共通ルート", "桐香ルート", "礼ルート", "郁子ルート", "麻沙音ルート", "奈々瀬ルート", "ヒナミルート", "美岬ルート",
        "文乃ルート", "スス子ルート", "未分類"
      }
    };
    for (int g = 0; g < 2; g++) {
      List<byte[]> expected = new ArrayList<>();
      for (int i = 0; i < prefixes[g].length; i++) {
        int p = prefixes[g][i];
        file(1000 + g * 100 + p, g + 1, p + 1, String.format(Locale.ROOT, "%02d_file", p), null);
        expected.add(route(p, names[g][i], 1));
      }
      try (Connection c = read()) {
        assertPayload(
            REPOSITORY.routes(c, USER, new RouteListRequestData(g == 0 ? G1 : G2)),
            numeric(9, prefixes[g].length),
            expected);
      }
    }
    file(9999, 1, 101, "01_more", null);
    try (Connection c = read()) {
      RouteRecord r =
          (RouteRecord) REPOSITORY.routes(c, USER, new RouteListRequestData(G1)).records().get(1);
      assertEquals(2, r.fileCount());
    }
    sql(FIXTURE_TRUNCATE_SCHUBERT_SCRIPT_FILES_CASCADE_B7F22DE8);
    try (Connection c = read()) {
      assertPayload(
          REPOSITORY.routes(c, USER, new RouteListRequestData(G2)), numeric(9, 0), List.of());
    }
    for (String section : Arrays.asList(null, "", "1", "xx")) {
      file(1, 1, 1, section, null);
      try (Connection c = read()) {
        failure(
            () -> REPOSITORY.routes(c, USER, new RouteListRequestData(G1)),
            ResultCode.TEMPORARY_FAILURE);
      }
      sql("delete from schubert.script_files");
    }
  }

  @Test
  void ptScn004FilesUseDisplayOrderTitleAndEntryNotAudioCount() throws Exception {
    file(5, 1, 3, "01_Z", "");
    try (Connection c = read()) {
      assertPayload(
          REPOSITORY.files(c, USER, new ScenarioFileListRequestData(G1, 1)),
          fileData(FIXTURE_NUKITASHI1_F97F2EAE, 1, "共通ルート", 2),
          List.of(fileRecord(30, FIXTURE_CHAPTER_A_E3A27D05, 2), fileRecord(5, "01_Z", 0)));
      assertPayload(
          REPOSITORY.files(c, ADMIN, new ScenarioFileListRequestData(G2, 2)),
          fileData(FIXTURE_NUKITASHI2_3B3D052F, 2, "共通ルート", 0),
          List.of());
    }
  }

  @Test
  void ptScn005SixFiltersWildcardsAndRepresentativeVoiceAreIndependent() throws Exception {
    try (Connection c = read()) {
      assertIds(c, request("", "", "", "", "", "", 1), 200, 300, 100, 400);
      assertIds(c, request(" alpha ", "", "", "", "", "", 1), 300, 100, 400);
      assertIds(c, request("", FIXTURE_NUKITASHI1_F97F2EAE, "", "", "", "", 1), 200, 300, 100);
      assertIds(c, request("", "", " Alice ", "", "", "", 1), 100, 400);
      assertIds(c, request("", "", "", " CHAPTER ", "", "", 1), 200, 100, 400);
      assertIds(c, request("", "", "", "", FIXTURE_NARRATION_320AF5F0, "", 1), 300);
      assertIds(c, request("", "", "", "", FIXTURE_DIALOGUE_37AC104E, "", 1), 200, 100, 400);
      assertIds(c, request("", "", "", "", "", "1", 1), 100);
      assertIds(c, request("", "", "", "", "", "0", 1), 200, 300, 400);
      assertIds(
          c,
          request(
              "Alpha",
              FIXTURE_NUKITASHI1_F97F2EAE,
              FIXTURE_ALICE_1EA1F9A4,
              "chapter a",
              FIXTURE_DIALOGUE_37AC104E,
              "1",
              1),
          100);
      assertIds(c, request("", FIXTURE_NUKITASHI2_3B3D052F, FIXTURE_BOB_2ABF6B98, "", "", "", 1));
      assertIds(c, request("%", "", "", "", "", "", 1), 200, 300, 100, 400);
      assertIds(c, request("_", "", "", "", "", "", 1), 200, 300, 100, 400);
      assertIds(c, request("\\%", "", "", "", "", "", 1), 100);
      assertIds(c, request("\\_", "", "", "", "", "", 1), 100);
      assertIds(c, request("\\\\", "", "", "", "", "", 1), 100);
      assertIds(c, request("O'Reilly", "", "", "", "", "", 1), 200);
      assertIds(c, request("' OR true --", "", "", "", "", "", 1));
      assertIds(c, request("", "", "", "chapter _", "", "", 1), 200, 100, 400);
      assertIds(c, request(" ", "", " ", " ", "", "", 1), 200, 300, 100, 400);
      TypedPayloadValues values = REPOSITORY.search(c, USER, request("\\%", "", "", "", "", "", 1));
      byte[] record = blank(5584);
      put(record, 0, numeric(12, 100));
      put(record, 12, numeric(12, 30));
      put(record, 24, FIXTURE_NUKITASHI1_F97F2EAE);
      put(record, 36, FIXTURE_CHAPTER_A_E3A27D05);
      put(record, 292, numeric(8, 11));
      put(record, 300, FIXTURE_DIALOGUE_37AC104E);
      // BUG-035: Current displays the joined speaker name, never the retained source label.
      put(record, 310, FIXTURE_ALICE_1EA1F9A4);
      put(record, 438, "Alpha 100% x_y \\ tail");
      put(record, 4534, "1");
      put(record, 4535, "800");
      put(record, 4547, "script/f30.ks");
      put(record, 5059, "voice/a800.ogg");
      assertPayload(values, page(1, 1, 1, 1, 1), List.of(record));
      ScenarioSearchRecord noVoice =
          (ScenarioSearchRecord)
              REPOSITORY
                  .search(c, USER, request("Beta", "", "", "", "", "", 1))
                  .records()
                  .getFirst();
      assertFalse(noVoice.audioPresent());
      assertTrue(noVoice.audioId().isEmpty());
      assertTrue(noVoice.audioDisplayPath().isEmpty());
    }
    sql("update schubert.script_entries set body='ガ' where id=300");
    try (Connection c = read()) {
      assertIds(c, request("カ\u3099", "", "", "", "", "", 1), 300);
    }
  }

  @Test
  void ptScn006PagesAreClippedWithOneStatementAndEmptyIsOnePage() throws Exception {
    sql("truncate schubert.script_entries cascade");
    for (int count : new int[] {0, 1, 99, 100, 101, 200, 201}) {
      sql("truncate schubert.script_entries cascade");
      sql(
          """
          insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,
            line_number,entry_type,body,raw_block,created_at)
          select i,1,30,i,i-1,i,'narration','row'||i,'synthetic','2026-09-01Z'
            from generate_series(1,%d) i
          """
              .formatted(count));
      for (int requested : new int[] {1, 2, 999999}) {
        int pages = Math.max(1, (count + 99) / 100);
        int effective = Math.min(requested, pages);
        long first = count == 0 ? 0 : (effective - 1) * 100L + 1;
        long last = Math.min(effective * 100L, count);
        try (Connection c = read()) {
          AtomicInteger statements = new AtomicInteger();
          Connection spy =
              wrap(
                  Connection.class,
                  c,
                  (target, method, args) -> {
                    if (method.getName().equals("prepareStatement")) statements.incrementAndGet();
                    return invoke(target, method, args);
                  });
          TypedPayloadValues result =
              REPOSITORY.search(spy, USER, request("", "", "", "", "", "", requested));
          assertArrayEquals(page(effective, count, pages, first, last), encoded(result).copyData());
          assertEquals(count == 0 ? 0 : last - first + 1, result.records().size());
          assertEquals(1, statements.get());
          if (count > 0) {
            assertEquals(
                first, ((ScenarioSearchRecord) result.records().getFirst()).entryId().value());
            assertEquals(
                last, ((ScenarioSearchRecord) result.records().getLast()).entryId().value());
          }
        }
      }
    }
  }

  @Test
  void ptScn007NullReadonlyAndRequiredMetadataNeverBecomeSuccess() throws Exception {
    try (Connection c = read()) {
      assertThrows(NullPointerException.class, () -> REPOSITORY.games(null, USER));
      assertThrows(NullPointerException.class, () -> REPOSITORY.games(c, null));
      assertThrows(NullPointerException.class, () -> REPOSITORY.speakers(c, USER, null));
      assertThrows(NullPointerException.class, () -> REPOSITORY.routes(c, USER, null));
      assertThrows(NullPointerException.class, () -> REPOSITORY.files(c, USER, null));
      assertThrows(NullPointerException.class, () -> REPOSITORY.search(c, USER, null));
      assertThrows(
          NullPointerException.class,
          () -> REPOSITORY.search(null, USER, request("", "", "", "", "", "", 1)));
      assertThrows(
          NullPointerException.class,
          () -> REPOSITORY.search(c, null, request("", "", "", "", "", "", 1)));
      assertThrows(
          IllegalArgumentException.class,
          () -> REPOSITORY.search(c, USER, request("", "", "", "", "", "", 0)));
      assertThrows(
          IllegalArgumentException.class,
          () -> REPOSITORY.search(c, USER, request("x".repeat(257), "", "", "", "", "", 1)));
    }
    try (Connection c = database.api()) {
      failure(() -> REPOSITORY.games(c, USER), ResultCode.TEMPORARY_FAILURE);
    }
    try (Connection c = database.transaction()) {
      failure(
          () -> REPOSITORY.search(c, USER, request("", "", "", "", "", "", 1)),
          ResultCode.TEMPORARY_FAILURE);
    }
    Connection closed = read();
    closed.close();
    failure(() -> REPOSITORY.games(closed, USER), ResultCode.TEMPORARY_FAILURE);
    for (String assignment :
        List.of("line_number=null", "line_number=100000000", "body=E'bad\\nbody'")) {
      sql("update schubert.script_entries set " + assignment + " where id=200");
      try (Connection c = read()) {
        failure(
            () -> REPOSITORY.search(c, USER, request("", "", "", "", "", "", 1)),
            ResultCode.TEMPORARY_FAILURE);
      }
      sql(
          "update schubert.script_entries set line_number=22,body='Beta',speaker_label='Bob' where id=200");
    }
    sql("update schubert.script_files set display_path='../escape' where id=30");
    try (Connection c = read()) {
      failure(
          () -> REPOSITORY.files(c, USER, new ScenarioFileListRequestData(G1, 1)),
          ResultCode.TEMPORARY_FAILURE);
    }
  }

  @Test
  void ptScn002004CapacityLimitsNeverReturnTruncatedSuccess() throws Exception {
    sql("truncate schubert.speakers,schubert.script_entries cascade");
    sql(
        """
        insert into schubert.speakers(id,game_id,name,normalized_name,created_at)
        select i,1,'speaker'||lpad(i::text,3,'0'),'s'||i,'2026-09-01Z' from generate_series(1,500) i;
        insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,
          line_number,entry_type,speaker_id,speaker_label,body,raw_block,created_at)
        select i,1,30,i,i-1,i,'dialogue',i,'speaker'||lpad(i::text,3,'0'),'body','synthetic','2026-09-01Z'
          from generate_series(1,500) i
        """);
    try (Connection c = read()) {
      TypedPayloadValues values =
          REPOSITORY.speakers(c, USER, new SpeakerListRequestData(Optional.empty()));
      assertEquals(500, values.records().size());
      assertArrayEquals(speaker(1, "speaker001", 1), encoded(values).copyRecords().getFirst());
      assertArrayEquals(speaker(500, "speaker500", 1), encoded(values).copyRecords().getLast());
    }
    sql(
        "insert into schubert.speakers(id,game_id,name,normalized_name,created_at) values(501,1,'speaker501','s501','2026-09-01Z')");
    entry(501, 1, 30, 501, 500, 501, 501, "speaker501", "body");
    try (Connection c = read()) {
      failure(
          () -> REPOSITORY.speakers(c, USER, new SpeakerListRequestData(Optional.empty())),
          ResultCode.RESOURCE_LIMIT);
    }
    sql(FIXTURE_TRUNCATE_SCHUBERT_SCRIPT_FILES_CASCADE_B7F22DE8);
    sql(
        """
        insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,
          file_name,section_code,chapter_title,sha256,byte_size,created_at)
        select i,1,i,'scenario/f'||i||'.ks','script/f'||i||'.ks','f'||i||'.ks','01_'||i,null,repeat('a',64),1,'2026-09-01Z'
          from generate_series(1,500) i
        """);
    try (Connection c = read()) {
      assertEquals(
          500, REPOSITORY.files(c, USER, new ScenarioFileListRequestData(G1, 1)).records().size());
    }
    file(501, 1, 501, "01_501", null);
    try (Connection c = read()) {
      failure(
          () -> REPOSITORY.files(c, USER, new ScenarioFileListRequestData(G1, 1)),
          ResultCode.RESOURCE_LIMIT);
    }
    sql(FIXTURE_TRUNCATE_SCHUBERT_SCRIPT_FILES_CASCADE_B7F22DE8);
    for (int i = 0; i < 50; i++) file(i + 1, 1, i + 1, String.format(Locale.ROOT, "%02d", i), null);
    try (Connection c = read()) {
      assertEquals(50, REPOSITORY.routes(c, USER, new RouteListRequestData(G1)).records().size());
    }
    file(51, 1, 51, "50", null);
    try (Connection c = read()) {
      failure(
          () -> REPOSITORY.routes(c, USER, new RouteListRequestData(G1)),
          ResultCode.RESOURCE_LIMIT);
    }
  }

  @Test
  void ptScn006007AggregateAndMetadataFaultsAreBounded() throws Exception {
    try (Connection c = read()) {
      for (String method :
          List.of(
              "getAutoCommit",
              "isReadOnly",
              "prepareStatement",
              "setString",
              "executeQuery",
              "next",
              FIXTURE_GETLONG_7D3C0BFE,
              FIXTURE_GETSTRING_B3B802ED,
              "wasNull",
              FIXTURE_CLOSE_97959247)) {
        AtomicInteger hits = new AtomicInteger();
        Connection broken =
            intercept(
                c,
                (target, m, args) -> {
                  if (m.getName().equals(method)) {
                    hits.incrementAndGet();
                    if (method.equals(FIXTURE_CLOSE_97959247)) invoke(target, m, args);
                    throw new SQLException(FIXTURE_SYNTHETIC_SQL_MUST_NOT_ESCAPE_6962B758, "08006");
                  }
                  return invoke(target, m, args);
                });
        failure(
            () -> REPOSITORY.files(broken, USER, new ScenarioFileListRequestData(G1, 1)),
            ResultCode.TEMPORARY_FAILURE);
        failure(
            () -> REPOSITORY.search(broken, USER, request("alpha", "", "", "", "", "", 1)),
            ResultCode.TEMPORARY_FAILURE);
        assertTrue(hits.get() > 0, method);
      }
      for (String field : List.of("code", "title")) {
        Connection nullText =
            intercept(
                c,
                (target, m, args) ->
                    m.getName().equals(FIXTURE_GETSTRING_B3B802ED) && args[0].equals(field)
                        ? null
                        : invoke(target, m, args));
        failure(() -> REPOSITORY.games(nullText, USER), ResultCode.TEMPORARY_FAILURE);
      }
      Connection unknownGame =
          intercept(
              c,
              (target, m, args) ->
                  m.getName().equals(FIXTURE_GETSTRING_B3B802ED) && args[0].equals("code")
                      ? "UNKNOWN"
                      : invoke(target, m, args));
      failure(() -> REPOSITORY.games(unknownGame, USER), ResultCode.TEMPORARY_FAILURE);
      Connection nullNumber =
          intercept(
              c,
              (target, m, args) -> m.getName().equals("wasNull") ? true : invoke(target, m, args));
      failure(() -> REPOSITORY.games(nullNumber, USER), ResultCode.TEMPORARY_FAILURE);
      Connection overflow =
          intercept(
              c,
              (target, m, args) ->
                  m.getName().equals(FIXTURE_GETLONG_7D3C0BFE) && args[0].equals("entries")
                      ? 2147483648L
                      : invoke(target, m, args));
      failure(
          () -> REPOSITORY.files(overflow, USER, new ScenarioFileListRequestData(G1, 1)),
          ResultCode.TEMPORARY_FAILURE);
      Connection missingAggregate =
          intercept(
              c, (target, m, args) -> m.getName().equals("next") ? false : invoke(target, m, args));
      failure(
          () -> REPOSITORY.search(missingAggregate, USER, request("", "", "", "", "", "", 1)),
          ResultCode.TEMPORARY_FAILURE);
      Connection unknownType =
          intercept(
              c,
              (target, m, args) ->
                  m.getName().equals(FIXTURE_GETSTRING_B3B802ED) && args[0].equals("entry_type")
                      ? "UNKNOWN"
                      : invoke(target, m, args));
      failure(
          () -> REPOSITORY.search(unknownType, USER, request("", "", "", "", "", "", 1)),
          ResultCode.TEMPORARY_FAILURE);
      Connection capacity =
          intercept(
              c,
              (target, m, args) ->
                  m.getName().equals(FIXTURE_GETLONG_7D3C0BFE) && args[0].equals("total")
                      ? 99999901L
                      : invoke(target, m, args));
      failure(
          () -> REPOSITORY.search(capacity, USER, request("", "", "", "", "", "", 1)),
          ResultCode.RESOURCE_LIMIT);
      // BUG-033: a full last page requires 100 actual projected records, not just count metadata.
      sql(
          """
          insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,
            line_number,entry_type,body,raw_block,created_at)
          select 1000+i,1,30,1000+i,1000+i,i,'narration','row'||i,'synthetic','2026-09-01Z'
            from generate_series(1,96) i
          """);
      Connection maximum =
          intercept(
              c,
              (target, m, args) ->
                  m.getName().equals(FIXTURE_GETLONG_7D3C0BFE)
                      ? switch (args[0].toString()) {
                        case "total" -> 99999900L;
                        case "pages", "effective" -> 999999L;
                        default -> invoke(target, m, args);
                      }
                      : invoke(target, m, args));
      TypedPayloadValues max =
          REPOSITORY.search(maximum, USER, request("", "", "", "", "", "", 999999));
      assertArrayEquals(
          page(999999, 99999900, 999999, 99999801, 99999900), encoded(max).copyData());
    }
  }

  @Test
  void ptScn007CapacityAndCloseFailureNeverExposeSuppressedSql() throws Exception {
    sql(FIXTURE_TRUNCATE_SCHUBERT_SCRIPT_FILES_CASCADE_B7F22DE8);
    for (int i = 0; i < 51; i++) file(i + 1, 1, i + 1, String.format(Locale.ROOT, "%02d", i), null);
    try (Connection c = read()) {
      Connection broken =
          intercept(
              c,
              (target, m, args) -> {
                if (m.getName().equals(FIXTURE_GETLONG_7D3C0BFE) && args[0].equals("total"))
                  return 99999901L;
                if (m.getName().equals(FIXTURE_CLOSE_97959247)) {
                  invoke(target, m, args);
                  throw new SQLException(FIXTURE_SYNTHETIC_SQL_MUST_NOT_ESCAPE_6962B758);
                }
                return invoke(target, m, args);
              });
      failure(
          () -> REPOSITORY.search(broken, USER, request("", "", "", "", "", "", 1)),
          ResultCode.TEMPORARY_FAILURE);
      failure(
          () -> REPOSITORY.routes(broken, USER, new RouteListRequestData(G1)),
          ResultCode.TEMPORARY_FAILURE);
    }
  }

  @Test
  void ptScn007JdbcIntegerWideningKeepsSqlNullDistinct() throws Exception {
    try (Connection c = read();
        Statement s = c.createStatement();
        ResultSet r =
            s.executeQuery("select 7::smallint a,11::integer b,13::bigint c,null::integer n")) {
      assertTrue(r.next());
      for (String field : List.of("a", "b"))
        assertThrows(SQLException.class, () -> r.getObject(field, Long.class));
      assertEquals(13L, r.getObject("c", Long.class));
      assertEquals(7, r.getLong("a"));
      assertFalse(r.wasNull());
      assertEquals(11, r.getLong("b"));
      assertFalse(r.wasNull());
      assertEquals(0, r.getLong("n"));
      assertTrue(r.wasNull());
    }
  }

  @Test
  void ptScn005ThreeTextInputsNormalizeBeforeByteChecks() throws Exception {
    sql("update schubert.speakers set name='ガ' where id=1");
    sql("update schubert.script_files set chapter_title='ガ' where id=30");
    sql("update schubert.script_entries set body='ガ' where id=100");
    try (Connection c = read()) {
      assertIds(c, request(" カ\u3099 ", "", " カ\u3099 ", " カ\u3099 ", "", "", 1), 100);
      assertIds(c, request(" ".repeat(300) + "ガ" + " ".repeat(300), "", "", "", "", "", 1), 100);
      assertIds(c, request("", "", " ".repeat(300) + "ガ ", "", "", "", 1), 100);
      assertIds(c, request("", "", "", " ".repeat(300) + "ガ ", "", "", 1), 200, 100);
      assertThrows(
          IllegalArgumentException.class,
          () -> REPOSITORY.search(c, USER, request("", "", "x".repeat(129), "", "", "", 1)));
      assertThrows(
          IllegalArgumentException.class,
          () -> REPOSITORY.search(c, USER, request("", "", "", "x".repeat(257), "", "", 1)));
    }
  }

  @Test
  void ptScn005ParallelReadsKeepOrderAndDoNotWriteMasterOrSessions() throws Exception {
    try (var executor = java.util.concurrent.Executors.newFixedThreadPool(16)) {
      List<java.util.concurrent.Callable<List<Long>>> work = new ArrayList<>();
      for (int i = 0; i < 100; i++)
        work.add(
            () -> {
              try (Connection c = read()) {
                return REPOSITORY
                    .search(c, USER, request("alpha", "", "", "", "", "", 1))
                    .records()
                    .stream()
                    .map(r -> ((ScenarioSearchRecord) r).entryId().value())
                    .toList();
              }
            });
      for (var future : executor.invokeAll(work))
        assertEquals(List.of(300L, 100L, 400L), future.get());
    }
    try (Connection c = database.admin();
        Statement s = c.createStatement();
        ResultSet r =
            s.executeQuery(
                "select (select count(*) from schubert.script_entries) entries,(select count(*) from schubert.auth_sessions) sessions")) {
      assertTrue(r.next());
      assertEquals(4, r.getInt("entries"));
      assertEquals(0, r.getInt("sessions"));
    }
  }

  @Test
  void ptScn008D01NavigationAndBlankTitlesFollowCurrentDisplayContract() throws Exception {
    for (String blank : Arrays.asList(null, "", "  ", "\u2003", "\n\t")) {
      try (Connection c = database.admin();
          PreparedStatement s =
              c.prepareStatement("update schubert.script_files set chapter_title=? where id=30")) {
        s.setString(1, blank);
        s.executeUpdate();
      }
      try (Connection c = read()) {
        assertPayload(
            REPOSITORY.files(c, USER, new ScenarioFileListRequestData(G1, 1)),
            fileData(FIXTURE_NUKITASHI1_F97F2EAE, 1, "共通ルート", 1),
            List.of(fileRecord(30, FIXTURE_01_A_D193F9D6, 2)));
        ScenarioDetailSnapshot first =
            REPOSITORY
                .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30)))
                .orElseThrow();
        assertEquals(FIXTURE_01_A_D193F9D6, first.metadata().displayTitle());
        assertTrue(first.metadata().previousFileId().isEmpty());
        assertEquals(10, first.metadata().nextFileId().orElseThrow().value());
        assertEquals("02_B", first.metadata().nextTitle().orElseThrow());
        ScenarioDetailSnapshot middle =
            REPOSITORY
                .detail(c, ADMIN, new ScenarioDetailRequestData(new ScriptFileId(10)))
                .orElseThrow();
        assertEquals(30, middle.metadata().previousFileId().orElseThrow().value());
        assertEquals(FIXTURE_01_A_D193F9D6, middle.metadata().previousTitle().orElseThrow());
        assertEquals(20, middle.metadata().nextFileId().orElseThrow().value());
        assertEquals("chapter B", middle.metadata().nextTitle().orElseThrow());
        ScenarioDetailSnapshot last =
            REPOSITORY
                .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(20)))
                .orElseThrow();
        assertEquals(10, last.metadata().previousFileId().orElseThrow().value());
        assertTrue(last.metadata().nextFileId().isEmpty());
      }
    }
    for (String blank : Arrays.asList(null, "", "  ", "\u2003")) {
      try (Connection c = database.admin();
          PreparedStatement s =
              c.prepareStatement(
                  "update schubert.script_files set chapter_title=null,section_code=? where id=10")) {
        s.setString(1, blank);
        s.executeUpdate();
      }
      try (Connection c = read()) {
        assertEquals(
            "f10.ks",
            REPOSITORY
                .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(10)))
                .orElseThrow()
                .metadata()
                .displayTitle());
        assertEquals(
            "f10.ks",
            REPOSITORY
                .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30)))
                .orElseThrow()
                .metadata()
                .nextTitle()
                .orElseThrow());
        assertEquals(
            "f10.ks",
            REPOSITORY
                .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(20)))
                .orElseThrow()
                .metadata()
                .previousTitle()
                .orElseThrow());
      }
    }
    file(5, 1, 3, "03_Z", null);
    try (Connection c = read()) {
      ScenarioDetailSnapshot empty =
          REPOSITORY
              .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(5)))
              .orElseThrow();
      assertTrue(empty.records().isEmpty());
      assertEquals(DeliveryMode.INLINE, empty.metadata().deliveryMode());
      assertTrue(
          REPOSITORY
              .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(9999)))
              .isEmpty());
    }
  }

  @Test
  void ptScn008D02AllVoiceRowsAndDataHaveIndependentByteOffsets() throws Exception {
    try (Connection c = read()) {
      ScenarioDetailSnapshot snapshot =
          REPOSITORY
              .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30)))
              .orElseThrow();
      byte[] metadata = blank(1728);
      put(metadata, 0, numeric(12, 30));
      put(metadata, 12, FIXTURE_NUKITASHI1_F97F2EAE);
      put(metadata, 24, FIXTURE_CHAPTER_A_E3A27D05);
      put(metadata, 280, "script/f30.ks");
      put(metadata, 1060, "10");
      put(metadata, 1072, "02_B");
      put(metadata, 1328, "I");
      put(metadata, 1621, numeric(12, 0));
      put(metadata, 1697, numeric(6, 0));
      put(metadata, 1703, numeric(9, 0));
      List<byte[]> records =
          List.of(
              detailRecord(
                  100,
                  1,
                  11,
                  FIXTURE_DIALOGUE_37AC104E,
                  FIXTURE_ALICE_1EA1F9A4,
                  "Alpha 100% x_y \\ tail",
                  1,
                  800),
              detailRecord(
                  100,
                  1,
                  11,
                  FIXTURE_DIALOGUE_37AC104E,
                  FIXTURE_ALICE_1EA1F9A4,
                  "Alpha 100% x_y \\ tail",
                  2,
                  700),
              detailRecord(
                  200,
                  2,
                  22,
                  FIXTURE_DIALOGUE_37AC104E,
                  FIXTURE_BOB_2ABF6B98,
                  "Beta O'Reilly",
                  0,
                  0));
      assertPayload(
          new TypedPayloadValues(
              new LayoutId("SCNRSP01"), snapshot.metadata(), new ArrayList<>(snapshot.records())),
          metadata,
          records);
      assertThrows(UnsupportedOperationException.class, () -> snapshot.records().clear());
      assertEquals("ScenarioDetailSnapshot[recordCount=3]", snapshot.toString());
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertTrue(c.isReadOnly());
      ScenarioDetailSnapshot narration =
          REPOSITORY
              .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(10)))
              .orElseThrow();
      assertArrayEquals(
          detailRecord(300, 1, 33, FIXTURE_NARRATION_320AF5F0, "", "alpha xy", 0, 0),
          rawDetail(narration.metadata(), narration.records().getFirst()));
    }
    sql("update schubert.script_entries set speaker_label=E'ignored\\tlabel' where id=100");
    try (Connection c = read()) {
      assertEquals(
          FIXTURE_ALICE_1EA1F9A4,
          ((ScenarioSearchRecord)
                  REPOSITORY
                      .search(c, USER, request("\\%", "", "", "", "", "", 1))
                      .records()
                      .getFirst())
              .speakerName()
              .orElseThrow());
    }
    sql("update schubert.speakers set name=E'invalid\\tname' where id=1");
    try (Connection c = read()) {
      failure(
          () -> REPOSITORY.search(c, USER, request("\\%", "", "", "", "", "", 1)),
          ResultCode.TEMPORARY_FAILURE);
      failure(
          () -> REPOSITORY.detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30))),
          ResultCode.TEMPORARY_FAILURE);
    }
  }

  @Test
  void ptScn008D03CountsExpandedRecordsAndBoundsSnapshotBeforeFileIo() throws Exception {
    for (int count : new int[] {0, 1, 200, 201, 10000, 10001}) {
      seedDetailEntries(count);
      try (Connection c = read()) {
        if (count == 10001) {
          failure(
              () -> REPOSITORY.detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30))),
              ResultCode.RESOURCE_LIMIT);
        } else {
          ScenarioDetailSnapshot snapshot =
              REPOSITORY
                  .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30)))
                  .orElseThrow();
          assertEquals(count, snapshot.records().size());
          assertEquals(DeliveryMode.INLINE, snapshot.metadata().deliveryMode());
          assertEquals(
              0,
              snapshot.metadata().fileRecordCount()); // Snapshot metadata is not a file response.
          if (count > 0) {
            assertEquals(count, snapshot.records().getLast().entrySequence());
            assertArrayEquals(
                detailRecord(count, count, count, FIXTURE_NARRATION_320AF5F0, "", "row", 0, 0),
                rawDetail(snapshot.metadata(), snapshot.records().getLast()));
          }
        }
      }
    }
    seedDetailEntries(1);
    sql("truncate schubert.audio_files cascade");
    sql(
        """
        insert into schubert.audio_files(id,game_id,storage_relative_path,display_path,file_name,basename,
          audio_role,byte_size,sha256,created_at)
        select 10000+i,1,'scenario/a'||i||'.ogg','voice/a'||(10000+i)||'.ogg','a'||i||'.ogg','a'||i,
          'voice',1,repeat('a',64),'2026-09-01Z' from generate_series(1,999) i;
        insert into schubert.entry_audio_links(entry_id,audio_file_id,game_id,link_type,display_order,created_at)
        select 1,10000+i,1,'voice',i,'2026-09-01Z' from generate_series(1,999) i
        """);
    try (Connection c = read()) {
      ScenarioDetailSnapshot snapshot =
          REPOSITORY
              .detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30)))
              .orElseThrow();
      assertEquals(999, snapshot.records().size());
      assertEquals(1, snapshot.records().getLast().entrySequence());
      assertArrayEquals(
          detailRecord(1, 1, 1, FIXTURE_NARRATION_320AF5F0, "", "row", 999, 10999),
          rawDetail(snapshot.metadata(), snapshot.records().getLast()));
    }
  }

  @Test
  void ptScn008D04NullMetadataSqlAndCompoundCloseFaultsStayBounded() throws Exception {
    try (Connection c = read()) {
      ScenarioDetailRequestData request = new ScenarioDetailRequestData(new ScriptFileId(30));
      assertThrows(NullPointerException.class, () -> REPOSITORY.detail(null, USER, request));
      assertThrows(NullPointerException.class, () -> REPOSITORY.detail(c, null, request));
      assertThrows(NullPointerException.class, () -> REPOSITORY.detail(c, USER, null));
      for (String method :
          List.of(
              "prepareStatement",
              "setLong",
              "executeQuery",
              "next",
              "getObject",
              FIXTURE_GETLONG_7D3C0BFE,
              FIXTURE_GETSTRING_B3B802ED,
              FIXTURE_CLOSE_97959247)) {
        Connection broken =
            intercept(
                c,
                (target, m, args) -> {
                  if (m.getName().equals(method)) {
                    if (method.equals(FIXTURE_CLOSE_97959247)) invoke(target, m, args);
                    throw new SQLException(FIXTURE_SYNTHETIC_SQL_MUST_NOT_ESCAPE_6962B758);
                  }
                  return invoke(target, m, args);
                });
        failure(() -> REPOSITORY.detail(broken, USER, request), ResultCode.TEMPORARY_FAILURE);
      }
      ScenarioDetailSnapshot valid = REPOSITORY.detail(c, USER, request).orElseThrow();
      assertThrows(NullPointerException.class, () -> new ScenarioDetailSnapshot(null, List.of()));
      assertThrows(
          NullPointerException.class, () -> new ScenarioDetailSnapshot(valid.metadata(), null));
      assertThrows(
          NullPointerException.class,
          () ->
              new ScenarioDetailSnapshot(
                  valid.metadata(), Arrays.asList((ScenarioEntryRecord) null)));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new ScenarioDetailSnapshot(
                  valid.metadata(), Collections.nCopies(10001, valid.records().getFirst())));
      ScenarioDetailResponseData file =
          new ScenarioDetailResponseData(
              new ScriptFileId(30),
              G1,
              "title",
              DisplayPath.of("script/f30.ks"),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              DeliveryMode.FILE,
              Optional.empty(),
              Optional.empty(),
              0,
              Optional.empty(),
              0,
              0);
      assertThrows(
          IllegalArgumentException.class, () -> new ScenarioDetailSnapshot(file, List.of()));
      assertThrows(
          NullPointerException.class,
          () -> PayloadSemanticValidator.validateScenarioSequence(null));
      assertThrows(
          NullPointerException.class,
          () ->
              PayloadSemanticValidator.validateScenarioSequence(
                  Arrays.asList((FieldValueSet) null)));
    }
    sql("update schubert.script_entries set line_number=null where id=100");
    try (Connection c = read()) {
      failure(
          () -> REPOSITORY.detail(c, USER, new ScenarioDetailRequestData(new ScriptFileId(30))),
          ResultCode.TEMPORARY_FAILURE);
    }
    seedDetailEntries(10001);
    try (Connection c = read()) {
      Connection broken =
          intercept(
              c,
              (target, m, args) -> {
                if (m.getName().equals(FIXTURE_CLOSE_97959247)) {
                  invoke(target, m, args);
                  throw new SQLException(FIXTURE_SYNTHETIC_SQL_MUST_NOT_ESCAPE_6962B758);
                }
                return invoke(target, m, args);
              });
      failure(
          () ->
              REPOSITORY.detail(broken, USER, new ScenarioDetailRequestData(new ScriptFileId(30))),
          ResultCode.TEMPORARY_FAILURE);
    }
  }

  private static void seedDetailEntries(int count) throws SQLException {
    sql("truncate schubert.script_entries cascade");
    sql(
        """
        insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,
          line_number,entry_type,body,raw_block,created_at)
        select i,1,30,i,i-1,i,'narration','row','synthetic','2026-09-01Z' from generate_series(1,%d) i
        """
            .formatted(count));
  }

  private static byte[] rawDetail(ScenarioDetailResponseData metadata, ScenarioEntryRecord record) {
    return PayloadCodec.standard()
        .encode(
            new PayloadValues(
                new LayoutId("SCNRSP01"), metadata.fields(), List.of(record.fields())),
            false)
        .copyRecords()
        .getFirst();
  }

  private static byte[] detailRecord(
      long id,
      int sequence,
      int line,
      String type,
      String speaker,
      String body,
      int audioSequence,
      long audio) {
    byte[] r = blank(4800);
    put(r, 0, numeric(12, id));
    put(r, 12, numeric(6, sequence));
    put(r, 18, numeric(8, line));
    put(r, 26, type);
    put(r, 36, speaker);
    put(r, 164, body);
    put(r, 4260, numeric(3, audioSequence));
    if (audio != 0) {
      put(r, 4263, Long.toString(audio));
      put(r, 4275, "voice/a" + audio + ".ogg");
    }
    return r;
  }

  private static Connection intercept(Connection connection, Interceptor action) {
    return wrap(
        Connection.class,
        connection,
        (target, m, args) -> {
          Object result = action.invoke(target, m, args);
          if (result instanceof PreparedStatement statement)
            return wrap(
                PreparedStatement.class,
                statement,
                (t, method, a) -> {
                  Object value = action.invoke(t, method, a);
                  return value instanceof ResultSet rows
                      ? wrap(ResultSet.class, rows, action)
                      : value;
                });
          return result;
        });
  }

  private static ScenarioSearchRequestData request(
      String q, String game, String speaker, String chapter, String type, String voice, int page) {
    return new ScenarioSearchRequestData(
        optional(q),
        optional(game).map(g -> g.equals(FIXTURE_NUKITASHI1_F97F2EAE) ? G1 : G2),
        optional(speaker),
        optional(chapter),
        optional(type)
            .map(
                t ->
                    t.equals(FIXTURE_DIALOGUE_37AC104E) ? EntryType.DIALOGUE : EntryType.NARRATION),
        optional(voice).map(v -> v.equals("1") ? VoiceCondition.PRESENT : VoiceCondition.ABSENT),
        page,
        100);
  }

  private static Optional<String> optional(String value) {
    return value.isEmpty() ? Optional.empty() : Optional.of(value);
  }

  private static Connection read() throws SQLException {
    Connection c = database.api();
    c.setReadOnly(true);
    c.setAutoCommit(false);
    return c;
  }

  private static void sql(String sql) throws SQLException {
    try (Connection c = database.admin();
        Statement s = c.createStatement()) {
      s.execute(sql);
    }
  }

  private static void file(long id, int game, int order, String section, String chapter)
      throws SQLException {
    try (Connection c = database.admin();
        PreparedStatement s =
            c.prepareStatement(
                """
        insert into schubert.script_files(id,game_id,display_order,storage_relative_path,display_path,file_name,
          section_code,chapter_title,sha256,byte_size,created_at) values(?,?,?,'scenario/f'||?||'.ks','script/f'||?||'.ks','f'||?||'.ks',?,?,repeat('a',64),1,'2026-09-01Z')
        """)) {
      s.setLong(1, id);
      s.setInt(2, game);
      s.setInt(3, order);
      s.setLong(4, id);
      s.setLong(5, id);
      s.setLong(6, id);
      s.setString(7, section);
      s.setString(8, chapter);
      s.executeUpdate();
    }
  }

  private static void entry(
      long id,
      int game,
      long file,
      long order,
      int index,
      int line,
      Integer speaker,
      String label,
      String body)
      throws SQLException {
    try (Connection c = database.admin();
        PreparedStatement s =
            c.prepareStatement(
                """
        insert into schubert.script_entries(id,game_id,script_file_id,display_order,entry_index,line_number,
          entry_type,speaker_id,speaker_label,body,raw_block,created_at) values(?,?,?,?,?,?,?,?,?,?,'synthetic','2026-09-01Z')
        """)) {
      s.setLong(1, id);
      s.setInt(2, game);
      s.setLong(3, file);
      s.setLong(4, order);
      s.setInt(5, index);
      s.setInt(6, line);
      s.setString(7, speaker == null ? FIXTURE_NARRATION_320AF5F0 : FIXTURE_DIALOGUE_37AC104E);
      s.setObject(8, speaker);
      s.setString(9, label);
      s.setString(10, body);
      s.executeUpdate();
    }
  }

  private static void assertIds(Connection c, ScenarioSearchRequestData request, long... ids) {
    assertEquals(
        Arrays.stream(ids).boxed().toList(),
        REPOSITORY.search(c, USER, request).records().stream()
            .map(r -> ((ScenarioSearchRecord) r).entryId().value())
            .toList());
  }

  private static FixedPayload encoded(TypedPayloadValues values) {
    return PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false);
  }

  private static void assertPayload(TypedPayloadValues actual, byte[] data, List<byte[]> records) {
    FixedPayload payload = encoded(actual);
    assertArrayEquals(data, payload.copyData());
    assertEquals(records.size(), payload.copyRecords().size());
    for (int i = 0; i < records.size(); i++)
      assertArrayEquals(records.get(i), payload.copyRecords().get(i), "independent record " + i);
  }

  private static byte[] blank(int length) {
    byte[] result = new byte[length];
    Arrays.fill(result, (byte) ' ');
    return result;
  }

  private static byte[] numeric(int length, long value) {
    return String.format(Locale.ROOT, "%0" + length + "d", value)
        .getBytes(StandardCharsets.US_ASCII);
  }

  private static void put(byte[] target, int offset, String value) {
    put(target, offset, value.getBytes(StandardCharsets.UTF_8));
  }

  private static void put(byte[] target, int offset, byte[] value) {
    System.arraycopy(value, 0, target, offset, value.length);
  }

  private static byte[] game(String code, String title, int order) {
    byte[] r = blank(272);
    put(r, 0, code);
    put(r, 12, title);
    put(r, 268, numeric(3, order));
    return r;
  }

  private static byte[] speaker(long id, String name, int count) {
    byte[] r = blank(152);
    put(r, 0, numeric(12, id));
    put(r, 12, name);
    put(r, 140, numeric(9, count));
    return r;
  }

  private static byte[] route(int prefix, String name, int count) {
    byte[] r = blank(72);
    put(r, 0, numeric(2, prefix));
    put(r, 2, name);
    put(r, 66, numeric(6, count));
    return r;
  }

  private static byte[] fileData(String game, int prefix, String route, int count) {
    byte[] r = blank(88);
    put(r, 0, game);
    put(r, 12, numeric(2, prefix));
    put(r, 14, route);
    put(r, 78, numeric(9, count));
    return r;
  }

  private static byte[] fileRecord(long id, String title, int count) {
    byte[] r = blank(800);
    put(r, 0, numeric(12, id));
    put(r, 12, title);
    put(r, 268, "script/f" + id + ".ks");
    put(r, 780, numeric(6, count));
    return r;
  }

  private static byte[] page(int effective, long total, int pages, long first, long last) {
    byte[] r = blank(48);
    put(r, 0, numeric(6, effective));
    put(r, 6, "100");
    put(r, 9, numeric(9, total));
    put(r, 18, numeric(6, pages));
    put(r, 24, numeric(9, first));
    put(r, 33, numeric(9, last));
    return r;
  }

  private static void failure(
      org.junit.jupiter.api.function.Executable action, ResultCode expected) {
    ScenarioQueryException e = assertThrows(ScenarioQueryException.class, action);
    assertEquals(expected, e.resultCode());
    assertEquals("scenario query is unavailable", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }

  @FunctionalInterface
  private interface Interceptor {
    Object invoke(Object target, Method method, Object[] args) throws Throwable;
  }

  private static <T> T wrap(Class<T> type, T target, Interceptor action) {
    return type.cast(
        Proxy.newProxyInstance(
            type.getClassLoader(),
            new Class<?>[] {type},
            (p, m, a) -> action.invoke(target, m, a)));
  }

  private static Object invoke(Object target, Method method, Object[] args) throws Throwable {
    try {
      return method.invoke(target, args);
    } catch (InvocationTargetException e) {
      throw e.getCause();
    }
  }
}
