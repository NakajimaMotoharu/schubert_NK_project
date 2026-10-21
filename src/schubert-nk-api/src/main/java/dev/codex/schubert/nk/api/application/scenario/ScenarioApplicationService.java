package dev.codex.schubert.nk.api.application.scenario;

import dev.codex.schubert.nk.api.error.CapacityExceededException;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.file.ScenarioFileInspector;
import dev.codex.schubert.nk.api.file.ScenarioFilePublisher;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionConsistency;
import dev.codex.schubert.nk.api.idempotency.InboxException;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxRequest;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.MessageStageGuard;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.persistence.ScenarioDetailSnapshot;
import dev.codex.schubert.nk.api.persistence.ScenarioQueryException;
import dev.codex.schubert.nk.api.persistence.ScenarioRepository;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
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
 * Internal staged Scenario processor; register only after single-instance/full storage startup.
 * NK-SCN-001/NK-MSG-002/NK-AUT-001; FUN-003..005/MQ-006..010/AUT-001..004/DAT-009; UI234/237/241;
 * SS312/324 §7.1/332 §4.2/333; SSC-027/PT-SCN-009-T01..T07. Owns JDBC transactions, never JMS,
 * ready deletion, provider keys or storage root lifetime.
 */
public final class ScenarioApplicationService implements SyncRequestProcessor {
  private final DataSource database;
  private final AuthenticationContextVerifier authentication;
  private final ScenarioRepository queries;
  private final JdbcInboxCoordinator inbox;
  private final ScenarioReplayService responses;
  private final ScenarioDetailDelivery delivery;
  private final ScenarioFileRegenerator regenerator;
  private final ScenarioFileInspector inspector;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final MessageStageGuard guard = new MessageStageGuard();
  private final ScenarioAuditWriter audit = new ScenarioAuditWriter();

