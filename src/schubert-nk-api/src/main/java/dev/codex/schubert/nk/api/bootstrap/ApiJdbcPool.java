package dev.codex.schubert.nk.api.bootstrap;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.util.Objects;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;

/**
 * API-only, bounded PostgreSQL pool. The caller owns credential loading, source role/URL admission,
 * and the returned pool lifetime; startup must still run the DB and broker readiness gates before
 * exposing consumers. NK-OPS-001/NK-DAT-001; RD SYS-002/004, DAT-001; UI212/253; SS311/342/343;
 * PG271/PT-OPS-DBPOOL-001..003.
 */
@NullMarked
public final class ApiJdbcPool {
  public ApiJdbcPool() {}

  /** Opens a real fail-fast pool; a lazy pool is not an accepted startup result. */
  public HikariDataSource open(DataSource admittedSource) {
    Objects.requireNonNull(admittedSource, "API database source");
    var config = new HikariConfig();
    config.setPoolName("schubert-nk-api");
    config.setDataSource(admittedSource);
    config.setMaximumPoolSize(8);
    config.setMinimumIdle(2);
    config.setConnectionTimeout(3_000);
    config.setValidationTimeout(2_000);
    config.setInitializationFailTimeout(1);
    config.setAutoCommit(true);
    config.setReadOnly(false);
    config.setRegisterMbeans(false);
    return new HikariDataSource(config);
  }
}
