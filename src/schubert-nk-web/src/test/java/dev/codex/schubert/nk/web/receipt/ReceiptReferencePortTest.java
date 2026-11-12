package dev.codex.schubert.nk.web.receipt;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** PT-WEB-RCPTPORT001..009. JDBC interfaces only; no driver, SQL engine, DB or real locator. */
final class ReceiptReferencePortTest {
  private static final String ID = "00000000000000000000000001";
  private static final String OTHER_ID = "00000000000000000000000002";
  private static final Instant AT = Instant.parse("2026-10-04T00:00:00.123Z");
  private static final String SELECT =
      "select receipt_id,question_id,submitted_at from schubert_web_session.web_receipt_references"
          + " where receipt_id=?";
  private static final String INSERT =
      "insert into schubert_web_session.web_receipt_references"
          + " (receipt_id,question_id,submitted_at) values (?,?,?) on conflict(receipt_id) do"
          + " nothing";
  private static final String POINT_SELECT = "select";
  private static final String POINT_AUTO = "auto";
  private static final String POINT_READONLY = "readonly";
  private static final String POINT_ISOLATION = "isolation";
  private static final String POINT_FIRST_NEXT = "next1";
  private static final String POINT_ROW_CLOSE = "rowClose";
  private static final String POINT_STATEMENT_CLOSE = "statementClose";
  private static final String POINT_COMMIT = "commit";
  private static final String POINT_CONNECTION_CLOSE = "connectionClose";
  private static final String POINT_ROLLBACK = "rollback";
  private static final String FIXED_DIAGNOSTIC = "receipt reference unavailable";

  @Test
  void literalSqlBindingsAndOwnedOrderMatchThreeColumnLocator() {
    Fixture fixture = new Fixture();
    var repository = new ReceiptReferenceRepository(fixture.source());
    var actual = repository.find(ID).orElseThrow();
    assertEquals(ID, actual.receiptId());
    assertEquals(7, actual.questionId());
    assertEquals(AT, actual.submittedAt());
    Conn first = fixture.connections.getFirst();
    assertEquals(
        List.of(
            POINT_AUTO,
            POINT_READONLY,
            POINT_ISOLATION,
            POINT_SELECT,
            "bind1",
            "query",
            POINT_FIRST_NEXT,
            "id",
            "question",
            "time",
            "next2",
            POINT_ROW_CLOSE,
            POINT_STATEMENT_CLOSE,
            POINT_COMMIT,
            POINT_CONNECTION_CLOSE),
        first.events);
    assertEquals(Map.of(1, ID), first.statements.getFirst().bindings);
    repository.register(new ReceiptReference(ID, 7, AT));
    Conn inserted = fixture.connections.getLast();
    assertEquals(2, inserted.statements.size());
    assertEquals(INSERT, inserted.statements.getFirst().sql);
    assertEquals(
        Map.of(1, ID, 2, 7L, 3, AT.atOffset(ZoneOffset.UTC)),
        inserted.statements.getFirst().bindings);
    assertEquals(SELECT, inserted.statements.getLast().sql);
    assertTrue(inserted.events.indexOf(POINT_STATEMENT_CLOSE) < inserted.events.indexOf("select"));
    assertEquals(1, inserted.commits);
    assertEquals(0, inserted.rollbacks);
    assertEquals(1, inserted.closeAttempts);
    assertEquals(2, fixture.connectAttempts.get());
  }

  @Test
  void absentRepeatedAndConflictingTuplesNeverBecomeAnUpdateOrAcceptanceProof() {
    Fixture absent = new Fixture();
    absent.rows = List.of();
    assertEquals(Optional.empty(), new ReceiptReferenceRepository(absent.source()).find(ID));
    assertEquals(1, absent.connections.getFirst().commits);
    for (int count : new int[] {0, 1}) {
      Fixture fixture = new Fixture();
      fixture.changed = count;
      var repository = new ReceiptReferenceRepository(fixture.source());
      repository.register(new ReceiptReference(ID, 7, AT));
      repository.register(new ReceiptReference(ID, 7, AT));
      assertEquals(2, fixture.connections.size());
      for (Conn connection : fixture.connections) assertEquals(1, connection.commits);
    }
    for (boolean missing : new boolean[] {false, true}) {
      Fixture fixture = new Fixture();
      if (missing) fixture.rows = List.of();
      var repository = new ReceiptReferenceRepository(fixture.source());
      catalog(() -> repository.register(new ReceiptReference(ID, 8, AT)));
      Conn connection = fixture.connections.getFirst();
      assertEquals(0, connection.commits);
      assertEquals(1, connection.rollbacks);
      assertEquals(1, connection.closeAttempts);
      assertEquals(INSERT, connection.statements.getFirst().sql);
    }
  }

