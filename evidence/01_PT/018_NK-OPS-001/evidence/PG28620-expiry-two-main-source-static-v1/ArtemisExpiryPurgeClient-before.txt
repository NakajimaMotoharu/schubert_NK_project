package dev.codex.schubert.nk.batch.mq;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Selected Expiry purge against one borrowed maintenance-role session. The parent must first prove
 * broker/queue health, own the fixed run/cutoff, durably commit the observation in batch_runs
 * before calling purgeObserved, and decide WARNING/FAILED startup policy. Never pass a
 * caller-supplied selector or touch the DLQ. NK-OPS-001; RD MQ-009/OPS-009; UI251; SS321 §12/341
 * §9; SSC-076/078/BUG-236/238/239/YKT-187/189; PG244/247/248/PT-OPS-MQ-023..028.
 */
@NullMarked
public final class ArtemisExpiryPurgeClient {
  interface Operations {
    long count(ClientSession session);

    long bytes(ClientSession session);

    long selected(ClientSession session, String selector);

    long remove(ClientSession session, String selector);
  }

  public record Observation(
      long cutoffEpochMillis,
      long beforeCount,
      long selectedCount,
      long beforeBytes,
      long estimatedSelectedBytes) {}

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

  public Observation observe(ClientSession session, BatchRun run) {
    Objects.requireNonNull(session, "maintenance session");
    Objects.requireNonNull(run, "fixed run");
    try {
      long cutoff = selectorCutoff(run);
      long beforeCount = nonnegative(operations.count(session));
      long beforeBytes = nonnegative(operations.bytes(session));
      long selected = nonnegative(operations.selected(session, selector(cutoff)));
      if (selected > beforeCount) throw new ArtemisExpiryPurgeException();
      long estimated = beforeCount == 0 ? 0 : product(beforeBytes, selected) / beforeCount;
      return new Observation(cutoff, beforeCount, selected, beforeBytes, estimated);
    } catch (ArtemisManagementReadinessException declaredProvider) {
      throw new ArtemisExpiryPurgeException();
    }
  }

  public Result purgeObserved(ClientSession session, BatchRun run, Observation observation) {
    Objects.requireNonNull(session, "maintenance session");
    Objects.requireNonNull(run, "fixed run");
    Objects.requireNonNull(observation, "durably staged observation");
    try {
      long cutoff = selectorCutoff(run);
      if (observation.cutoffEpochMillis() != cutoff
          || observation.beforeCount() < 0
          || observation.beforeBytes() < 0
          || observation.selectedCount() < 0
          || observation.selectedCount() > observation.beforeCount()
          || observation.estimatedSelectedBytes() < 0
          || observation.estimatedSelectedBytes() > observation.beforeBytes())
        throw new ArtemisExpiryPurgeException();
      long expectedEstimate =
          observation.beforeCount() == 0
              ? 0
              : product(observation.beforeBytes(), observation.selectedCount())
                  / observation.beforeCount();
      if (observation.estimatedSelectedBytes() != expectedEstimate
          || nonnegative(operations.count(session)) != observation.beforeCount()
          || nonnegative(operations.bytes(session)) != observation.beforeBytes()
          || nonnegative(operations.selected(session, selector(cutoff)))
              != observation.selectedCount()) throw new ArtemisExpiryPurgeException();
      long removed =
          observation.selectedCount() == 0
              ? 0
              : nonnegative(operations.remove(session, selector(cutoff)));
      long afterCount = nonnegative(operations.count(session));
      long afterBytes = nonnegative(operations.bytes(session));
      if (removed != observation.selectedCount()
          || afterCount != observation.beforeCount() - removed
          || afterBytes > observation.beforeBytes()) throw new ArtemisExpiryPurgeException();
      return new Result(
          cutoff,
          observation.beforeCount(),
          observation.selectedCount(),
          removed,
          afterCount,
          observation.beforeBytes(),
          observation.estimatedSelectedBytes(),
          observation.beforeBytes() - afterBytes,
          afterBytes);
    } catch (ArtemisManagementReadinessException declaredProvider) {
      throw new ArtemisExpiryPurgeException();
    }
  }

  private static long product(long left, long right) {
    try {
      return Math.multiplyExact(left, right);
    } catch (ArithmeticException overflow) {
      throw new ArtemisExpiryPurgeException();
    }
  }

  private static String selector(long cutoff) {
    return "_AMQ_ACTUAL_EXPIRY < " + cutoff;
  }

  private static long selectorCutoff(BatchRun run) {
    var exact = run.cutoff().minus(7, ChronoUnit.DAYS);
    long floor = exact.toEpochMilli();
    // Integer broker timestamp t < microsecond cutoff iff t < ceil(cutoff in milliseconds).
    return exact.getNano() % 1_000_000 == 0 ? floor : Math.addExact(floor, 1);
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
