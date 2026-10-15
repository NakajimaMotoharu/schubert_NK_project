package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.idempotency.CanonicalField.number;

import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteResponseData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import java.sql.Connection;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Strict NTC/QDL decoding, canonical original target; no auth/Inbox grant. SS323§9/324,
 * UI236§10/13; NK-NTF-001/NK-QRY-001; PG-D331; PT-NTF016/QRY033.
 */
public final class QuestionMutationRequest {
  private final CommonHeader retainedHeader;
  private final long target;
  private final UUID token;
  private final boolean cancel;

  private QuestionMutationRequest(CommonHeader header, long target, UUID token, boolean cancel) {
    this.retainedHeader = header;
    this.target = target;
    this.token = token;
    this.cancel = cancel;
  }

  public static QuestionMutationRequest decode(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    byte[] bytes = message.payload().copyData();
    try {
      var h = message.header();
      require(Set.of("NTCREQ01", "QDLREQ01").contains(h.layoutId().value()));
      h.validateAgainst(LayoutRegistry.standard().require(h.layoutId(), 1));
      var value =
          PayloadTypeCatalog.decode(
                  PayloadCodec.standard().decode(h.layoutId(), bytes, List.of(), false))
              .data();
      if (value instanceof NotificationCancelRequestData data)
        return new QuestionMutationRequest(
            h, data.notificationId().value(), data.operationToken(), true);
      var data = (QuestionDeleteRequestData) value;
      return new QuestionMutationRequest(
          h, data.questionId().value(), data.operationToken(), false);
    } catch (PermanentProtocolException | IllegalArgumentException invalid) {
      throw new PermanentProtocolException("question mutation request is invalid");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  public CommonHeader header() {
    return retainedHeader;
  }

  public long targetId() {
    return target;
  }

  public UUID operationToken() {
    return token;
  }

  public boolean cancellation() {
    return cancel;
  }

  public LayoutId responseLayoutId() {
    return new LayoutId(cancel ? "NTCRSP01" : "QDLRSP01");
  }

  /** Caller closes returned canonical independently; token/header/context/role excluded. */
  public CanonicalRequest canonical(AuthenticatedActor actor) {
    Objects.requireNonNull(actor, "actor");
    return new CanonicalRequest(
        Long.toString(actor.userId()),
        retainedHeader.layoutId().value(),
        "001",
        (cancel ? "NOTIFICATION:" : "QUESTION:") + target,
        List.of(number(cancel ? "notificationId" : "questionId", target)));
  }

  public record Result(ResultCode code, PayloadValues payload, InboxResultReference reference) {
    public Result {
      Objects.requireNonNull(code, "code");
      Objects.requireNonNull(payload, "payload");
      Objects.requireNonNull(reference, "reference");
      boolean cancel = payload.layoutId().value().equals("NTCRSP01");
      require(cancel || payload.layoutId().value().equals("QDLRSP01"));
      require(payload.records().isEmpty());
      if (code.usesSuccessProfile()) {
        require(
            reference.type()
                == (cancel ? InboxResultReferenceType.JOB : InboxResultReferenceType.QUESTION));
        require(reference.numericId().isPresent());
        PayloadTypeCatalog.decode(payload);
      } else {
        require(reference.equals(InboxResultReference.none()));
        require(
            code == ResultCode.NOT_FOUND
                || code == ResultCode.RESOURCE_LIMIT
                || (cancel && code == ResultCode.NOT_CANCELLABLE));
      }
    }

    @Override
    public String toString() {
      return "QuestionMutationResult[REDACTED]";
    }
  }

  /** Borrowed write transaction with current actor and Inbox NEW only. */
  public Result apply(
      QuestionCommandService commands,
      Connection c,
      AuthenticatedActor actor,
      QuestionCommandMetadata metadata) {
    Objects.requireNonNull(commands, "commands");
    if (cancel) {
      var result = commands.cancel(c, actor, target, metadata);
      var data =
          new NotificationCancelResponseData(
              result.state(),
              result.cancelledAt().map(time -> time.truncatedTo(ChronoUnit.MILLIS)));
      return new Result(
          result.code(),
          new PayloadValues(responseLayoutId(), data.fields(), List.of()),
          result.code().usesSuccessProfile()
              ? InboxResultReference.numeric(
                  InboxResultReferenceType.JOB, result.jobId().orElseThrow())
              : InboxResultReference.none());
    }
    var result = commands.logicalDelete(c, actor, target, metadata);
    return new Result(
        result.code(),
        new PayloadValues(
            responseLayoutId(),
            result.deletedAt().isPresent()
                ? new QuestionDeleteResponseData(
                        result.deletedAt().orElseThrow().truncatedTo(ChronoUnit.MILLIS))
                    .fields()
                : FieldValueSet.empty(),
            List.of()),
        result.code().usesSuccessProfile()
            ? InboxResultReference.numeric(InboxResultReferenceType.QUESTION, target)
            : InboxResultReference.none());
  }

  /** Code-specific frozen response invariants, independent of later live state. */
  public void validate(Result result) {
    Objects.requireNonNull(result, "result");
    require(result.payload().layoutId().equals(responseLayoutId()));
    if (result.code().usesSuccessProfile()) {
      // Result's typed decoder already establishes CANCELLED + required timestamp. Only
      // deletion's request-specific target binding remains to validate here.
      if (!cancel) require(result.reference().numericId().orElseThrow() == target);
    } else if (result.code() == ResultCode.NOT_CANCELLABLE) {
      var data = NotificationCancelResponseData.from(result.payload().data());
      require(
          data.cancelledAt().isEmpty()
              && Set.of(
                      Optional.of(NotificationState.PROCESSING),
                      Optional.of(NotificationState.COMPLETED),
                      Optional.of(NotificationState.ERROR))
                  .contains(data.updatedState()));
    }
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("question mutation invariant failed");
  }

  @Override
  public String toString() {
    return "QuestionMutationRequest[REDACTED]";
  }
}
