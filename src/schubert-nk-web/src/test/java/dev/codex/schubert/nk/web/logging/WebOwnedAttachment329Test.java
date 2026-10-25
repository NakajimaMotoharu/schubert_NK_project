package dev.codex.schubert.nk.web.logging;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.revocation.RevocationPayloadCodec;
import dev.codex.schubert.nk.web.revocation.RevocationRetryCoordinator;
import dev.codex.schubert.nk.web.revocation.RevocationRetryException;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.UUID;
import javax.sql.DataSource;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** SS312/324/332/354/SSC329330; BUG1592; PT-WEB-DISPATCH/REVOCATION-ATTACH329001..003. No I/O. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class WebOwnedAttachment329Test {
  private static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-10-22T00:00:00Z"), ZoneOffset.UTC);

  @Test
  void owned329001DispatcherRollbackGraphSurvivesDisabledSuppression() {
    for (boolean primaryHasFatal : new boolean[] {false, true}) {
      var first = new AssertionError("PUBLIC primary fatal");
      var second = new AssertionError("PUBLIC rollback fatal");
      var primary = new NoSuppression(primaryHasFatal ? graph(first) : null);
      var fixture = new Fixture(false, primary, graph(second), null);
      sameFatal(primaryHasFatal ? first : second, fixture);
      fixture.verifyOwned();
    }
  }

  @Test
  void owned329002DispatcherCloseGraphSurvivesAndNonFatalRawSqlRemainsSame() {
    var fatal = new AssertionError("PUBLIC close fatal");
    var fixture = new Fixture(false, new NoSuppression(null), null, graph(fatal));
    sameFatal(fatal, fixture);
    fixture.verifyOwned();
    var same = graph(null);
    var nonFatal = new Fixture(false, same, same, same);
    assertSame(same, assertThrows(SQLException.class, nonFatal::invoke));
    assertEquals(0, same.getSuppressed().length);
    nonFatal.verifyOwned();
  }

  @Test
  void owned329003DispatcherDirectErrorRollsBackAndKeepsLegacyClosePriority() {
    for (int mode = 0; mode < 4; mode++) {
      var primary = new AssertionError("PUBLIC primary");
      Throwable rollback =
          mode == 0 || mode == 3
              ? new SQLException("PUBLIC rollback")
              : mode == 1 ? new AssertionError("PUBLIC rollback fatal") : primary;
      var closing =
          mode == 2 ? primary : mode == 3 ? new AssertionError("PUBLIC close fatal") : null;
      var fixture = new Fixture(false, primary, rollback, closing);
      sameFatal(mode == 3 ? closing : primary, fixture);
      fixture.verifyOwned();
      if (mode == 2) assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void owned329004RevocationRollbackGraphCannotSkipRemainingClose() {
    for (boolean primaryHasFatal : new boolean[] {false, true}) {
      var first = new AssertionError("PUBLIC primary fatal");
      var second = new AssertionError("PUBLIC rollback fatal");
      var fixture =
          new Fixture(
              true, new NoSuppression(primaryHasFatal ? graph(first) : null), graph(second), null);
      sameFatal(primaryHasFatal ? first : second, fixture);
      fixture.verifyOwned();
    }
  }

  @Test
  void owned329005RevocationCloseGraphAndBothFatalGraphsKeepPrimary() {
    var closing = new AssertionError("PUBLIC close fatal");
    var fixture = new Fixture(true, new NoSuppression(null), null, graph(closing));
    sameFatal(closing, fixture);
    fixture.verifyOwned();
    var rollback = new AssertionError("PUBLIC rollback fatal");
    var both =
        new Fixture(
            true,
            new NoSuppression(null),
            graph(rollback),
            graph(new AssertionError("PUBLIC later close")));
    sameFatal(rollback, both);
    both.verifyOwned();
  }

  @Test
  void owned329006RevocationNonFatalAndDirectErrorPoliciesRemainFixed() {
    var cycle = graph(null);
    var fixture = new Fixture(true, new NoSuppression(null), cycle, cycle);
    var fixed = assertThrows(RevocationRetryException.class, fixture::invoke);
    assertEquals("retained revocation retry infrastructure unavailable", fixed.getMessage());
    assertNull(fixed.getCause());
    assertEquals(0, fixed.getSuppressed().length);
    fixture.verifyOwned();
    var primary = new AssertionError("PUBLIC primary fatal");
    var direct =
        new Fixture(
            true,
            primary,
            new AssertionError("PUBLIC rollback fatal"),
            new AssertionError("PUBLIC close fatal"));
    sameFatal(primary, direct);
    direct.verifyOwned();
  }

  private static void sameFatal(Throwable expected, Fixture fixture) {
    Throwable actual = assertThrows(Throwable.class, fixture::invoke);
    assertEquals(1, fixture.opens, "owned fixture source prerequisite");
    assertEquals(
        fixture.revocation ? 0 : 1, fixture.prepares, "owned fixture prepare prerequisite");
    assertEquals(
        fixture.revocation ? 0 : 1,
        fixture.autoCommitChecks,
        "owned fixture transaction prerequisite");
    assertEquals(0, fixture.sends, "owned fixture never sends");
    // Exact object identity implies the expected Error type, not just any thrown failure.
    assertTrue(actual == expected);
  }

  private static SQLException graph(@Nullable AssertionError fatal) {
    var primary = new SQLException("PUBLIC SQL");
    var next = new SQLException("PUBLIC next");
    primary.setNextException(next);
    if (fatal == null) next.setNextException(primary);
    else next.initCause(fatal);
    return primary;
  }

  private static final class NoSuppression extends RuntimeException {
    private static final long serialVersionUID = 1L;

    NoSuppression(@Nullable Throwable cause) {
      super("PUBLIC primary", cause, false, false);
    }
  }

  private static final class Fixture {
    final boolean revocation;
    final Throwable primary;
    final @Nullable Throwable rollback;
    final @Nullable Throwable closing;
    int opens;
    int prepares;
    int autoCommitChecks;
    int rollbacks;
    int closes;
    int commits;
    int sends;

    Fixture(
        boolean revocation,
        Throwable primary,
        @Nullable Throwable rollback,
        @Nullable Throwable closing) {
      this.revocation = revocation;
      this.primary = primary;
      this.rollback = rollback;
      this.closing = closing;
    }

    void invoke() throws SQLException {
      if (revocation) {
        try (var codec = new RevocationPayloadCodec("v1", new byte[32], null, null)) {
          var replies = new JmsRequestReplyClient(); // No thread, broker or external connection.
          var wire =
              new LogoutWireClient(
                  replies,
                  (id, body) -> {
                    sends++;
                    throw new AssertionError("must not send");
                  },
                  CLOCK,
                  () -> new UUID(0, 2),
                  Duration.ofMillis(50));
          try {
            new RevocationRetryCoordinator(source(), codec, wire, CLOCK).dispatchOne();
          } finally {
            assertEquals(0, replies.pendingCount());
          }
        }
      } else {
        try (var codec = new WebLogPayloadCodec("v1", new byte[32], null, null)) {
          var sender =
              new WebLogMessageSender(
                  codec,
                  () -> {
                    sends++;
                    throw new AssertionError("must not send");
                  });
          new WebLogDispatcher(source(), new WebLogOutboxRepository(() -> 0), sender, CLOCK)
              .dispatch("worker", 1);
        }
      }
    }

    DataSource source() {
      return (DataSource)
          Proxy.newProxyInstance(
              DataSource.class.getClassLoader(),
              new Class<?>[] {DataSource.class},
              (object, method, args) -> {
                assertEquals("getConnection", method.getName());
                opens++;
                return connection();
              });
    }

    Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (object, method, args) ->
                  switch (method.getName()) {
                    case "setAutoCommit" -> {
                      if (revocation) throw primary;
                      yield null;
                    }
                    case "getAutoCommit" -> {
                      autoCommitChecks++;
                      yield false;
                    }
                    case "prepareStatement" -> {
                      prepares++;
                      throw primary;
                    }
                    case "rollback" -> {
                      rollbacks++;
                      if (rollback != null) throw rollback;
                      yield null;
                    }
                    case "close" -> {
                      closes++;
                      if (closing != null) throw closing;
                      yield null;
                    }
                    case "commit" -> {
                      commits++;
                      yield null;
                    }
                    default ->
                        throw new AssertionError(
                            "Unexpected connection operation: " + method.getName());
                  });
    }

    void verifyOwned() {
      assertEquals(1, opens);
      assertEquals(1, rollbacks);
      assertEquals(1, closes);
      assertEquals(revocation ? 0 : 1, prepares);
      assertEquals(revocation ? 0 : 1, autoCommitChecks);
      assertEquals(0, commits);
      assertEquals(0, sends);
    }
  }
}
