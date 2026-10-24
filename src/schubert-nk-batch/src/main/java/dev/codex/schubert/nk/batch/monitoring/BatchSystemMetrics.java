package dev.codex.schubert.nk.batch.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.binder.MeterBinder;
import io.micrometer.core.instrument.binder.system.FileDescriptorMetrics;
import io.micrometer.core.instrument.binder.system.ProcessorMetrics;
import java.util.List;
import java.util.Objects;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS351/1791 BATCHSYS: two standard non-closeable binders, no GC listener,
 * registry lifetime, target process access or endpoint ownership.
 */
public final class BatchSystemMetrics {
  private static final int BINDER_COUNT = 2;

  public BatchSystemMetrics() {}

  /** The caller owns the borrowed registry, including partial registration after a binder fails. */
  public void bind(MeterRegistry source, String mode) {
    install(source, mode, BatchSystemMetrics::defaults);
  }

  // Exact non-resource port seam; public factory is fixed, no externally selected binder classes.
  static void install(MeterRegistry source, String mode, Supplier<List<MeterBinder>> factory) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(factory, "system binder factory");
    boolean detailed = MonitoringModePolicy.parse(mode).detailedMetricsEnabled();
    if (!detailed) return;
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var binders = List.copyOf(Objects.requireNonNull(factory.get(), "system binders"));
    if (binders.size() != BINDER_COUNT)
      throw new IllegalArgumentException("invalid system binder count");
    for (var binder : binders) binder.bindTo(source);
  }

  private static List<MeterBinder> defaults() {
    var tags = Tags.of("service", "BATCH");
    return List.of(new ProcessorMetrics(tags), new FileDescriptorMetrics(tags));
  }
}
