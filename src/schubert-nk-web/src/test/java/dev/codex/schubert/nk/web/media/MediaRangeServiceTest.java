package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Explicit HTTP header/body oracles on actual retained files and fault ports. PT-MED-027..032. */
class MediaRangeServiceTest {
  private static final String FIXTURE_BYTES_2_4_8BC33315 = "bytes=2-4";
  private static final String FIXTURE_AUDIO_OGG_96A5CB00 = "audio/ogg";
  private static final String FIXTURE_MUSIC_D5800D43 = "MUSIC";
  private static final String FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9 = "SYNTHETIC_PRIVATE_PATH";
  @TempDir Path root;
  private StorageIdentity identity;
  private final byte[] content = new byte[2_097_155];
  private final MediaDescriptor inline = descriptor(ContentDisposition.INLINE);
  private final MediaDescriptor attachment = descriptor(ContentDisposition.ATTACHMENT);

  @BeforeEach
  void prepare() throws Exception {
    for (int i = 0; i < content.length; i++) content[i] = (byte) (i * 19 + 7);
    Path music = Files.createDirectory(root.resolve("music"));
    for (Path path : List.of(root, music))
      Files.setPosixFilePermissions(path, PosixFilePermissions.fromString("rwxr-x---"));
    Files.write(music.resolve("a.ogg"), content);
    Files.setPosixFilePermissions(
        music.resolve("a.ogg"), PosixFilePermissions.fromString("rw-r-----"));
    var attrs = Files.readAttributes(root, java.nio.file.attribute.PosixFileAttributes.class);
    identity = new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
  }

