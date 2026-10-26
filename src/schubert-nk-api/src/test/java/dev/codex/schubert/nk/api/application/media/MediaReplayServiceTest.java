package dev.codex.schubert.nk.api.application.media;

import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.COMPLETED;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.LAYOUTS;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.NEXT;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.RESPONSE;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.SENT;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.SHA;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.codec;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.completion;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.decrypt;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.maximum;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.rebound;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.request;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.responseData;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.typed;
import static dev.codex.schubert.nk.api.application.media.MediaReplayFixture.wire;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.data;
import static dev.codex.schubert.nk.api.application.media.MediaRequestFixture.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** Independent fixed bytes and AES-AAD; no DB/file/current-auth claim. PT-MED-050..054. */
class MediaReplayServiceTest {
  private static final AuthenticatedActor ACTOR = new AuthenticatedActor(101, "reader", Role.USER);
  private static final AuthenticatedActor OTHER = new AuthenticatedActor(102, "other", Role.ADMIN);

  @Test
  void med050EightSuccessLayoutsPreserveLiteralWireAndEncryptedIdentity() throws Exception {
    try (var codec = codec()) {
      var service = new MediaReplayService(codec);
      for (String prefix : LAYOUTS) {
        for (int count : maximum(prefix) == 0 ? List.of(0) : List.of(0, 1, maximum(prefix))) {
          for (String extension :
              prefix.equals("MED")
                  ? List.of("m4a", "mp3", "ogg", "wav", "flac")
                  : List.of(prefix.equals("VID") ? "mp4" : "ogg")) {
            for (String mode :
                List.of("AUD", "MED").contains(prefix) ? List.of("I", "A") : List.of("I")) {
              var request = request(prefix, mode);
              var response = typed(prefix, count, extension, mode);
              var completion =
                  service.captureSuccess(request, ACTOR, response, RESPONSE, COMPLETED);
              assertEquals(InboxCompletionState.COMPLETED, completion.state());
              assertEquals(InboxResultReference.none(), completion.resultReference());
              assertEquals(COMPLETED.truncatedTo(ChronoUnit.MICROS), completion.completedAt());
              assertArrayEquals(
                  wire(
                      prefix,
                      request.header().messageId(),
                      RESPONSE,
                      "20260908090001123",
                      "b".repeat(64),
                      "0000",
                      count,
                      extension,
                      mode),
                  decrypt(request, completion.responseSnapshot().orElseThrow()));
              var saved = service.read(request, ACTOR, completion);
              assertEquals(ResultCode.SUCCESS, saved.resultCode());
              assertEquals(
                  List.of("AUD", "VID", "MED").contains(prefix), saved.descriptor().isPresent());
              assertEquals("MediaSnapshot[REDACTED]", saved.toString());
              if (saved.descriptor().isPresent()) {
                assertEquals(3, saved.descriptor().orElseThrow().byteLength());
                assertEquals(SHA, saved.descriptor().orElseThrow().sha256());
              }
              for (boolean replay : List.of(false, true))
                assertArrayEquals(
                    wire(
                        prefix,
                        request.header().messageId(),
                        NEXT,
                        "20260908090002789",
                        "b".repeat(64),
                        replay ? "0200" : "0000",
                        count,
                        extension,
                        mode),
                    service.reply(saved, request, ACTOR, NEXT, SENT, replay));
              byte[] currentData = data(prefix + "REQ01");
              if (prefix.equals("AUD")) put(currentData, 12, mode);
              if (prefix.equals("MED")) put(currentData, 64, mode);
              var current = rebound(request, currentData, "d".repeat(64));
              assertArrayEquals(
                  wire(
                      prefix,
                      current.header().messageId(),
                      NEXT,
                      "20260908090002789",
                      "d".repeat(64),
                      "0200",
                      count,
                      extension,
                      mode),
                  service.reply(saved, current, ACTOR, NEXT, SENT, true));
            }
          }
        }
      }
    }
  }

