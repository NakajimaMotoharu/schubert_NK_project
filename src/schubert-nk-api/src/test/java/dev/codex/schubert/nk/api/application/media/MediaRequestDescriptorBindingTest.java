package dev.codex.schubert.nk.api.application.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.media.MediaDescriptorData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.MediaMimeType;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.VideoCategory;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-MED-BIND001..004; UI235 MEDIA1024; memory metadata only, never physical asset authority. */
final class MediaRequestDescriptorBindingTest {
  private static final String AUDIO_LOGICAL_ID = "700";
  private static final String AUDIO_REQUEST = "AUDREQ01";
  private static final String MUSIC_REQUEST = "MEDREQ01";
  private static final String VIDEO_REQUEST = "VIDREQ01";
  private static final String AUDIO_RESPONSE = "AUDRSP01";
  private static final String MUSIC_RESPONSE = "MEDRSP01";
  private static final String VIDEO_RESPONSE = "VIDRSP01";
  private static final String TRACK_ID = "music-0";
  private static final String VIDEO_ID = "opening";
  private static final String HASH = "0".repeat(64);
  private static final long MAXIMUM_LENGTH = 999_999_999_999L;
  private static final int MUSIC_DISPOSITION_OFFSET = 64;

  @Test
  void mediaBind001AudioUsesCanonicalNumericIdAndRequestedDisposition() {
    for (var disposition : ContentDisposition.values()) {
      byte[] bytes = MediaRequestFixture.field(16, 0, "000000000700" + disposition.wireValue());
      var request = MediaRequest.decode(MediaRequestFixture.message(AUDIO_REQUEST, bytes));
      assertTrue(request.descriptorRequest());
      var correct = audio(AUDIO_LOGICAL_ID, disposition);
      var descriptor = request.descriptor(correct).orElseThrow();
      assertEquals(MediaType.AUDIO, descriptor.mediaType());
      assertEquals(AUDIO_LOGICAL_ID, descriptor.logicalId());
      assertEquals("scenario/a.ogg", descriptor.storageRelativePath());
      assertEquals("a.ogg", descriptor.fileName());
      assertEquals(1, descriptor.byteLength());
      assertEquals(HASH, descriptor.sha256());
      assertEquals("audio/ogg", descriptor.mimeType());
      assertEquals(disposition.name(), descriptor.disposition().name());
      assertThrows(
          IllegalArgumentException.class, () -> request.descriptor(audio("701", disposition)));
      var other =
          disposition == ContentDisposition.INLINE
              ? ContentDisposition.ATTACHMENT
              : ContentDisposition.INLINE;
      assertThrows(
          IllegalArgumentException.class, () -> request.descriptor(audio(AUDIO_LOGICAL_ID, other)));
      assertEquals(AUDIO_LOGICAL_ID, request.descriptor(correct).orElseThrow().logicalId());
    }
  }

  @Test
  void mediaBind002MusicKeepsTrackIdAndMaximumMetadataLength() {
    for (var disposition : ContentDisposition.values()) {
      byte[] bytes = MediaRequestFixture.field(72, 0, TRACK_ID);
      MediaRequestFixture.put(bytes, MUSIC_DISPOSITION_OFFSET, disposition.wireValue());
      var request = MediaRequest.decode(MediaRequestFixture.message(MUSIC_REQUEST, bytes));
      assertTrue(request.descriptorRequest());
      var correct = music(TRACK_ID, disposition);
      var descriptor = request.descriptor(correct).orElseThrow();
      assertEquals(MediaType.MUSIC, descriptor.mediaType());
      assertEquals(TRACK_ID, descriptor.logicalId());
      assertEquals(MAXIMUM_LENGTH, descriptor.byteLength());
      assertEquals("music/曲.flac", descriptor.storageRelativePath());
      assertEquals("曲.flac", descriptor.fileName());
      assertEquals("audio/flac", descriptor.mimeType());
      assertEquals(disposition.name(), descriptor.disposition().name());
      assertThrows(
          IllegalArgumentException.class, () -> request.descriptor(music("other", disposition)));
      var other =
          disposition == ContentDisposition.INLINE
              ? ContentDisposition.ATTACHMENT
              : ContentDisposition.INLINE;
      assertThrows(
          IllegalArgumentException.class, () -> request.descriptor(music(TRACK_ID, other)));
      assertEquals(TRACK_ID, request.descriptor(correct).orElseThrow().logicalId());
    }
  }