  @Test
  void med027GetStatusHeadersAndBytesMatchLiteralIntervals() throws Exception {
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var service = new MediaRangeService(new DescriptorFileResolver(held, identity));
      FakeResponse full = deliver(service, inline, Optional.empty(), false);
      expect(full, 200, 0, 2_097_155, null, false, false);
      for (String[] vector :
          List.of(
              new String[] {FIXTURE_BYTES_2_4_8BC33315, "2", "5"},
              new String[] {"bytes=-3", "2097152", "2097155"},
              new String[] {"bytes=0-", "0", "1048576"},
              new String[] {"BYTES= 2-4 ,bogus", "2", "5"},
              new String[] {"bytes=2097153-9999999", "2097153", "2097155"})) {
        int first = Integer.parseInt(vector[1]);
        int end = Integer.parseInt(vector[2]);
        expect(
            deliver(service, inline, Optional.of(vector[0]), false),
            206,
            first,
            end,
            "bytes " + first + "-" + (end - 1) + "/2097155",
            false,
            false);
      }
      for (String invalid : List.of("", "items=0-1", "bytes=2097155-", "bytes=-0", "bytes=3-2")) {
        expect(
            deliver(service, inline, Optional.of(invalid), false),
            416,
            0,
            0,
            "bytes */2097155",
            false,
            false);
      }
    }
  }

  @Test
  void med028HeadAndDownloadNeverApplyForbiddenBodyOrRange() throws Exception {
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var service = new MediaRangeService(new DescriptorFileResolver(held, identity));
      for (Optional<String> range :
          List.of(
              Optional.<String>empty(),
              Optional.of(FIXTURE_BYTES_2_4_8BC33315),
              Optional.of("invalid"))) {
        FakeResponse get = deliver(service, inline, range, false);
        FakeResponse head = deliver(service, inline, range, true);
        assertEquals(get.status, head.status);
        assertEquals(get.headers, head.headers);
        assertEquals(0, head.bodyCalls);
        assertEquals(0, head.output.size());
        for (boolean onlyHead : new boolean[] {false, true}) {
          expect(
              deliver(service, attachment, range, onlyHead),
              200,
              0,
              2_097_155,
              null,
              true,
              onlyHead);
        }
      }
      // The seven MIME mappings are descriptor-validated; HTTP preserves each real MIME inline.
      for (String[] format :
          List.of(
              new String[] {"AUDIO", "scenario/a.ogg", FIXTURE_AUDIO_OGG_96A5CB00},
              new String[] {"VIDEO", "video/a.mp4", "video/mp4"},
              new String[] {FIXTURE_MUSIC_D5800D43, "music/a.m4a", "audio/mp4"},
              new String[] {FIXTURE_MUSIC_D5800D43, "music/a.mp3", "audio/mpeg"},
              new String[] {FIXTURE_MUSIC_D5800D43, "music/a.ogg", FIXTURE_AUDIO_OGG_96A5CB00},
              new String[] {FIXTURE_MUSIC_D5800D43, "music/a.wav", "audio/wav"},
              new String[] {FIXTURE_MUSIC_D5800D43, "music/a.flac", "audio/flac"})) {
        var d =
            new MediaDescriptor(
                MediaType.valueOf(format[0]),
                "7",
                format[1],
                "name" + format[1].substring(format[1].lastIndexOf('.')),
                2_097_155,
                "a".repeat(64),
                format[2],
                ContentDisposition.INLINE);
        var port =
            new MediaRangeService(
                (ignored, operation) ->
                    new DescriptorFileResolver(held, identity).read(inline, operation));
        assertEquals(
            format[2], deliver(port, d, Optional.empty(), true).headers.get("Content-Type"));
      }
    }
  }

  @Test
  void med029DescriptorBindingRejectsBeforeFileAndPermit() throws Exception {
    AtomicInteger opens = new AtomicInteger();
    var service = new MediaRangeService((d, op) -> opens.incrementAndGet());
    FakeResponse response = new FakeResponse("none");
    for (int variant = 0; variant < 3; variant++) {
      int which = variant;
      reject(
          MediaDeliveryException.Reason.INVALID_DESCRIPTOR,
          () ->
              service.deliver(
                  which == 0 ? MediaType.AUDIO : MediaType.MUSIC,
                  which == 1 ? "wrong" : "7",
                  which == 2 ? ContentDisposition.ATTACHMENT : ContentDisposition.INLINE,
                  Optional.empty(),
                  false,
                  inline,
                  response));
    }
    assertEquals(0, opens.get());
    assertEquals(0, response.begins);
    assertThrows(NullPointerException.class, () -> new MediaRangeService(null));
    assertThrows(NullPointerException.class, () -> new MediaDeliveryException(null));
    assertThrows(
        NullPointerException.class,
        () ->
            service.deliver(
                null, "7", ContentDisposition.INLINE, Optional.empty(), false, inline, response));
    assertThrows(
        NullPointerException.class,
        () ->
            service.deliver(
                MediaType.MUSIC,
                null,
                ContentDisposition.INLINE,
                Optional.empty(),
                false,
                inline,
                response));
    assertThrows(
        NullPointerException.class,
        () ->
            service.deliver(MediaType.MUSIC, "7", null, Optional.empty(), false, inline, response));
    assertThrows(
        NullPointerException.class,
        () ->
            service.deliver(
                MediaType.MUSIC, "7", ContentDisposition.INLINE, null, false, inline, response));
    assertThrows(
        NullPointerException.class,
        () ->
            service.deliver(
                MediaType.MUSIC,
                "7",
                ContentDisposition.INLINE,
                Optional.empty(),
                false,
                null,
                response));
    assertThrows(
        NullPointerException.class,
        () ->
            service.deliver(
                MediaType.MUSIC,
                "7",
                ContentDisposition.INLINE,
                Optional.empty(),
                false,
                inline,
                null));
    assertEquals(0, opens.get());
  }

  @Test
  void med030TwentyStreamsRejectTwentyFirstAndRecoverAllPermits() throws Exception {
    for (int maximum : new int[] {1, 2, 20}) {
      try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
          var executor = Executors.newVirtualThreadPerTaskExecutor()) {
        var real = new DescriptorFileResolver(held, identity);
        AtomicInteger opens = new AtomicInteger();
        var entered =
            new java.util.concurrent.atomic.AtomicReference<>(new CountDownLatch(maximum));
        var release = new java.util.concurrent.atomic.AtomicReference<>(new CountDownLatch(1));
        var service =
            new MediaRangeService(
                (d, op) -> {
                  int position = opens.incrementAndGet();
                  entered.get().countDown();
                  try {
                    assertTrue(release.get().await(10, TimeUnit.SECONDS));
                  } catch (InterruptedException failure) {
                    Thread.currentThread().interrupt();
                    throw new IOException("interrupted");
                  }
                  if (position == 1) throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                  real.read(d, op);
                },
                maximum);
        for (int round = 0; round < 2; round++) {
          var tasks = new ArrayList<java.util.concurrent.Future<Boolean>>();
          try {
            for (int i = 0; i < maximum; i++)
              tasks.add(
                  executor.submit(
                      () -> {
                        try {
                          deliver(service, inline, Optional.of(FIXTURE_BYTES_2_4_8BC33315), false);
                          return true;
                        } catch (MediaDeliveryException failure) {
                          assertEquals(MediaDeliveryException.Reason.UNAVAILABLE, failure.reason());
                          return false;
                        }
                      }));
            assertTrue(entered.get().await(10, TimeUnit.SECONDS));
            int before = opens.get();
            reject(
                MediaDeliveryException.Reason.BUSY,
                () -> deliver(service, inline, Optional.empty(), true));
            reject(
                MediaDeliveryException.Reason.INVALID_DESCRIPTOR,
                () ->
                    service.deliver(
                        MediaType.AUDIO,
                        "7",
                        ContentDisposition.INLINE,
                        Optional.empty(),
                        true,
                        inline,
                        new FakeResponse("none")));
            assertEquals(before, opens.get());
          } finally {
            release.get().countDown();
          }
          int success = 0;
          for (var task : tasks) if (task.get(10, TimeUnit.SECONDS)) success++;
          assertEquals(round == 0 ? maximum - 1 : maximum, success);
          entered.set(new CountDownLatch(maximum));
          release.set(new CountDownLatch(1));
        }
        assertEquals(maximum * 2, opens.get());
        assertThrows(NullPointerException.class, () -> new MediaRangeService(null, maximum));
        assertThrows(IllegalArgumentException.class, () -> new MediaRangeService(real, 0));
        assertThrows(IllegalArgumentException.class, () -> new MediaRangeService(real, 21));
      }
    }
  }

  @Test
  void med031IoFailuresReleasePermitsWithoutSecondResponse() throws Exception {
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      var real = new DescriptorFileResolver(held, identity);
      for (String fault :
          List.of("source", "begin", "body", "write", "partial", "read", "post-close")) {
        AtomicInteger attempts = new AtomicInteger();
        var service =
            new MediaRangeService(
                (d, op) -> {
                  boolean first = attempts.incrementAndGet() == 1;
                  if (first && fault.equals("source"))
                    throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                  real.read(
                      d,
                      channel -> {
                        if (first && fault.equals("read")) channel.close();
                        op.execute(channel);
                      });
                  if (first && fault.equals("post-close"))
                    throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
                });
        FakeResponse response = new FakeResponse(fault);
        reject(
            MediaDeliveryException.Reason.UNAVAILABLE,
            () ->
                service.deliver(
                    MediaType.MUSIC,
                    "7",
                    ContentDisposition.INLINE,
                    Optional.empty(),
                    false,
                    inline,
                    response));
        assertEquals(fault.equals("source") ? 0 : 1, response.begins);
        assertEquals(0, response.closes);
        if (fault.equals("partial")) assertEquals(65_536, response.output.size());
        FakeResponse recovery =
            deliver(service, inline, Optional.of(FIXTURE_BYTES_2_4_8BC33315), false);
        expect(recovery, 206, 2, 5, "bytes 2-4/2097155", false, false);
      }
    }
  }

  @Test
  void med032OneHundredCallsHaveIndependentPositionsAndHeaders() throws Exception {
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root);
        var executor = Executors.newFixedThreadPool(10)) {
      AtomicInteger opens = new AtomicInteger();
      AtomicInteger closes = new AtomicInteger();
      var real = new DescriptorFileResolver(held, identity);
      var service =
          new MediaRangeService(
              (d, op) -> {
                opens.incrementAndGet();
                real.read(d, op);
                closes.incrementAndGet();
              });
      synchronized (service) {
        var tasks = new ArrayList<java.util.concurrent.Future<FakeResponse>>();
        for (int i = 0; i < 100; i++) {
          int start = i;
          tasks.add(
              executor.submit(
                  () ->
                      deliver(
                          service,
                          inline,
                          Optional.of("bytes=" + start + "-" + (start + 2)),
                          false)));
        }
        for (int i = 0; i < 100; i++)
          expect(
              tasks.get(i).get(10, TimeUnit.SECONDS),
              206,
              i,
              i + 3,
              "bytes " + i + "-" + (i + 2) + "/2097155",
              false,
              false);
      }
      assertEquals(100, opens.get());
      assertEquals(100, closes.get());
    }
  }

  private static MediaDescriptor descriptor(ContentDisposition disposition) {
    return new MediaDescriptor(
        MediaType.MUSIC,
        "7",
        "music/a.ogg",
        "音源.ogg",
        2_097_155,
        "a".repeat(64),
        FIXTURE_AUDIO_OGG_96A5CB00,
        disposition);
  }

  private static FakeResponse deliver(
      MediaRangeService service, MediaDescriptor d, Optional<String> range, boolean head)
      throws MediaDeliveryException {
    FakeResponse response = new FakeResponse("none");
    service.deliver(d.mediaType(), d.logicalId(), d.disposition(), range, head, d, response);
    return response;
  }

  private void expect(
      FakeResponse response,
      int status,
      int first,
      int end,
      String contentRange,
      boolean download,
      boolean head) {
    Map<String, String> expected = new HashMap<>();
    expected.put("Accept-Ranges", "bytes");
    expected.put(
        "Content-Type", download ? "application/octet-stream" : FIXTURE_AUDIO_OGG_96A5CB00);
    expected.put(
        "Content-Disposition",
        (download ? "attachment" : "inline")
            + "; filename=\"download.bin\"; filename*=UTF-8''%E9%9F%B3%E6%BA%90.ogg");
    expected.put("X-Content-Type-Options", "nosniff");
    expected.put("Cache-Control", "private, no-store");
    expected.put("Content-Length", Integer.toString(end - first));
    if (contentRange != null) expected.put("Content-Range", contentRange);
    assertEquals(status, response.status);
    assertEquals(expected, response.headers);
    assertThrows(UnsupportedOperationException.class, () -> response.headers.put("X", "Y"));
    assertArrayEquals(
        head || first == end ? new byte[0] : Arrays.copyOfRange(content, first, end),
        response.output.toByteArray());
    assertEquals(head || first == end ? 0 : 1, response.bodyCalls);
    assertEquals(1, response.begins);
    assertEquals(0, response.closes);
  }

  private static void reject(
      MediaDeliveryException.Reason reason, org.junit.jupiter.api.function.Executable action) {
    MediaDeliveryException failure = assertThrows(MediaDeliveryException.class, action);
    assertEquals(reason, failure.reason());
    assertEquals(503, failure.httpStatus());
    assertEquals(
        reason == MediaDeliveryException.Reason.BUSY
            ? java.util.OptionalInt.of(1)
            : java.util.OptionalInt.empty(),
        failure.retryAfterSeconds());
    assertEquals("media delivery failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class FakeResponse implements MediaRangeService.Response {
    final String fault;
    final ByteArrayOutputStream output = new ByteArrayOutputStream();
    Map<String, String> headers = Map.of();
    int status;
    int begins;
    int bodyCalls;
    int closes;
    int writes;

    FakeResponse(String fault) {
      this.fault = fault;
    }

    @Override
    public void begin(int value, Map<String, String> values) throws IOException {
      begins++;
      if (fault.equals("begin")) throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      status = value;
      headers = values;
    }

    @Override
    public OutputStream body() throws IOException {
      bodyCalls++;
      if (fault.equals("body")) throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
      return new OutputStream() {
        @Override
        public void write(int value) {
          fail("unexpected per-byte output");
        }

        @Override
        public void write(byte[] bytes, int offset, int length) throws IOException {
          writes++;
          if (fault.equals("write") || fault.equals("partial") && writes == 2)
            throw new IOException(FIXTURE_SYNTHETIC_PRIVATE_PATH_6CBCF6F9);
          assertTrue(length <= 65_536);
          output.write(bytes, offset, length);
        }

        @Override
        public void close() {
          closes++;
        }
      };
    }
  }
}
