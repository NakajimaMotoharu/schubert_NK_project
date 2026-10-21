package dev.codex.schubert.nk.api.application.question;

import dev.codex.schubert.nk.api.application.question.QuestionMutationAuditWriter.Event;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.BoundInboxExecution;
import dev.codex.schubert.nk.api.idempotency.InboxException;
import dev.codex.schubert.nk.api.idempotency.InboxRequest;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.maintenance.QuestionMutationInboxInspector;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
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
 * Current identity→Inbox→mutation/audit/snapshot→current result scope→commit→reply. DB connections
 * owned, pool/keys/JMS/startup borrowed. NK-QRY-001/NTF-001/AUT-001/MSG-002; RD
 * QST005..010/NTF001..012/AUT002/MQ006..010/MON004; UI224232236241; SS312323324332351352/QA046;
 * PG-D332; PT-QRY039..045/NTF016.
 */
public final class QuestionMutationApplicationService implements SyncRequestProcessor {
  private static final String QUESTION_ADMIN =
      "select id from schubert.questions where id=? for key share";
  private static final String QUESTION_USER =
      "select id from schubert.questions where id=? and owner_user_id=? for key share";
  private final DataSource database;
  private final AuthenticationContextVerifier authentication;
  private final JdbcInboxCoordinator inbox;
  private final QuestionCommandService commands;
  private final QuestionMutationReplayService responses;
  private final QuestionMutationInboxInspector integrity;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final QuestionMutationAuditWriter audit = new QuestionMutationAuditWriter();

