package dev.codex.schubert.nk.api.application.question;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadData;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.NotificationCancelRequestData;
import dev.codex.schubert.nk.protocol.layout.question.NotificationDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDeleteRequestData;
import dev.codex.schubert.nk.protocol.layout.question.QuestionDetailRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.NotificationId;
import dev.codex.schubert.nk.protocol.layout.semantic.QuestionId;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.time.DateTimeException;
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

/** QRY-AUDIT-PORT001..008; SS351352/SSC157: audit metadata only, no business/DB/auth operation. */
final class QuestionCriticalAuditPortTest {
  private static final Instant NOW = Instant.parse("2026-11-06T00:00:01.123456Z");
  private static final UUID MESSAGE = new UUID(0, 101);
  private static final UUID OPERATION = new UUID(0, 103);
  private static final AuthenticatedActor ACTOR =
      new AuthenticatedActor(7, "public-reader", Role.USER);
  private static final String SECURITY = "SECURITY";
  private static final String MQ = "MQ";
  private static final String INFO = "INFO";
  private static final String WARN = "WARN";
  private static final String AUTH_ACTION = "AUTHORIZATION_DENIED";
  private static final String OWNER_ACTION = "OWNER_SCOPE_DENIED";
  private static final String PROTOCOL_ACTION = "PROTOCOL_REJECTED";
  private static final String REPLAY_ACTION = "INBOX_REPLAYED";
  private static final String TARGET = "targetType";
  private static final String ROLE = "actorRole";
  private static final String LAYOUT = "layout";
  private static final String REASON = "reason";
  private static final String STEP = "step";
  private static final String OUTCOME = "outcome";
  private static final String QUESTION = "QUESTION";
  private static final String NOTIFICATION = "NOTIFICATION";
  private static final String PREPARE = "prepare";
  private static final String BIND = "bind";
  private static final String EXECUTE = "execute";
  private static final String CLOSE = "close";
  private static final String SAFE_FAULT = "public fixture";
  private static final String QUERY_SQL =
      "insert into schubert.app_logs(logged_at,service,category,level,action,message,"
          + " message_id,correlation_id,actor_user_id,actor_username,details) values"
          + " (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))";
  private static final String MUTATION_SQL =
      "insert into"
          + " schubert.app_logs(logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,actor_username,details)"
          + " values (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))";
  private static final List<QueryCase> QUERIES =
      List.of(
          new QueryCase(
              QuestionQueryAuditWriter.Event.SESSION_INVALID,
              AUTH_ACTION,
              SECURITY,
              INFO,
              "AUTH_CONTEXT"),
          new QueryCase(
              QuestionQueryAuditWriter.Event.ROLE_DENIED,
              AUTH_ACTION,
              SECURITY,
              WARN,
              "SAVED_SCOPE"),
          new QueryCase(
              QuestionQueryAuditWriter.Event.OWNER_DENIED,
              OWNER_ACTION,
              SECURITY,
              WARN,
              "SAVED_SCOPE"),
          new QueryCase(
              QuestionQueryAuditWriter.Event.VALIDATION,
              AUTH_ACTION,
              SECURITY,
              WARN,
              "REQUEST_VALIDATION"),
          new QueryCase(
              QuestionQueryAuditWriter.Event.MESSAGE_MISMATCH,
              PROTOCOL_ACTION,
              MQ,
              WARN,
              "MESSAGE_IDENTITY"),
          new QueryCase(
              QuestionQueryAuditWriter.Event.REPLAY, REPLAY_ACTION, MQ, INFO, "SAVED_RESULT"));
  private static final List<MutationCase> MUTATIONS =
      List.of(
          new MutationCase(
              QuestionMutationAuditWriter.Event.SESSION_INVALID,
              AUTH_ACTION,
              SECURITY,
              INFO,
              false),
          new MutationCase(
              QuestionMutationAuditWriter.Event.OWNER_DENIED, OWNER_ACTION, SECURITY, WARN, false),
          new MutationCase(
              QuestionMutationAuditWriter.Event.TOKEN_MISMATCH, AUTH_ACTION, SECURITY, WARN, false),
          new MutationCase(
              QuestionMutationAuditWriter.Event.MESSAGE_MISMATCH, PROTOCOL_ACTION, MQ, WARN, false),
          new MutationCase(
              QuestionMutationAuditWriter.Event.REPLAY, REPLAY_ACTION, MQ, INFO, false),
          new MutationCase(
              QuestionMutationAuditWriter.Event.CAPACITY,
              "RESOURCE_LIMIT_REACHED",
              "SYSTEM",
              "ERROR",
              true));

