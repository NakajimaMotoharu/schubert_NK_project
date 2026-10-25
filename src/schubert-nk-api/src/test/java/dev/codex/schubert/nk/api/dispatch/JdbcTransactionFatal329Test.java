package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-AUT-001/NK-MSG-002; SS312/324/354; SSC329/BUG1592; PT-TX-GRAPH329001..008. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class JdbcTransactionFatal329Test {
  private static final Instant NOW = Instant.parse("2026-10-21T00:00:00Z");

  @Test
  void tx329001SqlPrimaryAndCloseFatalRetainIdentityAfterRollback() {
    var fixture = new Fixture();
    var fatal = new AssertionError("PUBLIC close");
    fixture.closeFailure = fatal;
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class, () -> fixture.process(new SQLException("PUBLIC primary"))));
    assertEquals(List.of("acquire", "auto:false", "handle", "rollback", "close"), fixture.events);
  }

  @Test
  void tx329002ProtocolPrimaryAndCloseFatalCannotBecomeTemporary() {
    var fixture = new Fixture();
    var fatal = new AssertionError("PUBLIC close");
    fixture.closeFailure = fatal;
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> fixture.process(new PermanentProtocolException("PUBLIC primary"))));
    assertEquals(List.of("acquire", "auto:false", "handle", "rollback", "close"), fixture.events);
  }

  @Test
  void tx329003DirectFatalRollsBackOnceDespiteSecondaryAndSameClose() {
    var fixture = new Fixture();
    var fatal = new AssertionError("PUBLIC primary");
    fixture.rollbackFailure = new IllegalStateException("PUBLIC rollback");
    fixture.closeFailure = fatal;
    assertSame(fatal, assertThrows(AssertionError.class, () -> fixture.process(fatal)));
    assertEquals(List.of("acquire", "auto:false", "handle", "rollback", "close"), fixture.events);
  }

  @Test
  void tx329004CommitFatalWinsOverRollbackAndCloseFatals() {
    var fixture = new Fixture();
    var fatal = new AssertionError("PUBLIC commit");
    fixture.commitFailure = fatal;
    fixture.rollbackFailure = new AssertionError("PUBLIC rollback");
    fixture.closeFailure = new AssertionError("PUBLIC close");
    assertSame(fatal, assertThrows(AssertionError.class, () -> fixture.process(null)));
    assertEquals(
        List.of("acquire", "auto:false", "handle", "commit", "rollback", "close"), fixture.events);
  }

  @Test
  void tx329005NonFatalCycleReturnsOnlyTheFixedCatalog() {
    var fixture = new Fixture();
    var first = new SQLException("PUBLIC first");
    var second = new SQLException("PUBLIC second");
    first.setNextException(second);
    second.setNextException(first);
    fixture.rollbackFailure = second;
    var actual = assertThrows(TemporaryInfrastructureException.class, () -> fixture.process(first));
    assertEquals("request transaction is unavailable", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
    assertEquals(List.of("acquire", "auto:false", "handle", "rollback", "close"), fixture.events);
  }

  @Test
  void tx329006NormalSuccessCommitsAndClosesBeforeReturningLiteralBytes() {
    var fixture = new Fixture();
    assertArrayEquals(new byte[] {4, 2}, fixture.process(null));
    assertEquals(List.of("acquire", "auto:false", "handle", "commit", "close"), fixture.events);
  }

  @Test
  void tx329007SqlNextCauseFatalCannotBecomeTheFixedCatalog() {
    var fixture = new Fixture();
    var fatal = new AssertionError("PUBLIC nested");
    var root = new SQLException("PUBLIC first");
    root.setNextException(new SQLException("PUBLIC next", fatal));
    assertSame(fatal, assertThrows(AssertionError.class, () -> fixture.process(root)));
    assertEquals(List.of("acquire", "auto:false", "handle", "rollback", "close"), fixture.events);
  }

  @Test
  void tx329008PostCommitCloseFailureIsNotAReplyOrAnInventedRollback() {
    var fixture = new Fixture();
    fixture.closeFailure = new SQLException("PUBLIC close");
    var actual = assertThrows(TemporaryInfrastructureException.class, () -> fixture.process(null));
    assertEquals("request transaction is unavailable", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
    assertEquals(List.of("acquire", "auto:false", "handle", "commit", "close"), fixture.events);
  }

  private static final class Fixture {
    final List<String> events = new ArrayList<>();
    @Nullable Throwable commitFailure;
    @Nullable Throwable rollbackFailure;
    @Nullable Throwable closeFailure;

    byte[] process(@Nullable Throwable handlerFailure) {
      var request = ApiSyncRequestDispatcherTest.request("LGNREQ01");
      Connection connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) -> {
                    switch (method.getName()) {
                      case "setAutoCommit" -> events.add("auto:" + args[0]);
                      case "commit" -> {
                        events.add("commit");
                        throwIfPresent(commitFailure);
                      }
                      case "rollback" -> {
                        events.add("rollback");
                        throwIfPresent(rollbackFailure);
                      }
                      case "close" -> {
                        events.add("close");
                        throwIfPresent(closeFailure);
                      }
                      default ->
                          throw new UnsupportedOperationException(
                              "unexpected fixture connection call");
                    }
                    return null;
                  });
      DataSource dataSource =
          (DataSource)
              Proxy.newProxyInstance(
                  DataSource.class.getClassLoader(),
                  new Class<?>[] {DataSource.class},
                  (proxy, method, args) -> {
                    if (!method.getName().equals("getConnection")) {
                      throw new UnsupportedOperationException("unexpected fixture source call");
                    }
                    events.add("acquire");
                    return connection;
                  });
      return new JdbcSyncRequestProcessor(
              dataSource,
              (actualConnection, actualRequest, instant) -> {
                events.add("handle");
                assertSame(connection, actualConnection);
                assertSame(request, actualRequest);
                assertEquals(NOW, instant);
                if (handlerFailure instanceof SQLException sql) throw sql;
                if (handlerFailure instanceof RuntimeException runtime) throw runtime;
                if (handlerFailure instanceof Error fatal) throw fatal;
                assertNull(handlerFailure);
                return new byte[] {4, 2};
              },
              Clock.fixed(NOW, ZoneOffset.UTC))
          .process(request);
    }

    private static void throwIfPresent(@Nullable Throwable failure) throws Throwable {
      if (failure != null) throw failure;
    }
  }
}
