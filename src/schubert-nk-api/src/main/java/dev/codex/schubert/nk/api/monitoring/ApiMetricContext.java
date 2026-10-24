package dev.codex.schubert.nk.api.monitoring;

import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS311342351/1815/PG-D617: caller-held SDK context, not an endpoint, health
 * authority or observation-completeness certificate. Setup retains borrowed non-resource bindings
 * only; it must not acquire DB/JMS/workers or invoke this owner's lifecycle.
 */
public final class ApiMetricContext<T> implements AutoCloseable {
  private static final String INITIALIZATION_UNAVAILABLE = "metric initialization unavailable";
  private static final String CLOSE_UNCONFIRMED = "metric context close unconfirmed";
  private final ReentrantLock lock = new ReentrantLock();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final String mode;
  private final boolean detailed;
  private final Function<? super MeterRegistry, ? extends T> setup;
  private final Optional<Consumer<? super T>> refresh;
  private final Supplier<? extends MeterRegistry> customFactory;
  private final ApiStandardMetricSource standard;
  private Optional<MeterRegistry> ownedCustom = Optional.empty();
  private Optional<T> retainedBindings = Optional.empty();
  private boolean attempted;
  private boolean initialized;
  private boolean closed;

  /** Resource-free: the caller must retain this owner before invoking initialize. */
  public ApiMetricContext(String mode, Function<? super MeterRegistry, ? extends T> setup) {
    this(
        mode,
        setup,
        () ->
            new ExactDurationMeterRegistry(
                io.micrometer.core.instrument.simple.SimpleConfig.DEFAULT,
                io.micrometer.core.instrument.Clock.SYSTEM),
        new ApiStandardMetricSource());
  }

  /**
   * 1823/PG-D620: samples pre-owned non-resource metadata before DEBUG output, under this owner.
   * The sampler must not acquire connections/workers, perform I/O, or reenter this context.
   */
  public ApiMetricContext(
      String mode,
      Function<? super MeterRegistry, ? extends T> setup,
      Consumer<? super T> refresh) {
    this(
        mode,
        setup,
        refresh,
        () ->
            new ExactDurationMeterRegistry(
                io.micrometer.core.instrument.simple.SimpleConfig.DEFAULT,
                io.micrometer.core.instrument.Clock.SYSTEM),
        new ApiStandardMetricSource());
  }

  // Fixed production factories above; fresh unbound standard/test ports transfer SDK ownership.
  ApiMetricContext(
      String mode,
      Function<? super MeterRegistry, ? extends T> setup,
      Supplier<? extends MeterRegistry> customFactory,
      ApiStandardMetricSource standard) {
    this(mode, setup, Optional.empty(), customFactory, standard);
  }

  ApiMetricContext(
      String mode,
      Function<? super MeterRegistry, ? extends T> setup,
      Consumer<? super T> refresh,
      Supplier<? extends MeterRegistry> customFactory,
      ApiStandardMetricSource standard) {
    this(
        mode,
        setup,
        Optional.<Consumer<? super T>>of(
            Objects.requireNonNull(refresh, "metric metadata refresh")),
        customFactory,
        standard);
  }

  private ApiMetricContext(
      String mode,
      Function<? super MeterRegistry, ? extends T> setup,
      Optional<Consumer<? super T>> refresh,
      Supplier<? extends MeterRegistry> customFactory,
      ApiStandardMetricSource standard) {
    this.mode = Objects.requireNonNull(mode, "monitoring mode");
    this.detailed =
        switch (this.mode) {
          case "DEBUG" -> true;
          case "STANDARD" -> false;
          default -> throw new IllegalArgumentException("CONFIG_INVALID");
        };
    this.setup = Objects.requireNonNull(setup, "metric binding registration");
    this.refresh = Objects.requireNonNull(refresh, "metric refresh holder");
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
      if (detailed && refresh.isPresent()) {
        refresh.orElseThrow().accept(retainedBindings.orElseThrow());
        rejectStopping();
      }
      var borrowed = ownedCustom;
      return new ApiCustomMetricPayload().render(ready, mode, borrowed::orElseThrow, standard);
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
