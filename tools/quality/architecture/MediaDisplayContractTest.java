package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

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
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** UI223/235/SS313; MEDIA-DISPLAY001..012. No real file/hash/client/streaming actions. */
final class MediaDisplayContractTest {
  private static SessionPrincipal actor() {
    return new SessionPrincipal("PUBLIC_DISPLAY", UserRole.USER,
        AuthenticationContext.of("a".repeat(64)), Instant.parse("2026-11-01T00:00:00Z"));
  }

  private static VideoDescriptorResponseData video(String id, VideoCategory category) {
    return new VideoDescriptorResponseData(id, RelativePath.of("assets/public.mp4"),
        "public.mp4", 1, Sha256Hex.of("0".repeat(64)), MediaMimeType.VIDEO_MP4,
        ContentDisposition.INLINE, "PUBLIC VIDEO", category, DisplayPath.of("video/public.mp4"));
  }

  private static MusicTrackRecord track(String id, String title, String category, String section,
      long size, Optional<String> key, PairRole role, int order) {
    return new MusicTrackRecord(id, title, category, section, DisplayPath.of("music/public.mp3"),
        size, key, role, order);
  }

  private static MusicTrackRecord simple(String id, String title, int order) {
    return track(id, title, "BGM", "PUBLIC", 1, Optional.empty(), PairRole.NONE, order);
  }

  private static Map<String, Object> songs(List<MusicTrackRecord> rows) {
    return MusicTrackViewModel.from(actor(), "曲", "PUBLIC",
        new MusicTrackResponseData(rows.size()), rows).getValues();
  }

  private static MusicTrackRecord song(String id, String title, Optional<String> key,
      PairRole role, int order) {
    return track(id, title, "曲", "PUBLIC", 1, key, role, order);
  }

  private static List<?> list(Map<String, Object> values, String name) {
    return (List<?>) values.get(name);
  }

  private static Map<?, ?> map(Object value) {
    return (Map<?, ?>) value;
  }

  private static Optional<?> slot(Map<?, ?> pair, String name) {
    return (Optional<?>) pair.get(name);
  }

  @Test
  void mediaDisplay001VideoCategoryNavigationAndPublicFieldsAreExactlyBounded() {
    var expected = Map.of(
        VideoCategory.MAIN, List.of("メインパート", "/animation/main", "メインパート一覧"),
        VideoCategory.SUBTRACK, List.of("メインパート", "/animation/main", "メインパート一覧"),
        VideoCategory.OVA, List.of("OVA", "/animation/ova", "OVA一覧"),
        VideoCategory.OPENING, List.of("オープニング", "/animation", "アニメ視聴"));
    for (var entry : expected.entrySet()) {
      var page = AnimationWatchViewModel.from(actor(), video("public/id?あ", entry.getKey()));
      var values = page.getValues();
      assertEquals(Set.of("topBar", "title", "category", "displayPath", "backHref", "backLabel",
          "mediaHref"), values.keySet());
      assertEquals("PUBLIC VIDEO", values.get("title"));
      assertEquals(entry.getValue().get(0), values.get("category"));
      assertEquals(entry.getValue().get(1), values.get("backHref"));
      assertEquals(entry.getValue().get(2), values.get("backLabel"));
      assertEquals("video/public.mp4", values.get("displayPath"));
      assertEquals("/animation/media/public%2Fid%3F%E3%81%82", values.get("mediaHref"));
      assertEquals("PUBLIC_DISPLAY", ((TopBarViewModel) values.get("topBar")).getUsername());
      assertEquals("AnimationWatchViewModel[REDACTED]", page.toString());
      assertThrows(UnsupportedOperationException.class, () -> values.clear());
    }
  }

  @Test
  void mediaDisplay002VideoMissingAndDotIdsAndNullsRejectWithoutOpeningDescriptor() {
    for (String id : List.of("", ".", "..")) {
      assertEquals("invalid video link ID", assertThrows(IllegalArgumentException.class,
          () -> AnimationWatchViewModel.from(actor(), video(id, VideoCategory.MAIN))).getMessage());
    }
    assertThrows(NullPointerException.class,
        () -> AnimationWatchViewModel.from(null, video("public", VideoCategory.MAIN)));
    assertThrows(NullPointerException.class, () -> AnimationWatchViewModel.from(actor(), null));
  }

  @Test
  void mediaDisplay003EmptyBackgroundMusicHasNoPairsAndOnlyClosedOutput() {
    var page = MusicTrackViewModel.from(actor(), "BGM", "PUBLIC",
        new MusicTrackResponseData(0), List.of());
    var values = page.getValues();
    assertEquals(Set.of("topBar", "category", "section", "title", "trackCount", "songs",
        "categoryHref", "tracks", "pairs"), values.keySet());
    assertEquals("BGM / PUBLIC", values.get("title"));
    assertEquals(0, values.get("trackCount"));
    assertEquals(false, values.get("songs"));
    assertEquals("/music/BGM", values.get("categoryHref"));
    assertTrue(list(values, "tracks").isEmpty());
    assertTrue(list(values, "pairs").isEmpty());
    assertEquals("PUBLIC_DISPLAY", ((TopBarViewModel) values.get("topBar")).getUsername());
    assertEquals("MusicTrackViewModel[REDACTED]", page.toString());
  }

