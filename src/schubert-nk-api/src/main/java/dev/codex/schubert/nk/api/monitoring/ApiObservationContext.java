package dev.codex.schubert.nk.api.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.monitoring.persistence.OutboxObservationRepository;
import java.io.IOException;
import java.time.Clock;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Consumer;
import java.util.function.LongSupplier;
import java.util.function.Supplier;
import javax.sql.DataSource;

/**
 * NK-OPS-001/RD171/UI252/SS311332342351/1868/PG-D636: caller-held observation and SDK assembly.
 * Borrowed pool and original remaining stop budget never transfer ownership. Prepare acquires no
 * connection, SDK or running thread; the caller retains this owner before initialize. Manager
 * borrows metrics only. UNKNOWN retains this owner and forbids downstream pool/SDK release.
 */
public final class ApiObservationContext implements AutoCloseable {
  private static final String UNCONFIRMED = "API observation context close unconfirmed";
  private final ReentrantLock lock = new ReentrantLock();
  private final AtomicBoolean stopping = new AtomicBoolean();
  private final AtomicBoolean unconfirmed = new AtomicBoolean();
  private final ApiMetricContext<?> metricContext;
  private final Optional<OwnedApiObservationWorker> worker;
  private final LongSupplier remainingNanos;
  private final Consumer<Throwable> onUnconfirmed;
  private boolean attempted;
  private boolean closed;

  /** Only fixed resource-free owners are constructed; STANDARD creates no observation worker. */
  public static ApiObservationContext prepare(
      String mode,
      DataSource pool,
      Supplier<? extends HikariPoolMXBean> poolBean,
      Supplier<? extends HikariConfigMXBean> configBean,
      Clock clock,
      LongSupplier nanos,
      LongSupplier remainingNanos,
      Consumer<? super Throwable> onFailure,
      Consumer<Throwable> onUnconfirmed) {
    Objects.requireNonNull(pool, "borrowed observation pool");
    Objects.requireNonNull(clock, "observation clock");
    Objects.requireNonNull(nanos, "observation monotonic clock");
    Objects.requireNonNull(remainingNanos, "existing remaining stop budget");
    Objects.requireNonNull(onFailure, "observation failure notification");
    Objects.requireNonNull(onUnconfirmed, "unconfirmed assembly policy");
    var repository = new OutboxObservationRepository();
    var pump =
        ApiOutboxObservationPump.create(
            mode,
            nanos,
            () -> new ApiReadOnlyObservationAttempt(pool, clock, repository, onUnconfirmed),
            repository);
    var metrics = ApiServiceMetricBinding.prepareContext(mode, poolBean, configBean, pump);
    var worker =
        mode.equals("DEBUG")
            ? Optional.of(new OwnedApiObservationWorker(pump, onFailure, nanos))
            : Optional.<OwnedApiObservationWorker>empty();
    return new ApiObservationContext(metrics, worker, remainingNanos, onUnconfirmed);
  }

  // Resource-free test composition; these already-owned components perform their real lifecycle.
  ApiObservationContext(
      ApiMetricContext<?> metrics,
      Optional<OwnedApiObservationWorker> worker,
      LongSupplier remainingNanos,
      Consumer<Throwable> onUnconfirmed) {
    this.metricContext = Objects.requireNonNull(metrics, "metric context owner");
    this.worker = Objects.requireNonNull(worker, "observation worker holder");
    this.remainingNanos = Objects.requireNonNull(remainingNanos, "existing remaining stop budget");
    this.onUnconfirmed = Objects.requireNonNull(onUnconfirmed, "unconfirmed assembly policy");
  }

  /** SDK first, then DEBUG worker once; even partial initialization remains held by this owner. */
  public void initialize() {
    lock.lock();
    try {
      if (stopping.get() || attempted)
        throw new IllegalStateException("API observation initialization unavailable");
      attempted = true;
      metricContext.initialize();
      rejectStopping();
      worker.ifPresent(OwnedApiObservationWorker::start);
      rejectStopping();
    } finally {
      lock.unlock();
    }
  }

  private void rejectStopping() {
    if (stopping.get())
      throw new IllegalStateException("API observation initialization unavailable");
  }

  /** Borrowed endpoint input, not permission for Manager to initialize/close this context. */
  public ApiMetricContext<?> metrics() {
    return metricContext;
  }

  /** No wait behind initialization; drain the worker using the original budget before SDK close. */
  @Override
  public void close() throws IOException {
    stopping.set(true);
    try {
      worker.ifPresent(OwnedApiObservationWorker::requestStop);
      if (lock.isHeldByCurrentThread() || !lock.tryLock()) throw new IOException(UNCONFIRMED);
      try {
        if (closed) return;
        if (unconfirmed.get()) throw new IOException(UNCONFIRMED);
        if (worker.isPresent()) worker.orElseThrow().awaitStopped(remainingNanos);
        metricContext.close();
        if (unconfirmed.get()) throw new IOException(UNCONFIRMED);
        closed = true;
      } finally {
        lock.unlock();
      }
    } catch (IOException | RuntimeException | Error primary) {
      unconfirmed.set(true);
      try {
        onUnconfirmed.accept(primary);
      } catch (RuntimeException | Error diagnostic) {
        TemporaryInfrastructureException.attachSecondary(primary, diagnostic);
      }
      TemporaryInfrastructureException.preserveFatal(primary);
      throw primary;
    }
  }
}
