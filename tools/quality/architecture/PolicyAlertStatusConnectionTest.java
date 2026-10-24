package dev.codex.schubert.nk.batch.monitoring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.CauseClearance;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.Test;

/** SS351/1806: new pure threshold->registry->status connection, no scheduler or I/O. */
final class PolicyAlertStatusConnectionTest {
  private static final Instant AT = Instant.parse("2026-10-24T00:00:00Z");
  private static final String HEADER =
      "# SUPPLIED_MONITORING_STATE_V1 MODE=STANDARD\ncondition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n";
  private static final String TRANSFER =
      "TRANSFER\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n";

  @Test
  void alertpipe001AllTwelveThresholdsReachFixedCanonicalStatus() {
    var engine = new MonitoringPolicyEngine();
    var now = context(Duration.ZERO, CauseClearance.UNCONFIRMED);
    engine.integrity(Service.BATCH, 1, now);
    engine.restarts(Service.BATCH, 1, false, now);
    engine.backup(Service.BATCH, true, false, 0, now);
    engine.syncP95(Service.BATCH, 2.1, Duration.ofMinutes(5), Duration.ZERO, now);
    engine.jvmHeap(Service.BATCH, 75, Duration.ofMinutes(10), false, now);
    engine.dbPool(Service.BATCH, 80, Duration.ofMinutes(5), 0, 0, now);
    engine.expiry(Service.BATCH, 1000, now);
    engine.dlq(Service.BATCH, 1, false, false, now);
    engine.webLog(Service.BATCH, 5000, Duration.ZERO, now);
    engine.asyncQueue(Service.BATCH, 5000, 0, 10000, now);
    engine.transfer(Service.BATCH, 3500000000L, 0, now);
    engine.filesystem(Service.BATCH, 80, Duration.ofMinutes(5), Duration.ZERO, now);
    String expected =
        HEADER
            + "FILESYSTEM\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + TRANSFER
            + "ASYNC_QUEUE\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "WEB_LOG\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "DLQ\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "EXPIRY\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "DB_POOL\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "JVM_HEAP\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "SYNC_P95\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "BACKUP\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "RESTART\tBATCH\tWARNING\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "INTEGRITY_CONFIG\tBATCH\tCRITICAL\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n";
    assertEquals(expected, render(engine));
    assertEquals(12, engine.activeAlerts().size());
    assertFalse(render(engine).contains("SUPPLIED_MONITORING_STATE_V1 MODE=DEBUG"));
  }

  @Test
  void alertpipe002WarningCountAndFiveMinuteRecoveryReachStatus() {
    var engine = new MonitoringPolicyEngine();
    engine.transfer(
        Service.BATCH, 3500000000L, 0, context(Duration.ZERO, CauseClearance.UNCONFIRMED));
    engine.transfer(
        Service.BATCH, 0, 5000, context(Duration.ofMinutes(1), CauseClearance.UNCONFIRMED));
    String expected =
        HEADER
            + "TRANSFER\tBATCH\tWARNING\t2\t2026-10-24T00:00:00.000Z\t2026-10-24T00:01:00.000Z\n";
    engine.transfer(
        Service.BATCH, 0, 0, context(Duration.ofMinutes(2), CauseClearance.UNCONFIRMED));
    engine.transfer(
        Service.BATCH,
        0,
        0,
        context(Duration.ofMinutes(7).minusNanos(1), CauseClearance.UNCONFIRMED));
    assertEquals(expected, render(engine));
    assertFalse(
        engine
            .transfer(
                Service.BATCH, 0, 0, context(Duration.ofMinutes(7), CauseClearance.UNCONFIRMED))
            .orElseThrow()
            .isOpen());
    assertEquals(HEADER, render(engine));
  }

  @Test
  void alertpipe003CriticalRequiresCauseAndInvestigationsStayOpen() {
    var engine = new MonitoringPolicyEngine();
    engine.transfer(
        Service.BATCH, 4500000000L, 0, context(Duration.ZERO, CauseClearance.UNCONFIRMED));
    engine.transfer(
        Service.BATCH, 0, 0, context(Duration.ofMinutes(1), CauseClearance.UNCONFIRMED));
    engine.transfer(
        Service.BATCH, 0, 0, context(Duration.ofMinutes(11), CauseClearance.UNCONFIRMED));
    assertEquals(
        HEADER
            + "TRANSFER\tBATCH\tCRITICAL\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n",
        render(engine));
    engine.transfer(Service.BATCH, 0, 0, context(Duration.ofMinutes(11), CauseClearance.CONFIRMED));
    assertEquals(HEADER, render(engine));
    engine.dlq(Service.BATCH, 1, true, true, context(Duration.ZERO, CauseClearance.UNCONFIRMED));
    engine.integrity(Service.BATCH, 1, context(Duration.ZERO, CauseClearance.UNCONFIRMED));
    engine.dlq(
        Service.BATCH, 0, false, false, context(Duration.ofMinutes(30), CauseClearance.CONFIRMED));
    engine.integrity(Service.BATCH, 0, context(Duration.ofMinutes(30), CauseClearance.CONFIRMED));
    assertEquals(
        HEADER
            + "DLQ\tBATCH\tCRITICAL\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n"
            + "INTEGRITY_CONFIG\tBATCH\tCRITICAL\t1\t2026-10-24T00:00:00.000Z\t2026-10-24T00:00:00.000Z\n",
        render(engine));
  }

  @Test
  void alertpipe004MissingBreaksRecoveryAndUtcCannotAccelerateClosure() {
    var engine = new MonitoringPolicyEngine();
    engine.transfer(
        Service.BATCH, 3500000000L, 0, context(Duration.ZERO, CauseClearance.UNCONFIRMED));
    engine.transfer(
        Service.BATCH, 0, 0, context(Duration.ofMinutes(1), CauseClearance.UNCONFIRMED));
    engine.observationMissing(Condition.TRANSFER, Service.BATCH, Duration.ofMinutes(5));
    assertEquals(HEADER + TRANSFER, render(engine));
    engine.transfer(
        Service.BATCH,
        0,
        0,
        new ObservationContext(
            CauseClearance.UNCONFIRMED, AT.plusSeconds(999999), Duration.ofMinutes(6)));
    engine.transfer(
        Service.BATCH,
        0,
        0,
        new ObservationContext(
            CauseClearance.UNCONFIRMED,
            AT.minusSeconds(999999),
            Duration.ofMinutes(11).minusNanos(1)));
    assertEquals(HEADER + TRANSFER, render(engine));
    engine.transfer(
        Service.BATCH,
        0,
        0,
        new ObservationContext(
            CauseClearance.UNCONFIRMED, AT.minusSeconds(999999), Duration.ofMinutes(11)));
    assertTrue(engine.activeAlerts().isEmpty());
    assertEquals(HEADER, render(engine));
  }

  private static ObservationContext context(Duration elapsed, CauseClearance cause) {
    return new ObservationContext(cause, AT.plus(elapsed), elapsed);
  }

  private static String render(MonitoringPolicyEngine engine) {
    return new MonitoringStatusText().render(MonitoringModePolicy.STANDARD, engine.activeAlerts());
  }
}
