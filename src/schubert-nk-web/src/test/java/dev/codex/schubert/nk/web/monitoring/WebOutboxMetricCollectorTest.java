package dev.codex.schubert.nk.web.monitoring;

import static dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorderTest.unknown;
import static dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorderTest.values;
import static dev.codex.schubert.nk.web.monitoring.WebOutboxObservationRepositoryTest.AS_OF;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorder.Observation;
import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorderTest.Registry;
import dev.codex.schubert.nk.web.monitoring.WebOutboxMetricRecorderTest.Unformattable;
import dev.codex.schubert.nk.web.monitoring.WebOutboxObservationRepositoryTest.Fixture;
import dev.codex.schubert.nk.web.monitoring.WebOutboxObservationRepositoryTest.Row;
import java.sql.SQLException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** WEBOBXCONN001..008/1721, own JDBC proxy/registry/latches only, never real DB/clock/Root. */
class WebOutboxMetricCollectorTest {
  private static final String FIXTURE_PENDING_B11DB31F = "PENDING";
  private static final String FIXTURE_ERROR_F717E7D8 = "ERROR";
  private static final String FIXTURE_DEBUG_B6DFBABB = "DEBUG";

  private static void await(CountDownLatch latch) {
    try {
      assertTrue(latch.await(5, TimeUnit.SECONDS));
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw new AssertionError("owned fixture interrupted", interrupted);
    }
  }

  private static Fixture sample() {
    return new Fixture(
        Row.row(FIXTURE_PENDING_B11DB31F, 3, 2),
        Row.row("SENT", 5, 4),
        Row.row(FIXTURE_ERROR_F717E7D8, 7, 6));
  }

  @Test
  void webObxConn001PublicationWaitsForAllResourceClosesAndReturnsSameCompleteObservation()
      throws SQLException {
    try (var registry = new Registry()) {
      var collector =
          new WebOutboxMetricCollector(
              new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
      var f = sample();
      f.beforeStatementClose =
          () -> {
            assertEquals(List.of("RS"), f.closes);
            assertTrue(collector.snapshot().isEmpty());
            unknown(registry);
          };
      assertTrue(collector.snapshot().isEmpty());
      unknown(registry);
      var supplied = collector.collect(f.connection(), AS_OF).orElseThrow();
      assertSame(supplied, collector.snapshot().orElseThrow());
      assertEquals(3, supplied.pending());
      assertEquals(5, supplied.sent());
      assertEquals(7, supplied.error());
      assertEquals(Duration.ofSeconds(2), supplied.pendingAge());
      assertEquals(Duration.ofSeconds(4), supplied.sentAge());
      assertEquals(Duration.ofSeconds(6), supplied.errorAge());
      values(registry, 3, 5, 7, 2, 4, 6);
      f.complete();
      assertEquals(0, registry.closes.get());
    }
  }

  @Test
  void webObxConn002SuccessfulEmptyIsKnownZeroAndRecoveryDoesNotMutateAnotherOwner()
      throws SQLException {
    try (var registry = new Registry();
        var other = new Registry()) {
      var collector =
          new WebOutboxMetricCollector(
              new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
      var independent =
          new WebOutboxMetricCollector(
              new WebOutboxObservationRepository(), other, FIXTURE_DEBUG_B6DFBABB);
      var empty = new Fixture();
      var zero = collector.collect(empty.connection(), AS_OF).orElseThrow();
      assertSame(zero, collector.snapshot().orElseThrow());
      values(registry, 0, 0, 0, 0, 0, 0);
      empty.complete();
      unknown(other);
      var f = sample();
      var supplied = collector.collect(f.connection(), AS_OF).orElseThrow();
      assertSame(supplied, collector.snapshot().orElseThrow());
      values(registry, 3, 5, 7, 2, 4, 6);
      f.complete();
      var separate = new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, 9, 8));
      independent.collect(separate.connection(), AS_OF);
      values(other, 0, 0, 9, 0, 0, 8);
      separate.complete();
      assertSame(supplied, collector.snapshot().orElseThrow());
      values(registry, 3, 5, 7, 2, 4, 6);
    }
  }

