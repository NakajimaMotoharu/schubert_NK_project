package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicy.DetailService;
import java.math.BigInteger;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent SS351 input literals and fixed expected identity/levels; PT-OPS-MONPIPE-001..008. */
class MonitoringPolicyEngineTest {
  private static final Instant TIME = Instant.parse("2026-10-23T00:00:00Z");
  private static final Duration ZERO = Duration.ZERO;
  private static final Duration MINUTE = Duration.ofSeconds(60);
  private static final Duration FIVE = Duration.ofSeconds(300);
  private static final Duration TEN = Duration.ofSeconds(600);
  private static final Duration THIRTY = Duration.ofSeconds(1800);

  private static ObservationContext context(long seconds, CauseClearance cause) {
    return new ObservationContext(cause, TIME, Duration.ofSeconds(seconds));
  }

  // This creates independent SS input vectors, never expected values from Production evaluation.
  private static Optional<Event> evaluate(
      MonitoringPolicyEngine engine,
      Condition condition,
      Service service,
      Severity requested,
      ObservationContext context) {
    boolean normal = requested == Severity.NORMAL;
    boolean critical = requested == Severity.CRITICAL;
    return switch (condition) {
      case FILESYSTEM ->
          engine.filesystem(
              service,
              normal ? 0 : critical ? 90 : 80,
              normal ? ZERO : critical ? MINUTE : FIVE,
              critical ? MINUTE : ZERO,
              context);
      case TRANSFER ->
          engine.transfer(
              service, normal ? 0 : critical ? 4_500_000_000L : 3_500_000_000L, 0, context);
      case ASYNC_QUEUE ->
          engine.asyncQueue(service, 1, normal ? 0 : critical ? 900 : 700, 1000, context);
      case WEB_LOG ->
          engine.webLog(service, normal ? 0 : 1, normal ? ZERO : critical ? THIRTY : FIVE, context);
      case DLQ -> engine.dlq(service, normal ? 0 : 1, critical, false, context);
      case EXPIRY -> engine.expiry(service, normal ? 0 : critical ? 5000 : 1000, context);
      case DB_POOL ->
          engine.dbPool(
              service,
              normal || critical ? 0 : 80,
              normal || critical ? ZERO : FIVE,
              critical ? 1 : 0,
              0,
              context);
      case JVM_HEAP ->
          engine.jvmHeap(
              service,
              normal ? 0 : critical ? 90 : 75,
              normal || critical ? ZERO : TEN,
              false,
              context);
      case SYNC_P95 ->
          engine.syncP95(
              service,
              normal ? 0 : critical ? 2.6 : 2.1,
              normal ? ZERO : FIVE,
              critical ? FIVE : ZERO,
              context);
      case BACKUP -> engine.backup(service, true, normal, normal ? 0 : critical ? 2 : 1, context);
      case RESTART -> engine.restarts(service, normal ? 0 : critical ? 5 : 1, false, context);
      case INTEGRITY_CONFIG -> engine.integrity(service, normal ? 0 : 1, context);
    };
  }

  @Test
  void monPipe001ObservationContextInvariantsAndImmutableValues() {
    var context = context(1, CauseClearance.UNCONFIRMED);
    assertEquals(CauseClearance.UNCONFIRMED, context.clearance());
    assertEquals(TIME, context.at());
    assertEquals(Duration.ofSeconds(1), context.elapsed());
    assertEquals(
        new ObservationContext(CauseClearance.UNCONFIRMED, TIME, Duration.ofSeconds(1)), context);
    assertThrows(NullPointerException.class, () -> new ObservationContext(null, TIME, ZERO));
    assertThrows(
        NullPointerException.class,
        () -> new ObservationContext(CauseClearance.CONFIRMED, null, ZERO));
    assertThrows(
        NullPointerException.class,
        () -> new ObservationContext(CauseClearance.CONFIRMED, TIME, null));
    assertEquals(
        "invalid alert elapsed time",
        assertThrows(
                IllegalArgumentException.class,
                () -> new ObservationContext(CauseClearance.CONFIRMED, TIME, Duration.ofNanos(-1)))
            .getMessage());
  }

  @Test
  void monPipe002EveryNormalAndWarningEndpointIdentity() {
    var engine = new MonitoringPolicyEngine();
    for (var condition : Condition.values())
      assertTrue(
          evaluate(
                  engine,
                  condition,
                  Service.WEB,
                  Severity.NORMAL,
                  context(0, CauseClearance.UNCONFIRMED))
              .isEmpty());
    assertTrue(engine.activeAlerts().isEmpty());
    for (var condition : Condition.values()) {
      if (condition == Condition.INTEGRITY_CONFIG) continue;
      var event =
          evaluate(
                  engine,
                  condition,
                  Service.WEB,
                  Severity.WARNING,
                  context(0, CauseClearance.UNCONFIRMED))
              .orElseThrow();
      assertEquals(condition, event.condition());
      assertEquals(Service.WEB, event.service());
      assertEquals(Severity.WARNING, event.severity());
      assertEquals(BigInteger.ONE, event.count());
      assertEquals(TIME, event.firstSeen());
      assertEquals(TIME, event.lastSeen());
      assertTrue(event.isOpen());
    }
    assertEquals(11, engine.activeAlerts().size());
  }

