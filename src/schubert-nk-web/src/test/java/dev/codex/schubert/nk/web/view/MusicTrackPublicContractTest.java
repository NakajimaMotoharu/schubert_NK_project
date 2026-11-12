package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackRecord;
import dev.codex.schubert.nk.protocol.layout.media.MusicTrackResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.PairRole;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-MUSIC-TRACK-PUBLIC001..006 / UI223235 / SS313323. Public metadata projection only. */
@Timeout(20)
final class MusicTrackPublicContractTest {
  private static final String BGM = "BGM";
  private static final String SONGS = "曲";
  private static final String SECTION = "ゲーム";
  private static final String MEDIA = "mediaHref";
  private static final String TITLE = "title";
  private static final String MAIN = "main";
  private static final String INSTRUMENTAL = "instrumental";
  private static final String TRACK_COUNT = "trackCount";
  private static final String TRACKS = "tracks";
  private static final String PAIRS = "pairs";
  private static final String FIXED_BOUND_FAILURE = "invalid bound music track";

  private static SessionPrincipal actor(String name) {
    return new SessionPrincipal(
        name, UserRole.USER, AuthenticationContext.of("12".repeat(32)), Instant.EPOCH);
  }

  private static MusicTrackRecord row(
      String id,
      String title,
      String category,
      String section,
      long bytes,
      Optional<String> key,
      PairRole role,
      int order) {
    return new MusicTrackRecord(
        id, title, category, section, DisplayPath.of("display/track.mp3"), bytes, key, role, order);
  }

  private static MusicTrackRecord plain(String id, int order) {
    return row(id, "literal title", BGM, SECTION, 1, Optional.empty(), PairRole.NONE, order);
  }

  private static MusicTrackViewModel view(String category, List<MusicTrackRecord> input) {
    return MusicTrackViewModel.from(
        actor("public-listener"),
        category,
        SECTION,
        new MusicTrackResponseData(input.size()),
        input);
  }

  @Test
  void public001OrdinaryOrderUriAndMetadata() {
    var first = plain("音/7?%", 1);
    var second = plain("alpha", 2);
    var page = view(BGM, List.of(first, second));
    var values = page.getValues();
    assertFalse((Boolean) values.get("songs"));
    assertEquals("BGM / ゲーム", values.get(TITLE));
    assertEquals(2, values.get(TRACK_COUNT));
    assertEquals("/music/BGM", values.get("categoryHref"));
    var tracks = (List<?>) values.get(TRACKS);
    var track = (Map<?, ?>) tracks.getFirst();
    assertEquals("/music/media/%E9%9F%B3%2F7%3F%25", track.get(MEDIA));
    assertEquals("/music/download/%E9%9F%B3%2F7%3F%25", track.get("downloadHref"));
    assertEquals("display/track.mp3", track.get("displayPath"));
    assertEquals(1L, track.get("byteSize"));
    assertEquals("/music/media/alpha", ((Map<?, ?>) tracks.getLast()).get(MEDIA));
    assertTrue(((List<?>) values.get(PAIRS)).isEmpty());
    assertEquals("MusicTrackViewModel[REDACTED]", page.toString());
  }

  @Test
  void public002StoredPairOrderAndMainTitlePrecedence() {
    var records =
        List.of(
            row(
                "i1",
                "02-01 Moon (INSTRUMENTAL)",
                SONGS,
                SECTION,
                1,
                Optional.of("moon"),
                PairRole.INSTRUMENTAL,
                1),
            row("m1", "02-01 Moon", SONGS, SECTION, 1, Optional.of("moon"), PairRole.MAIN, 2),
            row(
                "m2",
                "03-02 Sun inst version",
                SONGS,
                SECTION,
                1,
                Optional.of("sun"),
                PairRole.MAIN,
                3),
            row(
                "solo",
                "04-03 Solo instrument",
                SONGS,
                SECTION,
                1,
                Optional.of("ignored-for-NONE"),
                PairRole.NONE,
                4),
            row(
                "i2",
                "05-01 Sky (inst)",
                SONGS,
                SECTION,
                1,
                Optional.of("sky"),
                PairRole.INSTRUMENTAL,
                5));
    var values = view(SONGS, records).getValues();
    assertTrue((Boolean) values.get("songs"));
    var pairs = (List<?>) values.get(PAIRS);
    assertEquals(
        List.of("Moon", "Sun", "Solo", "Sky"),
        pairs.stream().map(x -> ((Map<?, ?>) x).get(TITLE)).toList());
    var first = (Map<?, ?>) pairs.getFirst();
    var main = (Map<?, ?>) ((Optional<?>) first.get(MAIN)).orElseThrow();
    var instrumental = (Map<?, ?>) ((Optional<?>) first.get(INSTRUMENTAL)).orElseThrow();
    assertEquals("/music/media/m1", main.get(MEDIA));
    assertEquals("/music/media/i1", instrumental.get(MEDIA));
    assertTrue(((Optional<?>) ((Map<?, ?>) pairs.get(1)).get(INSTRUMENTAL)).isEmpty());
    assertTrue(((Optional<?>) ((Map<?, ?>) pairs.getLast()).get(MAIN)).isEmpty());
    assertEquals(5, values.get(TRACK_COUNT));
    assertEquals(4, pairs.size());
  }

