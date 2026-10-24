package dev.codex.schubert.nk.web.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Function;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS311342351/1815/PG-D617: caller-held SDK context, not an endpoint, health
 * authority or observation-completeness certificate. Setup retains borrowed non-resource bindings
 * only; it must not acquire DB/JMS/workers or invoke this owner's lifecycle.
 */
public final class WebMetricContext<T> implements AutoCloseable {
  private static final String INITIALIZATION_UNAVAILABLE = "metric initialization unavailable";
  private static final String CLOSE_UNCONFIRMED = "metric context close unconfirmed";
  private final ReentrantLock lock = new ReentrantLock();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final String mode;
  private final boolean detailed;
  private final Function<? super MeterRegistry, ? extends T> setup;
  private final Supplier<? extends MeterRegistry> customFactory;
  private final WebStandardMetricSource standard;
  private Optional<MeterRegistry> ownedCustom = Optional.empty();
  private Optional<T> retainedBindings = Optional.empty();
  private boolean attempted;
  private boolean initialized;
  private boolean closed;

  /** Resource-free: the caller must retain this owner before invoking initialize. */
  public WebMetricContext(String mode, Function<? super MeterRegistry, ? extends T> setup) {
    this(
        mode,
        setup,
        () -> new OverflowSafeHttpMeterRegistry(io.micrometer.core.instrument.Clock.SYSTEM),
        new WebStandardMetricSource());
  }

  // Fixed production factories above; fresh unbound standard/test ports transfer SDK ownership.
  WebMetricContext(
      String mode,
      Function<? super MeterRegistry, ? extends T> setup,
      Supplier<? extends MeterRegistry> customFactory,
      WebStandardMetricSource standard) {
    this.mode = Objects.requireNonNull(mode, "monitoring mode");
    this.detailed = new HttpMetricContract().detailedMetricsEnabled(this.mode);
    this.setup = Objects.requireNonNull(setup, "metric binding registration");
    this.customFactory = Objects.requireNonNull(customFactory, "custom metric factory");
    this.standard = Objects.requireNonNull(standard, "standard metric owner");
  }

  /** Single initialization; partial SDK state stays owned after failure or a concurrent stop. */
  public void initialize() {
    lock.lock();
    try {
      if (stopping.get() || attempted) throw new IllegalStateException(INITIALIZATION_UNAVAILABLE);
      attempted = true;
      if (!detailed) {
        initialized = true;
        return;
      }
      ownedCustom =
          Optional.of(Objects.requireNonNull(customFactory.get(), "custom metric registry"));
      var source = ownedCustom.orElseThrow();
      if (source.isClosed()) throw new IllegalStateException("custom metric registry closed");
      rejectStopping();
      retainedBindings =
          Optional.of(Objects.requireNonNull(setup.apply(source), "metric bindings"));
      rejectStopping();
      standard.bind(mode);
      rejectStopping();
      initialized = true;
    } finally {
      lock.unlock();
    }
  }

  /**
   * Strong metadata retention is not ownership of a caller's database, broker or other resource.
   */
  public Optional<T> bindings() {
    lock.lock();
    try {
      requireRunning();
      return retainedBindings;
    } finally {
      lock.unlock();
    }
  }

  /** Same-owner render/close serialization; no source acquisition, fallback or automatic retry. */
  public String render(boolean ready) {
    lock.lock();
    try {
      requireRunning();
      var borrowed = ownedCustom;
      return new WebCustomMetricPayload().render(ready, mode, borrowed::orElseThrow, standard);
    } finally {
      lock.unlock();
    }
  }

  private void rejectStopping() {
    if (stopping.get()) throw new IllegalStateException(INITIALIZATION_UNAVAILABLE);
  }

  private void requireRunning() {
    if (stopping.get() || !initialized)
      throw new IllegalStateException("metric context unavailable");
  }

  /**
   * No wait behind an active callback: request stop, then report contention/reentrancy unconfirmed.
   * The caller retains this owner and may explicitly retry after the active invocation terminates.
   * Standard GC/registry close precedes custom close; failed cleanup never confirms closed.
   */
  @Override
  public void close() {
    stopping.set(true);
    if (lock.isHeldByCurrentThread() || !lock.tryLock())
      throw new IllegalStateException(CLOSE_UNCONFIRMED);
    try {
      if (closed) return;
      initialized = false;
      standard.close();
      ownedCustom.ifPresent(MeterRegistry::close);
      retainedBindings = Optional.empty();
      ownedCustom = Optional.empty();
      closed = true;
    } finally {
      lock.unlock();
    }
  }
}
