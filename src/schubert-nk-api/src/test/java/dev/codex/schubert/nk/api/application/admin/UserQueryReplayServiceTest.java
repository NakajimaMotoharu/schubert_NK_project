package dev.codex.schubert.nk.api.application.admin;

import static dev.codex.schubert.nk.api.application.admin.UserMutationRequestTest.put;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.ADMIN;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.MESSAGE;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.NOW;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.detail;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.detailResponse;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.list;
import static dev.codex.schubert.nk.api.application.admin.UserQueryRequestTest.page;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** Independent UI232/236 wire vectors and JCE envelope; PT-ADM-044..047. */
class UserQueryReplayServiceTest {
  private static final String SEARCH_LAYOUT = "USRREQ01";
  private static final String SUCCESS_CODE = "0000";
  private static final String REPLAY_CODE = "0200";
  private static final String DETAIL_LAYOUT = "UDTREQ01";
  private static final String LAYOUT_VERSION = "001";

  static final UUID RESPONSE = new UUID(101, 1);
  static final UUID REPLY = new UUID(101, 2);
  static final Instant COMPLETED = NOW.plusNanos(123456789);
  static final Instant LATER = NOW.plusSeconds(3600);

  @Test
  void adm044FrozenListAndDetailRebuildExactFreshReplies() throws Exception {
    try (var keys = keys()) {
      var service = new UserQueryReplayService(keys);
      for (int count : new int[] {0, 1, 50}) {
        var request = list(null, null, null, 999999, MESSAGE);
        var values = page(count, count, 1, 50);
        var saved = service.captureSuccess(request, ADMIN, values, RESPONSE, COMPLETED);
        verify(
            service,
            request,
            saved,
            ADMIN,
            wire(
                SEARCH_LAYOUT,
                MESSAGE,
                RESPONSE,
                COMPLETED,
                SUCCESS_CODE,
                count,
                count,
                1,
                0,
                false));
        for (boolean replay : List.of(false, true))
          assertArrayEquals(
              wire(
                  SEARCH_LAYOUT,
                  MESSAGE,
                  REPLY,
                  LATER,
                  replay ? REPLAY_CODE : SUCCESS_CODE,
                  count,
                  count,
                  1,
                  0,
                  false),
              service.reply(
                  service.read(request, ADMIN, saved), request, ADMIN, REPLY, LATER, replay));
      }
      for (long target : new long[] {1, 999999999999L})
        for (boolean optional : List.of(false, true)) {
          var request = detail(target, MESSAGE);
          var saved =
              service.captureSuccess(
                  request, ADMIN, detailResponse(target, optional), RESPONSE, COMPLETED);
          verify(
              service,
              request,
              saved,
              ADMIN,
              wire(
                  DETAIL_LAYOUT,
                  MESSAGE,
                  RESPONSE,
                  COMPLETED,
                  SUCCESS_CODE,
                  0,
                  0,
                  0,
                  target,
                  optional));
          for (boolean replay : List.of(false, true))
            assertArrayEquals(
                wire(
                    DETAIL_LAYOUT,
                    MESSAGE,
                    REPLY,
                    LATER,
                    replay ? REPLAY_CODE : SUCCESS_CODE,
                    0,
                    0,
                    0,
                    target,
                    optional),
                service.reply(
                    service.read(request, ADMIN, saved), request, ADMIN, REPLY, LATER, replay));
        }
      // A previously captured page is immutable even when another query captures a different count.
      var request = list(null, null, null, 1, MESSAGE);
      var old = service.captureSuccess(request, ADMIN, page(1, 1, 1, 50), RESPONSE, COMPLETED);
      service.captureSuccess(request, ADMIN, page(50, 50, 1, 50), RESPONSE, COMPLETED);
      assertArrayEquals(
          wire(SEARCH_LAYOUT, MESSAGE, REPLY, LATER, REPLAY_CODE, 1, 1, 1, 0, false),
          service.reply(service.read(request, ADMIN, old), request, ADMIN, REPLY, LATER, true));
    }
  }

