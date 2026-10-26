package dev.codex.schubert.nk.api.application.admin;

import static dev.codex.schubert.nk.api.application.admin.UserMutationRequestTest.put;
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
import dev.codex.schubert.nk.api.persistence.UserQueryRepository;
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

/** Actual PG/Flyway and independent full wire/SQL assertions, PG-D-089/PT-ADM-048..054. */
class UserQueryApplicationServiceTest {
  // Independent wire/SQL/fault fixture literals; do not derive from Production results.
  private static final String SEARCH_LAYOUT = "USRREQ01";
  private static final String SUCCESS_RESULT = "0000";
  private static final String SYSTEM_ERROR_RESULT = "0200";
  private static final String FORBIDDEN_RESULT = "0103";
  private static final String NO_FAULT = "none";
  private static final String DATABASE_FAULT_POINT = "database";
  private static final String INBOX_COUNT_SQL = "select count(*) from schubert.request_inbox";
  private static final int FIRST_AUTH_COMMIT = 1;
  private static final int QUERY_RESULT_COMMIT = 2;
  private static final int REPLAY_AUTH_COMMIT = 3;
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static final Instant NOW = UserQueryRequestTest.NOW;
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
  void adm048QueriesCommitFrozenResponsesAndFullRetention() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
      for (boolean detail : List.of(false, true)) {
        seed(f);
        var service = service(f);
        var message = input(detail, 3, null, MESSAGE, 1);
        assertArrayEquals(
            expected(message, SUCCESS_RESULT, 2, detail ? 0 : 3, detail ? 3 : 0),
            service.process(message));
        assertEquals(2, f.commits.get());
        assertEquals(0, f.live.get());
        assertEquals(1, f.scalar(INBOX_COUNT_SQL));
        assertEquals(
            1,
            f.scalar(
                "select count(*) from schubert.request_inbox where owner_user_id=1 and"
                    + " operation_token is null and result_ref_type='NONE' and"
                    + " processing_state='COMPLETED' and expires_at=completed_at+interval '24"
                    + " hours'"));
        assertEquals(0, f.scalar("select sum(version) from schubert.app_users"));
        byte[] independent =
            UserQueryRequestTest.check(
                UserQueryRequest.decode(message),
                UserQueryRequestTest.ADMIN,
                detail ? "UDTREQ01" : SEARCH_LAYOUT,
                detail ? List.of("3") : Arrays.asList(null, null, null, "1", "50"));
        assertEquals(
            HexFormat.of().formatHex(independent),
            f.text("select request_fingerprint_hmac from schubert.request_inbox"));
        Arrays.fill(independent, (byte) 0);
        var saved = completion(f);
        assertArrayEquals(
            expected(message, SUCCESS_RESULT, 1, detail ? 0 : 3, detail ? 3 : 0),
            UserMutationReplayServiceTest.decrypt(saved, MESSAGE, 1));
        var metadata = f.inboxMetadata();
        f.sql(
            "update schubert.app_users set username='Changed',username_key='changed',version=99"
                + " where id=3");
        assertArrayEquals(
            expected(message, SYSTEM_ERROR_RESULT, 3, detail ? 0 : 3, detail ? 3 : 0),
            service.process(message));
        assertEquals(metadata, f.inboxMetadata());
        assertEquals(4, f.commits.get());
        assertEquals(
            1, f.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
      }
      seed(f);
      var service = service(f);
      var absent = input(true, 99, null, MESSAGE, 1);
      assertArrayEquals(expected(absent, "0104", 2, 0, 0), service.process(absent));
      f.sql(
          "insert into"
              + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
              + " values(99,'u99','u99','synthetic-unusable','USER','ACTIVE','2026-09-08T00:01:00Z','2026-09-08T00:01:00Z','2026-09-08T00:01:00Z')");
      assertArrayEquals(expected(absent, "0104", 3, 0, 0), service.process(absent));
      seed(f);
      var capacity = input(false, 0, null, MESSAGE, 1);
      var fault = new UserCommandFaults();
      fault.sqlPart = "with projected as";
      fault.columns.put("total", 49999951L);
      f.sqlFault = fault;
      assertArrayEquals(expected(capacity, "9001", 2, 0, 0), service(f).process(capacity));
      f.sqlFault = null;
      assertArrayEquals(expected(capacity, "9001", 3, 0, 0), service(f).process(capacity));
      assertEquals(
          1,
          f.scalar(
              "select count(*) from schubert.request_inbox where processing_state='ERROR' and"
                  + " expires_at=completed_at+interval '24 hours'"));
    }
  }

  @Test
  void adm049BothStagesRecheckIdentityRoleAndAuditDenials() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
      for (int context : new int[] {3, 99}) {
        seed(f);
        var request = input(false, 0, null, MESSAGE, context);
        String code = context == 3 ? FORBIDDEN_RESULT : "0102";
        assertArrayEquals(expected(request, code, 1, 0, 0), service(f).process(request));
        assertEquals(0, f.scalar(INBOX_COUNT_SQL));
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
              if (f.commits.get() == FIRST_AUTH_COMMIT)
                try {
                  f.sql(change);
                } catch (SQLException failure) {
                  throw new AssertionError(failure);
                }
            };
        var request = input(false, 0, null, MESSAGE, 1);
        String code = change.contains("role='USER'") ? FORBIDDEN_RESULT : "0102";
        assertArrayEquals(expected(request, code, 1, 0, 0), service(f).process(request));
        assertEquals(0, f.scalar(INBOX_COUNT_SQL));
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
              if (f.commits.get() == FIRST_AUTH_COMMIT)
                try {
                  if (missing) f.session(1, 99);
                  else f.sql("update schubert.app_users set role='ADMIN' where id=1");
                } catch (Exception failure) {
                  throw new AssertionError(failure);
                }
            };
        var request = input(false, 0, null, MESSAGE, missing ? 99 : 1);
        String code = missing ? "0102" : FORBIDDEN_RESULT;
        assertArrayEquals(expected(request, code, 1, 0, 0), service(f).process(request));
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
      service.process(input(false, 0, null, MESSAGE, 1));
      assertThrows(
          PermanentProtocolException.class,
          () -> service.process(input(false, 0, "different", MESSAGE, 1)));
      assertEquals(1, f.scalar(INBOX_COUNT_SQL));
      assertEquals(
          1, f.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
    }
  }

  @Test
  void adm054PublicBoundariesAndStageOwnershipAreExplicit() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
      seed(f);
      var auth = new AuthenticationContextVerifier(new ContextHash());
      var query = new UserQueryRepository();
      var replay = new UserQueryReplayService(f.snapshots);
      var clock = Clock.fixed(NOW, ZoneOffset.UTC);
      assertThrows(
          NullPointerException.class,
          () -> new UserQueryApplicationService(null, auth, query, f.inbox, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new UserQueryApplicationService(f.source, null, query, f.inbox, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new UserQueryApplicationService(f.source, auth, null, f.inbox, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new UserQueryApplicationService(f.source, auth, query, null, replay, clock));
      assertThrows(
          NullPointerException.class,
          () -> new UserQueryApplicationService(f.source, auth, query, f.inbox, null, clock));
      assertThrows(
          NullPointerException.class,
          () -> new UserQueryApplicationService(f.source, auth, query, f.inbox, replay, null));
      assertThrows(
          NullPointerException.class,
          () ->
              new UserQueryApplicationService(f.source, auth, query, f.inbox, replay, clock, null));
      var service = service(f);
      assertThrows(NullPointerException.class, () -> service.process(null));
      assertThrows(
          PermanentProtocolException.class,
          () ->
              service.process(
                  UserApplicationFixture.input(
                      "USTREQ01", 3, 0, false, MESSAGE, new UUID(110, 2), 1)));
      assertEquals(0, f.commits.get());
      assertEquals(0, f.live.get());
      var tracked =
          new UserQueryApplicationService(
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
      var request = input(false, 0, null, MESSAGE, 1);
      assertArrayEquals(expected(request, SUCCESS_RESULT, 2, 3, 0), tracked.process(request));
      seed(f);
      byte[] random =
          UserApplicationAssembly.queries(f.source, f.fingerprints, f.snapshots, clock)
              .process(request);
      // PT-ADM-ASSEMBLY-001: literal response/SQL stage oracle remains independent below.
      for (var missing :
          List.<org.junit.jupiter.api.function.Executable>of(
              () -> UserApplicationAssembly.queries(null, f.fingerprints, f.snapshots, clock),
              () -> UserApplicationAssembly.queries(f.source, null, f.snapshots, clock),
              () -> UserApplicationAssembly.queries(f.source, f.fingerprints, null, clock),
              () -> UserApplicationAssembly.queries(f.source, f.fingerprints, f.snapshots, null)))
        assertThrows(NullPointerException.class, missing);
      UUID response = UUID.fromString(new String(random, 24, 36, StandardCharsets.US_ASCII));
      assertEquals(4, response.version());
      byte[] expected = expected(request, SUCCESS_RESULT, 2, 3, 0);
      put(expected, 24, response.toString());
      assertArrayEquals(expected, random);
      seed(f);
      f.sql("update schubert.app_users set username=E'u3\\n' where id=3");
      var denied = input(false, 0, "synthetic-private-search", MESSAGE, 3);
      assertArrayEquals(expected(denied, FORBIDDEN_RESULT, 1, 0, 0), service(f).process(denied));
      assertEquals("u3 ", f.text("select actor_username from schubert.app_logs"));
      assertEquals("WARN", f.text("select level from schubert.app_logs"));
      assertEquals("SECURITY", f.text("select category from schubert.app_logs"));
      String details = f.text("select details::text from schubert.app_logs");
      var json = com.google.gson.JsonParser.parseString(details).getAsJsonObject();
      assertEquals(
          Set.of("layout", "reason", "targetType", "outcome", "actorRole", "step"), json.keySet());
      assertFalse(details.contains("synthetic-private-search"));
      // YKT-060: denial audit retains independent UI236 route/type, not only a request ID.
      assertEquals(SEARCH_LAYOUT, json.get("layout").getAsString());
      assertEquals("USER", json.get("targetType").getAsString());
      assertEquals("USER", json.get("actorRole").getAsString());
      assertTrue(details.getBytes(StandardCharsets.UTF_8).length <= 1024);
    }
  }

  @Test
  void adm050DatabaseCryptoAndResourceFailuresRollbackSafely() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
      var request = input(false, 0, null, MESSAGE, 1);
      for (boolean finalStage : List.of(false, true))
        for (String fault :
            List.of("open", "null", "setAutoCommit", "setReadOnly", "commit", "close")) {
          seed(f);
          if (finalStage)
            f.afterCommit =
                () -> {
                  if (f.commits.get() == FIRST_AUTH_COMMIT) f.connectionFault = fault;
                };
          else f.connectionFault = fault;
          deny(() -> service(f).process(request));
          assertEquals(0, f.live.get());
          f.connectionFault = NO_FAULT;
          f.afterCommit = () -> {};
          assertEquals(0, f.inboxCount());
        }
      for (String sql :
          List.of(
              "select s.id",
              "select correlation_id",
              "with projected as",
              "for update of u",
              "update schubert.auth_sessions",
              "insert into schubert.request_inbox",
              "update schubert.request_inbox"))
        for (String failure : List.of("prepareStatement", "statementClose")) {
          seed(f);
          var fault = new UserCommandFaults();
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
        var fault = new UserCommandFaults();
        fault.sqlPart = "update schubert.request_inbox";
        fault.updateCount = 0;
        fault.fault = close ? "statementClose" : NO_FAULT;
        f.sqlFault = fault;
        deny(() -> service(f).process(request));
        assertEquals(0, f.inboxCount());
        f.sqlFault = null;
      }
      seed(f);
      f.rollbackFails = true;
      var fault = new UserCommandFaults();
      fault.sqlPart = "with projected as";
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
          var auditFault = new UserCommandFaults();
          auditFault.sqlPart = "insert into schubert.app_logs";
          auditFault.fault = failure;
          if (failure.equals("count")) auditFault.updateCount = 0;
          f.sqlFault = auditFault;
          deny(() -> service(f).process(input(false, 0, null, MESSAGE, context)));
          assertEquals(0, f.inboxCount());
          assertEquals(0, f.scalar("select count(*) from schubert.app_logs"));
          f.sqlFault = null;
        }
      for (int idFailure : new int[] {1, 2}) {
        seed(f);
        var auth = new AuthenticationContextVerifier(new ContextHash());
        var service =
            new UserQueryApplicationService(
                f.source,
                auth,
                new UserQueryRepository(),
                f.inbox,
                new UserQueryReplayService(f.snapshots),
                Clock.fixed(NOW, ZoneOffset.UTC),
                () -> f.ids.incrementAndGet() == idFailure ? null : new UUID(101, 99));
        deny(() -> service.process(request));
        assertEquals(idFailure == 1 ? 0 : 1, f.inboxCount());
      }
      for (int stage : new int[] {1, 2, 3, 4, 5, 6}) {
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
            new UserQueryApplicationService(
                f.source,
                new AuthenticationContextVerifier(new ContextHash()),
                new UserQueryRepository(),
                f.inbox,
                new UserQueryReplayService(f.snapshots),
                clock,
                () -> new UUID(101, f.ids.incrementAndGet()));
        deny(() -> service.process(request));
        assertEquals(stage == 6 ? 1 : 0, f.inboxCount());
        assertEquals(0, f.live.get());
      }
      seed(f);
      f.afterCommit =
          () -> {
            if (f.commits.get() == QUERY_RESULT_COMMIT) f.connectionFault = "close";
          };
      deny(() -> service(f).process(request));
      assertEquals(1, f.inboxCount());
      f.afterCommit = () -> {};
      f.connectionFault = NO_FAULT;
      assertArrayEquals(
          expected(request, SYSTEM_ERROR_RESULT, 2, 3, 0), service(f).process(request));
      seed(f);
      f.fingerprints.close();
      deny(() -> service(f).process(request));
      assertEquals(0, f.inboxCount());
    }
    try (var f = new UserApplicationFixture(database)) {
      seed(f);
      f.snapshots.close();
      deny(() -> service(f).process(input(false, 0, null, MESSAGE, 1)));
      assertEquals(0, f.inboxCount());
    }
  }

  @Test
  void adm051ConcurrentRequestsReplayOnlyTheWinningSnapshot() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
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
                      var request =
                          input(false, 0, null, distinct ? new UUID(110, n + 1) : MESSAGE, 1);
                      byte[] actual = service.process(request);
                      String code = new String(actual, 208, 4, StandardCharsets.US_ASCII);
                      if (code.equals(SUCCESS_RESULT)) initial.incrementAndGet();
                      else {
                        assertEquals(SYSTEM_ERROR_RESULT, code);
                        repeated.incrementAndGet();
                      }
                      byte[] expected = expected(request, code, 1, 3, 0);
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
                              false,
                              0,
                              owner ? null : n % 2 == 0 ? null : "u",
                              MESSAGE,
                              owner ? n % 2 + 1 : 1);
                      try {
                        byte[] actual = service.process(request);
                        assertTrue(
                            List.of(SUCCESS_RESULT, SYSTEM_ERROR_RESULT)
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
      var request = input(false, 0, null, MESSAGE, 1);
      service(f).process(request);
      f.sql(
          "update schubert.request_inbox set"
              + " processing_state='PROCESSING',completed_at=null,result_ref_type=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null");
      deny(() -> service(f).process(request));
      assertEquals(1, f.inboxCount());
    }
  }

  @Test
  void adm052SavedRowsCannotDisappearOrChangeBetweenStages() throws Exception {
    try (var f = new UserApplicationFixture(database)) {
      var request = input(false, 0, null, MESSAGE, 1);
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
              if (f.commits.get() == REPLAY_AUTH_COMMIT)
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
  void adm053BrokerFailuresReplayOneCommittedQueryResult() throws Exception {
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
        .addAcceptorConfiguration("component", "vm://0");
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
            new org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(jakarta.jms.JMSContext.AUTO_ACKNOWLEDGE);
        var receiver = factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED);
        var observer = factory.createContext(jakarta.jms.JMSContext.AUTO_ACKNOWLEDGE);
        var requests = receiver.createConsumer(requestQueue);
        var replies = observer.createConsumer(replyQueue);
        var dlq = observer.createConsumer(dlqQueue)) {
      for (String point : List.of("createProducer", "commit", DATABASE_FAULT_POINT))
        try (var f = new UserApplicationFixture(database)) {
          seed(f);
          var request = input(false, 0, null, MESSAGE, 1);
          var listener =
              new dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListener(
                  service(f), Clock.fixed(NOW, ZoneOffset.UTC));
          if (point.equals(DATABASE_FAULT_POINT)) f.connectionFault = "open";
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
                        return UserApplicationFixture.invoke(receiver, m, a);
                      });
          UserMutationApplicationServiceTest.send(producer, requestQueue, request);
          var first = requests.receive(5000);
          assertNotNull(first);
          if (point.equals(DATABASE_FAULT_POINT)) deny(() -> listener.onMessage(failing, first));
          else
            assertThrows(
                jakarta.jms.JMSRuntimeException.class, () -> listener.onMessage(failing, first));
          assertNull(replies.receive(250));
          assertEquals(point.equals(DATABASE_FAULT_POINT) ? 0 : 1, f.inboxCount());
          f.connectionFault = NO_FAULT;
          var retry = requests.receive(5000);
          assertNotNull(retry);
          assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, retry);
          assertArrayEquals(
              expected(
                  request,
                  point.equals(DATABASE_FAULT_POINT) ? SUCCESS_RESULT : SYSTEM_ERROR_RESULT,
                  f.ids.get(),
                  3,
                  0),
              brokerBody(replies.receive(5000)));
          var frozen = f.inboxMetadata();
          f.sql(
              "update schubert.app_users set username='Changed',username_key='changed' where id=3");
          UserMutationApplicationServiceTest.send(producer, requestQueue, request);
          var duplicate = requests.receive(5000);
          assertNotNull(duplicate);
          listener.onMessage(receiver, duplicate);
          assertArrayEquals(
              expected(request, SYSTEM_ERROR_RESULT, f.ids.get(), 3, 0),
              brokerBody(replies.receive(5000)));
          assertEquals(frozen, f.inboxMetadata());
          UserMutationApplicationServiceTest.send(
              producer, requestQueue, input(false, 0, "changed", MESSAGE, 1));
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
    assertEquals(808, message.getBodyLength());
    byte[] body = new byte[808];
    assertEquals(808, message.readBytes(body));
    assertEquals(
        new String(body, 60, 36, StandardCharsets.US_ASCII), message.getJMSCorrelationID());
    assertEquals(
        new String(body, 24, 36, StandardCharsets.US_ASCII),
        message.getStringProperty("NKMessageID"));
    assertEquals("USRRSP01", message.getStringProperty("NKLayoutID"));
    assertEquals("001", message.getStringProperty("NKProtocolVersion"));
    return body;
  }

  static void deny(org.junit.jupiter.api.function.Executable action) {
    var error = assertThrows(TemporaryInfrastructureException.class, action);
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
    assertEquals("request transaction is unavailable", error.getMessage());
  }

  static UserQueryApplicationService service(UserApplicationFixture f) throws Exception {
    return new UserQueryApplicationService(
        f.source,
        new AuthenticationContextVerifier(new ContextHash()),
        new UserQueryRepository(),
        f.inbox,
        new UserQueryReplayService(f.snapshots),
        Clock.fixed(NOW, ZoneOffset.UTC),
        () -> new UUID(101, f.ids.incrementAndGet()));
  }

  static void seed(UserApplicationFixture f) throws Exception {
    f.seed();
    f.sql(
        "update schubert.app_users set"
            + " password_changed_at='2026-09-08T00:01:00Z',created_at='2026-09-08T00:01:00Z',updated_at='2026-09-08T00:01:00Z'");
  }

  static WireMessage<FixedPayload> input(
      boolean detail, long target, String prefix, UUID id, int context) {
    byte[] data =
        detail
            ? String.format(Locale.ROOT, "%012d", target).getBytes(StandardCharsets.US_ASCII)
            : UserQueryRequestTest.listData(prefix, null, null, 1);
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId(detail ? "UDTREQ01" : SEARCH_LAYOUT),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            id,
            id,
            NOW,
            Optional.of(AuthenticationContext.of(UserApplicationFixture.context(context))),
            256,
            data.length,
            0,
            0,
            256 + data.length,
            Optional.empty());
    return new WireMessage<>(header, new FixedPayload(data, 0, List.of()));
  }

  static byte[] expected(
      WireMessage<FixedPayload> message, String code, int response, int count, long target) {
    byte[] expected =
        UserQueryWireOracle.wire(
            message.header().layoutId().value(),
            message.header().messageId(),
            new UUID(101, response),
            NOW,
            UserQueryRequestTest.NOW,
            code,
            count,
            count,
            1,
            target,
            false);
    put(expected, 113, message.header().authenticationContext().orElseThrow().wireValue());
    if (code.equals(SUCCESS_RESULT) || code.equals(SYSTEM_ERROR_RESULT)) {
      if (message.header().layoutId().value().equals(SEARCH_LAYOUT)) {
        for (int i = 0; i < Math.min(2, count); i++) put(expected, 304 + i * 168 + 76, "ADMIN");
      } else put(expected, 430, "001");
    }
    return expected;
  }

  static InboxCompletion completion(UserApplicationFixture f) throws SQLException {
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
