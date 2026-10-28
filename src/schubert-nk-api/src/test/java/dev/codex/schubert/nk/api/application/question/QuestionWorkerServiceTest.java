package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.CONTEXT;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.Fixture;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.M0;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.NOW;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.RECEIPT;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.TOKEN;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.broker;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.invoke;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.request;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.response;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.work;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.inbound.DeliveryMetadata;
import dev.codex.schubert.nk.api.messaging.inbound.QuestionWorkListener;
import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcher;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxJmsSender;
import dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcher;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import jakarta.jms.BytesMessage;
import jakarta.jms.JMSContext;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** AWORK001..006: real PG18 and JMS, independently literal QWK/SQL; not Linux IT/ST. */
class QuestionWorkerServiceTest {
  private static final String FIXTURE_SELECT_STATUS_FROM_SCHUBERT_MQ_OUTBOX_WH_71AC8AB8 =
      "select status from schubert.mq_outbox where destination='nk.dead.letter'";
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_APP_LOGS_WHER_E5BBEC80 =
      "select count(*) from schubert.app_logs where action='QUESTION_COMPLETED'";
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B =
      "select count(*) from schubert.answers";
  private static final String FIXTURE_SELECT_COUNT_FROM_SCHUBERT_MQ_OUTBOX_73BAB5AA =
      "select count(*) from schubert.mq_outbox";
  private static final String FIXTURE_VM_0_0C76084A = "vm://0";
  private static final String FIXTURE_PUBLIC_FIXTURE_2BAE0C98 = "Public fixture";
  private static final String FIXTURE_PRIVATE_PROVIDER_9ABB4509 = "private-provider";
  private static final String FIXTURE_PROCESSING_01F94682 = "PROCESSING";
  private static final String FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91 =
      "select state from schubert.async_jobs";
  private static final String FIXTURE_COMPLETED_BA0AE16A = "COMPLETED";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_DATA_INTEGRITY_9097EAE7 = "DATA_INTEGRITY";
  private static final String FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3 =
      "select error_code from schubert.notifications";
  private static final String FIXTURE_RECEIVED_35302D54 = "RECEIVED";
  private static final String FIXTURE_JMSXDELIVERYCOUNT_90AF07ED = "JMSXDeliveryCount";
  private static final String FIXTURE_PENDING_B11DB31F = "PENDING";
  @TempDir static Path databaseRoot;
  static ApiLogDatabaseFixture database;
  static final UUID W = new UUID(700, 1);
  static final UUID D = new UUID(900, 1);

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(databaseRoot);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void awork001ActualAcceptanceBrokerWorkerEmptyAnswerAndReplay(@TempDir Path brokerRoot)
      throws Exception {
    var broker = broker(brokerRoot);
    try (var h = new Fixture(database);
        var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      factory.setConsumerWindowSize(0);
      try (var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
          var consumer =
              receiving.createConsumer(new ActiveMQQueue("nk.async.work::nk.async.work.q"));
          var owned = owned(factory, h.clock)) {
        h.signal = owned::wake;
        assertArrayEquals(
            response(M0, new UUID(700, 3), "0000", RECEIPT, 1, NOW),
            h.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        BytesMessage incoming = (BytesMessage) consumer.receive(2000);
        assertNotNull(incoming);
        var body = new byte[(int) incoming.getBodyLength()];
        assertEquals(320, incoming.readBytes(body));
        assertArrayEquals(work(W, M0, RECEIPT, 1, 1, NOW), body);
        incoming.reset();
        AtomicInteger calls = new AtomicInteger();
        var worker =
            new QuestionWorkerService(
                h.source,
                text -> {
                  assertEquals(0, h.live.get());
                  assertEquals(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, text);
                  calls.incrementAndGet();
                  return new StubAnswerProvider(h.clock).answer(text);
                },
                owned::wake,
                () -> false,
                h.clock);
        new QuestionWorkListener(worker, h.clock).onMessage(receiving, incoming);
        assertEquals(1, calls.get());
        assertEquals("", h.text("select body from schubert.answers"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.answers where provider_type='STUB' and not is_deleted and deleted_at is null and deleted_by is null and answered_at='2026-10-01T00:00:00.123456Z' and created_at=answered_at and updated_at=answered_at"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.async_jobs where state='COMPLETED' and processing_message_id='"
                    + W
                    + "' and retry_count=0 and received_at=started_at and started_at=completed_at and completed_at=state_changed_at and version=2"));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.notifications where state='COMPLETED' and notification_type='COMPLETED' and state_changed_at='2026-10-01T00:00:00.123456Z' and updated_at=state_changed_at and error_code is null"));
        assertEquals(
            2,
            h.scalar(
                "select count(*) from schubert.app_logs where action in('QUESTION_PROCESSING_STARTED','QUESTION_COMPLETED') and details->>'receiptId'='"
                    + RECEIPT
                    + "' and details->>'jobId'='1' and details->>'questionId'='1' and message_id='"
                    + W
                    + "' and correlation_id='"
                    + M0
                    + "'"));
        assertEquals(
            0,
            h.scalar(
                "select count(*) from schubert.app_logs where details::text like '%Public fixture%' or message like '%Public fixture%'"));
        worker.process(event(), delivery(2));
        assertEquals(1, calls.get());
        assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
        assertNull(consumer.receiveNoWait());
        assertArrayEquals(
            response(M0, new UUID(700, 4), "0200", RECEIPT, 1, NOW),
            h.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void awork002ProcessingRecoveryCancellationAndIdentityRefusal() throws Exception {
    try (var h = accepted()) {
      AtomicInteger calls = new AtomicInteger();
      var worker =
          worker(
              h,
              text -> {
                calls.incrementAndGet();
                throw new IllegalStateException(FIXTURE_PRIVATE_PROVIDER_9ABB4509);
              },
              () -> false);
      assertThrows(
          TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(1)));
      assertEquals(
          FIXTURE_PROCESSING_01F94682,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(0, h.scalar("select retry_count from schubert.async_jobs"));
      assertThrows(
          TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(3)));
      assertEquals(2, calls.get());
      assertEquals(2, h.scalar("select retry_count from schubert.async_jobs"));
      assertEquals(
          1,
          h.scalar(
              "select count(*) from schubert.app_logs where action='QUESTION_PROCESSING_STARTED'"));
      worker(h, text -> new AnswerResult("", NOW), () -> false).process(event(), delivery(4));
      assertEquals(
          FIXTURE_COMPLETED_BA0AE16A,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(3, h.scalar("select retry_count from schubert.async_jobs"));
    }
    try (var h = accepted()) {
      h.sql(
          "update schubert.async_jobs set state='CANCELLED',cancelled_at=received_at,version=1; update schubert.notifications set state='CANCELLED'");
      worker(
              h,
              text -> {
                fail("cancelled calls provider");
                return new AnswerResult("", NOW);
              },
              () -> false)
          .process(event(), delivery(1));
      assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      assertEquals("CANCELLED", h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      var wrong = event(new UUID(700, 99));
      assertThrows(
          PermanentProtocolException.class,
          () ->
              worker(h, text -> new AnswerResult("", NOW), () -> false)
                  .process(wrong, delivery(1)));
    }
  }

  @Test
  void awork003DeletionWhileProviderRunsIsInheritedAndContradictoryAnswerFails() throws Exception {
    try (var h = accepted()) {
      worker(
              h,
              text -> {
                assertEquals(0, h.live.get());
                h.sql(
                    "update schubert.questions set is_deleted=true,deleted_at='2026-10-01T00:00:00.123456Z',deleted_by=2,version=1");
                return new AnswerResult("", NOW.plusNanos(1000));
              },
              () -> false)
          .process(event(), delivery(1));
      assertEquals(
          1,
          h.scalar(
              "select count(*) from schubert.answers a join schubert.questions q on q.id=a.question_id where a.is_deleted and a.deleted_at=q.deleted_at and a.deleted_by=q.deleted_by and a.answered_at='2026-10-01T00:00:00.123457Z'"));
      assertEquals(
          1,
          h.scalar(
              "select count(*) from schubert.async_jobs j join schubert.notifications n on n.job_id=j.id where j.state='COMPLETED' and j.completed_at='2026-10-01T00:00:00.123457Z' and n.state_changed_at=j.completed_at"));
    }
    try (var h = accepted()) {
      h.sql(
          "insert into schubert.answers(question_id,body,answered_at,provider_type,created_at,updated_at) values(1,'Conflicting fixture','2026-10-01T00:00:00.123456Z','STUB','2026-10-01T00:00:00.123456Z','2026-10-01T00:00:00.123456Z')");
      worker(h, text -> new AnswerResult("", NOW), () -> false).process(event(), delivery(1));
      assertEquals(
          FIXTURE_ERROR_F717E7D8, h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(
          FIXTURE_DATA_INTEGRITY_9097EAE7,
          h.text(FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3));
      assertEquals("Conflicting fixture", h.text("select body from schubert.answers"));
      worker(
              h,
              text -> {
                fail("business ERROR provider replay");
                return new AnswerResult("", NOW);
              },
              () -> false)
          .process(event(), delivery(2));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_MQ_OUTBOX_73BAB5AA));
    }
  }

  @Test
  void awork004FinalErrorCommittedBeforePendingStopAndSameDispatchResume(@TempDir Path brokerRoot)
      throws Exception {
    var broker = broker(brokerRoot);
    try (var h = accepted();
        var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      factory.setConsumerWindowSize(0);
      String original =
          h.text("select md5(body)||':'||status||':'||sent_at::text from schubert.mq_outbox");
      AtomicBoolean stop = new AtomicBoolean();
      AtomicInteger calls = new AtomicInteger();
      h.signal =
          () -> {
            assertEquals(0, h.live.get());
            stop.set(true);
          };
      var worker =
          worker(
              h,
              text -> {
                calls.incrementAndGet();
                throw new IllegalStateException(FIXTURE_PRIVATE_PROVIDER_9ABB4509);
              },
              stop::get);
      assertThrows(
          TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(7)));
      assertEquals(1, calls.get());
      assertEquals(
          1,
          h.scalar(
              "select count(*) from schubert.async_jobs where state='ERROR' and retry_count=3 and last_error_code='SYSTEM_UNAVAIL' and error_at='2026-10-01T00:00:00.123456Z'"));
      assertEquals(
          1,
          h.scalar(
              "select count(*) from schubert.mq_outbox where destination='nk.dead.letter' and status='PENDING' and message_id='"
                  + D
                  + "' and dlq_original_message_id='"
                  + W
                  + "' and dlq_delivery_count=7 and dlq_original_transport_id='ID:independent-7' and dlq_error_code='QUESTION_RETRY_EXHAUSTED' and dlq_detected_at='2026-10-01T00:00:00.123456Z'"));
      assertEquals(
          original,
          h.text(
              "select md5(body)||':'||status||':'||sent_at::text from schubert.mq_outbox where destination='nk.async.work'"));
      stop.set(false);
      try (var owned = owned(factory, h.clock);
          var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
          var consumer =
              receiving.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
        h.signal = owned::wake;
        worker.process(event(), delivery(8));
        assertEquals(1, calls.get());
        BytesMessage dlq = (BytesMessage) consumer.receive(2000);
        assertNotNull(dlq);
        byte[] bytes = new byte[(int) dlq.getBodyLength()];
        assertEquals(320, dlq.readBytes(bytes));
        assertArrayEquals(work(W, M0, RECEIPT, 1, 1, NOW), bytes);
        assertEquals(W.toString(), dlq.getStringProperty("NKMessageID"));
        assertEquals(M0.toString(), dlq.getJMSCorrelationID());
        assertEquals(7, dlq.getIntProperty("NKDeliveryCount"));
        receiving.commit();
        assertEquals(2, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_MQ_OUTBOX_73BAB5AA));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
        assertNull(consumer.receiveNoWait());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void awork005BusinessFailureMalformedNullFaultAndCommitAtomicity() throws Exception {
    try (var h = accepted()) {
      var worker =
          worker(
              h,
              text -> {
                throw new AnswerBusinessException();
              },
              () -> false);
      worker.process(event(), delivery(1));
      assertEquals(
          "PROCESS_FAILED", h.text(FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_MQ_OUTBOX_73BAB5AA));
      worker.process(event(), delivery(2));
      assertThrows(TemporaryInfrastructureException.class, () -> worker.process(event()));
      assertThrows(NullPointerException.class, () -> worker.process(null, delivery(1)));
      assertThrows(NullPointerException.class, () -> worker.process(event(), null));
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              worker(h, text -> new AnswerResult("", NOW), () -> true)
                  .process(event(), delivery(1)));
    }
    for (String fault :
        List.of(
            "open", "null", "setAutoCommit", "setReadOnly", "setTransactionIsolation", "commit")) {
      try (var h = accepted()) {
        h.fault = fault;
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                worker(h, text -> new AnswerResult("", NOW), () -> false)
                    .process(event(), delivery(1)));
        assertEquals(
            FIXTURE_RECEIVED_35302D54,
            h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      }
    }
    for (String body : List.of("x".repeat(4097), "\ud800")) {
      try (var h = accepted()) {
        worker(h, text -> new AnswerResult(body, NOW), () -> false).process(event(), delivery(1));
        assertEquals(
            FIXTURE_DATA_INTEGRITY_9097EAE7,
            h.text(FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      }
    }
  }

  @Test
  void awork006RealFourthRollbackPreservesTwoPhysicalCopiesAndOneLogicalError(@TempDir Path root)
      throws Exception {
    for (boolean afterSent : List.of(false, true)) {
      var broker = broker(root.resolve(afterSent ? "after-sent" : "before-send"));
      try (var h = new Fixture(database);
          var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
        factory.setConsumerWindowSize(0);
        try (var owned = owned(factory, h.clock)) {
          h.signal = owned::wake;
          assertArrayEquals(
              response(M0, new UUID(700, 3), "0000", RECEIPT, 1, NOW),
              h.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        }
        String original =
            h.text("select md5(body)||':'||status||':'||sent_at::text from schubert.mq_outbox");
        AtomicInteger calls = new AtomicInteger();
        AtomicBoolean stop = new AtomicBoolean();
        var worker =
            worker(
                h,
                text -> {
                  assertEquals(0, h.live.get());
                  calls.incrementAndGet();
                  throw new IllegalStateException(FIXTURE_PRIVATE_PROVIDER_9ABB4509);
                },
                stop::get);
        var listener = new QuestionWorkListener(worker, h.clock);
        try (var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
            var consumer =
                receiving.createConsumer(new ActiveMQQueue("nk.async.work::nk.async.work.q"))) {
          long[] timeouts = {5000, 6000, 10000, 30000};
          for (int attempt = 1; attempt <= 3; attempt++) {
            var incoming = consumer.receive(timeouts[attempt - 1]);
            assertNotNull(incoming);
            assertEquals(attempt, incoming.getIntProperty(FIXTURE_JMSXDELIVERYCOUNT_90AF07ED));
            assertThrows(
                TemporaryInfrastructureException.class,
                () -> listener.onMessage(receiving, incoming));
          }
          var incoming = consumer.receive(timeouts[3]);
          assertNotNull(incoming);
          assertEquals(4, incoming.getIntProperty(FIXTURE_JMSXDELIVERYCOUNT_90AF07ED));
          if (afterSent) {
            try (var owned = owned(factory, h.clock)) {
              h.signal = owned::wake;
              var ackFault =
                  (JMSContext)
                      Proxy.newProxyInstance(
                          JMSContext.class.getClassLoader(),
                          new Class<?>[] {JMSContext.class},
                          (p, m, a) -> {
                            if (m.getName().equals("commit")) {
                              assertEquals(
                                  "SENT",
                                  h.text(
                                      FIXTURE_SELECT_STATUS_FROM_SCHUBERT_MQ_OUTBOX_WH_71AC8AB8));
                              throw new jakarta.jms.JMSRuntimeException(
                                  "independent ACK-window fault");
                            }
                            return invoke(receiving, m, a);
                          });
              assertThrows(
                  jakarta.jms.JMSRuntimeException.class,
                  () -> listener.onMessage(ackFault, incoming));
            }
          } else {
            h.signal = () -> stop.set(true);
            assertThrows(
                TemporaryInfrastructureException.class,
                () -> listener.onMessage(receiving, incoming));
            assertEquals(
                FIXTURE_PENDING_B11DB31F,
                h.text(FIXTURE_SELECT_STATUS_FROM_SCHUBERT_MQ_OUTBOX_WH_71AC8AB8));
          }
          assertNull(consumer.receive(500));
        }
        assertEquals(4, calls.get());
        stop.set(false);
        try (var owned = owned(factory, h.clock);
            var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
            var dlq =
                receiving.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
          h.signal = owned::wake;
          worker.process(event(), delivery(5));
          Set<String> transports = new HashSet<>();
          int application = 0;
          int brokerOnly = 0;
          for (int copy = 0; copy < 2; copy++) {
            BytesMessage physical = (BytesMessage) dlq.receive(2000);
            assertNotNull(physical);
            assertTrue(transports.add(physical.getJMSMessageID()));
            byte[] bytes = new byte[(int) physical.getBodyLength()];
            assertEquals(320, physical.readBytes(bytes));
            assertArrayEquals(work(W, M0, RECEIPT, 1, 1, NOW), bytes);
            assertEquals(W.toString(), physical.getStringProperty("NKMessageID"));
            assertEquals(M0.toString(), physical.getJMSCorrelationID());
            if (physical.propertyExists("NKErrorCode")) {
              application++;
              assertEquals("QUESTION_RETRY_EXHAUSTED", physical.getStringProperty("NKErrorCode"));
              assertEquals(4, physical.getIntProperty("NKDeliveryCount"));
              assertEquals("API_WORK", physical.getStringProperty("NKDetectedBy"));
            } else {
              brokerOnly++;
              assertFalse(physical.propertyExists("NKDetectedAt"));
            }
          }
          assertEquals(1, application);
          assertEquals(1, brokerOnly);
          receiving.commit();
          worker.process(event(), delivery(6));
          assertEquals(4, calls.get());
          assertNull(dlq.receive(500));
          assertEquals(
              1,
              h.scalar(
                  "select count(*) from schubert.mq_outbox where destination='nk.dead.letter' and status='SENT' and dlq_delivery_count=4"));
          assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
          assertEquals(
              original,
              h.text(
                  "select md5(body)||':'||status||':'||sent_at::text from schubert.mq_outbox where destination='nk.async.work'"));
        }
      } finally {
        broker.stop();
      }
    }
  }

  @Test
  void awork007PendingPollStopInterruptExistingAnswerAndConcurrentCompletion() throws Exception {
    try (var h = accepted();
        var executor = Executors.newSingleThreadExecutor()) {
      AtomicBoolean stop = new AtomicBoolean();
      CountDownLatch signal = new CountDownLatch(1);
      h.signal = signal::countDown;
      var worker =
          worker(
              h,
              text -> {
                throw new IllegalStateException("private");
              },
              stop::get);
      Future<?> pending = executor.submit(() -> worker.process(event(), delivery(4)));
      try {
        assertTrue(signal.await(3, TimeUnit.SECONDS));
        Thread.sleep(50);
        assertFalse(pending.isDone());
      } finally {
        stop.set(true);
      }
      assertInstanceOf(
          TemporaryInfrastructureException.class,
          assertThrows(ExecutionException.class, () -> pending.get(3, TimeUnit.SECONDS))
              .getCause());
      assertEquals(0, h.live.get());
      assertEquals(
          FIXTURE_ERROR_F717E7D8, h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(
          FIXTURE_PENDING_B11DB31F,
          h.text(FIXTURE_SELECT_STATUS_FROM_SCHUBERT_MQ_OUTBOX_WH_71AC8AB8));
    }
    try (var h = accepted()) {
      Thread.currentThread().interrupt();
      try {
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                worker(h, text -> new AnswerResult("", NOW), () -> false)
                    .process(event(), delivery(1)));
      } finally {
        assertTrue(Thread.interrupted());
      }
      assertEquals(
          FIXTURE_RECEIVED_35302D54,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      h.sql(
          "insert into schubert.answers(question_id,body,answered_at,provider_type,created_at,updated_at) values(1,'','2026-10-01T00:00:00.123456Z','STUB','2026-10-01T00:00:00.123456Z','2026-10-01T00:00:00.123456Z')");
      worker(h, text -> new AnswerResult("", NOW), () -> false).process(event(), delivery(1));
      assertEquals(
          FIXTURE_COMPLETED_BA0AE16A,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
    }
    try (var h = accepted()) {
      worker(
              h,
              text -> {
                worker(h, q -> new AnswerResult("", NOW), () -> false)
                    .process(event(), delivery(2));
                return new AnswerResult("", NOW);
              },
              () -> false)
          .process(event(), delivery(1));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_APP_LOGS_WHER_E5BBEC80));
    }
    try (var h = accepted()) {
      worker(
              h,
              text -> {
                worker(
                        h,
                        q -> {
                          throw new AnswerBusinessException();
                        },
                        () -> false)
                    .process(event(), delivery(2));
                throw new IllegalStateException("private");
              },
              () -> false)
          .process(event(), delivery(4));
      assertEquals(
          "PROCESS_FAILED", h.text(FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_MQ_OUTBOX_73BAB5AA));
    }
  }

  @Test
  void awork008MissingDurableDlqRollsBackRealOriginalAndCorruptProofIsNotFatal(@TempDir Path root)
      throws Exception {
    var broker = broker(root);
    try (var h = new Fixture(database);
        var factory = new ActiveMQConnectionFactory(FIXTURE_VM_0_0C76084A)) {
      factory.setConsumerWindowSize(0);
      try (var owned = owned(factory, h.clock)) {
        h.signal = owned::wake;
        h.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT));
      }
      AtomicBoolean stop = new AtomicBoolean();
      AtomicInteger calls = new AtomicInteger();
      var worker =
          worker(
              h,
              text -> {
                calls.incrementAndGet();
                throw new IllegalStateException(FIXTURE_PRIVATE_PROVIDER_9ABB4509);
              },
              stop::get);
      h.signal = () -> stop.set(true);
      assertThrows(
          TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(4)));
      stop.set(false);
      h.signal = () -> {};
      var corrupt =
          new QuestionWorkerService(
              tampered(h.source, "dlq-original"),
              text -> {
                fail("ERROR provider");
                return new AnswerResult("", NOW);
              },
              () -> {},
              () -> false,
              h.clock);
      assertThrows(
          TemporaryInfrastructureException.class, () -> corrupt.process(event(), delivery(5)));
      assertEquals(
          FIXTURE_PENDING_B11DB31F,
          h.text(FIXTURE_SELECT_STATUS_FROM_SCHUBERT_MQ_OUTBOX_WH_71AC8AB8));
      try (var c = database.admin();
          var s = c.createStatement()) {
        assertEquals(
            1,
            s.executeUpdate("delete from schubert.mq_outbox where destination='nk.dead.letter'"));
      }
      try (var receiving = factory.createContext(JMSContext.SESSION_TRANSACTED);
          var work = receiving.createConsumer(new ActiveMQQueue("nk.async.work::nk.async.work.q"));
          var readDlq = factory.createContext(JMSContext.SESSION_TRANSACTED);
          var dlq = readDlq.createConsumer(new ActiveMQQueue("nk.dead.letter::nk.dead.letter.q"))) {
        var incoming = work.receive(2000);
        assertNotNull(incoming);
        assertEquals(1, incoming.getIntProperty(FIXTURE_JMSXDELIVERYCOUNT_90AF07ED));
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> new QuestionWorkListener(worker, h.clock).onMessage(receiving, incoming));
        var redelivered = work.receive(6000);
        assertNotNull(redelivered);
        assertEquals(2, redelivered.getIntProperty(FIXTURE_JMSXDELIVERYCOUNT_90AF07ED));
        assertEquals(incoming.getJMSMessageID(), redelivered.getJMSMessageID());
        assertNull(dlq.receiveNoWait());
      }
      assertEquals(1, calls.get());
      assertEquals(
          FIXTURE_ERROR_F717E7D8, h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
    } finally {
      broker.stop();
    }
  }

  @Test
  void awork009NullContractsWireInputTimeBoundsNfcAndAtomicCompletionFaults() throws Exception {
    try (var h = accepted()) {
      var provider = new StubAnswerProvider(h.clock);
      assertThrows(
          NullPointerException.class,
          () -> new QuestionWorkerService(null, provider, () -> {}, () -> false, h.clock));
      assertThrows(
          NullPointerException.class,
          () -> new QuestionWorkerService(h.source, null, () -> {}, () -> false, h.clock));
      assertThrows(
          NullPointerException.class,
          () -> new QuestionWorkerService(h.source, provider, null, () -> false, h.clock));
      assertThrows(
          NullPointerException.class,
          () -> new QuestionWorkerService(h.source, provider, () -> {}, null, h.clock));
      assertThrows(
          NullPointerException.class,
          () -> new QuestionWorkerService(h.source, provider, () -> {}, () -> false, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new QuestionWorkerService(h.source, provider, () -> {}, () -> false, h.clock, null));
      assertThrows(
          TemporaryInfrastructureException.class,
          () -> worker(h, text -> null, () -> false).process(event(), delivery(1)));
      assertEquals(
          FIXTURE_PROCESSING_01F94682,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      byte[] literal = work(W, M0, RECEIPT, 1, 1, NOW);
      literal[306] = '!';
      var malformed =
          new WireMessage<>(
              HeaderCodec.standard().peek(literal),
              new FixedPayload(Arrays.copyOfRange(literal, 256, 320), 0, List.of()));
      assertThrows(
          PermanentProtocolException.class,
          () -> worker(h, provider, () -> false).process(malformed, delivery(2)));
    }
    for (Instant at : List.of(NOW.minusNanos(1000), Instant.MIN, Instant.MAX)) {
      try (var h = accepted()) {
        worker(h, text -> new AnswerResult("", at), () -> false).process(event(), delivery(1));
        assertEquals(
            FIXTURE_DATA_INTEGRITY_9097EAE7,
            h.text(FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      }
    }
    try (var h = accepted()) {
      worker(h, text -> new AnswerResult("e\u0301".repeat(2048), NOW), () -> false)
          .process(event(), delivery(1));
      assertEquals(4096, h.scalar("select octet_length(body) from schubert.answers"));
      assertEquals("é".repeat(2048), h.text("select body from schubert.answers"));
    }
    for (String fault :
        List.of(
            "insert into schubert.answers",
            "update schubert.async_jobs",
            "update schubert.notifications",
            "insert into schubert.app_logs")) {
      try (var h = accepted()) {
        var worker =
            worker(
                h,
                text -> {
                  h.prepareFault = fault;
                  return new AnswerResult("", NOW);
                },
                () -> false);
        assertThrows(
            TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(1)));
        assertEquals(
            FIXTURE_PROCESSING_01F94682,
            h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
        assertEquals(
            FIXTURE_PROCESSING_01F94682, h.text("select state from schubert.notifications"));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_APP_LOGS_WHER_E5BBEC80));
      }
    }
  }

  @Test
  void awork010ClockBoundsRollbackFailureAndExistingAnswerIntegrity() throws Exception {
    for (Instant value : List.of(Instant.MIN, Instant.MAX, NOW.minusNanos(1000))) {
      try (var h = accepted()) {
        var worker =
            new QuestionWorkerService(
                h.source,
                new StubAnswerProvider(h.clock),
                () -> {},
                () -> false,
                Clock.fixed(value, ZoneOffset.UTC));
        assertThrows(
            TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(1)));
        assertEquals(
            FIXTURE_RECEIVED_35302D54,
            h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      }
    }
    try (var h = accepted()) {
      AtomicInteger ticks = new AtomicInteger();
      Clock backwards =
          new Clock() {
            @Override
            public ZoneId getZone() {
              return ZoneOffset.UTC;
            }

            @Override
            public Clock withZone(ZoneId zone) {
              throw new UnsupportedOperationException();
            }

            @Override
            public Instant instant() {
              return ticks.getAndIncrement() == 0 ? NOW : NOW.minusNanos(1000);
            }
          };
      var worker =
          new QuestionWorkerService(
              h.source,
              text -> {
                throw new AnswerBusinessException();
              },
              () -> {},
              () -> false,
              backwards);
      assertThrows(
          TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(1)));
      assertEquals(
          FIXTURE_PROCESSING_01F94682,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_MQ_OUTBOX_73BAB5AA));
    }
    try (var h = accepted()) {
      h.fault = "rollback";
      h.prepareFault = "select j.id";
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              worker(h, text -> new AnswerResult("", NOW), () -> false)
                  .process(event(), delivery(1)));
      assertEquals(
          FIXTURE_RECEIVED_35302D54,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
    }
    for (String mismatch :
        List.of(
            "provider_type='EXTERNAL_AI'",
            "answered_at='2026-10-01T00:00:00.123457Z'",
            "is_deleted=true,deleted_at='2026-10-01T00:00:00.123456Z',deleted_by=2")) {
      try (var h = accepted()) {
        h.sql(
            "insert into schubert.answers(question_id,body,answered_at,provider_type,created_at,updated_at) values(1,'','2026-10-01T00:00:00.123456Z','STUB','2026-10-01T00:00:00.123456Z','2026-10-01T00:00:00.123456Z'); update schubert.answers set "
                + mismatch);
        worker(h, text -> new AnswerResult("", NOW), () -> false).process(event(), delivery(1));
        assertEquals(
            FIXTURE_DATA_INTEGRITY_9097EAE7,
            h.text(FIXTURE_SELECT_ERROR_CODE_FROM_SCHUBERT_NOTIFICA_8E9CC4F3));
        assertEquals(1, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      }
    }
  }

  @Test
  void awork011IndependentIdentityAndDriverShapeNegativesNeverComplete() throws Exception {
    for (String fault :
        List.of(
            "job-question",
            "job-receipt",
            "job-owner",
            "job-source",
            "job-source-work",
            "job-extra",
            "work-dlq",
            "work-extra",
            "notice-question",
            "notice-owner",
            "notice-extra",
            "deletion-at",
            "deletion-by",
            "deletion-extra")) {
      try (var h = accepted()) {
        if (fault.equals("deletion-by"))
          h.sql(
              "update schubert.questions set is_deleted=true,deleted_at='2026-10-01T00:00:00.123456Z',deleted_by=2");
        var worker =
            new QuestionWorkerService(
                tampered(h.source, fault),
                text -> new AnswerResult("", NOW),
                () -> {},
                () -> false,
                h.clock);
        var input = fault.equals("job-source-work") ? event(W, W) : event();
        assertThrows(
            PermanentProtocolException.class, () -> worker.process(input, delivery(1)), fault);
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
        assertNotEquals(
            FIXTURE_COMPLETED_BA0AE16A,
            h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_APP_LOGS_WHER_E5BBEC80));
      }
    }
    try (var h = accepted()) {
      byte[] literal = work(W, M0, RECEIPT, 1, 1, NOW);
      var header = HeaderCodec.standard().peek(literal);
      var wrong =
          new dev.codex.schubert.nk.protocol.header.CommonHeader(
              header.protocolIdentifier(),
              header.headerVersion(),
              header.layoutId(),
              header.layoutVersion(),
              header.messageKind(),
              header.interactionKind(),
              header.messageId(),
              header.correlationId(),
              header.sentAt(),
              header.authenticationContext(),
              256,
              65,
              0,
              0,
              321,
              header.resultCode());
      var event = new WireMessage<>(wrong, new FixedPayload(new byte[65], 0, List.of()));
      assertThrows(
          PermanentProtocolException.class,
          () ->
              worker(h, text -> new AnswerResult("", NOW), () -> false)
                  .process(event, delivery(1)));
      assertEquals(
          FIXTURE_RECEIVED_35302D54,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
    }
  }

  @Test
  void awork012FinalErrorAndSentProfilesRejectEachIndependentContradiction() throws Exception {
    for (String fault :
        List.of(
            "error-dispatch",
            "error-count",
            "error-extra",
            "error-null-statement",
            "error-null-result",
            "sent-status",
            "sent-sending",
            "sent-before",
            "sent-owner",
            "sent-until",
            "sent-extra")) {
      try (var h = accepted()) {
        finalError(h);
        h.sql(
            "update schubert.mq_outbox set status='SENT',sent_at='2026-10-01T00:00:00.123456Z' where destination='nk.dead.letter'"); // proof-negative fixture, not MQ-positive.
        h.signal = () -> {};
        AtomicInteger providers = new AtomicInteger();
        var worker =
            new QuestionWorkerService(
                tampered(h.source, fault),
                text -> {
                  providers.incrementAndGet();
                  return new AnswerResult("", NOW);
                },
                () -> {},
                () -> false,
                h.clock);
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> worker.process(event(), delivery(5)),
            fault);
        assertEquals(0, providers.get());
        assertEquals(
            1,
            h.scalar("select count(*) from schubert.mq_outbox where destination='nk.dead.letter'"));
        assertEquals(
            FIXTURE_ERROR_F717E7D8, h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
        assertEquals(0, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_ANSWERS_03E9AB4B));
      }
    }
    for (String state : List.of(FIXTURE_PENDING_B11DB31F, "LEASED", FIXTURE_ERROR_F717E7D8)) {
      try (var h = accepted()) {
        finalError(h);
        if (state.equals("LEASED"))
          h.sql(
              "update schubert.mq_outbox set lease_owner='independent',lease_until='2026-10-01T00:00:30Z' where destination='nk.dead.letter'");
        if (state.equals(FIXTURE_ERROR_F717E7D8))
          h.sql(
              "update schubert.mq_outbox set status='ERROR',last_error_code='JMS_SEND_FAILURE',last_error_detail='independent synthetic failure' where destination='nk.dead.letter'");
        AtomicInteger checks = new AtomicInteger();
        var worker =
            new QuestionWorkerService(
                h.source,
                text -> {
                  fail("ERROR provider");
                  return new AnswerResult("", NOW);
                },
                () -> {
                  assertEquals(0, h.live.get());
                },
                () -> checks.incrementAndGet() > 3,
                h.clock);
        assertThrows(
            TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(5)));
        assertEquals(
            state.equals("LEASED") ? FIXTURE_PENDING_B11DB31F : state,
            h.text(FIXTURE_SELECT_STATUS_FROM_SCHUBERT_MQ_OUTBOX_WH_71AC8AB8));
        assertEquals(0, h.live.get());
      }
    }
  }

  @Test
  void awork013ExtraAnswerAndUncertainRollbackDoNotCommitCompletion() throws Exception {
    for (String fault : List.of("answer-extra", "completed-extra", "update-zero")) {
      try (var h = accepted()) {
        if (fault.equals("answer-extra"))
          h.sql(
              "insert into schubert.answers(question_id,body,answered_at,provider_type,created_at,updated_at) values(1,'','2026-10-01T00:00:00.123456Z','STUB','2026-10-01T00:00:00.123456Z','2026-10-01T00:00:00.123456Z')");
        if (fault.equals("completed-extra"))
          worker(h, text -> new AnswerResult("", NOW), () -> false).process(event(), delivery(1));
        var worker =
            new QuestionWorkerService(
                tampered(h.source, fault),
                text -> new AnswerResult("", NOW),
                () -> {},
                () -> false,
                h.clock);
        long before = h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_APP_LOGS_WHER_E5BBEC80);
        assertThrows(PermanentProtocolException.class, () -> worker.process(event(), delivery(2)));
        assertEquals(before, h.scalar(FIXTURE_SELECT_COUNT_FROM_SCHUBERT_APP_LOGS_WHER_E5BBEC80));
        assertEquals(
            fault.equals("completed-extra")
                ? FIXTURE_COMPLETED_BA0AE16A
                : fault.equals("update-zero")
                    ? FIXTURE_RECEIVED_35302D54
                    : FIXTURE_PROCESSING_01F94682,
            h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
      }
    }
    try (var h = accepted()) {
      h.fault = "rollback";
      var worker =
          new QuestionWorkerService(
              tampered(h.source, "job-question"),
              text -> new AnswerResult("", NOW),
              () -> {},
              () -> false,
              h.clock);
      assertThrows(
          TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(1)));
      assertEquals(
          FIXTURE_RECEIVED_35302D54,
          h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
    }
  }

  static void finalError(Fixture h) throws SQLException {
    AtomicBoolean stop = new AtomicBoolean();
    h.signal = () -> stop.set(true);
    var worker =
        worker(
            h,
            text -> {
              throw new IllegalStateException(FIXTURE_PRIVATE_PROVIDER_9ABB4509);
            },
            stop::get);
    assertThrows(
        TemporaryInfrastructureException.class, () -> worker.process(event(), delivery(4)));
    assertEquals(
        FIXTURE_ERROR_F717E7D8, h.text(FIXTURE_SELECT_STATE_FROM_SCHUBERT_ASYNC_JOBS_E6C43F91));
    assertEquals(
        1,
        h.scalar(
            "select count(*) from schubert.app_logs where action='QUESTION_FAILED' and details->>'state'='ERROR' and details->>'errorCode'='SYSTEM_UNAVAIL' and details->>'receiptId'='"
                + RECEIPT
                + "' and details->>'jobId'='1' and details->>'questionId'='1'"));
  }

  // Real SQL result with one driver projection fault, never an expected generated by production.
  static DataSource tampered(DataSource actual, String fault) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (p, m, a) -> {
              Object result = invoke(actual, m, a);
              if (!m.getName().equals("getConnection")) return result;
              return Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (cp, cm, ca) -> {
                    Object statement = invoke(result, cm, ca);
                    if (!cm.getName().equals("prepareStatement")) return statement;
                    String sql = ca[0].toString();
                    String profile =
                        sql.contains("for update of j")
                            ? "job"
                            : sql.contains("and destination='nk.async.work'")
                                ? "work"
                                : sql.contains("where job_id=? for update")
                                    ? "notice"
                                    : sql.contains("from schubert.questions where id=? for update")
                                        ? "deletion"
                                        : sql.contains("status,sent_at")
                                            ? "sent"
                                            : sql.contains("where destination='nk.dead.letter'")
                                                ? "error"
                                                : sql.contains(
                                                        "select body,provider_type,answered_at")
                                                    ? "answer"
                                                    : sql.contains(
                                                            "select provider_type,answered_at")
                                                        ? "completed"
                                                        : sql.stripLeading()
                                                                .startsWith(
                                                                    "update schubert.async_jobs")
                                                            ? "update"
                                                            : "other";
                    if (!fault.startsWith(profile + "-")
                        && !(profile.equals("sent") && fault.equals("dlq-original")))
                      return statement;
                    if (fault.equals("error-null-statement")) {
                      ((PreparedStatement) statement).close();
                      return null;
                    }
                    AtomicInteger next = new AtomicInteger();
                    return Proxy.newProxyInstance(
                        PreparedStatement.class.getClassLoader(),
                        new Class<?>[] {PreparedStatement.class},
                        (sp, sm, sa) -> {
                          Object rows = invoke(statement, sm, sa);
                          if (fault.equals("update-zero") && sm.getName().equals("executeUpdate"))
                            return 0;
                          if (!sm.getName().equals("executeQuery")) return rows;
                          if (fault.equals("error-null-result")) {
                            ((ResultSet) rows).close();
                            return null;
                          }
                          return Proxy.newProxyInstance(
                              ResultSet.class.getClassLoader(),
                              new Class<?>[] {ResultSet.class},
                              (rp, rm, ra) -> {
                                if (fault.endsWith("-extra")
                                    && rm.getName().equals("next")
                                    && next.incrementAndGet() == 2) return true;
                                if (rm.getName().equals("getString")) {
                                  if (fault.equals("job-receipt") && ra[0].equals("receipt_id"))
                                    return "1".repeat(26);
                                  if (fault.equals("sent-status") && ra[0].equals("status"))
                                    return "UNKNOWN";
                                  if (fault.equals("sent-sending") && ra[0].equals("status"))
                                    return "SENDING";
                                }
                                if (rm.getName().equals("getObject")) {
                                  String column = ra[0].toString();
                                  if (fault.equals("job-question") && column.equals("question_id"))
                                    return 2L;
                                  if (fault.equals("job-owner") && column.equals("question_owner"))
                                    return 2L;
                                  if (fault.equals("job-source") && column.equals("message_id"))
                                    return new UUID(999, 999);
                                  if (fault.equals("job-source-work")
                                      && column.equals("message_id")) return W;
                                  if (fault.equals("work-dlq") && column.equals("dlq_detected_at"))
                                    return NOW.atOffset(ZoneOffset.UTC);
                                  if (fault.equals("notice-question")
                                      && column.equals("question_id")) return 2L;
                                  if (fault.equals("notice-owner")
                                      && column.equals("owner_user_id")) return 2L;
                                  if (fault.equals("deletion-at") && column.equals("deleted_at"))
                                    return NOW.atOffset(ZoneOffset.UTC);
                                  if (fault.equals("deletion-by") && column.equals("deleted_by"))
                                    return null;
                                  if (fault.equals("error-dispatch") && column.equals("message_id"))
                                    return W;
                                  if (fault.equals("error-count")
                                      && column.equals("dlq_delivery_count")) return 3;
                                  if (fault.equals("sent-before") && column.equals("sent_at"))
                                    return NOW.minusNanos(1000).atOffset(ZoneOffset.UTC);
                                  if (fault.equals("sent-owner") && column.equals("lease_owner"))
                                    return "unexpected-lease";
                                  if (fault.equals("sent-until") && column.equals("lease_until"))
                                    return NOW.plusSeconds(1).atOffset(ZoneOffset.UTC);
                                }
                                if (fault.equals("dlq-original")
                                    && rm.getName().equals("getObject")
                                    && ra[0].equals("dlq_original_message_id"))
                                  return new UUID(999, 999);
                                return invoke(rows, rm, ra);
                              });
                        });
                  });
            });
  }

  static Fixture accepted() throws Exception {
    var h = new Fixture(database);
    h.confirmOnSignal(); // SQL proof fixture only; AWORK001 uses actual MQ acceptance.
    assertArrayEquals(
        response(M0, new UUID(700, 3), "0000", RECEIPT, 1, NOW),
        h.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
    return h;
  }

  static QuestionWorkerService worker(
      Fixture h, AnswerProvider provider, java.util.function.BooleanSupplier stop) {
    return new QuestionWorkerService(
        h.source, provider, () -> h.signal.run(), stop, h.clock, () -> D);
  }

  static OwnedOutboxDispatcher owned(ActiveMQConnectionFactory factory, Clock clock) {
    return OwnedOutboxDispatcher.start(
        new OutboxDispatcher(
            database::api,
            () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
            new JdbcOutboxRepository(() -> 0),
            new OutboxJmsSender(),
            clock),
        "worker-pt");
  }

  static WireMessage<FixedPayload> event() {
    return event(W);
  }

  static WireMessage<FixedPayload> event(UUID id) {
    return event(id, M0);
  }

  static WireMessage<FixedPayload> event(UUID id, UUID correlation) {
    byte[] literal = work(id, correlation, RECEIPT, 1, 1, NOW);
    return new WireMessage<>(
        HeaderCodec.standard().peek(literal),
        new FixedPayload(Arrays.copyOfRange(literal, 256, 320), 0, List.of()));
  }

  static DeliveryMetadata delivery(int count) {
    return new DeliveryMetadata(count, "ID:independent-" + count, NOW);
  }
}
