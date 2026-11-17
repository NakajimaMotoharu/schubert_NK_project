package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/**
 * Full wire bytes are assembled from UI232/235 offsets, not a production encoder. PT-MED-037..040.
 */
class MediaResponseDecoderTest {
  private static final String SUCCESS_RESULT_CODE = "0000";
  private static final String OGG_AUDIO_MIME = "audio/ogg";
  private static final String MUSIC_OGG_PATH = "music/a.ogg";
  private static final String MUSIC_TYPE_NAME = "MUSIC";
  private static final String HASH = "0123456789abcdef".repeat(4);

  @Test
  void med037ThreeRequestsBindAllApprovedSuccessfulDescriptors() throws Exception {
    for (String[] format : formats()) {
      MediaType type = MediaType.valueOf(format[0]);
      for (String mode : type == MediaType.VIDEO ? List.of("I") : List.of("I", "A")) {
        for (String code : List.of(SUCCESS_RESULT_CODE, "0200")) {
          for (long size : new long[] {1, 999_999_999_999L}) {
            String id = type == MediaType.AUDIO ? "999999999999" : "論理é";
            var request = request(type, id, mode);
            String name = "音源" + format[1].substring(format[1].lastIndexOf('.'));
            byte[] data = media(type, id, format[1], name, size, format[2], mode);
            byte[] body = reply(request, data, code);
            byte[] before = body.clone();
            var result = MediaResponseDecoder.decode(request, body);
            assertEquals(
                code.equals(SUCCESS_RESULT_CODE)
                    ? ResultCode.SUCCESS
                    : ResultCode.IDEMPOTENT_SUCCESS,
                result.resultCode());
            var descriptor = result.descriptor().orElseThrow();
            assertEquals(type, descriptor.mediaType());
            assertEquals(id, descriptor.logicalId());
            assertEquals(format[1], descriptor.storageRelativePath());
            assertEquals(name, descriptor.fileName());
            assertEquals(size, descriptor.byteLength());
            assertEquals(HASH, descriptor.sha256());
            assertEquals(format[2], descriptor.mimeType());
            assertEquals(
                mode.equals("I") ? ContentDisposition.INLINE : ContentDisposition.ATTACHMENT,
                descriptor.disposition());
            assertEquals("MediaResponse[REDACTED]", result.toString());
            assertArrayEquals(before, body);
            assertEquals(type == MediaType.VIDEO, result.videoMetadata().isPresent());
            if (type == MediaType.VIDEO) {
              var video = result.videoMetadata().orElseThrow();
              assertEquals("Opening", video.title());
              assertEquals("OPENING", video.category().wireValue());
              assertEquals("opening.mp4", video.displayPath().wireValue());
            }
          }
        }
      }
    }
  }

  @Test
  void med038ErrorProfilesKeepCodesWithoutFabricatedDescriptors() throws Exception {
    Map<String, ResultCode> errors =
        Map.of(
            "0100",
            ResultCode.VALIDATION_ERROR,
            "0101",
            ResultCode.AUTHENTICATION_FAILED,
            "0102",
            ResultCode.SESSION_INVALID,
            "0103",
            ResultCode.FORBIDDEN,
            "0104",
            ResultCode.NOT_FOUND,
            "0105",
            ResultCode.CONFLICT,
            "0106",
            ResultCode.LOCKED,
            "0107",
            ResultCode.NOT_CANCELLABLE,
            "9000",
            ResultCode.TEMPORARY_FAILURE,
            "9001",
            ResultCode.RESOURCE_LIMIT);
    for (MediaType type : MediaType.values()) {
      var request = request(type, "7", "I");
      for (var error : errors.entrySet()) {
        byte[] data = spaces(type == MediaType.VIDEO ? 1808 : 1024);
        put(data, 832, "000000000000");
        var result = MediaResponseDecoder.decode(request, reply(request, data, error.getKey()));
        assertEquals(error.getValue(), result.resultCode());
        assertTrue(result.descriptor().isEmpty());
        assertTrue(result.videoMetadata().isEmpty());
        data[0] = 'X';
        reject(request, reply(request, data, error.getKey()));
      }
    }
  }

