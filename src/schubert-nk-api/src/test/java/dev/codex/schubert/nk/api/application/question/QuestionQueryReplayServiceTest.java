package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.ADMIN;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.MESSAGE;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.NOW;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.USER;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.data;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.message;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
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
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadRecord;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.common.PagedResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationRecord;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSummaryRecord;
import dev.codex.schubert.nk.protocol.layout.semantic.AnswerState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationType;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.zip.Deflater;
import java.util.zip.DeflaterOutputStream;
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** UI236 literal wire/SSC157 prefix and independent JCE; PT-QRY013..017/NTF010. */
final class QuestionQueryReplayServiceTest {
  private static final String KEY_FIXTURE_ID = "test";
  private static final String QSD_REQUEST = "QSDREQ01";
  private static final String NTD_REQUEST = "NTDREQ01";
  private static final String SUCCESS_CODE = "0000";
  private static final String REPLAY_CODE = "0200";
  private static final String LAYOUT_VERSION = "001";
  private static final String QUESTION_TEXT = "question";

  static final UUID RESPONSE = new UUID(101, 1);
  static final UUID REPLY = new UUID(101, 2);
  static final Instant COMPLETED = NOW.plusNanos(123456789);
  static final Instant LATER = NOW.plusSeconds(3600);
  static final long ID = 999999999999L;

  @Test
  void qry013FrozenFourRoutesScopeAndRepliesMatchIndependentWholeBytes() throws Exception {
    try (var keys = new ResponseSnapshotCodec(KEY_FIXTURE_ID, new byte[32], null, null)) {
      var service = new QuestionQueryReplayService(keys);
      for (String layout : List.of("QSSREQ01", QSD_REQUEST, "NTSREQ01", NTD_REQUEST))
        for (var actor : List.of(USER, ADMIN))
          for (int count : new int[] {0, 1}) {
            var request = QuestionQueryRequest.decode(message(layout, data(layout, false)));
            var saved =
                service.captureSuccess(request, actor, values(request, count), RESPONSE, COMPLETED);
            byte[] expected = wire(layout, RESPONSE, COMPLETED, SUCCESS_CODE, count);
            assertArrayEquals(frame(request, actor.role(), expected), decrypt(saved, MESSAGE, 1));
            assertEquals(InboxResultReference.none(), saved.resultReference());
            assertEquals(COMPLETED.truncatedTo(ChronoUnit.MICROS), saved.completedAt());
            byte[] original = saved.responseSnapshot().orElseThrow().ciphertext();
            for (boolean replay : List.of(false, true)) {
              var snapshot = service.read(request, actor, saved);
              assertEquals("QuestionQuerySnapshot[REDACTED]", snapshot.toString());
              assertTrue(snapshot.scopeAllowed(actor));
              assertArrayEquals(
                  wire(layout, REPLY, LATER, replay ? REPLAY_CODE : SUCCESS_CODE, count),
                  service.reply(snapshot, request, actor, REPLY, LATER, replay));
              assertTrue(snapshot.scopeAllowed(ADMIN));
              boolean permitted = !request.questionScope() || actor.role() == Role.USER;
              assertEquals(permitted, snapshot.scopeAllowed(USER));
              if (!permitted)
                deny(() -> service.reply(snapshot, request, USER, REPLY, LATER, true));
              else
                assertArrayEquals(
                    wire(layout, REPLY, LATER, REPLAY_CODE, count),
                    service.reply(snapshot, request, USER, REPLY, LATER, true));
              assertFalse(snapshot.scopeAllowed(new AuthenticatedActor(2, "u2", Role.ADMIN)));
              deny(
                  () ->
                      service.reply(
                          snapshot,
                          request,
                          new AuthenticatedActor(2, "u2", Role.USER),
                          REPLY,
                          LATER,
                          true));
            }
            assertArrayEquals(original, saved.responseSnapshot().orElseThrow().ciphertext());
          }
    }
  }

