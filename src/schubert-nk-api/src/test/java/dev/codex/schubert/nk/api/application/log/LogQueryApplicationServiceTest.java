package dev.codex.schubert.nk.api.application.log;

import static dev.codex.schubert.nk.api.application.log.LogVectors.put;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.idempotency.EncryptedResponseSnapshot;
import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.persistence.LogQueryRepository;
import dev.codex.schubert.nk.api.security.AuthContextCodec;
import dev.codex.schubert.nk.api.security.AuthenticationContextVerifier;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Actual PG/Flyway and independent full wire/SQL assertions, PG-D-092/PT-ADM-067..073. */
class LogQueryApplicationServiceTest {
  private static final int FIXTURE_FIRST_COMMIT_ORDINAL = 1;
  private static final int FIXTURE_SECOND_COMMIT_ORDINAL = 2;
  private static final int FIXTURE_THIRD_COMMIT_ORDINAL = 3;
  private static final String FIXTURE_RESULT_SUCCESS = "0000";
  private static final String FIXTURE_RESULT_IDEMPOTENT_SUCCESS = "0200";
  private static final String FIXTURE_RESULT_FORBIDDEN = "0103";
  private static final String FIXTURE_INBOX_COUNT_SQL =
      "select count(*) from schubert.request_inbox";
  private static final String FIXTURE_NO_CONNECTION_FAULT = "none";
  private static final String FIXTURE_IN_VM_BROKER_URL = "vm://0";
  private static final String FIXTURE_DATABASE_FAULT_POINT = "database";

  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static final Instant NOW = LogVectors.NOW.plusSeconds(60);
  static final UUID MESSAGE = new UUID(110, 1);

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @Test
  void adm067QueriesCommitFrozenRecordsAndFullRetention() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      for (int count : new int[] {0, 1, 100}) {
        seed(f, count);
        var service = service(f);
        var message = input(null, MESSAGE, 1);
        assertArrayEquals(
            expected(message, FIXTURE_RESULT_SUCCESS, 2, count), service.process(message));
        assertEquals(2, f.commits.get());
        assertEquals(0, f.live.get());
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.request_inbox where owner_user_id=1 and"
                    + " operation_token is null and result_ref_type='NONE' and"
                    + " processing_state='COMPLETED' and expires_at=completed_at+interval '24"
                    + " hours'"));
        byte[] independent =
            LogVectors.check(
                LogRequest.decode(message),
                LogVectors.ADMIN,
                Arrays.asList(null, null, "TEST", null, null, null, null),
                1);
        assertEquals(
            HexFormat.of().formatHex(independent),
            f.text("select request_fingerprint_hmac from schubert.request_inbox"));
        Arrays.fill(independent, (byte) 0);
        assertArrayEquals(
            expected(message, FIXTURE_RESULT_SUCCESS, 1, count),
            LogVectors.decrypt(completion(f), MESSAGE, 1));
        var metadata = f.inboxMetadata();
        f.sql("update schubert.app_logs set message='Changed' where action='TEST'");
        assertArrayEquals(
            expected(message, FIXTURE_RESULT_IDEMPOTENT_SUCCESS, 3, count),
            service.process(message));
        assertArrayEquals(
            expected(message, FIXTURE_RESULT_IDEMPOTENT_SUCCESS, 4, count),
            service.process(message));
        assertEquals(metadata, f.inboxMetadata());
        assertEquals(
            2, f.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
        assertEquals(0, f.scalar("select sum(version) from schubert.app_users"));
      }
      seed(f);
      var broad =
          new WireMessage<>(
              input(null, MESSAGE, 1).header(),
              new FixedPayload(LogVectors.data(LogVectors.emptyFilters(), 1), 0, List.of()));
      var broadService = service(f);
      assertArrayEquals(expected(broad, FIXTURE_RESULT_SUCCESS, 2, 1), broadService.process(broad));
      assertArrayEquals(
          expected(broad, FIXTURE_RESULT_IDEMPOTENT_SUCCESS, 3, 1), broadService.process(broad));
      // The replay audit is a newly visible Log, but cannot be appended to the frozen result.
      var fresh =
          new WireMessage<>(
              input(null, new UUID(110, 999), 1).header(),
              new FixedPayload(LogVectors.data(LogVectors.emptyFilters(), 1), 0, List.of()));
      byte[] freshBody = broadService.process(fresh);
      assertEquals("000002", new String(freshBody, 193, 6, StandardCharsets.US_ASCII));
      assertEquals("000000002", new String(freshBody, 265, 9, StandardCharsets.US_ASCII));
      assertEquals("000000000002", new String(freshBody, 304, 12, StandardCharsets.US_ASCII));
      assertEquals(
          "INBOX_REPLAYED",
          new String(freshBody, 357, 64, StandardCharsets.US_ASCII).stripTrailing());
      assertEquals("000000000001", new String(freshBody, 2392, 12, StandardCharsets.US_ASCII));
      assertArrayEquals(
          expected(broad, FIXTURE_RESULT_IDEMPOTENT_SUCCESS, 6, 1), broadService.process(broad));
      seed(f, 101);
      var message = input(null, MESSAGE, 1, 999999);
      byte[] last = expected(message, FIXTURE_RESULT_SUCCESS, 2, 1);
      LogVectors.put(last, 256, "000002100000000101000002000000101000000101");
      assertArrayEquals(last, service(f).process(message));
      seed(f);
      var filtered = input("message 1", MESSAGE, 1);
      assertArrayEquals(
          expected(filtered, FIXTURE_RESULT_SUCCESS, 2, 1), service(f).process(filtered));
      seed(f);
      var capacity = input(null, MESSAGE, 1);
      var fault = new LogJdbcFaults();
      fault.sqlPart = "with filtered as";
      fault.columns.put("total", 99999901L);
      f.sqlFault = fault;
      assertArrayEquals(expected(capacity, "9001", 2, 0), service(f).process(capacity));
      f.sqlFault = null;
      assertArrayEquals(expected(capacity, "9001", 3, 0), service(f).process(capacity));
      assertEquals(
          1,
          f.scalar(
              "select count(*) from schubert.request_inbox where processing_state='ERROR' and"
                  + " expires_at=completed_at+interval '24 hours'"));
    }
  }

  @Test
  void adm068BothStagesRecheckIdentityRoleAndAuditDenials() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      for (int context : new int[] {3, 99}) {
        seed(f);
        var request = input(null, MESSAGE, context);
        String code = context == 3 ? FIXTURE_RESULT_FORBIDDEN : "0102";
        assertArrayEquals(expected(request, code, 1, 0), service(f).process(request));
        assertEquals(0, f.scalar(FIXTURE_INBOX_COUNT_SQL));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='AUTHORIZATION_DENIED' and"
                    + " actor_user_id "
                    + (context == 3 ? "=3" : "is null")));
      }
      for (String change :
          List.of(
              "update schubert.auth_sessions set"
                  + " revoked=true,revoked_at='2026-09-08T00:01:00Z',revoke_reason='ADMIN' where"
                  + " user_id=1",
              "update schubert.auth_sessions set expires_at='2026-09-08T00:01:00Z' where user_id=1",
              "update schubert.app_users set status='DISABLED' where id=1",
              "update schubert.app_users set role='USER' where id=1",
              "update schubert.auth_sessions set user_id=2 where user_id=1")) {
        seed(f);
        f.afterCommit =
            () -> {
              if (f.commits.get() == FIXTURE_FIRST_COMMIT_ORDINAL)
                try {
                  f.sql(change);
                } catch (SQLException failure) {
                  throw new AssertionError(failure);
                }
            };
        var request = input(null, MESSAGE, 1);
        String code = change.contains("role='USER'") ? FIXTURE_RESULT_FORBIDDEN : "0102";
        assertArrayEquals(expected(request, code, 1, 0), service(f).process(request));
        assertEquals(0, f.scalar(FIXTURE_INBOX_COUNT_SQL));
        assertEquals(
            1,
            f.scalar("select count(*) from schubert.app_logs where action='AUTHORIZATION_DENIED'"));
        f.afterCommit = () -> {};
      }
      for (boolean missing : List.of(false, true)) {
        seed(f);
        if (!missing) f.sql("update schubert.app_users set role='USER' where id=1");
        f.afterCommit =
            () -> {
              if (f.commits.get() == FIXTURE_FIRST_COMMIT_ORDINAL)
                try {
                  if (missing) f.session(1, 99);
                  else f.sql("update schubert.app_users set role='ADMIN' where id=1");
                } catch (Exception failure) {
                  throw new AssertionError(failure);
                }
            };
        var request = input(null, MESSAGE, missing ? 99 : 1);
        String code = missing ? "0102" : FIXTURE_RESULT_FORBIDDEN;
        assertArrayEquals(expected(request, code, 1, 0), service(f).process(request));
        assertEquals(0, f.inboxCount());
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.app_logs where action='AUTHORIZATION_DENIED' and"
                    + " actor_user_id "
                    + (missing ? "is null" : "=1")));
        f.afterCommit = () -> {};
      }
      seed(f);
      var service = service(f);
      service.process(input(null, MESSAGE, 1));
      assertThrows(
          PermanentProtocolException.class, () -> service.process(input("different", MESSAGE, 1)));
      assertEquals(1, f.scalar(FIXTURE_INBOX_COUNT_SQL));
      assertEquals(
          1, f.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
    }
  }

  @Test
  void adm073PublicBoundariesAndAuditAllowlistAreExplicit() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      seed(f);
      var auth = new AuthenticationContextVerifier(new ContextHash());
      var query = new LogQueryRepository();
      var replay = new LogReplayService(f.snapshots);
      var clock = Clock.fixed(NOW, ZoneOffset.UTC);
      assertThrows(
          NullPointerException.class,
          () -> new LogQueryApplicationService(null, auth, query, f.inbox, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new LogQueryApplicationService(f.source, null, query, f.inbox, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new LogQueryApplicationService(f.source, auth, null, f.inbox, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new LogQueryApplicationService(f.source, auth, query, null, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new LogQueryApplicationService(f.source, auth, query, f.inbox, null, clock));
      assertThrows(
          NullPointerException.class,
          () -> new LogQueryApplicationService(f.source, auth, query, f.inbox, replay, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new LogQueryApplicationService(f.source, auth, query, f.inbox, replay, clock, null));
      var service = service(f);
      assertThrows(NullPointerException.class, () -> service.process(null));
      assertThrows(
          PermanentProtocolException.class,
          () ->
              service.process(
                  LogVectors.message(
                      "UDTREQ01", "000000000001".getBytes(StandardCharsets.US_ASCII), MESSAGE)));
      assertEquals(0, f.commits.get());
      assertEquals(0, f.live.get());
      var tracked =
          new LogQueryApplicationService(
              f.source,
              auth,
              query,
              f.inbox,
              replay,
              clock,
              () -> {
                int id = f.ids.incrementAndGet();
                assertEquals(id == 1 ? 1 : 0, f.live.get());
                assertEquals(id == 1 ? 1 : 2, f.commits.get());
                return new UUID(101, id);
              });
      var request = input(null, MESSAGE, 1);
      assertArrayEquals(expected(request, FIXTURE_RESULT_SUCCESS, 2, 1), tracked.process(request));
      seed(f);
      byte[] random =
          new LogQueryApplicationService(f.source, auth, query, f.inbox, replay, clock)
              .process(request);
      UUID response = UUID.fromString(new String(random, 24, 36, StandardCharsets.US_ASCII));
      assertEquals(4, response.version());
      byte[] expected = expected(request, FIXTURE_RESULT_SUCCESS, 2, 1);
      put(expected, 24, response.toString());
      assertArrayEquals(expected, random);
      seed(f);
      f.sql("update schubert.app_users set username=E'u3\\n' where id=3");
      var denied = input("synthetic-private-search", MESSAGE, 3);
      assertArrayEquals(
          expected(denied, FIXTURE_RESULT_FORBIDDEN, 1, 0), service(f).process(denied));
      assertEquals(
          "u3 ",
          f.text(
              "select actor_username from schubert.app_logs where action='AUTHORIZATION_DENIED'"));
      assertEquals(
          "WARN",
          f.text("select level from schubert.app_logs where action='AUTHORIZATION_DENIED'"));
      assertEquals(
          "SECURITY",
          f.text("select category from schubert.app_logs where action='AUTHORIZATION_DENIED'"));
      String details =
          f.text("select details::text from schubert.app_logs where action='AUTHORIZATION_DENIED'");
      var json = com.google.gson.JsonParser.parseString(details).getAsJsonObject();
      assertEquals(
          Set.of("layout", "reason", "targetType", "outcome", "actorRole", "step"), json.keySet());
      assertFalse(details.contains("synthetic-private-search"));
      assertEquals("USER", json.get("actorRole").getAsString());
      assertEquals("LOG", json.get("targetType").getAsString());
      assertEquals("LGSREQ01", json.get("layout").getAsString());
      assertEquals("ROLE_DENIED", json.get("reason").getAsString());
      assertEquals("DENIED", json.get("outcome").getAsString());
      assertEquals("ADMIN_ROLE", json.get("step").getAsString());
      assertTrue(details.getBytes(StandardCharsets.UTF_8).length <= 1024);
    }
  }

  @Test
  void adm069DatabaseCryptoAndResourceFailuresRollbackSafely() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      var request = input(null, MESSAGE, 1);
      for (boolean finalStage : List.of(false, true))
        for (String fault :
            List.of("open", "null", "setAutoCommit", "setReadOnly", "commit", "close")) {
          seed(f);
          if (finalStage)
            f.afterCommit =
                () -> {
                  if (f.commits.get() == FIXTURE_FIRST_COMMIT_ORDINAL) f.connectionFault = fault;
                };
          else f.connectionFault = fault;
          deny(() -> service(f).process(request));
          assertEquals(0, f.live.get());
          f.connectionFault = FIXTURE_NO_CONNECTION_FAULT;
          f.afterCommit = () -> {};
          assertEquals(0, f.inboxCount());
        }
      for (String sql :
          List.of(
              "select s.id",
              "select correlation_id",
              "with filtered as",
              "for update of u",
              "update schubert.auth_sessions",
              "insert into schubert.request_inbox",
              "update schubert.request_inbox"))
        for (String failure : List.of("prepareStatement", "statementClose")) {
          seed(f);
          var fault = new LogJdbcFaults();
          fault.sqlPart = sql;
          fault.fault = failure;
          f.sqlFault = fault;
          deny(() -> service(f).process(request));
          assertEquals(0, f.live.get());
          assertEquals(0, f.inboxCount());
          f.sqlFault = null;
        }
      for (boolean close : List.of(false, true)) {
        seed(f);
        var fault = new LogJdbcFaults();
        fault.sqlPart = "update schubert.request_inbox";
        fault.updateCount = 0;
        fault.fault = close ? "statementClose" : FIXTURE_NO_CONNECTION_FAULT;
        f.sqlFault = fault;
        deny(() -> service(f).process(request));
        assertEquals(0, f.inboxCount());
        f.sqlFault = null;
      }
      seed(f);
      f.rollbackFails = true;
      var fault = new LogJdbcFaults();
      fault.sqlPart = "with filtered as";
      fault.fault = "prepareStatement";
      f.sqlFault = fault;
      deny(() -> service(f).process(request));
      assertEquals(1, f.rollbacks.get());
      assertEquals(0, f.live.get());
      f.rollbackFails = false;
      f.sqlFault = null;
      for (int context : new int[] {3, 99})
        for (String failure : List.of("prepareStatement", "statementClose", "count")) {
          seed(f);
          var auditFault = new LogJdbcFaults();
          auditFault.sqlPart = "insert into schubert.app_logs";
          auditFault.fault = failure;
          if (failure.equals("count")) auditFault.updateCount = 0;
          f.sqlFault = auditFault;
          deny(() -> service(f).process(input(null, MESSAGE, context)));
          assertEquals(0, f.inboxCount());
          assertEquals(1, f.scalar("select count(*) from schubert.app_logs"));
          f.sqlFault = null;
        }
      for (int idFailure : new int[] {1, 2}) {
        seed(f);
        var auth = new AuthenticationContextVerifier(new ContextHash());
        var service =
            new LogQueryApplicationService(
                f.source,
                auth,
                new LogQueryRepository(),
                f.inbox,
                new LogReplayService(f.snapshots),
                Clock.fixed(NOW, ZoneOffset.UTC),
                () -> f.ids.incrementAndGet() == idFailure ? null : new UUID(101, 99));
        deny(() -> service.process(request));
        assertEquals(idFailure == 1 ? 0 : 1, f.inboxCount());
      }
      for (int stage : new int[] {1, 2, 3, 4, 5}) {
        seed(f);
        var calls = new java.util.concurrent.atomic.AtomicInteger();
        Clock clock =
            new Clock() {
              @Override
              public ZoneId getZone() {
                return ZoneOffset.UTC;
              }

              @Override
              public Clock withZone(ZoneId ignored) {
                return this;
              }

              @Override
              public Instant instant() {
                if (calls.incrementAndGet() == stage)
                  throw new IllegalStateException("synthetic-private-clock");
                return NOW;
              }
            };
        var service =
            new LogQueryApplicationService(
                f.source,
                new AuthenticationContextVerifier(new ContextHash()),
                new LogQueryRepository(),
                f.inbox,
                new LogReplayService(f.snapshots),
                clock,
                () -> new UUID(101, f.ids.incrementAndGet()));
        deny(() -> service.process(request));
        assertEquals(stage == 5 ? 1 : 0, f.inboxCount());
        assertEquals(0, f.live.get());
      }
      seed(f);
      f.afterCommit =
          () -> {
            if (f.commits.get() == FIXTURE_SECOND_COMMIT_ORDINAL) f.connectionFault = "close";
          };
      deny(() -> service(f).process(request));
      assertEquals(1, f.inboxCount());
      f.afterCommit = () -> {};
      f.connectionFault = FIXTURE_NO_CONNECTION_FAULT;
      assertArrayEquals(
          expected(request, FIXTURE_RESULT_IDEMPOTENT_SUCCESS, 2, 1), service(f).process(request));
      seed(f);
      f.fingerprints.close();
      deny(() -> service(f).process(request));
      assertEquals(0, f.inboxCount());
    }
    try (var f = new LogApplicationFixture(database)) {
      seed(f);
      f.snapshots.close();
      deny(() -> service(f).process(input(null, MESSAGE, 1)));
      assertEquals(0, f.inboxCount());
    }
  }

  @Test
  void adm070ConcurrentQueriesUseOnlyTheWinningSnapshot() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      for (boolean distinct : List.of(false, true)) {
        seed(f);
        var service = service(f);
        var initial = new java.util.concurrent.atomic.AtomicInteger();
        var repeated = new java.util.concurrent.atomic.AtomicInteger();
        try (var pool = java.util.concurrent.Executors.newFixedThreadPool(10)) {
          var futures = new ArrayList<java.util.concurrent.Future<Void>>();
          for (int i = 0; i < 100; i++) {
            int n = i;
            futures.add(
                pool.submit(
                    () -> {
                      var request = input(null, distinct ? new UUID(110, n + 1) : MESSAGE, 1);
                      byte[] actual = service.process(request);
                      String code = new String(actual, 208, 4, StandardCharsets.US_ASCII);
                      if (code.equals(FIXTURE_RESULT_SUCCESS)) initial.incrementAndGet();
                      else {
                        assertEquals(FIXTURE_RESULT_IDEMPOTENT_SUCCESS, code);
                        repeated.incrementAndGet();
                      }
                      byte[] expected = expected(request, code, 1, 1);
                      System.arraycopy(actual, 24, expected, 24, 36);
                      assertArrayEquals(expected, actual);
                      return null;
                    }));
          }
          for (var future : futures) future.get(30, java.util.concurrent.TimeUnit.SECONDS);
        }
        assertEquals(distinct ? 100 : 1, initial.get());
        assertEquals(distinct ? 0 : 99, repeated.get());
        assertEquals(distinct ? 100 : 1, f.inboxCount());
        assertEquals(200, f.commits.get());
        assertEquals(0, f.live.get());
      }
      for (boolean owner : List.of(false, true)) {
        seed(f);
        var service = service(f);
        var success = new java.util.concurrent.atomic.AtomicInteger();
        var denied = new java.util.concurrent.atomic.AtomicInteger();
        try (var pool = java.util.concurrent.Executors.newFixedThreadPool(10)) {
          var futures = new ArrayList<java.util.concurrent.Future<Void>>();
          for (int i = 0; i < 100; i++) {
            int n = i;
            futures.add(
                pool.submit(
                    () -> {
                      var request =
                          input(
                              owner ? null : n % 2 == 0 ? null : "u",
                              MESSAGE,
                              owner ? n % 2 + 1 : 1);
                      try {
                        byte[] actual = service.process(request);
                        assertTrue(
                            List.of(FIXTURE_RESULT_SUCCESS, FIXTURE_RESULT_IDEMPOTENT_SUCCESS)
                                .contains(new String(actual, 208, 4, StandardCharsets.US_ASCII)));
                        success.incrementAndGet();
                      } catch (PermanentProtocolException rejected) {
                        assertNull(rejected.getCause());
                        denied.incrementAndGet();
                      }
                      return null;
                    }));
          }
          for (var future : futures) future.get(30, java.util.concurrent.TimeUnit.SECONDS);
        }
        assertEquals(50, success.get());
        assertEquals(50, denied.get());
        assertEquals(1, f.inboxCount());
        assertEquals(
            50,
            f.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
      }
      seed(f);
      var request = input(null, MESSAGE, 1);
      service(f).process(request);
      f.sql(
          "update schubert.request_inbox set"
              + " processing_state='PROCESSING',completed_at=null,result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null");
      deny(() -> service(f).process(request));
      assertEquals(1, f.inboxCount());
    }
  }

  @Test
  void adm071SavedRowsCannotDisappearOrChangeBetweenStages() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      var request = input(null, MESSAGE, 1);
      for (String change :
          List.of(
              "delete from schubert.request_inbox",
              "update schubert.request_inbox set"
                  + " response_body_encrypted=set_byte(response_body_encrypted,30,1-get_byte(response_body_encrypted,30)%2)",
              "update schubert.request_inbox set completed_at=completed_at+interval '1"
                  + " millisecond'",
              "update schubert.request_inbox set response_key_version='gone'",
              "update schubert.request_inbox set request_fingerprint_hmac=repeat('0',64)")) {
        seed(f);
        var service = service(f);
        service.process(request);
        f.afterCommit =
            () -> {
              if (f.commits.get() == FIXTURE_THIRD_COMMIT_ORDINAL)
                try (var c = f.db.admin();
                    var s = c.createStatement()) {
                  s.executeUpdate(change);
                } catch (SQLException failure) {
                  throw new AssertionError(failure);
                }
            };
        if (change.contains("fingerprint"))
          assertThrows(PermanentProtocolException.class, () -> service.process(request));
        else deny(() -> service.process(request));
        f.afterCommit = () -> {};
        assertEquals(change.startsWith("delete") ? 0 : 1, f.inboxCount());
        assertEquals(0, f.live.get());
      }
      for (String change :
          List.of(
              "update schubert.request_inbox set response_key_version='gone'",
              "update schubert.request_inbox set fingerprint_key_version='gone'",
              "update schubert.request_inbox set"
                  + " response_body_encrypted=set_byte(response_body_encrypted,30,1-get_byte(response_body_encrypted,30)%2)")) {
        seed(f);
        service(f).process(request);
        f.sql(change);
        deny(() -> service(f).process(request));
        assertEquals(1, f.inboxCount());
      }
    }
  }

  @Test
  void adm072BrokerFailuresReplayOneCommittedLogResult() throws Exception {
    var brokerRoot = root.resolve("query-broker");
    org.apache.activemq.artemis.core.config.Configuration configuration;
    try (var file =
        java.nio.file.Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration =
          new org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser()
              .parseMainConfig(file);
    }
    configuration
        .setPagingDirectory(brokerRoot.resolve("paging").toString())
        .setBindingsDirectory(brokerRoot.resolve("bindings").toString())
        .setJournalDirectory(brokerRoot.resolve("journal").toString())
        .setLargeMessagesDirectory(brokerRoot.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", FIXTURE_IN_VM_BROKER_URL);
    var broker =
        new org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ()
            .setConfiguration(configuration)
            .start();
    var requestQueue =
        new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
            dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REQUEST
                .fullyQualifiedQueue());
    var replyQueue =
        new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
            dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REPLY_WEB
                .fullyQualifiedQueue());
    var dlqQueue =
        new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
            dev.codex.schubert.nk.protocol.transport.BrokerTopology.DEAD_LETTER
                .fullyQualifiedQueue());
    try (var factory =
            new org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory(
                FIXTURE_IN_VM_BROKER_URL);
        var producer = factory.createContext(jakarta.jms.JMSContext.AUTO_ACKNOWLEDGE);
        var receiver = factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED);
        var observer = factory.createContext(jakarta.jms.JMSContext.AUTO_ACKNOWLEDGE);
        var requests = receiver.createConsumer(requestQueue);
        var replies = observer.createConsumer(replyQueue);
        var dlq = observer.createConsumer(dlqQueue)) {
      for (String point : List.of("createProducer", "commit", FIXTURE_DATABASE_FAULT_POINT))
        try (var f = new LogApplicationFixture(database)) {
          seed(f);
          var request = input(null, MESSAGE, 1);
          var listener =
              new dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListener(
                  service(f), Clock.fixed(NOW, ZoneOffset.UTC));
          if (point.equals(FIXTURE_DATABASE_FAULT_POINT)) f.connectionFault = "open";
          var failing =
              (jakarta.jms.JMSContext)
                  java.lang.reflect.Proxy.newProxyInstance(
                      jakarta.jms.JMSContext.class.getClassLoader(),
                      new Class<?>[] {jakarta.jms.JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals(point)) {
                          assertEquals(1, f.inboxCount());
                          assertEquals(0, f.live.get());
                          throw new jakarta.jms.JMSRuntimeException("synthetic transport failure");
                        }
                        return LogApplicationFixture.invoke(receiver, m, a);
                      });
          send(producer, requestQueue, request);
          var first = requests.receive(5000);
          assertNotNull(first);
          if (point.equals(FIXTURE_DATABASE_FAULT_POINT))
            deny(() -> listener.onMessage(failing, first));
          else
            assertThrows(
                jakarta.jms.JMSRuntimeException.class, () -> listener.onMessage(failing, first));
          assertNull(replies.receive(250));
          assertEquals(point.equals(FIXTURE_DATABASE_FAULT_POINT) ? 0 : 1, f.inboxCount());
          f.connectionFault = FIXTURE_NO_CONNECTION_FAULT;
          var retry = requests.receive(5000);
          assertNotNull(retry);
          assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, retry);
          assertArrayEquals(
              expected(
                  request,
                  point.equals(FIXTURE_DATABASE_FAULT_POINT)
                      ? FIXTURE_RESULT_SUCCESS
                      : FIXTURE_RESULT_IDEMPOTENT_SUCCESS,
                  f.ids.get(),
                  1),
              brokerBody(replies.receive(5000)));
          var frozen = f.inboxMetadata();
          f.sql("update schubert.app_logs set message='Changed' where action='TEST'");
          send(producer, requestQueue, request);
          var duplicate = requests.receive(5000);
          assertNotNull(duplicate);
          listener.onMessage(receiver, duplicate);
          assertArrayEquals(
              expected(request, FIXTURE_RESULT_IDEMPOTENT_SUCCESS, f.ids.get(), 1),
              brokerBody(replies.receive(5000)));
          assertEquals(frozen, f.inboxMetadata());
          send(producer, requestQueue, input("changed", MESSAGE, 1));
          var invalid = requests.receive(5000);
          assertNotNull(invalid);
          assertThrows(
              dev.codex.schubert.nk.api.messaging.inbound.CommittedFatalInboundException.class,
              () -> listener.onMessage(receiver, invalid));
          assertNotNull(dlq.receive(5000));
          assertNull(replies.receive(250));
          assertNull(requests.receive(250));
          assertEquals(
              1,
              f.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
          assertEquals(frozen, f.inboxMetadata());
          assertEquals(0, f.live.get());
        }
    } finally {
      broker.stop();
    }
  }

  static byte[] brokerBody(jakarta.jms.Message received) throws Exception {
    var message = assertInstanceOf(jakarta.jms.BytesMessage.class, received);
    assertEquals(2392, message.getBodyLength());
    byte[] body = new byte[2392];
    assertEquals(2392, message.readBytes(body));
    assertEquals(
        new String(body, 60, 36, StandardCharsets.US_ASCII), message.getJMSCorrelationID());
    assertEquals(
        new String(body, 24, 36, StandardCharsets.US_ASCII),
        message.getStringProperty("NKMessageID"));
    assertEquals("LGSRSP01", message.getStringProperty("NKLayoutID"));
    assertEquals("001", message.getStringProperty("NKProtocolVersion"));
    return body;
  }

  static void deny(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(TemporaryInfrastructureException.class, action);
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertEquals("request transaction is unavailable", error.getMessage());
  }

  @Test
  void adm075ProductionAssemblyUsesRealDependenciesAndNullContract() throws Exception {
    try (var f = new LogApplicationFixture(database)) {
      seed(f);
      var service =
          LogQueryApplicationAssembly.create(
              f.source, f.fingerprints, f.snapshots, Clock.fixed(NOW, ZoneOffset.UTC));
      var request = input(null, MESSAGE, 1);
      byte[] first = service.process(request);
      assertEquals(FIXTURE_RESULT_SUCCESS, new String(first, 208, 4, StandardCharsets.US_ASCII));
      assertEquals(1, f.scalar(FIXTURE_INBOX_COUNT_SQL));
      byte[] replay = service.process(request);
      assertEquals(
          FIXTURE_RESULT_IDEMPOTENT_SUCCESS, new String(replay, 208, 4, StandardCharsets.US_ASCII));
      assertEquals(1, f.scalar(FIXTURE_INBOX_COUNT_SQL));
      assertEquals(
          1, f.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
      var fixed = Clock.fixed(NOW, ZoneOffset.UTC);
      assertThrows(
          NullPointerException.class,
          () -> LogQueryApplicationAssembly.create(null, f.fingerprints, f.snapshots, fixed));
      assertThrows(
          NullPointerException.class,
          () -> LogQueryApplicationAssembly.create(f.source, null, f.snapshots, fixed));
      assertThrows(
          NullPointerException.class,
          () -> LogQueryApplicationAssembly.create(f.source, f.fingerprints, null, fixed));
      assertThrows(
          NullPointerException.class,
          () -> LogQueryApplicationAssembly.create(f.source, f.fingerprints, f.snapshots, null));
    }
  }

  @Test
  void adm076ProductionLogRouteReceivesThroughBroker(@TempDir Path brokerRoot) throws Exception {
    org.apache.activemq.artemis.core.config.Configuration configuration;
    try (var file =
        java.nio.file.Files.newInputStream(Path.of(System.getProperty("broker.template")))) {
      configuration =
          new org.apache.activemq.artemis.core.deployers.impl.FileConfigurationParser()
              .parseMainConfig(file);
    }
    configuration
        .setPagingDirectory(brokerRoot.resolve("paging").toString())
        .setBindingsDirectory(brokerRoot.resolve("bindings").toString())
        .setJournalDirectory(brokerRoot.resolve("journal").toString())
        .setLargeMessagesDirectory(brokerRoot.resolve("large").toString())
        .setSecurityEnabled(false)
        .clearAcceptorConfigurations()
        .addAcceptorConfiguration("component", FIXTURE_IN_VM_BROKER_URL);
    var broker =
        new org.apache.activemq.artemis.core.server.embedded.EmbeddedActiveMQ()
            .setConfiguration(configuration)
            .start();
    try (var f = new LogApplicationFixture(database);
        var contexts = new AuthContextCodec("test", new byte[32], null, null);
        var factory =
            new org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory(
                FIXTURE_IN_VM_BROKER_URL);
        var producer = factory.createContext(jakarta.jms.JMSContext.AUTO_ACKNOWLEDGE);
        var observer = factory.createContext(jakarta.jms.JMSContext.AUTO_ACKNOWLEDGE);
        var replies =
            observer.createConsumer(
                new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
                    dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REPLY_WEB
                        .fullyQualifiedQueue()))) {
      seed(f);
      var request = input(null, MESSAGE, 1);
      var queue =
          new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
              dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REQUEST
                  .fullyQualifiedQueue());
      var terminal = new java.util.concurrent.atomic.AtomicInteger();
      try (var runtime =
          dev.codex.schubert.nk.api.dispatch.ApiLogPathApplicationRuntime.startWithLoginAndLog(
              () -> factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED),
              () -> factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED),
              f.source,
              f.fingerprints,
              contexts,
              f.snapshots,
              ignored -> {
                throw new AssertionError("Game route is outside this Log PT");
              },
              Clock.fixed(NOW, ZoneOffset.UTC),
              ignored -> terminal.incrementAndGet())) {
        assertTrue(runtime.ready());
        send(producer, queue, request);
        byte[] first = brokerBody(replies.receive(5_000));
        assertEquals(FIXTURE_RESULT_SUCCESS, new String(first, 208, 4, StandardCharsets.US_ASCII));
        send(producer, queue, request);
        byte[] replay = brokerBody(replies.receive(5_000));
        assertEquals(
            FIXTURE_RESULT_IDEMPOTENT_SUCCESS,
            new String(replay, 208, 4, StandardCharsets.US_ASCII));
        assertEquals(1, f.scalar(FIXTURE_INBOX_COUNT_SQL));
        assertEquals(
            1, f.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
        assertEquals(0, terminal.get());
      }
    } finally {
      broker.stop();
    }
  }

  static LogQueryApplicationService service(LogApplicationFixture f) throws Exception {
    return new LogQueryApplicationService(
        f.source,
        new AuthenticationContextVerifier(new ContextHash()),
        new LogQueryRepository(),
        f.inbox,
        new LogReplayService(f.snapshots),
        Clock.fixed(NOW, ZoneOffset.UTC),
        () -> new UUID(101, f.ids.incrementAndGet()));
  }

  static void seed(LogApplicationFixture f) throws Exception {
    seed(f, 1);
  }

  static void seed(LogApplicationFixture f, int count) throws Exception {
    f.seed();
    try (var c = f.db.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_logs restart identity");
    }
    f.sql(
        "insert into"
            + " schubert.app_logs(logged_at,service,category,level,action,message,request_id,message_id,correlation_id,http_method,request_uri,status_code,duration_ms,remote_address,details)"
            + " select '2026-09-08T00:00:00Z'::timestamptz,'API','ACTION','INFO','TEST','message"
            + " '||i,'00000000-0000-0000-0000-000000000001'::uuid,'00000000-0000-0000-0000-000000000002'::uuid,'00000000-0000-0000-0000-000000000003'::uuid,'GET','/safe',200,0,'2001:db8::1'::inet,'{\"count\":"
            + " 1}'::jsonb from generate_series(1,"
            + count
            + ")n(i)");
  }

  static WireMessage<FixedPayload> input(String keyword, UUID id, int context) {
    return input(keyword, id, context, 1);
  }

  static WireMessage<FixedPayload> input(String keyword, UUID id, int context, int page) {
    byte[] data =
        LogVectors.data(Arrays.asList(keyword, null, "TEST", null, null, null, null), page);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("LGSREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of(LogApplicationFixture.context(context))),
            256,
            656,
            0,
            0,
            912,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }

  static byte[] expected(WireMessage<FixedPayload> message, String code, int response, int count) {
    byte[] expected =
        LogVectors.wire(
            message.header().messageId(),
            new UUID(101, response),
            NOW,
            code,
            count,
            count,
            1,
            true);
    put(expected, 113, message.header().authenticationContext().orElseThrow().wireValue());
    // SQL order is logged_at DESC,id DESC. Fixture time is equal, so reverse IDs/messages.
    if (code.equals(FIXTURE_RESULT_SUCCESS) || code.equals(FIXTURE_RESULT_IDEMPOTENT_SUCCESS))
      for (int i = 0; i < count; i++) {
        int offset = 304 + i * 2088;
        put(expected, offset, String.format(Locale.ROOT, "%012d", count - i));
        Arrays.fill(expected, offset + 117, offset + 629, (byte) 32);
        put(expected, offset + 117, "message " + (count - i));
      }
    return expected;
  }

  static void send(
      jakarta.jms.JMSContext context,
      org.apache.activemq.artemis.jms.client.ActiveMQQueue queue,
      WireMessage<FixedPayload> input)
      throws Exception {
    byte[] data = input.payload().copyData();
    byte[] wire = new byte[256 + data.length];
    Arrays.fill(wire, (byte) 32);
    put(wire, 0, "SCHBNK01001LGSREQ01001QS");
    put(wire, 24, input.header().messageId().toString());
    put(wire, 60, input.header().messageId().toString());
    put(wire, 96, LogVectors.time(NOW));
    put(wire, 113, input.header().authenticationContext().orElseThrow().wireValue());
    put(
        wire,
        177,
        String.format(Locale.ROOT, "0256%06d000000000000%09d", data.length, wire.length));
    System.arraycopy(data, 0, wire, 256, data.length);
    var message = context.createBytesMessage();
    message.writeBytes(wire);
    message.setJMSCorrelationID(input.header().messageId().toString());
    message.setJMSReplyTo(
        new org.apache.activemq.artemis.jms.client.ActiveMQQueue(
            dev.codex.schubert.nk.protocol.transport.BrokerTopology.SYNC_REPLY_WEB
                .fullyQualifiedQueue()));
    message.setStringProperty("NKMessageID", input.header().messageId().toString());
    message.setStringProperty("NKLayoutID", "LGSREQ01");
    message.setStringProperty("NKProtocolVersion", "001");
    context
        .createProducer()
        .setDeliveryMode(jakarta.jms.DeliveryMode.PERSISTENT)
        .setTimeToLive(5000)
        .send(queue, message);
    Arrays.fill(data, (byte) 0);
    Arrays.fill(wire, (byte) 0);
  }

  static InboxCompletion completion(LogApplicationFixture f) throws SQLException {
    try (var c = f.db.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select"
                    + " processing_state,response_layout_id,response_version,response_body_encrypted,response_key_version,completed_at"
                    + " from schubert.request_inbox")) {
      assertTrue(r.next());
      var completion =
          new InboxCompletion(
              InboxCompletionState.valueOf(r.getString(1)),
              InboxResultReference.none(),
              r.getString(2),
              r.getString(3),
              Optional.of(new EncryptedResponseSnapshot(r.getString(5), r.getBytes(4))),
              r.getObject(6, java.time.OffsetDateTime.class).toInstant());
      assertFalse(r.next());
      return completion;
    }
  }
}
