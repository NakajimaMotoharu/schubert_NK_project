package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import io.micrometer.core.instrument.binder.MeterBinder;
import io.micrometer.core.instrument.binder.jvm.ClassLoaderMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmMemoryMetrics;
import io.micrometer.core.instrument.binder.jvm.JvmThreadMetrics;
import io.micrometer.core.instrument.binder.system.UptimeMetrics;
import java.util.List;
import java.util.Objects;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS351/1781 WEBJVM: four standard non-closeable binders, no GC listener,
 * registry lifetime, target process access or endpoint ownership.
 */
public final class WebJvmMetrics {
  private static final int BINDER_COUNT = 4;

  public WebJvmMetrics() {}

  /** The caller owns the borrowed registry, including partial registration after a binder fails. */
  public void bind(MeterRegistry source, String mode) {
    install(source, mode, WebJvmMetrics::defaults);
  }

  // Exact non-resource port seam; public factory is fixed, no externally selected binder classes.
  static void install(MeterRegistry source, String mode, Supplier<List<MeterBinder>> factory) {
    Objects.requireNonNull(source, "meter registry");
    Objects.requireNonNull(factory, "JVM binder factory");
    boolean detailed = new HttpMetricContract().detailedMetricsEnabled(mode);
    if (!detailed) return;
    if (source.isClosed()) throw new IllegalStateException("metric registry closed");
    var binders = List.copyOf(Objects.requireNonNull(factory.get(), "JVM binders"));
    if (binders.size() != BINDER_COUNT)
      throw new IllegalArgumentException("invalid JVM binder count");
    for (var binder : binders) binder.bindTo(source);
  }

  private static List<MeterBinder> defaults() {
    var tags = Tags.of("service", "WEB");
    return List.of(
        new ClassLoaderMetrics(tags),
        new JvmMemoryMetrics(tags),
        new JvmThreadMetrics(tags),
        new UptimeMetrics(tags));
  }
}
