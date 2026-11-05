package dev.codex.schubert.nk.api.application.log;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import dev.codex.schubert.nk.api.application.log.LogQueryAuditWriter.Event;
import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** PT-ADM-SEARCHPORT001..008; UI235/SS312324351/QA054/SSC336. JDBC interfaces only. */
final class LogSearchAuditPortTest {
  private static final Instant NOW = Instant.parse("2026-11-05T00:01:02.123456Z");
  private static final UUID MESSAGE = new UUID(0, 11);
  private static final UUID CORRELATION = new UUID(0, 12);
  private static final AuthenticatedActor ADMIN =
      new AuthenticatedActor(17, "audit-admin", Role.ADMIN);
  private static final String PREPARE = "prepare";
  private static final String BIND = "bind";
  private static final String EXECUTE = "execute";
  private static final String CLOSE = "close";
  private static final String SQL =
      "insert into schubert.app_logs(logged_at,service,category,level,action,message,"
          + " message_id,correlation_id,actor_user_id,actor_username,details) values"
          + " (?,'API',?,?,?,?,?,?,?,?,cast(? as jsonb))";
  private static final String AUTH_ACTION = "AUTHORIZATION_DENIED";
  private static final String SAFE_FAILURE = "safe fixture";
  private static final String SUCCESS_ACTION = "LOG_SEARCHED";
  private static final List<Expected> EVENTS =
      List.of(
          new Expected(
              Event.SESSION_INVALID,
              "SECURITY",
              "INFO",
              AUTH_ACTION,
              "SESSION_INVALID",
              "DENIED",
              "AUTH_CONTEXT"),
          new Expected(
              Event.ROLE_DENIED,
              "SECURITY",
              "WARN",
              AUTH_ACTION,
              "ROLE_DENIED",
              "DENIED",
              "ADMIN_ROLE"),
          new Expected(
              Event.MESSAGE_MISMATCH,
              "MQ",
              "WARN",
              "PROTOCOL_REJECTED",
              "MESSAGE_MISMATCH",
              "DENIED",
              "MESSAGE_IDENTITY"),
          new Expected(
              Event.REPLAY, "MQ", "INFO", "INBOX_REPLAYED", "REPLAY", "REPLAY", "SAVED_RESULT"),
          new Expected(
              Event.SEARCH_SUCCEEDED,
              "ACTION",
              "INFO",
              SUCCESS_ACTION,
              "SEARCH_SUCCEEDED",
              "SUCCESS",
              "SEARCH_COMPLETED"));

  @Test
  void searchPort001AllClosedEventsUseIndependentSqlAndBindings() throws Exception {
    for (Expected expected : EVENTS) {
      var jdbc = new Jdbc();
      new LogQueryAuditWriter()
          .write(jdbc.connection(), Optional.of(ADMIN), request(), expected.event(), NOW);
      assertEquals(SQL, jdbc.sql.replaceAll("\\s+", " ").trim());
      assertEquals(
          Map.of(
              1,
              NOW.atOffset(ZoneOffset.UTC),
              2,
              expected.category(),
              3,
              expected.level(),
              4,
              expected.action(),
              5,
              expected.action(),
              6,
              MESSAGE,
              7,
              CORRELATION,
              8,
              17L,
              9,
              "audit-admin"),
          jdbc.parametersWithoutDetails());
      String json =
          "{\"layout\":\"LGSREQ01\",\"reason\":\""
              + expected.reason()
              + "\",\"targetType\":\"LOG\",\"outcome\":\""
              + expected.outcome()
              + "\",\"actorRole\":\"ADMIN\",\"step\":\""
              + expected.step()
              + "\"}";
      assertEquals(
          JsonParser.parseString(json), JsonParser.parseString((String) jdbc.binds.get(10)));
      assertEquals(List.of(PREPARE, EXECUTE, CLOSE), jdbc.operations);
      assertEquals(10, jdbc.binds.size());
    }
  }