  public ScenarioApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      ScenarioRepository queries,
      JdbcInboxCoordinator inbox,
      ScenarioReplayService responses,
      ScenarioFilePublisher publisher,
      ScenarioFileInspector inspector,
      Clock clock) {
    this(
        database,
        authentication,
        queries,
        inbox,
        responses,
        publisher,
        inspector,
        clock,
        UUID::randomUUID);
  }

  ScenarioApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      ScenarioRepository queries,
      JdbcInboxCoordinator inbox,
      ScenarioReplayService responses,
      ScenarioFilePublisher publisher,
      ScenarioFileInspector inspector,
      Clock clock,
      Supplier<UUID> identifiers) {
    this.database = Objects.requireNonNull(database, "database");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.queries = Objects.requireNonNull(queries, "queries");
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.responses = Objects.requireNonNull(responses, "responses");
    this.delivery = new ScenarioDetailDelivery(publisher);
    this.regenerator = new ScenarioFileRegenerator(publisher);
    this.inspector = Objects.requireNonNull(inspector, "inspector");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    ScenarioRequest request = ScenarioRequest.decode(message);
    try {
      return guard.execute(request.header().messageId(), () -> run(request));
    } catch (PermanentProtocolException failure) {
      throw failure;
    } catch (RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private byte[] run(ScenarioRequest request) {
    try {
      Instant received = clock.instant().truncatedTo(ChronoUnit.MICROS);
      Initial initial = transaction(true, connection -> inspect(connection, request, received));
      Prepared prepared = prepare(request, initial);
      Completed completed =
          transaction(
              false,
              connection -> complete(connection, request, initial.actor(), prepared, received));
      return responses.reply(
          completed.snapshot(),
          request,
          completed.actor(),
          identifiers.get(),
          clock.instant(),
          completed.replay());
    } catch (AccessRejected denied) {
      TemporaryInfrastructureException.preserveFatal(denied);
      return responses.failure(
          request, ResultCode.SESSION_INVALID, identifiers.get(), clock.instant());
    } catch (IOException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private Initial inspect(Connection connection, ScenarioRequest request, Instant received)
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
        InboxCompletion completion = result.completion().orElseThrow();
        return new Initial(
            actor, new Saved(completion, responses.read(request, actor, completion)));
      }
      try {
        return new Initial(actor, new Query(request.query(queries, connection, actor)));
      } catch (ScenarioQueryException full) {
        TemporaryInfrastructureException.preserveFatal(full);
        // BUG-038/YKT-034: query limits and physical quota use different exception contracts.
        if (full.resultCode() != ResultCode.RESOURCE_LIMIT)
          throw new TemporaryInfrastructureException();
        return new Initial(actor, new Failed(ResultCode.RESOURCE_LIMIT));
      }
    } finally {
      canonical.close();
    }
  }

  private Prepared prepare(ScenarioRequest request, Initial initial) throws IOException {
    return switch (initial.work()) {
      case Failed failed -> failed;
      case Query query -> {
        try {
          yield switch (query.snapshot()) {
            case ScenarioQuerySnapshot.Inline inline -> new Success(inline.value());
            case ScenarioQuerySnapshot.Detail detail ->
                detail.value().isEmpty()
                    ? new Failed(ResultCode.NOT_FOUND)
                    : new Success(delivery.deliver(detail.value().orElseThrow(), clock.instant()));
          };
        } catch (CapacityExceededException full) {
          TemporaryInfrastructureException.preserveFatal(full);
          yield new Failed(ResultCode.RESOURCE_LIMIT);
        }
      }
      case Saved saved -> {
        Optional<LargeResultDescriptor> replacement = Optional.empty();
        if (saved.snapshot().descriptor().isPresent()) {
          var descriptor = saved.snapshot().descriptor().orElseThrow();
          var availability =
              Objects.requireNonNull(inspector.inspect(descriptor), "file availability");
          if (availability == ScenarioFileInspector.Availability.MISSING) {
            ScenarioDetailSnapshot current =
                transaction(
                    true,
                    connection -> {
                      AuthenticatedActor actor =
                          authentication.inspectReadOnly(
                              connection,
                              request.header().authenticationContext().orElseThrow(),
                              clock.instant());
                      owner(initial.actor(), actor);
                      var query =
                          (ScenarioQuerySnapshot.Detail) request.query(queries, connection, actor);
                      return query.value().orElseThrow(TemporaryInfrastructureException::new);
                    });
            replacement =
                Optional.of(regenerator.regenerate(saved.snapshot(), current, clock.instant()));
          }
        }
        yield new Replay(saved.completion(), replacement);
      }
    };
  }

  private Completed complete(
      Connection connection,
      ScenarioRequest request,
      AuthenticatedActor before,
      Prepared prepared,
      Instant received)
      throws SQLException {
    AuthenticatedActor actor =
        authentication.verify(
            connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    owner(before, actor);
    var canonical = request.canonical(actor);
    try {
      InboxRequest identity = identity(request, actor, canonical, received);
      var execution =
          inbox.execute(
              connection,
              identity,
              ignored ->
                  switch (prepared) {
                    case Success success -> {
                      var responseId = identifiers.get();
                      var completedAt = clock.instant();
                      var captured =
                          responses.captureSuccess(
                              request, actor, success.value(), responseId, completedAt);
                      audit.write(connection, actor, request, success.value(), completedAt);
                      yield captured;
                    }
                    case Failed failed ->
                        responses.captureFailure(
                            request, actor, failed.code(), identifiers.get(), clock.instant());
                    case Replay replay -> throw new TemporaryInfrastructureException();
                  });
      InboxCompletion completion =
          execution.completion().orElseThrow(TemporaryInfrastructureException::new);
      boolean replay = prepared instanceof Replay;
      require(
          execution.status()
              == (replay ? InboxExecutionStatus.REPLAY : InboxExecutionStatus.EXECUTED));
      if (prepared instanceof Replay saved) {
        require(InboxCompletionConsistency.sameSaved(saved.completion(), completion));
        if (saved.replacement().isPresent()) {
          InboxCompletion replacement =
              responses.replaceFile(request, actor, completion, saved.replacement().orElseThrow());
          inbox.replaceScenarioSnapshot(connection, identity, completion, replacement);
          completion = replacement;
        }
      }
      return new Completed(actor, responses.read(request, actor, completion), replay);
    } finally {
      canonical.close();
    }
  }

  private static InboxRequest identity(
      ScenarioRequest request,
      AuthenticatedActor actor,
      dev.codex.schubert.nk.api.idempotency.CanonicalRequest canonical,
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
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          connection.rollback();
        } catch (SQLException | RuntimeException | Error rollbackFailure) {
          TemporaryInfrastructureException.attachSecondary(failure, rollbackFailure);
        }
        throw failure;
      }
    } catch (AuthenticationContextException | AccessRejected failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      if (failure.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
      // BUG-039: fixed internal boundary, never the multi-catch common RuntimeException type.
      throw new AccessRejected();
    } catch (InboxException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      if (failure.getSuppressed().length == 0
          && failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE)
        throw new PermanentProtocolException(
            "scenario request identity differs from its saved request");
      throw new TemporaryInfrastructureException();
    } catch (SQLException | RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private static void owner(AuthenticatedActor before, AuthenticatedActor current) {
    if (before.userId() != current.userId()) throw new AccessRejected();
  }

  private static void require(boolean valid) {
    if (!valid) throw new TemporaryInfrastructureException();
  }

  @FunctionalInterface
  private interface SqlOperation<T> {
    T run(Connection connection) throws SQLException;
  }

  private sealed interface Work permits Query, Failed, Saved {}

  private sealed interface Prepared permits Success, Failed, Replay {}

  private record Query(ScenarioQuerySnapshot snapshot) implements Work {}

  private record Failed(ResultCode code) implements Work, Prepared {}

  private record Saved(InboxCompletion completion, ScenarioReplayService.Snapshot snapshot)
      implements Work {}

  private record Success(TypedPayloadValues value) implements Prepared {}

  private record Replay(InboxCompletion completion, Optional<LargeResultDescriptor> replacement)
      implements Prepared {}

  private record Initial(AuthenticatedActor actor, Work work) {}

  private record Completed(
      AuthenticatedActor actor, ScenarioReplayService.Snapshot snapshot, boolean replay) {}

  private static final class AccessRejected extends RuntimeException {
    private static final long serialVersionUID = 1L;
  }
}
