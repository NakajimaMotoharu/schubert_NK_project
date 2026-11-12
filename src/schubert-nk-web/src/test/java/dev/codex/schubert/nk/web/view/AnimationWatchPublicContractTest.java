package dev.codex.schubert.nk.web.view;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.MediaMimeType;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.protocol.layout.semantic.VideoCategory;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import java.time.Instant;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-ANIMATION-WATCH-PUBLIC001..004 / SCR010 / UI223235 / SS313323. Display DTO only. */
@Timeout(10)
final class AnimationWatchPublicContractTest {
  private static final String FIXTURE_CLIP_ID = "clip-7";
  private static final String FIXTURE_NAME = "watch-reader";
  private static final String FIXTURE_TITLE = "public watch title";
  private static final String EXPECTED_REDACTED = "AnimationWatchViewModel[REDACTED]";

  private static SessionPrincipal actor(UserRole role) {
    return new SessionPrincipal(
        FIXTURE_NAME,
        role,
        AuthenticationContext.of("12".repeat(32)),
        Instant.parse("2026-11-01T00:00:00Z"));
  }

  private static VideoDescriptorResponseData data(String id, VideoCategory category) {
    return new VideoDescriptorResponseData(
        id,
        RelativePath.of("fixture/not-displayed.mp4"),
        "not-displayed.mp4",
        19,
        Sha256Hex.of("34".repeat(32)),
        MediaMimeType.VIDEO_MP4,
        ContentDisposition.INLINE,
        FIXTURE_TITLE,
        category,
        DisplayPath.of("display/movie.mp4"));
  }

  @Test
  void public001AllCategoryNavigationAndRoles() {
    String[][] vectors = {
      {"MAIN", "メインパート", "/animation/main", "メインパート一覧"},
      {"SUBTRACK", "メインパート", "/animation/main", "メインパート一覧"},
      {"OVA", "OVA", "/animation/ova", "OVA一覧"},
      {"OPENING", "オープニング", "/animation", "アニメ視聴"}
    };
    for (UserRole role : UserRole.values()) {
      for (String[] vector : vectors) {
        var view =
            AnimationWatchViewModel.from(
                actor(role), data(FIXTURE_CLIP_ID, VideoCategory.valueOf(vector[0])));
        var values = view.getValues();
        assertEquals(vector[1], values.get("category"));
        assertEquals(vector[2], values.get("backHref"));
        assertEquals(vector[3], values.get("backLabel"));
        assertEquals(FIXTURE_TITLE, values.get("title"));
        assertEquals("display/movie.mp4", values.get("displayPath"));
        var top = (TopBarViewModel) values.get("topBar");
        assertNotNull(top);
        assertEquals(FIXTURE_NAME, top.getUsername());
        assertEquals(role == UserRole.USER ? "USER" : "ADMIN", top.getRole());
        assertEquals("schubert NK", top.getBrand());
        assertEquals("TopBarViewModel[REDACTED]", top.toString());
        assertEquals(EXPECTED_REDACTED, view.toString());
      }
    }
  }

  @Test
  void public002IndependentUtf8LogicalIdVector() {
    var view =
        AnimationWatchViewModel.from(actor(UserRole.USER), data("映像/a+b?", VideoCategory.OVA));
    // UTF-8 E6 98 A0 / E5 83 8F; reserved slash, plus and question mark are encoded.
    assertEquals(
        "/animation/media/%E6%98%A0%E5%83%8F%2Fa%2Bb%3F", view.getValues().get("mediaHref"));
    var opening =
        AnimationWatchViewModel.from(actor(UserRole.USER), data("opening", VideoCategory.OPENING));
    assertEquals("/animation/media/opening", opening.getValues().get("mediaHref"));
  }

  @Test
  void public003NullAndInvalidLogicalIdBoundaries() {
    var actor = actor(UserRole.USER);
    var valid = data(FIXTURE_CLIP_ID, VideoCategory.MAIN);
    assertThrows(NullPointerException.class, () -> AnimationWatchViewModel.from(null, valid));
    assertThrows(NullPointerException.class, () -> AnimationWatchViewModel.from(actor, null));
    for (String id : new String[] {"", ".", ".."}) {
      var invalid = data(id, VideoCategory.MAIN);
      var error =
          assertThrows(
              IllegalArgumentException.class, () -> AnimationWatchViewModel.from(actor, invalid));
      assertEquals("invalid video link ID", error.getMessage());
    }
  }

  @Test
  void public004ImmutableClosedDisplayMap() {
    var input = data(FIXTURE_CLIP_ID, VideoCategory.MAIN);
    var view = AnimationWatchViewModel.from(actor(UserRole.USER), input);
    var values = view.getValues();
    assertSame(values, view.getValues());
    assertEquals(
        Set.of("topBar", "title", "category", "displayPath", "backHref", "backLabel", "mediaHref"),
        values.keySet());
    assertThrows(UnsupportedOperationException.class, () -> values.put("storageRelativePath", "x"));
    assertThrows(UnsupportedOperationException.class, values::clear);
    assertFalse(values.values().contains(input));
    assertFalse(values.values().contains(input.storageRelativePath().wireValue()));
    assertFalse(values.values().contains(input.fileName()));
    assertFalse(values.values().contains(input.sha256().wireValue()));
    assertEquals(EXPECTED_REDACTED, view.toString());
  }
}
