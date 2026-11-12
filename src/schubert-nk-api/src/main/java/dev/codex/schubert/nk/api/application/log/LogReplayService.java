package dev.codex.schubert.nk.api.application.log;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
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
 * Frozen Log records, never current DB state, authentication, transaction or JMS handling.
 * NK-ADM-001/NK-MSG-002; FUN-008/MQ-006..010/DAT-009; UI232/235/241/242; SS324 §6/352;
 * SSC-037/PG-D-091/PT-ADM-064..066. Caller verifies current ADMIN and Inbox HMAC separately.
 */
public final class LogReplayService {
  private static final java.lang.String LITERAL_REQUEST = "request";

  private static final java.lang.String LITERAL_ACTOR = "actor";

  private static final java.lang.String LITERAL_RESPONSEID = "responseId";

  private final ResponseSnapshotCodec snapshots;

  public LogReplayService(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  public static final class Snapshot {
    private final LogRequest request;
    private final long owner;
    private final PayloadValues values;
    private final ResultCode code;

    private Snapshot(LogRequest request, long owner, PayloadValues values, ResultCode code) {
      this.request = request;
      this.owner = owner;
      this.values = values;
      this.code = code;
    }

    @Override
    public String toString() {
      return "LogSnapshot[REDACTED]";
    }
  }

  public InboxCompletion captureSuccess(
      LogRequest request,
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
      requireAdmin(actor);
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
      LogRequest request,
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
      requireAdmin(actor);
      require(persistentError(code));
      return capture(request, actor, empty(request), code, responseId, completedAt);
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  public Snapshot read(LogRequest request, AuthenticatedActor actor, InboxCompletion completion) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(completion, "completion");
    try {
      requireAdmin(actor);
      require(completion.responseLayoutId().equals(request.responseLayoutId().value()));
      require(completion.responseVersion().equals("001"));
      require(completion.resultReference().equals(InboxResultReference.none()));
      byte[] body =
          snapshots.decrypt(
              identity(request, actor),
              completion.responseSnapshot().orElseThrow(IllegalArgumentException::new));
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
          require(persistentError(code));
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
          return new Snapshot(request, actor.userId(), values, code);
        } finally {
          Arrays.fill(data, (byte) 0);
          records.forEach(r -> Arrays.fill(r, (byte) 0));
        }
      } finally {
        Arrays.fill(body, (byte) 0);
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
      LogRequest request,
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
      requireAdmin(actor);
      require(saved.request == request);
      require(saved.owner == actor.userId());
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

  public byte[] failure(LogRequest request, ResultCode code, UUID responseId, Instant sentAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(code, "code");
    Objects.requireNonNull(responseId, LITERAL_RESPONSEID);
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(
          code == ResultCode.SESSION_INVALID
              || code == ResultCode.FORBIDDEN
              || code == ResultCode.TEMPORARY_FAILURE
              || persistentError(code));
      return wire(request, empty(request), code, responseId, sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private InboxCompletion capture(
      LogRequest request,
      AuthenticatedActor actor,
      PayloadValues values,
      ResultCode code,
      UUID responseId,
      Instant completedAt) {
    byte[] body = wire(request, values, code, responseId, completedAt);
    try {
      return new InboxCompletion(
          code == ResultCode.SUCCESS ? InboxCompletionState.COMPLETED : InboxCompletionState.ERROR,
          InboxResultReference.none(),
          request.responseLayoutId().value(),
          "001",
          Optional.of(snapshots.encrypt(identity(request, actor), body)),
          completedAt.truncatedTo(ChronoUnit.MICROS));
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  private static boolean persistentError(ResultCode code) {
    return code == ResultCode.RESOURCE_LIMIT;
  }

  private static PayloadValues empty(LogRequest request) {
    return new PayloadValues(request.responseLayoutId(), FieldValueSet.empty(), List.of());
  }

  private static ResponseSnapshotIdentity identity(LogRequest request, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        request.header().messageId(), request.responseLayoutId().value(), "001", actor.userId());
  }

  private static byte[] wire(
      LogRequest request, PayloadValues values, ResultCode code, UUID responseId, Instant sentAt) {
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

  private static void requireAdmin(AuthenticatedActor actor) {
    require(actor.role() == Role.ADMIN);
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("saved log query is inconsistent");
  }
}
