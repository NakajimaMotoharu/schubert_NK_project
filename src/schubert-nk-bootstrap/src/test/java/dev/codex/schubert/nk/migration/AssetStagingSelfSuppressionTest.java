package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS366/450, BUG3136/YKT2607; independent JDBC-interface fixtures, no database or driver. */
final class AssetStagingSelfSuppressionTest {
  private static final String MARKER = "PUBLIC_INJECTED_SELF_FAILURE";

  @Test
  void assetSelf001SameBodyAndCloseObjectNeverSelfSuppressesInEitherOwnedScope() {
    for (boolean resultScope : List.of(false, true)) {
      for (int kind = 0; kind < 3; kind++) {
        Throwable failure =
            switch (kind) {
              case 0 -> new SQLException(MARKER);
              case 1 -> new IllegalStateException(MARKER);
              default -> new AssertionError(MARKER);
            };
        var fixture = new Fixture(resultScope, failure);
        var tables = new AssetStagingTables();
        Throwable actual =
            assertThrows(
                failure.getClass(),
                () -> {
                  if (resultScope) tables.transfer(fixture.connection, 1, 1, 1);
                  else tables.prepare(fixture.connection);
                });
        assertSame(failure, actual);
        assertEquals(0, actual.getSuppressed().length);
        assertEquals(1, fixture.autoCommitReads);
        assertEquals(1, fixture.statementsCreated);
        assertEquals(1, fixture.statementsClosed);
        assertEquals(resultScope ? 1 : 0, fixture.queries);
        assertEquals(resultScope ? 1 : 0, fixture.nextCalls);
        assertEquals(resultScope ? 1 : 0, fixture.resultsClosed);
      }
    }
  }

  private static final class Fixture {
    private final Connection connection;
    private int autoCommitReads;
    private int statementsCreated;
    private int statementsClosed;
    private int queries;
    private int nextCalls;
    private int resultsClosed;

    private Fixture(boolean resultScope, Throwable failure) {
      ResultSet result =
          proxy(
              ResultSet.class,
              (ignored, method, arguments) -> {
                switch (method.getName()) {
                  case "next" -> {
                    nextCalls++;
                    throw failure;
                  }
                  case "close" -> {
                    resultsClosed++;
                    throw failure;
                  }
                  default -> throw new AssertionError("unexpected result operation");
                }
              });
      Statement statement =
          proxy(
              Statement.class,
              (ignored, method, arguments) -> {
                switch (method.getName()) {
                  case "setQueryTimeout" -> {
                    assertNotNull(arguments);
                    assertEquals(Integer.valueOf(30), arguments[0]);
                    if (!resultScope) throw failure;
                    return null;
                  }
                  case "executeQuery" -> {
                    assertTrue(resultScope);
                    assertNotNull(arguments);
                    assertEquals("SELECT count(*) FROM schubert.audio_files", arguments[0]);
                    queries++;
                    return result;
                  }
                  case "close" -> {
                    statementsClosed++;
                    if (!resultScope) throw failure;
                    return null;
                  }
                  default -> throw new AssertionError("unexpected statement operation");
                }
              });
      connection =
          proxy(
              Connection.class,
              (ignored, method, arguments) -> {
                switch (method.getName()) {
                  case "getAutoCommit" -> {
                    autoCommitReads++;
                    return false;
                  }
                  case "createStatement" -> {
                    statementsCreated++;
                    return statement;
                  }
                  default -> throw new AssertionError("borrowed connection operation forbidden");
                }
              });
    }
  }

  private static <T> T proxy(Class<T> type, InvocationHandler handler) {
    return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, handler));
  }
}
