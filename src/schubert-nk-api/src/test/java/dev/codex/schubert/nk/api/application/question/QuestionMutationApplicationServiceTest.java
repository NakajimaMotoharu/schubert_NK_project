package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionMutationReplayServiceTest.AT;
import static dev.codex.schubert.nk.api.application.question.QuestionMutationReplayServiceTest.M;
import static dev.codex.schubert.nk.api.application.question.QuestionMutationReplayServiceTest.NEXT;
import static dev.codex.schubert.nk.api.application.question.QuestionMutationReplayServiceTest.TOKEN;
import static dev.codex.schubert.nk.api.application.question.QuestionMutationReplayServiceTest.message;
import static dev.codex.schubert.nk.api.application.question.QuestionMutationReplayServiceTest.wire;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Current DB/Inbox/ref/crypto, independent wire and seven-day no-rewrite postconditions. */
final class QuestionMutationApplicationServiceTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  static QuestionMutationApplicationService service(QuestionSubmissionServiceTest.Fixture f)
      throws Exception {
    return new QuestionMutationApplicationService(
        f.source,
        new AuthenticationContextVerifier(new ContextHash()),
        new JdbcInboxCoordinator(f.fingerprints),
        new QuestionCommandService(),
        f.snapshots,
        Clock.fixed(AT, ZoneOffset.UTC),
        () -> new UUID(712, f.ids.incrementAndGet()));
  }

  static byte[] expected(
      boolean cancel, UUID source, int response, ResultCode code, Instant operation) {
    return wire(cancel, source, new UUID(712, response), AT, code, operation);
  }

  static String metadata(QuestionSubmissionServiceTest.Fixture f) throws SQLException {
    return f.text(
        "select md5(string_agg(row(i.*)::text,',' order by message_id)) from schubert.request_inbox"
            + " i");
  }

  @Test
  void qry039BothActualMutationsSameAndNewMessageReplayKeepWholeInboxAndOriginalTime()
      throws Exception {
    for (boolean cancel : List.of(false, true))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var app = service(f);
        long id = cancel ? 6 : 3;
        var input = message(cancel, id, M, TOKEN);
        assertArrayEquals(expected(cancel, M, 2, ResultCode.SUCCESS, AT), app.process(input));
        assertEquals(0, f.live.get());
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.request_inbox where processing_state='COMPLETED' and"
                    + " expires_at=completed_at+interval '7 days' and"
                    + " completed_at='2026-10-01T00:00:01.123456Z' and result_ref_type='"
                    + (cancel ? "JOB" : "QUESTION")
                    + "' and result_ref_id="
                    + id));
        String saved = metadata(f);
        assertArrayEquals(
            expected(cancel, M, 3, ResultCode.IDEMPOTENT_SUCCESS, AT), app.process(input));
        assertArrayEquals(
            expected(cancel, NEXT, 4, ResultCode.IDEMPOTENT_SUCCESS, AT),
            app.process(message(cancel, id, NEXT, TOKEN)));
        assertEquals(saved, metadata(f));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='"
                    + (cancel ? "QUESTION_CANCELLED" : "QUESTION_DELETE_MARKED")
                    + "'"));
        assertEquals(
            2,
            f.scalar(
                "select count(*) from schubert.app_logs where action='INBOX_REPLAYED' and"
                    + " category='MQ'"));
        assertEquals(
            0,
            f.scalar(
                "select count(*) from schubert.app_logs where details::text like '%question3%' or"
                    + " details::text like '%"
                    + TOKEN
                    + "%'"));
        if (cancel) {
          f.sql("delete from schubert.notifications where id=6");
          assertArrayEquals(
              expected(true, NEXT, 5, ResultCode.IDEMPOTENT_SUCCESS, AT),
              app.process(message(true, id, NEXT, TOKEN)));
          assertEquals(saved, metadata(f));
        }
      }
  }

  @Test
  void qry040DefiniteErrorsOriginalNoopTimeCapacityAuditAndCurrentOwnerScope() throws Exception {
    for (boolean cancel : List.of(false, true))
      for (String kind : List.of("missing", "other", "noop", "capacity")) {
        try (var f = QuestionQueryRepositoryTest.fixture(db)) {
          long id =
              switch (kind) {
                case "missing" -> 999;
                case "other" -> 52;
                case "noop" -> cancel ? 1 : 5;
                default -> 8;
              };
          if (kind.equals("capacity"))
            f.sql(
                "update schubert."
                    + (cancel ? "async_jobs" : "questions")
                    + " set version=999999999 where id=8");
          var code =
              switch (kind) {
                case "missing", "other" -> ResultCode.NOT_FOUND;
                case "noop" -> ResultCode.IDEMPOTENT_SUCCESS;
                default -> ResultCode.RESOURCE_LIMIT;
              };
          Instant operation =
              kind.equals("noop")
                  ? Instant.parse(
                      cancel ? "2026-10-01T00:00:00.124456Z" : "2026-10-01T00:00:00.130456Z")
                  : AT;
          var app = service(f);
          assertArrayEquals(
              expected(cancel, M, 2, code, operation), app.process(message(cancel, id, M, TOKEN)));
          String saved = metadata(f);
          assertArrayEquals(
              expected(cancel, NEXT, 3, code, operation),
              app.process(message(cancel, id, NEXT, TOKEN)));
          assertEquals(saved, metadata(f));
          if (!(code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS))
            assertEquals(
                1,
                f.scalar(
                    "select count(*) from schubert.request_inbox where processing_state='ERROR' and"
                        + " result_ref_type='NONE'"));
          if (kind.equals("capacity")) {
            assertEquals(
                1,
                f.scalar(
                    "select count(*) from schubert.app_logs where action='RESOURCE_LIMIT_REACHED'"
                        + " and category='SYSTEM' and level='ERROR' and"
                        + " details->>'resource'='N9_VERSION' and details->>'errorCode'='9001'"));
            assertEquals(
                0,
                f.scalar(
                    "select count(*) from schubert.app_logs where action"
                        + " in('QUESTION_CANCELLED','QUESTION_DELETE_MARKED')"));
          }
        }
      }
    for (int id : List.of(2, 3, 4))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var app = service(f);
        byte[] gold = expected(true, M, 2, ResultCode.NOT_CANCELLABLE, AT);
        Arrays.fill(gold, 256, 268, (byte) 32);
        QuestionQueryRequestTest.put(
            gold, 256, List.of("PROCESSING", "COMPLETED", "ERROR").get(id - 2));
        assertArrayEquals(gold, app.process(message(true, id, M, TOKEN)));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.request_inbox where processing_state='ERROR' and"
                    + " result_ref_type='NONE'"));
      }
  }

  @Test
  void qry041LatestRevokeDisableOwnerRoleDowngradeCannotLeakSavedResult() throws Exception {
    for (boolean cancel : List.of(false, true))
      for (String change : List.of("revoke", "disable", "session-owner")) {
        try (var f = QuestionQueryRepositoryTest.fixture(db)) {
          var app = service(f);
          long id = cancel ? 6 : 3;
          assertArrayEquals(
              expected(cancel, M, 2, ResultCode.SUCCESS, AT),
              app.process(message(cancel, id, M, TOKEN)));
          String saved = metadata(f);
          f.sql(
              switch (change) {
                case "revoke" ->
                    "update schubert.auth_sessions set"
                        + " revoked=true,revoked_at='2026-10-01T00:00:01Z'";
                case "disable" -> "update schubert.app_users set status='DISABLED' where id=1";
                default -> "update schubert.auth_sessions set user_id=2";
              });
          if (change.equals("session-owner")) {
            assertThrows(
                PermanentProtocolException.class, () -> app.process(message(cancel, id, M, TOKEN)));
          } else
            assertArrayEquals(
                expected(cancel, M, 3, ResultCode.SESSION_INVALID, AT),
                app.process(message(cancel, id, M, TOKEN)));
          assertEquals(saved, metadata(f));
          assertEquals(0, f.live.get());
        }
      }
    for (String code : List.of("success", "capacity"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        f.sql("update schubert.app_users set role='ADMIN' where id=1");
        if (code.equals("capacity"))
          f.sql("update schubert.questions set version=999999999 where id=52");
        var app = service(f);
        assertArrayEquals(
            expected(
                false,
                M,
                2,
                code.equals("success") ? ResultCode.SUCCESS : ResultCode.RESOURCE_LIMIT,
                AT),
            app.process(message(false, 52, M, TOKEN)));
        String saved = metadata(f);
        f.sql("update schubert.app_users set role='USER' where id=1");
        assertArrayEquals(
            expected(false, NEXT, 3, ResultCode.NOT_FOUND, AT),
            app.process(message(false, 52, NEXT, TOKEN)));
        assertEquals(saved, metadata(f));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='OWNER_SCOPE_DENIED' and"
                    + " category='SECURITY'"));
      }
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      f.sql("update schubert.app_users set role='ADMIN' where id=1");
      assertArrayEquals(
          expected(true, M, 2, ResultCode.NOT_FOUND, AT),
          service(f).process(message(true, 52, M, TOKEN)));
    }
  }

  @Test
  void qry042TokenAndMessageIdentityConflictsKeepOriginalAndMandatoryAudit() throws Exception {
    for (boolean cancel : List.of(false, true))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var app = service(f);
        long id = cancel ? 6 : 3;
        app.process(message(cancel, id, M, TOKEN));
        String saved = metadata(f);
        assertArrayEquals(
            expected(cancel, NEXT, 3, ResultCode.CONFLICT, AT),
            app.process(message(cancel, 7, NEXT, TOKEN)));
        assertEquals(saved, metadata(f));
        assertThrows(
            PermanentProtocolException.class, () -> app.process(message(cancel, 7, M, TOKEN)));
        assertEquals(saved, metadata(f));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED' and"
                    + " category='MQ'"));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='AUTHORIZATION_DENIED' and"
                    + " category='SECURITY' and details->>'reason'='TOKEN_MISMATCH'"));
      }
  }

  @Test
  void qry043EveryOwnedConnectionFaultAndCriticalAuditFailureCannotReturnSuccess()
      throws Exception {
    for (boolean cancel : List.of(false, true))
      for (String fault :
          List.of(
              "open",
              "null",
              "setAutoCommit",
              "setReadOnly",
              "commit",
              "close",
              "rollback",
              "insert into schubert.app_logs",
              "update schubert.request_inbox"))
        try (var f = QuestionQueryRepositoryTest.fixture(db)) {
          f.fault = fault;
          if (fault.equals("rollback")) f.prepareFault = "insert into schubert.app_logs";
          var error =
              assertThrows(
                  TemporaryInfrastructureException.class,
                  () -> service(f).process(message(cancel, cancel ? 6 : 3, M, TOKEN)),
                  fault);
          assertNull(error.getCause());
          assertEquals(0, error.getSuppressed().length);
          assertEquals(0, f.live.get());
          assertEquals(
              fault.equals("close") ? 1 : 0,
              f.scalar("select count(*) from schubert.request_inbox"));
          assertEquals(
              fault.equals("close") ? 1 : 0,
              f.scalar(
                  "select count(*) from schubert.app_logs where action='"
                      + (cancel ? "QUESTION_CANCELLED" : "QUESTION_DELETE_MARKED")
                      + "'"));
        }
    for (String change : List.of("cipher", "state", "missing-key", "processing"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var app = service(f);
        app.process(message(false, 3, M, TOKEN));
        switch (change) {
          case "cipher" ->
              f.sql(
                  "update schubert.request_inbox set"
                      + " response_body_encrypted=decode(repeat('00',29),'hex')");
          case "state" ->
              f.sql(
                  "update schubert.questions set deleted_at='2026-10-01T00:00:01.999999Z' where"
                      + " id=3");
          case "missing-key" -> f.snapshots.close();
          case "processing" ->
              f.sql(
                  "update schubert.request_inbox set"
                      + " processing_state='PROCESSING',result_ref_type=null,result_ref_id=null,result_ref_uuid=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null");
        }
        String before = metadata(f);
        assertThrows(
            TemporaryInfrastructureException.class,
            () -> app.process(message(false, 3, M, TOKEN)),
            change);
        assertEquals(before, metadata(f));
        assertEquals(0, f.live.get());
      }
  }

  @Test
  void qry044ActualConcurrentSameOperationOnlyOneCommandAndOneInbox() throws Exception {
    for (boolean cancel : List.of(false, true))
      try (var f = QuestionQueryRepositoryTest.fixture(db);
          var pool = Executors.newFixedThreadPool(2)) {
        var start = new CountDownLatch(1);
        long id = cancel ? 6 : 3;
        var a =
            pool.submit(
                () -> {
                  start.await();
                  return service(f).process(message(cancel, id, M, TOKEN));
                });
        var b =
            pool.submit(
                () -> {
                  start.await();
                  return service(f).process(message(cancel, id, NEXT, TOKEN));
                });
        start.countDown();
        var one =
            HeaderCodec.standard().peek(a.get(10, TimeUnit.SECONDS)).resultCode().orElseThrow();
        var two =
            HeaderCodec.standard().peek(b.get(10, TimeUnit.SECONDS)).resultCode().orElseThrow();
        assertEquals(Set.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS), Set.of(one, two));
        assertEquals(1, f.scalar("select count(*) from schubert.request_inbox"));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='"
                    + (cancel ? "QUESTION_CANCELLED" : "QUESTION_DELETE_MARKED")
                    + "'"));
        assertEquals(0, f.live.get());
      }
  }

  @Test
  void qry045PublicConstructorNullContractsAndOwnedPostCommitReplyFailure() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      var auth = new AuthenticationContextVerifier(new ContextHash());
      var inbox = new JdbcInboxCoordinator(f.fingerprints);
      var commands = new QuestionCommandService();
      var clock = Clock.fixed(AT, ZoneOffset.UTC);
      var defaultApp =
          new QuestionMutationApplicationService(
              f.source, auth, inbox, commands, f.snapshots, clock);
      byte[] actual = defaultApp.process(message(false, 5, M, TOKEN));
      var header = HeaderCodec.standard().peek(actual);
      assertEquals(new LayoutId("QDLRSP01"), header.layoutId());
      assertEquals(M, header.correlationId());
      assertEquals(ResultCode.IDEMPOTENT_SUCCESS, header.resultCode().orElseThrow());
      assertNotEquals(new UUID(0, 0), header.messageId());
      assertNotEquals(M, header.messageId());
      assertArrayEquals(
          Arrays.copyOfRange(
              expected(
                  false,
                  M,
                  2,
                  ResultCode.IDEMPOTENT_SUCCESS,
                  Instant.parse("2026-10-01T00:00:00.130456Z")),
              256,
              280),
          Arrays.copyOfRange(actual, 256, 280));
      assertThrows(NullPointerException.class, () -> defaultApp.process(null));
      Object[] original = {f.source, auth, inbox, commands, f.snapshots, clock};
      for (int i = 0; i < original.length; i++) {
        var args = original.clone();
        args[i] = null;
        assertThrows(
            NullPointerException.class,
            () ->
                new QuestionMutationApplicationService(
                    (DataSource) args[0],
                    (AuthenticationContextVerifier) args[1],
                    (JdbcInboxCoordinator) args[2],
                    (QuestionCommandService) args[3],
                    (ResponseSnapshotCodec) args[4],
                    (Clock) args[5]));
      }
      assertThrows(
          NullPointerException.class,
          () ->
              new QuestionMutationApplicationService(
                  f.source, auth, inbox, commands, f.snapshots, clock, null));
      var calls = new AtomicInteger();
      var bad =
          new QuestionMutationApplicationService(
              f.source,
              auth,
              inbox,
              commands,
              f.snapshots,
              clock,
              () -> calls.incrementAndGet() == 1 ? new UUID(713, 1) : null);
      assertThrows(
          TemporaryInfrastructureException.class,
          () -> bad.process(message(false, 6, NEXT, new UUID(711, 8))));
      assertEquals(2, calls.get());
      assertEquals(2, f.scalar("select count(*) from schubert.request_inbox"));
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void qry047EveryCurrentResultScopeMissingOrExtraAndCriticalAuditZeroIsFailClosed()
      throws Exception {
    for (String mode :
        List.of(
            "job-missing",
            "notice-missing",
            "job-extra",
            "notice-extra",
            "question-extra",
            "audit-zero")) {
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        boolean cancel = !mode.equals("question-extra") && !mode.equals("audit-zero");
        boolean capacity = mode.startsWith("notice");
        long id = capacity ? 8 : cancel ? 6 : 3;
        if (capacity) f.sql("update schubert.async_jobs set version=999999999 where id=8");
        var app = service(f);
        app.process(message(cancel, id, M, TOKEN));
        String saved = metadata(f);
        String marker =
            switch (mode) {
              case "job-missing", "job-extra" -> "select id from schubert.async_jobs";
              case "notice-missing", "notice-extra" -> "select id from schubert.notifications";
              case "question-extra" -> "select id from schubert.questions";
              default -> "insert into schubert.app_logs";
            };
        String fault =
            mode.endsWith("missing")
                ? "missing"
                : mode.equals("audit-zero") ? "zero-update" : "duplicate";
        var hit = new AtomicInteger();
        DataSource source =
            (DataSource)
                Proxy.newProxyInstance(
                    DataSource.class.getClassLoader(),
                    new Class<?>[] {DataSource.class},
                    (p, m, a) ->
                        QuestionCommandServiceTest.shape(
                            (Connection) QuestionSubmissionServiceTest.invoke(f.source, m, a),
                            marker,
                            "",
                            fault,
                            hit));
        var guarded =
            new QuestionMutationApplicationService(
                source,
                new AuthenticationContextVerifier(new ContextHash()),
                new JdbcInboxCoordinator(f.fingerprints),
                new QuestionCommandService(),
                f.snapshots,
                Clock.fixed(AT, ZoneOffset.UTC),
                () -> new UUID(712, f.ids.incrementAndGet()));
        if (mode.endsWith("missing"))
          assertArrayEquals(
              expected(cancel, NEXT, 3, ResultCode.NOT_FOUND, AT),
              guarded.process(message(cancel, id, NEXT, TOKEN)));
        else
          assertThrows(
              TemporaryInfrastructureException.class,
              () -> guarded.process(message(cancel, id, NEXT, TOKEN)),
              mode);
        assertTrue(hit.get() > 0, mode);
        assertEquals(saved, metadata(f));
        assertEquals(0, f.live.get());
      }
    }
  }

  @Test
  void qry048UnavailableHmacAndStateCorruptCloseSuppressionAreInfrastructureNotConflict()
      throws Exception {
    for (String mode : List.of("key", "state", "state-close", "complete-close"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var app = service(f);
        app.process(message(false, 3, M, TOKEN));
        if (mode.equals("key"))
          f.sql("update schubert.request_inbox set fingerprint_key_version='missing'");
        String saved = metadata(f);
        var hit = new AtomicInteger();
        DataSource source =
            mode.equals("key")
                ? f.source
                : (DataSource)
                    Proxy.newProxyInstance(
                        DataSource.class.getClassLoader(),
                        new Class<?>[] {DataSource.class},
                        (p, m, a) ->
                            QuestionCommandServiceTest.shape(
                                (Connection) QuestionSubmissionServiceTest.invoke(f.source, m, a),
                                mode.equals("complete-close")
                                    ? "update schubert.request_inbox set processing_state="
                                    : "from schubert.request_inbox where message_id=?",
                                "processing_state",
                                mode.equals("complete-close")
                                    ? "zero-update-close"
                                    : mode.equals("state") ? "unknown" : "unknown-close",
                                hit));
        var guarded =
            new QuestionMutationApplicationService(
                source,
                new AuthenticationContextVerifier(new ContextHash()),
                new JdbcInboxCoordinator(f.fingerprints),
                new QuestionCommandService(),
                f.snapshots,
                Clock.fixed(AT, ZoneOffset.UTC),
                () -> new UUID(712, f.ids.incrementAndGet()));
        var error =
            assertThrows(
                TemporaryInfrastructureException.class,
                () ->
                    guarded.process(
                        mode.equals("complete-close")
                            ? message(false, 6, NEXT, new UUID(711, 9))
                            : message(false, 3, M, TOKEN)),
                mode);
        assertNull(error.getCause());
        assertEquals(0, error.getSuppressed().length);
        if (!mode.equals("key")) assertTrue(hit.get() > 0, mode);
        assertEquals(saved, metadata(f));
        assertEquals(0, f.live.get());
      }
  }
}
