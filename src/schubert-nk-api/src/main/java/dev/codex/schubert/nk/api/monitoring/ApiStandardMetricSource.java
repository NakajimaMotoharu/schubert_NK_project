package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.binder.jvm.JvmGcMetrics;
import io.micrometer.prometheusmetrics.PrometheusConfig;
import io.micrometer.prometheusmetrics.PrometheusMeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.function.BiConsumer;
import java.util.function.Predicate;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS351/1808/PG-D614: caller-held standard SDK text owner. No public
 * registry access, endpoint, scheduler, health authority or implicit rollback/retry.
 */
public final class ApiStandardMetricSource implements AutoCloseable {
  private final Object lock = new Object();
  private final Supplier<? extends PrometheusMeterRegistry> factory;
  private final BiConsumer<PrometheusMeterRegistry, Predicate<? super JvmGcMetrics>> registration;
  private Optional<PrometheusMeterRegistry> ownedRegistry = Optional.empty();
  private Optional<JvmGcMetrics> ownedGc = Optional.empty();
  private boolean attempted;
  private boolean bound;
  private boolean closed;

  /** No SDK acquisition: the caller receives and retains this owner before bind can acquire. */
  public ApiStandardMetricSource() {
    this(
        () -> new PrometheusMeterRegistry(PrometheusConfig.DEFAULT),
        (source, owner) -> new ApiStandardMetrics().bind(source, "DEBUG", owner));
  }

  // Fixed production factory above; package-local deterministic ownership/failure ports for PT.
  ApiStandardMetricSource(
      Supplier<? extends PrometheusMeterRegistry> factory,
      BiConsumer<PrometheusMeterRegistry, Predicate<? super JvmGcMetrics>> registration) {
    this.factory = Objects.requireNonNull(factory, "standard metric factory");
    this.registration = Objects.requireNonNull(registration, "standard metric registration");
  }

  /** Single explicit initialization. Partial resources remain held after any failure. */
  public void bind(String mode) {
    synchronized (lock) {
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
    }
  }

  /**
   * Only the fixed SDK binders can register; no supplied IDs/tags/text or mutable registry getter.
   */
  public String scrape(String mode) {
    synchronized (lock) {
      if (!detailed(mode)) return "";
      if (closed || !bound) throw new IllegalStateException("standard metric source unavailable");
      return ownedRegistry.orElseThrow().scrape();
    }
  }

  private static boolean detailed(String mode) {
    return switch (Objects.requireNonNull(mode, "monitoring mode")) {
      case "DEBUG" -> true;
      case "STANDARD" -> false;
      default -> throw new IllegalArgumentException("CONFIG_INVALID");
    };
  }

  /** Explicit caller close: GC before registry; failed close keeps ownership and is not success. */
  @Override
  public void close() {
    synchronized (lock) {
      if (closed) return;
      bound = false;
      ownedGc.ifPresent(JvmGcMetrics::close);
      ownedRegistry.ifPresent(PrometheusMeterRegistry::close);
      closed = true;
    }
  }
}