  @Test
  void med051DefiniteErrorsKeepCodesAndNeverInventDescriptors() throws Exception {
    try (var codec = codec()) {
      var service = new MediaReplayService(codec);
      for (String prefix : LAYOUTS) {
        var request = request(prefix, "A");
        for (ResultCode code : ResultCode.values()) {
          boolean persistent =
              code == ResultCode.RESOURCE_LIMIT
                  || (code == ResultCode.NOT_FOUND
                      && List.of("AUD", "VID", "MED").contains(prefix));
          if (persistent) {
            var completion = service.captureFailure(request, ACTOR, code, RESPONSE, COMPLETED);
            assertEquals(InboxCompletionState.ERROR, completion.state());
            assertEquals(InboxResultReference.none(), completion.resultReference());
            String literal = code == ResultCode.RESOURCE_LIMIT ? "9001" : "0104";
            assertArrayEquals(
                wire(
                    prefix,
                    request.header().messageId(),
                    RESPONSE,
                    "20260908090001123",
                    "b".repeat(64),
                    literal,
                    0,
                    "ogg",
                    "A"),
                decrypt(request, completion.responseSnapshot().orElseThrow()));
            var saved = service.read(request, ACTOR, completion);
            assertEquals(code, saved.resultCode());
            assertTrue(saved.descriptor().isEmpty());
            if (prefix.equals("ANM")) {
              for (String nonFiller : List.of("0", "1")) {
                byte[] bad =
                    wire(
                        prefix,
                        request.header().messageId(),
                        RESPONSE,
                        "20260908090001123",
                        "b".repeat(64),
                        literal,
                        0,
                        "ogg",
                        "A");
                assertEquals(32, bad[262]);
                put(bad, 262, nonFiller);
                var incorrect = completion(request, bad, InboxCompletionState.ERROR);
                reject(() -> service.read(request, ACTOR, incorrect));
              }
            }
            for (boolean replay : List.of(false, true))
              assertArrayEquals(
                  wire(
                      prefix,
                      request.header().messageId(),
                      NEXT,
                      "20260908090002789",
                      "b".repeat(64),
                      literal,
                      0,
                      "ogg",
                      "A"),
                  service.reply(saved, request, ACTOR, NEXT, SENT, replay));
          } else reject(() -> service.captureFailure(request, ACTOR, code, RESPONSE, COMPLETED));
          if (persistent
              || code == ResultCode.SESSION_INVALID
              || code == ResultCode.TEMPORARY_FAILURE) {
            String literal =
                switch (code) {
                  case RESOURCE_LIMIT -> "9001";
                  case NOT_FOUND -> "0104";
                  case SESSION_INVALID -> "0102";
                  default -> "9000";
                };
            assertArrayEquals(
                wire(
                    prefix,
                    request.header().messageId(),
                    NEXT,
                    "20260908090002789",
                    "b".repeat(64),
                    literal,
                    0,
                    "ogg",
                    "A"),
                service.failure(request, code, NEXT, SENT));
          } else reject(() -> service.failure(request, code, NEXT, SENT));
        }
      }
    }
  }

