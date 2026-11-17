package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutRequestData;
import dev.codex.schubert.nk.protocol.layout.media.AudioDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.MusicDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.media.VideoDescriptorRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.AudioId;
import dev.codex.schubert.nk.protocol.layout.semantic.ContentDisposition;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * PT-MED-VERIFIED001..004. Legitimate facade with synchronous memory sender; no broker/file/keys.
 */
final class MediaVerifiedProjectionTest {
  private static final String AUDIO_LAYOUT = "AUDREQ01";
  private static final String VIDEO_LAYOUT = "VIDREQ01";
  private static final String MUSIC_LAYOUT = "MEDREQ01";
  private static final String SUCCESS = "0000";
  private static final String IDEMPOTENT = "0200";
  private static final String MUSIC_NAME = "音源.ogg";
  private static final String VIDEO_NAME = "a.mp4";
  private static final String VIDEO_MIME = "video/mp4";
  private static final String OGG_MIME = "audio/ogg";
  private static final String SYNTHETIC_HASH = "0123456789abcdef".repeat(4);
  private static final String LOGICAL_ID = "7";
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-08T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void normalFacadeProjectsAllKindsAndBothSuccessCodes() throws Exception {
    for (MediaType type : MediaType.values()) {
      for (ContentDisposition mode :
          type == MediaType.VIDEO
              ? List.of(ContentDisposition.INLINE)
              : List.of(ContentDisposition.INLINE, ContentDisposition.ATTACHMENT)) {
        for (String code : List.of(SUCCESS, IDEMPOTENT)) {
          String id = type == MediaType.AUDIO ? LOGICAL_ID : "é";
          TypedPayloadValues request = request(type, id, mode);
          var response = exchange(request, type, id, mode, code);
          var result = MediaResponseDecoder.decodeVerified(request, response);
          assertEquals(
              code.equals(SUCCESS) ? ResultCode.SUCCESS : ResultCode.IDEMPOTENT_SUCCESS,
              result.resultCode());
          var descriptor = result.descriptor().orElseThrow();
          assertEquals(type, descriptor.mediaType());
          assertEquals(id, descriptor.logicalId());
          assertEquals(path(type), descriptor.storageRelativePath());
          assertEquals(type == MediaType.VIDEO ? VIDEO_NAME : MUSIC_NAME, descriptor.fileName());
          assertEquals(3, descriptor.byteLength());
          assertEquals(SYNTHETIC_HASH, descriptor.sha256());
          assertEquals(type == MediaType.VIDEO ? VIDEO_MIME : OGG_MIME, descriptor.mimeType());
          assertEquals(mode.name(), descriptor.disposition().name());
          assertEquals("MediaResponse[REDACTED]", result.toString());
          assertEquals(type == MediaType.VIDEO, result.videoMetadata().isPresent());
          if (type == MediaType.VIDEO) {
            var metadata = result.videoMetadata().orElseThrow();
            assertEquals("Opening", metadata.title());
            assertEquals("OPENING", metadata.category().wireValue());
            assertEquals("opening.mp4", metadata.displayPath().wireValue());
          }
        }
      }
    }
    TypedPayloadValues decomposed = request(MediaType.MUSIC, "e\u0301", ContentDisposition.INLINE);
    var normalizedResponse =
        exchange(decomposed, MediaType.MUSIC, "é", ContentDisposition.INLINE, SUCCESS);
    assertEquals(
        "é",
        MediaResponseDecoder.decodeVerified(decomposed, normalizedResponse)
            .descriptor()
            .orElseThrow()
            .logicalId());
  }

  @Test
  void errorProfilesRetainExactCodeWithoutAnyProjectedDescriptor() throws Exception {
    Map<String, ResultCode> errors =
        Map.ofEntries(
            Map.entry("0100", ResultCode.VALIDATION_ERROR),
            Map.entry("0101", ResultCode.AUTHENTICATION_FAILED),
            Map.entry("0102", ResultCode.SESSION_INVALID),
            Map.entry("0103", ResultCode.FORBIDDEN),
            Map.entry("0104", ResultCode.NOT_FOUND),
            Map.entry("0105", ResultCode.CONFLICT),
            Map.entry("0106", ResultCode.LOCKED),
            Map.entry("0107", ResultCode.NOT_CANCELLABLE),
            Map.entry("9000", ResultCode.TEMPORARY_FAILURE),
            Map.entry("9001", ResultCode.RESOURCE_LIMIT));
    for (MediaType type : MediaType.values()) {
      TypedPayloadValues request = request(type, LOGICAL_ID, ContentDisposition.INLINE);
      for (var error : errors.entrySet()) {
        var projected =
            MediaResponseDecoder.decodeVerified(
                request,
                exchange(request, type, LOGICAL_ID, ContentDisposition.INLINE, error.getKey()));
        assertEquals(error.getValue(), projected.resultCode());
        assertTrue(projected.descriptor().isEmpty());
        assertTrue(projected.videoMetadata().isEmpty());
      }
    }
  }

