package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalInt;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.opentest4j.AssertionFailedError;

/** PT-MED-PORT001..011. Memory-only response/byte-channel ports; no path, native or HTTP client. */
final class MediaRangePortTest {
  private static final int SIZE = 2_097_155;
  private static final String LOGICAL_ID = "7";
  private static final String MIME = "audio/ogg";
  private static final String RANGE = "bytes=2-4";
  private static final String THREE_BYTE_RANGE = "bytes 2-4/2097155";
  private static final String CONTENT_RANGE = "Content-Range";
  private static final String SYNTHETIC_FAILURE = "own synthetic port failure";

  @Test
  void literalStatusHeadersAndByteIntervals() throws MediaDeliveryException {
    for (Vector vector :
        List.of(
            new Vector(Optional.empty(), 200, 0, SIZE, null),
            new Vector(Optional.of(RANGE), 206, 2, 3, THREE_BYTE_RANGE),
            new Vector(Optional.of("bytes=-3"), 206, SIZE - 3, 3, "bytes 2097152-2097154/2097155"),
            new Vector(Optional.of("bytes=0-"), 206, 0, 1_048_576, "bytes 0-1048575/2097155"),
            new Vector(Optional.of("BYTES= 2-4 ,invalid"), 206, 2, 3, THREE_BYTE_RANGE),
            new Vector(Optional.of("bytes=2097155-"), 416, 0, 0, "bytes */2097155"))) {
      Probe source = new Probe();
      Reply reply = new Reply();
      call(
          new MediaRangeService(source),
          descriptor(ContentDisposition.INLINE),
          vector.range(),
          false,
          reply);
      verify(
          reply,
          vector.status(),
          vector.start(),
          vector.length(),
          vector.contentRange(),
          false,
          false);
      assertEquals(1, source.opens);
      assertEquals(1, source.closes);
      assertTrue(source.largestRead <= 65_536);
      assertEquals(vector.length(), source.bytesRead);
    }
  }

  @Test
  void invalidUnitAndOverLimitEndDoNotRequestOrReadABody() throws MediaDeliveryException {
    // PT-MED-PORT011 / SS333 §10.1 / SSC-476. The admitted channel supplies only the length.
    var source = new Probe();
    var service = new MediaRangeService(source, 1);
    var media = descriptor(ContentDisposition.INLINE);
    for (String header : List.of("byte\u017F=0-0", "bytes=0-9223372036854775808")) {
      var reply = new Reply();
      call(service, media, Optional.of(header), false, reply);
      verify(reply, 416, 0, 0, "bytes */" + SIZE, false, false);
      assertEquals(0, reply.bodyCalls);
      assertEquals(0, source.bytesRead);
      assertEquals(source.opens, source.closes);
    }
    assertEquals(2, source.opens);
    assertEquals(2, source.closes);
  }

  @Test
  void headNeverRequestsBodyAndAttachmentIgnoresRange() throws MediaDeliveryException {
    Probe source = new Probe();
    MediaRangeService service = new MediaRangeService(source);
    for (Optional<String> range :
        List.of(Optional.<String>empty(), Optional.of(RANGE), Optional.of("invalid"))) {
      Reply head = new Reply();
      call(service, descriptor(ContentDisposition.INLINE), range, true, head);
      assertEquals(0, head.bodyCalls);
      assertEquals(0, head.bytes.size());
      if (range.isEmpty()) verify(head, 200, 0, SIZE, null, false, true);
      else if (range.get().equals(RANGE)) verify(head, 206, 2, 3, THREE_BYTE_RANGE, false, true);
      else verify(head, 416, 0, 0, "bytes */2097155", false, true);
      for (boolean onlyHead : new boolean[] {false, true}) {
        Reply download = new Reply();
        call(service, descriptor(ContentDisposition.ATTACHMENT), range, onlyHead, download);
        verify(download, 200, 0, SIZE, null, true, onlyHead);
      }
    }
    assertEquals(source.opens, source.closes);
  }

