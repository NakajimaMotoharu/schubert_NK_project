package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.media.AnimationListRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AnimationMenuResponseData;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicSectionRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-MED-008..014; real production DDL/grants, synthetic master and independent UI235 bytes. */
class MediaRepositoryTest {
  private static final String FIXTURE_MUSIC_D5800D43 = "MUSIC";
  private static final String FIXTURE_MUSIC_0_A0B30B4A = "music-0";
  private static final String FIXTURE_TRACK_43CA9734 = "Track";
  private static final String FIXTURE_BGM_2427B415 = "BGM";
  private static final String FIXTURE_AUDREQ01_7A5DA392 = "AUDREQ01";
  private static final String FIXTURE_AUDIO_OGG_96A5CB00 = "audio/ogg";
  private static final String FIXTURE_MAIN_Z_82616435 = "main-z";
  private static final String FIXTURE_FIRST_81C9759D = "First";
  private static final String FIXTURE_MAIN_7FCC0BE2 = "MAIN";
  private static final String FIXTURE_SUB_B8F15D32 = "sub";
  private static final String FIXTURE_SUB_574FA518 = "Sub";
  private static final String FIXTURE_SUBTRACK_BF9F5649 = "SUBTRACK";
  private static final String FIXTURE_OPENING_583FF6F7 = "opening";
  private static final String FIXTURE_VIDEO_MP4_9A1C8BFA = "video/mp4";
  private static final String FIXTURE_MISSING_4B62D186 = "missing";
  private static final String FIXTURE_OGG_09018BA2 = ".ogg";
  private static final String FIXTURE_MUSIC_80DD0E40 = "music/";
  private static final String FIXTURE_MP4_90A2AC73 = ".mp4";
  private static final String FIXTURE_MEDIA_5FBF5FE3 = "media";
  private static final String FIXTURE_STORAGE_RELATIVE_PATH_3B93240E = "storage_relative_path";
  private static final String FIXTURE_FILE_NAME_13C51B3C = "file_name";
  private static final String FIXTURE_OVERRIDESTRING_6A02E9F8 = "overrideString";
  private static final String FIXTURE_OVERRIDELONG_54987068 = "overrideLong";
  private static final String FIXTURE_NUMERICNULL_C13B0A60 = "numericNull";
  private static final String FIXTURE_CATEGORY_DE46A45C = "category";
  private static final String FIXTURE_OTHER_D448C0E0 = "other";
  private static final String FIXTURE_FROZEN_KEY_959C182D = "frozen-key";
  private static final String FIXTURE_ANIMATION_4D33DF79 = "animation";
  private static final String FIXTURE_CATEGORIES_DCB1A2E4 = "categories";
  private static final String FIXTURE_SECTIONS_4914C922 = "sections";
  private static final String FIXTURE_TRACKS_7FF43291 = "tracks";
  private static final String FIXTURE_VIDEO_C9B6F4C2 = "VIDEO";
  @TempDir static Path root;
  private static ApiLogDatabaseFixture database;
  private static final MediaRepository QUERIES = new MediaRepository();
  private static final AuthenticatedActor USER = new AuthenticatedActor(7, "reader", Role.USER);
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(8, "admin", Role.ADMIN);
  private static final AnimationListRequestData MAIN =
      new AnimationListRequestData(AnimationListCategory.MAIN);

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void clear() throws Exception {
    sql("truncate schubert.media_assets,schubert.audio_files cascade");
  }

