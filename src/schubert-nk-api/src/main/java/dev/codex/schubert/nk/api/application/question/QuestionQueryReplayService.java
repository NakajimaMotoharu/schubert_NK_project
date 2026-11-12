package dev.codex.schubert.nk.api.application.question;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.QuestionQueryScopeFrame;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Frozen Question/Notification list/detail, never current DB state, authentication, transaction or
 * JMS handling. NK-QRY-001/NK-NTF-001; QST005..010/NTF001..012/MQ006..010; UI224232236241;
 * SS324/352; SSC157/PG-D-330/PT-QRY013..017/NTF010. Caller verifies current auth, scope and Inbox
 * HMAC.
 */
public final class QuestionQueryReplayService {
  private static final java.lang.String LITERAL_ACTOR = "actor";

  private static final java.lang.String LITERAL_REQUEST = "request";

  private static final java.lang.String LITERAL_RESPONSEID = "responseId";

  private final ResponseSnapshotCodec snapshots;

  public QuestionQueryReplayService(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  public static final class Snapshot {
    private final QuestionQueryRequest request;
    private final long owner;
    private final Role capturedScope;
    private final PayloadValues values;
    private final ResultCode code;

    private Snapshot(
        QuestionQueryRequest request,
        long owner,
        Role capturedScope,
        PayloadValues values,
        ResultCode code) {
      this.request = request;
      this.owner = owner;
      this.capturedScope = capturedScope;
      this.values = values;
      this.code = code;
    }

    /** SSC157: captured USER remains narrow; captured ADMIN cannot be returned to current USER. */
    public boolean scopeAllowed(AuthenticatedActor actor) {
      Objects.requireNonNull(actor, LITERAL_ACTOR);
      return owner == actor.userId()
          && (!request.questionScope() || capturedScope == Role.USER || actor.role() == Role.ADMIN);
    }

    @Override
    public String toString() {
      return "QuestionQuerySnapshot[REDACTED]";
    }
  }

  public InboxCompletion captureSuccess(
      QuestionQueryRequest request,
      AuthenticatedActor actor,
      TypedPayloadValues response,
      UUID responseId,
      Instant completedAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(responseId, LITERAL_RESPONSEID);
    Objects.requireNonNull(completedAt, "completedAt");
    try {
      request.validateResponse(response);
      return capture(
          request,
          actor,
          PayloadTypeCatalog.encode(response),
          ResultCode.SUCCESS,
          responseId,
          completedAt);
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  public InboxCompletion captureFailure(
      QuestionQueryRequest request,
      AuthenticatedActor actor,
      ResultCode code,
      UUID responseId,
      Instant completedAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(code, "code");
    Objects.requireNonNull(responseId, LITERAL_RESPONSEID);
    Objects.requireNonNull(completedAt, "completedAt");
    try {
      require(persistentError(request, code));
      return capture(request, actor, empty(request), code, responseId, completedAt);
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  public Snapshot read(
      QuestionQueryRequest request, AuthenticatedActor actor, InboxCompletion completion) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(completion, "completion");
    try {
      require(completion.responseLayoutId().equals(request.responseLayoutId().value()));
      require(completion.responseVersion().equals("001"));
      require(completion.resultReference().equals(InboxResultReference.none()));
      byte[] plaintext =
          snapshots.decrypt(
              identity(request, actor),
              completion.responseSnapshot().orElseThrow(IllegalArgumentException::new));
      try {
        Role scope =
            request.questionScope()
                ? QuestionQueryScopeFrame.capturedScope(plaintext)
                : actor.role();
        byte[] body =
            request.questionScope()
                ? Arrays.copyOfRange(plaintext, 8, plaintext.length)
                : plaintext.clone();
        try {
          var header = HeaderCodec.standard().peek(body);
          require(header.layoutId().equals(request.responseLayoutId()));
          require(header.totalLength() == body.length);
          require(header.correlationId().equals(request.header().messageId()));
          require(header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
          var code = header.resultCode().orElseThrow(IllegalArgumentException::new);
          if (code == ResultCode.SUCCESS)
            require(completion.state() == InboxCompletionState.COMPLETED);
          else {
            require(persistentError(request, code));
            require(completion.state() == InboxCompletionState.ERROR);
          }
          byte[] data = Arrays.copyOfRange(body, 256, 256 + header.dataLength());
          var records = new ArrayList<byte[]>();
          try {
            int offset = 256 + header.dataLength();
            for (int i = 0; i < header.recordCount(); i++) {
              records.add(Arrays.copyOfRange(body, offset, offset + header.recordLength()));
              offset += header.recordLength();
            }
            var values = PayloadCodec.standard().decode(header.layoutId(), data, records, code);
            if (code == ResultCode.SUCCESS)
              request.validateResponse(PayloadTypeCatalog.decode(values));
            return new Snapshot(request, actor.userId(), scope, values, code);
          } finally {
            Arrays.fill(data, (byte) 0);
            records.forEach(r -> Arrays.fill(r, (byte) 0));
          }
        } finally {
          Arrays.fill(body, (byte) 0);
        }
      } finally {
        Arrays.fill(plaintext, (byte) 0);
      }
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  public byte[] reply(
      Snapshot saved,
      QuestionQueryRequest request,
      AuthenticatedActor actor,
      UUID responseId,
      Instant sentAt,
      boolean replay) {
    Objects.requireNonNull(saved, "saved");
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(responseId, LITERAL_RESPONSEID);
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(saved.request == request);
      require(saved.scopeAllowed(actor));
      return wire(
          request,
          saved.values,
          replay && saved.code == ResultCode.SUCCESS ? ResultCode.IDEMPOTENT_SUCCESS : saved.code,
          responseId,
          sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  public byte[] failure(
      QuestionQueryRequest request, ResultCode code, UUID responseId, Instant sentAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(code, "code");
    Objects.requireNonNull(responseId, LITERAL_RESPONSEID);
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(
          code == ResultCode.VALIDATION_ERROR
              || code == ResultCode.SESSION_INVALID
              || code == ResultCode.FORBIDDEN
              || code == ResultCode.TEMPORARY_FAILURE
              || persistentError(request, code));
      return wire(request, empty(request), code, responseId, sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private InboxCompletion capture(
      QuestionQueryRequest request,
      AuthenticatedActor actor,
      PayloadValues values,
      ResultCode code,
      UUID responseId,
      Instant completedAt) {
    byte[] body = wire(request, values, code, responseId, completedAt);
    byte[] plaintext =
        request.questionScope() ? QuestionQueryScopeFrame.wrap(actor.role(), body) : body.clone();
    try {
      return new InboxCompletion(
          code == ResultCode.SUCCESS ? InboxCompletionState.COMPLETED : InboxCompletionState.ERROR,
          InboxResultReference.none(),
          request.responseLayoutId().value(),
          "001",
          Optional.of(snapshots.encrypt(identity(request, actor), plaintext)),
          completedAt.truncatedTo(ChronoUnit.MICROS));
    } finally {
      Arrays.fill(body, (byte) 0);
      Arrays.fill(plaintext, (byte) 0);
    }
  }

  private static boolean persistentError(QuestionQueryRequest request, ResultCode code) {
    return (code == ResultCode.NOT_FOUND && request.detailRequest())
        || (code == ResultCode.RESOURCE_LIMIT && !request.detailRequest());
  }

  private static PayloadValues empty(QuestionQueryRequest request) {
    return new PayloadValues(request.responseLayoutId(), FieldValueSet.empty(), List.of());
  }

  private static ResponseSnapshotIdentity identity(
      QuestionQueryRequest request, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        request.header().messageId(), request.responseLayoutId().value(), "001", actor.userId());
  }

  private static byte[] wire(
      QuestionQueryRequest request,
      PayloadValues values,
      ResultCode code,
      UUID responseId,
      Instant sentAt) {
    var payload = PayloadCodec.standard().encode(values, code);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            request.responseLayoutId(),
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            responseId,
            request.header().messageId(),
            sentAt.truncatedTo(ChronoUnit.MILLIS),
            request.header().authenticationContext(),
            256,
            payload.dataLength(),
            payload.recordLength(),
            payload.recordCount(),
            256 + payload.dataLength() + payload.recordLength() * payload.recordCount(),
            Optional.of(code));
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("saved question query is inconsistent");
  }
}
