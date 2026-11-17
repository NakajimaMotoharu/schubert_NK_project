package dev.codex.schubert.nk.web.media;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.util.Objects;

/**
 * Copies only an already authorized interval from a retained verified channel. Caller owns both
 * resources and the stream permit; no open/close/flush or HTTP error response here. NK-MED-001;
 * FUN-005..007/PER-004..006; UI237; SS333 §10/11; PT-MED-006/007.
 */
public final class MediaBodyStreamer {
  private MediaBodyStreamer() {
    throw new AssertionError("static namespace");
  }

  public static void copy(SeekableByteChannel source, OutputStream target, long start, long length)
      throws IOException {
    Objects.requireNonNull(source, "source");
    Objects.requireNonNull(target, "target");
    if (start < 0 || length < 0 || start > Long.MAX_VALUE - length)
      throw new IllegalArgumentException("media interval bounds are invalid");
    try {
      if (start + length > source.size()) throw new IOException("media interval exceeds file");
      source.position(start);
      ByteBuffer buffer = ByteBuffer.allocate(65_536);
      long remaining = length;
      while (remaining > 0) {
        buffer.clear().limit((int) Math.min(buffer.capacity(), remaining));
        int read = source.read(buffer);
        if (read <= 0) throw new IOException("media read made no progress");
        target.write(buffer.array(), 0, read);
        remaining -= read;
      }
    } catch (IOException failure) {
      throw new IOException("media transfer did not complete");
    }
  }
}
