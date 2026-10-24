package dev.codex.schubert.nk.batch.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import java.util.Objects;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS351/1787 BATCHGC: retain the fresh standard GC handle before activation.
 * Caller owns the acknowledged handle and its close, including after partial bind failure.
 */
public final class BatchGcMetricRegistration {
  public BatchGcMetricRegistration() {}

  /**
   * Dedicated GC namespace, one registration per caller-owned lifecycle; never an automatic retry.
   */
  public void bind(MeterRegistry source, String mode, Predicate<? super JvmGcMetrics> owner) {
    install(source, mode, owner, BatchGcMetricRegistration::candidate);
  }

  // Internal fresh-unbound SDK factory seam; not a user-selected implementation or target.
  static void install(
      MeterRegistry source,
      String mode,
      Predicate<? super JvmGcMetrics> owner,
      Supplier<JvmGcMetrics> factory) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(owner, "GC resource owner");
    Objects.requireNonNull(factory, "GC factory");
    boolean detailed = MonitoringModePolicy.parse(mode).detailedMetricsEnabled();
    if (!detailed) return;
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    activateOwned(source, Objects.requireNonNull(factory.get(), "fresh GC resource"), owner);
  }

  // Borrowed candidate: owner acknowledges retention before SDK activation; owner alone closes it.
  private static void activateOwned(
      MeterRegistry source, JvmGcMetrics resource, Predicate<? super JvmGcMetrics> owner) {
    if (!owner.test(resource)) throw new IllegalStateException("GC binding owner unavailable");
    resource.bindTo(source);
  }

  private static JvmGcMetrics candidate() {
    return new JvmGcMetrics(Tags.of("service", "BATCH"));
  }
}