  @Test
  void typedRequestMismatchAndNullGuardsDoNotBecomeAFileGrant() throws Exception {
    TypedPayloadValues request = request(MediaType.AUDIO, LOGICAL_ID, ContentDisposition.INLINE);
    var response =
        exchange(request, MediaType.AUDIO, LOGICAL_ID, ContentDisposition.INLINE, SUCCESS);
    List<TypedPayloadValues> wrong =
        List.of(
            new TypedPayloadValues(new LayoutId("LOGREQ01"), new LogoutRequestData(), List.of()),
            new TypedPayloadValues(new LayoutId(AUDIO_LAYOUT), new LogoutRequestData(), List.of()),
            new TypedPayloadValues(new LayoutId(VIDEO_LAYOUT), request.data(), List.of()),
            new TypedPayloadValues(new LayoutId(MUSIC_LAYOUT), request.data(), List.of()),
            request(MediaType.VIDEO, LOGICAL_ID, ContentDisposition.INLINE),
            request(MediaType.MUSIC, LOGICAL_ID, ContentDisposition.INLINE),
            request(MediaType.AUDIO, "8", ContentDisposition.INLINE),
            request(MediaType.AUDIO, LOGICAL_ID, ContentDisposition.ATTACHMENT),
            new TypedPayloadValues(
                new LayoutId(AUDIO_LAYOUT),
                request.data(),
                List.of((PayloadRecord) () -> new FieldValueSet(Map.of()))));
    for (TypedPayloadValues invalid : wrong) reject(invalid, response);
    assertThrows(
        NullPointerException.class, () -> MediaResponseDecoder.decodeVerified(null, response));
    assertThrows(
        NullPointerException.class, () -> MediaResponseDecoder.decodeVerified(request, null));
    assertEquals(
        LOGICAL_ID,
        MediaResponseDecoder.decodeVerified(request, response)
            .descriptor()
            .orElseThrow()
            .logicalId());
  }

  @Test
  void concurrentProjectionOfOneImmutableResultHasIndependentBinding() throws Exception {
    TypedPayloadValues valid = request(MediaType.AUDIO, LOGICAL_ID, ContentDisposition.INLINE);
    TypedPayloadValues wrong = request(MediaType.AUDIO, "8", ContentDisposition.INLINE);
    var response = exchange(valid, MediaType.AUDIO, LOGICAL_ID, ContentDisposition.INLINE, SUCCESS);
    var workers = Executors.newFixedThreadPool(2);
    try {
      var success = workers.submit(() -> MediaResponseDecoder.decodeVerified(valid, response));
      var failure =
          workers.submit(
              () -> {
                reject(wrong, response);
                return Boolean.TRUE;
              });
      assertEquals(
          LOGICAL_ID, success.get(5, TimeUnit.SECONDS).descriptor().orElseThrow().logicalId());
      assertTrue(failure.get(5, TimeUnit.SECONDS));
    } finally {
      workers.shutdownNow();
      assertTrue(
          workers.awaitTermination(10, TimeUnit.SECONDS), "media projection executor terminated");
    }
    assertEquals("ProtectedReadResponse[REDACTED]", response.toString());
    assertEquals(
        LOGICAL_ID,
        MediaResponseDecoder.decodeVerified(valid, response)
            .descriptor()
            .orElseThrow()
            .logicalId());
  }

  @Test
  void hashCollisionLayoutsNeverAcquireAProjectionFromALegitimateResult() throws Exception {
    MediaType[] types = {MediaType.AUDIO, MediaType.VIDEO, MediaType.MUSIC};
    String[][] vectors = {
      {"AUDREQ01", "B6DREQ01"}, {"VIDREQ01", "VIDRF201"}, {"MEDREQ01", "MEDRF201"}
    };
    for (int index = 0; index < vectors.length; index++) {
      assertNotEquals(vectors[index][0], vectors[index][1]);
      assertEquals(vectors[index][0].hashCode(), vectors[index][1].hashCode());
      var valid = request(types[index], LOGICAL_ID, ContentDisposition.INLINE);
      var response = exchange(valid, types[index], LOGICAL_ID, ContentDisposition.INLINE, SUCCESS);
      var invalid =
          new TypedPayloadValues(new LayoutId(vectors[index][1]), valid.data(), List.of());
      reject(invalid, response);
      assertEquals(
          LOGICAL_ID,
          MediaResponseDecoder.decodeVerified(valid, response)
              .descriptor()
              .orElseThrow()
              .logicalId());
    }
  }

