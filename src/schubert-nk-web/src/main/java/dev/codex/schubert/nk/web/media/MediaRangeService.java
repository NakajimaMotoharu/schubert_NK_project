package dev.codex.schubert.nk.web.media;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.channels.SeekableByteChannel;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.Semaphore;

/**
 * Internal delivery after per-GET API authentication and MQ response verification. One instance per
 * Web process is mandatory at startup. NK-MED-001; FUN-005..007/PER-004..006; UI223/235/237;
 * SS311/333; PG-D-075; PT-MED-027..032. This is not a registered HTTP endpoint or an auth cache.
 */
public final class MediaRangeService {
  @FunctionalInterface
  public interface ReadOperation {
    void execute(SeekableByteChannel channel) throws IOException;
  }

  /** Own and validate the file; invoke the callback in its lexical scope, then close it. */
  @FunctionalInterface
  public interface FileSource {
    void read(MediaDescriptor descriptor, ReadOperation operation) throws IOException;
  }

  /** HTTP adapter owns the output. Track commit/client abort there; never expose a storage path. */
  public interface Response {
    void begin(int status, Map<String, String> headers) throws IOException;

    OutputStream body() throws IOException;
  }

  private final FileSource source;
  private final Semaphore permits;

  public MediaRangeService(FileSource source) {
    this(source, 20);
  }

  /** Validated native configuration may reduce the stream count, never exceed the fixed20 cap. */
  public MediaRangeService(FileSource source, int maximumStreams) {
    this.source = Objects.requireNonNull(source, "source");
    if (maximumStreams < 1 || maximumStreams > 20)
      throw new IllegalArgumentException("media stream count is outside 1..20");
    permits = new Semaphore(maximumStreams);
  }

  /** Bind the verified descriptor to this request before admission, then stream without DB I/O. */
  public void deliver(
      MediaType type,
      String logicalId,
      ContentDisposition disposition,
      Optional<String> range,
      boolean head,
      MediaDescriptor descriptor,
      Response response)
      throws MediaDeliveryException {
    Objects.requireNonNull(type, "type");
    Objects.requireNonNull(logicalId, "logicalId");
    Objects.requireNonNull(disposition, "disposition");
    Objects.requireNonNull(range, "range");
    Objects.requireNonNull(descriptor, "descriptor");
    Objects.requireNonNull(response, "response");
    if (type != descriptor.mediaType()
        || !logicalId.equals(descriptor.logicalId())
        || disposition != descriptor.disposition()) {
      throw new MediaDeliveryException(MediaDeliveryException.Reason.INVALID_DESCRIPTOR);
    }
    if (!permits.tryAcquire()) throw new MediaDeliveryException(MediaDeliveryException.Reason.BUSY);
    try {
      source.read(descriptor, channel -> respond(channel, range, head, descriptor, response));
    } catch (IOException failure) {
      throw new MediaDeliveryException(MediaDeliveryException.Reason.UNAVAILABLE);
    } finally {
      permits.release();
    }
  }

  private static void respond(
      SeekableByteChannel channel,
      Optional<String> range,
      boolean head,
      MediaDescriptor descriptor,
      Response response)
      throws IOException {
    boolean attachment = descriptor.disposition() == ContentDisposition.ATTACHMENT;
    var selection =
        HttpByteRangeParser.parseFirst(
            attachment ? Optional.empty() : range, descriptor.byteLength());
    Map<String, String> headers = new HashMap<>();
    headers.put("Accept-Ranges", "bytes");
    headers.put("Content-Type", attachment ? "application/octet-stream" : descriptor.mimeType());
    headers.put("Content-Disposition", ContentDispositionFactory.create(descriptor));
    headers.put("X-Content-Type-Options", "nosniff");
    headers.put("Cache-Control", "private, no-store");
    int status;
    long start = 0;
    long length;
    if (selection instanceof HttpByteRangeParser.Full full) {
      status = 200;
      length = full.length();
    } else if (selection instanceof HttpByteRangeParser.Partial partial) {
      status = 206;
      start = partial.start();
      length = partial.length();
      headers.put(
          "Content-Range", "bytes " + start + "-" + partial.end() + "/" + descriptor.byteLength());
    } else {
      // SS333 / PG-D-1190: the remaining parser result is the bodyless Unsatisfiable.
      status = 416;
      length = 0;
      headers.put("Content-Range", "bytes */" + descriptor.byteLength());
    }
    headers.put("Content-Length", Long.toString(length));
    response.begin(status, Map.copyOf(headers));
    if (!head && length > 0) MediaBodyStreamer.copy(channel, response.body(), start, length);
  }
}