  @Test
  void nullAcquisitionsColumnsAndInvalidProjectionFailWithoutNpeOrEscapingResources() {
    Fixture constructor = new Fixture();
    var repository = new ReceiptReferenceRepository(constructor.source());
    assertThrows(NullPointerException.class, () -> new ReceiptReferenceRepository(null));
    assertThrows(NullPointerException.class, () -> repository.register(null));
    assertThrows(NullPointerException.class, () -> repository.find(null));
    assertThrows(IllegalArgumentException.class, () -> repository.find("invalid"));
    assertEquals(0, constructor.connectAttempts.get());
    for (String missing : List.of("connection", "statement", "row")) {
      Fixture fixture = new Fixture();
      fixture.missing = missing;
      catalog(() -> new ReceiptReferenceRepository(fixture.source()).find(ID));
      if (!missing.equals("connection")) {
        assertEquals(1, fixture.connections.getFirst().rollbacks);
        assertEquals(1, fixture.connections.getFirst().closeAttempts);
      } else assertTrue(fixture.connections.isEmpty());
    }
    for (Row row :
        List.of(
            new Row(null, 7L, AT.atOffset(ZoneOffset.UTC)),
            new Row(ID, null, AT.atOffset(ZoneOffset.UTC)),
            new Row(ID, 7L, null),
            new Row("I".repeat(26), 7L, AT.atOffset(ZoneOffset.UTC)),
            new Row(ID, 0L, AT.atOffset(ZoneOffset.UTC)),
            new Row(ID, 7L, AT.plusNanos(1).atOffset(ZoneOffset.UTC)),
            new Row(OTHER_ID, 7L, AT.atOffset(ZoneOffset.UTC)))) {
      Fixture fixture = new Fixture();
      fixture.rows = List.of(row);
      catalog(() -> new ReceiptReferenceRepository(fixture.source()).find(ID));
      assertEquals(1, fixture.connections.getFirst().rollbacks);
      assertEquals(1, fixture.connections.getFirst().closeAttempts);
    }
    Fixture duplicate = new Fixture();
    duplicate.rows = List.of(valid(), valid());
    catalog(() -> new ReceiptReferenceRepository(duplicate.source()).find(ID));
  }

  @Test
  void impossibleUpdateCountsAreRejectedBeforeReadAndCommit() {
    for (int count : new int[] {-1, 2, Integer.MIN_VALUE, Integer.MAX_VALUE}) {
      Fixture fixture = new Fixture();
      fixture.changed = count;
      catalog(
          () ->
              new ReceiptReferenceRepository(fixture.source())
                  .register(new ReceiptReference(ID, 7, AT)));
      Conn connection = fixture.connections.getFirst();
      assertEquals(1, connection.statements.size());
      assertEquals(0, connection.commits);
      assertEquals(1, connection.rollbacks);
      assertEquals(1, connection.closeAttempts);
    }
  }

  @Test
  void eachProviderFailureRollsBackAndAttemptsOwnedCloseBeforeCatalogOrIdentityEscapes() {
    for (String point :
        List.of(
            "connect",
            POINT_AUTO,
            POINT_READONLY,
            POINT_ISOLATION,
            "prepare",
            "bind",
            "query",
            POINT_FIRST_NEXT,
            "id",
            "question",
            "time",
            "next2",
            POINT_ROW_CLOSE,
            POINT_STATEMENT_CLOSE,
            POINT_COMMIT,
            POINT_CONNECTION_CLOSE)) {
      for (Throwable failure : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults = Map.of(point, failure);
        expected(failure, () -> new ReceiptReferenceRepository(fixture.source()).find(ID));
        if (point.equals("connect")) assertTrue(fixture.connections.isEmpty());
        else {
          Conn connection = fixture.connections.getFirst();
          assertEquals(1, connection.closeAttempts, point);
          boolean beforeWork =
              List.of(POINT_AUTO, POINT_READONLY, POINT_ISOLATION, POINT_CONNECTION_CLOSE)
                  .contains(point);
          assertEquals(beforeWork ? 0 : 1, connection.rollbacks, point);
        }
      }
    }
    for (Throwable failure : failures()) {
      Fixture fixture = new Fixture();
      fixture.faults = Map.of("update", failure);
      expected(
          failure,
          () ->
              new ReceiptReferenceRepository(fixture.source())
                  .register(new ReceiptReference(ID, 7, AT)));
      assertEquals(1, fixture.connections.getFirst().rollbacks);
      assertEquals(1, fixture.connections.getFirst().closeAttempts);
    }
  }