  @Test
  void med039MalformedAndMismatchedRepliesNeverAuthorizeFiles() {
    var request = request(MediaType.AUDIO, "7", "I");
    byte[] body =
        reply(
            request,
            media(MediaType.AUDIO, "7", "scenario/a.ogg", "a.ogg", 3, OGG_AUDIO_MIME, "I"),
            SUCCESS_RESULT_CODE);
    assertThrows(NullPointerException.class, () -> MediaResponseDecoder.decode(null, body));
    assertThrows(NullPointerException.class, () -> MediaResponseDecoder.decode(request, null));
    for (int length : new int[] {0, 255, 2065, body.length - 1, body.length + 1})
      reject(request, Arrays.copyOf(body, length));
    for (String[] mutation :
        List.of(
            new String[] {"0", "X"},
            new String[] {"8", "002"},
            new String[] {"11", "MEDRSP01"},
            new String[] {"19", "002"},
            new String[] {"22", "E"},
            new String[] {"23", "A"},
            new String[] {"24", "NOT-A-UUID"},
            new String[] {"60", "00000000-0000-4000-8000-000000000999"},
            new String[] {"96", "00000000000000000"},
            new String[] {"177", "0257"},
            new String[] {"181", "001025"},
            new String[] {"187", "000001"},
            new String[] {"193", "000001"},
            new String[] {"199", "000001279"},
            new String[] {"208", "9999"},
            new String[] {"212", "X"})) {
      byte[] changed = body.clone();
      put(changed, Integer.parseInt(mutation[0]), mutation[1]);
      reject(request, changed);
    }
    for (int i = 0; i < 64; i++) {
      byte[] changed = body.clone();
      changed[113 + i] = 'a';
      reject(request, changed);
    }
    for (String[] mutation :
        List.of(
            new String[] {"0", "8"},
            new String[] {"64", MUSIC_OGG_PATH},
            new String[] {"576", "a.mp3"},
            new String[] {"832", "000000000000"},
            new String[] {"844", "G"},
            new String[] {"908", "audio/wav"},
            new String[] {"972", "A"},
            new String[] {"973", "X"},
            new String[] {"576", "e\u0301.ogg"})) {
      byte[] changed = body.clone();
      put(changed, 256 + Integer.parseInt(mutation[0]), mutation[1]);
      reject(request, changed);
    }
    byte[] invalidUtf8 = body.clone();
    invalidUtf8[256 + 576] = (byte) 0xc3;
    reject(request, invalidUtf8);
    reject(
        request,
        reply(
            request,
            media(
                MediaType.AUDIO,
                "7",
                "scenario/" + "a".repeat(252) + ".ogg",
                "a.ogg",
                3,
                OGG_AUDIO_MIME,
                "I"),
            SUCCESS_RESULT_CODE));
    reject(wireRequest("ANMREQ01", new byte[0]), body);
    reject(wireRequest("ZZZREQ01", new byte[0]), body);
    reject(wireRequest("AUDREQ01", spaces(16)), body);
    reject(wireRequest("AUDREQ01", spaces(17)), body);
    var video = request(MediaType.VIDEO, "7", "I");
    byte[] validVideo = media(MediaType.VIDEO, "7", "video/a.mp4", "a.mp4", 3, "video/mp4", "I");
    for (String[] mutation :
        List.of(
            new String[] {"1024", "\n"},
            new String[] {"1280", "UNKNOWN"},
            new String[] {"1296", "/outside.mp4"})) {
      byte[] changed = validVideo.clone();
      put(changed, Integer.parseInt(mutation[0]), mutation[1]);
      reject(video, reply(video, changed, SUCCESS_RESULT_CODE));
    }
  }

