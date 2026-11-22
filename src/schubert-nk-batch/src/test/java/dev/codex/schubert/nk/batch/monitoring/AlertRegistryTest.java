package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent finite72-key registry/ownership vectors, PT-OPS-ALERTREG-001..004/spec1545. */
class AlertRegistryTest {
  private static final Instant TIME = Instant.parse("2026-10-23T00:00:00Z");

  private static void observe(
      AlertRegistry registry,
      Condition condition,
      Service service,
      Severity severity,
      long seconds) {
    registry.observe(
        condition, service, severity, CauseClearance.CONFIRMED, TIME, Duration.ofSeconds(seconds));
  }

  @Test
  void alertReg001PerKeyDedupIndependentIdentityAndImmutableOrder() {
    var registry = new AlertRegistry();
    assertTrue(registry.activeEvents().isEmpty());
    observe(registry, Condition.TRANSFER, Service.API, Severity.WARNING, 0);
    observe(registry, Condition.FILESYSTEM, Service.WEB, Severity.WARNING, 0);
    observe(registry, Condition.FILESYSTEM, Service.WEB, Severity.CRITICAL, 1);
    var events = registry.activeEvents();
    assertEquals(2, events.size());
    assertEquals(Condition.FILESYSTEM, events.get(0).condition());
    assertEquals(Service.WEB, events.get(0).service());
    assertEquals(BigInteger.TWO, events.get(0).count());
    assertEquals(Severity.CRITICAL, events.get(0).severity());
    assertEquals(Condition.TRANSFER, events.get(1).condition());
    assertEquals(Service.API, events.get(1).service());
    assertEquals(BigInteger.ONE, events.get(1).count());
    assertThrows(UnsupportedOperationException.class, events::clear);
  }

  @Test
  void alertReg002ExactlySeventyTwoKeysAndAllRecovery() {
    var registry = new AlertRegistry();
    for (var condition : Condition.values())
      for (var service : Service.values())
        observe(registry, condition, service, Severity.WARNING, 0);
    var historical = registry.activeEvents();
    assertEquals(72, historical.size());
    int index = 0;
    for (var condition : Condition.values()) {
      for (var service : Service.values()) {
        assertEquals(condition, historical.get(index).condition());
        assertEquals(service, historical.get(index).service());
        index++;
        observe(registry, condition, service, Severity.NORMAL, 0);
        observe(registry, condition, service, Severity.NORMAL, 300);
      }
    }
    assertEquals(12, registry.activeEvents().size());
    int retained = 0;
    for (var condition : new Condition[] {Condition.DLQ, Condition.INTEGRITY_CONFIG})
      for (var service : Service.values()) {
        var event = registry.activeEvents().get(retained);
        retained++;
        assertEquals(condition, event.condition());
        assertEquals(service, event.service());
        assertEquals(BigInteger.ONE, event.count());
        assertTrue(event.isOpen());
      }
    assertEquals(72, historical.size());
    assertTrue(historical.stream().allMatch(AlertLifecycle.Event::isOpen));
  }

  @Test
  void alertReg003MissingInputsDoNotChangeExistingKey() {
    var registry = new AlertRegistry();
    observe(registry, Condition.TRANSFER, Service.API, Severity.WARNING, 0);
    assertThrows(
        NullPointerException.class,
        () -> observe(registry, null, Service.WEB, Severity.WARNING, 0));
    assertThrows(
        NullPointerException.class,
        () -> observe(registry, Condition.FILESYSTEM, null, Severity.WARNING, 0));
    assertThrows(
        NullPointerException.class,
        () -> observe(registry, Condition.FILESYSTEM, Service.WEB, null, 0));
    assertThrows(
        NullPointerException.class,
        () ->
            registry.observe(
                Condition.FILESYSTEM, Service.WEB, Severity.WARNING, null, TIME, Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () ->
            registry.observe(
                Condition.FILESYSTEM,
                Service.WEB,
                Severity.WARNING,
                CauseClearance.CONFIRMED,
                null,
                Duration.ZERO));
    assertThrows(
        NullPointerException.class,
        () ->
            registry.observe(
                Condition.FILESYSTEM,
                Service.WEB,
                Severity.WARNING,
                CauseClearance.CONFIRMED,
                TIME,
                null));
    assertEquals(1, registry.activeEvents().size());
    assertEquals(Condition.TRANSFER, registry.activeEvents().getFirst().condition());
    assertEquals(BigInteger.ONE, registry.activeEvents().getFirst().count());
  }

  @Test
  void alertReg004ConcurrentCallersShareOneKeyOwner()
      throws InterruptedException, ExecutionException {
    var registry = new AlertRegistry();
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<String>>();
      for (int index = 0; index < 64; index++) {
        tasks.add(
            () -> {
              observe(registry, Condition.FILESYSTEM, Service.WEB, Severity.WARNING, 0);
              return "recorded";
            });
      }
      for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS))
        assertEquals("recorded", future.get());
      var events = registry.activeEvents();
      assertEquals(1, events.size());
      assertEquals(BigInteger.valueOf(64), events.getFirst().count());
      assertEquals(TIME, events.getFirst().firstSeen());
      assertEquals(TIME, events.getFirst().lastSeen());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }
}
