package dev.codex.schubert.nk.batch.cleanup;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchDatabaseFixture;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Independent real PG lock ownership and public JDBC fault oracle. PT-BAT-030..037; SS341. */
final class InspectorLockHandoffTest {
  private static final String FIXTURE_TRUE_18D10C7D = "true";
  private static final String FIXTURE_FALSE_076DE6E7 = "false";
  private static final String FIXTURE_TRANSACTION_3094DE95 = "transaction";
  private static final String FIXTURE_READONLY_C4A495E7 = "readonly";
  @TempDir static Path root;
  private static BatchDatabaseFixture db;

  @BeforeAll
  static void start() throws Exception {
    db = new BatchDatabaseFixture(root);
  }

  @AfterAll
  static void stop() throws Exception {
    if (db != null) db.stop();
  }

  @Test
  void actualTransactionHandoff() throws Exception {
    try (var parent = owned();
        var observer = db.admin()) {
      for (int iteration = 0; iteration < 2; iteration++) {
        assertEquals(
            FIXTURE_TRUE_18D10C7D,
            InspectorLockHandoff.execute(
                parent,
                () -> {
                  try (var child = db.open("schubert_inbox_inspector")) {
                    child.setAutoCommit(false);
                    assertEquals(
                        FIXTURE_TRUE_18D10C7D,
                        scalar(child, "select pg_try_advisory_xact_lock(71419602)::text"));
                    assertEquals(
                        FIXTURE_FALSE_076DE6E7,
                        scalar(observer, "select pg_try_advisory_lock(71419602)::text"));
                    child.commit();
                    return FIXTURE_TRUE_18D10C7D;
                  } catch (SQLException failure) {
                    throw new IOException(failure);
                  }
                }));
        assertTrue(parent.getAutoCommit());
        assertFalse(parent.isReadOnly());
        assertFalse(parent.isClosed());
        assertEquals(
            FIXTURE_FALSE_076DE6E7,
            scalar(observer, "select pg_try_advisory_lock(71419602)::text"));
      }
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(parent, "select pg_advisory_unlock(71419602)::text"));
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(observer, "select pg_try_advisory_lock(71419602)::text"));
    }
  }

  @Test
  void preconditionsAndReentrantLock() throws Exception {
    for (String condition :
        List.of(
            "none",
            FIXTURE_TRANSACTION_3094DE95,
            FIXTURE_READONLY_C4A495E7,
            "shared",
            "two-int",
            "reentrant")) {
      try (var parent = db.open("schubert_batch")) {
        if (condition.equals(FIXTURE_TRANSACTION_3094DE95)) parent.setAutoCommit(false);
        if (condition.equals(FIXTURE_READONLY_C4A495E7)) parent.setReadOnly(true);
        if (condition.equals("shared"))
          scalar(parent, "select pg_advisory_lock_shared(71419602)::text");
        if (condition.equals("two-int"))
          scalar(parent, "select pg_advisory_lock(0,71419602)::text");
        if (condition.equals("reentrant")) {
          scalar(parent, "select pg_advisory_lock(71419602)::text");
          scalar(parent, "select pg_advisory_lock(71419602)::text");
        }
        var calls = new AtomicInteger();
        failed(
            () ->
                InspectorLockHandoff.execute(
                    parent,
                    () -> {
                      calls.incrementAndGet();
                      return 1;
                    }));
        assertEquals(0, calls.get());
        if (condition.equals("reentrant")) {
          // Exactly one of the two acquisitions was released; the helper did not force-unlock.
          assertEquals(
              FIXTURE_TRUE_18D10C7D, scalar(parent, "select pg_advisory_unlock(71419602)::text"));
          assertEquals(
              FIXTURE_FALSE_076DE6E7, scalar(parent, "select pg_advisory_unlock(71419602)::text"));
        }
      }
    }
  }

  @Test
  void callbackFailuresAndNull() throws Exception {
    assertThrows(NullPointerException.class, () -> InspectorLockHandoff.execute(null, () -> 1));
    try (var parent = owned();
        var observer = db.admin()) {
      assertThrows(NullPointerException.class, () -> InspectorLockHandoff.execute(parent, null));
      failed(
          () ->
              InspectorLockHandoff.execute(
                  parent,
                  () -> {
                    throw new IOException("private-probe");
                  }));
      assertEquals(
          FIXTURE_FALSE_076DE6E7, scalar(observer, "select pg_try_advisory_lock(71419602)::text"));
      var runtime = new IllegalStateException("public programming failure");
      assertSame(
          runtime,
          assertThrows(
              IllegalStateException.class,
              () ->
                  InspectorLockHandoff.execute(
                      parent,
                      () -> {
                        throw runtime;
                      })));
      var error = new AssertionError("public fatal failure");
      assertSame(
          error,
          assertThrows(
              AssertionError.class,
              () ->
                  InspectorLockHandoff.execute(
                      parent,
                      () -> {
                        throw error;
                      })));
      assertThrows(
          NullPointerException.class, () -> InspectorLockHandoff.execute(parent, () -> null));
      assertEquals(
          FIXTURE_FALSE_076DE6E7, scalar(observer, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(parent, "select pg_advisory_unlock(71419602)::text"));
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(observer, "select pg_try_advisory_lock(71419602)::text"));
    }
  }

  @Test
  void reacquisitionConflict() throws Exception {
    try (var parent = owned();
        var other = db.admin()) {
      var calls = new AtomicInteger();
      failed(
          () ->
              InspectorLockHandoff.execute(
                  parent,
                  () -> {
                    try {
                      calls.incrementAndGet();
                      assertEquals(
                          FIXTURE_TRUE_18D10C7D,
                          scalar(other, "select pg_try_advisory_lock(71419602)::text"));
                      return "must not escape";
                    } catch (SQLException failure) {
                      throw new IOException(failure);
                    }
                  }));
      assertEquals(1, calls.get());
      assertEquals(
          FIXTURE_FALSE_076DE6E7, scalar(parent, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(other, "select pg_advisory_unlock(71419602)::text"));
    }
  }

  @Test
  void callbackIdentitySurvivesReacquisitionSqlFailure() throws Exception {
    for (String kind : List.of("runtime", "error", "io")) {
      var probe = new HandoffJdbcProbe();
      probe.failAt.put("connection.prepareStatement", 4);
      var calls = new AtomicInteger();
      try (var parent = owned()) {
        var wrapped = probe.wrap(parent);
        if (kind.equals("runtime")) {
          var marker = new IllegalStateException("public callback marker");
          assertSame(
              marker,
              assertThrows(
                  IllegalStateException.class,
                  () ->
                      InspectorLockHandoff.execute(
                          wrapped,
                          () -> {
                            calls.incrementAndGet();
                            throw marker;
                          })));
          fixedSecondary(marker);
        } else if (kind.equals("error")) {
          var marker = new AssertionError("public callback marker");
          assertSame(
              marker,
              assertThrows(
                  AssertionError.class,
                  () ->
                      InspectorLockHandoff.execute(
                          wrapped,
                          () -> {
                            calls.incrementAndGet();
                            throw marker;
                          })));
          fixedSecondary(marker);
        } else {
          failed(
              () ->
                  InspectorLockHandoff.execute(
                      wrapped,
                      () -> {
                        calls.incrementAndGet();
                        throw new IOException("private callback probe");
                      }));
        }
        assertEquals(1, calls.get());
        assertEquals(1, probe.failures);
        assertEquals(4, probe.seen.get("connection.prepareStatement"));
        assertEquals(3, probe.queries);
        resourcesClosed(probe);
      }
    }
  }

  private static void fixedSecondary(Throwable primary) {
    assertEquals(1, primary.getSuppressed().length);
    var secondary =
        assertInstanceOf(InspectorLockHandoff.Failure.class, primary.getSuppressed()[0]);
    assertEquals("maintenance lock handoff failed", secondary.getMessage());
    assertNull(secondary.getCause());
    assertEquals(0, secondary.getSuppressed().length);
  }

  @Test
  void jdbcFailureMatrix() throws Exception {
    var inventory =
        Map.of(
            "connection.getAutoCommit",
            2,
            "connection.isReadOnly",
            2,
            "connection.prepareStatement",
            5,
            "statement.setQueryTimeout",
            5,
            "statement.executeQuery",
            5,
            "row.next",
            10,
            "row.getObject",
            5,
            "row.close",
            5,
            "statement.close",
            5);
    try (var parent = owned()) {
      var probe = new HandoffJdbcProbe();
      assertEquals("done", InspectorLockHandoff.execute(probe.wrap(parent), () -> "done"));
      assertEquals(inventory, probe.seen);
      resourcesClosed(probe);
    }
    for (var entry : inventory.entrySet())
      for (int occurrence = 1; occurrence <= entry.getValue(); occurrence++) {
        var probe = new HandoffJdbcProbe();
        probe.failAt.put(entry.getKey(), occurrence);
        try (var parent = owned()) {
          failed(() -> InspectorLockHandoff.execute(probe.wrap(parent), () -> "done"));
          assertEquals(1, probe.failures);
          resourcesClosed(probe);
        }
      }
  }

  @Test
  void invalidResultMatrix() throws Exception {
    for (int query = 1; query <= 5; query++) {
      for (String anomaly :
          List.of("missing", "duplicate", "null", "flip", "nullStatement", "nullRows")) {
        var probe = new HandoffJdbcProbe();
        probe.anomalies.put(query, anomaly);
        var calls = new AtomicInteger();
        try (var parent = owned()) {
          failed(
              () ->
                  InspectorLockHandoff.execute(
                      probe.wrap(parent),
                      () -> {
                        calls.incrementAndGet();
                        return 1;
                      }));
          assertEquals(query <= 3 ? 0 : 1, calls.get());
          resourcesClosed(probe);
        }
      }
      // Multiple close failures must not leak when a checked primary SQL error already exists.
      var probe = new HandoffJdbcProbe();
      probe.anomalies.put(query, "missing");
      probe.failAt.put("row.close", query);
      probe.failAt.put("statement.close", query);
      try (var parent = owned()) {
        failed(() -> InspectorLockHandoff.execute(probe.wrap(parent), () -> 1));
        assertEquals(2, probe.failures);
        resourcesClosed(probe);
      }
    }
  }

  @Test
  void stateChangesAndInterrupts() throws Exception {
    var probe = new HandoffJdbcProbe();
    try (var parent = owned()) {
      try {
        Thread.currentThread().interrupt();
        failed(() -> InspectorLockHandoff.execute(probe.wrap(parent), () -> 1));
        assertTrue(Thread.currentThread().isInterrupted());
        assertTrue(probe.seen.isEmpty());
      } finally {
        Thread.interrupted();
      }
    }
    for (String change :
        List.of(FIXTURE_TRANSACTION_3094DE95, FIXTURE_READONLY_C4A495E7, "interrupt")) {
      try (var parent = owned()) {
        try {
          failed(
              () ->
                  InspectorLockHandoff.execute(
                      parent,
                      () -> {
                        try {
                          if (change.equals(FIXTURE_TRANSACTION_3094DE95))
                            parent.setAutoCommit(false);
                          if (change.equals(FIXTURE_READONLY_C4A495E7)) parent.setReadOnly(true);
                          if (change.equals("interrupt")) Thread.currentThread().interrupt();
                          return 1;
                        } catch (SQLException failure) {
                          throw new IOException(failure);
                        }
                      }));
          assertEquals(change.equals("interrupt"), Thread.currentThread().isInterrupted());
        } finally {
          Thread.interrupted();
        }
      }
    }
  }

  @Test
  void concurrentGapCompetition() throws Exception {
    var gap = new CountDownLatch(1);
    var acquired = new CountDownLatch(1);
    try (var parent = owned();
        var other = db.admin();
        var executor = Executors.newSingleThreadExecutor()) {
      var future =
          executor.submit(
              () ->
                  failed(
                      () ->
                          InspectorLockHandoff.execute(
                              parent,
                              () -> {
                                gap.countDown();
                                try {
                                  assertTrue(acquired.await(5, TimeUnit.SECONDS));
                                } catch (InterruptedException failure) {
                                  Thread.currentThread().interrupt();
                                  throw new IOException(failure);
                                }
                                return 1;
                              })));
      try {
        assertTrue(gap.await(5, TimeUnit.SECONDS));
        assertEquals(
            FIXTURE_TRUE_18D10C7D, scalar(other, "select pg_try_advisory_lock(71419602)::text"));
      } finally {
        acquired.countDown();
      }
      assertNotNull(future.get(5, TimeUnit.SECONDS));
      assertEquals(
          FIXTURE_FALSE_076DE6E7, scalar(parent, "select pg_try_advisory_lock(71419602)::text"));
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(other, "select pg_advisory_unlock(71419602)::text"));
    }
  }

  private static Connection owned() throws SQLException {
    var connection = db.open("schubert_batch");
    try {
      assertEquals(
          FIXTURE_TRUE_18D10C7D, scalar(connection, "select pg_try_advisory_lock(71419602)::text"));
    } catch (SQLException | RuntimeException | Error failure) {
      connection.close();
      throw failure;
    }
    return connection;
  }

  private static String scalar(Connection connection, String sql) throws SQLException {
    try (var statement = connection.createStatement();
        var row = statement.executeQuery(sql)) {
      assertTrue(row.next());
      String value = row.getString(1);
      assertFalse(row.next());
      return value;
    }
  }

  private static InspectorLockHandoff.Failure failed(Runnable action) {
    var failure = assertThrows(InspectorLockHandoff.Failure.class, action::run);
    assertEquals("maintenance lock handoff failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    return failure;
  }

  private static void resourcesClosed(HandoffJdbcProbe probe) {
    assertEquals(probe.openedRows, probe.closedRows);
    assertEquals(probe.openedStatements, probe.closedStatements);
    for (String key : List.of("connection.commit", "connection.rollback", "connection.close"))
      assertFalse(probe.seen.containsKey(key));
  }
}
