package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.logging.ApiLogDatabaseFixture;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.api.security.AuthSessionRevocationService;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthenticationContextException;
import dev.codex.schubert.nk.api.security.AuthenticationInfrastructureException;
import dev.codex.schubert.nk.api.security.AuthorizationException;
import dev.codex.schubert.nk.api.security.ContextHash;
import dev.codex.schubert.nk.api.security.PasswordHasher;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.sql.Connection;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * Real PostgreSQL/production grants; independent SQL/JCA oracles. SS312/332/351; PT-ADM-014..023.
 */
class UserCommandServiceTest {
  private static final String EXPECTED_ADMIN_ROLE = "ADMIN";

  private static final int FIXTURE_UNKNOWN_HASH_MODE = 1;
  private static final int FIXTURE_ARGUMENT_FAILURE_MODE = 2;

  private static final String FIXTURE_ROLE_COLUMN = "role";
  private static final String FIXTURE_ACTIVE_STATE = "ACTIVE";
  private static final String FIXTURE_STATUS_COLUMN = "status";
  private static final String FIXTURE_VERSION_COLUMN = "version";
  private static final String FIXTURE_FAILED_COUNT_COLUMN = "failed_count";
  private static final String FIXTURE_COUNT_COLUMN = "count";
  private static final String FIXTURE_ACTIVE_ADMINS_SQL =
      "select count(*) from schubert.app_users where role='ADMIN' and status='ACTIVE'";
  private static final String FIXTURE_INSERT_USERS_PREFIX = "insert into schubert.app_users";
  private static final String FIXTURE_UPDATE_USERS_PREFIX = "update schubert.app_users";
  private static final String FIXTURE_NEW_USERNAME = "new";
  private static final String FIXTURE_INSERT_PREFIX = "insert into";

  @TempDir static Path root;
  static ApiLogDatabaseFixture database;
  static final Instant NOW = Instant.parse("2026-09-08T00:01:00Z");
  static final UserCommandMetadata META =
      new UserCommandMetadata(new UUID(10, 1), new UUID(20, 1), NOW);
  static final AuthenticatedActor ADMIN = new AuthenticatedActor(1, "u1", Role.ADMIN);
  static final AuthenticationContext CONTEXT = AuthenticationContext.of("b".repeat(64));
  static final UserId TARGET = new UserId(3);
  static final String PASSWORD = "Synthetic-12";
  static final String TEST_HASH = "{pbkdf2-v1}" + "0".repeat(96);
  static UserCommandService service;
  static AdminCommandAuthenticator authentication;

