package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Selected Expiry purge against one borrowed maintenance-role session. The parent must first prove
 * broker/queue health, own the fixed run/cutoff, record before/after counters in batch_runs, and
 * decide WARNING/FAILED startup policy. Never pass a caller-supplied selector or touch the DLQ.
 * NK-OPS-001; RD MQ-009/OPS-009; UI251; SS321 §12/341 §9; SSC-076/BUG-236/YKT-187;
 * PG244/PT-OPS-MQ-023..026.
 */
@NullMarked
public final class ArtemisExpiryPurgeClient {
  interface Operations {
    long count(ClientSession session);

    long bytes(ClientSession session);

    long selected(ClientSession session, String selector);

    long remove(ClientSession session, String selector);
  }

  public record Result(
      long cutoffEpochMillis,
      long beforeCount,
      long selectedCount,
      long removedCount,
      long afterCount,
      long beforeBytes,
      long estimatedSelectedBytes,
      long removedBytes,
      long afterBytes) {}

  private final Operations operations;

  public ArtemisExpiryPurgeClient() {
    this(new ManagementOperations());
  }

  ArtemisExpiryPurgeClient(Operations operations) {
    this.operations = Objects.requireNonNull(operations, "expiry operations");
  }

  public Result purge(ClientSession session, BatchRun run) {
    Objects.requireNonNull(session, "maintenance session");
    Objects.requireNonNull(run, "fixed run");
    try {
      long cutoff = run.cutoff().minus(7, ChronoUnit.DAYS).toEpochMilli();
      String selector = "_AMQ_ACTUAL_EXPIRY < " + cutoff;
      long beforeCount = nonnegative(operations.count(session));
      long beforeBytes = nonnegative(operations.bytes(session));
      long selected = nonnegative(operations.selected(session, selector));
      if (selected > beforeCount) throw new ArtemisExpiryPurgeException();
      long estimated =
          beforeCount == 0 ? 0 : Math.multiplyExact(beforeBytes, selected) / beforeCount;
      long removed = selected == 0 ? 0 : nonnegative(operations.remove(session, selector));
      long afterCount = nonnegative(operations.count(session));
      long afterBytes = nonnegative(operations.bytes(session));
      if (removed != selected || afterCount != beforeCount - removed || afterBytes > beforeBytes)
        throw new ArtemisExpiryPurgeException();
      return new Result(
          cutoff,
          beforeCount,
          selected,
          removed,
          afterCount,
          beforeBytes,
          estimated,
          beforeBytes - afterBytes,
          afterBytes);
    } catch (RuntimeException failure) {
      throw new ArtemisExpiryPurgeException();
    }
  }

  private static long nonnegative(long value) {
    if (value < 0) throw new ArtemisExpiryPurgeException();
    return value;
  }

  static long integer(@Nullable Object value) {
    if (value instanceof Integer number) return number.longValue();
    if (value instanceof Long number) return number;
    throw new ArtemisExpiryPurgeException();
  }

  private static final class ManagementOperations implements Operations {
    @Override
    public long count(ClientSession session) {
      return integer(
          ArtemisManagementReadinessClient.queueMetric(session, "nk.expiry.q", "messageCount"));
    }

    @Override
    public long bytes(ClientSession session) {
      return integer(
          ArtemisManagementReadinessClient.queueMetric(session, "nk.expiry.q", "persistentSize"));
    }

    @Override
    public long selected(ClientSession session, String selector) {
      return integer(
          ArtemisManagementReadinessClient.expiryOperation(session, "countMessages", selector));
    }

    @Override
    public long remove(ClientSession session, String selector) {
      return integer(
          ArtemisManagementReadinessClient.expiryOperation(session, "removeMessages", selector));
    }
  }
}
