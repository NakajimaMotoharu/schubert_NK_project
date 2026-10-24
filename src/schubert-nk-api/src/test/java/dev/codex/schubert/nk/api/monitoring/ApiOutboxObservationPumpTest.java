package dev.codex.schubert.nk.api.monitoring;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.api.monitoring.ApiReadOnlyObservationAttemptTest.Fixture;
import dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest.Row;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** 1862/OUTBOXPUMP001..032: injected nano time/resource-free factory and typed fake JDBC only. */
final class ApiOutboxObservationPumpTest {
  private static final long PERIOD = 15_000_000_000L;

  static final class Harness {
    final List<Fixture> fixtures = new ArrayList<>();
    long now;
    int clockReads;
    int factoryReads;
    Throwable clockFault;
    Throwable factoryFault;
    Consumer<Fixture> configure = fixture -> {};
    Supplier<ApiReadOnlyObservationAttempt> prepared =
        () -> {
          var f =
              new Fixture(Row.row("ERROR", 7, 6), Row.row("PENDING", 3, 2), Row.row("SENT", 5, 4));
          fixtures.add(f);
          configure.accept(f);
          return f.attempt();
        };
    final ApiOutboxObservationPump pump =
        ApiOutboxObservationPump.create(
            "DEBUG", this::time, this::attempt, new OutboxObservationRepository());

    private static void unchecked(Throwable value) {
      if (value instanceof RuntimeException runtime) throw runtime;
      if (value instanceof Error fatal) throw fatal;
      assertNull(value);
    }

    long time() {
      clockReads++;
      unchecked(clockFault);
      return now;
    }

    ApiReadOnlyObservationAttempt attempt() {
      factoryReads++;
      unchecked(factoryFault);
      return prepared.get();
    }
  }

  private static void await(CountDownLatch value) {
    try {
      assertTrue(value.await(10, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError(interrupted);
    }
  }

  private static void ordinaryFailure(String point, Throwable primary, boolean unknown) {
    var h = new Harness();
    h.configure = f -> f.faults.put(point, primary);
    assertSame(primary, assertThrows(primary.getClass(), h.pump::sampleIfDue));
    assertTrue(h.pump.get().isEmpty());
    assertEquals(!unknown, h.pump.isQuiescent());
    if (unknown) {
      h.now = PERIOD;
      assertDoesNotThrow(h.pump::sampleIfDue);
      assertEquals(1, h.factoryReads);
      assertEquals(1, h.clockReads);
      h.fixtures.getFirst().cleanup(1, 1);
    }
  }

  @Test
  void outboxPump001() {
    var h = new Harness();
    var repository = new OutboxObservationRepository();
    assertThrows(
        NullPointerException.class,
        () ->
            new ApiOutboxObservationPump(
                null, Duration.ofSeconds(15), h::time, h::attempt, repository));
    assertThrows(
        NullPointerException.class,
        () -> new ApiOutboxObservationPump("DEBUG", null, h::time, h::attempt, repository));
    assertThrows(
        NullPointerException.class,
        () ->
            new ApiOutboxObservationPump(
                "DEBUG", Duration.ofSeconds(15), null, h::attempt, repository));
    assertThrows(
        NullPointerException.class,
        () ->
            new ApiOutboxObservationPump(
                "DEBUG", Duration.ofSeconds(15), h::time, null, repository));
    assertThrows(
        NullPointerException.class,
        () ->
            new ApiOutboxObservationPump(
                "DEBUG", Duration.ofSeconds(15), h::time, h::attempt, null));
    assertEquals(0, h.clockReads);
    assertEquals(0, h.factoryReads);
  }

  @Test
  void outboxPump002() {
    var h = new Harness();
    for (String mode : List.of("", "debug", " DEBUG", "UNKNOWN"))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              ApiOutboxObservationPump.create(
                  mode, h::time, h::attempt, new OutboxObservationRepository()));
    assertEquals(0, h.clockReads);
    assertEquals(0, h.factoryReads);
  }

  @Test
  void outboxPump003() {
    var h = new Harness();
    for (Duration period : List.of(Duration.ZERO, Duration.ofNanos(-1)))
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new ApiOutboxObservationPump(
                  "DEBUG", period, h::time, h::attempt, new OutboxObservationRepository()));
    assertThrows(
        ArithmeticException.class,
        () ->
            new ApiOutboxObservationPump(
                "DEBUG",
                Duration.ofSeconds(Long.MAX_VALUE),
                h::time,
                h::attempt,
                new OutboxObservationRepository()));
  }

