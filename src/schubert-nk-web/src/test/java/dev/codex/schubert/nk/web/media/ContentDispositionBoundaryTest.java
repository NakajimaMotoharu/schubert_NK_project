package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import org.junit.jupiter.api.Test;

/**
 * Independent percent-byte literals and supplementary byte boundary; SS333/323,
 * HEADERBOUND001..003.
 */
class ContentDispositionBoundaryTest {
  private static final String INLINE = "inline; filename=\"download.bin\"; filename*=UTF-8''";
  private static final String ATTACHMENT =
      "attachment; filename=\"download.bin\"; filename*=UTF-8''";
  private static final String EXTENSION = ".ogg";
  private static final String SUPPLEMENTARY = "𝄞";

  @Test
  void asciiAndReservedCharactersHaveLiteralEscapes() {
    assertEquals(
        INLINE + "AZaz09-_.ogg",
        ContentDispositionFactory.create(descriptor("AZaz09-_.ogg", ContentDisposition.INLINE)));
    assertEquals(
        INLINE + "%7E%21%23%24%26%2B%5E%60%7C%2A%25.ogg",
        ContentDispositionFactory.create(descriptor("~!#$&+^`|*%.ogg", ContentDisposition.INLINE)));
  }

  @Test
  void supplementaryUtf8AndLiteralPercentAreNotDecoded() {
    assertEquals(
        ATTACHMENT + "%E4%BA%8C%F0%9D%84%9E.ogg",
        ContentDispositionFactory.create(descriptor("二𝄞.ogg", ContentDisposition.ATTACHMENT)));
    assertEquals(
        ATTACHMENT + "%252F.ogg",
        ContentDispositionFactory.create(descriptor("%2F.ogg", ContentDisposition.ATTACHMENT)));
  }

  @Test
  void supplementaryNameLimitIsByteBasedForBothModes() {
    for (var disposition : ContentDisposition.values()) {
      String prefix = disposition == ContentDisposition.INLINE ? INLINE : ATTACHMENT;
      assertEquals(
          prefix + "%F0%9D%84%9E".repeat(63) + EXTENSION,
          ContentDispositionFactory.create(
              descriptor(SUPPLEMENTARY.repeat(63) + EXTENSION, disposition)));
      assertThrows(
          IllegalArgumentException.class,
          () -> descriptor(SUPPLEMENTARY.repeat(64) + EXTENSION, disposition));
    }
  }

  private static MediaDescriptor descriptor(String name, ContentDisposition disposition) {
    return new MediaDescriptor(
        MediaType.AUDIO,
        "synthetic-header",
        "scenario/test/audio.ogg",
        name,
        1,
        "0".repeat(64),
        "audio/ogg",
        disposition);
  }
}
