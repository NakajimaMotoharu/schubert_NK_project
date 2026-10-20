package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.messaging.inbound.DeliveryMetadata;
import dev.codex.schubert.nk.api.messaging.inbound.InternalEventProcessor;
import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDestination;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDlqMetadata;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxRequest;
import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.QuestionWorkData;
import java.nio.CharBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Types;
import java.text.Normalizer;
import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.locks.LockSupport;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import javax.sql.DataSource;

/**
 * One FIFO QWK delivery: short DB transition, connection-free provider, atomic completion. Final
 * retry ERROR owns a new immutable DLQ dispatch and returns only after its real SENT.
 * Pool/provider/dispatcher/stop flag are borrowed; listener owns original JMS transaction.
 * NK-QST-001/NK-ASY-001; QST003/ASY001..009/MQ006..010; UI213224236242;
 * SS312§8/9,324,331,332§8,351,353§7.2; SSC153..156; AWORK001..013.
 */
public final class QuestionWorkerService implements InternalEventProcessor {
  private static final int TERMINAL_DELIVERY_COUNT = 4;

  private static final java.lang.String LITERAL_QWKREQ01 = "QWKREQ01";

  private static final java.lang.String LITERAL_COMPLETED = "COMPLETED";

  private static final java.lang.String LITERAL_ERROR = "ERROR";

  private static final java.lang.String LITERAL_PROCESSING = "PROCESSING";

  private static final java.lang.String LITERAL_BODY = "body";

  private static final java.lang.String LITERAL_CORRELATION_ID = "correlation_id";

  private static final Instant MIN = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant MAX = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final DataSource database;
  private final AnswerProvider provider;
  private final Runnable wakeDispatcher;
  private final BooleanSupplier stopping;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final JdbcOutboxRepository outbox = new JdbcOutboxRepository();

  public QuestionWorkerService(
      DataSource database,
      AnswerProvider provider,
      Runnable wakeDispatcher,
      BooleanSupplier stopping,
      Clock clock) {
    this(database, provider, wakeDispatcher, stopping, clock, UUID::randomUUID);
  }

  QuestionWorkerService(
      DataSource database,
      AnswerProvider provider,
      Runnable wakeDispatcher,
      BooleanSupplier stopping,
      Clock clock,
      Supplier<UUID> identifiers) {
    this.database = Objects.requireNonNull(database, "database");
    this.provider = Objects.requireNonNull(provider, "provider");
    this.wakeDispatcher = Objects.requireNonNull(wakeDispatcher, "dispatcher signal");
    this.stopping = Objects.requireNonNull(stopping, "stop signal");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
  }

  /** Missing actual metadata is never silently treated as the first delivery. */
  @Override
  public void process(WireMessage<FixedPayload> event) {
    Objects.requireNonNull(event, "event");
    throw new TemporaryInfrastructureException();
  }

  @Override
  public void process(WireMessage<FixedPayload> event, DeliveryMetadata delivery) {
    Objects.requireNonNull(event, "event");
    Objects.requireNonNull(delivery, "delivery");
    byte[] wire = decodeWire(event);
    try {
      checkRunning();
      var work =
          (QuestionWorkData)
              PayloadTypeCatalog.decode(
                      PayloadCodec.standard()
                          .decode(
                              event.header().layoutId(),
                              event.payload().copyData(),
                              List.of(),
                              false))
                  .data();
      Stage stage = transaction(c -> begin(c, event.header(), work, wire, delivery));
      if (stage instanceof PendingDlq pending) {
        awaitSent(event.header(), wire, pending);
        return;
      }
      if (stage == Terminal.INSTANCE) return;
      Ready ready = (Ready) stage;
      AnswerResult answer;
      try {
        answer = Objects.requireNonNull(provider.answer(ready.question), "provider result");
      } catch (AnswerBusinessException expected) {
        transaction(c -> fail(c, event.header(), work, wire, delivery, "PROCESS_FAILED", false));
        return;
      } catch (RuntimeException unavailable) {
        if (delivery.deliveryCount() < TERMINAL_DELIVERY_COUNT)
          throw new TemporaryInfrastructureException();
        Stage failed =
            transaction(c -> fail(c, event.header(), work, wire, delivery, "SYSTEM_UNAVAIL", true));
        if (failed instanceof PendingDlq pending) awaitSent(event.header(), wire, pending);
        return;
      }
      transaction(c -> complete(c, event.header(), work, wire, answer));
    } catch (PermanentProtocolException invalid) {
      if (invalid.getSuppressed().length != 0) throw new TemporaryInfrastructureException();
      throw invalid;
    } catch (SQLException | RuntimeException unavailable) {
      throw new TemporaryInfrastructureException();
    } finally {
      Arrays.fill(wire, (byte) 0);
    }
  }