  @Test
  void med052AuthenticatedCorruptionAndRequestMixupsFailClosed() throws Exception {
    try (var codec = codec()) {
      var service = new MediaReplayService(codec);
      for (String prefix : LAYOUTS) {
        String extension = prefix.equals("VID") ? "mp4" : "ogg";
        String mode = prefix.equals("VID") ? "I" : "A";
        var request = request(prefix, mode);
        int count = maximum(prefix) > 0 ? 1 : 0;
        byte[] good =
            wire(
                prefix,
                request.header().messageId(),
                RESPONSE,
                "20260908090001123",
                "b".repeat(64),
                "0000",
                count,
                extension,
                mode);
        var completion = completion(request, good, InboxCompletionState.COMPLETED);
        assertEquals(ResultCode.SUCCESS, service.read(request, ACTOR, completion).resultCode());
        Object[][] mutations = {
          {0, "INVALID!"},
          {8, "002"},
          {11, "LGNRSP01"},
          {19, "002"},
          {22, "Q"},
          {23, "A"},
          {24, "not-a-uuid"},
          {60, NEXT.toString()},
          {96, "20260908090002123"},
          {113, "!"},
          {177, "0255"},
          {181, "999999"},
          {187, "999999"},
          {193, "999999"},
          {199, "000000256"},
          {208, "0200"},
          {212, "X"}
        };
        for (Object[] mutation : mutations) {
          byte[] bad = good.clone();
          put(bad, (int) mutation[0], (String) mutation[1]);
          var corrupted = completion(request, bad, InboxCompletionState.COMPLETED);
          reject(() -> service.read(request, ACTOR, corrupted));
        }
        for (int size : new int[] {0, 255, good.length - 1, good.length + 1}) {
          var bad = completion(request, Arrays.copyOf(good, size), InboxCompletionState.COMPLETED);
          reject(() -> service.read(request, ACTOR, bad));
        }
        byte[] invalid = good.clone();
        invalid[256] = (byte) 0xff;
        var invalidBody = completion(request, invalid, InboxCompletionState.COMPLETED);
        reject(() -> service.read(request, ACTOR, invalidBody));
        var wrongState = completion(request, good, InboxCompletionState.ERROR);
        reject(() -> service.read(request, ACTOR, wrongState));
        byte[] error =
            wire(
                prefix,
                request.header().messageId(),
                RESPONSE,
                "20260908090001123",
                "b".repeat(64),
                "9001",
                0,
                extension,
                mode);
        var errorState = completion(request, error, InboxCompletionState.COMPLETED);
        reject(() -> service.read(request, ACTOR, errorState));
        reject(() -> service.read(request, OTHER, completion));
        reject(() -> service.read(request(prefix, mode), ACTOR, completion));
        var saved = service.read(request, ACTOR, completion);
        reject(() -> service.reply(saved, request, OTHER, NEXT, SENT, true));
        reject(() -> service.reply(saved, request(prefix, mode), ACTOR, NEXT, SENT, true));
        for (var corrupt :
            List.of(
                new InboxCompletion(
                    completion.state(),
                    InboxResultReference.numeric(InboxResultReferenceType.USER, 101),
                    completion.responseLayoutId(),
                    "001",
                    completion.responseSnapshot(),
                    completion.completedAt()),
                new InboxCompletion(
                    completion.state(),
                    completion.resultReference(),
                    "LGNRSP01",
                    "001",
                    completion.responseSnapshot(),
                    completion.completedAt()),
                new InboxCompletion(
                    completion.state(),
                    completion.resultReference(),
                    completion.responseLayoutId(),
                    "002",
                    completion.responseSnapshot(),
                    completion.completedAt()),
                new InboxCompletion(
                    completion.state(),
                    completion.resultReference(),
                    completion.responseLayoutId(),
                    "001",
                    Optional.empty(),
                    completion.completedAt()))) reject(() -> service.read(request, ACTOR, corrupt));
        byte[] ciphertext = completion.responseSnapshot().orElseThrow().ciphertext();
        ciphertext[ciphertext.length - 1] ^= 1;
        for (var encrypted :
            List.of(
                new EncryptedResponseSnapshot("fixture", ciphertext),
                new EncryptedResponseSnapshot(
                    "unknown", completion.responseSnapshot().orElseThrow().ciphertext()))) {
          var corrupt =
              new InboxCompletion(
                  completion.state(),
                  completion.resultReference(),
                  completion.responseLayoutId(),
                  "001",
                  Optional.of(encrypted),
                  completion.completedAt());
          reject(() -> service.read(request, ACTOR, corrupt));
        }
        if (List.of("AUD", "VID", "MED").contains(prefix)) {
          for (Object[] mutation :
              new Object[][] {
                {0, "different"},
                {64, "/escape"},
                {832, "000000000000"},
                {844, "g"},
                {908, "bad/mime"},
                {972, "X"},
                {973, "X"}
              }) {
            byte[] bad = good.clone();
            put(bad, 256 + (int) mutation[0], (String) mutation[1]);
            var corrupt = completion(request, bad, InboxCompletionState.COMPLETED);
            reject(() -> service.read(request, ACTOR, corrupt));
          }
          byte[] changed = data(prefix + "REQ01");
          put(changed, 0, prefix.equals("AUD") ? "000000000701" : "changed");
          var otherId = rebound(request, changed, "b".repeat(64));
          reject(() -> service.read(otherId, ACTOR, completion));
          reject(() -> service.reply(saved, otherId, ACTOR, NEXT, SENT, true));
          if (!prefix.equals("VID")) {
            byte[] changedMode = data(prefix + "REQ01");
            put(changedMode, prefix.equals("AUD") ? 12 : 64, "I");
            var otherMode = rebound(request, changedMode, "b".repeat(64));
            reject(() -> service.read(otherMode, ACTOR, completion));
          }
        } else if (count > 0) {
          byte[] badRecord = good.clone();
          badRecord[256 + responseData(prefix, count, extension, mode, false).length] = (byte) 0xff;
          var corrupt = completion(request, badRecord, InboxCompletionState.COMPLETED);
          reject(() -> service.read(request, ACTOR, corrupt));
        }
      }
    }
  }

