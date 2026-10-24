package dev.codex.schubert.nk.batch.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import java.util.Objects;
import java.util.function.Predicate;

/**
 * NK-OPS-001/RD171/UI252/SS351/1795 BATCHSTD: role-local standard SDK composition, not an endpoint.
 */
public final class BatchStandardMetrics {
  public BatchStandardMetrics() {}

  /** Caller owns the borrowed registry and acknowledged GC handle, also after partial failure. */
  public void bind(MeterRegistry source, String mode, Predicate<? super JvmGcMetrics> owner) {
    install(
        source,
        mode,
        owner,
        () -> new BatchJvmMetrics().bind(source, mode),
        () -> new BatchSystemMetrics().bind(source, mode),
        () -> new BatchGcMetricRegistration().bind(source, mode, owner));
  }

  // Fixed public composition above; recording ports below are an internal deterministic PT seam.
  static void install(
      MeterRegistry source,
      String mode,
      Predicate<? super JvmGcMetrics> owner,
      Runnable jvm,
      Runnable system,
      Runnable gc) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(owner, "GC resource owner");
    Objects.requireNonNull(jvm, "JVM registration");
    Objects.requireNonNull(system, "system registration");
    Objects.requireNonNull(gc, "GC registration");
    boolean detailed = MonitoringModePolicy.parse(mode).detailedMetricsEnabled();
    if (!detailed) return;
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    jvm.run();
    system.run();
    gc.run();
  }
}
