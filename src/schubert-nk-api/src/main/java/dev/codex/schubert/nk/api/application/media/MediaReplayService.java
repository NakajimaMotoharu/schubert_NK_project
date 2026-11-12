package dev.codex.schubert.nk.api.application.media;

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
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
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
 * Frozen media query responses, never DB/file/JMS or current authorization. NK-MED-001/NK-MSG-002;
 * FUN-005..007/MQ-006..010/DAT-009; UI232/235/241/237; SS312/323/324/333/352; PG-D-079;
 * PT-MED-050..054. Caller owns keys, final auth/Inbox HMAC and physical verification.
 */
public final class MediaReplayService {
  private static final java.lang.String LITERAL_REQUEST = "request";

  private static final java.lang.String LITERAL_ACTOR = "actor";

  private static final java.lang.String LITERAL_RESPONSEID = "responseId";

  private final ResponseSnapshotCodec snapshots;

  public MediaReplayService(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  /** Opaque verified saved bytes; descriptor is not current physical admission or a principal. */
  public static final class Snapshot {
    private final ResponseSnapshotIdentity identity;
    private final PayloadValues values;
    private final ResultCode code;
    private final Optional<MediaDescriptor> retainedDescriptor;

    private Snapshot(
        ResponseSnapshotIdentity identity,
        PayloadValues values,
        ResultCode code,
        Optional<MediaDescriptor> descriptor) {
      this.identity = identity;
      this.values = values;
      this.code = code;
      this.retainedDescriptor = descriptor;
    }

    public ResultCode resultCode() {
      return code;
    }

    public Optional<MediaDescriptor> descriptor() {
      return retainedDescriptor;
    }

    @Override
    public String toString() {
      return "MediaSnapshot[REDACTED]";
    }
  }

  public InboxCompletion captureSuccess(
      MediaRequest request,
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
      PayloadValues values = PayloadTypeCatalog.encode(response);
      request.descriptor(response);
      return capture(request, actor, values, ResultCode.SUCCESS, responseId, completedAt);
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  /** Only definite query results persist; never turn auth/IO failure into a durable result. */
  public InboxCompletion captureFailure(
      MediaRequest request,
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

  public Snapshot read(MediaRequest request, AuthenticatedActor actor, InboxCompletion completion) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(completion, "completion");
    try {
      require(completion.responseLayoutId().equals(request.responseLayoutId().value()));
      require(completion.responseVersion().equals("001"));
      require(completion.resultReference().equals(InboxResultReference.none()));
      var identity = identity(request, actor);
      byte[] body =
          snapshots.decrypt(
              identity, completion.responseSnapshot().orElseThrow(IllegalArgumentException::new));
      try {
        CommonHeader header = HeaderCodec.standard().peek(body);
        require(header.layoutId().equals(request.responseLayoutId()));
        header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
        require(body.length == header.totalLength());
        require(header.correlationId().equals(request.header().messageId()));
        require(header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
        ResultCode code = header.resultCode().orElseThrow(IllegalArgumentException::new);
        if (code == ResultCode.SUCCESS)
          require(completion.state() == InboxCompletionState.COMPLETED);
        else {
          require(persistentError(request, code));
          require(completion.state() == InboxCompletionState.ERROR);
        }
        byte[] data = Arrays.copyOfRange(body, 256, 256 + header.dataLength());
        List<byte[]> records = new ArrayList<>();
        try {
          int offset = 256 + header.dataLength();
          for (int i = 0; i < header.recordCount(); i++) {
            records.add(Arrays.copyOfRange(body, offset, offset + header.recordLength()));
            offset += header.recordLength();
          }
          var values = PayloadCodec.standard().decode(header.layoutId(), data, records, code);
          var descriptor =
              code == ResultCode.SUCCESS
                  ? request.descriptor(PayloadTypeCatalog.decode(values))
                  : Optional.<MediaDescriptor>empty();
          return new Snapshot(identity, values, code, descriptor);
        } finally {
          Arrays.fill(data, (byte) 0);
          records.forEach(record -> Arrays.fill(record, (byte) 0));
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

  /** New header after caller's final owner/Inbox checks; successful replay alone becomes 0200. */
  public byte[] reply(
      Snapshot saved,
      MediaRequest request,
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
      require(saved.identity.equals(identity(request, actor)));
      if (saved.code == ResultCode.SUCCESS)
        request.descriptor(PayloadTypeCatalog.decode(saved.values));
      ResultCode code =
          replay && saved.code == ResultCode.SUCCESS ? ResultCode.IDEMPOTENT_SUCCESS : saved.code;
      return wire(request, saved.values, code, responseId, sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  /** Nonpersistent auth/temporary response, or a definite failure; never a success profile. */
  public byte[] failure(MediaRequest request, ResultCode code, UUID responseId, Instant sentAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(code, "code");
    Objects.requireNonNull(responseId, LITERAL_RESPONSEID);
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(
          code == ResultCode.SESSION_INVALID
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
      MediaRequest request,
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

  private static boolean persistentError(MediaRequest request, ResultCode code) {
    return code == ResultCode.RESOURCE_LIMIT
        || (code == ResultCode.NOT_FOUND && request.descriptorRequest());
  }

  private static PayloadValues empty(MediaRequest request) {
    return new PayloadValues(request.responseLayoutId(), FieldValueSet.empty(), List.of());
  }

  private static ResponseSnapshotIdentity identity(MediaRequest request, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        request.header().messageId(), request.responseLayoutId().value(), "001", actor.userId());
  }

  private static byte[] wire(
      MediaRequest request,
      PayloadValues values,
      ResultCode code,
      UUID responseId,
      Instant sentAt) {
    FixedPayload payload = PayloadCodec.standard().encode(values, code);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            values.layoutId(),
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
    if (!valid) throw new IllegalArgumentException("saved media result is inconsistent");
  }
}
