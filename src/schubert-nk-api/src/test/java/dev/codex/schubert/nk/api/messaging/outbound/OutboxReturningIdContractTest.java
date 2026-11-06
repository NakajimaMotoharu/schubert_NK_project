package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-OUT-JDBC009; SS331 §7.2 identity PK/NN; no database, driver or broker. */
final class OutboxReturningIdContractTest {
  private static <T> T port(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  @Test
  void sqlNullReturningIdentifierCannotBecomeSuccessfulZero() throws Exception {
    ResultSet row = port(ResultSet.class, (proxy, method, args) -> switch (method.getName()) {
      case "next" -> true;
      case "getLong" -> 0L;
      case "getObject", "close" -> null;
      case "wasNull" -> true;
      default -> throw new AssertionError("unexpected result operation " + method.getName());
    });
    PreparedStatement statement = port(PreparedStatement.class, (proxy, method, args) -> {
      if (method.getName().startsWith("set") || method.getName().equals("close")) {
        return null;
      }
      if (method.getName().equals("executeQuery")) {
        return row;
      }
      throw new AssertionError("unexpected statement operation " + method.getName());
    });
    Connection connection = port(Connection.class, (proxy, method, args) -> switch (method.getName()) {
      case "getAutoCommit" -> false;
      case "prepareStatement" -> statement;
      default -> throw new AssertionError("caller transaction must remain borrowed");
    });
    Instant now = Instant.parse("2026-01-02T03:04:05Z");
    OutboxRequest request = new OutboxRequest(
        UUID.fromString("00000000-0000-4000-8000-000000000001"),
        UUID.fromString("00000000-0000-4000-8000-000000000002"),
        OutboxDestination.ASYNC_WORK, "QWKREQ01", "001", new byte[320], now, now);
    assertThrows(OutboxIntegrityException.class,
        () -> new JdbcOutboxRepository(() -> 0).enqueue(connection, request));
  }
}
