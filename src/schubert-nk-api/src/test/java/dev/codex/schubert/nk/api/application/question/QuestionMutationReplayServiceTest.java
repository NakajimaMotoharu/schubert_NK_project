package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.lp;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.BoundInboxExecution;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.FingerprintKeyRing;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxExecution;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.jupiter.api.Test;

/** UI236 literal wire and SS324 LP/JCE/NKREF1 independent oracles; no expected codec. */
final class QuestionMutationReplayServiceTest {
  private static final String FIXTURE_CANCEL_RESPONSE = "NTCRSP01";
  private static final String FIXTURE_DELETE_RESPONSE = "QDLRSP01";
  private static final String FIXTURE_LAYOUT_VERSION = "001";
  private static final String FIXTURE_KEY_ID = "test";
  private static final String FIXTURE_LAYOUT_FIELD = "layout";

  static final UUID M = new UUID(711, 1);
  static final UUID R = new UUID(711, 2);
  static final UUID NEXT = new UUID(711, 3);
  static final UUID TOKEN = new UUID(711, 4);
  static final Instant AT = Instant.parse("2026-10-01T00:00:01.123456Z");
  static final Instant LATER = AT.plusSeconds(3600);
  static final AuthenticatedActor USER = new AuthenticatedActor(1, "u1", Role.USER);
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "u1", Role.ADMIN);

  @Test
  void qry036OriginalTargetCanonicalAndTokenHeaderRoleExcluded() throws Exception {
    for (boolean cancel : List.of(false, true))
      for (long id : List.of(1L, 999_999_999_999L)) {
        var original = message(cancel, id, M, TOKEN);
        var request = QuestionMutationRequest.decode(original);
        assertSame(original.header(), request.header());
        assertEquals(id, request.targetId());
        assertEquals(TOKEN, request.operationToken());
        assertEquals(cancel, request.cancellation());
        assertEquals(
            cancel ? FIXTURE_CANCEL_RESPONSE : FIXTURE_DELETE_RESPONSE,
            request.responseLayoutId().value());
        assertEquals("QuestionMutationRequest[REDACTED]", request.toString());
        var bytes = new ByteArrayOutputStream();
        try (var out = new DataOutputStream(bytes)) {
          out.write("SCHUBERT-NK-OP1".getBytes(StandardCharsets.US_ASCII));
          for (String s :
              List.of(
                  "1",
                  cancel ? "NTCREQ01" : "QDLREQ01",
                  FIXTURE_LAYOUT_VERSION,
                  (cancel ? "NOTIFICATION:" : "QUESTION:") + id)) lp(out, s);
          out.writeInt(1);
          lp(out, cancel ? "notificationId" : "questionId");
          lp(out, "N1");
          lp(out, Long.toString(id));
        }
        var mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(new byte[32], "HmacSHA256"));
        try (var keys = new FingerprintKeyRing(FIXTURE_KEY_ID, new byte[32], null, null);
            var canonical = request.canonical(USER);
            var admin = request.canonical(ADMIN);
            var another =
                QuestionMutationRequest.decode(message(cancel, id, NEXT, new UUID(711, 5)))
                    .canonical(USER)) {
          assertArrayEquals(mac.doFinal(bytes.toByteArray()), keys.calculate(canonical).digest());
          assertArrayEquals(keys.calculate(canonical).digest(), keys.calculate(admin).digest());
          assertArrayEquals(keys.calculate(canonical).digest(), keys.calculate(another).digest());
        }
      }
    assertThrows(NullPointerException.class, () -> QuestionMutationRequest.decode(null));
    var invalid = message(true, 0, M, TOKEN);
    assertThrows(PermanentProtocolException.class, () -> QuestionMutationRequest.decode(invalid));
    byte[] unsupported = new byte[12];
    Arrays.fill(unsupported, (byte) '0');
    assertThrows(
        PermanentProtocolException.class,
        () ->
            QuestionMutationRequest.decode(
                QuestionQueryRequestTest.message("QSDREQ01", unsupported)));
  }

  @Test
  void qry037AllFrozenProfilesNkrefIndependentJceAndReplyBytes() throws Exception {
    try (var keys = new ResponseSnapshotCodec(FIXTURE_KEY_ID, new byte[32], null, null)) {
      var service = new QuestionMutationReplayService(keys);
      for (boolean cancel : List.of(false, true)) {
        var request = QuestionMutationRequest.decode(message(cancel, 3, M, TOKEN));
        var codes =
            cancel
                ? List.of(
                    ResultCode.SUCCESS,
                    ResultCode.IDEMPOTENT_SUCCESS,
                    ResultCode.NOT_FOUND,
                    ResultCode.NOT_CANCELLABLE,
                    ResultCode.RESOURCE_LIMIT)
                : List.of(
                    ResultCode.SUCCESS,
                    ResultCode.IDEMPOTENT_SUCCESS,
                    ResultCode.NOT_FOUND,
                    ResultCode.RESOURCE_LIMIT);
        for (var code : codes) {
          var result = result(cancel, code, AT);
          assertEquals("QuestionMutationResult[REDACTED]", result.toString());
          var completion = service.capture(request, USER, result, R, AT);
          assertEquals(AT, completion.completedAt());
          byte[] expected = wire(cancel, M, R, AT, code, AT);
          byte[] plaintext = QuestionQueryReplayServiceTest.decrypt(completion, M, 1);
          if ((code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)) {
            byte[] prefix =
                ByteBuffer.allocate(35)
                    .put("NKREF1".getBytes(StandardCharsets.US_ASCII))
                    .put((byte) (cancel ? 2 : 1))
                    .putLong(cancel ? 7 : 3)
                    .putLong(TOKEN.getMostSignificantBits())
                    .putLong(TOKEN.getLeastSignificantBits())
                    .putInt(expected.length)
                    .array();
            var whole = new ByteArrayOutputStream();
            whole.write(prefix);
            whole.write(expected);
            assertArrayEquals(whole.toByteArray(), plaintext);
          } else {
            assertArrayEquals(expected, plaintext);
            assertEquals(InboxResultReference.none(), completion.resultReference());
          }
          byte[] cipher = completion.responseSnapshot().orElseThrow().ciphertext();
          for (boolean replay : List.of(false, true)) {
            var saved =
                service.read(
                    request,
                    USER,
                    new BoundInboxExecution(
                        M,
                        replay
                            ? InboxExecution.replay(completion)
                            : InboxExecution.executed(completion)));
            assertEquals(code, saved.resultCode());
            assertEquals(replay, saved.replay());
            assertEquals(completion.resultReference(), saved.reference());
            assertEquals("QuestionMutationSnapshot[REDACTED]", saved.toString());
            assertArrayEquals(
                wire(
                    cancel,
                    M,
                    NEXT,
                    LATER,
                    replay && (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)
                        ? ResultCode.IDEMPOTENT_SUCCESS
                        : code,
                    AT),
                service.reply(saved, request, ADMIN, NEXT, LATER));
          }
          assertArrayEquals(cipher, completion.responseSnapshot().orElseThrow().ciphertext());
        }
        for (var code :
            List.of(
                ResultCode.SESSION_INVALID,
                ResultCode.FORBIDDEN,
                ResultCode.NOT_FOUND,
                ResultCode.CONFLICT,
                ResultCode.TEMPORARY_FAILURE))
          assertArrayEquals(
              wire(cancel, M, R, AT, code, AT), service.failure(request, code, R, AT));
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> service.failure(request, ResultCode.SUCCESS, R, AT));
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                service.capture(
                    request, USER, result(cancel, ResultCode.SUCCESS, AT.plusMillis(1)), R, AT));
      }
    }
  }

  @Test
  void qry038AuthenticatedMetadataCorruptionAndClosedSnapshotCannotGrantScope() throws Exception {
    try (var keys = new ResponseSnapshotCodec(FIXTURE_KEY_ID, new byte[32], null, null)) {
      var service = new QuestionMutationReplayService(keys);
      for (boolean cancel : List.of(false, true)) {
        var request = QuestionMutationRequest.decode(message(cancel, 3, M, TOKEN));
        var completion =
            service.capture(request, USER, result(cancel, ResultCode.SUCCESS, AT), R, AT);
        var saved =
            service.read(
                request, USER, new BoundInboxExecution(M, InboxExecution.executed(completion)));
        var retry = QuestionMutationRequest.decode(message(cancel, 3, NEXT, TOKEN));
        assertThrows(
            TemporaryInfrastructureException.class, () -> service.reply(saved, retry, USER, R, AT));
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> service.reply(saved, request, new AuthenticatedActor(2, "u2", Role.USER), R, AT));
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                service.read(
                    request, USER, new BoundInboxExecution(M, InboxExecution.inProgress())));
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                service.read(
                    request,
                    USER,
                    new BoundInboxExecution(NEXT, InboxExecution.executed(completion))));
        for (String error :
            List.of(FIXTURE_LAYOUT_FIELD, "version", "missing", "time", "reference", "state")) {
          var changed =
              new InboxCompletion(
                  error.equals("state") ? InboxCompletionState.ERROR : completion.state(),
                  error.equals("reference")
                      ? InboxResultReference.none()
                      : completion.resultReference(),
                  error.equals(FIXTURE_LAYOUT_FIELD) ? "USDRSP01" : completion.responseLayoutId(),
                  error.equals("version") ? "002" : FIXTURE_LAYOUT_VERSION,
                  error.equals("missing") ? Optional.empty() : completion.responseSnapshot(),
                  error.equals("time") ? AT.plusSeconds(1) : AT);
          assertThrows(
              TemporaryInfrastructureException.class,
              () ->
                  service.read(
                      request, USER, new BoundInboxExecution(M, InboxExecution.replay(changed))),
              error);
        }
        var copied = completion.responseSnapshot().orElseThrow().ciphertext();
        copied[copied.length - 1] ^= 1;
        var broken =
            new InboxCompletion(
                completion.state(),
                completion.resultReference(),
                completion.responseLayoutId(),
                FIXTURE_LAYOUT_VERSION,
                Optional.of(new EncryptedResponseSnapshot(FIXTURE_KEY_ID, copied)),
                AT);
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                service.read(
                    request, USER, new BoundInboxExecution(M, InboxExecution.replay(broken))));
        var tokenChanged = QuestionMutationRequest.decode(message(cancel, 3, M, new UUID(711, 9)));
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                service.read(
                    tokenChanged,
                    USER,
                    new BoundInboxExecution(M, InboxExecution.replay(completion))));
      }
    }
    assertThrows(NullPointerException.class, () -> new QuestionMutationReplayService(null));
  }

  static WireMessage<FixedPayload> message(boolean cancel, long id, UUID message, UUID token) {
    byte[] data = new byte[48];
    Arrays.fill(data, (byte) 32);
    QuestionQueryRequestTest.put(data, 0, String.format(Locale.ROOT, "%012d", id));
    QuestionQueryRequestTest.put(data, 12, token.toString());
    var h =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(cancel ? "NTCREQ01" : "QDLREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            message,
            message,
            AT.truncatedTo(ChronoUnit.MILLIS),
            Optional.of(AuthenticationContext.of("b".repeat(64))),
            256,
            48,
            0,
            0,
            304,
            Optional.empty());
    return new WireMessage<>(h, new FixedPayload(data, 0, List.of()));
  }

  @Test
  void qry046ClosedResultNullAndAuthenticatedWrongKindLayoutStateCannotBecomeReplay()
      throws Exception {
    var cancel = QuestionMutationRequest.decode(message(true, 3, M, TOKEN));
    var delete = QuestionMutationRequest.decode(message(false, 3, M, TOKEN));
    assertThrows(NullPointerException.class, () -> cancel.canonical(null));
    assertThrows(NullPointerException.class, () -> cancel.validate(null));
    assertThrows(NullPointerException.class, () -> cancel.apply(null, null, USER, null));
    for (boolean c : List.of(false, true)) {
      var good = result(c, ResultCode.SUCCESS, AT);
      assertThrows(
          NullPointerException.class,
          () -> new QuestionMutationRequest.Result(null, good.payload(), good.reference()));
      assertThrows(
          NullPointerException.class,
          () -> new QuestionMutationRequest.Result(good.code(), null, good.reference()));
      assertThrows(
          NullPointerException.class,
          () -> new QuestionMutationRequest.Result(good.code(), good.payload(), null));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new QuestionMutationRequest.Result(
                  ResultCode.SUCCESS, good.payload(), InboxResultReference.none()));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new QuestionMutationRequest.Result(
                  ResultCode.NOT_FOUND, good.payload(), good.reference()));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new QuestionMutationRequest.Result(
                  ResultCode.NOT_FOUND,
                  new PayloadValues(new LayoutId("LOGRSP01"), FieldValueSet.empty(), List.of()),
                  InboxResultReference.none()));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new QuestionMutationRequest.Result(
                  ResultCode.NOT_FOUND,
                  new PayloadValues(
                      good.payload().layoutId(),
                      FieldValueSet.empty(),
                      List.of(FieldValueSet.empty())),
                  InboxResultReference.none()));
      for (var invalid :
          List.of(ResultCode.SESSION_INVALID, ResultCode.FORBIDDEN, ResultCode.CONFLICT))
        assertThrows(
            IllegalArgumentException.class,
            () ->
                new QuestionMutationRequest.Result(
                    invalid,
                    new PayloadValues(good.payload().layoutId(), FieldValueSet.empty(), List.of()),
                    InboxResultReference.none()));
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new QuestionMutationRequest.Result(
                ResultCode.NOT_CANCELLABLE,
                new PayloadValues(
                    new LayoutId(FIXTURE_DELETE_RESPONSE), FieldValueSet.empty(), List.of()),
                InboxResultReference.none()));
    for (var state :
        List.of(
            Optional.of(NotificationState.PROCESSING), Optional.of(NotificationState.CANCELLED))) {
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new QuestionMutationRequest.Result(
                  ResultCode.SUCCESS,
                  new PayloadValues(
                      new LayoutId(FIXTURE_CANCEL_RESPONSE),
                      new NotificationCancelResponseData(state, Optional.empty()).fields(),
                      List.of()),
                  InboxResultReference.numeric(InboxResultReferenceType.JOB, 7)));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> cancel.validate(result(false, ResultCode.SUCCESS, AT)));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            delete.validate(
                new QuestionMutationRequest.Result(
                    ResultCode.SUCCESS,
                    result(false, ResultCode.SUCCESS, AT).payload(),
                    InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 9))));
    for (boolean time : List.of(false, true)) {
      var bad =
          new QuestionMutationRequest.Result(
              ResultCode.NOT_CANCELLABLE,
              new PayloadValues(
                  new LayoutId(FIXTURE_CANCEL_RESPONSE),
                  new NotificationCancelResponseData(
                          Optional.of(
                              time ? NotificationState.PROCESSING : NotificationState.CANCELLED),
                          time ? Optional.of(AT.truncatedTo(ChronoUnit.MILLIS)) : Optional.empty())
                      .fields(),
                  List.of()),
              InboxResultReference.none());
      assertThrows(IllegalArgumentException.class, () -> cancel.validate(bad));
    }
    try (var keys = new ResponseSnapshotCodec(FIXTURE_KEY_ID, new byte[32], null, null)) {
      var service = new QuestionMutationReplayService(keys);
      for (String point : List.of("kind", FIXTURE_LAYOUT_FIELD, "success-error", "code")) {
        byte[] malformed =
            wire(
                false,
                M,
                R,
                AT,
                point.equals("success-error")
                    ? ResultCode.SUCCESS
                    : point.equals("code") ? ResultCode.SESSION_INVALID : ResultCode.NOT_FOUND,
                AT);
        if (point.equals("kind")) QuestionQueryRequestTest.put(malformed, 22, "R");
        if (point.equals(FIXTURE_LAYOUT_FIELD))
          QuestionQueryRequestTest.put(malformed, 11, "LOGRSP01");
        var encrypted =
            QuestionQueryReplayServiceTest.encrypt(malformed, M, 1, FIXTURE_DELETE_RESPONSE);
        var completion =
            new InboxCompletion(
                InboxCompletionState.ERROR,
                InboxResultReference.none(),
                FIXTURE_DELETE_RESPONSE,
                FIXTURE_LAYOUT_VERSION,
                Optional.of(encrypted),
                AT);
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                service.read(
                    delete, USER, new BoundInboxExecution(M, InboxExecution.replay(completion))),
            point);
      }
      var good = result(false, ResultCode.SUCCESS, AT);
      var completed = service.capture(delete, USER, good, R, AT);
      var saved =
          service.read(
              delete, USER, new BoundInboxExecution(M, InboxExecution.executed(completed)));
      Object[] capture = {delete, USER, good, R, AT};
      for (int i = 0; i < capture.length; i++) {
        var args = capture.clone();
        args[i] = null;
        assertThrows(
            NullPointerException.class,
            () ->
                service.capture(
                    (QuestionMutationRequest) args[0],
                    (AuthenticatedActor) args[1],
                    (QuestionMutationRequest.Result) args[2],
                    (UUID) args[3],
                    (Instant) args[4]));
      }
      assertThrows(
          NullPointerException.class,
          () ->
              service.read(
                  null, USER, new BoundInboxExecution(M, InboxExecution.executed(completed))));
      assertThrows(
          NullPointerException.class,
          () ->
              service.read(
                  delete, null, new BoundInboxExecution(M, InboxExecution.executed(completed))));
      assertThrows(NullPointerException.class, () -> service.read(delete, USER, null));
      Object[] reply = {saved, delete, USER, R, AT};
      for (int i = 0; i < reply.length; i++) {
        var args = reply.clone();
        args[i] = null;
        assertThrows(
            NullPointerException.class,
            () ->
                service.reply(
                    (QuestionMutationReplayService.Snapshot) args[0],
                    (QuestionMutationRequest) args[1],
                    (AuthenticatedActor) args[2],
                    (UUID) args[3],
                    (Instant) args[4]));
      }
      Object[] failure = {delete, ResultCode.NOT_FOUND, R, AT};
      for (int i = 0; i < failure.length; i++) {
        var args = failure.clone();
        args[i] = null;
        assertThrows(
            NullPointerException.class,
            () ->
                service.failure(
                    (QuestionMutationRequest) args[0],
                    (ResultCode) args[1],
                    (UUID) args[2],
                    (Instant) args[3]));
      }
    }
  }

  static QuestionMutationRequest.Result result(boolean cancel, ResultCode code, Instant at) {
    FieldValueSet fields;
    if (cancel)
      fields =
          new NotificationCancelResponseData(
                  (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)
                      ? Optional.of(NotificationState.CANCELLED)
                      : code == ResultCode.NOT_CANCELLABLE
                          ? Optional.of(NotificationState.PROCESSING)
                          : Optional.empty(),
                  (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)
                      ? Optional.of(at.truncatedTo(ChronoUnit.MILLIS))
                      : Optional.empty())
              .fields();
    else
      fields =
          (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)
              ? new QuestionDeleteResponseData(at.truncatedTo(ChronoUnit.MILLIS)).fields()
              : FieldValueSet.empty();
    return new QuestionMutationRequest.Result(
        code,
        new PayloadValues(
            new LayoutId(cancel ? FIXTURE_CANCEL_RESPONSE : FIXTURE_DELETE_RESPONSE),
            fields,
            List.of()),
        (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)
            ? InboxResultReference.numeric(
                cancel ? InboxResultReferenceType.JOB : InboxResultReferenceType.QUESTION,
                cancel ? 7 : 3)
            : InboxResultReference.none());
  }

  static byte[] wire(
      boolean cancel,
      UUID source,
      UUID response,
      Instant sent,
      ResultCode code,
      Instant operation) {
    int len = cancel ? 32 : 24;
    byte[] b = new byte[256 + len];
    Arrays.fill(b, (byte) 32);
    QuestionQueryRequestTest.put(b, 0, "SCHBNK01001");
    QuestionQueryRequestTest.put(b, 11, cancel ? FIXTURE_CANCEL_RESPONSE : FIXTURE_DELETE_RESPONSE);
    QuestionQueryRequestTest.put(b, 19, "001SS");
    QuestionQueryRequestTest.put(b, 24, response.toString());
    QuestionQueryRequestTest.put(b, 60, source.toString());
    QuestionQueryRequestTest.put(b, 96, QuestionSubmissionServiceTest.date(sent));
    QuestionQueryRequestTest.put(b, 113, "b".repeat(64));
    QuestionQueryRequestTest.put(
        b,
        177,
        "0256"
            + String.format(Locale.ROOT, "%06d", len)
            + "000000000000"
            + String.format(Locale.ROOT, "%09d", 256 + len));
    QuestionQueryRequestTest.put(b, 208, code.wireValue());
    if (cancel) {
      if ((code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)) {
        QuestionQueryRequestTest.put(b, 256, "CANCELLED");
        QuestionQueryRequestTest.put(b, 268, QuestionSubmissionServiceTest.date(operation));
      } else if (code == ResultCode.NOT_CANCELLABLE)
        QuestionQueryRequestTest.put(b, 256, "PROCESSING");
    } else {
      QuestionQueryRequestTest.put(
          b,
          256,
          (code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)
              ? QuestionSubmissionServiceTest.date(operation)
              : "0".repeat(17));
    }
    return b;
  }
}