  @Test
  void med036DecodedRequestsDispatchAllEightStoredQueries() throws Exception {
    audio();
    videos();
    asset(
        100,
        FIXTURE_MUSIC_D5800D43,
        FIXTURE_MUSIC_0_A0B30B4A,
        FIXTURE_TRACK_43CA9734,
        FIXTURE_BGM_2427B415,
        "ゲーム",
        null,
        null,
        "N",
        1);
    try (var c = read()) {
      for (String layout :
          List.of(
              FIXTURE_AUDREQ01_7A5DA392,
              "ANMREQ01",
              "ANLREQ01",
              "VIDREQ01",
              "MCTREQ01",
              "MCSREQ01",
              "MTRREQ01",
              "MEDREQ01")) {
        var request =
            dev.codex.schubert.nk.api.application.media.MediaRequest.decode(
                dev.codex.schubert.nk.api.application.media.MediaRequestFixture.message(
                    layout,
                    dev.codex.schubert.nk.api.application.media.MediaRequestFixture.data(layout)));
        var result = request.query(QUERIES, c, USER).orElseThrow();
        assertEquals(layout.replace("REQ", "RSP"), result.layoutId().value());
        switch (layout) {
          case FIXTURE_AUDREQ01_7A5DA392 ->
              assertWire(
                  result,
                  descriptorBytes(
                      "700",
                      "scenario/G/audio/700.ogg",
                      "Audio nice.ogg",
                      FIXTURE_AUDIO_OGG_96A5CB00,
                      "A"),
                  List.of());
          case "ANMREQ01" ->
              assertWire(result, "0030011005      ".getBytes(StandardCharsets.US_ASCII), List.of());
          case "ANLREQ01" ->
              assertWire(
                  result,
                  count(8, 6, 3),
                  List.of(
                      animation(
                          FIXTURE_MAIN_Z_82616435,
                          FIXTURE_FIRST_81C9759D,
                          FIXTURE_MAIN_7FCC0BE2,
                          "v/30.mp4",
                          null,
                          1),
                      animation("main-a", "Second", FIXTURE_MAIN_7FCC0BE2, "v/10.mp4", null, 2),
                      animation(
                          FIXTURE_SUB_B8F15D32,
                          FIXTURE_SUB_574FA518,
                          FIXTURE_SUBTRACK_BF9F5649,
                          "v/20.mp4",
                          FIXTURE_MAIN_Z_82616435,
                          3)));
          case "VIDREQ01" -> {
            byte[] expected = blank(1808);
            System.arraycopy(
                descriptorBytes(
                    FIXTURE_OPENING_583FF6F7,
                    "video/50.mp4",
                    "file.mp4",
                    FIXTURE_VIDEO_MP4_9A1C8BFA,
                    "I"),
                0,
                expected,
                0,
                1024);
            put(expected, 1024, "Opening");
            put(expected, 1280, "OPENING");
            put(expected, 1296, "v/50.mp4");
            assertWire(result, expected, List.of());
          }
          case "MCTREQ01" ->
              assertWire(result, count(8, 6, 1), List.of(group(72, 64, FIXTURE_BGM_2427B415, 1)));
          case "MCSREQ01" -> assertWire(result, count(8, 6, 1), List.of(group(136, 128, "ゲーム", 1)));
          case "MTRREQ01" ->
              assertWire(
                  result,
                  count(16, 9, 1),
                  List.of(
                      track(
                          FIXTURE_MUSIC_0_A0B30B4A,
                          FIXTURE_TRACK_43CA9734,
                          FIXTURE_BGM_2427B415,
                          "ゲーム",
                          "v/100.ogg",
                          null,
                          "N",
                          1)));
          case "MEDREQ01" ->
              assertWire(
                  result,
                  descriptorBytes(
                      FIXTURE_MUSIC_0_A0B30B4A,
                      "music/100.ogg",
                      "file.ogg",
                      FIXTURE_AUDIO_OGG_96A5CB00,
                      "A"),
                  List.of());
          default -> fail("unexpected query");
        }
        assertTrue(c.isReadOnly());
        assertFalse(c.getAutoCommit());
        assertFalse(c.isClosed());
      }
      for (String layout : List.of(FIXTURE_AUDREQ01_7A5DA392, "VIDREQ01", "MEDREQ01")) {
        byte[] data = dev.codex.schubert.nk.api.application.media.MediaRequestFixture.data(layout);
        if (layout.equals(FIXTURE_AUDREQ01_7A5DA392)) put(data, 0, "000000000701");
        else put(data, 0, FIXTURE_MISSING_4B62D186);
        var request =
            dev.codex.schubert.nk.api.application.media.MediaRequest.decode(
                dev.codex.schubert.nk.api.application.media.MediaRequestFixture.message(
                    layout, data));
        assertTrue(request.query(QUERIES, c, ADMIN).isEmpty());
      }
    }
    try (var invalid = database.api()) {
      var request =
          dev.codex.schubert.nk.api.application.media.MediaRequest.decode(
              dev.codex.schubert.nk.api.application.media.MediaRequestFixture.message(
                  "MCTREQ01", new byte[0]));
      failure(ResultCode.TEMPORARY_FAILURE, () -> request.query(QUERIES, invalid, USER));
    }
  }

  /** PT-MED-015: UI235 independent MEDIA1024 for Audio and five Music formats, both modes. */
  @Test
  void audioAndMusicMetadataUseCanonicalIdsAndAllApprovedFormats() throws Exception {
    audio();
    try (var c = read()) {
      for (var mode : ContentDisposition.values()) {
        assertWire(
            QUERIES
                .audioMetadata(c, USER, new AudioDescriptorRequestData(new AudioId(700), mode))
                .orElseThrow(),
            descriptorBytes(
                "700",
                "scenario/G/audio/700.ogg",
                "Audio nice.ogg",
                FIXTURE_AUDIO_OGG_96A5CB00,
                mode.wireValue()),
            List.of());
      }
      assertTrue(
          QUERIES
              .audioMetadata(
                  c,
                  USER,
                  new AudioDescriptorRequestData(new AudioId(701), ContentDisposition.INLINE))
              .isEmpty());
    }
    String[][] formats = {
      {".m4a", "audio/mp4"},
      {".mp3", "audio/mpeg"},
      {FIXTURE_OGG_09018BA2, FIXTURE_AUDIO_OGG_96A5CB00},
      {".wav", "audio/wav"},
      {".flac", "audio/flac"}
    };
    for (int i = 0; i < formats.length; i++) {
      int id = 100 + i;
      String suffix = formats[i][0];
      String mime = formats[i][1];
      String logical = "music-" + i;
      asset(
          id,
          FIXTURE_MUSIC_D5800D43,
          logical,
          FIXTURE_TRACK_43CA9734,
          FIXTURE_BGM_2427B415,
          "ゲーム",
          null,
          null,
          "N",
          i + 1);
      sql(
          "update schubert.media_assets set storage_relative_path='music/"
              + id
              + suffix
              + "',file_name='表示名"
              + suffix
              + "',mime_type='"
              + mime
              + "' where id="
              + id);
      try (var c = read()) {
        for (var mode : ContentDisposition.values())
          assertWire(
              QUERIES
                  .musicMetadata(c, ADMIN, new MusicDescriptorRequestData(logical, mode))
                  .orElseThrow(),
              descriptorBytes(
                  logical,
                  FIXTURE_MUSIC_80DD0E40 + id + suffix,
                  "表示名" + suffix,
                  mime,
                  mode.wireValue()),
              List.of());
      }
    }
    videos();
    try (var c = read()) {
      assertTrue(
          QUERIES
              .musicMetadata(
                  c,
                  USER,
                  new MusicDescriptorRequestData(
                      FIXTURE_OPENING_583FF6F7, ContentDisposition.INLINE))
              .isEmpty());
      assertTrue(
          QUERIES
              .musicMetadata(
                  c, USER, new MusicDescriptorRequestData("' OR '1'='1", ContentDisposition.INLINE))
              .isEmpty());
      assertTrue(
          QUERIES
              .videoMetadata(c, USER, new VideoDescriptorRequestData(FIXTURE_MUSIC_0_A0B30B4A))
              .isEmpty());
    }
  }

