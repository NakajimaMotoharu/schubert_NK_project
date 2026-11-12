package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** OPS-RVR-FATAL001..005; BUG2709/SS314332352: memory JDBC metadata, no DB or access grant. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class PendingRevocationFatalPortTest {
  @Test
  void fatal001MetadataCauseErrorRetainsIdentityAndClosesOwnedOnly() {
    var fatal = new AssertionError("PUBLIC cause fixture");
    var f = new Jdbc(new IllegalArgumentException("PUBLIC metadata", fatal));
    assertSame(fatal, assertThrows(AssertionError.class, f::claim));
    f.assertClosed();
  }

  @Test
  void fatal002DateTimeSuppressedSqlNextRetainsIdentityAndGraph() {
    var fatal = new AssertionError("PUBLIC SQL next fixture");
    var next = new SQLException("PUBLIC next", fatal);
    var sql = new SQLException("PUBLIC SQL");
    sql.setNextException(next);
    var metadata = new DateTimeException("PUBLIC metadata");
    metadata.addSuppressed(sql);
    var f = new Jdbc(metadata);
    assertSame(fatal, assertThrows(AssertionError.class, f::claim));
    assertSame(sql, metadata.getSuppressed()[0]);
    assertEquals(1, metadata.getSuppressed().length);
    assertSame(next, sql.getNextException());
    assertSame(fatal, next.getCause());
    f.assertClosed();
  }

  @Test
  void fatal003NonfatalCyclesKeepClosedDataStateAndBorrowedOwner() {
    var metadata = new IllegalArgumentException("PUBLIC cycle");
    var alias = new IllegalStateException("PUBLIC alias", metadata);
    metadata.initCause(alias);
    alias.addSuppressed(metadata);
    var f = new Jdbc(metadata);
    var failure = assertThrows(SQLDataException.class, f::claim);
    assertEquals("stored revocation metadata is invalid", failure.getMessage());
    assertEquals("22000", failure.getSQLState());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertSame(alias, metadata.getCause());
    assertSame(metadata, alias.getCause());
    f.assertClosed();
  }

  @Test
  void fatal004DirectErrorIsNotNormalizedAndBothResourcesClose() {
    var fatal = new AssertionError("PUBLIC direct fixture");
    var f = new Jdbc(fatal);
    assertSame(fatal, assertThrows(AssertionError.class, f::claim));
    f.assertClosed();
  }

  @Test
  void fatal005PrimaryFatalSurvivesTwoCloseFailuresInReverseResourceOrder() {
    var fatal = new AssertionError("PUBLIC primary fixture");
    var f = new Jdbc(new IllegalArgumentException("PUBLIC metadata", fatal));
    var resultClose = new SQLException("PUBLIC result close");
    var statementClose = new SQLException("PUBLIC statement close");
    f.resultClose = resultClose;
    f.statementClose = statementClose;
    assertSame(fatal, assertThrows(AssertionError.class, f::claim));
    assertArrayEquals(new Throwable[] {resultClose, statementClose}, fatal.getSuppressed());
    f.assertClosed();
  }

  private static final class Jdbc {
    private final Throwable metadataFailure;
    private final List<String> events = new ArrayList<>();
    private @Nullable SQLException resultClose;
    private @Nullable SQLException statementClose;

    private Jdbc(Throwable metadataFailure) {
      this.metadataFailure = metadataFailure;
    }

    private void claim() throws SQLException {
      new PendingRevocationRepository()
          .claim(connection(), new UUID(0, 1), Instant.EPOCH, Instant.ofEpochSecond(10), 1);
    }

    private void assertClosed() {
      assertEquals(
          List.of("prepare", "execute", "next", "metadata", "rs-close", "ps-close"), events);
    }

    private Connection connection() {
      return (Connection)
          Proxy.newProxyInstance(
              Connection.class.getClassLoader(),
              new Class<?>[] {Connection.class},
              (proxy, method, args) -> {
                if (method.getName().equals("getAutoCommit")) return false;
                if (method.getName().equals("prepareStatement")) {
                  events.add("prepare");
                  return statement();
                }
                throw new AssertionError("borrowed connection operation forbidden");
              });
    }

    private PreparedStatement statement() {
      return (PreparedStatement)
          Proxy.newProxyInstance(
              PreparedStatement.class.getClassLoader(),
              new Class<?>[] {PreparedStatement.class},
              (proxy, method, args) -> {
                String name = method.getName();
                if (name.startsWith("set")) return null;
                if (name.equals("executeQuery")) {
                  events.add("execute");
                  return result();
                }
                if (name.equals("close")) {
                  events.add("ps-close");
                  if (statementClose != null) throw statementClose;
                  return null;
                }
                throw new AssertionError("unexpected statement operation");
              });
    }

    private ResultSet result() {
      return (ResultSet)
          Proxy.newProxyInstance(
              ResultSet.class.getClassLoader(),
              new Class<?>[] {ResultSet.class},
              (proxy, method, args) -> {
                if (method.getName().equals("next")) {
                  events.add("next");
                  return true;
                }
                if (method.getName().equals("getObject")) {
                  assertEquals("expires_at", args[0]);
                  assertSame(OffsetDateTime.class, args[1]);
                  events.add("metadata");
                  throw metadataFailure;
                }
                if (method.getName().equals("close")) {
                  events.add("rs-close");
                  if (resultClose != null) throw resultClose;
                  return null;
                }
                throw new AssertionError("unexpected result operation");
              });
    }
  }
}