  @Test
  void port001EveryQueryEventBothScopesAndActorStatesMatchesIndependentTable() throws Exception {
    for (QueryCase expected : QUERIES)
      for (boolean question : new boolean[] {false, true})
        for (Optional<AuthenticatedActor> actor : actors()) {
          var f = new Jdbc();
          new QuestionQueryAuditWriter()
              .write(f.connection(), actor, query(question), expected.event(), NOW);
          columns(f, QUERY_SQL, expected.action(), expected.category(), expected.level(), actor);
          var details = f.details();
          assertEquals(question ? "QSDREQ01" : "NTDREQ01", details.get(LAYOUT).getAsString());
          assertEquals(question ? QUESTION : NOTIFICATION, details.get(TARGET).getAsString());
          assertEquals(expected.event().name(), details.get(REASON).getAsString());
          assertEquals(expected.step(), details.get(STEP).getAsString());
          assertEquals(
              expected.event() == QuestionQueryAuditWriter.Event.REPLAY ? "REPLAY" : "DENIED",
              details.get(OUTCOME).getAsString());
          assertEquals(actor.isPresent(), details.has(ROLE));
          actor.ifPresent(
              value -> assertEquals(value.role().name(), details.get(ROLE).getAsString()));
          assertEquals(actor.isPresent() ? 6 : 5, details.size());
        }
  }

  @Test
  void port002EveryMutationEventBothScopesAndActorStatesMatchesIndependentTable() throws Exception {
    for (MutationCase expected : MUTATIONS)
      for (boolean cancellation : new boolean[] {false, true})
        for (Optional<AuthenticatedActor> actor : actors()) {
          var f = new Jdbc();
          new QuestionMutationAuditWriter()
              .write(f.connection(), actor, mutation(cancellation), expected.event(), NOW);
          columns(f, MUTATION_SQL, expected.action(), expected.category(), expected.level(), actor);
          var details = f.details();
          assertEquals(cancellation ? "NTCREQ01" : "QDLREQ01", details.get(LAYOUT).getAsString());
          assertEquals(cancellation ? NOTIFICATION : QUESTION, details.get(TARGET).getAsString());
          assertEquals(expected.event().name(), details.get(REASON).getAsString());
          assertFalse(details.has(OUTCOME));
          assertFalse(details.has(STEP));
          assertEquals(actor.isPresent(), details.has(ROLE));
          actor.ifPresent(
              value -> assertEquals(value.role().name(), details.get(ROLE).getAsString()));
          assertEquals(expected.capacity(), details.has("resource"));
          assertEquals(expected.capacity(), details.has("errorCode"));
          if (expected.capacity()) {
            assertEquals("N9_VERSION", details.get("resource").getAsString());
            assertEquals("9001", details.get("errorCode").getAsString());
          }
          assertEquals(
              3 + (actor.isPresent() ? 1 : 0) + (expected.capacity() ? 2 : 0), details.size());
          assertFalse(details.toString().contains(OPERATION.toString()));
          assertFalse(details.toString().contains("0".repeat(64)));
        }
  }

  @Test
  void port003BothWritersSanitizeNfcUsernameAndProjectNoSensitiveFields() throws Exception {
    var actor = new AuthenticatedActor(8, "e\u0301\r\n\t\u2028\u2029", Role.USER);
    for (int mode = 0; mode < 2; mode++) {
      var f = new Jdbc();
      write(f.connection(), mode, Optional.of(actor), NOW);
      assertEquals("é     ", f.binds.get(9));
      assertEquals("USER", f.details().get(ROLE).getAsString());
      assertFalse(f.details().has("username"));
      assertFalse(f.details().has("body"));
      assertFalse(f.details().has("context"));
      assertFalse(f.details().has("token"));
      assertFalse(f.details().has("targetId"));
      assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
    }
  }