  /** PT-MED-016: all four public video categories and 1808 independent data bytes. */
  @Test
  void videoMetadataIncludesOpeningAndDisplayFields() throws Exception {
    videos();
    String[][] rows = {
      {FIXTURE_MAIN_Z_82616435, "30", FIXTURE_FIRST_81C9759D, FIXTURE_MAIN_7FCC0BE2},
      {FIXTURE_SUB_B8F15D32, "20", FIXTURE_SUB_574FA518, FIXTURE_SUBTRACK_BF9F5649},
      {"ova", "40", "Ova", "OVA"},
      {FIXTURE_OPENING_583FF6F7, "50", "Opening", "OPENING"}
    };
    try (var c = read()) {
      for (String[] row : rows) {
        byte[] expected = blank(1808);
        System.arraycopy(
            descriptorBytes(
                row[0],
                "video/" + row[1] + FIXTURE_MP4_90A2AC73,
                "file.mp4",
                FIXTURE_VIDEO_MP4_9A1C8BFA,
                "I"),
            0,
            expected,
            0,
            1024);
        put(expected, 1024, row[2]);
        put(expected, 1280, row[3]);
        put(expected, 1296, "v/" + row[1] + FIXTURE_MP4_90A2AC73);
        assertWire(
            QUERIES.videoMetadata(c, USER, new VideoDescriptorRequestData(row[0])).orElseThrow(),
            expected,
            List.of());
      }
      assertTrue(
          QUERIES
              .videoMetadata(c, USER, new VideoDescriptorRequestData(FIXTURE_MISSING_4B62D186))
              .isEmpty());
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertTrue(c.isReadOnly());
    }
  }

