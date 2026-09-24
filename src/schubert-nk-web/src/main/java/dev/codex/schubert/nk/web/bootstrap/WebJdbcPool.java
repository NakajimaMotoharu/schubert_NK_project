package dev.codex.schubert.nk.web.bootstrap;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.util.Objects;
import javax.sql.DataSource;
import org.jspecify.annotations.NullMarked;

/**
 * Web technical-schema pool with its independent two-connection ceiling. The caller owns
 * credential/role admission, source and returned pool lifetime, and all later readiness gates.
 * NK-OPS-001/NK-WEB-002; RD SYS-002/004, AUT-002; UI212/226; SS311/342/343;
 * PG271/PT-OPS-DBPOOL-004..006.
 */
@NullMarked
public final class WebJdbcPool {
  public WebJdbcPool() {}

  /** Opens a real fail-fast technical-schema pool before Web HTTP acceptance. */
  public HikariDataSource open(DataSource admittedSource) {
    Objects.requireNonNull(admittedSource, "Web database source");
    var config = new HikariConfig();
    config.setPoolName("schubert-nk-web");
    config.setDataSource(admittedSource);
    config.setMaximumPoolSize(2);
    config.setMinimumIdle(1);
    config.setConnectionTimeout(3_000);
    config.setValidationTimeout(2_000);
    config.setInitializationFailTimeout(1);
    config.setAutoCommit(true);
    config.setReadOnly(false);
    config.setRegisterMbeans(false);
    return new HikariDataSource(config);
  }
}
