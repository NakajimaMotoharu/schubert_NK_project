package dev.codex.schubert.nk.protocol.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.Test;

class MediaDescriptorValidatorTest {
  private static final String AUDIO_OGG_MIME = "audio/ogg";
  private static final String VIDEO_MP4_MIME = "video/mp4";
  private static final String AUDIO_MPEG_MIME = "audio/mpeg";
  private static final String MEDIA_ID_TEXT = "media-1";
  private static final String MUSIC_KIND_TEXT = "MUSIC";
  private static final String OGG_EXTENSION = ".ogg";
  private static final String MP4_EXTENSION = ".mp4";
  private static final String MUSIC_DIRECTORY_PREFIX = "music/";
  private static final String STORED_LABEL = "stored";
  private static final String VIDEO_RELATIVE_PATH = "video/a.mp4";
  private static final String VIDEO_FILE_NAME = "a.mp4";
  private static final String HASH = "0".repeat(64);

  @Test
  void acceptsExactlySevenSsc004ExtensionMimePairs() {
    List<MediaDescriptor> descriptors =
        List.of(
            media(
                MediaType.AUDIO,
                "scenario/game/audio/sample.ogg",
                "sample.ogg",
                AUDIO_OGG_MIME,
                ContentDisposition.INLINE),
            media(
                MediaType.VIDEO,
                "video/main/sample.mp4",
                "sample.mp4",
                VIDEO_MP4_MIME,
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
                AUDIO_MPEG_MIME,
                ContentDisposition.ATTACHMENT),
            media(
                MediaType.MUSIC,
                "music/sample.ogg",
                "sample.ogg",
                AUDIO_OGG_MIME,
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
    assertEquals(MEDIA_ID_TEXT, descriptor.logicalId());
    assertEquals("scenario/game/audio/sample.ogg", descriptor.storageRelativePath());
    assertEquals("sample.ogg", descriptor.fileName());
    assertEquals(1, descriptor.byteLength());
    assertEquals(HASH, descriptor.sha256());
    assertEquals(AUDIO_OGG_MIME, descriptor.mimeType());
    assertEquals(ContentDisposition.INLINE, descriptor.disposition());
    assertTrue(descriptor.toString().contains("storageRelativePath=REDACTED"));
    assertFalse(descriptor.toString().contains(descriptor.storageRelativePath()));
    MediaDescriptorValidator.validate(descriptor);
    assertThrows(NullPointerException.class, () -> MediaDescriptorValidator.validate(null));
    assertEquals(3, MediaType.values().length);
    assertEquals(MediaType.MUSIC, MediaType.valueOf(MUSIC_KIND_TEXT));
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

  /** PT-PRO-003-M04: SS333/UI235 literal byte bounds, not Production limit constants. */
  @Test
  void utf8MaximumFieldsAndN12UseIndependentCanonicalBoundaries() {
    String[][] pairs = {
      {"AUDIO", "scenario/", OGG_EXTENSION, AUDIO_OGG_MIME},
      {"VIDEO", "video/", MP4_EXTENSION, VIDEO_MP4_MIME},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".m4a", "audio/mp4"},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".mp3", AUDIO_MPEG_MIME},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, OGG_EXTENSION, AUDIO_OGG_MIME},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".wav", "audio/wav"},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".flac", "audio/flac"}
    };
    for (String[] pair : pairs) {
      var type = MediaType.valueOf(pair[0]);
      String logicalId = "あ".repeat(21) + "a";
      String child = "あ".repeat(83) + "a"; // 250 UTF-8 bytes, below the OS segment limit.
      String path =
          pair[1] + child + "/" + utf8TextAtByteLimit(512 - pair[1].length() - 251, pair[2]);
      String name = utf8TextAtByteLimit(256, pair[2]); // Display metadata, not the storage name.
      assertEquals(64, logicalId.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(512, path.getBytes(StandardCharsets.UTF_8).length);
      assertEquals(256, name.getBytes(StandardCharsets.UTF_8).length);
      var descriptor =
          new MediaDescriptor(
              type,
              logicalId,
              path,
              name,
              999_999_999_999L,
              HASH,
              pair[3],
              ContentDisposition.INLINE);
      assertEquals(type, descriptor.mediaType());
      assertEquals(logicalId, descriptor.logicalId());
      assertEquals(path, descriptor.storageRelativePath());
      assertEquals(name, descriptor.fileName());
      assertEquals(999_999_999_999L, descriptor.byteLength());
      assertEquals(HASH, descriptor.sha256());
      assertEquals(pair[3], descriptor.mimeType());
      assertEquals(ContentDisposition.INLINE, descriptor.disposition());
      assertInvalid(logicalId + "a", path, name, 1, HASH, pair[3], type, ContentDisposition.INLINE);
      assertInvalid(
          logicalId,
          pair[1] + "a" + path.substring(pair[1].length()),
          name,
          1,
          HASH,
          pair[3],
          type,
          ContentDisposition.INLINE);
      assertInvalid(logicalId, path, "a" + name, 1, HASH, pair[3], type, ContentDisposition.INLINE);
      assertInvalid(
          logicalId,
          path,
          name,
          1_000_000_000_000L,
          HASH,
          pair[3],
          type,
          ContentDisposition.INLINE);
    }
  }

  private static String utf8TextAtByteLimit(int bytes, String asciiSuffix) {
    int contentBytes = bytes - asciiSuffix.length();
    return "あ".repeat(contentBytes / 3) + "a".repeat(contentBytes % 3) + asciiSuffix;
  }

  /** PT-PRO-003-M03; independent SS333 §8 allowlist; BUG-040/YKT-036. */
  @Test
  void bug040StorageExtensionCannotBeHiddenByDisplayMetadata() {
    String[][] pairs = {
      {"AUDIO", "scenario/", OGG_EXTENSION, AUDIO_OGG_MIME},
      {"VIDEO", "video/", MP4_EXTENSION, VIDEO_MP4_MIME},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".m4a", "audio/mp4"},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".mp3", AUDIO_MPEG_MIME},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, OGG_EXTENSION, AUDIO_OGG_MIME},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".wav", "audio/wav"},
      {MUSIC_KIND_TEXT, MUSIC_DIRECTORY_PREFIX, ".flac", "audio/flac"}
    };
    for (String[] pair : pairs) {
      var type = MediaType.valueOf(pair[0]);
      String prefix = pair[1];
      String extension = pair[2];
      String mime = pair[3];
      var valid =
          media(
              type,
              prefix + STORED_LABEL + extension,
              "表示名" + extension,
              mime,
              ContentDisposition.INLINE);
      assertEquals(prefix + STORED_LABEL + extension, valid.storageRelativePath());
      assertEquals("表示名" + extension, valid.fileName());
      for (String badExtension :
          List.of(
              "",
              ".bin",
              extension.toUpperCase(java.util.Locale.ROOT),
              extension.equals(MP4_EXTENSION) ? OGG_EXTENSION : MP4_EXTENSION,
              extension + ".bin")) {
        var failure =
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    media(
                        type,
                        prefix + STORED_LABEL + badExtension,
                        "表示名" + extension,
                        mime,
                        ContentDisposition.INLINE));
        assertFalse(failure.getMessage().contains(STORED_LABEL));
        assertEquals(null, failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
      }
    }
  }

  @Test
  void rejectsNonCanonicalTextPathsNamesSizesAndHashes() {
    assertInvalid(
        "",
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "e\u0301",
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "あ".repeat(22),
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        "id ",
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    for (String logicalId : new String[] {"id\r", "id\n", "id\t", "id\0"}) {
      assertInvalid(
          logicalId,
          VIDEO_RELATIVE_PATH,
          VIDEO_FILE_NAME,
          1,
          HASH,
          VIDEO_MP4_MIME,
          MediaType.VIDEO,
          ContentDisposition.INLINE);
    }

    for (String path :
        new String[] {
          "/video/a.mp4", "video/a.mp4/", "video\\a.mp4", "video//a.mp4",
          "video/./a.mp4", "video/../a.mp4", "music/a.mp4", "video/a.mp4 "
        }) {
      assertInvalid(
          MEDIA_ID_TEXT,
          path,
          VIDEO_FILE_NAME,
          1,
          HASH,
          VIDEO_MP4_MIME,
          MediaType.VIDEO,
          ContentDisposition.INLINE);
    }
    assertInvalid(
        MEDIA_ID_TEXT,
        "video/" + "あ".repeat(170) + MP4_EXTENSION,
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        "video/a\u0001.mp4",
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);

    for (String name :
        new String[] {"a/b.mp4", "a\\b.mp4", "a\"b.mp4", "a'b.mp4", "a\u0001.mp4", "a.mp4 "}) {
      assertInvalid(
          MEDIA_ID_TEXT,
          VIDEO_RELATIVE_PATH,
          name,
          1,
          HASH,
          VIDEO_MP4_MIME,
          MediaType.VIDEO,
          ContentDisposition.INLINE);
    }
    assertInvalid(
        MEDIA_ID_TEXT,
        VIDEO_RELATIVE_PATH,
        "あ".repeat(86),
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        0,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1_000_000_000_000L,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        "A".repeat(64),
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
  }

  @Test
  void rejectsEveryMimeCrossProductAndVideoAttachment() {
    assertInvalid(
        MEDIA_ID_TEXT,
        "scenario/game/audio/a.mp3",
        "a.mp3",
        1,
        HASH,
        AUDIO_MPEG_MIME,
        MediaType.AUDIO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        "scenario/game/audio/a.ogg",
        "a.ogg",
        1,
        HASH,
        AUDIO_MPEG_MIME,
        MediaType.AUDIO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        "video/a.m4v",
        "a.m4v",
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        HASH,
        "application/octet-stream",
        MediaType.VIDEO,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        VIDEO_RELATIVE_PATH,
        VIDEO_FILE_NAME,
        1,
        HASH,
        VIDEO_MP4_MIME,
        MediaType.VIDEO,
        ContentDisposition.ATTACHMENT);
    assertInvalid(
        MEDIA_ID_TEXT,
        "music/a.MP3",
        "a.MP3",
        1,
        HASH,
        AUDIO_MPEG_MIME,
        MediaType.MUSIC,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        "music/a",
        "a",
        1,
        HASH,
        AUDIO_MPEG_MIME,
        MediaType.MUSIC,
        ContentDisposition.INLINE);
    assertInvalid(
        MEDIA_ID_TEXT,
        "music/a.mp3",
        "a.mp3",
        1,
        HASH,
        AUDIO_OGG_MIME,
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
                VIDEO_RELATIVE_PATH,
                VIDEO_FILE_NAME,
                1,
                HASH,
                VIDEO_MP4_MIME,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                null,
                VIDEO_RELATIVE_PATH,
                VIDEO_FILE_NAME,
                1,
                HASH,
                VIDEO_MP4_MIME,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                null,
                VIDEO_FILE_NAME,
                1,
                HASH,
                VIDEO_MP4_MIME,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                VIDEO_RELATIVE_PATH,
                null,
                1,
                HASH,
                VIDEO_MP4_MIME,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                VIDEO_RELATIVE_PATH,
                VIDEO_FILE_NAME,
                1,
                null,
                VIDEO_MP4_MIME,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                VIDEO_RELATIVE_PATH,
                VIDEO_FILE_NAME,
                1,
                HASH,
                null,
                ContentDisposition.INLINE));
    assertThrows(
        NullPointerException.class,
        () ->
            new MediaDescriptor(
                MediaType.VIDEO,
                "id",
                VIDEO_RELATIVE_PATH,
                VIDEO_FILE_NAME,
                1,
                HASH,
                VIDEO_MP4_MIME,
                null));
  }

  private static MediaDescriptor media(
      MediaType type, String path, String fileName, String mime, ContentDisposition disposition) {
    return new MediaDescriptor(type, MEDIA_ID_TEXT, path, fileName, 1, HASH, mime, disposition);
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
