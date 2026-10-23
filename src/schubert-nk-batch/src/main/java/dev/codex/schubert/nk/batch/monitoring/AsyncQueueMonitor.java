package dev.codex.schubert.nk.batch.monitoring;

import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Condition;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Event;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Service;
import dev.codex.schubert.nk.batch.monitoring.AlertLifecycle.Severity;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;

/** Supplied backlog evidence only; no broker/DB/controller. RD171/UI252/SS321/351; 1679/BUG1665. */
public final class AsyncQueueMonitor {
  /** Total storage use and its purpose-specific byte limit, not a message-count capacity. */
  public record ByteUsage(long usedBytes, long capacityBytes) {
    public ByteUsage {
      if (usedBytes < 0 || capacityBytes <= 0)
        throw new IllegalArgumentException("invalid async queue storage bytes");
    }
  }

  public record Evaluation(boolean queuedPresent, boolean byteUsagePresent, Optional<Event> event) {
    public Evaluation {
      Objects.requireNonNull(event, "async queue alert transition");
    }
  }

  private final MonitoringPoller<Evaluation> poller = new MonitoringPoller<>();
  private final AlertThresholds thresholds = new AlertThresholds();
  private final AlertLifecycle lifecycle = new AlertLifecycle(Condition.ASYNC_QUEUE, Service.API);

  /**
   * Known abnormal evidence may raise an alert; partial/unknown evidence can never establish normal
   * recovery. Source identity and coherent count/storage observation remain caller obligations.
   */
  public Evaluation observe(
      OptionalLong queued,
      Optional<ByteUsage> byteUsage,
      boolean consecutive,
      ObservationContext context) {
    Objects.requireNonNull(queued, "supplied async queue count");
    Objects.requireNonNull(byteUsage, "supplied async queue storage bytes");
    // Unknown storage contributes no abnormal evidence, never a fabricated normal recovery sample.
    ByteUsage bytes = byteUsage.orElse(new ByteUsage(0, 1));
    Severity level =
        thresholds.asyncQueue(queued.orElse(0), bytes.usedBytes(), bytes.capacityBytes());
    boolean complete = queued.isPresent() && byteUsage.isPresent();
    return poller.observe(
        consecutive,
        context,
        (continuous, at) -> {
          if (!continuous || !complete) lifecycle.interruptContinuity(at.elapsed());
          Optional<Event> event =
              !complete && level == Severity.NORMAL
                  ? lifecycle.snapshot()
                  : lifecycle.observe(level, at.clearance(), at.at(), at.elapsed());
          return new Evaluation(queued.isPresent(), byteUsage.isPresent(), event);
        });
  }

  public Optional<Event> snapshot() {
    return lifecycle.snapshot();
  }
}
