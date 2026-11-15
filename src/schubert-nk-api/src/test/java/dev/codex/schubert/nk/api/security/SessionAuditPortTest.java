package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.gson.JsonParser;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** AUT-SESSION-AUDIT001..009; SS314/351; Program007 spec039. Memory JDBC only. */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class SessionAuditPortTest {
  private static final String JDBC_PREPARE = "prepare";
  private static final String JDBC_EXECUTE = "execute";
  private static final String JDBC_CLOSE = "close";
  private static final SessionAuditWriter AUDIT_WRITER = new SessionAuditWriter();
  private static final Instant AUDIT_TIME = Instant.parse("2034-06-12T01:02:03.456789Z");
  private static final UUID MESSAGE_ID = UUID.fromString("70000000-0000-4000-8000-000000000001");
  private static final UUID CORRELATION_ID =
      UUID.fromString("70000000-0000-4000-8000-000000000002");
  private static final String EXPECTED_SQL =
      "insert into schubert.app_logs"
          + " (logged_at,service,category,level,action,message,message_id,correlation_id,actor_user_id,remote_address,details)"
          + " values(?,'API','SECURITY','INFO','SESSION_REVOKED','SESSION_REVOKED',?,?,?,cast(? as"
          + " inet),cast(? as jsonb))";

  @Test
  void closedReasonEventsHaveLiteralAuditFields() throws SQLException {
    var reasons =
        Map.of(
            SessionRevocationReason.LOGOUT, "LOGOUT",
            SessionRevocationReason.DISABLED, "DISABLED",
            SessionRevocationReason.PASSWORD_RESET, "PASSWORD_RESET",
            SessionRevocationReason.ADMIN, "ADMIN",
            SessionRevocationReason.EXPIRED, "EXPIRED",
            SessionRevocationReason.REPLACED, "REPLACED");
    assertEquals(6, SessionRevocationReason.values().length);
    for (var event : reasons.entrySet()) {
      var fixture = new Fixture();
      invoke(fixture, Optional.empty(), event.getKey());
      assertBindings(fixture, event.getValue(), new SqlNull(Types.VARCHAR));
      assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
    }
    var replay = new Fixture();
    invoke(replay, Optional.empty(), SessionRevocationReason.LOGOUT, ResultCode.IDEMPOTENT_SUCCESS);
    assertBindings(replay, "LOGOUT", new SqlNull(Types.VARCHAR), "0200");
  }

  @Test
  void missingIpv4AndIpv6HaveIndependentLiteralBindings()
      throws SQLException, UnknownHostException {
    var v4 = InetAddress.getByAddress(new byte[] {127, 0, 0, 1});
    var v6 =
        InetAddress.getByAddress(
            new byte[] {0x20, 1, 0x0d, (byte) 0xb8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x42});
    var clients = List.of(Optional.<InetAddress>empty(), Optional.of(v4), Optional.of(v6));
    List<Object> expected =
        List.of(new SqlNull(Types.VARCHAR), "127.0.0.1", "2001:db8:0:0:0:0:0:42");
    for (int index = 0; index < clients.size(); index++) {
      var fixture = new Fixture();
      invoke(fixture, clients.get(index), SessionRevocationReason.LOGOUT);
      assertBindings(fixture, "LOGOUT", expected.get(index));
    }
  }

  @Test
  void affectedRowCountMustBeExactlyOne() {
    for (int count : new int[] {-1, 0, 2}) {
      var fixture = new Fixture();
      fixture.affectedRows = count;
      var failure =
          assertThrows(
              SQLException.class,
              () -> invoke(fixture, Optional.empty(), SessionRevocationReason.ADMIN));
      assertEquals("40001", failure.getSQLState());
      assertEquals("critical session audit did not create one row", failure.getMessage());
      assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
      assertEquals(6, fixture.bindings.size());
    }
  }

  @Test
  void preparationFailuresPropagateWithoutBorrowedTransactionOperations() {
    for (Throwable original : failures()) {
      var fixture = new Fixture();
      fixture.prepareFailure = original;
      assertSame(
          original,
          assertThrows(
              original.getClass(),
              () -> invoke(fixture, Optional.empty(), SessionRevocationReason.EXPIRED)));
      assertEquals(List.of(JDBC_PREPARE), fixture.operations);
      assertTrue(fixture.bindings.isEmpty());
    }
  }

  @Test
  void executionFailuresStillCloseTheStatementOnce() {
    for (Throwable original : failures()) {
      var fixture = new Fixture();
      fixture.executeFailure = original;
      assertSame(
          original,
          assertThrows(
              original.getClass(),
              () -> invoke(fixture, Optional.empty(), SessionRevocationReason.DISABLED)));
      assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
    }
  }

  @Test
  void closeFailuresCannotBecomeSuccessfulReturn() {
    for (Throwable original : failures()) {
      var fixture = new Fixture();
      fixture.closeFailure = original;
      assertSame(
          original,
          assertThrows(
              original.getClass(),
              () -> invoke(fixture, Optional.empty(), SessionRevocationReason.PASSWORD_RESET)));
      assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
    }
  }

  @Test
  void distinctCleanupFailuresRemainInTheOriginalFailureGraph() {
    for (int primaryIndex = 0; primaryIndex < 3; primaryIndex++) {
      for (Throwable secondary : failures()) {
        Throwable primary = failures().get(primaryIndex);
        var fixture = new Fixture();
        fixture.executeFailure = primary;
        fixture.closeFailure = secondary;
        assertSame(
            primary,
            assertThrows(
                primary.getClass(),
                () -> invoke(fixture, Optional.empty(), SessionRevocationReason.REPLACED)));
        // Fresh primary per pair: no previous suppressed values may contaminate this oracle.
        var suppressed = primary.getSuppressed();
        assertEquals(1, suppressed.length);
        assertSame(secondary, suppressed[0]);
        assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
      }
    }
  }

  @Test
  void aliasedProviderFailureIsRecordedAsNonSuccessWithOriginalCause() {
    for (Throwable original : failures()) {
      var fixture = new Fixture();
      fixture.executeFailure = original;
      fixture.closeFailure = original;
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> invoke(fixture, Optional.empty(), SessionRevocationReason.LOGOUT));
      assertSame(original, failure.getCause());
      assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
    }
  }

  @Test
  void twoOwnedWorkersKeepIndependentStatementsAndValues()
      throws InterruptedException, ExecutionException, TimeoutException {
    var workers = Executors.newFixedThreadPool(2);
    try {
      var first =
          workers.submit(
              () -> {
                var fixture = new Fixture();
                invoke(fixture, Optional.empty(), SessionRevocationReason.ADMIN);
                return fixture;
              });
      var second =
          workers.submit(
              () -> {
                var fixture = new Fixture();
                invoke(fixture, Optional.empty(), SessionRevocationReason.EXPIRED);
                return fixture;
              });
      assertBindings(first.get(5, TimeUnit.SECONDS), "ADMIN", new SqlNull(Types.VARCHAR));
      assertBindings(second.get(5, TimeUnit.SECONDS), "EXPIRED", new SqlNull(Types.VARCHAR));
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static void invoke(
      Fixture fixture, Optional<InetAddress> client, SessionRevocationReason reason)
      throws SQLException {
    invoke(fixture, client, reason, ResultCode.SUCCESS);
  }

  private static void invoke(
      Fixture fixture,
      Optional<InetAddress> client,
      SessionRevocationReason reason,
      ResultCode result)
      throws SQLException {
    AUDIT_WRITER.write(
        fixture.connectionProxy,
        17,
        41,
        client,
        MESSAGE_ID,
        CORRELATION_ID,
        AUDIT_TIME,
        reason,
        result);
  }

  private static void assertBindings(Fixture fixture, String reason, Object client) {
    assertBindings(fixture, reason, client, "0000");
  }

  private static void assertBindings(
      Fixture fixture, String reason, Object client, String resultCode) {
    assertEquals(EXPECTED_SQL, fixture.preparedSql);
    assertEquals(OffsetDateTime.parse("2034-06-12T01:02:03.456789Z"), fixture.bindings.get(1));
    assertEquals(MESSAGE_ID, fixture.bindings.get(2));
    assertEquals(CORRELATION_ID, fixture.bindings.get(3));
    assertEquals(17L, fixture.bindings.get(4));
    assertEquals(client, fixture.bindings.get(5));
    var json = JsonParser.parseString(assertInstanceOf(String.class, fixture.bindings.get(6)));
    assertEquals(
        java.util.Set.of("targetUserId", "reason", "resultCode"), json.getAsJsonObject().keySet());
    assertEquals(41, json.getAsJsonObject().get("targetUserId").getAsInt());
    assertEquals(reason, json.getAsJsonObject().get("reason").getAsString());
    assertEquals(resultCode, json.getAsJsonObject().get("resultCode").getAsString());
    assertEquals(6, fixture.bindings.size());
    assertEquals(List.of(JDBC_PREPARE, JDBC_EXECUTE, JDBC_CLOSE), fixture.operations);
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("synthetic provider SQL"),
        new IllegalStateException("synthetic provider runtime"),
        new AssertionError("synthetic provider fatal"));
  }

  private static void throwIfPresent(@Nullable Throwable failure) throws SQLException {
    if (failure instanceof SQLException sql) throw sql;
    if (failure instanceof RuntimeException runtime) throw runtime;
    if (failure instanceof Error fatal) throw fatal;
  }

  private record SqlNull(int type) {}

  private static final class Fixture {
    private final Map<Integer, Object> bindings = new LinkedHashMap<>();
    private final java.util.ArrayList<String> operations = new java.util.ArrayList<>();
    private final Connection connectionProxy;
    private @Nullable String preparedSql;
    private @Nullable Throwable prepareFailure;
    private @Nullable Throwable executeFailure;
    private @Nullable Throwable closeFailure;
    private int affectedRows = 1;

    private Fixture() {
      var statementProxy =
          proxy(
              PreparedStatement.class,
              (target, method, args) -> {
                switch (method.getName()) {
                  case "setObject", "setLong", "setString" -> {
                    bindings.put((Integer) args[0], args[1]);
                    return null;
                  }
                  case "setNull" -> {
                    bindings.put((Integer) args[0], new SqlNull((Integer) args[1]));
                    return null;
                  }
                  case "executeUpdate" -> {
                    operations.add(JDBC_EXECUTE);
                    throwIfPresent(executeFailure);
                    return affectedRows;
                  }
                  case JDBC_CLOSE -> {
                    operations.add(JDBC_CLOSE);
                    throwIfPresent(closeFailure);
                    return null;
                  }
                  default -> throw new AssertionError("unexpected statement operation");
                }
              });
      connectionProxy =
          proxy(
              Connection.class,
              (target, method, args) -> {
                if (!method.getName().equals("prepareStatement"))
                  throw new AssertionError("borrowed transaction operation is forbidden");
                operations.add(JDBC_PREPARE);
                preparedSql = (String) args[0];
                throwIfPresent(prepareFailure);
                return statementProxy;
              });
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
