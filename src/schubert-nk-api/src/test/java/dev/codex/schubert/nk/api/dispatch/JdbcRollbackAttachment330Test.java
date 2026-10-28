package dev.codex.schubert.nk.api.dispatch;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-MSG-002; SS312/324/354; SSC329330/BUG1592; PT-TX-ATTACH330001..003; no I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class JdbcRollbackAttachment330Test {
  private static final String FIXTURE_ACQUIRE_1585EBC6 = "acquire";
  private static final String FIXTURE_HANDLE_A8507210 = "handle";
  private static final String FIXTURE_ROLLBACK_3770B198 = "rollback";
  private static final String FIXTURE_CLOSE_97959247 = "close";

  @Test
  void attachment330001DisabledPrimaryCannotLoseRollbackFatalAndMustClose() {
    var events = new ArrayList<String>();
    var fatal = new AssertionError("PUBLIC rollback fatal");
    var primary = new DisabledRuntime(null);
    var processor =
        processor(events, primary, new IllegalStateException("PUBLIC rollback", fatal), null);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> processor.process(ApiSyncRequestDispatcherTest.request("LGNREQ01"))));
    assertEquals(0, primary.getSuppressed().length);
    assertEquals(
        List.of(
            FIXTURE_ACQUIRE_1585EBC6,
            "auto:false",
            FIXTURE_HANDLE_A8507210,
            FIXTURE_ROLLBACK_3770B198,
            FIXTURE_CLOSE_97959247),
        events);
  }

  @Test
  void attachment330002PrimaryCauseFatalKeepsPrecedenceAfterRollbackAndClose() {
    var events = new ArrayList<String>();
    var fatal = new AssertionError("PUBLIC primary cause");
    var primary = new DisabledRuntime(fatal);
    var processor = processor(events, primary, new AssertionError("PUBLIC rollback"), null);
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () -> processor.process(ApiSyncRequestDispatcherTest.request("LGNREQ01"))));
    assertEquals(0, primary.getSuppressed().length);
    assertEquals(
        List.of(
            FIXTURE_ACQUIRE_1585EBC6,
            "auto:false",
            FIXTURE_HANDLE_A8507210,
            FIXTURE_ROLLBACK_3770B198,
            FIXTURE_CLOSE_97959247),
        events);
  }

  @Test
  void attachment330003DisabledRootErrorAndSameCloseCannotSkipOwnedRelease() {
    var events = new ArrayList<String>();
    var fatal = new DisabledError();
    var processor =
        processor(
            events,
            fatal,
            new IllegalStateException("PUBLIC rollback", new AssertionError("PUBLIC secondary")),
            fatal);
    assertSame(
        fatal,
        assertThrows(
            DisabledError.class,
            () -> processor.process(ApiSyncRequestDispatcherTest.request("LGNREQ01"))));
    assertEquals(0, fatal.getSuppressed().length);
    assertEquals(
        List.of(
            FIXTURE_ACQUIRE_1585EBC6,
            "auto:false",
            FIXTURE_HANDLE_A8507210,
            FIXTURE_ROLLBACK_3770B198,
            FIXTURE_CLOSE_97959247),
        events);
  }

  private static JdbcSyncRequestProcessor processor(
      List<String> events,
      Throwable primary,
      Throwable rollbackFailure,
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
                      throw rollbackFailure;
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
                    throw new UnsupportedOperationException("unexpected source fixture call");
                  events.add(FIXTURE_ACQUIRE_1585EBC6);
                  return connection;
                });
    return new JdbcSyncRequestProcessor(
        source,
        (c, request, at) -> {
          assertSame(connection, c);
          assertEquals(Instant.EPOCH, at);
          events.add(FIXTURE_HANDLE_A8507210);
          if (primary instanceof RuntimeException runtime) throw runtime;
          if (primary instanceof Error fatal) throw fatal;
          throw new AssertionError("unsupported fixture primary");
        },
        Clock.fixed(Instant.EPOCH, ZoneOffset.UTC));
  }

  private static final class DisabledRuntime extends RuntimeException {
    private static final long serialVersionUID = 1L;

    DisabledRuntime(@Nullable Throwable cause) {
      super("PUBLIC", cause, false, false);
    }
  }

  private static final class DisabledError extends Error {
    private static final long serialVersionUID = 1L;

    DisabledError() {
      super("PUBLIC", null, false, false);
    }
  }
}