  private static byte[] decodeWire(WireMessage<FixedPayload> event) {
    try {
      CommonHeader h = event.header();
      require(h.layoutId().value().equals(LITERAL_QWKREQ01));
      h.validateAgainst(LayoutRegistry.standard().require(h.layoutId(), 1));
      return FixedWidthEncoder.standard().encode(event);
    } catch (IllegalArgumentException invalid) {
      throw new PermanentProtocolException("question work wire is invalid");
    }
  }

  private Stage begin(
      Connection c, CommonHeader h, QuestionWorkData work, byte[] wire, DeliveryMetadata delivery)
      throws SQLException {
    Job job = job(c, h, work, wire);
    if (job.state.equals("CANCELLED")) return Terminal.INSTANCE;
    if (job.state.equals(LITERAL_COMPLETED)) {
      verifyCompleted(c, job);
      return Terminal.INSTANCE;
    }
    if (job.state.equals(LITERAL_ERROR)) return errorStage(c, h, wire, job);
    Instant at = now();
    if (at.isBefore(job.received)) throw new TemporaryInfrastructureException();
    if (job.state.equals("RECEIVED")) {
      try (var s =
          c.prepareStatement(
              """
          update schubert.async_jobs set state='PROCESSING',processing_message_id=?,
          started_at=?,state_changed_at=?,retry_count=?,version=version+1
          where id=? and state='RECEIVED'
          """)) {
        s.setObject(1, h.messageId());
        s.setObject(2, at.atOffset(ZoneOffset.UTC));
        s.setObject(3, at.atOffset(ZoneOffset.UTC));
        s.setInt(4, Math.min(delivery.deliveryCount() - 1, 3));
        s.setLong(5, job.id);
        one(s.executeUpdate());
      }
      notification(c, job, LITERAL_PROCESSING, "ACCEPTED", at, Optional.empty());
      audit(c, h, job, "QUESTION_PROCESSING_STARTED", LITERAL_PROCESSING, at);
    } else {
      require(job.state.equals(LITERAL_PROCESSING));
      require(job.processing.orElseThrow().equals(h.messageId()));
      try (var s = c.prepareStatement("update schubert.async_jobs set retry_count=? where id=?")) {
        s.setInt(1, Math.min(delivery.deliveryCount() - 1, 3));
        s.setLong(2, job.id);
        one(s.executeUpdate());
      }
    }
    return new Ready(job.body);
  }

