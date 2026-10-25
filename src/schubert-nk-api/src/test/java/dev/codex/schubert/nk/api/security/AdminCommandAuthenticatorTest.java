package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/** SSC-031; independent real PG lock/state postconditions, PT-ADM-008..013/074. */
class AdminCommandAuthenticatorTest {
  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static AdminCommandAuthenticator authentication;
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  static final AuthenticationContext CONTEXT = AuthenticationContext.of("b".repeat(64));

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    authentication = new AdminCommandAuthenticator(new ContextHash());
  }

  @AfterAll
  static void stop() throws Exception {
    if (database != null) database.stop();
  }

  @BeforeEach
  void reset() throws Exception {
    seed();
  }

  @Test
  void adm008AllMutationKindsLockThenAuthenticateCurrentAdmin() throws Exception {
    for (Mutation kind : Mutation.values()) {
      try (var c = database.transaction()) {
        var tracking = new AdminAuthFixture();
        var target = kind == Mutation.CREATE ? OptionalLong.empty() : OptionalLong.of(3);
        var actor = authentication.verify(tracking.wrap(c), CONTEXT, kind, target, NOW);
        assertEquals(new AuthenticatedActor(1, "u1", Role.ADMIN), actor);
        assertFalse(c.isClosed());
        assertFalse(c.getAutoCommit());
        boolean reducing = kind == Mutation.DISABLE || kind == Mutation.DEMOTE;
        assertEquals(reducing ? 7 : 6, tracking.statements.size());
        assertEquals(
            "select user_id from schubert.auth_sessions where context_hash=?",
            tracking.statements.getFirst());
        int users = reducing ? 2 : 1;
        if (reducing)
          assertEquals("select pg_advisory_xact_lock(71419601)", tracking.statements.get(1));
        assertTrue(tracking.statements.get(users).contains("order by id for update"));
        assertEquals(
            "select user_id from schubert.auth_sessions where context_hash=? for update",
            tracking.statements.get(users + 1));
        assertTrue(tracking.statements.getLast().startsWith("update schubert.auth_sessions"));
        for (int id = 1; id <= 4; id++)
          assertUserLock(id, id == 1 || (id == 3 && kind != Mutation.CREATE) || reducing);
        try (var statement = c.createStatement();
            var rows =
                statement.executeQuery(
                    "select count(*) from pg_locks where pid=pg_backend_pid() and locktype='advisory' and classid=0 and objid=71419601")) {
          assertTrue(rows.next());
          assertEquals(reducing ? 1 : 0, rows.getInt(1));
        }
        assertTimes(c, 1, NOW, Instant.parse("2026-09-08T08:01:00Z"));
        c.rollback();
      }
    }
    try (var c = database.transaction()) {
      assertEquals(
          1,
          authentication.verify(c, CONTEXT, Mutation.ENABLE, OptionalLong.of(999), NOW).userId());
      c.rollback();
    }
  }

  @Test
  void adm011NullTargetsAndWriteTransactionContractsFailClosed() throws Exception {
    assertThrows(NullPointerException.class, () -> new AdminCommandAuthenticator(null));
    try (var c = database.transaction()) {
      var tracking = new AdminAuthFixture();
      var wrapped = tracking.wrap(c);
      for (Executable call :
          List.<Executable>of(
              () ->
                  authentication.verify(null, CONTEXT, Mutation.CREATE, OptionalLong.empty(), NOW),
              () ->
                  authentication.verify(wrapped, null, Mutation.CREATE, OptionalLong.empty(), NOW),
              () -> authentication.verify(wrapped, CONTEXT, null, OptionalLong.empty(), NOW),
              () -> authentication.verify(wrapped, CONTEXT, Mutation.CREATE, null, NOW),
              () ->
                  authentication.verify(
                      wrapped, CONTEXT, Mutation.CREATE, OptionalLong.empty(), null)))
        assertThrows(NullPointerException.class, call);
      assertThrows(
          IllegalArgumentException.class,
          () -> authentication.verify(wrapped, CONTEXT, Mutation.CREATE, OptionalLong.of(1), NOW));
      for (Mutation kind : Mutation.values())
        if (kind != Mutation.CREATE) {
          assertThrows(
              IllegalArgumentException.class,
              () -> authentication.verify(wrapped, CONTEXT, kind, OptionalLong.empty(), NOW));
          for (long id : new long[] {0, -1, 1_000_000_000_000L})
            assertThrows(
                IllegalArgumentException.class,
                () -> authentication.verify(wrapped, CONTEXT, kind, OptionalLong.of(id), NOW));
        }
      assertEquals(0, tracking.statements.size());
      c.setReadOnly(true);
      infrastructure(
          () ->
              authentication.verify(wrapped, CONTEXT, Mutation.CREATE, OptionalLong.empty(), NOW));
      c.rollback();
      c.setReadOnly(false);
      c.setAutoCommit(true);
      infrastructure(
          () ->
              authentication.verify(wrapped, CONTEXT, Mutation.CREATE, OptionalLong.empty(), NOW));
      assertEquals(0, tracking.statements.size());
      assertFalse(c.isClosed());
    }
  }

  @Test
  void adm009ReciprocalAdminsFollowOneGlobalUserOrder() throws Exception {
    for (var pair :
        List.of(
            List.of(Mutation.ENABLE, Mutation.DISABLE),
            List.of(Mutation.DISABLE, Mutation.ENABLE),
            List.of(Mutation.RESET_PASSWORD, Mutation.RESET_PASSWORD))) {
      try (var first = database.transaction();
          var pool = Executors.newSingleThreadExecutor()) {
        authentication.verify(first, CONTEXT, pair.get(0), OptionalLong.of(2), NOW);
        CountDownLatch attempting = new CountDownLatch(1);
        var future =
            pool.submit(
                () -> {
                  try (var second = database.transaction()) {
                    var tracking = new AdminAuthFixture();
                    tracking.before =
                        sql -> {
                          if (sql.contains("pg_advisory_xact_lock")
                              || sql.contains("order by id for update")) attempting.countDown();
                        };
                    var actor =
                        authentication.verify(
                            tracking.wrap(second),
                            AuthenticationContext.of("c".repeat(64)),
                            pair.get(1),
                            OptionalLong.of(1),
                            NOW);
                    second.rollback();
                    return actor;
                  }
                });
        assertTrue(attempting.await(5, TimeUnit.SECONDS));
        assertFalse(future.isDone());
        first.rollback();
        assertEquals(new AuthenticatedActor(2, "u2", Role.ADMIN), future.get(5, TimeUnit.SECONDS));
      }
    }
    try (var first = database.transaction();
        var pool = Executors.newSingleThreadExecutor()) {
      authentication.verify(first, CONTEXT, Mutation.DEMOTE, OptionalLong.of(2), NOW);
      CountDownLatch attempting = new CountDownLatch(1);
      var future =
          pool.submit(
              () -> {
                try (var second = database.transaction()) {
                  var tracking = new AdminAuthFixture();
                  tracking.before =
                      sql -> {
                        if (sql.contains("order by id for update")) attempting.countDown();
                      };
                  assertEquals(
                      ResultCode.FORBIDDEN,
                      assertThrows(
                              AuthorizationException.class,
                              () ->
                                  authentication.verify(
                                      tracking.wrap(second),
                                      AuthenticationContext.of("c".repeat(64)),
                                      Mutation.PROMOTE,
                                      OptionalLong.of(1),
                                      NOW))
                          .resultCode());
                  second.rollback();
                  return true;
                }
              });
      assertTrue(attempting.await(5, TimeUnit.SECONDS));
      assertFalse(future.isDone());
      // Controlled state change, not a claim that the command service is implemented.
      try (var s = first.createStatement()) {
        assertEquals(1, s.executeUpdate("update schubert.app_users set role='USER' where id=2"));
      }
      first.commit();
      assertTrue(future.get(5, TimeUnit.SECONDS));
    }
    try (var c = database.api()) {
      assertTimes(
          c, 2, Instant.parse("2026-09-08T00:00:00Z"), Instant.parse("2026-09-08T08:00:00Z"));
    }
  }

  @Test
  void adm010RevokedExpiredChangedOwnerAndRoleNeverAuthorize() throws Exception {
    try (var c = database.transaction()) {
      denied(
          () ->
              authentication.verify(
                  c,
                  AuthenticationContext.of("f".repeat(64)),
                  Mutation.CREATE,
                  OptionalLong.empty(),
                  NOW));
      c.rollback();
    }
    for (String change :
        List.of("revoke", "expiry", "disabled", "role", "owner", "missing", "missingUser")) {
      seed();
      try (var c = database.transaction()) {
        var tracking = new AdminAuthFixture();
        tracking.before =
            text -> {
              if (!text.contains("order by id for update")) return;
              tracking.before = ignored -> {};
              switch (change) {
                case "revoke" ->
                    sql(
                        "update schubert.auth_sessions set revoked=true,revoked_at='2026-09-08T00:01:00Z',revoke_reason='ADMIN' where user_id=1");
                case "expiry" ->
                    sql(
                        "update schubert.auth_sessions set expires_at='2026-09-08T00:01:00Z' where user_id=1");
                case "disabled" ->
                    sql("update schubert.app_users set status='DISABLED' where id=1");
                case "role" -> sql("update schubert.app_users set role='USER' where id=1");
                case "owner" -> sql("update schubert.auth_sessions set user_id=4 where user_id=1");
                default -> {
                  sql("delete from schubert.auth_sessions where user_id=1");
                  if (change.equals("missingUser"))
                    try (var admin = database.admin();
                        var s = admin.createStatement()) {
                      s.executeUpdate("delete from schubert.app_users where id=1");
                    }
                }
              }
            };
        Executable call =
            () ->
                authentication.verify(
                    tracking.wrap(c), CONTEXT, Mutation.ENABLE, OptionalLong.of(3), NOW);
        if (change.equals("role"))
          assertEquals(
              ResultCode.FORBIDDEN, assertThrows(AuthorizationException.class, call).resultCode());
        else if (change.equals("missingUser")) infrastructure(call);
        else denied(call);
        assertFalse(c.isClosed());
        c.rollback();
      }
    }
    seed();
    sql(
        "update schubert.auth_sessions set expires_at='2026-09-08T00:01:00.000001Z' where user_id=1");
    try (var c = database.transaction()) {
      assertEquals(
          1,
          authentication.verify(c, CONTEXT, Mutation.CREATE, OptionalLong.empty(), NOW).userId());
      c.rollback();
    }
  }

  @Test
  void adm012JdbcClockAndResourceFailuresRollbackWithoutLeaks() throws Exception {
    for (String stage :
        List.of(
            "select user_id from",
            "pg_advisory_xact_lock",
            "order by id for update",
            "where context_hash=? for update",
            "for update of u",
            "for update of s",
            "update schubert.auth_sessions")) {
      List<String> points = new ArrayList<>(List.of("prepareStatement", "statementClose"));
      if (stage.startsWith("update"))
        points.addAll(List.of("executeUpdate", "zeroUpdate", "setObject", "setObject#2"));
      else points.addAll(List.of("executeQuery", "next", "resultClose"));
      if (stage.equals("select user_id from") || stage.equals("order by id for update"))
        points.addAll(List.of("getLong", "wasNull"));
      if (stage.equals("select user_id from")) points.add("setString");
      if (stage.equals("order by id for update")) points.addAll(List.of("setLong", "setBoolean"));
      for (String point : points) {
        try (var c = database.transaction()) {
          var fault = new AdminAuthFixture();
          fault.match = stage;
          fault.method = point;
          infrastructure(
              () ->
                  authentication.verify(
                      fault.wrap(c), CONTEXT, Mutation.DISABLE, OptionalLong.of(3), NOW));
          assertFalse(c.isClosed());
          c.rollback();
        }
      }
    }
    for (String connectionFault : List.of("getAutoCommit", "isReadOnly"))
      try (var c = database.transaction()) {
        var fault = new AdminAuthFixture();
        fault.method = connectionFault;
        infrastructure(
            () ->
                authentication.verify(
                    fault.wrap(c), CONTEXT, Mutation.CREATE, OptionalLong.empty(), NOW));
        c.rollback();
      }
    for (String stage :
        List.of(
            "select user_id from", "where context_hash=? for update", "order by id for update")) {
      try (var c = database.transaction()) {
        var fault = new AdminAuthFixture();
        fault.match = stage;
        fault.nullNumber = true;
        infrastructure(
            () ->
                authentication.verify(
                    fault.wrap(c), CONTEXT, Mutation.ENABLE, OptionalLong.of(3), NOW));
        c.rollback();
      }
    }
    for (long invalid : new long[] {0, 1_000_000_000_000L, 999})
      try (var c = database.transaction()) {
        var fault = new AdminAuthFixture();
        fault.match = "select user_id from";
        fault.ownerOverride = invalid;
        infrastructure(
            () ->
                authentication.verify(
                    fault.wrap(c), CONTEXT, Mutation.ENABLE, OptionalLong.of(3), NOW));
        c.rollback();
      }
    for (String kind :
        List.of(
            "duplicateOwner",
            "emptyAdvisory",
            "duplicateAdvisory",
            "reversedUserIds",
            "nullRole",
            "differentActor"))
      try (var c = database.transaction()) {
        var fault = new AdminAuthFixture();
        switch (kind) {
          case "duplicateOwner" -> {
            fault.match = "select user_id from";
            fault.duplicate = true;
          }
          case "emptyAdvisory" -> {
            fault.match = "pg_advisory_xact_lock";
            fault.empty = true;
          }
          case "duplicateAdvisory" -> {
            fault.match = "pg_advisory_xact_lock";
            fault.duplicate = true;
          }
          case "reversedUserIds" -> {
            fault.match = "order by id for update";
            fault.reverseIds = true;
          }
          case "nullRole" -> {
            fault.match = "for update of s";
            fault.nullText = true;
          }
          default -> {
            fault.match = "for update of s";
            fault.fields.put("user_id", 4L);
          }
        }
        infrastructure(
            () ->
                authentication.verify(
                    fault.wrap(c), CONTEXT, Mutation.DISABLE, OptionalLong.of(3), NOW));
        c.rollback();
      }
    for (String close : List.of("resultClose", "statementClose"))
      try (var c = database.transaction()) {
        var fault = new AdminAuthFixture();
        fault.match = "select user_id from";
        fault.method = close;
        infrastructure(
            () ->
                authentication.verify(
                    fault.wrap(c),
                    AuthenticationContext.of("f".repeat(64)),
                    Mutation.CREATE,
                    OptionalLong.empty(),
                    NOW));
        c.rollback();
      }
    try (var c = database.transaction()) {
      // Timestamp overflow must not grant authority or leak provider details.
      infrastructure(
          () ->
              authentication.verify(
                  c, CONTEXT, Mutation.CREATE, OptionalLong.empty(), Instant.MIN));
      c.rollback();
    }
    try (var c = database.api()) {
      assertTimes(
          c, 1, Instant.parse("2026-09-08T00:00:00Z"), Instant.parse("2026-09-08T08:00:00Z"));
    }
  }

  @Test
  void adm013ConcurrentAuthenticationKeepsNoCrossRequestState() throws Exception {
    CountDownLatch start = new CountDownLatch(1);
    try (var pool = Executors.newFixedThreadPool(10)) {
      List<Future<Long>> futures = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        final int user = i % 2 + 1;
        futures.add(
            pool.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  try (var c = database.transaction()) {
                    var actor =
                        authentication.verify(
                            c,
                            AuthenticationContext.of(
                                String.valueOf((char) ('a' + user)).repeat(64)),
                            Mutation.RESET_PASSWORD,
                            OptionalLong.of(3),
                            NOW);
                    assertEquals(user, actor.userId());
                    assertEquals(Role.ADMIN, actor.role());
                    assertTimes(c, user, NOW, Instant.parse("2026-09-08T08:01:00Z"));
                    c.commit();
                    return actor.userId();
                  }
                }));
      }
      start.countDown();
      for (int i = 0; i < 100; i++)
        assertEquals(i % 2 + 1, futures.get(i).get(10, TimeUnit.SECONDS));
    }
    try (var c = database.api()) {
      for (int user = 1; user <= 2; user++)
        assertTimes(c, user, NOW, Instant.parse("2026-09-08T08:01:00Z"));
      assertTimes(
          c, 3, Instant.parse("2026-09-08T00:00:00Z"), Instant.parse("2026-09-08T08:00:00Z"));
    }
  }

  @Test
  void adm074ProviderIllegalArgumentPlusCloseIsInfrastructure() throws Exception {
    // YKT-162: the borrowed JDBC provider is not a model validator. Both faults are redacted,
    // and the caller-owned transaction retains its original session state after rollback.
    try (var c = database.transaction()) {
      var fault = new AdminAuthFixture();
      fault.match = "select user_id from";
      fault.method = "providerIaeGetLongAndResultClose";
      infrastructure(
          () ->
              authentication.verify(
                  fault.wrap(c), CONTEXT, Mutation.ENABLE, OptionalLong.of(3), NOW));
      assertEquals(1, fault.resultsClosed);
      assertFalse(c.isClosed());
      c.rollback();
    }
    try (var c = database.api()) {
      assertTimes(
          c, 1, Instant.parse("2026-09-08T00:00:00Z"), Instant.parse("2026-09-08T08:00:00Z"));
    }
  }

  static void assertUserLock(int id, boolean locked) throws SQLException {
    try (var c = database.transaction();
        var s =
            c.prepareStatement("select id from schubert.app_users where id=? for update nowait")) {
      s.setInt(1, id);
      if (locked)
        assertEquals("55P03", assertThrows(SQLException.class, s::executeQuery).getSQLState());
      else
        try (var r = s.executeQuery()) {
          assertTrue(r.next());
          assertEquals(id, r.getInt(1));
        }
      c.rollback();
    }
  }

  static void assertTimes(Connection c, int user, Instant touched, Instant expires)
      throws SQLException {
    try (var s =
        c.prepareStatement(
            "select last_accessed_at,expires_at from schubert.auth_sessions where user_id=?")) {
      s.setInt(1, user);
      try (var r = s.executeQuery()) {
        assertTrue(r.next());
        assertEquals(touched, r.getObject(1, java.time.OffsetDateTime.class).toInstant());
        assertEquals(expires, r.getObject(2, java.time.OffsetDateTime.class).toInstant());
        assertFalse(r.next());
      }
    }
  }

  static void infrastructure(Executable call) {
    var error = assertThrows(AuthenticationInfrastructureException.class, call);
    assertEquals("authentication storage is unavailable", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  static void denied(Executable call) {
    var error = assertThrows(AuthenticationContextException.class, call);
    assertEquals("authentication context is not valid", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }

  static void sql(String text) throws SQLException {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.execute(text);
    }
  }

  static void seed() throws Exception {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users cascade");
    }
    sql(
        "insert into schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at) select i,'u'||i,'u'||i,'unusable-test-hash',case when i=3 then 'USER' else 'ADMIN' end,'ACTIVE','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z' from generate_series(1,4)i");
    try (var c = database.api();
        var s =
            c.prepareStatement(
                "insert into schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id) values (?,?,?,decode(repeat('00',29),'hex'),'test','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','127.0.0.1',?)")) {
      for (int id = 1; id <= 3; id++) {
        String raw = String.valueOf((char) ('a' + id)).repeat(64);
        String hash =
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest(raw.getBytes(StandardCharsets.US_ASCII)));
        s.setObject(1, new UUID(0, id));
        s.setInt(2, id);
        s.setString(3, hash);
        s.setObject(4, new UUID(1, id));
        s.executeUpdate();
      }
    }
  }
}
