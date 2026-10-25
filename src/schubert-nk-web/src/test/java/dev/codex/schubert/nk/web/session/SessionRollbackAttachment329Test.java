package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-WEB-001; SS312314331332354/SSC329330; BUG1592; PT-WEB-SESSION-ATTACH329001..003. No I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class SessionRollbackAttachment329Test {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-22T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void session329001DisabledPrimaryCannotLoseRollbackFatalBeforeOwnedClose() {
    for (int mode = 0; mode < 4; mode++) {
      var fatal = new AssertionError("PUBLIC fatal");
      var fixture = new Fixture(new NoSuppression(null), mode == 3 ? fatal : graph(fatal, mode));
      assertSame(fatal, assertThrows(AssertionError.class, fixture::create));
      fixture.verifyOwned(false);
    }
  }

  @Test
  void session329002PrimaryAndIdenticalErrorPriorityRemainFixed() {
    var first = new AssertionError("PUBLIC primary graph");
    var second = new AssertionError("PUBLIC secondary graph");
    var fixture = new Fixture(new NoSuppression(graph(first, 2)), graph(second, 2));
    assertSame(first, assertThrows(AssertionError.class, fixture::create));
    fixture.verifyOwned(false);
    for (boolean same : new boolean[] {false, true}) {
      var primary = new AssertionError("PUBLIC primary");
      var direct = new Fixture(primary, same ? primary : new AssertionError("PUBLIC secondary"));
      assertSame(primary, assertThrows(AssertionError.class, direct::create));
      direct.verifyOwned(false);
      if (same) assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void session329003NonFatalCycleSameThrowableAndMissingConnectionKeepFixedCatalog() {
    var primary = new NoSuppression(null);
    for (Throwable secondary : new Throwable[] {graph(null, 3), primary}) {
      var fixture = new Fixture(primary, secondary);
      fixed(assertThrows(SessionStoreException.class, fixture::create));
      fixture.verifyOwned(false);
    }
    var missing = new Fixture(primary, null);
    missing.missingConnection = true;
    fixed(assertThrows(SessionStoreException.class, missing::create));
    missing.verifyOwned(true);
  }

  private static void fixed(SessionStoreException actual) {
    assertEquals("session storage is unavailable", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
  }

  private static SQLException graph(@Nullable AssertionError fatal, int mode) {
    var sql = new SQLException("PUBLIC SQL");
    var next = new SQLException("PUBLIC next");
    sql.setNextException(next);
    if (fatal == null) next.setNextException(sql);
    else if (mode == 0) sql.initCause(fatal);
    else if (mode == 1) sql.addSuppressed(fatal);
    else next.initCause(fatal);
    return sql;
  }

  private static final class NoSuppression extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppression(@Nullable Throwable cause) {
      super("PUBLIC primary", cause, false, false);
    }
  }

  private static final class Fixture {
    final Throwable primary;
    final @Nullable Throwable secondary;
    boolean missingConnection;
    int opens;
    int rollbacks;
    int closes;
    int afterSetup;
    int identifiers;

    Fixture(Throwable primary, @Nullable Throwable secondary) {
      this.primary = primary;
      this.secondary = secondary;
    }

    void create() {
      try (var codec = new SessionPayloadCodec("v1", new byte[32], null, null)) {
        var source =
            (DataSource)
                Proxy.newProxyInstance(
                    DataSource.class.getClassLoader(),
                    new Class<?>[] {DataSource.class},
                    (object, method, args) -> {
                      assertEquals("getConnection", method.getName());
                      opens++;
                      return missingConnection ? null : connection();
                    });
        new EncryptedWebSessionRepository(
                source,
                codec,
                CLOCK,
                new SecureRandom(),
                () -> {
                  identifiers++;
                  throw new AssertionError("must not issue a session identity");
                })
            .create();
      }
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (object, method, args) ->
                  switch (method.getName()) {
                    case "setAutoCommit" -> throw primary;
                    case "rollback" -> {
                      rollbacks++;
                      if (secondary != null) throw secondary;
                      yield null;
                    }
                    case "close" -> {
                      closes++;
                      yield null;
                    }
                    default -> {
                      afterSetup++;
                      throw new AssertionError(
                          "Unexpected after setup operation: " + method.getName());
                    }
                  });
    }

    void verifyOwned(boolean missing) {
      assertEquals(1, opens);
      assertEquals(missing ? 0 : 1, rollbacks);
      assertEquals(missing ? 0 : 1, closes);
      assertEquals(0, afterSetup);
      assertEquals(0, identifiers);
    }
  }
}