  @Test
  void descriptorBindingRejectsEachMismatchBeforeSourceAdmission() throws MediaDeliveryException {
    Probe source = new Probe();
    MediaRangeService service = new MediaRangeService(source, 1);
    MediaDescriptor descriptor = descriptor(ContentDisposition.INLINE);
    for (Object[] values :
        List.of(
            new Object[] {MediaType.VIDEO, LOGICAL_ID, ContentDisposition.INLINE},
            new Object[] {MediaType.MUSIC, "8", ContentDisposition.INLINE},
            new Object[] {MediaType.MUSIC, LOGICAL_ID, ContentDisposition.ATTACHMENT})) {
      Reply response = new Reply();
      safeFailure(
          MediaDeliveryException.Reason.INVALID_DESCRIPTOR,
          () ->
              service.deliver(
                  (MediaType) values[0],
                  (String) values[1],
                  (ContentDisposition) values[2],
                  Optional.empty(),
                  true,
                  descriptor,
                  response));
      assertEquals(0, response.begins);
    }
    assertEquals(0, source.opens);
    call(service, descriptor, Optional.empty(), true, new Reply());
    assertEquals(1, source.opens);
  }

  @Test
  void configuredBoundariesAndDefaultTwentyRejectTwentyFirstAndRecover()
      throws MediaDeliveryException {
    for (int invalid : new int[] {Integer.MIN_VALUE, 0, 21, Integer.MAX_VALUE}) {
      assertThrows(
          IllegalArgumentException.class, () -> new MediaRangeService(new Probe(), invalid));
    }
    for (int maximum : new int[] {1, 20}) {
      AtomicReference<MediaRangeService> service = new AtomicReference<>();
      AtomicInteger depth = new AtomicInteger();
      AtomicInteger seen = new AtomicInteger();
      MediaDescriptor descriptor = descriptor(ContentDisposition.INLINE);
      service.set(
          maximum == 20
              ? new MediaRangeService(
                  (value, operation) ->
                      nested(service.get(), value, operation, maximum, depth, seen))
              : new MediaRangeService(
                  (value, operation) ->
                      nested(service.get(), value, operation, maximum, depth, seen),
                  maximum));
      call(service.get(), descriptor, Optional.empty(), true, new Reply());
      assertEquals(maximum, seen.get());
      assertEquals(0, depth.get());
      call(service.get(), descriptor, Optional.empty(), true, new Reply());
      assertEquals(maximum * 2, seen.get());
    }
    assertNotNull(new MediaRangeService(new Probe(), 20));
  }

  @Test
  void eachCheckedFailureIsRedactedAndReleasesSinglePermit() throws MediaDeliveryException {
    for (String fault : List.of("source", "begin", "body", "write", "read")) {
      Probe source = new Probe();
      source.fault = fault;
      MediaRangeService service = new MediaRangeService(source, 1);
      Reply reply = new Reply();
      reply.fault = fault;
      safeFailure(
          MediaDeliveryException.Reason.UNAVAILABLE,
          () ->
              call(
                  service,
                  descriptor(ContentDisposition.INLINE),
                  Optional.of(RANGE),
                  false,
                  reply));
      source.fault = "none";
      Reply recovered = new Reply();
      call(service, descriptor(ContentDisposition.INLINE), Optional.of(RANGE), false, recovered);
      verify(recovered, 206, 2, 3, THREE_BYTE_RANGE, false, false);
      assertEquals(2, source.opens);
      assertEquals(2, source.closes);
    }
  }

  @Test
  void runtimeFailureEscapesUnchangedAndStillReleasesPermit() throws MediaDeliveryException {
    Probe source = new Probe();
    IllegalStateException original = new IllegalStateException(SYNTHETIC_FAILURE);
    AtomicInteger attempts = new AtomicInteger();
    MediaRangeService service =
        new MediaRangeService(
            (descriptor, operation) -> {
              if (attempts.getAndIncrement() == 0) throw original;
              source.read(descriptor, operation);
            },
            1);
    assertSame(
        original,
        assertThrows(
            IllegalStateException.class,
            () ->
                call(
                    service,
                    descriptor(ContentDisposition.INLINE),
                    Optional.empty(),
                    true,
                    new Reply())));
    call(service, descriptor(ContentDisposition.INLINE), Optional.empty(), true, new Reply());
    assertEquals(2, attempts.get());
    assertEquals(1, source.closes);
  }