  @Test
  void mediaDisplay004MaximumTwoHundredRowsAreIndependentImmutableTrackSnapshots() {
    var caller = new ArrayList<MusicTrackRecord>();
    for (int i = 0; i < 200; i++) caller.add(simple("t" + i, "PUBLIC " + i, i));
    var values = MusicTrackViewModel.from(actor(), "BGM", "PUBLIC",
        new MusicTrackResponseData(200), caller).getValues();
    caller.clear();
    var tracks = list(values, "tracks");
    assertEquals(200, values.get("trackCount"));
    assertEquals(200, tracks.size());
    assertEquals(Map.of("title", "PUBLIC 0", "displayPath", "music/public.mp3", "byteSize", 1L,
        "mediaHref", "/music/media/t0", "downloadHref", "/music/download/t0"), tracks.getFirst());
    assertEquals("PUBLIC 199", map(tracks.getLast()).get("title"));
    assertTrue(list(values, "pairs").isEmpty());
    assertThrows(UnsupportedOperationException.class, () -> values.clear());
    assertThrows(UnsupportedOperationException.class, () -> tracks.clear());
    assertThrows(UnsupportedOperationException.class, () -> map(tracks.getFirst()).clear());
  }

  @Test
  void mediaDisplay005StoredMainAndInstrumentalRolesWinInEitherArrivalOrder() {
    for (boolean instrumentalFirst : new boolean[] {false, true}) {
      var rows = instrumentalFirst
          ? List.of(song("i", "01-02 OLD instrument", Optional.of("p"), PairRole.INSTRUMENTAL, 0),
              song("m", "01-01 MAIN", Optional.of("p"), PairRole.MAIN, 1))
          : List.of(song("m", "01-01 MAIN", Optional.of("p"), PairRole.MAIN, 0),
              song("i", "01-02 OLD instrument", Optional.of("p"), PairRole.INSTRUMENTAL, 1));
      var values = songs(rows);
      assertEquals(true, values.get("songs"));
      assertEquals("/music/%E6%9B%B2", values.get("categoryHref"));
      assertEquals(1, list(values, "pairs").size());
      var pair = map(list(values, "pairs").getFirst());
      assertEquals(Set.of("title", "main", "instrumental"), pair.keySet());
      assertEquals("MAIN", pair.get("title"));
      assertEquals("/music/media/m", map(slot(pair, "main").orElseThrow()).get("mediaHref"));
      assertEquals("/music/media/i", map(slot(pair, "instrumental").orElseThrow()).get("mediaHref"));
      assertEquals(instrumentalFirst ? "01-02 OLD instrument" : "01-01 MAIN",
          map(list(values, "tracks").getFirst()).get("title"));
      assertThrows(UnsupportedOperationException.class, () -> pair.clear());
      assertThrows(UnsupportedOperationException.class, () -> list(values, "pairs").clear());
    }
  }

  @Test
  void mediaDisplay006NoneAndMissingStoredSidesNeverInferMatchesFromTitles() {
    var none = songs(List.of(
        song("a", "01-01 SAME", Optional.empty(), PairRole.NONE, 0),
        song("b", "01-02 SAME (inst)", Optional.empty(), PairRole.NONE, 1)));
    assertEquals(2, list(none, "pairs").size());
    for (Object value : list(none, "pairs")) {
      var pair = map(value);
      assertEquals("SAME", pair.get("title"));
      assertTrue(slot(pair, "main").isPresent());
      assertTrue(slot(pair, "instrumental").isEmpty());
    }
    var onlyMain = map(list(songs(List.of(
        song("m", "PUBLIC MAIN", Optional.of("p"), PairRole.MAIN, 0))), "pairs").getFirst());
    assertTrue(slot(onlyMain, "main").isPresent());
    assertTrue(slot(onlyMain, "instrumental").isEmpty());
    var onlyInst = map(list(songs(List.of(
        song("i", "PUBLIC SOLO (inst)", Optional.of("p"), PairRole.INSTRUMENTAL, 0))), "pairs").getFirst());
    assertEquals("PUBLIC SOLO", onlyInst.get("title"));
    assertTrue(slot(onlyInst, "main").isEmpty());
    assertTrue(slot(onlyInst, "instrumental").isPresent());
  }