  @BeforeAll
  static void start() throws Exception {
    database = new ApiLogDatabaseFixture(root);
    authentication = new AdminCommandAuthenticator(new ContextHash());
    service =
        new UserCommandService(
            new PasswordHasher(), new AuthSessionRevocationService(new ContextHash()));
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
  void adm014CreateNormalizesAsciiUsersAndIndependentlyVerifiesPassword() throws Exception {
    String[] names = {" x ", "A".repeat(64), "New.User_3-4", "disabled"};
    String[] secrets = {PASSWORD, "p".repeat(128), "e\u0301".repeat(128), "z".repeat(12)};
    String[] normalized = {PASSWORD, "p".repeat(128), "é".repeat(128), "z".repeat(12)};
    for (int i = 0; i < names.length; i++) {
      int index = i;
      char[] input = secrets[i].toCharArray();
      var result =
          run(
              Mutation.CREATE,
              OptionalLong.empty(),
              (c, a) ->
                  service.create(
                      c,
                      a,
                      names[index],
                      input,
                      index % 2 == 0 ? UserRole.USER : UserRole.ADMIN,
                      index != 3,
                      META));
      success(result, 5 + i, 0, ResultCode.SUCCESS);
      erased(input);
      try (var c = database.api();
          var s = c.prepareStatement("select * from schubert.app_users where id=?")) {
        s.setLong(1, 5 + i);
        try (var r = s.executeQuery()) {
          assertTrue(r.next());
          assertEquals(names[i].trim(), r.getString("username"));
          assertEquals(names[i].trim().toLowerCase(Locale.ROOT), r.getString("username_key"));
          assertEquals(i % 2 == 0 ? "USER" : EXPECTED_ADMIN_ROLE, r.getString(FIXTURE_ROLE_COLUMN));
          assertEquals(
              i != 3 ? FIXTURE_ACTIVE_STATE : "DISABLED", r.getString(FIXTURE_STATUS_COLUMN));
          assertEquals(0, r.getLong(FIXTURE_VERSION_COLUMN));
          assertEquals(0, r.getInt(FIXTURE_FAILED_COUNT_COLUMN));
          for (String column : List.of("created_at", "updated_at", "password_changed_at"))
            assertEquals(NOW, r.getObject(column, java.time.OffsetDateTime.class).toInstant());
          assertEquals(1, r.getLong("created_by"));
          assertEquals(1, r.getLong("updated_by"));
          independentHash(r.getString("password_hash"), normalized[i]);
          assertNull(r.getObject("locked_until", java.time.OffsetDateTime.class));
          assertFalse(r.next());
        }
      }
    }
    assertEquals(8, count("select count(*) from schubert.app_logs where action='USER_CREATED'"));
    assertEquals(4, count("select count(*) from schubert.auth_sessions"));
  }

  @Test
  void adm015StatusChangesAtomicallyRevokeSessions() throws Exception {
    for (boolean enabled : new boolean[] {false, true}) {
      seed();
      extraSessions();
      var result =
          run(
              enabled ? Mutation.ENABLE : Mutation.DISABLE,
              OptionalLong.of(3),
              (c, a) -> service.changeStatus(c, a, TARGET, enabled, 0, META));
      success(result, 3, 1, ResultCode.SUCCESS);
      assertUser(FIXTURE_STATUS_COLUMN, enabled ? FIXTURE_ACTIVE_STATE : "DISABLED");
      assertUser(FIXTURE_VERSION_COLUMN, "1");
      assertEquals(
          3,
          count(
              "select count(*) from schubert.auth_sessions where user_id=3 and revoked and"
                  + " revoked_at='2026-09-08T00:01:00Z' and revoke_reason='"
                  + (enabled ? EXPECTED_ADMIN_ROLE : "DISABLED")
                  + "'"));
      assertEquals(
          1,
          count(
              "select count(*) from schubert.auth_sessions where user_id=3 and"
                  + " revoke_reason='LOGOUT' and revoked_at='2026-09-08T00:00:30Z'"));
      assertEquals(
          3, count("select count(*) from schubert.app_logs where action='SESSION_REVOKED'"));
      assertEquals(
          2, count("select count(*) from schubert.app_logs where action='USER_STATUS_CHANGED'"));
      result =
          run(
              enabled ? Mutation.ENABLE : Mutation.DISABLE,
              OptionalLong.of(3),
              (c, a) -> service.changeStatus(c, a, TARGET, enabled, 1, META));
      success(result, 3, 2, ResultCode.SUCCESS);
      assertEquals(
          3, count("select count(*) from schubert.app_logs where action='SESSION_REVOKED'"));
    }
  }

  @Test
  void adm016RoleChangesProtectSelfAndLastActiveAdmin() throws Exception {
    success(
        run(
            Mutation.PROMOTE,
            OptionalLong.of(2),
            (c, a) -> service.changeRole(c, a, new UserId(2), UserRole.ADMIN, 0, META)),
        2,
        1,
        ResultCode.SUCCESS);
    seed();
    success(
        run(
            Mutation.DISABLE,
            OptionalLong.of(2),
            (c, a) -> service.changeStatus(c, a, new UserId(2), false, 0, META)),
        2,
        1,
        ResultCode.SUCCESS);
    seed();
    // Defensive database count fault after the real ordered prelude must not reduce membership.
    try (var c = database.transaction()) {
      var actor = authentication.verify(c, CONTEXT, Mutation.DEMOTE, OptionalLong.of(2), NOW);
      var fault = new UserCommandFaults();
      fault.sqlPart = "select count(*)";
      fault.columns.put(FIXTURE_COUNT_COLUMN, 1L);
      denied(
          service.changeRole(fault.wrap(c), actor, new UserId(2), UserRole.USER, 0, META),
          ResultCode.CONFLICT);
      try (var s = c.createStatement();
          var r = s.executeQuery("select role,version from schubert.app_users where id=2")) {
        assertTrue(r.next());
        assertEquals(EXPECTED_ADMIN_ROLE, r.getString(1));
        assertEquals(0, r.getLong(2));
      }
      c.rollback();
    }
    for (UserRole role : UserRole.values()) {
      seed();
      success(
          run(
              role == UserRole.ADMIN ? Mutation.PROMOTE : Mutation.DEMOTE,
              OptionalLong.of(3),
              (c, a) -> service.changeRole(c, a, TARGET, role, 0, META)),
          3,
          1,
          ResultCode.SUCCESS);
      assertUser(
          FIXTURE_ROLE_COLUMN,
          switch (role) {
            case USER -> "USER";
            case ADMIN -> EXPECTED_ADMIN_ROLE;
          });
      assertEquals(
          1,
          count(
              "select count(*) from schubert.auth_sessions where user_id=3 and revoked and"
                  + " revoke_reason='ADMIN'"));
    }
    seed();
    denied(
        run(
            Mutation.DEMOTE,
            OptionalLong.of(1),
            (c, a) -> service.changeRole(c, a, new UserId(1), UserRole.USER, 0, META)),
        ResultCode.CONFLICT);
    denied(
        run(
            Mutation.DISABLE,
            OptionalLong.of(1),
            (c, a) -> service.changeStatus(c, a, new UserId(1), false, 0, META)),
        ResultCode.CONFLICT);
    assertEquals(3, count(FIXTURE_ACTIVE_ADMINS_SQL));
    success(
        run(
            Mutation.DEMOTE,
            OptionalLong.of(2),
            (c, a) -> service.changeRole(c, a, new UserId(2), UserRole.USER, 0, META)),
        2,
        1,
        ResultCode.SUCCESS);
    assertEquals(2, count(FIXTURE_ACTIVE_ADMINS_SQL));
    sql("update schubert.app_users set status='DISABLED' where id=4");
    success(
        run(
            Mutation.DEMOTE,
            OptionalLong.of(4),
            (c, a) -> service.changeRole(c, a, new UserId(4), UserRole.USER, 0, META)),
        4,
        1,
        ResultCode.SUCCESS);
    assertEquals(1, count(FIXTURE_ACTIVE_ADMINS_SQL));
  }

  @Test
  void adm017PasswordResetConsumesSecretsAndRevokesEverySession() throws Exception {
    extraSessions();
    sql(
        "update schubert.app_users set"
            + " username='é-user',username_key='é-user',failed_count=5,failure_window_started_at='2026-09-08T00:00:00Z',locked_until='2026-09-08T00:02:00Z'"
            + " where id=3");
    char[] input = "e\u0301".repeat(12).toCharArray();
    success(
        run(
            Mutation.RESET_PASSWORD,
            OptionalLong.of(3),
            (c, a) -> service.resetPassword(c, a, TARGET, input, 0, META)),
        3,
        1,
        ResultCode.SUCCESS);
    erased(input);
    independentHash(
        value("select password_hash from schubert.app_users where id=3"), "é".repeat(12));
    assertUser(FIXTURE_FAILED_COUNT_COLUMN, "5");
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_users where id=3 and"
                + " locked_until='2026-09-08T00:02:00Z' and"
                + " password_changed_at='2026-09-08T00:01:00Z'"));
    assertEquals(
        3,
        count(
            "select count(*) from schubert.auth_sessions where user_id=3 and"
                + " revoke_reason='PASSWORD_RESET'"));
    assertEquals(
        1,
        count(
            "select count(*) from schubert.app_logs where action='USER_PASSWORD_RESET' and"
                + " category='SECURITY'"));
    char[] own = PASSWORD.toCharArray();
    success(
        run(
            Mutation.RESET_PASSWORD,
            OptionalLong.of(1),
            (c, a) -> service.resetPassword(c, a, new UserId(1), own, 0, META)),
        1,
        1,
        ResultCode.SUCCESS);
    erased(own);
    assertEquals(
        1, count("select count(*) from schubert.auth_sessions where user_id=1 and revoked"));
  }

  @Test
  void adm018UnlockUsesExactExpiryAndNoopVersionRules() throws Exception {
    for (String lock :
        List.of(
            "NULL",
            "'2026-09-08T00:00:59.999999Z'",
            "'2026-09-08T00:01:00Z'",
            "'2026-09-08T00:01:00.000001Z'")) {
      for (long version : new long[] {0, 999_999_999}) {
        seed();
        sql(
            "update schubert.app_users set version="
                + version
                + ",failed_count=5,failure_window_started_at='2026-09-08T00:00:00Z',locked_until="
                + lock
                + " where id=3");
        var result =
            run(
                Mutation.UNLOCK,
                OptionalLong.of(3),
                (c, a) -> service.unlock(c, a, TARGET, version, META));
        boolean active = lock.contains("00.000001");
        if (active && version == 999_999_999) {
          denied(result, ResultCode.RESOURCE_LIMIT);
          assertUser(FIXTURE_FAILED_COUNT_COLUMN, "5");
        } else {
          success(
              result,
              3,
              active ? version + 1 : version,
              active ? ResultCode.SUCCESS : ResultCode.IDEMPOTENT_SUCCESS);
          assertUser(FIXTURE_FAILED_COUNT_COLUMN, active ? "0" : "5");
        }
        assertEquals(0, count("select count(*) from schubert.auth_sessions where revoked"));
        if (active && version == 0)
          assertEquals(
              1,
              count(
                  "select count(*) from schubert.app_users where id=3 and failure_window_started_at"
                      + " is null and locked_until is null"));
      }
    }
    denied(
        run(Mutation.UNLOCK, OptionalLong.of(3), (c, a) -> service.unlock(c, a, TARGET, 0, META)),
        ResultCode.CONFLICT);
  }

  @Test
  void adm019ExpectedVersionDuplicateAndCapacityAreBusinessResults() throws Exception {
    denied(
        run(
            Mutation.ENABLE,
            OptionalLong.of(999),
            (c, a) -> service.changeStatus(c, a, new UserId(999), true, 0, META)),
        ResultCode.NOT_FOUND);
    denied(
        run(
            Mutation.ENABLE,
            OptionalLong.of(3),
            (c, a) -> service.changeStatus(c, a, TARGET, true, 1, META)),
        ResultCode.CONFLICT);
    sql("update schubert.app_users set version=999999999 where id=3");
    denied(
        run(
            Mutation.ENABLE,
            OptionalLong.of(3),
            (c, a) -> service.changeStatus(c, a, TARGET, true, 999_999_999, META)),
        ResultCode.RESOURCE_LIMIT);
    // BUG-046: UI236 §4.2 is the independent oracle, not the production result or field UI.
    for (String name : List.of("u1", "U1", " U1 ")) {
      char[] input = PASSWORD.toCharArray();
      denied(
          run(
              Mutation.CREATE,
              OptionalLong.empty(),
              (c, a) -> service.create(c, a, name, input, UserRole.USER, true, META)),
          ResultCode.CONFLICT);
      erased(input);
    }
    assertEquals(
        3,
        count(
            "select count(*) from schubert.app_logs where action='USER_CREATED' and"
                + " details->>'outcome'='DENIED' and details->>'resultCode'='0105'"));
    for (String name : List.of("", " ", "é", "bad/name", "a".repeat(65), "line\nname")) {
      char[] input = PASSWORD.toCharArray();
      denied(
          run(
              Mutation.CREATE,
              OptionalLong.empty(),
              (c, a) -> service.create(c, a, name, input, UserRole.USER, true, META)),
          ResultCode.VALIDATION_ERROR);
      erased(input);
    }
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("select setval('schubert.app_users_id_seq',999999999999,true)");
    }
    char[] input = PASSWORD.toCharArray();
    denied(
        run(
            Mutation.CREATE,
            OptionalLong.empty(),
            (c, a) -> service.create(c, a, "capacity", input, UserRole.USER, true, META)),
        ResultCode.RESOURCE_LIMIT);
    erased(input);
    assertEquals(4, count("select count(*) from schubert.app_users"));
    assertEquals(
        2, count("select count(*) from schubert.app_logs where details->>'resultCode'='9001'"));
  }

  @Test
  void adm020SqlRevocationAndAuditFailuresRollbackTogether() throws Exception {
    for (Long id : Arrays.asList(null, 0L, 1_000_000_000_000L)) {
      var fault = new UserCommandFaults();
      fault.sqlPart = FIXTURE_INSERT_USERS_PREFIX;
      fault.columns.put("id", id);
      rollbackFault(fault, true);
    }
    for (Instant at : List.of(Instant.MIN, Instant.MAX)) {
      char[] password = PASSWORD.toCharArray();
      try (var c = database.transaction()) {
        infrastructure(
            () ->
                service.create(
                    c,
                    ADMIN,
                    "clock",
                    password,
                    UserRole.USER,
                    true,
                    new UserCommandMetadata(META.messageId(), META.correlationId(), at)));
        c.rollback();
      }
      erased(password);
    }
    var createdDuplicate = new UserCommandFaults();
    createdDuplicate.sqlPart = FIXTURE_INSERT_USERS_PREFIX;
    createdDuplicate.duplicate = true;
    rollbackFault(createdDuplicate, true);
    for (int invalid = 0; invalid < 5; invalid++) {
      var fault = new UserCommandFaults();
      fault.sqlPart = "select count(*)";
      switch (invalid) {
        case 0 -> fault.empty = true;
        case 1 -> fault.duplicate = true;
        case 2 -> fault.columns.put(FIXTURE_COUNT_COLUMN, null);
        case 3 -> fault.columns.put(FIXTURE_COUNT_COLUMN, -1L);
        case 4 -> fault.columns.put(FIXTURE_COUNT_COLUMN, 0L);
        default -> throw new AssertionError();
      }
      rollbackFault(fault, false);
    }
    var oversized = new UserCommandFaults();
    oversized.occurrence = 2;
    oversized.columns.put("username", "x".repeat(1024));
    rollbackFault(oversized, false);
    for (String point : List.of("statementClose", "rollback", "releaseSavepoint")) {
      try (var c = database.admin();
          var s = c.createStatement()) {
        s.execute("select setval('schubert.app_users_id_seq',999999999999,true)");
      }
      var fault = new UserCommandFaults();
      fault.sqlPart = FIXTURE_INSERT_USERS_PREFIX;
      fault.fault = point;
      rollbackFault(fault, true);
      try (var c = database.admin();
          var s = c.createStatement()) {
        s.execute("select setval('schubert.app_users_id_seq',4,true)");
      }
    }
    for (String sql :
        List.of(
            "select id,username",
            FIXTURE_UPDATE_USERS_PREFIX,
            "update schubert.auth_sessions",
            "insert into schubert.app_logs")) {
      for (String point :
          List.of("prepareStatement", "setLong", "executeUpdate", "statementClose")) {
        if (sql.startsWith("select") && point.equals("executeUpdate")) continue;
        if (sql.startsWith("update schubert.auth_sessions") && point.equals("setLong")) continue;
        var fault = new UserCommandFaults();
        fault.sqlPart = sql;
        fault.fault = point;
        rollbackFault(fault, false);
      }
    }
    for (String point :
        List.of(
            "executeQuery",
            "next",
            "getString",
            "getLong",
            "getObject",
            "wasNull",
            "resultClose")) {
      var fault = new UserCommandFaults();
      fault.fault = point;
      rollbackFault(fault, false);
    }
    for (String point :
        List.of("setSavepoint", "releaseSavepoint", "getAutoCommit", "isReadOnly")) {
      var fault = new UserCommandFaults();
      fault.fault = point;
      rollbackFault(fault, true);
    }
    for (String point :
        List.of(
            "prepareStatement",
            "setString",
            "setObject",
            "setLong",
            "executeQuery",
            "next",
            "resultClose",
            "statementClose")) {
      var fault = new UserCommandFaults();
      fault.sqlPart = FIXTURE_INSERT_USERS_PREFIX;
      fault.fault = point;
      rollbackFault(fault, true);
    }
    // Revocation audit then ACTION then SECURITY: failure at each position must erase all changes.
    for (int at : new int[] {1, 2, 3}) {
      var fault = new UserCommandFaults();
      fault.sqlPart = "insert into schubert.app_logs";
      fault.occurrence = at;
      fault.fault = "executeUpdate";
      rollbackFault(fault, false);
    }
    for (String column :
        List.of(
            "id",
            "username",
            FIXTURE_ROLE_COLUMN,
            FIXTURE_STATUS_COLUMN,
            FIXTURE_VERSION_COLUMN,
            FIXTURE_FAILED_COUNT_COLUMN)) {
      var fault = new UserCommandFaults();
      fault.columns.put(column, null);
      rollbackFault(fault, false);
    }
    for (var entry :
        Map.<String, List<Object>>of(
                "id",
                List.of(0L, 4L),
                FIXTURE_ROLE_COLUMN,
                List.of("UNKNOWN"),
                FIXTURE_STATUS_COLUMN,
                List.of("UNKNOWN"),
                FIXTURE_VERSION_COLUMN,
                List.of(-1L, 1_000_000_000L),
                FIXTURE_FAILED_COUNT_COLUMN,
                List.of(-1L, 6L))
            .entrySet()) {
      for (Object value : entry.getValue()) {
        var fault = new UserCommandFaults();
        fault.columns.put(entry.getKey(), value);
        rollbackFault(fault, false);
      }
    }
    var duplicate = new UserCommandFaults();
    duplicate.duplicate = true;
    rollbackFault(duplicate, false);
    for (int changed : new int[] {0, 2}) {
      var fault = new UserCommandFaults();
      fault.sqlPart = FIXTURE_UPDATE_USERS_PREFIX;
      fault.updateCount = changed;
      rollbackFault(fault, false);
    }
    for (int changed : new int[] {0, 2}) {
      var fault = new UserCommandFaults();
      fault.sqlPart = "insert into schubert.app_logs";
      fault.occurrence = 2;
      fault.updateCount = changed;
      rollbackFault(fault, false);
    }
    for (boolean create : new boolean[] {false, true}) {
      var missing = new UserCommandFaults();
      missing.occurrence = create ? 1 : 2;
      missing.empty = true;
      rollbackFault(missing, create);
      var wrongVersion = new UserCommandFaults();
      wrongVersion.occurrence = create ? 1 : 2;
      wrongVersion.columns.put(FIXTURE_VERSION_COLUMN, 2L);
      rollbackFault(wrongVersion, create);
    }
    // Conditional-update zero after a real provider-side version movement remains definite
    // conflict.
    try (var c = database.transaction()) {
      authentication.verify(c, CONTEXT, Mutation.ENABLE, OptionalLong.of(3), NOW);
      var fault = new UserCommandFaults();
      fault.sqlPart = FIXTURE_UPDATE_USERS_PREFIX;
      fault.updateCount = 0;
      fault.beforeUpdate =
          connection -> {
            try (var s = connection.createStatement()) {
              s.executeUpdate("update schubert.app_users set version=1 where id=3");
            }
          };
      denied(
          service.changeStatus(fault.wrap(c), ADMIN, TARGET, true, 0, META), ResultCode.CONFLICT);
      c.rollback();
    }
    assertUser(FIXTURE_VERSION_COLUMN, "0");
    try (var c = database.transaction()) {
      authentication.verify(c, CONTEXT, Mutation.ENABLE, OptionalLong.of(3), NOW);
      var update = new UserCommandFaults();
      update.sqlPart = FIXTURE_UPDATE_USERS_PREFIX;
      update.updateCount = 0;
      var missing = new UserCommandFaults();
      missing.occurrence = 2;
      missing.empty = true;
      denied(
          service.changeStatus(update.wrap(missing.wrap(c)), ADMIN, TARGET, true, 0, META),
          ResultCode.NOT_FOUND);
      c.rollback();
    }
  }

  @Test
  void adm021NullPolicyAndHashFailuresAlwaysErasePasswords() throws Exception {
    var revocations = new AuthSessionRevocationService(new ContextHash());
    assertThrows(
        NullPointerException.class,
        () -> new UserCommandService((PasswordHasher) null, revocations));
    assertThrows(
        NullPointerException.class, () -> new UserCommandService(new PasswordHasher(), null));
    assertThrows(
        NullPointerException.class,
        () -> new UserCommandService((UserCommandService.PasswordEncoding) null, revocations));
    assertThrows(NullPointerException.class, () -> new UserCommandService(p -> TEST_HASH, null));
    for (Executable call :
        List.<Executable>of(
            () -> new UserCommandMetadata(null, META.correlationId(), NOW),
            () -> new UserCommandMetadata(META.messageId(), null, NOW),
            () -> new UserCommandMetadata(META.messageId(), META.correlationId(), null)))
      assertThrows(NullPointerException.class, call);
    try (var c = database.transaction()) {
      for (Executable call :
          List.<Executable>of(
              () -> service.create(c, ADMIN, FIXTURE_NEW_USERNAME, null, UserRole.USER, true, META),
              () -> service.resetPassword(c, ADMIN, TARGET, null, 0, META),
              () -> service.changeStatus(null, ADMIN, TARGET, true, 0, META),
              () -> service.changeStatus(c, null, TARGET, true, 0, META),
              () -> service.changeStatus(c, ADMIN, null, true, 0, META),
              () -> service.changeStatus(c, ADMIN, TARGET, true, 0, null),
              () -> service.changeRole(c, ADMIN, TARGET, null, 0, META)))
        assertThrows(NullPointerException.class, call);
      for (long version : new long[] {-1, 1_000_000_000})
        assertThrows(
            IllegalArgumentException.class, () -> service.unlock(c, ADMIN, TARGET, version, META));
      assertThrows(
          AuthorizationException.class,
          () -> service.unlock(c, new AuthenticatedActor(3, "u3", Role.USER), TARGET, 0, META));
      c.setReadOnly(true);
      infrastructure(() -> service.unlock(c, ADMIN, TARGET, 0, META));
      c.rollback();
      c.setReadOnly(false);
      c.setAutoCommit(true);
      infrastructure(() -> service.unlock(c, ADMIN, TARGET, 0, META));
    }
    for (int missing = 0; missing < 5; missing++) {
      int at = missing;
      char[] password = PASSWORD.toCharArray();
      try (var c = database.transaction()) {
        assertThrows(
            NullPointerException.class,
            () ->
                service.create(
                    at == 0 ? null : c,
                    at == 1 ? null : ADMIN,
                    at == 2 ? null : FIXTURE_NEW_USERNAME,
                    password,
                    at == 3 ? null : UserRole.USER,
                    true,
                    at == 4 ? null : META));
      } finally {
        erased(password);
      }
    }
    for (String bad :
        List.of(
            "",
            "x".repeat(11),
            "x".repeat(129),
            "é".repeat(129),
            "Synthetic-12 ",
            "Synthetic-1\n",
            "Synthetic-1\ud800",
            "newusername1")) {
      char[] password = bad.toCharArray();
      denied(
          run(
              Mutation.CREATE,
              OptionalLong.empty(),
              (c, a) -> service.create(c, a, "newusername1", password, UserRole.USER, true, META)),
          ResultCode.VALIDATION_ERROR);
      erased(password);
      char[] reset = bad.equals("newusername1") ? "u3".toCharArray() : bad.toCharArray();
      denied(
          run(
              Mutation.RESET_PASSWORD,
              OptionalLong.of(3),
              (c, a) -> service.resetPassword(c, a, TARGET, reset, 0, META)),
          ResultCode.VALIDATION_ERROR);
      erased(reset);
    }
    for (int mode = 0; mode < 4; mode++) {
      int choice = mode;
      List<char[]> captured = new ArrayList<>();
      var broken =
          new UserCommandService(
              password -> {
                captured.add(password);
                if (choice == 0) return null;
                if (choice == FIXTURE_UNKNOWN_HASH_MODE) return "unknown-hash";
                if (choice == FIXTURE_ARGUMENT_FAILURE_MODE)
                  throw new IllegalArgumentException("synthetic encoder marker");
                throw new IllegalStateException("synthetic encoder marker");
              },
              revocations);
      for (boolean create : new boolean[] {true, false}) {
        char[] password = PASSWORD.toCharArray();
        try (var c = database.transaction()) {
          infrastructure(
              () -> {
                if (create)
                  broken.create(
                      c, ADMIN, FIXTURE_NEW_USERNAME, password, UserRole.USER, true, META);
                else broken.resetPassword(c, ADMIN, TARGET, password, 0, META);
              });
          c.rollback();
        }
        erased(password);
      }
      assertEquals(2, captured.size());
      captured.forEach(UserCommandServiceTest::erased);
    }
    assertUser("password_hash", "unusable-test-hash");
  }

  @Test
  void adm022ConcurrentMutationsPreserveAdminAndVersionInvariants() throws Exception {
    try (var pool = Executors.newFixedThreadPool(10)) {
      CountDownLatch start = new CountDownLatch(1);
      List<Future<ResultCode>> jobs = new ArrayList<>();
      for (int i = 0; i < 100; i++)
        jobs.add(
            pool.submit(
                () -> {
                  assertTrue(start.await(5, TimeUnit.SECONDS));
                  return run(
                          Mutation.ENABLE,
                          OptionalLong.of(3),
                          (c, a) -> service.changeStatus(c, a, TARGET, true, 0, META))
                      .resultCode();
                }));
      start.countDown();
      int success = 0;
      int conflict = 0;
      for (var job : jobs) {
        var code = job.get(30, TimeUnit.SECONDS);
        if (code == ResultCode.SUCCESS) success++;
        else {
          assertEquals(ResultCode.CONFLICT, code);
          conflict++;
        }
      }
      assertEquals(1, success);
      assertEquals(99, conflict);
    }
    assertUser(FIXTURE_VERSION_COLUMN, "1");
    assertEquals(102, count("select count(*) from schubert.app_logs"));
    seed();
    try (var pool = Executors.newFixedThreadPool(2)) {
      var barrier = new CyclicBarrier(2);
      List<Future<String>> jobs = new ArrayList<>();
      for (int actorId : new int[] {1, 2})
        jobs.add(
            pool.submit(
                () -> {
                  barrier.await(5, TimeUnit.SECONDS);
                  try (var c = database.transaction()) {
                    try {
                      var actor =
                          authentication.verify(
                              c,
                              AuthenticationContext.of((actorId == 1 ? "b" : "c").repeat(64)),
                              Mutation.DEMOTE,
                              OptionalLong.of(actorId == 1 ? 2 : 1),
                              NOW);
                      var result =
                          service.changeRole(
                              c, actor, new UserId(actorId == 1 ? 2 : 1), UserRole.USER, 0, META);
                      c.commit();
                      return result.resultCode().wireValue();
                    } catch (AuthenticationContextException | AuthorizationException denied) {
                      c.rollback();
                      return "DENIED";
                    }
                  }
                }));
      List<String> results = new ArrayList<>();
      for (var job : jobs) results.add(job.get(30, TimeUnit.SECONDS));
      assertEquals(1, Collections.frequency(results, "0000"));
      assertEquals(1, Collections.frequency(results, "DENIED"));
    }
    assertEquals(2, count(FIXTURE_ACTIVE_ADMINS_SQL));
    seed();
    sql(
        FIXTURE_INSERT_PREFIX
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " select"
            + " i,'u'||i,'u'||i,'unusable-test-hash','USER','ACTIVE','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z'"
            + " from generate_series(10,109)i");
    try (var pool = Executors.newFixedThreadPool(10)) {
      List<Future<UserMutationResult>> jobs = new ArrayList<>();
      for (long id = 10; id < 110; id++) {
        long target = id;
        jobs.add(
            pool.submit(
                () ->
                    run(
                        Mutation.ENABLE,
                        OptionalLong.of(target),
                        (c, a) -> service.changeStatus(c, a, new UserId(target), true, 0, META))));
      }
      for (int i = 0; i < 100; i++)
        success(jobs.get(i).get(30, TimeUnit.SECONDS), 10 + i, 1, ResultCode.SUCCESS);
    }
    assertEquals(
        100,
        count("select count(*) from schubert.app_users where id between 10 and 109 and version=1"));
    assertEquals(
        200, count("select count(*) from schubert.app_logs where action='USER_STATUS_CHANGED'"));
  }

  @Test
  void adm023ResultAndAuditProjectionsContainOnlyApprovedFields() throws Exception {
    var result =
        run(
            Mutation.ENABLE,
            OptionalLong.of(3),
            (c, a) -> service.changeStatus(c, a, TARGET, true, 0, META));
    var actual =
        PayloadCodec.standard()
            .encode(
                PayloadTypeCatalog.encode(
                    new TypedPayloadValues(
                        new LayoutId("USTRSP01"), result.data().orElseThrow(), List.of())),
                false);
    // DATA-only response: UI236 offset 0/12/21, lengths 12/9/3.
    assertArrayEquals(
        "000000000003000000001   ".getBytes(StandardCharsets.US_ASCII), actual.copyData());
    assertEquals("UserMutationResult[REDACTED]", result.toString());
    assertEquals("UserCommandMetadata[REDACTED]", META.toString());
    assertEquals(
        NOW,
        new UserCommandMetadata(META.messageId(), META.correlationId(), NOW.plusNanos(999)).at());
    for (ResultCode code : ResultCode.values()) {
      if ((code == ResultCode.SUCCESS || code == ResultCode.IDEMPOTENT_SUCCESS)) {
        assertThrows(
            IllegalArgumentException.class, () -> new UserMutationResult(code, Optional.empty()));
        assertEquals(code, new UserMutationResult(code, result.data()).resultCode());
      } else {
        assertThrows(
            IllegalArgumentException.class, () -> new UserMutationResult(code, result.data()));
        if (Set.of(
                ResultCode.VALIDATION_ERROR,
                ResultCode.NOT_FOUND,
                ResultCode.CONFLICT,
                ResultCode.RESOURCE_LIMIT)
            .contains(code)) denied(new UserMutationResult(code, Optional.empty()), code);
        else
          assertThrows(
              IllegalArgumentException.class, () -> new UserMutationResult(code, Optional.empty()));
      }
    }
    assertThrows(NullPointerException.class, () -> new UserMutationResult(null, Optional.empty()));
    assertThrows(
        NullPointerException.class, () -> new UserMutationResult(ResultCode.SUCCESS, null));
    try (var c = database.api();
        var s = c.createStatement();
        var r =
            s.executeQuery(
                "select * from schubert.app_logs where action='USER_STATUS_CHANGED' order by"
                    + " category")) {
      for (String category : List.of("ACTION", "SECURITY")) {
        assertTrue(r.next());
        assertEquals(category, r.getString("category"));
        assertEquals("INFO", r.getString("level"));
        assertEquals("API", r.getString("service"));
        assertEquals("USER_STATUS_CHANGED", r.getString("message"));
        assertEquals(1, r.getLong("actor_user_id"));
        assertEquals("u1", r.getString("actor_username"));
        assertEquals(NOW, r.getObject("logged_at", java.time.OffsetDateTime.class).toInstant());
        assertEquals(META.messageId(), r.getObject("message_id", UUID.class));
        assertEquals(META.correlationId(), r.getObject("correlation_id", UUID.class));
        var details = JsonParser.parseString(r.getString("details")).getAsJsonObject();
        assertEquals(
            Set.of("outcome", "resultCode", "targetUserId", "targetUsername", "before", "after"),
            details.keySet());
        assertEquals("SUCCESS", details.get("outcome").getAsString());
        assertEquals("0000", details.get("resultCode").getAsString());
        assertEquals(3, details.get("targetUserId").getAsLong());
        assertEquals("u3", details.get("targetUsername").getAsString());
        for (String state : List.of("before", "after")) {
          var fields = details.getAsJsonObject(state);
          assertEquals(
              Set.of(
                  FIXTURE_ROLE_COLUMN,
                  FIXTURE_STATUS_COLUMN,
                  FIXTURE_VERSION_COLUMN,
                  "failedCount",
                  "locked"),
              fields.keySet());
          assertEquals("USER", fields.get(FIXTURE_ROLE_COLUMN).getAsString());
          assertEquals(FIXTURE_ACTIVE_STATE, fields.get(FIXTURE_STATUS_COLUMN).getAsString());
          assertEquals(
              state.equals("before") ? 0 : 1, fields.get(FIXTURE_VERSION_COLUMN).getAsLong());
          assertEquals(0, fields.get("failedCount").getAsInt());
          assertFalse(fields.get("locked").getAsBoolean());
        }
      }
      assertFalse(r.next());
    }
  }

  static void infrastructure(Executable call) {
    RuntimeException failure = assertThrows(RuntimeException.class, call);
    assertTrue(
        failure instanceof TemporaryInfrastructureException
            || failure instanceof AuthenticationInfrastructureException);
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertFalse(failure.toString().contains("marker"));
  }

  static void rollbackFault(UserCommandFaults fault, boolean create) throws Exception {
    try (var c = database.transaction()) {
      authentication.verify(
          c,
          CONTEXT,
          create ? Mutation.CREATE : Mutation.DISABLE,
          create ? OptionalLong.empty() : OptionalLong.of(3),
          NOW);
      char[] password = PASSWORD.toCharArray();
      infrastructure(
          () -> {
            if (create)
              service.create(
                  fault.wrap(c), ADMIN, FIXTURE_NEW_USERNAME, password, UserRole.USER, true, META);
            else service.changeStatus(fault.wrap(c), ADMIN, TARGET, false, 0, META);
          });
      if (create) erased(password);
      c.rollback();
      assertFalse(c.isClosed());
    }
    assertUser(FIXTURE_STATUS_COLUMN, FIXTURE_ACTIVE_STATE);
    assertUser(FIXTURE_VERSION_COLUMN, "0");
    assertEquals(4, count("select count(*) from schubert.app_users"));
    assertEquals(0, count("select count(*) from schubert.auth_sessions where revoked"));
    assertEquals(0, count("select count(*) from schubert.app_logs"));
  }

  private static UserMutationResult run(Mutation kind, OptionalLong target, Command command)
      throws Exception {
    try (var c = database.transaction()) {
      var actor = authentication.verify(c, CONTEXT, kind, target, NOW);
      var result = command.run(c, actor);
      assertFalse(c.isClosed());
      assertFalse(c.getAutoCommit());
      c.commit();
      return result;
    }
  }

  @FunctionalInterface
  interface Command {
    UserMutationResult run(Connection c, AuthenticatedActor actor) throws Exception;
  }

  static void success(UserMutationResult result, long id, long version, ResultCode code) {
    assertEquals(code, result.resultCode());
    assertTrue(result.data().isPresent());
    assertEquals(id, result.data().orElseThrow().userId().value());
    assertEquals(version, result.data().orElseThrow().updatedVersion());
  }

  static void denied(UserMutationResult result, ResultCode code) {
    assertEquals(code, result.resultCode());
    assertTrue(result.data().isEmpty());
  }

  static void erased(char[] input) {
    assertArrayEquals(new char[input.length], input);
  }

  static void independentHash(String stored, String expected) throws Exception {
    assertTrue(stored.matches("\\{pbkdf2-v1}[0-9a-f]{96}"));
    byte[] bytes = HexFormat.of().parseHex(stored.substring(11));
    var specification =
        new PBEKeySpec(expected.toCharArray(), Arrays.copyOf(bytes, 16), 310000, 256);
    try {
      assertArrayEquals(
          Arrays.copyOfRange(bytes, 16, 48),
          SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
              .generateSecret(specification)
              .getEncoded());
    } finally {
      specification.clearPassword();
      Arrays.fill(bytes, (byte) 0);
    }
  }

  static void assertUser(String column, String expected) throws Exception {
    assertEquals(expected, value("select " + column + " from schubert.app_users where id=3"));
  }

  static long count(String sql) throws Exception {
    return Long.parseLong(value(sql));
  }

  static String value(String sql) throws Exception {
    try (var c = database.api();
        var s = c.createStatement();
        var r = s.executeQuery(sql)) {
      assertTrue(r.next());
      String v = r.getString(1);
      assertNotNull(v);
      assertFalse(r.next());
      return v;
    }
  }

  static void sql(String sql) throws Exception {
    try (var c = database.api();
        var s = c.createStatement()) {
      s.execute(sql);
    }
  }

  static void seed() throws Exception {
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("truncate schubert.app_users restart identity cascade");
    }
    sql(
        FIXTURE_INSERT_PREFIX
            + " schubert.app_users(id,username,username_key,password_hash,role,status,password_changed_at,created_at,updated_at)"
            + " select i,'u'||i,'u'||i,'unusable-test-hash',case when i=3 then 'USER' else 'ADMIN'"
            + " end,'ACTIVE','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z'"
            + " from generate_series(1,4)i");
    try (var c = database.admin();
        var s = c.createStatement()) {
      s.execute("select setval('schubert.app_users_id_seq',4,true)");
    }
    try (var c = database.api();
        var s =
            c.prepareStatement(
                FIXTURE_INSERT_PREFIX
                    + " schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)"
                    + " values(?,?,?,decode(repeat('00',29),'hex'),'test','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z','2026-09-08T08:00:00Z','127.0.0.1',?)")) {
      for (int id = 1; id <= 4; id++) {
        String raw = String.valueOf((char) ('a' + id)).repeat(64);
        s.setObject(1, new UUID(0, id));
        s.setInt(2, id);
        s.setString(
            3,
            HexFormat.of()
                .formatHex(
                    MessageDigest.getInstance("SHA-256")
                        .digest(raw.getBytes(StandardCharsets.US_ASCII))));
        s.setObject(4, new UUID(1, id));
        s.executeUpdate();
      }
    }
  }

  static void extraSessions() throws Exception {
    sql(
        FIXTURE_INSERT_PREFIX
            + " schubert.auth_sessions(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id,revoked,revoked_at,revoke_reason)"
            + " select"
            + " ('00000000-0000-0000-0000-'||lpad(i::text,12,'0'))::uuid,3,lpad(i::text,64,'0'),decode(repeat('00',29),'hex'),'test','2026-09-08T00:00:00Z','2026-09-08T00:00:00Z',case"
            + " when i=5 then '2026-09-08T00:00:01Z'::timestamptz else"
            + " '2026-09-08T08:00:00Z'::timestamptz"
            + " end,'127.0.0.1',('00000000-0000-0001-0000-'||lpad(i::text,12,'0'))::uuid,i=7,case"
            + " when i=7 then '2026-09-08T00:00:30Z'::timestamptz end,case when i=7 then 'LOGOUT'"
            + " end from generate_series(5,7)i");
  }
}