  @Test
  void searchPort002AbsentActorUsesSqlNullForExistingDenialAndReplay() throws Exception {
    for (Expected expected : EVENTS.subList(0, 4)) {
      var jdbc = new Jdbc();
      new LogQueryAuditWriter()
          .write(jdbc.connection(), Optional.empty(), request(), expected.event(), NOW);
      assertEquals(Map.of(8, Types.BIGINT, 9, Types.VARCHAR), jdbc.nullTypes);
      assertTrue(
          !JsonParser.parseString((String) jdbc.binds.get(10)).getAsJsonObject().has("actorRole"));
      assertEquals(expected.action(), jdbc.binds.get(4));
      assertEquals(List.of(PREPARE, EXECUTE, CLOSE), jdbc.operations);
    }
  }

  @Test
  void searchPort003SuccessRequiresPresentAdminBeforeAnySql() {
    for (Optional<AuthenticatedActor> actor :
        List.of(
            Optional.<AuthenticatedActor>empty(),
            Optional.of(new AuthenticatedActor(18, "user", Role.USER)))) {
      var jdbc = new Jdbc();
      var error =
          assertThrows(
              IllegalArgumentException.class,
              () ->
                  new LogQueryAuditWriter()
                      .write(jdbc.connection(), actor, request(), Event.SEARCH_SUCCEEDED, NOW));
      assertEquals("log search success requires ADMIN actor", error.getMessage());
      assertTrue(jdbc.operations.isEmpty());
    }
  }

  @Test
  void searchPort004NfcAndDisplaySanitizationDoNotCopyQueryOrCredentials() throws Exception {
    var jdbc = new Jdbc();
    var actor = new AuthenticatedActor(19, "e\u0301\r\n\t\u2028\u2029", Role.ADMIN);
    new LogQueryAuditWriter()
        .write(jdbc.connection(), Optional.of(actor), request(), Event.SEARCH_SUCCEEDED, NOW);
    assertEquals("é     ", jdbc.binds.get(9));
    assertEquals(SUCCESS_ACTION, jdbc.binds.get(5));
    assertEquals(6, JsonParser.parseString((String) jdbc.binds.get(10)).getAsJsonObject().size());
  }

  @Test
  void searchPort005ExactlyOneAffectedRowIsRequiredAndStatementClosed() {
    for (int rows : new int[] {-1, 0, 2}) {
      var jdbc = new Jdbc();
      jdbc.rows = rows;
      var failure =
          assertThrows(
              SQLException.class,
              () ->
                  new LogQueryAuditWriter()
                      .write(
                          jdbc.connection(),
                          Optional.of(ADMIN),
                          request(),
                          Event.SEARCH_SUCCEEDED,
                          NOW));
      assertEquals("critical log query audit did not create one row", failure.getMessage());
      assertEquals(List.of(PREPARE, EXECUTE, CLOSE), jdbc.operations);
    }
  }

  @Test
  void searchPort006OwnedSqlFaultsAndUnknownRuntimeIdentityPropagate() {
    for (String stage : List.of(PREPARE, BIND, EXECUTE, CLOSE)) {
      for (Throwable failure :
          List.of(
              new SQLException(SAFE_FAILURE),
              new IllegalStateException(SAFE_FAILURE),
              new AssertionError(SAFE_FAILURE))) {
        var jdbc = new Jdbc();
        jdbc.faultAt = stage;
        jdbc.fault = failure;
        Throwable actual =
            assertThrows(
                failure.getClass(),
                () ->
                    new LogQueryAuditWriter()
                        .write(
                            jdbc.connection(),
                            Optional.of(ADMIN),
                            request(),
                            Event.SEARCH_SUCCEEDED,
                            NOW));
        assertSame(failure, actual);
        if (!stage.equals(PREPARE)) assertEquals(CLOSE, jdbc.operations.getLast());
      }
    }
    var jdbc = new Jdbc();
    var first = new SQLException(SAFE_FAILURE);
    var second = new SQLException("close fixture");
    jdbc.faultAt = EXECUTE;
    jdbc.fault = first;
    jdbc.closeFault = second;
    assertSame(
        first,
        assertThrows(
            SQLException.class,
            () ->
                new LogQueryAuditWriter()
                    .write(
                        jdbc.connection(),
                        Optional.of(ADMIN),
                        request(),
                        Event.SEARCH_SUCCEEDED,
                        NOW)));
    assertEquals(1, first.getSuppressed().length);
    assertSame(second, first.getSuppressed()[0]);
  }