  @Test
  void mediaDisplay007CurrentTitleRuleUsesIndependentLiteralVectorsNotFilesystemMatching() {
    String[] input = {"01-02 PUBLIC SONG", "PUBLIC SONG (Inst.)",
        "PUBLIC SONG （instrumental） extra", "PUBLIC SONG Instrumental extra",
        "さくら（INST）", "PUBLIC SONG"};
    String[] expected = {"PUBLIC SONG", "PUBLIC SONG", "PUBLIC SONG", "PUBLIC SONG", "さくら", "PUBLIC SONG"};
    for (int i = 0; i < input.length; i++) {
      var pair = map(list(songs(List.of(
          song("p", input[i], Optional.empty(), PairRole.NONE, 0))), "pairs").getFirst());
      assertEquals(expected[i], pair.get("title"));
    }
  }

  @Test
  void mediaDisplay008OversizeAndDeclaredCountMismatchAreRejected() {
    var rows = new ArrayList<MusicTrackRecord>();
    for (int i = 0; i < 201; i++) rows.add(simple("t" + i, "PUBLIC", i));
    assertEquals("invalid music track count", assertThrows(IllegalArgumentException.class,
        () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC",
            new MusicTrackResponseData(201), rows)).getMessage());
    assertThrows(IllegalArgumentException.class, () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC",
        new MusicTrackResponseData(2), List.of(simple("p", "PUBLIC", 0))));
  }

  @Test
  void mediaDisplay009EachRecordBindingIdentitySizeAndOrderFailureIsRejected() {
    var damaged = List.of(
        List.of(track("p", "PUBLIC", "曲", "PUBLIC", 1, Optional.empty(), PairRole.NONE, 0)),
        List.of(track("p", "PUBLIC", "BGM", "OTHER", 1, Optional.empty(), PairRole.NONE, 0)),
        List.of(simple("p", "PUBLIC", 0), simple("p", "PUBLIC", 1)),
        List.of(track("p", "PUBLIC", "BGM", "PUBLIC", 0, Optional.empty(), PairRole.NONE, 0)),
        List.of(simple("p", "PUBLIC", 1), simple("q", "PUBLIC", 0)));
    for (var rows : damaged) {
      assertEquals("invalid bound music track", assertThrows(IllegalArgumentException.class,
          () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC",
              new MusicTrackResponseData(rows.size()), rows)).getMessage());
    }
    var equalOrder = MusicTrackViewModel.from(actor(), "BGM", "PUBLIC", new MusicTrackResponseData(2),
        List.of(simple("p", "PUBLIC P", 0), simple("q", "PUBLIC Q", 0))).getValues();
    assertEquals("PUBLIC P", map(list(equalOrder, "tracks").getFirst()).get("title"));
    assertEquals("PUBLIC Q", map(list(equalOrder, "tracks").getLast()).get("title"));
  }

  @Test
  void mediaDisplay010PairedRolesRequireStoredKeyAndRejectDuplicateSlots() {
    assertThrows(IllegalArgumentException.class,
        () -> songs(List.of(song("p", "PUBLIC", Optional.empty(), PairRole.MAIN, 0))));
    for (PairRole role : List.of(PairRole.MAIN, PairRole.INSTRUMENTAL)) {
      assertEquals("duplicate music pair role", assertThrows(IllegalArgumentException.class,
          () -> songs(List.of(song("p", "PUBLIC", Optional.of("p"), role, 0),
              song("q", "PUBLIC", Optional.of("p"), role, 1)))).getMessage());
    }
  }

  @Test
  void mediaDisplay011LinkSegmentsRejectEmptyAndDotAndEncodeReservedBytes() {
    for (String value : List.of("", ".", "..")) {
      assertEquals("invalid music link segment", assertThrows(IllegalArgumentException.class,
          () -> MusicTrackViewModel.from(actor(), value, "PUBLIC",
              new MusicTrackResponseData(0), List.of())).getMessage());
      assertThrows(IllegalArgumentException.class,
          () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC",
              new MusicTrackResponseData(1), List.of(simple(value, "PUBLIC", 0))));
    }
    var values = MusicTrackViewModel.from(actor(), "BGM", "PUBLIC", new MusicTrackResponseData(1),
        List.of(simple("public/id?あ", "PUBLIC", 0))).getValues();
    var item = map(list(values, "tracks").getFirst());
    assertEquals("/music/media/public%2Fid%3F%E3%81%82", item.get("mediaHref"));
    assertEquals("/music/download/public%2Fid%3F%E3%81%82", item.get("downloadHref"));
  }

  @Test
  void mediaDisplay012RequiredActorCategorySectionDataCollectionAndElementsRejectNull() {
    var count = new MusicTrackResponseData(0);
    assertThrows(NullPointerException.class,
        () -> MusicTrackViewModel.from(null, "BGM", "PUBLIC", count, List.of()));
    assertThrows(NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), null, "PUBLIC", count, List.of()));
    assertThrows(NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "BGM", null, count, List.of()));
    assertThrows(NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC", null, List.of()));
    assertThrows(NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC", count, null));
    assertThrows(NullPointerException.class,
        () -> MusicTrackViewModel.from(actor(), "BGM", "PUBLIC", new MusicTrackResponseData(1),
            Arrays.asList((MusicTrackRecord) null)));
  }
}
