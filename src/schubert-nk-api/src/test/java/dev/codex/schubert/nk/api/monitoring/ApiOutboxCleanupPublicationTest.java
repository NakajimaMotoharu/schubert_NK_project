package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.monitoring.ApiReadOnlyObservationAttemptTest.Fixture;
import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import java.sql.SQLException;
import java.time.Duration;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** 1860/OUTBOXPUBLISH001..014: cleanup-confirmed result/cache/SDK, own doubles only. */
final class ApiOutboxCleanupPublicationTest {
  private static final String FIXTURE_CLOSE_97959247 = "close";

  private static ApiOutboxObservationSource source() {
    return new ApiOutboxObservationSource(new OutboxObservationRepository(), "DEBUG");
  }

  private static Fixture rows() {
    return new Fixture(Row.row("ERROR", 7, 6), Row.row("PENDING", 3, 2), Row.row("SENT", 5, 4));
  }

  private static void await(CountDownLatch value) {
    try {
      assertTrue(value.await(10, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  @Test
  void outboxPublish001() throws SQLException {
    var value = source();
    var before = value.observe(rows().attempt());
    assertThrows(
        NullPointerException.class, () -> value.observe((ApiReadOnlyObservationAttempt) null));
    assertSame(before, value.get());
  }

  @Test
  void outboxPublish002() throws SQLException {
    var value = new ApiOutboxObservationSource(new OutboxObservationRepository(), "STANDARD");
    var f = rows();
    assertTrue(value.observe(f.attempt()).isEmpty());
    assertTrue(value.get().isEmpty());
    assertTrue(f.calls.isEmpty());
  }

  @Test
  void outboxPublish003() throws SQLException {
    var value = source();
    var f = rows();
    var actual = value.observe(f.attempt());
    f.cleanup(1, 1);
    f.query.complete();
    assertSame(actual, value.get());
    assertEquals(FIXTURE_CLOSE_97959247, f.calls.getLast());
    var pool = new DbPoolMetricObservationTest.Fixture();
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", pool::pool, pool::config, value)) {
      context.initialize();
      assertEquals(
          Set.of(
              "nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0",
              "nk_outbox_rows{status=\"SENT\",store=\"API\"} 5.0",
              "nk_outbox_rows{status=\"ERROR\",store=\"API\"} 7.0",
              "nk_outbox_oldest_seconds{status=\"PENDING\",store=\"API\"} 2.0",
              "nk_outbox_oldest_seconds{status=\"SENT\",store=\"API\"} 4.0",
              "nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} 6.0"),
          Set.copyOf(
              context.render(true).lines().filter(line -> line.startsWith("nk_outbox_")).toList()));
      f.cleanup(1, 1);
    }
  }

  @Test
  void outboxPublish004() throws SQLException {
    var value = source();
    var f = new Fixture();
    var actual = value.observe(f.attempt()).orElseThrow();
    assertEquals(0, actual.counts().pending());
    assertEquals(0, actual.counts().sent());
    assertEquals(0, actual.counts().error());
    assertEquals(Duration.ZERO, actual.ages().pending());
    assertEquals(Duration.ZERO, actual.ages().sent());
    assertEquals(Duration.ZERO, actual.ages().error());
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish005() throws SQLException {
    var value = source();
    value.observe(rows().attempt());
    var f = rows();
    var primary = new SQLException("open");
    f.faults.put("open", primary);
    assertSame(primary, assertThrows(SQLException.class, () -> value.observe(f.attempt())));
    assertTrue(value.get().isEmpty());
    f.cleanup(0, 0);
  }

  @Test
  void outboxPublish006() throws SQLException {
    var value = source();
    value.observe(rows().attempt());
    var f = rows();
    var primary = new SQLException("query");
    f.faults.put("query", primary);
    assertSame(primary, assertThrows(SQLException.class, () -> value.observe(f.attempt())));
    assertTrue(value.get().isEmpty());
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish007() throws SQLException {
    var value = source();
    value.observe(rows().attempt());
    var f = rows();
    var primary = new SQLException("rollback");
    f.faults.put("rollback", primary);
    assertSame(primary, assertThrows(SQLException.class, () -> value.observe(f.attempt())));
    assertTrue(value.get().isEmpty());
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish008() throws SQLException {
    var value = source();
    value.observe(rows().attempt());
    var f = rows();
    var primary = new SQLException(FIXTURE_CLOSE_97959247);
    f.faults.put(FIXTURE_CLOSE_97959247, primary);
    var owner = new AtomicReference<ApiReadOnlyObservationAttempt>();
    var attempt =
        f.attempt(
            failure -> {
              assertSame(primary, failure);
              assertTrue(owner.get().hasUnconfirmedResource());
              assertTrue(value.get().isEmpty());
              f.unconfirmed(failure);
            });
    owner.set(attempt);
    assertSame(primary, assertThrows(SQLException.class, () -> value.observe(attempt)));
    assertTrue(value.get().isEmpty());
    assertEquals(List.of(primary), f.unknown);
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish009() {
    var value = source();
    var f = rows();
    var fatal = new AssertionError(FIXTURE_CLOSE_97959247);
    f.faults.put(FIXTURE_CLOSE_97959247, fatal);
    assertSame(fatal, assertThrows(AssertionError.class, () -> value.observe(f.attempt())));
    assertTrue(value.get().isEmpty());
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish010() {
    var value = source();
    var f = rows();
    var fatal = new AssertionError("diagnostic");
    f.faults.put(FIXTURE_CLOSE_97959247, new SQLException(FIXTURE_CLOSE_97959247));
    f.faults.put("diagnostic", fatal);
    assertSame(fatal, assertThrows(AssertionError.class, () -> value.observe(f.attempt())));
    assertTrue(value.get().isEmpty());
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish011() throws Exception {
    var value = source();
    value.observe(rows().attempt());
    var closing = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var f = rows();
    f.query.beforeStatementClose =
        () -> {
          closing.countDown();
          await(release);
        };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending = worker.submit(() -> value.observe(f.attempt()));
      try {
        await(closing);
        assertTrue(value.get().isEmpty());
        value.missing();
        value.missing();
      } finally {
        release.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS).isEmpty());
      assertTrue(value.get().isEmpty());
      f.cleanup(1, 1);
    }
  }

  @Test
  void outboxPublish012() throws SQLException {
    var value = source();
    var f = rows();
    var attempt = f.attempt();
    var original = value.observe(attempt).orElseThrow();
    assertThrows(IllegalStateException.class, () -> value.observe(attempt));
    assertTrue(value.get().isEmpty());
    assertEquals(3, original.counts().pending());
    f.cleanup(1, 1);
  }

  @Test
  void outboxPublish013() throws SQLException {
    var value = source();
    var first = value.observe(rows().attempt()).orElseThrow();
    var next = new Fixture(Row.row("PENDING", 11, 13));
    var actual = value.observe(next.attempt()).orElseThrow();
    assertEquals(11, actual.counts().pending());
    assertEquals(Duration.ofSeconds(13), actual.ages().pending());
    assertEquals(3, first.counts().pending());
    assertEquals(Duration.ofSeconds(2), first.ages().pending());
    next.cleanup(1, 1);
  }

  @Test
  void outboxPublish014() throws Exception {
    var value = source();
    var pool = new DbPoolMetricObservationTest.Fixture();
    var closing = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var f = rows();
    f.query.beforeStatementClose =
        () -> {
          closing.countDown();
          await(release);
        };
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", pool::pool, pool::config, value)) {
      context.initialize();
      try (var worker = Executors.newSingleThreadExecutor()) {
        var pending = worker.submit(() -> value.observe(f.attempt()));
        try {
          await(closing);
          assertTrue(
              context
                  .render(true)
                  .contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} NaN"));
        } finally {
          release.countDown();
        }
        assertTrue(pending.get(10, TimeUnit.SECONDS).isPresent());
        assertTrue(
            context.render(true).contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0"));
        f.cleanup(1, 1);
      }
    }
  }
}
