package dev.codex.schubert.nk.web.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import io.micrometer.core.instrument.MeterRegistry;
import java.util.Objects;
import java.util.function.Supplier;

/**
 * NK-OPS-001/RD171/UI252/SS312351/1835/PG-D625: borrowed DB and HTTP metadata in one caller-owned
 * registry. Stop every terminal callback before closing that registry/context. No database, server,
 * executor or registry acquisition/close is delegated to this binding.
 */
public final class WebServiceMetricBinding {
  private final WebDbPoolMetricBinding database;
  private final HttpMetricRecorder http;
  private final Runnable terminal;

  /** Resource-free factory: caller captures the returned owner before initialize. */
  public static WebMetricContext<WebServiceMetricBinding> prepareContext(
      String mode,
      Supplier<? extends HikariPoolMXBean> pool,
      Supplier<? extends HikariConfigMXBean> config,
      Runnable terminal) {
    Objects.requireNonNull(pool, "borrowed pool supplier");
    Objects.requireNonNull(config, "borrowed pool configuration supplier");
    Objects.requireNonNull(terminal, "HTTP metric terminal signal");
    return new WebMetricContext<WebServiceMetricBinding>(
        mode,
        registry ->
            new WebServiceMetricBinding(
                Objects.requireNonNull(pool.get(), "borrowed pool observation"),
                Objects.requireNonNull(config.get(), "borrowed pool configuration observation"),
                registry,
                mode,
                terminal),
        WebServiceMetricBinding::refresh);
  }

  public WebServiceMetricBinding(
      HikariPoolMXBean pool,
      HikariConfigMXBean config,
      MeterRegistry registry,
      String mode,
      Runnable terminal) {
    this.terminal = Objects.requireNonNull(terminal, "HTTP metric terminal signal");
    database = new WebDbPoolMetricBinding(pool, config, registry, mode);
    http = new HttpMetricRecorder(registry, mode);
  }

  /** Read-only DB observation; HTTP is recorded by the native terminal callback, never replayed. */
  public void refresh() {
    database.refresh();
  }

  /** Fresh pipeline-owned observer borrows the retained recorder, never internal mutable state. */
  public HttpMetricValve createHttpObserver() {
    return new HttpMetricValve(http, terminal);
  }
}
