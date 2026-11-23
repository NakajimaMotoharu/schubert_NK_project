package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.UUID;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/** PT-BAT-SSC461-CT001–004: terminal SQL diagnostic paths before any resource is acquired. */
final class CleanupTerminalSqlDiagnosticTest {
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  private static final Instant OBSERVED = Instant.parse("2026-09-13T02:00:03Z");

  @Test
  void ct001ReadSanitizesAnOrdinarySqlFailureBeforeResourceAcquisition() {
    assertFixed(repository -> repository.read(RUN, OBSERVED));
  }

  @Test
  void ct002ReadRejectedSanitizesAnOrdinarySqlFailureBeforeResourceAcquisition() {
    assertFixed(repository -> repository.readRejected(RUN, OBSERVED));
  }

  @Test
  void ct003ReadPreservesTheSameFatalFromSqlNext() {
    var failure = new SQLException("fixture root");
    var fatal = new AssertionError("fixture failure at SQL next");
    failure.setNextException(new SQLException("fixture next", fatal));
    var fixture = new Fixture(failure);

    assertSame(
        fatal, assertThrows(AssertionError.class, () -> fixture.repository.read(RUN, OBSERVED)));
    assertEquals(1, fixture.probes);
  }

  @Test
  void ct004ReadRejectedPreservesCausePriorityOverSqlNext() {
    var cause = new AssertionError("fixture original cause");
    var failure = new SQLException("fixture root", cause);
    failure.setNextException(new SQLException("fixture next", new AssertionError("fixture other")));
    var fixture = new Fixture(failure);

    assertSame(
        cause,
        assertThrows(AssertionError.class, () -> fixture.repository.readRejected(RUN, OBSERVED)));
    assertEquals(1, fixture.probes);
  }

  private static void assertFixed(Consumer<CleanupTerminalRepository> call) {
    var fixture = new Fixture(new SQLException("fixture-only source diagnostic"));
    var failure =
        assertThrows(BatchRepositoryException.class, () -> call.accept(fixture.repository));
    assertEquals("batch repository operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(1, fixture.probes);
  }

  private static final class Fixture {
    int probes;
    final CleanupTerminalRepository repository;

    Fixture(SQLException failure) {
      var connection =
          Connection.class.cast(
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (object, method, arguments) -> {
                    assertEquals("getAutoCommit", method.getName());
                    probes++;
                    throw failure;
                  }));
      repository = new CleanupTerminalRepository(connection, () -> 5_000_000_000L);
    }
  }
}