  @Test
  void med040ConcurrentDecodeOwnsBytesAndIsolatesRequests() throws Exception {
    var executor = Executors.newFixedThreadPool(8);
    try {
      var jobs = new ArrayList<java.util.concurrent.Future<Boolean>>();
      for (int i = 0; i < 100; i++) {
        String id = "track-" + i;
        jobs.add(
            executor.submit(
                () -> {
                  var request = request(MediaType.MUSIC, id, "A");
                  byte[] body =
                      reply(
                          request,
                          media(
                              MediaType.MUSIC,
                              id,
                              MUSIC_OGG_PATH,
                              "音源.ogg",
                              3,
                              OGG_AUDIO_MIME,
                              "A"),
                          "0200");
                  var result = MediaResponseDecoder.decode(request, body);
                  reject(request(MediaType.MUSIC, id, "A"), body);
                  Arrays.fill(body, (byte) 0);
                  assertEquals(id, result.descriptor().orElseThrow().logicalId());
                  assertEquals(
                      MUSIC_OGG_PATH, result.descriptor().orElseThrow().storageRelativePath());
                  assertEquals(ResultCode.IDEMPOTENT_SUCCESS, result.resultCode());
                  return true;
                }));
      }
      for (var job : jobs) assertTrue(job.get(10, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      assertTrue(
          executor.awaitTermination(10, TimeUnit.SECONDS), "media decoder executor terminated");
    }
  }

  // PT-MED-CONTEXT001..006: independent heap fault vectors; no actual OOM or credentials.
  @Test
  void context001PositiveAndPortBoundaryPreserveCallerBytes() throws Exception {
    var request = contextRequest();
    byte[] body = contextReply(request);
    byte[] before = body.clone();
    assertThrows(
        NullPointerException.class, () -> MediaResponseDecoder.decode(request, body, null));
    var probe = new ContextProbe(64, 64);
    assertEquals(
        "7",
        MediaResponseDecoder.decode(request, body, probe).descriptor().orElseThrow().logicalId());
    assertEquals(2, probe.encodeCalls);
    assertEquals(1, probe.comparisons);
    assertArrayEquals(new byte[64], probe.first);
    assertArrayEquals(new byte[64], probe.second);
    assertArrayEquals(before, body);
  }

  @Test
  void context002SecondKnownAcquisitionFailureClearsOnlyOwnedFirst() {
    var request = contextRequest();
    byte[] body = contextReply(request);
    byte[] before = body.clone();
    var probe = new ContextProbe(64, 64);
    probe.failAt = 2;
    probe.encodingFailure = new IllegalStateException("PUBLIC second acquire");
    byte[] unowned = probe.second.clone();
    var failure =
        assertThrows(
            MediaDeliveryException.class, () -> MediaResponseDecoder.decode(request, body, probe));
    contextFailure(failure);
    assertEquals(2, probe.encodeCalls);
    assertEquals(0, probe.comparisons);
    assertArrayEquals(new byte[64], probe.first);
    assertArrayEquals(unowned, probe.second);
    assertArrayEquals(before, body);
  }

  @Test
  void context003ComparisonFailuresClearBothAndKeepFatalIdentity() {
    for (Throwable sentinel :
        List.of(
            new IllegalStateException("PUBLIC compare"), new AssertionError("PUBLIC compare"))) {
      var request = contextRequest();
      byte[] body = contextReply(request);
      byte[] before = body.clone();
      var probe = new ContextProbe(64, 64);
      probe.comparisonFailure = sentinel;
      if (sentinel instanceof Error) {
        assertSame(
            sentinel,
            assertThrows(
                AssertionError.class, () -> MediaResponseDecoder.decode(request, body, probe)));
      } else {
        contextFailure(
            assertThrows(
                MediaDeliveryException.class,
                () -> MediaResponseDecoder.decode(request, body, probe)));
      }
      assertEquals(2, probe.encodeCalls);
      assertEquals(1, probe.comparisons);
      assertArrayEquals(new byte[64], probe.first);
      assertArrayEquals(new byte[64], probe.second);
      assertArrayEquals(before, body);
    }
  }

  @Test
  void context004NullArraysAtEitherAcquisitionNeverCompare() {
    for (int stage : new int[] {1, 2}) {
      var request = contextRequest();
      byte[] body = contextReply(request);
      byte[] before = body.clone();
      var probe = new ContextProbe(64, 64);
      probe.nullAt = stage;
      byte[] unownedFirst = probe.first.clone();
      byte[] unownedSecond = probe.second.clone();
      contextFailure(
          assertThrows(
              MediaDeliveryException.class,
              () -> MediaResponseDecoder.decode(request, body, probe)));
      assertEquals(stage, probe.encodeCalls);
      assertEquals(0, probe.comparisons);
      assertArrayEquals(stage == 2 ? new byte[64] : unownedFirst, probe.first);
      assertArrayEquals(unownedSecond, probe.second);
      assertArrayEquals(before, body);
    }
  }

  @Test
  void context005WrongLengthsAreRejectedAndClearedBeforeOwnershipCanEscape() {
    for (int stage : new int[] {1, 2}) {
      for (int length : new int[] {0, 63, 65}) {
        var request = contextRequest();
        byte[] body = contextReply(request);
        byte[] before = body.clone();
        var probe = new ContextProbe(stage == 1 ? length : 64, stage == 2 ? length : 64);
        byte[] unownedSecond = probe.second.clone();
        contextFailure(
            assertThrows(
                MediaDeliveryException.class,
                () -> MediaResponseDecoder.decode(request, body, probe)));
        assertEquals(stage, probe.encodeCalls);
        assertEquals(0, probe.comparisons);
        assertArrayEquals(new byte[stage == 1 ? length : 64], probe.first);
        assertArrayEquals(stage == 2 ? new byte[length] : unownedSecond, probe.second);
        assertArrayEquals(before, body);
      }
    }
  }

  @Test
  void context006UnknownSecondAcquisitionFailuresKeepIdentityAndClearOwnedFirst() {
    for (Throwable sentinel :
        List.of(
            new UnsupportedOperationException("PUBLIC unknown acquire"),
            new AssertionError("PUBLIC fatal acquire"))) {
      var request = contextRequest();
      byte[] body = contextReply(request);
      byte[] before = body.clone();
      var probe = new ContextProbe(64, 64);
      probe.failAt = 2;
      probe.encodingFailure = sentinel;
      byte[] unownedSecond = probe.second.clone();
      assertSame(
          sentinel,
          assertThrows(
              sentinel.getClass(), () -> MediaResponseDecoder.decode(request, body, probe)));
      assertEquals(2, probe.encodeCalls);
      assertEquals(0, probe.comparisons);
      assertArrayEquals(new byte[64], probe.first);
      assertArrayEquals(unownedSecond, probe.second);
      assertArrayEquals(before, body);
    }
  }

  private static WireMessage<FixedPayload> contextRequest() {
    return request(MediaType.AUDIO, "7", "I");
  }

  private static byte[] contextReply(WireMessage<FixedPayload> request) {
    return reply(
        request,
        media(MediaType.AUDIO, "7", "scenario/a.ogg", "a.ogg", 3, OGG_AUDIO_MIME, "I"),
        SUCCESS_RESULT_CODE);
  }

  private static void contextFailure(MediaDeliveryException failure) {
    assertEquals(MediaDeliveryException.Reason.INVALID_DESCRIPTOR, failure.reason());
    assertEquals("media delivery failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class ContextProbe implements MediaResponseDecoder.ContextOperations {
    private final byte[] first;
    private final byte[] second;
    private int encodeCalls;
    private int comparisons;
    private int nullAt;
    private int failAt;
    private @Nullable Throwable encodingFailure;
    private @Nullable Throwable comparisonFailure;

    ContextProbe(int firstLength, int secondLength) {
      first = new byte[firstLength];
      second = new byte[secondLength];
      Arrays.fill(first, (byte) '1');
      Arrays.fill(second, (byte) '1');
    }

    @Override
    public byte @Nullable [] encode(AuthenticationContext context) {
      assertNotNull(context);
      encodeCalls++;
      if (encodeCalls == failAt) contextRaise(encodingFailure);
      if (encodeCalls == nullAt) return null;
      return encodeCalls == 1 ? first : second;
    }

    @Override
    public boolean same(byte[] left, byte[] right) {
      comparisons++;
      assertSame(first, left);
      assertSame(second, right);
      if (comparisonFailure != null) contextRaise(comparisonFailure);
      return MessageDigest.isEqual(left, right);
    }

    private static void contextRaise(@Nullable Throwable sentinel) {
      assertNotNull(sentinel);
      if (sentinel instanceof RuntimeException runtime) throw runtime;
      throw (Error) sentinel;
    }
  }

  private static List<String[]> formats() {
    return List.of(
        new String[] {"AUDIO", "scenario/a.ogg", OGG_AUDIO_MIME},
        new String[] {"VIDEO", "video/a.mp4", "video/mp4"},
        new String[] {MUSIC_TYPE_NAME, "music/a.m4a", "audio/mp4"},
        new String[] {MUSIC_TYPE_NAME, "music/a.mp3", "audio/mpeg"},
        new String[] {MUSIC_TYPE_NAME, MUSIC_OGG_PATH, OGG_AUDIO_MIME},
        new String[] {MUSIC_TYPE_NAME, "music/a.wav", "audio/wav"},
        new String[] {MUSIC_TYPE_NAME, "music/a.flac", "audio/flac"});
  }

  private static WireMessage<FixedPayload> request(MediaType type, String id, String mode) {
    String layout =
        switch (type) {
          case AUDIO -> "AUDREQ01";
          case VIDEO -> "VIDREQ01";
          case MUSIC -> "MEDREQ01";
        };
    byte[] data = spaces(type == MediaType.AUDIO ? 16 : type == MediaType.VIDEO ? 64 : 72);
    put(
        data,
        0,
        type == MediaType.AUDIO ? String.format(Locale.ROOT, "%012d", Long.parseLong(id)) : id);
    if (type != MediaType.VIDEO) put(data, type == MediaType.AUDIO ? 12 : 64, mode);
    return wireRequest(layout, data);
  }

  private static WireMessage<FixedPayload> wireRequest(String layout, byte[] data) {
    UUID id = UUID.randomUUID();
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            Instant.parse("2026-09-08T00:00:00Z"),
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }

  private static byte[] reply(WireMessage<FixedPayload> request, byte[] data, String code) {
    byte[] body = spaces(256 + data.length);
    put(body, 0, "SCHBNK01001");
    put(body, 11, request.header().layoutId().value().replace("REQ", "RSP"));
    put(body, 19, "001SS");
    put(body, 24, "00000000-0000-4000-8000-000000000123");
    put(body, 60, request.header().messageId().toString());
    put(body, 96, "20260908090000000");
    put(body, 113, "b".repeat(64));
    put(body, 177, "0256");
    put(body, 181, String.format(Locale.ROOT, "%06d", data.length));
    put(body, 187, "000000000000");
    put(body, 199, String.format(Locale.ROOT, "%09d", body.length));
    put(body, 208, code);
    System.arraycopy(data, 0, body, 256, data.length);
    return body;
  }

  private static byte[] media(
      MediaType type, String id, String path, String name, long size, String mime, String mode) {
    byte[] data = spaces(type == MediaType.VIDEO ? 1808 : 1024);
    put(data, 0, id);
    put(data, 64, path);
    put(data, 576, name);
    put(data, 832, String.format(Locale.ROOT, "%012d", size));
    put(data, 844, HASH);
    put(data, 908, mime);
    put(data, 972, mode);
    if (type == MediaType.VIDEO) {
      put(data, 1024, "Opening");
      put(data, 1280, "OPENING");
      put(data, 1296, "opening.mp4");
    }
    return data;
  }

  private static byte[] spaces(int size) {
    byte[] bytes = new byte[size];
    Arrays.fill(bytes, (byte) 32);
    return bytes;
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }

  private static void reject(WireMessage<FixedPayload> request, byte[] body) {
    var failure =
        assertThrows(
            MediaDeliveryException.class, () -> MediaResponseDecoder.decode(request, body));
    assertEquals(MediaDeliveryException.Reason.INVALID_DESCRIPTOR, failure.reason());
    assertEquals(503, failure.httpStatus());
    assertEquals("media delivery failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
