package dev.codex.schubert.nk.protocol.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

class MediaDescriptorValidatorTest {
  private static final String HASH = "0".repeat(64);

  @Test
  void acceptsExactlySevenSsc004ExtensionMimePairs() {
    List<MediaDescriptor> descriptors =
        List.of(
            media(
                MediaType.AUDIO,
                "scenario/game/audio/sample.ogg",
                "sample.ogg",
                "audio/ogg",
                ContentDisposition.INLINE),
            media(
                MediaType.VIDEO,
                "video/main/sample.mp4",
                "sample.mp4",
                "video/mp4",
                ContentDisposition.INLINE),
            media(
                MediaType.MUSIC,
                "music/sample.m4a",
                "sample.m4a",
                "audio/mp4",
                ContentDisposition.INLINE),
            media(
                MediaType.MUSIC,
                "music/sample.mp3",
                "sample.mp3",
                "audio/mpeg",
                ContentDisposition.ATTACHMENT),
            media(
                MediaType.MUSIC,
                "music/sample.ogg",
                "sample.ogg",
                "audio/ogg",
                ContentDisposition.INLINE),
            media(
                MediaType.MUSIC,
                "music/sample.wav",
                "sample.wav",
                "audio/wav",
                ContentDisposition.INLINE),
            media(
                MediaType.MUSIC,
                "music/sample.flac",
                "sample.flac",
                "audio/flac",
                ContentDisposition.ATTACHMENT));
    assertEquals(7, descriptors.size());
    MediaDescriptor descriptor = descriptors.getFirst();
    assertEquals(MediaType.AUDIO, descriptor.mediaType());
    assertEquals("media-1", descriptor.logicalId());
    assertEquals("scenario/game/audio/sample.ogg", descriptor.storageRelativePath());
    assertEquals("sample.ogg", descriptor.fileName());
    assertEquals(1, descriptor.byteLength());
    assertEquals(HASH, descriptor.sha256());
    assertEquals("audio/ogg", descriptor.mimeType());
    assertEquals(ContentDisposition.INLINE, descriptor.disposition());
    assertTrue(descriptor.toString().contains("storageRelativePath=REDACTED"));
    assertFalse(descriptor.toString().contains(descriptor.storageRelativePath()));
    MediaDescriptorValidator.validate(descriptor);
    assertThrows(NullPointerException.class, () -> MediaDescriptorValidator.validate(null));
    assertEquals(3, MediaType.values().length);
    assertEquals(MediaType.MUSIC, MediaType.valueOf("MUSIC"));
  }

  @Test
  void dispositionMapsOnlyIAndA() {
    assertEquals(ContentDisposition.INLINE, ContentDisposition.fromWire("I"));
    assertEquals(ContentDisposition.ATTACHMENT, ContentDisposition.fromWire("A"));
    assertEquals('I', ContentDisposition.INLINE.wireValue());
    assertEquals(2, ContentDisposition.values().length);
    assertEquals(ContentDisposition.ATTACHMENT, ContentDisposition.valueOf("ATTACHMENT"));
    assertThrows(NullPointerException.class, () -> ContentDisposition.fromWire(null));
    assertThrows(IllegalArgumentException.class, () -> ContentDisposition.fromWire("inline"));
  }

  @Test
  void rejectsNonCanonicalTextPathsNamesSizesAndHashes() {
    assertInvalid(
        "",
        "video/a.mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "e\u0301",
        "video/a.mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "あ".repeat(22),
        "video/a.mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "id ",
        "video/a.mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    for (String logicalId : new String[] {"id\r", "id\n", "id\t", "id\0"}) {
      assertInvalid(
          logicalId,
          "video/a.mp4",
          "a.mp4",
          1,
          HASH,
          "video/mp4",
          MediaType.VIDEO,
          ContentDisposition.INLINE);
    }

    for (String path :
        new String[] {
          "/video/a.mp4", "video/a.mp4/", "video\\a.mp4", "video//a.mp4",
          "video/./a.mp4", "video/../a.mp4", "music/a.mp4", "video/a.mp4 "
        }) {
      assertInvalid(
          "media-1",
          path,
          "a.mp4",
          1,
          HASH,
          "video/mp4",
          MediaType.VIDEO,
          ContentDisposition.INLINE);
    }
    assertInvalid(
        "media-1",
        "video/" + "あ".repeat(170) + ".mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a\u0001.mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);

    for (String name :
        new String[] {"a/b.mp4", "a\\b.mp4", "a\"b.mp4", "a'b.mp4", "a\u0001.mp4", "a.mp4 "}) {
      assertInvalid(
          "media-1",
          "video/a.mp4",
          name,
          1,
          HASH,
          "video/mp4",
          MediaType.VIDEO,
          ContentDisposition.INLINE);
    }
    assertInvalid(
        "media-1",
        "video/a.mp4",
        "あ".repeat(86),
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a.mp4",
        "a.mp4",
        0,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a.mp4",
        "a.mp4",
        1_000_000_000_000L,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a.mp4",
        "a.mp4",
        1,
        "A".repeat(64),
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
  }

  @Test
  void rejectsEveryMimeCrossProductAndVideoAttachment() {
    assertInvalid(
        "media-1",
        "scenario/game/audio/a.mp3",
        "a.mp3",
        1,
        HASH,
        "audio/mpeg",
        MediaType.AUDIO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "scenario/game/audio/a.ogg",
        "a.ogg",
        1,
        HASH,
        "audio/mpeg",
        MediaType.AUDIO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a.m4v",
        "a.m4v",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a.mp4",
        "a.mp4",
        1,
        HASH,
        "application/octet-stream",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "video/a.mp4",
        "a.mp4",
        1,
        HASH,
        "video/mp4",
        MediaType.VIDEO,
        ContentDisposition.ATTACHMENT);
    assertInvalid(
        "media-1",
        "music/a.MP3",
        "a.MP3",
        1,
        HASH,
        "audio/mpeg",
        MediaType.MUSIC,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "music/a",
        "a",
        1,
        HASH,
        "audio/mpeg",
        MediaType.MUSIC,
        ContentDisposition.INLINE);
    assertInvalid(
        "media-1",
        "music/a.mp3",
        "a.mp3",
        1,
        HASH,
        "audio/ogg",
        MediaType.MUSIC,
        ContentDisposition.INLINE);
  }

  @Test
  void constructorRejectsNullComponents() {
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                null,
                "id",
                "video/a.mp4",
                "a.mp4",
                1,
                HASH,
                "video/mp4",
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                null,
                "video/a.mp4",
                "a.mp4",
                1,
                HASH,
                "video/mp4",
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                null,
                "a.mp4",
                1,
                HASH,
                "video/mp4",
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                "video/a.mp4",
                null,
                1,
                HASH,
                "video/mp4",
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                "video/a.mp4",
                "a.mp4",
                1,
                null,
                "video/mp4",
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                "video/a.mp4",
                "a.mp4",
                1,
                HASH,
                null,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO, "id", "video/a.mp4", "a.mp4", 1, HASH, "video/mp4", null));
  }

  private static MediaDescriptor media(
      MediaType type, String path, String fileName, String mime, ContentDisposition disposition) {
    return new MediaDescriptor(type, "media-1", path, fileName, 1, HASH, mime, disposition);
  }

  private static void assertInvalid(
      String logicalId,
      String path,
      String fileName,
      long size,
      String hash,
      String mime,
      MediaType type,
      ContentDisposition disposition) {
    assertThrows(
        IllegalArgumentException.class,
        () -> new MediaDescriptor(type, logicalId, path, fileName, size, hash, mime, disposition));
  }
}
