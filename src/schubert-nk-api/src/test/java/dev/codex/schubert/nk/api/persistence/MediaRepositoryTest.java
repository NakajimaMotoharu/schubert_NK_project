package dev.codex.schubert.nk.api.persistence;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.media.*;
import dev.codex.schubert.nk.protocol.layout.semantic.AnimationListCategory;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.*;
import java.util.*;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.io.TempDir;

/** PT-MED-008..014; real production DDL/grants, synthetic master and independent UI235 bytes. */
class MediaRepositoryTest {
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
    database.stop();
  }

  @BeforeEach
  void clear() throws Exception {
    sql("truncate schubert.media_assets cascade");
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
    asset(60, "MUSIC", "ignored", "ignored", "BGM", "ゲーム", null, null, "N", 1);
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
            animation("main-z", "First", "MAIN", "v/30.mp4", null, 1),
            animation("main-a", "Second", "MAIN", "v/10.mp4", null, 2),
            animation("sub", "Sub", "SUBTRACK", "v/20.mp4", "main-z", 3));
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
      {"ZZ", "other"},
      {"BGM", "ゲーム"},
      {"曲", "アニメ"},
      {"曲", "ゲーム"},
      {"曲", "キャラクターソング"},
      {"曲", "ZZ"},
      {"曲", "AA"},
      {"AA", "other"},
      {"曲", "ゲーム"}
    };
    for (int i = 0; i < groups.length; i++)
      asset(i + 1, "MUSIC", "m" + i, "Track", groups[i][0], groups[i][1], null, null, "N", i + 1);
    try (var c = read()) {
      assertWire(
          QUERIES.musicCategories(c, USER),
          count(8, 6, 4),
          List.of(
              group(72, 64, "曲", 6),
              group(72, 64, "BGM", 1),
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
          QUERIES.musicSections(c, USER, new MusicSectionRequestData("missing")),
          count(8, 6, 0),
          List.of());
    }
    asset(20, "MUSIC", "quoted", "Track", "O'Reilly", "quote", null, null, "N", 20);
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
    asset(50, "MUSIC", "z-main", "Unrelated title", "曲", "ゲーム", null, "frozen-key", "M", 1);
    asset(10, "MUSIC", "a-inst", "No suffix inference", "曲", "ゲーム", null, "frozen-key", "I", 1);
    asset(30, "MUSIC", "lonely", "Solo", "曲", "ゲーム", null, "solo-key", "M", 2);
    asset(60, "MUSIC", "bgm", "Bgm", "BGM", "ゲーム", null, null, "N", 1);
    asset(70, "MUSIC", "other", "Other", "曲", "アニメ", null, "other", "M", 1);
    try (var c = read()) {
      assertWire(
          QUERIES.musicTracks(c, USER, new MusicTrackRequestData("曲", "ゲーム")),
          count(16, 9, 3),
          List.of(
              track("a-inst", "No suffix inference", "曲", "ゲーム", "v/10.ogg", "frozen-key", "I", 1),
              track("z-main", "Unrelated title", "曲", "ゲーム", "v/50.ogg", "frozen-key", "M", 1),
              track("lonely", "Solo", "曲", "ゲーム", "v/30.ogg", "solo-key", "M", 2)));
      assertWire(
          QUERIES.musicTracks(c, ADMIN, new MusicTrackRequestData("BGM", "ゲーム")),
          count(16, 9, 1),
          List.of(track("bgm", "Bgm", "BGM", "ゲーム", "v/60.ogg", null, "N", 1)));
      assertWire(
          QUERIES.musicTracks(c, USER, new MusicTrackRequestData("曲", "missing")),
          count(16, 9, 0),
          List.of());
    }
  }

  @Test
  void everyListCapacityRejectsTruncationAndCloseDowngrades() throws Exception {
    for (String kind : List.of("animation", "categories", "sections", "tracks")) {
      int maximum =
          switch (kind) {
            case "animation" -> 50;
            case "categories" -> 20;
            case "sections" -> 100;
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
    fill("animation", 999);
    try (var c = read()) {
      assertEquals(
          999,
          ((AnimationMenuResponseData) QUERIES.animationMenu(c, USER).data()).totalFileCount());
    }
    fill("animation", 1000);
    try (var c = read()) {
      failure(ResultCode.RESOURCE_LIMIT, () -> QUERIES.animationMenu(c, USER));
    }
    fill("tracks", 1);
    for (String kind : List.of("categories", "sections")) {
      try (var c = read()) {
        var value = select(kind, fault(c, "overrideLong", "track_count", 999999L), USER);
        var expected =
            kind.equals("categories")
                ? group(72, 64, "BGM", 999999)
                : group(136, 128, "ゲーム", 999999);
        assertWire(value, count(8, 6, 1), List.of(expected));
        failure(
            ResultCode.RESOURCE_LIMIT,
            () -> select(kind, fault(c, "overrideLong", "track_count", 1000000L), USER));
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> select(kind, fault(c, "overrideLong", "track_count", -1L), USER));
      }
    }
  }

  @Test
  void nullContractsAndJdbcMetadataFailuresRemainRedacted() throws Exception {
    fill("tracks", 1);
    for (String kind : List.of("menu", "animation", "categories", "sections", "tracks")) {
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
          () -> QUERIES.musicTracks(c, USER, new MusicTrackRequestData("BGM", "x".repeat(129))));
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
            () -> select("tracks", fault(c, problem, null, null), USER));
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        assertTrue(c.isReadOnly());
      }
      for (String column :
          List.of("logical_id", "title", "category", "section", "display_path", "pair_role"))
        failure(
            ResultCode.TEMPORARY_FAILURE,
            () -> select("tracks", fault(c, "overrideString", column, null), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> select("tracks", fault(c, "overrideString", "pair_role", "UNKNOWN"), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> select("tracks", fault(c, "overrideString", "display_path", "/outside"), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> select("tracks", fault(c, "overrideString", "title", " "), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> select("tracks", fault(c, "overrideLong", "display_order", Long.MAX_VALUE), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> select("tracks", fault(c, "numericNull", null, null), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> QUERIES.animationMenu(fault(c, "noRows", null, null), USER));
    }
    fill("animation", 1);
    try (var c = read()) {
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () ->
              QUERIES.animationList(fault(c, "overrideString", "category", "UNKNOWN"), USER, MAIN));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> QUERIES.animationMenu(fault(c, "overrideLong", "opening_count", -1L), USER));
      failure(
          ResultCode.TEMPORARY_FAILURE,
          () -> QUERIES.animationMenu(fault(c, "numericNull", null, null), USER));
    }
  }

  @Test
  void concurrentReadersNeverMutateOrAcquireRowLocks() throws Exception {
    fill("tracks", 3);
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
                return select("tracks", c, USER);
              }
            });
      var futures = workers.invokeAll(tasks);
      for (var future : futures)
        assertWire(
            future.get(),
            count(16, 9, 3),
            List.of(
                track("m0001", "Track", "BGM", "ゲーム", "v/1.ogg", null, "N", 1),
                track("m0002", "Track", "BGM", "ゲーム", "v/2.ogg", null, "N", 2),
                track("m0003", "Track", "BGM", "ゲーム", "v/3.ogg", null, "N", 3)));
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
      case "animation" -> QUERIES.animationList(c, actor, MAIN);
      case "categories" -> QUERIES.musicCategories(c, actor);
      case "sections" -> QUERIES.musicSections(c, actor, new MusicSectionRequestData("BGM"));
      case "tracks" -> QUERIES.musicTracks(c, actor, new MusicTrackRequestData("BGM", "ゲーム"));
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
    asset(30, "VIDEO", "main-z", "First", "MAIN", null, null, null, null, 1);
    asset(10, "VIDEO", "main-a", "Second", "MAIN", null, null, null, null, 2);
    asset(20, "VIDEO", "sub", "Sub", "SUBTRACK", null, "main-z", null, null, 3);
    asset(40, "VIDEO", "ova", "Ova", "OVA", null, null, null, null, 4);
    asset(50, "VIDEO", "opening", "Opening", "OPENING", null, null, null, null, 5);
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
    boolean video = type.equals("VIDEO");
    String suffix = video ? ".mp4" : ".ogg";
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
      s.setString(7, (video ? "video/" : "music/") + id + suffix);
      s.setString(8, "v/" + id + suffix);
      s.setString(9, "file" + suffix);
      s.setString(10, video ? "video/mp4" : "audio/ogg");
      s.setString(11, parent);
      s.setString(12, pair);
      s.setString(13, role);
      s.setInt(14, order);
      assertEquals(1, s.executeUpdate());
    }
  }

  private static void fill(String kind, int count) throws SQLException {
    sql("truncate schubert.media_assets cascade");
    boolean video = kind.equals("animation");
    String suffix = video ? ".mp4" : ".ogg";
    String category =
        video ? "'MAIN'" : kind.equals("categories") ? "'c'||lpad(i::text,4,'0')" : "'BGM'";
    String section =
        video ? "NULL" : kind.equals("sections") ? "'s'||lpad(i::text,4,'0')" : "'ゲーム'";
    sql(
        "insert into schubert.media_assets(id,logical_id,media_type,title,category,section,storage_relative_path,display_path,file_name,byte_size,sha256,mime_type,pair_role,display_order,created_at) select i,'m'||lpad(i::text,4,'0'),'"
            + (video ? "VIDEO" : "MUSIC")
            + "','Track',"
            + category
            + ","
            + section
            + ",'"
            + (video ? "video/" : "music/")
            + "'||i||'"
            + suffix
            + "','v/'||i||'"
            + suffix
            + "','file"
            + suffix
            + "',123,repeat('a',64),'"
            + (video ? "video/mp4" : "audio/ogg")
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
            if (fault.equals("numericNull") && name.equals("wasNull")) return true;
            if (((fault.equals("overrideLong") && name.equals("getLong"))
                    || (fault.equals("overrideString") && name.equals("getString")))
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