  @Test
  void outboxPump004() {
    var h = new Harness();
    assertEquals(0, h.clockReads);
    assertEquals(0, h.factoryReads);
    assertTrue(h.fixtures.isEmpty());
  }

  @Test
  void outboxPump005() throws SQLException {
    var h = new Harness();
    var pump =
        ApiOutboxObservationPump.create(
            "STANDARD",
            () -> {
              throw new AssertionError("STANDARD time");
            },
            () -> {
              throw new AssertionError("STANDARD factory");
            },
            new OutboxObservationRepository());
    pump.sampleIfDue();
    pump.sampleIfDue();
    assertTrue(pump.get().isEmpty());
    assertTrue(pump.isQuiescent());
    assertTrue(h.fixtures.isEmpty());
  }

  @Test
  void outboxPump006() {
    var h = new Harness();
    assertTrue(h.pump.isQuiescent());
    assertTrue(h.pump.get().isEmpty());
  }

  @Test
  void outboxPump007() throws SQLException {
    var h = new Harness();
    h.pump.sampleIfDue();
    var actual = h.pump.get().orElseThrow();
    assertEquals(3, actual.counts().pending());
    assertEquals(5, actual.counts().sent());
    assertEquals(7, actual.counts().error());
    assertEquals(Duration.ofSeconds(2), actual.ages().pending());
    assertEquals(Duration.ofSeconds(4), actual.ages().sent());
    assertEquals(Duration.ofSeconds(6), actual.ages().error());
    assertTrue(h.pump.isQuiescent());
    var pool = new DbPoolMetricObservationTest.Fixture();
    try (var context =
        ApiServiceMetricBinding.prepareContext("DEBUG", pool::pool, pool::config, h.pump)) {
      context.initialize();
      assertTrue(
          context.render(true).contains("nk_outbox_rows{status=\"PENDING\",store=\"API\"} 3.0"));
      assertTrue(
          context
              .render(true)
              .contains("nk_outbox_oldest_seconds{status=\"ERROR\",store=\"API\"} 6.0"));
    }
    assertEquals(1, h.factoryReads);
    assertEquals(1, h.clockReads);
    h.fixtures.getFirst().cleanup(1, 1);
  }

  @Test
  void outboxPump008() throws SQLException {
    var h = new Harness();
    h.pump.sampleIfDue();
    h.pump.sampleIfDue();
    h.now = PERIOD - 1;
    h.pump.sampleIfDue();
    assertEquals(1, h.factoryReads);
    assertEquals(3, h.clockReads);
    assertEquals(3, h.pump.get().orElseThrow().counts().pending());
  }

  @Test
  void outboxPump009() throws SQLException {
    var h = new Harness();
    h.pump.sampleIfDue();
    var first = h.pump.get().orElseThrow();
    h.now = PERIOD;
    h.prepared =
        () -> {
          var f = new Fixture(Row.row("PENDING", 11, 13));
          h.fixtures.add(f);
          return f.attempt();
        };
    h.pump.sampleIfDue();
    assertEquals(2, h.factoryReads);
    assertEquals(11, h.pump.get().orElseThrow().counts().pending());
    assertEquals(3, first.counts().pending());
  }

  @Test
  void outboxPump010() throws SQLException {
    var h = new Harness();
    var pump =
        new ApiOutboxObservationPump(
            "DEBUG", Duration.ofNanos(15), h::time, h::attempt, new OutboxObservationRepository());
    h.now = Long.MAX_VALUE - 5;
    pump.sampleIfDue();
    h.now = Long.MIN_VALUE + 8;
    pump.sampleIfDue();
    assertEquals(1, h.factoryReads);
    h.now = Long.MIN_VALUE + 9;
    pump.sampleIfDue();
    assertEquals(2, h.factoryReads);
  }

