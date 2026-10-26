package dev.codex.schubert.nk.api.application.question;

import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.MESSAGE;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.data;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.message;
import static dev.codex.schubert.nk.api.application.question.QuestionQueryRequestTest.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.persistence.QuestionQueryRepository;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-QRY018..024/NTF011; independent SQL, literal whole wire and read/write/race hooks. */
final class QuestionQueryApplicationServiceTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture db;
  static final Instant STAMP = QuestionSubmissionServiceTest.NOW;

  @BeforeAll
  static void start() throws Exception {
    db = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void qry018AllRoutesCommitFrozenResultsAndIndependentWireWithTwentyFourHourRetention()
      throws Exception {
    for (String layout : List.of("QSSREQ01", "QSDREQ01", "NTSREQ01", "NTDREQ01"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var service = service(f, f.source);
        var input = input(layout);
        assertArrayEquals(expected(layout, "0000", 2), service.process(input));
        assertEquals(0, f.live.get());
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.request_inbox where processing_state='COMPLETED' and"
                    + " operation_token is null and result_ref_type='NONE' and"
                    + " expires_at=completed_at+interval '24 hours'"));
        String old = metadata(f);
        f.sql(
            "update schubert.questions set body='changed independently',version=version+1 where"
                + " id=3");
        assertArrayEquals(expected(layout, "0200", 3), service.process(input));
        assertEquals(old, metadata(f));
        assertEquals(
            1, f.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
        assertEquals(53, f.scalar("select count(*) from schubert.notifications"));
      }
  }

  @Test
  void qry019AdminSnapshotCannotLeakToUserIncludingEmptyPageAndNewStage() throws Exception {
    for (String layout : List.of("QSSREQ01", "QSDREQ01")) {
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        f.sql("update schubert.app_users set role='ADMIN' where id=1");
        var input = input(layout);
        var service = service(f, f.source);
        assertArrayEquals(expected(layout, "0000", 2), service.process(input));
        String before = metadata(f);
        f.sql("update schubert.app_users set role='USER' where id=1");
        assertArrayEquals(
            expected(layout, layout.equals("QSSREQ01") ? "0103" : "0104", 3),
            service.process(input));
        assertEquals(before, metadata(f));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where category='SECURITY' and action='"
                    + (layout.equals("QSSREQ01") ? "AUTHORIZATION_DENIED" : "OWNER_SCOPE_DENIED")
                    + "'"));
      }
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        f.sql("update schubert.app_users set role='ADMIN' where id=1");
        var source =
            afterRead(f, () -> f.sql("update schubert.app_users set role='USER' where id=1"));
        assertArrayEquals(
            expected(layout, layout.equals("QSSREQ01") ? "0103" : "0104", 1),
            service(f, source).process(input(layout)));
        assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
      }
    }
  }

  @Test
  void qry020NarrowUserStageStaysUserAndFinalInboxWinnerIsRechecked() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      var source =
          afterRead(f, () -> f.sql("update schubert.app_users set role='ADMIN' where id=1"));
      assertArrayEquals(
          expected("QSSREQ01", "0000", 2), service(f, source).process(input("QSSREQ01")));
      byte[] plain = QuestionQueryReplayServiceTest.decrypt(completion(f), MESSAGE, 1);
      assertArrayEquals(HexFormat.of().parseHex("4e4b515259310055"), Arrays.copyOf(plain, 8));
      Arrays.fill(plain, (byte) 0);
    }
    for (String layout : List.of("QSSREQ01", "QSDREQ01"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var competitor = service(f, f.source);
        String[] winningMetadata = {""};
        var source =
            afterRead(
                f,
                () -> {
                  f.sql("update schubert.app_users set role='ADMIN' where id=1");
                  competitor.process(input(layout));
                  try {
                    winningMetadata[0] = metadata(f);
                  } catch (Exception e) {
                    throw new AssertionError(e);
                  }
                  f.sql("update schubert.app_users set role='USER' where id=1");
                });
        assertArrayEquals(
            expected(layout, layout.equals("QSSREQ01") ? "0103" : "0104", 3),
            service(f, source).process(input(layout)));
        assertEquals(winningMetadata[0], metadata(f));
        assertEquals(
            0, f.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
      }
  }

  @Test
  void qry021LatestRevokedOrChangedOwnerIsNonstoredAndValidationCannotAuthorize() throws Exception {
    for (String sql :
        List.of(
            "update schubert.auth_sessions set"
                + " revoked=true,revoked_at='2026-10-01T00:00:00.123456Z',revoke_reason='ADMIN'"
                + " where user_id=1",
            "update schubert.app_users set status='DISABLED' where id=1",
            "update schubert.auth_sessions set user_id=2 where user_id=1"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var source = afterRead(f, () -> f.sql(sql));
        assertArrayEquals(
            expected("QSSREQ01", "0102", 1), service(f, source).process(input("QSSREQ01")));
        assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
        assertEquals(
            1,
            f.scalar("select count(*) from schubert.app_logs where action='AUTHORIZATION_DENIED'"));
      }
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      byte[] bytes = data("QSSREQ01", false);
      put(bytes, 256, "u1");
      assertArrayEquals(
          expected("QSSREQ01", "0100", 1),
          service(f, f.source).process(message("QSSREQ01", bytes)));
      assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
    }
  }

  @Test
  void qry022MismatchAndDatabaseFailuresNeverReturnSuccessOrModifySavedResult() throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      var service = service(f, f.source);
      service.process(input("QSSREQ01"));
      String before = metadata(f);
      byte[] changed = data("QSSREQ01", false);
      put(changed, 0, "different");
      assertThrows(
          PermanentProtocolException.class, () -> service.process(message("QSSREQ01", changed)));
      assertEquals(before, metadata(f));
      assertEquals(
          1, f.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
      f.sql("update schubert.app_users set role='ADMIN' where id=1");
      service.process(input("QSSREQ01"));
      assertEquals(before, metadata(f));
    }
    for (String fault : List.of("open", "null", "setAutoCommit", "setReadOnly", "commit", "close"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        f.fault = fault;
        var service = service(f, f.source);
        var error =
            assertThrows(
                TemporaryInfrastructureException.class, () -> service.process(input("QSSREQ01")));
        assertNull(error.getCause());
        assertEquals(0, error.getSuppressed().length);
        assertEquals(0, f.live.get());
      }
  }

  static QuestionQueryApplicationService service(
      QuestionSubmissionServiceTest.Fixture f, DataSource source) throws Exception {
    return new QuestionQueryApplicationService(
        source,
        new AuthenticationContextVerifier(new ContextHash()),
        new QuestionQueryRepository(),
        new JdbcInboxCoordinator(f.fingerprints),
        new QuestionQueryReplayService(f.snapshots),
        Clock.fixed(STAMP, ZoneOffset.UTC),
        () -> new UUID(101, f.ids.incrementAndGet()));
  }

  @Test
  void qry026PublicAssemblyConstructorNullInvariantAndFreshUuidHaveIndependentPayload()
      throws Exception {
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      var authentication = new AuthenticationContextVerifier(new ContextHash());
      var repository = new QuestionQueryRepository();
      var inbox = new JdbcInboxCoordinator(f.fingerprints);
      var responses = new QuestionQueryReplayService(f.snapshots);
      var clock = Clock.fixed(STAMP, ZoneOffset.UTC);
      Object[] values = {f.source, authentication, repository, inbox, responses, clock};
      for (int missing = 0; missing < values.length; missing++) {
        Object[] args = values.clone();
        args[missing] = null;
        assertThrows(
            NullPointerException.class,
            () ->
                new QuestionQueryApplicationService(
                    (DataSource) args[0], (AuthenticationContextVerifier) args[1],
                    (QuestionQueryRepository) args[2], (JdbcInboxCoordinator) args[3],
                    (QuestionQueryReplayService) args[4], (Clock) args[5]));
      }
      assertThrows(
          NullPointerException.class,
          () ->
              new QuestionQueryApplicationService(
                  f.source, authentication, repository, inbox, responses, clock, null));
      var service =
          new QuestionQueryApplicationService(
              f.source, authentication, repository, inbox, responses, clock);
      assertThrows(NullPointerException.class, () -> service.process(null));
      byte[] actual = service.process(input("QSSREQ01"));
      assertArrayEquals(
          Arrays.copyOfRange(expected("QSSREQ01", "0000", 2), 256, 304),
          Arrays.copyOfRange(actual, 256, 304));
      assertEquals("0000", new String(actual, 208, 4, StandardCharsets.US_ASCII));
      assertEquals(MESSAGE.toString(), new String(actual, 60, 36, StandardCharsets.US_ASCII));
      UUID first = UUID.fromString(new String(actual, 24, 36, StandardCharsets.US_ASCII));
      assertNotEquals(new UUID(0, 0), first);
      String saved = metadata(f);
      byte[] replay = service.process(input("QSSREQ01"));
      assertEquals("0200", new String(replay, 208, 4, StandardCharsets.US_ASCII));
      assertNotEquals(
          first, UUID.fromString(new String(replay, 24, 36, StandardCharsets.US_ASCII)));
      assertArrayEquals(Arrays.copyOfRange(actual, 256, 304), Arrays.copyOfRange(replay, 256, 304));
      assertEquals(saved, metadata(f));
      assertEquals(0, f.live.get());
    }
  }

  @Test
  void qry023DefiniteFailureCapacityAndInitialInvalidContextKeepOriginalRows() throws Exception {
    for (String layout : List.of("QSDREQ01", "NTDREQ01"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        byte[] bytes = data(layout, false);
        var absent = message(layout, bytes);
        var service = service(f, f.source);
        assertArrayEquals(expected(layout, "0104", 2), service.process(absent));
        String saved = metadata(f);
        assertArrayEquals(expected(layout, "0104", 3), service.process(absent));
        assertEquals(saved, metadata(f));
        assertEquals(
            1,
            f.scalar("select count(*) from schubert.request_inbox where processing_state='ERROR'"));
      }
    for (String layout : List.of("QSSREQ01", "NTSREQ01"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        f.sql("update schubert.app_users set role='ADMIN' where id=1");
        var limited = mappedSource(f, c -> QuestionQueryRepositoryTest.fault(c, "total-cap"));
        assertArrayEquals(expected(layout, "9001", 2), service(f, limited).process(input(layout)));
        String saved = metadata(f);
        f.sql("update schubert.app_users set role='USER' where id=1");
        assertArrayEquals(
            expected(layout, layout.equals("QSSREQ01") ? "0103" : "9001", 3),
            service(f, f.source).process(input(layout)));
        assertEquals(saved, metadata(f));
      }
    try (var f = QuestionQueryRepositoryTest.fixture(db)) {
      f.sql("update schubert.app_users set status='DISABLED' where id=1");
      var source =
          afterRead(f, () -> f.sql("update schubert.app_users set status='ACTIVE' where id=1"));
      assertArrayEquals(
          expected("QSSREQ01", "0102", 1), service(f, source).process(input("QSSREQ01")));
      assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
    }
  }

  @Test
  void qry024ReadSavedRowsCannotDisappearChangeOrBeRepaired() throws Exception {
    for (String change :
        List.of(
            "delete from schubert.request_inbox",
            "update schubert.request_inbox set"
                + " response_body_encrypted=set_byte(response_body_encrypted,30,1-get_byte(response_body_encrypted,30)%2)",
            "update schubert.request_inbox set completed_at=completed_at+interval '1 millisecond'",
            "update schubert.request_inbox set response_key_version='gone'",
            "update schubert.request_inbox set fingerprint_key_version='gone'",
            "update schubert.request_inbox set request_fingerprint_hmac=repeat('0',64)"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        service(f, f.source).process(input("QSSREQ01"));
        var source = afterRead(f, () -> f.sql(change));
        var service = service(f, source);
        if (change.contains("fingerprint_hmac"))
          assertThrows(PermanentProtocolException.class, () -> service.process(input("QSSREQ01")));
        else
          assertThrows(
              TemporaryInfrastructureException.class, () -> service.process(input("QSSREQ01")));
        assertEquals(
            change.startsWith("delete") ? 0 : 1,
            f.scalar("select count(*) from schubert.request_inbox"));
        assertEquals(0, f.live.get());
      }
    for (String change :
        List.of(
            "update schubert.request_inbox set fingerprint_key_version='gone'",
            "update schubert.request_inbox set"
                + " processing_state='PROCESSING',completed_at=null,result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        service(f, f.source).process(input("QSSREQ01"));
        f.sql(change);
        var service = service(f, f.source);
        assertThrows(
            TemporaryInfrastructureException.class, () -> service.process(input("QSSREQ01")));
        assertEquals(1, f.scalar("select count(*) from schubert.request_inbox"));
      }
  }

  @Test
  void qry025SqlAuditCountSuppressedCloseRollbackAndFinalResourceFailureAreAtomic()
      throws Exception {
    for (String part :
        List.of(
            "with projected as",
            "insert into schubert.request_inbox",
            "update schubert.request_inbox"))
      for (String mode : List.of("execute", "close", "count", "count-close", "rollback")) {
        if (part.equals("with projected as") && mode.startsWith("count")) continue;
        try (var f = QuestionQueryRepositoryTest.fixture(db)) {
          var source = sqlFault(f, part, mode);
          var service = service(f, source);
          assertThrows(
              TemporaryInfrastructureException.class,
              () -> service.process(input("QSSREQ01")),
              part + ":" + mode);
          assertEquals(0, f.live.get());
          assertEquals(0, f.scalar("select count(*) from schubert.request_inbox"));
        }
      }
    for (String mode : List.of("execute", "close", "count", "rollback"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        f.sql("update schubert.app_users set role='ADMIN' where id=1");
        service(f, f.source).process(input("QSSREQ01"));
        String saved = metadata(f);
        f.sql("update schubert.app_users set role='USER' where id=1");
        var service = service(f, sqlFault(f, "insert into schubert.app_logs", mode));
        assertThrows(
            TemporaryInfrastructureException.class, () -> service.process(input("QSSREQ01")));
        assertEquals(saved, metadata(f));
        assertEquals(0, f.scalar("select count(*) from schubert.app_logs"));
      }
    for (String fault : List.of("open", "null", "setAutoCommit", "setReadOnly", "commit", "close"))
      try (var f = QuestionQueryRepositoryTest.fixture(db)) {
        var opens = new AtomicInteger();
        var source =
            (DataSource)
                Proxy.newProxyInstance(
                    DataSource.class.getClassLoader(),
                    new Class<?>[] {DataSource.class},
                    (p, m, a) -> {
                      if (opens.incrementAndGet() == 2) f.fault = fault;
                      return QuestionSubmissionServiceTest.invoke(f.source, m, a);
                    });
        var service = service(f, source);
        assertThrows(
            TemporaryInfrastructureException.class, () -> service.process(input("QSSREQ01")));
        assertEquals(0, f.live.get());
        // commit/close uncertainty must never be represented by a successful wire.
        assertEquals(2, opens.get());
        assertEquals(
            fault.equals("close") ? 1 : 0, f.scalar("select count(*) from schubert.request_inbox"));
      }
  }

  static DataSource mappedSource(
      QuestionSubmissionServiceTest.Fixture f,
      java.util.function.UnaryOperator<Connection> mapper) {
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (p, m, a) ->
                mapper.apply((Connection) QuestionSubmissionServiceTest.invoke(f.source, m, a)));
  }

  static DataSource sqlFault(QuestionSubmissionServiceTest.Fixture f, String part, String mode) {
    return mappedSource(
        f,
        c ->
            (Connection)
                Proxy.newProxyInstance(
                    Connection.class.getClassLoader(),
                    new Class<?>[] {Connection.class},
                    (p, m, a) -> {
                      if (m.getName().equals("rollback") && mode.equals("rollback"))
                        throw new java.sql.SQLException("synthetic rollback failure");
                      if (!m.getName().equals("prepareStatement")
                          || !a[0].toString().contains(part))
                        return QuestionSubmissionServiceTest.invoke(c, m, a);
                      var statement = QuestionSubmissionServiceTest.invoke(c, m, a);
                      return Proxy.newProxyInstance(
                          java.sql.PreparedStatement.class.getClassLoader(),
                          new Class<?>[] {java.sql.PreparedStatement.class},
                          (sp, sm, sa) -> {
                            if ((sm.getName().equals("executeQuery")
                                    || sm.getName().equals("executeUpdate"))
                                && (mode.equals("execute") || mode.equals("rollback")))
                              throw new java.sql.SQLException("synthetic statement failure");
                            if (sm.getName().equals("executeUpdate") && mode.startsWith("count"))
                              return 0;
                            Object actual = QuestionSubmissionServiceTest.invoke(statement, sm, sa);
                            if (sm.getName().equals("close") && mode.contains("close"))
                              throw new java.sql.SQLException("synthetic statement close failure");
                            return actual;
                          });
                    }));
  }

  static DataSource afterRead(QuestionSubmissionServiceTest.Fixture f, Runnable hook) {
    var commits = new AtomicInteger();
    return (DataSource)
        Proxy.newProxyInstance(
            DataSource.class.getClassLoader(),
            new Class<?>[] {DataSource.class},
            (p, m, a) -> {
              var connection = (Connection) QuestionSubmissionServiceTest.invoke(f.source, m, a);
              return Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (cp, cm, ca) -> {
                    Object value = QuestionSubmissionServiceTest.invoke(connection, cm, ca);
                    if (cm.getName().equals("commit") && commits.incrementAndGet() == 1) hook.run();
                    return value;
                  });
            });
  }

  static WireMessage<FixedPayload> input(String layout) {
    byte[] bytes = data(layout, false);
    if (layout.equals("QSSREQ01")) put(bytes, 0, "missing-literal");
    if (layout.equals("NTSREQ01")) put(bytes, 0, "ERROR");
    if (layout.contains("DREQ")) put(bytes, 0, "000000000003");
    return message(layout, bytes);
  }

  static String metadata(QuestionSubmissionServiceTest.Fixture f) throws Exception {
    return HexFormat.of()
        .formatHex(
            MessageDigest.getInstance("SHA-256")
                .digest(
                    f.text("select row_to_json(r)::text from schubert.request_inbox r")
                        .getBytes(StandardCharsets.UTF_8)));
  }

  static InboxCompletion completion(QuestionSubmissionServiceTest.Fixture f) throws Exception {
    try (var c = db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select response_body_encrypted,response_key_version,completed_at from"
                    + " schubert.request_inbox")) {
      assertTrue(r.next());
      return new InboxCompletion(
          InboxCompletionState.COMPLETED,
          InboxResultReference.none(),
          "QSSRSP01",
          "001",
          Optional.of(new EncryptedResponseSnapshot(r.getString(2), r.getBytes(1))),
          r.getObject(3, OffsetDateTime.class).toInstant());
    }
  }

  static byte[] expected(String layout, String code, int response) {
    boolean success = code.equals("0000") || code.equals("0200");
    byte[] b =
        QuestionQueryWireOracle.wire(
            layout,
            MESSAGE,
            new UUID(101, response),
            STAMP,
            QuestionQueryRequestTest.NOW,
            code,
            layout.equals("NTSREQ01") ? 1 : 0);
    if (!success) return b;
    String body = "😀".repeat(101) + "alpha%_\\";
    if (layout.equals("QSDREQ01")) {
      Arrays.fill(b, 256, b.length, (byte) 32);
      put(b, 256, "000000000003");
      put(b, 268, "0".repeat(25) + "3");
      put(b, 294, "u1");
      put(b, 358, "ANSWERED");
      put(b, 370, body);
      put(b, 8562, "20261001090000123");
      put(b, 8579, "20261001090000125");
    } else if (layout.equals("NTDREQ01")) {
      Arrays.fill(b, 256, b.length, (byte) 32);
      put(b, 256, "000000000003");
      put(b, 268, "0".repeat(25) + "3");
      put(b, 294, "COMPLETED");
      put(b, 306, "COMPLETED");
      put(b, 318, "20261001090000123");
      put(b, 335, "20261001090000124");
      put(b, 352, "20261001090000125");
      put(b, 403, "0");
      put(b, 404, body);
      put(b, 9124, "3");
    } else if (layout.equals("NTSREQ01")) {
      Arrays.fill(b, 304, b.length, (byte) 32);
      put(b, 304, "000000000004");
      put(b, 316, "0".repeat(25) + "4");
      put(b, 342, "ERROR");
      put(b, 354, "ERROR");
      put(b, 366, "20261001090000123");
      put(b, 383, "20261001090000125");
      put(b, 400, "question4");
      put(b, 912, "0");
    }
    return b;
  }
}