  public QuestionMutationApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      JdbcInboxCoordinator inbox,
      QuestionCommandService commands,
      ResponseSnapshotCodec snapshots,
      Clock clock) {
    this(database, authentication, inbox, commands, snapshots, clock, UUID::randomUUID);
  }

  QuestionMutationApplicationService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      JdbcInboxCoordinator inbox,
      QuestionCommandService commands,
      ResponseSnapshotCodec snapshots,
      Clock clock,
      Supplier<UUID> identifiers) {
    this.database = Objects.requireNonNull(database, "database");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.commands = Objects.requireNonNull(commands, "commands");
    this.responses =
        new QuestionMutationReplayService(Objects.requireNonNull(snapshots, "snapshots"));
    this.integrity = new QuestionMutationInboxInspector(snapshots);
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    var request = QuestionMutationRequest.decode(message);
    try {
      Instant received = clock.instant().truncatedTo(ChronoUnit.MICROS);
      var outcome = transaction(request, received);
      return switch (outcome) {
        case Completed done ->
            responses.reply(
                done.snapshot(), request, done.actor(), identifiers.get(), clock.instant());
        case Denied denied ->
            responses.failure(request, denied.code(), identifiers.get(), clock.instant());
        case InvalidMessage ignored ->
            throw new PermanentProtocolException(
                "question mutation identity differs from its saved request");
      };
    } catch (PermanentProtocolException invalid) {
      throw invalid;
    } catch (RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private Outcome transaction(QuestionMutationRequest request, Instant received) {
    try (var c = Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      c.setAutoCommit(false);
      c.setReadOnly(false);
      try {
        var outcome = execute(c, request, received);
        c.commit();
        return outcome;
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          c.rollback();
        } catch (SQLException | RuntimeException | Error cleanup) {
          TemporaryInfrastructureException.attachSecondary(failure, cleanup);
        }
        throw failure;
      }
    } catch (SQLException | RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private Outcome execute(Connection c, QuestionMutationRequest request, Instant received)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.verify(
              c,
              request.header().authenticationContext().orElseThrow(IllegalArgumentException::new),
              clock.instant());
    } catch (AuthenticationContextException invalid) {
      TemporaryInfrastructureException.preserveFatal(invalid);
      audit.write(c, Optional.empty(), request, Event.SESSION_INVALID, clock.instant());
      return new Denied(ResultCode.SESSION_INVALID);
    }
    var canonical = request.canonical(actor);
    try {
      BoundInboxExecution execution;
      try {
        execution =
            inbox.executeBound(
                c,
                new InboxRequest(
                    request.header().messageId(),
                    request.header().correlationId(),
                    OptionalLong.of(actor.userId()),
                    Optional.of(request.operationToken()),
                    canonical,
                    received,
                    received.plusSeconds(604800)),
                connection -> {
                  var result =
                      request.apply(
                          commands,
                          connection,
                          actor,
                          new QuestionCommandMetadata(
                              request.header().messageId(),
                              request.header().correlationId(),
                              clock.instant()));
                  if (result.code() == ResultCode.RESOURCE_LIMIT)
                    audit.write(
                        connection, Optional.of(actor), request, Event.CAPACITY, clock.instant());
                  return responses.capture(
                      request, actor, result, identifiers.get(), clock.instant());
                });
      } catch (InboxException conflict) {
        TemporaryInfrastructureException.preserveFatal(conflict);
        if (conflict.getSuppressed().length != 0) throw conflict;
        if (conflict.reason() == InboxException.Reason.OPERATION_TOKEN_REUSE) {
          audit.write(c, Optional.of(actor), request, Event.TOKEN_MISMATCH, clock.instant());
          return new Denied(ResultCode.CONFLICT);
        }
        if (conflict.reason() == InboxException.Reason.MESSAGE_ID_REUSE) {
          audit.write(c, Optional.of(actor), request, Event.MESSAGE_MISMATCH, clock.instant());
          return new InvalidMessage();
        }
        throw conflict;
      }
      var saved = responses.read(request, actor, execution);
      if (!currentScope(c, request, actor, saved)) {
        audit.write(c, Optional.of(actor), request, Event.OWNER_DENIED, clock.instant());
        return new Denied(ResultCode.NOT_FOUND);
      }
      var completion =
          execution.execution().completion().orElseThrow(IllegalArgumentException::new);
      if (!integrity.isConsistent(
          c,
          ResponseSnapshotIdentity.authenticated(
              execution.sourceMessageId(),
              request.responseLayoutId().value(),
              "001",
              actor.userId()),
          completion,
          request.operationToken())) throw new TemporaryInfrastructureException();
      if (saved.replay())
        audit.write(c, Optional.of(actor), request, Event.REPLAY, clock.instant());
      return new Completed(actor, saved);
    } finally {
      canonical.close();
    }
  }

  private static boolean currentScope(
      Connection c,
      QuestionMutationRequest request,
      AuthenticatedActor actor,
      QuestionMutationReplayService.Snapshot saved)
      throws SQLException {
    // Definite missing/0107 are frozen owner-bound denials, not proof of a live result row.
    if (saved.resultCode() == ResultCode.NOT_FOUND
        || saved.resultCode() == ResultCode.NOT_CANCELLABLE) return true;
    if (request.cancellation()) {
      if (saved.resultCode() == ResultCode.RESOURCE_LIMIT) {
        try (var s =
            c.prepareStatement(
                "select id from schubert.notifications where id=? and owner_user_id=? for key share")) {
          s.setLong(1, request.targetId());
          s.setLong(2, actor.userId());
          try (var r = s.executeQuery()) {
            boolean found = r.next();
            if (found && r.next()) throw new SQLException("notification scope is not singular");
            return found;
          }
        }
      }
      try (var s =
          c.prepareStatement(
              "select id from schubert.async_jobs where id=? and owner_user_id=? for key share")) {
        s.setLong(1, saved.reference().numericId().orElseThrow(IllegalArgumentException::new));
        s.setLong(2, actor.userId());
        try (var r = s.executeQuery()) {
          boolean found = r.next();
          if (found && r.next()) throw new SQLException("job scope is not singular");
          return found;
        }
      }
    }
    boolean admin = actor.role() == Role.ADMIN;
    try (var s = admin ? c.prepareStatement(QUESTION_ADMIN) : c.prepareStatement(QUESTION_USER)) {
      s.setLong(1, request.targetId());
      if (!admin) s.setLong(2, actor.userId());
      try (var r = s.executeQuery()) {
        boolean found = r.next();
        if (found && r.next()) throw new SQLException("question scope is not singular");
        return found;
      }
    }
  }

  private sealed interface Outcome permits Completed, Denied, InvalidMessage {}

  private record Completed(
      AuthenticatedActor actor, QuestionMutationReplayService.Snapshot snapshot)
      implements Outcome {}

  private record Denied(ResultCode code) implements Outcome {}

  private record InvalidMessage() implements Outcome {}
}