  @Test
  void qry014DefiniteErrorsRetainScopeAndNonstoredDenialsHaveIndependentFiller() throws Exception {
    try (var keys = new ResponseSnapshotCodec(KEY_FIXTURE_ID, new byte[32], null, null)) {
      var service = new QuestionQueryReplayService(keys);
      for (String layout : List.of("QSSREQ01", QSD_REQUEST, "NTSREQ01", NTD_REQUEST)) {
        var request = QuestionQueryRequest.decode(message(layout, data(layout, false)));
        for (var code : ResultCode.values()) {
          boolean persistent =
              request.detailRequest()
                  ? code == ResultCode.NOT_FOUND
                  : code == ResultCode.RESOURCE_LIMIT;
          if (persistent)
            for (var actor : List.of(USER, ADMIN)) {
              var saved = service.captureFailure(request, actor, code, RESPONSE, COMPLETED);
              assertEquals(InboxCompletionState.ERROR, saved.state());
              assertArrayEquals(
                  frame(
                      request,
                      actor.role(),
                      wire(layout, RESPONSE, COMPLETED, oracleResultCode(code), 0)),
                  decrypt(saved, MESSAGE, 1));
              assertArrayEquals(
                  wire(layout, REPLY, LATER, oracleResultCode(code), 0),
                  service.reply(
                      service.read(request, actor, saved), request, actor, REPLY, LATER, true));
            }
          else deny(() -> service.captureFailure(request, ADMIN, code, RESPONSE, COMPLETED));
          if (persistent
              || List.of(
                      ResultCode.VALIDATION_ERROR,
                      ResultCode.SESSION_INVALID,
                      ResultCode.FORBIDDEN,
                      ResultCode.TEMPORARY_FAILURE)
                  .contains(code))
            assertArrayEquals(
                wire(layout, REPLY, LATER, oracleResultCode(code), 0),
                service.failure(request, code, REPLY, LATER));
          else deny(() -> service.failure(request, code, REPLY, LATER));
        }
      }
    }
  }