  @Test
  void outboxPump011() throws SQLException {
    var h = new Harness();
    h.now = 1;
    h.pump.sampleIfDue();
    h.now = 0;
    h.pump.sampleIfDue();
    assertEquals(1, h.factoryReads);
    assertEquals(3, h.pump.get().orElseThrow().counts().pending());
  }

  @Test
  void outboxPump012() {
    ordinaryFailure("open", new SQLException("open"), false);
  }

  @Test
  void outboxPump013() {
    ordinaryFailure("query", new SQLException("query"), false);
  }

  @Test
  void outboxPump014() {
    ordinaryFailure("rollback", new SQLException("rollback"), false);
  }

  @Test
  void outboxPump015() {
    ordinaryFailure("close", new SQLException("close"), true);
  }

  @Test
  void outboxPump016() {
    ordinaryFailure("close", new AssertionError("close"), true);
  }

  @Test
  void outboxPump017() {
    var h = new Harness();
    var fatal = new AssertionError("diagnostic");
    h.configure =
        f -> {
          f.faults.put("close", new SQLException("close"));
          f.faults.put("diagnostic", fatal);
        };
    assertSame(fatal, assertThrows(AssertionError.class, h.pump::sampleIfDue));
    assertFalse(h.pump.isQuiescent());
    assertTrue(h.pump.get().isEmpty());
    h.now = PERIOD;
    assertDoesNotThrow(h.pump::sampleIfDue);
    assertEquals(1, h.factoryReads);
  }

  @Test
  void outboxPump018() {
    var h = new Harness();
    h.prepared = () -> null;
    assertThrows(NullPointerException.class, h.pump::sampleIfDue);
    assertTrue(h.pump.isQuiescent());
    assertTrue(h.pump.get().isEmpty());
  }

  @Test
  void outboxPump019() {
    var h = new Harness();
    var primary = new IllegalStateException("factory");
    h.factoryFault = primary;
    assertSame(primary, assertThrows(IllegalStateException.class, h.pump::sampleIfDue));
    assertTrue(h.pump.isQuiescent());
    assertTrue(h.fixtures.isEmpty());
  }

  @Test
  void outboxPump020() {
    var h = new Harness();
    var fatal = new AssertionError("factory");
    h.factoryFault = fatal;
    assertSame(fatal, assertThrows(AssertionError.class, h.pump::sampleIfDue));
    assertTrue(h.pump.isQuiescent());
    assertTrue(h.fixtures.isEmpty());
  }

  @Test
  void outboxPump021() throws SQLException {
    var h = new Harness();
    h.pump.sampleIfDue();
    var primary = new IllegalStateException("nano");
    h.clockFault = primary;
    assertSame(primary, assertThrows(IllegalStateException.class, h.pump::sampleIfDue));
    assertTrue(h.pump.isQuiescent());
    assertTrue(h.pump.get().isEmpty());
    assertEquals(1, h.factoryReads);
  }

  @Test
  void outboxPump022() {
    var h = new Harness();
    var fatal = new AssertionError("nano");
    h.clockFault = fatal;
    assertSame(fatal, assertThrows(AssertionError.class, h.pump::sampleIfDue));
    assertEquals(0, h.factoryReads);
    assertTrue(h.pump.isQuiescent());
  }

  @Test
  void outboxPump023() throws SQLException {
    var h = new Harness();
    h.pump.requestStop();
    h.pump.sampleIfDue();
    assertEquals(0, h.clockReads);
    assertEquals(0, h.factoryReads);
    assertTrue(h.pump.get().isEmpty());
    assertTrue(h.pump.isQuiescent());
  }

  @Test
  void outboxPump024() throws SQLException {
    var h = new Harness();
    h.pump.sampleIfDue();
    h.pump.requestStop();
    assertTrue(h.pump.get().isEmpty());
    assertTrue(h.pump.isQuiescent());
    h.now = PERIOD;
    h.pump.sampleIfDue();
    assertEquals(1, h.factoryReads);
  }

  @Test
  void outboxPump025() throws SQLException {
    var h = new Harness();
    h.pump.requestStop();
    h.pump.requestStop();
    h.pump.sampleIfDue();
    assertTrue(h.pump.isQuiescent());
    assertTrue(h.pump.get().isEmpty());
    assertTrue(h.fixtures.isEmpty());
  }