  @Test
  void monPipe003EveryCriticalEndpointAndCauseAwareRecovery() {
    var engine = new MonitoringPolicyEngine();
    for (var condition : Condition.values()) {
      var event =
          evaluate(
                  engine,
                  condition,
                  Service.API,
                  Severity.CRITICAL,
                  context(0, CauseClearance.UNCONFIRMED))
              .orElseThrow();
      assertEquals(condition, event.condition());
      assertEquals(Service.API, event.service());
      assertEquals(Severity.CRITICAL, event.severity());
    }
    assertEquals(12, engine.activeAlerts().size());
    for (var condition : Condition.values()) {
      assertTrue(
          evaluate(
                  engine,
                  condition,
                  Service.API,
                  Severity.NORMAL,
                  context(0, CauseClearance.UNCONFIRMED))
              .orElseThrow()
              .isOpen());
      assertTrue(
          evaluate(
                  engine,
                  condition,
                  Service.API,
                  Severity.NORMAL,
                  context(600, CauseClearance.UNCONFIRMED))
              .orElseThrow()
              .isOpen());
      var closed =
          evaluate(
                  engine,
                  condition,
                  Service.API,
                  Severity.NORMAL,
                  context(600, CauseClearance.CONFIRMED))
              .orElseThrow();
      boolean protectedAlert =
          condition == Condition.DLQ || condition == Condition.INTEGRITY_CONFIG;
      assertEquals(protectedAlert, closed.isOpen());
      assertEquals(BigInteger.ONE, closed.count());
    }
    assertEquals(2, engine.activeAlerts().size());
    assertEquals(Condition.DLQ, engine.activeAlerts().get(0).condition());
    assertEquals(Condition.INTEGRITY_CONFIG, engine.activeAlerts().get(1).condition());
  }

  @Test
  void monPipe004RejectedInputsDoNotPartiallyUpdateState() {
    var engine = new MonitoringPolicyEngine();
    var context = context(0, CauseClearance.UNCONFIRMED);
    engine.transfer(Service.WEB, 3_500_000_000L, 0, context);
    var before = engine.activeAlerts();
    assertThrows(
        IllegalArgumentException.class, () -> engine.transfer(Service.WEB, -1, 0, context));
    assertThrows(NullPointerException.class, () -> engine.transfer(null, 0, 0, context));
    assertThrows(NullPointerException.class, () -> engine.transfer(Service.WEB, 0, 0, null));
    assertEquals(before, engine.activeAlerts());
    assertEquals(BigInteger.ONE, engine.activeAlerts().getFirst().count());
  }

  @Test
  void asyncByte001EngineUsesStorageBytesIndependentOfMessageCount() {
    var context = context(0, CauseClearance.UNCONFIRMED);
    var storage = new MonitoringPolicyEngine();
    assertEquals(
        Severity.CRITICAL,
        storage.asyncQueue(Service.API, 1, 90, 100, context).orElseThrow().severity());
    var count = new MonitoringPolicyEngine();
    assertEquals(
        Severity.CRITICAL,
        count.asyncQueue(Service.API, 9000, 0, 1, context).orElseThrow().severity());
    var normal = new MonitoringPolicyEngine();
    assertTrue(normal.asyncQueue(Service.API, 4999, 0, 1, context).isEmpty());
    var before = storage.activeAlerts();
    assertThrows(
        IllegalArgumentException.class, () -> storage.asyncQueue(Service.API, 1, -1, 100, context));
    assertThrows(
        IllegalArgumentException.class, () -> storage.asyncQueue(Service.API, 1, 0, 0, context));
    assertEquals(before, storage.activeAlerts());
  }

  @Test
  void restartFlag001RateLimitIsIndependentOfCountAndInvalidCountCannotMutateState() {
    var at = context(0, CauseClearance.UNCONFIRMED);
    var owner = new MonitoringPolicyEngine();
    assertTrue(owner.restarts(Service.API, 0, false, at).isEmpty());
    var event = owner.restarts(Service.API, 0, true, at).orElseThrow();
    assertEquals(Condition.RESTART, event.condition());
    assertEquals(Service.API, event.service());
    assertEquals(Severity.CRITICAL, event.severity());
    assertEquals(BigInteger.ONE, event.count());
    var before = owner.activeAlerts();
    assertThrows(IllegalArgumentException.class, () -> owner.restarts(Service.API, -1, true, at));
    assertEquals(before, owner.activeAlerts());
  }