  @Test
  void searchPort007AllNonNullBoundaryContractsFailBeforeSql() {
    var writer = new LogQueryAuditWriter();
    var jdbc = new Jdbc();
    var connection = jdbc.connection();
    var request = request();
    assertThrows(
        NullPointerException.class,
        () -> writer.write(null, Optional.of(ADMIN), request, Event.SEARCH_SUCCEEDED, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(connection, null, request, Event.SEARCH_SUCCEEDED, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(connection, Optional.of(ADMIN), null, Event.SEARCH_SUCCEEDED, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(connection, Optional.of(ADMIN), request, null, NOW));
    assertThrows(
        NullPointerException.class,
        () -> writer.write(connection, Optional.of(ADMIN), request, Event.SEARCH_SUCCEEDED, null));
    assertTrue(jdbc.operations.isEmpty());
  }

  @Test
  void searchPort008IndependentOwnedWorkersDoNotShareBindings() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var first = workers.submit(() -> writeOne(Event.SEARCH_SUCCEEDED));
      var second = workers.submit(() -> writeOne(Event.REPLAY));
      assertEquals(SUCCESS_ACTION, first.get().get(4));
      assertEquals("INBOX_REPLAYED", second.get().get(4));
    }
  }

  private static Map<Integer, Object> writeOne(Event event) throws SQLException {
    var jdbc = new Jdbc();
    new LogQueryAuditWriter().write(jdbc.connection(), Optional.of(ADMIN), request(), event, NOW);
    assertEquals(List.of(PREPARE, EXECUTE, CLOSE), jdbc.operations);
    return jdbc.parametersWithoutDetails();
  }

  private static LogRequest request() {
    byte[] data = new byte[656];
    Arrays.fill(data, (byte) ' ');
    System.arraycopy("000001100".getBytes(StandardCharsets.US_ASCII), 0, data, 634, 9);
    // Public zero-format fixture, never an issued context and never an authentication call.
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            new LayoutId("LGSREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            MESSAGE,
            CORRELATION,
            NOW,
            Optional.of(AuthenticationContext.of("0".repeat(64))),
            256,
            656,
            0,
            0,
            912,
            Optional.empty());
    return LogRequest.decode(new WireMessage<>(header, new FixedPayload(data, 0, List.of())));
  }

  private record Expected(
      Event event,
      String category,
      String level,
      String action,
      String reason,
      String outcome,
      String step) {}

  private static final class Jdbc {
    private final Map<Integer, Object> binds = new HashMap<>();
    private final Map<Integer, Integer> nullTypes = new HashMap<>();
    private final List<String> operations = new ArrayList<>();
    private String sql = "";
    private int rows = 1;
    private String faultAt = "";
    private @Nullable Throwable fault;
    private @Nullable Throwable closeFault;

    private void fail(String stage) throws Throwable {
      if (stage.equals(faultAt) && fault != null) throw fault;
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (!method.getName().equals("prepareStatement"))
                  throw new AssertionError("borrowed connection operation forbidden");
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
                if (method.getName().startsWith("set")) {
                  fail(BIND);
                  int position = (int) args[0];
                  if (method.getName().equals("setNull")) nullTypes.put(position, (int) args[1]);
                  else binds.put(position, args[1]);
                  return null;
                }
                return switch (method.getName()) {
                  case "executeUpdate" -> {
                    operations.add(EXECUTE);
                    fail(EXECUTE);
                    yield rows;
                  }
                  case "close" -> {
                    operations.add(CLOSE);
                    if (closeFault != null) throw closeFault;
                    fail(CLOSE);
                    yield null;
                  }
                  default -> throw new AssertionError("statement operation forbidden");
                };
              });
    }

    private Map<Integer, Object> parametersWithoutDetails() {
      var copy = new HashMap<>(binds);
      copy.remove(10);
      return copy;
    }
  }
}
