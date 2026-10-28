package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.CONTEXT;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.Fixture;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.M0;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.NOW;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.RECEIPT;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.TOKEN;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.date;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.invoke;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.put;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.request;
import static dev.codex.schubert.nk.api.application.question.QuestionSubmissionServiceTest.response;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.InboxBoundaryFailureFixture;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.api.idempotency.ResultBoundResponseSnapshotCodec;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.ZoneOffset;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.postgresql.util.PSQLException;
import org.postgresql.util.PSQLState;
import org.postgresql.util.ServerErrorMessage;

/** PG-D380 / PT-QST-ASUB-008..012: public process, independent wire and SQL postconditions. */
class QuestionSubmissionBoundaryRemainderTest {
  private static final String FIXTURE_PUBLIC_FIXTURE_2BAE0C98 = "Public fixture";
  private static final String FIXTURE_9000_0CDC37EC = "9000";
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void asub008FutureHeaderAndCommittedDeadlineNeverRestartBudget() throws Exception {
    try (var f = new Boundary()) {
      f.h.confirmOnSignal();
      assertArrayEquals(
          response(M0, new UUID(700, 3), "0000", RECEIPT, 1, NOW),
          f.service.process(
              request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW.plusSeconds(10), CONTEXT)));
      assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
    }
    try (var f = new Boundary()) {
      var wake = new AtomicInteger();
      f.h.signal = wake::incrementAndGet;
      f.afterConnection =
          method -> {
            if (method.equals("commit")) f.h.nanos.set(2_000_000_000L);
          };
      assertArrayEquals(
          response(M0, new UUID(700, 3), FIXTURE_9000_0CDC37EC, "", 0, NOW),
          f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      assertEquals(0, wake.get());
      assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
      assertEquals("COMPLETED", f.h.text("select processing_state from schubert.request_inbox"));
      assertEquals("PENDING", f.h.text("select status from schubert.mq_outbox"));
    }
    try (var f = new Boundary()) {
      f.h.confirmOnSignal();
      var commits = new AtomicInteger();
      f.afterConnection =
          method -> {
            if (method.equals("commit") && commits.incrementAndGet() == 2)
              f.h.nanos.set(2_000_000_000L);
          };
      assertArrayEquals(
          response(M0, new UUID(700, 3), FIXTURE_9000_0CDC37EC, "", 0, NOW),
          f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      assertEquals("SENT", f.h.text("select status from schubert.mq_outbox"));
      assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
    }
  }

  @Test
  void asub009AuthenticationAndSentTimeoutSecondaryAreNotSuccess() throws Exception {
    try (var f = new Boundary()) {
      var observed = new AtomicInteger();
      f.afterConnection =
          method -> {
            if (method.equals("getAutoCommit")) {
              observed.incrementAndGet();
              f.h.nanos.set(2_000_000_000L);
            }
          };
      assertArrayEquals(
          response(M0, new UUID(700, 1), FIXTURE_9000_0CDC37EC, "", 0, NOW),
          f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
      assertTrue(observed.get() > 0);
    }
    for (boolean secondary : new boolean[] {false, true})
      try (var f = new Boundary()) {
        f.h.signal =
            () -> {
              f.expireOnOpen = true;
              if (secondary) f.h.fault = "rollback";
            };
        if (secondary)
          assertThrows(
              TemporaryInfrastructureException.class,
              () ->
                  f.service.process(
                      request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        else
          assertArrayEquals(
              response(M0, new UUID(700, 3), FIXTURE_9000_0CDC37EC, "", 0, NOW),
              f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
        assertEquals(0, f.h.live.get());
      }
    try (var f = new Boundary()) {
      f.h.signal = () -> Thread.currentThread().interrupt();
      try {
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                f.service.process(
                    request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        assertTrue(Thread.currentThread().isInterrupted());
      } finally {
        Thread.interrupted();
      }
      assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
    }
    try (var f = new Boundary()) {
      var calls = new AtomicInteger();
      f.h.signal = () -> f.ticks = () -> calls.incrementAndGet() < 3 ? 0 : 2_000_000_000L;
      assertArrayEquals(
          response(M0, new UUID(700, 3), FIXTURE_9000_0CDC37EC, "", 0, NOW),
          f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
      assertTrue(calls.get() >= 3);
    }
  }

  @Test
  void asub010IndependentDriverProofColumnsAndExtraRowFailClosed() throws Exception {
    var values = new LinkedHashMap<String, Object>();
    values.put("getObject:owner_user_id", 2L);
    values.put("getObject:operation_token", new UUID(900, 1));
    values.put("getObject:original", new UUID(900, 2));
    values.put("getObject:job_correlation", new UUID(900, 3));
    values.put("getObject:job_owner", 2L);
    values.put("getObject:work_id", M0);
    values.put("getObject:dlq_original_message_id", new UUID(900, 4));
    values.put("getString:lease_owner", "foreign");
    values.put("getObject:lease_until", NOW.atOffset(ZoneOffset.UTC));
    values.put("getString:status", "PENDING");
    values.put("getObject:sent_at", null);
    for (var entry : values.entrySet())
      try (var f = new Boundary()) {
        f.h.confirmOnSignal();
        f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT));
        String preserved =
            f.h.text(
                "select md5(response_body_encrypted)||':'||completed_at::text from schubert.request_inbox");
        f.hook =
            (sql, m, a, actual) ->
                sql.stripLeading().startsWith("select q.owner_user_id")
                        && a != null
                        && a.length > 0
                        && (m.getName() + ":" + a[0]).equals(entry.getKey())
                    ? entry.getValue()
                    : actual;
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                f.service.process(
                    request(
                        FIXTURE_PUBLIC_FIXTURE_2BAE0C98, new UUID(701, 2), TOKEN, NOW, CONTEXT)),
            entry.getKey());
        assertEquals(
            preserved,
            f.h.text(
                "select md5(response_body_encrypted)||':'||completed_at::text from schubert.request_inbox"));
        assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
        assertEquals(1, f.h.scalar("select count(*) from schubert.async_jobs"));
        assertEquals(1, f.h.scalar("select count(*) from schubert.mq_outbox"));
      }
    try (var f = new Boundary()) {
      f.h.confirmOnSignal();
      f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT));
      var calls = new AtomicInteger();
      f.hook =
          (sql, m, a, actual) ->
              sql.stripLeading().startsWith("select q.owner_user_id") && m.getName().equals("next")
                  ? calls.incrementAndGet() <= 2
                  : actual;
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              f.service.process(
                  request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, new UUID(701, 2), TOKEN, NOW, CONTEXT)));
      assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
      assertEquals(2, calls.get());
    }
  }

