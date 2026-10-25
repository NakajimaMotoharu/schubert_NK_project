package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import java.util.List;
import org.junit.jupiter.api.Test;

class ContentDispositionFactoryTest {
  /** PT-MED-005; literal UTF-8 byte percent strings, never production expected encoding. */
  @Test
  void literalHeadersEncodeUtf8WithoutRawMetadata() {
    assertEquals(
        "inline; filename=\"download.bin\"; filename*=UTF-8''a.ogg",
        ContentDispositionFactory.create(descriptor("a.ogg", ContentDisposition.INLINE)));
    assertEquals(
        "attachment; filename=\"download.bin\"; filename*=UTF-8''%E3%81%82%20%2B%2A%3F.ogg",
        ContentDispositionFactory.create(descriptor("あ +*?.ogg", ContentDisposition.ATTACHMENT)));
    assertEquals(
        "attachment; filename=\"download.bin\"; filename*=UTF-8''"
            + "%E3%81%82".repeat(84)
            + ".ogg",
        ContentDispositionFactory.create(
            descriptor("あ".repeat(84) + ".ogg", ContentDisposition.ATTACHMENT)));
    assertThrows(NullPointerException.class, () -> ContentDispositionFactory.create(null));
    for (String invalid :
        List.of("a\r\n.ogg", "a\".ogg", "a/.ogg", "a\\.ogg", "a\0.ogg", "あ".repeat(85) + ".ogg"))
      assertThrows(
          IllegalArgumentException.class,
          () -> ContentDispositionFactory.create(descriptor(invalid, ContentDisposition.INLINE)));
  }

  private static MediaDescriptor descriptor(String name, ContentDisposition disposition) {
    return new MediaDescriptor(
        MediaType.AUDIO,
        "synthetic",
        "scenario/test/audio.ogg",
        name,
        1,
        "0".repeat(64),
        "audio/ogg",
        disposition);
  }
}