  @Test
  void outboxPump026() throws Exception {
    var h = new Harness();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    h.configure =
        f ->
            f.query.beforeStatementClose =
                () -> {
                  entered.countDown();
                  await(release);
                };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending =
          worker.submit(
              () -> {
                h.pump.sampleIfDue();
                return true;
              });
      try {
        await(entered);
        assertFalse(h.pump.isQuiescent());
        assertTrue(h.pump.get().isEmpty());
      } finally {
        release.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS));
      assertTrue(h.pump.isQuiescent());
      assertEquals(3, h.pump.get().orElseThrow().counts().pending());
    }
  }

  @Test
  void outboxPump027() throws Exception {
    var h = new Harness();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    h.configure =
        f ->
            f.query.beforeStatementClose =
                () -> {
                  entered.countDown();
                  await(release);
                };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending =
          worker.submit(
              () -> {
                h.pump.sampleIfDue();
                return true;
              });
      try {
        await(entered);
        h.pump.sampleIfDue();
        assertEquals(1, h.factoryReads);
        assertEquals(1, h.clockReads);
      } finally {
        release.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS));
      h.fixtures.getFirst().cleanup(1, 1);
    }
  }

  @Test
  void outboxPump028() throws Exception {
    var h = new Harness();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    h.prepared =
        () -> {
          entered.countDown();
          await(release);
          var f = new Fixture();
          h.fixtures.add(f);
          return f.attempt();
        };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending =
          worker.submit(
              () -> {
                h.pump.sampleIfDue();
                return true;
              });
      try {
        await(entered);
        h.pump.requestStop();
        assertFalse(h.pump.isQuiescent());
        assertTrue(h.pump.get().isEmpty());
      } finally {
        release.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS));
      assertTrue(h.pump.isQuiescent());
      assertTrue(h.fixtures.getFirst().calls.isEmpty());
    }
  }

  @Test
  void outboxPump029() throws Exception {
    var h = new Harness();
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    h.configure =
        f ->
            f.query.beforeStatementClose =
                () -> {
                  entered.countDown();
                  await(release);
                };
    try (var worker = Executors.newSingleThreadExecutor()) {
      var pending =
          worker.submit(
              () -> {
                h.pump.sampleIfDue();
                return true;
              });
      try {
        await(entered);
        h.pump.requestStop();
        assertTrue(h.pump.get().isEmpty());
        assertFalse(h.pump.isQuiescent());
      } finally {
        release.countDown();
      }
      assertTrue(pending.get(10, TimeUnit.SECONDS));
      assertTrue(h.pump.get().isEmpty());
      assertTrue(h.pump.isQuiescent());
      h.fixtures.getFirst().cleanup(1, 1);
    }
  }

  @Test
  void outboxPump030() {
    var h = new Harness();
    var primary = new SQLException("close");
    h.configure = f -> f.faults.put("close", primary);
    assertSame(primary, assertThrows(SQLException.class, h.pump::sampleIfDue));
    h.pump.requestStop();
    assertFalse(h.pump.isQuiescent());
    assertTrue(h.pump.get().isEmpty());
    assertDoesNotThrow(h.pump::sampleIfDue);
    assertEquals(1, h.factoryReads);
  }

  @Test
  void outboxPump031() throws SQLException {
    var h = new Harness();
    h.pump.sampleIfDue();
    h.now = PERIOD;
    h.factoryFault = new IllegalStateException("later factory");
    assertThrows(IllegalStateException.class, h.pump::sampleIfDue);
    assertTrue(h.pump.get().isEmpty());
    assertTrue(h.pump.isQuiescent());
  }

  @Test
  void outboxPump032() throws SQLException {
    var h = new Harness();
    var f = new Fixture(Row.row("PENDING", 3, 2));
    var reused = f.attempt();
    h.prepared = () -> reused;
    h.pump.sampleIfDue();
    h.now = PERIOD;
    assertThrows(IllegalStateException.class, h.pump::sampleIfDue);
    assertTrue(h.pump.get().isEmpty());
    assertTrue(h.pump.isQuiescent());
    assertEquals(2, h.factoryReads);
    f.cleanup(1, 1);
  }
}