  @Test
  void webObxConn003ReadSqlRuntimeErrorAndNullResourcesBecomeUnknownAndOriginalFailureNotSuccess()
      throws SQLException {
    for (var failure :
        List.<Throwable>of(
            new SQLException("owned read"),
            new Unformattable(),
            new AssertionError("owned read"))) {
      try (var registry = new Registry()) {
        var collector =
            new WebOutboxMetricCollector(
                new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
        var good = sample();
        collector.collect(good.connection(), AS_OF);
        good.complete();
        var bad = sample();
        bad.faults.put("count", failure);
        assertSame(
            failure,
            assertThrows(failure.getClass(), () -> collector.collect(bad.connection(), AS_OF)));
        assertTrue(collector.snapshot().isEmpty());
        unknown(registry);
        bad.complete();
        var recovered = sample();
        collector.collect(recovered.connection(), AS_OF);
        values(registry, 3, 5, 7, 2, 4, 6);
        recovered.complete();
        assertEquals(0, registry.closes.get());
      }
    }
    for (boolean nullStatement : List.of(false, true))
      try (var registry = new Registry()) {
        var collector =
            new WebOutboxMetricCollector(
                new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
        var good = sample();
        collector.collect(good.connection(), AS_OF);
        good.complete();
        var bad = new Fixture();
        bad.nullStatement = nullStatement;
        bad.nullRows = !nullStatement;
        assertThrows(SQLException.class, () -> collector.collect(bad.connection(), AS_OF));
        assertTrue(collector.snapshot().isEmpty());
        unknown(registry);
        assertEquals(nullStatement ? List.of() : List.of("PS"), bad.closes);
      }
  }

  @Test
  void webObxConn004ConstructorNullBoundaryAndStandardNeverReadOrMutateConnection()
      throws SQLException {
    try (var registry = new Registry()) {
      var repo = new WebOutboxObservationRepository();
      assertThrows(
          NullPointerException.class,
          () -> new WebOutboxMetricCollector(null, registry, FIXTURE_DEBUG_B6DFBABB));
      assertThrows(
          NullPointerException.class,
          () -> new WebOutboxMetricCollector(repo, null, FIXTURE_DEBUG_B6DFBABB));
      assertThrows(
          NullPointerException.class, () -> new WebOutboxMetricCollector(repo, registry, null));
      for (String mode : List.of("", "debug", "unknown", "DEBTf", "STANDAQc"))
        assertEquals(
            "CONFIG_INVALID",
            assertThrows(
                    IllegalArgumentException.class,
                    () -> new WebOutboxMetricCollector(repo, registry, mode))
                .getMessage());
      var f = new Fixture();
      f.faults.put("autoCommit", new AssertionError("STANDARD SQL forbidden"));
      var collector = new WebOutboxMetricCollector(repo, registry, "STANDARD");
      assertTrue(collector.snapshot().isEmpty());
      assertTrue(collector.collect(f.connection(), AS_OF).isEmpty());
      assertThrows(NullPointerException.class, () -> collector.collect(null, AS_OF));
      assertThrows(NullPointerException.class, () -> collector.collect(f.connection(), null));
      assertEquals(0, f.prepared);
      assertEquals(0, registry.factories.get());
      assertEquals(0, registry.getMeters().size());
      assertTrue(f.closes.isEmpty());
    }
    try (var registry = new Registry()) {
      var collector =
          new WebOutboxMetricCollector(
              new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
      var f = new Fixture();
      assertThrows(NullPointerException.class, () -> collector.collect(null, AS_OF));
      assertThrows(NullPointerException.class, () -> collector.collect(f.connection(), null));
      assertEquals(0, f.prepared);
      unknown(registry);
    }
  }

  @Test
  void
      webObxConn005CloseFailuresAlsoInvalidateObservationWithoutLosingFailureOrConnectionOwnership()
          throws SQLException {
    for (String point : List.of("RSclose", "PSclose"))
      for (var failure :
          List.<Throwable>of(
              new SQLException("owned close"),
              new Unformattable(),
              new AssertionError("owned close"))) {
        try (var registry = new Registry()) {
          var collector =
              new WebOutboxMetricCollector(
                  new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
          var good = sample();
          collector.collect(good.connection(), AS_OF);
          good.complete();
          var bad = sample();
          bad.faults.put(point, failure);
          assertSame(
              failure,
              assertThrows(failure.getClass(), () -> collector.collect(bad.connection(), AS_OF)));
          assertTrue(collector.snapshot().isEmpty());
          unknown(registry);
          bad.complete();
          assertEquals(0, registry.closes.get());
        }
      }
  }

  @Test
  void webObxConn006OwnedContenderReallyBlocksUntilReadonlyAcquisitionAndPublicationFinish()
      throws Exception {
    try (var registry = new Registry()) {
      var executor = Executors.newFixedThreadPool(2);
      try {
        var collector =
            new WebOutboxMetricCollector(
                new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
        var entered = new CountDownLatch(1);
        var release = new CountDownLatch(1);
        var attempted = new CountDownLatch(1);
        var contender = new AtomicReference<Thread>();
        var first = new Fixture(Row.row(FIXTURE_PENDING_B11DB31F, 3, 2));
        var second = new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, 7, 6));
        var seen = new AtomicReference<Observation>();
        first.beforeStatementClose =
            () -> {
              assertTrue(collector.snapshot().isEmpty());
              unknown(registry);
              entered.countDown();
              await(release);
            };
        second.beforeStatementClose =
            () -> {
              seen.set(collector.snapshot().orElseThrow());
              values(registry, 3, 0, 0, 2, 0, 0);
            };
        var a = executor.submit(() -> collector.collect(first.connection(), AS_OF));
        try {
          await(entered);
          var b =
              executor.submit(
                  () -> {
                    contender.set(Thread.currentThread());
                    attempted.countDown();
                    return collector.collect(second.connection(), AS_OF);
                  });
          await(attempted);
          long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
          while (contender.get().getState() != Thread.State.BLOCKED && System.nanoTime() < deadline)
            Thread.onSpinWait();
          assertEquals(Thread.State.BLOCKED, contender.get().getState());
          assertEquals(0, second.prepared);
          assertTrue(collector.snapshot().isEmpty());
          release.countDown();
          var one = a.get(5, TimeUnit.SECONDS).orElseThrow();
          var two = b.get(5, TimeUnit.SECONDS).orElseThrow();
          assertSame(one, seen.get());
          assertSame(two, collector.snapshot().orElseThrow());
          values(registry, 0, 0, 7, 0, 0, 6);
        } finally {
          release.countDown();
        }
        first.complete();
        second.complete();
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void webObxConn007ParallelIndependentConnectionResultsMatchPrecomputedOwnerVectors()
      throws Exception {
    try (var registry = new Registry();
        var other = new Registry()) {
      var executor = Executors.newFixedThreadPool(8);
      try {
        var collector =
            new WebOutboxMetricCollector(
                new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB);
        var expected = new ArrayList<long[]>();
        var jobs = new ArrayList<Callable<Optional<Observation>>>();
        for (int i = 1; i <= 64; i++) {
          long p = i;
          long s = i + 1L;
          long e = i + 2L;
          expected.add(new long[] {p, s, e});
          jobs.add(
              () -> {
                var f =
                    new Fixture(
                        Row.row(FIXTURE_PENDING_B11DB31F, p, p),
                        Row.row("SENT", s, s),
                        Row.row(FIXTURE_ERROR_F717E7D8, e, e));
                var value = collector.collect(f.connection(), AS_OF);
                f.complete();
                return value;
              });
        }
        var returned = new ArrayList<Observation>();
        var futures = executor.invokeAll(jobs, 5, TimeUnit.SECONDS);
        for (int i = 0; i < 64; i++) {
          var value = futures.get(i).get(5, TimeUnit.SECONDS).orElseThrow();
          returned.add(value);
          var vector = expected.get(i);
          assertEquals(vector[0], value.pending());
          assertEquals(vector[1], value.sent());
          assertEquals(vector[2], value.error());
          assertEquals(Duration.ofSeconds(vector[0]), value.pendingAge());
          assertEquals(Duration.ofSeconds(vector[1]), value.sentAge());
          assertEquals(Duration.ofSeconds(vector[2]), value.errorAge());
        }
        var selected = collector.snapshot().orElseThrow();
        int owner = -1;
        for (int i = 0; i < returned.size(); i++) if (returned.get(i) == selected) owner = i;
        assertTrue(owner >= 0);
        var vector = expected.get(owner);
        values(registry, vector[0], vector[1], vector[2], vector[0], vector[1], vector[2]);
        var independent =
            new WebOutboxMetricCollector(
                new WebOutboxObservationRepository(), other, FIXTURE_DEBUG_B6DFBABB);
        unknown(other);
        var f = new Fixture(Row.row(FIXTURE_ERROR_F717E7D8, 9, 8));
        independent.collect(f.connection(), AS_OF);
        values(other, 0, 0, 9, 0, 0, 8);
        f.complete();
        assertSame(selected, collector.snapshot().orElseThrow());
        values(registry, vector[0], vector[1], vector[2], vector[0], vector[1], vector[2]);
      } finally {
        executor.shutdownNow();
        assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
      }
    }
  }

  @Test
  void
      webObxConn008PartialMetricFactoryFailureNeverCreatesSuccessfulCollectorOrClosesBorrowedRegistry() {
    for (var failure :
        List.<Throwable>of(new Unformattable(), new AssertionError("owned factory"))) {
      var registry = new Registry();
      registry.failure = Optional.of(failure);
      try {
        assertSame(
            failure,
            assertThrows(
                failure.getClass(),
                () ->
                    new WebOutboxMetricCollector(
                        new WebOutboxObservationRepository(), registry, FIXTURE_DEBUG_B6DFBABB)));
        assertEquals(2, registry.factories.get());
        assertEquals(1, registry.getMeters().size());
        assertTrue(
            Double.isNaN(
                WebOutboxMetricRecorderTest.gauge(
                    registry, "nk_outbox_rows", FIXTURE_PENDING_B11DB31F)));
        assertEquals(0, registry.closes.get());
      } finally {
        registry.close();
      }
      assertEquals(1, registry.closes.get());
    }
  }
}