  @Test
  void port004EveryRequiredInputRejectsNullWithoutOwningBorrowedConnection() {
    var f = new Jdbc();
    var queryWriter = new QuestionQueryAuditWriter();
    var mutationWriter = new QuestionMutationAuditWriter();
    var qr = query(true);
    var mr = mutation(true);
    var qe = QuestionQueryAuditWriter.Event.REPLAY;
    var me = QuestionMutationAuditWriter.Event.REPLAY;
    assertThrows(
        NullPointerException.class, () -> queryWriter.write(null, Optional.of(ACTOR), qr, qe, NOW));
    assertThrows(
        NullPointerException.class, () -> queryWriter.write(f.connection(), null, qr, qe, NOW));
    assertThrows(
        NullPointerException.class,
        () -> queryWriter.write(f.connection(), Optional.of(ACTOR), null, qe, NOW));
    assertThrows(
        NullPointerException.class,
        () -> queryWriter.write(f.connection(), Optional.of(ACTOR), qr, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> queryWriter.write(f.connection(), Optional.of(ACTOR), qr, qe, null));
    assertThrows(
        NullPointerException.class,
        () -> mutationWriter.write(null, Optional.of(ACTOR), mr, me, NOW));
    assertThrows(
        NullPointerException.class, () -> mutationWriter.write(f.connection(), null, mr, me, NOW));
    assertThrows(
        NullPointerException.class,
        () -> mutationWriter.write(f.connection(), Optional.of(ACTOR), null, me, NOW));
    assertThrows(
        NullPointerException.class,
        () -> mutationWriter.write(f.connection(), Optional.of(ACTOR), mr, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> mutationWriter.write(f.connection(), Optional.of(ACTOR), mr, me, null));
    assertEquals(f.prepared, f.closes);
  }

  @Test
  void port005OnlyOneAffectedRowIsSuccessfulCriticalAudit() {
    for (int mode = 0; mode < 2; mode++)
      for (int count : new int[] {0, 2}) {
        var f = new Jdbc();
        f.affected = count;
        int selected = mode;
        var failure =
            assertThrows(
                SQLException.class, () -> write(f.connection(), selected, Optional.of(ACTOR), NOW));
        assertEquals(
            mode == 0
                ? "critical question query audit did not create one row"
                : "critical question mutation audit count is invalid",
            failure.getMessage());
        assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
      }
  }

  @Test
  void port006AllSqlStagesAndTimeOverflowPreserveFailureAndCloseOwnedOnly() {
    for (int mode = 0; mode < 2; mode++) {
      int selected = mode;
      for (String phase : List.of(PREPARE, BIND, EXECUTE, CLOSE)) {
        var f = new Jdbc();
        var failure = new SQLException(SAFE_FAULT);
        f.failure = failure;
        f.failAt = phase;
        assertSame(
            failure,
            assertThrows(
                SQLException.class,
                () -> write(f.connection(), selected, Optional.of(ACTOR), NOW)));
        assertEquals(phase.equals(PREPARE) ? 0 : 1, f.closes);
      }
      var f = new Jdbc();
      assertThrows(
          DateTimeException.class,
          () -> write(f.connection(), selected, Optional.of(ACTOR), Instant.MAX));
      assertEquals(List.of(PREPARE, CLOSE), f.operations);
    }
  }

  @Test
  void port007PrimaryCloseAndUnknownFailuresRemainFailures() {
    for (int mode = 0; mode < 2; mode++) {
      int selected = mode;
      var f = new Jdbc();
      var primary = new SQLException(SAFE_FAULT);
      var secondary = new SQLException("public close fixture");
      f.failAt = EXECUTE;
      f.failure = primary;
      f.closeFailure = secondary;
      assertSame(
          primary,
          assertThrows(
              SQLException.class, () -> write(f.connection(), selected, Optional.of(ACTOR), NOW)));
      assertEquals(1, primary.getSuppressed().length);
      assertSame(secondary, primary.getSuppressed()[0]);
      for (Throwable failure :
          List.of(new IllegalArgumentException(SAFE_FAULT), new AssertionError(SAFE_FAULT))) {
        var other = new Jdbc();
        other.failAt = EXECUTE;
        other.failure = failure;
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () -> write(other.connection(), selected, Optional.of(ACTOR), NOW)));
        assertEquals(List.of(PREPARE, EXECUTE, CLOSE), other.operations);
      }
    }
  }

