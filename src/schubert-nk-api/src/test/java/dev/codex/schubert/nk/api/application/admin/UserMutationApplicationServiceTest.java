package dev.codex.schubert.nk.api.application.admin;

import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.MESSAGE;
import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.NOW;
import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.PASSWORD;
import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.TOKEN;
import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.context;
import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.input;
import static dev.codex.schubert.nk.api.application.admin.UserApplicationFixture.reply;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** Real User/Inbox/audit/session transactions with independent wire/SQL. PT-ADM-033..039. */
class UserMutationApplicationServiceTest {
  private static final String FIXTURE_UCRREQ01_841A676A = "UCRREQ01";
  private static final String FIXTURE_USTREQ01_D6E6CD9B = "USTREQ01";
  private static final String FIXTURE_URLREQ01_27B8B3D0 = "URLREQ01";
  private static final String FIXTURE_UPWREQ01_256BADE0 = "UPWREQ01";
  private static final String FIXTURE_ULKREQ01_CC99AF15 = "ULKREQ01";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_0103_09B05C76 = "0103";
  private static final String FIXTURE_0105_6F9AB3E4 = "0105";
  private static final String FIXTURE_DUPLICATE_E75B7650 = "duplicate";
  private static final String FIXTURE_PASSWORD_FF2BEA10 = "password";
  private static final String FIXTURE_CAPACITY_84594495 = "capacity";
  private static final String FIXTURE_NOOP_A48838A5 = "noop";
  private static final String FIXTURE_DATABASE_21C67C24 = "database";
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
  void adm033AllMutationsCommitOnceAndReplayFrozenVersions() throws Exception {
    for (String layout :
        List.of(
            FIXTURE_UCRREQ01_841A676A,
            FIXTURE_USTREQ01_D6E6CD9B,
            FIXTURE_URLREQ01_27B8B3D0,
            FIXTURE_UPWREQ01_256BADE0,
            FIXTURE_ULKREQ01_CC99AF15))
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        if (layout.equals(FIXTURE_ULKREQ01_CC99AF15))
          h.sql(
              "update schubert.app_users set locked_until='2026-09-08T00:02:00Z',failed_count=2,failure_window_started_at='2026-09-08T00:00:00Z' where id=3");
        var request = input(layout, 3, 0, true, MESSAGE, TOKEN, 1);
        long target = layout.equals(FIXTURE_UCRREQ01_841A676A) ? 4 : 3;
        long version = layout.equals(FIXTURE_UCRREQ01_841A676A) ? 0 : 1;
        reply(h.service.process(request), request, FIXTURE_0000_876EEFE0, target, version, 2);
        assertEquals(1, h.inboxCount());
        assertEquals(version, h.version(target));
        assertEquals(1, h.commits.get());
        assertEquals(0, h.live.get());
        assertEquals(
            604800,
            h.scalar(
                "select extract(epoch from (expires_at-completed_at))::bigint from schubert.request_inbox"));
        assertEquals("COMPLETED", h.text("select processing_state from schubert.request_inbox"));
        assertEquals("USER", h.text("select result_ref_type from schubert.request_inbox"));
        assertEquals(
            independentFingerprint(layout),
            h.text("select request_fingerprint_hmac from schubert.request_inbox"));
        var frozen = h.inboxMetadata();
        reply(h.service.process(request), request, FIXTURE_0200_FC9DB3AC, target, version, 3);
        var retry = input(layout, 3, 0, true, new UUID(90, 3), TOKEN, 1);
        reply(h.service.process(retry), retry, FIXTURE_0200_FC9DB3AC, target, version, 4);
        assertEquals(frozen, h.inboxMetadata());
        assertEquals(version, h.version(target));
        assertEquals(
            2, h.scalar("select count(*) from schubert.app_logs where action='INBOX_REPLAYED'"));
        if (List.of(FIXTURE_USTREQ01_D6E6CD9B, FIXTURE_URLREQ01_27B8B3D0, FIXTURE_UPWREQ01_256BADE0)
            .contains(layout))
          assertEquals(
              1,
              h.scalar("select count(*) from schubert.auth_sessions where user_id=3 and revoked"));
        if (layout.equals(FIXTURE_UPWREQ01_256BADE0) || layout.equals(FIXTURE_UCRREQ01_841A676A)) {
          String hash = h.text("select password_hash from schubert.app_users where id=" + target);
          UserCommandServiceTest.independentHash(hash, PASSWORD);
        }
        // A real later independent command advances DB; replay must retain the first version.
        var later =
            input(
                FIXTURE_USTREQ01_D6E6CD9B,
                target,
                version,
                true,
                new UUID(90, 4),
                new UUID(90, 5),
                1);
        reply(h.service.process(later), later, FIXTURE_0000_876EEFE0, target, version + 1, 6);
        reply(h.service.process(retry), retry, FIXTURE_0200_FC9DB3AC, target, version, 7);
        assertEquals(version + 1, h.version(target));
        assertEquals(2, h.inboxCount());
        assertEquals(
            0,
            h.scalar(
                "select count(*) from schubert.app_logs where details::text like '%Synthetic-%' or details::text like '%pbkdf2%'"));
      }
  }

  @Test
  void adm034CurrentAuthenticationAndIdentityDenialsAreAudited() throws Exception {
    try (var h = new UserApplicationFixture(database)) {
      for (String mutation :
          List.of(
              "role='USER'",
              "status='DISABLED'",
              "session-revoked",
              "session-expired",
              "unknown")) {
        h.seed();
        if (mutation.startsWith("session-"))
          h.sql(
              "update schubert.auth_sessions set "
                  + (mutation.equals("session-revoked")
                      ? "revoked=true,revoked_at='2026-09-08T00:01:00Z',revoke_reason='ADMIN'"
                      : "expires_at='2026-09-08T00:01:00Z'")
                  + " where user_id=1");
        else if (!mutation.equals("unknown"))
          h.sql("update schubert.app_users set " + mutation + " where id=1");
        var request =
            input(
                FIXTURE_USTREQ01_D6E6CD9B,
                3,
                0,
                true,
                MESSAGE,
                TOKEN,
                mutation.equals("unknown") ? 99 : 1);
        String code = mutation.equals("role='USER'") ? FIXTURE_0103_09B05C76 : "0102";
        reply(h.service.process(request), request, code, 0, 0, 1);
        assertEquals(0, h.inboxCount());
        assertEquals(0, h.version(3));
        assertEquals(
            1,
            h.scalar(
                "select count(*) from schubert.app_logs where action='AUTHORIZATION_DENIED' and category='SECURITY'"));
        // YKT-060: fixed request layout/type survive every denied admission path.
        assertEquals(
            FIXTURE_USTREQ01_D6E6CD9B, h.text("select details->>'layout' from schubert.app_logs"));
        assertEquals("USER", h.text("select details->>'targetType' from schubert.app_logs"));
        assertEquals(
            code.equals(FIXTURE_0103_09B05C76) ? 1 : 0,
            h.scalar("select count(actor_user_id) from schubert.app_logs"));
        assertEquals(
            code.equals(FIXTURE_0103_09B05C76) ? "WARN" : "INFO",
            h.text("select level from schubert.app_logs"));
      }
      h.seed();
      var first = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1);
      h.service.process(first);
      var stored = h.inboxMetadata();
      // Same token, changed target/version/value; no alias row or second command.
      for (var request :
          List.of(
              input(FIXTURE_USTREQ01_D6E6CD9B, 2, 0, true, new UUID(90, 6), TOKEN, 1),
              input(FIXTURE_USTREQ01_D6E6CD9B, 3, 1, true, new UUID(90, 7), TOKEN, 1),
              input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, false, new UUID(90, 8), TOKEN, 1))) {
        byte[] actual = h.service.process(request);
        reply(actual, request, FIXTURE_0105_6F9AB3E4, 0, 0, h.ids.get());
        assertEquals(stored, h.inboxMetadata());
        assertEquals(1, h.version(3));
      }
      for (var request :
          List.of(
              input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, false, MESSAGE, TOKEN, 1),
              input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 2))) {
        var failure =
            assertThrows(PermanentProtocolException.class, () -> h.service.process(request));
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertEquals(stored, h.inboxMetadata());
      }
      assertEquals(
          2, h.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
      h.sql("update schubert.app_users set role='USER' where id=1");
      byte[] denied = h.service.process(first);
      reply(denied, first, FIXTURE_0103_09B05C76, 0, 0, h.ids.get());
      assertEquals(stored, h.inboxMetadata());
    }
  }

  @Test
  void adm035SqlCryptoAuditAndTransactionFailuresNeverClaimSuccess() throws Exception {
    for (String fault :
        List.of("open", "null", "setAutoCommit", "setReadOnly", "commit", "close")) {
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        h.connectionFault = fault;
        var request = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1);
        temporary(() -> h.service.process(request));
        boolean committed = fault.equals("close");
        assertEquals(committed ? 1 : 0, h.inboxCount());
        assertEquals(committed ? 1 : 0, h.version(3));
        assertEquals(0, h.live.get());
        h.connectionFault = "none";
        byte[] retry = h.service.process(request);
        reply(
            retry,
            request,
            committed ? FIXTURE_0200_FC9DB3AC : FIXTURE_0000_876EEFE0,
            3,
            1,
            h.ids.get());
        assertEquals(1, h.inboxCount());
        assertEquals(1, h.version(3));
      }
    }
    for (String sqlPart :
        List.of(
            "select user_id",
            "select id from schubert.app_users",
            "select correlation_id",
            "insert into schubert.request_inbox",
            "select id,username",
            "update schubert.app_users",
            "insert into schubert.app_logs",
            "update schubert.request_inbox")) {
      for (String fault : List.of("prepareStatement", "statementClose"))
        try (var h = new UserApplicationFixture(database)) {
          h.seed();
          var failure = new UserCommandFaults();
          failure.sqlPart = sqlPart;
          failure.fault = fault;
          h.sqlFault = failure;
          temporary(
              () ->
                  h.service.process(
                      input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1)));
          assertEquals(0, h.inboxCount());
          assertEquals(0, h.version(3));
          assertEquals(0, h.scalar("select count(*) from schubert.app_logs"));
          assertEquals(0, h.live.get());
        }
    }
    for (boolean suppressed : List.of(false, true))
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        var failure = new UserCommandFaults();
        failure.sqlPart = "update schubert.request_inbox";
        failure.updateCount = 0;
        if (suppressed) failure.fault = "statementClose";
        h.sqlFault = failure;
        temporary(
            () ->
                h.service.process(input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1)));
        assertEquals(0, h.inboxCount());
        assertEquals(0, h.version(3));
      }
    for (String mode :
        List.of(
            "rollback",
            "null-row",
            "unknown-row",
            "crypto",
            "replay-audit",
            "role-audit",
            "session-audit",
            "token-audit",
            "message-audit")) {
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        var request = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1);
        boolean existing = List.of("replay-audit", "token-audit", "message-audit").contains(mode);
        if (existing) h.service.process(request);
        var failure = new UserCommandFaults();
        h.sqlFault = failure;
        switch (mode) {
          case "rollback" -> {
            failure.sqlPart = "update schubert.app_users";
            failure.fault = "executeUpdate";
            h.rollbackFails = true;
          }
          case "null-row" -> failure.columns.put("username", null);
          case "unknown-row" -> failure.columns.put("role", "UNKNOWN");
          case "crypto" -> h.snapshots.close();
          default -> {
            failure.sqlPart = "insert into schubert.app_logs";
            failure.updateCount = 0;
          }
        }
        if (mode.equals("role-audit"))
          h.sql("update schubert.app_users set role='USER' where id=1");
        if (mode.equals("session-audit"))
          h.sql(
              "update schubert.auth_sessions set expires_at='2026-09-08T00:01:00Z' where user_id=1");
        var attempted =
            mode.equals("token-audit")
                ? input(FIXTURE_USTREQ01_D6E6CD9B, 3, 1, true, new UUID(90, 11), TOKEN, 1)
                : mode.equals("message-audit")
                    ? input(FIXTURE_USTREQ01_D6E6CD9B, 3, 1, true, MESSAGE, TOKEN, 1)
                    : request;
        var before = h.inboxMetadata();
        long audit = h.scalar("select count(*) from schubert.app_logs");
        temporary(() -> h.service.process(attempted));
        assertEquals(before, h.inboxMetadata());
        assertEquals(existing ? 1 : 0, h.version(3));
        assertEquals(audit, h.scalar("select count(*) from schubert.app_logs"));
        assertEquals(0, h.live.get());
      }
    }
    for (int failAt : new int[] {1, 2})
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        var calls = new java.util.concurrent.atomic.AtomicInteger();
        h.service =
            h.build(
                java.time.Clock.fixed(NOW, java.time.ZoneOffset.UTC),
                () ->
                    calls.incrementAndGet() == failAt
                        ? null
                        : new UUID(900, h.ids.incrementAndGet()));
        temporary(
            () ->
                h.service.process(input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1)));
        assertEquals(failAt == 2 ? 1 : 0, h.inboxCount());
        assertEquals(failAt == 2 ? 1 : 0, h.version(3));
      }
    for (boolean after : List.of(false, true))
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        var committed = new java.util.concurrent.atomic.AtomicBoolean();
        h.afterCommit = () -> committed.set(true);
        var clock =
            new java.time.Clock() {
              @Override
              public java.time.ZoneId getZone() {
                return java.time.ZoneOffset.UTC;
              }

              @Override
              public java.time.Clock withZone(java.time.ZoneId ignored) {
                return this;
              }

              @Override
              public java.time.Instant instant() {
                if (!after || committed.get())
                  throw new IllegalStateException("synthetic-private-clock");
                return NOW;
              }
            };
        h.service = h.build(clock, () -> new UUID(900, h.ids.incrementAndGet()));
        temporary(
            () ->
                h.service.process(input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1)));
        assertEquals(after ? 1 : 0, h.inboxCount());
        assertEquals(0, h.live.get());
      }
  }

  @Test
  void adm036ConcurrentTokensAndReciprocalAdminsPreserveInvariants() throws Exception {
    for (boolean sameMessage : List.of(false, true))
      try (var h = new UserApplicationFixture(database);
          var workers = java.util.concurrent.Executors.newFixedThreadPool(10)) {
        h.seed();
        var results = new ArrayList<java.util.concurrent.Future<byte[]>>();
        for (int i = 0; i < 100; i++) {
          int n = i;
          results.add(
              workers.submit(
                  () ->
                      h.service.process(
                          input(
                              FIXTURE_USTREQ01_D6E6CD9B,
                              3,
                              0,
                              true,
                              sameMessage ? MESSAGE : new UUID(91, n),
                              TOKEN,
                              1))));
        }
        int fresh = 0;
        int replay = 0;
        var ids = new HashSet<String>();
        for (int i = 0; i < 100; i++) {
          byte[] body = results.get(i).get(30, java.util.concurrent.TimeUnit.SECONDS);
          String code = ascii(body, 208, 4);
          if (code.equals(FIXTURE_0000_876EEFE0)) fresh++;
          else {
            assertEquals(FIXTURE_0200_FC9DB3AC, code);
            replay++;
          }
          assertEquals((sameMessage ? MESSAGE : new UUID(91, i)).toString(), ascii(body, 60, 36));
          assertEquals("000000000003000000001   ", ascii(body, 256, 24));
          assertTrue(ids.add(ascii(body, 24, 36)));
        }
        assertEquals(1, fresh);
        assertEquals(99, replay);
        assertEquals(101, h.ids.get());
        assertEquals(1, h.inboxCount());
        assertEquals(1, h.version(3));
        assertEquals(0, h.live.get());
      }
    try (var h = new UserApplicationFixture(database);
        var workers = java.util.concurrent.Executors.newFixedThreadPool(10)) {
      h.seed();
      var results = new ArrayList<java.util.concurrent.Future<byte[]>>();
      for (int i = 0; i < 20; i++) {
        int n = i;
        results.add(
            workers.submit(
                () ->
                    h.service.process(
                        input(
                            FIXTURE_USTREQ01_D6E6CD9B,
                            3,
                            0,
                            true,
                            new UUID(92, n),
                            new UUID(93, n),
                            1))));
      }
      int successes = 0;
      for (var future : results) {
        String code = ascii(future.get(30, java.util.concurrent.TimeUnit.SECONDS), 208, 4);
        if (code.equals(FIXTURE_0000_876EEFE0)) successes++;
        else assertEquals(FIXTURE_0105_6F9AB3E4, code);
      }
      assertEquals(1, successes);
      assertEquals(20, h.inboxCount());
      assertEquals(1, h.version(3));
    }
    try (var h = new UserApplicationFixture(database);
        var workers = java.util.concurrent.Executors.newFixedThreadPool(2)) {
      h.seed();
      h.sql(
          "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select 4,'u4','u4',password_hash,role,status,password_changed_at,created_at,updated_at from schubert.app_users where id=3");
      var a =
          workers.submit(
              () ->
                  h.service.process(
                      input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, new UUID(94, 1), TOKEN, 1)));
      var b =
          workers.submit(
              () ->
                  h.service.process(
                      input(FIXTURE_USTREQ01_D6E6CD9B, 4, 0, true, new UUID(94, 2), TOKEN, 2)));
      assertEquals(
          FIXTURE_0000_876EEFE0, ascii(a.get(20, java.util.concurrent.TimeUnit.SECONDS), 208, 4));
      assertEquals(
          FIXTURE_0000_876EEFE0, ascii(b.get(20, java.util.concurrent.TimeUnit.SECONDS), 208, 4));
      assertEquals(2, h.inboxCount());
      assertEquals(1, h.version(3));
      assertEquals(1, h.version(4));
    }
    for (String mode : List.of("disable", "enable", "mixed", "demote"))
      try (var h = new UserApplicationFixture(database);
          var workers = java.util.concurrent.Executors.newFixedThreadPool(2)) {
        h.seed();
        var barrier = new java.util.concurrent.CyclicBarrier(2);
        var results = new ArrayList<java.util.concurrent.Future<byte[]>>();
        for (int i = 1; i <= 2; i++) {
          int owner = i;
          results.add(
              workers.submit(
                  () -> {
                    barrier.await(10, java.util.concurrent.TimeUnit.SECONDS);
                    return h.service.process(
                        input(
                            mode.equals("demote")
                                ? FIXTURE_URLREQ01_27B8B3D0
                                : FIXTURE_USTREQ01_D6E6CD9B,
                            owner == 1 ? 2 : 1,
                            0,
                            mode.equals("enable") || (mode.equals("mixed") && owner == 2),
                            new UUID(95, owner),
                            new UUID(96, owner),
                            owner));
                  }));
        }
        var codes = new ArrayList<String>();
        for (var result : results)
          codes.add(ascii(result.get(20, java.util.concurrent.TimeUnit.SECONDS), 208, 4));
        Collections.sort(codes);
        assertEquals(List.of(FIXTURE_0000_876EEFE0, "0102"), codes);
        assertEquals(1, h.inboxCount());
        assertTrue(
            h.scalar(
                    "select count(*) from schubert.app_users where role='ADMIN' and status='ACTIVE'")
                >= 1);
      }
  }

  static String ascii(byte[] body, int offset, int length) {
    return new String(body, offset, length, java.nio.charset.StandardCharsets.US_ASCII);
  }

  @Test
  void adm037DefiniteErrorsAndProcessingKeepApprovedResults() throws Exception {
    try (var h = new UserApplicationFixture(database)) {
      for (String kind :
          List.of(
              FIXTURE_DUPLICATE_E75B7650,
              "missing",
              FIXTURE_PASSWORD_FF2BEA10,
              FIXTURE_CAPACITY_84594495,
              FIXTURE_NOOP_A48838A5)) {
        h.seed();
        if (kind.equals(FIXTURE_CAPACITY_84594495))
          h.sql("update schubert.app_users set version=999999999 where id=3");
        if (kind.equals(FIXTURE_PASSWORD_FF2BEA10))
          h.sql(
              "update schubert.app_users set username='TargetUser12',username_key='targetuser12' where id=3");
        String layout =
            switch (kind) {
              case FIXTURE_DUPLICATE_E75B7650 -> FIXTURE_UCRREQ01_841A676A;
              case FIXTURE_PASSWORD_FF2BEA10 -> FIXTURE_UPWREQ01_256BADE0;
              case FIXTURE_NOOP_A48838A5 -> FIXTURE_ULKREQ01_CC99AF15;
              default -> FIXTURE_USTREQ01_D6E6CD9B;
            };
        var request =
            input(
                layout,
                kind.equals("missing") ? 99 : 3,
                kind.equals(FIXTURE_CAPACITY_84594495) ? 999_999_999L : 0,
                true,
                MESSAGE,
                TOKEN,
                1,
                kind.equals(FIXTURE_DUPLICATE_E75B7650) ? "u1" : "New",
                kind.equals(FIXTURE_PASSWORD_FF2BEA10) ? "targetuser12" : PASSWORD);
        String code =
            switch (kind) {
              case FIXTURE_DUPLICATE_E75B7650 -> FIXTURE_0105_6F9AB3E4;
              case "missing" -> "0104";
              case FIXTURE_PASSWORD_FF2BEA10 -> "0100";
              case FIXTURE_CAPACITY_84594495 -> "9001";
              default -> FIXTURE_0200_FC9DB3AC;
            };
        reply(
            h.service.process(request),
            request,
            code,
            kind.equals(FIXTURE_NOOP_A48838A5) ? 3 : 0,
            0,
            2);
        var stored = h.inboxMetadata();
        reply(
            h.service.process(request),
            request,
            code,
            kind.equals(FIXTURE_NOOP_A48838A5) ? 3 : 0,
            0,
            3);
        assertEquals(stored, h.inboxMetadata());
        assertEquals(1, h.inboxCount());
      }
      for (String corrupt :
          List.of(
              "processing",
              "fingerprint_key_version='unknown'",
              "response_key_version='unknown'",
              "response_body_encrypted=decode(repeat('00',29),'hex')")) {
        h.seed();
        var request = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1);
        h.service.process(request);
        if (corrupt.equals("processing"))
          h.sql(
              "update schubert.request_inbox set processing_state='PROCESSING',result_ref_type=null,result_ref_id=null,response_layout_id=null,response_version=null,response_body_encrypted=null,response_key_version=null,completed_at=null");
        else h.sql("update schubert.request_inbox set " + corrupt);
        var stored = h.inboxMetadata();
        temporary(() -> h.service.process(request));
        assertEquals(stored, h.inboxMetadata());
        assertEquals(1, h.version(3));
      }
    }
  }

  static void temporary(Executable call) {
    var failure = assertThrows(TemporaryInfrastructureException.class, call);
    assertEquals("request transaction is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void adm038BrokerSendAndAckFailuresReplayOneCommittedMutation() throws Exception {
    var brokerRoot = root.resolve("broker");
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
      for (String point : List.of("createProducer", "commit", FIXTURE_DATABASE_21C67C24))
        try (var h = new UserApplicationFixture(database)) {
          h.seed();
          var request = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1);
          var listener =
              new dev.codex.schubert.nk.api.messaging.inbound.SyncRequestListener(
                  h.service, java.time.Clock.fixed(NOW, java.time.ZoneOffset.UTC));
          if (point.equals(FIXTURE_DATABASE_21C67C24)) h.connectionFault = "open";
          var failing =
              (jakarta.jms.JMSContext)
                  java.lang.reflect.Proxy.newProxyInstance(
                      jakarta.jms.JMSContext.class.getClassLoader(),
                      new Class<?>[] {jakarta.jms.JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals(point)) {
                          assertEquals(1, h.inboxCount());
                          assertEquals(1, h.version(3));
                          assertEquals(0, h.live.get());
                          throw new jakarta.jms.JMSRuntimeException("synthetic transport failure");
                        }
                        return UserApplicationFixture.invoke(receiver, m, a);
                      });
          send(producer, requestQueue, request);
          var first = requests.receive(5000);
          assertNotNull(first);
          if (point.equals(FIXTURE_DATABASE_21C67C24))
            temporary(() -> listener.onMessage(failing, first));
          else
            assertThrows(
                jakarta.jms.JMSRuntimeException.class, () -> listener.onMessage(failing, first));
          assertNull(replies.receive(250));
          assertEquals(point.equals(FIXTURE_DATABASE_21C67C24) ? 0 : 1, h.inboxCount());
          h.connectionFault = "none";
          var retry = requests.receive(5000);
          assertNotNull(retry);
          assertEquals(2, retry.getIntProperty("JMSXDeliveryCount"));
          listener.onMessage(receiver, retry);
          byte[] response = brokerBody(replies.receive(5000));
          reply(
              response,
              request,
              point.equals(FIXTURE_DATABASE_21C67C24)
                  ? FIXTURE_0000_876EEFE0
                  : FIXTURE_0200_FC9DB3AC,
              3,
              1,
              h.ids.get());
          assertEquals(1, h.inboxCount());
          assertEquals(1, h.version(3));
          var frozen = h.inboxMetadata();
          send(producer, requestQueue, request);
          var duplicate = requests.receive(5000);
          assertNotNull(duplicate);
          listener.onMessage(receiver, duplicate);
          reply(
              brokerBody(replies.receive(5000)), request, FIXTURE_0200_FC9DB3AC, 3, 1, h.ids.get());
          assertEquals(frozen, h.inboxMetadata());
          var changed = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, false, MESSAGE, TOKEN, 1);
          send(producer, requestQueue, changed);
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
              h.scalar("select count(*) from schubert.app_logs where action='PROTOCOL_REJECTED'"));
          assertEquals(frozen, h.inboxMetadata());
          assertEquals(0, h.live.get());
        }
    } finally {
      broker.stop();
    }
  }

  @Test
  void adm039NullLifecycleAndAuditAllowlistProtectBoundaries() throws Exception {
    try (var h = new UserApplicationFixture(database)) {
      h.seed();
      var clock = java.time.Clock.fixed(NOW, java.time.ZoneOffset.UTC);
      for (Executable call :
          List.<Executable>of(
              () ->
                  new UserMutationApplicationService(
                      null, h.authentication, h.inbox, h.commands, h.responses, clock),
              () ->
                  new UserMutationApplicationService(
                      h.source, null, h.inbox, h.commands, h.responses, clock),
              () ->
                  new UserMutationApplicationService(
                      h.source, h.authentication, null, h.commands, h.responses, clock),
              () ->
                  new UserMutationApplicationService(
                      h.source, h.authentication, h.inbox, null, h.responses, clock),
              () ->
                  new UserMutationApplicationService(
                      h.source, h.authentication, h.inbox, h.commands, null, clock),
              () ->
                  new UserMutationApplicationService(
                      h.source, h.authentication, h.inbox, h.commands, h.responses, null),
              () -> h.build(clock, null),
              () -> h.service.process(null))) assertThrows(NullPointerException.class, call);
      var request = input(FIXTURE_USTREQ01_D6E6CD9B, 3, 0, true, MESSAGE, TOKEN, 1);
      h.service =
          h.build(
              clock,
              () -> {
                int i = h.ids.incrementAndGet();
                assertEquals(i == 1 ? 1 : 0, h.live.get());
                assertEquals(i == 1 ? 0 : 1, h.commits.get());
                return new UUID(900, i);
              });
      reply(h.service.process(request), request, FIXTURE_0000_876EEFE0, 3, 1, 2);
      assertEquals(1, h.commits.get());
      h.seed();
      var normal = UserApplicationAssembly.mutations(h.source, h.fingerprints, h.snapshots, clock);
      // PT-ADM-ASSEMBLY-002/003: production authentication/Inbox/User/audit graph.
      for (Executable missing :
          List.<Executable>of(
              () -> UserApplicationAssembly.mutations(null, h.fingerprints, h.snapshots, clock),
              () -> UserApplicationAssembly.mutations(h.source, null, h.snapshots, clock),
              () -> UserApplicationAssembly.mutations(h.source, h.fingerprints, null, clock),
              () -> UserApplicationAssembly.mutations(h.source, h.fingerprints, h.snapshots, null)))
        assertThrows(NullPointerException.class, missing);
      byte[] result = normal.process(request);
      assertEquals(FIXTURE_0000_876EEFE0, ascii(result, 208, 4));
      assertEquals(MESSAGE.toString(), ascii(result, 60, 36));
      assertNotEquals(MESSAGE, UUID.fromString(ascii(result, 24, 36)));
      assertEquals(1, h.version(3));
      h.seed();
      var unsupportedHeader =
          new dev.codex.schubert.nk.protocol.header.CommonHeader(
              "SCHBNK01",
              1,
              new dev.codex.schubert.nk.protocol.layout.LayoutId("UDTREQ01"),
              1,
              dev.codex.schubert.nk.protocol.header.MessageKind.REQUEST,
              dev.codex.schubert.nk.protocol.header.InteractionKind.SYNCHRONOUS,
              MESSAGE,
              MESSAGE,
              NOW,
              request.header().authenticationContext(),
              256,
              12,
              0,
              0,
              268,
              Optional.empty());
      var unsupported =
          new dev.codex.schubert.nk.protocol.layout.WireMessage<>(
              unsupportedHeader,
              new dev.codex.schubert.nk.protocol.layout.FixedPayload(
                  "000000000003".getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                  0,
                  List.of()));
      assertThrows(PermanentProtocolException.class, () -> normal.process(unsupported));
      assertEquals(0, h.commits.get());
      assertEquals(0, h.inboxCount());
      h.sql("update schubert.app_users set role='USER' where id=1");
      try (var c = database.transaction()) {
        var actor =
            h.authentication.verifyIdentity(
                c,
                request.header().authenticationContext().orElseThrow(),
                dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation.ENABLE,
                java.util.OptionalLong.of(3),
                NOW);
        assertEquals(dev.codex.schubert.nk.api.domain.Role.USER, actor.role());
        assertEquals(1, actor.userId());
        c.rollback();
        assertThrows(
            dev.codex.schubert.nk.api.security.AuthorizationException.class,
            () ->
                h.authentication.verify(
                    c,
                    request.header().authenticationContext().orElseThrow(),
                    dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation.ENABLE,
                    java.util.OptionalLong.of(3),
                    NOW));
        c.rollback();
      }
      h.seed();
      h.fingerprints.close();
      temporary(() -> normal.process(request));
      assertEquals(0, h.inboxCount());
      assertEquals(0, h.version(3));
    }
    for (String layout :
        List.of(
            FIXTURE_UCRREQ01_841A676A,
            FIXTURE_USTREQ01_D6E6CD9B,
            FIXTURE_URLREQ01_27B8B3D0,
            FIXTURE_UPWREQ01_256BADE0,
            FIXTURE_ULKREQ01_CC99AF15))
      try (var h = new UserApplicationFixture(database)) {
        h.seed();
        h.sql("update schubert.app_users set username=E'Admin\\nName' where id=1");
        var original = input(layout, 3, 0, true, MESSAGE, TOKEN, 1);
        h.service.process(original);
        var changed =
            input(
                layout,
                3,
                1,
                false,
                new UUID(97, 1),
                TOKEN,
                1,
                "New2",
                "Changed-Synthetic-Password-12");
        reply(h.service.process(changed), changed, FIXTURE_0105_6F9AB3E4, 0, 0, h.ids.get());
        assertEquals(
            "Admin Name",
            h.text(
                "select actor_username from schubert.app_logs where details->>'reason'='TOKEN_MISMATCH'"));
        String json =
            h.text(
                "select details::text from schubert.app_logs where details->>'reason'='TOKEN_MISMATCH'");
        var object = com.google.gson.JsonParser.parseString(json).getAsJsonObject();
        Set<String> expected =
            new HashSet<>(
                List.of(
                    "outcome",
                    "reason",
                    "layout",
                    "operation",
                    "targetType",
                    "actorRole",
                    "resultCode"));
        if (!layout.equals(FIXTURE_UCRREQ01_841A676A)) expected.add("targetUserId");
        assertEquals(expected, object.keySet());
        assertEquals("DENIED", object.get("outcome").getAsString());
        assertEquals("ADMIN", object.get("actorRole").getAsString());
        assertEquals(layout, object.get("layout").getAsString());
        assertEquals(FIXTURE_0105_6F9AB3E4, object.get("resultCode").getAsString());
        for (String secret :
            List.of(
                TOKEN.toString(), context(1), PASSWORD, "Changed-Synthetic-Password-12", "pbkdf2"))
          assertFalse(json.contains(secret));
        assertTrue(json.getBytes(java.nio.charset.StandardCharsets.UTF_8).length < 400);
        assertEquals(
            "SECURITY/WARN",
            h.text(
                "select category||'/'||level from schubert.app_logs where details->>'reason'='TOKEN_MISMATCH'"));
        assertEquals(1, h.inboxCount());
      }
  }

  static String independentFingerprint(String layout) throws Exception {
    var fields = UserMutationRequestTest.fields(layout, 0, true, "New", "new", PASSWORD);
    var bytes = new java.io.ByteArrayOutputStream();
    try (var out = new java.io.DataOutputStream(bytes)) {
      out.write("SCHUBERT-NK-OP1".getBytes(java.nio.charset.StandardCharsets.US_ASCII));
      for (String field :
          List.of(
              "1",
              layout,
              "001",
              layout.equals(FIXTURE_UCRREQ01_841A676A) ? "NEW_USER:new" : "USER:3"))
        UserMutationRequestTest.lp(out, field);
      out.writeInt(fields.size());
      for (var field : fields) {
        UserMutationRequestTest.lp(out, field.name());
        UserMutationRequestTest.lp(out, field.type());
        UserMutationRequestTest.lp(out, field.value());
      }
    }
    var mac = javax.crypto.Mac.getInstance("HmacSHA256");
    mac.init(new javax.crypto.spec.SecretKeySpec(new byte[32], "HmacSHA256"));
    return HexFormat.of().formatHex(mac.doFinal(bytes.toByteArray()));
  }

  static void send(
      jakarta.jms.JMSContext context,
      org.apache.activemq.artemis.jms.client.ActiveMQQueue queue,
      dev.codex.schubert.nk.protocol.layout.WireMessage<
              dev.codex.schubert.nk.protocol.layout.FixedPayload>
          input)
      throws Exception {
    byte[] data = input.payload().copyData();
    byte[] wire = new byte[256 + data.length];
    Arrays.fill(wire, (byte) 32);
    UserMutationRequestTest.put(
        wire, 0, "SCHBNK01001" + input.header().layoutId().value() + "001QS");
    UserMutationRequestTest.put(wire, 24, input.header().messageId().toString());
    UserMutationRequestTest.put(wire, 60, input.header().messageId().toString());
    UserMutationRequestTest.put(wire, 96, "20260908090100000");
    UserMutationRequestTest.put(
        wire, 113, input.header().authenticationContext().orElseThrow().wireValue());
    UserMutationRequestTest.put(
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
    message.setStringProperty("NKLayoutID", input.header().layoutId().value());
    message.setStringProperty("NKProtocolVersion", "001");
    context
        .createProducer()
        .setDeliveryMode(jakarta.jms.DeliveryMode.PERSISTENT)
        .setTimeToLive(5000)
        .send(queue, message);
    Arrays.fill(data, (byte) 0);
    Arrays.fill(wire, (byte) 0);
  }

  static byte[] brokerBody(jakarta.jms.Message received) throws Exception {
    var message = assertInstanceOf(jakarta.jms.BytesMessage.class, received);
    assertEquals(280, message.getBodyLength());
    byte[] body = new byte[280];
    assertEquals(280, message.readBytes(body));
    assertEquals(ascii(body, 60, 36), message.getJMSCorrelationID());
    assertEquals(ascii(body, 24, 36), message.getStringProperty("NKMessageID"));
    assertEquals("USTRSP01", message.getStringProperty("NKLayoutID"));
    assertEquals("001", message.getStringProperty("NKProtocolVersion"));
    return body;
  }
}
