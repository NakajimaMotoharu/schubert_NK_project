package dev.codex.schubert.nk.web.media;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Objects;

/** Safe header only. NK-MED-001; FUN-005/007; UI235/237; SS333 §9; PT-MED-005. */
public final class ContentDispositionFactory {
  private ContentDispositionFactory() {
    throw new AssertionError("static namespace");
  }

  public static String create(MediaDescriptor descriptor) {
    Objects.requireNonNull(descriptor, "descriptor");
    String mode = descriptor.disposition() == ContentDisposition.INLINE ? "inline" : "attachment";
    String encoded =
        URLEncoder.encode(descriptor.fileName(), StandardCharsets.UTF_8)
            .replace("+", "%20")
            .replace("*", "%2A");
    return mode + "; filename=\"download.bin\"; filename*=UTF-8''" + encoded;
  }
}