  @Test
  void insertStatementCloseUsesIndependentPrimaryAndSecondarySelectionTable() {
    for (Throwable secondary : failures()) {
      for (int primaryKind : new int[] {0, 1, 2, 3}) {
        Fixture fixture = new Fixture();
        Throwable primary =
            switch (primaryKind) {
              case 0 -> null;
              case 1 -> new SQLException("own insert SQL");
              case 2 -> new IllegalStateException("own insert runtime");
              default -> new AssertionError("own insert error");
            };
        fixture.faults =
            primary == null
                ? Map.of(POINT_STATEMENT_CLOSE, secondary)
                : Map.of("update", primary, POINT_STATEMENT_CLOSE, secondary);
        // SS331/332 and rcpt005: SQL is catalogued; unknown primary keeps identity.
        Throwable selected =
            primary instanceof RuntimeException
                    || primary instanceof Error
                    || (primaryKind == 1 && secondary instanceof SQLException)
                ? primary
                : secondary;
        expected(
            selected,
            () ->
                new ReceiptReferenceRepository(fixture.source())
                    .register(new ReceiptReference(ID, 7, AT)));
        Conn connection = fixture.connections.getFirst();
        assertEquals(1, connection.statements.size());
        assertEquals(0, connection.commits);
        assertEquals(1, connection.rollbacks);
        assertEquals(1, connection.closeAttempts);
        assertEquals(1, connection.events.stream().filter(POINT_STATEMENT_CLOSE::equals).count());
        assertTrue(!connection.events.contains(POINT_SELECT));
        if (primary instanceof RuntimeException || primary instanceof Error) {
          assertEquals(1, primary.getSuppressed().length);
          assertInstanceOf(ReceiptReferenceException.class, primary.getSuppressed()[0]);
          assertEquals(FIXED_DIAGNOSTIC, primary.getSuppressed()[0].getMessage());
        }
      }
    }
  }

