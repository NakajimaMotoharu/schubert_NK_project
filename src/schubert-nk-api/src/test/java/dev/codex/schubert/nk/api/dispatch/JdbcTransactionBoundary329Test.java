package dev.codex.schubert.nk.api.dispatch;

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

/** NK-MSG-002; SS312/324/354; SSC329; PT-TX-BOUNDARY329001..002; no I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class JdbcTransactionBoundary329Test {
  private static final String FIXTURE_ROLLBACK_3770B198 = "rollback";
  private static final String FIXTURE_CLOSE_97959247 = "close";

  @Test
  void boundary329001ProtocolCatalogDependsOnConfirmedCleanupOnly() {
    for (boolean closeFails : List.of(false, true)) {
      var events = new ArrayList<String>();
      var failure = new PermanentProtocolException("PUBLIC protocol");
      var processor =
          processor(events, failure, null, closeFails ? new SQLException("PUBLIC") : null);
      var request = ApiSyncRequestDispatcherTest.request("LGNREQ01");
      if (closeFails) {
        var actual =
            assertThrows(TemporaryInfrastructureException.class, () -> processor.process(request));
        assertEquals("request transaction is unavailable", actual.getMessage());
        assertNull(actual.getCause());
        assertEquals(0, actual.getSuppressed().length);
      } else {
        var actual =
            assertThrows(PermanentProtocolException.class, () -> processor.process(request));
        assertEquals("request transaction rejected invalid protocol", actual.getMessage());
        assertNull(actual.getCause());
        assertEquals(0, actual.getSuppressed().length);
      }
      assertEquals(
          List.of(
              "acquire", "auto:false", "handle", FIXTURE_ROLLBACK_3770B198, FIXTURE_CLOSE_97959247),
          events);
    }
  }

  @Test
  void boundary329002RollbackSameFatalDoesNotSelfSuppressOrSkipClose() {
    var events = new ArrayList<String>();
    var fatal = new AssertionError("PUBLIC fatal");
    var processor = processor(events, fatal, fatal, null);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> processor.process(ApiSyncRequestDispatcherTest.request("LGNREQ01"))));
    assertEquals(0, fatal.getSuppressed().length);
    assertEquals(
        List.of(
            "acquire", "auto:false", "handle", FIXTURE_ROLLBACK_3770B198, FIXTURE_CLOSE_97959247),
        events);
  }

  private static JdbcSyncRequestProcessor processor(
      List<String> events,
      Throwable primary,
      @Nullable Throwable rollbackFailure,
      @Nullable Throwable closeFailure) {
    Connection connection =
        (Connection)
            Proxy.newProxyInstance(
                Connection.class.getClassLoader(),
                new Class<?>[] {Connection.class},
                (proxy, method, args) -> {
                  switch (method.getName()) {
                    case "setAutoCommit" -> events.add("auto:" + args[0]);
                    case FIXTURE_ROLLBACK_3770B198 -> {
                      events.add(FIXTURE_ROLLBACK_3770B198);
                      if (rollbackFailure != null) throw rollbackFailure;
                    }
                    case FIXTURE_CLOSE_97959247 -> {
                      events.add(FIXTURE_CLOSE_97959247);
                      if (closeFailure != null) throw closeFailure;
                    }
                    default ->
                        throw new UnsupportedOperationException(
                            "unexpected connection fixture call");
                  }
                  return null;
                });
    DataSource source =
        (DataSource)
            Proxy.newProxyInstance(
                DataSource.class.getClassLoader(),
                new Class<?>[] {DataSource.class},
                (proxy, method, args) -> {
                  if (!method.getName().equals("getConnection"))
                    throw new UnsupportedOperationException("unexpected fixture call");
                  events.add("acquire");
                  return connection;
                });
    return new JdbcSyncRequestProcessor(
        source,
        (c, request, at) -> {
          assertSame(connection, c);
          assertEquals(Instant.EPOCH, at);
          events.add("handle");
          if (primary instanceof RuntimeException runtime) throw runtime;
          if (primary instanceof Error fatal) throw fatal;
          throw new AssertionError("unsupported fixture primary");
        },
        Clock.fixed(Instant.EPOCH, ZoneOffset.UTC));
  }
}