  private Stage complete(
      Connection c, CommonHeader h, QuestionWorkData work, byte[] wire, AnswerResult answer)
      throws SQLException {
    Job job = job(c, h, work, wire);
    if (job.state.equals(LITERAL_COMPLETED)) {
      verifyCompleted(c, job);
      return Terminal.INSTANCE;
    }
    require(job.state.equals(LITERAL_PROCESSING));
    require(job.processing.orElseThrow().equals(h.messageId()));
    Instant at = answer.answeredAt().truncatedTo(ChronoUnit.MICROS);
    String body = Normalizer.normalize(answer.body(), Normalizer.Form.NFC);
    boolean valid = finite(at) && !at.isBefore(job.started.orElseThrow()) && validBody(body);
    Deleted deleted = questionDeletion(c, job);
    boolean existing = false;
    try (var s =
        c.prepareStatement(
            """
        select body,provider_type,answered_at,is_deleted,deleted_at,deleted_by
        from schubert.answers where question_id=?
        """)) {
      s.setLong(1, job.questionId);
      try (var r = s.executeQuery()) {
        if (r.next()) {
          existing = true;
          valid &=
              requireValue(r.getString(LITERAL_BODY)).equals(body)
                  && requireValue(r.getString("provider_type")).equals("STUB")
                  && time(r, "answered_at").equals(at)
                  && deletion(r).equals(deleted);
          require(!r.next());
        }
      }
    }
    if (!valid) return businessError(c, h, job, "DATA_INTEGRITY", now());
    if (!existing) {
      try (var s =
          c.prepareStatement(
              """
          insert into schubert.answers(question_id,body,answered_at,provider_type,
          is_deleted,deleted_at,deleted_by,created_at,updated_at)
          values (?,?,?,'STUB',?,?,?,?,?)
          """)) {
        s.setLong(1, job.questionId);
        s.setString(2, body);
        s.setObject(3, at.atOffset(ZoneOffset.UTC));
        s.setBoolean(4, deleted.deleted());
        bindDeletion(s, 5, deleted);
        s.setObject(7, at.atOffset(ZoneOffset.UTC));
        s.setObject(8, at.atOffset(ZoneOffset.UTC));
        one(s.executeUpdate());
      }
    }
    try (var s =
        c.prepareStatement(
            """
        update schubert.async_jobs set state='COMPLETED',completed_at=?,state_changed_at=?,
        version=version+1 where id=? and state='PROCESSING' and processing_message_id=?
        """)) {
      s.setObject(1, at.atOffset(ZoneOffset.UTC));
      s.setObject(2, at.atOffset(ZoneOffset.UTC));
      s.setLong(3, job.id);
      s.setObject(4, h.messageId());
      one(s.executeUpdate());
    }
    notification(c, job, LITERAL_COMPLETED, LITERAL_COMPLETED, at, Optional.empty());
    audit(c, h, job, "QUESTION_COMPLETED", LITERAL_COMPLETED, at);
    return Terminal.INSTANCE;
  }

  private Stage fail(
      Connection c,
      CommonHeader h,
      QuestionWorkData work,
      byte[] wire,
      DeliveryMetadata delivery,
      String code,
      boolean dlq)
      throws SQLException {
    Job job = job(c, h, work, wire);
    if (job.state.equals(LITERAL_ERROR)) return errorStage(c, h, wire, job);
    require(job.state.equals(LITERAL_PROCESSING));
    require(job.processing.orElseThrow().equals(h.messageId()));
    Instant at = now();
    businessError(c, h, job, code, at);
    if (!dlq) return Terminal.INSTANCE;
    var metadata =
        new OutboxDlqMetadata(
            h.messageId(),
            delivery.transportMessageId(),
            delivery.deliveryCount(),
            OutboxDlqMetadata.RETRY_EXHAUSTED,
            at);
    UUID dispatch = Objects.requireNonNull(identifiers.get(), "DLQ dispatch ID");
    outbox.enqueue(
        c,
        new OutboxRequest(
            dispatch,
            h.correlationId(),
            OutboxDestination.DLQ,
            LITERAL_QWKREQ01,
            "001",
            wire,
            at,
            at,
            Optional.of(metadata)));
    return new PendingDlq(dispatch, metadata);
  }

  private Stage businessError(Connection c, CommonHeader h, Job job, String code, Instant at)
      throws SQLException {
    if (at.isBefore(job.started.orElseThrow())) throw new TemporaryInfrastructureException();
    try (var s =
        c.prepareStatement(
            """
        update schubert.async_jobs set state='ERROR',error_at=?,state_changed_at=?,
        last_error_code=?,last_error_message='Question work failed',version=version+1
        where id=? and state='PROCESSING' and processing_message_id=?
        """)) {
      s.setObject(1, at.atOffset(ZoneOffset.UTC));
      s.setObject(2, at.atOffset(ZoneOffset.UTC));
      s.setString(3, code);
      s.setLong(4, job.id);
      s.setObject(5, h.messageId());
      one(s.executeUpdate());
    }
    notification(c, job, LITERAL_ERROR, LITERAL_ERROR, at, Optional.of(code));
    audit(c, h, job, "QUESTION_FAILED", code, at);
    return Terminal.INSTANCE;
  }