  @Test
  void med053NullKeyAndClockBoundariesRemainRedacted() throws Exception {
    assertThrows(NullPointerException.class, () -> new MediaReplayService(null));
    try (var codec = codec()) {
      var service = new MediaReplayService(codec);
      var request = request("MED", "A");
      var response = typed("MED", 0, "ogg", "A");
      var completion = service.captureSuccess(request, ACTOR, response, RESPONSE, COMPLETED);
      var saved = service.read(request, ACTOR, completion);
      for (Executable nullCase :
          List.<Executable>of(
              () -> request.descriptor(null),
              () -> service.captureSuccess(null, ACTOR, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, null, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ACTOR, null, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ACTOR, response, null, COMPLETED),
              () -> service.captureSuccess(request, ACTOR, response, RESPONSE, null),
              () -> service.captureFailure(null, ACTOR, ResultCode.NOT_FOUND, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(request, null, ResultCode.NOT_FOUND, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, ACTOR, null, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, ACTOR, ResultCode.NOT_FOUND, null, COMPLETED),
              () -> service.captureFailure(request, ACTOR, ResultCode.NOT_FOUND, RESPONSE, null),
              () -> service.read(null, ACTOR, completion),
              () -> service.read(request, null, completion),
              () -> service.read(request, ACTOR, null),
              () -> service.reply(null, request, ACTOR, NEXT, SENT, true),
              () -> service.reply(saved, null, ACTOR, NEXT, SENT, true),
              () -> service.reply(saved, request, null, NEXT, SENT, true),
              () -> service.reply(saved, request, ACTOR, null, SENT, true),
              () -> service.reply(saved, request, ACTOR, NEXT, null, true),
              () -> service.failure(null, ResultCode.NOT_FOUND, NEXT, SENT),
              () -> service.failure(request, null, NEXT, SENT),
              () -> service.failure(request, ResultCode.NOT_FOUND, null, SENT),
              () -> service.failure(request, ResultCode.NOT_FOUND, NEXT, null)))
        assertThrows(NullPointerException.class, nullCase);
      reject(
          () ->
              service.captureSuccess(
                  request, ACTOR, typed("ANM", 0, "ogg", "I"), RESPONSE, COMPLETED));
      reject(
          () ->
              service.captureSuccess(
                  request, ACTOR, typed("MED", 0, "ogg", "I"), RESPONSE, COMPLETED));
      for (Instant invalid : List.of(Instant.MIN, Instant.MAX)) {
        reject(() -> service.captureSuccess(request, ACTOR, response, RESPONSE, invalid));
        reject(
            () -> service.captureFailure(request, ACTOR, ResultCode.NOT_FOUND, RESPONSE, invalid));
        reject(() -> service.reply(saved, request, ACTOR, NEXT, invalid, true));
        reject(() -> service.failure(request, ResultCode.NOT_FOUND, NEXT, invalid));
      }
    }
    var closedCodec = codec();
    var closedService = new MediaReplayService(closedCodec);
    var request = request("MED", "A");
    var completion =
        closedService.captureSuccess(
            request, ACTOR, typed("MED", 0, "ogg", "A"), RESPONSE, COMPLETED);
    closedCodec.close();
    reject(() -> closedService.read(request, ACTOR, completion));
    reject(
        () ->
            closedService.captureSuccess(
                request, ACTOR, typed("MED", 0, "ogg", "A"), RESPONSE, COMPLETED));
    reject(
        () ->
            closedService.captureFailure(
                request, ACTOR, ResultCode.NOT_FOUND, RESPONSE, COMPLETED));
  }

  @Test
  void med054ConcurrentSnapshotsRemainImmutableAndRequestBound() throws Exception {
    try (var codec = codec();
        var pool = Executors.newFixedThreadPool(10)) {
      var service = new MediaReplayService(codec);
      List<Callable<Boolean>> tasks = new ArrayList<>();
      for (int i = 0; i < 100; i++)
        tasks.add(
            () -> {
              var request = request("MED", "A");
              var completion =
                  service.captureSuccess(
                      request, ACTOR, typed("MED", 0, "ogg", "A"), RESPONSE, COMPLETED);
              byte[] exposed = completion.responseSnapshot().orElseThrow().ciphertext();
              Arrays.fill(exposed, (byte) 0);
              var saved = service.read(request, ACTOR, completion);
              byte[] expected =
                  wire(
                      "MED",
                      request.header().messageId(),
                      NEXT,
                      "20260908090002789",
                      "b".repeat(64),
                      "0200",
                      0,
                      "ogg",
                      "A");
              byte[] actual = service.reply(saved, request, ACTOR, NEXT, SENT, true);
              assertArrayEquals(expected, actual);
              Arrays.fill(actual, (byte) '!');
              assertArrayEquals(expected, service.reply(saved, request, ACTOR, NEXT, SENT, true));
              reject(() -> service.read(request("MED", "A"), ACTOR, completion));
              return true;
            });
      for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
    }
  }

  private static void reject(Executable action) {
    var failure = assertThrows(TemporaryInfrastructureException.class, action);
    assertEquals("request transaction is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
