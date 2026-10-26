package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.BoundInboxExecution;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxExecution;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** UI232/236 independent wire offsets and SS352 JCE envelope. PG-D-086/PT-ADM-028..032. */
final class UserMutationReplayServiceTest {
  private static final String FIXTURE_CREATE_REQUEST = "UCRREQ01";
  private static final String FIXTURE_STATE_REQUEST = "USTREQ01";
  private static final String FIXTURE_UNLOCK_REQUEST = "ULKREQ01";
  private static final String FIXTURE_SUCCESS_CODE = "0000";
  private static final String FIXTURE_REPLAY_CODE = "0200";
  private static final String FIXTURE_LAYOUT_VERSION = "001";
  private static final String FIXTURE_STATE_RESPONSE = "USTRSP01";
  private static final String FIXTURE_KEY_ID = "test";

  private static final List<String> LAYOUTS =
      List.of(
          FIXTURE_CREATE_REQUEST,
          FIXTURE_STATE_REQUEST,
          "URLREQ01",
          "UPWREQ01",
          FIXTURE_UNLOCK_REQUEST);
  private static final UUID SOURCE = new UUID(80, 1);
  private static final UUID RETRY = new UUID(80, 2);
  private static final UUID RESPONSE = new UUID(80, 3);
  private static final UUID REPLY = new UUID(80, 4);
  private static final UUID TOKEN = new UUID(80, 5);
  private static final Instant NOW = Instant.parse("2026-09-08T03:04:05.123456789Z");
  private static final Instant LATER = NOW.plusSeconds(3600);
  private static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "admin", Role.ADMIN);
  private static final String CONTEXT = "b".repeat(64);
  private static final String NEW_CONTEXT = "c".repeat(64);

  @Test
  void adm028FiveLayoutsFreezeOriginalResultVersionAndFreshHeaders() throws Exception {
    try (var keys = keys()) {
      var service = new UserMutationReplayService(keys);
      for (String layout : LAYOUTS)
        for (boolean flag : List.of(false, true))
          for (long expected : new long[] {0, 9, 999_999_998L}) {
            long version = layout.equals(FIXTURE_CREATE_REQUEST) ? 0 : expected + 1;
            for (long target : new long[] {3, 999_999_999_999L})
              try (var original = request(layout, target, expected, flag, SOURCE, CONTEXT);
                  var retry = request(layout, target, expected, flag, RETRY, NEW_CONTEXT)) {
                var result = success(target, version, ResultCode.SUCCESS);
                var saved = service.capture(original, ADMIN, result, RESPONSE, NOW);
                assertEquals(InboxCompletionState.COMPLETED, saved.state());
                assertEquals(
                    InboxResultReference.numeric(InboxResultReferenceType.USER, target),
                    saved.resultReference());
                assertEquals(
                    NOW.truncatedTo(java.time.temporal.ChronoUnit.MICROS), saved.completedAt());
                assertArrayEquals(
                    wire(
                        layout,
                        SOURCE,
                        RESPONSE,
                        NOW,
                        CONTEXT,
                        FIXTURE_SUCCESS_CODE,
                        target,
                        version),
                    decrypt(saved, SOURCE, 1));
                var first = service.read(original, ADMIN, bound(SOURCE, saved, false));
                assertArrayEquals(
                    wire(
                        layout,
                        SOURCE,
                        REPLY,
                        LATER,
                        CONTEXT,
                        FIXTURE_SUCCESS_CODE,
                        target,
                        version),
                    service.reply(first, original, ADMIN, REPLY, LATER));
                for (var current : List.of(original, retry)) {
                  var replay = service.read(current, ADMIN, bound(SOURCE, saved, true));
                  assertArrayEquals(
                      wire(
                          layout,
                          current.header().messageId(),
                          REPLY,
                          LATER,
                          current == original ? CONTEXT : NEW_CONTEXT,
                          FIXTURE_REPLAY_CODE,
                          target,
                          version),
                      service.reply(replay, current, ADMIN, REPLY, LATER));
                  assertEquals("UserMutationSnapshot[REDACTED]", replay.toString());
                }
              }
          }
      for (long version : new long[] {0, 999_999_999L})
        try (var request = request(FIXTURE_UNLOCK_REQUEST, 3, version, true, SOURCE, CONTEXT)) {
          var saved =
              service.capture(
                  request,
                  ADMIN,
                  success(3, version, ResultCode.IDEMPOTENT_SUCCESS),
                  RESPONSE,
                  NOW);
          for (boolean replay : List.of(false, true)) {
            var snapshot = service.read(request, ADMIN, bound(SOURCE, saved, replay));
            assertArrayEquals(
                wire(
                    FIXTURE_UNLOCK_REQUEST,
                    SOURCE,
                    REPLY,
                    LATER,
                    CONTEXT,
                    FIXTURE_REPLAY_CODE,
                    3,
                    version),
                service.reply(snapshot, request, ADMIN, REPLY, LATER));
          }
        }
    }
  }

  @Test
  void adm029DefiniteErrorsAndTransientFailuresKeepTheirProfiles() throws Exception {
    try (var keys = keys()) {
      var service = new UserMutationReplayService(keys);
      for (String layout : LAYOUTS)
        try (var request = request(layout, 3, 7, true, SOURCE, CONTEXT)) {
          for (var code : ResultCode.values()) {
            boolean definite =
                code == ResultCode.CONFLICT
                    || code == ResultCode.RESOURCE_LIMIT
                    || (code == ResultCode.NOT_FOUND && !layout.equals(FIXTURE_CREATE_REQUEST))
                    || (code == ResultCode.VALIDATION_ERROR
                        && List.of(FIXTURE_CREATE_REQUEST, "UPWREQ01").contains(layout));
            boolean transientError =
                List.of(
                        ResultCode.SESSION_INVALID,
                        ResultCode.FORBIDDEN,
                        ResultCode.TEMPORARY_FAILURE)
                    .contains(code);
            if (definite) {
              var saved =
                  service.capture(request, ADMIN, UserMutationResult.rejected(code), RESPONSE, NOW);
              assertEquals(InboxCompletionState.ERROR, saved.state());
              assertEquals(InboxResultReference.none(), saved.resultReference());
              assertArrayEquals(
                  wire(layout, SOURCE, RESPONSE, NOW, CONTEXT, oracleResultCode(code), 0, 0),
                  decrypt(saved, SOURCE, 1));
              for (boolean replay : List.of(false, true)) {
                var snapshot = service.read(request, ADMIN, bound(SOURCE, saved, replay));
                assertArrayEquals(
                    wire(layout, SOURCE, REPLY, LATER, CONTEXT, oracleResultCode(code), 0, 0),
                    service.reply(snapshot, request, ADMIN, REPLY, LATER));
              }
            } else if (List.of(ResultCode.NOT_FOUND, ResultCode.VALIDATION_ERROR).contains(code)) {
              deny(
                  () ->
                      service.capture(
                          request, ADMIN, UserMutationResult.rejected(code), RESPONSE, NOW));
            }
            if (definite || transientError)
              assertArrayEquals(
                  wire(layout, SOURCE, REPLY, LATER, CONTEXT, oracleResultCode(code), 0, 0),
                  service.failure(request, code, REPLY, LATER));
            else deny(() -> service.failure(request, code, REPLY, LATER));
            if (!definite
                && !(code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)) {
              byte[] body =
                  wire(layout, SOURCE, RESPONSE, NOW, CONTEXT, oracleResultCode(code), 0, 0);
              var invalid =
                  stored(
                      layout,
                      SOURCE,
                      1,
                      body,
                      InboxCompletionState.ERROR,
                      InboxResultReference.none(),
                      NOW.truncatedTo(java.time.temporal.ChronoUnit.MICROS));
              deny(() -> service.read(request, ADMIN, bound(SOURCE, invalid, true)));
            }
          }
        }
    }
  }

  @Test
  void adm030TamperedEncryptedRowsReferencesAndBodiesNeverReplay() throws Exception {
    try (var keys = keys();
        var request = request(FIXTURE_STATE_REQUEST, 3, 7, true, RETRY, NEW_CONTEXT)) {
      var service = new UserMutationReplayService(keys);
      byte[] valid =
          wire(FIXTURE_STATE_REQUEST, SOURCE, RESPONSE, NOW, CONTEXT, FIXTURE_SUCCESS_CODE, 3, 8);
      var saved =
          stored(
              FIXTURE_STATE_REQUEST,
              SOURCE,
              1,
              valid,
              InboxCompletionState.COMPLETED,
              InboxResultReference.numeric(InboxResultReferenceType.USER, 3),
              NOW.truncatedTo(java.time.temporal.ChronoUnit.MICROS));
      var read = service.read(request, ADMIN, bound(SOURCE, saved, true));
      assertArrayEquals(
          wire(FIXTURE_STATE_REQUEST, RETRY, REPLY, LATER, NEW_CONTEXT, FIXTURE_REPLAY_CODE, 3, 8),
          service.reply(read, request, ADMIN, REPLY, LATER));
      deny(() -> service.read(request, ADMIN, bound(RETRY, saved, true)));
      deny(() -> service.read(request, ADMIN, bound(SOURCE, saved, false)));
      deny(
          () ->
              service.read(
                  request, ADMIN, new BoundInboxExecution(SOURCE, InboxExecution.inProgress())));
      var otherOwner = new AuthenticatedActor(2, "other", Role.ADMIN);
      deny(() -> service.read(request, otherOwner, bound(SOURCE, saved, true)));
      List<InboxCompletion> badRows =
          List.of(
              change(
                  saved,
                  "URLRSP01",
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  saved.resultReference(),
                  saved.responseSnapshot(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  "002",
                  saved.state(),
                  saved.resultReference(),
                  saved.responseSnapshot(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  InboxCompletionState.ERROR,
                  saved.resultReference(),
                  saved.responseSnapshot(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  InboxResultReference.none(),
                  saved.responseSnapshot(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 3),
                  saved.responseSnapshot(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  InboxResultReference.numeric(InboxResultReferenceType.USER, 4),
                  saved.responseSnapshot(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  saved.resultReference(),
                  Optional.empty(),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  saved.resultReference(),
                  Optional.of(
                      new EncryptedResponseSnapshot(
                          "unknown", saved.responseSnapshot().orElseThrow().ciphertext())),
                  saved.completedAt()),
              change(
                  saved,
                  FIXTURE_STATE_RESPONSE,
                  FIXTURE_LAYOUT_VERSION,
                  saved.state(),
                  saved.resultReference(),
                  saved.responseSnapshot(),
                  saved.completedAt().plusMillis(1)));
      for (var row : badRows) deny(() -> service.read(request, ADMIN, bound(SOURCE, row, true)));
      byte[] ciphertext = saved.responseSnapshot().orElseThrow().ciphertext();
      ciphertext[ciphertext.length - 1] ^= 1;
      var corrupt =
          change(
              saved,
              FIXTURE_STATE_RESPONSE,
              FIXTURE_LAYOUT_VERSION,
              saved.state(),
              saved.resultReference(),
              Optional.of(new EncryptedResponseSnapshot(FIXTURE_KEY_ID, ciphertext)),
              saved.completedAt());
      deny(() -> service.read(request, ADMIN, bound(SOURCE, corrupt, true)));
      var mutations = new ArrayList<byte[]>();
      mutations.add(Arrays.copyOf(valid, 279));
      mutations.add(Arrays.copyOf(valid, 281));
      for (var field :
          Map.ofEntries(
                  Map.entry(0, "BROKEN01"),
                  Map.entry(11, "URLRSP01"),
                  Map.entry(19, "002"),
                  Map.entry(22, "Q"),
                  Map.entry(23, "A"),
                  Map.entry(60, RETRY.toString()),
                  Map.entry(96, "20260908120406123"),
                  Map.entry(181, "000023"),
                  Map.entry(187, "000001"),
                  Map.entry(193, "000001"),
                  Map.entry(199, "000000281"),
                  Map.entry(208, "9999"),
                  Map.entry(212, "x"),
                  Map.entry(256, "000000000004"),
                  Map.entry(268, "000000007"),
                  Map.entry(277, "x"))
              .entrySet()) {
        byte[] changed = valid.clone();
        put(changed, field.getKey(), field.getValue());
        mutations.add(changed);
      }
      mutations.add(
          wire(FIXTURE_STATE_REQUEST, SOURCE, RESPONSE, NOW, CONTEXT, FIXTURE_REPLAY_CODE, 3, 7));
      for (byte[] changed : mutations) {
        var row =
            stored(
                FIXTURE_STATE_REQUEST,
                SOURCE,
                1,
                changed,
                saved.state(),
                saved.resultReference(),
                saved.completedAt());
        deny(() -> service.read(request, ADMIN, bound(SOURCE, row, true)));
      }
      byte[] error = wire(FIXTURE_STATE_REQUEST, SOURCE, RESPONSE, NOW, CONTEXT, "0105", 0, 0);
      put(error, 256, "000000000003");
      var invalidFiller =
          stored(
              FIXTURE_STATE_REQUEST,
              SOURCE,
              1,
              error,
              InboxCompletionState.ERROR,
              InboxResultReference.none(),
              saved.completedAt());
      deny(() -> service.read(request, ADMIN, bound(SOURCE, invalidFiller, true)));
      byte[] wrongErrorState =
          wire(FIXTURE_STATE_REQUEST, SOURCE, RESPONSE, NOW, CONTEXT, "0105", 0, 0);
      var invalidState =
          stored(
              FIXTURE_STATE_REQUEST,
              SOURCE,
              1,
              wrongErrorState,
              InboxCompletionState.COMPLETED,
              InboxResultReference.none(),
              saved.completedAt());
      deny(() -> service.read(request, ADMIN, bound(SOURCE, invalidState, true)));
    }
  }

  @Test
  void adm031NullClosedAndCrossRequestScopesFailWithoutSecrets() throws Exception {
    var keys = keys();
    var request = request(FIXTURE_STATE_REQUEST, 3, 7, true, SOURCE, CONTEXT);
    try {
      var service = new UserMutationReplayService(keys);
      var result = success(3, 8, ResultCode.SUCCESS);
      var completion = service.capture(request, ADMIN, result, RESPONSE, NOW);
      var bound = bound(SOURCE, completion, false);
      var snapshot = service.read(request, ADMIN, bound);
      for (Executable call :
          List.<Executable>of(
              () -> new UserMutationReplayService(null),
              () -> service.capture(null, ADMIN, result, RESPONSE, NOW),
              () -> service.capture(request, null, result, RESPONSE, NOW),
              () -> service.capture(request, ADMIN, null, RESPONSE, NOW),
              () -> service.capture(request, ADMIN, result, null, NOW),
              () -> service.capture(request, ADMIN, result, RESPONSE, null),
              () -> service.read(null, ADMIN, bound),
              () -> service.read(request, null, bound),
              () -> service.read(request, ADMIN, null),
              () -> service.reply(null, request, ADMIN, REPLY, LATER),
              () -> service.reply(snapshot, null, ADMIN, REPLY, LATER),
              () -> service.reply(snapshot, request, null, REPLY, LATER),
              () -> service.reply(snapshot, request, ADMIN, null, LATER),
              () -> service.reply(snapshot, request, ADMIN, REPLY, null),
              () -> service.failure(null, ResultCode.CONFLICT, REPLY, LATER),
              () -> service.failure(request, null, REPLY, LATER),
              () -> service.failure(request, ResultCode.CONFLICT, null, LATER),
              () -> service.failure(request, ResultCode.CONFLICT, REPLY, null)))
        assertThrows(NullPointerException.class, call);
      var user = new AuthenticatedActor(1, "admin", Role.USER);
      deny(() -> service.capture(request, user, result, RESPONSE, NOW));
      deny(() -> service.read(request, user, bound));
      deny(() -> service.reply(snapshot, request, user, REPLY, LATER));
      deny(
          () ->
              service.reply(
                  snapshot, request, new AuthenticatedActor(2, "other", Role.ADMIN), REPLY, LATER));
      try (var other = request(FIXTURE_STATE_REQUEST, 3, 7, true, SOURCE, CONTEXT)) {
        deny(() -> service.reply(snapshot, other, ADMIN, REPLY, LATER));
      }
      for (var bad :
          List.of(
              success(4, 8, ResultCode.SUCCESS),
              success(3, 7, ResultCode.SUCCESS),
              success(3, 7, ResultCode.IDEMPOTENT_SUCCESS)))
        deny(() -> service.capture(request, ADMIN, bad, RESPONSE, NOW));
      try (var create = request(FIXTURE_CREATE_REQUEST, 3, 0, true, SOURCE, CONTEXT);
          var unlock = request(FIXTURE_UNLOCK_REQUEST, 3, 7, true, SOURCE, CONTEXT);
          var maximum = request(FIXTURE_STATE_REQUEST, 3, 999_999_999L, true, SOURCE, CONTEXT)) {
        deny(
            () -> service.capture(create, ADMIN, success(3, 1, ResultCode.SUCCESS), RESPONSE, NOW));
        deny(
            () ->
                service.capture(
                    create, ADMIN, success(3, 0, ResultCode.IDEMPOTENT_SUCCESS), RESPONSE, NOW));
        deny(
            () ->
                service.capture(
                    unlock, ADMIN, success(3, 8, ResultCode.IDEMPOTENT_SUCCESS), RESPONSE, NOW));
        deny(
            () ->
                service.capture(
                    maximum, ADMIN, success(3, 999_999_999L, ResultCode.SUCCESS), RESPONSE, NOW));
      }
      for (Instant invalid : List.of(Instant.MIN, Instant.MAX)) {
        deny(() -> service.capture(request, ADMIN, result, RESPONSE, invalid));
        deny(() -> service.reply(snapshot, request, ADMIN, REPLY, invalid));
        deny(() -> service.failure(request, ResultCode.CONFLICT, REPLY, invalid));
      }
      keys.close();
      deny(() -> service.capture(request, ADMIN, result, RESPONSE, NOW));
      deny(() -> service.read(request, ADMIN, bound));
      // Reply owns verified result, not keys; closing keys must not turn it into a DB reread.
      assertArrayEquals(
          wire(FIXTURE_STATE_REQUEST, SOURCE, REPLY, LATER, CONTEXT, FIXTURE_SUCCESS_CODE, 3, 8),
          service.reply(snapshot, request, ADMIN, REPLY, LATER));
      request.close();
      assertThrows(IllegalStateException.class, request::expectedVersion);
      deny(() -> service.capture(request, ADMIN, result, RESPONSE, NOW));
      deny(() -> service.read(request, ADMIN, bound));
      deny(() -> service.reply(snapshot, request, ADMIN, REPLY, LATER));
      deny(() -> service.failure(request, ResultCode.CONFLICT, REPLY, LATER));
    } finally {
      request.close();
      keys.close();
    }
  }

  @Test
  void adm032OneHundredIndependentReplaysDoNotShareHeadersOrVersions() throws Exception {
    try (var keys = keys();
        var workers = Executors.newFixedThreadPool(10)) {
      var service = new UserMutationReplayService(keys);
      var results = new ArrayList<java.util.concurrent.Future<UUID>>();
      for (int i = 0; i < 100; i++) {
        int n = i;
        results.add(
            workers.submit(
                () -> {
                  String layout = LAYOUTS.get(n % 5);
                  var actor = new AuthenticatedActor(n + 1, "admin" + n, Role.ADMIN);
                  UUID source = new UUID(81, n);
                  UUID retry = new UUID(82, n);
                  UUID response = new UUID(83, n);
                  long version = layout.equals(FIXTURE_CREATE_REQUEST) ? 0 : n + 1;
                  try (var original = request(layout, n + 3, n, true, source, CONTEXT);
                      var current = request(layout, n + 3, n, true, retry, NEW_CONTEXT)) {
                    var saved =
                        service.capture(
                            original,
                            actor,
                            success(n + 3, version, ResultCode.SUCCESS),
                            RESPONSE,
                            NOW);
                    var snapshot = service.read(current, actor, bound(source, saved, true));
                    assertArrayEquals(
                        wire(
                            layout,
                            retry,
                            response,
                            LATER,
                            NEW_CONTEXT,
                            FIXTURE_REPLAY_CODE,
                            n + 3,
                            version),
                        service.reply(snapshot, current, actor, response, LATER));
                    return response;
                  }
                }));
      }
      var unique = new HashSet<UUID>();
      for (var future : results) assertTrue(unique.add(future.get(20, TimeUnit.SECONDS)));
      assertEquals(100, unique.size());
    }
  }

  private static ResponseSnapshotCodec keys() {
    return new ResponseSnapshotCodec(FIXTURE_KEY_ID, new byte[32], null, null);
  }

  private static UserMutationRequest request(
      String layout, long target, long version, boolean flag, UUID message, String context) {
    // Independent UI236 input helper, not a production encoder or expected-value generator.
    byte[] data =
        UserMutationRequestTest.data(
            layout, target, version, flag, "New", "Synthetic-Password-12", TOKEN);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(layout),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            message,
            message,
            NOW.truncatedTo(java.time.temporal.ChronoUnit.MILLIS),
            Optional.of(AuthenticationContext.of(context)),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return UserMutationRequest.decode(
        new WireMessage<>(header, new FixedPayload(data, 0, List.of())));
  }

  private static UserMutationResult success(long target, long version, ResultCode code) {
    return new UserMutationResult(
        code, Optional.of(new UserMutationResponseData(new UserId(target), version)));
  }

  private static BoundInboxExecution bound(
      UUID source, InboxCompletion completion, boolean replay) {
    return new BoundInboxExecution(
        source, replay ? InboxExecution.replay(completion) : InboxExecution.executed(completion));
  }

  private static void deny(Executable call) {
    var failure = assertThrows(TemporaryInfrastructureException.class, call);
    assertEquals("request transaction is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertFalse(failure.toString().contains(CONTEXT));
  }

  private static InboxCompletion change(
      InboxCompletion unused,
      String layout,
      String version,
      InboxCompletionState state,
      InboxResultReference ref,
      Optional<EncryptedResponseSnapshot> snapshot,
      Instant time) {
    return new InboxCompletion(state, ref, layout, version, snapshot, time);
  }

  private static InboxCompletion stored(
      String layout,
      UUID source,
      long owner,
      byte[] body,
      InboxCompletionState state,
      InboxResultReference ref,
      Instant time)
      throws Exception {
    return new InboxCompletion(
        state,
        ref,
        layout.replace("REQ", "RSP"),
        FIXTURE_LAYOUT_VERSION,
        Optional.of(encrypt(body, source, owner, layout.replace("REQ", "RSP"))),
        time);
  }

  static byte[] wire(
      String layout,
      UUID source,
      UUID response,
      Instant time,
      String context,
      String code,
      long target,
      long version) {
    byte[] bytes = new byte[280];
    Arrays.fill(bytes, (byte) 32);
    put(bytes, 0, "SCHBNK01001");
    put(bytes, 11, layout.replace("REQ", "RSP"));
    put(bytes, 19, "001SS");
    put(bytes, 24, response.toString());
    put(bytes, 60, source.toString());
    put(
        bytes,
        96,
        DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
            .withZone(ZoneId.of("Asia/Tokyo"))
            .format(time));
    put(bytes, 113, context);
    put(bytes, 177, "0256000024000000000000000000280");
    put(bytes, 208, code);
    put(bytes, 256, String.format(Locale.ROOT, "%012d%09d", target, version));
    return bytes;
  }

  private static void put(byte[] bytes, int offset, String value) {
    byte[] data = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(data, 0, bytes, offset, data.length);
  }

  private static byte[] aad(UUID source, long owner, String layout) throws Exception {
    var bytes = new ByteArrayOutputStream();
    try (var out = new DataOutputStream(bytes)) {
      for (byte[] field :
          List.of(
              "api-inbox-response".getBytes(StandardCharsets.US_ASCII),
              "schubert.request_inbox".getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(16)
                  .putLong(source.getMostSignificantBits())
                  .putLong(source.getLeastSignificantBits())
                  .array(),
              new byte[] {1},
              FIXTURE_KEY_ID.getBytes(StandardCharsets.US_ASCII),
              layout.getBytes(StandardCharsets.US_ASCII),
              FIXTURE_LAYOUT_VERSION.getBytes(StandardCharsets.US_ASCII),
              ByteBuffer.allocate(8).putLong(owner).array())) {
        out.writeInt(field.length);
        out.write(field);
      }
    }
    return bytes.toByteArray();
  }

  static EncryptedResponseSnapshot encrypt(byte[] plaintext, UUID source, long owner, String layout)
      throws Exception {
    var output = new ByteArrayOutputStream();
    var deflater = new Deflater(3);
    try (var stream = new DeflaterOutputStream(output, deflater)) {
      stream.write(plaintext);
    } finally {
      deflater.end();
    }
    // Fixed nonce is an independent synthetic test vector only; production chooses a fresh nonce.
    byte[] nonce = new byte[12];
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.ENCRYPT_MODE,
        new SecretKeySpec(new byte[32], "AES"),
        new GCMParameterSpec(128, nonce));
    cipher.updateAAD(aad(source, owner, layout));
    byte[] encrypted = cipher.doFinal(output.toByteArray());
    return new EncryptedResponseSnapshot(
        FIXTURE_KEY_ID,
        ByteBuffer.allocate(24 + encrypted.length)
            .put("NKENC1".getBytes(StandardCharsets.US_ASCII))
            .put((byte) 1)
            .put((byte) 4)
            .put(FIXTURE_KEY_ID.getBytes(StandardCharsets.US_ASCII))
            .put(nonce)
            .put(encrypted)
            .array());
  }

  static byte[] decrypt(InboxCompletion completion, UUID source, long owner) throws Exception {
    byte[] stored = completion.responseSnapshot().orElseThrow().ciphertext();
    assertArrayEquals(
        "NKENC1".getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(stored, 0, 6));
    assertEquals(1, stored[6]);
    assertEquals(4, stored[7]);
    assertArrayEquals(
        FIXTURE_KEY_ID.getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(stored, 8, 12));
    var cipher = Cipher.getInstance("AES/GCM/NoPadding");
    cipher.init(
        Cipher.DECRYPT_MODE,
        new SecretKeySpec(new byte[32], "AES"),
        new GCMParameterSpec(128, Arrays.copyOfRange(stored, 12, 24)));
    cipher.updateAAD(aad(source, owner, completion.responseLayoutId()));
    byte[] compressed = cipher.doFinal(Arrays.copyOfRange(stored, 24, stored.length));
    try (var inflater =
        new java.util.zip.InflaterInputStream(new java.io.ByteArrayInputStream(compressed))) {
      return inflater.readAllBytes();
    }
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