  @Test
  void port008IndependentWorkersShareNoMutableJdbcOrJson() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> readOne(0));
      var second = workers.submit(() -> readOne(1));
      assertEquals(QUESTION, first.get(5, TimeUnit.SECONDS).get(TARGET).getAsString());
      assertEquals(NOTIFICATION, second.get(5, TimeUnit.SECONDS).get(TARGET).getAsString());
    }
  }

  private static List<Optional<AuthenticatedActor>> actors() {
    return List.of(
        Optional.empty(),
        Optional.of(ACTOR),
        Optional.of(new AuthenticatedActor(9, "public-admin", Role.ADMIN)));
  }

  private static JsonObject readOne(int mode) throws SQLException {
    var f = new Jdbc();
    write(f.connection(), mode, Optional.of(ACTOR), NOW);
    assertEquals(REPLAY_ACTION, f.binds.get(4));
    return f.details();
  }

  private static void write(
      @Nullable Connection connection, int mode, Optional<AuthenticatedActor> actor, Instant at)
      throws SQLException {
    if (mode == 0)
      new QuestionQueryAuditWriter()
          .write(connection, actor, query(true), QuestionQueryAuditWriter.Event.REPLAY, at);
    else
      new QuestionMutationAuditWriter()
          .write(connection, actor, mutation(true), QuestionMutationAuditWriter.Event.REPLAY, at);
  }

  private static void columns(
      Jdbc f,
      String sql,
      String action,
      String category,
      String level,
      Optional<AuthenticatedActor> actor) {
    assertEquals(sql, f.sql.replaceAll("\\s+", " ").strip());
    assertEquals(NOW.atOffset(ZoneOffset.UTC), f.binds.get(1));
    assertEquals(category, f.binds.get(2));
    assertEquals(level, f.binds.get(3));
    assertEquals(action, f.binds.get(4));
    assertEquals(action, f.binds.get(5));
    assertEquals(MESSAGE, f.binds.get(6));
    assertEquals(MESSAGE, f.binds.get(7));
    assertEquals(List.of(PREPARE, EXECUTE, CLOSE), f.operations);
    if (actor.isPresent()) {
      assertEquals(10, f.binds.size());
      assertEquals(actor.orElseThrow().userId(), f.binds.get(8));
      assertEquals(actor.orElseThrow().username(), f.binds.get(9));
      assertTrue(f.nullTypes.isEmpty());
    } else {
      assertEquals(8, f.binds.size());
      assertEquals(Map.of(8, Types.BIGINT, 9, Types.VARCHAR), f.nullTypes);
    }
  }

  private static QuestionQueryRequest query(boolean question) {
    return QuestionQueryRequest.decode(
        wire(
            question ? "QSDREQ01" : "NTDREQ01",
            question
                ? new QuestionDetailRequestData(new QuestionId(5))
                : new NotificationDetailRequestData(new NotificationId(9))));
  }

  private static QuestionMutationRequest mutation(boolean cancellation) {
    return QuestionMutationRequest.decode(
        wire(
            cancellation ? "NTCREQ01" : "QDLREQ01",
            cancellation
                ? new NotificationCancelRequestData(new NotificationId(9), OPERATION)
                : new QuestionDeleteRequestData(new QuestionId(5), OPERATION)));
  }

  private static WireMessage<FixedPayload> wire(String layout, PayloadData data) {
    var id = new LayoutId(layout);
    var values = new TypedPayloadValues(id, data, List.of());
    // Encoder builds the bounded input fixture only. No expected value is calculated by production.
    var payload = PayloadCodec.standard().encode(PayloadTypeCatalog.encode(values), false);
    int size = payload.copyData().length;
    return new WireMessage<>(
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
            Optional.empty()),
        payload);
  }

  private record QueryCase(
      QuestionQueryAuditWriter.Event event,
      String action,
      String category,
      String level,
      String step) {}

  private record MutationCase(
      QuestionMutationAuditWriter.Event event,
      String action,
      String category,
      String level,
      boolean capacity) {}

  private static final class Jdbc {
    final Map<Integer, Object> binds = new LinkedHashMap<>();
    final Map<Integer, Integer> nullTypes = new HashMap<>();
    final List<String> operations = new ArrayList<>();
    String sql = "";
    String failAt = "";
    int affected = 1;
    int prepared;
    int closes;
    @Nullable Throwable failure;
    @Nullable Throwable closeFailure;

    private void fail(String phase) throws Throwable {
      if (failAt.equals(phase) && failure != null) throw failure;
    }

    private JsonObject details() {
      return JsonParser.parseString((String) binds.get(10)).getAsJsonObject();
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (!method.getName().equals("prepareStatement"))
                  throw new AssertionError("borrowed connection operation forbidden");
                prepared++;
                operations.add(PREPARE);
                fail(PREPARE);
                sql = (String) args[0];
                return statement();
              });
    }

    private PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.startsWith("set")) {
                  fail(BIND);
                  if (name.equals("setNull")) nullTypes.put((int) args[0], (int) args[1]);
                  else binds.put((int) args[0], args[1]);
                  return null;
                }
                if (name.equals("executeUpdate")) {
                  operations.add(EXECUTE);
                  fail(EXECUTE);
                  return affected;
                }
                if (name.equals(CLOSE)) {
                  operations.add(CLOSE);
                  closes++;
                  if (closeFailure != null) throw closeFailure;
                  fail(CLOSE);
                  return null;
                }
                throw new AssertionError("unexpected statement operation");
              });
    }
  }
}
