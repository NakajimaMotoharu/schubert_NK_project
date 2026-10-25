package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.messaging.inbound.DeliveryMetadata;
import dev.codex.schubert.nk.api.messaging.outbound.JdbcOutboxRepository;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxDispatcher;
import dev.codex.schubert.nk.api.messaging.outbound.OutboxJmsSender;
import dev.codex.schubert.nk.api.messaging.outbound.OwnedOutboxDispatcher;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationState;
import jakarta.jms.JMSContext;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Literal DB expected states/triples; borrowed transaction and real row-lock competition. */
final class QuestionCommandServiceTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static final AuthenticatedActor USER = new AuthenticatedActor(1, "u1", Role.USER);
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "u1", Role.ADMIN);
  static final AuthenticatedActor OTHER = new AuthenticatedActor(2, "u2", Role.USER);
  static final Instant AT = Instant.parse("2026-10-01T00:00:01.123456789Z");
  static final QuestionCommandMetadata META =
      new QuestionCommandMetadata(new UUID(710, 1), new UUID(710, 2), AT);
  final QuestionCommandService service = new QuestionCommandService();

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  static Connection write() throws SQLException {
    var c = db.api();
    c.setAutoCommit(false);
    return c;
  }

  @Test
  void ntf012CancelCurrentSelfOnlyAllStatesAndOriginalTimeNoOwnershipEscape() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db);
        var c = write()) {
      assertEquals(53, f.scalar("select count(*) from schubert.notifications"));
      for (var actor : List.of(USER, ADMIN)) {
        var absent = service.cancel(c, actor, 52, META);
        assertEquals(ResultCode.NOT_FOUND, absent.code());
        assertTrue(absent.jobId().isEmpty());
        assertTrue(absent.state().isEmpty());
        assertTrue(absent.cancelledAt().isEmpty());
      }
      assertEquals(ResultCode.NOT_FOUND, service.cancel(c, USER, 999, META).code());
      var old = service.cancel(c, USER, 1, META);
      assertEquals(ResultCode.IDEMPOTENT_SUCCESS, old.code());
      assertEquals(Instant.parse("2026-10-01T00:00:00.124456Z"), old.cancelledAt().orElseThrow());
      for (int i = 2; i <= 4; i++) {
        var denied = service.cancel(c, USER, i, META);
        assertEquals(ResultCode.NOT_CANCELLABLE, denied.code());
        assertEquals(
            List.of(
                    NotificationState.PROCESSING,
                    NotificationState.COMPLETED,
                    NotificationState.ERROR)
                .get(i - 2),
            denied.state().orElseThrow());
        assertTrue(denied.cancelledAt().isEmpty());
        assertEquals(i, denied.jobId().orElseThrow());
      }
      var actual = service.cancel(c, USER, 6, META);
      assertEquals(ResultCode.SUCCESS, actual.code());
      assertEquals(6, actual.jobId().orElseThrow());
      assertEquals(NotificationState.CANCELLED, actual.state().orElseThrow());
      assertEquals(
          Instant.parse("2026-10-01T00:00:01.123456Z"), actual.cancelledAt().orElseThrow());
      assertEquals(ResultCode.IDEMPOTENT_SUCCESS, service.cancel(c, USER, 6, META).code());
      assertFalse(c.isClosed());
      assertEquals("RECEIVED", f.text("select state from schubert.async_jobs where id=6"));
      c.commit();
      assertEquals(
          "CANCELLED:1:2026-10-01 00:00:01.123456",
          f.text(
              "select state||':'||version||':'||to_char(cancelled_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US') from schubert.async_jobs where id=6"));
      assertEquals(
          "CANCELLED:2026-10-01 00:00:01.123456",
          f.text(
              "select state||':'||to_char(state_changed_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US') from schubert.notifications where id=6"));
      assertEquals(
          1,
          f.scalar(
              "select count(*) from schubert.app_logs where category='ACTION' and action='QUESTION_CANCELLED' and actor_user_id=1 and details->>'questionId'='6' and details->>'jobId'='6' and details->>'state'='CANCELLED'"));
      assertEquals(
          0,
          f.scalar(
              "select count(*) from schubert.app_logs where details::text like '%question6%'"));
      assertEquals(
          0, f.scalar("select count(*) from schubert.questions where id=6 and is_deleted"));
    }
  }

  @Test
  void qry028DeleteAnswerTripleScopeNoJobNoticeChangesAndIdempotentTime() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db);
        var c = write()) {
      assertEquals(53, f.scalar("select count(*) from schubert.async_jobs"));
      String jobs =
          f.text(
              "select md5(string_agg(row(j.*)::text,',' order by id)) from schubert.async_jobs j");
      String notices =
          f.text(
              "select md5(string_agg(row(n.*)::text,',' order by id)) from schubert.notifications n");
      assertEquals(ResultCode.NOT_FOUND, service.logicalDelete(c, USER, 52, META).code());
      assertEquals(ResultCode.NOT_FOUND, service.logicalDelete(c, OTHER, 3, META).code());
      assertEquals(ResultCode.NOT_FOUND, service.logicalDelete(c, ADMIN, 999, META).code());
      var old = service.logicalDelete(c, USER, 5, META);
      assertEquals(ResultCode.IDEMPOTENT_SUCCESS, old.code());
      assertEquals(Instant.parse("2026-10-01T00:00:00.130456Z"), old.deletedAt().orElseThrow());
      var first = service.logicalDelete(c, USER, 3, META);
      assertEquals(ResultCode.SUCCESS, first.code());
      assertEquals(Instant.parse("2026-10-01T00:00:01.123456Z"), first.deletedAt().orElseThrow());
      assertEquals(first.deletedAt(), service.logicalDelete(c, USER, 3, META).deletedAt());
      assertEquals(ResultCode.SUCCESS, service.logicalDelete(c, ADMIN, 52, META).code());
      assertEquals(ResultCode.SUCCESS, service.logicalDelete(c, OTHER, 53, META).code());
      c.commit();
      assertEquals(
          "true:1:1:2026-10-01 00:00:01.123456",
          f.text(
              "select is_deleted||':'||deleted_by||':'||version||':'||to_char(deleted_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US') from schubert.questions where id=3"));
      assertEquals(
          "true:1:2026-10-01 00:00:01.123456",
          f.text(
              "select is_deleted||':'||deleted_by||':'||to_char(deleted_at at time zone 'UTC','YYYY-MM-DD HH24:MI:SS.US') from schubert.answers where question_id=3"));
      assertEquals(
          3,
          f.scalar(
              "select count(*) from schubert.app_logs where action='QUESTION_DELETE_MARKED' and category='ACTION'"));
      assertEquals(
          jobs,
          f.text(
              "select md5(string_agg(row(j.*)::text,',' order by id)) from schubert.async_jobs j"));
      assertEquals(
          notices,
          f.text(
              "select md5(string_agg(row(n.*)::text,',' order by id)) from schubert.notifications n"));
    }
  }

  @Test
  void qry029VersionCapAndAnswerCorruptionNeverPartiallyRepair() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db);
        var c = write()) {
      f.sql("update schubert.questions set version=999999999 where id=7");
      f.sql("update schubert.async_jobs set version=999999999 where id=8");
      var cancelCap = service.cancel(c, USER, 8, META);
      assertEquals(ResultCode.RESOURCE_LIMIT, cancelCap.code());
      assertTrue(cancelCap.jobId().isEmpty());
      assertTrue(cancelCap.cancelledAt().isEmpty());
      var cap = service.logicalDelete(c, USER, 7, META);
      assertEquals(ResultCode.RESOURCE_LIMIT, cap.code());
      assertTrue(cap.deletedAt().isEmpty());
      f.sql(
          "update schubert.answers set is_deleted=true,deleted_at='2026-10-01T00:00:00.126456Z',deleted_by=1 where question_id=3");
      assertThrows(
          TemporaryInfrastructureException.class, () -> service.logicalDelete(c, USER, 3, META));
      c.rollback();
      assertEquals(
          0, f.scalar("select count(*) from schubert.questions where id in(3,7) and is_deleted"));
      assertEquals(0, f.scalar("select count(*) from schubert.app_logs"));
      f.sql(
          "update schubert.notifications set state_changed_at='2026-10-01T00:00:00.123457Z' where id=6");
      assertThrows(TemporaryInfrastructureException.class, () -> service.cancel(c, USER, 6, META));
      c.rollback();
      var before =
          new QuestionCommandMetadata(
              new UUID(710, 3), new UUID(710, 4), Instant.parse("2026-10-01T00:00:00Z"));
      assertThrows(
          TemporaryInfrastructureException.class, () -> service.cancel(c, USER, 7, before));
      c.rollback();
    }
  }

  @Test
  void ntf013BothActualLockCommitOrdersWorkerAndCancel() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db);
        var first = write();
        var second = write();
        var pool = Executors.newSingleThreadExecutor()) {
      assertEquals(53, f.scalar("select count(*) from schubert.async_jobs"));
      assertEquals(ResultCode.SUCCESS, service.cancel(first, USER, 6, META).code());
      var worker =
          pool.submit(
              () -> {
                try (var s =
                    second.prepareStatement(
                        "update schubert.async_jobs set state='PROCESSING',started_at='2026-10-01T00:00:02Z',state_changed_at='2026-10-01T00:00:02Z',processing_message_id=message_id,version=version+1 where id=6 and state='RECEIVED'")) {
                  return s.executeUpdate();
                }
              });
      assertThrows(TimeoutException.class, () -> worker.get(100, TimeUnit.MILLISECONDS));
      first.commit();
      assertEquals(0, worker.get(5, TimeUnit.SECONDS));
      second.rollback();
      try (var s = first.createStatement()) {
        assertEquals(
            1,
            s.executeUpdate(
                "update schubert.async_jobs set state='PROCESSING',started_at='2026-10-01T00:00:01Z',state_changed_at='2026-10-01T00:00:01Z',processing_message_id=message_id,version=version+1 where id=7 and state='RECEIVED'"));
        assertEquals(
            1,
            s.executeUpdate(
                "update schubert.notifications set state='PROCESSING',state_changed_at='2026-10-01T00:00:01Z',updated_at='2026-10-01T00:00:01Z' where id=7"));
      }
      var cancel = pool.submit(() -> service.cancel(second, USER, 7, META));
      assertThrows(TimeoutException.class, () -> cancel.get(100, TimeUnit.MILLISECONDS));
      first.commit();
      assertEquals(ResultCode.NOT_CANCELLABLE, cancel.get(5, TimeUnit.SECONDS).code());
      second.commit();
      assertEquals("PROCESSING", f.text("select state from schubert.async_jobs where id=7"));
    }
  }

  @Test
  void qry030EachJdbcFailureRequiresCallerRollbackPreservesDataAndPrivateDiagnostic()
      throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      assertEquals(53, f.scalar("select count(*) from schubert.questions"));
      for (boolean cancel : List.of(false, true)) {
        for (long target : List.of(cancel ? 6L : 3L, 999L)) {
          AtomicInteger total = new AtomicInteger();
          try (var c = write()) {
            Connection counted = fault(c, total, -1);
            if (cancel) service.cancel(counted, USER, target, META);
            else service.logicalDelete(counted, USER, target, META);
            c.rollback();
          }
          assertTrue(total.get() > (target == 999 ? 5 : 30));
          for (int point = 1; point <= total.get(); point++) {
            AtomicInteger reached = new AtomicInteger();
            try (var c = write()) {
              Connection broken = fault(c, reached, point);
              var error =
                  assertThrows(
                      TemporaryInfrastructureException.class,
                      () -> {
                        if (cancel) service.cancel(broken, USER, target, META);
                        else service.logicalDelete(broken, USER, target, META);
                      },
                      "fault point " + point);
              assertTrue(reached.get() >= point);
              assertNull(error.getCause());
              assertFalse(error.toString().contains("private-provider"));
              c.rollback();
              assertFalse(c.isClosed());
            }
            assertEquals(0, f.scalar("select count(*) from schubert.app_logs"));
            assertEquals("RECEIVED", f.text("select state from schubert.async_jobs where id=6"));
            assertEquals(
                0, f.scalar("select count(*) from schubert.questions where id=3 and is_deleted"));
            assertEquals(
                0,
                f.scalar(
                    "select count(*) from schubert.answers where question_id=3 and is_deleted"));
          }
        }
      }
    }
  }

  @Test
  void qry031NullTransactionAndMetadataBoundaries() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db);
        var c = write()) {
      assertEquals(53, f.scalar("select count(*) from schubert.questions"));
      for (boolean cancel : List.of(false, true)) {
        assertThrows(NullPointerException.class, () -> call(cancel, null, USER, 1, META));
        assertThrows(NullPointerException.class, () -> call(cancel, c, null, 1, META));
        assertThrows(NullPointerException.class, () -> call(cancel, c, USER, 1, null));
        for (long id : new long[] {0, -1, 1_000_000_000_000L})
          assertThrows(IllegalArgumentException.class, () -> call(cancel, c, USER, id, META));
        c.setReadOnly(true);
        assertThrows(TemporaryInfrastructureException.class, () -> call(cancel, c, USER, 1, META));
        c.setReadOnly(false);
        c.setAutoCommit(true);
        assertThrows(TemporaryInfrastructureException.class, () -> call(cancel, c, USER, 1, META));
        c.setAutoCommit(false);
      }
    }
    assertThrows(
        NullPointerException.class, () -> new QuestionCommandMetadata(null, new UUID(1, 2), AT));
    assertThrows(
        NullPointerException.class, () -> new QuestionCommandMetadata(new UUID(1, 2), null, AT));
    assertThrows(
        NullPointerException.class,
        () -> new QuestionCommandMetadata(new UUID(1, 2), new UUID(1, 3), null));
    for (Instant invalid : List.of(Instant.MIN, Instant.MAX))
      assertThrows(
          IllegalArgumentException.class,
          () -> new QuestionCommandMetadata(new UUID(1, 2), new UUID(1, 3), invalid));
    assertEquals("QuestionCommandMetadata[REDACTED]", META.toString());
    assertEquals(
        "CancelResult[REDACTED]",
        new QuestionCommandService.CancelResult(
                ResultCode.NOT_FOUND, OptionalLong.empty(), Optional.empty(), Optional.empty())
            .toString());
    assertEquals(
        "DeleteResult[REDACTED]",
        new QuestionCommandService.DeleteResult(ResultCode.NOT_FOUND, Optional.empty()).toString());
  }

  void call(
      boolean cancel, Connection c, AuthenticatedActor actor, long id, QuestionCommandMetadata m) {
    if (cancel) service.cancel(c, actor, id, m);
    else service.logicalDelete(c, actor, id, m);
  }

  @Test
  void qry034ClosedResultProfilesRejectImpossibleCombinations() {
    var jobs =
        List.of(
            OptionalLong.empty(),
            OptionalLong.of(-1),
            OptionalLong.of(0),
            OptionalLong.of(1),
            OptionalLong.of(999_999_999_999L),
            OptionalLong.of(1_000_000_000_000L));
    var states = new ArrayList<Optional<NotificationState>>();
    states.add(Optional.empty());
    for (var state : NotificationState.values()) states.add(Optional.of(state));
    var times = List.of(Optional.<Instant>empty(), Optional.of(AT));
    for (ResultCode code : ResultCode.values()) {
      for (var job : jobs)
        for (var state : states)
          for (var time : times) {
            // Contract profiles: success CANCELLED+time; 0107 terminal/in-flight+no time;
            // definite 0104/9001 no saved reference/state/time. Independent profile enumeration.
            boolean valid =
                switch (code) {
                  case SUCCESS, IDEMPOTENT_SUCCESS ->
                      Set.of(OptionalLong.of(1), OptionalLong.of(999_999_999_999L)).contains(job)
                          && state.equals(Optional.of(NotificationState.CANCELLED))
                          && time.isPresent();
                  case NOT_CANCELLABLE ->
                      Set.of(OptionalLong.of(1), OptionalLong.of(999_999_999_999L)).contains(job)
                          && time.isEmpty()
                          && Set.of(
                                  Optional.of(NotificationState.PROCESSING),
                                  Optional.of(NotificationState.COMPLETED),
                                  Optional.of(NotificationState.ERROR))
                              .contains(state);
                  case NOT_FOUND, RESOURCE_LIMIT ->
                      job.isEmpty() && state.isEmpty() && time.isEmpty();
                  default -> false;
                };
            if (valid)
              assertEquals(
                  code, new QuestionCommandService.CancelResult(code, job, state, time).code());
            else
              assertThrows(
                  IllegalArgumentException.class,
                  () -> new QuestionCommandService.CancelResult(code, job, state, time));
          }
      for (var time : times) {
        boolean valid =
            switch (code) {
              case SUCCESS, IDEMPOTENT_SUCCESS -> time.isPresent();
              case NOT_FOUND, RESOURCE_LIMIT -> time.isEmpty();
              default -> false;
            };
        if (valid) assertEquals(code, new QuestionCommandService.DeleteResult(code, time).code());
        else
          assertThrows(
              IllegalArgumentException.class,
              () -> new QuestionCommandService.DeleteResult(code, time));
      }
    }
    assertThrows(
        NullPointerException.class,
        () ->
            new QuestionCommandService.CancelResult(
                null, OptionalLong.empty(), Optional.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new QuestionCommandService.CancelResult(
                ResultCode.NOT_FOUND, null, Optional.empty(), Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new QuestionCommandService.CancelResult(
                ResultCode.NOT_FOUND, OptionalLong.empty(), null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () ->
            new QuestionCommandService.CancelResult(
                ResultCode.NOT_FOUND, OptionalLong.empty(), Optional.empty(), null));
    assertThrows(
        NullPointerException.class,
        () -> new QuestionCommandService.DeleteResult(null, Optional.empty()));
    assertThrows(
        NullPointerException.class,
        () -> new QuestionCommandService.DeleteResult(ResultCode.NOT_FOUND, null));
  }

  static Connection fault(Connection c, AtomicInteger calls, int point) {
    return (Connection) wrap(c, Connection.class, calls, point);
  }

  @Test
  void qry035MissingExtraNullUnknownAndCasZeroNeverCreateDefiniteSuccess() throws Exception {
    record Shape(boolean cancel, String sql, String column, String kind, long id) {}
    var shapes =
        List.of(
            new Shape(true, "select job_id from", "job_id", "zero", 6),
            new Shape(true, "select job_id from", "job_id", "overflow", 6),
            new Shape(true, "select job_id from", "job_id", "null", 6),
            new Shape(true, "select job_id from", "", "duplicate", 6),
            new Shape(true, "select question_id,state", "", "missing", 6),
            new Shape(true, "select question_id,state", "", "duplicate", 6),
            new Shape(true, "select question_id,state", "state", "unknown", 6),
            new Shape(true, "select question_id,state", "state", "null", 6),
            new Shape(true, "select question_id,state", "cancelled_at", "null", 1),
            new Shape(true, "select question_id,state", "cancelled_at", "time", 6),
            new Shape(true, "select job_id,question_id", "", "missing", 6),
            new Shape(true, "select job_id,question_id", "", "duplicate", 6),
            new Shape(true, "select job_id,question_id", "job_id", "wrong", 6),
            new Shape(true, "select job_id,question_id", "question_id", "wrong", 6),
            new Shape(true, "select job_id,question_id", "state", "unknown", 6),
            new Shape(true, "select job_id,question_id", "state_changed_at", "time", 6),
            new Shape(true, "update schubert.async_jobs", "", "zero-update", 6),
            new Shape(true, "update schubert.notifications", "", "zero-update", 6),
            new Shape(false, "select id,owner_user_id", "is_deleted", "true", 3),
            new Shape(false, "select id,owner_user_id", "deleted_at", "time", 3),
            new Shape(false, "select id,owner_user_id", "deleted_by", "wrong", 3),
            new Shape(false, "select id,owner_user_id", "", "duplicate", 3),
            new Shape(false, "select is_deleted", "is_deleted", "true", 3),
            new Shape(false, "select is_deleted", "deleted_at", "time", 3),
            new Shape(false, "select is_deleted", "deleted_by", "wrong", 3),
            new Shape(false, "select is_deleted", "", "duplicate", 3),
            new Shape(false, "update schubert.questions", "", "zero-update", 3),
            new Shape(false, "update schubert.answers", "", "zero-update", 3),
            new Shape(false, "select receipt_id", "", "missing", 3),
            new Shape(false, "select receipt_id", "", "duplicate", 3),
            new Shape(false, "select receipt_id", "receipt_id", "unknown", 3),
            new Shape(false, "insert into schubert.app_logs", "", "zero-update", 3));
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      assertEquals(53, f.scalar("select count(*) from schubert.questions"));
      for (var shape : shapes) {
        var hit = new AtomicInteger();
        try (var c = write()) {
          Connection altered = shape(c, shape.sql(), shape.column(), shape.kind(), hit);
          assertThrows(
              TemporaryInfrastructureException.class,
              () -> call(shape.cancel(), altered, USER, shape.id(), META),
              shape.toString());
          assertTrue(hit.get() > 0, shape.toString());
          c.rollback();
        }
        assertEquals(0, f.scalar("select count(*) from schubert.app_logs"));
        assertEquals(
            0, f.scalar("select count(*) from schubert.questions where id=3 and is_deleted"));
        assertEquals("RECEIVED", f.text("select state from schubert.async_jobs where id=6"));
      }
    }
  }

  @Test
  void qry032ActualWorkerInheritsDeleteCommittedWhileAnswerWaitsAndReverseOrder(
      @TempDir Path brokerRoot) throws Exception {
    var broker = QuestionSubmissionServiceTest.broker(brokerRoot);
    try (var factory = new ActiveMQConnectionFactory("vm://0")) {
      factory.setConsumerWindowSize(0);
      for (boolean deleteFirst : List.of(true, false)) {
        try (var f = new QuestionSubmissionServiceTest.Fixture(db);
            var owned =
                OwnedOutboxDispatcher.start(
                    new OutboxDispatcher(
                        db::api,
                        () -> factory.createContext(JMSContext.SESSION_TRANSACTED),
                        new JdbcOutboxRepository(() -> 0),
                        new OutboxJmsSender(),
                        f.clock),
                    "mutation-worker-pt");
            var pool = Executors.newSingleThreadExecutor();
            var deleting = write()) {
          f.signal = owned::wake;
          assertArrayEquals(
              QuestionSubmissionServiceTest.response(
                  QuestionSubmissionServiceTest.M0,
                  new UUID(700, 3),
                  "0000",
                  QuestionSubmissionServiceTest.RECEIPT,
                  1,
                  QuestionSubmissionServiceTest.NOW),
              f.service.process(
                  QuestionSubmissionServiceTest.request(
                      "Public fixture",
                      QuestionSubmissionServiceTest.M0,
                      QuestionSubmissionServiceTest.TOKEN,
                      QuestionSubmissionServiceTest.NOW,
                      QuestionSubmissionServiceTest.CONTEXT)));
          var literal =
              QuestionSubmissionServiceTest.work(
                  new UUID(700, 1),
                  QuestionSubmissionServiceTest.M0,
                  QuestionSubmissionServiceTest.RECEIPT,
                  1,
                  1,
                  QuestionSubmissionServiceTest.NOW);
          var event =
              new WireMessage<>(
                  HeaderCodec.standard().peek(literal),
                  new FixedPayload(Arrays.copyOfRange(literal, 256, 320), 0, List.of()));
          var providerEntered = new CountDownLatch(1);
          var worker =
              new QuestionWorkerService(
                  f.source,
                  text -> {
                    assertEquals("Public fixture", text);
                    assertEquals(0, f.live.get());
                    providerEntered.countDown();
                    return new AnswerResult("", Instant.parse("2026-10-01T00:00:02.123456Z"));
                  },
                  owned::wake,
                  () -> false,
                  f.clock);
          if (deleteFirst)
            assertEquals(ResultCode.SUCCESS, service.logicalDelete(deleting, USER, 1, META).code());
          var future =
              pool.submit(
                  () ->
                      worker.process(
                          event,
                          new DeliveryMetadata(
                              1, "ID:public-mutation-work", QuestionSubmissionServiceTest.NOW)));
          assertTrue(providerEntered.await(5, TimeUnit.SECONDS));
          if (deleteFirst) {
            assertThrows(TimeoutException.class, () -> future.get(100, TimeUnit.MILLISECONDS));
            deleting.commit();
          }
          future.get(5, TimeUnit.SECONDS);
          if (!deleteFirst) {
            assertEquals(ResultCode.SUCCESS, service.logicalDelete(deleting, USER, 1, META).code());
            deleting.commit();
          }
          assertEquals(
              1,
              f.scalar(
                  "select count(*) from schubert.answers a join schubert.questions q on q.id=a.question_id where a.is_deleted and q.is_deleted and a.deleted_by=1 and q.deleted_by=1 and a.deleted_at='2026-10-01T00:00:01.123456Z' and q.deleted_at=a.deleted_at and a.answered_at='2026-10-01T00:00:02.123456Z'"));
          assertEquals("COMPLETED", f.text("select state from schubert.async_jobs"));
          assertEquals("COMPLETED", f.text("select state from schubert.notifications"));
          assertEquals(
              1,
              f.scalar(
                  "select count(*) from schubert.app_logs where action='QUESTION_DELETE_MARKED' and details->>'receiptId'='"
                      + QuestionSubmissionServiceTest.RECEIPT
                      + "'"));
        }
      }
    } finally {
      broker.stop();
    }
  }

  static Connection shape(Connection c, String sql, String column, String kind, AtomicInteger hit) {
    return (Connection)
        Proxy.newProxyInstance(
            Connection.class.getClassLoader(),
            new Class<?>[] {Connection.class},
            (p, m, a) -> {
              Object result = QuestionSubmissionServiceTest.invoke(c, m, a);
              if (!m.getName().equals("prepareStatement") || !((String) a[0]).contains(sql))
                return result;
              return Proxy.newProxyInstance(
                  PreparedStatement.class.getClassLoader(),
                  new Class<?>[] {PreparedStatement.class},
                  (sp, sm, sa) -> {
                    if (sm.getName().equals("close") && kind.equals("zero-update-close")) {
                      QuestionSubmissionServiceTest.invoke(result, sm, sa);
                      hit.incrementAndGet();
                      throw new SQLException("private-close");
                    }
                    if (sm.getName().equals("executeUpdate")
                        && (kind.equals("zero-update") || kind.equals("zero-update-close"))) {
                      hit.incrementAndGet();
                      return 0;
                    }
                    Object rows = QuestionSubmissionServiceTest.invoke(result, sm, sa);
                    if (!sm.getName().equals("executeQuery")) return rows;
                    var next = new AtomicInteger();
                    return Proxy.newProxyInstance(
                        ResultSet.class.getClassLoader(),
                        new Class<?>[] {ResultSet.class},
                        (rp, rm, ra) -> {
                          Object value = QuestionSubmissionServiceTest.invoke(rows, rm, ra);
                          if (rm.getName().equals("close") && kind.equals("unknown-close")) {
                            hit.incrementAndGet();
                            throw new SQLException("private-close");
                          }
                          if (rm.getName().equals("next")) {
                            int n = next.incrementAndGet();
                            if (kind.equals("missing") && n == 1) {
                              hit.incrementAndGet();
                              return false;
                            }
                            if (kind.equals("duplicate") && n == 2) {
                              hit.incrementAndGet();
                              return true;
                            }
                          }
                          if ((rm.getName().equals("getObject") || rm.getName().equals("getString"))
                              && ra[0].equals(column)) {
                            hit.incrementAndGet();
                            return switch (kind) {
                              case "null" -> null;
                              case "zero" -> 0L;
                              case "overflow" -> 1_000_000_000_000L;
                              case "wrong" -> 99L;
                              case "unknown", "unknown-close" -> "UNKNOWN";
                              case "true" -> true;
                              case "time" ->
                                  java.time.OffsetDateTime.parse("2026-10-01T00:00:00.999999Z");
                              default -> throw new AssertionError("unrecognized fixture shape");
                            };
                          }
                          return value;
                        });
                  });
            });
  }

  static Object wrap(Object target, Class<?> type, AtomicInteger calls, int point) {
    return Proxy.newProxyInstance(
        type.getClassLoader(),
        new Class<?>[] {type},
        (p, m, a) -> {
          int call = calls.incrementAndGet();
          if (call == point) {
            if (m.getName().equals("close")) QuestionSubmissionServiceTest.invoke(target, m, a);
            throw new SQLException("private-provider");
          }
          Object value = QuestionSubmissionServiceTest.invoke(target, m, a);
          if (value instanceof PreparedStatement)
            return wrap(value, PreparedStatement.class, calls, point);
          if (value instanceof ResultSet) return wrap(value, ResultSet.class, calls, point);
          return value;
        });
  }
}
