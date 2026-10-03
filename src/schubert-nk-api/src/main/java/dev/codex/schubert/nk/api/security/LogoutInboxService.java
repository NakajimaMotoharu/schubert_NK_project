package dev.codex.schubert.nk.api.security;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.idempotency.*;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.*;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Logout-only owner lookup and Inbox transaction participant. Never creates a business actor.
 * NK-AUT-001/NK-MSG-002; AUT-004/MQ-006..010/MON-004; UI226/232/234/241; SS312/314/324 section 6.2;
 * SSC-015/PG-D-051, PT-AUT-LOGOUT-INBOX-001..006. Caller commits or rolls back, never this service.
 */
public final class LogoutInboxService {
  private final JdbcInboxCoordinator inbox;
  private final AuthSessionRevocationService revocations;
  private final LogoutReplayService responses;
  private final ContextHash hashes;
  private final Clock clock;
  private final Supplier<UUID> responseIds;

  public LogoutInboxService(
      JdbcInboxCoordinator inbox,
      AuthSessionRevocationService revocations,
      LogoutReplayService responses,
      ContextHash hashes,
      Clock clock) {
    this(inbox, revocations, responses, hashes, clock, UUID::randomUUID);
  }

  LogoutInboxService(
      JdbcInboxCoordinator inbox,
      AuthSessionRevocationService revocations,
      LogoutReplayService responses,
      ContextHash hashes,
      Clock clock,
      Supplier<UUID> responseIds) {
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.revocations = Objects.requireNonNull(revocations, "revocations");
    this.responses = Objects.requireNonNull(responses, "responses");
    this.hashes = Objects.requireNonNull(hashes, "hashes");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.responseIds = Objects.requireNonNull(responseIds, "responseIds");
  }

  public byte[] execute(
      Connection connection, WireMessage<FixedPayload> request, Instant receivedAt) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(receivedAt, "receivedAt");
    try {
      request
          .header()
          .validateAgainst(LayoutRegistry.standard().require(new LayoutId("LOGREQ01"), 1));
    } catch (IllegalArgumentException invalid) {
      throw new PermanentProtocolException("Logout request layout is invalid");
    }
    var raw = request.header().authenticationContext().orElseThrow();
    UUID message = request.header().messageId();
    UUID response = Objects.requireNonNull(responseIds.get(), "response ID");
    try {
      if (connection.getAutoCommit())
        throw new SQLException("Logout requires explicit transaction", "25000");
      OptionalLong owner = owner(connection, raw);
      if (owner.isEmpty())
        return responses.failure(
            ResultCode.SESSION_INVALID, raw, message, response, clock.instant());
      long userId = owner.getAsLong();
      Instant received = receivedAt.truncatedTo(ChronoUnit.MICROS);
      try (var canonical =
          new CanonicalRequest(
              Long.toString(userId), "LOGREQ01", "001", "REQUEST:LOGREQ01", List.of())) {
        var identity =
            new InboxRequest(
                message,
                request.header().correlationId(),
                owner,
                Optional.empty(),
                canonical,
                received,
                received.plusSeconds(604800));
        var execution =
            inbox.execute(
                connection,
                identity,
                transaction -> {
                  try {
                    var result =
                        revocations.logoutCurrent(
                            transaction,
                            raw,
                            Optional.empty(),
                            message,
                            request.header().correlationId(),
                            clock);
                    return responses.captureSuccess(
                        result, raw, message, response, clock.instant());
                  } catch (AuthenticationContextException denied) {
                    return responses.captureDenied(userId, raw, message, response, clock.instant());
                  }
                });
        if (execution.status() == InboxExecutionStatus.IN_PROGRESS)
          return responses.failure(
              ResultCode.TEMPORARY_FAILURE, raw, message, response, clock.instant());
        return responses.restore(
            connection,
            execution.completion().orElseThrow(),
            userId,
            raw,
            message,
            response,
            clock.instant(),
            execution.status() == InboxExecutionStatus.REPLAY);
      }
    } catch (InboxException failure) {
      if (failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE)
        throw new PermanentProtocolException(
            "Logout request identity differs from its saved request");
      throw new AuthenticationInfrastructureException();
    } catch (SQLException | IllegalArgumentException | IllegalStateException failure) {
      throw new AuthenticationInfrastructureException();
    }
  }

  private OptionalLong owner(Connection connection, AuthenticationContext raw) throws SQLException {
    try (var statement =
        connection.prepareStatement(
            "select u.id from schubert.app_users u join schubert.auth_sessions s on s.user_id=u.id "
                + "where s.context_hash=? for update of u")) {
      statement.setString(1, hashes.calculate(raw));
      try (var row = statement.executeQuery()) {
        return row.next()
            ? OptionalLong.of(requireValue(row.getObject("id", Long.class)))
            : OptionalLong.empty();
      }
    }
  }
}
