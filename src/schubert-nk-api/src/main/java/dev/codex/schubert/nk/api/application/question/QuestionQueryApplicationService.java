package dev.codex.schubert.nk.api.application.question;

import dev.codex.schubert.nk.api.application.question.QuestionQueryAuditWriter.Event;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionConsistency;
import dev.codex.schubert.nk.api.idempotency.InboxException;
import dev.codex.schubert.nk.api.idempotency.InboxExecution;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxRequest;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.persistence.QuestionQueryException;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.function.Supplier;
import javax.sql.DataSource;

/**
 * Read-only Question/Notification snapshot then current identity/scope/Inbox/audit transaction.
 * NK-QRY-001/NK-NTF-001/NK-AUT-001; QST005..010/NTF001..012/AUT002/MQ006..010/MON004;
 * UI224232236241; SS312/323/324/332/351/352/SSC157; PG-D-330/PT-QRY018..024/NTF011. Owns JDBC
 * transactions, not JMS, caller keys, HTTP or startup registration.
 */
public final class QuestionQueryApplicationService implements SyncRequestProcessor {
  private final DataSource database;
  private final AuthenticationContextVerifier authentication;
  private final QuestionQueryRepository queries;
  private final JdbcInboxCoordinator inbox;
  private final QuestionQueryReplayService responses;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final QuestionQueryAuditWriter audit = new QuestionQueryAuditWriter();