  private Stage errorStage(Connection c, CommonHeader h, byte[] wire, Job job) throws SQLException {
    Stage result;
    try (var s =
        c.prepareStatement(
            """
        select message_id,correlation_id,body,dlq_original_transport_id,dlq_delivery_count,
        dlq_error_code,dlq_detected_at from schubert.mq_outbox
        where destination='nk.dead.letter' and dlq_original_message_id=?
        """)) {
      s.setObject(1, h.messageId());
      try (var r = s.executeQuery()) {
        if (!r.next()) {
          require(
              job.errorCode.orElseThrow().equals("PROCESS_FAILED")
                  || job.errorCode.orElseThrow().equals("DATA_INTEGRITY"));
          result = Terminal.INSTANCE;
        } else {
          UUID dispatch = requireValue(r.getObject("message_id", UUID.class));
          require(!dispatch.equals(h.messageId()));
          require(
              requireValue(r.getObject(LITERAL_CORRELATION_ID, UUID.class))
                  .equals(h.correlationId()));
          require(Arrays.equals(requireValue(r.getBytes(LITERAL_BODY)), wire));
          var metadata =
              new OutboxDlqMetadata(
                  h.messageId(),
                  requireValue(r.getString("dlq_original_transport_id")),
                  requireValue(r.getObject("dlq_delivery_count", Integer.class)),
                  requireValue(r.getString("dlq_error_code")),
                  time(r, "dlq_detected_at"));
          require(metadata.deliveryCount() >= 4);
          require(metadata.detectedAt().equals(job.errorAt.orElseThrow()));
          require(job.errorCode.orElseThrow().equals("SYSTEM_UNAVAIL"));
          require(!r.next());
          result = new PendingDlq(dispatch, metadata);
        }
      }
    } catch (PermanentProtocolException inconsistentProof) {
      // This is durable ERROR/send proof, not invalid inbound wire: never fatal-ACK it.
      throw new TemporaryInfrastructureException();
    }
    return result;
  }

  private void awaitSent(CommonHeader h, byte[] wire, PendingDlq pending) throws SQLException {
    checkRunning();
    wakeDispatcher.run();
    while (true) {
      checkRunning();
      boolean sent = transaction(c -> dlqSent(c, h, wire, pending));
      if (sent) return;
      // The caller still owns unacknowledged JMS delivery, never a DB connection/lock here.
      LockSupport.parkNanos(10_000_000);
    }
  }

