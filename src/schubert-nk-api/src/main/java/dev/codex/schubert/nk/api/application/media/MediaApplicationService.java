package dev.codex.schubert.nk.api.application.media;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.MediaFileInspector;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionConsistency;
import dev.codex.schubert.nk.api.idempotency.InboxException;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxRequest;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.MessageStageGuard;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.persistence.MediaQueryException;
import dev.codex.schubert.nk.api.persistence.MediaRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.io.IOException;
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
 * Staged media query/retained-file/current-auth/Inbox processor. Register only after full startup.
 * NK-MED-001/NK-MSG-002/NK-AUT-001; FUN-005..007/MQ-006..010/FIL-006/007/DAT-009;
 * UI226/232/235/237/241; SS312/324/332/333; PG-D-080/PT-MED-055..061. Owns JDBC transactions, not
 * JMS, caller keys/roots, filesystem mutations or HTTP registration.
 */
public final class MediaApplicationService implements SyncRequestProcessor {
  private final DataSource database;
  private final AuthenticationContextVerifier authentication;
  private final MediaRepository queries;
  private final JdbcInboxCoordinator inbox;
  private final MediaReplayService responses;
  private final MediaFileInspector inspector;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final MessageStageGuard guard = new MessageStageGuard();

  public MediaApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      MediaRepository queries,
      JdbcInboxCoordinator inbox,
      MediaReplayService responses,
      MediaFileInspector inspector,
      Clock clock) {
    this(database, authentication, queries, inbox, responses, inspector, clock, UUID::randomUUID);
  }

  MediaApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      MediaRepository queries,
      JdbcInboxCoordinator inbox,
      MediaReplayService responses,
      MediaFileInspector inspector,
      Clock clock,
      Supplier<UUID> identifiers) {
    this.database = Objects.requireNonNull(database, "database");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.queries = Objects.requireNonNull(queries, "queries");
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.responses = Objects.requireNonNull(responses, "responses");
    this.inspector = Objects.requireNonNull(inspector, "inspector");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    MediaRequest request = MediaRequest.decode(message);
    try {
      return guard.execute(request.header().messageId(), () -> run(request));
    } catch (PermanentProtocolException failure) {
      throw failure;
    } catch (RuntimeException failure) {
      throw new TemporaryInfrastructureException();
    }
  }

  private byte[] run(MediaRequest request) {
    try {
      Instant received = clock.instant().truncatedTo(ChronoUnit.MICROS);
      Initial initial = transaction(true, c -> inspect(c, request, received));
      Prepared prepared = prepare(request, initial.work());
      Completed completed =
          transaction(false, c -> complete(c, request, initial.actor(), prepared, received));
      return responses.reply(
          completed.snapshot(),
          request,
          completed.actor(),
          identifiers.get(),
          clock.instant(),
          completed.replay());
    } catch (AccessRejected denied) {
      return responses.failure(
          request, ResultCode.SESSION_INVALID, identifiers.get(), clock.instant());
    } catch (IOException failure) {
      throw new TemporaryInfrastructureException();
    }
  }

  private Initial inspect(Connection connection, MediaRequest request, Instant received)
      throws SQLException {
    AuthenticatedActor actor =
        authentication.inspectReadOnly(
            connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    var canonical = request.canonical(actor);
    try {
      var stored = inbox.inspectMessage(connection, identity(request, actor, canonical, received));
      if (stored.isPresent()) {
        var result = stored.orElseThrow();
        require(result.status() == InboxExecutionStatus.REPLAY);
        var completion = result.completion().orElseThrow();
        return new Initial(
            actor, new Saved(completion, responses.read(request, actor, completion)));
      }
      try {
        return new Initial(actor, new Query(request.query(queries, connection, actor)));
      } catch (MediaQueryException failure) {
        if (failure.resultCode() != ResultCode.RESOURCE_LIMIT)
          throw new TemporaryInfrastructureException();
        return new Initial(actor, new Failed(ResultCode.RESOURCE_LIMIT));
      }
    } finally {
      canonical.close();
    }
  }

  private Prepared prepare(MediaRequest request, Work work) throws IOException {
    return switch (work) {
      case Failed failed -> failed;
      case Query query -> {
        if (query.value().isEmpty()) yield new Failed(ResultCode.NOT_FOUND);
        var value = query.value().orElseThrow();
        var descriptor = request.descriptor(value);
        if (descriptor.isPresent()) inspector.verify(descriptor.orElseThrow());
        yield new Success(value);
      }
      case Saved saved -> {
        var descriptor = saved.snapshot().descriptor();
        if (descriptor.isPresent()) inspector.verify(descriptor.orElseThrow());
        yield new Replay(saved.completion());
      }
    };
  }

  private Completed complete(
      Connection connection,
      MediaRequest request,
      AuthenticatedActor before,
      Prepared prepared,
      Instant received)
      throws SQLException {
    AuthenticatedActor actor =
        authentication.verify(
            connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    if (before.userId() != actor.userId()) throw new AccessRejected();
    var canonical = request.canonical(actor);
    try {
      var execution =
          inbox.execute(
              connection,
              identity(request, actor, canonical, received),
              ignored ->
                  switch (prepared) {
                    case Success success ->
                        responses.captureSuccess(
                            request, actor, success.value(), identifiers.get(), clock.instant());
                    case Failed failed ->
                        responses.captureFailure(
                            request, actor, failed.code(), identifiers.get(), clock.instant());
                    case Replay replay -> throw new TemporaryInfrastructureException();
                  });
      var completion = execution.completion().orElseThrow(TemporaryInfrastructureException::new);
      boolean replay = prepared instanceof Replay;
      require(
          execution.status()
              == (replay ? InboxExecutionStatus.REPLAY : InboxExecutionStatus.EXECUTED));
      if (prepared instanceof Replay saved)
        require(InboxCompletionConsistency.sameSaved(saved.completion(), completion));
      return new Completed(actor, responses.read(request, actor, completion), replay);
    } finally {
      canonical.close();
    }
  }

  private static InboxRequest identity(
      MediaRequest request,
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
        T result = Objects.requireNonNull(operation.run(connection), "transaction result");
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
    } catch (AuthenticationContextException | AccessRejected failure) {
      if (failure.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
      throw new AccessRejected();
    } catch (InboxException failure) {
      if (failure.getSuppressed().length == 0
          && failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE)
        throw new PermanentProtocolException(
            "media request identity differs from its saved request");
      throw new TemporaryInfrastructureException();
    } catch (SQLException | RuntimeException failure) {
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

  private sealed interface Work permits Query, Saved, Failed {}

  private sealed interface Prepared permits Success, Replay, Failed {}

  private record Query(Optional<TypedPayloadValues> value) implements Work {}

  private record Saved(InboxCompletion completion, MediaReplayService.Snapshot snapshot)
      implements Work {}

  private record Failed(ResultCode code) implements Work, Prepared {}

  private record Success(TypedPayloadValues value) implements Prepared {}

  private record Replay(InboxCompletion completion) implements Prepared {}

  private record Initial(AuthenticatedActor actor, Work work) {}

  private record Completed(
      AuthenticatedActor actor, MediaReplayService.Snapshot snapshot, boolean replay) {}

  private static final class AccessRejected extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }
}
