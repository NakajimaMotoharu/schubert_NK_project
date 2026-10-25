package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.MediaMimeType;
import dev.codex.schubert.nk.protocol.layout.semantic.PairRole;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.VideoCategory;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import dev.codex.schubert.nk.web.config.ContentDetailMvcConfiguration;
import dev.codex.schubert.nk.web.controller.ContentDetailController;
import dev.codex.schubert.nk.web.logging.WebLogDatabaseFixture;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.storage.LargeResultReader;
import dev.codex.schubert.nk.web.view.AnimationWatchViewModel;
import dev.codex.schubert.nk.web.view.MusicTrackViewModel;
import dev.codex.schubert.nk.web.view.ScenarioDetailViewModel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.jsoup.Jsoup;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.csrf.CsrfToken;
import org.springframework.security.web.csrf.DefaultCsrfToken;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;

/** Literal UI232234235 offsets; HTTP/DOM and held-file bytes independent of production encoding. */
class ContentDetailControllerTest {
  private static WebLogDatabaseFixture db;
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-04T00:00:00Z"), ZoneOffset.UTC);
  private static final UUID FILE = UUID.fromString("00000000-0000-4000-8000-000000000072");
  @TempDir Path root;

  @BeforeAll
  static void start(@TempDir Path path) throws Exception {
    db = new WebLogDatabaseFixture(path);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @AfterEach
  void clear() {
    SecurityContextHolder.clearContext();
  }

  private static SessionPrincipal actor() {
    return new SessionPrincipal(
        "reader", UserRole.USER, AuthenticationContext.of("a".repeat(64)), CLOCK.instant());
  }

  @Test
  void content001InlineAndHeldFileUseSameIndependentBodyAndNavigation() throws Exception {
    try (var f = new Fixture()) {
      for (int count : new int[] {0, 1, 200}) {
        f.count = count;
        var m = new ExtendedModelMap();
        assertEquals("scenario", f.call("SCN", m, new MockHttpServletResponse()));
        var page = assertInstanceOf(ScenarioDetailViewModel.class, m.get("page"));
        assertEquals(23, page.getId());
        assertEquals(count, page.getEntries().size());
        assertEquals("章<script>", page.getTitle());
        assertEquals("文章/23.txt", page.getDisplayPath());
        if (count > 0) assertEquals("本文", page.getEntries().getFirst().getBody());
      }
      f.file = true;
      for (int count : new int[] {1, 201, 10000}) {
        f.count = count;
        f.prepareFile();
        byte[] before = Files.readAllBytes(f.readyFile());
        var m = new ExtendedModelMap();
        assertEquals("scenario", f.call("SCN", m, new MockHttpServletResponse()));
        var page = assertInstanceOf(ScenarioDetailViewModel.class, m.get("page"));
        assertEquals(count, page.getEntries().size());
        assertEquals("本文", page.getEntries().getLast().getBody());
        assertArrayEquals(before, Files.readAllBytes(f.readyFile()));
      }
      f.erased();
    }
  }

  @Test
  void content002InputBindingAndFileIntegrityNeverTurnIntoEmptySuccess() throws Exception {
    try (var f = new Fixture()) {
      for (String id : List.of("", "0", "-1", "1e2", "1000000000000")) {
        int sent = f.sent.get();
        var r = new MockHttpServletResponse();
        assertNull(f.controller.scenario(id, actor(), new ExtendedModelMap(), f.request(), r));
        assertEquals(400, r.getStatus());
        assertEquals(sent, f.sent.get());
      }
      f.wrongId = true;
      var r = new MockHttpServletResponse();
      assertNull(f.call("SCN", new ExtendedModelMap(), r));
      assertEquals(503, r.getStatus());
      f.wrongId = false;
      f.file = true;
      f.count = 1;
      f.prepareFile();
      Files.write(f.readyFile(), new byte[] {0});
      r = new MockHttpServletResponse();
      assertNull(f.call("SCN", new ExtendedModelMap(), r));
      assertEquals(503, r.getStatus());
      Files.delete(f.readyFile());
      r = new MockHttpServletResponse();
      assertNull(f.call("SCN", new ExtendedModelMap(), r));
      assertEquals(503, r.getStatus());
      f.erased();
    }
  }

  @Test
  void content003EveryVideoCategoryHasLiteralBackLinkAndNoPhysicalDescriptor() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      for (String category : List.of("MAIN", "SUBTRACK", "OVA", "OPENING")) {
        f.category = category;
        for (String code : List.of("0000", "0200")) {
          f.code = code;
          var result =
              mvc.perform(
                      get("/animation/videos/論理é")
                          .principal(actor())
                          .requestAttr(
                              CsrfToken.class.getName(),
                              new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64))))
                  .andReturn();
          assertEquals(200, result.getResponse().getStatus());
          var dom = Jsoup.parse(result.getResponse().getContentAsString(StandardCharsets.UTF_8));
          assertEquals("映像<script>", dom.select("h1").text());
          assertEquals(0, dom.select("script").size());
          assertEquals(
              "/animation/media/%E8%AB%96%E7%90%86%C3%A9", dom.select("video").attr("src"));
          assertTrue(
              dom.select("a").stream()
                  .anyMatch(
                      a ->
                          a.attr("href")
                              .equals(
                                  category.equals("OVA")
                                      ? "/animation/ova"
                                      : category.equals("OPENING")
                                          ? "/animation"
                                          : "/animation/main")));
          assertFalse(result.getResponse().getContentAsString().contains("video/v.mp4"));
        }
      }
      f.category = "OPENING";
      var m = new ExtendedModelMap();
      assertEquals(
          "animation-watch",
          f.controller.opening(actor(), m, f.request(), new MockHttpServletResponse()));
      var page = assertInstanceOf(AnimationWatchViewModel.class, m.get("page"));
      assertEquals("/animation/media/opening", page.getValues().get("mediaHref"));
      assertEquals("AnimationWatchViewModel[REDACTED]", page.toString());
      assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
      var r = new MockHttpServletResponse();
      assertNull(
          f.controller.watch("x".repeat(65), actor(), new ExtendedModelMap(), f.request(), r));
      assertEquals(400, r.getStatus());
      f.videoPath = "private/video/v.mp4";
      r = new MockHttpServletResponse();
      var invalidModel = new ExtendedModelMap();
      assertNull(f.controller.watch("opening", actor(), invalidModel, f.request(), r));
      assertEquals(503, r.getStatus());
      assertFalse(invalidModel.containsKey("page"));
      f.erased();
    }
  }

  @Test
  void content004MusicNormalOrderAndZeroBoundary() throws Exception {
    try (var f = new Fixture();
        var context = f.mvc()) {
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      for (int count : new int[] {1, 200}) {
        f.count = count;
        var result =
            mvc.perform(
                    get("/music/BGM/ゲーム")
                        .principal(actor())
                        .requestAttr(
                            CsrfToken.class.getName(),
                            new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64))))
                .andReturn();
        assertEquals(200, result.getResponse().getStatus());
        var dom = Jsoup.parse(result.getResponse().getContentAsString(StandardCharsets.UTF_8));
        assertEquals("BGM / ゲーム", dom.select("h1").text());
        assertEquals(count, dom.select("audio").size());
        assertEquals("曲1", dom.select("strong").getFirst().text());
        assertEquals("/music/media/track1", dom.select("audio").getFirst().attr("src"));
        assertEquals("/music/download/track1", dom.select(".download").getFirst().attr("href"));
        assertEquals(0, dom.select(".song-row").size());
      }
      f.count = 0;
      var r = new MockHttpServletResponse();
      assertNull(f.call("MTR", new ExtendedModelMap(), r));
      assertEquals(404, r.getStatus());
      for (String value : List.of("", "x".repeat(129))) {
        int sent = f.sent.get();
        r = new MockHttpServletResponse();
        assertNull(
            f.controller.tracks("BGM", value, actor(), new ExtendedModelMap(), f.request(), r));
        assertEquals(400, r.getStatus());
        assertEquals(sent, f.sent.get());
      }
      f.erased();
    }
  }

  @Test
  void content005StoredPairProjectsMissingSidesWithoutMatchingTitles() throws Exception {
    var records =
        List.of(
            track("i", "07-01 異なる (instrumental)", "pair", PairRole.INSTRUMENTAL, 1),
            track("m", "07-02 歌<script>", "pair", PairRole.MAIN, 2),
            track("i2", "孤立インスト", "other", PairRole.INSTRUMENTAL, 3),
            track("m2", "主曲", "last", PairRole.MAIN, 4),
            track("n", "単独", "", PairRole.NONE, 5));
    var page =
        MusicTrackViewModel.from(actor(), "曲", "ゲーム", new MusicTrackResponseData(5), records);
    assertEquals("MusicTrackViewModel[REDACTED]", page.toString());
    assertEquals(5, page.getValues().get("trackCount"));
    assertThrows(UnsupportedOperationException.class, () -> page.getValues().clear());
    try (var f = new Fixture();
        var context = f.mvc()) {
      f.pairRecords = records;
      var mvc = MockMvcBuilders.webAppContextSetup(context).build();
      var result =
          mvc.perform(
                  get("/music/曲/ゲーム")
                      .principal(actor())
                      .requestAttr(
                          CsrfToken.class.getName(),
                          new DefaultCsrfToken("X-CSRF-TOKEN", "_csrf", "b".repeat(64))))
              .andReturn();
      assertEquals(200, result.getResponse().getStatus());
      var dom = Jsoup.parse(result.getResponse().getContentAsString(StandardCharsets.UTF_8));
      assertEquals(4, dom.select(".song-row").size());
      assertEquals(5, dom.select("audio").size());
      // BUG636: complete pair 0 + I-only 1 + M-only 1 + NONE single 1 = 3.
      assertEquals(3, dom.select(".song-player-placeholder").size());
      assertEquals("歌<script>", dom.select("strong").getFirst().text());
      assertEquals(0, dom.select("script,.scenario-meta").size());
      var pairs = assertInstanceOf(List.class, page.getValues().get("pairs"));
      assertEquals(4, pairs.size());
      assertEquals("歌<script>", assertInstanceOf(Map.class, pairs.getFirst()).get("title"));
      assertEquals(Optional.empty(), assertInstanceOf(Map.class, pairs.get(1)).get("main"));
      assertEquals(Optional.empty(), assertInstanceOf(Map.class, pairs.get(2)).get("instrumental"));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(), "BGM", "ゲーム", new MusicTrackResponseData(5), records));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(actor(), "曲", "ゲーム", new MusicTrackResponseData(0), records));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(),
                "曲",
                "ゲーム",
                new MusicTrackResponseData(2),
                List.of(records.get(1), records.get(1))));
  }

  @Test
  void content006EveryKnownErrorAndBrokenWireHasNoModel() throws Exception {
    try (var f = new Fixture()) {
      for (String type : List.of("SCN", "VID", "MTR")) {
        for (String[] pair :
            List.of(
                new String[] {"0100", "400"},
                new String[] {"0101", "401"},
                new String[] {"0103", "403"},
                new String[] {"0104", "404"},
                new String[] {"0105", "409"},
                new String[] {"0106", "429"},
                new String[] {"0107", "409"},
                new String[] {"9000", "503"},
                new String[] {"9001", "503"})) {
          f.code = pair[0];
          var m = new ExtendedModelMap();
          var r = new MockHttpServletResponse();
          assertNull(f.call(type, m, r));
          assertEquals(Integer.parseInt(pair[1]), r.getStatus());
          assertTrue(m.isEmpty());
        }
        f.code = "0000";
        f.badContext = true;
        var r = new MockHttpServletResponse();
        assertNull(f.call(type, new ExtendedModelMap(), r));
        assertEquals(503, r.getStatus());
        f.badContext = false;
      }
      f.erased();
    }
  }

  @Test
  void content007NullAndForeignPrincipalNeverIssueMq() throws Exception {
    try (var f = new Fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> new ContentDetailController(null, f.media, f.music, f.reader, f.security.handler));
      assertThrows(
          NullPointerException.class,
          () ->
              new ContentDetailController(
                  f.scenarios, null, f.music, f.reader, f.security.handler));
      assertThrows(
          NullPointerException.class,
          () ->
              new ContentDetailController(
                  f.scenarios, f.media, null, f.reader, f.security.handler));
      assertThrows(
          NullPointerException.class,
          () ->
              new ContentDetailController(f.scenarios, f.media, f.music, null, f.security.handler));
      assertThrows(
          NullPointerException.class,
          () -> new ContentDetailController(f.scenarios, f.media, f.music, f.reader, null));
      assertThrows(
          SessionStoreException.class,
          () ->
              f.controller.scenario(
                  "23",
                  () -> "foreign",
                  new ExtendedModelMap(),
                  f.request(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.scenario(
                  null,
                  actor(),
                  new ExtendedModelMap(),
                  f.request(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.watch(
                  null,
                  actor(),
                  new ExtendedModelMap(),
                  f.request(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.tracks(
                  null,
                  "section",
                  actor(),
                  new ExtendedModelMap(),
                  f.request(),
                  new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.tracks(
                  "category",
                  null,
                  actor(),
                  new ExtendedModelMap(),
                  f.request(),
                  new MockHttpServletResponse()));
      assertEquals(0, f.sent.get());
    }
  }

  @Test
  void content008ActualHttpSecurity0102AndOneHundredIndependentReads() throws Exception {
    try (var f = new Fixture();
        var server =
            new EmbeddedWebSecurityTest.Server(
                Files.createTempDirectory(root, "http-"),
                false,
                db,
                Optional.of(f.security.api.provider),
                true,
                true,
                (mvc, invalid) -> f.configure(mvc, invalid))) {
      var paths =
          List.of(
              "/scenarios/23", "/animation/opening", "/animation/videos/opening", "/music/BGM/ゲーム");
      for (String path : paths)
        assertEquals(302, server.send("GET", path, null, null, true).statusCode());
      assertEquals(0, f.sent.get());
      var first = server.send("GET", "/login", null, null, true);
      String initial = first.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
      var login =
          server.send(
              "POST",
              "/login",
              initial,
              "_csrf=" + first.body().substring(6) + "&username=reader&password=p",
              true);
      String cookie = login.headers().firstValue("set-cookie").orElseThrow().split(";", 2)[0];
      for (String path : paths) {
        var shown = server.send("GET", path, cookie, null, true);
        assertEquals(200, shown.statusCode(), path);
        assertEquals(200, server.send("HEAD", path, cookie, null, true).statusCode());
        String csrf = Jsoup.parse(shown.body()).select("input[name='_csrf']").attr("value");
        assertEquals(405, server.send("POST", path, cookie, "_csrf=" + csrf, true).statusCode());
      }
      try (var executor = Executors.newFixedThreadPool(12)) {
        var jobs = new ArrayList<Callable<Integer>>();
        for (int n = 0; n < 100; n++)
          jobs.add(() -> server.send("GET", "/scenarios/23", cookie, null, true).statusCode());
        for (var result : executor.invokeAll(jobs, 30, TimeUnit.SECONDS)) {
          assertFalse(result.isCancelled());
          assertEquals(200, result.get());
        }
      }
      f.code = "0102";
      var expired = server.send("GET", "/scenarios/23", cookie, null, true);
      assertEquals(302, expired.statusCode());
      assertEquals(
          "/login?session-expired", expired.headers().firstValue("location").orElseThrow());
      assertTrue(expired.headers().firstValue("set-cookie").orElseThrow().contains("Max-Age=0"));
      assertEquals(302, server.send("GET", "/animation/opening", cookie, null, true).statusCode());
      f.erased();
    }
  }

  private static MusicTrackRecord track(
      String id, String title, String pair, PairRole role, int order) {
    return new MusicTrackRecord(
        id,
        title,
        "曲",
        "ゲーム",
        DisplayPath.of("曲/" + id + ".m4a"),
        12,
        role == PairRole.NONE ? Optional.empty() : Optional.of(pair),
        role,
        order);
  }

  @Test
  void content009ProjectionContractsRejectInvalidIdsCountsAndBoundRows() {
    var data =
        new VideoDescriptorResponseData(
            "opening",
            RelativePath.of("video/v.mp4"),
            "v.mp4",
            12,
            Sha256Hex.of("a".repeat(64)),
            MediaMimeType.VIDEO_MP4,
            ContentDisposition.INLINE,
            "Opening",
            VideoCategory.OPENING,
            DisplayPath.of("op.mp4"));
    assertThrows(NullPointerException.class, () -> AnimationWatchViewModel.from(null, data));
    assertThrows(NullPointerException.class, () -> AnimationWatchViewModel.from(actor(), null));
    for (String id : List.of("", ".", "..")) {
      var bad =
          new VideoDescriptorResponseData(
              id,
              data.storageRelativePath(),
              data.fileName(),
              data.fileByteLength(),
              data.sha256(),
              data.mimeType(),
              data.contentDisposition(),
              data.title(),
              data.category(),
              data.displayPath());
      assertThrows(
          IllegalArgumentException.class, () -> AnimationWatchViewModel.from(actor(), bad));
    }
    var rows = List.of(track("id", "Title", "key", PairRole.MAIN, 1));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(null, "曲", "ゲーム", new MusicTrackResponseData(1), rows));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), null, "ゲーム", new MusicTrackResponseData(1), rows));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "曲", null, new MusicTrackResponseData(1), rows));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "曲", "ゲーム", null, rows));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "曲", "ゲーム", new MusicTrackResponseData(1), null));
    for (String id : List.of("", ".", ".."))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              MusicTrackViewModel.from(
                  actor(),
                  "曲",
                  "ゲーム",
                  new MusicTrackResponseData(1),
                  List.of(track(id, "Title", "key", PairRole.MAIN, 1))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(),
                "曲",
                "ゲーム",
                new MusicTrackResponseData(201),
                Collections.nCopies(201, rows.getFirst())));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(actor(), "曲", "foreign", new MusicTrackResponseData(1), rows));
    var zero =
        new MusicTrackRecord(
            "id",
            "Title",
            "曲",
            "ゲーム",
            DisplayPath.of("id.m4a"),
            0,
            Optional.of("key"),
            PairRole.MAIN,
            1);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(), "曲", "ゲーム", new MusicTrackResponseData(1), List.of(zero)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(),
                "曲",
                "ゲーム",
                new MusicTrackResponseData(2),
                List.of(
                    track("a", "Title", "key", PairRole.MAIN, 2),
                    track("b", "Title", "other", PairRole.MAIN, 1))));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(),
                "曲",
                "ゲーム",
                new MusicTrackResponseData(2),
                List.of(
                    track("a", "Title", "key", PairRole.MAIN, 1),
                    track("b", "Title", "key", PairRole.MAIN, 2))));
    var absent =
        new MusicTrackRecord(
            "id",
            "Title",
            "曲",
            "ゲーム",
            DisplayPath.of("id.m4a"),
            12,
            Optional.empty(),
            PairRole.MAIN,
            1);
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor(), "曲", "ゲーム", new MusicTrackResponseData(1), List.of(absent)));
  }

  @Test
  void content010ExactUtf8LimitsNfcAndCommonNullBoundaries() throws Exception {
    try (var f = new Fixture()) {
      var model = new ExtendedModelMap();
      var response = new MockHttpServletResponse();
      assertEquals(
          "music-list",
          f.controller.tracks(
              "x".repeat(64), "y".repeat(128), actor(), model, f.request(), response));
      assertEquals(
          "x".repeat(64) + " / " + "y".repeat(128),
          assertInstanceOf(MusicTrackViewModel.class, model.get("page")).getValues().get("title"));
      for (String category : List.of("", "x".repeat(65))) {
        int sent = f.sent.get();
        response = new MockHttpServletResponse();
        assertNull(
            f.controller.tracks(
                category, "section", actor(), new ExtendedModelMap(), f.request(), response));
        assertEquals(400, response.getStatus());
        assertEquals(sent, f.sent.get());
      }
      for (String id : List.of("x".repeat(64), "e\u0301")) {
        model = new ExtendedModelMap();
        assertEquals(
            "animation-watch",
            f.controller.watch(id, actor(), model, f.request(), new MockHttpServletResponse()));
        assertEquals(
            id.length() == 64 ? "/animation/media/" + id : "/animation/media/%C3%A9",
            assertInstanceOf(AnimationWatchViewModel.class, model.get("page"))
                .getValues()
                .get("mediaHref"));
      }
      int sent = f.sent.get();
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.scenario(
                  "23", null, new ExtendedModelMap(), f.request(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.scenario(
                  "23", actor(), null, f.request(), new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () ->
              f.controller.scenario(
                  "23", actor(), new ExtendedModelMap(), null, new MockHttpServletResponse()));
      assertThrows(
          NullPointerException.class,
          () -> f.controller.scenario("23", actor(), new ExtendedModelMap(), f.request(), null));
      assertEquals(sent, f.sent.get());
      assertThrows(
          NullPointerException.class,
          () ->
              MusicTrackViewModel.from(
                  actor(),
                  "曲",
                  "ゲーム",
                  new MusicTrackResponseData(1),
                  Arrays.asList((MusicTrackRecord) null)));
      f.erased();
    }
  }

  private final class Fixture implements AutoCloseable {
    final ApiSessionInvalidTest.Harness security = new ApiSessionInvalidTest.Harness(db);
    final AtomicInteger ids = new AtomicInteger();
    final AtomicInteger sent = new AtomicInteger();
    final Set<UUID> messages = ConcurrentHashMap.newKeySet();
    final List<byte[]> buffers = new CopyOnWriteArrayList<>();
    volatile String code = "0000";
    volatile String category = "OPENING";
    volatile String hash = "a".repeat(64);
    volatile String videoPath = "video/v.mp4";
    volatile int count = 1;
    volatile boolean file;
    volatile boolean wrongId;
    volatile boolean badContext;
    volatile List<MusicTrackRecord> pairRecords = List.of();
    final JmsRequestReplyClient wire =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 12);
    final JmsRequestSender sender =
        (id, b) -> {
          assertTrue(messages.add(id));
          sent.incrementAndGet();
          buffers.add(b);
          assertEquals(id.toString(), ascii(b, 24, 36));
          assertEquals(id.toString(), ascii(b, 60, 36));
          assertTrue(wire.onReply(id, response(id, b)));
        };
    final ScenarioWireClient scenarios =
        new ScenarioWireClient(
            wire, sender, CLOCK, () -> new UUID(0, ids.incrementAndGet()), Duration.ofSeconds(1));
    final MediaDescriptorWireClient media =
        new MediaDescriptorWireClient(
            wire, sender, CLOCK, () -> new UUID(0, ids.incrementAndGet()), Duration.ofSeconds(1));
    final MusicWireClient music =
        new MusicWireClient(
            wire, sender, CLOCK, () -> new UUID(0, ids.incrementAndGet()), Duration.ofSeconds(1));
    final OwnedTransferDirectory held;
    final LargeResultReader reader;
    final ContentDetailController controller;

    Fixture() throws Exception {
      Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
      var a = Files.readAttributes(root, PosixFileAttributes.class);
      held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
      reader =
          new LargeResultReader(
              held, new StorageIdentity(a.owner().getName(), a.group().getName()));
      controller = new ContentDetailController(scenarios, media, music, reader, security.handler);
    }

    MockHttpServletRequest request() throws Exception {
      return security.mock("GET", "/scenarios/23");
    }

    String call(String type, ExtendedModelMap m, MockHttpServletResponse r) throws Exception {
      return switch (type) {
        case "SCN" -> controller.scenario("23", actor(), m, request(), r);
        case "VID" -> controller.watch("opening", actor(), m, request(), r);
        case "MTR" -> controller.tracks("BGM", "ゲーム", actor(), m, request(), r);
        default -> throw new AssertionError();
      };
    }

    void configure(AnnotationConfigWebApplicationContext c, ApiSessionInvalidHandler invalid) {
      c.register(ContentDetailMvcConfiguration.class);
      c.addBeanFactoryPostProcessor(
          factory -> {
            factory.registerSingleton("scenarioWireClient", scenarios);
            factory.registerSingleton("mediaDescriptorWireClient", media);
            factory.registerSingleton("musicWireClient", music);
            factory.registerSingleton("largeResultReader", reader);
            factory.registerSingleton("apiSessionInvalidHandler", invalid);
          });
    }

    AnnotationConfigWebApplicationContext mvc() {
      var c = new AnnotationConfigWebApplicationContext();
      c.setServletContext(new MockServletContext());
      configure(c, security.handler);
      c.refresh();
      return c;
    }

    Path readyFile() {
      return root.resolve("20261004/" + FILE + ".ready");
    }

    void prepareFile() throws Exception {
      Files.createDirectories(readyFile().getParent());
      Files.setPosixFilePermissions(
          readyFile().getParent(), PosixFilePermissions.fromString("rwxr-x---"));
      byte[] b = new byte[4800 * count];
      for (int n = 0; n < count; n++) System.arraycopy(entry(n + 1), 0, b, n * 4800, 4800);
      Files.write(readyFile(), b);
      Files.setPosixFilePermissions(readyFile(), PosixFilePermissions.fromString("rw-r-----"));
      hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(b));
    }

    byte[] response(UUID id, byte[] q) {
      String type = ascii(q, 11, 3);
      boolean ok = code.equals("0000") || code.equals("0200");
      int data = type.equals("SCN") ? 1728 : type.equals("VID") ? 1808 : 16;
      int length = type.equals("SCN") ? 4800 : type.equals("MTR") ? 1312 : 0;
      int requested = type.equals("MTR") && !pairRecords.isEmpty() ? pairRecords.size() : count;
      int records = ok && !type.equals("VID") && !(type.equals("SCN") && file) ? requested : 0;
      byte[] b = new byte[256 + data + records * length];
      Arrays.fill(b, (byte) ' ');
      put(b, 0, "SCHBNK01001");
      put(b, 11, type + "RSP01");
      put(b, 19, "001SS");
      put(b, 24, new UUID(1, id.getLeastSignificantBits()).toString());
      put(b, 60, id.toString());
      put(b, 96, "20261004090000000");
      put(b, 113, badContext ? "c".repeat(64) : ascii(q, 113, 64));
      number(b, 177, 4, 256);
      number(b, 181, 6, data);
      number(b, 187, 6, length);
      number(b, 193, 6, records);
      number(b, 199, 9, b.length);
      put(b, 208, code);
      if (type.equals("SCN")) {
        number(b, 256, 12, ok ? (wrongId ? 24 : 23) : 0);
        number(b, 1877, 12, ok && file ? 4800L * count : 0);
        number(b, 1953, 6, ok && file ? 4800 : 0);
        number(b, 1959, 9, ok && file ? count : 0);
        if (ok) {
          put(b, 268, "NUKITASHI1");
          put(b, 280, "章<script>");
          put(b, 536, "文章/23.txt");
          put(b, 1584, file ? "F" : "I");
          if (file) {
            put(b, 1585, FILE.toString());
            put(b, 1621, "20261004/" + FILE + ".ready");
            put(b, 1889, hash);
          }
        }
        for (int n = 0; n < records; n++)
          System.arraycopy(entry(n + 1), 0, b, 1984 + n * 4800, 4800);
      } else if (type.equals("VID")) {
        number(b, 1088, 12, ok ? 12 : 0);
        if (ok) {
          put(b, 256, new String(q, 256, 64, StandardCharsets.UTF_8).stripTrailing());
          put(b, 320, videoPath);
          put(b, 832, "v.mp4");
          put(b, 1100, hash);
          put(b, 1164, "video/mp4");
          put(b, 1228, "I");
          put(b, 1280, "映像<script>");
          put(b, 1536, category);
          put(b, 1552, "映像/v.mp4");
        }
      } else {
        number(b, 256, 9, records);
        String cat = new String(q, 256, 64, StandardCharsets.UTF_8).stripTrailing();
        String sec = new String(q, 320, 128, StandardCharsets.UTF_8).stripTrailing();
        for (int n = 0; n < records; n++) {
          int o = 272 + n * 1312;
          put(b, o, "track" + (n + 1));
          put(b, o + 64, "曲" + (n + 1));
          put(b, o + 320, cat);
          put(b, o + 384, sec);
          put(b, o + 512, "音楽/" + (n + 1) + ".m4a");
          number(b, o + 1024, 12, 12);
          put(b, o + 1292, "N");
          number(b, o + 1293, 4, n + 1);
          if (!pairRecords.isEmpty()) {
            var track = pairRecords.get(n);
            Arrays.fill(b, o, o + 1312, (byte) ' ');
            put(b, o, track.trackId());
            put(b, o + 64, track.title());
            put(b, o + 320, track.category());
            put(b, o + 384, track.section());
            put(b, o + 512, track.displayPath().wireValue());
            number(b, o + 1024, 12, track.fileByteLength());
            put(b, o + 1036, track.pairKey().orElse(""));
            put(b, o + 1292, track.pairRole().wireValue());
            number(b, o + 1293, 4, track.displayOrder());
          }
        }
      }
      return b;
    }

    void erased() {
      assertEquals(0, wire.pendingCount());
      for (byte[] b : buffers) assertArrayEquals(new byte[b.length], b);
    }

    @Override
    public void close() throws StorageIoException {
      held.close();
      security.close();
    }
  }

  private static byte[] entry(int n) {
    byte[] b = new byte[4800];
    Arrays.fill(b, (byte) ' ');
    number(b, 0, 12, n);
    number(b, 12, 6, n);
    number(b, 18, 8, 42);
    put(b, 26, "narration");
    put(b, 164, "本文");
    put(b, 4260, "000");
    return b;
  }

  private static String ascii(byte[] b, int o, int n) {
    return new String(b, o, n, StandardCharsets.US_ASCII);
  }

  private static void put(byte[] b, int o, String s) {
    byte[] v = s.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(v, 0, b, o, v.length);
  }

  private static void number(byte[] b, int o, int n, long v) {
    put(b, o, String.format(Locale.ROOT, "%0" + n + "d", v));
  }
}
