package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariDataSource;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import java.sql.Connection;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicInteger;

/** 1876: test-only typed bridge; never starts a provider pool or reads external configuration. */
public final class ApiFactoryObservationFixture {
  private final ConcurrentLinkedQueue<ApiReadOnlyObservationAttemptTest.Fixture> attempts =
      new ConcurrentLinkedQueue<>();
  private final DbPoolMetricObservationTest.Fixture beans =
      new DbPoolMetricObservationTest.Fixture();
  private final AtomicInteger borrowedCloses = new AtomicInteger();
  private final Instant created = Instant.now();
  private final FakePool pool = new FakePool();

  private ApiFactoryObservationFixture() {}

  public static ApiFactoryObservationFixture create() {
    assertNull(
        System.getProperty("hikaricp.configurationFile"),
        "external Hikari configuration is not authorized in this fixture");
    return new ApiFactoryObservationFixture();
  }

  public HikariDataSource pool() {
    return pool;
  }

  public Instant created() {
    return created;
  }

  private Row row(String status, long count, long age) {
    return new Row(
        Optional.of(status),
        count,
        false,
        Optional.of(created.minusSeconds(age).atOffset(ZoneOffset.UTC)));
  }

  private final class FakePool extends HikariDataSource {
    @Override
    public Connection getConnection() {
      var attempt =
          new ApiReadOnlyObservationAttemptTest.Fixture(
              row("ERROR", 7, 6), row("PENDING", 3, 2), row("SENT", 5, 4));
      attempts.add(attempt);
      attempt.calls.add("open");
      return attempt.connection();
    }

    @Override
    public HikariPoolMXBean getHikariPoolMXBean() {
      return beans.pool();
    }

    @Override
    public HikariConfigMXBean getHikariConfigMXBean() {
      return beans.config();
    }

    @Override
    public void close() {
      borrowedCloses.incrementAndGet();
      fail("observation owner must not close the borrowed pool");
    }

    void dispose() {
      assertFalse(isRunning(), "the overridden fake must not start a provider pool");
      super.close();
    }
  }

  /** Call only after the observation owner has joined its own worker. */
  public void assertReleased() {
    assertFalse(attempts.isEmpty());
    for (var attempt : attempts) {
      attempt.cleanup(1, 1);
      attempt.query.complete();
      assertTrue(attempt.unknown.isEmpty());
    }
    assertTrue(beans.calls.containsAll(java.util.List.of("active", "idle", "pending", "max")));
    assertEquals(0, borrowedCloses.get());
  }

  public void dispose() {
    pool.dispose();
  }
}
