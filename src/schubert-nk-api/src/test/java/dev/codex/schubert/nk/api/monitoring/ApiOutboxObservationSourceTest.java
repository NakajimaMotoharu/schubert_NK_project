package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Fixture;
import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/**
 * 1854/OUTBOXSOURCE001..020: own typed JDBC doubles, no actual DB/driver/worker/source admission.
 */
final class ApiOutboxObservationSourceTest {
  private static ApiOutboxObservationSource source() {
    return new ApiOutboxObservationSource(new OutboxObservationRepository(), "DEBUG");
  }

  private static Fixture rows() {
    return new Fixture(Row.row("ERROR", 7, 6), Row.row("PENDING", 3, 2), Row.row("SENT", 5, 4));
  }

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(10, TimeUnit.SECONDS), "bounded own fixture coordination");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  @Test
  void outboxSource001() {
    assertThrows(NullPointerException.class, () -> new ApiOutboxObservationSource(null, "DEBUG"));
    assertThrows(
        NullPointerException.class,
        () -> new ApiOutboxObservationSource(new OutboxObservationRepository(), null));
  }

  @Test
  void outboxSource002() {
    for (String mode : List.of("", "debug", " DEBUG", "UNKNOWN"))
      assertThrows(
          IllegalArgumentException.class,
          () -> new ApiOutboxObservationSource(new OutboxObservationRepository(), mode));
  }

  @Test
  void outboxSource003() throws SQLException {
    var value = new ApiOutboxObservationSource(new OutboxObservationRepository(), "STANDARD");
    var f = rows();
    f.faults.put("autoCommit", new AssertionError("STANDARD must not touch JDBC"));
    assertTrue(value.observe(f.connection(), Instant.EPOCH).isEmpty());
    assertTrue(value.get().isEmpty());
    value.missing();
    assertTrue(value.get().isEmpty());
    assertEquals(0, f.prepared);
  }

  @Test
  void outboxSource004() {
    var value = source();
    assertTrue(value.get().isEmpty());
    value.missing();
    assertTrue(value.get().isEmpty());
  }

  @Test
  void outboxSource005() {
    var value = new ApiOutboxObservationSource(new OutboxObservationRepository(), "STANDARD");
    assertThrows(NullPointerException.class, () -> value.observe(null, Instant.EPOCH));
    assertThrows(NullPointerException.class, () -> value.observe(rows().connection(), null));
    assertTrue(value.get().isEmpty());
  }

  @Test
  void outboxSource006() throws SQLException {
    var value = source();
    var before = value.observe(rows().connection(), Instant.EPOCH);
    assertThrows(NullPointerException.class, () -> value.observe(null, Instant.EPOCH));
    assertSame(before, value.get());
  }

  @Test
  void outboxSource007() throws SQLException {
    var value = source();
    var before = value.observe(rows().connection(), Instant.EPOCH);
    var f = rows();
    assertThrows(NullPointerException.class, () -> value.observe(f.connection(), null));
    assertSame(before, value.get());
    assertEquals(0, f.prepared);
  }

  @Test
  void outboxSource008() throws SQLException {
    var value = source();
    var f = rows();
    var supplied = value.observe(f.connection(), Instant.EPOCH);
    assertSame(supplied, value.get());
    var actual = supplied.orElseThrow();
    assertEquals(3, actual.counts().pending());
    assertEquals(5, actual.counts().sent());
    assertEquals(7, actual.counts().error());
    assertEquals(Duration.ofSeconds(2), actual.ages().pending());
    assertEquals(Duration.ofSeconds(4), actual.ages().sent());
    assertEquals(Duration.ofSeconds(6), actual.ages().error());
    f.complete();
  }

  @Test
  void outboxSource009() throws SQLException {
    var value = source();
    var f = new Fixture();
    var actual = value.observe(f.connection(), Instant.EPOCH).orElseThrow();
    assertEquals(0, actual.counts().pending());
    assertEquals(0, actual.counts().sent());
    assertEquals(0, actual.counts().error());
    assertEquals(Duration.ZERO, actual.ages().pending());
    assertEquals(Duration.ZERO, actual.ages().sent());
    assertEquals(Duration.ZERO, actual.ages().error());
    f.complete();
  }

  @Test
  void outboxSource010() throws SQLException {
    var value = source();
    var first = value.observe(rows().connection(), Instant.EPOCH).orElseThrow();
    var f = new Fixture(Row.row("PENDING", 11, 13));
    var next = value.observe(f.connection(), Instant.EPOCH).orElseThrow();
    assertEquals(11, next.counts().pending());
    assertEquals(Duration.ofSeconds(13), next.ages().pending());
    assertEquals(3, first.counts().pending());
    assertEquals(Duration.ofSeconds(2), first.ages().pending());
    f.complete();
  }

  @Test
  void outboxSource011() throws SQLException {
    var value = source();
    value.observe(rows().connection(), Instant.EPOCH);
    var f = rows();
    var failure = new SQLException("fixture");
    f.faults.put("execute", failure);
    assertSame(
        failure,
        assertThrows(SQLException.class, () -> value.observe(f.connection(), Instant.EPOCH)));
    assertTrue(value.get().isEmpty());
    assertEquals(List.of("PS"), f.closes);
  }

  @Test
  void outboxSource012() throws SQLException {
    var value = source();
    value.observe(rows().connection(), Instant.EPOCH);
    var f = rows();
    var failure = new IllegalStateException("fixture");
    f.faults.put("prepare", failure);
    assertSame(
        failure,
        assertThrows(
            IllegalStateException.class, () -> value.observe(f.connection(), Instant.EPOCH)));
    assertTrue(value.get().isEmpty());
  }

  @Test
  void outboxSource013() throws SQLException {
    var value = source();
    value.observe(rows().connection(), Instant.EPOCH);
    var f = rows();
    var failure = new AssertionError("fixture");
    f.faults.put("next", failure);
    assertSame(
        failure,
        assertThrows(AssertionError.class, () -> value.observe(f.connection(), Instant.EPOCH)));
    assertTrue(value.get().isEmpty());
    f.complete();
  }

  @Test
  void outboxSource014() throws SQLException {
    var value = source();
    value.observe(rows().connection(), Instant.EPOCH);
    var f = rows();
    var primary = new SQLException("result close");
    var secondary = new SQLException("statement close");
    f.faults.put("RSclose", primary);
    f.faults.put("PSclose", secondary);
    assertSame(
        primary,
        assertThrows(SQLException.class, () -> value.observe(f.connection(), Instant.EPOCH)));
    assertArrayEquals(new Throwable[] {secondary}, primary.getSuppressed());
    assertTrue(value.get().isEmpty());
    f.complete();
  }

  @Test
  void outboxSource015() {
    var value = source();
    var f = rows();
    var failure = new AssertionError("statement close");
    f.faults.put("PSclose", failure);
    assertSame(
        failure,
        assertThrows(AssertionError.class, () -> value.observe(f.connection(), Instant.EPOCH)));
    assertTrue(value.get().isEmpty());
    f.complete();
  }

  @Test
  void outboxSource016() throws SQLException {
    var value = source();
    value.observe(rows().connection(), Instant.EPOCH);
    value.missing();
    value.missing();
    assertTrue(value.get().isEmpty());
    var f = rows();
    assertTrue(value.observe(f.connection(), Instant.EPOCH).isPresent());
    assertEquals(7, value.get().orElseThrow().counts().error());
    f.complete();
  }

  @Test
  void outboxSource017() throws Exception {
    var value = source();
    value.observe(rows().connection(), Instant.EPOCH);
    var closing = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var f = rows();
    f.beforeStatementClose =
        () -> {
          closing.countDown();
          await(release);
        };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending = worker.submit(() -> value.observe(f.connection(), Instant.EPOCH));
      try {
        await(closing);
        // Query and RS close have completed, but PS close/publication has not.
        assertTrue(value.get().isEmpty());
        value.missing();
        value.missing();
        assertTrue(value.get().isEmpty());
      } finally {
        release.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS).isEmpty());
      assertTrue(value.get().isEmpty());
      f.complete();
    }
  }

  @Test
  void outboxSource018() throws Exception {
    var value = source();
    var closing = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var started = new CountDownLatch(1);
    var first = rows();
    var second = new Fixture(Row.row("PENDING", 11, 13));
    first.beforeStatementClose =
        () -> {
          closing.countDown();
          await(release);
        };
    try (var workers = Executors.newFixedThreadPool(2)) {
      var a = workers.submit(() -> value.observe(first.connection(), Instant.EPOCH));
      try {
        await(closing);
        var b =
            workers.submit(
                () -> {
                  started.countDown();
                  return value.observe(second.connection(), Instant.EPOCH);
                });
        await(started);
        assertTrue(value.get().isEmpty());
        release.countDown();
        assertEquals(3, a.get(10, TimeUnit.SECONDS).orElseThrow().counts().pending());
        assertEquals(11, b.get(10, TimeUnit.SECONDS).orElseThrow().counts().pending());
        assertEquals(11, value.get().orElseThrow().counts().pending());
      } finally {
        release.countDown();
      }
      first.complete();
      second.complete();
    }
  }

  @Test
  void outboxSource019() throws SQLException {
    var value = source();
    var f = rows();
    value.observe(f.connection(), Instant.EPOCH);
    var pool = new DbPoolMetricObservationTest.Fixture();
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", pool::pool, pool::config, value)) {
      context.initialize();
      var actual =
          Set.copyOf(
              context
                  .render(true)
                  .lines()
                  .filter(line -> line.startsWith("nk_outbox_") && !line.startsWith("#"))
                  .toList());
      assertEquals(
          Set.of(
              "nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0",
              "nk_outbox_rows{status=\"SENT\",store=\"API\"} 5.0",
              "nk_outbox_rows{status=\"ERROR\",store=\"API\"} 7.0",
              "nk_outbox_oldest_seconds{status=\"PENDING\",store=\"API\"} 2.0",
              "nk_outbox_oldest_seconds{status=\"SENT\",store=\"API\"} 4.0",
              "nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} 6.0"),
          actual);
      context.render(false);
      f.complete(); // rendering did not issue SQL or close the connection again.
    }
  }

  @Test
  void outboxSource020() throws SQLException {
    var value = source();
    var pool = new DbPoolMetricObservationTest.Fixture();
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", pool::pool, pool::config, value)) {
      context.initialize();
      assertTrue(
          context.render(true).contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} NaN"));
      var f = new Fixture();
      value.observe(f.connection(), Instant.EPOCH);
      assertTrue(
          context.render(true).contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} 0.0"));
      value.missing();
      assertTrue(
          context.render(true).contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} NaN"));
      f.complete();
    }
  }
}
