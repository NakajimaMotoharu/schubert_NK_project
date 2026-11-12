package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.scenario.ScenarioDetailResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.DeliveryMode;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Frozen Scenario response capture/validation/rendering without DB, physical file or JMS I/O.
 * NK-SCN-001/NK-MSG-002; FUN-003..005/MQ-006..010/DAT-009; UI232/234/237/241; SS324 §6.3/323 §9.1,
 * SSC-026/PT-SCN-009-S01..S05. Caller owns final authentication/Inbox/TX.
 */
public final class ScenarioReplayService {
  private static final java.lang.String LITERAL_REQUEST = "request";

  private static final java.lang.String LITERAL_ACTOR = "actor";

  private static final java.lang.String LITERAL_RESPONSEID = "responseId";

  private final ResponseSnapshotCodec snapshots;

  public ScenarioReplayService(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  /** The opaque result binds payload to its verified snapshot identity, never an auth principal. */
  public static final class Snapshot {
    private final ResponseSnapshotIdentity identity;
    private final CommonHeader header;
    private final PayloadValues values;
    private final ResultCode code;
    private final Optional<ScenarioDetailResponseData> retainedDetail;
    private final Optional<LargeResultDescriptor> retainedDescriptor;

    private Snapshot(
        ResponseSnapshotIdentity identity,
        CommonHeader header,
        PayloadValues values,
        ResultCode code,
        Optional<ScenarioDetailResponseData> detail,
        Optional<LargeResultDescriptor> descriptor) {
      this.identity = identity;
      this.header = header;
      this.values = values;
      this.code = code;
      this.retainedDetail = detail;
      this.retainedDescriptor = descriptor;
    }

    public ResultCode resultCode() {
      return code;
    }

    public Optional<ScenarioDetailResponseData> detail() {
      return retainedDetail;
    }

    /** Metadata validation only; caller must verify the physical file outside DB transaction. */
    public Optional<LargeResultDescriptor> descriptor() {
      return retainedDescriptor;
    }

    @Override
    public String toString() {
      return "ScenarioSnapshot[REDACTED]";
    }
  }

  public InboxCompletion captureSuccess(
      ScenarioRequest request,
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
      require(response.layoutId().equals(request.responseLayoutId()));
      PayloadValues values = PayloadTypeCatalog.encode(response);
      Optional<ScenarioDetailResponseData> detail = detail(request, response);
      Optional<LargeResultDescriptor> descriptor = descriptor(detail);
      InboxResultReference reference = reference(detail, descriptor);
      return capture(
          request, actor, values, ResultCode.SUCCESS, reference, responseId, completedAt);
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  /** Persist only definite query failures, never a session rejection or infrastructure failure. */
  public InboxCompletion captureFailure(
      ScenarioRequest request,
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
      return capture(
          request,
          actor,
          empty(request),
          code,
          InboxResultReference.none(),
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

  /**
   * Validates every saved byte and logical reference; grants no physical-file or current access.
   */
  public Snapshot read(
      ScenarioRequest request, AuthenticatedActor actor, InboxCompletion completion) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(completion, "completion");
    try {
      require(completion.responseLayoutId().equals(request.responseLayoutId().value()));
      require(completion.responseVersion().equals("001"));
      ResponseSnapshotIdentity identity = identity(request, actor);
      byte[] body =
          snapshots.decrypt(
              identity, completion.responseSnapshot().orElseThrow(IllegalArgumentException::new));
      try {
        CommonHeader header = HeaderCodec.standard().peek(body);
        require(header.layoutId().equals(request.responseLayoutId()));
        require(body.length == header.totalLength());
        require(header.correlationId().equals(request.header().messageId()));
        require(header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
        ResultCode code = header.resultCode().orElseThrow(IllegalArgumentException::new);
        if (code == ResultCode.SUCCESS) {
          require(completion.state() == InboxCompletionState.COMPLETED);
        } else {
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
          PayloadValues values =
              PayloadCodec.standard().decode(header.layoutId(), data, records, code);
          Optional<ScenarioDetailResponseData> detail =
              code == ResultCode.SUCCESS
                  ? detail(request, PayloadTypeCatalog.decode(values))
                  : Optional.empty();
          Optional<LargeResultDescriptor> descriptor = descriptor(detail);
          require(completion.resultReference().equals(reference(detail, descriptor)));
          return new Snapshot(identity, header, values, code, detail, descriptor);
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

  /**
   * Change only the verified F descriptor, retaining original header/state/reference/time. SS324
   * §7.1/SSC-027/PT-SCN-009-S06. Caller owns final row lock/CAS and physical verification.
   */
  public InboxCompletion replaceFile(
      ScenarioRequest request,
      AuthenticatedActor actor,
      InboxCompletion original,
      LargeResultDescriptor replacement) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, LITERAL_ACTOR);
    Objects.requireNonNull(original, "original");
    Objects.requireNonNull(replacement, "replacement");
    try {
      Snapshot saved = read(request, actor, original);
      require(
          ScenarioFileRegenerator.sameContent(
              saved.retainedDescriptor.orElseThrow(IllegalArgumentException::new), replacement));
      TypedPayloadValues typed =
          ScenarioDetailDelivery.fileResponse(
              saved.retainedDetail.orElseThrow(IllegalArgumentException::new), replacement);
      FixedPayload payload =
          PayloadCodec.standard().encode(PayloadTypeCatalog.encode(typed), ResultCode.SUCCESS);
      byte[] body = FixedWidthEncoder.standard().encode(new WireMessage<>(saved.header, payload));
      try {
        return new InboxCompletion(
            original.state(),
            original.resultReference(),
            original.responseLayoutId(),
            original.responseVersion(),
            Optional.of(snapshots.encrypt(saved.identity, body)),
            original.completedAt());
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

  /** Final owner must be freshly verified by caller; only successful replays change to 0200. */
  public byte[] reply(
      Snapshot saved,
      ScenarioRequest request,
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

  /** Non-persisted rejection/error response; never synthesizes a success profile. */
  public byte[] failure(ScenarioRequest request, ResultCode code, UUID responseId, Instant sentAt) {
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
      ScenarioRequest request,
      AuthenticatedActor actor,
      PayloadValues values,
      ResultCode code,
      InboxResultReference reference,
      UUID responseId,
      Instant completedAt) {
    byte[] body = wire(request, values, code, responseId, completedAt);
    try {
      return new InboxCompletion(
          code == ResultCode.SUCCESS ? InboxCompletionState.COMPLETED : InboxCompletionState.ERROR,
          reference,
          request.responseLayoutId().value(),
          "001",
          Optional.of(snapshots.encrypt(identity(request, actor), body)),
          completedAt.truncatedTo(ChronoUnit.MICROS));
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  private static Optional<ScenarioDetailResponseData> detail(
      ScenarioRequest request, TypedPayloadValues response) {
    if (response.data() instanceof ScenarioDetailResponseData detail) {
      require(detail.scriptFileId().value() == request.scriptFileId().orElseThrow());
      return Optional.of(detail);
    }
    return Optional.empty();
  }

  private static Optional<LargeResultDescriptor> descriptor(
      Optional<ScenarioDetailResponseData> detail) {
    if (detail.isEmpty() || detail.orElseThrow().deliveryMode() == DeliveryMode.INLINE)
      return Optional.empty();
    ScenarioDetailResponseData data = detail.orElseThrow();
    return Optional.of(
        new LargeResultDescriptor(
            data.fileId().orElseThrow(),
            data.fileRelativePath().orElseThrow().wireValue(),
            data.fileByteLength(),
            data.fileSha256().orElseThrow().wireValue(),
            (int) data.fileRecordCount()));
  }

  private static InboxResultReference reference(
      Optional<ScenarioDetailResponseData> detail, Optional<LargeResultDescriptor> descriptor) {
    return descriptor.isPresent()
        ? InboxResultReference.numeric(
            InboxResultReferenceType.SCENARIO_FILE, detail.orElseThrow().scriptFileId().value())
        : InboxResultReference.none();
  }

  private static boolean persistentError(ScenarioRequest request, ResultCode code) {
    return code == ResultCode.RESOURCE_LIMIT
        || (code == ResultCode.NOT_FOUND && request.scriptFileId().isPresent());
  }

  private static PayloadValues empty(ScenarioRequest request) {
    return new PayloadValues(request.responseLayoutId(), FieldValueSet.empty(), List.of());
  }

  private static ResponseSnapshotIdentity identity(
      ScenarioRequest request, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        request.header().messageId(), request.responseLayoutId().value(), "001", actor.userId());
  }

  private static byte[] wire(
      ScenarioRequest request,
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
    if (!valid) throw new IllegalArgumentException("saved scenario result is inconsistent");
  }
}
