package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.zaxxer.hikari.HikariDataSource;
import java.io.PrintWriter;
import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.SQLFeatureNotSupportedException;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.logging.Logger;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-OPS-001/NK-DAT-001; SS311/342/343; OPS-POOL-OWN-002; memory DataSource ownership only. */
final class WebPoolSourceOwnershipPortTest {
  private static final String POOL_NAME = "schubert-nk-web";
  private static final String FORBIDDEN = "unsupported memory datasource method";
  private static final long STOP_NANOS = TimeUnit.SECONDS.toNanos(10);

  @Test
  @Timeout(45)
  void poolOwn002FailFastPoolsCloseOwnResourcesAndLeaveCallerSourceOpen() throws Exception {
    for (String key : List.of("hikaricp.configurationFile", "slf4j.provider")) {
      assertTrue(System.getProperty(key) == null, "SDK override must be absent");
    }
    var factory = new WebJdbcPool();
    assertThrows(NullPointerException.class, () -> factory.open(null));
    var source = new SourcePort();
    try (source) {
      for (int cycle = 0; cycle < 2; cycle++) {
        int before = source.issued.get();
        HikariDataSource pool = factory.open(source);
        try (pool) {
          assertTrue(source.issued.get() > before, "pool construction must be fail-fast");
          assertSame(source, pool.getDataSource());
          assertEquals(POOL_NAME, pool.getPoolName());
          assertEquals(2, pool.getMaximumPoolSize());
          assertEquals(1, pool.getMinimumIdle());
          assertEquals(3_000L, pool.getConnectionTimeout());
          assertEquals(2_000L, pool.getValidationTimeout());
          assertEquals(1L, pool.getInitializationFailTimeout());
          assertTrue(pool.isAutoCommit());
          assertFalse(pool.isReadOnly());
          assertFalse(pool.isRegisterMbeans());
          try (var loan = pool.getConnection()) {
            assertFalse(loan.isClosed());
          }
        }
        assertTrue(pool.isClosed());
        awaitOwnedWorkers();
        assertEquals(
            source.issued.get(), source.closed.get(), "all issued memory connections closed");
        assertEquals(0, source.sourceCloses.get(), "borrowed DataSource remains caller-owned");
        assertFalse(Thread.currentThread().isInterrupted(), "cleanup must finish normally");
      }
    }
    assertEquals(1, source.sourceCloses.get(), "only the fixture owner closes its DataSource");
  }

  /**
   * Only the pinned SDK's fixed pool namespace in this isolated test JVM, never host/guest PIDs.
   */
  private static void awaitOwnedWorkers() throws InterruptedException {
    long deadline = System.nanoTime() + STOP_NANOS;
    while (true) {
      var workers =
          Thread.getAllStackTraces().keySet().stream()
              .filter(thread -> thread.getName().startsWith(POOL_NAME) && thread.isAlive())
              .toList();
      if (workers.isEmpty()) return;
      long remaining = deadline - System.nanoTime();
      assertTrue(remaining > 0, "owned pool workers did not terminate");
      for (Thread worker : workers) {
        remaining = deadline - System.nanoTime();
        assertTrue(remaining > 0, "owned pool worker deadline expired");
        TimeUnit.NANOSECONDS.timedJoin(worker, remaining);
      }
    }
  }

  /** No driver/SQL/network, no repair in close; atomic callback counts are the postcondition. */
  private static final class SourcePort implements DataSource, AutoCloseable {
    private final AtomicInteger issued = new AtomicInteger();
    private final AtomicInteger closed = new AtomicInteger();
    private final AtomicInteger sourceCloses = new AtomicInteger();
    private final AtomicInteger loginSeconds = new AtomicInteger(1);

    @Override
    public Connection getConnection() throws SQLException {
      if (sourceCloses.get() != 0) throw new SQLException(FORBIDDEN);
      var ended = new java.util.concurrent.atomic.AtomicBoolean();
      var connection =
          (Connection)
              Proxy.newProxyInstance(
                  Connection.class.getClassLoader(),
                  new Class<?>[] {Connection.class},
                  (proxy, method, args) ->
                      switch (method.getName()) {
                        case "isClosed" -> ended.get();
                        case "isValid" -> !ended.get();
                        case "isReadOnly" -> false;
                        case "getAutoCommit" -> true;
                        case "getNetworkTimeout" -> 0;
                        case "getTransactionIsolation" -> Connection.TRANSACTION_READ_COMMITTED;
                        case "setNetworkTimeout", "clearWarnings" -> null;
                        case "close" -> {
                          if (ended.compareAndSet(false, true)) closed.incrementAndGet();
                          yield null;
                        }
                        case "hashCode" -> System.identityHashCode(proxy);
                        case "equals" -> proxy == Objects.requireNonNull(args)[0];
                        case "toString" -> "public-memory-connection";
                        default -> throw new AssertionError("unsupported memory Connection method");
                      });
      issued.incrementAndGet();
      return connection;
    }

    @Override
    public Connection getConnection(String username, String password) throws SQLException {
      throw new SQLFeatureNotSupportedException(FORBIDDEN);
    }

    @Override
    public PrintWriter getLogWriter() {
      throw new AssertionError(FORBIDDEN);
    }

    @Override
    public void setLogWriter(PrintWriter writer) {
      throw new AssertionError(FORBIDDEN);
    }

    @Override
    public void setLoginTimeout(int seconds) {
      assertTrue(seconds >= 0, "invalid SDK timeout");
      loginSeconds.set(seconds);
    }

    @Override
    public int getLoginTimeout() {
      return loginSeconds.get();
    }

    @Override
    public Logger getParentLogger() {
      throw new AssertionError(FORBIDDEN);
    }

    @Override
    public <T> T unwrap(Class<T> type) throws SQLException {
      throw new SQLFeatureNotSupportedException(FORBIDDEN);
    }

    @Override
    public boolean isWrapperFor(Class<?> type) {
      return false;
    }

    @Override
    public void close() {
      sourceCloses.incrementAndGet();
    }
  }
}
