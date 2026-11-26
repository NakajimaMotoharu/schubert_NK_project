package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.fixture.BoundedBatchFixtureWorkers;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Closed owner state only, no real metric/service. Spec1567/MONMISSING001..003. */
class MonitoringMissingObservationTest {
  private static final Instant AT = Instant.parse("2026-10-23T00:00:00Z");

  private static ObservationContext context(long seconds) {
    return new ObservationContext(CauseClearance.UNCONFIRMED, AT, Duration.ofSeconds(seconds));
  }

  private static void warning(MonitoringPolicyEngine engine) {
    engine.filesystem(Service.WEB, 80, Duration.ofMinutes(5), Duration.ZERO, context(0));
  }

  @Test
  void monMissing001AllRegistryKeysRequireFreshRecovery() {
    var registry = new AlertRegistry();
    for (var condition : Condition.values())
      for (var service : Service.values()) {
        registry.observe(
            condition, service, Severity.WARNING, CauseClearance.UNCONFIRMED, AT, Duration.ZERO);
        registry.observe(
            condition,
            service,
            Severity.NORMAL,
            CauseClearance.UNCONFIRMED,
            AT,
            Duration.ofSeconds(1));
      }
    var before = registry.activeEvents();
    assertEquals(72, before.size());
    for (var condition : Condition.values())
      for (var service : Service.values())
        registry.interruptContinuity(condition, service, Duration.ofSeconds(300));
    assertEquals(before, registry.activeEvents());
    for (var event : registry.activeEvents()) {
      assertEquals(BigInteger.ONE, event.count());
      assertEquals(AT, event.firstSeen());
      assertEquals(AT, event.lastSeen());
      assertTrue(event.isOpen());
    }
    int closed = 0;
    for (var condition : Condition.values())
      for (var service : Service.values()) {
        assertTrue(
            registry
                .observe(
                    condition,
                    service,
                    Severity.NORMAL,
                    CauseClearance.UNCONFIRMED,
                    AT,
                    Duration.ofSeconds(301))
                .orElseThrow()
                .isOpen());
        assertTrue(
            registry
                .observe(
                    condition,
                    service,
                    Severity.NORMAL,
                    CauseClearance.UNCONFIRMED,
                    AT,
                    Duration.ofSeconds(600))
                .orElseThrow()
                .isOpen());
        boolean protectedKey =
            condition == Condition.DLQ || condition == Condition.INTEGRITY_CONFIG;
        boolean stillOpen =
            registry
                .observe(
                    condition,
                    service,
                    Severity.NORMAL,
                    CauseClearance.UNCONFIRMED,
                    AT,
                    Duration.ofSeconds(601))
                .orElseThrow()
                .isOpen();
        assertEquals(protectedKey, stillOpen);
        if (!stillOpen) closed++;
      }
    assertEquals(60, closed);
    assertEquals(12, registry.activeEvents().size());
    for (var event : registry.activeEvents()) {
      assertTrue(
          event.condition() == Condition.DLQ || event.condition() == Condition.INTEGRITY_CONFIG);
      assertTrue(event.isOpen());
      assertEquals(BigInteger.ONE, event.count());
      assertEquals(AT, event.firstSeen());
      assertEquals(AT, event.lastSeen());
    }
  }

  @Test
  void monMissing002EngineBoundariesPreserveEachOwner() {
    var engine = new MonitoringPolicyEngine();
    warning(engine);
    var before = engine.activeAlerts();
    assertThrows(
        NullPointerException.class,
        () -> engine.observationMissing(null, Service.WEB, Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () -> engine.observationMissing(Condition.FILESYSTEM, null, Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () -> engine.observationMissing(Condition.FILESYSTEM, Service.WEB, null));
    assertThrows(
        IllegalArgumentException.class,
        () -> engine.observationMissing(Condition.FILESYSTEM, Service.WEB, Duration.ofNanos(-1)));
    engine.observationMissing(Condition.FILESYSTEM, Service.WEB, Duration.ofSeconds(1));
    assertEquals(before, engine.activeAlerts());
    assertThrows(
        IllegalArgumentException.class,
        () -> engine.observationMissing(Condition.FILESYSTEM, Service.WEB, Duration.ZERO));
    engine.observationMissing(Condition.INTEGRITY_CONFIG, Service.API, Duration.ofSeconds(10));
    assertEquals(before, engine.activeAlerts());
    assertThrows(
        IllegalArgumentException.class, () -> engine.integrity(Service.API, 1, context(9)));
    assertEquals(before, engine.activeAlerts());
    assertEquals(
        Severity.CRITICAL, engine.integrity(Service.API, 1, context(10)).orElseThrow().severity());
    assertEquals(2, engine.activeAlerts().size());
    assertEquals(BigInteger.ONE, before.getFirst().count());
  }

  @Test
  void monMissing003ConcurrentAbsencePreservesImmutableSnapshot() throws Exception {
    var engine = new MonitoringPolicyEngine();
    warning(engine);
    engine.filesystem(Service.WEB, 0, Duration.ZERO, Duration.ZERO, context(1));
    var before = engine.activeAlerts();
    try (var workers =
        new BoundedBatchFixtureWorkers(
            Executors.newFixedThreadPool(4), 10, "missing observations")) {
      var tasks = new ArrayList<Callable<List<Event>>>();
      for (int index = 0; index < 64; index++)
        tasks.add(
            () -> {
              engine.observationMissing(Condition.FILESYSTEM, Service.WEB, Duration.ofSeconds(300));
              return engine.activeAlerts();
            });
      for (var future : workers.executor().invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals(before, future.get());
    }
    assertThrows(UnsupportedOperationException.class, () -> before.clear());
    assertEquals(BigInteger.ONE, before.getFirst().count());
    assertEquals(AT, before.getFirst().lastSeen());
    assertTrue(
        engine
            .filesystem(Service.WEB, 0, Duration.ZERO, Duration.ZERO, context(301))
            .orElseThrow()
            .isOpen());
    assertTrue(
        engine
            .filesystem(Service.WEB, 0, Duration.ZERO, Duration.ZERO, context(600))
            .orElseThrow()
            .isOpen());
    assertFalse(
        engine
            .filesystem(Service.WEB, 0, Duration.ZERO, Duration.ZERO, context(601))
            .orElseThrow()
            .isOpen());
    assertTrue(engine.activeAlerts().isEmpty());
    assertTrue(before.getFirst().isOpen());
  }
}
