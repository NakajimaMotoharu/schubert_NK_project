package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.net.InetAddress;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-AUT-001; SS312/314/324/354; SSC329/BUG1592; PT-AUTH-BOUNDARY329001..003, no I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthenticationJdbcBoundary329Test {
  private static final Instant NOW = Instant.parse("2026-10-22T00:00:00Z");
  private static final InetAddress CLIENT = InetAddress.ofLiteral("127.0.0.1");
  private static final UUID MESSAGE = UUID.fromString("00000000-0000-4000-8000-000000000001");
  private static final UUID CORRELATION = UUID.fromString("00000000-0000-4000-8000-000000000002");

  @Test
  void authBoundary329001LockPreservesFatalAfterOwnedStatementClose() {
    verify(
        1,
        fixture ->
            new LoginAttemptRepository().lockForAttempt(fixture.connection, "public", CLIENT, NOW),
        null);
  }

  @Test
  void authBoundary329002BothRecordOutcomesPreserveFatalWithoutOwningConnection() {
    for (boolean success : new boolean[] {false, true}) {
      verify(
          1,
          fixture -> {
            var locked =
                new LockedLoginAttempt(
                    "127.0.0.1", Optional.empty(), LoginAttemptState.empty(LoginAttemptKind.IP));
            if (success)
              new LoginAttemptRepository().recordSuccess(fixture.connection, locked, NOW);
            else new LoginAttemptRepository().recordFailure(fixture.connection, locked, NOW);
          },
          null);
    }
  }

  @Test
  void authBoundary329003AuditFatalCannotBecomeRetryAndAlwaysWipesInput() throws Exception {
    // Public, all-zero constructor fixture, never encrypted/issued or read from a credential file.
    try (var codec = new AuthContextCodec("v1", new byte[32], null, null)) {
      var passwordCalls = new AtomicInteger();
      var service =
          new AuthenticationService(
              new LoginAttemptRepository(),
              (password, stored) -> {
                passwordCalls.incrementAndGet();
                return false;
              },
              new AuthSessionService(new ContextHash(), codec),
              new LoginAuditWriter());
      char[] password = new char[] {'P', 'U', 'B'};
      verify(
          5,
          fixture -> {
            Arrays.fill(password, 'P');
            service.authenticate(
                fixture.connection, "public", password, CLIENT, MESSAGE, CORRELATION, NOW);
          },
          password);
      assertEquals(3, passwordCalls.get());
    }
  }

  private static void verify(int failAt, Consumer<Fixture> action, char @Nullable [] password) {
    for (int mode = 0; mode < 3; mode++) {
      var fatal = new AssertionError("PUBLIC fatal");
      var sql = new SQLException("PUBLIC primary");
      var next = new SQLException("PUBLIC next");
      sql.setNextException(next);
      if (mode == 1) next.initCause(fatal);
      else if (mode == 2) next.setNextException(sql);
      var fixture = new Fixture(failAt, sql, mode == 0 ? fatal : null);
      if (mode < 2) {
        assertSame(fatal, assertThrows(AssertionError.class, () -> action.accept(fixture)));
      } else {
        var actual =
            assertThrows(AuthenticationInfrastructureException.class, () -> action.accept(fixture));
        assertEquals("authentication storage is unavailable", actual.getMessage());
        assertNull(actual.getCause());
        assertEquals(0, actual.getSuppressed().length);
      }
      assertEquals(failAt, fixture.prepares);
      assertEquals(failAt, fixture.executes);
      assertEquals(failAt, fixture.statementCloses);
      assertEquals(failAt == 5 ? 2 : 0, fixture.resultCloses);
      assertEquals(0, fixture.connectionCloses);
      assertEquals(0, fixture.commits);
      assertEquals(0, fixture.rollbacks);
      if (password != null) assertArrayEquals(new char[3], password);
    }
  }

  private static final class Fixture {
    int prepares;
    int executes;
    int statementCloses;
    int resultCloses;
    int connectionCloses;
    int commits;
    int rollbacks;
    final Connection connection;

    Fixture(int failAt, SQLException primary, @Nullable Error closeFailure) {
      connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    return switch (method.getName()) {
                      case "getAutoCommit" -> false;
                      case "prepareStatement" -> {
                        prepares++;
                        yield statement(prepares, failAt, primary, closeFailure);
                      }
                      case "close" -> {
                        connectionCloses++;
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
                      default ->
                          throw new UnsupportedOperationException(
                              "unexpected connection fixture call");
                    };
                  });
    }

    private PreparedStatement statement(
        int index, int failAt, SQLException primary, @Nullable Error closeFailure) {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                if (method.getName().startsWith("set")) return null;
                return switch (method.getName()) {
                  case "executeQuery", "executeUpdate" -> {
                    executes++;
                    if (index == failAt) throw primary;
                    yield method.getName().equals("executeQuery") ? row(index) : 1;
                  }
                  case "close" -> {
                    statementCloses++;
                    if (index == failAt && closeFailure != null) throw closeFailure;
                    yield null;
                  }
                  default ->
                      throw new UnsupportedOperationException("unexpected statement fixture call");
                };
              });
    }

    private ResultSet row(int index) {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                return switch (method.getName()) {
                  case "next" -> index == 3;
                  case "getObject" ->
                      switch ((String) args[0]) {
                        case "failed_count" -> 0;
                        case "window_started_at" -> NOW.atOffset(ZoneOffset.UTC);
                        case "locked_until" -> null;
                        default -> throw new UnsupportedOperationException("unexpected row field");
                      };
                  case "close" -> {
                    resultCloses++;
                    yield null;
                  }
                  default -> throw new UnsupportedOperationException("unexpected row fixture call");
                };
              });
    }
  }
}
