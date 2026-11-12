package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.BoundInboxExecution;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxException;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxRequest;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.idempotency.ResultBoundResponseSnapshotCodec;
import dev.codex.schubert.nk.api.messaging.inbound.SyncRequestProcessor;
import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDestination;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxRequest;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitResponseData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionWorkData;
import dev.codex.schubert.nk.protocol.layout.semantic.AsyncJobId;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Savepoint;
import java.sql.Types;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.locks.LockSupport;
import java.util.function.LongSupplier;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.postgresql.util.PSQLException;

/**
 * Atomic QSB acceptance and authenticated frozen replay, then a short connection-free SENT wait.
 * The separately owned dispatcher is only signalled here; no JMS send on the request thread.
 * NK-QST-001/NK-MSG-002; QST001/ASY001/MQ006..010; UI224232236241; SS312§7/324/331332352;
 * SSC151..155; PT-QST-ASUB-001..007. Caller owns pool, keys and dispatcher lifetime.
 */
public final class QuestionSubmissionService implements SyncRequestProcessor {
  private static final java.lang.String LITERAL_001 = "001";

  private static final java.lang.String LITERAL_QSBRSP01 = "QSBRSP01";

  private final DataSource database;
  private final AuthenticationContextVerifier authentication;
  private final JdbcInboxCoordinator inbox;
  private final ResultBoundResponseSnapshotCodec snapshots;
  private final JdbcOutboxRepository outbox = new JdbcOutboxRepository();
  private final QuestionReceiptIdGenerator receipts;
  private final Runnable wakeDispatcher;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final LongSupplier nanos;