  @Test
  void adm045ErrorsAndAuthenticatedCorruptSnapshotsFailClosed() throws Exception {
    try (var keys = keys()) {
      var service = new UserQueryReplayService(keys);
      for (boolean detail : List.of(false, true)) {
        var request = detail ? detail(3, MESSAGE) : list(null, null, null, 1, MESSAGE);
        for (var code : ResultCode.values()) {
          boolean definite =
              detail ? code == ResultCode.NOT_FOUND : code == ResultCode.RESOURCE_LIMIT;
          if (definite) {
            var saved = service.captureFailure(request, ADMIN, code, RESPONSE, COMPLETED);
            assertEquals(InboxCompletionState.ERROR, saved.state());
            assertEquals(InboxResultReference.none(), saved.resultReference());
            assertArrayEquals(
                wire(
                    detail ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                    MESSAGE,
                    RESPONSE,
                    COMPLETED,
                    oracleResultCode(code),
                    0,
                    0,
                    0,
                    0,
                    false),
                UserMutationReplayServiceTest.decrypt(saved, MESSAGE, 1));
            for (boolean replay : List.of(false, true))
              assertArrayEquals(
                  wire(
                      detail ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                      MESSAGE,
                      REPLY,
                      LATER,
                      oracleResultCode(code),
                      0,
                      0,
                      0,
                      0,
                      false),
                  service.reply(
                      service.read(request, ADMIN, saved), request, ADMIN, REPLY, LATER, replay));
          } else deny(() -> service.captureFailure(request, ADMIN, code, RESPONSE, COMPLETED));
          if (definite
              || List.of(
                      ResultCode.SESSION_INVALID,
                      ResultCode.FORBIDDEN,
                      ResultCode.TEMPORARY_FAILURE)
                  .contains(code))
            assertArrayEquals(
                wire(
                    detail ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                    MESSAGE,
                    REPLY,
                    LATER,
                    oracleResultCode(code),
                    0,
                    0,
                    0,
                    0,
                    false),
                service.failure(request, code, REPLY, LATER));
          else deny(() -> service.failure(request, code, REPLY, LATER));
          if (!definite && code != ResultCode.SUCCESS) {
            byte[] body =
                wire(
                    detail ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                    MESSAGE,
                    RESPONSE,
                    COMPLETED,
                    oracleResultCode(code),
                    0,
                    0,
                    1,
                    3,
                    false);
            deny(
                () ->
                    service.read(
                        request,
                        ADMIN,
                        stored(request, body, InboxCompletionState.ERROR, COMPLETED)));
          }
        }
        byte[] valid =
            wire(
                detail ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                MESSAGE,
                RESPONSE,
                COMPLETED,
                SUCCESS_CODE,
                detail ? 0 : 1,
                1,
                1,
                3,
                false);
        var saved = stored(request, valid, InboxCompletionState.COMPLETED, COMPLETED);
        service.read(request, ADMIN, saved);
        for (var bad :
            List.of(
                new InboxCompletion(
                    saved.state(),
                    saved.resultReference(),
                    detail ? "USRRSP01" : "UDTRSP01",
                    LAYOUT_VERSION,
                    saved.responseSnapshot(),
                    saved.completedAt()),
                new InboxCompletion(
                    saved.state(),
                    saved.resultReference(),
                    saved.responseLayoutId(),
                    "002",
                    saved.responseSnapshot(),
                    saved.completedAt()),
                new InboxCompletion(
                    saved.state(),
                    InboxResultReference.numeric(InboxResultReferenceType.USER, 3),
                    saved.responseLayoutId(),
                    LAYOUT_VERSION,
                    saved.responseSnapshot(),
                    saved.completedAt()),
                new InboxCompletion(
                    saved.state(),
                    saved.resultReference(),
                    saved.responseLayoutId(),
                    LAYOUT_VERSION,
                    Optional.empty(),
                    saved.completedAt()),
                new InboxCompletion(
                    InboxCompletionState.ERROR,
                    saved.resultReference(),
                    saved.responseLayoutId(),
                    LAYOUT_VERSION,
                    saved.responseSnapshot(),
                    saved.completedAt()),
                new InboxCompletion(
                    saved.state(),
                    saved.resultReference(),
                    saved.responseLayoutId(),
                    LAYOUT_VERSION,
                    saved.responseSnapshot(),
                    saved.completedAt().plusMillis(1))))
          deny(() -> service.read(request, ADMIN, bad));
        var deniedCode = detail ? ResultCode.NOT_FOUND : ResultCode.RESOURCE_LIMIT;
        var denied = service.captureFailure(request, ADMIN, deniedCode, RESPONSE, COMPLETED);
        deny(
            () ->
                service.read(
                    request,
                    ADMIN,
                    new InboxCompletion(
                        InboxCompletionState.COMPLETED,
                        denied.resultReference(),
                        denied.responseLayoutId(),
                        LAYOUT_VERSION,
                        denied.responseSnapshot(),
                        denied.completedAt())));
        for (var edit :
            Map.of(
                    0,
                    "BROKEN00",
                    11,
                    detail ? "USRRSP01" : "UDTRSP01",
                    19,
                    "002",
                    22,
                    "Q",
                    60,
                    new UUID(100, 2).toString(),
                    181,
                    "000001",
                    187,
                    "000001",
                    193,
                    "000002",
                    199,
                    "000000001",
                    208,
                    REPLAY_CODE)
                .entrySet()) {
          byte[] body = valid.clone();
          put(body, edit.getKey(), edit.getValue());
          assertFalse(Arrays.equals(valid, body), "negative header must actually differ");
          deny(
              () ->
                  service.read(
                      request,
                      ADMIN,
                      stored(request, body, InboxCompletionState.COMPLETED, COMPLETED)));
        }
        byte[] wrongTarget = valid.clone();
        put(wrongTarget, 256, detail ? "000000000004" : "000002");
        deny(
            () ->
                service.read(
                    request,
                    ADMIN,
                    stored(request, wrongTarget, InboxCompletionState.COMPLETED, COMPLETED)));
        for (byte[] wrongLength :
            List.of(Arrays.copyOf(valid, valid.length - 1), Arrays.copyOf(valid, valid.length + 1)))
          deny(
              () ->
                  service.read(
                      request,
                      ADMIN,
                      stored(request, wrongLength, InboxCompletionState.COMPLETED, COMPLETED)));
        if (!detail) {
          for (var edit :
              Map.of(
                      262,
                      "049",
                      265,
                      "000000000",
                      274,
                      "000002",
                      289,
                      "000000002",
                      304,
                      "000000000000")
                  .entrySet()) {
            byte[] body = valid.clone();
            put(body, edit.getKey(), edit.getValue());
            deny(
                () ->
                    service.read(
                        request,
                        ADMIN,
                        stored(request, body, InboxCompletionState.COMPLETED, COMPLETED)));
          }
        }
        byte[] corrupted = saved.responseSnapshot().orElseThrow().ciphertext();
        corrupted[corrupted.length - 1] ^= 1;
        for (var encrypted :
            List.of(
                new EncryptedResponseSnapshot("test", corrupted),
                new EncryptedResponseSnapshot(
                    "gone", saved.responseSnapshot().orElseThrow().ciphertext()),
                UserMutationReplayServiceTest.encrypt(
                    valid, new UUID(100, 2), 1, request.responseLayoutId().value()),
                UserMutationReplayServiceTest.encrypt(
                    valid, MESSAGE, 2, request.responseLayoutId().value()))) {
          deny(
              () ->
                  service.read(
                      request,
                      ADMIN,
                      new InboxCompletion(
                          saved.state(),
                          saved.resultReference(),
                          saved.responseLayoutId(),
                          LAYOUT_VERSION,
                          Optional.of(encrypted),
                          saved.completedAt())));
        }
      }
    }
  }

