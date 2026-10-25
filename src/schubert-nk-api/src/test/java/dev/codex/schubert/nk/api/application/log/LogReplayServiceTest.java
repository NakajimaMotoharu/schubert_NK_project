package dev.codex.schubert.nk.api.application.log;

import static dev.codex.schubert.nk.api.application.log.LogVectors.ADMIN;
import static dev.codex.schubert.nk.api.application.log.LogVectors.COMPLETED;
import static dev.codex.schubert.nk.api.application.log.LogVectors.LATER;
import static dev.codex.schubert.nk.api.application.log.LogVectors.MESSAGE;
import static dev.codex.schubert.nk.api.application.log.LogVectors.NOW;
import static dev.codex.schubert.nk.api.application.log.LogVectors.REPLY;
import static dev.codex.schubert.nk.api.application.log.LogVectors.RESPONSE;
import static dev.codex.schubert.nk.api.application.log.LogVectors.decrypt;
import static dev.codex.schubert.nk.api.application.log.LogVectors.emptyFilters;
import static dev.codex.schubert.nk.api.application.log.LogVectors.encrypt;
import static dev.codex.schubert.nk.api.application.log.LogVectors.page;
import static dev.codex.schubert.nk.api.application.log.LogVectors.put;
import static dev.codex.schubert.nk.api.application.log.LogVectors.request;
import static dev.codex.schubert.nk.api.application.log.LogVectors.time;
import static dev.codex.schubert.nk.api.application.log.LogVectors.wire;
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
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** Independent UI235 full wire and SS352 authenticated encryption, PT-ADM-064..066. */
class LogReplayServiceTest {
  @Test
  void adm064FrozenRecordsAndCapacityRebuildExactReplies() throws Exception {
    try (var keys = keys()) {
      var service = new LogReplayService(keys);
      for (int count : new int[] {0, 1, 100})
        for (boolean optional : List.of(false, true)) {
          var request = request(1);
          var response = page(count, count, 1, optional);
          var completion = service.captureSuccess(request, ADMIN, response, RESPONSE, COMPLETED);
          assertEquals(InboxCompletionState.COMPLETED, completion.state());
          assertEquals(InboxResultReference.none(), completion.resultReference());
          assertEquals("LGSRSP01", completion.responseLayoutId());
          assertEquals("001", completion.responseVersion());
          assertEquals(COMPLETED.truncatedTo(ChronoUnit.MICROS), completion.completedAt());
          assertArrayEquals(
              wire(MESSAGE, RESPONSE, COMPLETED, "0000", count, count, 1, optional),
              decrypt(completion, MESSAGE, 1));
          var snapshot = service.read(request, ADMIN, completion);
          assertEquals("LogSnapshot[REDACTED]", snapshot.toString());
          for (boolean replay : List.of(false, true))
            assertArrayEquals(
                wire(MESSAGE, REPLY, LATER, replay ? "0200" : "0000", count, count, 1, optional),
                service.reply(snapshot, request, ADMIN, REPLY, LATER, replay));
        }
      var last = request(999999);
      var saved = service.captureSuccess(last, ADMIN, page(1, 101, 2, true), RESPONSE, COMPLETED);
      assertArrayEquals(
          wire(MESSAGE, REPLY, LATER, "0200", 1, 101, 2, true),
          service.reply(service.read(last, ADMIN, saved), last, ADMIN, REPLY, LATER, true));
      var request = request(1);
      var capacity =
          service.captureFailure(request, ADMIN, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED);
      assertEquals(InboxCompletionState.ERROR, capacity.state());
      assertEquals(InboxResultReference.none(), capacity.resultReference());
      assertArrayEquals(
          wire(MESSAGE, RESPONSE, COMPLETED, "9001", 0, 0, 1, false),
          decrypt(capacity, MESSAGE, 1));
      for (boolean replay : List.of(false, true))
        assertArrayEquals(
            wire(MESSAGE, REPLY, LATER, "9001", 0, 0, 1, false),
            service.reply(
                service.read(request, ADMIN, capacity), request, ADMIN, REPLY, LATER, replay));
      for (var code : ResultCode.values()) {
        if (List.of(
                ResultCode.SESSION_INVALID,
                ResultCode.FORBIDDEN,
                ResultCode.TEMPORARY_FAILURE,
                ResultCode.RESOURCE_LIMIT)
            .contains(code))
          assertArrayEquals(
              wire(MESSAGE, REPLY, LATER, code.wireValue(), 0, 0, 1, false),
              service.failure(request, code, REPLY, LATER));
        else deny(() -> service.failure(request, code, REPLY, LATER));
        if (code != ResultCode.RESOURCE_LIMIT)
          deny(() -> service.captureFailure(request, ADMIN, code, RESPONSE, COMPLETED));
      }
    }
  }