  private static boolean dlqSent(Connection c, CommonHeader h, byte[] wire, PendingDlq pending)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            """
        select correlation_id,destination,layout_id,layout_version,body,status,sent_at,
        lease_owner,lease_until,created_at,dlq_original_message_id,dlq_original_transport_id,
        dlq_delivery_count,dlq_error_code,dlq_detected_at from schubert.mq_outbox where message_id=?
        """)) {
      s.setObject(1, pending.dispatch());
      try (var r = s.executeQuery()) {
        require(r.next());
        require(
            requireValue(r.getObject(LITERAL_CORRELATION_ID, UUID.class))
                .equals(h.correlationId()));
        require(requireValue(r.getString("destination")).equals("nk.dead.letter"));
        require(requireValue(r.getString("layout_id")).equals(LITERAL_QWKREQ01));
        require(requireValue(r.getString("layout_version")).equals("001"));
        require(Arrays.equals(requireValue(r.getBytes(LITERAL_BODY)), wire));
        var metadata =
            new OutboxDlqMetadata(
                requireValue(r.getObject("dlq_original_message_id", UUID.class)),
                requireValue(r.getString("dlq_original_transport_id")),
                requireValue(r.getObject("dlq_delivery_count", Integer.class)),
                requireValue(r.getString("dlq_error_code")),
                time(r, "dlq_detected_at"));
        require(metadata.equals(pending.metadata()));
        require(time(r, "created_at").equals(metadata.detectedAt()));
        String status = requireValue(r.getString("status"));
        boolean sent = status.equals("SENT");
        require(sent || status.equals("PENDING") || status.equals(LITERAL_ERROR));
        if (sent) {
          require(!time(r, "sent_at").isBefore(metadata.detectedAt()));
          require(r.getObject("lease_owner") == null && r.getObject("lease_until") == null);
        }
        require(!r.next());
        return sent;
      }
    } catch (PermanentProtocolException inconsistentProof) {
      throw new TemporaryInfrastructureException();
    }
  }

  private static Job job(Connection c, CommonHeader h, QuestionWorkData work, byte[] wire)
      throws SQLException {
    Job job;
    try (var s =
        c.prepareStatement(
            """
        select j.id,j.question_id,j.owner_user_id,j.message_id,j.correlation_id,j.state,
        j.processing_message_id,j.received_at,j.started_at,j.completed_at,j.error_at,j.last_error_code,
        q.owner_user_id as question_owner,q.receipt_id,q.body,u.username
        from schubert.async_jobs j join schubert.questions q on q.id=j.question_id
        join schubert.app_users u on u.id=j.owner_user_id where j.id=? for update of j
        """)) {
      s.setLong(1, work.asyncJobId().value());
      try (var r = s.executeQuery()) {
        require(r.next());
        long question = requireValue(r.getObject("question_id", Long.class));
        long owner = requireValue(r.getObject("owner_user_id", Long.class));
        String receipt = requireValue(r.getString("receipt_id"));
        UUID original = requireValue(r.getObject("message_id", UUID.class));
        Instant received = time(r, "received_at");
        require(question == work.questionId().value() && receipt.equals(work.receiptId()));
        require(owner == requireValue(r.getObject("question_owner", Long.class)));
        require(original.equals(h.correlationId()) && !original.equals(h.messageId()));
        require(requireValue(r.getObject(LITERAL_CORRELATION_ID, UUID.class)).equals(original));
        require(received.truncatedTo(ChronoUnit.MILLIS).equals(h.sentAt()));
        job =
            new Job(
                requireValue(r.getObject("id", Long.class)),
                question,
                owner,
                receipt,
                requireValue(r.getString("username")),
                requireValue(r.getString(LITERAL_BODY)),
                requireValue(r.getString("state")),
                received,
                Optional.ofNullable(r.getObject("processing_message_id", UUID.class)),
                optionalTime(r, "started_at"),
                optionalTime(r, "completed_at"),
                optionalTime(r, "error_at"),
                Optional.ofNullable(r.getString("last_error_code")));
        require(!r.next());
      }
    }
    try (var s =
        c.prepareStatement(
            """
        select message_id,correlation_id,layout_id,layout_version,body,created_at,
        dlq_original_message_id,dlq_original_transport_id,dlq_delivery_count,dlq_error_code,dlq_detected_at
        from schubert.mq_outbox where message_id=? and destination='nk.async.work'
        """)) {
      s.setObject(1, h.messageId());
      try (var r = s.executeQuery()) {
        require(r.next());
        require(
            requireValue(r.getObject(LITERAL_CORRELATION_ID, UUID.class))
                .equals(h.correlationId()));
        require(requireValue(r.getString("layout_id")).equals(LITERAL_QWKREQ01));
        require(requireValue(r.getString("layout_version")).equals("001"));
        require(Arrays.equals(requireValue(r.getBytes(LITERAL_BODY)), wire));
        require(time(r, "created_at").equals(job.received));
        for (String name :
            List.of(
                "dlq_original_message_id",
                "dlq_original_transport_id",
                "dlq_delivery_count",
                "dlq_error_code",
                "dlq_detected_at")) require(r.getObject(name) == null);
        require(!r.next());
      }
    }
    try (var s =
        c.prepareStatement(
            """
        select question_id,owner_user_id,state,accepted_at from schubert.notifications
        where job_id=? for update
        """)) {
      s.setLong(1, job.id);
      try (var r = s.executeQuery()) {
        require(r.next());
        require(requireValue(r.getObject("question_id", Long.class)) == job.questionId);
        require(requireValue(r.getObject("owner_user_id", Long.class)) == job.owner);
        require(requireValue(r.getString("state")).equals(job.state));
        require(time(r, "accepted_at").equals(job.received));
        require(!r.next());
      }
    }
    return job;
  }

  private static Deleted questionDeletion(Connection c, Job job) throws SQLException {
    try (var s =
        c.prepareStatement(
            """
        select is_deleted,deleted_at,deleted_by from schubert.questions where id=? for update
        """)) {
      s.setLong(1, job.questionId);
      try (var r = s.executeQuery()) {
        require(r.next());
        Deleted result = deletion(r);
        require(!r.next());
        return result;
      }
    }
  }

  private static Deleted deletion(ResultSet r) throws SQLException {
    boolean deleted = requireValue(r.getObject("is_deleted", Boolean.class));
    var at = optionalTime(r, "deleted_at");
    var by = Optional.ofNullable(r.getObject("deleted_by", Long.class));
    require(deleted == at.isPresent() && deleted == by.isPresent());
    return new Deleted(deleted, at, by);
  }

  private static void bindDeletion(PreparedStatement s, int offset, Deleted deleted)
      throws SQLException {
    if (deleted.deleted()) {
      s.setObject(offset, deleted.at().orElseThrow().atOffset(ZoneOffset.UTC));
      s.setLong(offset + 1, deleted.by().orElseThrow());
    } else {
      s.setNull(offset, Types.TIMESTAMP_WITH_TIMEZONE);
      s.setNull(offset + 1, Types.BIGINT);
    }
  }

  private static void verifyCompleted(Connection c, Job job) throws SQLException {
    Deleted deleted = questionDeletion(c, job);
    try (var s =
        c.prepareStatement(
            """
        select provider_type,answered_at,is_deleted,deleted_at,deleted_by
        from schubert.answers where question_id=?
        """)) {
      s.setLong(1, job.questionId);
      try (var r = s.executeQuery()) {
        require(r.next());
        require(requireValue(r.getString("provider_type")).equals("STUB"));
        require(time(r, "answered_at").equals(job.completed.orElseThrow()));
        require(deletion(r).equals(deleted));
        require(!r.next());
      }
    }
  }

  private static void notification(
      Connection c, Job job, String state, String type, Instant at, Optional<String> error)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            """
        update schubert.notifications set state=?,notification_type=?,state_changed_at=?,
        updated_at=?,error_code=?,error_message=? where job_id=? and state=?
        """)) {
      s.setString(1, state);
      s.setString(2, type);
      s.setObject(3, at.atOffset(ZoneOffset.UTC));
      s.setObject(4, at.atOffset(ZoneOffset.UTC));
      if (error.isPresent()) {
        s.setString(5, error.orElseThrow());
        s.setString(6, "Question work failed");
      } else {
        s.setNull(5, Types.VARCHAR);
        s.setNull(6, Types.VARCHAR);
      }
      s.setLong(7, job.id);
      s.setString(8, job.state);
      one(s.executeUpdate());
    }
  }

  private static void audit(
      Connection c, CommonHeader h, Job job, String action, String state, Instant at)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            """
        insert into schubert.app_logs(logged_at,service,category,level,action,message,message_id,
        correlation_id,actor_user_id,actor_username,details)
        values (?,'API','ACTION','INFO',?,'Question work state changed',?,?,?,?,cast(? as jsonb))
        """)) {
      s.setObject(1, at.atOffset(ZoneOffset.UTC));
      s.setString(2, action);
      s.setObject(3, h.messageId());
      s.setObject(4, h.correlationId());
      s.setLong(5, job.owner);
      s.setString(
          6,
          Normalizer.normalize(job.username, Normalizer.Form.NFC)
              .replaceAll("[\\r\\n\\t\\u2028\\u2029]", " "));
      s.setString(
          7,
          "{\"receiptId\":\""
              + job.receipt
              + "\",\"jobId\":"
              + job.id
              + ",\"questionId\":"
              + job.questionId
              + ",\"state\":\""
              + (action.equals("QUESTION_FAILED") ? LITERAL_ERROR : state)
              + "\""
              + (action.equals("QUESTION_FAILED") ? ",\"errorCode\":\"" + state + "\"" : "")
              + "}");
      one(s.executeUpdate());
    }
  }

  private <T> T transaction(DatabaseWork<T> work) throws SQLException {
    try (var c = Objects.requireNonNull(database.getConnection(), "JDBC connection")) {
      c.setAutoCommit(false);
      c.setReadOnly(false);
      c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
      try {
        try (var s =
            c.prepareStatement(
                "select set_config('statement_timeout','1500',true),set_config('lock_timeout','500',true)")) {
          try (var r = s.executeQuery()) {
            require(r.next());
          }
        }
        T result = work.execute(c);
        c.commit();
        return result;
      } catch (SQLException | RuntimeException | Error failure) {
        try {
          c.rollback();
        } catch (SQLException | RuntimeException cleanup) {
          failure.addSuppressed(cleanup);
        }
        throw failure;
      }
    }
  }

  private Instant now() {
    Instant result = clock.instant().truncatedTo(ChronoUnit.MICROS);
    if (!finite(result)) throw new TemporaryInfrastructureException();
    return result;
  }

  private void checkRunning() {
    if (stopping.getAsBoolean() || Thread.currentThread().isInterrupted())
      throw new TemporaryInfrastructureException();
  }

  private static boolean validBody(String body) {
    try {
      return StandardCharsets.UTF_8.newEncoder().encode(CharBuffer.wrap(body)).remaining() <= 4096;
    } catch (CharacterCodingException invalid) {
      return false;
    }
  }

  private static boolean finite(Instant at) {
    return !at.isBefore(MIN) && !at.isAfter(MAX);
  }

  private static Instant time(ResultSet r, String name) throws SQLException {
    Instant at = requireValue(r.getObject(name, OffsetDateTime.class)).toInstant();
    require(finite(at));
    return at;
  }

  private static Optional<Instant> optionalTime(ResultSet r, String name) throws SQLException {
    OffsetDateTime at = r.getObject(name, OffsetDateTime.class);
    if (at == null) return Optional.empty();
    Instant result = at.toInstant();
    require(finite(result));
    return Optional.of(result);
  }

  private static void one(int count) {
    require(count == 1);
  }

  private static void require(boolean valid) {
    if (!valid) throw new PermanentProtocolException("question work identity is inconsistent");
  }

  @FunctionalInterface
  private interface DatabaseWork<T> {
    T execute(Connection c) throws SQLException;
  }

  private sealed interface Stage permits Terminal, Ready, PendingDlq {}

  private enum Terminal implements Stage {
    INSTANCE
  }

  // Opaque internal object: Object.toString cannot expose the borrowed question body.
  private static final class Ready implements Stage {
    private final String question;

    private Ready(String question) {
      this.question = question;
    }
  }

  private record PendingDlq(UUID dispatch, OutboxDlqMetadata metadata) implements Stage {}

  private record Deleted(boolean deleted, Optional<Instant> at, Optional<Long> by) {}

  // SQL projection never escapes; no generated record toString containing body/username.
  private static final class Job {
    private final long id;
    private final long questionId;
    private final long owner;
    private final String receipt;
    private final String username;
    private final String body;
    private final String state;
    private final Instant received;
    private final Optional<UUID> processing;
    private final Optional<Instant> started;
    private final Optional<Instant> completed;
    private final Optional<Instant> errorAt;
    private final Optional<String> errorCode;

    private Job(
        long id,
        long questionId,
        long owner,
        String receipt,
        String username,
        String body,
        String state,
        Instant received,
        Optional<UUID> processing,
        Optional<Instant> started,
        Optional<Instant> completed,
        Optional<Instant> errorAt,
        Optional<String> errorCode) {
      this.id = id;
      this.questionId = questionId;
      this.owner = owner;
      this.receipt = receipt;
      this.username = username;
      this.body = body;
      this.state = state;
      this.received = received;
      this.processing = processing;
      this.started = started;
      this.completed = completed;
      this.errorAt = errorAt;
      this.errorCode = errorCode;
    }
  }
}