  @Test
  void knownPrimaryAndCleanupPrecedenceMatchIndependentSqlUnknownTable() {
    for (String close :
        List.of(POINT_ROW_CLOSE, POINT_STATEMENT_CLOSE, POINT_ROLLBACK, POINT_CONNECTION_CLOSE)) {
      for (Throwable secondary : failures()) {
        Fixture fixture = new Fixture();
        fixture.faults =
            Map.of(POINT_FIRST_NEXT, new SQLException("own primary SQL"), close, secondary);
        expected(secondary, () -> new ReceiptReferenceRepository(fixture.source()).find(ID));
        assertEquals(1, fixture.connections.getFirst().closeAttempts);
      }
    }
    for (String close :
        List.of(POINT_ROW_CLOSE, POINT_STATEMENT_CLOSE, POINT_ROLLBACK, POINT_CONNECTION_CLOSE)) {
      AssertionError fatal = new AssertionError("own hidden fatal");
      SQLException secondary = new SQLException("own secondary SQL", fatal);
      Fixture fixture = new Fixture();
      fixture.faults =
          Map.of(POINT_FIRST_NEXT, new SQLException("own primary SQL"), close, secondary);
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () -> new ReceiptReferenceRepository(fixture.source()).find(ID)));
      assertEquals(1, fixture.connections.getFirst().closeAttempts);
    }
    SQLException repeated = new SQLException("own repeated SQL");
    Fixture identical = new Fixture();
    identical.faults = Map.of(POINT_FIRST_NEXT, repeated, POINT_ROW_CLOSE, repeated);
    catalog(() -> new ReceiptReferenceRepository(identical.source()).find(ID));
  }

  @Test
  void originalUnknownKeepsIdentityAndOnlyFixedSecondaryDiagnostics() {
    for (String close :
        List.of(POINT_ROW_CLOSE, POINT_STATEMENT_CLOSE, POINT_ROLLBACK, POINT_CONNECTION_CLOSE)) {
      for (boolean error : new boolean[] {false, true}) {
        for (Throwable secondary : failures()) {
          Throwable primary =
              error
                  ? new AssertionError("own primary unknown")
                  : new IllegalStateException("own primary unknown");
          Fixture fixture = new Fixture();
          fixture.faults = Map.of(POINT_FIRST_NEXT, primary, close, secondary);
          Throwable actual;
          if (error)
            actual =
                assertThrows(
                    AssertionError.class,
                    () -> new ReceiptReferenceRepository(fixture.source()).find(ID));
          else
            actual =
                assertThrows(
                    IllegalStateException.class,
                    () -> new ReceiptReferenceRepository(fixture.source()).find(ID));
          assertSame(primary, actual);
          assertEquals(1, actual.getSuppressed().length);
          assertInstanceOf(ReceiptReferenceException.class, actual.getSuppressed()[0]);
          assertEquals(FIXED_DIAGNOSTIC, actual.getSuppressed()[0].getMessage());
          assertNull(actual.getSuppressed()[0].getCause());
          assertEquals(1, fixture.connections.getFirst().closeAttempts);
        }
      }
    }
    IllegalStateException repeated = new IllegalStateException("own repeated unknown");
    Fixture identical = new Fixture();
    identical.faults = Map.of(POINT_FIRST_NEXT, repeated, POINT_ROW_CLOSE, repeated);
    assertSame(
        repeated,
        assertThrows(
            IllegalStateException.class,
            () -> new ReceiptReferenceRepository(identical.source()).find(ID)));
    assertEquals(1, repeated.getSuppressed().length);
    assertInstanceOf(ReceiptReferenceException.class, repeated.getSuppressed()[0]);
    RuntimeException disabled = new NoSuppression();
    Fixture noSuppression = new Fixture();
    noSuppression.faults =
        Map.of(POINT_FIRST_NEXT, disabled, POINT_ROW_CLOSE, new SQLException("own secondary"));
    assertSame(
        disabled,
        assertThrows(
            RuntimeException.class,
            () -> new ReceiptReferenceRepository(noSuppression.source()).find(ID)));
    assertEquals(0, disabled.getSuppressed().length);
  }

  @Test
  void concurrentIndependentReadsNeverShareConnectionsStatementsOrResults() throws Exception {
    Fixture fixture = new Fixture();
    var repository = new ReceiptReferenceRepository(fixture.source());
    var workers = Executors.newFixedThreadPool(2);
    try {
      var first = workers.submit(() -> repository.find(ID).orElseThrow());
      var second = workers.submit(() -> repository.find(ID).orElseThrow());
      for (var future : List.of(first, second)) {
        var value = future.get(5, TimeUnit.SECONDS);
        assertEquals(ID, value.receiptId());
        assertEquals(7, value.questionId());
        assertEquals(AT, value.submittedAt());
      }
    } finally {
      workers.shutdownNow();
      if (!workers.awaitTermination(10, TimeUnit.SECONDS)) {
        throw new AssertionError("receipt reference workers did not terminate");
      }
    }
    assertEquals(2, fixture.connections.size());
    assertNotSame(fixture.connections.getFirst(), fixture.connections.getLast());
    assertNotSame(
        fixture.connections.getFirst().statements.getFirst(),
        fixture.connections.getLast().statements.getFirst());
    for (Conn connection : fixture.connections) {
      assertEquals(1, connection.commits);
      assertEquals(0, connection.rollbacks);
      assertEquals(1, connection.closeAttempts);
      assertEquals(POINT_CONNECTION_CLOSE, connection.events.getLast());
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("own SQL"),
        new IllegalStateException("own unknown"),
        new AssertionError("own error"));
  }

  private static void expected(Throwable failure, Executable action) {
    if (failure instanceof SQLException) catalog(action);
    else if (failure instanceof AssertionError)
      assertSame(failure, assertThrows(AssertionError.class, action));
    else assertSame(failure, assertThrows(IllegalStateException.class, action));
  }

  private static void catalog(Executable action) {
    var failure = assertThrows(ReceiptReferenceException.class, action);
    assertEquals(FIXED_DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static Row valid() {
    return new Row(ID, 7L, AT.atOffset(ZoneOffset.UTC));
  }

  private record Row(String id, Long question, OffsetDateTime time) {}

  private static final class NoSuppression extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppression() {
      super("own suppression-disabled unknown", null, false, false);
    }
  }

  private static final class Fixture {
    final AtomicInteger connectAttempts = new AtomicInteger();
    final List<Conn> connections = new CopyOnWriteArrayList<>();
    List<Row> rows = List.of(valid());
    Map<String, Throwable> faults = Map.of();
    String missing = "none";
    int changed = 1;

    void fault(String point) throws Throwable {
      Throwable failure = faults.get(point);
      if (failure != null) throw failure;
    }

    DataSource source() {
      return proxy(
          DataSource.class,
          (object, method, args) -> {
            if (!method.getName().equals("getConnection"))
              throw new AssertionError("unexpected data source method");
            connectAttempts.incrementAndGet();
            fault("connect");
            if (missing.equals("connection")) return null;
            Conn connection = new Conn(this);
            connections.add(connection);
            return connection.proxy;
          });
    }
  }

  private static final class Conn {
    final Fixture fixture;
    final List<String> events = new ArrayList<>();
    final List<Statement> statements = new ArrayList<>();
    final Connection proxy;
    int commits;
    int rollbacks;
    int closeAttempts;

    Conn(Fixture fixture) {
      this.fixture = fixture;
      proxy =
          proxy(
              Connection.class,
              (object, method, args) -> {
                switch (method.getName()) {
                  case "setAutoCommit" -> {
                    assertEquals(Boolean.FALSE, args[0]);
                    event(POINT_AUTO);
                  }
                  case "setReadOnly" -> {
                    assertEquals(Boolean.FALSE, args[0]);
                    event(POINT_READONLY);
                  }
                  case "setTransactionIsolation" -> {
                    assertEquals(2, args[0]);
                    event(POINT_ISOLATION);
                  }
                  case "prepareStatement" -> {
                    event("prepare");
                    String sql = (String) args[0];
                    assertTrue(sql.equals(INSERT) || sql.equals(SELECT));
                    if (fixture.missing.equals("statement")) return null;
                    Statement statement = new Statement(this, sql);
                    statements.add(statement);
                    events.add(sql.equals(INSERT) ? "insert" : "select");
                    return statement.proxy;
                  }
                  case POINT_COMMIT -> {
                    commits++;
                    event(POINT_COMMIT);
                  }
                  case POINT_ROLLBACK -> {
                    rollbacks++;
                    event(POINT_ROLLBACK);
                  }
                  case "close" -> {
                    closeAttempts++;
                    event(POINT_CONNECTION_CLOSE);
                  }
                  default ->
                      throw new AssertionError("unexpected connection method: " + method.getName());
                }
                return null;
              });
    }

    void event(String point) throws Throwable {
      if (!point.equals("prepare")) events.add(point);
      fixture.fault(point);
    }
  }

  private static final class Statement {
    final Conn connection;
    final String sql;
    final Map<Integer, Object> bindings = new HashMap<>();
    final PreparedStatement proxy;

    Statement(Conn connection, String sql) {
      this.connection = connection;
      this.sql = sql;
      proxy =
          proxy(
              PreparedStatement.class,
              (object, method, args) -> {
                switch (method.getName()) {
                  case "setString", "setLong", "setObject" -> {
                    bindings.put((Integer) args[0], args[1]);
                    connection.events.add("bind" + args[0]);
                    connection.fixture.fault("bind");
                  }
                  case "executeUpdate" -> {
                    connection.event("update");
                    return connection.fixture.changed;
                  }
                  case "executeQuery" -> {
                    connection.event("query");
                    if (connection.fixture.missing.equals("row")) return null;
                    return row();
                  }
                  case "close" -> connection.event(POINT_STATEMENT_CLOSE);
                  default ->
                      throw new AssertionError("unexpected statement method: " + method.getName());
                }
                return null;
              });
    }

    ResultSet row() {
      int[] cursor = {-1};
      return proxy(
          ResultSet.class,
          (object, method, args) -> {
            switch (method.getName()) {
              case "next" -> {
                cursor[0]++;
                connection.event("next" + (cursor[0] + 1));
                return cursor[0] < connection.fixture.rows.size();
              }
              case "getString" -> {
                assertEquals("receipt_id", args[0]);
                connection.event("id");
                return connection.fixture.rows.get(cursor[0]).id();
              }
              case "getObject" -> {
                if (args[0].equals("question_id")) {
                  assertSame(Long.class, args[1]);
                  connection.event("question");
                  return connection.fixture.rows.get(cursor[0]).question();
                }
                assertEquals("submitted_at", args[0]);
                assertSame(OffsetDateTime.class, args[1]);
                connection.event("time");
                return connection.fixture.rows.get(cursor[0]).time();
              }
              case "close" -> {
                connection.event(POINT_ROW_CLOSE);
                return null;
              }
              default -> throw new AssertionError("unexpected row method: " + method.getName());
            }
          });
    }
  }

  private static <T> T proxy(Class<T> type, java.lang.reflect.InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
