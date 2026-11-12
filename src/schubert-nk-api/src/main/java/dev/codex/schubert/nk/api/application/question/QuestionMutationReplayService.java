package dev.codex.schubert.nk.api.application.question;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.BoundInboxExecution;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.idempotency.ResultBoundResponseSnapshotCodec;
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
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteResponseData;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Frozen NTC/QDL wire plus authenticated NKREF1 success binding. No live authorization or DB/JMS
 * ownership. Caller rechecks current result scope before commit/reply. NK-QRY-001/NTF-001;
 * SS324§6/12.9,352§11.2.1/UI232236; QA046; PG-D331; PT-QRY033/NTF016.
 */
public final class QuestionMutationReplayService {
  private static final java.lang.String LITERAL_REQUEST = "request";

  private final ResponseSnapshotCodec snapshots;
  private final ResultBoundResponseSnapshotCodec bound;

  public QuestionMutationReplayService(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    this.bound = new ResultBoundResponseSnapshotCodec(snapshots);
  }

  public static final class Snapshot {
    private final QuestionMutationRequest request;
    private final long owner;
    private final QuestionMutationRequest.Result result;
    private final boolean retainedReplay;

    private Snapshot(
        QuestionMutationRequest request,
        long owner,
        QuestionMutationRequest.Result result,
        boolean replay) {
      this.request = request;
      this.owner = owner;
      this.result = result;
      this.retainedReplay = replay;
    }

    public ResultCode resultCode() {
      return result.code();
    }

    public InboxResultReference reference() {
      return result.reference();
    }

    public boolean replay() {
      return retainedReplay;
    }

    @Override
    public String toString() {
      return "QuestionMutationSnapshot[REDACTED]";
    }
  }

  public InboxCompletion capture(
      QuestionMutationRequest request,
      AuthenticatedActor actor,
      QuestionMutationRequest.Result result,
      UUID responseId,
      Instant completedAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(result, "result");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(completedAt, "completedAt");
    try {
      request.validate(result);
      validateTime(result, completedAt);
      byte[] wire = wire(request, result.payload(), result.code(), responseId, completedAt);
      try {
        var identity = identity(request.header().messageId(), request, actor);
        var encrypted =
            result.code().usesSuccessProfile()
                ? bound.encrypt(identity, result.reference(), request.operationToken(), wire)
                : snapshots.encrypt(identity, wire);
        return new InboxCompletion(
            result.code().usesSuccessProfile()
                ? InboxCompletionState.COMPLETED
                : InboxCompletionState.ERROR,
            result.reference(),
            request.responseLayoutId().value(),
            "001",
            Optional.of(encrypted),
            completedAt.truncatedTo(ChronoUnit.MICROS));
      } finally {
        Arrays.fill(wire, (byte) 0);
      }
    } catch (ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  public Snapshot read(
      QuestionMutationRequest request, AuthenticatedActor actor, BoundInboxExecution execution) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(execution, "execution");
    try {
      var status = execution.execution().status();
      require(status != InboxExecutionStatus.IN_PROGRESS);
      if (status == InboxExecutionStatus.EXECUTED)
        require(execution.sourceMessageId().equals(request.header().messageId()));
      var completion =
          execution.execution().completion().orElseThrow(IllegalArgumentException::new);
      require(
          completion.responseLayoutId().equals(request.responseLayoutId().value())
              && completion.responseVersion().equals("001"));
      var identity = identity(execution.sourceMessageId(), request, actor);
      var encrypted = completion.responseSnapshot().orElseThrow(IllegalArgumentException::new);
      byte[] wire =
          completion.state() == InboxCompletionState.COMPLETED
              ? bound.decrypt(
                  identity, completion.resultReference(), request.operationToken(), encrypted)
              : snapshots.decrypt(identity, encrypted);
      try {
        require(wire.length == (request.cancellation() ? 288 : 280));
        var header = HeaderCodec.standard().peek(wire);
        // peek enforces registry kind/dimensions. Our expected response layout binds that
        // validation to this request; a second kind comparison would add no distinct gate.
        require(header.layoutId().equals(request.responseLayoutId()));
        require(header.correlationId().equals(execution.sourceMessageId()));
        require(header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
        var code = header.resultCode().orElseThrow(IllegalArgumentException::new);
        require(
            code.usesSuccessProfile() == (completion.state() == InboxCompletionState.COMPLETED));
        byte[] data = Arrays.copyOfRange(wire, 256, wire.length);
        try {
          var result =
              new QuestionMutationRequest.Result(
                  code,
                  PayloadCodec.standard().decode(header.layoutId(), data, List.of(), code),
                  completion.resultReference());
          request.validate(result);
          validateTime(result, completion.completedAt());
          return new Snapshot(
              request, actor.userId(), result, status == InboxExecutionStatus.REPLAY);
        } finally {
          Arrays.fill(data, (byte) 0);
        }
      } finally {
        Arrays.fill(wire, (byte) 0);
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
      QuestionMutationRequest request,
      AuthenticatedActor actor,
      UUID responseId,
      Instant sentAt) {
    Objects.requireNonNull(saved, "snapshot");
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(saved.request == request && saved.owner == actor.userId());
      request.validate(saved.result);
      var code =
          saved.retainedReplay && saved.result.code().usesSuccessProfile()
              ? ResultCode.IDEMPOTENT_SUCCESS
              : saved.result.code();
      return wire(request, saved.result.payload(), code, responseId, sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  /** Nonstored authentication/scope/identity denial only; definite stored errors use capture. */
  public byte[] failure(
      QuestionMutationRequest request, ResultCode code, UUID responseId, Instant sentAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(code, "code");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(
          Set.of(
                  ResultCode.SESSION_INVALID,
                  ResultCode.FORBIDDEN,
                  ResultCode.NOT_FOUND,
                  ResultCode.CONFLICT,
                  ResultCode.TEMPORARY_FAILURE)
              .contains(code));
      return wire(
          request,
          new PayloadValues(request.responseLayoutId(), FieldValueSet.empty(), List.of()),
          code,
          responseId,
          sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private static void validateTime(QuestionMutationRequest.Result result, Instant completed) {
    if (!result.code().usesSuccessProfile()) return;
    Instant time =
        result.payload().layoutId().value().equals("NTCRSP01")
            ? NotificationCancelResponseData.from(result.payload().data())
                .cancelledAt()
                .orElseThrow(IllegalArgumentException::new)
            : QuestionDeleteResponseData.from(result.payload().data()).deletedAt();
    require(!time.isAfter(completed));
  }

  private static ResponseSnapshotIdentity identity(
      UUID source, QuestionMutationRequest request, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        source, request.responseLayoutId().value(), "001", actor.userId());
  }

  private static byte[] wire(
      QuestionMutationRequest request, PayloadValues values, ResultCode code, UUID id, Instant at) {
    var payload = PayloadCodec.standard().encode(values, code);
    int length = request.cancellation() ? 32 : 24;
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            request.responseLayoutId(),
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            id,
            request.header().messageId(),
            at.truncatedTo(ChronoUnit.MILLIS),
            request.header().authenticationContext(),
            256,
            length,
            0,
            0,
            256 + length,
            Optional.of(code));
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("saved question mutation is inconsistent");
  }
}