  @Test
  void directErrorBeforeResponseEscapesUnchangedAndReleasesThePermit()
      throws MediaDeliveryException {
    var fatal = new AssertionError("synthetic fatal port failure");
    var source = new Probe();
    var attempts = new AtomicInteger();
    var service =
        new MediaRangeService(
            (descriptor, operation) -> {
              if (attempts.getAndIncrement() == 0) throw fatal;
              source.read(descriptor, operation);
            },
            1);
    var descriptor = descriptor(ContentDisposition.INLINE);
    var failed = new Reply();

    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> call(service, descriptor, Optional.of(RANGE), false, failed)));
    assertEquals(0, failed.begins);
    assertEquals(0, source.opens);
    assertEquals(0, source.closes);

    var recovered = new Reply();
    call(service, descriptor, Optional.of(RANGE), false, recovered);
    verify(recovered, 206, 2, 3, THREE_BYTE_RANGE, false, false);
    assertEquals(2, attempts.get());
    assertEquals(1, source.opens);
    assertEquals(1, source.closes);
  }

  @Test
  void writeErrorAfterBeginClosesSourceWithoutRetryingAndReleasesThePermit()
      throws MediaDeliveryException {
    var fatal = new AssertionError("synthetic fatal write failure");
    var source = new Probe();
    var service = new MediaRangeService(source, 1);
    var descriptor = descriptor(ContentDisposition.INLINE);
    var failed = new Reply();
    var writes = new AtomicInteger();
    var bodyCalls = new AtomicInteger();
    var outputCloses = new AtomicInteger();
    var response =
        new MediaRangeService.Response() {
          @Override
          public void begin(int status, Map<String, String> headers) throws IOException {
            failed.begin(status, headers);
          }

          @Override
          public OutputStream body() {
            bodyCalls.incrementAndGet();
            return new ByteArrayOutputStream() {
              @Override
              public synchronized void write(byte[] value, int offset, int length) {
                writes.incrementAndGet();
                throw fatal;
              }

              @Override
              public void close() {
                outputCloses.incrementAndGet();
              }
            };
          }
        };

    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                service.deliver(
                    MediaType.MUSIC,
                    LOGICAL_ID,
                    ContentDisposition.INLINE,
                    Optional.of(RANGE),
                    false,
                    descriptor,
                    response)));
    assertEquals(1, failed.begins);
    assertEquals(206, failed.status);
    assertEquals(THREE_BYTE_RANGE, failed.headers.get(CONTENT_RANGE));
    assertEquals(1, bodyCalls.get());
    assertEquals(1, writes.get());
    assertEquals(0, outputCloses.get());
    assertEquals(1, source.opens);
    assertEquals(1, source.closes);

    var recovered = new Reply();
    call(service, descriptor, Optional.of(RANGE), false, recovered);
    verify(recovered, 206, 2, 3, THREE_BYTE_RANGE, false, false);
    assertEquals(2, source.opens);
    assertEquals(2, source.closes);
  }

  @Test
  void nullContractGuardsRejectBeforeAnyPortAndDoNotConsumePermit() throws MediaDeliveryException {
    Probe source = new Probe();
    assertThrows(NullPointerException.class, () -> new MediaRangeService(null));
    MediaRangeService service = new MediaRangeService(source, 1);
    MediaDescriptor descriptor = descriptor(ContentDisposition.INLINE);
    for (int missing = 0; missing < 6; missing++) {
      int index = missing;
      Reply reply = new Reply();
      assertThrows(
          NullPointerException.class,
          () ->
              service.deliver(
                  index == 0 ? null : MediaType.MUSIC,
                  index == 1 ? null : LOGICAL_ID,
                  index == 2 ? null : ContentDisposition.INLINE,
                  index == 3 ? null : Optional.empty(),
                  true,
                  index == 4 ? null : descriptor,
                  index == 5 ? null : reply));
      assertEquals(0, reply.begins);
    }
    assertEquals(0, source.opens);
    call(service, descriptor, Optional.empty(), true, new Reply());
    assertEquals(1, source.opens);
  }

  @Test
  void twoConcurrentRequestsObserveOnePermitWithoutSharingResponseState()
      throws MediaDeliveryException, InterruptedException, ExecutionException, TimeoutException {
    Probe source = new Probe();
    CountDownLatch entered = new CountDownLatch(1);
    CountDownLatch release = new CountDownLatch(1);
    MediaRangeService service =
        new MediaRangeService(
            (descriptor, operation) -> {
              entered.countDown();
              try {
                if (!release.await(5, TimeUnit.SECONDS))
                  throw new IOException("own latch timed out");
              } catch (InterruptedException interrupted) {
                Thread.currentThread().interrupt();
                throw new IOException("own latch interrupted");
              }
              source.read(descriptor, operation);
            },
            1);
    var workers = Executors.newFixedThreadPool(2);
    try {
      Reply first = new Reply();
      var pending =
          workers.submit(
              () -> {
                call(
                    service,
                    descriptor(ContentDisposition.INLINE),
                    Optional.of(RANGE),
                    false,
                    first);
                return first;
              });
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        Reply second = new Reply();
        var rejected =
            workers.submit(
                () ->
                    safeFailure(
                        MediaDeliveryException.Reason.BUSY,
                        () ->
                            call(
                                service,
                                descriptor(ContentDisposition.INLINE),
                                Optional.empty(),
                                true,
                                second)));
        assertNotNull(rejected.get(5, TimeUnit.SECONDS));
        assertEquals(0, second.begins);
      } finally {
        release.countDown();
      }
      assertSame(first, pending.get(5, TimeUnit.SECONDS));
      verify(first, 206, 2, 3, THREE_BYTE_RANGE, false, false);
      call(service, descriptor(ContentDisposition.INLINE), Optional.empty(), true, new Reply());
      assertEquals(2, source.opens);
      assertEquals(2, source.closes);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS), "media range executor terminated");
    }
  }

  private static void nested(
      MediaRangeService service,
      MediaDescriptor value,
      MediaRangeService.ReadOperation operation,
      int maximum,
      AtomicInteger depth,
      AtomicInteger seen)
      throws IOException {
    int current = depth.incrementAndGet();
    seen.incrementAndGet();
    try {
      if (current < maximum) call(service, value, Optional.empty(), true, new Reply());
      else {
        safeFailure(
            MediaDeliveryException.Reason.BUSY,
            () -> call(service, value, Optional.empty(), true, new Reply()));
        safeFailure(
            MediaDeliveryException.Reason.INVALID_DESCRIPTOR,
            () ->
                service.deliver(
                    MediaType.VIDEO,
                    LOGICAL_ID,
                    ContentDisposition.INLINE,
                    Optional.empty(),
                    true,
                    value,
                    new Reply()));
      }
      operation.execute(new MemoryChannel());
    } finally {
      depth.decrementAndGet();
    }
  }

  private static MediaDeliveryException safeFailure(
      MediaDeliveryException.Reason expected, org.junit.jupiter.api.function.Executable action) {
    MediaDeliveryException failure = assertThrows(MediaDeliveryException.class, action);
    assertEquals(expected, failure.reason());
    assertEquals(503, failure.httpStatus());
    assertEquals(
        expected == MediaDeliveryException.Reason.BUSY ? OptionalInt.of(1) : OptionalInt.empty(),
        failure.retryAfterSeconds());
    assertEquals("media delivery failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    return failure;
  }

  private static MediaDescriptor descriptor(ContentDisposition disposition) {
    return new MediaDescriptor(
        MediaType.MUSIC,
        LOGICAL_ID,
        "music/a.ogg",
        "音源.ogg",
        SIZE,
        "a".repeat(64),
        MIME,
        disposition);
  }

  private static void call(
      MediaRangeService service,
      MediaDescriptor descriptor,
      Optional<String> range,
      boolean head,
      Reply response)
      throws MediaDeliveryException {
    service.deliver(
        descriptor.mediaType(),
        descriptor.logicalId(),
        descriptor.disposition(),
        range,
        head,
        descriptor,
        response);
  }

  private static void verify(
      Reply reply,
      int status,
      int start,
      int length,
      String contentRange,
      boolean attachment,
      boolean head) {
    Map<String, String> headers =
        new java.util.HashMap<>(
            Map.of(
                "Accept-Ranges",
                "bytes",
                "Content-Type",
                attachment ? "application/octet-stream" : MIME,
                "Content-Disposition",
                (attachment ? "attachment" : "inline")
                    + "; filename=\"download.bin\"; filename*=UTF-8''%E9%9F%B3%E6%BA%90.ogg",
                "X-Content-Type-Options",
                "nosniff",
                "Cache-Control",
                "private, no-store",
                "Content-Length",
                Integer.toString(length)));
    if (contentRange != null) headers.put(CONTENT_RANGE, contentRange);
    assertEquals(status, reply.status);
    assertEquals(headers, reply.headers);
    byte[] expected = new byte[head ? 0 : length];
    for (int i = 0; i < expected.length; i++) expected[i] = (byte) ((start + i) * 19 + 7);
    assertArrayEquals(expected, reply.bytes.toByteArray());
    assertEquals(head || length == 0 ? 0 : 1, reply.bodyCalls);
    assertEquals(1, reply.begins);
    assertEquals(0, reply.outputCloses);
  }

  private static final class Probe implements MediaRangeService.FileSource {
    String fault = "none";
    int opens;
    int closes;
    int largestRead;
    int bytesRead;

    @Override
    public void read(MediaDescriptor descriptor, MediaRangeService.ReadOperation operation)
        throws IOException {
      opens++;
      try (MemoryChannel channel = new MemoryChannel()) {
        if (fault.equals("source")) throw new IOException(SYNTHETIC_FAILURE);
        channel.failRead = fault.equals("read");
        try {
          operation.execute(channel);
        } finally {
          largestRead = Math.max(largestRead, channel.largestRead);
          bytesRead += channel.bytesRead;
        }
      } finally {
        closes++;
      }
    }
  }

  @Test
  void replyFixtureRejectsMutableHeadersBeforeTakingItsSnapshot() {
    var reply = new Reply();
    var mutable = new java.util.HashMap<String, String>();
    mutable.put("Content-Length", "3");

    assertThrows(AssertionFailedError.class, () -> reply.begin(206, mutable));
    assertEquals(0, reply.status);
    assertTrue(reply.headers.isEmpty());
  }

  private static final class Reply implements MediaRangeService.Response {
    String fault = "none";
    int status;
    int begins;
    int bodyCalls;
    int outputCloses;
    Map<String, String> headers = Map.of();
    ByteArrayOutputStream bytes = new ByteArrayOutputStream();

    @Override
    public void begin(int value, Map<String, String> values) throws IOException {
      begins++;
      if (fault.equals("begin")) throw new IOException(SYNTHETIC_FAILURE);
      assertThrows(UnsupportedOperationException.class, () -> values.put("X", "Y"));
      status = value;
      headers = Map.copyOf(values);
    }

    @Override
    public OutputStream body() throws IOException {
      bodyCalls++;
      if (fault.equals("body")) throw new IOException(SYNTHETIC_FAILURE);
      return new OutputStream() {
        @Override
        public void write(int value) {
          fail("unexpected single-byte write");
        }

        @Override
        public void write(byte[] value, int offset, int length) throws IOException {
          if (fault.equals("write")) throw new IOException(SYNTHETIC_FAILURE);
          assertTrue(length <= 65_536);
          bytes.write(value, offset, length);
        }

        @Override
        public void close() {
          outputCloses++;
        }
      };
    }
  }

  private static final class MemoryChannel implements SeekableByteChannel {
    int offset;
    int largestRead;
    int bytesRead;
    boolean failRead;
    boolean open = true;

    @Override
    public int read(ByteBuffer buffer) throws IOException {
      if (failRead) throw new IOException(SYNTHETIC_FAILURE);
      if (offset >= SIZE) return -1;
      int count = Math.min(buffer.remaining(), SIZE - offset);
      largestRead = Math.max(largestRead, count);
      bytesRead += count;
      for (int i = 0; i < count; i++) {
        buffer.put((byte) (offset * 19 + 7));
        offset++;
      }
      return count;
    }

    @Override
    public long position() {
      return offset;
    }

    @Override
    public SeekableByteChannel position(long value) {
      offset = Math.toIntExact(value);
      return this;
    }

    @Override
    public long size() {
      return SIZE;
    }

    @Override
    public boolean isOpen() {
      return open;
    }

    @Override
    public void close() {
      open = false;
    }

    @Override
    public int write(ByteBuffer ignored) {
      throw new UnsupportedOperationException();
    }

    @Override
    public SeekableByteChannel truncate(long ignored) {
      throw new UnsupportedOperationException();
    }
  }

  private record Vector(
      Optional<String> range, int status, int start, int length, String contentRange) {}
}
