package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import dev.codex.schubert.nk.batch.monitoring.MonitoringModePolicy.DetailService;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

/**
 * One pure policy-to-alert connection, not runtime health or a service controller.
 * NK-OPS-001/P018-09; MON005..013; UI252; SS351 §7..10; PG-D521/PT-OPS-MONPIPE-001..007.
 */
public final class MonitoringPolicyEngine {
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertRegistry registry = new AlertRegistry();

  public Optional<Event> filesystem(
      Service service,
      double percent,
      Duration above80,
      Duration above90,
      ObservationContext context) {
    return registry.observeWindowed(
        Condition.FILESYSTEM,
        service,
        thresholds.filesystem(percent, above80, above90),
        AlertThresholds.filesystemAboveWarning(percent),
        context);
  }

  public Optional<Event> transfer(
      Service service, long bytes, long files, ObservationContext context) {
    return record(Condition.TRANSFER, service, thresholds.transfer(bytes, files), context);
  }

  public Optional<Event> asyncQueue(
      Service service,
      long queued,
      long usedBytes,
      long capacityBytes,
      ObservationContext context) {
    return record(
        Condition.ASYNC_QUEUE,
        service,
        thresholds.asyncQueue(queued, usedBytes, capacityBytes),
        context);
  }

  public Optional<Event> webLog(
      Service service, long queued, Duration oldest, ObservationContext context) {
    return record(Condition.WEB_LOG, service, thresholds.webLog(queued, oldest), context);
  }

  public Optional<Event> dlq(
      Service service,
      long messages,
      boolean increasing,
      boolean uninvestigated,
      ObservationContext context) {
    return record(
        Condition.DLQ, service, thresholds.dlq(messages, increasing, uninvestigated), context);
  }

  public Optional<Event> expiry(Service service, long messages, ObservationContext context) {
    return record(Condition.EXPIRY, service, thresholds.expiry(messages), context);
  }

  public Optional<Event> dbPool(
      Service service,
      double percent,
      Duration above80,
      long pending,
      long timeouts,
      ObservationContext context) {
    return registry.observeWindowed(
        Condition.DB_POOL,
        service,
        thresholds.dbPool(percent, above80, pending, timeouts),
        AlertThresholds.dbPoolAboveWarning(percent),
        context);
  }

  public Optional<Event> jvmHeap(
      Service service,
      double percent,
      Duration above75,
      boolean outOfMemory,
      ObservationContext context) {
    return registry.observeWindowed(
        Condition.JVM_HEAP,
        service,
        thresholds.jvmHeap(percent, above75, outOfMemory),
        AlertThresholds.heapAboveWarning(percent),
        context);
  }

  public Optional<Event> syncP95(
      Service service,
      double seconds,
      Duration above2,
      Duration above2Point5,
      ObservationContext context) {
    return registry.observeWindowed(
        Condition.SYNC_P95,
        service,
        thresholds.syncP95(seconds, above2, above2Point5),
        AlertThresholds.syncLatencyAboveWarning(seconds),
        context);
  }

  public Optional<Event> backup(
      Service service,
      boolean scheduledRunPassed,
      boolean todaySuccess,
      long consecutiveFailures,
      ObservationContext context) {
    return record(
        Condition.BACKUP,
        service,
        thresholds.backup(scheduledRunPassed, todaySuccess, consecutiveFailures),
        context);
  }

  public Optional<Event> restarts(
      Service service, long lastTenMinutes, boolean rateLimited, ObservationContext context) {
    return record(
        Condition.RESTART, service, thresholds.restarts(lastTenMinutes, rateLimited), context);
  }

  public Optional<Event> integrity(Service service, long failures, ObservationContext context) {
    return record(Condition.INTEGRITY_CONFIG, service, thresholds.integrity(failures), context);
  }

  private Optional<Event> record(
      Condition condition, Service service, Severity severity, ObservationContext context) {
    Objects.requireNonNull(context, "observation context");
    return registry.observe(
        condition, service, severity, context.clearance(), context.at(), context.elapsed());
  }

  /** Validate supplied detail-service observations only; never start/stop or alter alert state. */
  public MonitoringModePolicy verifyMode(String mode, Map<DetailService, Boolean> observed) {
    var policy = MonitoringModePolicy.parse(mode);
    policy.verifyObserved(observed);
    return policy;
  }

  /** Explicit absence, never a synthetic NORMAL severity or cause-clearance observation. */
  public void observationMissing(Condition condition, Service service, Duration elapsed) {
    registry.interruptContinuity(condition, service, elapsed);
  }

  public List<Event> activeAlerts() {
    return registry.activeEvents();
  }
}
