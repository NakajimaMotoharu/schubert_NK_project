package dev.codex.schubert.nk.api.application.admin;

import dev.codex.schubert.nk.api.application.admin.UserQueryAuditWriter.Event;
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
import dev.codex.schubert.nk.api.persistence.UserQueryException;
import dev.codex.schubert.nk.api.persistence.UserQueryRepository;
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
 * Read-only User snapshot then current identity/ADMIN/Inbox/audit write transaction.
 * NK-ADM-001/NK-MSG-002/NK-AUT-001; FUN-009/AUT-002/003/MQ-006..010/MON-004; UI226/232/236/241/242;
 * SS312/314/323 §9.4/324/332/351/352; PG-D-089/PT-ADM-048..054. Owns JDBC transactions, not JMS,
 * caller keys, HTTP or startup registration.
 */
public final class UserQueryApplicationService implements SyncRequestProcessor {
  private final DataSource database;
  private final AuthenticationContextVerifier authentication;
  private final UserQueryRepository queries;
  private final JdbcInboxCoordinator inbox;
  private final UserQueryReplayService responses;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final UserQueryAuditWriter audit = new UserQueryAuditWriter();

  public UserQueryApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      UserQueryRepository queries,
      JdbcInboxCoordinator inbox,
      UserQueryReplayService responses,
      Clock clock) {
    this(database, authentication, queries, inbox, responses, clock, UUID::randomUUID);
  }

  UserQueryApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      UserQueryRepository queries,
      JdbcInboxCoordinator inbox,
      UserQueryReplayService responses,
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
    var request = UserQueryRequest.decode(message);
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
                "user query identity differs from its saved request");
      };
    } catch (PermanentProtocolException failure) {
      throw failure;
    } catch (RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private Stage inspect(Connection connection, UserQueryRequest request, Instant received)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.inspectReadOnly(
              connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    } catch (AuthenticationContextException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      return new Rejected(ResultCode.SESSION_INVALID);
    }
    if (actor.role() != Role.ADMIN) return new Rejected(ResultCode.FORBIDDEN);
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
        var value = request.query(queries, connection, actor, clock.instant());
        return new Ready(
            actor,
            value.isPresent()
                ? new Success(value.orElseThrow())
                : new Failure(ResultCode.NOT_FOUND));
      } catch (UserQueryException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        if (failure.resultCode() != ResultCode.RESOURCE_LIMIT) throw failure;
        return new Ready(actor, new Failure(ResultCode.RESOURCE_LIMIT));
      }
    } finally {
      canonical.close();
    }
  }

  private Outcome complete(
      Connection connection, UserQueryRequest request, Stage stage, Instant received)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.verify(
              connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    } catch (AuthenticationContextException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      return reject(connection, request, Optional.empty(), ResultCode.SESSION_INVALID);
    }
    if (actor.role() != Role.ADMIN)
      return reject(connection, request, Optional.of(actor), ResultCode.FORBIDDEN);
    if (stage instanceof VerifiedStage verified && verified.actor().userId() != actor.userId())
      return reject(connection, request, Optional.empty(), ResultCode.SESSION_INVALID);
    return switch (stage) {
      case Rejected denied ->
          reject(
              connection,
              request,
              denied.code() == ResultCode.SESSION_INVALID ? Optional.empty() : Optional.of(actor),
              denied.code());
      case Mismatch ignored -> invalid(connection, request, actor);
      case Ready ready -> persist(connection, request, actor, ready.prepared(), received);
    };
  }

  private Outcome persist(
      Connection connection,
      UserQueryRequest request,
      AuthenticatedActor actor,
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
                              request, actor, value.value(), identifiers.get(), clock.instant());
                      case Failure value ->
                          responses.captureFailure(
                              request, actor, value.code(), identifiers.get(), clock.instant());
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
      if (replay)
        audit.write(connection, Optional.of(actor), request, Event.REPLAY, clock.instant());
      return new Completed(actor, snapshot, replay);
    } finally {
      canonical.close();
    }
  }

  private Rejected reject(
      Connection connection,
      UserQueryRequest request,
      Optional<AuthenticatedActor> actor,
      ResultCode code)
      throws SQLException {
    audit.write(
        connection,
        actor,
        request,
        code == ResultCode.SESSION_INVALID ? Event.SESSION_INVALID : Event.ROLE_DENIED,
        clock.instant());
    return new Rejected(code);
  }

  private InvalidMessage invalid(
      Connection connection, UserQueryRequest request, AuthenticatedActor actor)
      throws SQLException {
    audit.write(connection, Optional.of(actor), request, Event.MESSAGE_MISMATCH, clock.instant());
    return new InvalidMessage();
  }

  private static boolean messageMismatch(InboxException failure) {
    return failure.getSuppressed().length == 0
        && failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE;
  }

  private static InboxRequest identity(
      UserQueryRequest request,
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

  private record Rejected(ResultCode code) implements Stage, Outcome {}

  private record InvalidMessage() implements Outcome {}

  private record Completed(
      AuthenticatedActor actor, UserQueryReplayService.Snapshot snapshot, boolean replay)
      implements Outcome {}
}
