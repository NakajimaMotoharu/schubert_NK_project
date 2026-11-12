package dev.codex.schubert.nk.api.application.admin;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.BoundInboxExecution;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
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
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Frozen User mutation results, not DB authentication/Inbox ownership or transaction management.
 * NK-ADM-001/NK-MSG-002; FUN-009/MQ-006..010/DAT-009; UI232/236/241; SS324 §6/352;
 * SSC-033/PG-D-086; PT-ADM-028..032. Caller must authenticate current ADMIN and verify HMAC.
 */
public final class UserMutationReplayService {
  private static final java.lang.String LITERAL_REQUEST = "request";

  private final ResponseSnapshotCodec snapshots;

  public UserMutationReplayService(ResponseSnapshotCodec snapshots) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
  }

  /** Verified bytes are usable only with the same current request scope and owner. */
  public static final class Snapshot {
    private final UserMutationRequest request;
    private final long owner;
    private final UserMutationResult result;
    private final boolean replay;

    private Snapshot(
        UserMutationRequest request, long owner, UserMutationResult result, boolean replay) {
      this.request = request;
      this.owner = owner;
      this.result = result;
      this.replay = replay;
    }

    @Override
    public String toString() {
      return "UserMutationSnapshot[REDACTED]";
    }
  }

  /** Preserve the initial result/version, never a later DB projection. */
  public InboxCompletion capture(
      UserMutationRequest request,
      AuthenticatedActor actor,
      UserMutationResult result,
      UUID responseId,
      Instant completedAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(result, "result");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(completedAt, "completedAt");
    try {
      requireAdmin(actor);
      validateResult(request, result);
      byte[] body = wire(request, result.data(), result.resultCode(), responseId, completedAt);
      try {
        return new InboxCompletion(
            result.resultCode().usesSuccessProfile()
                ? InboxCompletionState.COMPLETED
                : InboxCompletionState.ERROR,
            reference(result),
            request.responseLayoutId().value(),
            "001",
            Optional.of(
                snapshots.encrypt(identity(request.header().messageId(), request, actor), body)),
            completedAt.truncatedTo(ChronoUnit.MICROS));
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

  /** Saved Message PK controls AAD; current retry Message controls the later response header. */
  public Snapshot read(
      UserMutationRequest request, AuthenticatedActor actor, BoundInboxExecution bound) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(bound, "bound");
    try {
      requireAdmin(actor);
      var execution = bound.execution();
      require(execution.status() != InboxExecutionStatus.IN_PROGRESS);
      if (execution.status() == InboxExecutionStatus.EXECUTED)
        require(bound.sourceMessageId().equals(request.header().messageId()));
      var completion = execution.completion().orElseThrow(IllegalArgumentException::new);
      require(completion.responseLayoutId().equals(request.responseLayoutId().value()));
      require(completion.responseVersion().equals("001"));
      byte[] body =
          snapshots.decrypt(
              identity(bound.sourceMessageId(), request, actor),
              completion.responseSnapshot().orElseThrow(IllegalArgumentException::new));
      try {
        require(body.length == 280);
        CommonHeader header = HeaderCodec.standard().peek(body);
        require(header.layoutId().equals(request.responseLayoutId()));
        // peek already enforces registry dimensions and the calculated total. These five
        // responses have DATA24/no records, so the verified total is necessarily 280.
        require(header.correlationId().equals(bound.sourceMessageId()));
        require(header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
        var code = header.resultCode().orElseThrow(IllegalArgumentException::new);
        require(
            completion.state()
                == (code.usesSuccessProfile()
                    ? InboxCompletionState.COMPLETED
                    : InboxCompletionState.ERROR));
        byte[] data = Arrays.copyOfRange(body, 256, 280);
        try {
          var values = PayloadCodec.standard().decode(header.layoutId(), data, List.of(), code);
          var result =
              new UserMutationResult(
                  code,
                  code.usesSuccessProfile()
                      ? Optional.of(
                          (UserMutationResponseData) PayloadTypeCatalog.decode(values).data())
                      : Optional.empty());
          validateResult(request, result);
          require(completion.resultReference().equals(reference(result)));
          return new Snapshot(
              request, actor.userId(), result, execution.status() == InboxExecutionStatus.REPLAY);
        } finally {
          Arrays.fill(data, (byte) 0);
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

  /** Caller has committed and rechecked ownership; no database read or new business effect. */
  public byte[] reply(
      Snapshot saved,
      UserMutationRequest request,
      AuthenticatedActor actor,
      UUID responseId,
      Instant sentAt) {
    Objects.requireNonNull(saved, "saved");
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      requireAdmin(actor);
      require(saved.request == request);
      require(saved.owner == actor.userId());
      validateResult(request, saved.result);
      var code =
          saved.replay && saved.result.resultCode().usesSuccessProfile()
              ? ResultCode.IDEMPOTENT_SUCCESS
              : saved.result.resultCode();
      return wire(request, saved.result.data(), code, responseId, sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  /** Only an error response; auth/temporary failures are never durable Inbox completions here. */
  public byte[] failure(
      UserMutationRequest request, ResultCode code, UUID responseId, Instant sentAt) {
    Objects.requireNonNull(request, LITERAL_REQUEST);
    Objects.requireNonNull(code, "code");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(
          code == ResultCode.SESSION_INVALID
              || code == ResultCode.FORBIDDEN
              || code == ResultCode.TEMPORARY_FAILURE
              || persistentError(request, code));
      return wire(request, Optional.empty(), code, responseId, sentAt);
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private static void validateResult(UserMutationRequest request, UserMutationResult result) {
    var code = result.resultCode();
    if (!code.usesSuccessProfile()) {
      require(persistentError(request, code));
      return;
    }
    var data = result.data().orElseThrow(IllegalArgumentException::new);
    if (request.mutation() == Mutation.CREATE) {
      require(code == ResultCode.SUCCESS);
      require(data.updatedVersion() == 0);
    } else {
      require(data.userId().value() == request.targetUserId().orElseThrow());
      if (code == ResultCode.IDEMPOTENT_SUCCESS) {
        require(request.mutation() == Mutation.UNLOCK);
        require(data.updatedVersion() == request.expectedVersion());
      } else require(data.updatedVersion() == request.expectedVersion() + 1);
    }
  }

  private static boolean persistentError(UserMutationRequest request, ResultCode code) {
    return code == ResultCode.CONFLICT
        || code == ResultCode.RESOURCE_LIMIT
        || (code == ResultCode.NOT_FOUND && request.mutation() != Mutation.CREATE)
        || (code == ResultCode.VALIDATION_ERROR
            && (request.mutation() == Mutation.CREATE
                || request.mutation() == Mutation.RESET_PASSWORD));
  }

  private static InboxResultReference reference(UserMutationResult result) {
    return result.data().isPresent()
        ? InboxResultReference.numeric(
            InboxResultReferenceType.USER, result.data().orElseThrow().userId().value())
        : InboxResultReference.none();
  }

  private static ResponseSnapshotIdentity identity(
      UUID source, UserMutationRequest request, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        source, request.responseLayoutId().value(), "001", actor.userId());
  }

  private static byte[] wire(
      UserMutationRequest request,
      Optional<UserMutationResponseData> data,
      ResultCode code,
      UUID responseId,
      Instant sentAt) {
    var values =
        new PayloadValues(
            request.responseLayoutId(),
            data.isPresent() ? data.orElseThrow().fields() : FieldValueSet.empty(),
            List.of());
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
            24,
            0,
            0,
            280,
            Optional.of(code));
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static void requireAdmin(AuthenticatedActor actor) {
    require(actor.role() == Role.ADMIN);
  }

  private static void require(boolean condition) {
    if (!condition) throw new IllegalArgumentException("saved user mutation is inconsistent");
  }
}