  /** PT-MED-017: absence is distinct from corrupt metadata and JDBC failure. */
  @Test
  void descriptorNullDatabaseAndMetadataFaultsNeverBecomeMissing() throws Exception {
    audio();
    videos();
    asset(
        90,
        FIXTURE_MUSIC_D5800D43,
        FIXTURE_MEDIA_5FBF5FE3,
        FIXTURE_TRACK_43CA9734,
        FIXTURE_BGM_2427B415,
        "ゲーム",
        null,
        null,
        "N",
        1);
    for (String kind : List.of("audio", "video", "music")) {
      assertThrows(NullPointerException.class, () -> metadata(kind, null, USER));
      try (var c = read()) {
        assertThrows(NullPointerException.class, () -> metadata(kind, c, null));
        for (String problem :
            List.of(
                "connection.prepareStatement",
                "statement.setString",
                "statement.executeQuery",
                "result.next",
                "result.close",
                "statement.close"))
          failure(
              ResultCode.TEMPORARY_FAILURE,
              () -> metadata(kind, fault(c, problem, null, null), USER));
        for (String column :
            List.of(
                "logical_id",
                FIXTURE_STORAGE_RELATIVE_PATH_3B93240E,
                FIXTURE_FILE_NAME_13C51B3C,
                "sha256",
                "mime_type"))
          failure(
              ResultCode.TEMPORARY_FAILURE,
              () -> metadata(kind, fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, column, null), USER));
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () ->
                metadata(
                    kind,
                    fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, "logical_id", "different"),
                    USER));
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> metadata(kind, fault(c, FIXTURE_OVERRIDELONG_54987068, "byte_size", 0L), USER));
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> metadata(kind, fault(c, FIXTURE_NUMERICNULL_C13B0A60, null, null), USER));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        assertTrue(c.isReadOnly());
      }
    }
    try (var c = read()) {
      assertThrows(NullPointerException.class, () -> QUERIES.audioMetadata(c, USER, null));
      assertThrows(NullPointerException.class, () -> QUERIES.videoMetadata(c, USER, null));
      assertThrows(NullPointerException.class, () -> QUERIES.musicMetadata(c, USER, null));
      for (String column : List.of("title", FIXTURE_CATEGORY_DE46A45C, "display_path"))
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () ->
                QUERIES.videoMetadata(
                    fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, column, null),
                    USER,
                    new VideoDescriptorRequestData(FIXTURE_OPENING_583FF6F7)));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              QUERIES.videoMetadata(
                  fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, FIXTURE_CATEGORY_DE46A45C, "UNKNOWN"),
                  USER,
                  new VideoDescriptorRequestData(FIXTURE_OPENING_583FF6F7)));
      String[][] invalid = {
        {FIXTURE_STORAGE_RELATIVE_PATH_3B93240E, "video/wrong.ogg"},
        {FIXTURE_STORAGE_RELATIVE_PATH_3B93240E, "music/wrong.bin"},
        {FIXTURE_STORAGE_RELATIVE_PATH_3B93240E, "music/../wrong.ogg"},
        {
          FIXTURE_STORAGE_RELATIVE_PATH_3B93240E,
          FIXTURE_MUSIC_80DD0E40 + "あ".repeat(84) + FIXTURE_OGG_09018BA2
        },
        {FIXTURE_FILE_NAME_13C51B3C, "wrong.mp4"},
        {FIXTURE_FILE_NAME_13C51B3C, "line\r\n.ogg"},
        {"sha256", "g".repeat(64)},
        {"mime_type", "audio/wav"}
      };
      for (String[] value : invalid)
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () ->
                metadata(
                    "music", fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, value[0], value[1]), USER));
      var renamed =
          QUERIES
              .musicMetadata(
                  fault(
                      c,
                      FIXTURE_OVERRIDESTRING_6A02E9F8,
                      FIXTURE_FILE_NAME_13C51B3C,
                      "あ".repeat(84) + FIXTURE_OGG_09018BA2),
                  USER,
                  new MusicDescriptorRequestData(FIXTURE_MEDIA_5FBF5FE3, ContentDisposition.INLINE))
              .orElseThrow();
      assertWire(
          renamed,
          descriptorBytes(
              FIXTURE_MEDIA_5FBF5FE3,
              "music/90.ogg",
              "あ".repeat(84) + FIXTURE_OGG_09018BA2,
              FIXTURE_AUDIO_OGG_96A5CB00,
              "I"),
          List.of());
      var segmented =
          QUERIES
              .musicMetadata(
                  fault(
                      c,
                      FIXTURE_OVERRIDESTRING_6A02E9F8,
                      FIXTURE_STORAGE_RELATIVE_PATH_3B93240E,
                      FIXTURE_MUSIC_80DD0E40 + "a".repeat(251) + FIXTURE_OGG_09018BA2),
                  USER,
                  new MusicDescriptorRequestData(FIXTURE_MEDIA_5FBF5FE3, ContentDisposition.INLINE))
              .orElseThrow();
      assertWire(
          segmented,
          descriptorBytes(
              FIXTURE_MEDIA_5FBF5FE3,
              FIXTURE_MUSIC_80DD0E40 + "a".repeat(251) + FIXTURE_OGG_09018BA2,
              "file.ogg",
              FIXTURE_AUDIO_OGG_96A5CB00,
              "I"),
          List.of());
    }
  }

  private static Optional<TypedPayloadValues> metadata(
      String kind, Connection c, AuthenticatedActor actor) {
    return switch (kind) {
      case "audio" ->
          QUERIES.audioMetadata(
              c,
              actor,
              new AudioDescriptorRequestData(new AudioId(700), ContentDisposition.INLINE));
      case "video" ->
          QUERIES.videoMetadata(c, actor, new VideoDescriptorRequestData(FIXTURE_OPENING_583FF6F7));
      case "music" ->
          QUERIES.musicMetadata(
              c,
              actor,
              new MusicDescriptorRequestData(FIXTURE_MEDIA_5FBF5FE3, ContentDisposition.INLINE));
      default -> throw new AssertionError(kind);
    };
  }

  private static void audio() throws SQLException {
    sql(
        "insert into schubert.audio_files(id,game_id,storage_relative_path,display_path,file_name,basename,audio_role,byte_size,sha256,created_at) values(700,1,'scenario/G/audio/700.ogg','voice/700.ogg','Audio nice.ogg','700','voice',123,repeat('a',64),'2026-09-08Z')");
  }

  private static byte[] descriptorBytes(
      String id, String path, String name, String mime, String disposition) {
    byte[] expected = blank(1024);
    put(expected, 0, id);
    put(expected, 64, path);
    put(expected, 576, name);
    number(expected, 832, 12, 123);
    put(expected, 844, "a".repeat(64));
    put(expected, 908, mime);
    put(expected, 972, disposition);
    return expected;
  }

  @Test
  void animationMenuCountsStoredCategoriesWithoutFilesystem() throws Exception {
    try (var c = read()) {
      assertWire(
          QUERIES.animationMenu(c, USER),
          "0000000000      ".getBytes(StandardCharsets.US_ASCII),
          List.of());
    }
    videos();
    asset(
        60,
        FIXTURE_MUSIC_D5800D43,
        "ignored",
        "ignored",
        FIXTURE_BGM_2427B415,
        "ゲーム",
        null,
        null,
        "N",
        1);
    try (var c = read()) {
      assertWire(
          QUERIES.animationMenu(c, USER),
          "0030011005      ".getBytes(StandardCharsets.US_ASCII),
          List.of());
      assertWire(
          QUERIES.animationMenu(c, ADMIN),
          "0030011005      ".getBytes(StandardCharsets.US_ASCII),
          List.of());
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      assertTrue(c.isReadOnly());
    }
    sql("update schubert.media_assets set category='UNKNOWN' where logical_id='opening'");
    try (var c = read()) {
      failure(ResultCode.TEMPORARY_FAILURE, () -> QUERIES.animationMenu(c, USER));
    }
    sql(
        "update schubert.media_assets set category='OPENING' where logical_id in ('opening','ova')");
    try (var c = read()) {
      failure(ResultCode.TEMPORARY_FAILURE, () -> QUERIES.animationMenu(c, USER));
    }
  }

  @Test
  void animationRowsPreserveParentAndDisplayOrder() throws Exception {
    videos();
    List<byte[]> expected =
        List.of(
            animation(
                FIXTURE_MAIN_Z_82616435,
                FIXTURE_FIRST_81C9759D,
                FIXTURE_MAIN_7FCC0BE2,
                "v/30.mp4",
                null,
                1),
            animation("main-a", "Second", FIXTURE_MAIN_7FCC0BE2, "v/10.mp4", null, 2),
            animation(
                FIXTURE_SUB_B8F15D32,
                FIXTURE_SUB_574FA518,
                FIXTURE_SUBTRACK_BF9F5649,
                "v/20.mp4",
                FIXTURE_MAIN_Z_82616435,
                3));
    try (var c = read()) {
      var value = QUERIES.animationList(c, USER, MAIN);
      assertWire(value, count(8, 6, 3), expected);
      assertWire(QUERIES.animationList(c, ADMIN, MAIN), count(8, 6, 3), expected);
      assertThrows(UnsupportedOperationException.class, () -> value.records().clear());
      assertWire(
          QUERIES.animationList(c, USER, new AnimationListRequestData(AnimationListCategory.OVA)),
          count(8, 6, 1),
          List.of(animation("ova", "Ova", "OVA", "v/40.mp4", null, 4)));
    }
    sql("update schubert.media_assets set parent_logical_id='ova' where logical_id='sub'");
    try (var c = read()) {
      failure(ResultCode.TEMPORARY_FAILURE, () -> QUERIES.animationList(c, USER, MAIN));
    }
    clear();
    try (var c = read()) {
      assertWire(QUERIES.animationList(c, USER, MAIN), count(8, 6, 0), List.of());
    }
  }

  @Test
  void musicGroupsUseApprovedCategoryAndSectionOrder() throws Exception {
    String[][] groups = {
      {"ZZ", FIXTURE_OTHER_D448C0E0},
      {FIXTURE_BGM_2427B415, "ゲーム"},
      {"曲", "アニメ"},
      {"曲", "ゲーム"},
      {"曲", "キャラクターソング"},
      {"曲", "ZZ"},
      {"曲", "AA"},
      {"AA", FIXTURE_OTHER_D448C0E0},
      {"曲", "ゲーム"}
    };
    for (int i = 0; i < groups.length; i++)
      asset(
          i + 1,
          FIXTURE_MUSIC_D5800D43,
          "m" + i,
          FIXTURE_TRACK_43CA9734,
          groups[i][0],
          groups[i][1],
          null,
          null,
          "N",
          i + 1);
    try (var c = read()) {
      assertWire(
          QUERIES.musicCategories(c, USER),
          count(8, 6, 4),
          List.of(
              group(72, 64, "曲", 6),
              group(72, 64, FIXTURE_BGM_2427B415, 1),
              group(72, 64, "AA", 1),
              group(72, 64, "ZZ", 1)));
      assertWire(
          QUERIES.musicSections(c, USER, new MusicSectionRequestData("曲")),
          count(8, 6, 5),
          List.of(
              group(136, 128, "ゲーム", 2),
              group(136, 128, "アニメ", 1),
              group(136, 128, "キャラクターソング", 1),
              group(136, 128, "AA", 1),
              group(136, 128, "ZZ", 1)));
      assertWire(
          QUERIES.musicSections(c, USER, new MusicSectionRequestData(FIXTURE_MISSING_4B62D186)),
          count(8, 6, 0),
          List.of());
    }
    asset(
        20,
        FIXTURE_MUSIC_D5800D43,
        "quoted",
        FIXTURE_TRACK_43CA9734,
        "O'Reilly",
        "quote",
        null,
        null,
        "N",
        20);
    try (var c = read()) {
      assertWire(
          QUERIES.musicSections(c, USER, new MusicSectionRequestData("O'Reilly")),
          count(8, 6, 1),
          List.of(group(136, 128, "quote", 1)));
      assertWire(
          QUERIES.musicSections(c, USER, new MusicSectionRequestData("' OR '1'='1")),
          count(8, 6, 0),
          List.of());
    }
    clear();
    try (var c = read()) {
      assertWire(QUERIES.musicCategories(c, USER), count(8, 6, 0), List.of());
    }
  }

  @Test
  void musicTracksReadFrozenPairsAndLogicalIdTies() throws Exception {
    asset(
        50,
        FIXTURE_MUSIC_D5800D43,
        "z-main",
        "Unrelated title",
        "曲",
        "ゲーム",
        null,
        FIXTURE_FROZEN_KEY_959C182D,
        "M",
        1);
    asset(
        10,
        FIXTURE_MUSIC_D5800D43,
        "a-inst",
        "No suffix inference",
        "曲",
        "ゲーム",
        null,
        FIXTURE_FROZEN_KEY_959C182D,
        "I",
        1);
    asset(30, FIXTURE_MUSIC_D5800D43, "lonely", "Solo", "曲", "ゲーム", null, "solo-key", "M", 2);
    asset(
        60, FIXTURE_MUSIC_D5800D43, "bgm", "Bgm", FIXTURE_BGM_2427B415, "ゲーム", null, null, "N", 1);
    asset(
        70,
        FIXTURE_MUSIC_D5800D43,
        FIXTURE_OTHER_D448C0E0,
        "Other",
        "曲",
        "アニメ",
        null,
        FIXTURE_OTHER_D448C0E0,
        "M",
        1);
    try (var c = read()) {
      assertWire(
          QUERIES.musicTracks(c, USER, new MusicTrackRequestData("曲", "ゲーム")),
          count(16, 9, 3),
          List.of(
              track(
                  "a-inst",
                  "No suffix inference",
                  "曲",
                  "ゲーム",
                  "v/10.ogg",
                  FIXTURE_FROZEN_KEY_959C182D,
                  "I",
                  1),
              track(
                  "z-main",
                  "Unrelated title",
                  "曲",
                  "ゲーム",
                  "v/50.ogg",
                  FIXTURE_FROZEN_KEY_959C182D,
                  "M",
                  1),
              track("lonely", "Solo", "曲", "ゲーム", "v/30.ogg", "solo-key", "M", 2)));
      assertWire(
          QUERIES.musicTracks(c, ADMIN, new MusicTrackRequestData(FIXTURE_BGM_2427B415, "ゲーム")),
          count(16, 9, 1),
          List.of(track("bgm", "Bgm", FIXTURE_BGM_2427B415, "ゲーム", "v/60.ogg", null, "N", 1)));
      assertWire(
          QUERIES.musicTracks(c, USER, new MusicTrackRequestData("曲", FIXTURE_MISSING_4B62D186)),
          count(16, 9, 0),
          List.of());
    }
  }

  @Test
  void everyListCapacityRejectsTruncationAndCloseDowngrades() throws Exception {
    for (String kind :
        List.of(
            FIXTURE_ANIMATION_4D33DF79,
            FIXTURE_CATEGORIES_DCB1A2E4,
            FIXTURE_SECTIONS_4914C922,
            FIXTURE_TRACKS_7FF43291)) {
      int maximum =
          switch (kind) {
            case FIXTURE_ANIMATION_4D33DF79 -> 50;
            case FIXTURE_CATEGORIES_DCB1A2E4 -> 20;
            case FIXTURE_SECTIONS_4914C922 -> 100;
            default -> 200;
          };
      fill(kind, maximum);
      try (var c = read()) {
        assertEquals(maximum, select(kind, c, USER).records().size());
      }
      fill(kind, maximum + 1);
      try (var c = read()) {
        failure(ResultCode.RESOURCE_LIMIT, () -> select(kind, c, USER));
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> select(kind, fault(c, "result.close", null, null), USER));
      }
    }
    fill(FIXTURE_ANIMATION_4D33DF79, 999);
    try (var c = read()) {
      assertEquals(
          999,
          ((AnimationMenuResponseData) QUERIES.animationMenu(c, USER).data()).totalFileCount());
    }
    fill(FIXTURE_ANIMATION_4D33DF79, 1000);
    try (var c = read()) {
      failure(ResultCode.RESOURCE_LIMIT, () -> QUERIES.animationMenu(c, USER));
    }
    fill(FIXTURE_TRACKS_7FF43291, 1);
    for (String kind : List.of(FIXTURE_CATEGORIES_DCB1A2E4, FIXTURE_SECTIONS_4914C922)) {
      try (var c = read()) {
        var value =
            select(kind, fault(c, FIXTURE_OVERRIDELONG_54987068, "track_count", 999999L), USER);
        var expected =
            kind.equals(FIXTURE_CATEGORIES_DCB1A2E4)
                ? group(72, 64, FIXTURE_BGM_2427B415, 999999)
                : group(136, 128, "ゲーム", 999999);
        assertWire(value, count(8, 6, 1), List.of(expected));
        failure(
            ResultCode.RESOURCE_LIMIT,
            () ->
                select(
                    kind, fault(c, FIXTURE_OVERRIDELONG_54987068, "track_count", 1000000L), USER));
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> select(kind, fault(c, FIXTURE_OVERRIDELONG_54987068, "track_count", -1L), USER));
      }
    }
  }

  @Test
  void nullContractsAndJdbcMetadataFailuresRemainRedacted() throws Exception {
    fill(FIXTURE_TRACKS_7FF43291, 1);
    for (String kind :
        List.of(
            "menu",
            FIXTURE_ANIMATION_4D33DF79,
            FIXTURE_CATEGORIES_DCB1A2E4,
            FIXTURE_SECTIONS_4914C922,
            FIXTURE_TRACKS_7FF43291)) {
      assertThrows(NullPointerException.class, () -> select(kind, null, USER));
      try (var c = read()) {
        assertThrows(NullPointerException.class, () -> select(kind, c, null));
        c.setReadOnly(false);
        failure(ResultCode.TEMPORARY_FAILURE, () -> select(kind, c, USER));
        c.setAutoCommit(true);
        failure(ResultCode.TEMPORARY_FAILURE, () -> select(kind, c, USER));
      }
    }
    try (var c = read()) {
      assertThrows(NullPointerException.class, () -> QUERIES.animationList(c, USER, null));
      assertThrows(NullPointerException.class, () -> QUERIES.musicSections(c, USER, null));
      assertThrows(NullPointerException.class, () -> QUERIES.musicTracks(c, USER, null));
      assertThrows(
          RuntimeException.class,
          () -> QUERIES.musicSections(c, USER, new MusicSectionRequestData("x".repeat(65))));
      assertThrows(
          RuntimeException.class,
          () ->
              QUERIES.musicTracks(
                  c, USER, new MusicTrackRequestData(FIXTURE_BGM_2427B415, "x".repeat(129))));
      for (String problem :
          List.of(
              "connection.getAutoCommit",
              "connection.isReadOnly",
              "connection.prepareStatement",
              "statement.setString",
              "statement.executeQuery",
              "result.next",
              "result.getLong",
              "result.getString",
              "result.wasNull",
              "result.close",
              "statement.close")) {
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> select(FIXTURE_TRACKS_7FF43291, fault(c, problem, null, null), USER));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        assertTrue(c.isReadOnly());
      }
      for (String column :
          List.of(
              "logical_id",
              "title",
              FIXTURE_CATEGORY_DE46A45C,
              "section",
              "display_path",
              "pair_role"))
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () ->
                select(
                    FIXTURE_TRACKS_7FF43291,
                    fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, column, null),
                    USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              select(
                  FIXTURE_TRACKS_7FF43291,
                  fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, "pair_role", "UNKNOWN"),
                  USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              select(
                  FIXTURE_TRACKS_7FF43291,
                  fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, "display_path", "/outside"),
                  USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              select(
                  FIXTURE_TRACKS_7FF43291,
                  fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, "title", " "),
                  USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              select(
                  FIXTURE_TRACKS_7FF43291,
                  fault(c, FIXTURE_OVERRIDELONG_54987068, "display_order", Long.MAX_VALUE),
                  USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              select(
                  FIXTURE_TRACKS_7FF43291,
                  fault(c, FIXTURE_NUMERICNULL_C13B0A60, null, null),
                  USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> QUERIES.animationMenu(fault(c, "noRows", null, null), USER));
    }
    fill(FIXTURE_ANIMATION_4D33DF79, 1);
    try (var c = read()) {
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              QUERIES.animationList(
                  fault(c, FIXTURE_OVERRIDESTRING_6A02E9F8, FIXTURE_CATEGORY_DE46A45C, "UNKNOWN"),
                  USER,
                  MAIN));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              QUERIES.animationMenu(
                  fault(c, FIXTURE_OVERRIDELONG_54987068, "opening_count", -1L), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> QUERIES.animationMenu(fault(c, FIXTURE_NUMERICNULL_C13B0A60, null, null), USER));
    }
  }

  @Test
  void concurrentReadersNeverMutateOrAcquireRowLocks() throws Exception {
    fill(FIXTURE_TRACKS_7FF43291, 3);
    try (var lock = database.admin();
        var statement = lock.createStatement();
        var workers = Executors.newFixedThreadPool(8)) {
      lock.setAutoCommit(false);
      statement.executeQuery("select id from schubert.media_assets for update").close();
      List<Callable<TypedPayloadValues>> tasks = new ArrayList<>();
      for (int index = 0; index < 100; index++)
        tasks.add(
            () -> {
              try (var c = read()) {
                return select(FIXTURE_TRACKS_7FF43291, c, USER);
              }
            });
      var futures = workers.invokeAll(tasks);
      for (var future : futures)
        assertWire(
            future.get(),
            count(16, 9, 3),
            List.of(
                track(
                    "m0001",
                    FIXTURE_TRACK_43CA9734,
                    FIXTURE_BGM_2427B415,
                    "ゲーム",
                    "v/1.ogg",
                    null,
                    "N",
                    1),
                track(
                    "m0002",
                    FIXTURE_TRACK_43CA9734,
                    FIXTURE_BGM_2427B415,
                    "ゲーム",
                    "v/2.ogg",
                    null,
                    "N",
                    2),
                track(
                    "m0003",
                    FIXTURE_TRACK_43CA9734,
                    FIXTURE_BGM_2427B415,
                    "ゲーム",
                    "v/3.ogg",
                    null,
                    "N",
                    3)));
      try (var result =
          statement.executeQuery(
              "select count(*),min(display_order),max(display_order) from schubert.media_assets")) {
        assertTrue(result.next());
        assertEquals(3, result.getInt(1));
        assertEquals(1, result.getInt(2));
        assertEquals(3, result.getInt(3));
      }
      lock.rollback();
    }
  }

  private static TypedPayloadValues select(String kind, Connection c, AuthenticatedActor actor) {
    return switch (kind) {
      case "menu" -> QUERIES.animationMenu(c, actor);
      case FIXTURE_ANIMATION_4D33DF79 -> QUERIES.animationList(c, actor, MAIN);
      case FIXTURE_CATEGORIES_DCB1A2E4 -> QUERIES.musicCategories(c, actor);
      case FIXTURE_SECTIONS_4914C922 ->
          QUERIES.musicSections(c, actor, new MusicSectionRequestData(FIXTURE_BGM_2427B415));
      case FIXTURE_TRACKS_7FF43291 ->
          QUERIES.musicTracks(c, actor, new MusicTrackRequestData(FIXTURE_BGM_2427B415, "ゲーム"));
      default -> throw new AssertionError(kind);
    };
  }

  private static void failure(
      ResultCode code, org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(MediaQueryException.class, operation);
    assertEquals(code, failure.resultCode());
    assertEquals("media query is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Connection read() throws SQLException {
    var c = database.api();
    c.setReadOnly(true);
    c.setAutoCommit(false);
    return c;
  }

  private static void sql(String text) throws SQLException {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute(text);
    }
  }

  private static void videos() throws Exception {
    asset(
        30,
        FIXTURE_VIDEO_C9B6F4C2,
        FIXTURE_MAIN_Z_82616435,
        FIXTURE_FIRST_81C9759D,
        FIXTURE_MAIN_7FCC0BE2,
        null,
        null,
        null,
        null,
        1);
    asset(
        10,
        FIXTURE_VIDEO_C9B6F4C2,
        "main-a",
        "Second",
        FIXTURE_MAIN_7FCC0BE2,
        null,
        null,
        null,
        null,
        2);
    asset(
        20,
        FIXTURE_VIDEO_C9B6F4C2,
        FIXTURE_SUB_B8F15D32,
        FIXTURE_SUB_574FA518,
        FIXTURE_SUBTRACK_BF9F5649,
        null,
        FIXTURE_MAIN_Z_82616435,
        null,
        null,
        3);
    asset(40, FIXTURE_VIDEO_C9B6F4C2, "ova", "Ova", "OVA", null, null, null, null, 4);
    asset(
        50,
        FIXTURE_VIDEO_C9B6F4C2,
        FIXTURE_OPENING_583FF6F7,
        "Opening",
        "OPENING",
        null,
        null,
        null,
        null,
        5);
  }

  private static void asset(
      int id,
      String type,
      String logical,
      String title,
      String category,
      String section,
      String parent,
      String pair,
      String role,
      int order)
      throws SQLException {
    boolean video = type.equals(FIXTURE_VIDEO_C9B6F4C2);
    String suffix = video ? FIXTURE_MP4_90A2AC73 : FIXTURE_OGG_09018BA2;
    try (var c = database.admin();
        var s =
            c.prepareStatement(
                """
      insert into schubert.media_assets(id,logical_id,media_type,title,category,section,storage_relative_path,
        display_path,file_name,byte_size,sha256,mime_type,parent_logical_id,pair_key,pair_role,display_order,created_at)
      values(?,?,?,?,?,?,?,?,?,123,repeat('a',64),?,?,?,?,?,'2026-09-08Z')
      """)) {
      s.setInt(1, id);
      s.setString(2, logical);
      s.setString(3, type);
      s.setString(4, title);
      s.setString(5, category);
      s.setString(6, section);
      s.setString(7, (video ? "video/" : FIXTURE_MUSIC_80DD0E40) + id + suffix);
      s.setString(8, "v/" + id + suffix);
      s.setString(9, "file" + suffix);
      s.setString(10, video ? FIXTURE_VIDEO_MP4_9A1C8BFA : FIXTURE_AUDIO_OGG_96A5CB00);
      s.setString(11, parent);
      s.setString(12, pair);
      s.setString(13, role);
      s.setInt(14, order);
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void fill(String kind, int count) throws SQLException {
    sql("truncate schubert.media_assets cascade");
    boolean video = kind.equals(FIXTURE_ANIMATION_4D33DF79);
    String suffix = video ? FIXTURE_MP4_90A2AC73 : FIXTURE_OGG_09018BA2;
    String category =
        video
            ? "'MAIN'"
            : kind.equals(FIXTURE_CATEGORIES_DCB1A2E4) ? "'c'||lpad(i::text,4,'0')" : "'BGM'";
    String section =
        video
            ? "NULL"
            : kind.equals(FIXTURE_SECTIONS_4914C922) ? "'s'||lpad(i::text,4,'0')" : "'ゲーム'";
    sql(
        "insert into schubert.media_assets(id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,pair_role,display_order,created_at) select i,'m'||lpad(i::text,4,'0'),'"
            + (video ? FIXTURE_VIDEO_C9B6F4C2 : FIXTURE_MUSIC_D5800D43)
            + "','Track',"
            + category
            + ","
            + section
            + ",'"
            + (video ? "video/" : FIXTURE_MUSIC_80DD0E40)
            + "'||i||'"
            + suffix
            + "','v/'||i||'"
            + suffix
            + "','file"
            + suffix
            + "',123,repeat('a',64),'"
            + (video ? FIXTURE_VIDEO_MP4_9A1C8BFA : FIXTURE_AUDIO_OGG_96A5CB00)
            + "',"
            + (video ? "NULL" : "'N'")
            + ",i,'2026-09-08Z' from generate_series(1,"
            + count
            + ") i");
  }

  private static Connection fault(Connection c, String fault, String column, Object value) {
    return (Connection) wrap(c, Connection.class, "connection", fault, column, value);
  }

  private static Object wrap(
      Object target, Class<?> type, String layer, String fault, String column, Object value) {
    return Proxy.newProxyInstance(
        type.getClassLoader(),
        new Class<?>[] {type},
        (proxy, method, args) -> {
          String name = method.getName();
          if (fault.equals(layer + "." + name) && !name.equals("close"))
            throw new SQLException("synthetic private JDBC");
          if (layer.equals("result")) {
            if (fault.equals("noRows") && name.equals("next")) return false;
            if (fault.equals(FIXTURE_NUMERICNULL_C13B0A60) && name.equals("wasNull")) return true;
            if (((fault.equals(FIXTURE_OVERRIDELONG_54987068) && name.equals("getLong"))
                    || (fault.equals(FIXTURE_OVERRIDESTRING_6A02E9F8) && name.equals("getString")))
                && Objects.equals(args[0], column)) return value;
          }
          Object result;
          try {
            result = method.invoke(target, args);
          } catch (InvocationTargetException e) {
            throw e.getCause();
          }
          if (fault.equals(layer + "." + name)) throw new SQLException("synthetic private close");
          if (result instanceof PreparedStatement s)
            return wrap(s, PreparedStatement.class, "statement", fault, column, value);
          if (result instanceof ResultSet r)
            return wrap(r, ResultSet.class, "result", fault, column, value);
          return result;
        });
  }

  private static void assertWire(TypedPayloadValues value, byte[] data, List<byte[]> records) {
    var typed = PayloadTypeCatalog.encode(value);
    var encoded = PayloadCodec.standard().encode(typed, false);
    assertArrayEquals(data, encoded.copyData());
    assertEquals(records.size(), encoded.copyRecords().size());
    for (int i = 0; i < records.size(); i++)
      assertArrayEquals(records.get(i), encoded.copyRecords().get(i), "record " + i);
  }

  private static byte[] blank(int n) {
    byte[] bytes = new byte[n];
    Arrays.fill(bytes, (byte) ' ');
    return bytes;
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] text = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(text, 0, bytes, offset, text.length);
  }

  private static void number(byte[] bytes, int offset, int length, long value) {
    put(bytes, offset, String.format(Locale.ROOT, "%0" + length + "d", value));
  }

  private static byte[] count(int size, int digits, int value) {
    byte[] b = blank(size);
    number(b, 0, digits, value);
    return b;
  }

  private static byte[] group(int size, int offset, String name, int value) {
    byte[] b = blank(size);
    put(b, 0, name);
    number(b, offset, 6, value);
    return b;
  }

  private static byte[] animation(
      String id, String title, String category, String path, String parent, int order) {
    byte[] b = blank(928);
    put(b, 0, id);
    put(b, 64, title);
    put(b, 320, category);
    put(b, 336, path);
    number(b, 848, 12, 123);
    if (parent != null) put(b, 860, parent);
    number(b, 924, 4, order);
    return b;
  }

  private static byte[] track(
      String id,
      String title,
      String category,
      String section,
      String path,
      String pair,
      String role,
      int order) {
    byte[] b = blank(1312);
    put(b, 0, id);
    put(b, 64, title);
    put(b, 320, category);
    put(b, 384, section);
    put(b, 512, path);
    number(b, 1024, 12, 123);
    if (pair != null) put(b, 1036, pair);
    put(b, 1292, role);
    number(b, 1293, 4, order);
    return b;
  }
}