  @Test
  void adm046NullScopeRoleAndKeyLifecycleProtectReplies() throws Exception {
    var keys = keys();
    try {
      var service = new UserQueryReplayService(keys);
      var request = detail(3, MESSAGE);
      var response = detailResponse(3, false);
      var saved = service.captureSuccess(request, ADMIN, response, RESPONSE, COMPLETED);
      var snapshot = service.read(request, ADMIN, saved);
      assertThrows(NullPointerException.class, () -> new UserQueryReplayService(null));
      for (Executable operation :
          List.<Executable>of(
              () -> service.captureSuccess(null, ADMIN, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, null, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ADMIN, null, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ADMIN, response, null, COMPLETED),
              () -> service.captureSuccess(request, ADMIN, response, RESPONSE, null),
              () -> service.captureFailure(null, ADMIN, ResultCode.NOT_FOUND, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(request, null, ResultCode.NOT_FOUND, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, ADMIN, null, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, ADMIN, ResultCode.NOT_FOUND, null, COMPLETED),
              () -> service.captureFailure(request, ADMIN, ResultCode.NOT_FOUND, RESPONSE, null),
              () -> service.read(null, ADMIN, saved),
              () -> service.read(request, null, saved),
              () -> service.read(request, ADMIN, null),
              () -> service.reply(null, request, ADMIN, REPLY, LATER, true),
              () -> service.reply(snapshot, null, ADMIN, REPLY, LATER, true),
              () -> service.reply(snapshot, request, null, REPLY, LATER, true),
              () -> service.reply(snapshot, request, ADMIN, null, LATER, true),
              () -> service.reply(snapshot, request, ADMIN, REPLY, null, true),
              () -> service.failure(null, ResultCode.NOT_FOUND, REPLY, LATER),
              () -> service.failure(request, null, REPLY, LATER),
              () -> service.failure(request, ResultCode.NOT_FOUND, null, LATER),
              () -> service.failure(request, ResultCode.NOT_FOUND, REPLY, null)))
        assertThrows(NullPointerException.class, operation);
      var user = new AuthenticatedActor(1, "u1", Role.USER);
      var other = new AuthenticatedActor(2, "u2", Role.ADMIN);
      deny(() -> service.captureSuccess(request, user, response, RESPONSE, COMPLETED));
      deny(() -> service.captureFailure(request, user, ResultCode.NOT_FOUND, RESPONSE, COMPLETED));
      deny(() -> service.read(request, user, saved));
      deny(() -> service.read(request, other, saved));
      deny(() -> service.reply(snapshot, request, user, REPLY, LATER, true));
      deny(() -> service.reply(snapshot, request, other, REPLY, LATER, true));
      deny(() -> service.reply(snapshot, detail(3, MESSAGE), ADMIN, REPLY, LATER, true));
      deny(
          () ->
              service.captureSuccess(
                  request, ADMIN, detailResponse(4, false), RESPONSE, COMPLETED));
      var historical = Instant.parse("1800-01-01T00:00:00Z");
      assertArrayEquals(
          wire(DETAIL_LAYOUT, MESSAGE, REPLY, historical, REPLAY_CODE, 0, 0, 0, 3, false),
          service.reply(snapshot, request, ADMIN, REPLY, historical, true));
      for (Instant invalid :
          List.of(
              Instant.parse("-0001-01-01T00:00:00Z"), Instant.parse("+10000-01-01T00:00:00Z"))) {
        deny(() -> service.captureSuccess(request, ADMIN, response, RESPONSE, invalid));
        deny(() -> service.captureFailure(request, ADMIN, ResultCode.NOT_FOUND, RESPONSE, invalid));
        deny(() -> service.reply(snapshot, request, ADMIN, REPLY, invalid, true));
        deny(() -> service.failure(request, ResultCode.NOT_FOUND, REPLY, invalid));
      }
      keys.close();
      deny(() -> service.captureSuccess(request, ADMIN, response, RESPONSE, COMPLETED));
      deny(() -> service.captureFailure(request, ADMIN, ResultCode.NOT_FOUND, RESPONSE, COMPLETED));
      deny(() -> service.read(request, ADMIN, saved));
      assertArrayEquals(
          wire(DETAIL_LAYOUT, MESSAGE, REPLY, LATER, REPLAY_CODE, 0, 0, 0, 3, false),
          service.reply(snapshot, request, ADMIN, REPLY, LATER, true));
      assertEquals("UserQuerySnapshot[REDACTED]", snapshot.toString());
    } finally {
      keys.close();
    }
  }

  @Test
  void adm047ConcurrentSnapshotsNeverShareQueryResults() throws Exception {
    try (var keys = keys();
        var pool = Executors.newFixedThreadPool(10)) {
      var service = new UserQueryReplayService(keys);
      var results = new ArrayList<Future<Void>>();
      for (int i = 1; i <= 100; i++) {
        int n = i;
        results.add(
            pool.submit(
                () -> {
                  var actor = new AuthenticatedActor(n, "u" + n, Role.ADMIN);
                  var request =
                      n % 2 == 0
                          ? detail(n, new UUID(100, n))
                          : list("u", null, null, 1, new UUID(100, n));
                  int count = n % 2 == 0 ? 0 : n % 51;
                  var values = n % 2 == 0 ? detailResponse(n, true) : page(count, count, 1, 50);
                  UUID responseId = new UUID(101, n);
                  UUID replyId = new UUID(102, n);
                  var saved = service.captureSuccess(request, actor, values, responseId, COMPLETED);
                  var snapshot = service.read(request, actor, saved);
                  assertArrayEquals(
                      wire(
                          n % 2 == 0 ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                          new UUID(100, n),
                          responseId,
                          COMPLETED,
                          SUCCESS_CODE,
                          count,
                          count,
                          1,
                          n,
                          true),
                      UserMutationReplayServiceTest.decrypt(
                          saved, request.header().messageId(), n));
                  assertArrayEquals(
                      wire(
                          n % 2 == 0 ? DETAIL_LAYOUT : SEARCH_LAYOUT,
                          new UUID(100, n),
                          replyId,
                          LATER,
                          REPLAY_CODE,
                          count,
                          count,
                          1,
                          n,
                          true),
                      service.reply(snapshot, request, actor, replyId, LATER, true));
                  return null;
                }));
      }
      for (var result : results) result.get(20, TimeUnit.SECONDS);
    }
  }

  static ResponseSnapshotCodec keys() {
    return new ResponseSnapshotCodec("test", new byte[32], null, null);
  }

  static void deny(Executable action) {
    var e = assertThrows(TemporaryInfrastructureException.class, action);
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
    assertEquals("request transaction is unavailable", e.getMessage());
  }

  static InboxCompletion stored(
      UserQueryRequest request, byte[] body, InboxCompletionState state, Instant time)
      throws Exception {
    return new InboxCompletion(
        state,
        InboxResultReference.none(),
        request.responseLayoutId().value(),
        LAYOUT_VERSION,
        Optional.of(
            UserMutationReplayServiceTest.encrypt(
                body, request.header().messageId(), 1, request.responseLayoutId().value())),
        time.truncatedTo(ChronoUnit.MICROS));
  }

  static void verify(
      UserQueryReplayService service,
      UserQueryRequest request,
      InboxCompletion saved,
      AuthenticatedActor actor,
      byte[] expected)
      throws Exception {
    assertEquals(InboxCompletionState.COMPLETED, saved.state());
    assertEquals(InboxResultReference.none(), saved.resultReference());
    assertEquals(request.responseLayoutId().value(), saved.responseLayoutId());
    assertEquals(LAYOUT_VERSION, saved.responseVersion());
    assertEquals(COMPLETED.truncatedTo(ChronoUnit.MICROS), saved.completedAt());
    assertArrayEquals(
        expected,
        UserMutationReplayServiceTest.decrypt(saved, request.header().messageId(), actor.userId()));
    assertEquals("UserQuerySnapshot[REDACTED]", service.read(request, actor, saved).toString());
  }

  /** Literal UI236 DATA/RECORD offsets, no production codec or field catalog used for expected. */
  static byte[] wire(
      String layout,
      UUID request,
      UUID response,
      Instant at,
      String code,
      int count,
      long total,
      int page,
      long target,
      boolean optional) {
    return UserQueryWireOracle.wire(
        layout, request, response, at, NOW, code, count, total, page, target, optional);
  }

  static String time(Instant instant) {
    return DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
        .withZone(ZoneId.of("Asia/Tokyo"))
        .format(instant);
  }

  /** UI232 section7 literal oracle; never call Production wireValue. */
  private static String oracleResultCode(ResultCode code) {
    return switch (code) {
      case SUCCESS -> "0000";
      case VALIDATION_ERROR -> "0100";
      case AUTHENTICATION_FAILED -> "0101";
      case SESSION_INVALID -> "0102";
      case FORBIDDEN -> "0103";
      case NOT_FOUND -> "0104";
      case CONFLICT -> "0105";
      case LOCKED -> "0106";
      case NOT_CANCELLABLE -> "0107";
      case IDEMPOTENT_SUCCESS -> "0200";
      case TEMPORARY_FAILURE -> "9000";
      case RESOURCE_LIMIT -> "9001";
    };
  }
}
