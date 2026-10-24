package dev.codex.schubert.nk.web.monitoring;

import com.zaxxer.hikari.HikariConfigMXBean;
import com.zaxxer.hikari.HikariPoolMXBean;
import dev.codex.schubert.nk.web.monitoring.WebDbPoolMetricRecorder.Counts;
import java.util.Objects;
import java.util.Optional;

/**
 * Borrowed typed getters only; no pool/config creation, management lookup or controls.
 * PG-D579/1728.
 */
public final class WebDbPoolMetricObservation {
  public Optional<Counts> observe(HikariPoolMXBean pool, HikariConfigMXBean config) {
    Objects.requireNonNull(pool, "borrowed pool observation");
    Objects.requireNonNull(config, "borrowed pool configuration observation");
    int active = pool.getActiveConnections();
    int idle = pool.getIdleConnections();
    int pending = pool.getThreadsAwaitingConnection();
    int maximum = config.getMaximumPoolSize();
    if (active < 0 || idle < 0 || pending < 0 || maximum < 1) return Optional.empty();
    return Optional.of(new Counts(active, idle, pending, maximum));
  }
}
