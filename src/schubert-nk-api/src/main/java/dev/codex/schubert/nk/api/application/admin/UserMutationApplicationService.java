package dev.codex.schubert.nk.api.application.admin;

import dev.codex.schubert.nk.api.application.admin.UserRequestAuditWriter.Event;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.*;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
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
 * Current identity/ADMIN, Inbox, User/session/audit and frozen reply in one DB transaction.
 * NK-ADM-001/NK-MSG-002/NK-AUT-001; FUN-009/AUT-002/003/MQ-006..010/MON-004; UI226/232/236/241/242;
 * SS312 §6/314/324/332/351/352; SSC-031/034/PG-D-087; PT-ADM-033..039. Owns DB transactions, not
 * JMS/HTTP/startup or caller keys.
 */
public final class UserMutationApplicationService implements SyncRequestProcessor {
  private final DataSource database;
  private final AdminCommandAuthenticator authentication;
  private final JdbcInboxCoordinator inbox;
  private final UserCommandService commands;
  private final UserMutationReplayService responses;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final UserRequestAuditWriter audit = new UserRequestAuditWriter();

  public UserMutationApplicationService(
      DataSource database,
      AdminCommandAuthenticator authentication,
      JdbcInboxCoordinator inbox,
      UserCommandService commands,
      UserMutationReplayService responses,
      Clock clock) {
    this(database, authentication, inbox, commands, responses, clock, UUID::randomUUID);
  }

  UserMutationApplicationService(
      DataSource database,
      AdminCommandAuthenticator authentication,
      JdbcInboxCoordinator inbox,
      UserCommandService commands,
      UserMutationReplayService responses,
      Clock clock,
      Supplier<UUID> identifiers) {
    this.database = Objects.requireNonNull(database, "database");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.commands = Objects.requireNonNull(commands, "commands");
    this.responses = Objects.requireNonNull(responses, "responses");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    try (var request = UserMutationRequest.decode(message)) {
      Instant received = clock.instant().truncatedTo(ChronoUnit.MICROS);
      Outcome outcome = transaction(request, received);
      return switch (outcome) {
        case Completed result ->
            responses.reply(
                result.snapshot(), request, result.actor(), identifiers.get(), clock.instant());
        case Denied result ->
            responses.failure(request, result.code(), identifiers.get(), clock.instant());
        case InvalidMessage ignored ->
            throw new PermanentProtocolException(
                "user request identity differs from its saved request");
      };
    } catch (PermanentProtocolException failure) {
      throw failure;
    } catch (RuntimeException failure) {
      throw new TemporaryInfrastructureException();
    }
  }

  private Outcome transaction(UserMutationRequest request, Instant received) {
    try (Connection connection =
        Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      connection.setReadOnly(false);
      try {
        Outcome result = execute(connection, request, received);
        connection.commit();
        return result;
      } catch (SQLException | RuntimeException failure) {
        try {
          connection.rollback();
        } catch (SQLException rollbackFailure) {
          failure.addSuppressed(rollbackFailure);
        }
        throw failure;
      }
    } catch (SQLException | RuntimeException failure) {
      throw new TemporaryInfrastructureException();
    }
  }

  private Outcome execute(Connection connection, UserMutationRequest request, Instant received)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.verifyIdentity(
              connection,
              request.header().authenticationContext().orElseThrow(),
              request.mutation(),
              request.targetUserId(),
              clock.instant());
    } catch (AuthenticationContextException failure) {
      audit.write(connection, Optional.empty(), request, Event.SESSION_INVALID, clock.instant());
      return new Denied(ResultCode.SESSION_INVALID);
    }
    if (actor.role() != Role.ADMIN) {
      audit.write(connection, Optional.of(actor), request, Event.ROLE_DENIED, clock.instant());
      return new Denied(ResultCode.FORBIDDEN);
    }
    var canonical = request.canonical(actor);
    try {
      BoundInboxExecution execution;
      try {
        execution =
            inbox.executeBound(
                connection,
                new InboxRequest(
                    request.header().messageId(),
                    request.header().correlationId(),
                    OptionalLong.of(actor.userId()),
                    Optional.of(request.operationToken()),
                    canonical,
                    received,
                    received.plusSeconds(604800)),
                c -> {
                  var result =
                      request.apply(
                          commands,
                          c,
                          actor,
                          new UserCommandMetadata(
                              request.header().messageId(),
                              request.header().correlationId(),
                              clock.instant()));
                  return responses.capture(
                      request, actor, result, identifiers.get(), clock.instant());
                });
      } catch (InboxException failure) {
        if (failure.getSuppressed().length != 0) throw failure;
        if (failure.reason() == InboxException.Reason.OPERATION_TOKEN_REUSE) {
          audit.write(
              connection, Optional.of(actor), request, Event.TOKEN_MISMATCH, clock.instant());
          return new Denied(ResultCode.CONFLICT);
        }
        if (failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE) {
          audit.write(
              connection, Optional.of(actor), request, Event.MESSAGE_MISMATCH, clock.instant());
          return new InvalidMessage();
        }
        throw failure;
      }
      var snapshot = responses.read(request, actor, execution);
      if (execution.execution().status() == InboxExecutionStatus.REPLAY)
        audit.write(connection, Optional.of(actor), request, Event.REPLAY, clock.instant());
      return new Completed(actor, snapshot);
    } finally {
      canonical.close();
    }
  }

  private sealed interface Outcome permits Completed, Denied, InvalidMessage {}

  private record Completed(AuthenticatedActor actor, UserMutationReplayService.Snapshot snapshot)
      implements Outcome {}

  private record Denied(ResultCode code) implements Outcome {}

  private record InvalidMessage() implements Outcome {}
}
