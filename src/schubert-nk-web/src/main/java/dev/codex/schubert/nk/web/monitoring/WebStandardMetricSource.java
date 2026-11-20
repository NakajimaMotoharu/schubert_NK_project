package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.BiConsumer;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS351/1810/PG-D615: caller-held standard SDK text owner. No public
 * registry access, endpoint, scheduler, health authority or implicit rollback/retry.
 */
public final class WebStandardMetricSource implements AutoCloseable {
  private final ReentrantLock lock = new ReentrantLock();
  private final Supplier<? extends PrometheusMeterRegistry> factory;
  private final BiConsumer<PrometheusMeterRegistry, Predicate<? super JvmGcMetrics>> registration;
  private Optional<PrometheusMeterRegistry> ownedRegistry = Optional.empty();
  private Optional<JvmGcMetrics> ownedGc = Optional.empty();
  private boolean attempted;
  private boolean bound;
  private boolean closed;

  /** No SDK acquisition: the caller receives and retains this owner before bind can acquire. */
  public WebStandardMetricSource() {
    this(
        () -> new PrometheusMeterRegistry(PrometheusConfig.DEFAULT),
        (source, owner) -> new WebStandardMetrics().bind(source, "DEBUG", owner));
  }

  // Fixed production factory above; package-local deterministic ownership/failure ports for PT.
  WebStandardMetricSource(
      Supplier<? extends PrometheusMeterRegistry> factory,
      BiConsumer<PrometheusMeterRegistry, Predicate<? super JvmGcMetrics>> registration) {
    this.factory = Objects.requireNonNull(factory, "standard metric factory");
    this.registration = Objects.requireNonNull(registration, "standard metric registration");
  }

  /** Single explicit initialization. Partial resources remain held after any failure. */
  public void bind(String mode) {
    lock.lock();
    try {
      if (!detailed(mode)) return;
      if (closed || attempted)
        throw new IllegalStateException("standard metric binding unavailable");
      attempted = true;
      ownedRegistry =
          Optional.of(Objects.requireNonNull(factory.get(), "standard metric registry"));
      var source = ownedRegistry.orElseThrow();
      if (source.isClosed()) throw new IllegalStateException("standard metric registry closed");
      registration.accept(
          source,
          resource -> {
            ownedGc = Optional.of(Objects.requireNonNull(resource, "standard GC resource"));
            return true;
          });
      bound = true;
    } finally {
      lock.unlock();
    }
  }

  /**
   * Only the fixed SDK binders can register; no supplied IDs/tags/text or mutable registry getter.
   */
  public String scrape(String mode) {
    lock.lock();
    try {
      if (!detailed(mode)) return "";
      if (closed || !bound) throw new IllegalStateException("standard metric source unavailable");
      return ownedRegistry.orElseThrow().scrape();
    } finally {
      lock.unlock();
    }
  }

  private static boolean detailed(String mode) {
    return new HttpMetricContract().detailedMetricsEnabled(mode);
  }

  /** Explicit caller close: GC before registry; failed close keeps ownership and is not success. */
  @Override
  public void close() {
    lock.lock();
    try {
      if (closed) return;
      bound = false;
      ownedGc.ifPresent(JvmGcMetrics::close);
      ownedGc = Optional.empty();
      ownedRegistry.ifPresent(PrometheusMeterRegistry::close);
      ownedRegistry = Optional.empty();
      closed = true;
    } finally {
      lock.unlock();
    }
  }
}