  @Test
  void monPipe005ModeConsistencyDoesNotChangeAlerts() {
    var engine = new MonitoringPolicyEngine();
    engine.transfer(Service.WEB, 3_500_000_000L, 0, context(0, CauseClearance.UNCONFIRMED));
    var before = engine.activeAlerts();
    var enabled =
        Map.of(
            DetailService.ACTUATOR,
            true,
            DetailService.PROMETHEUS,
            true,
            DetailService.GRAFANA,
            true,
            DetailService.EXPORTERS,
            true);
    var disabled =
        Map.of(
            DetailService.ACTUATOR,
            false,
            DetailService.PROMETHEUS,
            false,
            DetailService.GRAFANA,
            false,
            DetailService.EXPORTERS,
            false);
    assertEquals(MonitoringModePolicy.DEBUG, engine.verifyMode("DEBUG", enabled));
    assertEquals(MonitoringModePolicy.STANDARD, engine.verifyMode("STANDARD", disabled));
    assertEquals(
        "CONFIG_DRIFT",
        assertThrows(IllegalStateException.class, () -> engine.verifyMode("DEBUG", disabled))
            .getMessage());
    assertEquals(
        "CONFIG_INVALID",
        assertThrows(IllegalArgumentException.class, () -> engine.verifyMode("DEBUG ", enabled))
            .getMessage());
    assertThrows(NullPointerException.class, () -> engine.verifyMode(null, enabled));
    assertThrows(NullPointerException.class, () -> engine.verifyMode("DEBUG", null));
    assertEquals(before, engine.activeAlerts());
  }

  @Test
  void monPipe006ConcurrentSingleEntryKeepsOneOwner() throws Exception {
    var engine = new MonitoringPolicyEngine();
    var context = context(0, CauseClearance.UNCONFIRMED);
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Callable<BigInteger>>();
      for (int index = 0; index < 64; index++)
        tasks.add(
            () -> engine.transfer(Service.WEB, 3_500_000_000L, 0, context).orElseThrow().count());
      var counts = new HashSet<BigInteger>();
      for (var future : executor.invokeAll(tasks, 10, TimeUnit.SECONDS)) counts.add(future.get());
      var expected = new HashSet<BigInteger>();
      for (int value = 1; value <= 64; value++) expected.add(BigInteger.valueOf(value));
      assertEquals(expected, counts);
      assertEquals(1, engine.activeAlerts().size());
      assertEquals(BigInteger.valueOf(64), engine.activeAlerts().getFirst().count());
    } finally {
      executor.shutdownNow();
      assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  @Test
  void monPipe007AllSeventyTwoFixedKeysAndImmutableProjection() {
    var engine = new MonitoringPolicyEngine();
    for (var condition : Condition.values()) {
      for (var service : Service.values()) {
        Severity severity =
            condition == Condition.INTEGRITY_CONFIG ? Severity.CRITICAL : Severity.WARNING;
        evaluate(engine, condition, service, severity, context(0, CauseClearance.UNCONFIRMED));
      }
    }
    var actual = engine.activeAlerts();
    assertEquals(72, actual.size());
    int index = 0;
    for (var condition : Condition.values()) {
      for (var service : Service.values()) {
        assertEquals(condition, actual.get(index).condition());
        assertEquals(service, actual.get(index).service());
        assertEquals(BigInteger.ONE, actual.get(index).count());
        index++;
      }
    }
    assertThrows(UnsupportedOperationException.class, actual::clear);
  }

  @Test
  void monPipe008MissingObservationResetsOnlyItsConditionAndService() {
    var engine = new MonitoringPolicyEngine();
    var initial = context(0, CauseClearance.UNCONFIRMED);
    engine.filesystem(Service.WEB, 80, FIVE, ZERO, initial);
    engine.filesystem(Service.API, 80, FIVE, ZERO, initial);
    engine.transfer(Service.WEB, 3_500_000_000L, 0, initial);

    var firstNormal = context(1, CauseClearance.UNCONFIRMED);
    engine.filesystem(Service.WEB, 0, ZERO, ZERO, firstNormal);
    engine.filesystem(Service.API, 0, ZERO, ZERO, firstNormal);
    engine.transfer(Service.WEB, 0, 0, firstNormal);
    engine.observationMissing(Condition.FILESYSTEM, Service.WEB, Duration.ofSeconds(150));

    var peerDeadline = context(301, CauseClearance.UNCONFIRMED);
    var api = engine.filesystem(Service.API, 0, ZERO, ZERO, peerDeadline).orElseThrow();
    var transfer = engine.transfer(Service.WEB, 0, 0, peerDeadline).orElseThrow();
    var web = engine.filesystem(Service.WEB, 0, ZERO, ZERO, peerDeadline).orElseThrow();
    assertFalse(api.isOpen());
    assertFalse(transfer.isOpen());
    assertTrue(web.isOpen());
    assertEquals(List.of(web), engine.activeAlerts());
    assertEquals(BigInteger.ONE, web.count());

    assertTrue(
        engine
            .filesystem(Service.WEB, 0, ZERO, ZERO, context(600, CauseClearance.UNCONFIRMED))
            .orElseThrow()
            .isOpen());
    assertFalse(
        engine
            .filesystem(Service.WEB, 0, ZERO, ZERO, context(601, CauseClearance.UNCONFIRMED))
            .orElseThrow()
            .isOpen());
    assertTrue(engine.activeAlerts().isEmpty());
  }
}