  @Test
  void qry015LegacyMalformedEncryptedAndMetadataCannotGrantReplay() throws Exception {
    try (var keys = new ResponseSnapshotCodec(KEY_FIXTURE_ID, new byte[32], null, null)) {
      var service = new QuestionQueryReplayService(keys);
      for (String layout : List.of("QSSREQ01", QSD_REQUEST, "NTSREQ01", NTD_REQUEST)) {
        var request = QuestionQueryRequest.decode(message(layout, data(layout, false)));
        byte[] expected = wire(layout, RESPONSE, COMPLETED, SUCCESS_CODE, 1);
        var saved =
            stored(request, frame(request, Role.ADMIN, expected), InboxCompletionState.COMPLETED);
        service.read(request, ADMIN, saved);
        var legacy = stored(request, expected, InboxCompletionState.COMPLETED);
        if (request.questionScope()) deny(() -> service.read(request, ADMIN, legacy));
        else service.read(request, ADMIN, legacy);
        for (int offset : new int[] {0, 11, 19, 22, 60, 96, 181, 187, 193, 199, 208}) {
          byte[] changed = expected.clone();
          changed[offset] = (byte) '?';
          deny(
              () ->
                  service.read(
                      request,
                      ADMIN,
                      stored(
                          request,
                          frame(request, Role.ADMIN, changed),
                          InboxCompletionState.COMPLETED)));
        }
        for (byte[] changed :
            List.of(
                Arrays.copyOf(expected, expected.length - 1),
                Arrays.copyOf(expected, expected.length + 1)))
          deny(
              () ->
                  service.read(
                      request,
                      ADMIN,
                      stored(
                          request,
                          frame(request, Role.ADMIN, changed),
                          InboxCompletionState.COMPLETED)));
        byte[] wrongId = expected.clone();
        put(wrongId, 256, request.detailRequest() ? "000000000001" : "000002");
        deny(
            () ->
                service.read(
                    request,
                    ADMIN,
                    stored(
                        request,
                        frame(request, Role.ADMIN, wrongId),
                        InboxCompletionState.COMPLETED)));
        for (var bad :
            List.of(
                new InboxCompletion(
                    saved.state(),
                    saved.resultReference(),
                    "USRRSP01",
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
                    InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 1),
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
        byte[] corrupt = saved.responseSnapshot().orElseThrow().ciphertext();
        corrupt[corrupt.length - 1] ^= 1;
        for (var encrypted :
            List.of(
                new EncryptedResponseSnapshot(KEY_FIXTURE_ID, corrupt),
                new EncryptedResponseSnapshot(
                    "gone", saved.responseSnapshot().orElseThrow().ciphertext()),
                encrypt(
                    frame(request, Role.ADMIN, expected),
                    MESSAGE,
                    2,
                    request.responseLayoutId().value()))) {
          var bad =
              new InboxCompletion(
                  saved.state(),
                  saved.resultReference(),
                  saved.responseLayoutId(),
                  LAYOUT_VERSION,
                  Optional.of(encrypted),
                  saved.completedAt());
          deny(() -> service.read(request, ADMIN, bad));
        }
        var denied =
            service.captureFailure(
                request,
                ADMIN,
                request.detailRequest() ? ResultCode.NOT_FOUND : ResultCode.RESOURCE_LIMIT,
                RESPONSE,
                COMPLETED);
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
      }
    }
  }

  static TypedPayloadValues values(QuestionQueryRequest request, int count) {
    String layout = request.responseLayoutId().value();
    if (layout.equals("QSDRSP01"))
      return new TypedPayloadValues(
          new LayoutId(layout),
          new QuestionDetailResponseData(
              new QuestionId(ID),
              "0".repeat(26),
              "u1",
              AnswerState.UNANSWERED,
              QUESTION_TEXT,
              Optional.empty(),
              NOW,
              Optional.empty()),
          List.of());
    if (layout.equals("NTDRSP01"))
      return new TypedPayloadValues(
          new LayoutId(layout),
          new NotificationDetailResponseData(
              new NotificationId(ID),
              "0".repeat(26),
              NotificationType.ACCEPTED,
              NotificationState.RECEIVED,
              NOW,
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              false,
              Optional.of(QUESTION_TEXT),
              Optional.empty(),
              Optional.empty(),
              Optional.empty(),
              Optional.of(new QuestionId(ID))),
          List.of());
    List<PayloadRecord> records =
        count == 0
            ? List.of()
            : layout.equals("QSSRSP01")
                ? List.of(
                    new QuestionSummaryRecord(
                        new QuestionId(ID),
                        "0".repeat(26),
                        "u1",
                        QUESTION_TEXT,
                        AnswerState.UNANSWERED,
                        NOW,
                        Optional.empty()))
                : List.of(
                    new NotificationRecord(
                        new NotificationId(ID),
                        "0".repeat(26),
                        NotificationType.ACCEPTED,
                        NotificationState.RECEIVED,
                        NOW,
                        NOW,
                        QUESTION_TEXT,
                        false));
    return new TypedPayloadValues(
        new LayoutId(layout),
        new PagedResponseData(1, 50, count, 1, count == 0 ? 0 : 1, count),
        records);
  }

  @Test
  void qry016PublicNullContractsInvalidTimesAndClosedKeysFailWithoutSecretDiagnostics()
      throws Exception {
    var keys = new ResponseSnapshotCodec(KEY_FIXTURE_ID, new byte[32], null, null);
    try {
      var service = new QuestionQueryReplayService(keys);
      var request = QuestionQueryRequest.decode(message(QSD_REQUEST, data(QSD_REQUEST, false)));
      var response = values(request, 0);
      var saved = service.captureSuccess(request, USER, response, RESPONSE, COMPLETED);
      var snapshot = service.read(request, USER, saved);
      assertThrows(NullPointerException.class, () -> new QuestionQueryReplayService(null));
      for (var action :
          List.<org.junit.jupiter.api.function.Executable>of(
              () -> service.captureSuccess(null, USER, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, null, response, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, USER, null, RESPONSE, COMPLETED),
              () -> service.captureSuccess(request, USER, response, null, COMPLETED),
              () -> service.captureSuccess(request, USER, response, RESPONSE, null),
              () -> service.captureFailure(null, USER, ResultCode.NOT_FOUND, RESPONSE, COMPLETED),
              () ->
                  service.captureFailure(request, null, ResultCode.NOT_FOUND, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, USER, null, RESPONSE, COMPLETED),
              () -> service.captureFailure(request, USER, ResultCode.NOT_FOUND, null, COMPLETED),
              () -> service.captureFailure(request, USER, ResultCode.NOT_FOUND, RESPONSE, null),
              () -> service.read(null, USER, saved),
              () -> service.read(request, null, saved),
              () -> service.read(request, USER, null),
              () -> snapshot.scopeAllowed(null),
              () -> service.reply(null, request, USER, REPLY, LATER, true),
              () -> service.reply(snapshot, null, USER, REPLY, LATER, true),
              () -> service.reply(snapshot, request, null, REPLY, LATER, true),
              () -> service.reply(snapshot, request, USER, null, LATER, true),
              () -> service.reply(snapshot, request, USER, REPLY, null, true),
              () -> service.failure(null, ResultCode.NOT_FOUND, REPLY, LATER),
              () -> service.failure(request, null, REPLY, LATER),
              () -> service.failure(request, ResultCode.NOT_FOUND, null, LATER),
              () -> service.failure(request, ResultCode.NOT_FOUND, REPLY, null)))
        assertThrows(NullPointerException.class, action);
      var otherRequest =
          QuestionQueryRequest.decode(message(QSD_REQUEST, data(QSD_REQUEST, false)));
      deny(() -> service.reply(snapshot, otherRequest, USER, REPLY, LATER, true));
      var bad =
          new TypedPayloadValues(
              new LayoutId("NTSRSP01"), new PagedResponseData(1, 50, 0, 1, 0, 0), List.of());
      deny(() -> service.captureSuccess(request, USER, bad, RESPONSE, COMPLETED));
      for (Instant invalid :
          List.of(
              Instant.parse("-0001-01-01T00:00:00Z"), Instant.parse("+10000-01-01T00:00:00Z"))) {
        deny(() -> service.captureSuccess(request, USER, response, RESPONSE, invalid));
        deny(() -> service.captureFailure(request, USER, ResultCode.NOT_FOUND, RESPONSE, invalid));
        deny(() -> service.reply(snapshot, request, USER, REPLY, invalid, true));
        deny(() -> service.failure(request, ResultCode.NOT_FOUND, REPLY, invalid));
      }
      keys.close();
      deny(() -> service.captureSuccess(request, USER, response, RESPONSE, COMPLETED));
      deny(() -> service.captureFailure(request, USER, ResultCode.NOT_FOUND, RESPONSE, COMPLETED));
      deny(() -> service.read(request, USER, saved));
      assertArrayEquals(
          wire(QSD_REQUEST, REPLY, LATER, REPLAY_CODE, 0),
          service.reply(snapshot, request, USER, REPLY, LATER, true));
    } finally {
      keys.close();
    }
  }

  @Test
  void qry017OptionalIdMinimumUsesXLeftPaddingNotNumericZeroPadding() throws Exception {
    byte[] data = "000000000001".getBytes(StandardCharsets.US_ASCII);
    var request = QuestionQueryRequest.decode(message(NTD_REQUEST, data));
    var response =
        new TypedPayloadValues(
            new LayoutId("NTDRSP01"),
            new NotificationDetailResponseData(
                new NotificationId(1),
                "0".repeat(26),
                NotificationType.ACCEPTED,
                NotificationState.RECEIVED,
                NOW,
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                false,
                Optional.of(QUESTION_TEXT),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.of(new QuestionId(1))),
            List.of());
    try (var keys = new ResponseSnapshotCodec(KEY_FIXTURE_ID, new byte[32], null, null)) {
      var service = new QuestionQueryReplayService(keys);
      var saved = service.captureSuccess(request, USER, response, RESPONSE, COMPLETED);
      byte[] expected = wire(NTD_REQUEST, RESPONSE, COMPLETED, SUCCESS_CODE, 0);
      put(expected, 256, "000000000001");
      Arrays.fill(expected, 9124, 9136, (byte) 32);
      put(expected, 9124, "1");
      assertArrayEquals(expected, decrypt(saved, MESSAGE, 1));
      put(expected, 24, REPLY.toString());
      put(expected, 96, time(LATER));
      put(expected, 208, REPLAY_CODE);
      assertArrayEquals(
          expected,
          service.reply(service.read(request, USER, saved), request, USER, REPLY, LATER, true));
    }
  }

  /** UI236 profile comes from the Test input, not a Production request decoder. */
  static byte[] wire(String layout, UUID response, Instant at, String code, int count) {
    return QuestionQueryWireOracle.wire(layout, MESSAGE, response, at, NOW, code, count);
  }

  static String time(Instant at) {
    return DateTimeFormatter.ofPattern("uuuuMMddHHmmssSSS", Locale.ROOT)
        .withZone(ZoneId.of("Asia/Tokyo"))
        .format(at);
  }

  static byte[] frame(QuestionQueryRequest request, Role scope, byte[] wire) {
    if (!request.questionScope()) return wire.clone();
    byte[] prefix =
        HexFormat.of().parseHex(scope == Role.USER ? "4e4b515259310055" : "4e4b515259310041");
    byte[] result = Arrays.copyOf(prefix, 8 + wire.length);
    System.arraycopy(wire, 0, result, 8, wire.length);
    return result;
  }

  static InboxCompletion stored(
      QuestionQueryRequest request, byte[] plain, InboxCompletionState state) throws Exception {
    return new InboxCompletion(
        state,
        InboxResultReference.none(),
        request.responseLayoutId().value(),
        LAYOUT_VERSION,
        Optional.of(encrypt(plain, MESSAGE, 1, request.responseLayoutId().value())),
        COMPLETED.truncatedTo(ChronoUnit.MICROS));
  }

  static void deny(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(TemporaryInfrastructureException.class, action);
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
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
              KEY_FIXTURE_ID.getBytes(StandardCharsets.US_ASCII),
              layout.getBytes(StandardCharsets.US_ASCII),
              LAYOUT_VERSION.getBytes(StandardCharsets.US_ASCII),
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
        KEY_FIXTURE_ID,
        ByteBuffer.allocate(24 + encrypted.length)
            .put("NKENC1".getBytes(StandardCharsets.US_ASCII))
            .put((byte) 1)
            .put((byte) 4)
            .put(KEY_FIXTURE_ID.getBytes(StandardCharsets.US_ASCII))
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
        KEY_FIXTURE_ID.getBytes(StandardCharsets.US_ASCII), Arrays.copyOfRange(stored, 8, 12));
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