  @Test
  void mediaBind003VideoIsInlineAndCannotRebindLogicalIdentity() {
    var request =
        MediaRequest.decode(
            MediaRequestFixture.message(VIDEO_REQUEST, MediaRequestFixture.data(VIDEO_REQUEST)));
    assertTrue(request.descriptorRequest());
    var correct = video(VIDEO_ID, ContentDisposition.INLINE);
    var descriptor = request.descriptor(correct).orElseThrow();
    assertEquals(MediaType.VIDEO, descriptor.mediaType());
    assertEquals(VIDEO_ID, descriptor.logicalId());
    assertEquals("video/opening.mp4", descriptor.storageRelativePath());
    assertEquals("video/mp4", descriptor.mimeType());
    assertEquals("INLINE", descriptor.disposition().name());
    assertThrows(
        IllegalArgumentException.class,
        () -> request.descriptor(video("other", ContentDisposition.INLINE)));
    assertThrows(
        IllegalArgumentException.class,
        () -> request.descriptor(video(VIDEO_ID, ContentDisposition.ATTACHMENT)));
    assertThrows(NullPointerException.class, () -> request.descriptor(null));
    assertThrows(
        IllegalArgumentException.class,
        () -> request.descriptor(audio(AUDIO_LOGICAL_ID, ContentDisposition.INLINE)));
    assertEquals(VIDEO_ID, request.descriptor(correct).orElseThrow().logicalId());
  }

  @Test
  void mediaBind004NonDescriptorsReturnEmptyOnlyAfterLayoutCheck() {
    for (String layout : List.of("ANMREQ01", "ANLREQ01", "MCTREQ01", "MCSREQ01", "MTRREQ01")) {
      var request =
          MediaRequest.decode(
              MediaRequestFixture.message(layout, MediaRequestFixture.data(layout)));
      assertFalse(request.descriptorRequest());
      var sameLayout =
          new TypedPayloadValues(
              request.responseLayoutId(), new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
      assertTrue(request.descriptor(sameLayout).isEmpty());
      assertThrows(NullPointerException.class, () -> request.descriptor(null));
      assertThrows(
          IllegalArgumentException.class,
          () -> request.descriptor(audio(AUDIO_LOGICAL_ID, ContentDisposition.INLINE)));
      assertTrue(request.descriptor(sameLayout).isEmpty());
    }
  }

  private static TypedPayloadValues audio(String id, ContentDisposition disposition) {
    return new TypedPayloadValues(
        new LayoutId(AUDIO_RESPONSE),
        new MediaDescriptorData(
            id,
            RelativePath.of("scenario/a.ogg"),
            "a.ogg",
            1,
            Sha256Hex.of(HASH),
            MediaMimeType.AUDIO_OGG,
            disposition),
        List.of());
  }

  private static TypedPayloadValues music(String id, ContentDisposition disposition) {
    return new TypedPayloadValues(
        new LayoutId(MUSIC_RESPONSE),
        new MediaDescriptorData(
            id,
            RelativePath.of("music/曲.flac"),
            "曲.flac",
            MAXIMUM_LENGTH,
            Sha256Hex.of(HASH),
            MediaMimeType.AUDIO_FLAC,
            disposition),
        List.of());
  }

  private static TypedPayloadValues video(String id, ContentDisposition disposition) {
    return new TypedPayloadValues(
        new LayoutId(VIDEO_RESPONSE),
        new VideoDescriptorResponseData(
            id,
            RelativePath.of("video/opening.mp4"),
            "opening.mp4",
            1,
            Sha256Hex.of(HASH),
            MediaMimeType.VIDEO_MP4,
            disposition,
            "Opening",
            VideoCategory.OPENING,
            DisplayPath.of("opening.mp4")),
        List.of());
  }
}