  @Test
  void adm065CorruptSnapshotsAndPublicBoundariesFailClosed() throws Exception {
    var keys = keys();
    try {
      var service = new LogReplayService(keys);
      var request = request(1);
      var response = page(1, 1, 1, true);
      var saved = service.captureSuccess(request, ADMIN, response, RESPONSE, COMPLETED);
      var snapshot = service.read(request, ADMIN, saved);
      assertThrows(NullPointerException.class, () -> new LogReplayService(null));
      for (Executable operation :
          List.<Executable>of(
              () -> service.captureSuccess(null, ADMIN, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, null, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ADMIN, null, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, ADMIN, response, null, COMPLETED),
              () -> service.captureSuccess(request, ADMIN, response, RESPONSE, null),
              () ->
                  service.captureFailure(
                      null, ADMIN, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(
                      request, null, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, ADMIN, null, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(
                      request, ADMIN, ResultCode.RESOURCE_LIMIT, null, COMPLETED),
              () ->
                  service.captureFailure(request, ADMIN, ResultCode.RESOURCE_LIMIT, RESPONSE, null),
              () -> service.read(null, ADMIN, saved),
              () -> service.read(request, null, saved),
              () -> service.read(request, ADMIN, null),
              () -> service.reply(null, request, ADMIN, REPLY, LATER, true),
              () -> service.reply(snapshot, null, ADMIN, REPLY, LATER, true),
              () -> service.reply(snapshot, request, null, REPLY, LATER, true),
              () -> service.reply(snapshot, request, ADMIN, null, LATER, true),
              () -> service.reply(snapshot, request, ADMIN, REPLY, null, true),
              () -> service.failure(null, ResultCode.RESOURCE_LIMIT, REPLY, LATER),
              () -> service.failure(request, null, REPLY, LATER),
              () -> service.failure(request, ResultCode.RESOURCE_LIMIT, null, LATER),
              () -> service.failure(request, ResultCode.RESOURCE_LIMIT, REPLY, null)))
        assertThrows(NullPointerException.class, operation);
      var user = new AuthenticatedActor(1, "user", Role.USER);
      var other = new AuthenticatedActor(2, "admin2", Role.ADMIN);
      deny(() -> service.captureSuccess(request, user, response, RESPONSE, COMPLETED));
      deny(
          () ->
              service.captureFailure(
                  request, user, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED));
      deny(() -> service.read(request, user, saved));
      deny(() -> service.read(request, other, saved));
      deny(() -> service.reply(snapshot, request, user, REPLY, LATER, true));
      deny(() -> service.reply(snapshot, request, other, REPLY, LATER, true));
      deny(() -> service.reply(snapshot, request(1), ADMIN, REPLY, LATER, true));
      deny(
          () -> service.captureSuccess(request, ADMIN, page(1, 101, 2, true), RESPONSE, COMPLETED));
      byte[] valid = wire(MESSAGE, RESPONSE, COMPLETED, "0000", 1, 1, 1, true);
      for (var edit :
          Map.ofEntries(
                  Map.entry(0, "BADMAGIC"),
                  Map.entry(11, "USRRSP01"),
                  Map.entry(22, "Q"),
                  Map.entry(23, "A"),
                  Map.entry(60, new UUID(200, 2).toString()),
                  Map.entry(96, time(NOW)),
                  Map.entry(193, "000002"),
                  Map.entry(208, "0200"),
                  Map.entry(212, "x"),
                  Map.entry(256, "000002"),
                  Map.entry(262, "099"),
                  Map.entry(265, "000000000"),
                  Map.entry(274, "000002"),
                  Map.entry(289, "000000002"),
                  Map.entry(304, "000000000000"),
                  Map.entry(304 + 45, "TRACE"),
                  Map.entry(304 + 2082, "x"))
              .entrySet()) {
        byte[] body = valid.clone();
        put(body, edit.getKey(), edit.getValue());
        assertFalse(Arrays.equals(valid, body));
        deny(
            () ->
                service.read(
                    request, ADMIN, stored(body, InboxCompletionState.COMPLETED, COMPLETED)));
      }
      for (byte[] body :
          List.of(Arrays.copyOf(valid, valid.length - 1), Arrays.copyOf(valid, valid.length + 1)))
        deny(
            () ->
                service.read(
                    request, ADMIN, stored(body, InboxCompletionState.COMPLETED, COMPLETED)));
      for (var state : InboxCompletionState.values())
        if (state != InboxCompletionState.COMPLETED)
          deny(() -> service.read(request, ADMIN, stored(valid, state, COMPLETED)));
      for (String code : List.of("0102", "0103", "0104", "9000", "0200")) {
        byte[] body = wire(MESSAGE, RESPONSE, COMPLETED, code, 0, 0, 1, false);
        deny(
            () ->
                service.read(request, ADMIN, stored(body, InboxCompletionState.ERROR, COMPLETED)));
      }
      byte[] error = wire(MESSAGE, RESPONSE, COMPLETED, "9001", 0, 0, 1, false);
      deny(
          () ->
              service.read(
                  request, ADMIN, stored(error, InboxCompletionState.COMPLETED, COMPLETED)));
      error[256] = '1';
      deny(
          () -> service.read(request, ADMIN, stored(error, InboxCompletionState.ERROR, COMPLETED)));
      deny(() -> service.read(request, ADMIN, stored(valid, InboxCompletionState.COMPLETED, NOW)));
      for (String layout : List.of("USRRSP01", "LGSRSP01"))
        for (String version : List.of("001", "002"))
          if (!layout.equals("LGSRSP01") || !version.equals("001"))
            deny(
                () ->
                    service.read(
                        request,
                        ADMIN,
                        new InboxCompletion(
                            saved.state(),
                            saved.resultReference(),
                            layout,
                            version,
                            saved.responseSnapshot(),
                            saved.completedAt())));
      deny(
          () ->
              service.read(
                  request,
                  ADMIN,
                  new InboxCompletion(
                      saved.state(),
                      InboxResultReference.numeric(InboxResultReferenceType.USER, 1),
                      saved.responseLayoutId(),
                      "001",
                      saved.responseSnapshot(),
                      saved.completedAt())));
      deny(
          () ->
              service.read(
                  request,
                  ADMIN,
                  new InboxCompletion(
                      saved.state(),
                      saved.resultReference(),
                      saved.responseLayoutId(),
                      "001",
                      Optional.empty(),
                      saved.completedAt())));
      byte[] corrupt = saved.responseSnapshot().orElseThrow().ciphertext();
      corrupt[corrupt.length - 1] ^= 1;
      for (var encrypted :
          List.of(
              new EncryptedResponseSnapshot("test", corrupt),
              new EncryptedResponseSnapshot(
                  "gone", saved.responseSnapshot().orElseThrow().ciphertext()),
              encrypt(valid, new UUID(200, 2), 1, "LGSRSP01"),
              encrypt(valid, MESSAGE, 2, "LGSRSP01"),
              encrypt(valid, MESSAGE, 1, "USRRSP01")))
        deny(
            () ->
                service.read(
                    request,
                    ADMIN,
                    new InboxCompletion(
                        saved.state(),
                        saved.resultReference(),
                        saved.responseLayoutId(),
                        "001",
                        Optional.of(encrypted),
                        saved.completedAt())));
      var historical = Instant.parse("1800-01-01T00:00:00Z");
      assertArrayEquals(
          wire(MESSAGE, REPLY, historical, "0200", 1, 1, 1, true),
          service.reply(snapshot, request, ADMIN, REPLY, historical, true));
      for (var invalid :
          List.of(
              Instant.parse("-0001-01-01T00:00:00Z"), Instant.parse("+10000-01-01T00:00:00Z"))) {
        deny(() -> service.captureSuccess(request, ADMIN, response, RESPONSE, invalid));
        deny(
            () ->
                service.captureFailure(
                    request, ADMIN, ResultCode.RESOURCE_LIMIT, RESPONSE, invalid));
        deny(() -> service.reply(snapshot, request, ADMIN, REPLY, invalid, true));
        deny(() -> service.failure(request, ResultCode.RESOURCE_LIMIT, REPLY, invalid));
      }
      keys.close();
      deny(() -> service.captureSuccess(request, ADMIN, response, RESPONSE, COMPLETED));
      deny(
          () ->
              service.captureFailure(
                  request, ADMIN, ResultCode.RESOURCE_LIMIT, RESPONSE, COMPLETED));
      deny(() -> service.read(request, ADMIN, saved));
      assertArrayEquals(
          wire(MESSAGE, REPLY, LATER, "0200", 1, 1, 1, true),
          service.reply(snapshot, request, ADMIN, REPLY, LATER, true));
    } finally {
      keys.close();
    }
  }

  @Test
  void adm066ConcurrentSnapshotsDoNotShareBodiesOrHeaders() throws Exception {
    try (var keys = keys();
        var pool = Executors.newFixedThreadPool(10)) {
      var service = new LogReplayService(keys);
      var results = new ArrayList<Future<Void>>();
      for (int i = 1; i <= 100; i++) {
        final int n = i;
        results.add(
            pool.submit(
                () -> {
                  var id = new UUID(200, n);
                  var responseId = new UUID(201, n);
                  var replyId = new UUID(202, n);
                  var request = request(emptyFilters(), 1, id);
                  var actor = new AuthenticatedActor(n, "admin" + n, Role.ADMIN);
                  var response = page(n, n, 1, n % 2 == 0);
                  var saved =
                      service.captureSuccess(request, actor, response, responseId, COMPLETED);
                  assertArrayEquals(
                      wire(id, responseId, COMPLETED, "0000", n, n, 1, n % 2 == 0),
                      decrypt(saved, id, n));
                  assertArrayEquals(
                      wire(id, replyId, LATER, "0200", n, n, 1, n % 2 == 0),
                      service.reply(
                          service.read(request, actor, saved),
                          request,
                          actor,
                          replyId,
                          LATER,
                          true));
                  return null;
                }));
      }
      for (var result : results) result.get(20, TimeUnit.SECONDS);
    }
  }

  static ResponseSnapshotCodec keys() {
    return new ResponseSnapshotCodec("test", new byte[32], null, null);
  }

  static InboxCompletion stored(byte[] body, InboxCompletionState state, Instant time)
      throws Exception {
    return new InboxCompletion(
        state,
        InboxResultReference.none(),
        "LGSRSP01",
        "001",
        Optional.of(encrypt(body, MESSAGE, 1, "LGSRSP01")),
        time.truncatedTo(ChronoUnit.MICROS));
  }

  static void deny(Executable operation) {
    var e = assertThrows(TemporaryInfrastructureException.class, operation);
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
    assertEquals("request transaction is unavailable", e.getMessage());
  }
}
