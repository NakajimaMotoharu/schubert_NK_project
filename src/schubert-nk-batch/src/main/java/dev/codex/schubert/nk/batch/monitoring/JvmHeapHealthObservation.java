package dev.codex.schubert.nk.batch.monitoring;

import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.util.Objects;
import java.util.OptionalDouble;
import java.util.function.Supplier;

/**
 * Borrowed heap-read capability only, never GC/control/dump or an exporter replacement.
 * NK-OPS-001/P018-09; RD171/UI252/SS351; PG-D531/HEAPINPUT001..009/spec1591.
 */
public final class JvmHeapHealthObservation {
  private final Supplier<MemoryUsage> heapUsage;
  private final HealthUsageRatio ratio = new HealthUsageRatio();

  private JvmHeapHealthObservation(Supplier<MemoryUsage> heapUsage) {
    this.heapUsage = heapUsage;
  }

  /** The outer owner proves a local provider and lifetime; binding performs no bean operation. */
  public static JvmHeapHealthObservation from(MemoryMXBean bean) {
    Objects.requireNonNull(bean, "heap observation source");
    return new JvmHeapHealthObservation(bean::getHeapMemoryUsage);
  }

  /** Unknown max (-1/0) is UNKNOWN, not an invented committed-capacity denominator or zero. */
  public OptionalDouble read() {
    var usage = Objects.requireNonNull(heapUsage.get(), "heap usage");
    return ratio.fromUsed(usage.getUsed(), usage.getMax());
  }
}
