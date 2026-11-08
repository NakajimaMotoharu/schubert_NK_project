package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.time.Clock;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OWN-EMPTY001; ASY001/MQ006; UI213/241; SS324§8/332§7.1; BUG2524/YKT2258. */
final class OwnedOutboxNormalCyclePortTest {
  private static final Instant NOW = Instant.parse("2026-01-02T03:04:05.123456Z");

  private static <T> T port(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }

  /**
   * Records a JDBC interface protocol; no driver, external database or cleanup failure injection.
   */
  private static final class EmptyClaim {
    private final List<String> calls = new ArrayList<>();
    private final Map<Integer, Object> parameters = new HashMap<>();
    private String sql;
    private boolean autoCommit = true;
    private final Connection connection;

    private EmptyClaim(CountDownLatch completed) {
      ResultSet result =
          port(
              ResultSet.class,
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "next":
                    calls.add("next");
                    return false;
                  case "close":
                    calls.add("result.close");
                    return null;
                  default:
                    throw new AssertionError("unexpected ResultSet call: " + method.getName());
                }
              });
      PreparedStatement statement =
          port(
              PreparedStatement.class,
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setObject", "setString", "setInt":
                    calls.add("bind" + args[0]);
                    parameters.put((Integer) args[0], args[1]);
                    return null;
                  case "executeQuery":
                    calls.add("query");
                    return result;
                  case "close":
                    calls.add("statement.close");
                    return null;
                  default:
                    throw new AssertionError("unexpected statement call: " + method.getName());
                }
              });
      connection =
          port(
              Connection.class,
              (proxy, method, args) -> {
                switch (method.getName()) {
                  case "setAutoCommit":
                    calls.add("autoCommit=false");
                    autoCommit = (Boolean) args[0];
                    return null;
                  case "getAutoCommit":
                    calls.add("getAutoCommit");
                    return autoCommit;
                  case "prepareStatement":
                    calls.add("prepare");
                    sql = (String) args[0];
                    return statement;
                  case "commit":
                    calls.add("commit");
                    return null;
                  case "rollback":
                    calls.add("rollback");
                    return null;
                  case "close":
                    calls.add("connection.close");
                    completed.countDown();
                    return null;
                  default:
                    throw new AssertionError("unexpected Connection call: " + method.getName());
                }
              });
    }
  }

  @Test
  void ownEmpty001NormalEmptyClaimsCommitAndCloseBeforeOwnedStop() throws Exception {
    var completed = new CountDownLatch(2);
    var claims = new ConcurrentLinkedQueue<EmptyClaim>();
    var jmsOpens = new AtomicInteger();
    var dispatcher =
        new OutboxDispatcher(
            () -> {
              var claim = new EmptyClaim(completed);
              claims.add(claim);
              return claim.connection;
            },
            () -> {
              jmsOpens.incrementAndGet();
              throw new AssertionError("empty claim must not acquire JMS");
            },
            new JdbcOutboxRepository(() -> 0),
            new OutboxJmsSender(),
            Clock.fixed(NOW, ZoneOffset.UTC));
    var owned = OwnedOutboxDispatcher.create(dispatcher, "normal-empty-owner");
    try {
      assertEquals(0, claims.size());
      assertFalse(owned.healthy());
      owned.start();
      owned.wake();
      assertTrue(completed.await(5, TimeUnit.SECONDS));
      assertTrue(owned.healthy());
    } finally {
      owned.close();
    }
    assertFalse(owned.healthy());
    assertThrows(IllegalStateException.class, owned::wake);
    assertThrows(IllegalStateException.class, owned::start);
    int stoppedClaims = claims.size();
    owned.close();
    assertEquals(stoppedClaims, claims.size());
    assertTrue(stoppedClaims >= 2);
    assertEquals(0, jmsOpens.get());
    for (EmptyClaim claim : claims) {
      assertEquals(
          List.of(
              "autoCommit=false",
              "getAutoCommit",
              "prepare",
              "bind1",
              "bind2",
              "bind3",
              "bind4",
              "bind5",
              "query",
              "next",
              "result.close",
              "statement.close",
              "commit",
              "connection.close"),
          claim.calls);
      // Independent literal values from SS332 §7.1: UTC and a ten-second lease, not production
      // output.
      assertEquals(
          Map.of(
              1, OffsetDateTime.parse("2026-01-02T03:04:05.123456Z"),
              2, OffsetDateTime.parse("2026-01-02T03:04:05.123456Z"),
              3, 32,
              4, "normal-empty-owner",
              5, OffsetDateTime.parse("2026-01-02T03:04:15.123456Z")),
          claim.parameters);
      for (String fragment :
          List.of(
              "with due as (select id from schubert.mq_outbox",
              "status in ('PENDING','ERROR') and next_attempt_at<=?",
              "(lease_until is null or lease_until<?)",
              "order by next_attempt_at,id",
              "for update skip locked limit ?",
              "set lease_owner=?,lease_until=? from due where o.id=due.id")) {
        assertTrue(claim.sql.contains(fragment), fragment);
      }
    }
  }
}
