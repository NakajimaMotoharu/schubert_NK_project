package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLNonTransientConnectionException;
import java.time.Instant;
import java.util.Map;
import java.util.Properties;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-DAT-001; SS312/324/332/343/354; BUG1592/1595; PT-DB-INSPECTOR-GRAPH329001..009. No I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class InspectorFailureGraph329Test {
  private static final String FIXTURE_PUBLIC_CLOSE_7F17170B = "PUBLIC close";
  private static final String FIXTURE_CLOSE_97959247 = "close";
  private static final String URL = "jdbc:postgresql://127.0.0.1:1/public_fixture";

  @Test
  void inspector329001ConnectorGraphCannotBecomeUnavailable() throws Exception {
    var fatal = new AssertionError("PUBLIC fatal");
    var failure = graph(fatal, 2);
    try (var credential = material()) {
      var observed = new Properties[1];
      try (var provider =
          new InspectorDatabaseConnections(
              URL,
              credential,
              (url, properties) -> {
                observed[0] = properties;
                throw failure;
              })) {
        assertSame(fatal, assertThrows(AssertionError.class, provider::open));
        assertTrue(observed[0].isEmpty());
      }
    }
  }

  @Test
  void inspector329002AdmissionGraphClosesOnceBeforeFatalEscapes() throws Exception {
    for (int mode = 0; mode < 3; mode++) {
      var fatal = new AssertionError("PUBLIC fatal");
      var fixture =
          new Factory(graph(fatal, mode), new SQLException(FIXTURE_PUBLIC_CLOSE_7F17170B));
      withProvider(
          fixture,
          provider -> assertSame(fatal, assertThrows(AssertionError.class, provider::open)));
      assertEquals(1, fixture.closes);
      assertEquals(0, fixture.prepares);
    }
  }

  @Test
  void inspector329003DirectPrimaryAndCleanupFatalIdentitiesStayDistinct() throws Exception {
    var fatal = new AssertionError("PUBLIC primary");
    for (Throwable close :
        new Throwable[] {
          new SQLException(FIXTURE_PUBLIC_CLOSE_7F17170B),
          new IllegalStateException(FIXTURE_PUBLIC_CLOSE_7F17170B),
          new AssertionError(FIXTURE_PUBLIC_CLOSE_7F17170B),
          fatal
        }) {
      var fixture = new Factory(fatal, close);
      withProvider(
          fixture,
          provider -> assertSame(fatal, assertThrows(AssertionError.class, provider::open)));
      assertEquals(1, fixture.closes);
    }
    var secondary = new AssertionError("PUBLIC cleanup fatal");
    var fixture = new Factory(new SQLException("PUBLIC nonfatal"), secondary);
    withProvider(
        fixture,
        provider -> assertSame(secondary, assertThrows(AssertionError.class, provider::open)));
    assertEquals(1, fixture.closes);
  }

  @Test
  void inspector329004NonFatalCyclesAndSameThrowableKeepExistingOutcomes() throws Exception {
    var same = graph(null, 3);
    var sqlFixture = new Factory(same, same);
    withProvider(
        sqlFixture,
        provider -> fixed(assertThrows(SQLNonTransientConnectionException.class, provider::open)));
    assertEquals(1, sqlFixture.closes);
    var runtime = new IllegalStateException("PUBLIC primary");
    runtime.initCause(graph(null, 3));
    var runtimeFixture = new Factory(runtime, new SQLException(FIXTURE_PUBLIC_CLOSE_7F17170B));
    withProvider(
        runtimeFixture,
        provider -> assertSame(runtime, assertThrows(IllegalStateException.class, provider::open)));
    assertEquals(1, runtimeFixture.closes);
  }

  @Test
  void inspector329005SuccessfulHandoffDoesNotCloseBorrowedConnection() throws Exception {
    var fixture = new Factory(null, null);
    withProvider(
        fixture,
        provider -> {
          var actual = provider.open();
          assertSame(fixture.connection, actual);
          assertEquals(0, fixture.closes);
          actual.close();
          assertEquals(1, fixture.closes);
        });
    assertEquals(1, fixture.prepares);
    assertEquals(1, fixture.statementCloses);
    assertEquals(1, fixture.resultCloses);
  }

  @Test
  void inspector329006NullAndRejectedAdmissionRemainFixedAndClosedProviderDoesNotConnect()
      throws Exception {
    try (var credential = material()) {
      var calls = new AtomicInteger();
      var provider =
          new InspectorDatabaseConnections(
              URL,
              credential,
              (url, properties) -> {
                calls.incrementAndGet();
                return null;
              });
      try {
        fixed(assertThrows(SQLNonTransientConnectionException.class, provider::open));
        provider.close();
        fixed(assertThrows(SQLNonTransientConnectionException.class, provider::open));
        assertEquals(1, calls.get());
      } finally {
        provider.close();
      }
    }
    var fixture = new Factory(null, null);
    fixture.autoCommit = false;
    withProvider(
        fixture,
        provider -> fixed(assertThrows(SQLNonTransientConnectionException.class, provider::open)));
    assertEquals(1, fixture.closes);
    assertEquals(0, fixture.prepares);
  }

  @Test
  void inspector329007AuthenticationFalseMapperMustPreserveFatal() throws Exception {
    try (var fixture = new AuthenticationInboxInspectorTest.Fixture()) {
      var id = ResponseSnapshotIdentity.anonymous(new UUID(0, 101), "LGNRSP01", "001");
      var completion =
          fixture.saved(id, "0000", InboxResultReference.authSession(new UUID(0, 104)));
      inspect(connection -> fixture.inspector.isConsistent(connection, id, completion));
    }
  }

  @Test
  void inspector329008NonAuthenticationFalseMapperMustPreserveFatal() throws Exception {
    try (var fixture = new InboxResponseInspectorTest.Fixture()) {
      var id = ResponseSnapshotIdentity.authenticated(new UUID(0, 1), "UCRRSP01", "001", 7);
      var wire = NonAuthenticationInboxInspectorTest.wire("UCRRSP01", "9001", Map.of(), 0);
      var completion =
          fixture.saved(
              id, wire, InboxCompletionState.ERROR, Instant.parse("2026-09-09T00:00:00.123Z"));
      var inspector = new NonAuthenticationInboxInspector(fixture.codec);
      inspect(connection -> inspector.isConsistent(connection, id, completion));
    }
  }

  @Test
  void inspector329009QuestionMutationFalseMapperMustPreserveFatal() throws Exception {
    try (var fixture = new QuestionMutationInboxInspectorTest.Fixture()) {
      String route = "QSBRSP01";
      var id = QuestionMutationInboxInspectorTest.id(route);
      var token = QuestionMutationInboxInspectorTest.token(route);
      var wire = QuestionMutationInboxInspectorTest.golden(route, "0000", id.requestMessageId());
      var completion =
          QuestionMutationInboxInspectorTest.snapshot(fixture, id, "0000", wire, token);
      inspect(connection -> fixture.inspector.isConsistent(connection, id, completion, token));
    }
  }

  private static void inspect(Inspection action) throws Exception {
    for (int mode = 0; mode < 4; mode++) {
      var fatal = new AssertionError("PUBLIC fatal");
      var calls = new AtomicInteger();
      var ownedOperations = new AtomicInteger();
      var failure = graph(mode == 3 ? null : fatal, mode);
      var connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (object, method, args) -> {
                    if (method.getName().equals("getAutoCommit")) {
                      calls.incrementAndGet();
                      throw failure;
                    }
                    if (java.util.Set.of("commit", "rollback", FIXTURE_CLOSE_97959247)
                        .contains(method.getName())) ownedOperations.incrementAndGet();
                    throw new AssertionError(
                        "Unexpected borrowed connection operation: " + method.getName());
                  });
      if (mode < 3)
        assertSame(fatal, assertThrows(AssertionError.class, () -> action.run(connection)));
      else assertFalse(action.run(connection));
      assertEquals(1, calls.get());
      assertEquals(0, ownedOperations.get());
    }
  }

  private static SQLException graph(@Nullable AssertionError fatal, int mode) {
    var sql = new SQLException("PUBLIC SQL");
    var next = new SQLException("PUBLIC next");
    sql.setNextException(next);
    if (fatal != null) {
      if (mode == 0) sql.initCause(fatal);
      else if (mode == 1) sql.addSuppressed(fatal);
      else next.initCause(fatal);
    } else next.setNextException(sql);
    return sql;
  }

  private static InspectorDbCredential material() {
    // Public inert constructor bytes, never connected/authenticated or serialized as evidence.
    return InspectorDbCredential.consume(new byte[] {'P', 'U', 'B'});
  }

  private static void fixed(SQLException failure) {
    assertEquals("08001", failure.getSQLState());
    assertEquals("inspector database connection unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void withProvider(Factory fixture, ProviderAction action) throws Exception {
    try (var credential = material();
        var provider =
            new InspectorDatabaseConnections(
                URL,
                credential,
                (url, properties) -> {
                  fixture.properties = properties;
                  return fixture.connection;
                })) {
      action.run(provider);
      assertNotNull(fixture.properties);
      assertTrue(fixture.properties != null && fixture.properties.isEmpty());
      assertEquals(0, fixture.commits);
      assertEquals(0, fixture.rollbacks);
    }
  }

  @FunctionalInterface
  private interface ProviderAction {
    void run(InspectorDatabaseConnections provider) throws Exception;
  }

  @FunctionalInterface
  private interface Inspection {
    boolean run(Connection connection) throws Exception;
  }

  private static final class Factory {
    final Connection connection;
    @Nullable Properties properties;
    boolean autoCommit = true;
    int closes;
    int prepares;
    int statementCloses;
    int resultCloses;
    int rows;
    int commits;
    int rollbacks;

    Factory(@Nullable Throwable primary, @Nullable Throwable secondary) {
      connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (object, method, args) ->
                      switch (method.getName()) {
                        case "getAutoCommit" -> {
                          if (primary != null) throw primary;
                          yield autoCommit;
                        }
                        case "isReadOnly" -> false;
                        case FIXTURE_CLOSE_97959247 -> {
                          closes++;
                          if (secondary != null) throw secondary;
                          yield null;
                        }
                        case "commit" -> {
                          commits++;
                          yield null;
                        }
                        case "rollback" -> {
                          rollbacks++;
                          yield null;
                        }
                        case "prepareStatement" -> {
                          prepares++;
                          yield statement();
                        }
                        default ->
                            throw new AssertionError(
                                "Unexpected connection operation: " + method.getName());
                      });
    }

    private PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (object, method, args) ->
                  switch (method.getName()) {
                    case "executeQuery" -> result();
                    case FIXTURE_CLOSE_97959247 -> {
                      statementCloses++;
                      yield null;
                    }
                    default ->
                        throw new AssertionError(
                            "Unexpected statement operation: " + method.getName());
                  });
    }

    private ResultSet result() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (object, method, args) ->
                  switch (method.getName()) {
                    case "next" -> ++rows == 1;
                    case "getString" ->
                        switch ((String) args[0]) {
                          case "effective_role", "login_role" -> "schubert_inbox_inspector";
                          case "database_name" -> "public_fixture";
                          default -> throw new AssertionError("Unexpected column");
                        };
                    case "getObject" -> false;
                    case FIXTURE_CLOSE_97959247 -> {
                      resultCloses++;
                      yield null;
                    }
                    default ->
                        throw new AssertionError(
                            "Unexpected result operation: " + method.getName());
                  });
    }
  }
}