  @Test
  void public003CountAffinityIdentityLengthAndOrderBounds() {
    assertEquals(0, view(BGM, List.of()).getValues().get(TRACK_COUNT));
    var maximum = new ArrayList<MusicTrackRecord>();
    for (int i = 0; i < 200; i++) maximum.add(plain("v" + i, i));
    assertEquals(200, view(BGM, maximum).getValues().get(TRACK_COUNT));
    maximum.add(plain("v200", 200));
    assertEquals(
        "invalid music track count",
        assertThrows(IllegalArgumentException.class, () -> view(BGM, maximum)).getMessage());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            MusicTrackViewModel.from(
                actor("public-listener"),
                BGM,
                SECTION,
                new MusicTrackResponseData(0),
                List.of(plain("id", 0))));
    var invalids =
        List.of(
            List.of(row("id", "x", "other", SECTION, 1, Optional.empty(), PairRole.NONE, 0)),
            List.of(row("id", "x", BGM, "other", 1, Optional.empty(), PairRole.NONE, 0)),
            List.of(plain("same", 0), plain("same", 1)),
            List.of(row("id", "x", BGM, SECTION, 0, Optional.empty(), PairRole.NONE, 0)),
            List.of(plain("a", 2), plain("b", 1)));
    for (var input : invalids)
      assertEquals(
          FIXED_BOUND_FAILURE,
          assertThrows(IllegalArgumentException.class, () -> view(BGM, input)).getMessage());
    assertEquals(2, view(BGM, List.of(plain("a", 1), plain("b", 1))).getValues().get(TRACK_COUNT));
  }

  @Test
  void public004MissingPairDuplicateRoleAndLinkSegments() {
    var missingKey = row("id", "x", SONGS, SECTION, 1, Optional.empty(), PairRole.MAIN, 0);
    assertThrows(IllegalArgumentException.class, () -> view(SONGS, List.of(missingKey)));
    var duplicateRole =
        List.of(
            row("a", "x", SONGS, SECTION, 1, Optional.of("pair"), PairRole.MAIN, 0),
            row("b", "x", SONGS, SECTION, 1, Optional.of("pair"), PairRole.MAIN, 1));
    assertEquals(
        "duplicate music pair role",
        assertThrows(IllegalArgumentException.class, () -> view(SONGS, duplicateRole))
            .getMessage());
    for (String bad : List.of("", ".", "..")) {
      assertEquals(
          "invalid music link segment",
          assertThrows(IllegalArgumentException.class, () -> view(bad, List.of())).getMessage());
      assertEquals(
          "invalid music link segment",
          assertThrows(IllegalArgumentException.class, () -> view(BGM, List.of(plain(bad, 0))))
              .getMessage());
    }
  }

  @Test
  void public005NullOwnershipAndClosedMap() {
    var actor = actor("public-listener");
    var data = new MusicTrackResponseData(0);
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(null, BGM, SECTION, data, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor, null, SECTION, data, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor, BGM, null, data, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor, BGM, SECTION, null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> MusicTrackViewModel.from(actor, BGM, SECTION, data, null));
    assertThrows(
        NullPointerException.class,
        () ->
            MusicTrackViewModel.from(
                actor, BGM, SECTION, data, Arrays.asList((MusicTrackRecord) null)));
    var original = new ArrayList<>(List.of(plain("id", 0)));
    var values = view(BGM, original).getValues();
    original.clear();
    assertEquals(1, ((List<?>) values.get(TRACKS)).size());
    assertEquals(
        Set.of(
            "topBar",
            "category",
            "section",
            TITLE,
            TRACK_COUNT,
            "songs",
            "categoryHref",
            TRACKS,
            PAIRS),
        values.keySet());
    assertThrows(UnsupportedOperationException.class, values::clear);
    assertThrows(UnsupportedOperationException.class, ((List<?>) values.get(TRACKS))::clear);
    assertThrows(
        UnsupportedOperationException.class,
        ((Map<?, ?>) ((List<?>) values.get(TRACKS)).getFirst())::clear);
    var pairValues =
        view(SONGS, List.of(row("id", "x", SONGS, SECTION, 1, Optional.empty(), PairRole.NONE, 0)))
            .getValues();
    assertThrows(UnsupportedOperationException.class, ((List<?>) pairValues.get(PAIRS))::clear);
    assertThrows(
        UnsupportedOperationException.class,
        ((Map<?, ?>) ((List<?>) pairValues.get(PAIRS)).getFirst())::clear);
  }

  @Test
  void public006FiniteConcurrentProjectionsRemainIndependent() throws Exception {
    var pool = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Future<?>>();
      for (int i = 0; i < 16; i++) {
        int n = i;
        tasks.add(
            pool.submit(
                () -> {
                  var values =
                      MusicTrackViewModel.from(
                              actor("listener" + n),
                              BGM,
                              SECTION,
                              new MusicTrackResponseData(1),
                              List.of(plain("id-" + n, 0)))
                          .getValues();
                  assertEquals(
                      "listener" + n, ((TopBarViewModel) values.get("topBar")).getUsername());
                  assertEquals(
                      "/music/media/id-" + n,
                      ((Map<?, ?>) ((List<?>) values.get(TRACKS)).getFirst()).get(MEDIA));
                  assertEquals(1, values.get(TRACK_COUNT));
                }));
      }
      for (var task : tasks) task.get(5, TimeUnit.SECONDS);
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