  private static void reject(TypedPayloadValues request, ProtectedReadWireClient.Result response) {
    MediaDeliveryException failure =
        assertThrows(
            MediaDeliveryException.class,
            () -> MediaResponseDecoder.decodeVerified(request, response));
    assertEquals(MediaDeliveryException.Reason.INVALID_DESCRIPTOR, failure.reason());
    assertEquals("media delivery failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static TypedPayloadValues request(MediaType type, String id, ContentDisposition mode) {
    return switch (type) {
      case AUDIO ->
          new TypedPayloadValues(
              new LayoutId(AUDIO_LAYOUT),
              new AudioDescriptorRequestData(new AudioId(Long.parseLong(id)), mode),
              List.of());
      case VIDEO ->
          new TypedPayloadValues(
              new LayoutId(VIDEO_LAYOUT), new VideoDescriptorRequestData(id), List.of());
      case MUSIC ->
          new TypedPayloadValues(
              new LayoutId(MUSIC_LAYOUT), new MusicDescriptorRequestData(id, mode), List.of());
    };
  }

  private static ProtectedReadWireClient.Result exchange(
      TypedPayloadValues request, MediaType type, String id, ContentDisposition mode, String code) {
    JmsRequestReplyClient waiting =
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1);
    var facade =
        new MediaDescriptorWireClient(
            waiting,
            (correlation, bytes) -> {
              byte[] golden = response(type, id, mode, code, correlation);
              try {
                assertTrue(waiting.onReply(correlation, golden));
              } finally {
                Arrays.fill(golden, (byte) 0);
              }
            },
            CLOCK,
            () -> new UUID(0, 17),
            Duration.ofSeconds(1));
    // This repeated marker is an inert test context. No session, key, credential or real actor
    // exists.
    var result = facade.exchange(request, AuthenticationContext.of("b".repeat(64)));
    assertEquals(0, waiting.pendingCount());
    assertEquals(0, waiting.lateReplyCount());
    return result;
  }

  private static byte[] response(
      MediaType type, String id, ContentDisposition mode, String code, UUID correlation) {
    boolean video = type == MediaType.VIDEO;
    int dataLength = video ? 1808 : 1024;
    byte[] body = new byte[256 + dataLength];
    Arrays.fill(body, (byte) ' ');
    put(body, 0, "SCHBNK01001");
    put(body, 11, type == MediaType.AUDIO ? "AUDRSP01" : video ? "VIDRSP01" : "MEDRSP01");
    put(body, 19, "001SS");
    put(body, 24, "00000000-0000-4000-8000-000000000123");
    put(body, 60, correlation.toString());
    put(body, 96, "20260908090000000");
    put(body, 113, "b".repeat(64));
    put(body, 177, "0256");
    put(body, 181, String.format(Locale.ROOT, "%06d", dataLength));
    put(body, 187, "000000000000");
    put(body, 199, String.format(Locale.ROOT, "%09d", body.length));
    put(body, 208, code);
    put(body, 256 + 832, "000000000000");
    if (code.equals(SUCCESS) || code.equals(IDEMPOTENT)) {
      put(body, 256, id);
      put(body, 256 + 64, path(type));
      put(body, 256 + 576, video ? VIDEO_NAME : MUSIC_NAME);
      put(body, 256 + 832, "000000000003");
      put(body, 256 + 844, SYNTHETIC_HASH);
      put(body, 256 + 908, video ? VIDEO_MIME : OGG_MIME);
      put(body, 256 + 972, mode == ContentDisposition.INLINE ? "I" : "A");
      if (video) {
        put(body, 256 + 1024, "Opening");
        put(body, 256 + 1280, "OPENING");
        put(body, 256 + 1296, "opening.mp4");
      }
    }
    return body;
  }

  private static String path(MediaType type) {
    return switch (type) {
      case AUDIO -> "scenario/a.ogg";
      case VIDEO -> "video/a.mp4";
      case MUSIC -> "music/a.ogg";
    };
  }

  private static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }
}
