package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/SS351/PG-D631,633/PT-OPS-OBS001..008. Synthetic JDBC, no driver or SDK. */
final class ApiOutboxPublicationPortTest {
  private static final String DEBUG = "DEBUG";
  private static final String STANDARD = "STANDARD";
  private static final Instant NOW = Instant.EPOCH;
  private static final String SQL =
      "SELECT status, COUNT(*) AS row_count, MIN(created_at) AS oldest_created_at"
          + " FROM schubert.mq_outbox GROUP BY status";

  private static ApiOutboxObservationSource source(String mode) {
    return new ApiOutboxObservationSource(new OutboxObservationRepository(), mode);
  }

  @Test
  void constructorsAndNullContracts() throws SQLException {
    assertThrows(NullPointerException.class, () -> new ApiOutboxObservationSource(null, DEBUG));
    assertThrows(NullPointerException.class, () -> source(null));
    for (String mode : List.of("", "debug", " DEBUG", "UNKNOWN")) {
      var failure = assertThrows(IllegalArgumentException.class, () -> source(mode));
      assertEquals("CONFIG_INVALID", failure.getMessage());
    }
    var value = source(DEBUG);
    var f = new Fixture(false);
    var before = value.observe(f.connection, NOW);
    assertThrows(NullPointerException.class, () -> value.observe(null, NOW));
    assertThrows(NullPointerException.class, () -> value.observe(f.connection, null));
    assertThrows(
        NullPointerException.class, () -> value.observe((ApiReadOnlyObservationAttempt) null));
    assertSame(before, value.get());
    assertEquals(1, f.prepared);
  }

  @Test
  void standardDoesNotAcquire() throws SQLException {
    var value = source(STANDARD);
    var f = new Fixture(true);
    assertTrue(value.get().isEmpty());
    assertTrue(value.observe(f.connection, NOW).isEmpty());
    assertTrue(value.observe(f.attempt()).isEmpty());
    value.missing();
    assertTrue(value.get().isEmpty());
    assertEquals(0, f.checkouts);
    assertEquals(0, f.prepared);
    assertEquals(List.of(), f.calls);
  }

  @Test
  void borrowedPublicationAndMissing() throws SQLException {
    var value = source(DEBUG);
    var f = new Fixture(false);
    var supplied = value.observe(f.connection, NOW);
    assertSame(supplied, value.get());
    assertRows(supplied.orElseThrow());
    f.assertReleased(false);
    value.missing();
    value.missing();
    assertTrue(value.get().isEmpty());
    assertEquals(1, f.prepared);
  }

  @Test
  void borrowedFailureClearsPriorValue() throws SQLException {
    var value = source(DEBUG);
    value.observe(new Fixture(false).connection, NOW);
    var f = new Fixture(false);
    var failure = new SQLException("synthetic prepare failure");
    f.prepareFailure = failure;
    assertSame(failure, assertThrows(SQLException.class, () -> value.observe(f.connection, NOW)));
    assertTrue(value.get().isEmpty());
    assertEquals(0, f.statementCloses);
    assertEquals(0, f.connectionCloses);
  }

