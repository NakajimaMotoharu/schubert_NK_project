package dev.codex.schubert.nk.api.database;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-JDBC-CLEANUP001..005; DAT-009/AUT-004; SS332/352/SSC424; no real JDBC resource or driver. */
@Timeout(value = 5, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class JdbcResourceCleanupTest {
  @Test
  void cleanup001NullActionFailsAtTheExplicitCallBoundary() {
    assertThrows(NullPointerException.class, () -> JdbcResourceCleanup.close(null, null));
  }

  @Test
  void cleanup002SuccessfulCloseRunsOnceAndLeavesThePrimaryGraphUnchanged() throws SQLException {
    for (Throwable primary : Arrays.asList(null, new SQLException("PUBLIC primary"))) {
      var calls = new AtomicInteger();
      JdbcResourceCleanup.close(primary, () -> calls.incrementAndGet());
      assertEquals(1, calls.get());
      if (primary != null) assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void cleanup003FailedCloseWithoutPrimaryPropagatesTheSameSqlRuntimeOrError() {
    for (Throwable failure : failures()) {
      var calls = new AtomicInteger();
      Throwable observed =
          assertThrows(
              failure.getClass(),
              () ->
                  JdbcResourceCleanup.close(
                      null,
                      () -> {
                        calls.incrementAndGet();
                        throwFailure(failure);
                      }));
      assertSame(failure, observed);
      assertEquals(1, calls.get());
    }
  }

  @Test
  void cleanup004FailedCloseRetainsTheExactPrimaryAndSuppressedIdentity() throws SQLException {
    for (Throwable secondary : failures()) {
      var primary = new SQLException("PUBLIC original");
      var calls = new AtomicInteger();
      JdbcResourceCleanup.close(
          primary,
          () -> {
            calls.incrementAndGet();
            throwFailure(secondary);
          });
      assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
      assertEquals(1, calls.get());
    }
  }

  @Test
  void cleanup005AliasedFailurePreservesTheJdkSelfSuppressionCause() {
    var failure = new SQLException("PUBLIC alias");
    var calls = new AtomicInteger();
    var observed =
        assertThrows(
            IllegalArgumentException.class,
            () ->
                JdbcResourceCleanup.close(
                    failure,
                    () -> {
                      calls.incrementAndGet();
                      throw failure;
                    }));
    assertSame(failure, observed.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(1, calls.get());
  }

  private static List<Throwable> failures() {
    return List.of(
        new SQLException("PUBLIC SQL"),
        new IllegalStateException("PUBLIC runtime"),
        new AssertionError("PUBLIC fatal"));
  }

  private static void throwFailure(Throwable failure) throws SQLException {
    if (failure instanceof SQLException sql) throw sql;
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }
}
