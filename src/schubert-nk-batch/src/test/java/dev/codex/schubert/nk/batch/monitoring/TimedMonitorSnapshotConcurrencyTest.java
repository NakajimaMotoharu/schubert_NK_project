package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.ContinuousConditionWindow.State;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.OptionalDouble;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.IntConsumer;
import java.util.function.Supplier;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/** PT-OPS-MON-SNAP001..005; RD171/UI252/SS351 §7; synthetic observations only. */
final class TimedMonitorSnapshotConcurrencyTest {
  private static final Instant EPOCH = Instant.parse("2026-08-31T12:00:00Z");
  private static final int FIRST_ELAPSED = 300;
  private static final int UPDATES = 32;

  @Test
  void snap001FilesystemPublishesWholeEvents() throws Exception {
    var monitor = new TimedFilesystemMonitor(Service.API);
    monitor.observe(OptionalDouble.of(92), false, at(0));
    verifySnapshots(
        Condition.FILESYSTEM,
        seconds -> monitor.observe(OptionalDouble.of(92), true, at(seconds)),
        monitor::snapshot);
  }

  @Test
  void snap002HeapPublishesWholeEvents() throws Exception {
    var monitor = new TimedJvmHeapMonitor(Service.API);
    verifySnapshots(
        Condition.JVM_HEAP,
        seconds -> monitor.observe(OptionalDouble.of(90), false, true, at(seconds)),
        monitor::snapshot);
  }

  @Test
  void snap003PoolPublishesWholeEvents() throws Exception {
    var monitor = new TimedDbPoolMonitor(Service.API);
    verifySnapshots(
        Condition.DB_POOL,
        seconds -> monitor.observe(OptionalDouble.of(0), 1, 0, true, at(seconds)),
        monitor::snapshot);
  }

  @Test
  void snap004LatencyPublishesWholeEvents() throws Exception {
    var monitor = new TimedSyncLatencyMonitor(Service.API);
    monitor.observe(OptionalDouble.of(3), false, at(0));
    verifySnapshots(
        Condition.SYNC_P95,
        seconds -> monitor.observe(OptionalDouble.of(3), true, at(seconds)),
        monitor::snapshot);
  }

  @Test
  @DisplayName("PT-OPS-MON-SNAP005 rejected elapsed time releases all six observation locks")
  void rejectedElapsedTimeReleasesAllSixLocks() throws Exception {
    var filesystem = new TimedFilesystemMonitor(Service.API);
    var heap = new TimedJvmHeapMonitor(Service.API);
    var pool = new TimedDbPoolMonitor(Service.API);
    var latency = new TimedSyncLatencyMonitor(Service.API);
    var window = new ContinuousConditionWindow();
    var alert = new AlertLifecycle(Condition.TRANSFER, Service.API);

    List<IntConsumer> transitions =
        List.of(
            seconds -> filesystem.observe(OptionalDouble.of(92), true, at(seconds)),
            seconds -> heap.observe(OptionalDouble.of(88), false, true, at(seconds)),
            seconds -> pool.observe(OptionalDouble.of(0), 1, 0, true, at(seconds)),
            seconds -> latency.observe(OptionalDouble.of(3), true, at(seconds)),
            seconds -> window.observe(State.VIOLATING, Duration.ofSeconds(seconds), true),
            seconds ->
                alert.observe(
                    Severity.WARNING,
                    CauseClearance.CONFIRMED,
                    EPOCH.plusSeconds(seconds),
                    Duration.ofSeconds(seconds)));
    for (IntConsumer observe : transitions) {
      observe.accept(1);
      assertThrows(IllegalArgumentException.class, () -> observe.accept(0));
    }

    var worker = Executors.newVirtualThreadPerTaskExecutor();
    try {
      worker
          .submit(
              () -> {
                assertTrue(filesystem.observe(OptionalDouble.of(92), true, at(2)).event().isEmpty());
                assertTrue(heap.observe(OptionalDouble.of(88), false, true, at(2)).event().isEmpty());
                assertEquals(
                    2,
                    pool.observe(OptionalDouble.of(0), 1, 0, true, at(2))
                        .event()
                        .orElseThrow()
                        .count()
                        .intValueExact());
                assertTrue(latency.observe(OptionalDouble.of(3), true, at(2)).event().isEmpty());
                assertEquals(
                    Duration.ofSeconds(1),
                    window.observe(State.VIOLATING, Duration.ofSeconds(2), true).orElseThrow());
                assertEquals(
                    2,
                    alert
                        .observe(
                            Severity.WARNING,
                            CauseClearance.CONFIRMED,
                            EPOCH.plusSeconds(2),
                            Duration.ofSeconds(2))
                        .orElseThrow()
                        .count()
                        .intValueExact());
                assertEquals(EPOCH.plusSeconds(2), alert.snapshot().orElseThrow().lastSeen());
              })
          .get(10, TimeUnit.SECONDS);
    } finally {
      worker.shutdownNow();
      assertTrue(worker.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static ObservationContext at(int seconds) {
    return new ObservationContext(
        CauseClearance.CONFIRMED, EPOCH.plusSeconds(seconds), Duration.ofSeconds(seconds));
  }

  private static void verifySnapshots(
      Condition condition, IntConsumer observe, Supplier<Optional<Event>> snapshot)
      throws Exception {
    observe.accept(FIRST_ELAPSED);
    Event original = snapshot.get().orElseThrow();
    assertEquals(1, verifyEvent(condition, original));

    var start = new CountDownLatch(1);
    var workers = Executors.newFixedThreadPool(2);
    try {
      var writer =
          workers.submit(
              () -> {
                assertTrue(start.await(10, TimeUnit.SECONDS));
                for (int i = 1; i <= UPDATES; i++) {
                  observe.accept(FIRST_ELAPSED + i);
                }
                return null;
              });
      var reader =
          workers.submit(
              () -> {
                assertTrue(start.await(10, TimeUnit.SECONDS));
                int lastCount = 1;
                for (int i = 0; i < UPDATES; i++) {
                  int count = verifyEvent(condition, snapshot.get().orElseThrow());
                  assertTrue(count >= lastCount);
                  lastCount = count;
                }
                return null;
              });
      start.countDown();
      writer.get(10, TimeUnit.SECONDS);
      reader.get(10, TimeUnit.SECONDS);
    } finally {
      workers.shutdownNow();
      assertTrue(workers.awaitTermination(10, TimeUnit.SECONDS));
    }

    assertEquals(UPDATES + 1, verifyEvent(condition, snapshot.get().orElseThrow()));
    assertEquals(1, verifyEvent(condition, original));
  }

  private static int verifyEvent(Condition condition, Event event) {
    int count = event.count().intValueExact();
    assertTrue(count >= 1 && count <= UPDATES + 1);
    assertEquals(condition, event.condition());
    assertEquals(Service.API, event.service());
    assertEquals(Severity.CRITICAL, event.severity());
    assertTrue(event.isOpen());
    assertEquals(EPOCH.plusSeconds(FIRST_ELAPSED), event.firstSeen());
    assertEquals(EPOCH.plusSeconds(FIRST_ELAPSED + count - 1), event.lastSeen());
    return count;
  }
}