  @Test
  void borrowedInvalidationRaces() throws Exception {
    var value = source(DEBUG);
    var f = new Fixture(false);
    var closing = new CountDownLatch(1);
    var released = new CountDownLatch(1);
    f.beforeStatementClose =
        () -> {
          closing.countDown();
          await(released);
        };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending = worker.submit(() -> value.observe(f.connection, NOW));
      try {
        assertTrue(closing.await(10, TimeUnit.SECONDS));
        assertTrue(value.get().isEmpty());
        value.missing();
        value.missing();
      } finally {
        released.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS).isEmpty());
      assertTrue(value.get().isEmpty());
    }
    f.assertReleased(false);
  }

  @Test
  void ownedPublicationAfterClose() throws SQLException {
    var value = source(DEBUG);
    var f = new Fixture(true);
    f.beforeConnectionClose = () -> assertTrue(value.get().isEmpty());
    var attempt = f.attempt();
    var supplied = value.observe(attempt);
    assertSame(supplied, value.get());
    assertRows(supplied.orElseThrow());
    f.assertReleased(true);
    assertFalse(attempt.hasUnconfirmedResource());
    assertEquals(0, f.unconfirmed);
    assertTrue(f.calls.indexOf("rollback") < f.calls.indexOf("connectionClose"));
  }

  @Test
  void ownedInvalidationSuppressesPublication() throws SQLException {
    var value = source(DEBUG);
    var f = new Fixture(true);
    f.beforeConnectionClose = value::missing;
    assertTrue(value.observe(f.attempt()).isEmpty());
    assertTrue(value.get().isEmpty());
    f.assertReleased(true);
    assertEquals(0, f.unconfirmed);
  }

  @Test
  void ownedOneShotFailureClearsValue() throws SQLException {
    var value = source(DEBUG);
    var f = new Fixture(true);
    var attempt = f.attempt();
    assertTrue(value.observe(attempt).isPresent());
    var failure = assertThrows(IllegalStateException.class, () -> value.observe(attempt));
    assertEquals("observation attempt already used", failure.getMessage());
    assertTrue(value.get().isEmpty());
    f.assertReleased(true);
    assertEquals(0, f.unconfirmed);
  }

  private static void assertRows(OutboxObservationRepository.Snapshot actual) {
    assertEquals(3, actual.counts().pending());
    assertEquals(5, actual.counts().sent());
    assertEquals(7, actual.counts().error());
    assertEquals(Duration.ofSeconds(2), actual.ages().pending());
    assertEquals(Duration.ofSeconds(4), actual.ages().sent());
    assertEquals(Duration.ofSeconds(6), actual.ages().error());
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(10, TimeUnit.SECONDS));
    } catch (InterruptedException failure) {
      Thread.currentThread().interrupt();
      throw new AssertionError(failure);
    }
  }

  private static final class Fixture {
    private final List<String> calls = new ArrayList<>();
    private final Connection connection;
    private boolean autoCommit;
    private int checkouts;
    private int prepared;
    private int statementCloses;
    private int resultCloses;
    private int connectionCloses;
    private int rollbacks;
    private int unconfirmed;
    private int row = -1;
    private SQLException prepareFailure;
    private Runnable beforeStatementClose = () -> {};
    private Runnable beforeConnectionClose = () -> {};

    Fixture(boolean initiallyAutoCommit) {
      autoCommit = initiallyAutoCommit;
      connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    calls.add(method.getName());
                    return switch (method.getName()) {
                      case "getAutoCommit" -> autoCommit;
                      case "isReadOnly" -> true;
                      case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                      case "setReadOnly" -> {
                        assertEquals(true, args[0]);
                        yield null;
                      }
                      case "setTransactionIsolation" -> {
                        assertEquals(Connection.TRANSACTION_READ_COMMITTED, args[0]);
                        yield null;
                      }
                      case "setAutoCommit" -> {
                        assertEquals(false, args[0]);
                        autoCommit = false;
                        yield null;
                      }
                      case "prepareStatement" -> {
                        assertEquals(SQL, args[0]);
                        prepared++;
                        if (prepareFailure != null) throw prepareFailure;
                        yield statement();
                      }
                      case "rollback" -> {
                        rollbacks++;
                        yield null;
                      }
                      case "close" -> {
                        beforeConnectionClose.run();
                        connectionCloses++;
                        calls.add("connectionClose");
                        yield null;
                      }
                      default -> throw new AssertionError("unexpected synthetic connection method");
                    };
                  });
    }

    private ApiReadOnlyObservationAttempt attempt() {
      var pool =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (proxy, method, args) -> {
                    assertEquals("getConnection", method.getName());
                    checkouts++;
                    return connection;
                  });
      return new ApiReadOnlyObservationAttempt(
          pool,
          Clock.fixed(NOW, ZoneOffset.UTC),
          new OutboxObservationRepository(),
          ignored -> unconfirmed++);
    }

    private PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "setQueryTimeout" -> {
                      assertEquals(1, args[0]);
                      yield null;
                    }
                    case "executeQuery" -> resultSet();
                    case "close" -> {
                      beforeStatementClose.run();
                      statementCloses++;
                      yield null;
                    }
                    default -> throw new AssertionError("unexpected synthetic statement method");
                  });
    }

    private ResultSet resultSet() {
      row = -1;
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) ->
                  switch (method.getName()) {
                    case "next" -> {
                      row++;
                      yield row < 3;
                    }
                    case "getString" -> {
                      assertEquals("status", args[0]);
                      yield List.of("PENDING", "SENT", "ERROR").get(row);
                    }
                    case "getLong" -> {
                      assertEquals("row_count", args[0]);
                      yield new long[] {3, 5, 7}[row];
                    }
                    case "wasNull" -> false;
                    case "getObject" -> {
                      assertEquals("oldest_created_at", args[0]);
                      assertEquals(java.time.OffsetDateTime.class, args[1]);
                      yield NOW.minusSeconds(new long[] {2, 4, 6}[row]).atOffset(ZoneOffset.UTC);
                    }
                    case "close" -> {
                      resultCloses++;
                      yield null;
                    }
                    default -> throw new AssertionError("unexpected synthetic result method");
                  });
    }

    private void assertReleased(boolean owned) {
      assertEquals(1, prepared);
      assertEquals(1, statementCloses);
      assertEquals(1, resultCloses);
      assertEquals(owned ? 1 : 0, checkouts);
      assertEquals(owned ? 1 : 0, connectionCloses);
      assertEquals(owned ? 1 : 0, rollbacks);
    }
  }
}