  public QuestionQueryApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      QuestionQueryRepository queries,
      JdbcInboxCoordinator inbox,
      QuestionQueryReplayService responses,
      Clock clock) {
    this(database, authentication, queries, inbox, responses, clock, UUID::randomUUID);
  }

  QuestionQueryApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      QuestionQueryRepository queries,
      JdbcInboxCoordinator inbox,
      QuestionQueryReplayService responses,
      Clock clock,
      Supplier<UUID> identifiers) {
    this.database = Objects.requireNonNull(database, "database");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.queries = Objects.requireNonNull(queries, "queries");
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.responses = Objects.requireNonNull(responses, "responses");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    var request = QuestionQueryRequest.decode(message);
    try {
      Instant received = clock.instant().truncatedTo(ChronoUnit.MICROS);
      Stage stage = transaction(true, c -> inspect(c, request, received));
      Outcome outcome = transaction(false, c -> complete(c, request, stage, received));
      return switch (outcome) {
        case Completed result ->
            responses.reply(
                result.snapshot(),
                request,
                result.actor(),
                identifiers.get(),
                clock.instant(),
                result.replay());
        case Rejected result ->
            responses.failure(request, result.code(), identifiers.get(), clock.instant());
        case InvalidMessage ignored ->
            throw new PermanentProtocolException(
                "question query identity differs from its saved request");
      };
    } catch (PermanentProtocolException failure) {
      throw failure;
    } catch (RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private Stage inspect(Connection connection, QuestionQueryRequest request, Instant received)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.inspectReadOnly(
              connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    } catch (AuthenticationContextException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      return new Rejected(Rejection.SESSION_INVALID);
    }
    var canonical = request.canonical(actor);
    try {
      Optional<InboxExecution> stored;
      try {
        stored = inbox.inspectMessage(connection, identity(request, actor, canonical, received));
      } catch (InboxException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        if (messageMismatch(failure)) return new Mismatch(actor);
        throw failure;
      }
      if (stored.isPresent()) {
        var execution = stored.orElseThrow();
        require(execution.status() == InboxExecutionStatus.REPLAY);
        var completion = execution.completion().orElseThrow(TemporaryInfrastructureException::new);
        responses.read(request, actor, completion);
        return new Ready(actor, new Saved(completion));
      }
      try {
        var value = request.query(queries, connection, actor);
        return new Ready(
            actor,
            value.isPresent()
                ? new Success(value.orElseThrow())
                : new Failure(ResultCode.NOT_FOUND));
      } catch (QuestionQueryException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        if (failure.resultCode() == ResultCode.VALIDATION_ERROR)
          return new Rejected(Rejection.VALIDATION);
        if (failure.resultCode() != ResultCode.RESOURCE_LIMIT) throw failure;
        return new Ready(actor, new Failure(ResultCode.RESOURCE_LIMIT));
      }
    } finally {
      canonical.close();
    }
  }

  private Outcome complete(
      Connection connection, QuestionQueryRequest request, Stage stage, Instant received)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.verify(
              connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    } catch (AuthenticationContextException failure) {
      // BUG2093/YKT1840; SS312 SSC329: inspect fatal graph before SESSION_INVALID.
      TemporaryInfrastructureException.preserveFatal(failure);
      return reject(connection, request, Optional.empty(), Rejection.SESSION_INVALID);
    }
    if (stage instanceof VerifiedStage verified && verified.actor().userId() != actor.userId())
      return reject(connection, request, Optional.empty(), Rejection.SESSION_INVALID);
    return switch (stage) {
      case Rejected denied ->
          reject(
              connection,
              request,
              denied.code() == ResultCode.SESSION_INVALID ? Optional.empty() : Optional.of(actor),
              denied.reason());
      case Mismatch ignored -> invalid(connection, request, actor);
      case Ready ready -> {
        if (!(ready.prepared() instanceof Saved)
            && request.questionScope()
            && ready.actor().role() == Role.ADMIN
            && actor.role() == Role.USER)
          yield reject(connection, request, Optional.of(actor), scopeDenial(request));
        yield persist(connection, request, actor, ready.actor(), ready.prepared(), received);
      }
    };
  }

  private Outcome persist(
      Connection connection,
      QuestionQueryRequest request,
      AuthenticatedActor actor,
      AuthenticatedActor capturedActor,
      Prepared prepared,
      Instant received)
      throws SQLException {
    var canonical = request.canonical(actor);
    try {
      InboxExecution execution;
      try {
        execution =
            inbox.execute(
                connection,
                identity(request, actor, canonical, received),
                ignored ->
                    switch (prepared) {
                      case Success value ->
                          responses.captureSuccess(
                              request,
                              capturedActor,
                              value.value(),
                              identifiers.get(),
                              clock.instant());
                      case Failure value ->
                          responses.captureFailure(
                              request,
                              capturedActor,
                              value.code(),
                              identifiers.get(),
                              clock.instant());
                      case Saved ignoredSaved -> throw new TemporaryInfrastructureException();
                    });
      } catch (InboxException failure) {
        // BUG2092/YKT1840; SS312/324 SSC329: inspect fatal graph before mismatch.
        TemporaryInfrastructureException.preserveFatal(failure);
        if (messageMismatch(failure)) return invalid(connection, request, actor);
        throw failure;
      }
      var completion = execution.completion().orElseThrow(TemporaryInfrastructureException::new);
      if (prepared instanceof Saved saved)
        require(InboxCompletionConsistency.sameSaved(saved.completion(), completion));
      boolean replay = execution.status() == InboxExecutionStatus.REPLAY;
      var snapshot = responses.read(request, actor, completion);
      // The locked Inbox can return a competing ADMIN snapshot; recheck the actual completion.
      if (!snapshot.scopeAllowed(actor))
        return reject(connection, request, Optional.of(actor), scopeDenial(request));
      if (replay)
        audit.write(connection, Optional.of(actor), request, Event.REPLAY, clock.instant());
      return new Completed(actor, snapshot, replay);
    } finally {
      canonical.close();
    }
  }

  // Closed internal rejection type: no externally supplied/unknown ResultCode reaches audit
  // mapping.
  private Rejected reject(
      Connection connection,
      QuestionQueryRequest request,
      Optional<AuthenticatedActor> actor,
      Rejection reason)
      throws SQLException {
    audit.write(connection, actor, request, reason.event, clock.instant());
    return new Rejected(reason);
  }

  private InvalidMessage invalid(
      Connection connection, QuestionQueryRequest request, AuthenticatedActor actor)
      throws SQLException {
    audit.write(connection, Optional.of(actor), request, Event.MESSAGE_MISMATCH, clock.instant());
    return new InvalidMessage();
  }

  private static Rejection scopeDenial(QuestionQueryRequest request) {
    return request.detailRequest() ? Rejection.OWNER_DENIED : Rejection.ROLE_DENIED;
  }

  private static boolean messageMismatch(InboxException failure) {
    return failure.getSuppressed().length == 0
        && failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE;
  }

  private static InboxRequest identity(
      QuestionQueryRequest request,
      AuthenticatedActor actor,
      CanonicalRequest canonical,
      Instant received) {
    return new InboxRequest(
        request.header().messageId(),
        request.header().correlationId(),
        OptionalLong.of(actor.userId()),
        Optional.empty(),
        canonical,
        received,
        received.plusSeconds(86400));
  }

  private <T> T transaction(boolean readOnly, SqlOperation<T> operation) {
    try (Connection connection =
        Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      connection.setReadOnly(readOnly);
      try {
        T value = operation.run(connection);
        connection.commit();
        return value;
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException | Error rollbackFailure) {
          TemporaryInfrastructureException.attachSecondary(failure, rollbackFailure);
        }
        throw failure;
      }
    } catch (SQLException | RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private static void require(boolean valid) {
    if (!valid) throw new TemporaryInfrastructureException();
  }

  @FunctionalInterface
  private interface SqlOperation<T> {
    T run(Connection connection) throws SQLException;
  }

  private sealed interface Stage permits Rejected, VerifiedStage {}

  private sealed interface VerifiedStage extends Stage permits Ready, Mismatch {
    AuthenticatedActor actor();
  }

  private record Ready(AuthenticatedActor actor, Prepared prepared) implements VerifiedStage {}

  private record Mismatch(AuthenticatedActor actor) implements VerifiedStage {}

  private sealed interface Prepared permits Success, Failure, Saved {}

  private record Success(TypedPayloadValues value) implements Prepared {}

  private record Failure(ResultCode code) implements Prepared {}

  private record Saved(InboxCompletion completion) implements Prepared {}

  private sealed interface Outcome permits Rejected, InvalidMessage, Completed {}

  private enum Rejection {
    SESSION_INVALID(ResultCode.SESSION_INVALID, Event.SESSION_INVALID),
    ROLE_DENIED(ResultCode.FORBIDDEN, Event.ROLE_DENIED),
    OWNER_DENIED(ResultCode.NOT_FOUND, Event.OWNER_DENIED),
    VALIDATION(ResultCode.VALIDATION_ERROR, Event.VALIDATION);
    final ResultCode code;
    final Event event;

    Rejection(ResultCode code, Event event) {
      this.code = code;
      this.event = event;
    }
  }

  private record Rejected(Rejection reason) implements Stage, Outcome {
    ResultCode code() {
      return reason.code;
    }
  }

  private record InvalidMessage() implements Outcome {}

  private record Completed(
      AuthenticatedActor actor, QuestionQueryReplayService.Snapshot snapshot, boolean replay)
      implements Outcome {}
}
