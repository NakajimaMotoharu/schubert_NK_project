package dev.codex.schubert.nk.api.application.admin;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRoleRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserStatusRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserUnlockRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** ADM-AUDIT-PORT001..020. SS351/352: critical audit ports, no authentication/DB/keys. */
final class UserCriticalAuditPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:01:02.123456Z");
  private static final UUID MESSAGE = new UUID(0, 101);
  private static final UUID OPERATION = new UUID(0, 102);
  private static final UserCommandMetadata META = new UserCommandMetadata(MESSAGE, MESSAGE, NOW);
  private static final AuthenticatedActor ADMIN =
      new AuthenticatedActor(7, "public-admin", Role.ADMIN);
  private static final String PREPARE = "prepare";
  private static final String BIND = "bind";
  private static final String EXECUTE = "execute";
  private static final String CLOSE = "close";
  private static final String ACTION = "ACTION";
  private static final String SECURITY = "SECURITY";
  private static final String INFO = "INFO";
  private static final String WARN = "WARN";
  private static final String REPLAY_ACTION = "INBOX_REPLAYED";
  private static final String AUTH_ACTION = "AUTHORIZATION_DENIED";
  private static final String PROTOCOL_ACTION = "PROTOCOL_REJECTED";
  private static final String MQ = "MQ";
  private static final String USER_TARGET = "USER";
  private static final String TARGET_NAME = "targetUsername";
  private static final String ACTOR_ROLE = "actorRole";
  private static final String TARGET_ID = "targetUserId";
  private static final String OUTCOME = "outcome";
  private static final String REASON = "reason";
  private static final String LAYOUT = "layout";
  private static final String TARGET_TYPE = "targetType";
  private static final String STEP = "step";
  private static final String RESULT = "resultCode";
  private static final String BEFORE = "before";
  private static final String AFTER = "after";
  private static final String SAFE_FAULT = "public JDBC fixture";
  private static final String SELECT_LAYOUT = "UDTREQ01";
  private static final String STATUS_LAYOUT = "USTREQ01";
  private static final String USER_NAME = "public-target";
  private static final String SQL =
      "insert into schubert.app_logs(logged_at,service,category,level,action,message,"
          + " message_id,correlation_id,actor_user_id,actor_username,details) values"
          + " (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))";
  private static final List<ActionCase> ACTIONS =
      List.of(
          new ActionCase(Mutation.CREATE, "USER_CREATED", true),
          new ActionCase(Mutation.ENABLE, "USER_STATUS_CHANGED", true),
          new ActionCase(Mutation.DISABLE, "USER_STATUS_CHANGED", true),
          new ActionCase(Mutation.PROMOTE, "USER_ROLE_CHANGED", true),
          new ActionCase(Mutation.DEMOTE, "USER_ROLE_CHANGED", true),
          new ActionCase(Mutation.RESET_PASSWORD, "USER_PASSWORD_RESET", false),
          new ActionCase(Mutation.UNLOCK, "USER_UNLOCKED", false));
  private static final List<QueryCase> QUERIES =
      List.of(
          new QueryCase(
              UserQueryAuditWriter.Event.SESSION_INVALID,
              SECURITY,
              INFO,
              AUTH_ACTION,
              "AUTH_CONTEXT"),
          new QueryCase(
              UserQueryAuditWriter.Event.ROLE_DENIED, SECURITY, WARN, AUTH_ACTION, "ADMIN_ROLE"),
          new QueryCase(
              UserQueryAuditWriter.Event.MESSAGE_MISMATCH,
              MQ,
              WARN,
              PROTOCOL_ACTION,
              "MESSAGE_IDENTITY"),
          new QueryCase(
              UserQueryAuditWriter.Event.REPLAY, MQ, INFO, REPLAY_ACTION, "SAVED_RESULT"));
  private static final List<AdmissionCase> ADMISSIONS =
      List.of(
          new AdmissionCase(
              UserRequestAuditWriter.Event.SESSION_INVALID,
              SECURITY,
              INFO,
              AUTH_ACTION,
              RESULT,
              "0102"),
          new AdmissionCase(
              UserRequestAuditWriter.Event.ROLE_DENIED,
              SECURITY,
              WARN,
              AUTH_ACTION,
              RESULT,
              "0103"),
          new AdmissionCase(
              UserRequestAuditWriter.Event.TOKEN_MISMATCH,
              SECURITY,
              WARN,
              "USER_STATUS_CHANGED",
              RESULT,
              "0105"),
          new AdmissionCase(
              UserRequestAuditWriter.Event.MESSAGE_MISMATCH,
              MQ,
              WARN,
              PROTOCOL_ACTION,
              STEP,
              "MESSAGE_IDENTITY"),
          new AdmissionCase(
              UserRequestAuditWriter.Event.REPLAY, MQ, INFO, REPLAY_ACTION, "count", "1"));

  @Test
  void audit001BusinessSuccessCatalogHasActionThenSecurityExceptResetUnlock() throws Exception {
    for (ActionCase expected : ACTIONS) {
      var f = new Jdbc();
      new UserAuditWriter()
          .write(
              f.connection(),
              ADMIN,
              expected.kind(),
              change(true, Optional.empty(), Optional.empty(), Optional.of(new UserId(5))),
              META);
      assertEquals(expected.action(), UserAuditWriter.action(expected.kind()));
      assertEquals(expected.businessAction() ? 2 : 1, f.writes.size());
      for (int index = 0; index < f.writes.size(); index++) {
        Map<Integer, Object> values = f.writes.get(index);
        columns(
            f,
            values,
            expected.businessAction() && index == 0 ? ACTION : SECURITY,
            INFO,
            expected.action(),
            ADMIN);
        assertEquals(
            JsonParser.parseString(
                "{\"outcome\":\"SUCCESS\",\"resultCode\":\"0000\",\"targetUserId\":5}"),
            json(values));
      }
    }
  }

  @Test
  void audit002EveryDefiniteDenialWritesOnlySecurityWithClosedResult() throws Exception {
    for (ResultCode code :
        List.of(
            ResultCode.VALIDATION_ERROR,
            ResultCode.NOT_FOUND,
            ResultCode.CONFLICT,
            ResultCode.RESOURCE_LIMIT)) {
      for (ActionCase expected : ACTIONS) {
        var f = new Jdbc();
        var change =
            new UserCommandService.Change(
                new UserMutationResult(code, Optional.empty()),
                Optional.empty(),
                Optional.empty(),
                Optional.empty());
        new UserAuditWriter().write(f.connection(), ADMIN, expected.kind(), change, META);
        assertEquals(1, f.writes.size());
        var values = f.writes.getFirst();
        columns(f, values, SECURITY, WARN, expected.action(), ADMIN);
        assertEquals("DENIED", json(values).get(OUTCOME).getAsString());
        assertEquals(
            Map.of(
                    ResultCode.VALIDATION_ERROR,
                    "0100",
                    ResultCode.NOT_FOUND,
                    "0104",
                    ResultCode.CONFLICT,
                    "0105",
                    ResultCode.RESOURCE_LIMIT,
                    "9001")
                .get(code),
            json(values).get(RESULT).getAsString());
        assertEquals(2, json(values).size());
      }
    }
  }

  @Test
  void audit003BeforeAfterStateProjectionMatchesLiteralContract() throws Exception {
    var f = new Jdbc();
    var before = state("old", UserRole.USER, false, 1, Optional.of(NOW.plusSeconds(1)), 3);
    var after = state("new", UserRole.ADMIN, true, 2, Optional.of(NOW), 0);
    new UserAuditWriter()
        .write(
            f.connection(),
            ADMIN,
            Mutation.PROMOTE,
            change(true, Optional.of(before), Optional.of(after), Optional.of(new UserId(5))),
            META);
    var expected =
        JsonParser.parseString(
            "{\"outcome\":\"SUCCESS\",\"resultCode\":\"0000\",\"targetUserId\":5,\"before\":{\"role\":\"USER\",\"status\":\"DISABLED\",\"version\":1,\"failedCount\":3,\"locked\":true},\"after\":{\"role\":\"ADMIN\",\"status\":\"ACTIVE\",\"version\":2,\"failedCount\":0,\"locked\":false},\"targetUsername\":\"new\"}");
    assertEquals(expected, json(f.writes.getFirst()));
    assertEquals(expected, json(f.writes.getLast()));
  }

  @Test
  void audit004MissingStateOmitsFieldsAndLockTimeBoundaryIsStrict() throws Exception {
    for (Optional<Instant> locked :
        List.of(
            Optional.<Instant>empty(),
            Optional.of(NOW.minusSeconds(1)),
            Optional.of(NOW),
            Optional.of(NOW.plusNanos(1)))) {
      var f = new Jdbc();
      var after = state(USER_NAME, UserRole.USER, true, 9, locked, 1);
      new UserAuditWriter()
          .write(
              f.connection(),
              ADMIN,
              Mutation.ENABLE,
              change(true, Optional.empty(), Optional.of(after), Optional.empty()),
              META);
      var details = json(f.writes.getFirst());
      assertFalse(details.has(BEFORE));
      assertFalse(details.has(TARGET_ID));
      assertEquals(
          locked.isPresent() && locked.orElseThrow().isAfter(NOW),
          details.getAsJsonObject(AFTER).get("locked").getAsBoolean());
      assertEquals(USER_NAME, details.get(TARGET_NAME).getAsString());
    }
  }

  @Test
  void audit005UsernameUsesAfterThenBeforeAndNfcControlsAreSanitized() throws Exception {
    var f = new Jdbc();
    var actor = new AuthenticatedActor(8, "e\u0301\r\n\t\u2028\u2029", Role.USER);
    var before = state("e\u0301\r\n\t\u2028\u2029", UserRole.USER, true, 1, Optional.empty(), 0);
    new UserAuditWriter()
        .write(
            f.connection(),
            actor,
            Mutation.DISABLE,
            change(false, Optional.of(before), Optional.empty(), Optional.of(new UserId(5))),
            META);
    assertEquals("é     ", f.writes.getFirst().get(9));
    assertEquals("é     ", json(f.writes.getFirst()).get(TARGET_NAME).getAsString());
    assertFalse(json(f.writes.getFirst()).has(AFTER));
    assertEquals(1, f.writes.size());
  }

  @Test
  void audit006Utf8Limit1024And1025UseIndependentLiteralJsonSize() throws Exception {
    String prefix =
        "{\"outcome\":\"DENIED\",\"resultCode\":\"0105\",\"before\":{\"role\":\"USER\",\"status\":\"ACTIVE\",\"version\":1,\"failedCount\":0,\"locked\":false},\"targetUsername\":\"";
    String suffix = "\"}";
    int fixed = (prefix + suffix).getBytes(StandardCharsets.UTF_8).length;
    for (int size : new int[] {1024, 1025}) {
      int bytes = size - fixed;
      String name = "é".repeat(bytes / 2) + (bytes % 2 == 0 ? "" : "x");
      String expected = prefix + name + suffix;
      assertEquals(size, expected.getBytes(StandardCharsets.UTF_8).length);
      var f = new Jdbc();
      var before = state(name, UserRole.USER, true, 1, Optional.empty(), 0);
      var value = change(false, Optional.of(before), Optional.empty(), Optional.empty());
      if (size == 1024) {
        new UserAuditWriter().write(f.connection(), ADMIN, Mutation.DISABLE, value, META);
        assertEquals(1, f.writes.size());
        assertEquals(expected, f.writes.getFirst().get(10));
      } else {
        assertEquals(
            "user audit exceeds limit",
            assertThrows(
                    SQLException.class,
                    () ->
                        new UserAuditWriter()
                            .write(f.connection(), ADMIN, Mutation.DISABLE, value, META))
                .getMessage());
        assertEquals(List.of(), f.operations);
      }
    }
  }

  @Test
  void audit007AllWritersRequireOneAffectedRow() {
    for (int mode = 0; mode < 3; mode++)
      for (int rows : new int[] {0, 2}) {
        var f = new Jdbc();
        f.affected = rows;
        int operation = mode;
        var error = assertThrows(SQLException.class, () -> operate(f.connection(), operation));
        assertEquals(
            List.of(
                    "critical user audit did not create one row",
                    "critical user admission audit did not create one row",
                    "critical user query audit did not create one row")
                .get(mode),
            error.getMessage());
        assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
      }
  }

  @Test
  void audit008BusinessFirstOrSecondSqlFailureStopsWithoutOwningConnection() {
    for (int ordinal : new int[] {1, 2})
      for (String phase : List.of(PREPARE, BIND, EXECUTE, CLOSE)) {
        var f = new Jdbc();
        var failure = new SQLException(SAFE_FAULT);
        f.failAt = phase;
        f.failOrdinal = ordinal;
        f.failure = failure;
        assertSame(
            failure,
            assertThrows(
                SQLException.class,
                () ->
                    new UserAuditWriter()
                        .write(
                            f.connection(),
                            ADMIN,
                            Mutation.CREATE,
                            change(true, Optional.empty(), Optional.empty(), Optional.empty()),
                            META)));
        assertEquals(ordinal, f.prepared);
        assertEquals(ordinal - (phase.equals(PREPARE) ? 1 : 0), f.closes);
      }
  }

  @Test
  void audit009BusinessRequiredInputsRejectNullAndCloseOwnedStatements() {
    var writer = new UserAuditWriter();
    var value = change(true, Optional.empty(), Optional.empty(), Optional.empty());
    var f = new Jdbc();
    assertThrows(
        NullPointerException.class, () -> writer.write(null, ADMIN, Mutation.CREATE, value, META));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(f.connection(), null, Mutation.CREATE, value, META));
    assertThrows(
        NullPointerException.class, () -> writer.write(f.connection(), ADMIN, null, value, META));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(f.connection(), ADMIN, Mutation.CREATE, null, META));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(f.connection(), ADMIN, Mutation.CREATE, value, null));
    assertEquals(f.prepared, f.closes);
  }

  @Test
  void audit010QueryAllClosedEventsAndOptionalActorMatchIndependentTable() throws Exception {
    for (QueryCase expected : QUERIES)
      for (boolean present : new boolean[] {false, true}) {
        var f = new Jdbc();
        new UserQueryAuditWriter()
            .write(
                f.connection(),
                present ? Optional.of(ADMIN) : Optional.empty(),
                query(),
                expected.event(),
                NOW);
        assertEquals(1, f.writes.size());
        var values = f.writes.getFirst();
        optionalColumns(
            f, values, expected.category(), expected.level(), expected.action(), present);
        var details = json(values);
        assertEquals(SELECT_LAYOUT, details.get(LAYOUT).getAsString());
        assertEquals(expected.event().name(), details.get(REASON).getAsString());
        assertEquals(USER_TARGET, details.get(TARGET_TYPE).getAsString());
        assertEquals(expected.step(), details.get(STEP).getAsString());
        assertEquals(
            expected.event() == UserQueryAuditWriter.Event.REPLAY ? "REPLAY" : "DENIED",
            details.get(OUTCOME).getAsString());
        assertEquals(present, details.has(ACTOR_ROLE));
        if (present) assertEquals("ADMIN", details.get(ACTOR_ROLE).getAsString());
        assertEquals(present ? 6 : 5, details.size());
      }
  }

  @Test
  void audit011QueryMissingInputsAreContractFailures() {
    var f = new Jdbc();
    var writer = new UserQueryAuditWriter();
    var request = query();
    var event = UserQueryAuditWriter.Event.REPLAY;
    assertThrows(
        NullPointerException.class,
        () -> writer.write(null, Optional.of(ADMIN), request, event, NOW));
    assertThrows(
        NullPointerException.class, () -> writer.write(f.connection(), null, request, event, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(f.connection(), Optional.of(ADMIN), null, event, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(f.connection(), Optional.of(ADMIN), request, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(f.connection(), Optional.of(ADMIN), request, event, null));
    assertEquals(f.prepared, f.closes);
  }

  @Test
  void audit012QuerySqlFailuresKeepIdentityAndCloseStatement() {
    faultsFor(2);
  }

  @Test
  void audit013AdmissionClosedCatalogAndOptionalActorMatchIndependentTable() throws Exception {
    for (AdmissionCase expected : ADMISSIONS)
      for (boolean present : new boolean[] {false, true}) {
        var f = new Jdbc();
        try (var request = mutation(Mutation.ENABLE)) {
          new UserRequestAuditWriter()
              .write(
                  f.connection(),
                  present ? Optional.of(ADMIN) : Optional.empty(),
                  request,
                  expected.event(),
                  NOW);
        }
        assertEquals(1, f.writes.size());
        var values = f.writes.getFirst();
        optionalColumns(
            f, values, expected.category(), expected.level(), expected.action(), present);
        var details = json(values);
        assertEquals(STATUS_LAYOUT, details.get(LAYOUT).getAsString());
        assertEquals(expected.event().name(), details.get(REASON).getAsString());
        assertEquals("ENABLE", details.get("operation").getAsString());
        assertEquals(USER_TARGET, details.get(TARGET_TYPE).getAsString());
        assertEquals(5, details.get(TARGET_ID).getAsLong());
        assertEquals(expected.result(), details.get(expected.field()).getAsString());
        if (expected.field().equals("count"))
          assertTrue(details.get("count").getAsJsonPrimitive().isNumber());
        assertEquals(
            expected.event() == UserRequestAuditWriter.Event.REPLAY ? "REPLAY" : "DENIED",
            details.get(OUTCOME).getAsString());
        assertEquals(present, details.has(ACTOR_ROLE));
        assertEquals(present ? 8 : 7, details.size());
      }
  }

  @Test
  void audit014AdmissionCreateOmitsTargetAndNeverContainsRequestValues() throws Exception {
    var f = new Jdbc();
    try (var request = mutation(Mutation.CREATE)) {
      new UserRequestAuditWriter()
          .write(
              f.connection(),
              Optional.of(ADMIN),
              request,
              UserRequestAuditWriter.Event.REPLAY,
              NOW);
    }
    var details = json(f.writes.getFirst());
    assertFalse(details.has(TARGET_ID));
    assertEquals("UCRREQ01", details.get(LAYOUT).getAsString());
    assertEquals("CREATE", details.get("operation").getAsString());
    assertFalse(details.toString().contains(USER_NAME));
    assertFalse(details.toString().contains(OPERATION.toString()));
    assertFalse(details.has("password"));
    assertFalse(details.has("context"));
    assertFalse(details.has("username"));
  }

  @Test
  void audit015AdmissionTokenMismatchUsesEveryMutationActionWithoutInputSecrets() throws Exception {
    for (ActionCase expected : ACTIONS) {
      var f = new Jdbc();
      try (var request = mutation(expected.kind())) {
        new UserRequestAuditWriter()
            .write(
                f.connection(),
                Optional.of(ADMIN),
                request,
                UserRequestAuditWriter.Event.TOKEN_MISMATCH,
                NOW);
      }
      var values = f.writes.getFirst();
      assertEquals(expected.action(), values.get(4));
      assertEquals(SECURITY, values.get(2));
      var details = json(values);
      assertEquals("0105", details.get(RESULT).getAsString());
      assertEquals(expected.kind().name(), details.get("operation").getAsString());
      assertFalse(details.toString().contains(OPERATION.toString()));
    }
  }

  @Test
  void audit016AdmissionMissingOrClosedRequestIsNotSuccessfulAudit() {
    var f = new Jdbc();
    var writer = new UserRequestAuditWriter();
    try (var request = mutation(Mutation.ENABLE)) {
      var event = UserRequestAuditWriter.Event.REPLAY;
      assertThrows(
          NullPointerException.class,
          () -> writer.write(null, Optional.of(ADMIN), request, event, NOW));
      assertThrows(
          NullPointerException.class,
          () -> writer.write(f.connection(), null, request, event, NOW));
      assertThrows(
          NullPointerException.class,
          () -> writer.write(f.connection(), Optional.of(ADMIN), null, event, NOW));
      assertThrows(
          NullPointerException.class,
          () -> writer.write(f.connection(), Optional.of(ADMIN), request, null, NOW));
      assertThrows(
          NullPointerException.class,
          () -> writer.write(f.connection(), Optional.of(ADMIN), request, event, null));
    }
    var closed = mutation(Mutation.ENABLE);
    closed.close();
    assertThrows(
        IllegalStateException.class,
        () ->
            writer.write(
                f.connection(),
                Optional.of(ADMIN),
                closed,
                UserRequestAuditWriter.Event.REPLAY,
                NOW));
    assertEquals(f.prepared, f.closes);
  }

  @Test
  void audit017AdmissionSqlFailuresKeepIdentityAndCloseStatement() {
    faultsFor(1);
  }

  @Test
  void audit018ConcurrentWritersHaveNoSharedBindOrConnectionState() throws Exception {
    try (var workers = Executors.newFixedThreadPool(3)) {
      var first = workers.submit(() -> writeOne(0));
      var second = workers.submit(() -> writeOne(1));
      var third = workers.submit(() -> writeOne(2));
      assertEquals("USER_UNLOCKED", first.get(5, TimeUnit.SECONDS));
      assertEquals(REPLAY_ACTION, second.get(5, TimeUnit.SECONDS));
      assertEquals(REPLAY_ACTION, third.get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void audit019UnknownRuntimeAndErrorAreNotNormalizedAsSuccessfulAudit() {
    for (int mode = 0; mode < 3; mode++)
      for (Throwable fault :
          List.of(new IllegalStateException(SAFE_FAULT), new AssertionError(SAFE_FAULT))) {
        var f = new Jdbc();
        f.failAt = EXECUTE;
        f.failure = fault;
        int selected = mode;
        assertSame(fault, assertThrows(fault.getClass(), () -> operate(f.connection(), selected)));
        assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
      }
  }

  @Test
  void audit020PrimarySqlFailureRetainsSuppressedCloseAndBorrowedOwnership() {
    for (int mode = 0; mode < 3; mode++) {
      var f = new Jdbc();
      var primary = new SQLException(SAFE_FAULT);
      var close = new SQLException("public close fixture");
      f.failure = primary;
      f.failAt = EXECUTE;
      f.closeFailure = close;
      int selected = mode;
      assertSame(
          primary, assertThrows(SQLException.class, () -> operate(f.connection(), selected)));
      assertEquals(1, primary.getSuppressed().length);
      assertSame(close, primary.getSuppressed()[0]);
      assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
    }
  }

  private static void faultsFor(int operation) {
    for (String phase : List.of(PREPARE, BIND, EXECUTE, CLOSE)) {
      var f = new Jdbc();
      var fault = new SQLException(SAFE_FAULT);
      f.failAt = phase;
      f.failure = fault;
      assertSame(fault, assertThrows(SQLException.class, () -> operate(f.connection(), operation)));
      assertEquals(phase.equals(PREPARE) ? 0 : 1, f.closes);
    }
  }

  private static String writeOne(int operation) throws SQLException {
    var f = new Jdbc();
    operate(f.connection(), operation);
    assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
    return (String) f.writes.getFirst().get(4);
  }

  private static void operate(@Nullable Connection connection, int operation) throws SQLException {
    switch (operation) {
      case 0 ->
          new UserAuditWriter()
              .write(
                  connection,
                  ADMIN,
                  Mutation.UNLOCK,
                  change(true, Optional.empty(), Optional.empty(), Optional.empty()),
                  META);
      case 1 -> {
        try (var request = mutation(Mutation.ENABLE)) {
          new UserRequestAuditWriter()
              .write(
                  connection,
                  Optional.of(ADMIN),
                  request,
                  UserRequestAuditWriter.Event.REPLAY,
                  NOW);
        }
      }
      case 2 ->
          new UserQueryAuditWriter()
              .write(
                  connection, Optional.of(ADMIN), query(), UserQueryAuditWriter.Event.REPLAY, NOW);
      default -> throw new AssertionError("unknown audit fixture mode");
    }
  }

  private static void columns(
      Jdbc f,
      Map<Integer, Object> values,
      String category,
      String level,
      String action,
      AuthenticatedActor actor) {
    assertEquals(SQL, f.sqls.getFirst().replaceAll("\\s+", " ").strip());
    assertEquals(10, values.size());
    assertEquals(NOW.atOffset(ZoneOffset.UTC), values.get(1));
    assertEquals(category, values.get(2));
    assertEquals(level, values.get(3));
    assertEquals(action, values.get(4));
    assertEquals(action, values.get(5));
    assertEquals(MESSAGE, values.get(6));
    assertEquals(MESSAGE, values.get(7));
    assertEquals(actor.userId(), values.get(8));
    assertEquals(actor.username(), values.get(9));
  }

  private static void optionalColumns(
      Jdbc f,
      Map<Integer, Object> values,
      String category,
      String level,
      String action,
      boolean present) {
    if (present) columns(f, values, category, level, action, ADMIN);
    else {
      assertEquals(SQL, f.sqls.getFirst().replaceAll("\\s+", " ").strip());
      assertEquals(8, values.size());
      assertEquals(category, values.get(2));
      assertEquals(level, values.get(3));
      assertEquals(action, values.get(4));
      assertEquals(action, values.get(5));
      assertEquals(NOW.atOffset(ZoneOffset.UTC), values.get(1));
      assertEquals(MESSAGE, values.get(6));
      assertEquals(MESSAGE, values.get(7));
      assertEquals(Map.of(8, Types.BIGINT, 9, Types.VARCHAR), f.nullTypes);
    }
  }

  private static JsonObject json(Map<Integer, Object> values) {
    return JsonParser.parseString((String) values.get(10)).getAsJsonObject();
  }

  private static UserCommandService.State state(
      String name,
      UserRole role,
      boolean enabled,
      long version,
      Optional<Instant> lock,
      int count) {
    return new UserCommandService.State(new UserId(5), name, role, enabled, version, lock, count);
  }

  private static UserCommandService.Change change(
      boolean success,
      Optional<UserCommandService.State> before,
      Optional<UserCommandService.State> after,
      Optional<UserId> target) {
    var result =
        success
            ? new UserMutationResult(
                ResultCode.SUCCESS,
                Optional.of(
                    new dev.codex.schubert.nk.protocol.layout.admin.UserMutationResponseData(
                        new UserId(5), 2)))
            : new UserMutationResult(ResultCode.CONFLICT, Optional.empty());
    return new UserCommandService.Change(result, before, after, target);
  }

  private static UserQueryRequest query() {
    return UserQueryRequest.decode(wire(SELECT_LAYOUT, new UserDetailRequestData(new UserId(5))));
  }

  private static UserMutationRequest mutation(Mutation kind) {
    PayloadData data;
    String layout;
    // Only public zero-format input fields; no issued password/token/context, no auth operation.
    switch (kind) {
      case CREATE -> {
        layout = "UCRREQ01";
        data = new UserCreateRequestData(USER_NAME, "0".repeat(12), UserRole.USER, true, OPERATION);
      }
      case ENABLE, DISABLE -> {
        layout = STATUS_LAYOUT;
        data = new UserStatusRequestData(new UserId(5), kind == Mutation.ENABLE, 1, OPERATION);
      }
      case PROMOTE, DEMOTE -> {
        layout = "URLREQ01";
        data =
            new UserRoleRequestData(
                new UserId(5),
                kind == Mutation.PROMOTE ? UserRole.ADMIN : UserRole.USER,
                1,
                OPERATION);
      }
      case RESET_PASSWORD -> {
        layout = "UPWREQ01";
        data = new PasswordResetRequestData(new UserId(5), "0".repeat(12), 1, OPERATION);
      }
      case UNLOCK -> {
        layout = "ULKREQ01";
        data = new UserUnlockRequestData(new UserId(5), 1, OPERATION);
      }
      default -> throw new AssertionError("unsupported fixture mutation");
    }
    return UserMutationRequest.decode(wire(layout, data));
  }

  private static WireMessage<dev.codex.schubert.nk.protocol.layout.FixedPayload> wire(
      String layout, PayloadData data) {
    var id = new LayoutId(layout);
    var values = new TypedPayloadValues(id, data, List.of());
    // Production encoder supplies only the input DTO fixture; every audit expectation is
    // hand-authored.
    var payload = PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false);
    int size = payload.copyData().length;
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            id,
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            MESSAGE,
            MESSAGE,
            NOW.truncatedTo(ChronoUnit.MILLIS),
            Optional.of(AuthenticationContext.of("0".repeat(64))),
            256,
            size,
            0,
            0,
            256 + size,
            Optional.empty());
    return new WireMessage<>(header, payload);
  }

  private record ActionCase(Mutation kind, String action, boolean businessAction) {}

  private record QueryCase(
      UserQueryAuditWriter.Event event,
      String category,
      String level,
      String action,
      String step) {}

  private record AdmissionCase(
      UserRequestAuditWriter.Event event,
      String category,
      String level,
      String action,
      String field,
      String result) {}

  private static final class Jdbc {
    final List<Map<Integer, Object>> writes = new ArrayList<>();
    final Map<Integer, Integer> nullTypes = new HashMap<>();
    final List<String> sqls = new ArrayList<>();
    final List<String> operations = new ArrayList<>();
    String failAt = "";
    int failOrdinal = 1;
    int prepared;
    int closes;
    int affected = 1;
    @Nullable Throwable failure;
    @Nullable Throwable closeFailure;

    private void fail(String phase, int ordinal) throws Throwable {
      if (failAt.equals(phase) && failOrdinal == ordinal && failure != null) throw failure;
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (!method.getName().equals("prepareStatement"))
                  throw new AssertionError("borrowed connection method forbidden");
                operations.add(PREPARE);
                prepared++;
                fail(PREPARE, prepared);
                sqls.add((String) args[0]);
                return statement(prepared);
              });
    }

    private PreparedStatement statement(int ordinal) {
      var binds = new LinkedHashMap<Integer, Object>();
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.startsWith("set")) {
                  fail(BIND, ordinal);
                  if (name.equals("setNull")) nullTypes.put((int) args[0], (int) args[1]);
                  else binds.put((int) args[0], args[1]);
                  return null;
                }
                if (name.equals("executeUpdate")) {
                  operations.add(EXECUTE);
                  fail(EXECUTE, ordinal);
                  writes.add(Map.copyOf(binds));
                  return affected;
                }
                if (name.equals(CLOSE)) {
                  operations.add(CLOSE);
                  closes++;
                  if (closeFailure != null) throw closeFailure;
                  fail(CLOSE, ordinal);
                  return null;
                }
                throw new AssertionError("unexpected statement operation");
              });
    }
  }
}