  @Test
  void asub011OtherConstraintSqlstateAndUpdateZeroRollbackWithoutRetry() throws Exception {
    for (SQLException failure :
        List.of(
            new SQLException("literal provider", "23505"),
            new PSQLException("literal provider", PSQLState.UNIQUE_VIOLATION),
            new PSQLException(
                new ServerErrorMessage("SERROR\u0000C23505\u0000nother_constraint\u0000\u0000")),
            new PSQLException("literal provider", PSQLState.SERIALIZATION_FAILURE)))
      try (var f = new Boundary()) {
        var inserts = new AtomicInteger();
        f.hook =
            (sql, m, a, actual) -> {
              if (sql.stripLeading().startsWith("insert into schubert.questions")
                  && m.getName().equals("executeQuery")) {
                inserts.incrementAndGet();
                throw failure;
              }
              return actual;
            };
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                f.service.process(
                    request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        assertEquals(1, inserts.get());
        assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
        assertEquals(0, f.h.scalar("select count(*) from schubert.request_inbox"));
      }
    try (var f = new Boundary()) {
      f.hook =
          (sql, m, a, actual) ->
              sql.stripLeading().startsWith("insert into schubert.app_logs")
                      && m.getName().equals("executeUpdate")
                  ? 0
                  : actual;
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
      assertEquals(0, f.h.scalar("select count(*) from schubert.request_inbox"));
      assertEquals(0, f.h.scalar("select count(*) from schubert.app_logs"));
    }
    try (var f = new Boundary()) {
      f.h.ids.set(0);
      f.identifier = () -> M0;
      assertThrows(
          TemporaryInfrastructureException.class,
          () ->
              f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
      assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
      assertEquals(0, f.h.scalar("select count(*) from schubert.async_jobs"));
    }
  }

  @Test
  void asub012InboxClassificationSavedHeaderAndReturningShapeRejectCorruption() throws Exception {
    for (String reason : List.of("OPERATION_TOKEN_REUSE", "MESSAGE_ID_REUSE", "STATE_CORRUPT"))
      for (boolean secondary : new boolean[] {false, true})
        try (var f = new Boundary()) {
          SQLException failure = InboxBoundaryFailureFixture.create(reason, secondary);
          f.hook =
              (sql, m, a, actual) -> {
                if (sql.contains("schubert.request_inbox") && m.getName().equals("executeQuery"))
                  throw failure;
                return actual;
              };
          var input = request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT);
          if (secondary || reason.equals("STATE_CORRUPT"))
            assertThrows(TemporaryInfrastructureException.class, () -> f.service.process(input));
          else if (reason.equals("MESSAGE_ID_REUSE"))
            assertThrows(
                dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class,
                () -> f.service.process(input));
          else
            assertArrayEquals(
                response(M0, new UUID(700, 1), "0105", "", 0, NOW), f.service.process(input));
          assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
          assertEquals(0, f.h.scalar("select count(*) from schubert.request_inbox"));
        }
    for (boolean secondary : new boolean[] {false, true})
      try (var f = new Boundary()) {
        var failure =
            new dev.codex.schubert.nk.protocol.codec.PermanentProtocolException("literal");
        if (secondary) failure.addSuppressed(new SQLException("literal secondary"));
        f.hook =
            (sql, m, a, actual) -> {
              if (sql.contains("schubert.request_inbox") && m.getName().equals("executeQuery"))
                throw failure;
              return actual;
            };
        var input = request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT);
        if (secondary)
          assertThrows(TemporaryInfrastructureException.class, () -> f.service.process(input));
        else
          assertSame(
              failure,
              assertThrows(
                  dev.codex.schubert.nk.protocol.codec.PermanentProtocolException.class,
                  () -> f.service.process(input)));
        assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
      }
    for (boolean extra : new boolean[] {false, true})
      try (var f = new Boundary()) {
        var rows = new AtomicInteger();
        f.hook =
            (sql, m, a, actual) ->
                sql.stripLeading().startsWith("insert into schubert.questions")
                        && m.getName().equals("next")
                    ? (extra ? rows.incrementAndGet() <= 2 : false)
                    : actual;
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                f.service.process(
                    request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT)));
        assertEquals(0, f.h.scalar("select count(*) from schubert.questions"));
        assertEquals(0, f.h.scalar("select count(*) from schubert.request_inbox"));
      }
    for (String defect : List.of("result", "time", "question", "submitted"))
      try (var f = new Boundary()) {
        f.h.confirmOnSignal();
        f.service.process(request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT));
        byte[] wire =
            response(
                M0,
                new UUID(700, 2),
                defect.equals("result") ? "0200" : "0000",
                RECEIPT,
                defect.equals("question") ? 2 : 1,
                defect.equals("time") ? NOW.plusMillis(1) : NOW);
        if (defect.equals("submitted")) put(wire, 294, date(NOW.plusMillis(1)));
        var saved =
            new ResultBoundResponseSnapshotCodec(f.h.snapshots)
                .encrypt(
                    ResponseSnapshotIdentity.authenticated(M0, "QSBRSP01", "001", 1),
                    InboxResultReference.numeric(InboxResultReferenceType.QUESTION, 1),
                    TOKEN,
                    wire);
        try (var c = database.api();
            var s =
                c.prepareStatement("update schubert.request_inbox set response_body_encrypted=?")) {
          s.setBytes(1, saved.ciphertext());
          assertEquals(1, s.executeUpdate());
        }
        assertThrows(
            TemporaryInfrastructureException.class,
            () ->
                f.service.process(
                    request(
                        FIXTURE_PUBLIC_FIXTURE_2BAE0C98, new UUID(701, 2), TOKEN, NOW, CONTEXT)));
        assertEquals(1, f.h.scalar("select count(*) from schubert.questions"));
        assertEquals(1, f.h.scalar("select count(*) from schubert.async_jobs"));
      }
  }

  @Test
  void asub013FatalProviderIdentityAndSuppressedCloseKeepBorrowedInput() throws Exception {
    for (boolean secondary : new boolean[] {false, true})
      try (var f = new Boundary()) {
        var fatal = new LinkageError("literal fatal provider");
        var wake = new AtomicInteger();
        f.h.signal = wake::incrementAndGet;
        if (secondary) f.h.fault = "close";
        f.hook =
            (sql, m, a, actual) -> {
              if (sql.stripLeading().startsWith("insert into schubert.notifications")
                  && m.getName().equals("executeUpdate")) throw fatal;
              return actual;
            };
        var input = request(FIXTURE_PUBLIC_FIXTURE_2BAE0C98, M0, TOKEN, NOW, CONTEXT);
        byte[] borrowed = input.payload().copyData();
        assertSame(fatal, assertThrows(LinkageError.class, () -> f.service.process(input)));
        assertEquals(secondary ? 1 : 0, fatal.getSuppressed().length);
        if (secondary) assertInstanceOf(SQLException.class, fatal.getSuppressed()[0]);
        assertEquals(0, wake.get());
        assertArrayEquals(borrowed, input.payload().copyData());
        for (String table :
            List.of(
                "questions",
                "async_jobs",
                "notifications",
                "request_inbox",
                "mq_outbox",
                "app_logs"))
          assertEquals(0, f.h.scalar("select count(*) from schubert." + table), table);
        assertEquals(0, f.h.live.get());
      }
  }

  @FunctionalInterface
  interface SqlHook {
    Object apply(String sql, Method method, Object[] args, Object actual) throws Throwable;
  }

  @FunctionalInterface
  interface AfterConnection {
    void apply(String method) throws Throwable;
  }

  static final class Boundary implements AutoCloseable {
    final Fixture h = new Fixture(database);
    SqlHook hook = (sql, m, a, actual) -> actual;
    AfterConnection afterConnection = method -> {};
    boolean expireOnOpen;
    LongSupplier ticks = () -> h.nanos.get();
    java.util.function.Supplier<UUID> identifier = () -> new UUID(700, h.ids.incrementAndGet());
    final QuestionSubmissionService service;

    Boundary() throws Exception {
      DataSource source =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (p, m, a) -> {
                    Object connection = invoke(h.source, m, a);
                    if (expireOnOpen) h.nanos.set(2_000_000_000L);
                    return Proxy.newProxyInstance(
                        Connection.class.getClassLoader(),
                        new Class<?>[] {Connection.class},
                        (cp, cm, ca) -> {
                          Object actual = invoke(connection, cm, ca);
                          if (cm.getName().equals("prepareStatement"))
                            actual = statement((PreparedStatement) actual, (String) ca[0]);
                          afterConnection.apply(cm.getName());
                          return actual;
                        });
                  });
      service =
          new QuestionSubmissionService(
              source,
              new AuthenticationContextVerifier(new ContextHash()),
              new JdbcInboxCoordinator(h.fingerprints),
              new ResultBoundResponseSnapshotCodec(h.snapshots),
              () -> h.signal.run(),
              h.clock,
              h.receipts,
              () -> identifier.get(),
              () -> ticks.getAsLong());
    }

    Object statement(PreparedStatement statement, String sql) {
      return Proxy.newProxyInstance(
          PreparedStatement.class.getClassLoader(),
          new Class<?>[] {PreparedStatement.class},
          (p, m, a) -> {
            Object actual = invoke(statement, m, a);
            if (actual instanceof ResultSet rows)
              actual =
                  Proxy.newProxyInstance(
                      ResultSet.class.getClassLoader(),
                      new Class<?>[] {ResultSet.class},
                      (rp, rm, ra) -> hook.apply(sql, rm, ra, invoke(rows, rm, ra)));
            return hook.apply(sql, m, a, actual);
          });
    }

    @Override
    public void close() {
      h.close();
    }
  }
}