  public QuestionSubmissionService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      JdbcInboxCoordinator inbox,
      ResultBoundResponseSnapshotCodec snapshots,
      Runnable wakeDispatcher,
      Clock clock) {
    this(
        database,
        authentication,
        inbox,
        snapshots,
        wakeDispatcher,
        clock,
        QuestionReceiptIdGenerator.create(),
        UUID::randomUUID,
        System::nanoTime);
  }

  QuestionSubmissionService(
      DataSource database,
      AuthenticationContextVerifier authentication,
      JdbcInboxCoordinator inbox,
      ResultBoundResponseSnapshotCodec snapshots,
      Runnable wakeDispatcher,
      Clock clock,
      QuestionReceiptIdGenerator receipts,
      Supplier<UUID> identifiers,
      LongSupplier nanos) {
    this.database = Objects.requireNonNull(database, "database");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    this.wakeDispatcher = Objects.requireNonNull(wakeDispatcher, "dispatcher signal");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.receipts = Objects.requireNonNull(receipts, "receipts");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
    this.nanos = Objects.requireNonNull(nanos, "monotonic clock");
  }

  @Override
  public byte[] process(WireMessage<FixedPayload> message) {
    Objects.requireNonNull(message, "message");
    try (var request = QuestionSubmitRequest.decode(message)) {
      return processOwned(request);
    } catch (PermanentProtocolException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      if (failure.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
      throw failure;
    } catch (SQLException | RuntimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new TemporaryInfrastructureException();
    }
  }

  private boolean expired(long start, long budget) {
    return nanos.getAsLong() - start >= budget;
  }

  /** One request owner; reply, exception classification and clearing keep their original order. */
  private byte[] processOwned(QuestionSubmitRequest request) throws SQLException {
    Instant received = clock.instant().truncatedTo(ChronoUnit.MICROS);
    long start = nanos.getAsLong();
    Instant deadline = request.header().sentAt().plusSeconds(2);
    if (received.plusSeconds(2).isBefore(deadline)) deadline = received.plusSeconds(2);
    long budget = Math.max(0, Duration.between(received, deadline).toNanos());
    if (expired(start, budget)) return failure(request, ResultCode.TEMPORARY_FAILURE);
    Outcome outcome;
    try {
      outcome = transaction(request, received, start, budget);
    } catch (RetainedRequest failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      // The newly inserted PROCESSING row was rolled back. Never restore/predict history.
      if (failure.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
      if (failure.actorId != 0) auditRetained(request, failure);
      return failure(request, failure.code);
    }
    if (outcome instanceof Denied denied) return failure(request, denied.code());
    if (outcome instanceof InvalidMessage)
      throw new PermanentProtocolException("question request differs from saved identity");
    Accepted accepted = (Accepted) outcome;
    if (expired(start, budget)) return failure(request, ResultCode.TEMPORARY_FAILURE);
    wakeDispatcher.run();
    while (!expired(start, budget)) {
      boolean confirmed;
      try {
        confirmed = sent(accepted, request, start, budget);
      } catch (RetainedRequest elapsed) {
        TemporaryInfrastructureException.preserveFatal(elapsed);
        if (elapsed.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
        break;
      }
      if (confirmed) {
        if (expired(start, budget)) break;
        return reply(
            request,
            Optional.of(accepted.data()),
            accepted.replay() ? ResultCode.IDEMPOTENT_SUCCESS : ResultCode.SUCCESS);
      }
      if (Thread.currentThread().isInterrupted()) throw new TemporaryInfrastructureException();
      long remaining = budget - (nanos.getAsLong() - start);
      if (remaining > 0) LockSupport.parkNanos(Math.min(remaining, 10_000_000));
    }
    return failure(request, ResultCode.TEMPORARY_FAILURE);
  }

  private Outcome transaction(
      QuestionSubmitRequest request, Instant received, long start, long budget)
      throws SQLException {
    try (var connection = Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      connection.setReadOnly(false);
      try {
        timeout(connection, start, budget);
        Outcome outcome = execute(connection, request, received, start, budget);
        connection.commit();
        return outcome;
      } catch (SQLException | RuntimeException | Error failure) {
        rollback(connection, failure);
        throw failure;
      }
    }
  }

  private Outcome execute(
      Connection connection,
      QuestionSubmitRequest request,
      Instant received,
      long start,
      long budget)
      throws SQLException {
    AuthenticatedActor actor;
    try {
      actor =
          authentication.verify(
              connection, request.header().authenticationContext().orElseThrow(), clock.instant());
    } catch (AuthenticationContextException invalid) {
      TemporaryInfrastructureException.preserveFatal(invalid);
      audit(connection, Optional.empty(), request, "AUTHORIZATION_DENIED", "0102", received);
      return new Denied(ResultCode.SESSION_INVALID);
    }
    if (expired(start, budget)) throw new RetainedRequest(ResultCode.TEMPORARY_FAILURE);
    try (var canonical = request.canonical(actor)) {
      return executeCanonical(connection, request, actor, canonical, received);
    }
  }

  /** Canonical scope closes before its caller commits, including conflict and fatal paths. */
  private Outcome executeCanonical(
      Connection connection,
      QuestionSubmitRequest request,
      AuthenticatedActor actor,
      CanonicalRequest canonical,
      Instant received)
      throws SQLException {
    BoundInboxExecution bound;
    try {
      bound =
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
              c -> create(c, request, actor, clock.instant().truncatedTo(ChronoUnit.MICROS)));
    } catch (InboxException conflict) {
      TemporaryInfrastructureException.preserveFatal(conflict);
      if (conflict.getSuppressed().length != 0) throw conflict;
      if (conflict.reason() == InboxException.Reason.OPERATION_TOKEN_REUSE) {
        audit(connection, Optional.of(actor), request, "QUESTION_SUBMITTED", "0105", received);
        return new Denied(ResultCode.CONFLICT);
      }
      if (conflict.reason() == InboxException.Reason.MESSAGE_ID_REUSE) {
        audit(
            connection,
            Optional.of(actor),
            request,
            "PROTOCOL_REJECTED",
            "MESSAGE_IDENTITY",
            received);
        return new InvalidMessage();
      }
      throw conflict;
    }
    Accepted result = read(request, actor, bound);
    if (result.replay())
      audit(connection, Optional.of(actor), request, "INBOX_REPLAYED", "0200", received);
    return result;
  }

  private InboxCompletion create(
      Connection connection, QuestionSubmitRequest request, AuthenticatedActor actor, Instant at)
      throws SQLException {
    char[] body = request.copyQuestion();
    try {
      // Only NEW enters this guard. Existing Inbox HMAC always takes precedence over DB text.
      try (var statement =
          connection.prepareStatement(
              "select body from schubert.questions where owner_user_id=? and operation_token=?")) {
        statement.setLong(1, actor.userId());
        statement.setObject(2, request.operationToken());
        try (var row = statement.executeQuery()) {
          if (row.next())
            throw new RetainedRequest(
                requireValue(row.getString(1)).equals(new String(body))
                    ? ResultCode.TEMPORARY_FAILURE
                    : ResultCode.CONFLICT,
                Optional.of(actor));
        }
      }
      QuestionSubmitResponseData data = insertQuestion(connection, request, actor, body, at);
      long job;
      try (var statement =
          connection.prepareStatement(
              """
          insert into schubert.async_jobs(question_id,owner_user_id,state,message_id,correlation_id,
          received_at,state_changed_at) values (?,?,'RECEIVED',?,?,?,?) returning id
          """)) {
        statement.setLong(1, data.questionId().value());
        statement.setLong(2, actor.userId());
        statement.setObject(3, request.header().messageId());
        statement.setObject(4, request.header().messageId());
        statement.setObject(5, at.atOffset(ZoneOffset.UTC));
        statement.setObject(6, at.atOffset(ZoneOffset.UTC));
        job = oneId(statement);
      }
      try (var statement =
          connection.prepareStatement(
              """
          insert into schubert.notifications(job_id,question_id,owner_user_id,notification_type,
          state,accepted_at,state_changed_at,created_at,updated_at)
          values (?,?,?,'ACCEPTED','RECEIVED',?,?,?,?)
          """)) {
        statement.setLong(1, job);
        statement.setLong(2, data.questionId().value());
        statement.setLong(3, actor.userId());
        for (int i = 4; i <= 7; i++) statement.setObject(i, at.atOffset(ZoneOffset.UTC));
        requireOne(statement.executeUpdate());
      }
      UUID work = Objects.requireNonNull(identifiers.get(), "work identifier");
      require(!work.equals(request.header().messageId()));
      byte[] wire = workWire(work, request.header().messageId(), data, job, at);
      try {
        outbox.enqueue(
            connection,
            new OutboxRequest(
                work,
                request.header().messageId(),
                OutboxDestination.ASYNC_WORK,
                "QWKREQ01",
                LITERAL_001,
                wire,
                at,
                at));
      } finally {
        Arrays.fill(wire, (byte) 0);
      }
      audit(
          connection,
          Optional.of(actor),
          request,
          "QUESTION_SUBMITTED",
          "0000",
          at,
          ",\"receiptId\":\""
              + data.receiptId()
              + "\",\"jobId\":"
              + job
              + ",\"questionId\":"
              + data.questionId().value()
              + ",\"state\":\"RECEIVED\"");
      var reference =
          InboxResultReference.numeric(
              InboxResultReferenceType.QUESTION, data.questionId().value());
      byte[] saved = reply(request, Optional.of(data), ResultCode.SUCCESS, at);
      try {
        return new InboxCompletion(
            InboxCompletionState.COMPLETED,
            reference,
            LITERAL_QSBRSP01,
            LITERAL_001,
            Optional.of(
                snapshots.encrypt(
                    identity(request.header().messageId(), actor),
                    reference,
                    request.operationToken(),
                    saved)),
            at);
      } finally {
        Arrays.fill(saved, (byte) 0);
      }
    } finally {
      Arrays.fill(body, '\0');
    }
  }

  private QuestionSubmitResponseData insertQuestion(
      Connection connection,
      QuestionSubmitRequest request,
      AuthenticatedActor actor,
      char[] body,
      Instant at)
      throws SQLException {
    // Savepoint retries only the named receipt collision, not owner/token/id/FK failures.
    for (int attempt = 0; attempt < 3; attempt++) {
      String receipt = receipts.generate().value();
      Savepoint before = connection.setSavepoint();
      try (var statement =
          connection.prepareStatement(
              """
          insert into schubert.questions(receipt_id,owner_user_id,body,operation_token,submitted_at)
          values (?,?,?,?,?) returning id
          """)) {
        statement.setString(1, receipt);
        statement.setLong(2, actor.userId());
        statement.setString(3, new String(body));
        statement.setObject(4, request.operationToken());
        statement.setObject(5, at.atOffset(ZoneOffset.UTC));
        long id = oneId(statement);
        connection.releaseSavepoint(before);
        return new QuestionSubmitResponseData(
            receipt, new QuestionId(id), at.truncatedTo(ChronoUnit.MILLIS));
      } catch (SQLException failure) {
        TemporaryInfrastructureException.preserveFatal(failure);
        // BUG2699/YKT2373: a failed close cannot be recovered as a clean receipt collision.
        if (failure.getSuppressed().length != 0) throw failure;
        if (!(failure instanceof PSQLException postgres) || !"23505".equals(failure.getSQLState()))
          throw failure;
        var error = postgres.getServerErrorMessage();
        if (error == null || !"uq_questions_receipt_id".equals(error.getConstraint()))
          throw failure;
        connection.rollback(before);
        connection.releaseSavepoint(before);
      }
    }
    throw new SQLException("receipt identity collision budget exhausted", "40001");
  }

  private Accepted read(
      QuestionSubmitRequest request, AuthenticatedActor actor, BoundInboxExecution bound) {
    var execution = bound.execution();
    require(execution.status() != InboxExecutionStatus.IN_PROGRESS);
    var completion = execution.completion().orElseThrow();
    require(completion.state() == InboxCompletionState.COMPLETED);
    require(completion.responseLayoutId().equals(LITERAL_QSBRSP01));
    require(completion.responseVersion().equals(LITERAL_001));
    byte[] body =
        snapshots.decrypt(
            identity(bound.sourceMessageId(), actor),
            completion.resultReference(),
            request.operationToken(),
            completion.responseSnapshot().orElseThrow());
    try {
      var header = HeaderCodec.standard().peek(body);
      require(header.layoutId().value().equals(LITERAL_QSBRSP01));
      require(header.correlationId().equals(bound.sourceMessageId()));
      require(header.resultCode().orElseThrow() == ResultCode.SUCCESS);
      require(header.sentAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
      byte[] payload = Arrays.copyOfRange(body, 256, 320);
      try {
        var data =
            (QuestionSubmitResponseData)
                PayloadTypeCatalog.decode(
                        PayloadCodec.standard()
                            .decode(header.layoutId(), payload, List.of(), ResultCode.SUCCESS))
                    .data();
        require(
            data.questionId().value() == completion.resultReference().numericId().orElseThrow());
        require(data.submittedAt().equals(completion.completedAt().truncatedTo(ChronoUnit.MILLIS)));
        return new Accepted(
            actor,
            data,
            bound.sourceMessageId(),
            completion.completedAt(),
            execution.status() == InboxExecutionStatus.REPLAY);
      } finally {
        Arrays.fill(payload, (byte) 0);
      }
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  private boolean sent(Accepted accepted, QuestionSubmitRequest request, long start, long budget)
      throws SQLException {
    try (var connection = Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      connection.setReadOnly(true);
      try {
        timeout(connection, start, budget);
        boolean sent = proof(connection, accepted, request);
        connection.commit();
        return sent;
      } catch (SQLException | RuntimeException | Error failure) {
        rollback(connection, failure);
        throw failure;
      }
    }
  }

  private boolean proof(Connection connection, Accepted accepted, QuestionSubmitRequest request)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            """
        select q.owner_user_id,q.operation_token,q.receipt_id,j.id as job_id,j.message_id as original,
        j.correlation_id as job_correlation,j.owner_user_id as job_owner,o.message_id as work_id,
        o.body,o.created_at,o.status,o.sent_at,o.lease_owner,o.lease_until,
        o.dlq_original_message_id,o.dlq_original_transport_id,o.dlq_delivery_count,
        o.dlq_error_code,o.dlq_detected_at
        from schubert.questions q join schubert.async_jobs j on j.question_id=q.id
        join schubert.mq_outbox o on o.correlation_id=j.message_id
        where q.id=? and o.destination='nk.async.work' and o.layout_id='QWKREQ01'
        and o.layout_version='001'
        """)) {
      statement.setLong(1, accepted.data().questionId().value());
      try (var row = statement.executeQuery()) {
        require(row.next());
        require(
            requireValue(row.getObject("owner_user_id", Long.class)) == accepted.actor().userId());
        require(
            requireValue(row.getObject("operation_token", UUID.class))
                .equals(request.operationToken()));
        require(requireValue(row.getString("receipt_id")).equals(accepted.data().receiptId()));
        require(requireValue(row.getObject("original", UUID.class)).equals(accepted.source()));
        require(
            requireValue(row.getObject("job_correlation", UUID.class)).equals(accepted.source()));
        require(requireValue(row.getObject("job_owner", Long.class)) == accepted.actor().userId());
        long job = requireValue(row.getObject("job_id", Long.class));
        UUID work = requireValue(row.getObject("work_id", UUID.class));
        require(!work.equals(accepted.source()));
        require(
            requireValue(row.getObject("created_at", OffsetDateTime.class))
                .toInstant()
                .equals(accepted.completed()));
        for (String name :
            List.of(
                "dlq_original_message_id",
                "dlq_original_transport_id",
                "dlq_delivery_count",
                "dlq_error_code",
                "dlq_detected_at")) require(row.getObject(name) == null);
        byte[] actual = requireValue(row.getBytes("body"));
        byte[] expected =
            workWire(work, accepted.source(), accepted.data(), job, accepted.completed());
        try {
          require(java.security.MessageDigest.isEqual(actual, expected));
        } finally {
          Arrays.fill(actual, (byte) 0);
          Arrays.fill(expected, (byte) 0);
        }
        String status = requireValue(row.getString("status"));
        require(List.of("PENDING", "ERROR", "SENT").contains(status));
        OffsetDateTime sentAt = row.getObject("sent_at", OffsetDateTime.class);
        boolean sent = status.equals("SENT");
        if (sent) {
          require(!requireValue(sentAt).toInstant().isBefore(accepted.completed()));
          require(row.getString("lease_owner") == null);
          require(row.getObject("lease_until") == null);
        } else require(sentAt == null);
        require(!row.next());
        return sent;
      }
    }
  }

  private void timeout(Connection connection, long start, long budget) throws SQLException {
    long remaining = budget - (nanos.getAsLong() - start);
    if (remaining <= 0) throw new RetainedRequest(ResultCode.TEMPORARY_FAILURE);
    // PostgreSQL's 0 means infinite. Round up, never silently disable the remaining budget.
    long millis = Math.max(1, (remaining + 999_999) / 1_000_000);
    try (var statement =
        connection.prepareStatement("select set_config('statement_timeout',?,true)")) {
      statement.setString(1, millis + "ms");
      try (var row = statement.executeQuery()) {
        require(row.next());
      }
    }
  }

  private byte[] failure(QuestionSubmitRequest request, ResultCode code) {
    return reply(request, Optional.empty(), code);
  }

  private void auditRetained(QuestionSubmitRequest request, RetainedRequest retained)
      throws SQLException {
    try (var connection = Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      connection.setAutoCommit(false);
      try {
        audit(
            connection,
            Optional.of(
                new AuthenticatedActor(retained.actorId, retained.actorName, retained.actorRole)),
            request,
            "QUESTION_SUBMITTED",
            retained.code == ResultCode.CONFLICT ? "0105" : "9000",
            clock.instant());
        connection.commit();
      } catch (SQLException | RuntimeException | Error failure) {
        rollback(connection, failure);
        throw failure;
      }
    }
  }

  private byte[] reply(
      QuestionSubmitRequest request, Optional<QuestionSubmitResponseData> data, ResultCode code) {
    return reply(request, data, code, clock.instant());
  }

  private byte[] reply(
      QuestionSubmitRequest request,
      Optional<QuestionSubmitResponseData> data,
      ResultCode code,
      Instant at) {
    var layout = new LayoutId(LITERAL_QSBRSP01);
    var payload =
        PayloadCodec.standard()
            .encode(
                new PayloadValues(
                    layout,
                    data.isPresent() ? data.orElseThrow().fields() : FieldValueSet.empty(),
                    List.of()),
                code);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            layout,
            1,
            MessageKind.RESPONSE,
            InteractionKind.ASYNC_ACCEPTANCE,
            Objects.requireNonNull(identifiers.get(), "response ID"),
            request.header().messageId(),
            at.truncatedTo(ChronoUnit.MILLIS),
            request.header().authenticationContext(),
            256,
            64,
            0,
            0,
            320,
            Optional.of(code));
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static byte[] workWire(
      UUID work, UUID source, QuestionSubmitResponseData data, long job, Instant at) {
    var layout = new LayoutId("QWKREQ01");
    var values =
        PayloadTypeCatalog.encode(
            new TypedPayloadValues(
                layout,
                new QuestionWorkData(data.receiptId(), data.questionId(), new AsyncJobId(job)),
                List.of()));
    var payload = PayloadCodec.standard().encode(values, false);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            layout,
            1,
            MessageKind.EVENT,
            InteractionKind.INTERNAL,
            work,
            source,
            at.truncatedTo(ChronoUnit.MILLIS),
            Optional.empty(),
            256,
            64,
            0,
            0,
            320,
            Optional.empty());
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static ResponseSnapshotIdentity identity(UUID source, AuthenticatedActor actor) {
    return ResponseSnapshotIdentity.authenticated(
        source, LITERAL_QSBRSP01, LITERAL_001, actor.userId());
  }

  private static long oneId(PreparedStatement statement) throws SQLException {
    try (var row = statement.executeQuery()) {
      require(row.next());
      long id = requireValue(row.getObject(1, Long.class));
      require(!row.next());
      return id;
    }
  }

  private static void audit(
      Connection connection,
      Optional<AuthenticatedActor> actor,
      QuestionSubmitRequest request,
      String action,
      String result,
      Instant at)
      throws SQLException {
    audit(connection, actor, request, action, result, at, "");
  }

  /** Suffix is constructed only at NEW acceptance from validated receipt/numeric IDs. */
  private static void audit(
      Connection connection,
      Optional<AuthenticatedActor> actor,
      QuestionSubmitRequest request,
      String action,
      String result,
      Instant at,
      String detailsSuffix)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            """
        insert into schubert.app_logs(logged_at,service,category,level,action,message,
        message_id,correlation_id,actor_user_id,actor_username,details)
        values (?,'API',?,'INFO',?,?,?,?,?,?,cast(? as jsonb))
        """)) {
      statement.setObject(1, at.atOffset(ZoneOffset.UTC));
      statement.setString(
          2,
          action.equals("AUTHORIZATION_DENIED")
              ? "SECURITY"
              : action.equals("INBOX_REPLAYED") || action.equals("PROTOCOL_REJECTED")
                  ? "MQ"
                  : "ACTION");
      statement.setString(3, action);
      statement.setString(4, action);
      statement.setObject(5, request.header().messageId());
      statement.setObject(6, request.header().correlationId());
      if (actor.isPresent()) {
        statement.setLong(7, actor.orElseThrow().userId());
        statement.setString(
            8,
            java.text.Normalizer.normalize(
                    actor.orElseThrow().username(), java.text.Normalizer.Form.NFC)
                .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
      } else {
        statement.setNull(7, Types.BIGINT);
        statement.setNull(8, Types.VARCHAR);
      }
      statement.setString(
          9,
          "{\"layout\":\"QSBREQ01\",\""
              + (action.equals("PROTOCOL_REJECTED") ? "step" : "resultCode")
              + "\":\""
              + result
              + "\""
              + detailsSuffix
              + "}");
      requireOne(statement.executeUpdate());
    }
  }

  private static void requireOne(int count) {
    require(count == 1);
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("question acceptance evidence is inconsistent");
  }

  private static void rollback(Connection connection, Throwable failure) {
    try {
      connection.rollback();
    } catch (SQLException | RuntimeException | Error rollback) {
      TemporaryInfrastructureException.attachSecondary(failure, rollback);
    }
  }

  private sealed interface Outcome permits Accepted, Denied, InvalidMessage {}

  private record InvalidMessage() implements Outcome {}

  private record Accepted(
      AuthenticatedActor actor,
      QuestionSubmitResponseData data,
      UUID source,
      Instant completed,
      boolean replay)
      implements Outcome {}

  private record Denied(ResultCode code) implements Outcome {}

  private static final class RetainedRequest extends RuntimeException {
    private static final long serialVersionUID = 1L;
    private final ResultCode code;
    private final long actorId;
    private final String actorName;
    private final dev.codex.schubert.nk.api.domain.Role actorRole;

    RetainedRequest(ResultCode code) {
      this(code, Optional.empty());
    }

    RetainedRequest(ResultCode code, Optional<AuthenticatedActor> actor) {
      super("historical acceptance unavailable");
      this.code = code;
      actorId = actor.map(AuthenticatedActor::userId).orElse(0L);
      actorName = actor.map(AuthenticatedActor::username).orElse("");
      actorRole =
          actor.map(AuthenticatedActor::role).orElse(dev.codex.schubert.nk.api.domain.Role.USER);
    }
  }
}
